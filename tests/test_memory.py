# Test custom memory persistence
import pytest
from agent.memory import MemoryManager
import os
from pathlib import Path

TEST_DB = "storage/test_memory.db"


@pytest.fixture
async def memory():
    """Create test memory manager"""
    # Clean up test DB if exists
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    mem = MemoryManager(db_path=TEST_DB)
    await mem.initialize()
    yield mem

    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_save_and_retrieve_memory(memory):
    """Test saving and retrieving custom memories"""
    # Save memories
    await memory.save_memory("business", "company_name", "Lady's Bakery", "session-1")
    await memory.save_memory("business", "industry", "Food & Beverage", "session-1")
    await memory.save_memory("preferences", "report_format", "markdown", "session-1")

    # Retrieve all memories
    memories = await memory.get_memories()
    assert len(memories) == 3

    # Retrieve by category
    business_memories = await memory.get_memories(category="business")
    assert len(business_memories) == 2

    # Check formatted output
    formatted = await memory.get_all_memories_formatted()
    assert "BUSINESS:" in formatted
    assert "company_name: Lady's Bakery" in formatted
    assert "PREFERENCES:" in formatted
    assert "report_format: markdown" in formatted


@pytest.mark.asyncio
async def test_update_memory(memory):
    """Test updating existing memory"""
    # Save initial value
    await memory.save_memory("business", "employee_count", "5", "session-1")

    # Update value
    await memory.save_memory("business", "employee_count", "10", "session-2")

    # Should only have 1 entry
    memories = await memory.get_memories()
    assert len(memories) == 1
    assert memories[0]["value"] == "10"


@pytest.mark.asyncio
async def test_delete_memory(memory):
    """Test deleting memory"""
    # Save memory
    await memory.save_memory("personal", "timezone", "UTC", "session-1")

    # Verify it exists
    memories = await memory.get_memories()
    assert len(memories) == 1

    # Delete it
    deleted = await memory.delete_memory("personal", "timezone")
    assert deleted is True

    # Verify it's gone
    memories = await memory.get_memories()
    assert len(memories) == 0

    # Try deleting again
    deleted = await memory.delete_memory("personal", "timezone")
    assert deleted is False


@pytest.mark.asyncio
async def test_memory_persists_across_sessions(memory):
    """Test that memories persist across different sessions"""
    # Session 1: Save memory
    session_1 = "session-abc"
    await memory.create_session(session_1)
    await memory.save_memory("business", "founded_year", "2020", session_1)

    # Session 2: Should still be able to retrieve it
    session_2 = "session-xyz"
    await memory.create_session(session_2)

    memories = await memory.get_memories()
    assert len(memories) == 1
    assert memories[0]["value"] == "2020"

    # Session 2 can also add memories
    await memory.save_memory("business", "location", "New York", session_2)

    # Both should be available
    memories = await memory.get_memories()
    assert len(memories) == 2
