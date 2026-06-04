#!/usr/bin/env python
"""
20 AI-extraction tests — judge the quality yourself.

Runs 20 diverse, realistic participant "dumps" (different jobs, languages,
lengths, messiness) through the free-form extraction + builds the CV, then
writes ONE HTML report showing, for each: the raw input, exactly what the AI
pulled out (name / contact / target job / experience / education / skills /
motivation), what it would still ask about, and the final CV quality. Opens in
your browser so you can judge the output at a glance.

Usage:  python run_extraction_tests.py
"""
import os, sys, time, socket, json, subprocess, tempfile, webbrowser, html, datetime
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
T1 = os.path.join(ROOT, "tool-1-cv-maker", "src", "backend")
MODEL = os.path.join(ROOT, "tool-1-cv-maker", "data", "models", "qwen2.5-1.5b-instruct-q4_k_m.gguf")

# 20 diverse dumps — different professions, languages, completeness, messiness.
DUMPS = [
    ("CNC-Techniker (de, knapp)", "career-switch",
     "ich bin mina, ich habe als cnc engineer gearbeitet, ich bin 27, ich kann automatisierung, microcontrollers, electronics, rhino3d, cnc maschinen, holzarbeit"),
    ("Lagerarbeiter (en)", "unemployed",
     "My name is John Smith, I live in Graz, phone 0660 9999999, john@mail.com. I worked 3 years as a warehouse worker driving a forklift and packing orders. Driving licence B. I speak English and German. Looking for logistics work."),
    ("Reinigungskraft (de, mixed)", "unemployed",
     "ich heisse Amina, wohne in Wien 1100, ich hab 4 jahre putzen gemacht in hotel und buro, bin sehr genau und punktlich, spreche arabisch und ein bisschen deutsch, suche reinigung oder kuche"),
    ("Köchin (de)", "career-switch",
     "Maria Huber, Linz, +43 664 1112233, maria.huber@gmx.at. 6 Jahre Köchin in einem Restaurant, Frühstück und Mittagsservice, Team von 4 Personen geleitet. HLW Matura. Suche Stelle als Küchenleiterin."),
    ("Pflegehilfe (de)", "pause",
     "Ich bin Fatima, 35, war 5 Jahre zuhause bei den Kindern, davor 3 Jahre Pflegehelferin im Altersheim, Pflegehelfer-Ausbildung abgeschlossen, geduldig und einfühlsam, suche Wiedereinstieg in der Pflege"),
    ("Verkäufer (de, sehr knapp)", "unemployed",
     "Tom, Verkäufer bei BILLA gewesen, suche wieder Verkauf"),
    ("IT/Programmierer (en/de)", "career-switch",
     "Ich bin David Berger aus Wien, david.berger@dev.io. I worked 4 years as a junior web developer with JavaScript, Python, React and SQL. FH Informatik Bachelor. I want a full stack developer position."),
    ("Maurer (de, dialekt)", "unemployed",
     "i hoas Stefan, kumm aus Klagenfurt, hob 10 joa ois maurer goarbeit, mauern verputzen betonieren, fuhrerschein B und C, such wieda om bau"),
    ("Studentin Praktikum (de)", "student",
     "Lena, 21, studiere Wirtschaft an der WU Wien im 4. Semester, Praktikum im Marketing bei einer Agentur gemacht, kann Excel PowerPoint und Social Media, suche Teilzeit oder Praktikum im Marketing"),
    ("Fahrer (de)", "unemployed",
     "Ahmed, Wien, 0676 5544332. 7 Jahre LKW Fahrer und Paketzusteller, Führerschein C und E, pünktlich und ortskundig, suche Stelle als Fahrer oder in der Logistik"),
    ("Friseurin (de)", "career-switch",
     "Ich bin Sara, friseurin seit 8 jahren, schneiden faerben hochsteckfrisuren, eigene stammkunden, friseur lehre abgeschlossen, freundlich und kreativ, moechte gerne in ein groesseres salon team"),
    ("Büroangestellte (de)", "unemployed",
     "Petra Wagner, Wels, petra.w@aon.at, +43 650 7778899. 12 Jahre Bürokauffrau, Buchhaltung Rechnungen Ablage Kundenkontakt, MS Office sehr gut, Lehre Bürokauffrau, suche Büro oder Verwaltung Teilzeit"),
    ("Elektriker (de)", "career-switch",
     "Goran, Elektriker, 9 jahre erfahrung, installationen verkabelung fehlersuche, elektriker gesellenbrief, fuehrerschein B, spreche serbisch kroatisch deutsch, suche elektriker oder haustechnik"),
    ("Kellner (en, short)", "unemployed",
     "Carlos, waiter for 5 years, restaurants and cafes, fast and friendly, speak Spanish English German, looking for service job in Vienna"),
    ("Schneiderin (de, mixed)", "pause",
     "ich bin Nilufar aus afghanistan, naehe seit kind, 6 jahre als schneiderin gearbeitet, kleider reparieren und naehen, war 2 jahre pause, lerne jetzt deutsch a2, suche naeherei oder textil"),
    ("Gärtner (de)", "unemployed",
     "Markus, Garten und Landschaftsbau, 4 jahre, rasen baeume hecken pflanzen, fuehrerschein B, koerperlich fit, arbeite gern draussen, suche gartenarbeit oder hausmeister"),
    ("Buchhalter (de, detailliert)", "career-switch",
     "Mein Name ist Elena Petrova, ich wohne in Graz, Tel +43 660 2223344, elena.p@outlook.com. Ich habe 8 Jahre als Buchhalterin gearbeitet, Bilanzen, Lohnverrechnung, Steuererklärungen, BMD und SAP. Studium Betriebswirtschaft. Ich suche eine Stelle als Bilanzbuchhalterin oder im Controlling."),
    ("Hilfsarbeiter (de, sehr roh)", "unemployed",
     "hallo ich heisse omar ich brauche arbeit ich kann alles machen lager bau reinigung kein problem ich bin stark und schnell"),
    ("Krankenschwester (de)", "career-switch",
     "Ich bin Ivana, diplomierte Gesundheits- und Krankenpflegerin, 6 Jahre im Krankenhaus auf der Chirurgie, Patientenbetreuung Medikamente Dokumentation, spreche kroatisch und deutsch, suche Pflege oder OP-Bereich"),
    ("Quereinsteiger leer (de)", "other",
     "Ich weiss nicht so genau was ich schreiben soll. Ich hab verschiedene Sachen gemacht, mal im Geschäft geholfen, mal am Bau. Ich möchte einfach einen guten Job finden."),
]


