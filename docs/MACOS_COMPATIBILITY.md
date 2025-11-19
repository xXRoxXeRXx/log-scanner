# macOS Compatibility Notes

## Date Picker on macOS

### Issue
The `tkcalendar` library's `DateEntry` widget does not work reliably on macOS:
- Calendar popup may not appear
- Application may crash when clicking the calendar button
- Visual glitches and rendering issues

### Solution (v17.9.1+)
The application now automatically detects macOS and uses a native text-based date picker instead:

**On macOS:**
```
Von: [2025-11-18] (YYYY-MM-DD HH:MM)
Bis: [2025-11-18 23:59] (YYYY-MM-DD HH:MM)
```

**On Windows/Linux:**
```
Von: [📅 Calendar Button] HH:MM
Bis: [📅 Calendar Button] HH:MM
```

### How to Use (macOS)

1. **Date Format**: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM`
   - Example: `2025-11-18` or `2025-11-18 14:30`

2. **Pre-filled Values**: Fields are pre-filled with today's date
   - Start field: Today at 00:00
   - End field: Today at 23:59

3. **Editing**: Simply click the field and type your date
   - Format hints are shown next to each field
   - Invalid formats will be handled gracefully

### Examples

**Filter last 7 days:**
```
Von: 2025-11-11
Bis: 2025-11-18 23:59
```

**Filter specific day:**
```
Von: 2025-11-15 00:00
Bis: 2025-11-15 23:59
```

**Filter with time range:**
```
Von: 2025-11-18 09:00
Bis: 2025-11-18 17:00
```

## Platform Detection

The application automatically detects your platform:

```python
import sys

IS_MACOS = sys.platform == 'darwin'  # True on macOS
IS_WINDOWS = sys.platform == 'win32'  # True on Windows
IS_LINUX = sys.platform.startswith('linux')  # True on Linux
```

### Date Picker Selection

| Platform | Widget Used | Calendar Popup |
|----------|-------------|----------------|
| **macOS** | Text Entry | ❌ No (doesn't work) |
| **Windows** | DateEntry | ✅ Yes |
| **Linux** | DateEntry | ✅ Yes |

## Testing

Run the compatibility test:

```bash
python test_macos_compatibility.py
```

Expected output on macOS:
```
🍎 macOS Platform
   Expected behavior:
   - HAS_TKCALENDAR = False ✅
   - Using text entry with date format hints ✅
   - Pre-filled with today's date ✅

✅ ALL TESTS PASSED
```

## Installation on macOS

### Standard Installation

```bash
# Clone repository
git clone https://github.com/xXRoxXeRXx/log-scanner.git
cd log-scanner

# Install dependencies
pip3 install -r requirements.txt

# Run application
python3 log_analyzer_v17.py
```

### Note about tkcalendar

On macOS, the application will **not** try to import `tkcalendar`, so you don't need to install it. However, if you have it installed, it will be automatically disabled on macOS.

## Troubleshooting

### Date picker not working?
✅ **v17.9.1+**: Should work out of the box on macOS

❌ **v17.9.0 and earlier**: Upgrade to v17.9.1:
```bash
git pull origin main
python3 log_analyzer_v17.py
```

### Wrong date format?
Use the format hint shown next to each field:
- `YYYY-MM-DD` for date only
- `YYYY-MM-DD HH:MM` for date + time

### Application crashes on macOS?
This should be fixed in v17.9.1. If it still happens:
1. Check your Python version: `python3 --version` (requires Python 3.8+)
2. Check tkinter: `python3 -c "import tkinter; print('OK')"`
3. Update to latest version: `git pull origin main`

## Version History

| Version | macOS Support | Notes |
|---------|---------------|-------|
| **17.9.1** | ✅ Full | Platform detection, native date picker |
| 17.9.0 | ⚠️ Broken | tkcalendar doesn't work on macOS |
| 17.8.x | ⚠️ Broken | No platform detection |

## Related Issues

- tkcalendar issue: https://github.com/j4321/tkcalendar/issues/46
- Platform-specific tkinter issues are common

## Alternative: Manual Date Editing

Even on Windows/Linux, you can ignore the calendar popup and type dates manually in the same format:
```
YYYY-MM-DD HH:MM
```

This works consistently across all platforms.
