@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title AMS JobAssist - Installation
cd /d "%~dp0"

:: ============================================================================
::  AMS JobAssist - Batch Installer (no Inno Setup needed)
::
::  What it does:
::    1. Copies the 3 .exe files to a target folder
::    2. Creates Start Menu shortcuts
::    3. Creates a Desktop shortcut (optional)
::    4. Creates an uninstaller (uninstall.bat) in the target folder
::    5. Registers in Add/Remove Programs (registry)
::
::  Run from the dist\ folder or the repo root (auto-detects .exe location).
:: ============================================================================

:: -- Locate the .exe files ----------------------------------------------------
set "EXE_DIR="
if exist "AMS-JobAssist-Launcher.exe" (
    set "EXE_DIR=%~dp0"
) else if exist "dist\AMS-JobAssist-Launcher.exe" (
    set "EXE_DIR=%~dp0dist\"
) else if exist "..\dist\AMS-JobAssist-Launcher.exe" (
    set "EXE_DIR=%~dp0..\dist\"
)

if "!EXE_DIR!"=="" (
    echo.
    echo  [!!] Konnte die .exe-Dateien nicht finden.
    echo       Bitte fuehren Sie zuerst build_all.bat aus.
    echo.
    pause
    exit /b 1
)

:: -- Default install location -------------------------------------------------
set "INSTALL_DIR=%LOCALAPPDATA%\AMS JobAssist"
set "DATA_DIR=%APPDATA%\AMS-JobAssist"
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\AMS JobAssist"

cls
echo.
echo  ================================================================
echo     AMS JobAssist - Installation
echo  ================================================================
echo.
echo     Die folgenden Dateien werden installiert:
echo.
echo       AMS-JobAssist-Launcher.exe    (Starter)
echo       AMS-JobAssist-Tool1.exe       (CV-Ersteller)
echo       AMS-JobAssist-Tool2.exe       (Trainer-Dashboard)
echo.
echo     Installationsort:
echo       !INSTALL_DIR!
echo.
echo     Datenverzeichnis:
echo       !DATA_DIR!
echo.
echo  ----------------------------------------------------------------
echo.
echo     Moechten Sie fortfahren?
echo.
choice /c JN /n /m "     [J] Ja, installieren   [N] Nein, abbrechen: "
echo.
if errorlevel 2 (
    echo     Installation abgebrochen.
    pause
    exit /b 0
)

:: -- Create directories -------------------------------------------------------
echo     Erstelle Verzeichnisse...
mkdir "!INSTALL_DIR!" >nul 2>&1
mkdir "!DATA_DIR!" >nul 2>&1
mkdir "!DATA_DIR!\data" >nul 2>&1
mkdir "!DATA_DIR!\models" >nul 2>&1
mkdir "!DATA_DIR!\exports" >nul 2>&1
mkdir "!DATA_DIR!\backups" >nul 2>&1
mkdir "!STARTMENU!" >nul 2>&1
echo     [OK] Verzeichnisse erstellt.
echo.

:: -- Copy executables ---------------------------------------------------------
echo     Kopiere Programmdateien...
copy /Y "!EXE_DIR!AMS-JobAssist-Launcher.exe" "!INSTALL_DIR!\" >nul
if errorlevel 1 (
    echo     [!!] Fehler beim Kopieren von Launcher.exe
    pause
    exit /b 1
)
copy /Y "!EXE_DIR!AMS-JobAssist-Tool1.exe" "!INSTALL_DIR!\" >nul
if errorlevel 1 (
    echo     [!!] Fehler beim Kopieren von Tool1.exe
    pause
    exit /b 1
)
copy /Y "!EXE_DIR!AMS-JobAssist-Tool2.exe" "!INSTALL_DIR!\" >nul
if errorlevel 1 (
    echo     [!!] Fehler beim Kopieren von Tool2.exe
    pause
    exit /b 1
)

:: Copy icon if available
if exist "!EXE_DIR!..\packaging\icon.ico" (
    copy /Y "!EXE_DIR!..\packaging\icon.ico" "!INSTALL_DIR!\" >nul
) else if exist "icon.ico" (
    copy /Y "icon.ico" "!INSTALL_DIR!\" >nul
)

echo     [OK] Programmdateien kopiert.
echo.

