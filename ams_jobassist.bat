@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title AMS JobAssist
cd /d "%~dp0"

:: ============================================================================
::  AMS JobAssist  --  Hauptmenue
::  Alle Aktionen von hier aus steuerbar.
:: ============================================================================


:MENU
cls

:: -- Installations-Status ermitteln ------------------------------------------
set "S1=[ ]"
set "S2=[ ]"
pip show ams-cv-maker >nul 2>&1
if not errorlevel 1 set "S1=[X]"
pip show ams-trainer >nul 2>&1
if not errorlevel 1 set "S2=[X]"

:: -- Daten-Status ermitteln --------------------------------------------------
set "DATEN=Keine Daten vorhanden"
if exist "tool-1-cv-maker\data\ams_jobassist.db"      set "DATEN=Teilnehmer-Daten vorhanden"
if exist "tool-2-trainer-dashboard\data\ams_trainer.db" set "DATEN=Teilnehmer- und Trainer-Daten vorhanden"

:: -- Bildschirm ausgeben -----------------------------------------------------
echo.
echo  ================================================================
echo     AMS JobAssist  --  Lebenslauf-Assistent fuer AMS-Kurse
echo  ================================================================
echo.
echo     Installations-Status:
echo       !S1!  CV-Ersteller         (Tool 1 - fuer Teilnehmer)
echo       !S2!  Trainer-Dashboard    (Tool 2 - fuer Kursleiter)
echo.
echo     Daten-Status:
echo       !DATEN!
echo.
echo  ----------------------------------------------------------------
echo.
echo     Was moechten Sie tun?
echo.
echo       [1]  Installieren und Starten
echo            Erstes Mal einrichten und direkt loslegen
echo.
echo       [2]  Starten
echo            Programm starten  (wenn bereits installiert)
echo.
echo       [3]  Deinstallieren
echo            Programme vom Computer entfernen
echo            Ihre Daten bleiben erhalten
echo.
echo       [4]  Daten loeschen
echo            Alle Lebenslaeufe und Protokolle dauerhaft loeschen
echo.
echo       [5]  Beenden
echo.
echo  ================================================================
echo.

echo     Druecken Sie eine Taste (1, 2, 3, 4 oder 5) -- kein Enter noetig.
echo.
choice /c 12345 /n /m "     Ihre Auswahl: "
if errorlevel 5 goto :END
if errorlevel 4 goto :DELETE_DATA
if errorlevel 3 goto :UNINSTALL
if errorlevel 2 goto :RUN_ONLY
if errorlevel 1 goto :INSTALL_AND_RUN
goto :MENU


:: ============================================================================
:INSTALL_AND_RUN
:: ============================================================================
cls
echo.
echo  ================================================================
echo     [1]  Installieren und Starten
echo  ================================================================
echo.

:: Schritt 1 -- Python pruefen ------------------------------------------------
echo     Schritt 1 von 5  --  Pruefe ob Python vorhanden ist...
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo     [!!] Python wurde nicht gefunden!
    echo.
    echo          Bitte laden Sie Python herunter und installieren Sie es:
    echo          https://www.python.org/downloads/
    echo.
    echo          Wichtig: Waehlen Sie "Add Python to PATH" aus!
    echo.
    pause
    goto :MENU
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do (
    echo     [OK] %%v ist vorhanden.
)
echo.

:: Schritt 2 -- Tool 1 installieren/aktualisieren ----------------------------
:: Always runs pip install (fast when already satisfied) to ensure all
:: dependencies are resolved, including lingua-language-detector.
echo     Schritt 2 von 5  --  Installiere CV-Ersteller (Tool 1) + Spracherkennung...
echo.
echo          Bitte warten -- pruefe Abhaengigkeiten...
python -m pip install -e "tool-1-cv-maker" -q --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo     [!!] Installation von Tool 1 fehlgeschlagen.
    echo          Pruefe die Fehlermeldung oben.
    pause
    goto :MENU
)
echo     [OK] CV-Ersteller + Spracherkennung installiert.
echo.

