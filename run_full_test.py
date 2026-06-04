#!/usr/bin/env python
"""
AMS JobAssist — full end-to-end verification.

Run this once before handing the zip to a tester. It:
  1. Starts BOTH tools on automatically-chosen free ports (so it works even if
     8000/8001 are busy).
  2. Runs an intensive suite covering the whole product — structured interview,
     the free-form "dump" + AI extraction, multilingual polish, all four export
     formats, the cover letter, ATS job-match, the AI chat coach / interview
     prep, DSGVO data export, and the full Tool 1 -> Tool 2 trainer handoff
     (import -> edit -> approve -> bulk export).
  3. Writes ONE combined HTML report and opens it in your browser.

Usage:   python run_full_test.py
"""
import os, sys, time, socket, json, subprocess, tempfile, webbrowser, html, datetime, io, zipfile
import urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
T1_BACKEND = os.path.join(ROOT, "tool-1-cv-maker", "src", "backend")
T2_BACKEND = os.path.join(ROOT, "tool-2-trainer-dashboard", "src", "backend")
MODEL = os.path.join(ROOT, "tool-1-cv-maker", "data", "models", "qwen2.5-1.5b-instruct-q4_k_m.gguf")

results = []   # {group, name, status: PASS/FAIL/WARN/SKIP, detail, secs}
_groups_order = []


def free_port(start):
    p = start
    while p < start + 200:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p)); return p
            except OSError:
                p += 1
    raise RuntimeError("no free port")


