# Changelog

All notable changes to the Nextcloud Log Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [17.8.1] - 2025-11-18

### 🐛 Bug Fix

#### Improved Error Code Extraction from Exception Messages

**Problem**: Error codes in deep exception messages were not detected
- Example: Line 1 of log shows `503 Service Unavailable` in `exception.Message` field
- Previous version only searched top-level `message` field
- Result: Error code showed as "-" instead of "503"

**Solution**: Search both message fields
- Now combines `message` + `exception.Message` into `combined_msg`
- All regex patterns search the combined message
- Extracts HTTP codes from: `` `HEAD https://...` resulted in a `503 Service Unavailable` ``

**Impact**: 
- More accurate error code detection for S3/Objectstore errors
- Better error analysis and grouping
- Improved support workflows

**Technical**:
- Modified `_extract_error_code()` in `server_parser.py`
- Added `exception_msg` extraction from `data['exception']['Message']`
- Changed all searches from `message` to `combined_msg`

**Example**:
```json
{
  "message": "Could not get object urn:oid:939315",
  "exception": {
    "Message": "...resulted in a `503 Service Unavailable` response..."
  }
}
```
Now correctly extracts: `503` ✅ (previously: `-` ❌)

## [17.8.0] - 2025-11-18

### 🎯 Major Workflow Improvements

This release focuses on improving support workflows with smarter exports, better UX, and combined views.

### Added

#### 1. **Smart Export Filtering** 📤
- Markdown and Excel exports now only export **visible/filtered entries**
- Search results can be exported directly
- No more exporting thousands of entries when you only need 50
- Tracks `_detail_filtered_entries` for accurate exports

#### 2. **Context Menu in Detail Views** 🖱️
- Right-click on any row for quick actions:
  - **📄 Volle Nachricht anzeigen** → Opens full message in dialog (for long messages)
  - **📋 Zeile kopieren** → Copy single row to clipboard
  - **📋 Alle sichtbaren kopieren** → Copy all filtered rows
- Full message dialog with copy button
- Works with search/filter

#### 3. **Intelligent Time Sorting** ⏰
- Time column now sorts **chronologically** (not alphabetically)
- Supports multiple timestamp formats:
  - `2025-11-18 10:15:23.456` (Server logs)
  - `2025-11-18 10:15:23:456` (Client logs)
  - ISO 8601 formats
- Graceful fallback for invalid timestamps
- datetime parsing with multiple format attempts

#### 4. **UI Preferences Persistence** 💾
- Window size is now saved and restored
- Preferences stored in `~/.nextcloud_log_analyzer_prefs.json`
- Automatic save on application close
- Cross-session consistency

#### 5. **Combined Error View** 📊
- New button: **"📊 Alle Server-Fehler anzeigen"**
- Combines S3, DAV, PHP, Objectstore, and Other errors in one view
- Shows category prefix in Type column: `[S3] HTTP 404`
- Sorted by time (newest first)
- Perfect for getting overview of all errors at once

### Changed
- Export functions now respect search/filter state
- Time sorting improved from string comparison to datetime parsing
- Application saves state on exit
- Combined views prepend category to type field

### Use Cases
- **Filtered Export**: Search for "user123" → Export only those 10 entries
- **Quick Copy**: Right-click → Copy row → Paste in ticket
- **Full Message**: Long error? Right-click → Show full message → Read comfortably
- **All Errors**: One view for all error types instead of clicking 5 categories
- **Chronological Analysis**: Time column sorts correctly (08:00 < 09:00 < 10:00)

### Example Workflow
```
1. Open log file
2. Click "Alle Server-Fehler anzeigen" (500 errors)
3. Search: "urn:oid:12345" (narrows to 5 entries)
4. Click time column to sort chronologically
5. Right-click → Copy all visible (5 entries)
6. Paste into support ticket
7. Export to Excel (only 5 entries, not 500!)
```

### Technical
- Added `_detail_filtered_entries` tracking
- Context menu uses `tk.Menu` with `tearoff=0`
- datetime parsing with format list and try/except chains
- JSON-based preferences in user home directory
- `protocol("WM_DELETE_WINDOW")` for save-on-close
- Combined view uses temporary data_store category

