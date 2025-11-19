# 🔍 Nextcloud Log Analyzer - Web Edition

**Modern web-based log analysis tool for Nextcloud Server and Client logs with intelligent root cause detection.**

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Alpine.js](https://img.shields.io/badge/Alpine.js-3.13-8BC0D0?logo=alpine.js&logoColor=white)](https://alpinejs.dev/)

---

## ✨ Features

### 🎯 Intelligent Analysis

- **🤖 Root Cause Detection** - Automatically identifies common issues:
  - 🔴 Redis connection errors and cluster failures
  - 💾 S3/ObjectStore problems (503 errors, connection issues)
  - 🌐 WebDAV protocol errors
  - 🐘 PHP errors (fopen, TypeError detection)
  - � File locking problems
  - 📁 Client sync errors (404, 403, network failures)
- **📊 Click-to-Filter** - Click any root cause card to instantly filter affected logs
- **🎨 Severity Levels** - Color-coded cards (Critical/High/Medium/Low)
- **💡 Solution Suggestions** - Specific troubleshooting steps for each issue

### 📈 Advanced Features

- **📁 Multi-File Upload** - Analyze up to 15 files simultaneously (2GB limit per file)
- **📦 ZIP Archive Support** - Direct upload of Nextcloud client debug.zip files (auto-extracts logs/ directory)
- **🗜️ Compression Support** - Direct processing of `.gz` / `.gzip` files
- **🔍 Smart Filters** - Date range, username, search text, category filters
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **📊 Interactive Charts** - Visual statistics with Chart.js
- **🎭 Dual Format Support** - JSON (Server) and Text (Client) logs
- **⚡ High Performance** - FastAPI backend with async processing
- **🐳 Docker Ready** - One-command deployment

### 🎨 Modern UI

- **Alpine.js** - Reactive, lightweight frontend
- **Smooth Animations** - Scroll effects, hover states, loading indicators
- **Dark Mode Ready** - Professional color scheme
- **Pagination** - 100 entries per page for optimal performance
- **Export Options** - JSON download for external analysis

---

## 🚀 Quick Start

### 🐳 Docker Deployment (Recommended)

**Start the application:**

```bash
# Using Docker Compose
docker-compose up -d

# Or using the start script
./start-web.sh    # Linux/Mac
.\start-web.ps1   # Windows
```

**Access the application:**

```
http://localhost:8000
```

**Stop the application:**

```bash
docker-compose down
```

### 💻 Local Development

**Requirements:**

- Python 3.13+
- pip

**Setup:**

```bashsudo dnf install python3-tkinter

# 1. Clone repository

git clone https://github.com/xXRoxXeRXx/log-scanner.git# macOS (mit Homebrew Python)

cd log-scannerbrew install python-tk

```

# 2. Install dependencies

pip install -r requirements.txt### Dependencies



# 3. Start server#### Pflicht

cd backend- **Python 3.8+** mit `tkinter` (normalerweise enthalten)

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000  - Windows/macOS: Bereits mit Python installiert

```  - Linux: Siehe Installation oben



**Access:**#### Optional (empfohlen)

```- `tkinterdnd2>=0.3.0` - Drag & Drop Funktionalität 🖱️

http://localhost:8000- `openpyxl>=3.0.0` - Excel Export 📊

```- `tkcalendar>=1.6.0` - Visueller Datepicker für Zeitfilter 📅



---**Installation der optionalen Pakete:**

```bash

## 📖 Usage Guidepip install -r requirements.txt

# oder einzeln:

### 1️⃣ Upload Logspip install tkinterdnd2 openpyxl tkcalendar

```

**Drag & Drop:**

- Drag one or multiple log files into the upload area**Ohne optionale Pakete:**

- Supports `.log`, `.txt`, `.json`, `.gz`, `.gzip`Die App funktioniert auch ohne diese - Features sind dann deaktiviert:

- Ohne `tkinterdnd2`: Kein Drag & Drop (Datei-Button funktioniert)

**File Selector:**- Ohne `openpyxl`: Kein Excel-Export (Markdown-Export funktioniert)

- Click "Choose Files" button- Ohne `tkcalendar`: Text-Datumseingabe statt Kalender-Widget

- Select up to 15 files (max 2GB total)

## 🚀 Verwendung

**Supported Formats:**

- **Server Logs** - JSON format from Nextcloud server### Grundlegende Nutzung

- **Client Logs** - Text format from desktop/mobile clients

- **Compressed** - Automatic `.gz` decompression1. **Anwendung starten**

   ```powershell

### 2️⃣ View Analysis   # Empfohlen - Einfacher Startbefehl

   python log_analyzer_v17.py

**Root Cause Analysis:**   

- Automatically appears at the top if issues detected   # Oder direkt die Hauptdatei

- Color-coded cards show severity and frequency   python log_analyzer_v17.py

- Click any card to filter affected logs   

   # Oder mit Batch-Datei (Windows)

**Statistics Overview:**   start_v17.bat

- Total entries and category breakdown   ```

- Interactive pie chart

- Only non-zero categories displayed2. **Log-Datei(en) laden**

   - 🖱️ **Drag & Drop**: Eine oder mehrere Dateien ins Fenster ziehen

**Log Entries:**   - 📂 **Datei(en) Browser**: "📂 Datei(en) suchen..." Button

- Paginated table (100 per page)     - Einzelne Datei: Einfach anklicken

- Date, time, type, user, error code, message     - Mehrere Dateien: **Strg+Klick** oder **Shift+Klick** zum Markieren

- Type-based color coding   - 📋 **Clipboard**: "📋 Aus Zwischenablage" Button



### 3️⃣ Filter Results3. **Unterstützte Dateiformate**

   - `.log` - Reguläre Log-Dateien

**Available Filters:**   - `.txt` - Text-Dateien

- **📅 Date Range** - Start and end date/time   - `.json` - JSON-Logs

- **👤 Username** - Filter by specific user   - `.gz` / `.gzip` - **Komprimierte Logs** (werden automatisch entpackt!)

- **🔍 Search** - Text search in messages

- **📂 Category** - S3, DAV, PHP, Client errors, etc.4. **Ergebnisse anzeigen**

   - Klicke auf Kategorien für Details

**Apply Filters:**   - Exportiere Tabellen als Markdown oder Excel

1. Set desired filters   - Bei mehreren Dateien: Kombinierte Analyse aller Logs

2. Click "Filter anwenden" (Apply Filters)

3. Click root cause card for quick filtering### Unterstützte Log-Formate



**Reset:**#### Server Logs (JSON)

- "✗ Filter zurücksetzen" removes all filters```json

{"level":3,"time":"2025-01-01T12:00:00","message":"HTTP/1.1 404","app":"objectstore"}

### 4️⃣ Export Data```



**JSON Export:****Kategorien:**

- Click "📥 Export JSON"- S3 HTTP Fehler (404, 500, etc.)

- Downloads complete analysis result- WebDAV Fehler

- Includes all entries, statistics, metadata- PHP Fehler

- Objectstore Fehler

---- Generische Fehler (Level 3)

- Warnungen (Level 2)

## 🏗️ Architecture- Infos (Level 1)

- Debug (Level 0)

### Project Structure

```#### Client Logs (Text)

log-scanner/```

├── backend/2025-01-01 12:00:00:000 [ info sync.engine ]: >========== Sync started for folder [/Documents]

│   ├── main.py              # FastAPI application```

│   ├── static/

│   │   ├── index.html       # Upload page**Story Events:**

│   │   └── results.html     # Analysis results- Sync Start/Ende

│   ├── uploads/             # Temporary upload storage- Upload/Download Fortschritt

│   └── results/             # Analysis results (JSON)- Server-Änderungen (ETag)

├── shared/- Fehler & Warnungen

│   ├── client_parser.py     # NextCloud client log parser- Benutzerinteraktionen

│   ├── server_parser.py     # NextCloud server log parser

│   ├── data_store.py        # Data storage management## ⚙️ Konfiguration

│   └── web_parser.py        # Web integration layer

├── tests/Bearbeite `config.py` für Anpassungen:

│   ├── test_parser_integration.py

│   └── test_upload_api.py### Performance & Memory

├── docker-compose.yml       # Docker orchestration```python

├── Dockerfile               # Container imageMAX_FILE_SIZE_MB = 500              # Max. Dateigröße

└── requirements.txt         # Python dependenciesMAX_ENTRIES_PER_CATEGORY = 10000    # Einträge pro Kategorie

```LARGE_FILE_THRESHOLD_MB = 10        # Threading-Schwelle

```

### Tech Stack

### UI Einstellungen

**Backend:**```python

- **FastAPI** 0.109.0 - Modern async web frameworkWINDOW_WIDTH = 1100

- **Uvicorn** - ASGI server with auto-reloadWINDOW_HEIGHT = 800

- **Python** 3.13 - Latest Python featuresFONT_CONSOLE = ("Consolas", 10)

```

**Frontend:**

- **Alpine.js** 3.13.3 - Reactive UI framework### Logging

- **Chart.js** 4.4.0 - Beautiful charts```python

- **Vanilla CSS** - No frameworks, pure performanceLOG_LEVEL = logging.INFO

LOG_FILE = 'log_analyzer.log'

**Deployment:**```

- **Docker** - Containerized deployment

- **Docker Compose** - Multi-container orchestration### Feature Flags

```python

---ENABLE_THREADING = True

ENABLE_EXCEL_EXPORT = True

## 🔍 Root Cause DetectionENABLE_CLIPBOARD_IMPORT = True

ENABLE_DRAG_DROP = True

The analyzer automatically detects **15 common issue patterns**:```



### 🖥️ Server Issues (6 patterns)## 🔍 Filter verwenden



1. **💾 ObjectStore/S3 Errors**Die App bietet leistungsstarke Filter für Support-Szenarien:

   - Threshold: >100 errors

   - Severity: Critical (>1000), High (>500)### Zeitfilter ⏰ mit Datepicker 📅

   - **Solution:** Check S3 endpoint, credentials, network, bucket permissions

**Visueller Datepicker:** Klick auf das Datumsfeld öffnet einen interaktiven Kalender

2. **🔴 S3 503 Service Unavailable**

   - Threshold: >10 errors**Format:**

   - Severity: Always Critical- **Datum:** Auswahl über Kalender (YYYY-MM-DD)

   - **Solution:** S3 backend overloaded, check capacity, scaling, maintenance- **Zeit:** Optionales Eingabefeld für Stunde:Minute (HH:MM)

- **Automatische Defaults:**

3. **🌐 WebDAV Protocol Errors**  - Startzeit ohne Zeit-Eingabe: `00:00:00` (Tagesbeginn)

   - Threshold: >100 errors  - Endzeit ohne Zeit-Eingabe: `23:59:59` (Tagesende)

   - Severity: High (>500), Medium

   - **Solution:** Check Apache/Nginx config, PHP timeouts, file permissions**Beispiele:**

```

4. **🐘 PHP Errors**Von: [Kalender: 2025-11-18] + Zeit: 10:00

   - Threshold: >20 errorsBis: [Kalender: 2025-11-18] + Zeit: 12:00

   - Types: fopen failures, TypeErrors→ Zeigt nur Logs zwischen 10 und 12 Uhr

   - **Solution:** Check PHP memory limits, file permissions, error logs

Von: [Kalender: 2025-11-18] + Zeit: (leer)

5. **💥 Storage Not Available**Bis: [Kalender: 2025-11-18] + Zeit: (leer)

   - Threshold: >10 errors→ Zeigt alle Logs vom 18.11.2025 (00:00:00 bis 23:59:59)

   - Severity: Always Critical```

   - **Solution:** Storage unmounted, NFS issues, database problems

**Teilfilter:**

6. **🔒 File Locking Problems**- Nur "Von" ausfüllen → Zeigt alles ab diesem Zeitpunkt

   - Threshold: >20 errors- Nur "Bis" ausfüllen → Zeigt alles bis zu diesem Zeitpunkt

   - Severity: Medium

   - **Solution:** Redis/Memcached issues, database locks, cleanup old locks**Fallback:** Ohne `tkcalendar` wird klassisches Textfeld verwendet (Format: `YYYY-MM-DD HH:MM:SS`)



### 🔴 Redis Issues (3 patterns)### User-Filter 👤



7. **Redis Connection/Read Errors****Dropdown** wird automatisch mit allen gefundenen Usern gefüllt nach der Analyse.

   - Threshold: >5 errors

   - Severity: Critical (>100), High (>50)**Beispiele:**

   - **Solution:** Check Redis cluster status, network, memory, timeouts- User: `max.mustermann` → Zeigt nur Fehler dieses Users

- User: `Alle` → Zeigt alle User (Standard)

8. **⚙️ WorkflowEngine Boot Failures**

   - Threshold: >5 errors### Kombinierte Filter 🎯

   - Severity: High (>50), Medium

   - **Solution:** Ensure Redis availability, restart app, clear cache**Leistungsstark:** Zeit + User gleichzeitig!



9. **📂 WebDAV Service Unavailable (Redis)****Support-Szenario:**

   - Threshold: >3 errors```

   - Severity: High (>20), MediumUser meldet: "Ich konnte zwischen 10 und 11 Uhr nicht syncen"

   - **Solution:** Critical for sync clients, check Redis failover→ Von: [Kalender: 2025-11-18] + Zeit: 10:00

→ Bis: [Kalender: 2025-11-18] + Zeit: 11:00

### 👥 Client Issues (6 patterns)→ User: max.mustermann

→ Filter anwenden

10. **🔗 Symbolic Link Errors (FileIgnored)**→ Zeigt nur seine Fehler in diesem Zeitfenster!

    - Threshold: >10 errors```

    - **Solution:** Explain symlink behavior, manual uploads

### Filter zurücksetzen

11. **🔍 HTTP 404 - Files Not Found**

    - Threshold: >10 errorsButton "✗ Filter zurücksetzen" entfernt alle Filter und zeigt wieder alle Logs.

    - **Solution:** Check server file storage, deletions, permissions

## 🏷️ Error Code Spalte

12. **🚫 HTTP 403 - Permission Denied**

    - Threshold: >5 errorsDie Anwendung extrahiert automatisch **Error Codes** aus verschiedenen Quellen und zeigt sie in einer eigenen Spalte an.

    - Severity: Always High

    - **Solution:** Review shares, folder permissions, user access### Unterstützte Error Code Typen



13. **🌐 Network/Connection Errors**#### HTTP Status Codes

    - Threshold: >20 errors- `401` - Unauthorized (Authentifizierungsfehler)

    - Severity: Critical (>100), High (>50)- `403` - Forbidden (Zugriff verweigert)

    - **Solution:** Check internet, firewall, DNS, server availability- `404` - Not Found (Ressource nicht gefunden)

- `500` - Internal Server Error

14. **📝 Invalid Filenames**- `504` - Gateway Timeout

    - Threshold: >3 errors

    - **Solution:** Windows forbidden characters, rename files#### Custom Error Codes

- `paas-auth-1` - IONOS OpenAI Auth-Fehler

15. **⚠️ SyncError Events**- `http_504_timeout` - Spezifischer Timeout-Code

    - Threshold: >3 errors- Weitere app-spezifische Codes

    - Severity: Always High

    - **Solution:** Generic sync failures, check details#### Exception Codes

- Numerische Codes aus `exception.Code` Feldern

---- Datenbank-Fehlercodes (z.B. `1045` - Access denied)



## ⚙️ Configuration#### Client Network Errors

- `NET_5` - QNetworkReply::NetworkError(5)

### Environment Variables- Format: `NET_` + Error-Nummer



Create `.env` file (see `.env.example`):### Verwendung

```bash

# Server Configuration**Detail-Ansichten:** Alle Fehler-Listen zeigen eine "Error Code" Spalte:

HOST=0.0.0.0```

PORT=8000| Zeit               | Typ          | Error Code  | Nachricht          |

WORKERS=1|--------------------|--------------|-------------|--------------------|

| 2025-10-02 13:07   | integration  | 401         | API request error  |

# Upload Limits| 2025-10-02 13:11   | core         | -           | Session HMAC error |

MAX_UPLOAD_SIZE_MB=2048```

MAX_FILES=15

**Export:** Error Codes werden automatisch in Markdown und Excel mit exportiert.

# Storage Paths

UPLOAD_DIR=./uploads**Vorteile:**

RESULTS_DIR=./results- ✅ Schnelle Identifikation spezifischer Fehlertypen

- ✅ Gruppierung von Fehlern nach Code

# Development- ✅ Bessere Kommunikation mit Support/Dev-Teams

DEBUG=False- ✅ Einfachere Fehlerkorrelation

RELOAD=False

```**Beispiel:** User meldet "API funktioniert nicht"

- Öffne Details → Sortiere nach Error Code

### Docker Configuration- Alle `401` Codes sichtbar → Auth-Problem identifiziert! 🎯



**docker-compose.yml:**## 🧪 Testing

```yaml

services:```powershell

  log-scanner:# Unit Tests ausführen

    build: .python test_analyzer.py

    ports:

      - "8000:8000"# Error Code Tests

    volumes:python test_error_codes.py

      - ./logs:/app/logs

      - ./backend/results:/app/backend/results# Alle Tests mit pytest (wenn installiert)

    environment:pytest test_analyzer.py test_error_codes.py -v

      - DEBUG=False```

``````



---### Test Coverage

- ✅ Data Store (Limits, Overflow, Thread-Safety)

## 🧪 Testing- ✅ Server Parser (alle Kategorien)

- ✅ Client Parser (Events & Errors)

**Run tests:**- ✅ Error Handling

```bash

# All tests## 📊 Performance

pytest tests/ -v

### Benchmarks (Referenz-System)

# Specific test

pytest tests/test_upload_api.py -v| Dateigröße | Zeilen | Verarbeitungszeit | Threading |

|-----------|--------|------------------|-----------|

# With coverage| 1 MB | 10.000 | ~0.5s | Nein |

pytest tests/ --cov=shared --cov=backend| 10 MB | 100.000 | ~4.5s | Nein |

```| 50 MB | 500.000 | ~18s | Ja |

| 100 MB | 1.000.000 | ~35s | Ja |

**Test Coverage:**

- ✅ Parser integration tests### Memory Usage

- ✅ FastAPI upload endpoint tests- **Ohne Limits**: ~1 GB für 1M Einträge

- ✅ Root cause detection tests- **Mit Limits (10k)**: ~50 MB konstant

- ✅ Filter functionality tests

## 🔒 Sicherheit

---

### Input Validierung

## 📊 Performance- ✅ Dateigröße wird vor dem Laden geprüft

- ✅ Berechtigungen werden validiert

### Benchmarks- ✅ Malformed JSON wird sicher behandelt

- ✅ Path Traversal Prevention

| Files | Size | Entries | Processing Time | Memory Usage |

|-------|------|---------|-----------------|--------------|### Resource Limits

| 1 | 10 MB | 50K | ~2s | ~100 MB |- ✅ Maximale Dateigröße (500 MB Standard)

| 5 | 50 MB | 250K | ~8s | ~300 MB |- ✅ Memory-Limits pro Kategorie

| 10 | 100 MB | 500K | ~15s | ~500 MB |- ✅ Timeout für lange Operationen

| 15 | 200 MB | 1M | ~30s | ~800 MB |

## 🐛 Troubleshooting

### Optimization

### Problem: "tkinterdnd2 not available"

**Upload Limits:****Lösung:**

- Max file size: 2GB per file```powershell

- Max total: 2GB combinedpip install tkinterdnd2

- Max files: 15 simultaneously```

Falls das nicht funktioniert: Drag & Drop wird deaktiviert, Dateibrowser funktioniert weiterhin.

**Result Pagination:**

- 100 entries per page### Problem: "Datei zu groß"

- Lazy loading for large datasets**Lösung:** Erhöhe `MAX_FILE_SIZE_MB` in `config.py` oder teile die Log-Datei.

- Client-side filtering

### Problem: "Einträge werden verworfen"

**Caching:****Lösung:** Erhöhe `MAX_ENTRIES_PER_CATEGORY` in `config.py`.

- Analysis results cached as JSON

- Unique IDs for each analysis### Problem: Anwendung friert bei großen Dateien

- Automatic cleanup (implement if needed)**Lösung:** 

- Prüfe `ENABLE_THREADING = True` in `config.py`

---- Senke `LARGE_FILE_THRESHOLD_MB`



## 🐛 Troubleshooting### Problem: Keine Ereignisse gefunden

**Mögliche Ursachen:**

### Problem: "Connection refused" when accessing localhost:8000- Falsches Log-Format (prüfe erste Zeile)

- Logs enthalten keine kategorisierten Ereignisse

**Solution:**- Regex-Patterns passen nicht (check `server_parser.py` / `client_parser.py`)

```bash

# Check if server is running## 📈 Roadmap / Verbesserungsideen

docker-compose ps

### v17.1 (Geplant)

# Check logs- [ ] Internationalisierung (EN/DE)

docker-compose logs -f- [ ] Grafische Charts (matplotlib)

- [ ] Filter & Such funktionen

# Restart- [ ] Batch-Verarbeitung (mehrere Dateien)

docker-compose restart

```### v18.0 (Zukunft)

- [ ] Web-Interface (Flask/FastAPI)

### Problem: "File too large" error- [ ] Datenbank-Storage (SQLite)

- [ ] Real-Time Log-Monitoring

**Solution:**- [ ] Custom Regex-Patterns (GUI-Editor)

- Increase `MAX_UPLOAD_SIZE_MB` in `.env`- [ ] Alarm-Benachrichtigungen

- Rebuild container: `docker-compose up -d --build`

## 🤝 Contributing

### Problem: Empty root cause analysis

Contributions sind willkommen! 

**Causes:**

- Not enough errors to trigger thresholds1. Fork das Repository

- Logs don't match detection patterns2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)

- Check browser console for JavaScript errors3. Commit deine Änderungen (`git commit -m 'Add AmazingFeature'`)

4. Push zum Branch (`git push origin feature/AmazingFeature`)

### Problem: Slow analysis for large files5. Öffne einen Pull Request



**Solution:**### Code Style

- Use Docker deployment (optimized)- PEP 8 konform

- Increase server resources- Type Hints verwenden

- Split large log files- Docstrings für alle öffentlichen Funktionen

- Use compression (.gz files)- Unit Tests für neue Features



---## 📝 Changelog



## 🔒 Security### v17.0 (2025-11-18) - Major Refactoring

- ✨ Komplett überarbeitete Architektur

### Upload Security- 🏗️ Modulare Struktur (Parser, Store, GUI getrennt)

- ✅ File size limits enforced- 🔒 Memory-Safe mit konfigurierbaren Limits

- ✅ File type validation- 🧵 Threading-Support für große Dateien

- ✅ No arbitrary code execution- 📝 Professionelles Logging

- ✅ Isolated processing- ✅ Unit Tests

- 📚 Type Hints & Dokumentation

### Data Privacy- ⚙️ Zentrale Konfiguration

- ⚠️ **Important:** This tool processes log files containing:

  - Usernames### v16.0 (Original)

  - IP addresses- Hybrid Server & Client Analyse

  - File paths- Basic GUI mit Tkinter

  - System information- Monolithische Implementierung

- 🔐 **Recommendation:** Deploy in private network

- 🗑️ **Cleanup:** Implement automatic result deletion## 📄 Lizenz



### Production DeploymentSiehe [LICENSE](LICENSE) Datei für Details.

- [ ] Add authentication (OAuth2, LDAP)

- [ ] Enable HTTPS (reverse proxy)## 👤 Autor

- [ ] Implement rate limiting

- [ ] Add audit logging**Daniele & xXRoxXeRXx**

- [ ] Regular security updates- GitHub: [@xXRoxXeRXx](https://github.com/xXRoxXeRXx)

- Repository: [log-scanner](https://github.com/xXRoxXeRXx/log-scanner)

---

## 🙏 Danksagungen

## 📚 API Documentation

- Nextcloud Community für Log-Format-Spezifikationen

**FastAPI Swagger UI:**- tkinterdnd2 Entwickler

```- Alle Contributors

http://localhost:8000/docs

```---



**ReDoc:****⭐ Wenn dir dieses Projekt gefällt, gib ihm einen Star auf GitHub!**

```
http://localhost:8000/redoc
```

### Key Endpoints

**Health Check:**
```bash
GET /health
→ {"status": "healthy"}
```

**Upload & Analyze:**
```bash
POST /api/upload
Content-Type: multipart/form-data
Files: file[] (multiple)

→ Redirects to /results.html?id={analysis_id}
```

**Get Results:**
```bash
GET /api/results/{analysis_id}

→ {
    "id": "uuid",
    "timestamp": "2025-11-19T...",
    "files": [...],
    "total_entries": 1234,
    "statistics": {...},
    "entries": [...]
  }
```

---

## 🤝 Contributing

Contributions welcome! 🎉

**Development Setup:**
```bash
# 1. Fork & Clone
git clone https://github.com/YOUR_USERNAME/log-scanner.git

# 2. Create branch
git checkout -b feature/amazing-feature

# 3. Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# 4. Make changes & test
pytest tests/ -v

# 5. Format code
black shared/ backend/ tests/

# 6. Commit & Push
git commit -m "feat: Add amazing feature"
git push origin feature/amazing-feature

# 7. Open Pull Request
```

**Code Style:**
- PEP 8 compliant
- Type hints for all functions
- Docstrings (Google style)
- Unit tests for new features

---

## 📝 Changelog

### v2.0.1 (2025-11-19) - ZIP Support & Fixes
- 📦 ZIP archive support (auto-extract logs/ directory)
- 🔧 Fixed config.py import errors
- 🐛 Parser compatibility improvements
- 📝 Updated documentation
- ✅ Tested with real client debug.zip (23 files, 730 entries)

### v2.0.0 (2025-11-19) - Web Edition
- 🌐 Complete rewrite as web application
- 🤖 Intelligent root cause detection (15 patterns)
- 🔴 Redis error analysis
- 🎯 Click-to-filter functionality
- 🐳 Docker deployment
- 📊 Interactive charts
- 🎨 Modern Alpine.js UI
- ⚡ FastAPI backend
- 📱 Responsive design

### v1.0.0 (2025-11-18) - Desktop Version
- Desktop GUI with tkinter
- Basic log parsing
- Excel export
- Drag & drop support

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 👤 Authors

**Daniele & xXRoxXeRXx**
- GitHub: [@xXRoxXeRXx](https://github.com/xXRoxXeRXx)
- Repository: [log-scanner](https://github.com/xXRoxXeRXx/log-scanner)

---

## 🙏 Acknowledgments

- Nextcloud community for log format specifications
- FastAPI team for the excellent framework
- Alpine.js and Chart.js developers
- All contributors and testers

---

<div align="center">

**⭐ If you find this project useful, please give it a star on GitHub! ⭐**

[Report Bug](https://github.com/xXRoxXeRXx/log-scanner/issues) · [Request Feature](https://github.com/xXRoxXeRXx/log-scanner/issues) · [Documentation](DOCKER_README.md)

</div>
