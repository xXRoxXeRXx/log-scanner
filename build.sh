#!/bin/bash
# ========================================
# Nextcloud Log Analyzer - Build Script (Linux/Mac)
# Erstellt Single-File Binary mit PyInstaller
# ========================================

echo ""
echo "=========================================="
echo " Nextcloud Log Analyzer - Build Script"
echo "=========================================="
echo ""

# Detect platform
OS_TYPE=$(uname -s)
case "$OS_TYPE" in
    Darwin*)
        PLATFORM="macOS"
        EXECUTABLE_NAME="Nextcloud-Log-Analyzer.app"
        ;;
    Linux*)
        PLATFORM="Linux"
        EXECUTABLE_NAME="Nextcloud-Log-Analyzer"
        ;;
    *)
        PLATFORM="Unknown"
        EXECUTABLE_NAME="Nextcloud-Log-Analyzer"
        ;;
esac

echo "Platform detected: $PLATFORM"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 nicht gefunden!"
    echo "Bitte Python 3.11+ installieren"
    exit 1
fi

echo "[1/5] Python gefunden"
python3 --version

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo ""
    echo "[2/5] PyInstaller wird installiert..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "[ERROR] PyInstaller Installation fehlgeschlagen!"
        exit 1
    fi
else
    echo "[2/5] PyInstaller bereits installiert"
fi

# Install dependencies
echo ""
echo "[3/5] Dependencies werden installiert..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Dependency Installation fehlgeschlagen!"
    exit 1
fi

# macOS: Create icon if needed
if [ "$PLATFORM" = "macOS" ]; then
    if [ ! -f "backend/static/favicon.icns" ]; then
        echo ""
        echo "[3.5/5] macOS Icon wird erstellt..."
        if command -v iconutil &> /dev/null; then
            chmod +x create-macos-icon.sh
            ./create-macos-icon.sh
        else
            echo "Warning: iconutil not found, skipping .icns creation"
        fi
    fi
fi

# Clean previous builds
echo ""
echo "[4/5] Alte Builds werden gelöscht..."
rm -rf dist build

# Build with PyInstaller
echo ""
echo "[5/5] Executable wird erstellt..."
echo "Dies kann einige Minuten dauern..."
echo ""
pyinstaller --clean nextcloud-log-analyzer.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Build fehlgeschlagen!"
    exit 1
fi

# Success
echo ""
echo "=========================================="
echo " BUILD ERFOLGREICH!"
echo "=========================================="
echo ""

if [ "$PLATFORM" = "macOS" ]; then
    echo "Application Bundle: dist/$EXECUTABLE_NAME"
    echo ""
    echo "Größe:"
    du -sh "dist/$EXECUTABLE_NAME" | awk '{print "  " $1}'
    echo ""
    echo "Zum Testen:"
    echo "  open dist/$EXECUTABLE_NAME"
    echo "  # oder"
    echo "  dist/$EXECUTABLE_NAME/Contents/MacOS/Nextcloud-Log-Analyzer"
else
    echo "Executable: dist/$EXECUTABLE_NAME"
    echo ""
    echo "Größe:"
    ls -lh "dist/$EXECUTABLE_NAME" | awk '{print "  " $5}'
    echo ""
    echo "Zum Testen:"
    echo "  cd dist"
    echo "  ./$EXECUTABLE_NAME"
fi

echo ""
echo "=========================================="
echo ""
