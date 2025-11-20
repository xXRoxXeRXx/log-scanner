"""
Test script to upload a log file via API and check the categorization
"""
import requests
import json
import time
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
API_KEY = "your-super-secret-key-here"  # From .env file
LOG_FILE = r"d:\DEV Projekte\log-scanner\dev\122511000.log"  # Error-Heavy (S3 + TypeErrors)

def test_log_upload():
    """Upload a log file and check the categorization."""
    print(f"\n{'='*80}")
    print("🧪 Testing Log Upload & Categorization via API")
    print(f"{'='*80}\n")
    
    # 1. Upload the log file
    print(f"📤 Uploading: {Path(LOG_FILE).name}")
    
    with open(LOG_FILE, 'rb') as f:
        files = {'files': (Path(LOG_FILE).name, f, 'application/octet-stream')}
        headers = {'X-API-Key': API_KEY}
        
        response = requests.post(
            f"{API_URL}/api/upload",
            files=files,
            headers=headers
        )
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    analysis_id = data.get('analysis_id')
    print(f"✅ Upload & Analysis successful! Analysis ID: {analysis_id}")
    
    # Get results immediately (no status check needed - synchronous API)
    print("\n📊 Fetching results...")
    response = requests.get(
        f"{API_URL}/api/results/{analysis_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Results fetch failed: {response.status_code}")
        return
    
    result = response.json()
    
    # 4. Display categorization
    print(f"\n{'='*80}")
    print("📂 CATEGORIZATION RESULTS")
    print(f"{'='*80}\n")
    
    print(f"Total entries: {result.get('total_entries', 0)}")
    print(f"Parsed entries: {result.get('parsed_entries', 0)}")
    
    categories = result.get('categories', {})
    print(f"\n📂 Categories found:")
    
    category_labels = {
        'authentication': '🔐 Authentication & Access',
        'file_sync': '📁 File Sync & WebDAV',
        'storage': '☁️ Storage & S3',
        'database': '🗄️ Database',
        'security': '🔒 Security',
        'apps': '📱 Apps',
        'background_jobs': '⚙️ Background Jobs',
        'php_runtime': '🐘 PHP Runtime',
        'system': '⚡ System'
    }
    
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            label = category_labels.get(category, category)
            percentage = (count / result.get('total_entries', 1)) * 100
            print(f"  {label}: {count} entries ({percentage:.1f}%)")
    
    # 5. Show sample entries
    print(f"\n📝 Sample Entries:")
    entries = result.get('entries', [])
    for entry in entries[:5]:
        category = entry.get('category', 'unknown')
        severity = entry.get('severity', 'unknown')
        msg = entry.get('message', '')[:80]
        label = category_labels.get(category, category)
        print(f"\n  [{label}] [{severity.upper()}]")
        print(f"  {msg}...")
    
    print(f"\n{'='*80}\n")
    print(f"✅ Test completed! View full results at: {API_URL}/results/{analysis_id}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    test_log_upload()
