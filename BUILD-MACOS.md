# macOS Build Anleitung

## Voraussetzungen

1. **macOS 10.13+** (High Sierra oder neuer)
2. **Xcode Command Line Tools:**
   ```bash
   xcode-select --install
   ```
3. **Python 3.11+:**
   ```bash
   # Mit Homebrew:
   brew install python@3.11
   
   # Oder von python.org:
   # https://www.python.org/downloads/macos/
   ```

## Schnell-Build

```bash
# 1. Repository klonen
git clone https://github.com/xXRoxXeRXx/log-scanner.git
cd log-scanner
git checkout desktop

# 2. Scripts ausführbar machen
chmod +x build.sh create-macos-icon.sh

# 3. Build ausführen
./build.sh

# 4. Application testen
open dist/Nextcloud-Log-Analyzer.app
```

## Schritt-für-Schritt

### 1. Dependencies installieren

```bash
# PyInstaller und Requirements
pip3 install -r requirements.txt
pip3 install pyinstaller
```

### 2. macOS Icon erstellen (optional)

Das Build-Script macht das automatisch, aber manuell:

```bash
./create-macos-icon.sh
# Erstellt: backend/static/favicon.icns
```

### 3. Build ausführen

```bash
pyinstaller --clean nextcloud-log-analyzer.spec
```

**Output:**
```
dist/
└── Nextcloud-Log-Analyzer.app/
    ├── Contents/
    │   ├── Info.plist
    │   ├── MacOS/
    │   │   └── Nextcloud-Log-Analyzer  # Binary
    │   └── Resources/
    │       └── favicon.icns
    └── ...
```

### 4. Application testen

```bash
# Variante 1: Über Finder
open dist/Nextcloud-Log-Analyzer.app

# Variante 2: Direkt Binary
dist/Nextcloud-Log-Analyzer.app/Contents/MacOS/Nextcloud-Log-Analyzer

# Variante 3: Mit Optionen
dist/Nextcloud-Log-Analyzer.app/Contents/MacOS/Nextcloud-Log-Analyzer --port 9000
```

## Build-Optionen

### UPX Komprimierung

Für kleinere Binaries:

```bash
# UPX installieren
brew install upx

# Automatisch verwendet wenn vorhanden
./build.sh
```

### DMG erstellen (Distribution)

```bash
# Nach erfolgreichem Build:
hdiutil create -volname "Nextcloud Log Analyzer" \
  -srcfolder dist/Nextcloud-Log-Analyzer.app \
  -ov -format UDZO \
  Nextcloud-Log-Analyzer.dmg
```

### Code Signing (optional)

Für Distribution außerhalb des App Store:

```bash
# 1. Developer Certificate holen (Apple Developer Account nötig)

# 2. Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  dist/Nextcloud-Log-Analyzer.app

# 3. Verify
codesign --verify --verbose dist/Nextcloud-Log-Analyzer.app
spctl -a -v dist/Nextcloud-Log-Analyzer.app
```

### Notarization (für Gatekeeper)

```bash
# 1. Create archive
ditto -c -k --keepParent dist/Nextcloud-Log-Analyzer.app \
  Nextcloud-Log-Analyzer.zip

# 2. Submit to Apple
xcrun notarytool submit Nextcloud-Log-Analyzer.zip \
  --apple-id "your@email.com" \
  --team-id "TEAMID" \
  --password "app-specific-password"

# 3. Staple ticket
xcrun stapler staple dist/Nextcloud-Log-Analyzer.app
```

## Troubleshooting

### Problem: "Python not found"

```bash
# Check Python installation
which python3
python3 --version

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"
```

### Problem: "iconutil not found"

```bash
# Install Xcode Command Line Tools
xcode-select --install
```

### Problem: ".app won't open - unidentified developer"

```bash
# Option 1: Control-click → Open
# Option 2: System Settings → Security & Privacy → Allow

# Option 3: Remove quarantine
xattr -d com.apple.quarantine dist/Nextcloud-Log-Analyzer.app
```

### Problem: "Port already in use"

```bash
# Use different port
dist/Nextcloud-Log-Analyzer.app/Contents/MacOS/Nextcloud-Log-Analyzer --port 9000
```

### Problem: Build-Error "module not found"

```bash
# Clean cache and rebuild
rm -rf build/ dist/
pip3 install --upgrade -r requirements.txt
pyinstaller --clean nextcloud-log-analyzer.spec
```

## App Bundle Struktur

```
Nextcloud-Log-Analyzer.app/
├── Contents/
│   ├── Info.plist              # Bundle Info
│   ├── MacOS/
│   │   └── Nextcloud-Log-Analyzer  # Binary (~15 MB)
│   ├── Resources/
│   │   └── favicon.icns        # Icon
│   └── Frameworks/             # Dependencies
│       └── Python.framework/   # Embedded Python
```

## Performance

- **Build Zeit:** ~2-3 Minuten
- **Bundle Größe:** ~18 MB
- **Start Zeit:** ~2-3 Sekunden
- **RAM Usage:** ~50-80 MB

## Distribution

### Für End-User:

1. **DMG erstellen** (siehe oben)
2. **Auf GitHub releasen:**
   ```bash
   gh release create v1.0-desktop \
     dist/Nextcloud-Log-Analyzer.dmg \
     --title "Desktop v1.0 (macOS)" \
     --notes "macOS Application Bundle"
   ```

### Für Entwickler:

- Ungesigntes .app Bundle funktioniert lokal
- Für externe Distribution: Code Signing + Notarization empfohlen

## GitHub Actions (Automatisch)

Der Workflow `.github/workflows/build-desktop.yml` baut automatisch:

```bash
# Push triggert Build
git push origin desktop

# Artifacts downloaden von:
# GitHub → Actions → Build Desktop Executables → Artifacts
```

## Nächste Schritte

1. **Lokaler Test:** `./build.sh && open dist/*.app`
2. **GitHub Actions:** Push triggert automatischen Build
3. **Release:** Tag `v1.0-desktop` für automatisches Release

---

**Bei Fragen:** [GitHub Issues](https://github.com/xXRoxXeRXx/log-scanner/issues)
