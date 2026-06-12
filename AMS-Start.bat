@echo off
chcp 65001 >nul 2>&1
title AMS JobAssist
cd /d "%~dp0"
cls
echo.
echo  ================================================================
echo     AMS JobAssist  -  Lebenslauf-Assistent
echo  ================================================================
echo.
echo     Einen Moment bitte - die App wird vorbereitet...
echo.

REM ---------------------------------------------------------------------------
REM  1) Ist Python vorhanden?
REM ---------------------------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python wurde nicht gefunden.
    echo.
    echo      Bitte installieren Sie Python 3.10 oder neuer von:
    echo          https://www.python.org/downloads/
    echo.
    echo      WICHTIG: Im Setup das Haekchen "Add Python to PATH" setzen.
    echo      Danach diese Datei erneut doppelklicken.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  [OK] %%v gefunden.

REM ---------------------------------------------------------------------------
REM  2) Sind die Komponenten installiert?  (einmalige Einrichtung)
REM ---------------------------------------------------------------------------
python -c "import fastapi, uvicorn, reportlab, docx, sqlalchemy, lingua" >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [i] Erstmalige Einrichtung - benoetigte Komponenten werden installiert.
    echo      Beim ersten Mal dauert das einige Minuten. Bitte warten...
    echo.
    python -m pip install --disable-pip-version-check -q -r requirements.txt
    if errorlevel 1 (
        echo.
        echo  [X] Die Installation ist fehlgeschlagen.
        echo      Bitte Internetverbindung pruefen und Datei erneut starten.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Komponenten installiert.
) else (
    echo  [OK] Komponenten bereits installiert.
)

REM ---------------------------------------------------------------------------
REM  3) Ist das KI-Modell vorhanden?  (nur Hinweis - App laeuft auch ohne)
REM ---------------------------------------------------------------------------
if exist "tool-1-cv-maker\data\models\qwen2.5-3b-instruct-q4_k_m.gguf" (
    echo  [OK] KI-Modell vorhanden ^(vollstaendig offline, kein Download noetig^).
) else (
    echo  [!] KI-Modell nicht gefunden - die App nutzt den regelbasierten Modus.
)

REM ---------------------------------------------------------------------------
REM  4) Starten.  launcher.py waehlt freie Ports, waermt das Modell vor und
REM     oeffnet den Browser automatisch.  Dieses Fenster offen lassen.
REM ---------------------------------------------------------------------------
echo.
echo  ----------------------------------------------------------------
echo     Start... der Browser oeffnet sich gleich automatisch.
echo     Zum BEENDEN einfach dieses Fenster schliessen.
echo  ----------------------------------------------------------------
echo.
python launcher.py

echo.
echo  AMS JobAssist wurde beendet.
pause
