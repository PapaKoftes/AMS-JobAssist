@echo off
REM ============================================================================
REM  AMS JobAssist — Build script
REM
REM  Produces three standalone Windows .exe files in ./dist/:
REM    - AMS-JobAssist-Tool1.exe        (participant CV maker)
REM    - AMS-JobAssist-Tool2.exe        (trainer dashboard)
REM    - AMS-JobAssist-Launcher.exe     (one-click start for both tools)
REM
REM  Run from anywhere — the script anchors itself to its own directory.
REM
REM  Prerequisites (the script will install PyInstaller if missing):
REM    - Python 3.10+
REM    - All runtime deps installed:
REM        pip install -e tool-1-cv-maker[ai] -e tool-2-trainer-dashboard -e shared
REM ============================================================================

setlocal enableextensions

REM Pin the working directory to the script's location (repo root)
pushd "%~dp0"

echo.
echo ========================================
echo  AMS JobAssist - Build Script
echo ========================================
echo.

REM ---- Sanity check: Python ---------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ and re-run.
    popd & pause & exit /b 1
)

REM ---- Sanity check: PyInstaller ----------------------------------------------
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install --upgrade pyinstaller
    if errorlevel 1 (
        echo [ERROR] Could not install PyInstaller.
        popd & pause & exit /b 1
    )
)

REM ---- Wipe previous build artifacts so stale files can't shadow results -----
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"

REM ---- Build Tool 1 -----------------------------------------------------------
echo.
echo [1/3] Building Tool 1 (CV Maker)...
echo.
python -m PyInstaller packaging\build_tool1.spec --distpath dist --workpath build --noconfirm --clean
if errorlevel 1 (
    echo [ERROR] Tool 1 build failed.
    popd & pause & exit /b 1
)
echo [OK] Tool 1 build complete.

REM ---- Build Tool 2 -----------------------------------------------------------
echo.
echo [2/3] Building Tool 2 (Trainer Dashboard)...
echo.
python -m PyInstaller packaging\build_tool2.spec --distpath dist --workpath build --noconfirm --clean
if errorlevel 1 (
    echo [ERROR] Tool 2 build failed.
    popd & pause & exit /b 1
)
echo [OK] Tool 2 build complete.

REM ---- Build Launcher ---------------------------------------------------------
echo.
echo [3/3] Building Launcher...
echo.
python -m PyInstaller packaging\launcher.spec --distpath dist --workpath build --noconfirm --clean
if errorlevel 1 (
    echo [ERROR] Launcher build failed.
    popd & pause & exit /b 1
)
echo [OK] Launcher build complete.

REM ---- Copy batch installer to dist\ for easy distribution --------------------
echo.
echo [4/4] Copying installer files to dist\...
copy /Y "packaging\install.bat" "dist\install.bat" >nul
copy /Y "packaging\uninstall_template.bat" "dist\uninstall_template.bat" >nul
copy /Y "packaging\icon.ico" "dist\icon.ico" >nul 2>&1
echo [OK] Installer files copied to dist\.

REM ---- Pre-seed the AI model so the app is FULLY OFFLINE (no runtime download) -
REM The frozen exe looks for the GGUF in <exe-dir>\data\models (see local_llm.py
REM _MODEL_DIR frozen branch). Ship ONLY the 3B (the shipped default, "full" tier);
REM the 1.5B is redundant once 3B is present (3B auto-wins, similar speed) and would
REM just add ~1.1 GB of dead weight.
set "MODEL_3B=qwen2.5-3b-instruct-q4_k_m.gguf"
echo.
echo [4b/4] Pre-seeding 3B AI model into dist\data\models\ ...
if exist "tool-1-cv-maker\data\models\%MODEL_3B%" (
    if not exist "dist\data\models" mkdir "dist\data\models"
    copy /Y "tool-1-cv-maker\data\models\%MODEL_3B%" "dist\data\models\" >nul
    echo [OK] 3B model pre-seeded — the build is fully offline with good-quality AI.
) else (
    echo [!!] %MODEL_3B% not found in tool-1-cv-maker\data\models\ — the build will
    echo      have NO bundled model and would try to download at first run. Run
    echo      download_3b_model.bat first, or accept rules-only mode.
)

REM ---- Optionally build Inno Setup installer ---------------------------------
where iscc >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [BONUS] Inno Setup found — building Setup.exe...
    iscc packaging\installer.iss
    if not errorlevel 1 (
        echo [OK] AMS-JobAssist-Setup.exe built in packaging\output\.
    ) else (
        echo [!!] Inno Setup build failed — the .exe files are still usable without it.
    )
) else (
    echo.
    echo [INFO] Inno Setup not found — skipping Setup.exe build.
    echo        Install Inno Setup from https://jrsoftware.org/isinfo.php
    echo        to build a proper Windows installer.
)

REM ---- Done ------------------------------------------------------------------
echo.
echo ========================================
echo  BUILD COMPLETE
echo ========================================
echo.
echo Output (in dist\):
echo   - AMS-JobAssist-Tool1.exe       participant interface
echo   - AMS-JobAssist-Tool2.exe       trainer interface
echo   - AMS-JobAssist-Launcher.exe    starts both, opens browser
echo   - install.bat                   batch installer (no Inno Setup needed)
echo.
echo Install options:
echo   1. Quick:    dist\AMS-JobAssist-Launcher.exe   (run directly, no install)
echo   2. Batch:    dist\install.bat                   (Start Menu + Add/Remove Programs)
echo   3. Pro:      packaging\output\AMS-JobAssist-Setup.exe   (if Inno Setup was available)
echo.
echo To run without installing:  dist\AMS-JobAssist-Launcher.exe
echo.

popd
endlocal
pause
