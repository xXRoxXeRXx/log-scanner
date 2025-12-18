"""
Tests for S3 503 error extraction functionality
"""

import pytest
import json
from pathlib import Path
import tempfile
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from main import extract_s3_errors


# Sample log data with S3 503 errors
SAMPLE_S3_ERROR_LOG = '''
{"reqId":"Rj0KYXgHBYZlFDKKtqfR","level":2,"time":"2025-12-10T22:35:44+00:00","remoteAddr":"100.109.117.136","user":"mr2","app":"PHP","method":"GET","url":"/remote.php/dav/files/mr2/OG_Einsatz/PintschBamag1.zip","message":"fopen(https://ionos-nextcloudbucket-live3-ru599954-14899957.s3-eu-central-2.ionoscloud.com/urn%3Aoid%3A453197): Failed to open stream: HTTP request failed! HTTP/1.1 503 Service Unavailable\\r\\n at /var/www/html/lib/private/Files/ObjectStore/S3ObjectTrait.php#72","userAgent":"rclone/","version":"31.0.6.3","clientReqId":"5a40653f455868e38a81bc4a870aa632","data":{"app":"PHP"}}
{"reqId":"Rj0KYXgHBYZlFDKKtqfR","level":3,"time":"2025-12-10T22:35:44+00:00","remoteAddr":"100.109.117.136","user":"mr2","app":"objectstore","method":"GET","url":"/remote.php/dav/files/mr2/OG_Einsatz/PintschBamag1.zip","message":"Could not get object urn:oid:453197 for file __groupfolders/13/PintschBamag1.zip","userAgent":"rclone/","version":"31.0.6.3","clientReqId":"5a40653f455868e38a81bc4a870aa632","exception":{"Exception":"Exception","Message":"Failed to read object urn:oid:453197","Code":0}}
{"reqId":"foFwwqoCx3shL3UEvj7Z","level":3,"time":"2025-12-10T22:35:45+00:00","remoteAddr":"100.109.117.136","user":"mr2","app":"objectstore","method":"GET","url":"/remote.php/dav/files/mr2/OG_Einsatz/PintschBamag1.zip","message":"Could not get object urn:oid:453197 for file __groupfolders/13/PintschBamag1.zip","userAgent":"rclone/","version":"31.0.6.3","clientReqId":"736a984fdb2fd3d18fabf986194aee08","exception":{"Exception":"Exception","Message":"Failed to read object urn:oid:453197","Code":0}}
{"reqId":"TestEntry","level":3,"time":"2025-12-10T22:35:50+00:00","remoteAddr":"100.109.117.136","user":"testuser","app":"objectstore","method":"GET","url":"/remote.php/dav/files/testuser/Test.jpg","message":"Could not get object urn:oid:999999 for file appdata_oc8vyzlpwnof/preview/c/6/d/3/0/5/6/153001/4032-3024-max.jpg","userAgent":"Mozilla/5.0","version":"31.0.6.3","clientReqId":"test123","exception":{"Exception":"Exception","Message":"Failed to read object urn:oid:999999","Code":0}}
'''


def test_extract_s3_errors_basic():
    """Test basic S3 error extraction"""
    result = extract_s3_errors(SAMPLE_S3_ERROR_LOG)
    
    assert result is not None
    assert "s3_config" in result
    assert "errors" in result
    assert "total_broken_objects" in result
    
    # Should have 2 unique files (PintschBamag1.zip appears 2x, Test.jpg 1x)
    assert result["total_broken_objects"] == 2
    assert len(result["errors"]) == 2


def test_extract_s3_errors_grouping():
    """Test that errors are grouped by filename"""
    result = extract_s3_errors(SAMPLE_S3_ERROR_LOG)
    
    errors = result["errors"]
    
    # Find the PintschBamag1.zip entry
    pintsch_error = next(e for e in errors if "PintschBamag1.zip" in e["file"])
    
    # Should have count of 2 (appears twice in log)
    assert pintsch_error["count"] == 2
    assert pintsch_error["example_oid"] == "urn:oid:453197"
    
    # Find the preview entry
    preview_error = next(e for e in errors if "preview" in e["file"])
    assert preview_error["count"] == 1
    assert preview_error["example_oid"] == "urn:oid:999999"


