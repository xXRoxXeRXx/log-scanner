"""
Quick test script for the new functional categorization system
"""
import sys
import json
from pathlib import Path

# Add shared folder to path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from data_store import LogDataStore
from server_parser import ServerLogParser

def test_log_file(log_path: str):
    """Test a log file with the new categorization system."""
    print(f"\n{'='*80}")
    print(f"Testing: {log_path}")
    print(f"{'='*80}\n")
    
    # Initialize data store and parser
    data_store = LogDataStore()
    parser = ServerLogParser(data_store)
    
    # Parse the log file
    total_lines = 0
    parsed_lines = 0
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            if parser.parse_line(line.strip(), source_file=Path(log_path).name, line_number=total_lines):
                parsed_lines += 1
    
    print(f"\n📊 Summary:")
    print(f"  Total lines: {total_lines}")
    print(f"  Parsed & stored: {parsed_lines}")
    print(f"  Filtered/skipped: {total_lines - parsed_lines}")
    print(f"  Filter rate: {((total_lines - parsed_lines) / total_lines * 100):.2f}%")
    
    print(f"\n📂 Categories:")
    for category in data_store.get_all_categories():
        entries = data_store.get_entries(category)
        if entries:
            print(f"\n  {category.upper()} ({len(entries)} entries):")
            
            # Show first 3 entries
            for i, entry in enumerate(entries[:3]):
                severity = entry.get('severity', 'unknown')
                msg = entry.get('msg', '')[:80]
                print(f"    [{severity.upper()}] {msg}...")
            
            if len(entries) > 3:
                print(f"    ... and {len(entries) - 3} more")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    # Test with the debug-heavy log first
    print("\n🧪 TEST 1: Debug-Heavy Log (99.98% Debug)")
    test_log_file(r"d:\DEV Projekte\log-scanner\dev\136931020.log")
    
    # Test with error-heavy log
    print("\n🧪 TEST 2: Error-Heavy Log (99.92% Errors - S3 NoSuchUpload)")
    test_log_file(r"d:\DEV Projekte\log-scanner\dev\122511000.log")
    
    # Test with warning-heavy log
    print("\n🧪 TEST 3: Warning-Heavy Log (76.5% Warnings - PHP Undefined Array Key)")
    test_log_file(r"d:\DEV Projekte\log-scanner\dev\150141120.log")
