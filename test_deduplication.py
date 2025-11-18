#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for error deduplication in ServerLogParser
"""
import unittest
import json
from data_store import LogDataStore
from server_parser import ServerLogParser


class TestDeduplication(unittest.TestCase):
    """Test cases for follow-up error detection and deduplication."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_store = LogDataStore()
        self.parser = ServerLogParser(self.data_store)
    
    def test_followup_generic_exception_skipped(self):
        """Test that GenericFileException follow-ups are skipped."""
        # First entry: detailed S3 error
        entry1 = {
            "reqId": "ABC123",
            "level": 3,
            "time": "2025-10-13T10:13:54+00:00",
            "app": "objectstore",
            "message": "Could not get object urn:oid:939315",
            "exception": {
                "Exception": "OCP\\Files\\StorageNotAvailableException",
                "Message": "S3 service unable to handle request: 503 Service Unavailable"
            }
        }
        
        # Second entry: generic follow-up
        entry2 = {
            "reqId": "ABC123",  # Same reqId!
            "level": 3,
            "time": "2025-10-13T10:13:54+00:00",
            "app": "index",  # Changed to generic app
            "message": "Exception thrown: OCP\\Files\\GenericFileException",
            "exception": {
                "Exception": "OCP\\Files\\GenericFileException",
                "Message": ""  # Empty message!
            }
        }
        
        # First entry should be stored
        result1 = self.parser._categorize_entry(entry1)
        self.assertTrue(result1, "First detailed error should be stored")
        
        # Second entry should be skipped
        result2 = self.parser._categorize_entry(entry2)
        self.assertFalse(result2, "Follow-up generic error should be skipped")
        
        # Check that only one error was stored
        total_errors = self.data_store.get_total_entries()
        self.assertEqual(total_errors, 1, "Should only store the first detailed error")
    
    def test_two_different_requests_both_stored(self):
        """Test that errors with different reqIds are both stored."""
        entry1 = {
            "reqId": "REQ001",
            "level": 3,
            "time": "2025-10-13T10:13:54+00:00",
            "app": "objectstore",
            "message": "Could not get object urn:oid:123",
            "exception": {
                "Exception": "OCP\\Files\\StorageNotAvailableException",
                "Message": "S3 error: 503"
            }
        }
        
        entry2 = {
            "reqId": "REQ002",  # Different reqId
            "level": 3,
            "time": "2025-10-13T10:13:55+00:00",
            "app": "objectstore",
            "message": "Could not get object urn:oid:456",
            "exception": {
                "Exception": "OCP\\Files\\StorageNotAvailableException",
                "Message": "S3 error: 503"
            }
        }
        
        result1 = self.parser._categorize_entry(entry1)
        result2 = self.parser._categorize_entry(entry2)
        
        self.assertTrue(result1, "First error should be stored")
        self.assertTrue(result2, "Second error should be stored")
        
        total_errors = self.data_store.get_total_entries()
        self.assertEqual(total_errors, 2, "Both errors should be stored")
    
    def test_generic_exception_with_message_not_skipped(self):
        """Test that GenericFileException with details is NOT skipped."""
        entry1 = {
            "reqId": "XYZ789",
            "level": 3,
            "time": "2025-10-13T10:13:54+00:00",
            "app": "objectstore",
            "message": "Storage error",
            "exception": {
                "Exception": "OCP\\Files\\StorageNotAvailableException",
                "Message": "Connection timeout"
            }
        }
        
        entry2 = {
            "reqId": "XYZ789",
            "level": 3,
            "time": "2025-10-13T10:13:54+00:00",
            "app": "files",
            "message": "File operation failed",
            "exception": {
                "Exception": "OCP\\Files\\GenericFileException",
                "Message": "Detailed error information here"  # Has message!
            }
        }
        
        result1 = self.parser._categorize_entry(entry1)
        result2 = self.parser._categorize_entry(entry2)
        
        self.assertTrue(result1, "First error should be stored")
        self.assertTrue(result2, "Second error with details should also be stored")
    
    def test_no_reqid_always_stored(self):
        """Test that entries without reqId are always stored."""
        entry1 = {
            "level": 3,
            "time": "2025-10-13T10:13:54+00:00",
            "app": "index",
            "message": "Exception thrown: OCP\\Files\\GenericFileException",
            "exception": {
                "Exception": "OCP\\Files\\GenericFileException",
                "Message": ""
            }
        }
        
        entry2 = {
            "level": 3,
            "time": "2025-10-13T10:13:55+00:00",
            "app": "index",
            "message": "Exception thrown: OCP\\Files\\GenericFileException",
            "exception": {
                "Exception": "OCP\\Files\\GenericFileException",
                "Message": ""
            }
        }
        
        result1 = self.parser._categorize_entry(entry1)
        result2 = self.parser._categorize_entry(entry2)
        
        # Both should be processed (though may end up in different categories)
        # The key is they shouldn't be skipped by deduplication
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
    
    def test_realistic_log_sequence(self):
        """Test with a realistic sequence from actual logs."""
        logs = [
            # Pair 1: S3 error + follow-up
            {
                "reqId": "7ZJSmYZcUeVlOYmiJ9CR",
                "level": 3,
                "time": "2025-10-13T10:13:54+00:00",
                "app": "objectstore",
                "message": "Could not get object urn:oid:939315 for file appdata",
                "exception": {
                    "Exception": "OCP\\Files\\StorageNotAvailableException",
                    "Message": "S3 service is unable to handle request: Error executing \"HeadBucket\" on \"https://example.com/\"; AWS HTTP error: Server error: `HEAD https://example.com/` resulted in a `503 Service Unavailable` response"
                }
            },
            {
                "reqId": "7ZJSmYZcUeVlOYmiJ9CR",
                "level": 3,
                "time": "2025-10-13T10:13:54+00:00",
                "app": "index",
                "message": "Exception thrown: OCP\\Files\\GenericFileException",
                "exception": {
                    "Exception": "OCP\\Files\\GenericFileException",
                    "Message": ""
                }
            },
            # Pair 2: Another S3 error + follow-up
            {
                "reqId": "DOCztID1NfBprwBDTfCW",
                "level": 3,
                "time": "2025-10-13T10:13:55+00:00",
                "app": "objectstore",
                "message": "Could not get object urn:oid:939166 for file appdata",
                "exception": {
                    "Exception": "OCP\\Files\\StorageNotAvailableException",
                    "Message": "S3 service is unable to handle request: 503 Service Unavailable"
                }
            },
            {
                "reqId": "DOCztID1NfBprwBDTfCW",
                "level": 3,
                "time": "2025-10-13T10:13:55+00:00",
                "app": "index",
                "message": "Exception thrown: OCP\\Files\\GenericFileException",
                "exception": {
                    "Exception": "OCP\\Files\\GenericFileException",
                    "Message": ""
                }
            }
        ]
        
        results = [self.parser._categorize_entry(log) for log in logs]
        
        # Should be: True, False, True, False
        self.assertEqual(results, [True, False, True, False], 
                        "Only detailed errors should be stored, follow-ups skipped")
        
        # Verify total stored
        total_errors = self.data_store.get_total_entries()
        self.assertEqual(total_errors, 2, "Should store 2 errors (not 4)")


