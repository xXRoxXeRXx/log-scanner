"""
Tests for parser integration with web backend
"""

import pytest
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.web_parser import analyze_log_files, _mock_analysis


def test_mock_analysis_empty():
    """Test mock analysis with no files"""
    result = _mock_analysis([])
    assert result["status"] == "completed"
    assert result["file_count"] == 0
    assert result["total_entries"] == 0


def test_mock_analysis_single_file(tmp_path):
    """Test mock analysis with single file"""
    log_file = tmp_path / "test.log"
    log_file.write_text("Line 1\nLine 2\nLine 3\n")
    
    result = _mock_analysis([log_file])
    assert result["status"] == "completed"
    assert result["file_count"] == 1
    assert result["total_entries"] == 3  # 3 lines


def test_mock_analysis_multiple_files(tmp_path):
    """Test mock analysis with multiple files"""
    log_file1 = tmp_path / "test1.log"
    log_file2 = tmp_path / "test2.log"
    log_file1.write_text("Line 1\nLine 2\n")
    log_file2.write_text("Line 3\nLine 4\nLine 5\n")
    
    result = _mock_analysis([log_file1, log_file2])
    assert result["status"] == "completed"
    assert result["file_count"] == 2
    assert result["total_entries"] == 5  # 2 + 3 lines


def test_analyze_log_files_function_exists():
    """Test that analyze_log_files function exists"""
    assert callable(analyze_log_files)


def test_analyze_log_files_empty():
    """Test analyze_log_files with empty list"""
    result = analyze_log_files([])
    assert "status" in result
    assert "file_count" in result
    assert result["file_count"] == 0


def test_analyze_log_files_with_json_log(tmp_path):
    """Test analyze_log_files with JSON log file"""
    log_file = tmp_path / "nextcloud.log"
    log_file.write_text("""
{"reqId":"abc123","level":3,"time":"2024-01-01T10:00:00+00:00","message":"Test error","app":"files"}
{"reqId":"def456","level":2,"time":"2024-01-01T10:00:01+00:00","message":"Test warning","app":"dav"}
    """.strip())
    
    result = analyze_log_files([log_file])
    
    assert result["status"] in ["completed", "failed"]
    assert result["file_count"] == 1
    assert "categories" in result
    assert "entries" in result


def test_analyze_log_files_with_server_log(tmp_path):
    """Test with filename containing 'server'"""
    log_file = tmp_path / "server.log"
    log_file.write_text('{"level":3,"message":"Server error"}')
    
    result = analyze_log_files([log_file])
    
    assert result["file_count"] == 1
    assert "categories" in result


def test_analyze_log_files_with_client_log(tmp_path):
    """Test with filename containing 'client'"""
    log_file = tmp_path / "client.log"
    log_file.write_text("Some client log content")
    
    result = analyze_log_files([log_file])
    
    assert result["file_count"] == 1


def test_analyze_log_files_categories_structure(tmp_path):
    """Test that result has expected categories"""
    log_file = tmp_path / "test.log"
    log_file.write_text('{"level":3,"message":"Test"}')
    
    result = analyze_log_files([log_file])
    
    if result["status"] == "completed":
        categories = result["categories"]
        # New functional categories (9 total)
        expected_keys = [
            "authentication", "file_sync", "storage", "database",
            "security", "apps", "background_jobs", "php_runtime", "system"
        ]
        
        for key in expected_keys:
            assert key in categories
            assert isinstance(categories[key], int)
            assert categories[key] >= 0


def test_analyze_log_files_entries_structure(tmp_path):
    """Test that entries have expected structure"""
    log_file = tmp_path / "test.log"
    log_file.write_text('{"level":3,"message":"Test error"}')
    
    result = analyze_log_files([log_file])
    
    if result["status"] == "completed" and len(result["entries"]) > 0:
        entry = result["entries"][0]
        
        # Check expected fields
        assert "time" in entry
        assert "type" in entry
        assert "message" in entry
        assert "category" in entry


def test_analyze_log_files_error_handling(tmp_path):
    """Test error handling with non-existent file"""
    non_existent = tmp_path / "nonexistent.log"
    
    result = analyze_log_files([non_existent])
    
    # Should handle gracefully, either failed status or empty result
    assert "status" in result
    assert result["status"] in ["completed", "failed"]


def test_analyze_log_files_limit_entries(tmp_path):
    """Test that all entries are returned (no artificial limit on entries array)"""
    log_file = tmp_path / "large.log"
    
    # Create log with many entries
    lines = []
    for i in range(300):
        lines.append(f'{{"level":3,"message":"Error {i}"}}')
    
    log_file.write_text("\n".join(lines))
    
    result = analyze_log_files([log_file])
    
    if result["status"] == "completed":
        # All entries should be returned (no limit on entries array)
        # Categories may have limits (10000 per category), but entries array has no limit
        assert len(result["entries"]) == 300, f"Expected 300 entries, got {len(result['entries'])}"
        assert result["total_entries"] == 300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
