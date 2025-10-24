# ABOUTME: Tests for message persistence
# ABOUTME: Verify all message types saved correctly

import pytest
import json


@pytest.mark.asyncio
async def test_save_user_message(memory_manager, test_session):
    """Test saving user messages"""
    await memory_manager.save_message(
        test_session,
        "user",
        "Hello, assistant!"
    )

    history = await memory_manager.get_session_history(test_session)
    assert len(history) == 1
    assert history[0]['role'] == 'user'
    assert history[0]['content'] == 'Hello, assistant!'


@pytest.mark.asyncio
async def test_save_assistant_message(memory_manager, test_session):
    """Test saving assistant messages"""
    await memory_manager.save_message(
        test_session,
        "assistant",
        "Hello! How can I help?"
    )

    history = await memory_manager.get_session_history(test_session)
    assert len(history) == 1
    assert history[0]['role'] == 'assistant'


@pytest.mark.asyncio
async def test_save_tool_message(memory_manager, test_session):
    """Test saving tool use/result messages"""
    tool_data = {
        'type': 'tool_use',
        'name': 'web_search',
        'input': {'query': 'python asyncio'}
    }

    await memory_manager.save_message(
        test_session,
        "tool",
        json.dumps(tool_data)
    )

    history = await memory_manager.get_session_history(test_session)
    assert len(history) == 1
    assert history[0]['role'] == 'tool'

    # Verify can parse JSON back
    saved_tool_data = json.loads(history[0]['content'])
    assert saved_tool_data['type'] == 'tool_use'
    assert saved_tool_data['name'] == 'web_search'


@pytest.mark.asyncio
async def test_save_conversation_flow(memory_manager, test_session):
    """Test saving full conversation with tools"""
    # User message
    await memory_manager.save_message(test_session, "user", "Search for Python")

    # Tool use
    tool_use = json.dumps({
        'type': 'tool_use',
        'name': 'web_search',
        'input': {'query': 'Python'}
    })
    await memory_manager.save_message(test_session, "tool", tool_use)

    # Tool result
    tool_result = json.dumps({
        'type': 'tool_result',
        'content': 'Found 5 results'
    })
    await memory_manager.save_message(test_session, "tool", tool_result)

    # Assistant response
    await memory_manager.save_message(test_session, "assistant", "Here are the results...")

    history = await memory_manager.get_session_history(test_session)
    assert len(history) == 4
    assert history[0]['role'] == 'user'
    assert history[1]['role'] == 'tool'
    assert history[2]['role'] == 'tool'
    assert history[3]['role'] == 'assistant'
