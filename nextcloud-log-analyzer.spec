# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File für Nextcloud Log Analyzer Desktop
Unterstützt: Windows, macOS, Linux
Erstellt eine Single-File Executable ohne Admin-Rechte
"""

import sys
import platform
from pathlib import Path

# Projekt Root
project_root = Path(SPECPATH)

# Platform detection
IS_WINDOWS = platform.system() == 'Windows'
IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'

# Icon path based on platform
icon_file = None
if IS_WINDOWS:
    icon_path = project_root / 'backend' / 'static' / 'favicon.ico'
    if icon_path.exists():
        icon_file = str(icon_path)
elif IS_MACOS:
    icon_path = project_root / 'backend' / 'static' / 'favicon.icns'
    if icon_path.exists():
        icon_file = str(icon_path)
    # Fallback to .ico if .icns not available (PyInstaller converts automatically)
    elif (project_root / 'backend' / 'static' / 'favicon.ico').exists():
        icon_file = str(project_root / 'backend' / 'static' / 'favicon.ico')

# Alle Python-Dateien sammeln
backend_files = []
shared_files = []

# Backend-Dateien
for py_file in (project_root / 'backend').rglob('*.py'):
    if '__pycache__' not in str(py_file):
        backend_files.append((str(py_file), 'backend'))

# Shared-Dateien
for py_file in (project_root / 'shared').rglob('*.py'):
    if '__pycache__' not in str(py_file):
        shared_files.append((str(py_file), 'shared'))

# Static Files (HTML, CSS, JS, Logos, Favicons)
static_files = [
    (str(project_root / 'backend' / 'static'), 'backend/static'),
]

# Alle Dateien kombinieren
datas = static_files

a = Analysis(
    ['desktop_main.py'],
    pathex=[
        str(project_root),
        str(project_root / 'backend'),
        str(project_root / 'shared'),
    ],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'pydantic',
        'pydantic_core',
        'aiofiles',
        'backend.main',
        'shared.config',
        'shared.parser',
        'shared.data_store',
        'shared.web_parser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Nextcloud-Log-Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True = Zeigt Konsole für Logs
    disable_windowed_traceback=False,
    argv_emulation=IS_MACOS,  # Enable on macOS for drag & drop
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version_file=None,
)

# macOS-specific: Create .app bundle
if IS_MACOS:
    app = BUNDLE(
        exe,
        name='Nextcloud-Log-Analyzer.app',
        icon=icon_file,
        bundle_identifier='com.ionos.nextcloud-log-analyzer',
        info_plist={
            'CFBundleName': 'Nextcloud Log Analyzer',
            'CFBundleDisplayName': 'Nextcloud Log Analyzer',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra
            'NSRequiresAquaSystemAppearance': False,  # Dark Mode support
        },
    )
