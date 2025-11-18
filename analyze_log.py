#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick analysis of log file for categorization review."""

import json
from collections import Counter, defaultdict

def analyze_log(filepath):
    apps = Counter()
    levels = Counter()
    exception_messages = []
    error_patterns = defaultdict(list)
    
    with open(filepath, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                entry = json.loads(line)
                app = entry.get('app', 'N/A')
                level = entry.get('level', 'N/A')
                message = entry.get('message', '')
                
                apps[app] += 1
                levels[level] += 1
                
                # Collect error patterns (level 3 = Error)
                if level == 3:
                    exception = entry.get('exception', {})
                    if exception:
                        exc_msg = exception.get('Message', '')[:100]
                        exception_messages.append({
                            'line': i,
                            'app': app,
                            'message': exc_msg,
                            'full_msg': message[:50]
                        })
                    
                    # Check for specific error patterns
                    combined = (message + ' ' + exception.get('Message', '')).lower()
                    if 'http' in combined and any(code in combined for code in ['401', '403', '404', '500', '502', '503']):
                        error_patterns['HTTP Errors'].append((i, app, message[:50]))
                    elif 'objectstore' in app.lower():
                        error_patterns['Objectstore'].append((i, app, message[:50]))
                    elif 'dav' in app.lower():
                        error_patterns['DAV'].append((i, app, message[:50]))
                    elif 'php' in combined:
                        error_patterns['PHP'].append((i, app, message[:50]))
                    
            except json.JSONDecodeError:
                continue
    
    print("=" * 80)
    print("LOG ANALYSIS - nextcloud (1).log")
    print("=" * 80)
    
    print(f"\n📊 STATISTICS:")
    print(f"Total entries analyzed: {sum(apps.values())}")
    print(f"Total errors (level 3): {levels.get(3, 0)}")
    print(f"Errors with exceptions: {len(exception_messages)}")
    
    print(f"\n📱 TOP 15 APPS:")
    for app, count in apps.most_common(15):
        print(f"  {app:25} {count:5} ({count*100/sum(apps.values()):.1f}%)")
    
    print(f"\n📊 LOG LEVELS:")
    level_names = {0: 'Debug', 1: 'Info', 2: 'Warning', 3: 'Error', 4: 'Fatal'}
    for level in sorted(levels.keys()):
        name = level_names.get(level, f'Unknown({level})')
        count = levels[level]
        print(f"  Level {level} ({name:8}): {count:5} ({count*100/sum(levels.values()):.1f}%)")
    
    print(f"\n🔍 ERROR PATTERNS:")
    for pattern, errors in error_patterns.items():
        print(f"\n  {pattern}: {len(errors)} occurrences")
        for line, app, msg in errors[:3]:  # Show first 3 examples
            print(f"    Line {line:3} [{app:15}] {msg}")
        if len(errors) > 3:
            print(f"    ... and {len(errors) - 3} more")
    
    print(f"\n🐛 SAMPLE EXCEPTIONS (first 5):")
    for exc in exception_messages[:5]:
        print(f"  Line {exc['line']:3} [{exc['app']:15}]")
        print(f"       Message: {exc['full_msg']}")
        print(f"       Exception: {exc['message']}")
        print()
    
    # Check for potential uncategorized errors
    print(f"\n💡 CATEGORIZATION REVIEW:")
    uncategorized = []
    for exc in exception_messages:
        app = exc['app']
        msg = (exc['full_msg'] + ' ' + exc['message']).lower()
        
        is_categorized = False
        if any(code in msg for code in ['401', '403', '404', '500', '502', '503']):
            is_categorized = True
        elif 'objectstore' in app.lower():
            is_categorized = True
        elif 'dav' in app.lower():
            is_categorized = True
        elif 'php' in msg:
            is_categorized = True
        
        if not is_categorized:
            uncategorized.append(exc)
    
    print(f"  ✅ Well categorized errors: {len(exception_messages) - len(uncategorized)}")
    print(f"  ⚠️  Potentially uncategorized: {len(uncategorized)}")
    
    if uncategorized:
        print(f"\n  Sample uncategorized errors:")
        for exc in uncategorized[:5]:
            print(f"    Line {exc['line']:3} [{exc['app']:15}] {exc['full_msg'][:60]}")

if __name__ == '__main__':
    analyze_log('nextcloud (1).log')
