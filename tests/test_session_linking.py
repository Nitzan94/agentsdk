# ABOUTME: Tests for session_id linking in tools
# ABOUTME: Verify research and documents linked to sessions

import pytest
from tools.research import ResearchTools
from tools.documents import DocumentTools


@pytest.mark.asyncio
async def test_research_tools_session_linking(memory_manager, test_session):
    """Test research tools link to session_id"""
    tools = ResearchTools(memory_manager, session_id=test_session)

    # Verify session_id set
    assert tools.session_id == test_session

    # Save research
    research_id = await memory_manager.save_research(
        query="test query",
        sources=["http://example.com"],
        analysis="test analysis",
        session_id=tools.session_id
    )

    # Verify saved with session_id
    assert research_id > 0


@pytest.mark.asyncio
async def test_document_tools_session_linking(memory_manager, test_session):
    """Test document tools link to session_id"""
    tools = DocumentTools(memory_manager, session_id=test_session)

    # Verify session_id set
    assert tools.session_id == test_session

    # Save document
    doc_id = await memory_manager.save_document(
        filename="test.pdf",
        file_type="pdf",
        file_path="/path/to/test.pdf",
        description="test doc",
        session_id=tools.session_id
    )

    # Verify saved with session_id
    assert doc_id > 0


@pytest.mark.asyncio
async def test_tools_without_session_id(memory_manager):
    """Test tools work without session_id"""
    tools = ResearchTools(memory_manager, session_id=None)

    # Should have None session_id
    assert tools.session_id is None

    # Can still save (session_id will be None in DB)
    research_id = await memory_manager.save_research(
        query="test",
        sources=[],
        analysis="test",
        session_id=tools.session_id
    )

    assert research_id > 0
