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
echo "Executable: dist/Nextcloud-Log-Analyzer"
echo ""
echo "Größe:"
ls -lh dist/Nextcloud-Log-Analyzer | awk '{print "  " $5}'
echo ""
echo "Zum Testen:"
echo "  cd dist"
echo "  ./Nextcloud-Log-Analyzer"
echo ""
echo "=========================================="
echo ""
