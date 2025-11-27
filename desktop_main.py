"""
Desktop-Version des Nextcloud Log Analyzers
Startet FastAPI-Server und öffnet automatisch den Browser
"""
import sys
import os
import webbrowser
import threading
import time
import signal
from pathlib import Path

# Add backend and shared to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "backend"))
sys.path.insert(0, str(current_dir / "shared"))

import uvicorn
from backend.main import app

# Determine if running as PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running as script
    BASE_DIR = Path(__file__).parent


class DesktopServer:
    """Desktop-Server mit Auto-Browser-Start"""
    
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.server = None
        self.should_stop = False
        
    def open_browser(self):
        """Öffnet Browser nach kurzer Verzögerung"""
        time.sleep(2)  # Warte bis Server läuft
        url = f"http://{self.host}:{self.port}"
        print(f"\n🌐 Öffne Browser: {url}\n")
        webbrowser.open(url)
        
    def signal_handler(self, signum, frame):
        """Behandelt CTRL+C für sauberes Herunterfahren"""
        print("\n\n🛑 Server wird heruntergefahren...")
        self.should_stop = True
        sys.exit(0)
        
    def run(self):
        """Startet Server und Browser"""
        # Signal Handler registrieren
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("=" * 60)
        print("🔍 Nextcloud Log Analyzer - Desktop Version")
        print("=" * 60)
        print(f"\n📡 Server startet auf http://{self.host}:{self.port}")
        print(f"📁 Arbeitsverzeichnis: {os.getcwd()}")
        print(f"\n💡 Tipps:")
        print("   - Browser öffnet sich automatisch")
        print("   - Zum Beenden: CTRL+C drücken")
        print("   - Port ändern: --port <port>")
        print("\n" + "=" * 60 + "\n")
        
        # Browser in separatem Thread öffnen
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()
        
        # Server starten
        try:
            uvicorn.run(
                app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=False  # Weniger Spam in der Konsole
            )
        except KeyboardInterrupt:
            print("\n\n🛑 Server wird heruntergefahren...")
        except Exception as e:
            print(f"\n❌ Fehler beim Starten: {e}")
            input("\nDrücke Enter zum Beenden...")
            sys.exit(1)


def main():
    """Main Entry Point"""
    # Parse command line arguments
    host = "127.0.0.1"
    port = 8000
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg == "--port" and i + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[i + 1])
                except ValueError:
                    print(f"❌ Ungültiger Port: {sys.argv[i + 1]}")
                    sys.exit(1)
            elif arg == "--host" and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
            elif arg in ["--help", "-h"]:
                print("Nextcloud Log Analyzer - Desktop Version")
                print("\nVerwendung:")
                print("  nextcloud-log-analyzer.exe [optionen]")
                print("\nOptionen:")
                print("  --host <host>    Server Host (Standard: 127.0.0.1)")
                print("  --port <port>    Server Port (Standard: 8000)")
                print("  --help, -h       Diese Hilfe anzeigen")
                sys.exit(0)
    
    # Server starten
    server = DesktopServer(host=host, port=port)
    server.run()


if __name__ == "__main__":
    main()