:: Schritt 3 -- Tool 2 installieren/aktualisieren ----------------------------
echo     Schritt 3 von 5  --  Installiere Trainer-Dashboard (Tool 2)...
echo.
echo          Bitte warten -- pruefe Abhaengigkeiten...
python -m pip install -e "tool-2-trainer-dashboard" -q --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo     [!!] Installation von Tool 2 fehlgeschlagen.
    echo          Pruefe die Fehlermeldung oben.
    pause
    goto :MENU
)
echo     [OK] Trainer-Dashboard installiert.
echo.

:: Schritt 4 -- KI-Modul + Modell --------------------------------------------
echo     Schritt 4 von 5  --  KI-Modul ^(llama-cpp-python^) + KI-Modell...
echo.
python -c "import llama_cpp" >nul 2>&1
if not errorlevel 1 (
    echo     [OK] KI-Modul bereits installiert.
) else (
    echo          Installiere llama-cpp-python CPU-Version ^(~50 MB^)...
    echo          ^(Dieser Schritt kann 1-2 Minuten dauern^)
    python -m pip install llama-cpp-python -q --disable-pip-version-check ^
        --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
    if errorlevel 1 (
        echo.
        echo     [!] KI-Modul konnte nicht installiert werden.
        echo         Das Programm laeuft auch ohne KI -- mit regelbasierter Verbesserung.
    ) else (
        echo     [OK] KI-Modul erfolgreich installiert.
    )
)
:: Download model if not present (regardless of whether llama-cpp-python just installed)
if not exist "tool-1-cv-maker\data\models\qwen2.5-1.5b-instruct-q4_k_m.gguf" (
    echo.
    echo     Lade KI-Modell herunter ^(~1,1 GB -- einmalig^)...
    echo     Bitte warten -- ca. 2-5 Minuten je nach Internetverbindung.
    echo     ^(Ohne Modell funktioniert alles -- nur der KI-Coach ist einfacher^)
    echo.
    python -c "import sys; sys.path.insert(0,'tool-1-cv-maker/src/backend'); from ai.local_llm import download_model; ok=download_model(); print('[OK] KI-Modell heruntergeladen.' if ok else '[!] Download fehlgeschlagen -- KI-Coach laeuft regelbasiert.')"
) else (
    echo     [OK] KI-Modell bereits vorhanden.
)
echo.

:: Schritt 5 -- Starten -------------------------------------------------------
echo     Schritt 5 von 5  --  Starte AMS JobAssist...
echo.
echo     Der Browser oeffnet sich automatisch.
echo     Lassen Sie dieses Fenster geoeffnet, solange Sie arbeiten.
echo.
echo  ================================================================
echo     Druecken Sie STRG+C um das Programm zu beenden.
echo  ================================================================
echo.
python launcher.py
echo.
echo     Programm wurde beendet.
echo.
pause
goto :MENU


:: ============================================================================
:RUN_ONLY
:: ============================================================================
cls
echo.
echo  ================================================================
echo     [2]  Starten
echo  ================================================================
echo.

pip show ams-cv-maker >nul 2>&1
if errorlevel 1 (
    echo     [!!] AMS JobAssist ist noch nicht installiert.
    echo.
    echo          Bitte waehlen Sie Option [1]  "Installieren und Starten".
    echo.
    pause
    goto :MENU
)

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
echo.
pause
goto :MENU


:: ============================================================================
:UNINSTALL
:: ============================================================================
cls
echo.
echo  ================================================================
echo     [3]  Deinstallieren
echo  ================================================================
echo.
echo     Folgendes wird vom Computer entfernt:
echo.
echo       - CV-Ersteller (Tool 1)
echo       - Trainer-Dashboard (Tool 2)
echo.
echo     Ihre Lebenslaeufe und Daten bleiben erhalten.
echo     (Option [4] zum dauerhaften Loeschen der Daten)
echo.
echo  ----------------------------------------------------------------
echo.

:: Pruefen ob ueberhaupt etwas installiert ist
pip show ams-cv-maker >nul 2>&1
set "T1_INST=!errorlevel!"
pip show ams-trainer >nul 2>&1
set "T2_INST=!errorlevel!"

if !T1_INST! neq 0 if !T2_INST! neq 0 (
    echo     [ ] Nichts installiert -- nichts zu entfernen.
    echo.
    pause
    goto :MENU
)

