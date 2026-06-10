@echo off
REM ============================================================================
REM  Download the shipped default AI model (Qwen2.5-3B-Instruct Q4_K_M, ~1.9 GB)
REM  into tool-1-cv-maker\data\models\ so build_all.bat can pre-seed it.
REM
REM  Run this ONCE on a build machine before build_all.bat. It uses the app's own
REM  downloader, which verifies the pinned SHA-256 after download. Requires network
REM  for THIS step only (the resulting product is fully offline).
REM ============================================================================
setlocal
set "TOOL1=%~dp0tool-1-cv-maker"
set "MODELS=%TOOL1%\data\models"
set "TARGET=%MODELS%\qwen2.5-3b-instruct-q4_k_m.gguf"

if exist "%TARGET%" (
    echo [OK] 3B model already present: %TARGET%
    goto :eof
)

if not exist "%MODELS%" mkdir "%MODELS%"

echo Downloading Qwen2.5-3B-Instruct Q4_K_M (~1.9 GB)...
echo This needs internet for this step only; the built product stays offline.
echo.

REM AMS_ENFORCE_OFFLINE=0 lets the downloader reach HuggingFace for this one step.
set "AMS_ENFORCE_OFFLINE=0"
python -c "import sys; sys.path.insert(0, r'%TOOL1%\src\backend'); from ai.local_llm import download_model; ok=download_model(tier='full'); sys.exit(0 if ok else 1)"

if errorlevel 1 (
    echo.
    echo [!!] Download failed. Check your connection and retry, or copy a
    echo      qwen2.5-3b-instruct-q4_k_m.gguf into %MODELS% manually.
    exit /b 1
)
echo.
echo [OK] 3B model ready at %TARGET%
endlocal