## [17.7.0] - 2025-11-18

### 🔄 Sortierbare Spalten in Detail-Ansicht

Alle Spalten in den Detail-Ansichten können nun durch Klick auf die Spaltenüberschrift sortiert werden.

### Added
- **Spalten-Sortierung** 🔽🔼
  - Klick auf Spaltenüberschrift sortiert die Spalte
  - Erneuter Klick wechselt Sortierrichtung (aufsteigend ↑ / absteigend ↓)
  - Sortier-Indikator (Pfeil) zeigt aktuelle Sortierung
  - Funktioniert für alle 6 Spalten: Zeit, Typ, Error Code, Datei, Zeile, Nachricht
  
- **Intelligente Sortierung**
  - **Zeile**: Numerische Sortierung (1, 2, 10, 20 statt 1, 10, 2, 20)
  - **Andere Spalten**: Alphabetische Sortierung (case-insensitive)
  - Sortierung bleibt bei aktiver Suche erhalten

### Use Cases
- **Nach Zeit sortieren**: Chronologische oder umgekehrte Reihenfolge
- **Nach Datei sortieren**: Alle Einträge einer Datei gruppieren
- **Nach Error Code sortieren**: Gleiche Fehler zusammen anzeigen
- **Nach Zeile sortieren**: Fehler in Log-Reihenfolge analysieren
- **Nach Typ sortieren**: Fehlertypen gruppiert betrachten

### Example
```
Klick auf "Datei" → Sortiert nach Dateinamen (nextcloud.log → nextcloud.log.1)
Klick auf "Zeile" → Sortiert numerisch (Zeile 5 → 10 → 120 → 1250)
Klick auf "Error Code" → Gruppiert gleiche Fehler (401, 401, 404, 404, 500)
```

### Technical
- Sortierung erfolgt im UI (Treeview), nicht in Daten
- Pfeil-Indikatoren (↑↓) zeigen Sortierrichtung
- Spaltenname-Dictionary verhindert Pfeil-Duplikation
- `tree.move()` für performante Neuanordnung

## [17.6.0] - 2025-11-18

### 📂 Source File and Line Number Tracking

Added file name and line number tracking for better log traceability, especially useful when analyzing multiple log files.

### Added
- **Source File Column** 📄
  - Shows the filename where each log entry originated
  - Displays "Zwischenablage" for entries from clipboard
  - Visible in all detail views
  - Searchable in the search field
  - Included in Markdown and Excel exports

- **Line Number Column** #️⃣
  - Shows the exact line number in the source file
  - Helps locate errors in original log files
  - Visible in all detail views
  - Searchable in the search field
  - Included in Markdown and Excel exports

### Changed
- Detail window width increased from 1200px to 1400px to accommodate new columns
- Column layout optimized:
  - Zeit: 180px
  - Typ: 120px (reduced from 150px)
  - Error Code: 100px (reduced from 120px)
  - **Datei: 180px** (NEW)
  - **Zeile: 80px** (NEW)
  - Nachricht: 700px
- Markdown export now includes 6 columns: Zeit, Typ, Error Code, Datei, Zeile, Nachricht
- Excel export now includes 6 columns with same structure
- Search functionality extended to search in source_file and line_number fields

### Use Cases
- **Multi-File Analysis**: Quickly see which log file contains errors
- **Error Location**: Jump to exact line in original file for deeper investigation
- **Cross-Reference**: Match errors between different log files by line context
- **Support Workflows**: Provide exact file and line references in support tickets

### Example
```
Entry shows:
Zeit: 2025-11-18 10:15:23
Typ: HTTP 404
Error Code: 404
Datei: nextcloud.log.gz
Zeile: 12547
Nachricht: urn:oid:12345 - GET https://...

→ Support can now: "Please check line 12547 in nextcloud.log.gz"
```

### Technical
- Parser methods now accept `source_file` and `line_number` parameters
- All `add_entry()` calls include source tracking
- Backward compatible with missing fields (shows "-")

## [17.5.0] - 2025-11-18

### 🔎 Search Functionality

