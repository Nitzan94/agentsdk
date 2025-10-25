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
        from tools.research import ResearchTools
        from tools.memory import MemoryTools
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

        # Test custom memory
        await memory.save_memory("test", "key", "value", session_id)
        memories = await memory.get_memories()
        print(f"[OK] Custom memory: {len(memories)} entry(ies)")

        print("[OK] Memory manager working")

    except Exception as e:
        print(f"[ERROR] Memory test failed: {e}")
        return False

    print("\n[INFO] Testing tool initialization...")
    try:
        research_tools = ResearchTools(memory, session_id)
        tools = research_tools.get_tools()
        print(f"[OK] Research tools: {len(tools)} tools")

        memory_tools = MemoryTools(memory, session_id)
        tools = memory_tools.get_tools()
        print(f"[OK] Memory tools: {len(tools)} tools")

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
