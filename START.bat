@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title AMS JobAssist
cd /d "%~dp0"

:: ============================================================================
::  AMS JobAssist — START HERE
::
::  This is the ONE file you run. It figures out the best way to launch:
::    1. If .exe files exist in dist\  → runs them directly (no Python needed)
::    2. If Python is installed         → installs deps and runs from source
::    3. Otherwise                      → tells you what to do
:: ============================================================================

cls
echo.
echo  ================================================================
echo     AMS JobAssist  --  Lebenslauf-Assistent fuer AMS-Kurse
echo  ================================================================
echo.

:: -- Check for pre-built .exe files first (fastest path) ----------------------
if exist "dist\AMS-JobAssist-Launcher.exe" (
    echo     [OK] Fertige Programmdateien gefunden.
    echo.
    echo     Was moechten Sie tun?
    echo.
    echo       [1]  Starten
    echo            Programm direkt starten
    echo.
    echo       [2]  Installieren und Starten
    echo            Start-Menue-Eintrag erstellen, dann starten
    echo.
    echo       [3]  Deinstallieren
    echo            Programme und Verknuepfungen entfernen
    echo.
    echo       [4]  Beenden
    echo.
    choice /c 1234 /n /m "     Ihre Auswahl: "
    echo.
    if errorlevel 4 goto :END
    if errorlevel 3 goto :EXE_UNINSTALL
    if errorlevel 2 goto :EXE_INSTALL
    if errorlevel 1 goto :EXE_RUN
)

:: -- No .exe found — try Python path -----------------------------------------
echo     Keine fertigen .exe-Dateien gefunden.
echo     Pruefe ob Python vorhanden ist...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo     [!!] Python wurde nicht gefunden und keine .exe vorhanden.
    echo.
    echo     Sie haben zwei Moeglichkeiten:
    echo.
    echo       A) Laden Sie die fertigen .exe-Dateien herunter:
    echo          https://github.com/PapaKoftes/AMS-JobAssist/releases
    echo          und legen Sie sie in den Ordner "dist\" dieses Verzeichnisses.
    echo.
    echo       B) Installieren Sie Python von https://www.python.org/downloads/
    echo          ^(Wichtig: "Add Python to PATH" ankreuzen!^)
    echo          und starten Sie diese Datei erneut.
    echo.
    pause
    goto :END
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do (
    echo     [OK] %%v gefunden.
)
echo.

:: -- Python is available — offer source-based options -------------------------
echo     Was moechten Sie tun?
echo.
echo       [1]  Installieren und Starten
echo            Abhaengigkeiten installieren und Programm starten
echo.
echo       [2]  Nur Starten
echo            Programm starten ^(wenn bereits installiert^)
echo.
echo       [3]  .exe-Dateien bauen
echo            Eigenstaendige .exe-Dateien erstellen ^(dauert 5-10 Min^)
echo.
echo       [4]  Deinstallieren
echo            Programme vom Computer entfernen
echo.
echo       [5]  Daten loeschen
echo            Alle Lebenslaeufe dauerhaft loeschen
echo.
echo       [6]  Beenden
echo.
choice /c 123456 /n /m "     Ihre Auswahl: "
echo.
if errorlevel 6 goto :END
if errorlevel 5 goto :PY_DELETE_DATA
if errorlevel 4 goto :PY_UNINSTALL
if errorlevel 3 goto :PY_BUILD
if errorlevel 2 goto :PY_RUN
if errorlevel 1 goto :PY_INSTALL_AND_RUN


:: ============================================================================
:EXE_RUN
:: ============================================================================
echo     Starte AMS JobAssist...
echo     Der Browser oeffnet sich automatisch.
echo.
echo  ================================================================
echo     Schliessen Sie dieses Fenster um das Programm zu beenden.
echo  ================================================================
echo.
start "" "dist\AMS-JobAssist-Launcher.exe"
pause
goto :END


:: ============================================================================
:EXE_INSTALL
:: ============================================================================
echo     Starte Installer...
echo.
if exist "dist\install.bat" (
    call "dist\install.bat"
) else (
    echo     [!] install.bat nicht in dist\ gefunden.
    echo         Starte Programm direkt...
    echo.
    start "" "dist\AMS-JobAssist-Launcher.exe"
    pause
)
goto :END


:: ============================================================================
:EXE_UNINSTALL
:: ============================================================================
echo     Suche installiertes Programm...
echo.

:: Check if installed via install.bat
set "INSTALL_DIR=%LOCALAPPDATA%\AMS JobAssist"
if exist "!INSTALL_DIR!\uninstall.bat" (
    echo     Installiertes Programm gefunden in:
    echo       !INSTALL_DIR!
    echo.
    call "!INSTALL_DIR!\uninstall.bat"
    goto :END
)

echo     Kein installiertes Programm gefunden.
echo     Falls Sie die .exe-Dateien direkt gestartet haben,
echo     loeschen Sie einfach den dist\ Ordner.
echo.
pause
goto :END


:: ============================================================================
:PY_INSTALL_AND_RUN
:: ============================================================================
cls
echo.
echo  ================================================================
echo     Installieren und Starten
echo  ================================================================
echo.

:: Call the existing ams_jobassist.bat if available
if exist "ams_jobassist.bat" (
    call "ams_jobassist.bat"
    goto :END
)

