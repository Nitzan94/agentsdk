# ABOUTME: Tests for session resume functionality
# ABOUTME: Verify resume logic works correctly

import pytest
from agent.client import AssistantClient


@pytest.mark.asyncio
async def test_resume_with_session_id():
    """Test resume logic when session_id exists"""
    client = AssistantClient(session_id="existing-session", resume=True)
    await client.initialize()

    # Setup client to get options
    sdk_client = await client.setup_client()

    # Check resume parameter passed correctly
    # Note: Can't directly access options, but session_id should be set
    assert client.session_id == "existing-session"
    assert client.resume is True


@pytest.mark.asyncio
async def test_resume_without_session_id():
    """Test resume logic when session_id is None"""
    client = AssistantClient(session_id=None, resume=True)
    await client.initialize()

    # Should create new session even though resume=True
    assert client.session_id is not None
    assert len(client.session_id) > 0


@pytest.mark.asyncio
async def test_no_resume():
    """Test no resume creates new session"""
    client = AssistantClient(session_id="old-session", resume=False)
    await client.initialize()

    # Should use provided session_id but not resume
    assert client.session_id == "old-session"
    assert client.resume is False


@pytest.mark.asyncio
async def test_new_session():
    """Test creating entirely new session"""
    client = AssistantClient()
    await client.initialize()

    # Should create UUID session_id
    assert client.session_id is not None
    assert len(client.session_id) == 36  # UUID format
    assert client.resume is False
