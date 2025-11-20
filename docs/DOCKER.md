# Nextcloud Log Analyzer - Docker Web Deployment

## 🐳 Quick Start

### Option 1: Docker Compose (Empfohlen)

```bash
# Build und starten
docker-compose up -d

# Zugriff über Browser
http://localhost:8000
```

### Option 2: Docker direkt

```bash
# Build image
docker build -t log-scanner .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  --name log-scanner \
  log-scanner

# Zugriff über Browser
http://localhost:8000
```

## 📋 Features

- ✅ **File Upload**: Drag & Drop .log/.gz/.zip Dateien
- ✅ **ZIP Support**: Automatische Extraktion von Client-Logs aus ZIP-Archiven
- ✅ **Synchrone Analyse**: Keine Background-Jobs, sofortige Ergebnisse
- ✅ **Root Cause Analysis**: 15 intelligente Muster-Erkennungen (Redis, S3, WebDAV, PHP, Client-Errors)
- ✅ **Click-to-Filter**: Direkte Filterung aus Root Cause Cards
- ✅ **Visualisierung**: Charts mit Chart.js
- ✅ **Historie**: Alle Analysen gespeichert
- ✅ **Export**: JSON Download
- ✅ **Lightweight**: Single Container, ~200MB Image

## 🛠️ Architektur

```
┌─────────────────────────────────────┐
│     Single Docker Container         │
│  ┌───────────────────────────────┐  │
│  │   FastAPI Backend (Port 8000) │  │
│  │   + Static Files (Alpine.js)  │  │
│  │   + Parser Logic              │  │
│  └───────────────────────────────┘  │
│                                     │
│  Volumes:                           │
│  - /app/uploads (temp)              │
│  - /app/results (persistent)        │
└─────────────────────────────────────┘
```

## 📚 API Endpoints

```
GET    /                      # Frontend (index.html)
GET    /results.html          # Results page
GET    /health                # Health check
POST   /api/upload            # Upload & analyze
GET    /api/results/{id}      # Get analysis result
GET    /api/results           # List all results
DELETE /api/results/{id}      # Delete result
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=backend --cov=shared
```

## 🔧 Development

### Lokal ohne Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
cd backend
python main.py

# Or with uvicorn auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Mit Docker Development Mode:

```bash
# Build with live code mounting
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/backend:/app/backend \
  -v $(pwd)/shared:/app/shared \
  log-scanner
```

## 📦 Deployment

### Production Deployment:

1. **Build optimized image**:
   ```bash
   docker build -t log-scanner:prod --target production .
   ```

2. **Run with constraints**:
   ```bash
   docker run -d \
     -p 8000:8000 \
     --memory="512m" \
     --cpus="1.0" \
     -v /data/uploads:/app/uploads \
     -v /data/results:/app/results \
     --restart=always \
     log-scanner:prod
   ```

3. **Optional: Nginx Reverse Proxy**:
   ```nginx
   server {
       listen 80;
       server_name logs.example.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🔒 Security

- **File Size Limit**: 2GB per file
- **Allowed Extensions**: .log, .txt, .gz, .zip only
- **ZIP Extraction**: Only files from `logs/` directory extracted
- **CORS**: Configure for production domains
- **Rate Limiting**: Add nginx rate limiting if needed

## 📊 Monitoring

### Health Check:

```bash
curl http://localhost:8000/health
```

### Docker Logs:

```bash
docker logs -f log-scanner
```

### Container Stats:

```bash
docker stats log-scanner
```

## 🐛 Troubleshooting

### Container won't start:

```bash
# Check logs
docker logs log-scanner

# Check if port is already in use
netstat -an | grep 8000

# Rebuild image
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Parser errors:

```bash
# Check shared/ directory is copied
docker exec log-scanner ls -la /app/shared

# Check Python import
docker exec log-scanner python -c "from shared.web_parser import analyze_log_files"
```

### File upload fails:

```bash
# Check upload directory permissions
docker exec log-scanner ls -la /app/uploads

# Check volume mount
docker inspect log-scanner | grep Mounts
```

## 📈 Performance

- **Upload**: < 10s for 10MB file
- **Analysis**: Depends on file size, ~1s per 1000 lines
- **Memory**: ~200-300MB RAM
- **Storage**: Results stored as JSON (~1KB per analysis)

## 🔄 Updates

```bash
# Pull latest changes
git pull origin dockerweb

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## 🗑️ Cleanup

```bash
# Stop and remove container
docker-compose down

# Remove volumes (deletes all results!)
docker-compose down -v

# Remove image
docker rmi log-scanner
```

## 📝 Environment Variables

```bash
# .env file (optional)
PORT=8000
MAX_UPLOAD_SIZE=52428800  # 50MB
PYTHONUNBUFFERED=1
```

## 🆘 Support

- **Issues**: GitHub Issues
- **Logs**: Check `docker logs log-scanner`
- **Health**: Check `/health` endpoint

## 📜 License

See LICENSE file in repository.
