# 🔍 Nextcloud Log Analyzer v17.4

Eine professionelle Desktop-Anwendung zur Analyse von Nextcloud Server- und Client-Logs mit grafischer Benutzeroberfläche.

## ✨ Features

### Kernfunktionen
- 📊 **Dual-Format-Support**: Analysiert JSON (Server) und Text (Client) Logs
- 🗜️ **Kompression**: Direkte Verarbeitung von `.gz` / `.gzip` Dateien
- 📁 **Multi-File**: Mehrere Log-Dateien gleichzeitig analysieren
- 🔍 **Filter**: Zeit- und User-basierte Filterung für präzise Analysen
- �️ **Error Codes**: Dedizierte Spalte für HTTP-Codes, Custom-Codes und Exception-Codes
- 🗓️ **DatePicker**: Visueller Kalender für einfache Datumsauswahl
- �🎯 **Intelligente Kategorisierung**: Automatische Fehlerklassifizierung (S3, DAV, PHP, etc.)
- 📖 **Client Story Mode**: Chronologischer Sync-Verlauf mit Ereignissen
- 🚀 **High Performance**: Threading für große Dateien (>10 MB)
- 💾 **Memory-Safe**: Konfigurierbare Speicher-Limits (Standard: 10.000 Einträge/Kategorie)
- 🎨 **Moderne GUI**: Intuitive Benutzeroberfläche mit farbiger Kategorisierung

### Erweiterte Features
- 🖱️ **Drag & Drop**: Dateien (auch mehrere) einfach in die Anwendung ziehen
- 📋 **Clipboard-Support**: Logs direkt aus der Zwischenablage analysieren
- 📥 **Export**: Markdown-Tabellen & Excel-Export (inkl. Error Codes)
- ⚙️ **Konfigurierbar**: Alle Limits und Einstellungen anpassbar
- 📝 **Professionelles Logging**: Detaillierte Log-Dateien für Debugging

## 🏗️ Architektur

### Modular & Wartbar

```
log-scanner/
├── log_analyzer_v17.py # Haupt-GUI-Anwendung
├── log_scanner.py      # Convenience Wrapper
├── config.py           # Zentrale Konfiguration
├── data_store.py       # Thread-sichere Datenverwaltung
├── server_parser.py    # JSON Server-Log Parser
├── client_parser.py    # Text Client-Log Parser
├── test_analyzer.py    # Unit Tests
├── test_error_codes.py # Error Code Tests
└── requirements.txt    # Dependencies
```

### Design Patterns
- **Separation of Concerns**: Parser, Storage, GUI getrennt
- **Thread-Safety**: Lock-basierte Synchronisation
- **Type Hints**: Vollständige Type Annotations
- **Defensive Programming**: Umfassende Input-Validierung
- **Resource Management**: Context Managers & Limits

## 📦 Installation

### Voraussetzungen
- Python 3.8 oder höher
- Windows, Linux oder macOS

### Schnellinstallation

```bash
# 1. Repository klonen
git clone https://github.com/xXRoxXeRXx/log-scanner.git
cd log-scanner

# 2. Dependencies installieren (optional, aber empfohlen)
pip install -r requirements.txt

# 3. Anwendung starten
python log_scanner.py
```

