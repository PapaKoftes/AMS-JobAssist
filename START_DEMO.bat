@echo off
REM ====================================================================
REM  AMS-JobAssist - Friday Demo launcher
REM  Double-click this. It starts both tools, pre-warms the AI model,
REM  and opens the browser only when everything is READY.
REM  See DEMO_FRIDAY.md for the walkthrough script.
REM ====================================================================
cd /d "%~dp0"

REM Prefer the py launcher, fall back to python on PATH.
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py start_demo.py %*
) else (
    python start_demo.py %*
)

echo.
echo Demo stopped. You can close this window.
pause
