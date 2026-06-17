# Packaging

PyInstaller spec files, installer scripts, and Inno Setup configuration for
building and distributing AMS JobAssist on Windows.

## Files

| File | Output | Purpose |
|------|--------|---------|
| `build_tool1.spec` | `AMS-JobAssist-Tool1.exe` | Standalone Tool 1 (participant CV maker) |
| `build_tool2.spec` | `AMS-JobAssist-Tool2.exe` | Standalone Tool 2 (trainer dashboard) |
| `launcher.spec` | `AMS-JobAssist-Launcher.exe` | Single-entry launcher that starts both tools and opens the browser |
| `installer.iss` | `AMS-JobAssist-Setup.exe` | Inno Setup script — proper Windows installer with Add/Remove Programs |
| `install.bat` | *(runs in place)* | Batch-based installer — no Inno Setup needed |
| `icon.ico` | Application icon | Embedded in all .exe files and installer |

All three specs are **relocatable** — they derive the project root from
`SPECPATH`, so the build works no matter what the current working directory is.

## Build

From the repo root:

```bat
build_all.bat
```

The batch script:
1. Verifies Python and PyInstaller are available (installs PyInstaller if missing).
2. Wipes `build/` and `dist/` to avoid stale artifacts.
3. Runs PyInstaller against all three specs with `--noconfirm --clean`.
4. Emits the .exe files to `dist/`.

Output:

```
dist/
├── AMS-JobAssist-Tool1.exe
├── AMS-JobAssist-Tool2.exe
└── AMS-JobAssist-Launcher.exe
```

## Hidden imports

The specs explicitly list hidden imports that PyInstaller's static analysis
can miss:

- `uvicorn.{logging,loops.auto,protocols.http.auto,protocols.websockets.auto,lifespan.on}`
- `pydantic_core`, `pydantic_settings`
- `starlette.{middleware.base,responses,staticfiles}`
- `reportlab.{pdfgen,lib,platypus}` and `docx.shared` (export deps)
- `llama_cpp` and `lingua` (Tool 1 only — optional AI deps; absent imports are tolerated at runtime)
- `sqlalchemy.{dialects.sqlite,engine,orm}` (Tool 2 only)

If a future code change introduces a new dynamically-imported module, add it
to the `hiddenimports` list in the relevant spec.

## Bundled data

- **Tool 1**: bundles the frontend (`src/frontend`), backend resources
  (schema.sql, JSON dictionaries), and the `shared/` schema package.
- **Tool 2**: bundles its frontend, backend, the `shared/` schema package,
  plus Tool 1's `export/` and `cv/` packages (needed for bulk PDF/DOCX
  export, which Tool 2 reaches into Tool 1 to perform).

## AI model

The Qwen2.5-3B-Instruct GGUF model (Q4_K_M, ~1.9 GB) is **shipped with the
installer and auto-installed into `data/models` beside the .exe** — it is *not*
embedded inside the .exe itself. `build_all.bat` pre-seeds `dist\data\models\`
from `tool-1-cv-maker\data\models\qwen2.5-3b-instruct-q4_k_m.gguf`, and
`installer.iss` bundles that file into `{app}\data\models`. The frozen app loads
it from there, so the local AI runs **fully offline out of the box — nothing is
downloaded at runtime**. If the model is missing, Tool 1 silently drops to the
rule-based fallback.

## Testing the build

After building:

```bat
dist\AMS-JobAssist-Launcher.exe
```

Expected: console shows "Tool 1 ready" + "Tool 2 ready" + opens default browser
to `http://localhost:8000`. Test on a clean Windows 10 VM with no Python
installed to verify the bundle is truly self-contained.

## Installation options

After building, three ways to deploy:

### Option 1 — Run directly (no install)

Double-click `dist\AMS-JobAssist-Launcher.exe`. No installation step,
no shortcuts, no registry entries. Good for quick demos.

### Option 2 — Batch installer (no extra tools needed)

```bat
dist\install.bat
```

This copies the .exe files to `%LOCALAPPDATA%\AMS JobAssist`, creates
Start Menu and optional Desktop shortcuts, registers in Add/Remove Programs,
and creates an `uninstall.bat` for clean removal.

No admin rights needed — installs to the current user's AppData.

### Option 3 — Inno Setup installer (professional)

Requires [Inno Setup 6+](https://jrsoftware.org/isinfo.php) to be installed.

```bat
iscc packaging\installer.iss
```

Produces `packaging\output\AMS-JobAssist-Setup.exe` — a proper Windows
installer with:
- Install wizard (German + English)
- Start Menu group
- Optional Desktop shortcut
- Add/Remove Programs registration
- Clean uninstall with optional data deletion prompt
- No admin rights required (user-level install by default)

If Inno Setup is available when running `build_all.bat`, the Setup.exe is
built automatically.

## Uninstalling

| Install method | Uninstall method |
|---|---|
| Direct run | Delete the .exe files |
| `install.bat` | Run `uninstall.bat` from install dir, or use Add/Remove Programs |
| `AMS-JobAssist-Setup.exe` | Use Add/Remove Programs, or run the uninstaller from Start Menu |
| `ams_jobassist.bat` (pip) | Option [3] in the menu |

All uninstall methods preserve user data by default. Data deletion is a
separate explicit step.

## Code signing

Not yet configured. If you have a Windows code-signing certificate, add the
`signtool` step to `build_all.bat` after the PyInstaller runs:

```bat
signtool sign /f cert.pfx /p PASSWORD /tr http://timestamp.digicert.com /td sha256 dist\*.exe
```
