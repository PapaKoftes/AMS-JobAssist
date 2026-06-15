"""
Tests for PDF Export functionality (Day 10 Phase 10.2 continuation).

Tests the PDFExporter class that:
- Exports CVData as PDF files
- Exports in multiple languages
- Validates CVData before export
- Generates professional formatted PDFs
- Handles edge cases and errors
"""

import pytest
from pathlib import Path
from src.backend.export.pdf_export import PDFExporter
from src.backend.cv.models import CVData, CVSection, QuestionCategory
import tempfile
import shutil


class TestPDFExporter:
    """Test PDF export functionality."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory for exports."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def exporter(self, temp_output_dir):
        """Provide PDFExporter with temporary output directory."""
        return PDFExporter(output_dir=temp_output_dir)

    @pytest.fixture
    def sample_cv_data(self):
        """Provide sample CVData with sections."""
        cv_data = CVData(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en"
        )
        cv_data.language_output_primary = "de"
        cv_data.language_output_secondary = "en"

        # Add background section
        bg = CVSection(
            german="Ich bin ein Software-Ingenieur mit 5 Jahren Erfahrung.",
            english="I am a software engineer with 5 years of experience.",
            native="I am a software engineer with 5 years of experience.",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.85,
            confidence_level="high",
            detected_skills=["Software Engineering"]
        )
        cv_data.background.append(bg)

        # Add experience section
        exp = CVSection(
            german="Ich leitete ein Team von fünf Entwicklern.",
            english="I led a team of five developers.",
            native="I led a team of five developers.",
            category=QuestionCategory.EXPERIENCE,
            question_id="exp_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.80,
            confidence_level="high",
            detected_skills=["Leadership"]
        )
        cv_data.experience.append(exp)

        # Add skills section
        skills = CVSection(
            german="Ich beherrsche Python, SQL und MySQL.",
            english="I master Python, SQL and MySQL.",
            native="I master Python, SQL and MySQL.",
            category=QuestionCategory.SKILLS,
            question_id="skills_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.90,
            confidence_level="high",
            detected_skills=["Python", "SQL", "MySQL"]
        )
        cv_data.skills.append(skills)

        # Set all skills and quality
        cv_data.all_skills = ["Python", "SQL", "MySQL", "Leadership", "Software Engineering"]
        quality_scores = [bg.quality_score, exp.quality_score, skills.quality_score]
        cv_data.overall_quality = sum(quality_scores) / len(quality_scores)
        cv_data.ready_for_export = cv_data.overall_quality >= 0.5

        return cv_data

    def test_export_pdf_creates_file(self, exporter, sample_cv_data):
        """Test that export creates a PDF file."""
        result = exporter.export(sample_cv_data, language="de")

        assert result is not None
        assert Path(result).exists()
        assert result.endswith(".pdf")

    def test_export_pdf_file_has_content(self, exporter, sample_cv_data):
        """Test that exported PDF file has content."""
        result = exporter.export(sample_cv_data, language="de")

        # Check file size (PDF should have content)
        file_size = Path(result).stat().st_size
        assert file_size > 1000  # Minimum expected size for a PDF

    def test_export_pdf_german_content(self, exporter, sample_cv_data):
        """Test that German export creates valid PDF."""
        result = exporter.export(sample_cv_data, language="de")

        assert result is not None
        assert Path(result).exists()
        # File should be readable and valid
        with open(result, "rb") as f:
            content = f.read()
            # PDF files start with %PDF
            assert content.startswith(b'%PDF')

    def test_export_pdf_english_content(self, exporter, sample_cv_data):
        """Test that English export creates valid PDF."""
        result = exporter.export(sample_cv_data, language="en")

        assert result is not None
        assert Path(result).exists()
        # Verify it's a valid PDF
        with open(result, "rb") as f:
            content = f.read()
            assert content.startswith(b'%PDF')

    def test_export_pdf_with_custom_filename(self, exporter, sample_cv_data):
        """Test export with custom filename."""
        result = exporter.export(sample_cv_data, language="de", filename="my_cv")

        assert "my_cv" in result
        assert Path(result).exists()
        assert result.endswith(".pdf")

    def test_export_pdf_validates_cv_data(self, exporter):
        """Test that export validates CVData before exporting."""
        # Create invalid CVData (no sections)
        invalid_cv = CVData(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en"
        )

        result = exporter.export(invalid_cv, language="de")

        # Should fail validation
        assert result is None

    def test_export_multiple_sections_same_category(self, exporter, sample_cv_data):
        """Test export with multiple sections in same category."""
        exp2 = CVSection(
            german="Ich entwickelte eine mobile Anwendung.",
            english="I developed a mobile application.",
            native="I developed a mobile application.",
            category=QuestionCategory.EXPERIENCE,
            question_id="exp_002",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.75,
            confidence_level="high",
            detected_skills=["Mobile Development"]
        )
        sample_cv_data.experience.append(exp2)

        result = exporter.export(sample_cv_data, language="de")

        assert result is not None
        assert Path(result).exists()
        file_size = Path(result).stat().st_size
        assert file_size > 1000

    def test_export_with_empty_sections(self, exporter):
        """Test export with some empty category lists."""
        cv = CVData(
            session_id=1,
            user_id="test",
            interview_path="unemployed",
            language_input="en"
        )
        cv.language_output_primary = "de"
        cv.language_output_secondary = "en"

        # Only add background, leave others empty
        bg = CVSection(
            german="Hintergrund Info",
            english="Background info",
            native="Background info",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.70,
            confidence_level="high",
            detected_skills=[]
        )
        cv.background.append(bg)
        cv.all_skills = []
        cv.overall_quality = 0.70
        cv.ready_for_export = True

        result = exporter.export(cv, language="de")

        assert result is not None
        assert Path(result).exists()

    def test_filename_generation_for_pdf(self, exporter, sample_cv_data):
        """Test PDF-specific filename generation."""
        filename = exporter.generate_filename(sample_cv_data, "de", "pdf")

        # Should contain user_id, interview_path, and language
        assert "test_user" in filename
        assert "unemployed" in filename
        assert "de" in filename
        assert filename.endswith(".pdf")

    def test_export_different_languages_creates_different_files(self, exporter, sample_cv_data):
        """Test that exporting in different languages creates different files."""
        result_de = exporter.export(sample_cv_data, language="de")
        result_en = exporter.export(sample_cv_data, language="en")

        assert result_de is not None
        assert result_en is not None
        assert result_de != result_en  # Different file paths
        assert Path(result_de).exists()
        assert Path(result_en).exists()

    def test_export_pdf_with_long_text(self, exporter):
        """Test export with long text sections."""
        cv = CVData(
            session_id=1,
            user_id="test_long",
            interview_path="unemployed",
            language_input="en"
        )
        cv.language_output_primary = "de"
        cv.language_output_secondary = "en"

        # Add section with long text
        long_text = "I have extensive experience in software development. " * 10
        section = CVSection(
            german=long_text,
            english=long_text,
            native=long_text,
            category=QuestionCategory.EXPERIENCE,
            question_id="exp_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.80,
            confidence_level="high",
            detected_skills=["Python"]
        )
        cv.experience.append(section)
        cv.all_skills = ["Python"]
        cv.overall_quality = 0.80
        cv.ready_for_export = True

        result = exporter.export(cv, language="en")

        assert result is not None
        assert Path(result).exists()
        file_size = Path(result).stat().st_size
        assert file_size > 1000

    def test_export_pdf_with_special_characters(self, exporter):
        """Test export with special characters and umlauts."""
        cv = CVData(
            session_id=1,
            user_id="test_special",
            interview_path="unemployed",
            language_input="en"
        )
        cv.language_output_primary = "de"
        cv.language_output_secondary = "en"

        # Add section with German umlauts
        section = CVSection(
            german="Ich beherrsche Programmierung, Öffentlichkeitsarbeit und ähnliches.",
            english="I master programming, public relations and similar.",
            native="I master programming, public relations and similar.",
            category=QuestionCategory.SKILLS,
            question_id="skills_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.85,
            confidence_level="high",
            detected_skills=["Programmierung", "Öffentlichkeitsarbeit"]
        )
        cv.skills.append(section)
        cv.all_skills = ["Programmierung", "Öffentlichkeitsarbeit"]
        cv.overall_quality = 0.85
        cv.ready_for_export = True

        result = exporter.export(cv, language="de")

        assert result is not None
        assert Path(result).exists()

    def test_pdf_export_creates_valid_format(self, exporter, sample_cv_data):
        """Test that exported PDF is in valid PDF format."""
        result = exporter.export(sample_cv_data, language="de")

        with open(result, "rb") as f:
            # Read PDF header
            header = f.read(4)
            assert header == b'%PDF'

            # Read end marker (should be near the end)
            f.seek(-20, 2)  # Seek to 20 bytes before end
            end_content = f.read()
            assert b'%%EOF' in end_content or b'endstream' in end_content


class TestPDFMarkupSafety:
    """S2: user text must be XML-escaped before reportlab Paragraph (no injection,
    no self-DoS when a name/skill contains '<' or '&')."""

    def test_angle_brackets_in_fields_do_not_crash_and_are_escaped(self, tmp_path):
        from src.backend.export.pdf_export import PDFExporter, _esc
        from src.backend.cv.models import CVIdentity
        assert _esc("a<b>c & d") == "a&lt;b&gt;c &amp; d"  # _esc neutralises markup

        cv = CVData(session_id=1, user_id="u", interview_path="unemployed", language_input="de")
        cv.language_output_primary = "de"
        cv.identity = CVIdentity(full_name="</b><font color='red'>Eve",
                                 location="Wien <script>", contact_email="e&v@x.at")
        cv.experience.append(CVSection(
            german="Leitete <b>Team</b> & mehr", english="", native="",
            category=QuestionCategory.EXPERIENCE, question_id="e1",
            quality_score=0.8, confidence_level="high", detected_skills=["C<>++"]))
        cv.all_skills = ["C<>++", "Excel & Word"]

        exporter = PDFExporter(output_dir=str(tmp_path))
        path = exporter.export(cv, language="de")  # must NOT raise on the markup
        assert path and Path(path).exists()
        with open(path, "rb") as f:
            assert f.read(4) == b"%PDF"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
