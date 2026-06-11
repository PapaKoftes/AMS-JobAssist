# AMS-JobAssist — Test-Anleitung für Marko

Danke fürs Testen! Ziel: Du installierst das Tool, gibst ein paar echte/erfundene
Fälle ein, **speicherst sie**, und notierst, was gut läuft und was nicht. Alles
läuft **offline** auf deinem PC — es verlässt nichts deinen Rechner.

---

## 1. Installieren (5 Minuten, kein Admin nötig)

1. Du bekommst einen Ordner `dist` (oder eine `AMS-JobAssist-Setup.exe`).
2. Doppelklick auf **`install.bat`** (bzw. die Setup-Datei).
3. Fertig — es entsteht eine Verknüpfung **„AMS JobAssist"** (Startmenü/Desktop).
   Das KI-Modell (3B) ist schon enthalten, **kein Download nötig**.
4. Falls Windows „SmartScreen" warnt: **„Weitere Informationen" → „Trotzdem ausführen"**
   (die .exe ist nicht signiert — harmlos).

Starten: **„AMS JobAssist"** öffnen. Der Browser geht automatisch auf:
- **http://localhost:8000** — CV-Ersteller (Teilnehmer-Sicht)
- **http://localhost:8001** — Trainer-Dashboard

> Der **erste** KI-Aufruf dauert ~15–20 Sek. (Modell lädt). Danach schnell.

---

## 2. Einen Fall durchspielen (Teilnehmer-Sicht, localhost:8000)

1. Sprache wählen (Flagge), Einverständnis ankreuzen, einen Weg wählen
   (z. B. „Berufswechsel"), Name eingeben, **Start**.
2. Im Chat **alles in einem Schwung eintippen** — beliebige Sprache, ruhig grob.
   Beispiel:
   > *„Ich heiße Amir Yilmaz, wohne in 1100 Wien, 0660 1234567, amir@example.at.
   > Drei Jahre Lager bei einer Spedition: kommissioniert, Stapler gefahren. Davor
   > Kassa im Supermarkt. Pflichtschule, Staplerschein. Deutsch und Türkisch.
   > Suche Lagermitarbeiter."*
3. Schau zu, wie die KI das **oben in den Lebenslauf** einsortiert. Dann **„✓ Lebenslauf
   erstellen"**.
4. Auf der Abschluss-Seite: **PDF / Word** herunterladen, **Anschreiben**, und der Button
   **„🔎 Passende Jobs beim AMS finden"** (öffnet das AMS-Jobportal mit dem Suchbegriff).

---

## 3. Fälle SPEICHERN — der „Testmodus"

Damit wir genau sehen, was du eingegeben hast und was rauskam:

1. **Testmodus einschalten:** Drücke **Strg + Shift + T**. Unten rechts erscheint
   **„🧪 Testmodus aktiv"**. (Nochmal drücken = aus. Bleibt gespeichert.)
2. Spiele einen Fall durch (Schritt 2 oben) bis zum fertigen Lebenslauf.
3. Auf der Abschluss-Seite erscheint jetzt **„💾 Diesen Fall als Testfall speichern (JSON)"**.
   Klick → es lädt eine Datei `testfall_<name>.json` herunter (Eingabe **und** Ergebnis).
4. Sammle alle `testfall_*.json` in **einem Ordner**.

> Kein Testmodus? Du kannst auch jederzeit **„🔒 Meine Daten herunterladen"** klicken —
> das speichert denselben Fall (DSGVO-Export).

---

## 4. Worauf achten (und in `TESTFAELLE.md` notieren)

Bitte pro Fall kurz notieren (Vorlage: **`TESTFAELLE.md`**):
- **Name/Kontakt** richtig erkannt?
- **Zielberuf** richtig?
- **Berufserfahrung** sinnvoll strukturiert (Tätigkeit/Arbeitgeber/Zeitraum)?
- **Kenntnisse/Skills** — fehlt etwas Offensichtliches? Steht Falsches drin?
- **Ausbildung** korrekt?
- **PDF/Word** — sieht es brauchbar aus? (Foto optional hochladen für besseres Bild)
- Irgendwo **abgestürzt, hängengeblieben, verwirrend**?
- Mehrsprachig: probier ruhig Türkisch/BKS/Arabisch als Eingabe.

---

## 5. Zurückschicken

Schick mir:
1. den Ordner mit den **`testfall_*.json`**-Dateien, und
2. die ausgefüllte **`TESTFAELLE.md`** (deine Notizen).

Das reicht, damit wir genau nachstellen können, was passiert ist.

---

## Was NOCH NICHT drin ist (nicht als Fehler melden)
- **Live-Job-Matching im Tool** (Stellen direkt aus AMS holen + bewerten) ist
  geplant, aber noch nicht gebaut — der **Button öffnet** nur die AMS-Jobsuche.
- Kohorten-Anlage-UI im Trainer-Dashboard.

Alles andere — CV erstellen, mehrsprachig, PDF/Word/Anschreiben, Trainer-Review,
Skill-Auswertung, AMS-Job-Link — ist echt und funktioniert.
