"""
Test script for GZ file support and multi-file processing
"""
import gzip
import os
import json
from datetime import datetime

def create_test_files():
    """Create test log files including compressed ones."""
    
    # Test 1: Regular server log
    server_log = "test_server.log"
    with open(server_log, 'w', encoding='utf-8') as f:
        for i in range(10):
            log_entry = {
                "reqId": f"test-{i}",
                "level": 3,
                "time": datetime.now().isoformat(),
                "remoteAddr": "192.168.1.100",
                "user": "testuser",
                "app": "PHP",
                "method": "GET",
                "url": "/index.php/apps/files",
                "message": f"Test error message {i}",
                "userAgent": "Mozilla/5.0",
                "version": "27.0.0.0"
            }
            f.write(json.dumps(log_entry) + '\n')
    
    print(f"✅ Created {server_log}")
    
    # Test 2: Compressed server log
    server_log_gz = "test_server.log.gz"
    with gzip.open(server_log_gz, 'wt', encoding='utf-8') as f:
        for i in range(10, 20):
            log_entry = {
                "reqId": f"test-{i}",
                "level": 3,
                "time": datetime.now().isoformat(),
                "remoteAddr": "192.168.1.100",
                "user": "testuser",
                "app": "webdav",
                "method": "PROPFIND",
                "url": "/remote.php/dav/files/user/",
                "message": f"DAV error {i}",
                "userAgent": "Mozilla/5.0",
                "version": "27.0.0.0"
            }
            f.write(json.dumps(log_entry) + '\n')
    
    print(f"✅ Created {server_log_gz} (compressed)")
    
    # Test 3: Regular client log
    client_log = "test_client.log"
    with open(client_log, 'w', encoding='utf-8') as f:
        f.write("2025-11-18 10:00:00:123 [ info nextcloud.gui.application ]: Nextcloud 3.10.0\n")
        f.write("2025-11-18 10:00:01:456 [ info sync.engine ]: >========== Sync started for folder [/home/user/Nextcloud]\n")
        f.write("2025-11-18 10:00:02:789 [ info sync.engine ]: Chunked upload of 1024000 bytes took 500\n")
        f.write("2025-11-18 10:00:03:012 [ info sync.engine ]: <========== Sync finished for folder [/home/user/Nextcloud]\n")
        f.write("2025-11-18 10:00:04:345 [ warning sync.networkjob ]: Error transferring file.txt - server replied: 403 Forbidden\n")
    
    print(f"✅ Created {client_log}")
    
    # Test 4: Compressed client log
    client_log_gz = "test_client.log.gz"
    with gzip.open(client_log_gz, 'wt', encoding='utf-8') as f:
        f.write("2025-11-18 11:00:00:123 [ info nextcloud.gui.application ]: Nextcloud 3.10.0\n")
        f.write("2025-11-18 11:00:01:456 [ info sync.engine ]: >========== Sync started for folder [/home/user/Nextcloud2]\n")
        f.write("2025-11-18 11:00:02:789 [ info sync.engine ]: Compare etag abc123 -> CHANGED\n")
        f.write("2025-11-18 11:00:03:012 [ info sync.engine ]: <========== Sync finished for folder [/home/user/Nextcloud2]\n")
    
    print(f"✅ Created {client_log_gz} (compressed)")
    
    print("\n📦 Test files created successfully!")
    print("Now you can test:")
    print("  1. Load single .gz file")
    print("  2. Load multiple files (mix of .log and .gz)")
    print("  3. Drag & drop multiple files")

if __name__ == "__main__":
    create_test_files()
