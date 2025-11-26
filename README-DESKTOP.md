# 🖥️ Nextcloud Log Analyzer - Desktop Version

> **Portable Windows Executable - KEINE Admin-Rechte erforderlich!**

## 📦 Was ist das?

Eine **Single-File `.exe`** des Nextcloud Log Analyzers, die:
- ✅ **Keine Installation** benötigt
- ✅ **Keine Admin-Rechte** erfordert
- ✅ Automatisch den **Browser öffnet**
- ✅ Auf jedem Windows 10/11 PC läuft
- ✅ Alle Features der Web-Version enthält

---

## 🚀 Schnellstart (für Endnutzer)

### Option A: Fertige .exe nutzen (EINFACHSTE)

1. **Download** die `.exe` aus den Releases
2. **Doppelklick** auf `Nextcloud-Log-Analyzer.exe`
3. **Browser öffnet sich automatisch**
4. **Fertig!** 🎉

### Verwendung:

```
Nextcloud-Log-Analyzer.exe          # Startet auf Port 8000
Nextcloud-Log-Analyzer.exe --port 9000  # Anderer Port
Nextcloud-Log-Analyzer.exe --help   # Hilfe anzeigen
```

**Beenden:**
- `CTRL + C` in der Konsole
- Oder einfach Konsolen-Fenster schließen

---

## 🔨 Build (für Entwickler)

### Voraussetzungen:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Git** (optional, für Clone)

### Build-Prozess:

#### Windows:

```batch
# 1. Repository klonen
git clone https://github.com/xXRoxXeRXx/log-scanner.git
cd log-scanner
git checkout desktop

# 2. Build ausführen (installiert automatisch PyInstaller)
build.bat

# 3. Executable testen
cd dist
Nextcloud-Log-Analyzer.exe
```

#### Linux/Mac:

```bash
# 1. Repository klonen
git clone https://github.com/xXRoxXeRXx/log-scanner.git
cd log-scanner
git checkout desktop

# 2. Build-Script ausführbar machen
chmod +x build.sh

# 3. Build ausführen
./build.sh

# 4. Executable testen
cd dist
./Nextcloud-Log-Analyzer
```

### Manueller Build:

```bash
# 1. Dependencies installieren
pip install -r requirements.txt
pip install pyinstaller

# 2. Build
pyinstaller --clean nextcloud-log-analyzer.spec

# 3. Fertig!
# Executable liegt in: dist/Nextcloud-Log-Analyzer.exe
```

---

## 📁 Projekt-Struktur

```
log-scanner/
├── desktop_main.py              # Desktop Entry Point (Auto-Browser)
├── nextcloud-log-analyzer.spec  # PyInstaller Config
├── build.bat                    # Windows Build-Script
├── build.sh                     # Linux/Mac Build-Script
├── requirements-desktop.txt     # Desktop Dependencies
├── backend/                     # FastAPI Backend
│   ├── main.py                 # API Server
│   └── static/                 # HTML/CSS/JS/Assets
├── shared/                      # Shared Logic
│   ├── config.py
│   ├── parser.py
│   └── ...
└── dist/                        # Build Output
    └── Nextcloud-Log-Analyzer.exe  # Final Executable
```

---

## ⚙️ Technische Details

### Was wird gebündelt?

- **FastAPI** Server
- **Uvicorn** ASGI Server
- **Alle Static Files** (HTML, CSS, JS, Logos)
- **Python Runtime** (embedded)
- **Alle Dependencies**

### Größe:

- **~50-70 MB** Single-File .exe
- Kann mit UPX auf ~30-40 MB komprimiert werden

### PyInstaller Spec Features:

```python
# Aus nextcloud-log-analyzer.spec:
- Single-File Executable (--onefile)
- Konsolen-Fenster für Logs (console=True)
- IONOS Favicon als Icon
- UPX Komprimierung aktiviert
- Alle Static Files gebündelt
```

### Security:

- ✅ Läuft nur lokal (`127.0.0.1`)
- ✅ Keine Admin-Rechte nötig
- ✅ Keine Registry-Änderungen
- ✅ Keine System-Dateien
- ✅ Portable - läuft aus jedem Ordner

---

## 🐛 Troubleshooting

### Build schlägt fehl

**Problem:** `PyInstaller not found`
```bash
# Lösung:
pip install pyinstaller
```

**Problem:** `Module not found` während Build
```bash
# Lösung: Hidden imports in .spec hinzufügen
# Siehe nextcloud-log-analyzer.spec -> hiddenimports=[]
```

