# Docker Web Deployment - Projekt-Übersicht (Simplified)

## 🎯 Ziel
Transformation des Desktop-Tools (Tkinter) in eine **einfache** Web-Anwendung mit:
- **Docker-basiertes Deployment** (plattformunabhängig)
- **Web-Interface** für Upload und Visualisierung
- **Moderne Visualisierungen** (Charts, Graphs, interaktive Tabellen)
- **Single-User-Optimiert** (1-2 Analysen/Tag)

## ⚡ Vereinfachter Ansatz
**KEIN** Celery, **KEIN** Redis, **KEIN** PostgreSQL!
- Synchrone Verarbeitung (ausreichend für kleine Logs)
- SQLite für temporäre Job-History
- Direktes Processing ohne Queue
- Single Docker Container (all-in-one)

## 🏗️ Vereinfachte Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│             (Vanilla JS/Alpine.js + Chart.js)                │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Single Docker Container                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          FastAPI Backend + Static Frontend            │  │
│  │                                                        │  │
│  │  - REST API (FastAPI)                                │  │
│  │  - Synchronous Processing                            │  │
│  │  - File Upload Handler                               │  │
│  │  - server_parser.py / client_parser.py              │  │
│  │  - SQLite (job history, optional)                   │  │
│  │  - Static Files (HTML/CSS/JS)                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Volume: /app/uploads (temporary storage)                   │
│  Volume: /app/results (analysis results)                    │
└─────────────────────────────────────────────────────────────┘
```

**Vorteile:**
- ✅ Eine einzige `docker run` Befehl
- ✅ Keine externen Dependencies (Redis, PostgreSQL)
- ✅ Schnelles Setup (< 1 Minute)
- ✅ Minimaler Resource-Verbrauch
- ✅ Einfaches Backup (ein Container)

## 📁 Vereinfachte Verzeichnisstruktur

```
log-scanner/
├── backend/                    # FastAPI Application
│   ├── main.py                # FastAPI Entry Point
│   ├── api.py                 # API Endpoints (upload, results)
│   ├── static/                # Frontend (HTML/CSS/JS)
│   │   ├── index.html         # Upload Page
│   │   ├── results.html       # Results Page
│   │   ├── app.js             # Alpine.js Logic
│   │   └── style.css          # Minimal CSS
│   └── uploads/               # Temporary Upload Storage
│
├── shared/                     # Shared Parser Logic
│   ├── server_parser.py       # From existing (adapted)
│   ├── client_parser.py       # From existing (adapted)
│   └── data_store.py          # Modified for Web
│
├── tests/                      # Tests
│   ├── test_upload_api.py
│   └── test_parser_integration.py
│
├── Dockerfile                  # Single Container
├── docker-compose.yml          # Optional (single service)
├── requirements.txt            # Python Dependencies
├── .dockerignore
├── .env.example
└── README.md
```

**Entfernt:**
- `frontend/` directory (kein Build-Process)
- `docker/nginx/` (kein Reverse Proxy)
- `backend/tasks/` (kein Celery)
- `backend/db/` (kein ORM, optional SQLite)
- `backend/models/` (simple Pydantic models in `api.py`)
- `docker-compose.dev.yml` (nur ein Service)
└── DEPLOYMENT.md               # Setup Guide
```

## 🔧 Minimaler Tech-Stack

### Backend
- **FastAPI** 0.104+ (Python Web Framework)
- **Uvicorn** (ASGI Server)
- **Pydantic** 2.0+ (Data Validation)
- **python-multipart** (File Uploads)
- **aiofiles** (Async File Operations)
- **SQLite** (Optional, Job-History)

### Frontend
- **Alpine.js** oder **Vanilla JavaScript** (Lightweight)
- **Chart.js** (Visualisierung)
- **Minimal CSS** (Kein Framework nötig)

### Infrastructure
- **Docker** 24+
- **docker-compose** 2.0+ (Optional, Single Service)

## 🚀 Features (Minimal MVP)

### Phase 1: Core Functionality
- ✅ File Upload (Single/Multiple, .log/.gz)
- ✅ Synchronous Analysis (server_parser.py, client_parser.py)
- ✅ Basic Dashboard
- ✅ Results Display (Tables)
- ✅ Docker Deployment

### Phase 2: Enhanced Visualization
- 📊 Simple Charts (Error Timeline)
- 📈 Category Breakdown
- 🗂️ Sortable Tables
- 💾 Export to JSON/CSV

### Optional Features (später)
- � Log-Suche
- � History (letzte Analysen)
- 📱 Mobile Responsive

## 📋 Vereinfachte API Endpoints

```
POST   /api/upload             # Upload & analyze (synchron)
GET    /api/results/{id}       # Get analysis results
GET    /                       # Static HTML frontend
GET    /health                 # Health check
```

**Hinweis:** Keine WebSockets, keine Job-Queue, keine komplexe Session-Verwaltung.

## 🐳 Simplified Docker Setup

### docker-compose.yml (Optional, Single Service)

```yaml
version: '3.8'

services:
  log-scanner:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./results:/app/results
    environment:
      - ENV=production
```

### Dockerfile (Multi-Stage)

```dockerfile
# Stage 1: Build (optional für Frontend)
FROM node:18-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Python Runtime
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy parsers and backend
COPY server_parser.py client_parser.py data_store.py ./
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-build /frontend/dist ./backend/static

# Run FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Oder noch einfacher:**

```bash
# Ohne docker-compose, direkt:
docker build -t log-scanner .
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads log-scanner
```
## 📊 Minimale Data Models

### AnalysisResult (Response)

```python
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class AnalysisResult(BaseModel):
    id: str                    # Unique ID
    timestamp: datetime
    file_count: int
    total_entries: int
    categories: Dict[str, int]  # {'s3_errors': 42, ...}
    entries: List[Dict]         # Parsed log entries
