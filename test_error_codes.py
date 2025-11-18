"""
Unit tests for error code extraction
"""
import unittest
import json
from data_store import LogDataStore
from server_parser import ServerLogParser
from client_parser import ClientLogParser


class TestErrorCodeExtraction(unittest.TestCase):
    """Test error code extraction from various log formats"""
    
    def setUp(self):
        """Create test parsers"""
        self.data_store = LogDataStore()
        self.server_parser = ServerLogParser(self.data_store)
        self.client_parser = ClientLogParser(self.data_store)
    
    def test_extract_http_401_from_server_log(self):
        """Test extracting HTTP 401 from server log"""
        log_data = {
            "level": 2,
            "time": "2025-10-02T13:07:24+00:00",
            "app": "integration_openai",
            "message": "Client error: `GET https://example.com/api` resulted in a `401 Unauthorized` response",
            "user": "testuser"
        }
        
        error_code = self.server_parser._extract_error_code(log_data, log_data['message'])
        self.assertEqual(error_code, "401")
    
    def test_extract_http_504_from_server_log(self):
        """Test extracting HTTP 504 from server log"""
        log_data = {
            "level": 3,
            "time": "2025-10-02T13:07:24+00:00",
            "app": "core",
            "message": "POST request resulted in a `504 Gateway Timeout` response",
            "user": "admin"
        }
        
        error_code = self.server_parser._extract_error_code(log_data, log_data['message'])
        self.assertEqual(error_code, "504")
    
    def test_extract_custom_error_code(self):
        """Test extracting custom error code from message"""
        log_data = {
            "level": 2,
            "time": "2025-10-02T13:07:24+00:00",
            "app": "integration_openai",
            "message": '{"errorCode":"paas-auth-1","message":"Unauthorized"}',
            "user": "testuser"
        }
        
        error_code = self.server_parser._extract_error_code(log_data, log_data['message'])
        self.assertEqual(error_code, "paas-auth-1")
    
    def test_extract_exception_code(self):
        """Test extracting code from exception field"""
        log_data = {
            "level": 3,
            "time": "2025-10-02T13:07:24+00:00",
            "app": "core",
            "message": "Database connection failed",
            "user": "system",
            "exception": {
                "Exception": "PDOException",
                "Code": 1045,
                "Message": "Access denied"
            }
        }
        
        error_code = self.server_parser._extract_error_code(log_data, log_data['message'])
        self.assertEqual(error_code, "1045")
    
    def test_no_error_code(self):
        """Test log entry without error code"""
        log_data = {
            "level": 1,
            "time": "2025-10-02T13:07:24+00:00",
            "app": "core",
            "message": "User logged in successfully",
            "user": "testuser"
        }
        
        error_code = self.server_parser._extract_error_code(log_data, log_data['message'])
        self.assertIsNone(error_code)
    
    def test_client_http_error_extraction(self):
        """Test extracting HTTP error from client log"""
        message = "Network request failed: HTTP 403 Forbidden"
        error_code = self.client_parser._extract_error_code(message)
        self.assertEqual(error_code, "403")
    
    def test_client_network_error_extraction(self):
        """Test extracting QNetworkReply error from client log"""
        message = "Connection failed with QNetworkReply::NetworkError(5)"
        error_code = self.client_parser._extract_error_code(message)
        self.assertEqual(error_code, "NET_5")
    
    def test_client_no_error_code(self):
        """Test client log without error code"""
        message = "Sync completed successfully"
        error_code = self.client_parser._extract_error_code(message)
        self.assertIsNone(error_code)
    
    def test_server_log_with_error_code_field(self):
        """Test log with explicit error_code field"""
        log_data = {
            "level": 2,
            "time": "2025-10-02T13:07:24+00:00",
            "app": "monitor",
            "message": "Service timeout",
            "user": "system",
            "error_code": "http_504_timeout"
        }
        
        error_code = self.server_parser._extract_error_code(log_data, log_data['message'])
        self.assertEqual(error_code, "http_504_timeout")
    
    def test_full_server_log_integration(self):
        """Test full server log parsing with error code"""
        log_line = json.dumps({
            "reqId": "test123",
            "level": 2,
            "time": "2025-10-02T13:07:24+00:00",
            "app": "integration_openai",
            "message": "API request failed: `POST https://api.example.com` resulted in a `401 Unauthorized` response",
            "user": "daniele"
        })
        
        # Parse the log
        self.data_store.clear()
        self.server_parser.parse_line(log_line)
        
        # Check if entry was stored with error code
        entries = self.data_store.get_entries("server_warnings")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].get("error_code"), "401")
        self.assertEqual(entries[0].get("user"), "daniele")


if __name__ == '__main__':
    unittest.main()
