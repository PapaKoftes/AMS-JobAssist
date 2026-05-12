"""End-to-end demo test — runs against a running server on port 8000."""
import json, urllib.request, urllib.error, sys, os, pathlib

BASE = "http://localhost:8000"

def post(path, payload, raw=False):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{BASE}{path}", data=data,
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read()
            return body if raw else json.loads(body.decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  HTTP {e.code}: {body}")
        return None

def get(path):
    with urllib.request.urlopen(f"{BASE}{path}") as r:
        return json.loads(r.read().decode("utf-8"))

# --- Health check ---
h = get("/health")
print(f"[health] {h}")

# --- Start session ---
r = post("/api/interview/start", {"user_id": "demo001", "interview_path": "unemployed", "language": "de"})
sid = r["data"]["session_id"]
print(f"[start]  session_id={sid}, q={r['data']['question_id']}")

# --- Submit answers (question IDs from actual path) ---
answers = [
    ("id_name",       "Hans Mueller"),
    ("id_location",   "Wien, Oesterreich"),
    ("id_target_job", "Lager und Logistik oder Produktion"),
    ("u_01",          "Ich habe drei Jahre im Lager gearbeitet, Waren sortiert und Gabelstapler bedient."),
    ("u_02",          "Davor habe ich in der Produktion gearbeitet und Maschinen bedient."),
    ("u_02_employer", "Fabrik AG"),
    ("u_02_title",    "Produktionsmitarbeiter"),
    ("u_02_dates",    "2016 bis 2019"),
    ("u_03",          "Ich habe immer puenktlich gearbeitet und bin sehr zuverlaessig."),
    ("u_04",          "Gabelstapler, Lagerverwaltung, Teamarbeit"),
    ("u_05",          "Hauptschulabschluss und Staplerschein"),
    ("u_06",          "Ich spreche Deutsch und etwas Englisch"),
    ("u_07",          "Ich bin flexibel und lerne schnell"),
]

for qid, text in answers:
    r = post("/api/interview/submit-answer", {"session_id": sid, "question_id": qid, "answer_text": text})
    if r:
        nd = r["data"]
        nq = nd.get("next_question", {})
        print(f"  [{qid}] -> next={nq.get('id','—')} complete={nd.get('interview_complete',False)}")
    else:
        print(f"  [{qid}] FAILED")

# --- Complete interview (builds CV) ---
print("\n[complete] Finalizing interview...")
r = post(f"/api/interview/complete/{sid}", {})
if r and r.get("status") == "success":
    print(f"  [OK] CV built: quality={r['data'].get('quality_score','?')} sections={r['data'].get('sections_count','?')}")
else:
    print(f"  [FAIL] {r}")

# --- Export PDF ---
print("\n[export] Requesting PDF...")
r = post("/api/export/pdf", {"session_id": sid, "language": "de", "force": True}, raw=True)
if r and r[:4] == b"%PDF":
    out_path = pathlib.Path("demo_output.pdf")
    out_path.write_bytes(r)
    print(f"  [OK] PDF written: {out_path} ({out_path.stat().st_size} bytes)")
elif r:
    print(f"  [FAIL] not a PDF — starts with: {r[:20]}")
else:
    print(f"  [FAIL] no response")

# --- Export DOCX ---
print("\n[export] Requesting DOCX...")
r = post("/api/export/docx", {"session_id": sid, "language": "de", "force": True}, raw=True)
if r and r[:2] == b"PK":
    out_path = pathlib.Path("demo_output.docx")
    out_path.write_bytes(r)
    print(f"  [OK] DOCX written: {out_path} ({out_path.stat().st_size} bytes)")
elif r:
    print(f"  [FAIL] not a DOCX — starts with: {r[:20]}")
else:
    print(f"  [FAIL] no response")

print("\n[done] Demo complete.")
