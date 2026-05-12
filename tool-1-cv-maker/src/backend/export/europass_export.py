"""
Europass XML Exporter — minimal Europass-compatible CV XML.

Generates a simplified Europass XML document following the Europass CV
data model structure. Not a full schema-validated Europass XML but
contains all required fields for import by Europass-compatible systems.
"""

from __future__ import annotations
import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Optional
from pathlib import Path
from datetime import datetime

from cv.models import CVData
from export.base import CVExporter

logger = logging.getLogger(__name__)


class EuropassExporter(CVExporter):
    """Export CVData as Europass-compatible XML."""

    def export(
        self,
        cv_data: CVData,
        language: str = "de",
        filename: Optional[str] = None
    ) -> Optional[str]:
        try:
            logger.info(f"Exporting CVData as Europass XML (language: {language})")
            if not self.validate_cv_data(cv_data):
                return None

            xml_filename = self.generate_filename(cv_data, language, "xml", filename)
            xml_path = self.output_dir / xml_filename

            root = self._build_xml(cv_data, language)
            xml_str = self._pretty_print(root)
            xml_path.write_text(xml_str, encoding="utf-8")

            logger.info(f"Europass XML export successful: {xml_path}")
            return str(xml_path)
        except Exception as e:
            logger.error(f"Europass XML export failed: {e}")
            return None

    def _build_xml(self, cv_data: CVData, language: str) -> ET.Element:
        root = ET.Element("EuropassCV", {
            "xmlns": "http://europass.cedefop.europa.eu/Europass/V3.0",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://europass.cedefop.europa.eu/Europass/V3.0",
            "locale": language,
        })

        # Print section
        ps = ET.SubElement(root, "PrintingPreferences")
        ET.SubElement(ps, "document", {"type": "ECV"})

        # Learner info
        li = ET.SubElement(root, "LearnerInfo")

        # Identification
        ident = ET.SubElement(li, "Identification")
        name_el = ET.SubElement(ident, "PersonName")
        identity = cv_data.identity
        if identity:
            full = identity.full_name or cv_data.user_id
            parts = full.strip().split(None, 1)
            ET.SubElement(name_el, "FirstName").text = parts[0] if parts else full
            if len(parts) > 1:
                ET.SubElement(name_el, "Surname").text = parts[1]
            # Contact
            if identity.contact_email or identity.contact_phone or identity.location:
                contact = ET.SubElement(ident, "ContactInfo")
                if identity.contact_email:
                    email_el = ET.SubElement(contact, "Email")
                    ET.SubElement(email_el, "Contact").text = identity.contact_email
                if identity.contact_phone:
                    phone_el = ET.SubElement(contact, "Telephone")
                    ET.SubElement(phone_el, "Contact").text = identity.contact_phone
                if identity.location:
                    addr = ET.SubElement(contact, "Address")
                    ET.SubElement(addr, "Municipality").text = identity.location
        else:
            ET.SubElement(name_el, "FirstName").text = cv_data.user_id

        # Headline (interview path)
        hl = ET.SubElement(li, "Headline")
        ET.SubElement(hl, "Description").text = cv_data.interview_path.replace("-", " ").title()

        # Work experience
        if cv_data.experience:
            we = ET.SubElement(li, "WorkExperience")
            for i, section in enumerate(cv_data.experience):
                text = (section.german if language == "de" else section.english) or ""
                exp = ET.SubElement(we, "Experience", {"order": str(i + 1)})
                pd = ET.SubElement(exp, "Period")
                ET.SubElement(pd, "From").text = ""
                act = ET.SubElement(exp, "Activities")
                ET.SubElement(act, "Description").text = text

        # Education
        edu_sections = cv_data.background + cv_data.training
        if edu_sections:
            ed = ET.SubElement(li, "Education")
            for i, section in enumerate(edu_sections):
                text = (section.german if language == "de" else section.english) or ""
                edexp = ET.SubElement(ed, "EducationalExperience", {"order": str(i + 1)})
                pd = ET.SubElement(edexp, "Period")
                ET.SubElement(pd, "From").text = ""
                desc = ET.SubElement(edexp, "Description")
                ET.SubElement(desc, "Label").text = text

        # Skills
        if cv_data.all_skills:
            skills_el = ET.SubElement(li, "Skills")
            other = ET.SubElement(skills_el, "OtherSkills")
            for skill in cv_data.all_skills:
                sk = ET.SubElement(other, "Skill")
                ET.SubElement(sk, "Description").text = skill

        # Motivation / cover letter snippet
        if cv_data.motivation:
            for section in cv_data.motivation[:1]:
                text = (section.german if language == "de" else section.english) or ""
                if text:
                    cover = ET.SubElement(li, "CoverLetter")
                    ET.SubElement(cover, "Text").text = text

        return root

    def _pretty_print(self, root: ET.Element) -> str:
        raw = ET.tostring(root, encoding="unicode", xml_declaration=False)
        dom = minidom.parseString(raw)
        pretty = dom.toprettyxml(indent="  ", encoding=None)
        # Remove the auto-inserted <?xml version ...?> line minidom adds
        lines = pretty.split("\n")
        if lines and lines[0].startswith("<?xml"):
            lines = lines[1:]
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(lines)
