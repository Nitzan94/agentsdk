# ABOUTME: Setup validation script
# ABOUTME: Tests imports, database initialization, tool creation

import asyncio
import sys


async def test_setup():
    """Validate setup without requiring API key"""
    print("[INFO] Testing imports...")

    try:
        from agent.memory import MemoryManager
        from agent.prompts import get_system_prompt
        from agent.client import AssistantClient
        from tools.notes import NoteTools
        from tools.research import ResearchTools
        from tools.reports import ReportTools
        print("[OK] All imports successful")
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("[INFO] Run: pip install -r requirements.txt")
        return False

    print("\n[INFO] Testing memory manager...")
    try:
        memory = MemoryManager("test_agent.db")
        await memory.initialize()
        print("[OK] Database initialized")

        # Test session creation
        session_id = await memory.create_session("test-session-123")
        print(f"[OK] Session created: {session_id}")

        # Test message storage
        await memory.save_message(session_id, "user", "Test message")
        print("[OK] Message saved")

        # Test note creation
        note_id = await memory.save_note(
            title="Test Note",
            content="Test content",
            tags=["test"],
            file_path="test.md"
        )
        print(f"[OK] Note saved: ID {note_id}")

        # Test note search
        notes = await memory.search_notes(query="Test")
        print(f"[OK] Note search: found {len(notes)} note(s)")

        print("[OK] Memory manager working")

    except Exception as e:
        print(f"[ERROR] Memory test failed: {e}")
        return False

    print("\n[INFO] Testing tool initialization...")
    try:
        note_tools = NoteTools(memory)
        tools = note_tools.get_tools()
        print(f"[OK] Note tools: {len(tools)} tools")

        research_tools = ResearchTools(memory)
        tools = research_tools.get_tools()
        print(f"[OK] Research tools: {len(tools)} tools")

        report_tools = ReportTools(memory)
        tools = report_tools.get_tools()
        print(f"[OK] Report tools: {len(tools)} tools")

        await research_tools.close()

    except Exception as e:
        print(f"[ERROR] Tool test failed: {e}")
        return False

    print("\n[INFO] Testing system prompt...")
    try:
        prompt = get_system_prompt()
        print(f"[OK] System prompt: {len(prompt)} chars")
    except Exception as e:
        print(f"[ERROR] Prompt test failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("[OK] All tests passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Set ANTHROPIC_API_KEY environment variable")
    print("2. Run: python main.py")
    print("3. Or resume last session: python main.py --resume")
    print()

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_setup())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        sys.exit(1)
