# 🔍 Nextcloud Log Analyzer - Web Edition

**Modern web-based log analysis tool for Nextcloud Server and Client logs with intelligent root cause detection.**

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Alpine.js](https://img.shields.io/badge/Alpine.js-3.13-8BC0D0?logo=alpine.js&logoColor=white)](https://alpinejs.dev/)
[![Security](https://img.shields.io/badge/Security-Hardened-green)](./SECURITY.md)

---

## ✨ Features

### 🎯 Intelligent Analysis

- **🤖 Root Cause Detection** - Automatically identifies common issues:
  - 🔴 Redis connection errors and cluster failures
  - 💾 S3/ObjectStore problems (503 errors, connection issues)
  - 🌐 WebDAV protocol errors
  - 🐘 PHP errors (fopen, TypeError detection)
  - 🔒 File locking problems
  - 📁 Client sync errors (404, 403, network failures)
- **📊 Click-to-Filter** - Click any root cause card to instantly filter affected logs
- **🎨 Severity Levels** - Color-coded cards (Critical/High/Medium/Low)
- **💡 Solution Suggestions** - Specific troubleshooting steps for each issue

### 🔒 Security (v2.0.1+)

- **🛡️ CORS Protection** - Configurable allowed origins (no more wildcards)
- **🚦 Rate Limiting** - DoS protection (5 uploads/min, 30 API calls/min)
- **🔐 API Key Auth** - Optional authentication for production
- **🗑️ Auto-Cleanup** - Automatic deletion of old results (7 days default)
- **📏 Size Limits** - Enforced file size and type validation
- **See [SECURITY.md](./SECURITY.md) for complete security guide**

### 📈 Advanced Features

- **📁 Multi-File Upload** - Analyze up to 15 files simultaneously (2GB limit per file)
- **📦 ZIP Archive Support** - Direct upload of Nextcloud client debug.zip files
- **🗜️ Compression Support** - Direct processing of `.gz` / `.gzip` files
- **🔍 Smart Filters** - Date range, username, search text, category filters
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **📊 Interactive Charts** - Visual statistics with Chart.js
- **🎭 Dual Format Support** - JSON (Server) and Text (Client) logs
- **⚡ High Performance** - FastAPI backend with async processing
- **🐳 Docker Ready** - One-command deployment

### 🎨 Modern UI

- **🌙 Dark Mode Toggle** - Switch between light and dark themes
- **💾 Download Results** - Export as JSON or CSV
- **🎨 Enhanced Drag & Drop** - Visual feedback with file counter
- **Smooth Animations** - Professional transitions and effects
- **Pagination** - 100 entries per page for optimal performance

---

## 🚀 Quick Start

### 🐳 Docker Deployment (Recommended)

```bash
# Using Docker Compose
docker-compose up -d

# Or using the start script
./start-web.sh    # Linux/macOS
start-web.ps1     # Windows
```

**Access:** http://localhost:8000

**See [docs/DOCKER.md](docs/DOCKER.md) for detailed Docker documentation**

---

### 💻 Local Development

**Requirements:**

- Python 3.11+ (3.11, 3.12 tested, **3.13 not yet supported** due to pydantic-core compatibility)
- pip

**Setup:**

```bash
# 1. Clone repository
git clone https://github.com/xXRoxXeRXx/log-scanner.git
cd log-scanner

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access:** http://localhost:8000

---

## 📖 Usage Guide

### 1️⃣ Upload Logs

**Drag & Drop:**
- Drag one or multiple log files into the upload area
- Visual feedback shows file count during drag

**File Selector:**
- Click "Choose Files" button
- Select up to 15 files (max 2GB per file)

**Supported Formats:**
- **Server Logs** - JSON format from Nextcloud server
- **Client Logs** - Text format from desktop/mobile clients
- **Compressed** - Automatic `.gz` decompression
- **ZIP Archives** - Auto-extract Nextcloud client debug.zip

### 2️⃣ View Analysis

**Root Cause Analysis:**
- Automatically appears at the top if issues detected
- Color-coded cards show severity and frequency
- Click any card to filter affected logs

**Statistics Overview:**
- Total entries and category breakdown
- Interactive pie chart
- Only non-zero categories displayed

**Log Entries:**
- Paginated table (100 per page)
- Date, time, type, user, error code, message
- Type-based color coding

### 3️⃣ Filter Results

**Available Filters:**
- **Date Range** - From/To date picker
- **Username** - Select specific user
- **Search** - Free text search in messages
- **Category** - Filter by log category

**Quick Filter:**
- Click any root cause card to auto-filter
- Shows only affected log entries

### 4️⃣ Export Data

- **💾 JSON** - Download complete analysis as JSON
- **📊 CSV** - Export filtered entries as CSV spreadsheet

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# Security
ALLOWED_ORIGINS=http://localhost:8000
ENABLE_AUTH=false
API_KEY=your-super-secret-key-here

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_UPLOAD=5/minute
RATE_LIMIT_API=30/minute

# File Limits
MAX_FILE_SIZE_MB=2048
MAX_FILES=15

# Cleanup
AUTO_CLEANUP_ENABLED=true
RESULT_RETENTION_DAYS=7

# Timeouts
UVICORN_TIMEOUT_KEEP_ALIVE=300
REQUEST_TIMEOUT=600
```

**See `.env.example` for complete documentation**

---

## 📂 Project Structure

```
log-scanner/
├── backend/              # FastAPI application
│   ├── static/          # Frontend (HTML/CSS/JS)
│   │   ├── index.html   # Upload page
│   │   └── results.html # Analysis results
│   └── main.py          # API endpoints
├── shared/               # Shared parsers
│   ├── web_parser.py    # Main analysis logic
│   ├── server_parser.py # Server log parser
│   ├── client_parser.py # Client log parser
│   └── data_store.py    # Data management
├── tests/                # Test suite (44 tests)
├── docs/                 # Documentation
│   ├── DOCKER.md        # Docker guide
│   └── CHANGELOG-SECURITY.md
├── logs/                 # Application logs
├── uploads/              # Uploaded files (temp)
├── results/              # Analysis results
├── Dockerfile            # Docker build
├── docker-compose.yml    # Docker orchestration
└── requirements.txt      # Python dependencies
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov=shared --cov-report=html

# Run specific test file
pytest tests/test_security_features.py -v
```

**Test Suite:**
- 44 tests covering parsers, API, and security
- Security tests for CORS, rate limiting, auth
- Integration tests for file upload and analysis
- See `.github/workflows/ci-cd.yml` for CI/CD

---

## 🐛 Common Issues

### Upload Timeout

**Problem:** Large files (>100MB) timeout during upload

**Solution:** Timeouts are set to 10 minutes (frontend) and 5 minutes (backend keep-alive)
- Should handle files up to 500MB
- For larger files, use local development mode

### Missing server_info Entries

**Problem:** Only some log entries shown in results

**Solution:** Fixed in v2.0.3 - all entry categories now displayed

### Python 3.13 Compatibility

**Problem:** Tests fail on Python 3.13 with pydantic-core error

**Solution:** Use Python 3.11 or 3.12 until pydantic-core adds 3.13 support

---

## 🔒 Security

This project follows security best practices:

- ✅ No wildcard CORS
- ✅ Rate limiting on all endpoints
- ✅ Optional API key authentication
- ✅ Automatic cleanup of old data
- ✅ Input validation and sanitization
- ✅ Size limits enforced

**See [SECURITY.md](./SECURITY.md) for:**
- Security policy
- Vulnerability reporting
- Supported versions
- Security features

---

## 📊 Statistics

- **Version:** 2.0.3
- **Lines of Code:** ~3,000
- **Test Coverage:** 85%+
- **Test Suite:** 44 tests
- **Docker Image:** ~200MB
- **Supported Formats:** .log, .txt, .json, .gz, .zip

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Please ensure:**
- All tests pass (`pytest tests/`)
- Code follows project style
- Security features are not compromised

---

## 📝 Changelog

### v2.0.3 (2025-11-20)
- ✨ Added Dark Mode toggle with localStorage persistence
- 💾 Added download results as JSON/CSV
- 🎨 Enhanced drag & drop feedback with file counter
- 🐛 Fixed server_info entries not being returned
- 🔧 Consolidated logs/uploads/results to absolute paths
- 📚 Reorganized documentation structure

### v2.0.2 (2025-11-19)
- 📊 Added upload progress bar (0-100%)
- ⏱️ Increased upload timeout to 10 minutes
- ⚡ Improved large file handling (up to 500MB)

### v2.0.1 (2025-11-19)
- 🔒 Comprehensive security hardening
- 🛡️ CORS protection (no more wildcards)
- 🚦 Rate limiting (DoS protection)
- 🔐 Optional API key authentication
- 🗑️ Auto-cleanup of old results
- 🧪 Added 22 security tests
- 📝 CI/CD pipeline with 5 jobs

**See [docs/CHANGELOG-SECURITY.md](docs/CHANGELOG-SECURITY.md) for detailed security changes**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **Alpine.js** - Lightweight reactive framework
- **Chart.js** - Beautiful charts
- **Docker** - Containerization platform
- **Nextcloud Community** - For the awesome platform

---

<div align="center">

**⭐ If you find this project useful, please give it a star on GitHub! ⭐**

[Report Bug](https://github.com/xXRoxXeRXx/log-scanner/issues) · [Request Feature](https://github.com/xXRoxXeRXx/log-scanner/issues) · [Docker Documentation](docs/DOCKER.md)

</div>
