# ABOUTME: Tests for session history access tools
# ABOUTME: Validates list_sessions, view_session, search_history functionality

import pytest
from agent.memory import MemoryManager
from tools.memory import MemoryTools


@pytest.fixture
async def memory_manager():
    """Create test memory manager with clean database"""
    import tempfile
    import os

    # Create temp database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    manager = MemoryManager(db_path=db_path)
    await manager.initialize()

    yield manager

    # Cleanup
    os.unlink(db_path)


@pytest.fixture
async def populated_memory(memory_manager):
    """Memory manager with multiple sessions and messages"""
    # Create 3 sessions with messages
    sessions = []
    for i in range(3):
        session_id = f"test-session-{i}"
        await memory_manager.create_session(session_id)
        sessions.append(session_id)

        # Add messages to each session
        await memory_manager.save_message(session_id, "user", f"Hello from session {i}")
        await memory_manager.save_message(session_id, "assistant", f"Response in session {i}")
        await memory_manager.save_message(session_id, "user", "Tell me about Python")
        await memory_manager.save_message(session_id, "assistant", "Python is a programming language")

    return memory_manager, sessions


@pytest.mark.asyncio
async def test_list_all_sessions(populated_memory):
    """list_sessions tool returns all sessions with metadata"""
    memory, sessions = populated_memory
    tools = MemoryTools(memory, sessions[0])

    # Get list_sessions tool
    list_sessions_tool = None
    for tool in tools.get_tools():
        if tool.name == "list_sessions":
            list_sessions_tool = tool
            break

    assert list_sessions_tool is not None

    # Call tool
    result = await list_sessions_tool.handler({"limit": 10})

    assert "content" in result
    assert len(result["content"]) > 0
    text = result["content"][0]["text"]

    # Should contain session info
    assert "Found 3 session(s)" in text
    assert "Session:" in text
    assert "Messages:" in text
    assert "Cost:" in text


@pytest.mark.asyncio
async def test_view_specific_session(populated_memory):
    """view_session tool retrieves conversation history"""
    memory, sessions = populated_memory
    tools = MemoryTools(memory, sessions[0])

    # Get view_session tool
    view_session_tool = None
    for tool in tools.get_tools():
        if tool.name == "view_session":
            view_session_tool = tool
            break

    assert view_session_tool is not None

    # View session 1
    result = await view_session_tool.handler({
        "session_id": sessions[1],
        "limit": 50
    })

    assert "content" in result
    text = result["content"][0]["text"]

    # Should contain messages from session 1
    assert "Hello from session 1" in text
    assert "Response in session 1" in text
    assert "Python" in text


@pytest.mark.asyncio
async def test_search_across_all_sessions(populated_memory):
    """search_history tool finds messages across sessions"""
    memory, sessions = populated_memory
    tools = MemoryTools(memory, sessions[0])

    # Get search_history tool
    search_tool = None
    for tool in tools.get_tools():
        if tool.name == "search_history":
            search_tool = tool
            break

    assert search_tool is not None

    # Search for "Python"
    result = await search_tool.handler({
        "query": "Python",
        "limit": 20
    })

    assert "content" in result
    text = result["content"][0]["text"]

    # Should find matches in all 3 sessions
    assert "Found" in text
    assert "Python" in text
    # Should have results from multiple sessions
    assert text.count("Session:") >= 3


@pytest.mark.asyncio
async def test_list_sessions_limits_results(populated_memory):
    """list_sessions respects limit parameter"""
    memory, sessions = populated_memory
    tools = MemoryTools(memory, sessions[0])

    list_sessions_tool = None
    for tool in tools.get_tools():
        if tool.name == "list_sessions":
            list_sessions_tool = tool
            break

    # Request limit of 2
    result = await list_sessions_tool.handler({"limit": 2})
    text = result["content"][0]["text"]

    # Should show 2 sessions
    assert "Found 2 session(s)" in text


@pytest.mark.asyncio
async def test_view_nonexistent_session(memory_manager):
    """view_session handles nonexistent session gracefully"""
    tools = MemoryTools(memory_manager, "test")

    view_session_tool = None
    for tool in tools.get_tools():
        if tool.name == "view_session":
            view_session_tool = tool
            break

    result = await view_session_tool.handler({
        "session_id": "nonexistent-session-id",
        "limit": 50
    })

    text = result["content"][0]["text"]
    assert "No messages found" in text


@pytest.mark.asyncio
async def test_search_with_no_matches(memory_manager):
    """search_history handles no matches gracefully"""
    tools = MemoryTools(memory_manager, "test")

    search_tool = None
    for tool in tools.get_tools():
        if tool.name == "search_history":
            search_tool = tool
            break

    result = await search_tool.handler({
        "query": "nonexistent-search-term-xyz",
        "limit": 20
    })

    text = result["content"][0]["text"]
    assert "No messages found matching" in text
