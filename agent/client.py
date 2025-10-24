# ABOUTME: Agent client wrapper managing SDK interaction
# ABOUTME: Handles conversation flow, memory integration, session management

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, create_sdk_mcp_server
from typing import Optional, AsyncIterator, Dict, Any
import uuid
import json
from .memory import MemoryManager
from .prompts import get_system_prompt
from tools.research import ResearchTools
from tools.documents import DocumentTools
from tools.export import ExportTools


class AssistantClient:
    def __init__(self, session_id: Optional[str] = None, resume: bool = False):
        self.memory = MemoryManager()
        self.session_id = session_id
        self.resume = resume
        self.client: Optional[ClaudeSDKClient] = None
        self.research_tools = None

    async def initialize(self):
        """Initialize memory and determine session"""
        await self.memory.initialize()

        if self.resume and not self.session_id:
            self.session_id = await self.memory.get_last_session_id()
            if self.session_id:
                print(f"[INFO] Resuming session: {self.session_id}")
                stats = await self.memory.get_session_stats(self.session_id)
                if stats:
                    print(f"[INFO] Previous session: {stats['message_count']} messages, "
                          f"${stats['total_cost_usd']:.4f} total cost")

        if not self.session_id:
            self.session_id = str(uuid.uuid4())
            await self.memory.create_session(self.session_id)
            print(f"[INFO] New session: {self.session_id}")

    async def _permission_handler(self, tool_name: str, input_data: Dict[str, Any],
                                  context: Any) -> Dict[str, Any]:
        """Custom permission handler with terminal prompts"""
        # Auto-approve MCP tools (our custom tools)
        if tool_name.startswith("mcp__"):
            return {"behavior": "allow", "updatedInput": input_data}

        # Prompt for Bash commands
        if tool_name == "Bash":
            command = input_data.get("command", "")
            print(f"\n{'='*60}")
            print(f"[PERMISSION] Bash command requested:")
            print(f"  {command}")
            print(f"{'='*60}")

            while True:
                response = input("Approve? (y/n): ").strip().lower()
                if response in ('y', 'yes'):
                    return {"behavior": "allow", "updatedInput": input_data}
                elif response in ('n', 'no'):
                    return {"behavior": "deny", "message": "User denied bash execution"}
                else:
                    print("[WARN] Please enter 'y' or 'n'")

        # Auto-approve other tools (Read, Write, Edit, etc.)
        return {"behavior": "allow", "updatedInput": input_data}

    async def setup_client(self) -> ClaudeSDKClient:
        """Configure and create SDK client with tools"""

        # Initialize tool instances
        self.research_tools = ResearchTools(self.memory, self.session_id)
        document_tools = DocumentTools(self.memory, self.session_id)
        export_tools = ExportTools(self.memory)

        # Collect all tools
        all_tools = []
        all_tools.extend(self.research_tools.get_tools())
        all_tools.extend(document_tools.get_tools())
        all_tools.extend(export_tools.get_tools())

        # Create MCP server with tools
        mcp_server = create_sdk_mcp_server(
            name="assistant",
            tools=all_tools
        )

        # Configure options with skills and tools
        options = ClaudeAgentOptions(
            system_prompt={
                "type": "custom",
                "custom": get_system_prompt()
            },
            mcp_servers={"assistant": mcp_server},
            allowed_tools=[
                # Skills system
                "Skill",  # Enable Agent Skills
                # Research
                "mcp__assistant__web_search",
                "mcp__assistant__fetch_url",
                "mcp__assistant__analyze_research",
                # Document tracking
                "mcp__assistant__register_document",
                "mcp__assistant__list_documents",
                "mcp__assistant__read_pdf",
                # Export/Import
                "mcp__assistant__export_data",
                "mcp__assistant__import_data",
                "mcp__assistant__list_exports",
                # Built-in tools
                "Bash",
                "Read",
                "Write",
                "Edit",
                "WebSearch"  # Built-in web search
            ],
            setting_sources=["user", "project"],  # Load skills from filesystem
            can_use_tool=self._permission_handler,  # Custom permission handler with terminal prompts
            cwd=".",
            resume=self.session_id if (self.resume and self.session_id) else None
        )

        return ClaudeSDKClient(options=options)

    async def send_message(self, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        """Send message and stream responses"""
        try:
            if not self.client:
                self.client = await self.setup_client()
                await self.client.connect()

            # Save user message
            await self.memory.save_message(self.session_id, "user", prompt)

            # Get previous cost to calculate delta
            session_stats = await self.memory.get_session_stats(self.session_id)
            previous_cost = session_stats['total_cost_usd'] if session_stats else 0.0

            # Send query
            await self.client.query(prompt)

            # Stream responses
            assistant_response = []
            tool_messages = []
            last_cost = None

            async for message in self.client.receive_response():
                yield message

                # Save tool_use messages
                if hasattr(message, 'type') and message.type == 'tool_use':
                    tool_data = {
                        'type': 'tool_use',
                        'name': getattr(message, 'name', ''),
                        'input': getattr(message, 'input', {})
                    }
                    tool_messages.append(json.dumps(tool_data))

                # Save tool_result messages
                elif hasattr(message, 'type') and message.type == 'tool_result':
                    tool_data = {
                        'type': 'tool_result',
                        'content': getattr(message, 'content', '')
                    }
                    tool_messages.append(json.dumps(tool_data))

                # Collect text responses
                elif hasattr(message, 'content'):
                    if isinstance(message.content, str):
                        assistant_response.append(message.content)
                    elif isinstance(message.content, list):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                assistant_response.append(block.text)

                # Track last cost
                if hasattr(message, 'total_cost_usd'):
                    last_cost = message.total_cost_usd

            # Update session with cost delta after response completes
            if last_cost is not None:
                cost_delta = last_cost - previous_cost
                await self.memory.update_session(
                    self.session_id,
                    cost_usd=cost_delta,
                    message_count=2  # user + assistant
                )

            # Save tool messages
            for tool_msg in tool_messages:
                await self.memory.save_message(
                    self.session_id,
                    "tool",
                    tool_msg
                )

            # Save assistant response
            if assistant_response:
                await self.memory.save_message(
                    self.session_id,
                    "assistant",
                    "\n".join(assistant_response)
                )
        finally:
            # Cleanup happens in close() method
            pass

    async def get_session_summary(self) -> Optional[Dict[str, Any]]:
        """Get current session statistics"""
        return await self.memory.get_session_stats(self.session_id)

    async def close(self):
        """Clean up resources"""
        try:
            if self.client:
                await self.client.disconnect()
        finally:
            if self.research_tools:
                await self.research_tools.close()
