# Upload-Limits Konfiguration

## Aktuelle Einstellungen

- **Max. Dateigröße**: 2 GB pro Datei
- **Unterstützte Formate**: `.log`, `.txt`, `.gz`

## Server-Start für große Dateien

### Development Mode (start-web.ps1)

Das Start-Script ist bereits konfiguriert für große Uploads:

```powershell
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --limit-max-requests 10000 --timeout-keep-alive 300
```

### Manueller Start

Wenn du den Server manuell startest, verwende diese Optionen:

```bash
# Windows PowerShell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --limit-max-requests 10000 --timeout-keep-alive 300

# Linux/macOS
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --limit-max-requests 10000 --timeout-keep-alive 300
```

### Docker (nginx reverse proxy)

Wenn du Docker mit nginx verwendest, füge in der nginx-Konfiguration hinzu:

```nginx
client_max_body_size 2048M;
proxy_read_timeout 600;
proxy_connect_timeout 600;
proxy_send_timeout 600;
```

## Performance-Hinweise

### Große Dateien (> 500 MB)

- **Parsing kann mehrere Minuten dauern**
- Browser-Tab offen lassen während des Uploads
- Bei sehr großen Dateien: Empfohlen, die Desktop-Version zu verwenden

### Memory-Verbrauch

- Beim Parsen wird die gesamte Datei im Speicher gehalten
- Empfohlener RAM: Mindestens 4 GB frei
- Bei mehreren gleichzeitigen Uploads kann der Speicher knapp werden

### Timeout-Einstellungen

Die Standard-Timeouts sind auf große Dateien ausgelegt:
- **timeout-keep-alive**: 300 Sekunden (5 Minuten)
- Browser-Timeouts können separat auftreten (abhängig vom Browser)

## Limits anpassen

### Backend (backend/main.py)

```python
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB in bytes
```

### Frontend (backend/static/index.html)

```javascript
// Check file size (2GB limit)
const oversized = validFiles.filter(f => f.size > 2 * 1024 * 1024 * 1024);
```

## Troubleshooting

### "413 Request Entity Too Large"

- Prüfe nginx/reverse proxy Konfiguration
- Erhöhe `client_max_body_size` in nginx

### "Connection Timeout"

- Erhöhe `--timeout-keep-alive` beim Uvicorn-Start
- Prüfe Browser-Timeouts (Edge: max 10 Minuten)

### "Out of Memory"

- Reduziere `MAX_FILE_SIZE`
- Verarbeite große Dateien einzeln
- Verwende Desktop-Version für sehr große Logs
