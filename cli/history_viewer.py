# ABOUTME: Conversation history management
# ABOUTME: View, search, export conversation history

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class HistoryViewer:
    """Manage conversation history viewing and export"""

    def __init__(self, memory_manager):
        self.memory = memory_manager

    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from session

        Args:
            session_id: Session identifier
            limit: Number of messages to retrieve

        Returns:
            List of message dictionaries with role, content, timestamp
        """
        messages = await self.memory.get_messages(session_id, limit=limit)
        return messages

    async def search_messages(self, session_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search messages in session

        Args:
            session_id: Session identifier
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching messages
        """
        messages = await self.memory.get_messages(session_id, limit=1000)  # Get all messages

        # Simple search - case insensitive substring match
        query_lower = query.lower()
        results = []

        for msg in messages:
            content = msg.get('content', '')
            if query_lower in content.lower():
                results.append(msg)
                if len(results) >= limit:
                    break

        return results

    async def export_conversation(self, session_id: str, output_path: Optional[str] = None) -> str:
        """Export conversation to markdown file

        Args:
            session_id: Session identifier
            output_path: Optional custom output path

        Returns:
            Path to exported file
        """
        messages = await self.memory.get_messages(session_id, limit=10000)  # Get all

        # Generate filename if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"storage/exports/conversation_{timestamp}.md"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Build markdown content
        content = f"# Conversation Export\n\n"
        content += f"**Session ID:** {session_id}\n"
        content += f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**Total Messages:** {len(messages)}\n\n"
        content += "---\n\n"

        for msg in messages:
            role = msg.get('role', 'unknown')
            text = msg.get('content', '')
            timestamp = msg.get('timestamp', '')

            if role == 'user':
                content += f"### 👤 User ({timestamp})\n\n"
                content += f"{text}\n\n"
            elif role == 'assistant':
                content += f"### 🤖 Assistant ({timestamp})\n\n"
                content += f"{text}\n\n"
            elif role == 'tool':
                # Skip tool messages in export (too verbose)
                continue
            else:
                content += f"### {role} ({timestamp})\n\n"
                content += f"{text}\n\n"

            content += "---\n\n"

        # Write to file
        output_file.write_text(content, encoding='utf-8')

        return str(output_file)

    async def get_conversation_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics about the conversation

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with conversation stats
        """
        messages = await self.memory.get_messages(session_id, limit=10000)

        user_msgs = sum(1 for m in messages if m.get('role') == 'user')
        assistant_msgs = sum(1 for m in messages if m.get('role') == 'assistant')
        tool_msgs = sum(1 for m in messages if m.get('role') == 'tool')

        total_chars = sum(len(m.get('content', '')) for m in messages if m.get('role') in ['user', 'assistant'])

        return {
            'total_messages': len(messages),
            'user_messages': user_msgs,
            'assistant_messages': assistant_msgs,
            'tool_messages': tool_msgs,
            'total_characters': total_chars
        }
