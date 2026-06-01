@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title AMS JobAssist — Installation
cd /d "%~dp0"

cls
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║         AMS JobAssist — Einmalige Installation           ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  Dieses Programm richtet AMS JobAssist ein.
echo  Dauer: ca. 3-10 Minuten (je nach Internetverbindung)
echo.
echo  Was installiert wird:
echo    1. Python (Programmierumgebung, falls nicht vorhanden)
echo    2. AMS CV-Ersteller (Tool 1 — fuer Teilnehmer)
echo    3. AMS Trainer-Dashboard (Tool 2 — fuer Kursleiter)
echo    4. Desktop-Verkuepfungen fuer beide Programme
echo.
pause

:: ============================================================================
:: SCHRITT 1 — Python pruefen und ggf. installieren
:: ============================================================================
echo.
echo  [Schritt 1/4]  Pruefe Python...
echo.

python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do (
        echo  [OK] %%v ist bereits installiert.
    )
    goto :STEP2
)

echo  Python wurde nicht gefunden.
echo  Installiere Python automatisch via winget...
echo.

:: Try winget first (Windows 10/11 built-in)
winget --version >nul 2>&1
if not errorlevel 1 (
    echo  Lade Python herunter und installiere es...
    echo  ^(Dies kann 2-5 Minuten dauern^)
    echo.
    winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    if not errorlevel 1 (
        echo.
        echo  [OK] Python wurde installiert.
        :: Refresh PATH for current session
        set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
        set "PATH=%PATH%;%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts"
        :: Also try user-level Python location
        for /d %%p in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
            set "PATH=!PATH!;%%p;%%p\Scripts"
        )
        goto :STEP2
    )
)

:: Fallback: download Python installer directly
echo  Lade Python-Installer herunter...
echo.
set "PY_URL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
set "PY_INSTALLER=%TEMP%\python-installer.exe"

:: Use PowerShell to download
PowerShell -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%' -UseBasicParsing" >nul 2>&1
if exist "%PY_INSTALLER%" (
    echo  Python-Installer heruntergeladen. Starte Installation...
    echo  ^(Bitte folgen Sie dem Installationsassistenten^)
    echo  WICHTIG: Aktivieren Sie "Add Python to PATH"!
    echo.
    "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del "%PY_INSTALLER%" >nul 2>&1
    :: Reload PATH
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
    for /d %%p in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        set "PATH=!PATH!;%%p;%%p\Scripts"
    )
) else (
    echo  [!!] Download fehlgeschlagen. Bitte installieren Sie Python manuell:
    echo       https://www.python.org/downloads/
    echo       ^(Wichtig: "Add Python to PATH" auswaehlen!^)
    echo.
    start "" "https://www.python.org/downloads/"
    pause
    goto :END
)

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [!!] Python konnte nicht gestartet werden.
    echo       Bitte starten Sie den Computer neu und fuehren Sie
    echo       diese Datei danach erneut aus.
    echo.
    pause
    goto :END
)

:STEP2
:: ============================================================================
:: SCHRITT 2 — Tool 1 (CV-Ersteller) installieren
:: ============================================================================
echo.
echo  [Schritt 2/4]  Installiere CV-Ersteller (Tool 1)...
echo.

python -m pip install -e "%~dp0tool-1-cv-maker" -q --disable-pip-version-check 2>&1
if errorlevel 1 (
    echo.
    echo  [!!] Installation von Tool 1 fehlgeschlagen.
    echo       Pruefe ob Sie Internetverbindung haben.
    pause
    goto :END
)
echo  [OK] CV-Ersteller installiert.

:: ============================================================================
:: SCHRITT 3 — Tool 2 (Trainer-Dashboard) installieren
:: ============================================================================
echo.
echo  [Schritt 3/4]  Installiere Trainer-Dashboard (Tool 2)...
echo.

python -m pip install -e "%~dp0shared" -q --disable-pip-version-check 2>&1
python -m pip install -e "%~dp0tool-2-trainer-dashboard" -q --disable-pip-version-check 2>&1
if errorlevel 1 (
    echo.
    echo  [!!] Installation von Tool 2 fehlgeschlagen.
    pause
    goto :END
)
echo  [OK] Trainer-Dashboard installiert.

:: ============================================================================
:: SCHRITT 4 — Desktop-Verkuepfungen erstellen
:: ============================================================================
echo.
echo  [Schritt 4/4]  Erstelle Desktop-Verkuepfungen...
echo.

