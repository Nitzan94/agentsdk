# ABOUTME: Rich terminal CLI for personal assistant
# ABOUTME: Enhanced visuals, multi-line input, history, markdown rendering

import asyncio
import sys
import argparse
from pathlib import Path
from agent.client import AssistantClient
from cli.rich_display import RichDisplay
from cli.input_handler import InputHandler
from cli.history_viewer import HistoryViewer


def _is_skill_message(text: str) -> bool:
    """Check if text is a skill-related system message"""
    if not isinstance(text, str):
        return False

    skill_indicators = [
        "skill is running",
        "skill is loading",
        "ABOUTME:",
    ]

    text_lower = text.lower().strip()

    for indicator in skill_indicators:
        if indicator.lower() in text_lower:
            return True

    if text.strip().startswith("#") and len(text) > 100:
        return True

    return False


async def display_stream(display: RichDisplay, client: AssistantClient, prompt: str):
    """Display streaming response from assistant"""
    try:
        display.show_assistant_prefix()
        display.start_streaming()

        async for message in client.send_message(prompt):
            # Handle different message types
            if hasattr(message, 'type'):
                if message.type == 'text':
                    content = message.content
                    if not _is_skill_message(content):
                        display.update_stream(content)

                elif message.type == 'tool_use':
                    tool_name = getattr(message, 'name', 'unknown')
                    if tool_name != 'Skill':
                        display.show_tool_usage(tool_name)

                elif message.type == 'tool_result':
                    pass

            elif hasattr(message, 'content'):
                if isinstance(message.content, str):
                    content = message.content
                    if not _is_skill_message(content):
                        display.update_stream(content)

                elif isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            text = block.text
                            if not _is_skill_message(text):
                                display.update_stream(text)
                        elif hasattr(block, 'type') and block.type == 'text':
                            text = block.get('text', '')
                            if not _is_skill_message(text):
                                display.update_stream(text)

        display.end_stream(markdown=True)

    except KeyboardInterrupt:
        display.end_stream(markdown=False)
        display.show_warning("Response interrupted")
        if client.client:
            try:
                await asyncio.wait_for(client.client.interrupt(), timeout=1.0)
            except asyncio.TimeoutError:
                display.show_error("Interrupt timeout")


async def run_interactive(resume: bool = False):
    """Run rich interactive CLI session"""
    display = RichDisplay()
    input_handler = InputHandler()

    display.print_banner()

    if resume:
        display.show_info("Attempting to resume last session...")
    else:
        display.show_info("Starting new session...")

    # Initialize client
    client = AssistantClient(resume=resume)
    await client.initialize()

    # Initialize history viewer
    history_viewer = HistoryViewer(client.memory)

    display.print_help()
    display.show_success("Ready! Type your message or /help for commands.")
    display.print()

    try:
        while True:
            try:
                # Get user input (async)
                user_input = await input_handler.get_input("You: ")

                if not user_input:
                    continue

                # Handle commands
                if user_input == "/exit":
                    display.show_info("Goodbye!")
                    break

                elif user_input == "/help":
                    display.print_help()
                    continue

                elif user_input == "/stats":
                    stats = await client.get_session_summary()
                    if stats:
                        display.show_stats(client.session_id, stats)
                    continue

                elif user_input.startswith("/history"):
                    # Parse limit
                    parts = user_input.split()
                    limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10

                    messages = await history_viewer.get_recent_messages(client.session_id, limit=limit)
                    if messages:
                        display.show_history(messages)
                    else:
                        display.show_info("No messages in history")
                    continue

                elif user_input.startswith("/search "):
                    query = user_input[8:].strip()  # Remove "/search "
                    if query:
                        messages = await history_viewer.search_messages(client.session_id, query, limit=10)
                        if messages:
                            display.show_success(f"Found {len(messages)} matching message(s):")
                            display.show_history(messages)
                        else:
                            display.show_info(f"No messages found matching: {query}")
                    else:
                        display.show_warning("Usage: /search <query>")
                    continue

                elif user_input == "/export":
                    display.show_info("Exporting conversation...")
                    export_path = await history_viewer.export_conversation(client.session_id)
                    display.show_success(f"Conversation exported to: {export_path}")
                    continue

                elif user_input == "/clear":
                    display.clear_screen()
                    display.print_banner()
                    continue

                elif user_input.startswith("/"):
                    display.show_warning(f"Unknown command: {user_input}")
                    display.print_help()
                    continue

                # Send message and display response (user input already shown by prompt)
                display.print()  # Add newline after user input
                await display_stream(display, client, user_input)
                display.print()

            except KeyboardInterrupt:
                display.print()
                display.show_info("Use /exit to quit or continue chatting")
                continue

            except EOFError:
                break

    finally:
        await client.close()


def main():
    """Parse arguments and start rich CLI"""
    parser = argparse.ArgumentParser(description="Personal Assistant Agent (Rich UI)")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume last session"
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Use simple CLI instead of rich UI"
    )
    args = parser.parse_args()

    if args.simple:
        # Fall back to simple CLI
        import main
        main.main()
        return

    try:
        asyncio.run(run_interactive(resume=args.resume))
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
