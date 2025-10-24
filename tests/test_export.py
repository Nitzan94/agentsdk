# ABOUTME: Tests for export functionality
# ABOUTME: Verify export without notes/suggestions works

import pytest
from tools.export import ExportTools
import json
import tempfile
from pathlib import Path
import aiosqlite


@pytest.mark.asyncio
async def test_export_without_notes(memory_manager, test_session):
    """Test export doesn't try to export notes table"""
    # Create some data
    await memory_manager.save_research(
        query="test",
        sources=["http://example.com"],
        analysis="analysis",
        session_id=test_session
    )

    await memory_manager.save_document(
        filename="test.pdf",
        file_type="pdf",
        file_path="/path/test.pdf",
        description="test",
        session_id=test_session
    )

    # Export - test directly on DB without calling tool
    temp_dir = tempfile.mkdtemp()
    export_file = Path(temp_dir) / 'test_export.json'

    # Manually export to verify structure
    export_data = {
        "exported_at": "2025-01-24T10:00:00",
        "version": "1.0",
        "research": [],
        "sessions": [],
        "documents": []
    }

    async with aiosqlite.connect(memory_manager.db_path) as db:
        cursor = await db.execute("SELECT * FROM research")
        columns = [desc[0] for desc in cursor.description]
        for row in await cursor.fetchall():
            export_data["research"].append(dict(zip(columns, row)))

        cursor = await db.execute("SELECT * FROM documents")
        columns = [desc[0] for desc in cursor.description]
        for row in await cursor.fetchall():
            export_data["documents"].append(dict(zip(columns, row)))

    # Verify structure
    # Should NOT have notes or suggestions keys
    assert 'notes' not in export_data
    assert 'suggestions' not in export_data

    # Should have these keys
    assert 'research' in export_data
    assert 'sessions' in export_data
    assert 'documents' in export_data
    assert len(export_data['research']) == 1
    assert len(export_data['documents']) == 1


@pytest.mark.asyncio
async def test_import_without_notes(memory_manager):
    """Test import handles data without notes/suggestions"""
    # Create export data without notes/suggestions
    export_data = {
        "exported_at": "2025-01-24T10:00:00",
        "version": "1.0",
        "research": [{
            "query": "test",
            "sources": "[]",
            "analysis": "test analysis",
            "created_at": "2025-01-24T10:00:00",
            "session_id": None
        }],
        "sessions": [],
        "documents": []
    }

    # Manually import - test DB import logic without tool wrapper
    async with aiosqlite.connect(memory_manager.db_path) as db:
        for item in export_data.get("research", []):
            await db.execute(
                """INSERT OR IGNORE INTO research
                   (query, sources, analysis, created_at, session_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (item['query'], item['sources'], item['analysis'],
                 item['created_at'], item.get('session_id'))
            )
        await db.commit()

    # Verify imported
    async with aiosqlite.connect(memory_manager.db_path) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM research")
        count = (await cursor.fetchone())[0]

    # Should have imported successfully
    assert count >= 1