:: -- Create Start Menu shortcuts (via PowerShell) -----------------------------
echo     Erstelle Startmenue-Verknuepfungen...

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$sc = $ws.CreateShortcut('%STARTMENU%\AMS JobAssist.lnk'); " ^
  "$sc.TargetPath = '%INSTALL_DIR%\AMS-JobAssist-Launcher.exe'; " ^
  "$sc.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$sc.Description = 'AMS JobAssist - Lebenslauf-Assistent'; " ^
  "if (Test-Path '%INSTALL_DIR%\icon.ico') { $sc.IconLocation = '%INSTALL_DIR%\icon.ico' }; " ^
  "$sc.Save()"

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$sc = $ws.CreateShortcut('%STARTMENU%\AMS JobAssist deinstallieren.lnk'); " ^
  "$sc.TargetPath = '%INSTALL_DIR%\uninstall.bat'; " ^
  "$sc.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$sc.Description = 'AMS JobAssist entfernen'; " ^
  "$sc.Save()"

echo     [OK] Startmenue-Eintraege erstellt.
echo.

:: -- Desktop shortcut (optional) ----------------------------------------------
echo     Moechten Sie eine Desktop-Verknuepfung erstellen?
echo.
choice /c JN /n /m "     [J] Ja   [N] Nein: "
echo.
if not errorlevel 2 (
    powershell -NoProfile -Command ^
      "$ws = New-Object -ComObject WScript.Shell; " ^
      "$sc = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\AMS JobAssist.lnk'); " ^
      "$sc.TargetPath = '%INSTALL_DIR%\AMS-JobAssist-Launcher.exe'; " ^
      "$sc.WorkingDirectory = '%INSTALL_DIR%'; " ^
      "$sc.Description = 'AMS JobAssist - Lebenslauf-Assistent'; " ^
      "if (Test-Path '%INSTALL_DIR%\icon.ico') { $sc.IconLocation = '%INSTALL_DIR%\icon.ico' }; " ^
      "$sc.Save()"
    echo     [OK] Desktop-Verknuepfung erstellt.
    echo.
)

:: -- Copy uninstaller ----------------------------------------------------------
echo     Kopiere Deinstallationsprogramm...

:: Look for uninstall_template.bat in common locations
set "TEMPLATE="
if exist "%~dp0uninstall_template.bat" set "TEMPLATE=%~dp0uninstall_template.bat"
if "!TEMPLATE!"=="" if exist "%~dp0..\packaging\uninstall_template.bat" set "TEMPLATE=%~dp0..\packaging\uninstall_template.bat"
if "!TEMPLATE!"=="" if exist "packaging\uninstall_template.bat" set "TEMPLATE=packaging\uninstall_template.bat"

if "!TEMPLATE!"=="" (
    echo     [!] uninstall_template.bat nicht gefunden — Deinstallation nur manuell.
) else (
    copy /Y "!TEMPLATE!" "!INSTALL_DIR!\uninstall.bat" >nul
    echo     [OK] Deinstallationsprogramm erstellt.
)
echo.

:: -- Register in Add/Remove Programs (HKCU — no admin needed) -----------------
echo     Registriere in "Programme und Features"...

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "DisplayName"     /t REG_SZ /d "AMS JobAssist" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "DisplayVersion"  /t REG_SZ /d "1.0" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "Publisher"       /t REG_SZ /d "Mina Mikail" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "InstallLocation" /t REG_SZ /d "!INSTALL_DIR!" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "UninstallString" /t REG_SZ /d "\"!INSTALL_DIR!\uninstall.bat\"" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "DisplayIcon"     /t REG_SZ /d "!INSTALL_DIR!\icon.ico" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "NoModify"        /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "NoRepair"        /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMS JobAssist" ^
    /v "URLInfoAbout"    /t REG_SZ /d "https://github.com/PapaKoftes/AMS-JobAssist" /f >nul 2>&1

echo     [OK] In "Programme und Features" registriert.
echo.

:: -- Done ---------------------------------------------------------------------
echo  ================================================================
echo     Installation abgeschlossen!
echo  ================================================================
echo.
echo     Starten:
echo       - Startmenue: "AMS JobAssist"
echo       - Oder direkt: "!INSTALL_DIR!\AMS-JobAssist-Launcher.exe"
echo.
echo     Deinstallieren:
echo       - Startmenue: "AMS JobAssist deinstallieren"
echo       - Oder: Systemsteuerung ^> Programme und Features
echo       - Oder: "!INSTALL_DIR!\uninstall.bat"
echo.
echo     Moechten Sie AMS JobAssist jetzt starten?
echo.
choice /c JN /n /m "     [J] Ja   [N] Nein: "
if not errorlevel 2 (
    start "" "!INSTALL_DIR!\AMS-JobAssist-Launcher.exe"
)

echo.
endlocal
exit /b 0
