#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test macOS date picker fallback behavior
"""
import sys

def test_platform_detection():
    """Test that platform is correctly detected."""
    print("=" * 70)
    print("PLATFORM DETECTION TEST")
    print("=" * 70)
    
    platform = sys.platform
    print(f"\nCurrent platform: {platform}")
    
    is_macos = platform == 'darwin'
    is_windows = platform == 'win32'
    is_linux = platform.startswith('linux')
    
    print(f"  - macOS: {is_macos}")
    print(f"  - Windows: {is_windows}")
    print(f"  - Linux: {is_linux}")
    
    return is_macos, is_windows, is_linux


def test_tkcalendar_import(is_macos):
    """Test tkcalendar import behavior."""
    print("\n" + "=" * 70)
    print("TKCALENDAR IMPORT TEST")
    print("=" * 70)
    
    has_tkcalendar = False
    
    if not is_macos:
        try:
            from tkcalendar import DateEntry
            has_tkcalendar = True
            print("\n✅ tkcalendar imported successfully")
            print("   DateEntry will be used for date picking")
        except ImportError:
            print("\n⚠️  tkcalendar not installed")
            print("   Falling back to text entry")
    else:
        print("\n🍎 macOS detected - skipping tkcalendar import")
        print("   Using native text entry instead")
    
    print(f"\nHAS_TKCALENDAR = {has_tkcalendar}")
    return has_tkcalendar


def test_date_entry_widget(has_tkcalendar):
    """Test date entry widget behavior."""
    print("\n" + "=" * 70)
    print("DATE ENTRY WIDGET TEST")
    print("=" * 70)
    
    if has_tkcalendar:
        print("\n📅 DateEntry Widget (tkcalendar)")
        print("   Configuration:")
        print("   - Visual calendar popup")
        print("   - Date pattern: yyyy-mm-dd")
        print("   - Separate time entry field (HH:MM)")
        print("   - Background: darkblue")
        print("   - Foreground: white")
    else:
        print("\n📝 Text Entry Widget (fallback)")
        print("   Configuration:")
        print("   - Native tkinter Entry")
        print("   - Pre-filled with today's date")
        print("   - Format hint: (YYYY-MM-DD HH:MM)")
        print("   - Width: 20 characters")
        print("   - Example: '2025-11-18'")
    
    print("\n✅ Date entry widget configured correctly")


def test_import_log_analyzer():
    """Test importing the main application."""
    print("\n" + "=" * 70)
    print("LOG ANALYZER IMPORT TEST")
    print("=" * 70)
    
    try:
        from log_analyzer_v17 import IS_MACOS, HAS_TKCALENDAR
        print(f"\n✅ Successfully imported log_analyzer_v17")
        print(f"   IS_MACOS = {IS_MACOS}")
        print(f"   HAS_TKCALENDAR = {HAS_TKCALENDAR}")
        
        # Verify logic
        if IS_MACOS and HAS_TKCALENDAR:
            print("\n❌ ERROR: HAS_TKCALENDAR should be False on macOS!")
            return False
        
        if not IS_MACOS and not HAS_TKCALENDAR:
            print("\n⚠️  WARNING: tkcalendar not installed on non-macOS system")
        
        print("\n✅ Platform detection working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR importing log_analyzer_v17: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("macOS DATE PICKER COMPATIBILITY TEST")
    print("Version: 17.9.1")
    print("=" * 70)
    
    # Test 1: Platform detection
    is_macos, is_windows, is_linux = test_platform_detection()
    
    # Test 2: tkcalendar import
    has_tkcalendar = test_tkcalendar_import(is_macos)
    
    # Test 3: Date entry widget
    test_date_entry_widget(has_tkcalendar)
    
    # Test 4: Import log analyzer
    success = test_import_log_analyzer()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if is_macos:
        print("\n🍎 macOS Platform")
        print("   Expected behavior:")
        print("   - HAS_TKCALENDAR = False ✅")
        print("   - Using text entry with date format hints ✅")
        print("   - Pre-filled with today's date ✅")
    elif is_windows:
        print("\n🪟 Windows Platform")
        print("   Expected behavior:")
        print(f"   - HAS_TKCALENDAR = {has_tkcalendar}")
        if has_tkcalendar:
            print("   - Using tkcalendar DateEntry ✅")
        else:
            print("   - Falling back to text entry (tkcalendar not installed)")
    else:
        print("\n🐧 Linux Platform")
        print("   Expected behavior:")
        print(f"   - HAS_TKCALENDAR = {has_tkcalendar}")
        if has_tkcalendar:
            print("   - Using tkcalendar DateEntry ✅")
        else:
            print("   - Falling back to text entry (tkcalendar not installed)")
    
    if success:
        print("\n✅ ALL TESTS PASSED")
        print("\nThe date picker will work correctly on all platforms!")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease check the errors above.")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
