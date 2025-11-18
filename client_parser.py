"""
Client log parser for text-formatted Nextcloud client logs
"""
from typing import Dict, List, Tuple, Pattern, Optional
import re
import logging
from data_store import LogDataStore
from config import open_file

logger = logging.getLogger(__name__)


class ClientLogParser:
    """
    Parser for Nextcloud client logs in text format.
    
    Extracts sync events, errors, and builds a "story" of client activities.
    """
    
    def __init__(self, data_store: LogDataStore):
        """
        Initialize client log parser.
        
        Args:
            data_store: LogDataStore instance for storing parsed entries
        """
        self.data_store = data_store
        
        # Main log line pattern: 2025-11-11 12:34:56:789 [ level component ]: message
        self.log_line_regex: Pattern = re.compile(
            r'^([\d\-]+ [\d:]+:\d{3})\s+\[\s*(\w+)\s+([\w\d\._\-]+).*?\]:\s+(.*)$'
        )
        
        # Story patterns: (regex, event_name)
        self.story_patterns: List[Tuple[Pattern, str]] = [
            (re.compile(r'>========== Sync started for folder \[(.*?)\]'), "Sync gestartet"),
            (re.compile(r'<========== Sync finished for folder \[(.*?)\]'), "Sync beendet"),
            (re.compile(r'Chunked upload of (\d+) bytes took (\d+)'), "Upload Fortschritt"),
            (re.compile(r'Compare etag .* -> CHANGED'), "Server-Änderung erkannt (ETag)"),
            (re.compile(r'Opening file details view in tray for\s+"?(.*?)"?$'), "Benutzer: Datei-Details geöffnet"),
            (re.compile(r'Error transferring (.*?) - server replied: (.*)'), "Übertragungsfehler"),
            (re.compile(r'Network request error'), "Netzwerkfehler"),
            (re.compile(r'discovered "(.*?)" .* OCC::SyncFileItem::Up'), "Datei zum Upload gefunden"),
            (re.compile(r'discovered "(.*?)" .* OCC::SyncFileItem::Down'), "Datei zum Download gefunden"),
            (re.compile(r'DELETE .* FINISHED WITH STATUS "OK"'), "Löschen erfolgreich")
        ]
        
        logger.info("ClientLogParser initialized")
    
    def parse_line(self, line: str, source_file: str = "", line_number: int = 0) -> bool:
        """
        Parse a single text log line.
        
        Args:
            line: Raw log line string
            source_file: Name of the source log file
            line_number: Line number in the source file
            
        Returns:
            True if successfully parsed, False otherwise
        """
        match = self.log_line_regex.match(line)
        if not match:
            return False
        
        try:
            timestamp, level_str, component, message = match.groups()
            
            # Check for errors/warnings
            if self._is_error_level(level_str, message):
                self._store_error(timestamp, message, source_file, line_number)
            
            # Check for story events
            self._check_story_patterns(timestamp, message, source_file, line_number)
            
            return True
            
        except Exception as e:
            logger.error(f"Error parsing client log line: {e}")
            return False
    
    def _is_error_level(self, level: str, message: str) -> bool:
        """
        Check if log entry is an error or warning.
        
        Args:
            level: Log level string (info, warning, error, etc.)
            message: Log message
            
        Returns:
            True if error/warning level
        """
        return (
            level.lower() in ['warning', 'error', 'fatal', 'critical'] or
            "Network request error" in message or
            "Error transferring" in message
        )
    
    def _store_error(self, timestamp: str, message: str, source_file: str = "", line_number: int = 0) -> None:
        """
        Store error entry in data store.
        
        Args:
            timestamp: Log timestamp
            message: Error message
            source_file: Name of the source log file
            line_number: Line number in the source file
        """
        # Extract error code from client message
        error_code = self._extract_error_code(message)
        
        self.data_store.add_entry("client_errors", {
            "time": timestamp,
            "type": "Client Error",
            "msg": message,
            "error_code": error_code,
            "source_file": source_file,
            "line_number": line_number
        })
    
    def _extract_error_code(self, message: str) -> Optional[str]:
        """
        Extract error code from client log message.
        
        Args:
            message: Log message
            
        Returns:
            Error code or None
        """
        import re
        
        # Check for HTTP status codes
        http_match = re.search(r'HTTP[/\s]+(\d{3})', message, re.IGNORECASE)
        if http_match:
            return http_match.group(1)
        
        # Check for QNetworkReply errors
        network_error = re.search(r'QNetworkReply::NetworkError\((\d+)\)', message)
        if network_error:
            return f"NET_{network_error.group(1)}"
        
        # Check for error codes in format "Error: XXX" or "error code: XXX"
        error_match = re.search(r'error\s*(?:code)?[:\s]+([A-Za-z0-9_-]+)', message, re.IGNORECASE)
        if error_match:
            code = error_match.group(1)
            if len(code) < 30:
                return code
        
        return None
    
    def _check_story_patterns(self, timestamp: str, message: str, source_file: str = "", line_number: int = 0) -> None:
        """
        Check message against story patterns and store matches.
        
        Args:
            timestamp: Log timestamp
            message: Log message
            source_file: Name of the source log file
            line_number: Line number in the source file
        """
        for pattern, event_name in self.story_patterns:
            match = pattern.search(message)
            if match:
                details = self._extract_event_details(match, event_name, message)
                self.data_store.add_entry("client_events", {
                    "time": timestamp,
                    "type": event_name,
                    "msg": details,
                    "source_file": source_file,
                    "line_number": line_number
                })
                break  # Only match first pattern
    
    def _extract_event_details(
        self, 
        match: re.Match, 
        event_name: str, 
        full_message: str
    ) -> str:
        """
        Extract detailed information from pattern match.
        
        Args:
            match: Regex match object
            event_name: Name of the event
            full_message: Complete log message
            
        Returns:
            Formatted event details
        """
        # Special handling for upload progress
        if "Upload Fortschritt" in event_name and match.lastindex and match.lastindex >= 2:
            bytes_str = match.group(1)
            ms_str = match.group(2)
            try:
                mb = int(bytes_str) / (1024 * 1024)
                seconds = int(ms_str) / 1000
                return f"{mb:.2f} MB in {seconds:.1f}s"
            except (ValueError, ZeroDivisionError):
                return full_message
        
        # Extract first capture group if available
        if match.lastindex and match.lastindex >= 1:
            return match.group(1)
        
        # Return full message as fallback
        return full_message
