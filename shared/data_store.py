"""
Log data storage with memory limits and thread-safety
"""
from typing import Dict, List, Any, Optional, Callable
from threading import Lock
from datetime import datetime
import logging
from config import MAX_ENTRIES_PER_CATEGORY, FUNCTIONAL_CATEGORIES

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
        
        # Initialize functional categories from config
        self._data: Dict[str, List[Dict[str, str]]] = {
            category: [] for category in FUNCTIONAL_CATEGORIES.keys()
        }
        
        # Add client categories (not in FUNCTIONAL_CATEGORIES as they're client-side)
        self._data["client_events"] = []
        self._data["client_errors"] = []
        
        self._overflow_counts: Dict[str, int] = {key: 0 for key in self._data.keys()}
        
        # Filters
        self._time_filter_start: Optional[datetime] = None
        self._time_filter_end: Optional[datetime] = None
        self._user_filter: Optional[str] = None
        self._users: set = set()  # Track all unique users
    
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
            
            # Track users if present
            if 'user' in entry and entry['user']:
                self._users.add(entry['user'])
            
            return True
    
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
    
    def set_time_filter(self, start: Optional[datetime], end: Optional[datetime]) -> None:
        """
        Set time range filter.
        
        Args:
            start: Start datetime (inclusive) or None for no start limit
            end: End datetime (inclusive) or None for no end limit
        """
        with self._lock:
            self._time_filter_start = start
            self._time_filter_end = end
            logger.info(f"Time filter set: {start} to {end}")
    
    def set_user_filter(self, user: Optional[str]) -> None:
        """
        Set user filter.
        
        Args:
            user: Username to filter by, or None to show all users
        """
        with self._lock:
            self._user_filter = user
            logger.info(f"User filter set: {user}")
    
    def clear_filters(self) -> None:
        """Clear all active filters."""
        with self._lock:
            self._time_filter_start = None
            self._time_filter_end = None
            self._user_filter = None
            logger.info("Filters cleared")
    
    def get_users(self) -> List[str]:
        """
        Get list of all unique users found in logs.
        
        Returns:
            Sorted list of usernames
        """
        with self._lock:
            return sorted(self._users)
    
    def _matches_filters(self, entry: Dict[str, str]) -> bool:
        """
        Check if entry matches current filters.
        
        Args:
            entry: Log entry to check
            
        Returns:
            True if entry passes all active filters
        """
        # Time filter
        if self._time_filter_start or self._time_filter_end:
            entry_time = self._parse_timestamp(entry.get('time', ''))
            if entry_time:
                if self._time_filter_start and entry_time < self._time_filter_start:
                    return False
                if self._time_filter_end and entry_time > self._time_filter_end:
                    return False
            else:
                # If we can't parse time and filter is active, exclude entry
                return False
        
        # User filter
        if self._user_filter:
            entry_user = entry.get('user', '')
            if entry_user != self._user_filter:
                return False
        
        return True
    
    def _parse_timestamp(self, time_str: str) -> Optional[datetime]:
        """
        Parse timestamp from various formats.
        
        Args:
            time_str: Timestamp string
            
        Returns:
            datetime object or None if parsing fails
        """
        if not time_str:
            return None
        
        # Try ISO format (server logs): 2025-11-18T12:34:56+00:00
        formats = [
            '%Y-%m-%dT%H:%M:%S%z',  # With timezone
            '%Y-%m-%dT%H:%M:%S',     # Without timezone
            '%Y-%m-%d %H:%M:%S',     # Space separator
            '%Y-%m-%d %H:%M:%S:%f',  # Client format with milliseconds
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str.split('.')[0].split('+')[0], fmt.replace('%z', ''))
            except (ValueError, IndexError):
                continue
        
        return None
    
    def get_entries(self, category: str) -> List[Dict[str, str]]:
        """
        Get entries from category, applying active filters.
        
        Args:
            category: Category name
            
        Returns:
            List of entries (filtered if filters are active)
        """
        with self._lock:
            if category not in self._data:
                return []
            
            entries = self._data[category]
            
            # Apply filters if any are active
            if self._time_filter_start or self._time_filter_end or self._user_filter:
                entries = [e for e in entries if self._matches_filters(e)]
            
            return entries.copy()
    
    def get_count(self, category: str) -> int:
        """
        Get number of entries in category (after applying filters).
        
        Args:
            category: Category name
            
        Returns:
            Number of entries
        """
        return len(self.get_entries(category))

