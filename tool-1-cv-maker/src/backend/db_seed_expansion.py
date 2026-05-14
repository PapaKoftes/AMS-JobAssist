"""
Database Seed Expansion for AMS JobAssist CV Maker.

Adds ~80 German CV verbs, ~50 English CV verbs, ~100+ multilingual skills,
and an AMS-specific ATS keyword bank.

Can be imported by db.py or run standalone:
    python db_seed_expansion.py            # applies to default DB
    python db_seed_expansion.py path/to.db # applies to specific DB

Idempotent: uses INSERT OR IGNORE so it is safe to run multiple times.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db import DatabaseManager

logger = logging.getLogger(__name__)


# ============================================================================
# 1. English CV Verbs  (~50 new weak -> strong mappings)
# ============================================================================

def get_expanded_verbs_en() -> list[tuple[str, str]]:
    """Return (weak_verb, strong_verb) pairs for English.

    Covers phrases real job seekers use when describing work experience
    informally, mapped to professional CV action verbs.
    """
    return [
        # Responsibility / leadership
        ("was responsible for", "managed"),
        ("was in charge of", "directed"),
        ("was in charge", "directed"),
        ("looked after", "supervised"),
        ("oversaw", "administered"),
        ("took over", "assumed responsibility for"),
        ("was the lead", "spearheaded"),
        ("kept track of", "monitored"),
        ("made sure", "ensured"),
        ("was given", "was entrusted with"),
        # Communication
        ("talked to", "communicated with"),
        ("spoke with", "liaised with"),
        ("told", "informed"),
        ("explained", "articulated"),
        ("presented to", "delivered presentations to"),
        ("wrote", "authored"),
        ("emailed", "corresponded with"),
        ("answered phones", "handled inbound communications"),
        # Problem solving / analysis
        ("figured out", "determined"),
        ("found out", "identified"),
        ("looked into", "investigated"),
        ("thought of", "devised"),
        ("came up with", "developed"),
        ("worked out", "resolved"),
        ("dealt with", "addressed"),
        ("sorted out", "rectified"),
        # Task execution
        ("put together", "assembled"),
        ("started", "initiated"),
        ("finished", "completed"),
        ("carried out", "executed"),
        ("did the work", "performed"),
        ("took part in", "participated in"),
        ("was involved in", "contributed to"),
        ("filled in", "substituted"),
        ("covered for", "deputised for"),
        # Sales / customer
        ("sold", "generated sales of"),
        ("served", "attended to"),
        ("dealt with customers", "provided customer service"),
        ("took orders", "processed orders"),
        ("rang up", "processed transactions"),
        # Training / learning
        ("learned", "acquired proficiency in"),
        ("taught", "trained"),
        ("showed someone", "mentored"),
        ("got trained in", "completed training in"),
        ("picked up", "developed competence in"),
        # Operations / logistics
        ("packed", "prepared shipments"),
        ("delivered", "distributed"),
        ("moved", "transported"),
        ("cleaned", "maintained"),
        ("stocked", "replenished inventory"),
        ("counted", "conducted inventory"),
    ]


# ============================================================================
# 2. German CV Verbs  (~80 new weak -> strong mappings)
# ============================================================================

def get_expanded_verbs_de() -> list[tuple[str, str]]:
    """Return (weak_verb, strong_verb) pairs for German.

    Organised by domain: basic speech, work actions, management, customer,
    technical, office, social/care, and Austrian-specific terms.
    """
    return [
        # ── Grundlegende Ausdrucksweise (Basic speech) ─────────────────────
        ("gesagt", "kommuniziert"),
        ("erzählt", "vermittelt"),
        ("geredet mit", "beraten"),
        ("gesprochen", "verhandelt"),
        ("angerufen", "kontaktiert"),
        ("geschickt", "übermittelt"),
        ("zugehört", "aktiv zugehört"),
        ("gefragt", "erfragt"),
        ("geantwortet", "Stellung genommen"),
        ("beschrieben", "erläutert"),

        # ── Arbeitshandlungen (Work actions) ───────────────────────────────
        ("gearbeitet an", "mitgewirkt an"),
        ("gearbeitet als", "tätig gewesen als"),
        ("angefangen", "initiiert"),
        ("aufgehört", "abgeschlossen"),
        ("weitergemacht", "fortgeführt"),
        ("ausprobiert", "erprobt"),
        ("fertiggemacht", "fertiggestellt"),
        ("hergestellt", "produziert"),
        ("zusammengebaut", "montiert"),
        ("ausgeführt", "realisiert"),
        ("zuständig gewesen", "verantwortlich gezeichnet"),
        ("geschafft", "bewältigt"),

        # ── Management / Führung ───────────────────────────────────────────
        ("aufgepasst", "überwacht"),
        ("bestimmt", "festgelegt"),
        ("entschieden", "beschlossen"),
        ("aufgeteilt", "zugeteilt"),
        ("eingeteilt", "disponiert"),
        ("zugewiesen", "delegiert"),
        ("vorgegeben", "definiert"),
        ("organisiert", "koordiniert"),
        ("angeleitet", "instruiert"),
        ("eingestellt", "rekrutiert"),
        ("eingearbeitet", "eingeschult"),
        ("beurteilt", "evaluiert"),

        # ── Kunden / Verkauf (Customer / sales) ───────────────────────────
        ("geredet", "beraten"),
        ("gezeigt", "präsentiert"),
        ("angeboten", "offeriert"),
        ("beraten", "fachlich beraten"),
        ("empfohlen", "empfohlen und vermittelt"),
        ("kassiert", "abgerechnet"),
        ("Kunden betreut", "Kundenbeziehungen gepflegt"),
        ("bedient", "serviciert"),
        ("reklamiert", "reklamationsbearbeitet"),
        ("telefoniert", "telefonische Beratung durchgeführt"),

        # ── Technik / Handwerk (Technical / trades) ───────────────────────
        ("repariert", "instand gesetzt"),
        ("gebaut", "konstruiert"),
        ("installiert", "in Betrieb genommen"),
        ("gewartet", "gewartet und instand gehalten"),
        ("eingebaut", "verbaut"),
        ("abgebaut", "demontiert"),
        ("verdrahtet", "verkabelt"),
        ("geschweißt", "Schweißarbeiten durchgeführt"),
        ("gebohrt", "Bohrarbeiten ausgeführt"),
        ("geschraubt", "Montagearbeiten durchgeführt"),
        ("lackiert", "Oberflächen behandelt"),
        ("gereinigt", "Reinigungsarbeiten durchgeführt"),

        # ── Büro / Verwaltung (Office / administration) ────────────────────
        ("geschrieben", "verfasst"),
        ("gelesen", "ausgewertet"),
        ("abgelegt", "archiviert"),
        ("kopiert", "vervielfältigt"),
        ("eingegeben", "erfasst"),
        ("sortiert", "systematisiert"),
        ("bestellt", "disponiert"),
        ("abgerechnet", "fakturiert"),
        ("gebucht", "verbucht"),
        ("ausgedruckt", "dokumentiert"),
        ("eingetragen", "protokolliert"),

        # ── Soziales / Pflege (Social / care) ─────────────────────────────
        ("geholfen", "unterstützt"),
        ("betreut", "begleitet"),
        ("gepflegt", "pflegerisch versorgt"),
        ("aufgepasst auf", "beaufsichtigt"),
        ("gekümmert um", "betreut und versorgt"),
        ("gefüttert", "Mahlzeiten verabreicht"),
        ("gewaschen", "Körperpflege durchgeführt"),
        ("nur zugehört", "einfühlsam begleitet"),
        ("getröstet", "psychosozial unterstützt"),

        # ── Logistik / Lager (Logistics / warehouse) ─────────────────────
        ("getragen", "transportiert"),
        ("eingeräumt", "kommissioniert"),
        ("ausgeräumt", "entladen"),
        ("verpackt", "versandfertig verpackt"),
        ("gezählt", "inventarisiert"),
        ("geliefert", "ausgeliefert und zugestellt"),
        ("gefahren", "Waren transportiert"),
        ("aufgeladen", "be- und entladen"),

        # ── Österreich-spezifisch (Austrian terms) ────────────────────────
        ("g'macht", "umgesetzt"),
        ("g'holfen", "unterstützt"),
        ("g'schrieben", "verfasst"),
        ("g'redet", "kommuniziert"),
        ("g'arbeitet", "mitgewirkt"),
        ("ausg'liefert", "zugestellt"),
        ("aufg'räumt", "Ordnung hergestellt"),
        ("z'amm g'arbeitet", "kollegial zusammengearbeitet"),
    ]


# ============================================================================
# 3. Expanded Skills (multilingual)
# ============================================================================

def get_expanded_skills() -> list[tuple[str, str, str, str]]:
    """Return (key_term, normalized_skill, category, language) tuples.

    Covers German, English, Turkish, Arabic, Bosnian/Serbian/Croatian,
    Polish, Ukrainian, Russian, and Romanian terms -- the most common
    native languages among Austrian AMS participants.
    """
    return [
        # ================================================================
        # German (de) -- additional terms
        # ================================================================
        # Retail / Gastronomy
        ("kassensystem", "Kassensystem-Bedienung", "Retail", "de"),
        ("registrierkasse", "Registrierkasse", "Retail", "de"),
        ("warenpräsentation", "Warenpräsentation", "Retail", "de"),
        ("verkauf", "Verkauf & Vertrieb", "Retail", "de"),
        ("verkaufserfahrung", "Verkaufserfahrung", "Retail", "de"),
        ("einzelhandel", "Einzelhandelserfahrung", "Retail", "de"),
        ("bestellungen", "Bestellwesen", "Logistics", "de"),
        ("gastronomie", "Gastronomie-Erfahrung", "Gastronomy", "de"),
        ("barista", "Barista-Kenntnisse", "Gastronomy", "de"),
        ("catering", "Catering & Eventservice", "Gastronomy", "de"),
        ("reinigung", "Professionelle Reinigung", "Cleaning", "de"),
        ("hauswirtschaft", "Hauswirtschaft", "Cleaning", "de"),
        ("gebäudereinigung", "Gebäudereinigung", "Cleaning", "de"),
        # Finance / Admin
        ("buchhaltung", "Buchhaltung", "Finance", "de"),
        ("rechnungswesen", "Rechnungswesen", "Finance", "de"),
        ("lohnverrechnung", "Lohnverrechnung", "Finance", "de"),
        ("personalverrechnung", "Personalverrechnung", "Finance", "de"),
        ("bmd", "BMD Buchhaltungssoftware", "ERP", "de"),
        ("datev", "DATEV", "ERP", "de"),
        ("bmd ntcs", "BMD NTCS", "ERP", "de"),
        ("sap business one", "SAP Business One", "ERP", "de"),
        ("registrierkassenpflicht", "Registrierkassenpflicht (RKSV)", "Compliance", "de"),
        # Technical / trades
        ("schweißen", "Schweißtechnik", "Technical", "de"),
        ("schweißzertifikat", "Schweißzertifikat nach EN ISO", "Qualification", "de"),
        ("cnc", "CNC-Bearbeitung", "Technical", "de"),
        ("cnc-fräsen", "CNC-Fräsen", "Technical", "de"),
        ("cnc-drehen", "CNC-Drehen", "Technical", "de"),
        ("metalltechnik", "Metalltechnik", "Technical", "de"),
        ("elektrotechnik", "Elektrotechnik", "Technical", "de"),
        ("installationstechnik", "Installationstechnik (Gas/Wasser/Heizung)", "Technical", "de"),
        ("kfz", "KFZ-Technik", "Technical", "de"),
        ("kfz-mechaniker", "KFZ-Mechanik", "Technical", "de"),
        ("tischler", "Tischlerei", "Technical", "de"),
        ("malerei", "Malerei & Anstrich", "Technical", "de"),
        ("friseur", "Friseur & Haarpflege", "Technical", "de"),
        ("bau", "Bau & Baunebengewerbe", "Technical", "de"),
        ("maurer", "Maurerarbeiten", "Technical", "de"),
        ("fliesenleger", "Fliesenverlegung", "Technical", "de"),
        ("produktion", "Produktionserfahrung", "Technical", "de"),
        ("maschinenführung", "Maschinenführung", "Technical", "de"),
        # Logistics / Transport
        ("staplerschein", "Staplerschein", "Qualification", "de"),
        ("b-führerschein", "Führerschein Klasse B", "Qualification", "de"),
        ("c-führerschein", "Führerschein Klasse C (LKW)", "Qualification", "de"),
        ("d-führerschein", "Führerschein Klasse D (Bus)", "Qualification", "de"),
        ("adr-schein", "ADR-Gefahrgutschein", "Qualification", "de"),
        ("kommissionierung", "Kommissionierung", "Logistics", "de"),
        ("versand", "Versand & Logistik", "Logistics", "de"),
        ("lieferung", "Lieferung & Zustellung", "Logistics", "de"),
        ("paketdienst", "Paketzustellung", "Logistics", "de"),
        # Healthcare / Social
        ("altenpflege", "Altenpflege", "Healthcare", "de"),
        ("krankenpflege", "Krankenpflege", "Healthcare", "de"),
        ("pflegehilfe", "Pflegehilfe / Pflegeassistenz", "Healthcare", "de"),
        ("heimhilfe", "Heimhilfe", "Healthcare", "de"),
        ("24-stunden-betreuung", "24-Stunden-Personenbetreuung", "Healthcare", "de"),
        ("rettungssanitäter", "Rettungssanitäter", "Healthcare", "de"),
        ("sozialarbeit", "Sozialarbeit", "Healthcare", "de"),
        # IT (additional)
        ("html", "HTML/CSS", "Technical", "de"),
        ("css", "HTML/CSS", "Technical", "de"),
        ("linux", "Linux-Administration", "Technical", "de"),
        ("windows", "Windows-Administration", "Technical", "de"),
        ("netzwerk", "Netzwerktechnik", "Technical", "de"),
        # Soft skills (additional)
        ("pünktlichkeit", "Pünktlichkeit", "Soft", "de"),
        ("belastbarkeit", "Belastbarkeit", "Soft", "de"),
        ("flexibilität", "Flexibilität", "Soft", "de"),
        ("lernbereitschaft", "Lernbereitschaft", "Soft", "de"),
        ("eigeninitiative", "Eigeninitiative", "Soft", "de"),
        ("genauigkeit", "Genauigkeit & Sorgfalt", "Soft", "de"),
        ("freundlichkeit", "Freundlicher Umgang", "Soft", "de"),
        ("stressresistenz", "Stressresistenz", "Soft", "de"),
        ("konfliktfähigkeit", "Konfliktfähigkeit", "Soft", "de"),
        ("interkulturell", "Interkulturelle Kompetenz", "Soft", "de"),
        # Languages (additional)
        ("türkisch", "Türkischkenntnisse", "Language", "de"),
        ("arabisch", "Arabischkenntnisse", "Language", "de"),
        ("serbisch", "Serbischkenntnisse", "Language", "de"),
        ("kroatisch", "Kroatischkenntnisse", "Language", "de"),
        ("bosnisch", "Bosnischkenntnisse", "Language", "de"),
        ("polnisch", "Polnischkenntnisse", "Language", "de"),
        ("rumänisch", "Rumänischkenntnisse", "Language", "de"),
        ("russisch", "Russischkenntnisse", "Language", "de"),
        ("ukrainisch", "Ukrainischkenntnisse", "Language", "de"),
        ("ungarisch", "Ungarischkenntnisse", "Language", "de"),
        ("farsi", "Farsi-/Dari-Kenntnisse", "Language", "de"),
        ("dari", "Farsi-/Dari-Kenntnisse", "Language", "de"),
        ("französisch", "Französischkenntnisse", "Language", "de"),
        # Austrian qualifications
        ("lehrabschluss", "Lehrabschluss", "Qualification", "de"),
        ("lehre", "Lehrabschluss", "Qualification", "de"),
        ("lap", "Lehrabschlussprüfung (LAP)", "Qualification", "de"),
        ("ams-kurs", "AMS-geförderte Weiterbildung", "Qualification", "de"),
        ("berufserfahrung", "Berufserfahrung", "Qualification", "de"),
        ("matura", "Matura (Reifeprüfung)", "Qualification", "de"),
        ("hauptschule", "Hauptschulabschluss", "Qualification", "de"),
        ("mittelschule", "Mittelschulabschluss", "Qualification", "de"),
        ("pflichtschule", "Pflichtschulabschluss", "Qualification", "de"),
        ("meisterprüfung", "Meisterprüfung", "Qualification", "de"),
        ("werkmeister", "Werkmeisterabschluss", "Qualification", "de"),
        ("nostrifikation", "Nostrifikation (anerkannter Abschluss)", "Qualification", "de"),

        # ================================================================
        # English (en) -- additional terms
        # ================================================================
        ("forklift operation", "Forklift Operation", "Technical", "en"),
        ("forklift license", "Forklift Licence", "Qualification", "en"),
        ("welding", "Welding", "Technical", "en"),
        ("catering service", "Catering & Hospitality", "Gastronomy", "en"),
        ("cooking", "Cooking & Kitchen", "Gastronomy", "en"),
        ("cleaning", "Professional Cleaning", "Cleaning", "en"),
        ("warehouse", "Warehouse Operations", "Logistics", "en"),
        ("delivery", "Delivery & Distribution", "Logistics", "en"),
        ("security", "Security Services", "Technical", "en"),
        ("accounting", "Accounting", "Finance", "en"),
        ("bookkeeping", "Bookkeeping", "Finance", "en"),
        ("payroll", "Payroll Administration", "Finance", "en"),
        ("data entry", "Data Entry", "Office", "en"),
        ("typing", "Typing / Text Processing", "Office", "en"),
        ("filing", "Filing & Document Management", "Office", "en"),
        ("scheduling", "Scheduling & Planning", "Office", "en"),
        ("reception", "Reception / Front Desk", "Office", "en"),
        ("first aid", "First Aid Certificate", "Qualification", "en"),
        ("food safety", "Food Safety (HACCP)", "Compliance", "en"),
        ("sewing", "Sewing & Tailoring", "Technical", "en"),
        ("childcare", "Childcare", "Healthcare", "en"),
        ("elderly care", "Elderly Care", "Healthcare", "en"),
        ("nursing", "Nursing / Care Work", "Healthcare", "en"),
        ("social work", "Social Work", "Healthcare", "en"),
        ("teamwork", "Teamwork", "Soft", "en"),
        ("punctuality", "Punctuality", "Soft", "en"),
        ("reliability", "Reliability", "Soft", "en"),
        ("flexibility", "Flexibility", "Soft", "en"),
        ("problem solving", "Problem Solving", "Soft", "en"),
        ("time management", "Time Management", "Soft", "en"),
        ("multitasking", "Multitasking", "Soft", "en"),
        ("attention to detail", "Attention to Detail", "Soft", "en"),
        ("html css", "HTML/CSS", "Technical", "en"),
        ("web development", "HTML/CSS", "Technical", "en"),
        ("linux admin", "Linux Administration", "Technical", "en"),
        ("networking", "Networking", "Technical", "en"),
        ("project management", "Project Management", "Soft", "en"),

        # ================================================================
        # Turkish (tr) -- expanded
        # ================================================================
        ("muhasebe", "Buchhaltung", "Finance", "tr"),
        ("müşteri hizmetleri", "Kundenbetreuung", "Soft", "tr"),
        ("satış", "Verkauf & Vertrieb", "Retail", "tr"),
        ("garsonluk", "Service & Bedienung", "Gastronomy", "tr"),
        ("aşçılık", "Kochen & Küche", "Gastronomy", "tr"),
        ("temizlik", "Professionelle Reinigung", "Cleaning", "tr"),
        ("forklift belgesi", "Gabelstaplerschein", "Technical", "tr"),
        ("kaynak", "Schweißtechnik", "Technical", "tr"),
        ("bakım", "Instandhaltung", "Technical", "tr"),
        ("üretim", "Produktionserfahrung", "Technical", "tr"),
        ("teslimat", "Lieferung & Zustellung", "Logistics", "tr"),
        ("lojistik", "Logistik", "Logistics", "tr"),
        ("hemşirelik", "Pflegetätigkeiten", "Healthcare", "tr"),
        ("çocuk bakımı", "Kinderbetreuung", "Healthcare", "tr"),
        ("yaşlı bakımı", "Altenpflege", "Healthcare", "tr"),
        ("ilkyardım", "Erste Hilfe", "Qualification", "tr"),
        ("ehliyet", "Führerschein Klasse B", "Qualification", "tr"),
        ("güvenilirlik", "Zuverlässigkeit", "Soft", "tr"),
        ("dakiklik", "Pünktlichkeit", "Soft", "tr"),
        ("esneklik", "Flexibilität", "Soft", "tr"),
        ("iletişim", "Kommunikationsfähigkeit", "Soft", "tr"),

        # ================================================================
        # Arabic (ar) -- expanded
        # ================================================================
        ("محاسبة", "Buchhaltung", "Finance", "ar"),
        ("خدمة العملاء", "Kundenbetreuung", "Soft", "ar"),
        ("مبيعات", "Verkauf & Vertrieb", "Retail", "ar"),
        ("نادل", "Service & Bedienung", "Gastronomy", "ar"),
        ("طبخ", "Kochen & Küche", "Gastronomy", "ar"),
        ("تنظيف", "Professionelle Reinigung", "Cleaning", "ar"),
        ("رافعة شوكية", "Gabelstaplerschein", "Technical", "ar"),
        ("لحام", "Schweißtechnik", "Technical", "ar"),
        ("صيانة", "Instandhaltung", "Technical", "ar"),
        ("إنتاج", "Produktionserfahrung", "Technical", "ar"),
        ("توصيل", "Lieferung & Zustellung", "Logistics", "ar"),
        ("تخزين", "Lagerverwaltung", "Logistics", "ar"),
        ("تمريض", "Pflegetätigkeiten", "Healthcare", "ar"),
        ("رعاية أطفال", "Kinderbetreuung", "Healthcare", "ar"),
        ("رعاية المسنين", "Altenpflege", "Healthcare", "ar"),
        ("إسعافات أولية", "Erste Hilfe", "Qualification", "ar"),
        ("رخصة قيادة", "Führerschein Klasse B", "Qualification", "ar"),
        ("موثوقية", "Zuverlässigkeit", "Soft", "ar"),
        ("اتصال", "Kommunikationsfähigkeit", "Soft", "ar"),
        ("عمل جماعي", "Teamfähigkeit", "Soft", "ar"),
        ("خياطة", "Schneiderarbeiten", "Technical", "ar"),
        ("حلاقة", "Friseur & Haarpflege", "Technical", "ar"),
        ("بناء", "Bau & Baunebengewerbe", "Technical", "ar"),
        ("كهرباء", "Elektrotechnik", "Technical", "ar"),
        ("سباكة", "Installationstechnik (Gas/Wasser/Heizung)", "Technical", "ar"),

        # ================================================================
        # Bosnian / Serbian / Croatian (bs / sr / hr)
        # Using 'bs' as the primary code; these are mutually intelligible
        # ================================================================
        ("računovodstvo", "Buchhaltung", "Finance", "bs"),
        ("korisničke usluge", "Kundenbetreuung", "Soft", "bs"),
        ("prodaja", "Verkauf & Vertrieb", "Retail", "bs"),
        ("konobar", "Service & Bedienung", "Gastronomy", "bs"),
        ("kuhanje", "Kochen & Küche", "Gastronomy", "bs"),
        ("čišćenje", "Professionelle Reinigung", "Cleaning", "bs"),
        ("viljuškar", "Gabelstaplerschein", "Technical", "bs"),
        ("zavarivanje", "Schweißtechnik", "Technical", "bs"),
        ("održavanje", "Instandhaltung", "Technical", "bs"),
        ("proizvodnja", "Produktionserfahrung", "Technical", "bs"),
        ("dostava", "Lieferung & Zustellung", "Logistics", "bs"),
        ("skladište", "Lagerverwaltung", "Logistics", "bs"),
        ("njega", "Pflegetätigkeiten", "Healthcare", "bs"),
        ("briga o djeci", "Kinderbetreuung", "Healthcare", "bs"),
        ("prva pomoć", "Erste Hilfe", "Qualification", "bs"),
        ("vozačka dozvola", "Führerschein Klasse B", "Qualification", "bs"),
        ("pouzdanost", "Zuverlässigkeit", "Soft", "bs"),
        ("komunikacija", "Kommunikationsfähigkeit", "Soft", "bs"),
        ("timski rad", "Teamfähigkeit", "Soft", "bs"),
        ("kompjuter", "PC-Kenntnisse (MS Office)", "Office", "bs"),
        ("majstor", "Handwerkliche Fähigkeiten", "Technical", "bs"),
        ("moler", "Malerei & Anstrich", "Technical", "bs"),
        ("keramičar", "Fliesenverlegung", "Technical", "bs"),
        ("električar", "Elektrotechnik", "Technical", "bs"),
        ("automehaničar", "KFZ-Mechanik", "Technical", "bs"),
        ("šnajder", "Schneiderarbeiten", "Technical", "bs"),
        ("frizer", "Friseur & Haarpflege", "Technical", "bs"),
        ("njemački", "Deutschkenntnisse", "Language", "bs"),
        ("engleski", "Englischkenntnisse", "Language", "bs"),

        # ================================================================
        # Polish (pl)
        # ================================================================
        ("księgowość", "Buchhaltung", "Finance", "pl"),
        ("obsługa klienta", "Kundenbetreuung", "Soft", "pl"),
        ("sprzedaż", "Verkauf & Vertrieb", "Retail", "pl"),
        ("kelner", "Service & Bedienung", "Gastronomy", "pl"),
        ("gotowanie", "Kochen & Küche", "Gastronomy", "pl"),
        ("sprzątanie", "Professionelle Reinigung", "Cleaning", "pl"),
        ("wózek widłowy", "Gabelstaplerschein", "Technical", "pl"),
        ("spawanie", "Schweißtechnik", "Technical", "pl"),
        ("konserwacja", "Instandhaltung", "Technical", "pl"),
        ("produkcja", "Produktionserfahrung", "Technical", "pl"),
        ("dostawa", "Lieferung & Zustellung", "Logistics", "pl"),
        ("magazyn", "Lagerverwaltung", "Logistics", "pl"),
        ("opieka", "Pflegetätigkeiten", "Healthcare", "pl"),
        ("opieka nad dziećmi", "Kinderbetreuung", "Healthcare", "pl"),
        ("pierwsza pomoc", "Erste Hilfe", "Qualification", "pl"),
        ("prawo jazdy", "Führerschein Klasse B", "Qualification", "pl"),
        ("niezawodność", "Zuverlässigkeit", "Soft", "pl"),
        ("komunikacja", "Kommunikationsfähigkeit", "Soft", "pl"),
        ("praca zespołowa", "Teamfähigkeit", "Soft", "pl"),
        ("komputer", "PC-Kenntnisse (MS Office)", "Office", "pl"),
        ("murarz", "Maurerarbeiten", "Technical", "pl"),
        ("malarz", "Malerei & Anstrich", "Technical", "pl"),
        ("elektryk", "Elektrotechnik", "Technical", "pl"),
        ("mechanik", "KFZ-Mechanik", "Technical", "pl"),
        ("stolarz", "Tischlerei", "Technical", "pl"),
        ("krawiec", "Schneiderarbeiten", "Technical", "pl"),
        ("fryzjer", "Friseur & Haarpflege", "Technical", "pl"),
        ("niemiecki", "Deutschkenntnisse", "Language", "pl"),
        ("angielski", "Englischkenntnisse", "Language", "pl"),

        # ================================================================
        # Ukrainian (uk)
        # ================================================================
        ("бухгалтерія", "Buchhaltung", "Finance", "uk"),
        ("обслуговування клієнтів", "Kundenbetreuung", "Soft", "uk"),
        ("продаж", "Verkauf & Vertrieb", "Retail", "uk"),
        ("офіціант", "Service & Bedienung", "Gastronomy", "uk"),
        ("готування", "Kochen & Küche", "Gastronomy", "uk"),
        ("прибирання", "Professionelle Reinigung", "Cleaning", "uk"),
        ("навантажувач", "Gabelstaplerschein", "Technical", "uk"),
        ("зварювання", "Schweißtechnik", "Technical", "uk"),
        ("обслуговування", "Instandhaltung", "Technical", "uk"),
        ("виробництво", "Produktionserfahrung", "Technical", "uk"),
        ("доставка", "Lieferung & Zustellung", "Logistics", "uk"),
        ("склад", "Lagerverwaltung", "Logistics", "uk"),
        ("догляд", "Pflegetätigkeiten", "Healthcare", "uk"),
        ("догляд за дітьми", "Kinderbetreuung", "Healthcare", "uk"),
        ("перша допомога", "Erste Hilfe", "Qualification", "uk"),
        ("водійські права", "Führerschein Klasse B", "Qualification", "uk"),
        ("надійність", "Zuverlässigkeit", "Soft", "uk"),
        ("комунікація", "Kommunikationsfähigkeit", "Soft", "uk"),
        ("командна робота", "Teamfähigkeit", "Soft", "uk"),
        ("комп'ютер", "PC-Kenntnisse (MS Office)", "Office", "uk"),
        ("електрик", "Elektrotechnik", "Technical", "uk"),
        ("муляр", "Maurerarbeiten", "Technical", "uk"),
        ("маляр", "Malerei & Anstrich", "Technical", "uk"),
        ("механік", "KFZ-Mechanik", "Technical", "uk"),
        ("столяр", "Tischlerei", "Technical", "uk"),
        ("кравець", "Schneiderarbeiten", "Technical", "uk"),
        ("перукар", "Friseur & Haarpflege", "Technical", "uk"),
        ("німецька", "Deutschkenntnisse", "Language", "uk"),
        ("англійська", "Englischkenntnisse", "Language", "uk"),

        # ================================================================
        # Russian (ru)
        # ================================================================
        ("бухгалтерия", "Buchhaltung", "Finance", "ru"),
        ("обслуживание клиентов", "Kundenbetreuung", "Soft", "ru"),
        ("продажи", "Verkauf & Vertrieb", "Retail", "ru"),
        ("официант", "Service & Bedienung", "Gastronomy", "ru"),
        ("готовка", "Kochen & Küche", "Gastronomy", "ru"),
        ("уборка", "Professionelle Reinigung", "Cleaning", "ru"),
        ("погрузчик", "Gabelstaplerschein", "Technical", "ru"),
        ("сварка", "Schweißtechnik", "Technical", "ru"),
        ("обслуживание", "Instandhaltung", "Technical", "ru"),
        ("производство", "Produktionserfahrung", "Technical", "ru"),
        ("служба доставки", "Lieferung & Zustellung", "Logistics", "ru"),
        ("складская работа", "Lagerverwaltung", "Logistics", "ru"),
        ("уход", "Pflegetätigkeiten", "Healthcare", "ru"),
        ("уход за детьми", "Kinderbetreuung", "Healthcare", "ru"),
        ("первая помощь", "Erste Hilfe", "Qualification", "ru"),
        ("водительские права", "Führerschein Klasse B", "Qualification", "ru"),
        ("надёжность", "Zuverlässigkeit", "Soft", "ru"),
        ("коммуникация", "Kommunikationsfähigkeit", "Soft", "ru"),
        ("командная работа", "Teamfähigkeit", "Soft", "ru"),
        ("компьютер", "PC-Kenntnisse (MS Office)", "Office", "ru"),
        ("электрик", "Elektrotechnik", "Technical", "ru"),
        ("каменщик", "Maurerarbeiten", "Technical", "ru"),
        ("маляр-штукатур", "Malerei & Anstrich", "Technical", "ru"),
        ("механик", "KFZ-Mechanik", "Technical", "ru"),
        ("столяр-плотник", "Tischlerei", "Technical", "ru"),
        ("портной", "Schneiderarbeiten", "Technical", "ru"),
        ("парикмахер", "Friseur & Haarpflege", "Technical", "ru"),
        ("немецкий", "Deutschkenntnisse", "Language", "ru"),
        ("английский", "Englischkenntnisse", "Language", "ru"),

        # ================================================================
        # Romanian (ro)
        # ================================================================
        ("contabilitate", "Buchhaltung", "Finance", "ro"),
        ("serviciu clienți", "Kundenbetreuung", "Soft", "ro"),
        ("vânzări", "Verkauf & Vertrieb", "Retail", "ro"),
        ("chelner", "Service & Bedienung", "Gastronomy", "ro"),
        ("gătit", "Kochen & Küche", "Gastronomy", "ro"),
        ("curățenie", "Professionelle Reinigung", "Cleaning", "ro"),
        ("stivuitor", "Gabelstaplerschein", "Technical", "ro"),
        ("sudură", "Schweißtechnik", "Technical", "ro"),
        ("întreținere", "Instandhaltung", "Technical", "ro"),
        ("producție", "Produktionserfahrung", "Technical", "ro"),
        ("livrare", "Lieferung & Zustellung", "Logistics", "ro"),
        ("depozit", "Lagerverwaltung", "Logistics", "ro"),
        ("îngrijire", "Pflegetätigkeiten", "Healthcare", "ro"),
        ("îngrijire copii", "Kinderbetreuung", "Healthcare", "ro"),
        ("prim ajutor", "Erste Hilfe", "Qualification", "ro"),
        ("permis de conducere", "Führerschein Klasse B", "Qualification", "ro"),
        ("fiabilitate", "Zuverlässigkeit", "Soft", "ro"),
        ("comunicare", "Kommunikationsfähigkeit", "Soft", "ro"),
        ("lucru în echipă", "Teamfähigkeit", "Soft", "ro"),
        ("calculator", "PC-Kenntnisse (MS Office)", "Office", "ro"),
        ("electrician", "Elektrotechnik", "Technical", "ro"),
        ("zidar", "Maurerarbeiten", "Technical", "ro"),
        ("zugrav", "Malerei & Anstrich", "Technical", "ro"),
        ("mecanic", "KFZ-Mechanik", "Technical", "ro"),
        ("tâmplar", "Tischlerei", "Technical", "ro"),
        ("croitor", "Schneiderarbeiten", "Technical", "ro"),
        ("coafor", "Friseur & Haarpflege", "Technical", "ro"),
        ("germană", "Deutschkenntnisse", "Language", "ro"),
        ("engleză", "Englischkenntnisse", "Language", "ro"),

        # ================================================================
        # Farsi / Dari (fa) -- large Afghan/Iranian community in Austria
        # ================================================================
        ("حسابداری", "Buchhaltung", "Finance", "fa"),
        ("خدمات مشتری", "Kundenbetreuung", "Soft", "fa"),
        ("فروش", "Verkauf & Vertrieb", "Retail", "fa"),
        ("آشپزی", "Kochen & Küche", "Gastronomy", "fa"),
        ("نظافت", "Professionelle Reinigung", "Cleaning", "fa"),
        ("جوشکاری", "Schweißtechnik", "Technical", "fa"),
        ("تولید", "Produktionserfahrung", "Technical", "fa"),
        ("تحویل", "Lieferung & Zustellung", "Logistics", "fa"),
        ("انبار", "Lagerverwaltung", "Logistics", "fa"),
        ("پرستاری", "Pflegetätigkeiten", "Healthcare", "fa"),
        ("مراقبت از کودکان", "Kinderbetreuung", "Healthcare", "fa"),
        ("کمک‌های اولیه", "Erste Hilfe", "Qualification", "fa"),
        ("گواهینامه رانندگی", "Führerschein Klasse B", "Qualification", "fa"),
        ("کامپیوتر", "PC-Kenntnisse (MS Office)", "Office", "fa"),
        ("آلمانی", "Deutschkenntnisse", "Language", "fa"),
        ("انگلیسی", "Englischkenntnisse", "Language", "fa"),
        ("کار تیمی", "Teamfähigkeit", "Soft", "fa"),
        ("ارتباطات", "Kommunikationsfähigkeit", "Soft", "fa"),
        ("خیاطی", "Schneiderarbeiten", "Technical", "fa"),
        ("برقکاری", "Elektrotechnik", "Technical", "fa"),
    ]


# ============================================================================
# 4. ATS Keyword Bank (Austrian labour market focus)
# ============================================================================

def get_expanded_ats_keywords() -> dict[str, list[str]]:
    """Return canonical_keyword: [synonyms] for the ATS bank.

    Covers Austrian-specific terms, common certifications, industry tools,
    and job categories frequently seen in AMS contexts.
    """
    return {
        # ── Austrian qualifications ────────────────────────────────────────
        "Lehrabschluss": [
            "lehre", "lehrberuf", "lehrabschlussprüfung", "lap",
            "lehrling", "apprenticeship",
        ],
        "AMS-Kurs": [
            "ams-ausbildung", "ams kurs", "ams-weiterbildung",
            "ams maßnahme", "ams-maßnahme", "arbeitsmarktservice",
        ],
        "Berufserfahrung": [
            "work experience", "praxiserfahrung", "arbeitserfahrung",
            "berufspraxis", "einschlägige erfahrung",
        ],
        "Matura": [
            "reifeprüfung", "abitur", "allgemeine hochschulreife",
            "berufsreifeprüfung", "brp",
        ],
        "Pflichtschulabschluss": [
            "hauptschulabschluss", "mittelschulabschluss",
            "neue mittelschule", "nms",
        ],
        "Nostrifikation": [
            "anerkennung", "anerkannter abschluss",
            "nostrifizierung", "gleichhaltung",
        ],

        # ── Driving & transport licences ──────────────────────────────────
        "B-Führerschein": [
            "führerschein b", "führerschein klasse b", "pkw-führerschein",
            "fahrerlaubnis b", "driving licence b", "klasse b",
        ],
        "C-Führerschein": [
            "führerschein c", "lkw-führerschein", "führerschein klasse c",
            "fahrerlaubnis c", "driving licence c", "klasse c",
        ],
        "Staplerschein": [
            "gabelstaplerschein", "staplerschein", "forklift licence",
            "forklift certificate", "gabelstapler", "flurförderzeug",
        ],
        "ADR-Schein": [
            "gefahrgut", "gefahrgutschein", "adr-führerschein",
            "gefahrgutzertifikat", "dangerous goods",
        ],
        "Kranschein": [
            "kranführerschein", "kranführer", "crane licence",
            "mobilkran", "brückenkran",
        ],

        # ── Certifications ────────────────────────────────────────────────
        "Schweißzertifikat": [
            "schweißschein", "schweißprüfung", "welding certificate",
            "en iso 9606", "schweißer",
        ],
        "HACCP": [
            "haccp-zertifikat", "lebensmittelhygiene",
            "hygieneschulung", "food safety", "food hygiene",
        ],
        "Erste-Hilfe-Kurs": [
            "erste hilfe", "first aid", "ersthelfer",
            "erste-hilfe-zertifikat", "ersthelferausbildung",
        ],
        "Sicherheitsvertrauensperson": [
            "svp", "sicherheitsbeauftragter", "arbeitssicherheit",
            "safety officer", "arbeitsschutz",
        ],
        "Brandschutzbeauftragter": [
            "brandschutz", "feuerlöscher", "fire safety",
            "brandschutzwart", "brandschutzschulung",
        ],

        # ── Industry tools / software ─────────────────────────────────────
        "DATEV": [
            "datev unternehmen online", "datev buchhaltung",
        ],
        "BMD": [
            "bmd ntcs", "bmd software", "bmd buchhaltung",
            "bmd business software",
        ],
        "SAP Business One": [
            "sap b1", "sap business one",
        ],
        "SAP": [
            "sap erp", "sap r/3", "sap s/4hana", "sap mm", "sap fi",
        ],
        "Microsoft Excel": [
            "excel", "ms excel", "spreadsheet", "tabellenkalkulation",
            "pivot-tabelle", "vlookup",
        ],
        "Microsoft Word": [
            "word", "ms word", "textverarbeitung",
        ],
        "Microsoft Office": [
            "ms office", "office suite", "office paket",
            "office 365", "microsoft 365",
        ],
        "Microsoft Outlook": [
            "outlook", "e-mail-programm",
        ],
        "Microsoft Teams": [
            "teams", "ms teams", "videokonferenz",
        ],

        # ── Soft skills (ATS-tracked) ─────────────────────────────────────
        "Teamarbeit": [
            "teamwork", "team player", "teamfähigkeit",
            "teamfähig", "zusammenarbeit",
        ],
        "Kommunikation": [
            "communication", "kommunikationsstärke",
            "kommunikationsfähigkeit", "kontaktfreudig",
        ],
        "Führungserfahrung": [
            "leadership", "leitungserfahrung", "führungskompetenz",
            "personalführung", "teamleitung",
        ],
        "Projektmanagement": [
            "project management", "projektleitung",
            "projektkoordination", "projektarbeit",
        ],
        "Kundenservice": [
            "customer service", "kundendienst", "kundenbetreuung",
            "kundenberatung", "kundenkontakt",
        ],
        "Organisationsfähigkeit": [
            "organisationstalent", "organizational skills",
            "organisiert", "organisatorisch",
        ],
        "Selbstständigkeit": [
            "eigenverantwortung", "selbstständige arbeitsweise",
            "eigeninitiative", "selbständig",
        ],
        "Belastbarkeit": [
            "stressresistenz", "belastbar", "stressfähig",
            "resilience", "stress resistant",
        ],
        "Zuverlässigkeit": [
            "verlässlichkeit", "reliability", "zuverlässig",
            "pünktlichkeit", "punctuality",
        ],
        "Flexibilität": [
            "flexibility", "anpassungsfähigkeit", "flexibel",
            "einsatzbereitschaft", "vielseitigkeit",
        ],

        # ── Work environment ──────────────────────────────────────────────
        "Schichtarbeit": [
            "shift work", "wechselschicht", "schichtbereitschaft",
            "2-schicht", "3-schicht", "nachtschicht",
        ],
        "Führerschein": [
            "driver's licence", "driving licence", "fahrerlaubnis",
        ],
        "Reisebereitschaft": [
            "travel readiness", "reisebereit", "mobilität",
            "außendienst", "field service",
        ],

        # ── Industry sectors (AMS-relevant) ───────────────────────────────
        "Produktion": [
            "fertigung", "manufacturing", "maschinenbedienung",
            "produktionsmitarbeiter", "fließband",
        ],
        "Lagerwirtschaft": [
            "lagerverwaltung", "warehouse", "kommissionierung",
            "lagerlogistik", "wareneingang", "warenausgang",
        ],
        "Reinigung": [
            "cleaning", "gebäudereinigung", "unterhaltsreinigung",
            "sonderreinigung", "reinigungskraft",
        ],
        "Pflege": [
            "care", "pflegehilfe", "pflegeassistenz",
            "heimhilfe", "altenpflege", "krankenpflege",
        ],
        "Gastronomie": [
            "gastgewerbe", "hospitality", "restaurant",
            "hotel", "hotellerie", "küche",
        ],
        "Handel": [
            "einzelhandel", "retail", "verkauf",
            "vertrieb", "großhandel",
        ],
        "Bau": [
            "bauwesen", "construction", "hochbau", "tiefbau",
            "bauarbeiter", "bauhelfer",
        ],
        "Transport": [
            "logistik", "spedition", "zustellung",
            "lieferdienst", "paketdienst", "kurier",
        ],

        # ── Languages (ATS keywords in job ads) ──────────────────────────
        "Deutsch B1": [
            "deutsch b1", "deutschkenntnisse b1",
            "german b1", "deutsch niveau b1",
        ],
        "Deutsch B2": [
            "deutsch b2", "deutschkenntnisse b2",
            "german b2", "deutsch niveau b2",
        ],
        "Englisch": [
            "english", "englischkenntnisse", "english skills",
        ],
    }


# ============================================================================
# 5. Apply expansion to database
# ============================================================================

def apply_expansion(db_manager: "DatabaseManager") -> dict:
    """Apply all expansions to the database via the DatabaseManager.

    Uses INSERT OR IGNORE to be idempotent (safe to run multiple times).
    Returns a dict with counts of rows inserted for each category.

    Args:
        db_manager: An initialized DatabaseManager instance.

    Returns:
        Dict like {"verbs_en": 50, "verbs_de": 80, "skills": 230, "ats_keywords": 45}
    """
    counts = {"verbs_en": 0, "verbs_de": 0, "skills": 0, "ats_keywords": 0}

    # ── English verbs ────────────────────────────────────────────────────
    en_verbs = get_expanded_verbs_en()
    if en_verbs:
        verb_params = [(weak, strong, "en") for weak, strong in en_verbs]
        try:
            db_manager.execute_batch(
                "INSERT OR IGNORE INTO verb_replacements (weak_verb, strong_verb, language) "
                "VALUES (?, ?, ?)",
                verb_params,
            )
            counts["verbs_en"] = len(en_verbs)
            logger.info(f"Seed expansion: {len(en_verbs)} English verbs queued")
        except Exception as e:
            logger.error(f"Seed expansion error (EN verbs): {e}")

    # ── German verbs ─────────────────────────────────────────────────────
    de_verbs = get_expanded_verbs_de()
    if de_verbs:
        verb_params = [(weak, strong, "de") for weak, strong in de_verbs]
        try:
            db_manager.execute_batch(
                "INSERT OR IGNORE INTO verb_replacements (weak_verb, strong_verb, language) "
                "VALUES (?, ?, ?)",
                verb_params,
            )
            counts["verbs_de"] = len(de_verbs)
            logger.info(f"Seed expansion: {len(de_verbs)} German verbs queued")
        except Exception as e:
            logger.error(f"Seed expansion error (DE verbs): {e}")

    # ── Skills (all languages) ───────────────────────────────────────────
    skills = get_expanded_skills()
    if skills:
        try:
            db_manager.execute_batch(
                "INSERT OR IGNORE INTO skills_dictionary "
                "(key_term, normalized_skill, category, language) VALUES (?, ?, ?, ?)",
                skills,
            )
            counts["skills"] = len(skills)
            logger.info(f"Seed expansion: {len(skills)} skills queued")
        except Exception as e:
            logger.error(f"Seed expansion error (skills): {e}")

    # ── ATS keywords (update in-memory bank in polish/ats.py) ────────────
    # The ATS bank lives as a Python dict, not in the DB. We still provide
    # the data here so that callers can merge it programmatically.
    ats = get_expanded_ats_keywords()
    counts["ats_keywords"] = len(ats)
    logger.info(f"Seed expansion: {len(ats)} ATS keyword groups available")

    logger.info(
        f"Seed expansion complete: "
        f"{counts['verbs_en']} EN verbs, "
        f"{counts['verbs_de']} DE verbs, "
        f"{counts['skills']} skills, "
        f"{counts['ats_keywords']} ATS keyword groups"
    )
    return counts


def apply_ats_expansion() -> dict[str, list[str]]:
    """Merge the expanded ATS keywords into the in-memory ATS_KEYWORD_BANK.

    Call this at application startup (e.g. in app.py) to enrich the ATS
    analyser without touching the database.

    Returns:
        The merged keyword bank (reference to the same dict in polish.ats).
    """
    try:
        from polish.ats import ATS_KEYWORD_BANK
    except ImportError:
        logger.warning("Could not import ATS_KEYWORD_BANK -- skipping ATS expansion")
        return {}

    expanded = get_expanded_ats_keywords()
    for canonical, synonyms in expanded.items():
        if canonical in ATS_KEYWORD_BANK:
            # Merge new synonyms, avoiding duplicates
            existing = set(ATS_KEYWORD_BANK[canonical])
            ATS_KEYWORD_BANK[canonical] = list(existing | set(synonyms))
        else:
            ATS_KEYWORD_BANK[canonical] = synonyms

    logger.info(f"ATS bank expanded: now {len(ATS_KEYWORD_BANK)} keyword groups")
    return ATS_KEYWORD_BANK


# ============================================================================
# CLI entry point
# ============================================================================

def _main():
    """Run seed expansion from the command line."""
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/ams_jobassist.db"
    logger.info(f"Applying seed expansion to: {db_path}")

    # Direct SQLite connection for standalone use (no DatabaseManager dependency)
    db_file = Path(db_path)
    if not db_file.exists():
        logger.error(f"Database not found: {db_file.resolve()}")
        logger.info("Run the application first to create the database, or provide a path.")
        sys.exit(1)

    conn = sqlite3.connect(str(db_file))
    conn.execute("PRAGMA foreign_keys=ON")

    counts = {"verbs_en": 0, "verbs_de": 0, "skills": 0, "ats_keywords": 0}

    # English verbs
    en_verbs = get_expanded_verbs_en()
    for weak, strong in en_verbs:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO verb_replacements (weak_verb, strong_verb, language) "
                "VALUES (?, ?, ?)",
                (weak, strong, "en"),
            )
            counts["verbs_en"] += 1
        except sqlite3.Error as e:
            logger.warning(f"Skipping EN verb '{weak}': {e}")

    # German verbs
    de_verbs = get_expanded_verbs_de()
    for weak, strong in de_verbs:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO verb_replacements (weak_verb, strong_verb, language) "
                "VALUES (?, ?, ?)",
                (weak, strong, "de"),
            )
            counts["verbs_de"] += 1
        except sqlite3.Error as e:
            logger.warning(f"Skipping DE verb '{weak}': {e}")

    # Skills (all languages)
    skills = get_expanded_skills()
    for key_term, normalized, category, lang in skills:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO skills_dictionary "
                "(key_term, normalized_skill, category, language) VALUES (?, ?, ?, ?)",
                (key_term, normalized, category, lang),
            )
            counts["skills"] += 1
        except sqlite3.Error as e:
            logger.warning(f"Skipping skill '{key_term}': {e}")

    # ATS keywords (just count -- they live in Python memory)
    ats = get_expanded_ats_keywords()
    counts["ats_keywords"] = len(ats)

    conn.commit()
    conn.close()

    print(f"\nSeed expansion applied successfully:")
    print(f"  English verbs:     {counts['verbs_en']}")
    print(f"  German verbs:      {counts['verbs_de']}")
    print(f"  Skills (all lang): {counts['skills']}")
    print(f"  ATS keyword groups: {counts['ats_keywords']}")
    print(f"\nTotal new DB rows: {counts['verbs_en'] + counts['verbs_de'] + counts['skills']}")
    print(f"(Duplicates were skipped via INSERT OR IGNORE)")


if __name__ == "__main__":
    _main()
