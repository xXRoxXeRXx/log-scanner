# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File für Nextcloud Log Analyzer Desktop
Erstellt eine Single-File .exe ohne Admin-Rechte
"""

import sys
from pathlib import Path

# Projekt Root
project_root = Path(SPECPATH)

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
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'backend' / 'static' / 'favicon.ico') if (project_root / 'backend' / 'static' / 'favicon.ico').exists() else None,
    version_file=None,
)