:: Fallback: manual install
echo     Installiere Abhaengigkeiten...
echo.
python -m pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo     [!!] Installation fehlgeschlagen.
    pause
    goto :END
)
echo     [OK] Abhaengigkeiten installiert.
echo.

:: Download AI model if not present
if not exist "tool-1-cv-maker\data\models\qwen2.5-1.5b-instruct-q4_k_m.gguf" (
    echo     Lade KI-Modell herunter ^(~1,1 GB -- einmalig^)...
    echo     Bitte warten -- ca. 2-5 Minuten je nach Internetverbindung.
    echo.
    python -c "import sys,os; os.environ['AMS_ENFORCE_OFFLINE']='0'; sys.path.insert(0,'tool-1-cv-maker/src/backend'); from ai.local_llm import download_model; ok=download_model(); print('[OK] KI-Modell heruntergeladen.' if ok else '[!] Download fehlgeschlagen -- KI laeuft regelbasiert.')"
    echo.
)

echo     Starte AMS JobAssist...
echo.
python launcher.py
pause
goto :END


:: ============================================================================
:PY_RUN
:: ============================================================================
echo     Starte AMS JobAssist...
echo     Der Browser oeffnet sich automatisch.
echo.
echo  ================================================================
echo     Druecken Sie STRG+C um das Programm zu beenden.
echo  ================================================================
echo.
python launcher.py
echo.
echo     Programm wurde beendet.
pause
goto :END


:: ============================================================================
:PY_BUILD
:: ============================================================================
cls
echo.
echo  ================================================================
echo     .exe-Dateien bauen
echo  ================================================================
echo.
echo     Dies erstellt eigenstaendige .exe-Dateien, die ohne Python laufen.
echo     Der Vorgang dauert ca. 5-10 Minuten.
echo.
choice /c JN /n /m "     Fortfahren? [J] Ja  [N] Nein: "
echo.
if errorlevel 2 goto :END
echo.
call "build_all.bat"
goto :END


:: ============================================================================
:PY_UNINSTALL
:: ============================================================================
cls
echo.
echo  ================================================================
echo     Deinstallieren
echo  ================================================================
echo.

pip show ams-cv-maker >nul 2>&1
set "T1=!errorlevel!"
pip show ams-trainer >nul 2>&1
set "T2=!errorlevel!"

if !T1! neq 0 if !T2! neq 0 (
    echo     Nichts installiert -- nichts zu entfernen.
    echo.
    pause
    goto :END
)

echo     Folgendes wird entfernt:
if !T1! == 0 echo       - CV-Ersteller ^(Tool 1^)
if !T2! == 0 echo       - Trainer-Dashboard ^(Tool 2^)
echo.
choice /c JN /n /m "     Fortfahren? [J] Ja  [N] Nein: "
if errorlevel 2 goto :END

echo.
if !T1! == 0 (
    pip uninstall ams-cv-maker -y -q
    echo     [OK] CV-Ersteller entfernt.
)
if !T2! == 0 (
    pip uninstall ams-trainer -y -q
    echo     [OK] Trainer-Dashboard entfernt.
)

python -c "import lingua" >nul 2>&1
if not errorlevel 1 (
    pip uninstall lingua-language-detector -y -q
    echo     [OK] Spracherkennungs-Modul entfernt.
)

echo.
echo     Deinstallation abgeschlossen.
echo     Ihre Daten sind noch vorhanden ^(Option 5 zum Loeschen^).
echo.
pause
goto :END


:: ============================================================================
:PY_DELETE_DATA
:: ============================================================================
cls
echo.
echo  ================================================================
echo     Daten loeschen
echo  ================================================================
echo.

set "FOUND=0"
if exist "tool-1-cv-maker\data" set "FOUND=1"
if exist "tool-2-trainer-dashboard\data" set "FOUND=1"

if !FOUND! == 0 (
    echo     Keine Daten gefunden.
    pause
    goto :END
)

echo     WARNUNG: Alle Lebenslaeufe werden DAUERHAFT geloescht!
echo.
choice /c JN /n /m "     Sind Sie sicher? [J] Ja  [N] Nein: "
if errorlevel 2 goto :END

echo.
choice /c JN /n /m "     Letzte Bestaetigung -- wirklich loeschen? [J] Ja  [N] Nein: "
if errorlevel 2 goto :END

echo.
if exist "tool-1-cv-maker\data" (
    rmdir /s /q "tool-1-cv-maker\data"
    echo     [OK] Teilnehmer-Daten geloescht.
)
if exist "tool-1-cv-maker\logs" (
    rmdir /s /q "tool-1-cv-maker\logs"
    echo     [OK] Tool-1-Protokolle geloescht.
)
if exist "tool-2-trainer-dashboard\data" (
    rmdir /s /q "tool-2-trainer-dashboard\data"
    echo     [OK] Trainer-Daten geloescht.
)
if exist "tool-2-trainer-dashboard\logs" (
    rmdir /s /q "tool-2-trainer-dashboard\logs"
    echo     [OK] Tool-2-Protokolle geloescht.
)
echo.
echo     Alle Daten wurden geloescht.
pause
goto :END


:: ============================================================================
:END
:: ============================================================================
endlocal
exit /b 0
