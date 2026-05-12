# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — Launcher .exe that starts both Tool 1 and Tool 2 and opens
the default browser.

Build:
    cd <repo-root>
    pyinstaller packaging/launcher.spec --distpath dist --workpath build
"""
import os

PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))
LAUNCHER_PY  = os.path.join(PROJECT_ROOT, "launcher.py")
ICON_PATH    = os.path.join(PROJECT_ROOT, "packaging", "icon.ico")

block_cipher = None

a = Analysis(
    [LAUNCHER_PY],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "PyQt5", "PyQt6", "PySide2", "PySide6"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="AMS-JobAssist-Launcher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
)
