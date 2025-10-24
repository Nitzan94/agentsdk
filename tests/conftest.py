# ABOUTME: Pytest configuration and shared fixtures
# ABOUTME: Test setup for agent, memory, and tools

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from agent.memory import MemoryManager
from agent.client import AssistantClient


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_db():
    """Create temporary database for testing"""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    yield str(db_path)

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
async def memory_manager(temp_db):
    """Create memory manager with temporary database"""
    memory = MemoryManager(db_path=temp_db)
    await memory.initialize()
    return memory


@pytest.fixture
async def test_session(memory_manager):
    """Create test session"""
    session_id = "test-session-123"
    await memory_manager.create_session(session_id)
    return session_id
