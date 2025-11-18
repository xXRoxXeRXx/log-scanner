"""
Configuration settings for Nextcloud Log Analyzer
"""
from typing import Dict, Any
import logging
import gzip
import os
from pathlib import Path

# Application Settings
APP_VERSION = "17.4.0"
APP_TITLE = "Nextcloud Log Analyzer"

# Performance & Memory Limits
MAX_FILE_SIZE_MB = 500  # Maximum file size in MB
MAX_ENTRIES_PER_CATEGORY = 10000  # Maximum log entries per category
PROGRESS_UPDATE_INTERVAL = 2000  # Update UI every N lines

# File Support
SUPPORTED_EXTENSIONS = ['.log', '.txt', '.json', '.gz']  # Supported file types
GZIP_EXTENSIONS = ['.gz', '.gzip']  # Compressed file extensions

# Threading
ENABLE_THREADING = True  # Use threading for large files
LARGE_FILE_THRESHOLD_MB = 10  # Files larger than this use threading

# Logging Configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'log_analyzer.log'

# UI Settings
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 800
FONT_CONSOLE = ("Consolas", 10)
FONT_DEFAULT = ("TkDefaultFont", 10)
FONT_H1 = ("TkDefaultFont", 14, "bold")
FONT_H2 = ("TkDefaultFont", 12, "bold")

# Color Scheme
COLORS: Dict[str, str] = {
    'error': '#FF0000',
    'warning': '#FFA500',
    'info': '#007ACC',
    'debug': '#808080',
    'story': '#009900',
    'clickable': '#0000EE'
}

# Feature Flags
ENABLE_EXCEL_EXPORT = True
ENABLE_CLIPBOARD_IMPORT = True
ENABLE_DRAG_DROP = True

def get_max_file_size_bytes() -> int:
    """Returns maximum file size in bytes"""
    return MAX_FILE_SIZE_MB * 1024 * 1024

def get_large_file_threshold_bytes() -> int:
    """Returns large file threshold in bytes"""
    return LARGE_FILE_THRESHOLD_MB * 1024 * 1024

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

def setup_logging() -> logging.Logger:
    """Configure and return logger instance"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
