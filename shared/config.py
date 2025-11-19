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
