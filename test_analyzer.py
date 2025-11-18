"""
Unit tests for Nextcloud Log Analyzer
"""
import unittest
import json
import gzip
import os
import tempfile
from data_store import LogDataStore
from server_parser import ServerLogParser
from client_parser import ClientLogParser
from config import open_file, is_gzip_file


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


class TestGzipSupport(unittest.TestCase):
    """Test gzip file support"""
    
    def setUp(self):
        """Create temporary test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.regular_file = os.path.join(self.temp_dir, "test.log")
        self.gzip_file = os.path.join(self.temp_dir, "test.log.gz")
        
        # Create regular file
        with open(self.regular_file, 'w', encoding='utf-8') as f:
            f.write("Line 1\nLine 2\nLine 3\n")
        
        # Create gzip file
        with gzip.open(self.gzip_file, 'wt', encoding='utf-8') as f:
            f.write("Compressed Line 1\nCompressed Line 2\n")
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_is_gzip_file(self):
        """Test gzip file detection"""
        self.assertTrue(is_gzip_file("test.log.gz"))
        self.assertTrue(is_gzip_file("test.log.gzip"))
        self.assertFalse(is_gzip_file("test.log"))
        self.assertFalse(is_gzip_file("test.txt"))
    
    def test_open_regular_file(self):
        """Test opening regular file"""
        with open_file(self.regular_file, 'r') as f:
            content = f.read()
            self.assertIn("Line 1", content)
            self.assertIn("Line 3", content)
    
    def test_open_gzip_file(self):
        """Test opening gzip file"""
        with open_file(self.gzip_file, 'r') as f:
            content = f.read()
            self.assertIn("Compressed Line 1", content)
            self.assertIn("Compressed Line 2", content)
    
    def test_parse_server_log_gz(self):
        """Test parsing compressed server log"""
        store = LogDataStore()
        parser = ServerLogParser(store)
        
        # Create compressed server log
        gz_file = os.path.join(self.temp_dir, "server.log.gz")
        log_entry = {
            "reqId": "test",
            "level": 3,
            "time": "2025-01-01T12:00:00+00:00",
            "app": "PHP",
            "message": "Test error"
        }
        
        with gzip.open(gz_file, 'wt', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Parse compressed file
        with open_file(gz_file, 'r') as f:
            for line in f:
                parser.parse_line(line)
        
        self.assertEqual(store.get_count("php_errors"), 1)


class TestFilters(unittest.TestCase):
    """Test time and user filters"""
    
    def setUp(self):
        """Create test data store with sample data"""
        from datetime import datetime
        self.store = LogDataStore()
        
        # Add test entries with different times and users
        self.store.add_entry("s3_errors", {
            "time": "2025-11-18T10:00:00",
            "type": "HTTP 404",
            "msg": "File not found",
            "user": "alice"
        })
        
        self.store.add_entry("s3_errors", {
            "time": "2025-11-18T12:00:00",
            "type": "HTTP 500",
            "msg": "Server error",
            "user": "bob"
        })
        
        self.store.add_entry("s3_errors", {
            "time": "2025-11-18T14:00:00",
            "type": "HTTP 403",
            "msg": "Forbidden",
            "user": "alice"
        })
    
    def test_no_filter(self):
        """Test getting entries without filters"""
        entries = self.store.get_entries("s3_errors")
        self.assertEqual(len(entries), 3)
    
    def test_time_filter_start(self):
        """Test filtering by start time"""
        from datetime import datetime
        start = datetime(2025, 11, 18, 11, 0, 0)
        self.store.set_time_filter(start, None)
        
        entries = self.store.get_entries("s3_errors")
        self.assertEqual(len(entries), 2)  # 12:00 and 14:00
    
    def test_time_filter_end(self):
        """Test filtering by end time"""
        from datetime import datetime
        end = datetime(2025, 11, 18, 13, 0, 0)
        self.store.set_time_filter(None, end)
        
        entries = self.store.get_entries("s3_errors")
        self.assertEqual(len(entries), 2)  # 10:00 and 12:00
    
    def test_time_filter_range(self):
        """Test filtering by time range"""
        from datetime import datetime
        start = datetime(2025, 11, 18, 11, 0, 0)
        end = datetime(2025, 11, 18, 13, 0, 0)
        self.store.set_time_filter(start, end)
        
        entries = self.store.get_entries("s3_errors")
        self.assertEqual(len(entries), 1)  # Only 12:00
        self.assertEqual(entries[0]["user"], "bob")
    
    def test_user_filter(self):
        """Test filtering by user"""
        self.store.set_user_filter("alice")
        
        entries = self.store.get_entries("s3_errors")
        self.assertEqual(len(entries), 2)  # alice has 2 entries
        self.assertTrue(all(e["user"] == "alice" for e in entries))
    
    def test_combined_filters(self):
        """Test combining time and user filters"""
        from datetime import datetime
        start = datetime(2025, 11, 18, 11, 0, 0)
        self.store.set_time_filter(start, None)
        self.store.set_user_filter("alice")
        
        entries = self.store.get_entries("s3_errors")
        self.assertEqual(len(entries), 1)  # Only alice at 14:00
        self.assertEqual(entries[0]["time"], "2025-11-18T14:00:00")
    
    def test_clear_filters(self):
        """Test clearing all filters"""
        from datetime import datetime
        self.store.set_time_filter(datetime(2025, 11, 18, 11, 0, 0), None)
        self.store.set_user_filter("alice")
        self.store.clear_filters()
        
        entries = self.store.get_entries("s3_errors")
        self.assertEqual(len(entries), 3)  # All entries visible again
    
    def test_get_users(self):
        """Test extracting unique users"""
        users = self.store.get_users()
        self.assertEqual(set(users), {"alice", "bob"})
        self.assertEqual(len(users), 2)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()

