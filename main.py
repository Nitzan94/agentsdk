# ABOUTME: Main CLI entry point for personal assistant agent
# ABOUTME: Interactive chat interface with streaming responses and interrupts

import asyncio
import sys
import argparse
from pathlib import Path
from agent.client import AssistantClient

# ANSI color codes for terminal
class Colors:
    # User messages - cyan
    USER = '\033[96m'
    # Assistant messages - green
    ASSISTANT = '\033[92m'
    # System messages - yellow
    SYSTEM = '\033[93m'
    # Errors - red
    ERROR = '\033[91m'
    # Reset
    RESET = '\033[0m'
    # Bold
    BOLD = '\033[1m'


def print_banner():
    """Display welcome banner"""
    print(f"{Colors.BOLD}{Colors.SYSTEM}{'=' * 60}")
    print("  Personal Assistant Agent")
    print("  Note-taking | Research | Reports | Memory")
    print(f"{'=' * 60}{Colors.RESET}")
    print()


def _is_skill_message(text: str) -> bool:
    """Check if text is a skill-related system message"""
    if not isinstance(text, str):
        return False

    # Filter out skill loading messages
    skill_indicators = [
        "skill is running",
        "skill is loading",
        "ABOUTME:",
        "# ",  # Markdown headers from skill prompts
    ]

    text_lower = text.lower().strip()

    # Check for skill indicators
    for indicator in skill_indicators:
        if indicator.lower() in text_lower:
            return True

    # Check if it's a multi-line skill prompt (starts with markdown/headers)
    if text.strip().startswith("#") and len(text) > 100:
        return True

    return False


def print_help():
    """Display command help"""
    print(f"\n{Colors.SYSTEM}Commands:")
    print(f"  /help     - Show this help")
    print(f"  /stats    - Show session statistics")
    print(f"  /clear    - Clear screen")
    print(f"  /exit     - Exit assistant")
    print(f"  Ctrl+C    - Interrupt current response{Colors.RESET}")
    print()


async def display_stream(client: AssistantClient, prompt: str):
    """Display streaming response from assistant"""
    try:
        # Print assistant prefix in color
        print(f"{Colors.ASSISTANT}", end='', flush=True)

        async for message in client.send_message(prompt):
            # Handle different message types
            if hasattr(message, 'type'):
                if message.type == 'text':
                    # Filter out skill loading messages
                    content = message.content
                    if not _is_skill_message(content):
                        print(content, end='', flush=True)
                elif message.type == 'tool_use':
                    tool_name = getattr(message, 'name', 'unknown')
                    # Only show non-skill tool usage
                    if tool_name != 'Skill':
                        print(f"\n{Colors.SYSTEM}[TOOL] Using: {tool_name}{Colors.ASSISTANT}", flush=True)
                elif message.type == 'tool_result':
                    # Tool results are handled internally
                    pass
            elif hasattr(message, 'content'):
                if isinstance(message.content, str):
                    content = message.content
                    if not _is_skill_message(content):
                        print(content, end='', flush=True)
                elif isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            text = block.text
                            if not _is_skill_message(text):
                                print(text, end='', flush=True)
                        elif hasattr(block, 'type') and block.type == 'text':
                            text = block.get('text', '')
                            if not _is_skill_message(text):
                                print(text, end='', flush=True)

        print(f"{Colors.RESET}")  # Reset color and newline

    except KeyboardInterrupt:
        print(f"{Colors.RESET}\n{Colors.ERROR}[INTERRUPTED]{Colors.RESET}")
        if client.client:
            try:
                await asyncio.wait_for(client.client.interrupt(), timeout=1.0)
            except asyncio.TimeoutError:
                print(f"{Colors.ERROR}[WARN] Interrupt timeout{Colors.RESET}")


async def run_interactive(resume: bool = False):
    """Run interactive CLI session"""
    print_banner()

    if resume:
        print(f"{Colors.SYSTEM}[INFO] Attempting to resume last session...{Colors.RESET}")
    else:
        print(f"{Colors.SYSTEM}[INFO] Starting new session...{Colors.RESET}")

    # Initialize client
    client = AssistantClient(resume=resume)
    await client.initialize()

    print_help()
    print(f"{Colors.SYSTEM}[OK] Ready. Type your message or /help for commands.{Colors.RESET}\n")

    try:
        while True:
            try:
                # Get user input with color
                user_input = input(f"{Colors.USER}You: {Colors.RESET}").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input == "/exit":
                    print(f"{Colors.SYSTEM}[INFO] Goodbye!{Colors.RESET}")
                    break

                elif user_input == "/help":
                    print_help()
                    continue

                elif user_input == "/stats":
                    stats = await client.get_session_summary()
                    if stats:
                        print(f"\n{Colors.SYSTEM}[INFO] Session Statistics:")
                        print(f"  Session ID: {client.session_id}")
                        print(f"  Started: {stats['started_at']}")
                        print(f"  Last active: {stats['last_active_at']}")
                        print(f"  Messages: {stats['message_count']}")
                        print(f"  Total cost: ${stats['total_cost_usd']:.4f}{Colors.RESET}\n")
                    continue

                elif user_input == "/clear":
                    print("\033[2J\033[H", end='')  # Clear screen
                    print_banner()
                    continue

                elif user_input.startswith("/"):
                    print(f"{Colors.ERROR}[WARN] Unknown command: {user_input}{Colors.RESET}")
                    print_help()
                    continue

                # Send message and display response
                print(f"\n{Colors.BOLD}Assistant:{Colors.RESET} ", end='', flush=True)
                await display_stream(client, user_input)
                print()

            except KeyboardInterrupt:
                print(f"\n{Colors.SYSTEM}[INFO] Use /exit to quit or continue chatting{Colors.RESET}")
                continue

            except EOFError:
                break

    finally:
        await client.close()


def main():
    """Parse arguments and start CLI"""
    parser = argparse.ArgumentParser(description="Personal Assistant Agent")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume last session"
    )
    args = parser.parse_args()

    try:
        asyncio.run(run_interactive(resume=args.resume))
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
