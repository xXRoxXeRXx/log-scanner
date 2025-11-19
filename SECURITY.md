# 🔒 Security Guide - Nextcloud Log Analyzer

## Overview

Version 2.0.1+ includes comprehensive security features for production deployment. This guide covers all security aspects and best practices.

---

## ✅ Built-in Security Features

### 1. CORS Protection

**Problem:** Version 2.0.0 had `allow_origins=["*"]` which allowed ANY domain to access the API.

**Solution:** Configurable CORS with strict origin control.

```bash
# Development (default)
ALLOWED_ORIGINS=http://localhost:8000

# Production (multiple domains)
ALLOWED_ORIGINS=https://logs.company.com,https://logs-backup.company.com
```

**Configuration:**
- Set via `ALLOWED_ORIGINS` environment variable
- Comma-separated list of allowed domains
- No wildcards allowed
- `allow_credentials` disabled for security

---

### 2. Rate Limiting

**Protection against:**
- DoS (Denial of Service) attacks
- Resource exhaustion
- API abuse

**Default Limits:**
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_UPLOAD=5/minute    # Upload endpoint (strict)
RATE_LIMIT_API=30/minute      # Other API endpoints
```

**Customization:**
```bash
# Stricter limits for public deployment
RATE_LIMIT_UPLOAD=2/minute
RATE_LIMIT_API=10/minute

# More relaxed for internal use
RATE_LIMIT_UPLOAD=10/minute
RATE_LIMIT_API=100/minute
```

**Response on limit exceeded:**
```json
{
  "error": "Rate limit exceeded",
  "detail": "5 per 1 minute"
}
```

---

### 3. API Key Authentication

**Smart authentication** for external API clients while keeping the web UI accessible.

#### 🎯 How it works:

**Web Frontend (Browser):**
- ✅ **ALWAYS accessible** - No authentication required
- Users can use the web interface without any API key
- Detected via `Referer` header (automatically sent by browsers)

**API Clients (curl, scripts, external tools):**
- 🔒 **Requires API key** when `ENABLE_AUTH=true`
- Protects against unauthorized programmatic access
- Detected by absence of `Referer` header

#### 📝 Configuration:

```bash
# .env file
ENABLE_AUTH=true  # Enables auth for API clients (not web UI!)
API_KEY=your-super-secret-api-key-min-32-chars-recommended
```

#### 🔑 Generate secure API key:

```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

#### 🚀 Usage Examples:

**Web Browser (No auth needed):**
```
Just open: http://localhost:8000
Upload files normally through the UI ✅
```

**API Client (Requires auth):**
```bash
# With API key - Works ✅
curl -X POST http://localhost:8000/api/upload \
  -H "X-API-Key: your-api-key-here" \
  -F "files=@nextcloud.log"

# Without API key - Fails ❌
curl -X POST http://localhost:8000/api/upload \
  -F "files=@nextcloud.log"
# → 401 Unauthorized
```

#### 🔒 Protected Endpoints (API clients only):

When `ENABLE_AUTH=true`, these require `X-API-Key` header:
- `POST /api/upload` (only for API clients, web UI exempt)
- `GET /api/results/{id}` (only for API clients, web UI exempt)
- `GET /api/results` (only for API clients, web UI exempt)
- `DELETE /api/results/{id}` (only for API clients, web UI exempt)

#### 🌐 Always Public (No auth):

- `GET /` (homepage)
- `GET /results.html` (results page)
- `GET /health` (health check)
- `GET /api/config` (configuration info)

#### ⚠️ Important Notes:

- **Web UI is ALWAYS accessible** - Users never need to enter an API key
- **API key is for external tools only** (scripts, monitoring, integrations)
- Never commit API keys to version control (use `.env` file)
- Rotate API keys regularly in production

---

### 4. Automatic Cleanup

**Problem:** Results stored indefinitely → disk space exhaustion

**Solution:** Automatic deletion of old files

**Configuration:**
```bash
CLEANUP_ENABLED=true
CLEANUP_DAYS=7  # Retention period
```

**What gets cleaned:**
- Analysis results in `results/` directory
- Uploaded files in `uploads/` directory
- Files older than `CLEANUP_DAYS`

**Cleanup timing:**
- On application startup
- Can be manually triggered (future: scheduled task)

**Disable cleanup:**
```bash
CLEANUP_ENABLED=false  # Keep all results forever
```

---

### 5. File Upload Security

✅ **File size limits** (2GB default)
```bash
MAX_FILE_SIZE_MB=2048  # Configurable
```

✅ **File type validation**
- Only allowed: `.log`, `.txt`, `.gz`, `.zip`
- Rejects: `.exe`, `.sh`, `.php`, etc.

✅ **ZIP path traversal protection**
```python
# Only extracts files from logs/ directory
if file_info.startswith('logs/') and not file_info.endswith('/'):
    # Extract safely
```

✅ **No code execution**
- Files are parsed as text/JSON only
- No `eval()` or `exec()` calls
- Isolated processing

---

## 🚀 Production Deployment

### Minimal Security Configuration

```bash
# .env file
ALLOWED_ORIGINS=https://logs.yourcompany.com
ENABLE_AUTH=true
API_KEY=<generate-strong-key-here>
RATE_LIMIT_ENABLED=true
CLEANUP_ENABLED=true
CLEANUP_DAYS=30
MAX_FILE_SIZE_MB=1024
```

### Docker Compose with Security