echo     Sind Sie sicher, dass Sie deinstallieren moechten?
echo.
choice /c JN /n /m "     [J] Ja, deinstallieren   [N] Nein, abbrechen:  "
echo.
if errorlevel 2 goto :MENU

echo.
echo     Deinstalliere...
echo.

if !T1_INST! == 0 (
    pip uninstall ams-cv-maker -y -q
    echo     [OK] CV-Ersteller (Tool 1) entfernt.
) else (
    echo     [ ] CV-Ersteller war nicht installiert.
)

if !T2_INST! == 0 (
    pip uninstall ams-trainer -y -q
    echo     [OK] Trainer-Dashboard (Tool 2) entfernt.
) else (
    echo     [ ] Trainer-Dashboard war nicht installiert.
)

python -c "import lingua" >nul 2>&1
if not errorlevel 1 (
    pip uninstall lingua-language-detector -y -q
    echo     [OK] Spracherkennungs-Modul entfernt.
) else (
    echo     [ ] Spracherkennungs-Modul war nicht installiert.
)

echo.
echo     Deinstallation abgeschlossen.
echo     Ihre Daten sind noch vorhanden (Option [4] zum Loeschen).
echo.
pause
goto :MENU


:: ============================================================================
:DELETE_DATA
:: ============================================================================
cls
echo.
echo  ================================================================
echo     [4]  Daten loeschen
echo  ================================================================
echo.
echo     Folgende Ordner werden DAUERHAFT geloescht:
echo.

set "FOUND=0"
if exist "tool-1-cv-maker\data" (
    echo       tool-1-cv-maker\data\         (Lebenslaeufe der Teilnehmer)
    set "FOUND=1"
)
if exist "tool-1-cv-maker\logs" (
    echo       tool-1-cv-maker\logs\         (Protokolldateien Tool 1)
    set "FOUND=1"
)
if exist "tool-2-trainer-dashboard\data" (
    echo       tool-2-trainer-dashboard\data\  (Trainer-Datenbank)
    set "FOUND=1"
)
if exist "tool-2-trainer-dashboard\logs" (
    echo       tool-2-trainer-dashboard\logs\  (Protokolldateien Tool 2)
    set "FOUND=1"
)

if !FOUND! == 0 (
    echo       Keine Daten gefunden -- nichts zu loeschen.
    echo.
    pause
    goto :MENU
)

echo.
echo  ----------------------------------------------------------------
echo.
echo     WARNUNG: Dies kann NICHT rueckgaengig gemacht werden!
echo     Alle Lebenslaeufe und Dateien werden dauerhaft geloescht.
echo.
echo     Sind Sie absolut sicher?
echo.
choice /c JN /n /m "     [J] Ja, ALLES loeschen   [N] Nein, abbrechen:  "
echo.
if errorlevel 2 goto :MENU

:: Zweite Bestaetigung - Sicherheitsstufe 2 ----------------------------------
echo.
echo     Letzte Bestaetigung erforderlich:
echo.
choice /c JN /n /m "     [J] Ja, ich bin sicher   [N] Abbrechen:  "
echo.
if errorlevel 2 goto :MENU

echo.
echo     Loeschen laeuft...
echo.

if exist "tool-1-cv-maker\data" (
    rmdir /s /q "tool-1-cv-maker\data"
    echo     [OK] tool-1-cv-maker\data\ geloescht.
)
if exist "tool-1-cv-maker\logs" (
    rmdir /s /q "tool-1-cv-maker\logs"
    echo     [OK] tool-1-cv-maker\logs\ geloescht.
)
if exist "tool-2-trainer-dashboard\data" (
    rmdir /s /q "tool-2-trainer-dashboard\data"
    echo     [OK] tool-2-trainer-dashboard\data\ geloescht.
)
if exist "tool-2-trainer-dashboard\logs" (
    rmdir /s /q "tool-2-trainer-dashboard\logs"
    echo     [OK] tool-2-trainer-dashboard\logs\ geloescht.
)

echo.
echo     Alle Daten wurden erfolgreich geloescht.
echo.
pause
goto :MENU


:: ============================================================================
:END
:: ============================================================================
cls
echo.
echo  ================================================================
echo     AMS JobAssist  --  Auf Wiedersehen!
echo  ================================================================
echo.
exit /b 0
