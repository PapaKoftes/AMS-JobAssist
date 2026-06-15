"""
PDF Exporter - Export CVData as Austrian Tabellarischer Lebenslauf (tabular CV).

Uses reportlab to generate clean, A4-formatted PDFs matching the Austrian
employment standard layout:
  - Header: name left / photo top-right in a two-column table
  - Contact line: location · phone · email · DOB · nationality
  - Sections: bold uppercase heading with horizontal rule, then two-column
    date | content layout for work/education entries
  - Font: Helvetica (built-in, full umlaut support via latin-1 subset)
  - Margins: 2 cm all sides
"""

import base64
import io
import logging
import tempfile
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

from xml.sax.saxutils import escape as _xml_escape

from cv.models import CVData, CVSection
from cv.language_levels import display_label as _level_display_label
from export.base import CVExporter

logger = logging.getLogger(__name__)


def _esc(value) -> str:
    """Escape user/AI text before it goes into a reportlab Paragraph.

    reportlab parses a mini-XML markup, so an unescaped '<' or '&' in a name/skill
    would corrupt the PDF (or fail the build → the user can't export their own CV)
    and could inject markup. We add our OWN <b>/<font> tags around escaped values.
    """
    return _xml_escape(str(value if value is not None else ""))


# ---------------------------------------------------------------------------
# Section-heading translations
# ---------------------------------------------------------------------------
_LABELS_DE = {
    "background": "AUSBILDUNG",
    "experience": "BERUFSERFAHRUNG",
    "skills":     "KENNTNISSE",
    "motivation": "MOTIVATION",
    "training":   "WEITERBILDUNG & ZERTIFIKATE",
    "projects":   "PROJEKTE",
    "languages":  "SPRACHEN",
    "all_skills": "KENNTNISSE",
}
_LABELS_EN = {
    "background": "EDUCATION",
    "experience": "PROFESSIONAL EXPERIENCE",
    "skills":     "SKILLS",
    "motivation": "MOTIVATION",
    "training":   "TRAINING & CERTIFICATIONS",
    "projects":   "PROJECTS",
    "languages":  "LANGUAGES",
    "all_skills": "ALL SKILLS",
}

# Language-level display labels live in cv.language_levels (single source of truth).

# Date column width (≈4 cm) / content column fills the rest
DATE_COL_WIDTH = 3.8 * cm


