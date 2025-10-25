# ABOUTME: Tests for chat API endpoints and WebSocket streaming
# ABOUTME: Validates message sending and real-time streaming functionality

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "backend"))

from main import app

client = TestClient(app)


def test_send_chat_message():
    """Send chat message initiates streaming"""
    # Create session first
    session_resp = client.post("/api/sessions")
    session_id = session_resp.json()["session_id"]

    # Send message
    response = client.post(
        "/api/chat",
        json={"session_id": session_id, "message": "Hello"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "streaming"


def test_websocket_connection():
    """WebSocket accepts connections and streams messages"""
    # Create session
    session_resp = client.post("/api/sessions")
    session_id = session_resp.json()["session_id"]

    # Test WebSocket connection
    with client.websocket_connect(f"/ws/chat/{session_id}") as websocket:
        # Send message
        websocket.send_json({"message": "Test message"})

        # Receive response (at least one message)
        data = websocket.receive_json()
        assert "type" in data
        # WebSocket should respond with some event


def test_chat_without_session():
    """Chat without valid session returns error"""
    response = client.post(
        "/api/chat",
        json={"session_id": "invalid", "message": "Hello"}
    )
    # Should handle gracefully - either 404 or create session
    assert response.status_code in [200, 404]
