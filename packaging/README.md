# Packaging

PyInstaller spec files for building standalone Windows executables of
AMS JobAssist (Tool 1, Tool 2, and the combined launcher).

## Files

| File | Output | Purpose |
|------|--------|---------|
| `build_tool1.spec` | `AMS-JobAssist-Tool1.exe`     | Standalone Tool 1 (participant CV maker) |
| `build_tool2.spec` | `AMS-JobAssist-Tool2.exe`     | Standalone Tool 2 (trainer dashboard) |
| `launcher.spec`    | `AMS-JobAssist-Launcher.exe`  | Single-entry launcher that starts both tools and opens the browser |
| `icon.ico`         | Application icon              | Embedded in all three .exe files |

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

The Qwen2.5-1.5B GGUF model (~1.1 GB) is **not** bundled in the .exe — it is
downloaded on demand via the in-app `/api/ai/download-model` endpoint, or can
be placed manually at `<data-dir>/models/qwen2.5-1.5b-instruct-q4_k_m.gguf`.
For air-gapped centers, ship the model file alongside the .exe.

## Testing the build

After building:

```bat
dist\AMS-JobAssist-Launcher.exe
```

Expected: console shows "Tool 1 ready" + "Tool 2 ready" + opens default browser
to `http://localhost:8000`. Test on a clean Windows 10 VM with no Python
installed to verify the bundle is truly self-contained.

## Code signing

Not yet configured. If you have a Windows code-signing certificate, add the
`signtool` step to `build_all.bat` after the PyInstaller runs:

```bat
signtool sign /f cert.pfx /p PASSWORD /tr http://timestamp.digicert.com /td sha256 dist\*.exe
```