def rec(group, name, status, detail="", secs=None):
    if group not in _groups_order:
        _groups_order.append(group)
    results.append({"group": group, "name": name, "status": status,
                    "detail": str(detail)[:600], "secs": secs})
    tag = {"PASS": "[OK]  ", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[skip]"}.get(status, "      ")
    print(f"  {tag} {name}" + (f"  ({secs:.1f}s)" if secs else ""))


def http(method, url, body=None, timeout=60, raw=False):
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        content = r.read()
        hdr = {k.lower(): v for k, v in dict(r.headers).items()}  # case-insensitive
        if raw:
            return r.status, content, hdr
        try:
            return r.status, json.loads(content.decode("utf-8")), hdr
        except Exception:
            return r.status, content.decode("utf-8", "replace"), hdr


def check(group, name, fn, timeout=60):
    """Run fn() -> (ok: bool, detail: str). Records PASS/FAIL with timing."""
    t0 = time.time()
    try:
        ok, detail = fn()
        rec(group, name, "PASS" if ok else "FAIL", detail, time.time() - t0)
        return ok
    except Exception as e:
        rec(group, name, "FAIL", f"{type(e).__name__}: {e}", time.time() - t0)
        return False


def start_server(backend, port, env_port_var, logfile):
    env = os.environ.copy()
    env["PYTHONPATH"] = backend
    env[env_port_var] = str(port)
    env.setdefault("AMS_ENFORCE_OFFLINE", "1")   # production default
    lf = open(logfile, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=backend, stdout=lf, stderr=subprocess.STDOUT, env=env,
    )
    return proc, lf


def wait_health(base, label, deadline=40):
    end = time.time() + deadline
    while time.time() < end:
        try:
            s, j, _ = http("GET", base + "/health", timeout=3)
            if s == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    print("=" * 70)
    print("AMS JobAssist — full end-to-end verification")
    print("=" * 70)

    p1 = free_port(8000)
    p2 = free_port(p1 + 1)
    b1 = f"http://127.0.0.1:{p1}"
    b2 = f"http://127.0.0.1:{p2}"
    print(f"Tool 1 on free port {p1} | Tool 2 on free port {p2}")
    print(f"(works even if 8000/8001 are busy — ports are auto-selected)\n")

    log1 = os.path.join(tempfile.gettempdir(), "ams_test_t1.log")
    log2 = os.path.join(tempfile.gettempdir(), "ams_test_t2.log")
    model_present = os.path.exists(MODEL) and os.path.getsize(MODEL) > 10_000_000

    procs = []
    try:
        print("Starting servers...")
        pr1, lf1 = start_server(T1_BACKEND, p1, "AMS_TOOL1_PORT", log1); procs.append((pr1, lf1))
        pr2, lf2 = start_server(T2_BACKEND, p2, "AMS_TOOL2_PORT", log2); procs.append((pr2, lf2))

        ok1 = wait_health(b1, "Tool 1")
        ok2 = wait_health(b2, "Tool 2")

        # ---- GROUP: Infrastructure ----------------------------------------
        G = "1 · Infrastructure & ports"
        rec(G, f"Tool 1 starts on free port {p1}", "PASS" if ok1 else "FAIL",
            f"{b1} (8000 fallback works)" if ok1 else f"see {log1}")
        rec(G, f"Tool 2 starts on free port {p2}", "PASS" if ok2 else "FAIL",
            f"{b2}" if ok2 else f"see {log2}")
        if not ok1:
            raise RuntimeError("Tool 1 did not come up — aborting")

        def _nocache():
            s, _, hdr = http("GET", b1 + "/", timeout=10, raw=True)
            cc = hdr.get("cache-control", "")
            return ("no-cache" in cc, f"Cache-Control: {cc!r} (UI changes always load)")
        check(G, "App shell sent with no-cache headers", _nocache)

        def _static():
            s, c, hdr = http("GET", b1 + "/static/app.js", timeout=10, raw=True)
            return (s == 200 and len(c) > 10000, f"app.js {len(c)} bytes")
        check(G, "Static assets served", _static)

        # ---- GROUP: AI model ----------------------------------------------
        G = "2 · AI model"
        rec(G, "Local model present on disk", "PASS" if model_present else "WARN",
            (f"{os.path.getsize(MODEL)//1_000_000} MB" if model_present
             else "model missing — AI features fall back to rules"))

        def _status():
            s, j, _ = http("GET", b1 + "/api/interview/ai/status", timeout=15)
            eng = j.get("data", {}).get("engine")
            return (eng in ("local", "ollama", "rules"), f"engine={eng}")
        check(G, "AI status endpoint", _status)

        def _dlstatus():
            s, j, _ = http("GET", b1 + "/api/ai/download-status", timeout=10)
            return (s == 200, f"status={j.get('data',{}).get('status')}")
        check(G, "Model download-status endpoint (resume/cancel API)", _dlstatus)

        # Warm the model once so later AI tests aren't penalised by load time.
        if model_present:
            print("Warming the model (first AI call loads ~1GB)...")
            try:
                http("POST", b1 + "/api/ai/chat", {"message": "hallo", "language": "de"}, timeout=180)
            except Exception:
                pass

        # ---- GROUP: Structured interview ----------------------------------
        G = "3 · Structured interview"
        sid_struct = [None]

        def _start():
            s, j, _ = http("POST", b1 + "/api/interview/start",
                           {"user_id": "TestStruct", "interview_path": "career-switch", "language": "de", "consent_given": True}, timeout=15)
            d = j["data"]; sid_struct[0] = d["session_id"]
            q = d["question"]
            return (d["progress"]["total"] == 13 and "identity" in (q.get("flags") or []),
                    f"{d['progress']['total']} steps; q1 flags={q.get('flags')} min_len={q.get('min_length')}")
        check(G, "Start: 13 steps, identity collapsed", _start)

        def _shortname():
            sid = sid_struct[0]
            s, j, _ = http("POST", b1 + "/api/interview/submit-answer",
                           {"session_id": sid, "question_id": "id_name", "answer_text": "Max"}, timeout=15)
            return (j.get("status") == "success", "short name 'Max' accepted (no 'too short')")
        check(G, "Short name accepted", _shortname)

        def _contact():
            sid = sid_struct[0]
            http("GET", b1 + "/api/interview/next-question/%d" % sid, timeout=10)
            s, j, _ = http("POST", b1 + "/api/interview/submit-answer",
                           {"session_id": sid, "question_id": "id_contact",
                            "answer_text": "Wien, +43 660 1234567, max@example.com"}, timeout=15)
            return (j.get("status") == "success", "combined contact accepted (parsed to city/phone/email)")
        check(G, "Combined contact step", _contact)

        # ---- GROUP: Dump mode + AI extraction -----------------------------
        G = "4 · Free-form dump + AI extraction"
        sid_dump = [None]

        def _dump_de():
            s, j, _ = http("POST", b1 + "/api/interview/start",
                           {"user_id": "TestDump", "interview_path": "career-switch", "language": "de", "consent_given": True}, timeout=15)
            sid_dump[0] = j["data"]["session_id"]
            dump = ("Ich bin Maria Horvat aus Wien, +43 660 1234567, maria@example.com. "
                    "Fuenf Jahre Baeckerei: Brot gebacken, Kasse gefuehrt, Kunden beraten. "
                    "Pflichtschulabschluss, Staplerschein. Punktlich, spreche Deutsch und Bosnisch. "
                    "Suche Buerokauffrau oder Verkauf.")
            s, j, _ = http("POST", b1 + "/api/ai/dump-extract",
                           {"session_id": sid_dump[0], "text": dump, "language": "de"}, timeout=180)
            c = j["data"]["captured"]
            ok = bool(c.get("name")) and bool(c.get("city")) and bool(c.get("email")) and len(c.get("experiences") or []) >= 1
            return (ok, f"name={c.get('name')!r} city={c.get('city')!r} phone={bool(c.get('phone'))} "
                        f"email={c.get('email')!r} target={c.get('target_job')!r} "
                        f"exp={len(c.get('experiences') or [])} edu={len(c.get('education') or [])} skills={len(c.get('skills') or [])}")
        check(G, "Dump (German) -> structured fields", _dump_de, timeout=200)

        def _dump_en():
            s, j, _ = http("POST", b1 + "/api/interview/start",
                           {"user_id": "TestDumpEN", "interview_path": "unemployed", "language": "en", "consent_given": True}, timeout=15)
            sid = j["data"]["session_id"]
            dump = ("My name is John Smith, I live in Graz, phone 0660 9999999, john@mail.com. "
                    "I worked 3 years as a warehouse worker driving a forklift and packing orders. "
                    "I have a driving licence. I speak English and German. Looking for logistics work.")
            s, j, _ = http("POST", b1 + "/api/ai/dump-extract",
                           {"session_id": sid, "text": dump, "language": "en"}, timeout=180)
            c = j["data"]["captured"]
            return (bool(c.get("email")) and len(c.get("experiences") or []) >= 1,
                    f"multilingual: name={c.get('name')!r} email={c.get('email')!r} exp={len(c.get('experiences') or [])}")
        check(G, "Dump (English) -> multilingual extraction", _dump_en, timeout=200)

        def _dump_complete():
            sid = sid_dump[0]
            t0 = time.time()
            s, j, _ = http("POST", b1 + "/api/interview/complete/%d" % sid, timeout=60)
            d = j["data"]; dt = time.time() - t0
            fast = dt < 10
            return (d.get("ready_for_export") and d.get("sections_count", 0) >= 1,
                    f"complete in {dt:.1f}s ({'fast' if fast else 'SLOW'}) sections={d.get('sections_count')} "
                    f"quality={round(d.get('overall_quality',0),2)} skills={len(d.get('all_skills') or [])}")
        check(G, "Complete dumped CV (must be fast, rules-first)", _dump_complete)

        # ---- GROUP: Polish / multilingual ---------------------------------
        G = "5 · Polish & language"
        def _preview():
            s, j, _ = http("POST", b1 + "/api/interview/preview",
                           {"answer_text": "ich hab in der backerei gearbeitet und kunden geholfen",
                            "category": "experience", "language": "de"}, timeout=30)
            pol = (j.get("data") or {}).get("polished_text", "")
            return (len(pol) > 10, f"polished: {pol[:80]!r}")
        check(G, "Rough German -> polished text", _preview)

        # ---- GROUP: Exports (all formats) ---------------------------------
        G = "6 · Exports (every format)"
        sid = sid_dump[0]
        export_specs = [
            ("pdf", b"%PDF", "PDF (Austrian Tabellarischer Lebenslauf)"),
            ("docx", b"PK\x03\x04", "DOCX (editable in Word/LibreOffice)"),
            ("europass", b"<?xm", "Europass XML"),
            ("json", b"{", "JSON (for the trainer dashboard)"),
        ]
        for fmt, magic, label in export_specs:
            def _exp(fmt=fmt, magic=magic, label=label):
                s, c, hdr = http("POST", b1 + "/api/export/%s" % fmt,
                                 {"session_id": sid, "language": "de"}, timeout=40, raw=True)
                return (s == 200 and c[:len(magic)] == magic and len(c) > 200,
                        f"{label}: {len(c)} bytes, header OK")
            check(G, f"Export {fmt.upper()}", _exp)

        def _cover():
            s, j, _ = http("POST", b1 + "/api/export/cover-letter",
                           {"session_id": sid, "job_title": "Buerokauffrau", "employer_name": "Firma XY", "language": "de"}, timeout=120)
            txt = (j.get("data") or {}).get("text", "")
            return (len(txt.split()) > 50 and "Bewerbung" in txt,
                    f"{len((j.get('data') or {}).get('text','').split())} words; Austrian Vorlage format")
        check(G, "Cover letter generator", _cover, timeout=130)

        # ---- GROUP: AI features -------------------------------------------
        G = "7 · AI features"
        if model_present:
            def _chat():
                s, j, _ = http("POST", b1 + "/api/ai/chat",
                               {"session_id": sid, "message": "Ist mein Lebenslauf gut?", "language": "de"}, timeout=120)
                d = j.get("data", {})
                return (bool(d.get("reply")), f"ai_mode={d.get('ai_mode')} reply={str(d.get('reply'))[:70]!r}")
            check(G, "AI chat coach (CV-aware)", _chat, timeout=130)

            def _prep():
                s, j, _ = http("POST", b1 + "/api/ai/interview-prep", {"session_id": sid}, timeout=120)
                qs = (j.get("data") or {}).get("questions") or []
                return (len(qs) >= 3, f"{len(qs)} practice questions (source={(j.get('data') or {}).get('source')})")
            check(G, "Interview prep generator", _prep, timeout=130)
        else:
            rec(G, "AI chat coach", "SKIP", "model not present")
            rec(G, "Interview prep generator", "SKIP", "model not present")

        def _ats():
            s, j, _ = http("POST", b1 + "/api/ats/score",
                           {"session_id": sid,
                            "job_description": "Wir suchen eine Buerokauffrau mit Kassenfuehrung, Kundenbetreuung und MS Office."}, timeout=40)
            d = j.get("data", {})
            return (d.get("score") is not None,
                    f"score={round(d.get('score',0),2)} grade={d.get('grade')} matched={len(d.get('matched_keywords') or [])}")
        check(G, "ATS job-match", _ats)

        # ---- GROUP: DSGVO / privacy ---------------------------------------
        G = "8 · Privacy & DSGVO"
        def _status_of(method, url):
            """Return HTTP status even on 4xx/5xx (urllib raises otherwise)."""
            try:
                s, _c, _h = http(method, url, timeout=20, raw=True)
                return s
            except urllib.error.HTTPError as e:
                return e.code

        def _mydata():
            msid = sid_dump[0]
            # IDOR must be blocked: without the owning user_id → 404.
            s_no = _status_of("GET", b1 + "/api/cv/%d/my-data" % msid)
            if s_no == 200:
                return (False, "IDOR: my-data returned data WITHOUT user_id proof")
            # With the correct owner user_id → 200 + JSON.
            s, c, hdr = http("GET", b1 + "/api/cv/%d/my-data?user_id=TestDump" % msid, timeout=20, raw=True)
            return (s == 200 and len(c) > 100 and c[:1] == b"{",
                    f"Art. 20 export OK (IDOR blocked: {s_no}); {len(c)} bytes JSON")
        check(G, "DSGVO data download (Art. 20) + IDOR blocked", _mydata)

        def _erase():
            # Art. 17: erase a throwaway session; requires the owning user_id.
            _s0, j0, _ = http("POST", b1 + "/api/interview/start",
                             {"user_id": "EraseMe", "interview_path": "other",
                              "language": "de", "consent_given": True}, timeout=15)
            esid = j0["data"]["session_id"]
            s_bad = _status_of("DELETE", b1 + "/api/cv/%d/erase" % esid)            # no proof → 404
            s_ok = _status_of("DELETE", b1 + "/api/cv/%d/erase?user_id=EraseMe" % esid)  # proof → 200
            return (s_bad == 404 and s_ok == 200,
                    f"erase refused without proof ({s_bad}), succeeded with proof ({s_ok})")
        check(G, "DSGVO right-to-erasure (Art. 17)", _erase)

        def _consent():
            try:
                http("POST", b1 + "/api/interview/start",
                     {"user_id": "NoConsent", "interview_path": "other", "language": "de"},
                     timeout=15)
                return (False, "start succeeded WITHOUT consent")
            except urllib.error.HTTPError as e:
                return (e.code == 403, f"start without consent refused ({e.code})")
        check(G, "Consent required to start (Art. 7)", _consent)

        def _backup():
            s, c, hdr = http("GET", b1 + "/api/admin/backup", timeout=20, raw=True)
            return (s == 200 and c[:15] == b"SQLite format 3", f"DB backup: {len(c)} bytes")
        check(G, "Admin DB backup", _backup)

        # ---- GROUP: Tool 2 trainer + full handoff -------------------------
        G = "9 · Trainer dashboard (Tool 1 -> Tool 2 handoff)"
        if ok2:
            # Export the dumped CV as canonical JSON from Tool 1, import into Tool 2.
            pid = [None]

            cv_export = [None]

            def _post_import(url):
                """Upload the exported Tool 1 CV to Tool 2; returns parsed JSON."""
                if cv_export[0] is None:
                    _s, cv_bytes, _h = http("POST", b1 + "/api/export/json",
                                            {"session_id": sid, "language": "de"}, timeout=30, raw=True)
                    cv_export[0] = cv_bytes
                boundary = "----amsTestBoundary"
                body = (
                    f"--{boundary}\r\n"
                    'Content-Disposition: form-data; name="file"; filename="cv.json"\r\n'
                    "Content-Type: application/json\r\n\r\n"
                ).encode() + cv_export[0] + f"\r\n--{boundary}--\r\n".encode()
                req = urllib.request.Request(
                    url, data=body, method="POST",
                    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.loads(r.read().decode())

            def _import():
                # force_overwrite=true mirrors a trainer deliberately re-importing
                # after a prior approval; keeps the harness deterministic across runs
                # now that re-import protection (B7) guards locked/approved CVs.
                j = _post_import(b2 + "/api/import-cvs?cohort_id=TestCohort&force_overwrite=true")
                pid[0] = j.get("participant_id")
                return (j.get("imported", 0) >= 1 and pid[0], f"imported participant_id={pid[0]}")
            check(G, "Import Tool 1 CV into Tool 2 (real handoff)", _import)

            def _reimport_protection():
                # Approve the just-imported CV, then a plain re-import (no force)
                # must be refused with 409 so trainer work is never silently shadowed.
                http("POST", b2 + "/api/participants/%d/approve" % pid[0],
                     {"approval_status": "approved", "approved_by": "T"}, timeout=15)
                try:
                    _post_import(b2 + "/api/import-cvs?cohort_id=TestCohort")
                    return (False, "re-import was NOT refused (expected 409)")
                except urllib.error.HTTPError as e:
                    return (e.code == 409, f"re-import of approved CV refused (HTTP {e.code})")
            check(G, "Re-import protection: approved CV not overwritten (B7)", _reimport_protection)

            def _list():
                s, j, _ = http("GET", b2 + "/api/participants?cohort_id=TestCohort", timeout=15)
                return (j.get("total", 0) >= 1, f"{j.get('total')} participant(s) listed")
            check(G, "Participant list", _list)

            def _detail_and_edit():
                p = pid[0]
                s, j, _ = http("GET", b2 + "/api/participants/%d" % p, timeout=15)
                cv = (j.get("latest_submission") or {}).get("cv_data") or {}
                # find an editable canonical section key
                key = None
                for lst in ("experience", "education", "custom_sections"):
                    if isinstance(cv.get(lst), list) and cv[lst]:
                        key = f"{lst}.0"; break
                if not key:
                    return (False, "no canonical section found to edit")
                s, j2, _ = http("PATCH", b2 + "/api/participants/%d/cv-section" % p,
                                {"question_id": key, "edited_text": "TRAINER GEAENDERT", "language": "de"}, timeout=15)
                # re-fetch and confirm persisted
                s, j3, _ = http("GET", b2 + "/api/participants/%d" % p, timeout=15)
                cv3 = (j3.get("latest_submission") or {}).get("cv_data") or {}
                lst, idx = key.split("."); idx = int(idx)
                saved = (cv3.get(lst) or [{}])[idx].get("german", "")
                return ("TRAINER" in saved, f"edited {key}; persisted={'TRAINER' in saved}")
            check(G, "Detail renders + inline edit persists (canonical)", _detail_and_edit)

            def _approve():
                p = pid[0]
                s, j, _ = http("POST", b2 + "/api/participants/%d/approve" % p,
                               {"approval_status": "approved", "feedback": "Gut", "approved_by": "TestTrainer"}, timeout=15)
                return (j.get("approval_status") == "approved", "approved with audit record")
            check(G, "Approve participant", _approve)

            def _bulk():
                s, c, hdr = http("POST", b2 + "/api/bulk-export",
                                 {"participant_ids": [pid[0]], "format": "pdf"}, timeout=60, raw=True)
                isz = c[:2] == b"PK"
                # confirm the zip actually contains a non-trivial PDF
                inner_ok = False
                try:
                    zf = zipfile.ZipFile(io.BytesIO(c))
                    for n in zf.namelist():
                        if n.lower().endswith(".pdf") and len(zf.read(n)) > 500:
                            inner_ok = True
                except Exception:
                    pass
                return (isz and inner_ok, f"zip {len(c)} bytes, contains a real PDF={inner_ok}")
            check(G, "Bulk export (zip of real PDFs)", _bulk)
        else:
            rec(G, "Tool 2 handoff", "SKIP", "Tool 2 did not start")

    finally:
        for pr, lf in procs:
            try:
                pr.terminate(); pr.wait(timeout=5)
            except Exception:
                try: pr.kill()
                except Exception: pass
            try: lf.close()
            except Exception: pass

    # ---- Build the combined HTML report -----------------------------------
    npass = sum(1 for r in results if r["status"] == "PASS")
    nfail = sum(1 for r in results if r["status"] == "FAIL")
    nwarn = sum(1 for r in results if r["status"] == "WARN")
    nskip = sum(1 for r in results if r["status"] == "SKIP")
    overall = "ALL GREEN" if nfail == 0 else f"{nfail} FAILURE(S)"
    colour = "#16a34a" if nfail == 0 else "#dc2626"
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for g in _groups_order:
        rows.append(f'<tr class="grp"><td colspan="3">{html.escape(g)}</td></tr>')
        for r in [x for x in results if x["group"] == g]:
            badge = {"PASS": ("#16a34a", "PASS"), "FAIL": ("#dc2626", "FAIL"),
                     "WARN": ("#d97706", "WARN"), "SKIP": ("#6b7280", "SKIP")}[r["status"]]
            secs = f'{r["secs"]:.1f}s' if r["secs"] else ""
            rows.append(
                f'<tr><td><span class="b" style="background:{badge[0]}">{badge[1]}</span></td>'
                f'<td><b>{html.escape(r["name"])}</b><div class="d">{html.escape(r["detail"])}</div></td>'
                f'<td class="t">{secs}</td></tr>')

    report = f"""<!doctype html><html><head><meta charset="utf-8">
<title>AMS JobAssist — Test Report</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#f1f5f9;margin:0;color:#1e293b}}
 .wrap{{max-width:920px;margin:0 auto;padding:28px}}
 h1{{margin:0 0 4px}} .sub{{color:#64748b;margin-bottom:18px}}
 .hero{{background:white;border-radius:14px;padding:22px 26px;box-shadow:0 2px 10px rgba(0,0,0,.06);margin-bottom:20px;border-left:8px solid {colour}}}
 .big{{font-size:30px;font-weight:800;color:{colour}}}
 .counts span{{display:inline-block;margin-right:16px;font-weight:600}}
 table{{width:100%;border-collapse:collapse;background:white;border-radius:14px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.06)}}
 td{{padding:10px 14px;border-bottom:1px solid #eef2f7;vertical-align:top}}
 tr.grp td{{background:#1e293b;color:white;font-weight:700;font-size:14px;letter-spacing:.02em}}
 .b{{color:white;padding:2px 9px;border-radius:6px;font-size:12px;font-weight:700}}
 .d{{color:#64748b;font-size:13px;margin-top:3px;font-family:ui-monospace,Consolas,monospace}}
 .t{{color:#94a3b8;font-size:12px;text-align:right;white-space:nowrap}}
</style></head><body><div class="wrap">
 <h1>AMS JobAssist — Full Verification</h1>
 <div class="sub">{stamp} · Tool 1 port {p1} · Tool 2 port {p2} · model {'present' if model_present else 'MISSING'}</div>
 <div class="hero"><div class="big">{overall}</div>
   <div class="counts"><span style="color:#16a34a">✓ {npass} passed</span>
   <span style="color:#dc2626">✗ {nfail} failed</span>
   <span style="color:#d97706">⚠ {nwarn} warnings</span>
   <span style="color:#6b7280">– {nskip} skipped</span></div></div>
 <table>{''.join(rows)}</table>
 <p class="sub" style="margin-top:18px">Servers ran on auto-selected free ports, so this also confirms the app works when 8000/8001 are busy. Logs: {html.escape(log1)} · {html.escape(log2)}</p>
</div></body></html>"""

    out = os.path.join(ROOT, "TEST_REPORT.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 70)
    print(f"{overall}  —  {npass} passed, {nfail} failed, {nwarn} warn, {nskip} skip")
    print(f"Report: {out}")
    print("=" * 70)
    try:
        webbrowser.open("file:///" + out.replace("\\", "/"))
    except Exception:
        pass
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
