# ABOUTME: Tests for resource cleanup
# ABOUTME: Verify no leaks on errors

import pytest
from agent.client import AssistantClient
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_cleanup_on_error(memory_manager):
    """Test resources cleaned up even on error"""
    client = AssistantClient()
    client.memory = memory_manager
    await client.initialize()

    # Create mock research tools
    mock_research_tools = MagicMock()
    mock_research_tools.close = AsyncMock()
    client.research_tools = mock_research_tools

    # Call close
    await client.close()

    # Verify cleanup called
    mock_research_tools.close.assert_called_once()


@pytest.mark.asyncio
async def test_close_handles_missing_client():
    """Test close doesn't error when client not initialized"""
    client = AssistantClient()

    # Should not raise error
    try:
        await client.close()
    except Exception as e:
        pytest.fail(f"close() raised {e}")


@pytest.mark.asyncio
async def test_close_handles_disconnect_error():
    """Test close handles errors during disconnect"""
    client = AssistantClient()

    # Mock client that raises on disconnect
    mock_sdk_client = MagicMock()
    mock_sdk_client.disconnect = AsyncMock(side_effect=Exception("Disconnect failed"))
    client.client = mock_sdk_client

    # Mock research tools
    mock_research_tools = MagicMock()
    mock_research_tools.close = AsyncMock()
    client.research_tools = mock_research_tools

    # Should still call research_tools.close despite disconnect error
    try:
        await client.close()
    except:
        pass

    # Research tools close should still be called (in finally block)
    mock_research_tools.close.assert_called_once()
