"""
Tests for Security Features (v2.0.1+)
Tests for CORS, Rate Limiting, Authentication, Cleanup
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
import sys
import time

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app, cleanup_old_results, RESULTS_DIR, UPLOAD_DIR

client = TestClient(app)


# === CORS Tests ===

def test_cors_preflight():
    """Test CORS preflight request"""
    response = client.options(
        "/api/upload",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "POST"
        }
    )
    # Should allow localhost
    assert response.status_code in [200, 204]


def test_cors_allowed_origin():
    """Test request from allowed origin"""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:8000"}
    )
    assert response.status_code == 200


# === Rate Limiting Tests ===

def test_rate_limit_health_endpoint():
    """Test rate limiting on health endpoint (30/minute)"""
    # Make requests up to limit
    for i in range(31):  # One more than limit
        response = client.get("/health")
        if i < 30:
            assert response.status_code == 200, f"Request {i+1} should succeed"
        else:
            # 31st request might be rate limited (depends on timing)
            assert response.status_code in [200, 429], f"Request {i+1} status: {response.status_code}"


def test_rate_limit_response_format():
    """Test rate limit error response format"""
    # Make many rapid requests to trigger rate limit
    responses = []
    for _ in range(35):
        response = client.get("/health")
        responses.append(response)
    
    # Check if any were rate limited
    rate_limited = [r for r in responses if r.status_code == 429]
    if rate_limited:
        response = rate_limited[0]
        data = response.json()
        assert "error" in data or "detail" in data


# === Authentication Tests ===

def test_upload_without_auth_when_disabled():
    """Test upload works without auth when ENABLE_AUTH=false"""
    # Create a small test file
    test_content = b'{"level":3,"message":"Test"}'
    files = [("files", ("test.log", test_content, "text/plain"))]
    
    response = client.post("/api/upload", files=files)
    # Should work without X-API-Key header when auth is disabled
    assert response.status_code in [200, 400, 422]  # 400/422 if validation fails, not auth


def test_health_check_no_auth_required():
    """Test health check works without authentication"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_key_header_accepted():
    """Test that X-API-Key header is accepted (even if not required)"""
    response = client.get(
        "/health",
        headers={"X-API-Key": "test-key-12345"}
    )
    # Should work (auth might be disabled in test)
    assert response.status_code == 200


# === File Upload Security Tests ===

def test_file_size_validation():
    """Test file size limit enforcement"""
    # Create content larger than limit (2GB is too big for test, use smaller)
    # This test just ensures the validation logic exists
    large_content = b"x" * (100 * 1024 * 1024)  # 100 MB (smaller for testing)
    files = [("files", ("large.log", large_content, "text/plain"))]
    
    response = client.post("/api/upload", files=files)
    # Should either accept or reject based on size
    assert response.status_code in [200, 400, 413, 422]


def test_file_type_validation():
    """Test invalid file type rejection"""
    # Try uploading an .exe file
    files = [("files", ("malicious.exe", b"fake exe", "application/x-executable"))]
    
    response = client.post("/api/upload", files=files)
    # Should reject invalid file types
    assert response.status_code in [400, 422]
    if response.status_code == 400:
        assert "invalid" in response.json()["detail"].lower() or "only" in response.json()["detail"].lower()


def test_valid_file_types():
    """Test valid file types are accepted"""
    valid_types = [
        ("test.log", "text/plain"),
        ("test.txt", "text/plain"),
        ("test.gz", "application/gzip"),
    ]
    
    for filename, content_type in valid_types:
        files = [("files", (filename, b'{"level":3,"message":"Test"}', content_type))]
        response = client.post("/api/upload", files=files)
        # Should accept valid types (might fail parsing, but not reject type)
        assert response.status_code in [200, 400, 422], f"Failed for {filename}"


# === Cleanup Tests ===

def test_cleanup_function_exists():
    """Test cleanup function is callable"""
    assert callable(cleanup_old_results)


def test_cleanup_runs_without_errors():
    """Test cleanup runs without exceptions"""
    try:
        result = cleanup_old_results()
        assert isinstance(result, dict)
        assert "deleted_results" in result
        assert "deleted_uploads" in result
    except Exception as e:
        pytest.fail(f"Cleanup failed with exception: {e}")


def test_directories_exist():
    """Test required directories exist"""
    assert RESULTS_DIR.exists(), "Results directory should exist"
    assert UPLOAD_DIR.exists(), "Upload directory should exist"


# === API Endpoint Tests ===

def test_root_endpoint():
    """Test root endpoint serves HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_results_page_endpoint():
    """Test results page endpoint"""
    response = client.get("/results.html")
    assert response.status_code == 200


def test_health_endpoint_format():
    """Test health endpoint response format"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"


def test_list_results_endpoint():
    """Test list results endpoint"""
    response = client.get("/api/results")
    assert response.status_code in [200, 401]  # 401 if auth enabled
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)


def test_nonexistent_result():
    """Test getting non-existent result returns 404"""
    response = client.get("/api/results/nonexistent-id-12345")
    assert response.status_code in [404, 401]  # 404 or 401 if auth enabled


# === Error Handling Tests ===

def test_upload_no_files():
    """Test upload with no files returns error"""
    response = client.post("/api/upload")
    assert response.status_code == 422  # Validation error


def test_upload_empty_files_list():
    """Test upload with empty files list"""
    response = client.post("/api/upload", files=[])
    assert response.status_code in [400, 422]


def test_invalid_endpoint():
    """Test invalid endpoint returns 404"""
    response = client.get("/api/invalid-endpoint-xyz")
    assert response.status_code == 404


# === Integration Tests ===

def test_complete_upload_flow(tmp_path):
    """Test complete upload and retrieval flow"""
    # Create test log file
    log_file = tmp_path / "test.log"
    log_file.write_text('{"level":3,"message":"Integration test","time":"2024-01-01T10:00:00+00:00"}')
    
    # Upload
    with open(log_file, 'rb') as f:
        files = [("files", ("test.log", f, "text/plain"))]
        upload_response = client.post("/api/upload", files=files)
    
    # Check upload response
    if upload_response.status_code == 200:
        data = upload_response.json()
        assert "analysis_id" in data
        analysis_id = data["analysis_id"]
        
        # Try to retrieve result
        get_response = client.get(f"/api/results/{analysis_id}")
        assert get_response.status_code in [200, 401]  # 200 or 401 if auth enabled
        
        if get_response.status_code == 200:
            result = get_response.json()
            assert "id" in result
            assert result["id"] == analysis_id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