**Hinweis:** Falls `tkinter` fehlt (meist nur Linux):
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# macOS (mit Homebrew Python)
brew install python-tk
```

### Dependencies

#### Pflicht
- **Python 3.8+** mit `tkinter` (normalerweise enthalten)
  - Windows/macOS: Bereits mit Python installiert
  - Linux: Siehe Installation oben

#### Optional (empfohlen)
- `tkinterdnd2>=0.3.0` - Drag & Drop Funktionalität 🖱️
- `openpyxl>=3.0.0` - Excel Export 📊
- `tkcalendar>=1.6.0` - Visueller Datepicker für Zeitfilter 📅

**Installation der optionalen Pakete:**
```bash
pip install -r requirements.txt
# oder einzeln:
pip install tkinterdnd2 openpyxl tkcalendar
```

**Ohne optionale Pakete:**
Die App funktioniert auch ohne diese - Features sind dann deaktiviert:
- Ohne `tkinterdnd2`: Kein Drag & Drop (Datei-Button funktioniert)
- Ohne `openpyxl`: Kein Excel-Export (Markdown-Export funktioniert)
- Ohne `tkcalendar`: Text-Datumseingabe statt Kalender-Widget

## 🚀 Verwendung

### Grundlegende Nutzung

1. **Anwendung starten**
   ```powershell
   # Empfohlen - Einfacher Startbefehl
   python log_scanner.py
   
   # Oder direkt die Hauptdatei
   python log_analyzer_v17.py
   
   # Oder mit Batch-Datei (Windows)
   start_v17.bat
   ```

2. **Log-Datei(en) laden**
   - 🖱️ **Drag & Drop**: Eine oder mehrere Dateien ins Fenster ziehen
   - 📂 **Datei(en) Browser**: "📂 Datei(en) suchen..." Button
     - Einzelne Datei: Einfach anklicken
     - Mehrere Dateien: **Strg+Klick** oder **Shift+Klick** zum Markieren
   - 📋 **Clipboard**: "📋 Aus Zwischenablage" Button

3. **Unterstützte Dateiformate**
   - `.log` - Reguläre Log-Dateien
   - `.txt` - Text-Dateien
   - `.json` - JSON-Logs
   - `.gz` / `.gzip` - **Komprimierte Logs** (werden automatisch entpackt!)

4. **Ergebnisse anzeigen**
   - Klicke auf Kategorien für Details
   - Exportiere Tabellen als Markdown oder Excel
   - Bei mehreren Dateien: Kombinierte Analyse aller Logs

### Unterstützte Log-Formate

#### Server Logs (JSON)
```json
{"level":3,"time":"2025-01-01T12:00:00","message":"HTTP/1.1 404","app":"objectstore"}
```

**Kategorien:**
- S3 HTTP Fehler (404, 500, etc.)
- WebDAV Fehler
- PHP Fehler
- Objectstore Fehler
- Generische Fehler (Level 3)
- Warnungen (Level 2)
- Infos (Level 1)
- Debug (Level 0)

#### Client Logs (Text)
```
2025-01-01 12:00:00:000 [ info sync.engine ]: >========== Sync started for folder [/Documents]
```

**Story Events:**
- Sync Start/Ende
- Upload/Download Fortschritt
- Server-Änderungen (ETag)
- Fehler & Warnungen
- Benutzerinteraktionen

## ⚙️ Konfiguration

Bearbeite `config.py` für Anpassungen:

### Performance & Memory
```python
MAX_FILE_SIZE_MB = 500              # Max. Dateigröße
MAX_ENTRIES_PER_CATEGORY = 10000    # Einträge pro Kategorie
LARGE_FILE_THRESHOLD_MB = 10        # Threading-Schwelle
```

### UI Einstellungen
```python
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 800
FONT_CONSOLE = ("Consolas", 10)
```

### Logging
```python
LOG_LEVEL = logging.INFO
LOG_FILE = 'log_analyzer.log'
```

### Feature Flags
```python
ENABLE_THREADING = True
ENABLE_EXCEL_EXPORT = True
ENABLE_CLIPBOARD_IMPORT = True
ENABLE_DRAG_DROP = True
```

## 🔍 Filter verwenden

Die App bietet leistungsstarke Filter für Support-Szenarien:

### Zeitfilter ⏰ mit Datepicker 📅

**Visueller Datepicker:** Klick auf das Datumsfeld öffnet einen interaktiven Kalender

**Format:**
- **Datum:** Auswahl über Kalender (YYYY-MM-DD)
- **Zeit:** Optionales Eingabefeld für Stunde:Minute (HH:MM)
- **Automatische Defaults:**
  - Startzeit ohne Zeit-Eingabe: `00:00:00` (Tagesbeginn)
  - Endzeit ohne Zeit-Eingabe: `23:59:59` (Tagesende)

**Beispiele:**
```
Von: [Kalender: 2025-11-18] + Zeit: 10:00
Bis: [Kalender: 2025-11-18] + Zeit: 12:00
→ Zeigt nur Logs zwischen 10 und 12 Uhr

