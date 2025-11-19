# 🚀 Quick Start Guide - Nextcloud Log Analyzer

## Installation (60 Sekunden)

```powershell
# 1. In Projekt-Verzeichnis wechseln
cd "d:\DEV Projekte\log-scanner"

# 2. Dependencies installieren (optional, aber empfohlen)
pip install tkinterdnd2 openpyxl

# 3. Starten!
python log_scanner.py
```

## Erste Schritte

### Variante 1: Drag & Drop
1. Anwendung starten
2. Log-Datei ins Fenster ziehen
3. Fertig! Ergebnisse werden angezeigt

### Variante 2: File Browser
1. Anwendung starten
2. "📂 Datei suchen..." klicken
3. Log-Datei auswählen
4. Fertig!

### Variante 3: Clipboard
1. Log-Inhalt kopieren (Strg+C)
2. Anwendung starten
3. "📋 Aus Zwischenablage" klicken
4. Fertig!

## Was macht die App?

### Bei Server Logs (JSON)
```json
{"level":3,"time":"2025-01-01T12:00:00","message":"HTTP/1.1 404"}
```

**Zeigt:**
- ❌ S3/HTTP Fehler (404, 500, etc.)
- ❌ WebDAV Fehler
- ❌ PHP Fehler
- ⚠️ Warnungen
- ℹ️ Infos & Debug

### Bei Client Logs (Text)
```
2025-01-01 12:00:00:000 [ info sync ]: >========== Sync started
```

**Zeigt:**
- 📖 Chronologische "Story" des Syncs
- 📤 Uploads & Downloads
- ❌ Fehler & Probleme
- ⚡ Fortschritts-Events

## Ergebnisse nutzen

### Kategorien erkunden
- Klick auf Kategorien (z.B. "S3 HTTP Fehler: 42x")
- Detaillierte Tabelle öffnet sich

### Export
- **Markdown**: Klick auf "📋 Kopieren (Markdown)" → Strg+V
- **Excel**: Klick auf "📊 Exportieren (Excel)" → Datei speichern

## Konfiguration (optional)

Bearbeite `config.py`:

```python
# Für riesige Dateien
MAX_FILE_SIZE_MB = 1000        # Standard: 500

# Mehr Einträge speichern
MAX_ENTRIES_PER_CATEGORY = 50000  # Standard: 10000
```

## Troubleshooting

### "tkinterdnd2 not available"
```powershell
pip install tkinterdnd2
```
→ Oder: Ignorieren und File Browser nutzen

### "Datei zu groß"
→ Erhöhe `MAX_FILE_SIZE_MB` in `config.py`

### "Einträge verworfen"
→ Erhöhe `MAX_ENTRIES_PER_CATEGORY` in `config.py`

### Anwendung friert
→ Warte kurz! Große Dateien werden im Hintergrund verarbeitet

## Tipps & Tricks

### Performance
- Dateien > 10 MB nutzen automatisch Threading
- Fortschrittsbalken zeigt Status
- Bei sehr großen Dateien (>100 MB): Geduld!

### Best Practices
- Teste mit kleinen Dateien zuerst
- Nutze Filter in Log-Dateien vor dem Import
- Exportiere nur benötigte Kategorien

### Regex-Anpassungen
Für eigene Log-Formate:
1. Öffne `server_parser.py` oder `client_parser.py`
2. Passe Regex-Patterns an
3. Speichern & neu starten

## Weiterführende Dokumentation

- **Vollständige Doku**: Siehe `README.md`
- **Changelog**: Siehe `CHANGELOG.md`
- **Tests**: `python test_analyzer.py`

## Support

Probleme? → [GitHub Issues](https://github.com/xXRoxXeRXx/log-scanner/issues)

---

**Happy Log Analyzing! 🎉**
