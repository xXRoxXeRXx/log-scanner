"""
Tests for FastAPI upload endpoint
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_no_files():
    """Test upload endpoint with no files"""
    response = client.post("/api/upload")
    assert response.status_code == 422  # Validation error


def test_upload_invalid_file_type():
    """Test upload with invalid file type"""
    files = [
        ("files", ("test.txt", b"test content", "text/plain"))
    ]
    response = client.post("/api/upload", files=files)
    # Should either accept .txt or reject it
    assert response.status_code in [200, 400]


def test_upload_valid_log_file(tmp_path):
    """Test upload with valid .log file"""
    # Create a temporary log file
    log_file = tmp_path / "test.log"
    log_file.write_text("""
{"reqId":"abc123","level":3,"time":"2024-01-01T10:00:00+00:00","message":"Test error"}
{"reqId":"abc123","level":3,"time":"2024-01-01T10:00:01+00:00","message":"Test error 2"}
    """)
    
    # Upload file
    with open(log_file, 'rb') as f:
        files = [("files", ("test.log", f, "text/plain"))]
        response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["file_count"] == 1


def test_get_results_not_found():
    """Test getting non-existent result"""
    response = client.get("/api/results/nonexistent-id")
    assert response.status_code == 404


def test_list_results():
    """Test listing all results"""
    response = client.get("/api/results")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert isinstance(data["results"], list)


def test_upload_and_get_result(tmp_path):
    """Test complete flow: upload -> get result"""
    # Create log file
    log_file = tmp_path / "test.log"
    log_file.write_text('{"level":3,"message":"Test"}')
    
    # Upload
    with open(log_file, 'rb') as f:
        files = [("files", ("test.log", f, "text/plain"))]
        upload_response = client.post("/api/upload", files=files)
    
    assert upload_response.status_code == 200
    analysis_id = upload_response.json()["analysis_id"]
    
    # Get result
    result_response = client.get(f"/api/results/{analysis_id}")
    assert result_response.status_code == 200
    
    result = result_response.json()
    assert result["id"] == analysis_id
    assert "categories" in result
    assert "entries" in result


def test_delete_result(tmp_path):
    """Test deleting a result"""
    # Create and upload log file
    log_file = tmp_path / "test.log"
    log_file.write_text('{"level":3,"message":"Test"}')
    
    with open(log_file, 'rb') as f:
        files = [("files", ("test.log", f, "text/plain"))]
        upload_response = client.post("/api/upload", files=files)
    
    analysis_id = upload_response.json()["analysis_id"]
    
    # Delete result
    delete_response = client.delete(f"/api/results/{analysis_id}")
    assert delete_response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/api/results/{analysis_id}")
    assert get_response.status_code == 404


def test_file_size_limit():
    """Test file size limit (50MB)"""
    # Create large file content (> 50MB)
    large_content = b"x" * (51 * 1024 * 1024)  # 51 MB
    
    files = [("files", ("large.log", large_content, "text/plain"))]
    response = client.post("/api/upload", files=files)
    
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_multiple_files_upload(tmp_path):
    """Test uploading multiple files"""
    # Create multiple log files
    log_file1 = tmp_path / "test1.log"
    log_file2 = tmp_path / "test2.log"
    log_file1.write_text('{"level":3,"message":"Test 1"}')
    log_file2.write_text('{"level":3,"message":"Test 2"}')
    
    # Upload both files
    files = []
    with open(log_file1, 'rb') as f1, open(log_file2, 'rb') as f2:
        files = [
            ("files", ("test1.log", f1.read(), "text/plain")),
            ("files", ("test2.log", f2.read(), "text/plain"))
        ]
        response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