Von: [Kalender: 2025-11-18] + Zeit: (leer)
Bis: [Kalender: 2025-11-18] + Zeit: (leer)
→ Zeigt alle Logs vom 18.11.2025 (00:00:00 bis 23:59:59)
```

**Teilfilter:**
- Nur "Von" ausfüllen → Zeigt alles ab diesem Zeitpunkt
- Nur "Bis" ausfüllen → Zeigt alles bis zu diesem Zeitpunkt

**Fallback:** Ohne `tkcalendar` wird klassisches Textfeld verwendet (Format: `YYYY-MM-DD HH:MM:SS`)

### User-Filter 👤

**Dropdown** wird automatisch mit allen gefundenen Usern gefüllt nach der Analyse.

**Beispiele:**
- User: `max.mustermann` → Zeigt nur Fehler dieses Users
- User: `Alle` → Zeigt alle User (Standard)

### Kombinierte Filter 🎯

**Leistungsstark:** Zeit + User gleichzeitig!

**Support-Szenario:**
```
User meldet: "Ich konnte zwischen 10 und 11 Uhr nicht syncen"
→ Von: [Kalender: 2025-11-18] + Zeit: 10:00
→ Bis: [Kalender: 2025-11-18] + Zeit: 11:00
→ User: max.mustermann
→ Filter anwenden
→ Zeigt nur seine Fehler in diesem Zeitfenster!
```

### Filter zurücksetzen

Button "✗ Filter zurücksetzen" entfernt alle Filter und zeigt wieder alle Logs.

## 🏷️ Error Code Spalte

Die Anwendung extrahiert automatisch **Error Codes** aus verschiedenen Quellen und zeigt sie in einer eigenen Spalte an.

### Unterstützte Error Code Typen

#### HTTP Status Codes
- `401` - Unauthorized (Authentifizierungsfehler)
- `403` - Forbidden (Zugriff verweigert)
- `404` - Not Found (Ressource nicht gefunden)
- `500` - Internal Server Error
- `504` - Gateway Timeout

#### Custom Error Codes
- `paas-auth-1` - IONOS OpenAI Auth-Fehler
- `http_504_timeout` - Spezifischer Timeout-Code
- Weitere app-spezifische Codes

#### Exception Codes
- Numerische Codes aus `exception.Code` Feldern
- Datenbank-Fehlercodes (z.B. `1045` - Access denied)

#### Client Network Errors
- `NET_5` - QNetworkReply::NetworkError(5)
- Format: `NET_` + Error-Nummer

### Verwendung

**Detail-Ansichten:** Alle Fehler-Listen zeigen eine "Error Code" Spalte:
```
| Zeit               | Typ          | Error Code  | Nachricht          |
|--------------------|--------------|-------------|--------------------|
| 2025-10-02 13:07   | integration  | 401         | API request error  |
| 2025-10-02 13:11   | core         | -           | Session HMAC error |
```

**Export:** Error Codes werden automatisch in Markdown und Excel mit exportiert.

**Vorteile:**
- ✅ Schnelle Identifikation spezifischer Fehlertypen
- ✅ Gruppierung von Fehlern nach Code
- ✅ Bessere Kommunikation mit Support/Dev-Teams
- ✅ Einfachere Fehlerkorrelation

**Beispiel:** User meldet "API funktioniert nicht"
- Öffne Details → Sortiere nach Error Code
- Alle `401` Codes sichtbar → Auth-Problem identifiziert! 🎯

## 🧪 Testing

```powershell
# Unit Tests ausführen
python test_analyzer.py

# Error Code Tests
python test_error_codes.py

# Alle Tests mit pytest (wenn installiert)
pytest test_analyzer.py test_error_codes.py -v
```
```

### Test Coverage
- ✅ Data Store (Limits, Overflow, Thread-Safety)
- ✅ Server Parser (alle Kategorien)
- ✅ Client Parser (Events & Errors)
- ✅ Error Handling

## 📊 Performance

### Benchmarks (Referenz-System)

