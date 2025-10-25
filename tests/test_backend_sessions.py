# ABOUTME: Tests for session management API endpoints
# ABOUTME: Validates session creation, retrieval, and history operations

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "backend"))

from main import app

client = TestClient(app)


def test_list_sessions():
    """List all sessions returns 200"""
    response = client.get("/api/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_session():
    """Create new session returns session_id"""
    response = client.post("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], str)


def test_get_session_details():
    """Get session details returns stats"""
    # Create session first
    create_resp = client.post("/api/sessions")
    session_id = create_resp.json()["session_id"]

    # Get details
    response = client.get(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "started_at" in data
    assert "message_count" in data


def test_get_session_messages():
    """Get session messages returns conversation history"""
    # Create session
    create_resp = client.post("/api/sessions")
    session_id = create_resp.json()["session_id"]

    # Get messages
    response = client.get(f"/api/sessions/{session_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_session():
    """Getting nonexistent session returns 404"""
    response = client.get("/api/sessions/nonexistent-id")
    assert response.status_code == 404
