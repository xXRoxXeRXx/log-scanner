@echo off
REM ========================================
REM Nextcloud Log Analyzer - Build Script
REM Erstellt Single-File .exe mit PyInstaller
REM ========================================

echo.
echo ==========================================
echo  Nextcloud Log Analyzer - Build Script
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nicht gefunden!
    echo Bitte Python 3.11+ installieren: https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python gefunden
python --version

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [2/5] PyInstaller wird installiert...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] PyInstaller Installation fehlgeschlagen!
        pause
        exit /b 1
    )
) else (
    echo [2/5] PyInstaller bereits installiert
)

REM Install dependencies
echo.
echo [3/5] Dependencies werden installiert...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency Installation fehlgeschlagen!
    pause
    exit /b 1
)

REM Clean previous builds
echo.
echo [4/5] Alte Builds werden geloescht...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build with PyInstaller
echo.
echo [5/5] Executable wird erstellt...
echo Dies kann einige Minuten dauern...
echo.
pyinstaller --clean nextcloud-log-analyzer.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build fehlgeschlagen!
    pause
    exit /b 1
)

REM Success
echo.
echo ==========================================
echo  BUILD ERFOLGREICH!
echo ==========================================
echo.
echo Executable: dist\Nextcloud-Log-Analyzer.exe
echo.
echo Groesse:
for %%F in ("dist\Nextcloud-Log-Analyzer.exe") do echo   %%~zF Bytes (%%~zF / 1048576 = ~%%F MB)
echo.
echo Zum Testen:
echo   cd dist
echo   Nextcloud-Log-Analyzer.exe
echo.
echo ==========================================
echo.

pause