```

### LogEntry (von existierendem Code)

```python
# Bereits vorhanden in data_store.py
time: str
type: str  # ERROR, WARNING, INFO
message: str
user: Optional[str]
category: str  # s3_errors, dav_errors, ...
```

**Hinweis:** Keine komplexen Job-Status-Maschinen, keine User-Sessions, keine Datenbank-Modelle nötig.

## 🔒 Minimale Security

- File upload size limit (50MB)
- MIME type validation (.log, .gz only)
- Path traversal prevention
- Simple rate limiting (optional)
- CORS: nur localhost/eigene Domain

**Keine:** Authentication, JWT, komplexe Rate-Limiting, Multi-User-Sessions

## 🎨 Einfaches UI Design

### Upload Page

```text
┌────────────────────────────────────────┐
│  Nextcloud Log Analyzer                │
│  ┌──────────────────────────────────┐  │
│  │  📁 Drag & Drop .log Files       │  │
│  │     oder klicken zum Auswählen   │  │
│  └──────────────────────────────────┘  │
│  [Analyse starten]                     │
└────────────────────────────────────────┘
```

### Results Page

```text
┌────────────────────────────────────────┐
│  📊 Analyse-Ergebnisse                 │
│                                        │
│  🔴 Errors: 1234  |  ⚠️ Warnings: 567  │
│  ℹ️ Info: 890     |  📁 Files: 3       │
│                                        │
│  📈 [Chart.js: Error Timeline]         │
│                                        │
│  📋 Error Details (sortable)           │
│  ┌──────────┬──────┬──────┬─────┐    │
│  │Time      │Type  │Code  │User │    │
│  📊 Error-Kategorien:                  │
│  - S3 Errors: 234                      │
│  - DAV Errors: 156                     │
│  - DB Errors: 89                       │
│                                        │
│  [JSON Export] [CSV Export]            │
└────────────────────────────────────────┘
```

## 🧪 Simplified Testing

### Backend Tests

```bash
pytest tests/
# - test_upload_api.py
# - test_parser_integration.py
```

**Kein:** Celery-Tests, Redis-Tests, komplexe Integration-Tests

## 📈 Realistische Performance-Ziele

- **Upload + Analyse**: < 10s für 10MB file (synchron)
- **API Response**: < 500ms
- **Page Load**: < 3s

**Hinweis:** Keine Parallelität, keine Background-Jobs → einfachere Metriken

## 🚦 Einfache Deployment-Schritte

```bash
# 1. Clone repository
git clone <repo>
cd log-scanner

# 2. Build Docker image
docker build -t log-scanner .

# 3. Run container
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  log-scanner

# 4. Access UI
# Browser: http://localhost:8000
```

**Optional mit docker-compose:**

```bash
docker-compose up -d
```

## 📝 Minimale Environment Variables

```bash
# .env (optional)
PORT=8000
MAX_UPLOAD_SIZE=52428800  # 50MB
LOG_LEVEL=info
```

## 🎯 Vereinfachte Success Criteria

- ✅ Docker-Container baut erfolgreich
- ✅ Web-UI ist unter `localhost:8000` erreichbar
- ✅ File-Upload funktioniert (.log, .gz)
- ✅ Analyse läuft synchron (kein Background-Job)
- ✅ Ergebnisse werden als JSON zurückgegeben
- ✅ Basic Charts (Chart.js)
- ✅ Multi-File-Support

**Keine:** Mobile Responsive (desktop-first), Real-time Progress, Sessions, Authentication

## 📚 Simplified Next Steps

1. ✅ **Plan erstellt** (dieses Dokument)
2. **Backend-Struktur**
   - `backend/main.py` (FastAPI App)
   - `/api/upload` Endpoint
   - `/api/results/{id}` Endpoint
3. **Parser-Anpassung**
   - `shared/server_parser.py`
   - `shared/client_parser.py`
   - Von Tkinter entkoppeln
4. **Minimal-Frontend**
   - `backend/static/index.html` (File Upload Form)
   - `backend/static/results.html` (Results Display)
   - Alpine.js + Chart.js (< 50KB gesamt)
5. **Docker Setup**
   - `Dockerfile` (Single-Stage oder Multi-Stage)
   - Optional: `docker-compose.yml`
6. **Testing**
   - `tests/test_upload_api.py`
   - `tests/test_parser_integration.py`

---

## 💡 Architektur-Entscheidungen (SIMPLIFIED)

### ❌ NICHT verwenden
- Redis (kein Cache/Queue nötig)
- Celery (kein Background-Processing)
- PostgreSQL (SQLite reicht)
- WebSockets (keine Real-time Updates)
- React/Vue Build-Process (zu komplex)
- Nginx (FastAPI kann Static Files direkt ausliefern)
- JWT/Sessions (Single-User)

### ✅ Verwenden
- FastAPI (mit StaticFiles)
- Uvicorn (ASGI Server)
- Alpine.js (Lightweight JavaScript)
- Chart.js (Simple Visualizations)
- SQLite (optional, für History)
- Docker (Single Container)

---

**Geschätzte Implementierungszeit:**
- Backend API: 2-3 Stunden
- Frontend (minimal): 2-3 Stunden
- Docker Setup: 1 Stunde
- Testing: 1-2 Stunden
- **Gesamt: 6-9 Stunden**

vs. ursprünglicher Plan: 40-60 Stunden (6-8 Arbeitstage)
9. **Testing**
10. **Documentation**
