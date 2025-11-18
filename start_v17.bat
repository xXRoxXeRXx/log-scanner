@echo off
REM Nextcloud Log Analyzer - Starter Script
REM Startet die refactored v17 Version

echo ========================================
echo  Nextcloud Log Analyzer v17.0
echo  Refactored Edition
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    echo Bitte installiere Python 3.8 oder hoeher.
    pause
    exit /b 1
)

REM Start the application
echo Starte Anwendung...
echo.
python log_analyzer_v17.py

REM If app closes with error, pause to show error message
if errorlevel 1 (
    echo.
    echo ========================================
    echo  Fehler beim Starten!
    echo ========================================
    pause
)
