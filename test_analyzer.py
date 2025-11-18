"""
Unit tests for Nextcloud Log Analyzer
"""
import unittest
import json
from data_store import LogDataStore
from server_parser import ServerLogParser
from client_parser import ClientLogParser


class TestLogDataStore(unittest.TestCase):
    """Test LogDataStore functionality"""
    
    def setUp(self):
        """Create test data store with small limit"""
        self.store = LogDataStore(max_entries_per_category=3)
    
    def test_add_entry(self):
        """Test adding entries"""
        entry = {"time": "2025-01-01", "type": "Test", "msg": "Test message"}
        result = self.store.add_entry("s3_errors", entry)
        self.assertTrue(result)
        self.assertEqual(self.store.get_count("s3_errors"), 1)
    
    def test_limit_enforcement(self):
        """Test memory limit enforcement"""
        for i in range(5):
            entry = {"time": f"2025-01-0{i}", "type": "Test", "msg": f"Msg {i}"}
            self.store.add_entry("s3_errors", entry)
        
        # Should only have 3 entries (limit)
        self.assertEqual(self.store.get_count("s3_errors"), 3)
        # Should have 2 overflow
        self.assertEqual(self.store.get_overflow_count("s3_errors"), 2)
    
    def test_clear(self):
        """Test clearing data"""
        entry = {"time": "2025-01-01", "type": "Test", "msg": "Test"}
        self.store.add_entry("s3_errors", entry)
        self.store.clear()
        self.assertEqual(self.store.get_total_entries(), 0)
    
    def test_invalid_category(self):
        """Test adding to invalid category"""
        entry = {"time": "2025-01-01", "type": "Test", "msg": "Test"}
        result = self.store.add_entry("invalid_category", entry)
        self.assertFalse(result)


class TestServerLogParser(unittest.TestCase):
    """Test ServerLogParser functionality"""
    
    def setUp(self):
        """Create parser with test data store"""
        self.store = LogDataStore()
        self.parser = ServerLogParser(self.store)
    
    def test_parse_s3_error(self):
        """Test parsing S3 HTTP error"""
        log_line = json.dumps({
            "level": 3,
            "time": "2025-01-01T12:00:00",
            "message": "S3 request failed: HTTP/1.1 404 Not Found",
            "app": "objectstore"
        })
        
        self.parser.parse_line(log_line)
        self.assertEqual(self.store.get_count("s3_errors"), 1)
        
        entries = self.store.get_entries("s3_errors")
        self.assertEqual(entries[0]["type"], "HTTP 404")
    
    def test_parse_dav_error(self):
        """Test parsing WebDAV error"""
        log_line = json.dumps({
            "level": 3,
            "time": "2025-01-01T12:00:00",
            "message": "Sabre\\DAV\\Exception",
            "app": "webdav"
        })
        
        self.parser.parse_line(log_line)
        self.assertEqual(self.store.get_count("dav_errors"), 1)
    
    def test_parse_php_error(self):
        """Test parsing PHP error"""
        log_line = json.dumps({
            "level": 3,
            "time": "2025-01-01T12:00:00",
            "message": "Fatal error in script.php",
            "app": "PHP"
        })
        
        self.parser.parse_line(log_line)
        self.assertEqual(self.store.get_count("php_errors"), 1)
    
    def test_parse_warning(self):
        """Test parsing warning level"""
        log_line = json.dumps({
            "level": 2,
            "time": "2025-01-01T12:00:00",
            "message": "Deprecated function used",
            "app": "core"
        })
        
        self.parser.parse_line(log_line)
        self.assertEqual(self.store.get_count("server_warnings"), 1)
    
    def test_invalid_json(self):
        """Test handling invalid JSON"""
        result = self.parser.parse_line("not a json string")
        self.assertFalse(result)


class TestClientLogParser(unittest.TestCase):
    """Test ClientLogParser functionality"""
    
    def setUp(self):
        """Create parser with test data store"""
        self.store = LogDataStore()
        self.parser = ClientLogParser(self.store)
    
    def test_parse_sync_start(self):
        """Test parsing sync start event"""
        log_line = "2025-01-01 12:00:00:000 [ info sync.engine ]: >========== Sync started for folder [/Documents]"
        
        self.parser.parse_line(log_line)
        self.assertEqual(self.store.get_count("client_events"), 1)
        
        entries = self.store.get_entries("client_events")
        self.assertIn("Sync gestartet", entries[0]["type"])
    
    def test_parse_sync_end(self):
        """Test parsing sync end event"""
        log_line = "2025-01-01 12:00:01:000 [ info sync.engine ]: <========== Sync finished for folder [/Documents]"
        
        self.parser.parse_line(log_line)
        self.assertEqual(self.store.get_count("client_events"), 1)
    
    def test_parse_error(self):
        """Test parsing error level"""
        log_line = "2025-01-01 12:00:00:000 [ error sync.network ]: Network request error"
        
        self.parser.parse_line(log_line)
        self.assertEqual(self.store.get_count("client_errors"), 1)
    
    def test_parse_upload_progress(self):
        """Test parsing upload progress"""
        log_line = "2025-01-01 12:00:00:000 [ info sync ]: Chunked upload of 10485760 bytes took 5000"
        
        self.parser.parse_line(log_line)
        self.assertEqual(self.store.get_count("client_events"), 1)
        
        entries = self.store.get_entries("client_events")
        self.assertIn("MB", entries[0]["msg"])  # Should format bytes
    
    def test_invalid_line_format(self):
        """Test handling invalid line format"""
        result = self.parser.parse_line("invalid log line format")
        self.assertFalse(result)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