**Problem:** `.exe` zu groß (>100 MB)
```bash
# Lösung 1: UPX installieren
# Download: https://upx.github.io/
# Automatisch verwendet wenn im PATH

# Lösung 2: excludes in .spec erweitern
excludes=[
    'matplotlib', 'numpy', 'pandas', ...
]
```

### Runtime-Probleme

**Problem:** Browser öffnet nicht
- Manuell öffnen: `http://127.0.0.1:8000`
- Port bereits belegt? → `--port 9000` verwenden

**Problem:** "Port already in use"
```bash
# Lösung: Anderen Port verwenden
Nextcloud-Log-Analyzer.exe --port 9000
```

**Problem:** Antivirus blockiert .exe
- **False Positive** - PyInstaller-Executables werden oft fälschlicherweise erkannt
- Lösung: Ausnahme in Antivirus hinzufügen
- Oder: Source-Code inspizieren und selbst builden

---

## 🔄 Updates

### Neue Version builden:

```bash
# 1. Code aktualisieren
git pull origin desktop

# 2. Neu builden
build.bat  # oder ./build.sh

# 3. Neue .exe in dist/
```

### Version anzeigen:

```bash
Nextcloud-Log-Analyzer.exe --help
```

---

## 📋 Command-Line Options

```
Nextcloud-Log-Analyzer.exe [optionen]

Optionen:
  --host <host>    Server Host (Standard: 127.0.0.1)
  --port <port>    Server Port (Standard: 8000)
  --help, -h       Hilfe anzeigen
```

**Beispiele:**

```bash
# Standard (Port 8000, localhost)
Nextcloud-Log-Analyzer.exe

# Anderer Port
Nextcloud-Log-Analyzer.exe --port 9000

# Netzwerk-Zugriff erlauben (VORSICHT!)
Nextcloud-Log-Analyzer.exe --host 0.0.0.0 --port 8000
```

---

## 🎯 Use Cases

### 1. Support-Mitarbeiter
- **Szenario:** Logs vor Ort beim Kunden analysieren
- **Lösung:** .exe auf USB-Stick → einstecken → starten
- **Vorteil:** Keine Installation, keine Admin-Rechte

### 2. Offline-Umgebung
- **Szenario:** Firmen-PC ohne Internet/Admin
- **Lösung:** .exe per File-Share verteilen
- **Vorteil:** Funktioniert komplett offline

### 3. Schnelle Ad-hoc Analyse
- **Szenario:** Kurz mal Logs checken
- **Lösung:** .exe starten → Logs droppen → fertig
- **Vorteil:** Kein Docker, kein Setup

---

## 📦 Distribution

### Für Endnutzer bereitstellen:

1. **GitHub Release erstellen:**
   ```bash
   # Nach Build:
   cd dist
   # ZIP erstellen
   powershell Compress-Archive -Path Nextcloud-Log-Analyzer.exe -DestinationPath Nextcloud-Log-Analyzer-v1.0.zip
   ```

2. **Release hochladen:**
   - GitHub → Releases → New Release
   - Tag: `v1.0-desktop`
   - Anhang: `Nextcloud-Log-Analyzer-v1.0.zip`

3. **README verlinken:**
   ```markdown
   ## Download
   [Windows .exe (v1.0)](https://github.com/xXRoxXeRXx/log-scanner/releases/tag/v1.0-desktop)
   ```

---

## 🤝 Contributing

### Desktop-spezifische Änderungen:

1. Branch: `desktop`
2. Dateien:
   - `desktop_main.py` - Entry Point
   - `nextcloud-log-analyzer.spec` - Build Config
   - `build.bat` / `build.sh` - Build Scripts

3. Testen:
   ```bash
   # Nach Änderungen:
   build.bat
   cd dist
   Nextcloud-Log-Analyzer.exe
   ```

---

## 📝 License

Siehe [LICENSE](../LICENSE) im Root-Verzeichnis.

---

## 🙏 Credits

- **FastAPI** - Web Framework
- **Uvicorn** - ASGI Server
- **PyInstaller** - Executable Builder
- **IONOS** - Branding & Sponsoring

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/xXRoxXeRXx/log-scanner/issues)
- **Diskussionen:** [GitHub Discussions](https://github.com/xXRoxXeRXx/log-scanner/discussions)
- **Email:** [Support kontaktieren]

---

**Viel Erfolg! 🚀**
