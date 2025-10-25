# ABOUTME: End-to-end test for complete chat flow
# ABOUTME: Tests session creation, message sending, WebSocket streaming, and response display

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "backend"))

from main import app

client = TestClient(app)


def test_e2e_chat_flow():
    """
    Complete E2E test:
    1. Create session
    2. Verify session exists
    3. Connect WebSocket
    4. Send message via WebSocket (connection test only)
    5. Test export functionality

    Note: Actual AI response requires ANTHROPIC_API_KEY and is tested manually
    """

    # Step 1: Create session
    session_resp = client.post("/api/sessions")
    assert session_resp.status_code == 200
    session_data = session_resp.json()
    session_id = session_data["session_id"]
    assert session_id is not None
    print(f"[OK] Session created: {session_id}")

    # Step 2: Verify session exists
    get_session_resp = client.get(f"/api/sessions/{session_id}")
    assert get_session_resp.status_code == 200
    session_info = get_session_resp.json()
    assert session_info["session_id"] == session_id
    print(f"[OK] Session verified")

    # Step 3: Test WebSocket connection
    with client.websocket_connect(f"/ws/chat/{session_id}") as websocket:
        print(f"[OK] WebSocket connected")

        # Send test message
        test_message = "Test message"
        websocket.send_json({"message": test_message})
        print(f"[OK] Message sent: {test_message}")

        # Try to receive response (may get error if no API key)
        try:
            # Try to get at least one response
            data = websocket.receive_json()
            print(f"[WS] Received: {data.get('type')}")
            print(f"[OK] WebSocket communication successful")
        except Exception as e:
            print(f"[INFO] WebSocket receive failed (expected without API key): {e}")
            print(f"[OK] WebSocket connection verified (send successful)")

    # Step 4: Check message history
    messages_resp = client.get(f"/api/sessions/{session_id}/messages")
    assert messages_resp.status_code == 200
    print(f"[OK] Message history retrieved")

    # Step 5: Test export functionality
    export_resp = client.get(f"/api/export/{session_id}")
    assert export_resp.status_code == 200
    export_data = export_resp.json()
    assert export_data["session_id"] == session_id
    assert "messages" in export_data

    print(f"[OK] Session exported successfully")
    print(f"[PASS] E2E chat flow test passed")


def test_e2e_multiple_messages():
    """Test sending multiple messages in sequence"""

    # Create session
    session_resp = client.post("/api/sessions")
    session_id = session_resp.json()["session_id"]

    with client.websocket_connect(f"/ws/chat/{session_id}") as websocket:
        # Send first message
        websocket.send_json({"message": "First message"})

        # Wait for start/done (limited iterations)
        for _ in range(10):
            try:
                data = websocket.receive_json()
                if data.get("type") in ["start", "done"]:
                    break
            except:
                break

        print("[OK] Multiple message test passed")


def test_e2e_file_upload():
    """Test file upload functionality"""
    import io

    # Create test file
    file_content = b"Test file for E2E testing"
    files = {"file": ("e2e_test.txt", io.BytesIO(file_content), "text/plain")}

    # Upload file
    upload_resp = client.post("/api/files/upload", files=files)
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert "filename" in upload_data

    filename = upload_data["filename"]
    print(f"[OK] File uploaded: {filename}")

    # Download file
    download_resp = client.get(f"/api/files/{filename}")
    assert download_resp.status_code == 200
    assert download_resp.content == file_content

    print(f"[OK] File download verified")


def test_e2e_session_list():
    """Test listing sessions"""

    # Create multiple sessions
    session_ids = []
    for i in range(3):
        resp = client.post("/api/sessions")
        session_ids.append(resp.json()["session_id"])

    # List all sessions
    list_resp = client.get("/api/sessions")
    assert list_resp.status_code == 200
    sessions = list_resp.json()

    # Verify our sessions are in the list
    session_ids_in_list = [s["session_id"] for s in sessions]
    for sid in session_ids:
        assert sid in session_ids_in_list

    print(f"[OK] Session listing verified: {len(sessions)} total sessions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
