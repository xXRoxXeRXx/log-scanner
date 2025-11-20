"""
Server log parser for JSON-formatted Nextcloud server logs
"""
from typing import Dict, Any, Optional, Pattern
import re
import urllib.parse
import json
import logging
from data_store import LogDataStore
from config import open_file, FUNCTIONAL_CATEGORIES, APP_CATEGORY_MAPPING

logger = logging.getLogger(__name__)


class ServerLogParser:
    """
    Parser for Nextcloud server logs in JSON format.
    
    Categorizes log entries by type (S3, DAV, PHP, etc.) and severity level.
    """
    
    def __init__(self, data_store: LogDataStore):
        """
        Initialize server log parser.
        
        Args:
            data_store: LogDataStore instance for storing parsed entries
        """
        self.data_store = data_store
        
        # Compile regex patterns for efficient matching
        self.oid_regex: Pattern = re.compile(r'(urn(?:%3A|:)oid(?:%3A|:)[0-9]+)')
        self.http_error_regex: Pattern = re.compile(r'HTTP/[0-9\.]+\s([45][0-9]{2})')
        
        # Cache for tracking request IDs and detecting follow-up errors
        # Maps reqId -> {app, exception_type, has_details}
        self.req_id_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info("ServerLogParser initialized")
    
    def _get_functional_category(self, data: Dict[str, Any], msg: str, app: Optional[str], exception_type: Optional[str]) -> str:
        """
        Determine the functional category based on app, message, and exception.
        
        Implements priority-based detection logic with special routing:
        - WebDAV + S3 keywords → storage (not file_sync)
        - PHP exceptions → php_runtime
        - App-specific routing via APP_CATEGORY_MAPPING
        
        Args:
            data: Full parsed JSON log entry
            msg: Log message string
            app: App name from log entry
            exception_type: Exception class name if present
            
        Returns:
            Category key string (e.g., 'authentication', 'storage')
        """
        msg_lower = msg.lower()
        
        # Priority 1: Authentication & Access (CSRF, login, session, permissions)
        if any(keyword in msg_lower for keyword in ['csrf', 'token check', 'bruteforce', 'password', 'login', 'logout', 'session']):
            return 'authentication'
        if any(keyword in msg_lower for keyword in ['permission', 'forbidden', 'access denied', 'unauthorized', '401', '403']):
            return 'authentication'
        
        # Priority 2: Security Issues (explicit security events)
        if any(keyword in msg_lower for keyword in ['security', 'attack', 'suspicious', 'blocked', 'rate limit']):
            return 'security'
        
        # Priority 3: Storage (S3, ObjectStore) - WITH SPECIAL WEBDAV ROUTING
        # If app=webdav AND S3 keywords → storage (not file_sync)
        if app == 'webdav' and any(keyword in msg_lower for keyword in ['s3', 'objectstore', 'object store', 'nosuchupload', 'bucket']):
            return 'storage'
        
        # Regular S3/ObjectStore detection
        if any(keyword in msg_lower for keyword in ['s3', 'objectstore', 'object store', 'nosuchupload', 'bucket', 'aws']):
            return 'storage'
        
        # Priority 4: Database Issues
        if any(keyword in msg_lower for keyword in ['database', 'mysql', 'postgres', 'sqlite', 'query', 'deadlock', 'db error']):
            return 'database'
        
        # Priority 5: File Sync (WebDAV without S3 keywords)
        if app == 'webdav' or any(keyword in msg_lower for keyword in ['webdav', 'sabre', 'dav', 'sync', 'upload', 'download']):
            return 'file_sync'
        
        # Priority 6: PHP Runtime Errors (TypeError, Undefined Array Key, etc.)
        if exception_type:
            if any(php_error in exception_type for php_error in ['TypeError', 'Error', 'Exception', 'Warning']):
                return 'php_runtime'
        if any(keyword in msg_lower for keyword in ['undefined array key', 'undefined variable', 'undefined offset', 'type error']):
            return 'php_runtime'
        
        # Priority 7: Background Jobs (Cron)
        if any(keyword in msg_lower for keyword in ['cron', 'background job', 'scheduled task']):
            return 'background_jobs'
        
        # Priority 8: App-specific (use mapping)
        if app and app in APP_CATEGORY_MAPPING:
            return APP_CATEGORY_MAPPING[app]
        
        # Priority 9: Apps (generic app errors not covered above)
        if app and app not in ['core', 'no app in context']:
            return 'apps'
        
        # Default: System
        return 'system'
    
    def _get_severity(self, level: int, exception_type: Optional[str], msg: str) -> str:
        """
        Determine severity level based on log level, exception type, and message.
        
        Maps old Level 0-3 to new Critical/High/Medium/Low scale:
        - Critical: Level 3 + NoSuchUpload, S3 failures
        - High: Level 3 + TypeError, CSRF, security issues
        - Medium: Level 2 + undefined array key
        - Low: Level 1, Level 0 (if included)
        
        Args:
            level: Nextcloud log level (0=Debug, 1=Info, 2=Warning, 3=Error)
            exception_type: Exception class name if present
            msg: Log message string
            
        Returns:
            Severity string: 'critical', 'high', 'medium', 'low'
        """
        msg_lower = msg.lower()
        
        # Level 3 (Error) differentiation
        if level == 3:
            # Critical: S3 upload failures, data loss risks
            if any(keyword in msg_lower for keyword in ['nosuchupload', 's3 error', 'object not found', 'bucket']):
                return 'critical'
            
            # High: Type errors, security issues, major functional problems
            if exception_type and 'TypeError' in exception_type:
                return 'high'
            if any(keyword in msg_lower for keyword in ['csrf', 'security', 'forbidden', 'access denied']):
                return 'high'
            
            # Default for Level 3: high
            return 'high'
        
        # Level 2 (Warning) differentiation
        if level == 2:
            # High: Security warnings
            if any(keyword in msg_lower for keyword in ['csrf', 'security', 'attack', 'suspicious']):
                return 'high'
            
            # Medium: Common PHP notices (undefined array key, deprecated)
            if any(keyword in msg_lower for keyword in ['undefined array key', 'undefined variable', 'deprecated']):
                return 'medium'
            
            # Default for Level 2: medium
            return 'medium'
        
        # Level 1 (Info) and Level 0 (Debug)
        return 'low'
    
    def _get_display_type(self, category: str, app: Optional[str]) -> str:
        """
        Get user-friendly display name for the category.
        
        For app-specific errors, shows "App: <AppName>".
        Otherwise returns the category's display name with icon.
        
        Args:
            category: Category key (e.g., 'authentication', 'apps')
            app: App name from log entry
            
        Returns:
            Display string (e.g., "🔐 Authentication & Access", "App: Calendar")
        """
        # Special handling for apps category
        if category == 'apps' and app and app not in ['core', 'no app in context']:
            return f"App: {app.title()}"
        
        # Return category display name with icon
        if category in FUNCTIONAL_CATEGORIES:
            return FUNCTIONAL_CATEGORIES[category]['name']
        
        # Fallback
        return category.replace('_', ' ').title()
    
    def parse_line(self, line: str, source_file: str = "", line_number: int = 0) -> bool:
        """
        Parse a single JSON log line.
        
        Args:
            line: Raw log line string
            source_file: Name of the source log file
            line_number: Line number in the source file
            
        Returns:
            True if successfully parsed and stored, False otherwise
        """
        try:
            data = json.loads(line)
            # Store the raw line in data for later use
            data['raw_line'] = line.strip()
            return self._categorize_entry(data, source_file, line_number)
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse JSON line: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error parsing line: {e}")
            return False
    
    def _categorize_entry(self, data: Dict[str, Any], source_file: str = "", line_number: int = 0) -> bool:
        """
        Categorize and store a parsed log entry.
        
        Args:
            data: Parsed JSON log entry
            source_file: Name of the source log file
            line_number: Line number in the source file
            
        Returns:
            True if entry was stored, False if skipped (duplicate/follow-up)
        """
        # Check if this is a follow-up error that should be skipped
        if self._is_followup_error(data):
            logger.debug(f"Skipping follow-up error for reqId: {data.get('reqId')}")
            return False
        
        # Extract basic fields
        msg = data.get('message', '')
        level = data.get('level')
        app = data.get('app', '')
        timestamp = data.get('time', '')
        user = data.get('user', '')
        
        # Skip debug level if configured
        from config import INCLUDE_DEBUG_LEVEL
        if level == 0 and not INCLUDE_DEBUG_LEVEL:
            logger.debug(f"Skipping debug entry (INCLUDE_DEBUG_LEVEL=False)")
            return False
        
        # Extract error code and exception info
        error_code = self._extract_error_code(data, msg)
        exception = data.get('exception', {})
        exception_type = None
        if isinstance(exception, dict) and 'Exception' in exception:
            exception_type = exception['Exception']
        
        # Determine functional category, severity, and display type
        category = self._get_functional_category(data, msg, app, exception_type)
        severity = self._get_severity(level, exception_type, msg)
        display_type = self._get_display_type(category, app)
        
        # Store entry in functional category
        return self.data_store.add_entry(category, {
            "time": timestamp,
            "type": display_type,
            "msg": msg[:200],  # Increased from 100 to 200 for better context
            "user": user,
            "app": app,
            "severity": severity,
            "error_code": error_code,
            "source_file": source_file,
            "line_number": line_number,
            "raw_line": data.get('raw_line', '')
        })
    
    def _extract_error_code(self, data: Dict[str, Any], message: str) -> Optional[str]:
        """
        Extract error code from various log sources.
        
        Checks multiple locations:
        1. HTTP status codes (401, 404, 500, etc.)
        2. Custom error_code fields
        3. errorCode in messages JSON
        4. Exception Code field
        5. Exception Message field
        
        Args:
            data: Full parsed JSON log entry
            message: Log message string
            
        Returns:
            Error code string or None
        """
        # Get exception message if available
        exception = data.get('exception', {})
        exception_msg = ""
        if isinstance(exception, dict) and 'Message' in exception:
            exception_msg = exception['Message']
        
        # Combine message and exception_msg for searching
        combined_msg = message + " " + exception_msg
        
        # 1. Check for HTTP status codes in combined message (various formats)
        # Format: `GET https://...` resulted in a `401 Unauthorized`
        http_match = re.search(r'`(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)[^`]*` resulted in a `(\d{3})', combined_msg)
        if http_match:
            return http_match.group(2)
        
        # Format: resulted in a `504 Gateway Timeout`
        http_match2 = re.search(r'resulted in a `(\d{3})', combined_msg)
        if http_match2:
            return http_match2.group(1)
        
        # 2. Check for custom error_code in data
        if 'error_code' in data:
            return str(data['error_code'])
        
        # 3. Check for errorCode in message (JSON embedded)
        error_code_match = re.search(r'"errorCode"\s*:\s*"([^"]+)"', combined_msg)
        if error_code_match:
            return error_code_match.group(1)
        
        # 4. Check exception data for Code field
        if isinstance(exception, dict) and 'Code' in exception:
            code = exception['Code']
            if code and code != 0:  # Ignore zero codes
                return str(code)
        
        # 5. Check for HTTP codes in generic format
        generic_http = re.search(r'HTTP[/\s]+(\d{3})', combined_msg, re.IGNORECASE)
        if generic_http:
            return generic_http.group(1)
        
        # 6. Check for error codes in format "error: XXX"
        error_pattern = re.search(r'error[:\s]+([A-Za-z0-9_-]+)', combined_msg, re.IGNORECASE)
        if error_pattern:
            code = error_pattern.group(1)
            # Filter out common words that aren't error codes
            if len(code) < 30 and not code.lower() in ['error', 'failed', 'exception']:
                return code
        
        return None
    
    def _is_followup_error(self, data: Dict[str, Any]) -> bool:
        """
        Detect if this is a follow-up/duplicate error that should be skipped.
        
        Nextcloud often logs the same error twice:
        1. First with detailed info (objectstore, webdav, etc.)
        2. Then as generic exception (index, no app in context)
        
        This method detects pattern #2 and filters it out.
        
        Args:
            data: Parsed JSON log entry
            
        Returns:
            True if this is a follow-up error that should be skipped
        """
        req_id = data.get('reqId')
        if not req_id:
            return False
        
        app = data.get('app', '')
        exception = data.get('exception', {})
        exception_type = exception.get('Exception', '')
        exception_msg = exception.get('Message', '')
        message = data.get('message', '')
        
        # Check if we've seen this reqId before
        if req_id in self.req_id_cache:
            prev_entry = self.req_id_cache[req_id]
            
            # Pattern: GenericFileException after specific error
            if exception_type == 'OCP\\Files\\GenericFileException':
                # Empty exception message is a strong indicator
                if not exception_msg:
                    # App context changed to generic
                    if app in ['index', 'no app in context']:
                        # Previous entry was a specific error
                        if prev_entry.get('has_details'):
                            logger.debug(
                                f"Follow-up detected: reqId={req_id}, "
                                f"prev_app={prev_entry.get('app')} -> curr_app={app}"
                            )
                            return True
        
        # Store this entry in cache for future comparisons
        has_details = bool(
            exception_msg or 
            (exception_type and exception_type != 'OCP\\Files\\GenericFileException') or
            (app and app not in ['index', 'no app in context'])
        )
        
        self.req_id_cache[req_id] = {
            'app': app,
            'exception_type': exception_type,
            'has_details': has_details,
            'message': message[:100]
        }
        
        return False
    
    def _extract_oid(self, message: str) -> str:
        """
        Extract and decode OID from message.
        
        Args:
            message: Log message
            
        Returns:
            Decoded OID or empty string
        """
        match = self.oid_regex.search(message)
        if match:
            try:
                return urllib.parse.unquote(match.group(1))
            except Exception as e:
                logger.debug(f"Failed to decode OID: {e}")
        return ""
    
    def _is_s3_error(self, message: str) -> bool:
        """
        Check if message contains S3/HTTP error.
        
        Args:
            message: Log message
            
        Returns:
            True if S3 error detected
        """
        return bool(self.http_error_regex.search(message))
    
    def _extract_http_code(self, message: str) -> str:
        """
        Extract HTTP error code from message.
        
        Args:
            message: Log message
            
        Returns:
            HTTP code or 'Unknown'
        """
        match = self.http_error_regex.search(message)
        return match.group(1) if match else "Unknown"
    
    def _is_dav_error(self, app: str, message: str) -> bool:
        """
        Check if entry is a WebDAV error.
        
        Args:
            app: Application name
            message: Log message
            
        Returns:
            True if DAV error detected
        """
        return app == 'webdav' or "Sabre\\DAV" in message
