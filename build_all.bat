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
echo.
echo To run:  dist\AMS-JobAssist-Launcher.exe
echo.

popd
endlocal
pause
