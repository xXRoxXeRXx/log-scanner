"""
Web-adapted parser integration
Connects existing parsers to FastAPI backend
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(Path(__file__).parent))

logger.debug(f"Python path: {sys.path[:3]}")

try:
    # Import parser classes
    from server_parser import ServerLogParser
    from client_parser import ClientLogParser
    from data_store import LogDataStore
    from config import open_file
    
    PARSERS_AVAILABLE = True
    logger.info("Parser classes imported successfully!")
except ImportError as e:
    logger.error(f"Parser import failed: {e}")
    PARSERS_AVAILABLE = False
    ServerLogParser = None
    ClientLogParser = None
    LogDataStore = None


def analyze_log_files(file_paths: List[Path]) -> Dict:
    """
    Analyze log files using existing parsers
    
    Args:
        file_paths: List of paths to log files
        
    Returns:
        Dictionary with analysis results
    """
    if not PARSERS_AVAILABLE or not ServerLogParser or not LogDataStore:
        # Fallback: return mock data
        logger.warning("Parsers not available, using mock data")
        return _mock_analysis(file_paths)
    
    try:
        # Create data store
        data_store = LogDataStore()
        
        # Create parser instances
        server_parser = ServerLogParser(data_store)
        client_parser = ClientLogParser(data_store)
        
        logger.info(f"Analyzing {len(file_paths)} file(s)...")
        
        # Parse each file
        for file_path in file_paths:
            filename = file_path.name.lower()
            
            logger.info(f"Parsing: {filename}")
            
            # Determine file type by reading first few lines
            is_client_log = False
            try:
                with open_file(str(file_path)) as f:
                    # Check first 5 lines for client log format
                    for i, line in enumerate(f):
                        if i >= 5:
                            break
                        # Client logs have format: "2025-11-18 14:17:18:495 [ info nextcloud.gui..."
                        if '[ info nextcloud.gui' in line or '[ warning nextcloud' in line or '[ debug nextcloud' in line:
                            is_client_log = True
                            break
            except:
                pass
            
            # Parse with appropriate parser
            if is_client_log:
                # Client log
                logger.debug(f"Using ClientLogParser for {filename} (detected by format)")
                with open_file(str(file_path)) as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line:
                            client_parser.parse_line(line, str(file_path), line_num)
            elif 'client' in filename:
                # Client log by filename
                logger.debug(f"Using ClientLogParser for {filename} (by filename)")
                with open_file(str(file_path)) as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line:
                            client_parser.parse_line(line, str(file_path), line_num)
            else:
                # Server log (default)
                logger.debug(f"Using ServerLogParser for {filename}")
                with open_file(str(file_path)) as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line:
                            server_parser.parse_line(line, str(file_path), line_num)
        
        # Extract results from data_store._data
        categories = {
            "s3_errors": len(data_store._data.get("s3_errors", [])),
            "dav_errors": len(data_store._data.get("dav_errors", [])),
            "objectstore_errors": len(data_store._data.get("objectstore_errors", [])),
            "php_errors": len(data_store._data.get("php_errors", [])),
            "other_errors": len(data_store._data.get("other_errors", [])),
            "server_warnings": len(data_store._data.get("server_warnings", [])),
            "server_info": len(data_store._data.get("server_info", [])),
            "client_errors": len(data_store._data.get("client_errors", [])),
            "client_events": len(data_store._data.get("client_events", []))
        }
        
        logger.info(f"Analysis results: {categories}")
        total_entries = sum(categories.values())
        logger.info(f"Total entries parsed: {total_entries}")
        
        # Combine all entries for display
        all_entries = []
        
        # Add S3 errors
        for entry in data_store._data.get("s3_errors", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("msg", entry.get("message", "")),
                "category": "s3_errors",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Add DAV errors
        for entry in data_store._data.get("dav_errors", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("msg", entry.get("message", "")),
                "category": "dav_errors",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Add ObjectStore errors
        for entry in data_store._data.get("objectstore_errors", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("msg", entry.get("message", "")),
                "category": "objectstore_errors",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Add PHP errors
        for entry in data_store._data.get("php_errors", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("msg", entry.get("message", "")),
                "category": "php_errors",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Add other errors
        for entry in data_store._data.get("other_errors", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("msg", entry.get("message", "")),
                "category": "other_errors",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Add warnings (all entries)
        for entry in data_store._data.get("server_warnings", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "WARNING",
                "message": entry.get("msg", entry.get("message", "")),
                "category": "server_warnings",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Add server info entries
        for entry in data_store._data.get("server_info", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "INFO",
                "message": entry.get("msg", entry.get("message", "")),
                "category": "server_info",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Add client errors
        for entry in data_store._data.get("client_errors", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": entry.get("type", "ERROR"),  # Use type from parser (WARNING/ERROR/INFO)
                "message": entry.get("msg", entry.get("message", "")),
                "category": "client_errors",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Add client events (story events)
        for entry in data_store._data.get("client_events", []):
            all_entries.append({
                "time": entry.get("time", ""),
                "type": entry.get("type", "INFO"),
                "message": entry.get("msg", entry.get("message", "")),
                "category": "client_events",
                "error_code": entry.get("error_code", ""),
                "source_file": entry.get("source_file", ""),
                "line_number": entry.get("line_number", 0),
                "raw_line": entry.get("raw_line", "")
            })
        
        # Sort by time (most recent first)
        all_entries.sort(key=lambda x: x.get("time", ""), reverse=True)
        
        logger.info(f"Returning {len(all_entries)} total entries")
        
        return {
            "status": "completed",
            "file_count": len(file_paths),
            "total_entries": sum(categories.values()),
            "categories": categories,
            "entries": all_entries  # Return ALL entries (no limit)
        }
    
    except Exception as e:
        import traceback
        logger.error(f"Parser error: {e}")
        logger.debug(traceback.format_exc())
        return {
            "status": "failed",
            "error_message": f"Parser error: {str(e)}",
            "file_count": len(file_paths),
            "total_entries": 0,
            "categories": {},
            "entries": []
        }


def _mock_analysis(file_paths: List[Path]) -> Dict:
    """
    Mock analysis for testing without parsers
    """
    total_lines = 0
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = len(f.readlines())
                total_lines += lines
        except:
            pass
    
    return {
        "status": "completed",
        "file_count": len(file_paths),
        "total_entries": total_lines,
        "categories": {
            "s3_errors": 0,
            "dav_errors": 0,
            "db_errors": 0,
            "other_errors": 0,
            "warnings": 0,
            "info": total_lines
        },
        "entries": []
    }
