"""
Nextcloud Log Analyzer - Refactored Version 17.0
Main application with GUI
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import time
import re
import threading
import logging
from typing import Optional, List
from enum import Enum

# Local imports
from config import *
from data_store import LogDataStore
from server_parser import ServerLogParser
from client_parser import ClientLogParser

# Optional dependencies
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    logging.warning("tkinterdnd2 not available - drag & drop disabled")

try:
    from openpyxl import Workbook
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    logging.warning("openpyxl not installed - Excel export unavailable")

# Setup logging
logger = setup_logging()


class LogFormat(Enum):
    """Supported log formats"""
    JSON_SERVER = "json_server"
    TEXT_CLIENT = "text_client"
    UNKNOWN = "unknown"


class LogAnalyzerApp(TkinterDnD.Tk if HAS_DND else tk.Tk):
    """
    Main application window for Nextcloud Log Analyzer.
    
    Features:
    - Server and client log parsing
    - Memory-safe operation with configurable limits
    - Threading for large files
    - Drag & drop support (if available)
    - Detailed error reporting
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Initialize data store and parsers
        self.data_store = LogDataStore()
        self.server_parser = ServerLogParser(self.data_store)
        self.client_parser = ClientLogParser(self.data_store)
        
        # Thread management
        self.analysis_thread: Optional[threading.Thread] = None
        self.analysis_running = False
        
        # Setup GUI
        self.setup_gui()
        
        logger.info("Application initialized")
    
    def setup_gui(self):
        """Create and configure GUI elements."""
        # File input frame
        file_frame = ttk.Frame(self, padding=10)
        file_frame.pack(fill="x")
        
        # Drop target / file list
        self.drop_target = tk.Listbox(file_frame, height=3, relief="sunken", borderwidth=2)
        self.drop_target.pack(fill="x", expand=True, side="left", padx=(0, 10))
        
        if HAS_DND and ENABLE_DRAG_DROP:
            self.drop_target.insert(tk.END, " 📁 Ziehe Server- (JSON) oder Client- (Text) Logs hierher...")
            self.drop_target.drop_target_register(DND_FILES)
            self.drop_target.dnd_bind('<<Drop>>', self.on_drop)
        else:
            self.drop_target.insert(tk.END, " 📁 Drag & Drop nicht verfügbar - nutze 'Datei suchen'")
        
        # Button frame
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(side="right", anchor="n")
        
        ttk.Button(btn_frame, text="📂 Datei suchen...", command=self.browse_file).pack(fill="x", pady=(0, 5))
        
        if ENABLE_CLIPBOARD_IMPORT:
            ttk.Button(btn_frame, text="📋 Aus Zwischenablage", command=self.paste_and_analyze).pack(fill="x")
        
        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)
        
        # Summary text area
        self.summary_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, height=30, font=FONT_CONSOLE
        )
        self.summary_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Configure text tags
        self._configure_text_tags()
        
        # Bind click handlers
        self._setup_click_handlers()
    
    def _configure_text_tags(self):
        """Configure text formatting tags."""
        self.summary_text.tag_configure("h1", font=FONT_H1, spacing1=10)
        self.summary_text.tag_configure("h2", font=FONT_H2, spacing1=5)
        self.summary_text.tag_configure("error", foreground=COLORS['error'])
        self.summary_text.tag_configure("warning", foreground=COLORS['warning'])
        self.summary_text.tag_configure("info", foreground=COLORS['info'])
        self.summary_text.tag_configure("debug", foreground=COLORS['debug'])
        self.summary_text.tag_configure("story", foreground=COLORS['story'], font=(FONT_DEFAULT[0], 10, "bold"))
        self.summary_text.tag_configure("clickable", foreground=COLORS['clickable'], underline=True)
        
        # Clickable behavior
        self.summary_text.tag_bind("clickable", "<Enter>", 
            lambda e: self.summary_text.config(cursor="hand2"))
        self.summary_text.tag_bind("clickable", "<Leave>", 
            lambda e: self.summary_text.config(cursor=""))
    
    def _setup_click_handlers(self):
        """Bind click handlers for categories."""
        categories = [
            ("s3_filter", "s3_errors", "S3 HTTP Fehler"),
            ("dav_filter", "dav_errors", "DAV-Fehler"),
            ("php_filter", "php_errors", "PHP Fehler"),
            ("obj_filter", "objectstore_errors", "Objectstore Fehler"),
            ("other_filter", "other_errors", "Andere Fehler"),
            ("warn_filter", "server_warnings", "Server Warnungen"),
            ("info_filter", "server_info", "Server Infos"),
            ("debug_filter", "server_debug", "Server Debug"),
            ("client_err_filter", "client_errors", "Client Fehler"),
            ("client_story_filter", "client_events", "Client Sync-Verlauf")
        ]
        
        for tag, key, title in categories:
            self.summary_text.tag_bind(tag, "<Button-1>", 
                lambda e, k=key, t=title: self.open_table_window(k, t))
    
    def browse_file(self):
        """Open file dialog and start analysis."""
        file_types = [
            ("Log Dateien", " ".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS)),
            ("Alle Dateien", "*.*")
        ]
        path = filedialog.askopenfilename(filetypes=file_types)
        if path:
            self.start_analysis(path, is_file=True)
    
    def on_drop(self, event):
        """Handle drag & drop event."""
        path = event.data.strip('{}')
        if os.path.isfile(path):
            self.start_analysis(path, is_file=True)
        else:
            messagebox.showerror("Fehler", "Ungültige Datei")
    
    def paste_and_analyze(self):
        """Analyze text from clipboard."""
        try:
            text = self.clipboard_get()
            if text and text.strip():
                lines = text.splitlines()
                self.start_analysis(lines, is_file=False)
            else:
                messagebox.showwarning("Warnung", "Zwischenablage ist leer")
        except tk.TclError:
            messagebox.showerror("Fehler", "Kein Text in Zwischenablage")
    
    def start_analysis(self, source, is_file: bool):
        """
        Start log analysis with validation.
        
        Args:
            source: File path (str) or line list (List[str])
            is_file: True if source is a file path
        """
        # Prevent concurrent analysis
        if self.analysis_running:
            messagebox.showwarning("Warnung", "Analyse läuft bereits")
            return
        
        # Validate file
        if is_file:
            validation_error = self._validate_file(source)
            if validation_error:
                messagebox.showerror("Fehler", validation_error)
                return
        
        # Reset UI and data
        self._reset_for_new_analysis()
        
        # Determine if threading is needed
        use_threading = False
        if is_file and ENABLE_THREADING:
            file_size = os.path.getsize(source)
            use_threading = file_size > get_large_file_threshold_bytes()
        
        if use_threading:
            self._start_threaded_analysis(source, is_file)
        else:
            self._start_sync_analysis(source, is_file)
    
    def _validate_file(self, filepath: str) -> Optional[str]:
        """
        Validate file before analysis.
        
        Args:
            filepath: Path to file
            
        Returns:
            Error message or None if valid
        """
        # Check existence
        if not os.path.isfile(filepath):
            return f"Datei nicht gefunden:\n{filepath}"
        
        # Check permissions
        if not os.access(filepath, os.R_OK):
            return f"Keine Leseberechtigung:\n{filepath}"
        
        # Check size
        try:
            size = os.path.getsize(filepath)
            max_size = get_max_file_size_bytes()
            if size > max_size:
                size_mb = size / (1024 * 1024)
                max_mb = max_size / (1024 * 1024)
                return (f"Datei zu groß: {size_mb:.1f} MB\n"
                       f"Maximum: {max_mb:.0f} MB\n\n"
                       f"Passe MAX_FILE_SIZE_MB in config.py an.")
        except OSError as e:
            return f"Fehler beim Lesen der Dateigröße:\n{e}"
        
        # Check extension
        _, ext = os.path.splitext(filepath)
        if ext.lower() not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Ungewöhnliche Dateierweiterung: {ext}")
        
        return None
    
    def _reset_for_new_analysis(self):
        """Reset UI and data store for new analysis."""
        self.progress['value'] = 0
        self.summary_text.delete(1.0, tk.END)
        self.data_store.clear()
        self.summary_text.insert(tk.END, "🔍 Analysiere...\n", "h1")
        self.update_idletasks()
    
    def _start_sync_analysis(self, source, is_file: bool):
        """Run analysis synchronously (blocking)."""
        try:
            self._run_analysis(source, is_file)
        except Exception as e:
            logger.exception("Analysis failed")
            self._show_analysis_error(e)
    
    def _start_threaded_analysis(self, source, is_file: bool):
        """Run analysis in background thread."""
        self.analysis_running = True
        self.analysis_thread = threading.Thread(
            target=self._run_analysis_threaded,
            args=(source, is_file),
            daemon=True
        )
        self.analysis_thread.start()
        logger.info("Started threaded analysis")
    
    def _run_analysis_threaded(self, source, is_file: bool):
        """Thread worker for analysis."""
        try:
            self._run_analysis(source, is_file)
        except Exception as e:
            logger.exception("Threaded analysis failed")
            self.after(0, lambda: self._show_analysis_error(e))
        finally:
            self.analysis_running = False
    
    def _run_analysis(self, source, is_file: bool):
        """
        Core analysis logic.
        
        Args:
            source: File path or line list
            is_file: True if source is a file
        """
        start_time = time.time()
        line_count = 0
        bytes_read = 0
        
        # Open file or use provided lines
        if is_file:
            with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                # Detect format
                first_line = f.readline()
                log_format = self._detect_format(first_line)
                f.seek(0)
                
                # Get file size for progress
                file_size = os.path.getsize(source)
                self.progress['maximum'] = file_size
                
                # Process lines
                for line in f:
                    line_count += 1
                    bytes_read += len(line.encode('utf-8', 'ignore'))
                    
                    self._parse_line(line, log_format)
                    
                    # Update progress periodically
                    if line_count % PROGRESS_UPDATE_INTERVAL == 0:
                        self._update_progress(bytes_read)
        else:
            # Process lines from clipboard
            self.progress['maximum'] = len(source)
            log_format = self._detect_format(source[0] if source else "")
            
            for line in source:
                line_count += 1
                self._parse_line(line, log_format)
                
                if line_count % PROGRESS_UPDATE_INTERVAL == 0:
                    self._update_progress(line_count)
        
        # Finalize
        duration = time.time() - start_time
        self._update_progress(self.progress['maximum'])
        self._show_summary(line_count, log_format, duration)
        
        logger.info(f"Analysis complete: {line_count} lines in {duration:.2f}s")
    
    def _detect_format(self, first_line: str) -> LogFormat:
        """
        Detect log format from first line.
        
        Args:
            first_line: First line of log
            
        Returns:
            Detected LogFormat
        """
        line = first_line.strip()
        
        if line.startswith("{") and line.endswith("}"):
            return LogFormat.JSON_SERVER
        
        if re.match(r'^\d{4}-\d{2}-\d{2}', line):
            return LogFormat.TEXT_CLIENT
        
        logger.warning(f"Unknown log format: {line[:50]}")
        return LogFormat.UNKNOWN
    
    def _parse_line(self, line: str, log_format: LogFormat):
        """
        Parse a single log line.
        
        Args:
            line: Log line
            log_format: Detected format
        """
        if log_format == LogFormat.JSON_SERVER:
            self.server_parser.parse_line(line)
        elif log_format == LogFormat.TEXT_CLIENT:
            self.client_parser.parse_line(line)
    
    def _update_progress(self, value: int):
        """
        Update progress bar (thread-safe).
        
        Args:
            value: Progress value
        """
        if threading.current_thread() is threading.main_thread():
            self.progress['value'] = value
            self.update_idletasks()
        else:
            self.after(0, lambda: self._update_progress(value))
    
    def _show_summary(self, line_count: int, log_format: LogFormat, duration: float):
        """
        Display analysis summary.
        
        Args:
            line_count: Number of processed lines
            log_format: Detected log format
            duration: Analysis duration in seconds
        """
        def _display():
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, 
                f"✅ Fertig in {duration:.2f}s ({line_count:,} Zeilen)\n"
                f"Format: {log_format.value}\n\n", "h2")
            
            if log_format == LogFormat.TEXT_CLIENT:
                self._show_client_summary()
            elif log_format == LogFormat.JSON_SERVER:
                self._show_server_summary()
            else:
                self.summary_text.insert(tk.END, 
                    "⚠️ Unbekanntes Format - keine Analyse möglich\n", "warning")
            
            # Show overflow warnings
            self._show_overflow_warnings()
        
        if threading.current_thread() is threading.main_thread():
            _display()
        else:
            self.after(0, _display)
    
    def _show_client_summary(self):
        """Display client log summary."""
        self.summary_text.insert(tk.END, "📱 Client Analyse:\n", "h2")
        
        events = self.data_store.get_count("client_events")
        errors = self.data_store.get_count("client_errors")
        
        if events:
            self.summary_text.insert(tk.END, 
                f"  ▶ Client Sync-Verlauf: {events} Ereignisse\n",
                ("story", "clickable", "client_story_filter"))
        
        if errors:
            self.summary_text.insert(tk.END,
                f"  ▶ Client Fehler/Warnungen: {errors}x\n",
                ("error", "clickable", "client_err_filter"))
        
        if not events and not errors:
            self.summary_text.insert(tk.END, 
                "  Keine relevanten Client-Ereignisse gefunden.\n")
    
    def _show_server_summary(self):
        """Display server log summary."""
        self.summary_text.insert(tk.END, "🖥️ Server Analyse:\n", "h2")
        
        # Errors
        categories_error = [
            ("s3_errors", "S3 HTTP Fehler", "s3_filter", "error"),
            ("dav_errors", "DAV Fehler", "dav_filter", "error"),
            ("php_errors", "PHP Fehler", "php_filter", "error"),
            ("objectstore_errors", "Objectstore Fehler", "obj_filter", "error"),
            ("other_errors", "Andere Fehler", "other_filter", "error"),
        ]
        
        # Other levels
        categories_other = [
            ("server_warnings", "Warnungen", "warn_filter", "warning"),
            ("server_info", "Infos", "info_filter", "info"),
            ("server_debug", "Debug", "debug_filter", "debug"),
        ]
        
        found_any = False
        
        for key, label, tag, style in categories_error + categories_other:
            count = self.data_store.get_count(key)
            if count > 0:
                found_any = True
                self.summary_text.insert(tk.END, f"  ▶ {label}: {count}x\n",
                    (style, "clickable", tag))
        
        if not found_any:
            self.summary_text.insert(tk.END, 
                "  Keine kategorisierten Einträge gefunden.\n")
    
    def _show_overflow_warnings(self):
        """Display warnings for categories that hit limits."""
        stats = self.data_store.get_statistics()
        overflow_categories = [
            (cat, data['overflow']) 
            for cat, data in stats.items() 
            if data['overflow'] > 0
        ]
        
        if overflow_categories:
            self.summary_text.insert(tk.END, "\n⚠️ Speicher-Limits erreicht:\n", "warning")
            for cat, overflow in overflow_categories:
                self.summary_text.insert(tk.END,
                    f"  • {cat}: {overflow:,} Einträge verworfen\n", "warning")
            self.summary_text.insert(tk.END,
                f"\nErhöhe MAX_ENTRIES_PER_CATEGORY in config.py für mehr Daten.\n", "info")
    
    def _show_analysis_error(self, error: Exception):
        """
        Display analysis error to user.
        
        Args:
            error: Exception that occurred
        """
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "❌ Fehler bei Analyse:\n\n", "h1")
        
        error_type = type(error).__name__
        error_msg = str(error)
        
        self.summary_text.insert(tk.END, f"{error_type}: {error_msg}\n", "error")
        
        logger.error(f"Analysis error: {error_type}: {error_msg}")
    
    def open_table_window(self, category: str, title: str):
        """
        Open detailed table window for a category.
        
        Args:
            category: Data category key
            title: Window title
        """
        entries = self.data_store.get_entries(category)
        
        if not entries:
            messagebox.showinfo("Info", f"Keine Einträge in Kategorie '{title}'")
            return
        
        # Create window
        win = tk.Toplevel(self)
        win.geometry("1000x500")
        win.title(f"{title} ({len(entries):,} Einträge)")
        
        # Create treeview
        tree = ttk.Treeview(win, columns=("time", "type", "msg"), show="headings")
        tree.heading("time", text="Zeitstempel")
        tree.heading("type", text="Typ/App")
        tree.heading("msg", text="Nachricht / Datei")
        
        tree.column("time", width=180, stretch=False)
        tree.column("type", width=200, stretch=False)
        tree.column("msg", width=600)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        
        # Populate
        for entry in entries:
            tree.insert("", "end", values=(
                entry.get("time", ""),
                entry.get("type", ""),
                entry.get("msg", "")
            ))
        
        # Export button
        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="📋 Kopieren (Markdown)", 
                  command=lambda: self._copy_as_markdown(tree)).pack(side="left", padx=5)
        
        if HAS_OPENPYXL and ENABLE_EXCEL_EXPORT:
            ttk.Button(btn_frame, text="📊 Exportieren (Excel)",
                      command=lambda: self._export_to_excel(entries, title)).pack(side="left", padx=5)
    
    def _copy_as_markdown(self, tree: ttk.Treeview):
        """
        Copy treeview content as Markdown table.
        
        Args:
            tree: Treeview widget
        """
        self.clipboard_clear()
        
        # Header
        markdown = "| Zeit | Typ | Nachricht |\n|---|---|---|\n"
        
        # Rows
        for item_id in tree.get_children():
            values = tree.item(item_id, 'values')
            # Escape pipes in content
            escaped = [str(v).replace('|', '\\|') for v in values]
            markdown += f"| {escaped[0]} | {escaped[1]} | {escaped[2]} |\n"
        
        self.clipboard_append(markdown)
        messagebox.showinfo("✓ Kopiert", "Markdown-Tabelle in Zwischenablage kopiert!")
    
    def _export_to_excel(self, entries: List[dict], title: str):
        """
        Export entries to Excel file.
        
        Args:
            entries: List of entry dictionaries
            title: Sheet title
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("Alle", "*.*")],
            initialfile=f"{title.replace(' ', '_')}.xlsx"
        )
        
        if not filepath:
            return
        
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = title[:31]  # Excel limit
            
            # Headers
            ws.append(["Zeitstempel", "Typ", "Nachricht"])
            
            # Data
            for entry in entries:
                ws.append([
                    entry.get("time", ""),
                    entry.get("type", ""),
                    entry.get("msg", "")
                ])
            
            wb.save(filepath)
            messagebox.showinfo("✓ Exportiert", f"Erfolgreich nach Excel exportiert:\n{filepath}")
            logger.info(f"Exported {len(entries)} entries to {filepath}")
            
        except Exception as e:
            logger.exception("Excel export failed")
            messagebox.showerror("Fehler", f"Excel-Export fehlgeschlagen:\n{e}")


def main():
    """Application entry point."""
    logger.info("Starting Nextcloud Log Analyzer")
    
    # Check dependencies
    if not HAS_DND:
        logger.warning("tkinterdnd2 not installed - drag & drop unavailable")
    if not HAS_OPENPYXL:
        logger.warning("openpyxl not installed - Excel export unavailable")
    
    # Create and run app
    app = LogAnalyzerApp()
    app.mainloop()
    
    logger.info("Application closed")


if __name__ == "__main__":
    main()