class PDFExporter(CVExporter):
    """Export CVData as Austrian Tabellarischer Lebenslauf PDF."""

    # --- Layout ---------------------------------------------------------
    PAGE_WIDTH, PAGE_HEIGHT = A4
    MARGIN = 2.0 * cm
    CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

    # --- Palette --------------------------------------------------------
    COLOR_NAME    = HexColor("#1a1a1a")
    COLOR_SECTION = HexColor("#1a1a1a")
    COLOR_TEXT    = HexColor("#333333")
    COLOR_MUTED   = HexColor("#666666")
    COLOR_RULE    = HexColor("#cccccc")
    COLOR_ACCENT  = HexColor("#2c3e50")

    # --- Photo dimensions (Austrian standard) ---------------------------
    PHOTO_W = 3.5 * cm
    PHOTO_H = 4.5 * cm

    # ====================================================================
    # Public API
    # ====================================================================

    def export(
        self,
        cv_data: CVData,
        language: str = "de",
        filename: Optional[str] = None,
    ) -> Optional[str]:
        """
        Export CVData as PDF.

        Returns path to the generated file, or None on failure.
        """
        try:
            logger.info(f"Exporting CVData as PDF (language={language})")

            if not self.validate_cv_data(cv_data):
                logger.error("CVData validation failed")
                return None

            content = self.get_cv_content_for_language(cv_data, language)
            if content is None:
                logger.error("Failed to extract CV content")
                return None

            pdf_filename = self.generate_filename(cv_data, language, "pdf", filename)
            pdf_path = self.output_dir / pdf_filename

            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=self.MARGIN,
                leftMargin=self.MARGIN,
                topMargin=self.MARGIN,
                bottomMargin=self.MARGIN,
                title=f"CV_{cv_data.user_id}",
                author="AMS JobAssist",
            )

            styles = self._make_styles()
            elements = self._build_elements(cv_data, content, language, styles)
            doc.build(elements)

            logger.info(f"PDF export successful: {pdf_path}")
            return str(pdf_path)

        except Exception as e:
            logger.error(f"PDF export error: {e}", exc_info=True)
            return None

    # ====================================================================
    # Element builders
    # ====================================================================

    def _build_elements(
        self,
        cv_data: CVData,
        content: Dict[str, Any],
        language: str,
        styles: Dict,
    ) -> list:
        """Assemble the full list of Platypus flowables."""
        elems = []

        # 1. Header (name + contact + photo)
        elems.append(self._build_header(cv_data, language, styles))
        elems.append(Spacer(1, 0.4 * cm))

        # 2. Work experience (grouped, two-column date|content layout)
        experience_sections = cv_data.experience
        if experience_sections:
            elems.append(self._section_heading("experience", language, styles))
            groups = self._group_experience_sections(experience_sections)
            for block in groups:
                elems.append(self._build_experience_block(block, language, styles))
                elems.append(Spacer(1, 0.25 * cm))

        # 3. Education / Background
        background_sections = cv_data.background
        if background_sections:
            elems.append(self._section_heading("background", language, styles))
            groups = self._group_experience_sections(background_sections)
            for block in groups:
                elems.append(self._build_experience_block(block, language, styles))
                elems.append(Spacer(1, 0.25 * cm))

        # 4. Training
        training_sections = cv_data.training
        if training_sections:
            elems.append(self._section_heading("training", language, styles))
            groups = self._group_experience_sections(training_sections)
            for block in groups:
                elems.append(self._build_experience_block(block, language, styles))
                elems.append(Spacer(1, 0.25 * cm))

        # 5. Skills / Kenntnisse
        all_skills = content.get("all_skills", [])
        skills_sections = cv_data.skills
        if all_skills or skills_sections:
            elems.append(self._section_heading("skills", language, styles))
            elems.append(self._build_skills_block(all_skills, skills_sections, language, styles))
            elems.append(Spacer(1, 0.25 * cm))

        # 6. Languages
        if cv_data.languages:
            elems.append(self._section_heading("languages", language, styles))
            elems.append(self._build_languages_block(cv_data.languages, language, styles))
            elems.append(Spacer(1, 0.25 * cm))

        # 7. Motivation / Projects (free text sections)
        for key in ("motivation", "projects"):
            section_list = getattr(cv_data, key, [])
            if section_list:
                elems.append(self._section_heading(key, language, styles))
                for s in section_list:
                    if s.hidden:
                        continue
                    text = s.german if language == "de" else s.english
                    if text:
                        elems.append(Paragraph(_esc(text), styles["normal"]))
                        elems.append(Spacer(1, 0.15 * cm))

        # 8. Austrian signature block (Ort, Datum + Unterschrift) — customary on AT CVs
        sig = self._build_signature_block(cv_data, language, styles)
        if sig:
            elems.append(Spacer(1, 0.7 * cm))
            elems.extend(sig)

        # 9. Footer
        elems.append(Spacer(1, 0.5 * cm))
        elems.append(self._build_footer(cv_data, language, styles))

        return elems

    # ------------------------------------------------------------------ #
    # Header                                                               #
    # ------------------------------------------------------------------ #

    def _build_header(self, cv_data: CVData, language: str, styles: Dict):
        """
        Build the Austrian CV header:
          left column: name (large), contact details, DOB, nationality
          right column: passport-style photo (3.5 × 4.5 cm)
        """
        identity = cv_data.identity

        display_name = (
            identity.full_name
            if identity and identity.full_name
            else cv_data.user_id
        )

        # ---- left: name + contact info --------------------------------
        left_elems = []

        # Full name — largest text on page
        left_elems.append(Paragraph(f"<b>{_esc(display_name)}</b>", styles["cv_name"]))
        left_elems.append(Spacer(1, 0.15 * cm))

        # Contact bullets
        if identity:
            contact_lines = []
            if identity.location:
                contact_lines.append(f"📍 {_esc(identity.location)}")
            if identity.contact_phone:
                contact_lines.append(f"📞 {_esc(identity.contact_phone)}")
            if identity.contact_email:
                contact_lines.append(f"✉ {_esc(identity.contact_email)}")
            if contact_lines:
                left_elems.append(
                    Paragraph("  ".join(contact_lines), styles["contact"])
                )

            # DOB + nationality on their own line
            extra = []
            if identity.date_of_birth:
                extra.append(f"📅 Geburtsdatum: {_esc(identity.date_of_birth)}")
            if identity.nationality:
                extra.append(f"🌍 Staatsangehörigkeit: {_esc(identity.nationality)}")
            if extra:
                left_elems.append(Spacer(1, 0.05 * cm))
                left_elems.append(Paragraph("  ".join(extra), styles["contact"]))

        # ---- right: photo (or empty cell) ----------------------------
        photo_element = self._build_photo_element(identity)

        # Photo column width + small gap
        photo_col_w = self.PHOTO_W + 0.3 * cm
        left_col_w  = self.CONTENT_WIDTH - photo_col_w

        header_table = Table(
            [[left_elems, photo_element]],
            colWidths=[left_col_w, photo_col_w],
            style=TableStyle([
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                ("ALIGN",        (1, 0), (1, 0),   "RIGHT"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ]),
        )

        return KeepTogether([
            header_table,
            Spacer(1, 0.2 * cm),
            HRFlowable(
                width=self.CONTENT_WIDTH,
                thickness=1.5,
                color=self.COLOR_ACCENT,
                spaceAfter=0,
            ),
        ])

    def _build_photo_element(self, identity):
        """
        Decode photo from base64 data URI or file path, return an Image flowable.
        Returns empty Spacer when no photo is available or decoding fails.
        """
        if identity is None or not identity.photo:
            return Spacer(self.PHOTO_W, self.PHOTO_H)

        try:
            photo_bytes = self._decode_photo(identity.photo)
            if not photo_bytes:
                return Spacer(self.PHOTO_W, self.PHOTO_H)

            from reportlab.platypus import Image as RLImage
            img_io = io.BytesIO(photo_bytes)
            img = RLImage(img_io, width=self.PHOTO_W, height=self.PHOTO_H)
            img.hAlign = "RIGHT"
            return img

        except Exception as exc:
            logger.warning(f"Could not load photo: {exc}")
            return Spacer(self.PHOTO_W, self.PHOTO_H)

    # ------------------------------------------------------------------ #
    # Section heading                                                       #
    # ------------------------------------------------------------------ #

    def _section_heading(self, key: str, language: str, styles: Dict):
        """Bold uppercase section heading with horizontal rule underneath."""
        label = (
            _LABELS_DE.get(key, key.upper())
            if language == "de"
            else _LABELS_EN.get(key, key.upper())
        )
        return KeepTogether([
            Spacer(1, 0.3 * cm),
            Paragraph(f"<b>{label}</b>", styles["section_heading"]),
            HRFlowable(
                width=self.CONTENT_WIDTH,
                thickness=0.75,
                color=self.COLOR_RULE,
                spaceAfter=4,
            ),
        ])

    # ------------------------------------------------------------------ #
    # Experience / Education blocks                                         #
    # ------------------------------------------------------------------ #

    def _group_experience_sections(
        self, sections: List[CVSection]
    ) -> List[Dict]:
        """
        Group CVSections by their base question_id.

        Sections whose question_id ends with ``_employer``, ``_title``, or
        ``_dates`` are attached to the main section (same base id).

        Returns a list of dicts:
            {
              "main":     CVSection | None,
              "employer": str | None,
              "title":    str | None,
              "dates":    str | None,
            }
        """
        groups: Dict[str, Dict] = {}
        order: List[str] = []   # preserve insertion order

        for s in sections:
            if s.hidden:
                continue
            qid = s.question_id or ""

            if qid.endswith("_employer"):
                base = qid[: -len("_employer")]
                groups.setdefault(base, {})["employer"] = s.german
                if base not in order:
                    order.append(base)
            elif qid.endswith("_title"):
                base = qid[: -len("_title")]
                groups.setdefault(base, {})["title"] = s.german
                if base not in order:
                    order.append(base)
            elif qid.endswith("_dates"):
                base = qid[: -len("_dates")]
                groups.setdefault(base, {})["dates"] = s.german
                if base not in order:
                    order.append(base)
            else:
                groups.setdefault(qid, {})["main"] = s
                if qid not in order:
                    order.append(qid)

        result = []
        for base in order:
            g = groups.get(base, {})
            main = g.get("main")
            # Prefer values folded onto the main section by the builder
            # (title / employer / period). Fall back to the legacy separate
            # _title / _employer / _dates sub-sections for older sessions.
            title = g.get("title") or (getattr(main, "title", "") if main else "")
            employer = g.get("employer") or (getattr(main, "employer", "") if main else "")
            dates = g.get("dates")
            if not dates and main and getattr(main, "period", None):
                dates = self._format_period(main.period)
            result.append({
                "main":     main,
                "employer": employer or None,
                "title":    title or None,
                "dates":    dates,
            })
        return result

    def _build_experience_block(
        self, block: Dict, language: str, styles: Dict
    ):
        """
        Render one work/education block as a two-column table:

            Jan 2020 –      Lagermitarbeiterin
            März 2022       Huber GmbH, Wien
                            • Übernahm Verantwortung …
                            • Koordinierte Wareneingang …
        """
        main: Optional[CVSection] = block.get("main")

        # --- Date string --------------------------------------------
        _dates_raw = block.get("dates")
        if _dates_raw is None:
            dates_str = ""
        elif hasattr(_dates_raw, "german"):
            # It's a CVSection — extract the text
            dates_str = _dates_raw.german or _dates_raw.english or ""
        else:
            dates_str = str(_dates_raw)
        if not dates_str and main and main.period:
            dates_str = self._format_period(main.period)
        dates_str = dates_str or "–"  # never pass None/empty to Paragraph

        # --- Title / employer line ----------------------------------
        _title_raw    = block.get("title")
        _employer_raw = block.get("employer")
        title_str    = (_title_raw.german    if hasattr(_title_raw,    "german") else str(_title_raw    or ""))
        employer_str = (_employer_raw.german if hasattr(_employer_raw, "german") else str(_employer_raw or ""))

        if not title_str and main:
            # Fall back: use the german text as the title line
            title_str = main.german or ""

        # --- Bullet points ------------------------------------------
        bullets: List[str] = []
        if main and main.bullets:
            bullets = main.bullets
        elif main and not title_str:
            # Nothing else set — show the raw text instead
            pass

        # Build right-column content
        right_paras = []
        if title_str:
            right_paras.append(Paragraph(f"<b>{_esc(title_str)}</b>", styles["entry_title"]))
        if employer_str:
            right_paras.append(Paragraph(_esc(employer_str), styles["entry_employer"]))
        for b in bullets:
            bullet_text = b if b.startswith("•") else f"• {b}"
            right_paras.append(Paragraph(_esc(bullet_text), styles["bullet"]))
        # If we have neither title nor bullets, render the main text as a paragraph
        if not right_paras and main:
            text = main.german if language == "de" else main.english
            if text:
                right_paras.append(Paragraph(_esc(text), styles["normal"]))

        if not right_paras:
            right_paras.append(Paragraph("", styles["normal"]))

        content_col = self.CONTENT_WIDTH - DATE_COL_WIDTH - 0.3 * cm

        tbl = Table(
            [[Paragraph(_esc(dates_str), styles["date_cell"]), right_paras]],
            colWidths=[DATE_COL_WIDTH, content_col],
            style=TableStyle([
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                ("ALIGN",        (0, 0), (0, -1),  "LEFT"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
            ]),
        )
        return tbl

    # ------------------------------------------------------------------ #
    # Skills block                                                          #
    # ------------------------------------------------------------------ #

    def _build_skills_block(
        self,
        all_skills: List[str],
        skills_sections: List[CVSection],
        language: str,
        styles: Dict,
    ):
        """
        Render skills as bullet list.

        Prefers ``all_skills`` (normalised, deduplicated).  Falls back to
        full section text when all_skills is empty.
        """
        lines = []
        if all_skills:
            for skill in all_skills:
                lines.append(Paragraph(f"• {_esc(skill)}", styles["bullet"]))
        else:
            for s in skills_sections:
                if s.hidden:
                    continue
                text = s.german if language == "de" else s.english
                if text:
                    lines.append(Paragraph(f"• {_esc(text)}", styles["bullet"]))

        if not lines:
            lines.append(Paragraph("–", styles["normal"]))

        # Wrap in a single-column table to maintain consistent left margin
        tbl = Table(
            [[lines]],
            colWidths=[self.CONTENT_WIDTH],
            style=TableStyle([
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ]),
        )
        return tbl

    # ------------------------------------------------------------------ #
    # Languages block                                                       #
    # ------------------------------------------------------------------ #

    def _build_languages_block(
        self,
        languages: List[Dict],
        language: str,
        styles: Dict,
    ):
        """
        Render language proficiencies as a two-column table:
            Deutsch        Muttersprache
            Türkisch       Arbeitsniveau (B2)
        """
        rows = []
        for lang_entry in languages:
            lang_name = lang_entry.get("language", "")
            level_label = _level_display_label(lang_entry.get("level", ""))
            rows.append([
                Paragraph(_esc(lang_name), styles["entry_title"]),
                Paragraph(_esc(level_label), styles["normal"]),
            ])

        if not rows:
            return Spacer(1, 0.1 * cm)

        col_w = self.CONTENT_WIDTH / 2
        tbl = Table(
            rows,
            colWidths=[col_w, col_w],
            style=TableStyle([
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
            ]),
        )
        return tbl

    # ------------------------------------------------------------------ #
    # Footer                                                               #
    # ------------------------------------------------------------------ #

    def _build_signature_block(self, cv_data: CVData, language: str, styles: Dict):
        """
        Austrian convention: a tabellarischer Lebenslauf ends with place + date
        and a signature (handwritten space above the typed name). Returns a list
        of flowables, or None if there's no name to sign with.
        """
        ident = getattr(cv_data, "identity", None)
        name = (getattr(ident, "full_name", "") or "").strip() if ident else ""
        if not name:
            return None
        city = (getattr(ident, "location", "") or "").strip() if ident else ""
        date_str = datetime.now().strftime("%d.%m.%Y")
        ort_datum = f"{city}, {date_str}" if city else date_str
        return [
            Paragraph(f"<font size='9'>{_esc(ort_datum)}</font>", styles["normal"]),
            Spacer(1, 1.0 * cm),  # blank space for the handwritten signature
            Paragraph("<font size='9'>______________________________</font>", styles["normal"]),
            Paragraph(f"<font size='9'>{_esc(name)}</font>", styles["normal"]),
        ]

    def _build_footer(self, cv_data: CVData, language: str, styles: Dict):
        date_str = datetime.now().strftime("%d.%m.%Y")
        quality_pct = f"{cv_data.overall_quality:.0%}"
        if language == "de":
            text = f"Lebenslauf erstellt: {date_str} | Qualität: {quality_pct} | AMS JobAssist"
        else:
            text = f"CV generated: {date_str} | Quality: {quality_pct} | AMS JobAssist"
        return Paragraph(
            f"<font size='7' color='#999999'>{text}</font>",
            styles["normal"],
        )

    # ====================================================================
    # Helpers
    # ====================================================================

    def _decode_photo(self, photo_str: str) -> Optional[bytes]:
        """
        Decode a photo from either:
          • A base64 data URI  – ``data:image/jpeg;base64,/9j/4AAQ...``
          • A filesystem path  – ``/path/to/photo.jpg``

        Returns raw image bytes, or None on failure.
        """
        if not photo_str:
            return None

        if photo_str.startswith("data:"):
            # Base64 data URI
            try:
                _header, b64data = photo_str.split(",", 1)
                return base64.b64decode(b64data)
            except Exception as exc:
                logger.warning(f"Base64 decode failed: {exc}")
                return None

        # Filesystem path
        path = Path(photo_str)
        if path.exists():
            return path.read_bytes()

        logger.warning(f"Photo path not found: {photo_str}")
        return None

    def _format_period(self, period: Optional[Dict]) -> str:
        """
        Format a period dict to a human-readable date range string.
        e.g. {"start": "2020-01", "end": "2023-03"} → "Jan 2020 – Mär 2023"
        """
        if not period:
            return ""
        start = self._format_month(period.get("start"))
        end   = self._format_month(period.get("end"))
        if start and end:
            return f"{start} –\n{end}"
        if start:
            return f"{start} –\nheute"
        return ""

    @staticmethod
    def _format_month(ym: Optional[str]) -> str:
        """
        Format "YYYY-MM" → "MMM YYYY" using short German month names.
        Passes through plain years or free-text unchanged.
        """
        if not ym:
            return ""
        _month_names = [
            "", "Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
            "Jul", "Aug", "Sep", "Okt", "Nov", "Dez",
        ]
        parts = ym.split("-")
        if len(parts) == 2:
            try:
                year  = int(parts[0])
                month = int(parts[1])
                if 1 <= month <= 12:
                    return f"{_month_names[month]} {year}"
            except ValueError:
                pass
        return ym

    # ====================================================================
    # Paragraph styles
    # ====================================================================

    def _make_styles(self) -> Dict:
        """Build and return all custom Platypus ParagraphStyles."""
        base = getSampleStyleSheet()

        def _ps(name, parent="BodyText", **kwargs):
            return ParagraphStyle(name=name, parent=base[parent], **kwargs)

        return {
            "cv_name": _ps(
                "cv_name",
                parent="Heading1",
                fontName="Helvetica-Bold",
                fontSize=20,
                leading=24,
                textColor=self.COLOR_NAME,
                spaceAfter=2,
                spaceBefore=0,
            ),
            "contact": _ps(
                "contact",
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=self.COLOR_MUTED,
                spaceAfter=2,
            ),
            "section_heading": _ps(
                "section_heading",
                parent="Heading2",
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=14,
                textColor=self.COLOR_SECTION,
                spaceAfter=2,
                spaceBefore=0,
                leftIndent=0,
            ),
            "date_cell": _ps(
                "date_cell",
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=self.COLOR_MUTED,
                spaceAfter=0,
            ),
            "entry_title": _ps(
                "entry_title",
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=self.COLOR_TEXT,
                spaceAfter=1,
            ),
            "entry_employer": _ps(
                "entry_employer",
                fontName="Helvetica-Oblique",
                fontSize=9,
                leading=12,
                textColor=self.COLOR_MUTED,
                spaceAfter=2,
            ),
            "bullet": _ps(
                "bullet",
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=self.COLOR_TEXT,
                leftIndent=6,
                spaceAfter=1,
            ),
            "normal": _ps(
                "normal",
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=self.COLOR_TEXT,
                spaceAfter=3,
            ),
        }


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from cv.models import CVData, CVSection, CVIdentity, QuestionCategory

    cv = CVData(
        session_id="1",
        user_id="test_user",
        interview_path="unemployed",
        language_input="de",
        language_output_primary="de",
        language_output_secondary="en",
    )

    cv.identity = CVIdentity(
        full_name="Ayşe Yılmaz",
        date_of_birth="15.03.1990",
        nationality="Türkisch",
        location="Wien, Österreich",
        contact_email="ayse@example.com",
        contact_phone="+43 676 1234567",
    )

    exp = CVSection(
        german="Lagermitarbeiterin",
        english="Warehouse Worker",
        native="Lagermitarbeiterin",
        category=QuestionCategory.EXPERIENCE,
        question_id="exp_001",
        detected_input_language="de",
        user_native_language="tr",
        quality_score=0.85,
        confidence_level="high",
        detected_skills=["Lagerlogistik"],
        period={"start": "2020-01", "end": "2022-03"},
        bullets=[
            "Übernahm Verantwortung für Lagerlogistik",
            "Koordinierte Wareneingang und -ausgang",
        ],
    )
    cv.experience.append(exp)

    employer_sec = CVSection(
        german="Huber GmbH, Wien",
        english="Huber GmbH, Vienna",
        native="Huber GmbH, Wien",
        category=QuestionCategory.EXPERIENCE,
        question_id="exp_001_employer",
        detected_input_language="de",
        user_native_language="tr",
        quality_score=1.0,
        confidence_level="high",
        detected_skills=[],
    )
    cv.experience.append(employer_sec)

    cv.all_skills = ["Microsoft Office (Word, Excel, Outlook)", "Führerschein Klasse B"]
    cv.languages = [
        {"language": "Deutsch", "code": "de", "level": "b2"},
        {"language": "Türkisch", "code": "tr", "level": "native"},
        {"language": "Englisch", "code": "en", "level": "a2"},
    ]
    cv.overall_quality = 0.85
    cv.ready_for_export = True

    exporter = PDFExporter()
    path = exporter.export(cv, language="de", filename="test_austrian_cv")
    print(f"Exported to: {path}")