| Dateigröße | Zeilen | Verarbeitungszeit | Threading |
|-----------|--------|------------------|-----------|
| 1 MB | 10.000 | ~0.5s | Nein |
| 10 MB | 100.000 | ~4.5s | Nein |
| 50 MB | 500.000 | ~18s | Ja |
| 100 MB | 1.000.000 | ~35s | Ja |

### Memory Usage
- **Ohne Limits**: ~1 GB für 1M Einträge
- **Mit Limits (10k)**: ~50 MB konstant

## 🔒 Sicherheit

### Input Validierung
- ✅ Dateigröße wird vor dem Laden geprüft
- ✅ Berechtigungen werden validiert
- ✅ Malformed JSON wird sicher behandelt
- ✅ Path Traversal Prevention

### Resource Limits
- ✅ Maximale Dateigröße (500 MB Standard)
- ✅ Memory-Limits pro Kategorie
- ✅ Timeout für lange Operationen

## 🐛 Troubleshooting

### Problem: "tkinterdnd2 not available"
**Lösung:**
```powershell
pip install tkinterdnd2
```
Falls das nicht funktioniert: Drag & Drop wird deaktiviert, Dateibrowser funktioniert weiterhin.

### Problem: "Datei zu groß"
**Lösung:** Erhöhe `MAX_FILE_SIZE_MB` in `config.py` oder teile die Log-Datei.

### Problem: "Einträge werden verworfen"
**Lösung:** Erhöhe `MAX_ENTRIES_PER_CATEGORY` in `config.py`.

### Problem: Anwendung friert bei großen Dateien
**Lösung:** 
- Prüfe `ENABLE_THREADING = True` in `config.py`
- Senke `LARGE_FILE_THRESHOLD_MB`

### Problem: Keine Ereignisse gefunden
**Mögliche Ursachen:**
- Falsches Log-Format (prüfe erste Zeile)
- Logs enthalten keine kategorisierten Ereignisse
- Regex-Patterns passen nicht (check `server_parser.py` / `client_parser.py`)

## 📈 Roadmap / Verbesserungsideen

### v17.1 (Geplant)
- [ ] Internationalisierung (EN/DE)
- [ ] Grafische Charts (matplotlib)
- [ ] Filter & Such funktionen
- [ ] Batch-Verarbeitung (mehrere Dateien)

### v18.0 (Zukunft)
- [ ] Web-Interface (Flask/FastAPI)
- [ ] Datenbank-Storage (SQLite)
- [ ] Real-Time Log-Monitoring
- [ ] Custom Regex-Patterns (GUI-Editor)
- [ ] Alarm-Benachrichtigungen

## 🤝 Contributing

Contributions sind willkommen! 

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

### Code Style
- PEP 8 konform
- Type Hints verwenden
- Docstrings für alle öffentlichen Funktionen
- Unit Tests für neue Features

## 📝 Changelog

### v17.0 (2025-11-18) - Major Refactoring
- ✨ Komplett überarbeitete Architektur
- 🏗️ Modulare Struktur (Parser, Store, GUI getrennt)
- 🔒 Memory-Safe mit konfigurierbaren Limits
- 🧵 Threading-Support für große Dateien
- 📝 Professionelles Logging
- ✅ Unit Tests
- 📚 Type Hints & Dokumentation
- ⚙️ Zentrale Konfiguration

### v16.0 (Original)
- Hybrid Server & Client Analyse
- Basic GUI mit Tkinter
- Monolithische Implementierung

## 📄 Lizenz

Siehe [LICENSE](LICENSE) Datei für Details.

## 👤 Autor

**Daniele & xXRoxXeRXx**
- GitHub: [@xXRoxXeRXx](https://github.com/xXRoxXeRXx)
- Repository: [log-scanner](https://github.com/xXRoxXeRXx/log-scanner)

## 🙏 Danksagungen

- Nextcloud Community für Log-Format-Spezifikationen
- tkinterdnd2 Entwickler
- Alle Contributors

---

**⭐ Wenn dir dieses Projekt gefällt, gib ihm einen Star auf GitHub!**
