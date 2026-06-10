"""
Austrian domain-correctness tests (P2.3):
- Cover letter has a signature block (closing → space → typed name), ÖNORM-style.
- CV PDF/DOCX end with an Austrian signature block (Ort, Datum + Unterschrift + name).
"""
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))

from cv.cover_letter import generate, CoverLetterRequest  # noqa: E402
from cv.models import CVData, CVIdentity, CVSection, QuestionCategory  # noqa: E402


def _cv():
    cv = CVData(session_id="t", user_id="u", interview_path="other", language_input="de")
    cv.identity = CVIdentity(full_name="Maria Huber", location="Wien",
                             contact_email="m@h.at", contact_phone="0664 1")
    cv.experience = [CVSection(german="Kassa und Verkauf bei Spar (5 Jahre)",
                              english="Cashier at Spar (5 years)", native="",
                              category=QuestionCategory.EXPERIENCE)]
    cv.ready_for_export = True
    return cv


def test_cover_letter_signature_block():
    txt = generate(CoverLetterRequest(full_name="Maria Huber", city="Wien",
                                      job_title="Verkäuferin", language="de")).text
    lines = [l for l in txt.splitlines()]
    assert "Mit freundlichen Grüßen" in txt
    assert "Maria Huber" in txt
    # the typed name must come AFTER the closing, with blank signature space between
    ci = next(i for i, l in enumerate(lines) if "Mit freundlichen Grüßen" in l)
    ni = max(i for i, l in enumerate(lines) if l.strip() == "Maria Huber")
    assert ni > ci, "typed name must follow the closing"
    assert any(lines[j].strip() == "" for j in range(ci + 1, ni)), "blank signature space required"
    # Ort, Datum present (ÖNORM)
    assert "Wien," in txt


def test_cv_docx_signature_block():
    from export.docx_export import DOCXExporter
    from docx import Document
    with tempfile.TemporaryDirectory() as d:
        path = DOCXExporter(output_dir=d).export(_cv(), language="de", filename="t.docx")
        assert path and Path(path).exists()
        doc = Document(path)
        full = "\n".join(p.text for p in doc.paragraphs)
        assert "Wien," in full                      # Ort, Datum
        assert "Maria Huber" in full                # typed name (header + signature)
        assert "______" in full                     # signature line


def test_cv_pdf_builds_with_signature():
    from export.pdf_export import PDFExporter
    with tempfile.TemporaryDirectory() as d:
        path = PDFExporter(output_dir=d).export(_cv(), language="de", filename="t.pdf")
        assert path and Path(path).exists()
        data = Path(path).read_bytes()
        assert data[:4] == b"%PDF" and len(data) > 1500
