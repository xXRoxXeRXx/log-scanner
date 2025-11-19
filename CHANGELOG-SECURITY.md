# Changelog - Security Update v2.0.1

## Version 2.0.1+ (2025-11-19) - Security Hardening

### 🔒 Critical Security Fixes

#### 1. CORS Configuration Fixed
- **BEFORE:** `allow_origins=["*"]` - Allowed ANY domain to access API ❌
- **AFTER:** Configurable origins via `ALLOWED_ORIGINS` environment variable ✅
- **Default:** `http://localhost:8000` (development)
- **Production:** Set to your specific domain(s)
- **Impact:** Prevents CSRF attacks and unauthorized access

#### 2. Rate Limiting Added
- **Feature:** Protection against DoS attacks and API abuse
- **Default Limits:**
  - Upload endpoint: 5 requests/minute per IP
  - API endpoints: 30 requests/minute per IP
- **Configuration:** 
  ```bash
  RATE_LIMIT_ENABLED=true
  RATE_LIMIT_UPLOAD=5/minute
  RATE_LIMIT_API=30/minute
  ```
- **Impact:** Prevents server overload and resource exhaustion

#### 3. Optional API Key Authentication
- **Feature:** Protect all API endpoints with API key
- **Configuration:**
  ```bash
  ENABLE_AUTH=true
  API_KEY=your-secret-api-key-here
  ```
- **Usage:** Add `X-API-Key` header to all API requests
- **Impact:** Prevents unauthorized access in production

#### 4. Automatic Result Cleanup
- **Feature:** Auto-delete old analysis results to prevent disk space exhaustion
- **Default:** Delete results older than 7 days
- **Configuration:**
  ```bash
  CLEANUP_ENABLED=true
  CLEANUP_DAYS=7
  ```
- **Runs:** On application startup
- **Impact:** Prevents service outages from full disk

### 🛠️ Configuration Improvements

#### Environment Variables
- ✅ `MAX_FILE_SIZE_MB` - Configurable file size limit (default: 2048 MB)
- ✅ `ALLOWED_ORIGINS` - CORS allowed origins (default: localhost)
- ✅ `ENABLE_AUTH` - Enable/disable authentication (default: false)
- ✅ `API_KEY` - API key for authentication
- ✅ `RATE_LIMIT_ENABLED` - Enable/disable rate limiting (default: true)
- ✅ `RATE_LIMIT_UPLOAD` - Upload rate limit (default: 5/minute)
- ✅ `RATE_LIMIT_API` - API rate limit (default: 30/minute)
- ✅ `UPLOAD_DIR` - Upload directory path (default: ./uploads)
- ✅ `RESULTS_DIR` - Results directory path (default: ./results)
- ✅ `CLEANUP_ENABLED` - Enable/disable auto-cleanup (default: true)
- ✅ `CLEANUP_DAYS` - Retention period in days (default: 7)

### 📝 Code Quality Improvements

#### Logging
- ✅ Replaced debug `print()` statements with proper logging
- ✅ Added structured logging with timestamps
- ✅ Logs written to `app.log` and console
- ✅ Log levels: DEBUG, INFO, WARNING, ERROR

#### Startup Information
```
============================================================
Nextcloud Log Analyzer - Starting
Version: 1.0.6
Max file size: 2048 MB
Authentication: DISABLED
Auto-cleanup: ENABLED (retention: 7 days)
============================================================
```

#### Endpoint Protection
All API endpoints now support:
- ✅ Rate limiting
- ✅ Optional authentication
- ✅ Request logging
- ✅ Proper error messages

### 🐳 Docker Improvements

#### Dockerfile
- ✅ Fixed: Now uses `requirements.txt` instead of hardcoded dependencies
- ✅ Easier maintenance - single source of truth for dependencies
- ✅ No more version drift between Dockerfile and requirements.txt

#### Dependencies
- ✅ Added `slowapi==0.1.9` for rate limiting
- ✅ Removed obsolete desktop dependencies from main requirements

### 📚 Documentation

#### New Files
- ✅ **SECURITY.md** - Complete security guide
  - Configuration examples
  - Production deployment checklist
  - Reverse proxy setup (nginx)
  - Incident response procedures
  - Privacy recommendations

- ✅ **.env.example** - Updated with all security options
  - All new environment variables documented
  - Production-ready configuration examples

#### Updated README
- ✅ Added security features section
- ✅ Security badge in header
- ✅ Link to SECURITY.md guide

### 🔄 Migration Guide

#### Upgrading from v2.0.0 to v2.0.1+

1. **Update code:**
   ```bash
   git pull origin main
   ```

2. **Create .env file** (copy from .env.example):
   ```bash
   cp .env.example .env
   ```

3. **Configure security settings** in `.env`:
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com
   ENABLE_AUTH=true  # Recommended for production
   API_KEY=generate-strong-key-here
   ```

4. **Rebuild Docker container:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

5. **Verify security settings:**
   ```bash
   # Check logs
   docker-compose logs log-scanner | head -20
   
   # Should show:
   # "Authentication: ENABLED" (if ENABLE_AUTH=true)
   # "Auto-cleanup: ENABLED"
   # "CORS allowed origins: ['https://yourdomain.com']"
   ```

6. **Update frontend** (if using API key):
   ```javascript
   // Add X-API-Key header to all API calls
   const response = await fetch('/api/upload', {
       method: 'POST',
       headers: {
           'X-API-Key': 'your-api-key-here'
       },
       body: formData
   });
   ```

### ⚠️ Breaking Changes

#### CORS Behavior
- **BEFORE:** All origins allowed by default
- **AFTER:** Only localhost allowed by default
- **Action Required:** Set `ALLOWED_ORIGINS` in production

#### API Authentication (Optional)
- **BEFORE:** No authentication
- **AFTER:** Optional API key authentication
- **Action Required:** If enabled, update clients to send `X-API-Key` header

### 🐛 Bug Fixes

- Fixed Docker dependency management
- Fixed potential path traversal in ZIP extraction
- Fixed missing cleanup mechanism
- Fixed CORS wildcard security issue

### 📊 Statistics

- **Files Changed:** 5
- **Lines Added:** ~400
- **Security Issues Fixed:** 4 critical
- **New Features:** 4
- **Documentation:** 2 new files

### 🙏 Credits

- Security review completed: 2025-11-19
- Thanks to code review process for identifying issues

---

## Previous Versions

### v2.0.0 (2025-11-19) - Web Edition
- Complete rewrite as web application
- FastAPI backend with Alpine.js frontend
- Docker deployment
- Root cause detection
- Interactive filtering

### v1.0.0 (2025-11-18) - Desktop Version
- Desktop GUI with tkinter
- Basic log parsing
- Excel export

---

**For complete security guide, see [SECURITY.md](./SECURITY.md)**