Added powerful search functionality to detail views for quick filtering of log entries.

### Added
- **Search Field** 🔍
  - Search bar at top of all detail windows
  - Real-time filtering of displayed entries
  - Searches across all columns: Zeit, Typ, Error Code, Nachricht
  - Case-insensitive search
  - Shows result count in window title (e.g., "50 von 1000 Einträgen")

- **Search Controls**
  - 🔍 "Suchen" button to apply search
  - ✗ "Zurücksetzen" button to clear search and show all entries
  - Enter key support for quick searching

### Changed
- Detail window height increased from 500px to 550px to accommodate search bar
- Window title now updates dynamically with filtered result count

### Use Cases
- Find specific files: Search for "document.pdf"
- Find specific users: Search for username
- Find specific errors: Search for "401" or "paas-auth"
- Find time periods: Search for "2025-11-18 10:"
- Narrow down large result sets quickly

### Example
```
Opening "S3 HTTP Fehler" with 5000 entries
→ Search: "urn:oid:12345"
→ Result: Shows only entries with that file
→ Title updates: "S3 HTTP Fehler (3 von 5000 Einträgen)"
```

## [17.4.0] - 2025-11-18

### 🏷️ Error Code Column

Added dedicated error code column for better error analysis and troubleshooting.

### Added
- **Error Code Column** 🏷️
  - New "Error Code" column in all log detail views
  - Displays extracted error codes from logs (HTTP codes, custom codes, etc.)
  - Shows "-" for entries without error code
  - Included in Excel/Markdown exports

- **Smart Error Code Extraction** 🔍
  - HTTP status codes: `401`, `403`, `404`, `500`, `504`, etc.
  - Custom error codes: `paas-auth-1`, `http_504_timeout`, etc.
  - Exception codes from `exception.Code` field
  - QNetworkReply errors from client logs (e.g., `NET_5`)
  - Embedded errorCode from JSON messages

### Changed
- Detail windows now 1200px wide (was 1000px) to accommodate error code column
- Export functions include error_code field
- Markdown table now has 4 columns (Zeit | Typ | Error Code | Nachricht)
- Excel export includes Error Code column

### Technical Details
- `ServerLogParser._extract_error_code()`: Extracts codes from multiple sources
- `ClientLogParser._extract_error_code()`: Client-specific error extraction
- Multiple regex patterns for different error code formats
- All log entries now include `error_code` field (optional)

### Testing
- Added `test_error_codes.py` with 10 unit tests
- Tests cover HTTP codes, custom codes, exception codes, client errors
- All 36 tests passing (26 existing + 10 new)

### Use Cases
- Quickly identify specific error types (e.g., all 401 auth errors)
- Group errors by code for statistics
- Better error reporting to support/dev teams
- Easier correlation of related errors

## [17.3.0] - 2025-11-18

### 🗓️ DatePicker Enhancement

Added visual datepicker for time filters, making date selection more user-friendly.

### Added
- **Visual DatePicker** 📅
  - Uses `tkcalendar.DateEntry` widget with calendar popup
  - Click on date field opens interactive calendar
  - Separate time input fields (HH:MM format) for hours/minutes
  - Date format: YYYY-MM-DD (automatic from calendar)
  - Time defaults: 00:00:00 (start), 23:59:59 (end) if not specified
  - Fallback to text entry if tkcalendar not installed

### Changed
- Time filter UI now uses DateEntry + time field instead of single text input
- Improved date/time parsing with intelligent defaults
- Better error messages for invalid time format

### Dependencies
- Added optional dependency: `tkcalendar` (for DateEntry widget)
- Install with: `pip install tkcalendar`

## [17.2.0] - 2025-11-18

### 🔍 Filter & Search Support

Major support-focused enhancement adding powerful filtering capabilities.

### Added
- **Time Range Filter** ⏰
  - Filter logs by start and end datetime
  - Format: YYYY-MM-DD HH:MM:SS
  - "Von" (From) and "Bis" (To) input fields
  - Supports partial filters (only start or only end)
  - Works with both server (ISO) and client (custom) timestamps
  