def test_extract_s3_errors_with_overrides():
    """Test S3 config overrides"""
    result = extract_s3_errors(
        SAMPLE_S3_ERROR_LOG,
        s3_bucket="my-custom-bucket",
        s3_region="us-east-1",
        s3_hostname="s3.amazonaws.com"
    )
    
    config = result["s3_config"]
    assert config["bucket"] == "my-custom-bucket"
    assert config["region"] == "us-east-1"
    assert config["hostname"] == "s3.amazonaws.com"


def test_extract_s3_errors_auto_detect_config():
    """Test automatic S3 config detection from logs"""
    result = extract_s3_errors(SAMPLE_S3_ERROR_LOG)
    
    config = result["s3_config"]
    # Should auto-detect from exception message URL
    assert config["bucket"] == "ionos-nextcloudbucket-live3-ru599954-14899957"
    assert config["hostname"] == "s3-eu-central-2.ionoscloud.com"
    assert config["region"] == "eu-central-2"


def test_extract_s3_errors_empty_log():
    """Test with empty log"""
    result = extract_s3_errors("")
    
    assert result["total_broken_objects"] == 0
    assert len(result["errors"]) == 0


def test_extract_s3_errors_no_s3_errors():
    """Test with log that has no S3 errors"""
    log = '''
    {"reqId":"test","level":1,"time":"2025-12-10T10:00:00+00:00","app":"core","message":"Login successful"}
    {"reqId":"test2","level":2,"time":"2025-12-10T10:01:00+00:00","app":"files","message":"File uploaded"}
    '''
    
    result = extract_s3_errors(log)
    
    assert result["total_broken_objects"] == 0
    assert len(result["errors"]) == 0


def test_extract_s3_errors_malformed_json():
    """Test with malformed JSON lines (should skip them)"""
    log = '''
    {"valid": "json"}
    this is not json
    {"reqId":"test","level":3,"time":"2025-12-10T22:35:44+00:00","app":"objectstore","message":"Could not get object urn:oid:12345 for file test.txt"}
    another invalid line
    '''
    
    result = extract_s3_errors(log)
    
    # Should still extract the one valid S3 error
    assert result["total_broken_objects"] == 1
    assert result["errors"][0]["file"] == "test.txt"
    assert result["errors"][0]["example_oid"] == "urn:oid:12345"


def test_extract_s3_errors_sorting():
    """Test that errors are sorted by count (descending)"""
    # Create log with varying counts
    log = '''
    {"app":"objectstore","message":"Could not get object urn:oid:1 for file fileA.txt","time":"2025-12-10T10:00:00+00:00"}
    {"app":"objectstore","message":"Could not get object urn:oid:2 for file fileB.txt","time":"2025-12-10T10:00:00+00:00"}
    {"app":"objectstore","message":"Could not get object urn:oid:2 for file fileB.txt","time":"2025-12-10T10:00:00+00:00"}
    {"app":"objectstore","message":"Could not get object urn:oid:3 for file fileC.txt","time":"2025-12-10T10:00:00+00:00"}
    {"app":"objectstore","message":"Could not get object urn:oid:3 for file fileC.txt","time":"2025-12-10T10:00:00+00:00"}
    {"app":"objectstore","message":"Could not get object urn:oid:3 for file fileC.txt","time":"2025-12-10T10:00:00+00:00"}
    '''
    
    result = extract_s3_errors(log)
    
    errors = result["errors"]
    
    # Should be sorted by count: fileC (3x), fileB (2x), fileA (1x)
    assert errors[0]["file"] == "fileC.txt"
    assert errors[0]["count"] == 3
    
    assert errors[1]["file"] == "fileB.txt"
    assert errors[1]["count"] == 2
    
    assert errors[2]["file"] == "fileA.txt"
    assert errors[2]["count"] == 1


def test_extract_s3_errors_timestamp_tracking():
    """Test that last timestamp is tracked correctly"""
    log = '''
    {"app":"objectstore","message":"Could not get object urn:oid:1 for file test.txt","time":"2025-12-10T10:00:00+00:00"}
    {"app":"objectstore","message":"Could not get object urn:oid:1 for file test.txt","time":"2025-12-10T12:00:00+00:00"}
    {"app":"objectstore","message":"Could not get object urn:oid:1 for file test.txt","time":"2025-12-10T14:00:00+00:00"}
    '''
    
    result = extract_s3_errors(log)
    
    # Should track the latest timestamp
    assert result["errors"][0]["last_timestamp"] == "2025-12-10T14:00:00+00:00"
    assert result["errors"][0]["count"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