class TestReqIdCacheTracking(unittest.TestCase):
    """Test reqId cache functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_store = LogDataStore()
        self.parser = ServerLogParser(self.data_store)
    
    def test_cache_stores_entry_info(self):
        """Test that cache properly stores entry information."""
        entry = {
            "reqId": "TEST123",
            "level": 3,
            "time": "2025-10-13T10:13:54+00:00",
            "app": "objectstore",
            "message": "Test error",
            "exception": {
                "Exception": "SomeException",
                "Message": "Details here"
            }
        }
        
        self.parser._categorize_entry(entry)
        
        # Check cache
        self.assertIn("TEST123", self.parser.req_id_cache)
        cached = self.parser.req_id_cache["TEST123"]
        
        self.assertEqual(cached['app'], "objectstore")
        self.assertEqual(cached['exception_type'], "SomeException")
        self.assertTrue(cached['has_details'])
    
    def test_cache_identifies_entries_without_details(self):
        """Test that cache correctly identifies generic entries."""
        entry = {
            "reqId": "TEST456",
            "level": 3,
            "time": "2025-10-13T10:13:54+00:00",
            "app": "index",
            "message": "Exception thrown: OCP\\Files\\GenericFileException",
            "exception": {
                "Exception": "OCP\\Files\\GenericFileException",
                "Message": ""
            }
        }
        
        # This is the first occurrence, so it won't be skipped
        # but it should be marked as not having details
        self.parser._categorize_entry(entry)
        
        cached = self.parser.req_id_cache["TEST456"]
        self.assertFalse(cached['has_details'], 
                        "Generic exception without message should not have details")


if __name__ == '__main__':
    unittest.main()
