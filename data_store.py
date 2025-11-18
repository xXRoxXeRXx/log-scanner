"""
Log data storage with memory limits and thread-safety
"""
from typing import Dict, List, Any, Optional
from threading import Lock
import logging
from config import MAX_ENTRIES_PER_CATEGORY

logger = logging.getLogger(__name__)


class LogDataStore:
    """
    Thread-safe storage for parsed log entries with configurable memory limits.
    
    Prevents memory overflow by limiting entries per category.
    """
    
    def __init__(self, max_entries_per_category: int = MAX_ENTRIES_PER_CATEGORY):
        """
        Initialize data store with empty categories.
        
        Args:
            max_entries_per_category: Maximum number of entries per category
        """
        self.max_entries = max_entries_per_category
        self._lock = Lock()
        self._data: Dict[str, List[Dict[str, str]]] = {
            # Server categories
            "s3_errors": [],
            "dav_errors": [],
            "objectstore_errors": [],
            "php_errors": [],
            "other_errors": [],
            "server_warnings": [],
            "server_info": [],
            "server_debug": [],
            # Client categories
            "client_events": [],
            "client_errors": []
        }
        self._overflow_counts: Dict[str, int] = {key: 0 for key in self._data.keys()}
    
    def add_entry(self, category: str, entry: Dict[str, str]) -> bool:
        """
        Add entry to specified category with thread-safety.
        
        Args:
            category: Category name (e.g., 's3_errors')
            entry: Dictionary with 'time', 'type', 'msg' keys
            
        Returns:
            True if added, False if limit reached
        """
        with self._lock:
            if category not in self._data:
                logger.warning(f"Unknown category: {category}")
                return False
            
            if len(self._data[category]) >= self.max_entries:
                self._overflow_counts[category] += 1
                if self._overflow_counts[category] == 1:
                    logger.warning(
                        f"Category '{category}' reached limit of {self.max_entries} entries. "
                        f"Additional entries will be discarded."
                    )
                return False
            
            self._data[category].append(entry)
            return True
    
    def get_entries(self, category: str) -> List[Dict[str, str]]:
        """
        Retrieve all entries for a category (thread-safe copy).
        
        Args:
            category: Category name
            
        Returns:
            List of entry dictionaries
        """
        with self._lock:
            return self._data.get(category, []).copy()
    
    def get_count(self, category: str) -> int:
        """
        Get number of entries in category.
        
        Args:
            category: Category name
            
        Returns:
            Number of entries
        """
        with self._lock:
            return len(self._data.get(category, []))
    
    def get_overflow_count(self, category: str) -> int:
        """
        Get number of entries that were discarded due to limit.
        
        Args:
            category: Category name
            
        Returns:
            Number of discarded entries
        """
        with self._lock:
            return self._overflow_counts.get(category, 0)
    
    def clear(self) -> None:
        """Clear all stored data."""
        with self._lock:
            for category in self._data:
                self._data[category].clear()
                self._overflow_counts[category] = 0
            logger.info("Data store cleared")
    
    def get_all_categories(self) -> List[str]:
        """
        Get list of all category names.
        
        Returns:
            List of category names
        """
        return list(self._data.keys())
    
    def get_total_entries(self) -> int:
        """
        Get total number of entries across all categories.
        
        Returns:
            Total entry count
        """
        with self._lock:
            return sum(len(entries) for entries in self._data.values())
    
    def get_statistics(self) -> Dict[str, Dict[str, int]]:
        """
        Get statistics about stored data.
        
        Returns:
            Dictionary with counts and overflow info per category
        """
        with self._lock:
            return {
                category: {
                    'count': len(self._data[category]),
                    'overflow': self._overflow_counts[category]
                }
                for category in self._data
            }