```yaml
version: '3.8'

services:
  log-scanner:
    build: .
    ports:
      - "127.0.0.1:8000:8000"  # Only localhost (use reverse proxy)
    environment:
      - ALLOWED_ORIGINS=https://logs.company.com
      - ENABLE_AUTH=true
      - API_KEY=${API_KEY}  # From .env file
      - RATE_LIMIT_ENABLED=true
      - RATE_LIMIT_UPLOAD=3/minute
      - CLEANUP_ENABLED=true
      - CLEANUP_DAYS=14
    volumes:
      - ./uploads:/app/uploads
      - ./results:/app/results
      - ./logs:/app/logs  # Application logs
    restart: unless-stopped
    networks:
      - internal
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

networks:
  internal:
    driver: bridge
```

### Nginx Reverse Proxy (HTTPS)

```nginx
# /etc/nginx/sites-available/log-analyzer

upstream log_analyzer {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name logs.company.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name logs.company.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/logs.company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/logs.company.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Upload size limit
    client_max_body_size 2G;
    
    # Timeouts for large uploads
    client_body_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    
    # Proxy to FastAPI
    location / {
        proxy_pass http://log_analyzer;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Rate limiting (nginx level - additional to app)
    limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=5r/m;
    
    location /api/upload {
        limit_req zone=upload_limit burst=2 nodelay;
        proxy_pass http://log_analyzer;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Access logs
    access_log /var/log/nginx/log-analyzer-access.log;
    error_log /var/log/nginx/log-analyzer-error.log;
}
```

---

## 🔐 Data Privacy

### Sensitive Data in Logs

Log files contain:
- ✅ **Usernames** - Personal identifiers
- ✅ **IP addresses** - Network locations
- ✅ **File paths** - System structure
- ✅ **Timestamps** - Activity patterns
- ✅ **Error messages** - System information

### Privacy Recommendations

1. **Access Control**
   - Deploy in **private network** only
   - Use **VPN** for remote access
   - Enable **API authentication**

2. **Data Retention**
   - Set appropriate `CLEANUP_DAYS` (GDPR: 30 days recommended)
   - Regularly review stored results
   - Delete unnecessary analyses

3. **Network Isolation**
   - Use Docker internal networks
   - Firewall rules (only allow necessary ports)
   - No direct internet exposure

4. **Audit Logging**
   - Monitor `app.log` for access patterns
   - Review failed authentication attempts
   - Track uploaded files and analysis IDs

---

## 📋 Security Checklist

### Pre-Deployment

- [ ] **Change default API key** (if using authentication)
- [ ] **Set ALLOWED_ORIGINS** to your domain (not `*` or `localhost`)
- [ ] **Enable RATE_LIMIT** with appropriate limits
- [ ] **Configure AUTO_CLEANUP** retention period
- [ ] **Review MAX_FILE_SIZE_MB** limit
- [ ] **Set up HTTPS** with reverse proxy
- [ ] **Configure firewall** rules
- [ ] **Test authentication** is working
- [ ] **Verify CORS** only allows your domain

### Post-Deployment

- [ ] **Monitor logs** regularly (`app.log`)
- [ ] **Check disk usage** (uploads + results directories)
- [ ] **Review rate limit** effectiveness
- [ ] **Test cleanup** is running (check old files deleted)
- [ ] **Update dependencies** monthly (`docker-compose pull && docker-compose up -d`)
- [ ] **Backup critical results** before cleanup
- [ ] **Review access patterns** for anomalies
- [ ] **Document incidents** and responses

### Monthly Maintenance

- [ ] Review and rotate API keys
- [ ] Check for security updates
- [ ] Audit stored results
- [ ] Review rate limit logs
- [ ] Test backup restoration
- [ ] Update SSL certificates (if needed)

---

## 🚨 Incident Response

### Unauthorized Access Detected

1. **Immediate:**
   - Change `API_KEY` immediately
   - Review `app.log` for access patterns
   - Identify compromised analysis IDs

2. **Investigation:**
   - Check nginx/Apache logs for source IPs
   - Review uploaded files for malicious content
   - Verify no data exfiltration occurred

3. **Remediation:**
   - Block malicious IPs at firewall
   - Delete compromised results
   - Strengthen rate limits
   - Enable authentication if disabled

### Rate Limit Exceeded (Legitimate)

1. **Identify:**
   - Check logs: `Rate limit exceeded for IP: x.x.x.x`
   - Verify if legitimate user or attack

2. **Adjust:**
   ```bash
   # Increase limits for legitimate use
   RATE_LIMIT_UPLOAD=10/minute
   RATE_LIMIT_API=50/minute
   ```

3. **Whitelist (if needed):**
   - Use nginx `allow` directive for trusted IPs
   - Or implement IP whitelist in application

### Disk Space Full

1. **Immediate:**
   - Check `uploads/` and `results/` directories
   - Manual cleanup: `rm -rf uploads/* results/*`

2. **Fix:**
   ```bash
   # Reduce retention period
   CLEANUP_DAYS=3
   
   # Or reduce file size limit
   MAX_FILE_SIZE_MB=512
   ```

3. **Monitor:**
   - Set up disk usage alerts
   - Consider external storage (S3, NFS)

---

## 📞 Security Contacts

- **GitHub Issues:** https://github.com/xXRoxXeRXx/log-scanner/issues
- **Security Vulnerabilities:** Report privately via GitHub Security tab
- **General Support:** Create discussion on GitHub

---

## 📚 Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)

---

**Last Updated:** November 19, 2025  
**Version:** 2.0.1+  
**Maintainer:** xXRoxXeRXx
