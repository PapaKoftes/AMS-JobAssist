# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — Tool 1 (CV Maker), bundled as standalone Windows .exe.

Build:
    cd <repo-root>
    pyinstaller packaging/build_tool1.spec --distpath dist --workpath build

This spec is path-agnostic — it derives repo root from SPECPATH so the build
works from any working directory.
"""
import os

# SPECPATH is provided by PyInstaller and points to the directory of this spec.
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))
TOOL1_ROOT   = os.path.join(PROJECT_ROOT, "tool-1-cv-maker")
BACKEND_DIR  = os.path.join(TOOL1_ROOT, "src", "backend")
FRONTEND_DIR = os.path.join(TOOL1_ROOT, "src", "frontend")
SHARED_DIR   = os.path.join(PROJECT_ROOT, "shared")
ICON_PATH    = os.path.join(PROJECT_ROOT, "packaging", "icon.ico")

block_cipher = None

a = Analysis(
    [os.path.join(BACKEND_DIR, "app.py")],
    pathex=[BACKEND_DIR, PROJECT_ROOT],
    binaries=[],
    datas=[
        # Bundle the entire frontend so static files can be served
        (FRONTEND_DIR, os.path.join("src", "frontend")),
        # Bundle backend resources (schema.sql, JSON dictionaries, etc.)
        (BACKEND_DIR, os.path.join("src", "backend")),
        # Bundle shared schema package
        (SHARED_DIR, "shared"),
        # Bundle the Austrian job knowledge base (berufe.json). knowledge.py looks
        # for it at <bundle-root>/data/knowledge, which is where this lands — so the
        # frozen .exe finds it (without this, AI prompts lose job context).
        (os.path.join(TOOL1_ROOT, "data", "knowledge"), os.path.join("data", "knowledge")),
    ],
    hiddenimports=[
        # FastAPI / Starlette / Pydantic core
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
        # uvicorn + its lifecycle/loop hooks
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
        # Multipart form / static file extras
        "python_multipart",
        # Export deps
        "reportlab",
        "reportlab.pdfgen",
        "reportlab.lib",
        "reportlab.platypus",
        "docx",
        "docx.shared",
        # Language detection
        "lingua",
        # Local LLM (optional — silently no-op'd if not present)
        "llama_cpp",
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
        # Heavyweight transitive deps pulled in by llama-cpp-python but not used
        # by Tool 1. Excluding these brings the .exe from ~375 MB down to ~150 MB.
        "torch",
        "torchvision",
        "torchaudio",
        "numpy.testing",
        "pandas",
        "scipy",
        "pyarrow",
        "cv2",
        "av",
        "sklearn",
        "matplotlib.tests",
        "IPython",
        "jupyter",
        "notebook",
        "tornado",
        "zmq",
        "tensorflow",
        "transformers",
        "sentencepiece",
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
    name="AMS-JobAssist-Tool1",
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