set "DESKTOP=%USERPROFILE%\Desktop"
set "REPO=%~dp0"
:: Remove trailing backslash
if "!REPO:~-1!"=="\" set "REPO=!REPO:~0,-1!"

:: Find python executable
set "PYTHON_EXE=python"
for /f "tokens=*" %%p in ('where python 2^>nul') do (
    set "PYTHON_EXE=%%p"
    goto :FOUND_PYTHON
)
:FOUND_PYTHON

:: Create VBS helper to make shortcuts (no admin needed)
set "VBS=%TEMP%\make_shortcut.vbs"

:: --- Shortcut 1: CV-Ersteller (Tool 1 only) ----------------------------------
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS%"
echo sLinkFile = "%DESKTOP%\AMS CV-Ersteller.lnk" >> "%VBS%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS%"
echo oLink.TargetPath = "!PYTHON_EXE!" >> "%VBS%"
echo oLink.Arguments = """!REPO!\launcher.py"" --tool1-only" >> "%VBS%"
echo oLink.WorkingDirectory = "!REPO!" >> "%VBS%"
echo oLink.Description = "AMS JobAssist — CV-Ersteller fuer Teilnehmer" >> "%VBS%"
if exist "%~dp0packaging\icon.ico" (
    echo oLink.IconLocation = "!REPO!\packaging\icon.ico" >> "%VBS%"
)
echo oLink.Save >> "%VBS%"
cscript //nologo "%VBS%" >nul 2>&1

:: --- Shortcut 2: Trainer-Dashboard (both tools, open Tool 2 URL) -------------
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS%"
echo sLinkFile = "%DESKTOP%\AMS Trainer-Dashboard.lnk" >> "%VBS%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS%"
echo oLink.TargetPath = "!PYTHON_EXE!" >> "%VBS%"
echo oLink.Arguments = """!REPO!\launcher.py"" --open-trainer" >> "%VBS%"
echo oLink.WorkingDirectory = "!REPO!" >> "%VBS%"
echo oLink.Description = "AMS JobAssist — Trainer-Dashboard" >> "%VBS%"
if exist "%~dp0packaging\icon.ico" (
    echo oLink.IconLocation = "!REPO!\packaging\icon.ico" >> "%VBS%"
)
echo oLink.Save >> "%VBS%"
cscript //nologo "%VBS%" >nul 2>&1

:: --- Shortcut 3: Beide Tools starten ----------------------------------------
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS%"
echo sLinkFile = "%DESKTOP%\AMS JobAssist (beide).lnk" >> "%VBS%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS%"
echo oLink.TargetPath = "!PYTHON_EXE!" >> "%VBS%"
echo oLink.Arguments = """!REPO!\launcher.py""" >> "%VBS%"
echo oLink.WorkingDirectory = "!REPO!" >> "%VBS%"
echo oLink.Description = "AMS JobAssist — CV-Ersteller und Trainer-Dashboard" >> "%VBS%"
if exist "%~dp0packaging\icon.ico" (
    echo oLink.IconLocation = "!REPO!\packaging\icon.ico" >> "%VBS%"
)
echo oLink.Save >> "%VBS%"
cscript //nologo "%VBS%" >nul 2>&1

del "%VBS%" >nul 2>&1

if exist "%DESKTOP%\AMS CV-Ersteller.lnk" (
    echo  [OK] Desktop-Verkuepfungen erstellt:
    echo         - "AMS CV-Ersteller"        ^(fuer Teilnehmer^)
    echo         - "AMS Trainer-Dashboard"   ^(fuer Kursleiter^)
    echo         - "AMS JobAssist (beide)"   ^(startet alles^)
) else (
    echo  [!] Desktop-Verkuepfungen konnten nicht erstellt werden.
    echo      Starten Sie das Programm manuell mit:
    echo      python launcher.py
)

:: ============================================================================
:: FERTIG
:: ============================================================================
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║              Installation abgeschlossen!                 ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  AMS JobAssist ist jetzt eingerichtet.
echo.
echo  Starten Sie das Programm mit einem der Desktop-Symbole:
echo    - "AMS CV-Ersteller"       fuer Teilnehmer
echo    - "AMS Trainer-Dashboard"  fuer Kursleiter
echo.
echo  Oder starten Sie es jetzt direkt:
echo.
choice /c JN /n /m "  Jetzt starten? [J] Ja  [N] Nein: "
if errorlevel 2 goto :END

echo.
python "%~dp0launcher.py"

:END
endlocal
exit /b 0