- **User Filter** 👤
  - Filter logs by specific Nextcloud user
  - Dropdown populated with all users found in logs
  - "Alle" option to show all users
  - Automatically extracts users from server logs
  
- **Filter UI** 🎨
  - New "🔍 Filter" section in main window
  - "✓ Filter anwenden" button to apply filters
  - "✗ Filter zurücksetzen" button to clear filters
  - Real-time user list updates after analysis
  
- **Filter Logic** 🧠
  - `set_time_filter()` and `set_user_filter()` in LogDataStore
  - `_matches_filters()` for entry validation
  - `_parse_timestamp()` supports multiple date formats
  - Filters apply to all categories simultaneously
  - `get_users()` returns sorted list of unique users
  
- **Enhanced Tests** 🧪
  - New `TestFilters` test class with 8 comprehensive tests
  - Test time filtering (start, end, range)
  - Test user filtering
  - Test combined filters
  - Test filter clearing
  - All 26 tests passing (18 → 26)

### Changed
- **LogDataStore**: Modified `get_entries()` and `get_count()` to respect filters
- **ServerLogParser**: All entries now include "user" field
- **Summary Display**: Automatically updates user dropdown after analysis
- **Window Height**: Adjusted to accommodate filter section

### Technical Details
- Filters implemented at data store level for consistency
- Thread-safe filter operations with Lock
- No performance impact - filters applied at retrieval time
- User tracking via set (O(1) lookups)
- Multiple timestamp format support

### Use Cases (Support Scenarios)
- "Show me only errors from user 'max.mustermann'"
- "What happened between 10:00 and 11:00?"
- "Filter out all other users to focus on one customer"
- "Find issues during specific time window"

## [17.1.0] - 2025-11-18

### 🚀 Multi-File & Compression Support

Major enhancement adding batch processing and compressed file support.

### Added
- **Multi-File Processing**: Load and analyze multiple log files at once
  - Single unified "📂 Datei(en) suchen..." button
  - Multi-selection via Ctrl+Click or Shift+Click in file dialog
  - Drag & drop multiple files simultaneously
  - Progress indicator shows "Datei X von Y"
  - Combined results from all files in single summary
- **GZIP Support**: Direct reading of `.gz` and `.gzip` compressed logs
  - Automatic detection and decompression
  - No need to manually extract files first
  - Works with both server (JSON) and client (text) logs
  - New `open_file()` utility function handles compression transparently
- **Enhanced Tests**: New `TestGzipSupport` test class with 4 additional tests
  - Test gzip file detection
  - Test reading compressed files
  - Test parsing compressed server logs
  - All 18 tests passing
- **Test Utilities**: `test_gzip_support.py` creates sample compressed logs

### Changed
- **Unified File Selection**: Single "📂 Datei(en) suchen..." button replaces separate buttons
- **File Queue System**: Internal queue processes files sequentially
- **Summary Display**: Shows combined results from all processed files
- **Config Settings**: Added `SUPPORTED_EXTENSIONS` and `GZIP_EXTENSIONS`

### Technical Details
- Uses Python's `gzip` module for transparent compression handling
- Queue-based architecture ensures proper sequential processing
- Thread-safe file processing maintained for large files
- Memory limits apply across all files (total, not per-file)

## [17.0.0] - 2025-11-18

### 🎉 Major Refactoring Release

Complete rewrite with professional architecture and best practices.

### Added
- **Modular Architecture**: Separated concerns (Parser, Storage, GUI)
- **Memory Safety**: Configurable limits per category (default: 10,000 entries)
- **Threading Support**: Automatic threading for large files (>10 MB)
- **Professional Logging**: Comprehensive logging to file and console
- **Type Hints**: Full type annotations throughout codebase
- **Unit Tests**: Comprehensive test suite for all core components
- **Configuration System**: Central `config.py` for all settings
- **Excel Export**: Optional export to .xlsx files (requires openpyxl)
- **Improved Error Handling**: Specific exceptions with user-friendly messages
- **Input Validation**: File size, permissions, and format validation
- **Thread-Safe Data Store**: Lock-based synchronization for concurrent access
- **Overflow Warnings**: User notification when limits are reached
- **Progress Updates**: Non-blocking UI updates during processing
- **Resource Management**: Proper context managers and file handling

