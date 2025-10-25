# ABOUTME: Tests for file upload and download API endpoints
# ABOUTME: Validates file operations and export functionality

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import io

sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "backend"))

from main import app

client = TestClient(app)


def test_upload_file():
    """Upload file returns filename"""
    # Create test file
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

    response = client.post("/api/files/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "file_path" in data


def test_download_file():
    """Download file returns content"""
    # Upload file first
    file_content = b"Download test content"
    files = {"file": ("download.txt", io.BytesIO(file_content), "text/plain")}
    upload_resp = client.post("/api/files/upload", files=files)
    filename = upload_resp.json()["filename"]

    # Download file
    response = client.get(f"/api/files/{filename}")
    assert response.status_code == 200
    assert response.content == file_content


def test_download_nonexistent_file():
    """Downloading nonexistent file returns 404"""
    response = client.get("/api/files/nonexistent.txt")
    assert response.status_code == 404


def test_export_session():
    """Export session returns JSON data"""
    # Create session
    session_resp = client.post("/api/sessions")
    session_id = session_resp.json()["session_id"]

    # Export session
    response = client.get(f"/api/export/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "messages" in data
