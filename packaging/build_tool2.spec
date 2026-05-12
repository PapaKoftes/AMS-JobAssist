# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — Tool 2 (Trainer Dashboard), bundled as standalone Windows .exe.

Build:
    cd <repo-root>
    pyinstaller packaging/build_tool2.spec --distpath dist --workpath build

Note: Tool 2 PDF/DOCX bulk-export reaches into Tool 1's export modules at
runtime via sys.path. To keep the .exe self-contained we ALSO bundle Tool 1's
export package and its export-relevant deps.
"""
import os

PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))
TOOL2_ROOT   = os.path.join(PROJECT_ROOT, "tool-2-trainer-dashboard")
BACKEND_DIR  = os.path.join(TOOL2_ROOT, "src", "backend")
FRONTEND_DIR = os.path.join(TOOL2_ROOT, "frontend")
SHARED_DIR   = os.path.join(PROJECT_ROOT, "shared")
# Bundle Tool 1's export package + schema so the lazy sys.path import works
TOOL1_EXPORT_DIR = os.path.join(PROJECT_ROOT, "tool-1-cv-maker", "src", "backend", "export")
TOOL1_CV_DIR     = os.path.join(PROJECT_ROOT, "tool-1-cv-maker", "src", "backend", "cv")
ICON_PATH        = os.path.join(PROJECT_ROOT, "packaging", "icon.ico")

block_cipher = None

a = Analysis(
    [os.path.join(BACKEND_DIR, "app.py")],
    pathex=[BACKEND_DIR, PROJECT_ROOT],
    binaries=[],
    datas=[
        (FRONTEND_DIR, "frontend"),
        (BACKEND_DIR, os.path.join("src", "backend")),
        (SHARED_DIR, "shared"),
        # Bundle Tool 1's export + cv packages for bulk PDF/DOCX
        (TOOL1_EXPORT_DIR, os.path.join("tool-1-cv-maker", "src", "backend", "export")),
        (TOOL1_CV_DIR,     os.path.join("tool-1-cv-maker", "src", "backend", "cv")),
    ],
    hiddenimports=[
        "fastapi",
        "fastapi.middleware",
        "fastapi.middleware.cors",
        "fastapi.staticfiles",
        "starlette",
        "starlette.middleware",
        "starlette.middleware.base",
        "starlette.responses",
        "starlette.staticfiles",
        "pydantic",
        "pydantic_core",
        "pydantic_settings",
        "sqlalchemy",
        "sqlalchemy.dialects.sqlite",
        "sqlalchemy.engine",
        "sqlalchemy.orm",
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "python_multipart",
        # Export deps reachable via Tool 1 export package
        "reportlab",
        "reportlab.pdfgen",
        "reportlab.lib",
        "reportlab.platypus",
        "docx",
        "docx.shared",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "PIL.ImageTk",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "llama_cpp",  # Tool 2 doesn't need the LLM
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="AMS-JobAssist-Tool2",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
)
