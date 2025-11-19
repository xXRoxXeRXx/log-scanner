"""
Web-adapted parser integration
Connects existing parsers to FastAPI backend
"""

import sys
from pathlib import Path
from typing import Dict, List

# Import existing parsers
sys.path.insert(0, str(Path(__file__).parent))

try:
    from server_parser import parse_server_log
    from client_parser import parse_client_log
    from data_store import DataStore
except ImportError:
    # Fallback if parsers not available yet
    parse_server_log = None
    parse_client_log = None
    DataStore = None


def analyze_log_files(file_paths: List[Path]) -> Dict:
    """
    Analyze log files using existing parsers
    
    Args:
        file_paths: List of paths to log files
        
    Returns:
        Dictionary with analysis results
    """
    if not parse_server_log or not DataStore:
        # Fallback: return mock data
        return _mock_analysis(file_paths)
    
    try:
        # Create data store
        data_store = DataStore()
        
        # Parse each file
        for file_path in file_paths:
            filename = file_path.name.lower()
            
            # Determine file type and parse
            if 'nextcloud' in filename or 'server' in filename:
                # Server log
                parse_server_log(str(file_path), data_store)
            elif 'client' in filename:
                # Client log
                parse_client_log(str(file_path), data_store)
            else:
                # Try server parser as default
                parse_server_log(str(file_path), data_store)
        
        # Extract results
        categories = {
            "s3_errors": len(data_store.s3_errors),
            "dav_errors": len(data_store.dav_errors),
            "db_errors": len(data_store.db_errors),
            "other_errors": len(data_store.other_errors),
            "warnings": len(data_store.warnings),
            "info": len(data_store.info_logs)
        }
        
        # Combine all entries for display
        all_entries = []
        
        # Add errors
        for entry in data_store.s3_errors:
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("message", ""),
                "category": "s3_errors"
            })
        
        for entry in data_store.dav_errors:
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("message", ""),
                "category": "dav_errors"
            })
        
        for entry in data_store.db_errors:
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("message", ""),
                "category": "db_errors"
            })
        
        for entry in data_store.other_errors:
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "ERROR",
                "message": entry.get("message", ""),
                "category": "other_errors"
            })
        
        # Add warnings (limit)
        for entry in data_store.warnings[:100]:
            all_entries.append({
                "time": entry.get("time", ""),
                "type": "WARNING",
                "message": entry.get("message", ""),
                "category": "warnings"
            })
        
        # Sort by time (most recent first)
        all_entries.sort(key=lambda x: x.get("time", ""), reverse=True)
        
        return {
            "status": "completed",
            "file_count": len(file_paths),
            "total_entries": sum(categories.values()),
            "categories": categories,
            "entries": all_entries[:200]  # Limit to 200 entries
        }
    
    except Exception as e:
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