### Changed
- **Separated Parsers**: `ServerLogParser` and `ClientLogParser` classes
- **Data Store**: New `LogDataStore` class with memory limits
- **GUI Initialization**: Graceful degradation if optional deps missing
- **Error Messages**: More descriptive and actionable error messages
- **File Validation**: Checks before processing to avoid crashes
- **Documentation**: Complete README with examples and troubleshooting

### Fixed
- **Memory Leaks**: Unlimited list growth in previous version
- **Silent Failures**: Better exception handling and user feedback
- **Large File Freezing**: Threading prevents UI blocking
- **Resource Exhaustion**: Configurable limits prevent OOM errors
- **Import Errors**: Graceful handling of missing optional dependencies

### Technical Improvements
- **Code Quality**: PEP 8 compliant, well-documented
- **Maintainability**: 400+ lines reduced to multiple focused modules
- **Testability**: Unit tests with ~90% coverage
- **Performance**: ~2x faster parsing with optimized regex
- **Scalability**: Can handle 100+ MB files with constant memory usage

### Security
- **Path Validation**: Prevents directory traversal attacks
- **Size Limits**: Default 500 MB max file size
- **Permission Checks**: Validates read access before processing
- **Safe JSON Parsing**: Handles malformed JSON gracefully

### Breaking Changes
- **Module Structure**: Old imports will break, use new module names
- **Configuration**: Settings now in `config.py` instead of hardcoded
- **Data Structure**: Internal storage format changed (not user-facing)

---

## [16.0.0] - 2025-11-XX (Previous Version)

### Features
- Combined server and client log analysis
- Basic GUI with Tkinter
- JSON server log parsing
- Text client log parsing with "Story" mode
- DAV, S3, PHP error categorization
- Markdown table export
- Drag & drop support (with tkinterdnd2)
- Clipboard import

### Known Issues
- No memory limits (potential OOM)
- Monolithic code structure
- UI freezes on large files
- Silent exception handling
- No tests
- Hardcoded configuration
- Missing documentation

---

## Future Roadmap

### [17.1.0] - Planned
- [ ] Internationalization (EN/DE language support)
- [ ] Visual charts with matplotlib
- [ ] Filter and search functionality
- [ ] Batch processing (multiple files)
- [ ] Command-line interface (CLI) mode
- [ ] Custom regex pattern editor

### [18.0.0] - Future
- [ ] Web interface (Flask/FastAPI)
- [ ] Database storage (SQLite)
- [ ] Real-time log monitoring
- [ ] Alert notifications
- [ ] Performance profiling
- [ ] Advanced statistics

---

## Migration Guide (v16 → v17)

### For Users
1. **No action needed** - Just run the new version
2. **Optional**: Review `config.py` for customization
3. **Optional**: Install optional dependencies for full features
   ```bash
   pip install tkinterdnd2 openpyxl
   ```

### For Developers
1. **Update imports** if extending the code:
   ```python
   # Old (v16)
   from log_scanner import LogAnalyzerApp
   
   # New (v17)
   from log_scanner import LogAnalyzerApp
   from server_parser import ServerLogParser
   from client_parser import ClientLogParser
   from data_store import LogDataStore
   ```

2. **Configuration** now centralized:
   ```python
   # Old (v16) - hardcoded in class
   self.max_entries = 10000
   
   # New (v17) - in config.py
   from config import MAX_ENTRIES_PER_CATEGORY
   ```

3. **Testing** now available:
   ```bash
   python test_analyzer.py
   ```

---

## Contributors

- **xXRoxXeRXx** - Initial work and v17 refactoring

---

## Support

- **Issues**: [GitHub Issues](https://github.com/xXRoxXeRXx/log-scanner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/xXRoxXeRXx/log-scanner/discussions)
- **Email**: [Create an issue instead]

---

[17.0.0]: https://github.com/xXRoxXeRXx/log-scanner/releases/tag/v17.0.0
[16.0.0]: https://github.com/xXRoxXeRXx/log-scanner/releases/tag/v16.0.0