def free_port(start):
    p = start
    while p < start + 200:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try: s.bind(("127.0.0.1", p)); return p
            except OSError: p += 1
    raise RuntimeError("no free port")


def http(method, url, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode())


def main():
    port = free_port(8000)
    base = f"http://127.0.0.1:{port}"
    model_present = os.path.exists(MODEL) and os.path.getsize(MODEL) > 10_000_000
    print(f"Tool 1 on free port {port} | model {'present' if model_present else 'MISSING (rule-based only)'}")
    log = os.path.join(tempfile.gettempdir(), "ams_xtract.log")
    env = os.environ.copy(); env["PYTHONPATH"] = T1; env["AMS_TOOL1_PORT"] = str(port)
    lf = open(log, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port)],
                            cwd=T1, stdout=lf, stderr=subprocess.STDOUT, env=env)
    rows = []
    try:
        # wait for health
        for _ in range(40):
            try:
                if http("GET", base + "/health", timeout=3)[0] == 200: break
            except Exception: pass
            time.sleep(1)
        if model_present:
            print("Warming the model (first call loads ~1GB)…")
            try: http("POST", base + "/api/ai/chat", {"message": "hi", "language": "de"}, timeout=180)
            except Exception: pass

        for i, (persona, path, dump) in enumerate(DUMPS, 1):
            t0 = time.time()
            try:
                _, s = http("POST", base + "/api/interview/start",
                            {"user_id": f"x{i}", "interview_path": path, "language": "de"}, timeout=20)
                sid = s["data"]["session_id"]
                _, r = http("POST", base + "/api/ai/dump-extract",
                            {"session_id": sid, "text": dump, "language": "de"}, timeout=120)
                cap = r["data"]["captured"]; missing = r["data"]["missing"]
                _, comp = http("POST", f"{base}/api/interview/complete/{sid}", timeout=60)
                cd = comp["data"]
                rows.append({"persona": persona, "dump": dump, "cap": cap, "missing": missing,
                             "sections": cd.get("sections_count"), "quality": round(cd.get("overall_quality", 0), 2),
                             "skills": cd.get("all_skills", []), "secs": round(time.time() - t0, 1)})
                print(f"  [{i:2}/20] {persona}  ({round(time.time()-t0,1)}s)")
            except Exception as e:
                rows.append({"persona": persona, "dump": dump, "error": str(e)})
                print(f"  [{i:2}/20] {persona}  ERROR {e}")
    finally:
        try: proc.terminate(); proc.wait(timeout=5)
        except Exception:
            try: proc.kill()
            except Exception: pass
        lf.close()

    # ---- HTML report ----
    def esc(x): return html.escape(str(x))
    def chips(items, cls):
        return "".join(f'<span class="chip {cls}">{esc(x)}</span>' for x in (items or [])) or '<span class="none">—</span>'
    cards = []
    for n, r in enumerate(rows, 1):
        if "error" in r:
            cards.append(f'<div class="card err"><div class="ph">{n}. {esc(r["persona"])}</div><div class="d">ERROR: {esc(r["error"])}</div></div>')
            continue
        cap = r["cap"]
        contact = " · ".join([x for x in (cap.get("city"), cap.get("phone"), cap.get("email")) if x]) or "—"
        cards.append(f"""
        <div class="card">
          <div class="ph">{n}. {esc(r['persona'])} <span class="meta">CV: {r['sections']} sections · quality {r['quality']} · {r['secs']}s</span></div>
          <div class="dump">“{esc(r['dump'])}”</div>
          <table class="kv">
            <tr><td>Name</td><td><b>{esc(cap.get('name') or '—')}</b></td></tr>
            <tr><td>Kontakt</td><td>{esc(contact)}</td></tr>
            <tr><td>Zielberuf</td><td>{esc(cap.get('target_job') or '—')}</td></tr>
            <tr><td>Erfahrung</td><td>{chips(cap.get('experiences'), 'exp')}</td></tr>
            <tr><td>Ausbildung</td><td>{chips(cap.get('education'), 'edu')}</td></tr>
            <tr><td>Kenntnisse</td><td>{chips(cap.get('skills'), 'sk')}</td></tr>
            <tr><td>CV-Skills (final)</td><td>{chips(r.get('skills'), 'sk2')}</td></tr>
            <tr><td>Fragt noch nach</td><td>{chips(r.get('missing'), 'm')}</td></tr>
          </table>
        </div>""")
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    avg_q = round(sum(r.get("quality", 0) for r in rows if "error" not in r) / max(1, sum(1 for r in rows if "error" not in r)), 2)
    report = f"""<!doctype html><html><head><meta charset="utf-8"><title>AMS — 20 Extraction Tests</title><style>
    body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#eef1f6;margin:0;color:#1e293b}}
    .wrap{{max-width:980px;margin:0 auto;padding:26px}} h1{{margin:0 0 2px}} .sub{{color:#64748b;margin-bottom:18px}}
    .card{{background:#fff;border-radius:12px;padding:16px 18px;margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,.06);border-left:6px solid #6c3483}}
    .card.err{{border-left-color:#dc2626}}
    .ph{{font-weight:700;font-size:16px;margin-bottom:8px}} .meta{{font-weight:500;font-size:12px;color:#64748b;margin-left:6px}}
    .dump{{font-style:italic;color:#475569;background:#f8fafc;border-radius:8px;padding:9px 12px;margin-bottom:10px;font-size:13.5px}}
    table.kv{{width:100%;border-collapse:collapse}} td{{padding:4px 6px;vertical-align:top;font-size:13.5px}}
    td:first-child{{color:#64748b;width:130px;white-space:nowrap}}
    .chip{{display:inline-block;background:#eef2ff;color:#3730a3;border-radius:6px;padding:2px 8px;margin:2px 3px 2px 0;font-size:12.5px}}
    .chip.exp{{background:#e0f2fe;color:#075985}} .chip.edu{{background:#dcfce7;color:#166534}} .chip.sk,.chip.sk2{{background:#f3e8ff;color:#6b21a8}}
    .chip.m{{background:#fef3c7;color:#92400e}} .none{{color:#94a3b8}}
    .hero{{background:#fff;border-radius:12px;padding:18px 22px;margin-bottom:18px;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
    </style></head><body><div class="wrap">
    <h1>AMS JobAssist — 20 AI extraction tests</h1>
    <div class="sub">{stamp} · model {'present (local Qwen 1.5B)' if model_present else 'MISSING — rule-based only'} · judge the output below</div>
    <div class="hero"><b>{sum(1 for r in rows if 'error' not in r)}/20</b> processed · average CV quality <b>{avg_q}</b><br>
    <span class="sub">Each card: the raw participant input, then exactly what the AI structured out of it, and what it would still ask in the conversation.</span></div>
    {''.join(cards)}
    </div></body></html>"""
    out = os.path.join(ROOT, "EXTRACTION_REPORT.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport: {out}")
    try: webbrowser.open("file:///" + out.replace("\\", "/"))
    except Exception: pass


if __name__ == "__main__":
    main()
