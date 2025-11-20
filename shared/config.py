"""
Configuration settings for Nextcloud Log Analyzer - Web Edition
Minimal config for web parser support
"""
import gzip
from pathlib import Path

# Performance & Memory Limits
MAX_ENTRIES_PER_CATEGORY = 10000  # Maximum log entries per category

# File Support
SUPPORTED_EXTENSIONS = ['.log', '.txt', '.json', '.gz']  # Supported file types
GZIP_EXTENSIONS = ['.gz', '.gzip']  # Compressed file extensions

# Log Filtering & Grouping
INCLUDE_DEBUG_LEVEL = False  # Include Debug-Level (0) entries (reduces noise by ~99%)
GROUP_REPEATED_ERRORS = True  # Group identical errors together (e.g., 53x S3 error -> 1 entry)

# Functional Categories (NEW - Based on Multi-Log Analysis)
FUNCTIONAL_CATEGORIES = {
    'authentication': {
        'name': '🔐 Authentication & Access',
        'description': 'Login issues, session problems, access denied',
        'priority': 1,
        'default_severity': 'high',
        'icon': '🔐'
    },
    'file_sync': {
        'name': '📁 File Synchronization',
        'description': 'WebDAV, file access, sync conflicts',
        'priority': 2,
        'default_severity': 'high',
        'icon': '📁'
    },
    'storage': {
        'name': '☁️ Storage & Object Store',
        'description': 'S3 errors, storage backend issues',
        'priority': 3,
        'default_severity': 'critical',
        'icon': '☁️'
    },
    'database': {
        'name': '🗄️ Database',
        'description': 'Database performance and query issues',
        'priority': 4,
        'default_severity': 'medium',
        'icon': '🗄️'
    },
    'security': {
        'name': '🔒 Security & CSRF',
        'description': 'Security warnings, CSRF checks, cookie issues',
        'priority': 5,
        'default_severity': 'high',
        'icon': '🔒'
    },
    'apps': {
        'name': '📱 Apps & Extensions',
        'description': 'Issues from installed Nextcloud apps',
        'priority': 6,
        'default_severity': 'medium',
        'icon': '📱'
    },
    'background_jobs': {
        'name': '⚙️ Background Jobs',
        'description': 'Cron jobs and scheduled tasks',
        'priority': 7,
        'default_severity': 'low',
        'icon': '⚙️'
    },
    'php_runtime': {
        'name': '🐘 PHP Runtime',
        'description': 'PHP errors, warnings, and runtime issues',
        'priority': 8,
        'default_severity': 'high',
        'icon': '🐘'
    },
    'system': {
        'name': '⚡ System & Core',
        'description': 'Core system messages, general info',
        'priority': 9,
        'default_severity': 'low',
        'icon': '⚡'
    }
}

# App to Category Mapping
APP_CATEGORY_MAPPING = {
    # Authentication
    'core': 'authentication',
    
    # File Sync
    'webdav': 'file_sync',  # Note: Can be 'storage' if S3-related
    'dav': 'file_sync',
    'files': 'file_sync',
    
    # Storage
    'objectstore': 'storage',
    
    # Apps
    'deck': 'apps',
    'text': 'apps',
    'calendar': 'apps',
    'contacts': 'apps',
    'talk': 'apps',
    'mail': 'apps',
    'forms': 'apps',
    'polls': 'apps',
    'richdocuments': 'apps',
    'notes': 'apps',
    
    # Background
    'cron': 'background_jobs',
    
    # PHP
    'PHP': 'php_runtime',
    
    # System
    'activity': 'system',
    'no app in context': 'system'
}

def is_gzip_file(filepath: str) -> bool:
    """Check if file is gzip compressed"""
    ext = Path(filepath).suffix.lower()
    return ext in GZIP_EXTENSIONS

def open_file(filepath: str, mode: str = 'r', encoding: str = 'utf-8'):
    """
    Open file with automatic gzip detection

    Args:
        filepath: Path to file
        mode: File mode ('r' for text, 'rb' for binary)
        encoding: Text encoding (only for text mode)

    Returns:
        File handle (text or binary depending on mode)
    """
    if is_gzip_file(filepath):
        if 'b' in mode:
            return gzip.open(filepath, mode)
        else:
            return gzip.open(filepath, mode + 't', encoding=encoding)
    else:
        if 'b' in mode:
            return open(filepath, mode)
        else:
            return open(filepath, mode, encoding=encoding)
