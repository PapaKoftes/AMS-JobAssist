"""
Interview paths configuration for AMS JobAssist.

5 hardcoded paths with questions, examples, quick-fill suggestions, and helper tips:
1. unemployed  - Person looking for first job or re-entering workforce
2. career-switch - Person changing careers intentionally
3. student      - Current student with internship/part-time experience
4. pause        - Person returning after career break
5. other        - Generic path for other situations

Each question includes:
- text: The question (warm, human German)
- hint: Gentle guidance without pressure
- examples.good: A realistic positive example from everyday work
- examples.bad:  A too-vague version showing what to avoid
- quick_fill: Clickable starter phrases users can tap to begin typing
- helper_tip: Contextual advice when user seems stuck
- min_length: Minimum characters before we accept the answer
- category: For CV section grouping
- flags: For polish engine targeting
"""

_IDENTITY_QUESTIONS = [
    {
        "id": "id_name",
        "order": 0,
        "category": "identity",
        "text": "Wie heißen Sie?",
        "hint": "Geben Sie Ihren vollständigen Namen ein — Vor- und Nachname.",
        "examples": {
            "good": "Maria Horvat",
            "bad": "Maria"
        },
        "quick_fill": [],
        "helper_tip": "Ihr voller Name hilft uns, Ihren Lebenslauf professionell zu gestalten.",
        "min_length": 2,
        "flags": ["identity"]
    },
    {
        "id": "id_location",
        "order": 1,
        "category": "identity",
        "text": "In welcher Stadt wohnen Sie?",
        "hint": "Zum Beispiel: Wien, Graz, Linz, Salzburg, Wels",
        "examples": {
            "good": "Wien, 1100",
            "bad": "in Österreich"
        },
        "quick_fill": ["Wien", "Graz", "Linz", "Salzburg", "Innsbruck", "Wels", "Klagenfurt"],
        "helper_tip": "Ihr Wohnort wird für den Lebenslauf benötigt — kein Stressthema!",
        "min_length": 2,
        "flags": ["identity"]
    },
    {
        "id": "id_phone",
        "order": 1.2,
        "category": "identity",
        "text": "Wie lautet Ihre Telefonnummer?",
        "hint": "Optional — Sie können diese Frage überspringen, wenn Sie möchten.",
        "examples": {
            "good": "+43 660 123 45 67",
            "bad": "mein Handy"
        },
        "quick_fill": [],
        "helper_tip": "Ihre Nummer erscheint im Kontaktbereich Ihres Lebenslaufs. Kein Pflichtfeld.",
        "min_length": 0,
        "flags": ["identity", "optional"]
    },
    {
        "id": "id_email",
        "order": 1.4,
        "category": "identity",
        "text": "Wie lautet Ihre E-Mail-Adresse?",
        "hint": "Optional — falls Sie eine haben. Sie können diese Frage auch überspringen.",
        "examples": {
            "good": "maria.horvat@gmail.com",
            "bad": "meine E-Mail"
        },
        "quick_fill": [],
        "helper_tip": "Eine E-Mail-Adresse erleichtert es Arbeitgebern, Sie zu kontaktieren.",
        "min_length": 0,
        "flags": ["identity", "optional"]
    },
]

# Target-job question — inserted as the third question on every path.
# Stored as target_job and used to align follow-up probes throughout the interview.
_TARGET_JOB_QUESTION = {
    "id": "id_target_job",
    "order": 1.5,   # between identity questions (order=1) and path questions (order=2)
    "category": "motivation",
    "text": "Welche Art von Stelle suchen Sie?",
    "hint": "Schreiben Sie einen Jobwunsch, eine Berufsbezeichnung, oder fügen Sie einfach einen Teil der Stellenanzeige ein. Muss nicht perfekt sein.",
    "examples": {
        "good": "Ich suche eine Stelle im Lager, Einzelhandel oder als Reinigungskraft — Teilzeit wäre super.",
        "bad": "Irgendwas"
    },
    "quick_fill": [
        "Lager / Logistik",
        "Einzelhandel / Verkauf",
        "Reinigung / Haushalt",
        "Büro / Verwaltung",
        "Pflege / Soziales",
        "Gastronomie / Küche",
        "Produktion / Fabrik",
        "Ich bin offen für vieles",
    ],
    "helper_tip": "Keine Sorge — das können Sie auch als ungefähre Angabe machen. Dieser Schritt hilft uns, Ihren Lebenslauf besser auf Ihre Ziele abzustimmen.",
    "min_length": 3,
    "flags": ["target_job"],
}

# Reusable structured question templates (inserted after each work-experience question)
def _make_employer_question(base_id: str, order: float) -> dict:
    """Generate an employer-name question linked to a base experience question."""
    return {
        "id": f"{base_id}_employer",
        "order": order,
        "category": "experience",
        "text": "Bei welchem Unternehmen haben Sie das gemacht? (Firmenname oder Beschreibung)",
        "hint": "Zum Beispiel: 'BILLA Supermarkt', 'Reinigungsfirma meiner Tante', 'Familienbetrieb'. Kein offizieller Name nötig.",
        "examples": {
            "good": "Reinigungsfirma Maier GmbH, Wien",
            "bad": "Eine Firma"
        },
        "quick_fill": [
            "Familienunternehmen",
            "Ich kenne den offiziellen Namen nicht mehr",
            "Ehrenamtlich / ohne Unternehmen",
            "Selbständig / auf eigene Rechnung",
        ],
        "helper_tip": "Auch 'Familienbetrieb' oder 'Nachbarschaftshilfe' ist eine gültige Antwort — schreiben Sie einfach, was es war.",
        "min_length": 2,
        "flags": ["employer_name"],
    }


def _make_title_question(base_id: str, order: float) -> dict:
    """Generate a job-title question linked to a base experience question."""
    return {
        "id": f"{base_id}_title",
        "order": order,
        "category": "experience",
        "text": "Was war Ihre Funktion oder Berufsbezeichnung?",
        "hint": "Zum Beispiel: Lagermitarbeiter/in, Kassier/in, Reinigungskraft, Helfer/in, Praktikant/in",
        "examples": {
            "good": "Lagermitarbeiterin / Helferin",
            "bad": "Ich habe gearbeitet"
        },
        "quick_fill": [
            "Hilfskraft / Helfer/in",
            "Praktikant/in",
            "Kassier/in",
            "Lagermitarbeiter/in",
            "Reinigungskraft",
            "Pflegehelferin / Pflegehelfer",
            "Ich hatte keine offizielle Bezeichnung",
        ],
        "helper_tip": "Keine offizielle Berufsbezeichnung? Beschreiben Sie kurz, was Sie gemacht haben — z.B. 'Allroundkraft' oder 'Haushaltshelfer'.",
        "min_length": 2,
        "flags": ["job_title"],
    }


def _make_dates_question(base_id: str, order: float) -> dict:
    """Generate a date-range question linked to a base experience question."""
    return {
        "id": f"{base_id}_dates",
        "order": order,
        "category": "experience",
        "text": "Von wann bis wann haben Sie dort gearbeitet? (Ungefähre Angaben sind in Ordnung)",
        "hint": "Zum Beispiel: 'Jänner 2020 bis März 2022', 'ca. 2 Jahre', 'bis letztes Jahr', 'noch aktuell'",
        "examples": {
            "good": "Jänner 2020 bis März 2022 (ca. 2 Jahre)",
            "bad": "Schon lange"
        },
        "quick_fill": [
            "Von 20__ bis 20__",
            "Ungefähr __ Jahre",
            "Bis heute / noch aktuell",
            "Ich erinnere mich nicht genau",
        ],
        "helper_tip": "Ungefähre Angaben sind völlig in Ordnung — Ihr Trainer kann das später mit Ihnen genauer besprechen.",
        "min_length": 2,
        "flags": ["date_range"],
    }

INTERVIEW_PATHS = {

    # =========================================================================
    # PATH 1: JOBSUCHEND
    # For: people without recent work history, re-entry, first-timers
    # Key challenge: "I've never worked" → help them see what they DID do
    # =========================================================================
    "unemployed": {
        "label": "Jobsuchend",
        "description": "Auf der Suche nach Arbeit oder Wiedereinstieg",
        "questions": _IDENTITY_QUESTIONS + [_TARGET_JOB_QUESTION] + [
            {
                "id": "u_01",
                "order": 2,
                "category": "background",
                "text": "Welche Schule oder Ausbildung haben Sie abgeschlossen?",
                "hint": "Schule, Lehre, Kurs, Umschulung — alles zählt. Sagen Sie auch, was Sie dabei gelernt haben.",
                "examples": {
                    "good": "Ich habe eine 3-jährige Lehre als Köchin abgeschlossen. Ich habe gelernt, für große Gruppen zu kochen, Bestellungen zu organisieren und die Küche sauber zu halten.",
                    "bad": "Ich habe die Schule fertig gemacht."
                },
                "quick_fill": [
                    "Ich habe die Hauptschule abgeschlossen.",
                    "Ich habe eine Lehre gemacht als ",
                    "Ich habe einen Kurs abgeschlossen.",
                    "Ich habe keinen Abschluss, aber ich habe viel gelernt.",
                ],
                "helper_tip": "Auch ein Kurs bei AMS oder eine Umschulung ist eine echte Ausbildung — schreiben Sie es auf!",
                "min_length": 15,
                "flags": ["education"]
            },
            {
                "id": "u_02",
                "order": 3,
                "category": "experience",
                "text": "Haben Sie jemals gearbeitet — bezahlt oder unbezahlt? Auch Familienhilfe oder Ehrenamt?",
                "hint": "Familienbetrieb, Babysitting, Helfen bei Nachbarn, Ehrenamtliches, Schuljobs — das alles zählt!",
                "examples": {
                    "good": "Ich habe 2 Jahre lang meiner Tante in ihrer Reinigungsfirma geholfen. Ich habe Büros gereinigt, Geräte bedient und Termine koordiniert. Ich habe gelernt, pünktlich und gründlich zu arbeiten.",
                    "bad": "Ich habe keine Berufserfahrung."
                },
                "quick_fill": [
                    "Ich habe in der Familie mitgeholfen beim ",
                    "Ich habe Babysitting gemacht.",
                    "Ich habe ehrenamtlich gearbeitet bei ",
                    "Ich habe im Haushalt geholfen und ",
                    "Ich habe noch nicht bezahlt gearbeitet, aber ich habe ",
                ],
                "helper_tip": "Keine bezahlte Arbeit ist kein Problem! Was haben Sie zu Hause, in der Schule oder für andere gemacht?",
                "min_length": 20,
                "flags": ["work_experience"]
            },
            _make_employer_question("u_02", 3.1),
            _make_title_question("u_02", 3.2),
            _make_dates_question("u_02", 3.3),
            {
                "id": "u_03",
                "order": 4,
                "category": "skills",
                "text": "Was können Sie gut? Mit welchen Werkzeugen, Maschinen oder Programmen kennen Sie sich aus?",
                "hint": "Computer, Maschinen, Küchengeräte, Kasse, Fahrzeuge, Programme — was haben Sie schon benutzt?",
                "examples": {
                    "good": "Ich kann mit dem Computer arbeiten (Word, E-Mail), ich bin Inhaber eines Führerscheins der Klasse B, und ich kenne mich mit einfachen Haushaltsgeräten aus. Ich habe auch ein paar Monate eine Kaffeemaschine bedient.",
                    "bad": "Ich kann ein bisschen Computer."
                },
                "quick_fill": [
                    "Ich kann Microsoft Office (Word, Excel) bedienen.",
                    "Ich habe Erfahrung mit der Kasse.",
                    "Ich bin körperlich fit und kann schwere Arbeit machen.",
                    "Ich kann mit Maschinen umgehen, zum Beispiel ",
                    "Ich habe einen Führerschein (Klasse B).",
                    "Ich kenne mich mit Reinigungsgeräten aus.",
                ],
                "helper_tip": "Fast alles zählt als Fähigkeit: Autofahren, Kochen, Geräte bedienen, mit Menschen reden.",
                "min_length": 15,
                "flags": ["technical_skills", "practical_skills"]
            },
            {
                "id": "u_04",
                "order": 5,
                "category": "skills",
                "text": "Welche Sprachen sprechen Sie? Auch wenn Sie noch lernen — bitte alles angeben.",
                "hint": "Deutsch, Englisch, Türkisch, Bosnisch, Arabisch, Rumänisch — jede Sprache ist wertvoll!",
                "examples": {
                    "good": "Ich spreche Deutsch (Arbeitsniveau), Bosnisch (Muttersprache) und ein bisschen Englisch. Ich lerne gerade Deutsch und werde besser.",
                    "bad": "Ich spreche Deutsch."
                },
                "quick_fill": [
                    "Deutsch (Grundkenntnisse)",
                    "Deutsch (Arbeitsniveau)",
                    "Deutsch (fließend)",
                    "Meine Muttersprache ist ",
                    "Ich spreche auch ein bisschen Englisch.",
                ],
                "helper_tip": "Mehrsprachigkeit ist ein echter Vorteil — auch wenn Ihr Deutsch noch nicht perfekt ist!",
                "min_length": 5,
                "flags": ["languages"]
            },
            {
                "id": "u_05",
                "order": 6,
                "category": "experience",
                "text": "Haben Sie schon mal mit anderen zusammengearbeitet — in einer Gruppe, einem Team, einer Familie?",
                "hint": "Sport, Schulprojekt, Verein, Kirche, Nachbarschaft — wann haben Sie mit anderen etwas gemeinsam gemacht?",
                "examples": {
                    "good": "Im Sportverein war ich Schiedsrichter bei Kinderspielen. Ich musste Regeln erklären, fair bleiben und Streitigkeiten lösen. 20 bis 30 Kinder jedes Wochenende.",
                    "bad": "Ich habe in der Schule Gruppenarbeit gemacht."
                },
                "quick_fill": [
                    "Ich habe im Sportverein mitgemacht.",
                    "Ich habe in der Familie Aufgaben übernommen wie ",
                    "Ich habe in der Schule Gruppenarbeit gemacht.",
                    "Ich habe bei einem Verein oder einer Gemeinde mitgeholfen.",
                ],
                "helper_tip": "Teamarbeit bedeutet nicht unbedingt im Büro — überall wo Menschen zusammenarbeiten zählt.",
                "min_length": 20,
                "flags": ["teamwork"]
            },
            {
                "id": "u_06",
                "order": 7,
                "category": "skills",
                "text": "Was machen Sie gerne? Haben Sie Hobbys oder Interessen, die auch bei der Arbeit helfen könnten?",
                "hint": "Kochen, Reparieren, Basteln, Sport, Musik, Tiere, Kinder betreuen — manchmal ist das eine Fähigkeit!",
                "examples": {
                    "good": "Ich repariere gerne alte Fahrräder in meiner Freizeit. Ich habe schon über 20 Räder repariert, auch für Nachbarn. Ich verstehe Mechanik und arbeite gerne mit den Händen.",
                    "bad": "Ich höre Musik und schaue TV."
                },
                "quick_fill": [
                    "Ich koche gerne und gut.",
                    "Ich repariere gerne Dinge zu Hause.",
                    "Ich betreue gerne Kinder oder ältere Menschen.",
                    "Ich mache gerne Sport und bin körperlich aktiv.",
                    "Ich arbeite gerne mit meinen Händen.",
                ],
                "helper_tip": "Hobbys zeigen Persönlichkeit — und manchmal echte Fähigkeiten, die für den Job relevant sind.",
                "min_length": 10,
                "flags": ["soft_skills", "interests"]
            },
            {
                "id": "u_07",
                "order": 8,
                "category": "motivation",
                "text": "Was für eine Arbeit suchen Sie? Was ist Ihnen bei einem Job wichtig?",
                "hint": "Vollzeit, Teilzeit, körperliche Arbeit, Büro, mit Menschen, draußen — was passt zu Ihnen?",
                "examples": {
                    "good": "Ich suche eine Vollzeitstelle, gerne körperliche Arbeit wie Lager oder Reinigung. Mir ist wichtig, dass die Arbeitszeiten verlässlich sind, weil ich Kinder habe.",
                    "bad": "Ich suche einen Job."
                },
                "quick_fill": [
                    "Ich suche Vollzeitarbeit.",
                    "Ich suche Teilzeitarbeit.",
                    "Ich möchte körperliche Arbeit machen.",
                    "Ich möchte gerne im Büro arbeiten.",
                    "Mir ist wichtig, dass ich mit Menschen arbeite.",
                    "Mir ist wichtig, dass die Zeiten zu meiner Familie passen.",
                ],
                "helper_tip": "Es gibt keine falsche Antwort — sagen Sie einfach, was wirklich zu Ihnen passt.",
                "min_length": 15,
                "flags": ["motivation", "future_goals"]
            },
        ]
    },

    # =========================================================================
    # PATH 2: BERUFSWECHSEL
    # For: people changing from one industry to another
    # Key challenge: Fear of "starting over" → reframe transferable skills
    # =========================================================================
    "career-switch": {
        "label": "Berufswechsel",
        "description": "Wechsel in ein neues Berufsfeld oder eine andere Branche",
        "questions": _IDENTITY_QUESTIONS + [_TARGET_JOB_QUESTION] + [
            {
                "id": "cs_01",
                "order": 2,
                "category": "experience",
                "text": "Was war Ihr bisheriger Beruf? Erzählen Sie uns, was Sie dort gemacht haben.",
                "hint": "Position, Unternehmen, wie lange, was waren Ihre täglichen Aufgaben.",
                "examples": {
                    "good": "Ich war 6 Jahre lang Pflegehelferin in einem Seniorenheim. Jeden Tag habe ich 8-10 Bewohner betreut, beim Essen geholfen, Medikamente verteilt und die Pflegedokumentation ausgefüllt.",
                    "bad": "Ich war im Pflegebereich."
                },
                "quick_fill": [
                    "Ich habe in der Gastronomie gearbeitet als ",
                    "Ich habe im Handel gearbeitet als ",
                    "Ich habe in der Pflege gearbeitet als ",
                    "Ich habe in der Produktion gearbeitet als ",
                    "Ich habe im Handwerk gearbeitet als ",
                    "Ich habe im Büro gearbeitet als ",
                ],
                "helper_tip": "Egal wie verschieden der neue Job scheint — Ihre Erfahrungen haben echten Wert.",
                "min_length": 25,
                "flags": ["previous_career", "work_experience"]
            },
            _make_employer_question("cs_01", 2.1),
            _make_title_question("cs_01", 2.2),
            _make_dates_question("cs_01", 2.3),
            {
                "id": "cs_02",
                "order": 3,
                "category": "skills",
                "text": "Welche Dinge aus Ihrem alten Job können Ihnen im neuen Bereich helfen?",
                "hint": "Pünktlichkeit, Kundenkontakt, Organisation, körperliche Fitness, Teamarbeit, Geduld, Verantwortung — viele Fähigkeiten passen überall.",
                "examples": {
                    "good": "Als Köchin habe ich gelernt, sehr schnell zu arbeiten, Mengen richtig einzuschätzen und unter Druck ruhig zu bleiben. Diese Fähigkeiten helfen mir jetzt auch in der Lagerhaltung.",
                    "bad": "Ich lerne schnell."
                },
                "quick_fill": [
                    "Ich bin pünktlich und zuverlässig.",
                    "Ich bin gewohnt, unter Zeitdruck zu arbeiten.",
                    "Ich kann gut mit Menschen umgehen.",
                    "Ich bin organisiert und genau.",
                    "Ich bin körperlich fit und belastbar.",
                    "Ich kann gut im Team arbeiten.",
                ],
                "helper_tip": "Fast jede Fähigkeit kann man mitnehmen — auch Geduld, Fleiß und Teamgeist zählen.",
                "min_length": 20,
                "flags": ["skills_transfer", "soft_skills"]
            },
            {
                "id": "cs_03",
                "order": 4,
                "category": "background",
                "text": "Warum möchten Sie den Beruf wechseln? Was hat Sie dazu bewogen?",
                "hint": "Gesundheit, Wunsch nach Veränderung, bessere Zukunft, Familie, Interessen — alle Gründe sind in Ordnung.",
                "examples": {
                    "good": "Ich habe 8 Jahre als Kellnerin gearbeitet, aber die Abendarbeit passt nicht mehr zu meiner Familie. Ich möchte in einen Beruf wechseln, wo ich tagsüber arbeite und trotzdem meine Stärken einsetzen kann.",
                    "bad": "Mein alter Job war schlecht."
                },
                "quick_fill": [
                    "Ich möchte mehr Zeit für meine Familie haben.",
                    "Mein Körper hält die schwere Arbeit nicht mehr so gut aus.",
                    "Ich möchte beruflich weiterkommen.",
                    "Ich habe meine Interessen verändert.",
                    "Ich suche mehr Stabilität.",
                ],
                "helper_tip": "Ehrliche Gründe sind gut — Sie müssen sich nicht schämen dafür, dass Sie sich verändern möchten.",
                "min_length": 20,
                "flags": ["motivation", "stability"]
            },
            {
                "id": "cs_04",
                "order": 5,
                "category": "training",
                "text": "Haben Sie bereits etwas getan, um sich auf den neuen Beruf vorzubereiten?",
                "hint": "Kurs, Praktikum, Selbststudium, YouTube, Bücher, Freiwilligenarbeit in dem neuen Bereich — alles zählt!",
                "examples": {
                    "good": "Ich habe einen 4-wöchigen Kurs in Bürokommunikation abgeschlossen und übe täglich am Computer zuhause. Ich habe auch ein 2-wöchiges Schnupperpraktikum in einem Büro gemacht.",
                    "bad": "Ich möchte noch viel lernen."
                },
                "quick_fill": [
                    "Ich habe einen Kurs gemacht über ",
                    "Ich lerne gerade selbst über ",
                    "Ich habe noch keine formale Vorbereitung, bin aber bereit zu lernen.",
                    "Ich habe ein Praktikum gemacht in ",
                ],
                "helper_tip": "Auch Selbststudium oder ein kurzes Schnuppern zeigt echtes Interesse und Einsatz.",
                "min_length": 15,
                "flags": ["education", "training"]
            },
            {
                "id": "cs_05",
                "order": 6,
                "category": "skills",
                "text": "Welche Werkzeuge, Programme oder Geräte kennen Sie — aus altem oder neuem Bereich?",
                "hint": "Computer, Maschinen, Küchengeräte, Fahrzeuge, spezielle Software — was können Sie bedienen?",
                "examples": {
                    "good": "Aus meiner Zeit als Bürokauffrau kenne ich Word, Excel und Outlook. Ich habe auch das Warenwirtschaftssystem SAP grundlegend gelernt.",
                    "bad": "Ich kann Computer ein bisschen."
                },
                "quick_fill": [
                    "Ich kann Microsoft Office (Word, Excel, Outlook).",
                    "Ich habe Erfahrung mit der Kasse / dem POS-System.",
                    "Ich kenne mich mit Lagergeräten aus (Hubwagen, Gabelstapler).",
                    "Ich habe Führerschein Klasse B (und C).",
                    "Ich kenne mich mit Reinigungsgeräten aus.",
                    "Ich habe Erfahrung mit Pflegegeräten.",
                ],
                "helper_tip": "Auch sehr einfache Geräte-Kenntnisse sind wichtig zu erwähnen.",
                "min_length": 10,
                "flags": ["technical_skills", "practical_skills"]
            },
            {
                "id": "cs_06",
                "order": 7,
                "category": "experience",
                "text": "Gab es eine Situation in Ihrer Arbeit, wo Sie mit einem schwierigen Problem umgegangen sind?",
                "hint": "Schwieriger Kunde, Fehler der behoben werden musste, Stress — wie haben Sie reagiert?",
                "examples": {
                    "good": "Einmal hat unser ganzes Team gleichzeitig gekündigt und ich war plötzlich allein verantwortlich. Ich habe kurzfristig Aushilfen organisiert und den Betrieb eine Woche alleine geführt.",
                    "bad": "Arbeit ist manchmal schwierig."
                },
                "quick_fill": [
                    "Ich war einmal in einer stressigen Situation und habe ",
                    "Ich musste einmal schnell eine Lösung finden, weil ",
                    "Ich habe schon Konflikte gelöst, indem ich ",
                ],
                "helper_tip": "Diese Frage zeigt, dass Sie auch in schwierigen Momenten verlässlich sind.",
                "min_length": 20,
                "flags": ["resilience", "problem_solving"]
            },
            {
                "id": "cs_07",
                "order": 8,
                "category": "motivation",
                "text": "Was erhoffen Sie sich von Ihrer neuen Stelle? Was ist Ihr Ziel?",
                "hint": "Mehr Stabilität, Wachstum, bessere Zeiten, weniger körperliche Belastung, mehr Kreativität — was suchen Sie?",
                "examples": {
                    "good": "Ich möchte in einem Büro arbeiten, wo ich meine Organisations-Fähigkeiten gut einsetzen kann. Ich suche ein stabiles Team und möchte mich langfristig weiterentwickeln.",
                    "bad": "Ich brauche einen neuen Job."
                },
                "quick_fill": [
                    "Ich möchte eine stabile Arbeit mit geregelten Zeiten.",
                    "Ich möchte mich beruflich weiterentwickeln.",
                    "Ich möchte weniger körperliche Belastung haben.",
                    "Ich möchte langfristig bei einem Unternehmen bleiben.",
                ],
                "helper_tip": "Sagen Sie ehrlich was Sie sich wünschen — das hilft uns, Ihren Lebenslauf gut zu formulieren.",
                "min_length": 15,
                "flags": ["future_goals", "motivation"]
            },
        ]
    },

    # =========================================================================
    # PATH 3: SCHÜLER/STUDENT
    # For: people in education, apprenticeship, or just graduated
    # Key challenge: "I don't have real experience" → validate their work
    # =========================================================================
    "student": {
        "label": "Schüler/in oder Student/in",
        "description": "In Ausbildung oder kurz vor dem Abschluss",
        "questions": _IDENTITY_QUESTIONS + [_TARGET_JOB_QUESTION] + [
            {
                "id": "st_01",
                "order": 2,
                "category": "background",
                "text": "Was lernen oder studieren Sie gerade? In welchem Jahr sind Sie?",
                "hint": "Schule, Lehre, Studium, FH, Universität, Kurs — was machen Sie gerade genau?",
                "examples": {
                    "good": "Ich mache gerade eine Lehre als Tischler im 2. Lehrjahr bei Möbel Müller in Wien. Voraussichtlicher Abschluss: 2026.",
                    "bad": "Ich bin Schüler."
                },
                "quick_fill": [
                    "Ich mache eine Lehre als ",
                    "Ich studiere an der ",
                    "Ich besuche die ",
                    "Ich mache gerade einen Kurs bei ",
                ],
                "helper_tip": "Auch wenn Sie noch mitten drin sind — Ihre Ausbildung zeigt, dass Sie sich weiterentwickeln!",
                "min_length": 15,
                "flags": ["education"]
            },
            {
                "id": "st_02",
                "order": 3,
                "category": "experience",
                "text": "Haben Sie schon ein Praktikum oder Nebenjob gemacht? Was war Ihre Aufgabe?",
                "hint": "Erzählen Sie: Wo war es, wie lange, und was haben Sie täglich gemacht?",
                "examples": {
                    "good": "Letzten Sommer habe ich 6 Wochen Praktikum in einem Supermarkt gemacht. Ich habe Regale aufgefüllt, an der Kasse ausgeholfen und Kunden beim Finden von Produkten geholfen.",
                    "bad": "Ich habe ein Praktikum gemacht."
                },
                "quick_fill": [
                    "Ich habe Praktikum gemacht in einem/einer ",
                    "Ich arbeite nebenbei als ",
                    "Ich habe noch kein Praktikum gemacht, aber ich habe zu Hause geholfen bei ",
                ],
                "helper_tip": "Auch kurze Praktika oder Nebenjobs (Zeitungen austragen, Babysitting) zählen!",
                "min_length": 20,
                "flags": ["work_experience", "internship"]
            },
            _make_employer_question("st_02", 3.1),
            _make_title_question("st_02", 3.2),
            _make_dates_question("st_02", 3.3),
            {
                "id": "st_03",
                "order": 4,
                "category": "projects",
                "text": "Gibt es ein Schul- oder Ausbildungsprojekt, auf das Sie stolz sind?",
                "hint": "Gruppenarbeit, Werkstück, Abschlussarbeit, Wettbewerb, selbst gemachtes Projekt — erzählen Sie davon!",
                "examples": {
                    "good": "In der Berufsschule habe ich mit meiner Gruppe einen Holztisch komplett selbst gebaut — Planung, Zuschnitt, Schliff und Lackierung. Der Lehrer hat ihn sehr gelobt.",
                    "bad": "Wir haben in der Schule viel gemacht."
                },
                "quick_fill": [
                    "Ich habe in der Schule ein Projekt gemacht über/zu ",
                    "In der Lehre habe ich selbst ",
                    "Ich habe an einem Wettbewerb teilgenommen und ",
                    "Ich habe zu Hause selbst ",
                ],
                "helper_tip": "Auch wenn das Projekt einfach klingt — es zeigt was Sie wirklich können.",
                "min_length": 20,
                "flags": ["projects", "technical_skills"]
            },
            {
                "id": "st_04",
                "order": 5,
                "category": "skills",
                "text": "Was können Sie gut? Welche Werkzeuge, Programme oder Geräte kennen Sie?",
                "hint": "Computerprogramme, Werkzeuge, Maschinen, Instrumente, Sport — was haben Sie in der Ausbildung oder Schule gelernt?",
                "examples": {
                    "good": "Ich kann mit Holzmaschinen arbeiten (Säge, Fräse, Schleifmaschine). In der Schule habe ich auch Word und Excel gelernt. Außerdem spreche ich Kroatisch und Deutsch.",
                    "bad": "Ich kann Dinge in der Schule."
                },
                "quick_fill": [
                    "Ich kenne mich mit ",
                    "Ich habe in der Schule gelernt: ",
                    "In meiner Lehre arbeite ich täglich mit ",
                    "Ich kann gut mit dem Computer umgehen.",
                    "Ich kenne Maschinen wie ",
                ],
                "helper_tip": "Auch kleine Dinge zählen: Autofahren, tippen, Kassenarbeit, einfache Reparaturen.",
                "min_length": 15,
                "flags": ["technical_skills", "practical_skills"]
            },
            {
                "id": "st_05",
                "order": 6,
                "category": "skills",
                "text": "Welche Sprachen sprechen Sie?",
                "hint": "Deutsch, Englisch, Türkisch, Serbisch, Arabisch — jede Sprache ist ein Plus!",
                "examples": {
                    "good": "Deutsch (Schulniveau), Türkisch (Muttersprache), ein bisschen Englisch aus der Schule.",
                    "bad": "Deutsch."
                },
                "quick_fill": [
                    "Deutsch (gut / fließend / Grundkenntnisse)",
                    "Englisch (gut / ein bisschen)",
                    "Meine Muttersprache ist ",
                    "Ich spreche auch ",
                ],
                "helper_tip": "Mehrere Sprachen zu sprechen ist wertvoller als viele denken — schreiben Sie alle auf!",
                "min_length": 3,
                "flags": ["languages"]
            },
            {
                "id": "st_06",
                "order": 7,
                "category": "experience",
                "text": "Waren Sie jemals in einem Verein, Team oder einer Gruppe aktiv?",
                "hint": "Sport, Musik, Kirche, Jugendgruppe, Pfadfinder, Schulclub — was haben Sie außerhalb der Schule gemacht?",
                "examples": {
                    "good": "Ich spiele 3 Jahre lang Fußball in einem Verein. Ich bin Mannschaftskapitän und organisiere die Trainingszeiten für 15 Spieler.",
                    "bad": "Ich mache Sport."
                },
                "quick_fill": [
                    "Ich bin im Sportverein aktiv.",
                    "Ich mache Musik (Instrument: ).",
                    "Ich helfe in der Gemeinde / Kirche mit.",
                    "Ich war Klassensprecher/in.",
                    "Ich mache kein Vereinsleben.",
                ],
                "helper_tip": "Freizeitaktivitäten zeigen Charakter: Teamgeist, Verantwortung, Disziplin.",
                "min_length": 10,
                "flags": ["teamwork", "leadership", "interests"]
            },
            {
                "id": "st_07",
                "order": 8,
                "category": "motivation",
                "text": "Was für einen Job möchten Sie nach Ihrer Ausbildung machen?",
                "hint": "Welche Branche, welche Art von Aufgaben, welche Arbeitsumgebung — was stellen Sie sich vor?",
                "examples": {
                    "good": "Nach meiner Tischlerlehre möchte ich in einer kleinen Werkstatt anfangen und mich auf Möbeldesign spezialisieren. Ich möchte auch den Meister machen.",
                    "bad": "Ich möchte in meinem Beruf arbeiten."
                },
                "quick_fill": [
                    "Ich möchte in meinem Lehrberuf arbeiten.",
                    "Ich möchte weiter studieren nach der Schule.",
                    "Ich bin noch nicht sicher, aber ich interessiere mich für ",
                    "Ich möchte möglichst schnell Berufserfahrung sammeln.",
                ],
                "helper_tip": "Auch unsichere Pläne sind okay — sagen Sie einfach, was Sie sich vorstellen.",
                "min_length": 15,
                "flags": ["motivation", "future_goals"]
            },
        ]
    },

    # =========================================================================
    # PATH 4: BERUFLICHE PAUSE
    # For: people returning after gap (childcare, illness, migration, etc.)
    # Key challenge: Shame about "gap" → reframe gap as strength/growth
    # =========================================================================
    "pause": {
        "label": "Berufliche Pause",
        "description": "Rückkehr nach einer Zeit ohne Arbeit",
        "questions": _IDENTITY_QUESTIONS + [_TARGET_JOB_QUESTION] + [
            {
                "id": "p_01",
                "order": 2,
                "category": "experience",
                "text": "Was war Ihr Beruf vor der Pause? Was haben Sie dort hauptsächlich gemacht?",
                "hint": "Position, Branche, wie lange — und was waren Ihre täglichen Aufgaben?",
                "examples": {
                    "good": "Ich war 5 Jahre Kassiererin bei einem Supermarkt. Ich habe täglich Kunden bedient, die Kasse abgerechnet, Waren eingeräumt und bei Inventuren geholfen.",
                    "bad": "Ich habe früher gearbeitet."
                },
                "quick_fill": [
                    "Ich habe früher als ",
                    "Ich war im Bereich ",
                    "Ich habe vor der Pause in ",
                ],
                "helper_tip": "Jede Berufserfahrung zählt — auch wenn sie schon etwas länger her ist.",
                "min_length": 20,
                "flags": ["previous_career", "work_experience"]
            },
            _make_employer_question("p_01", 2.1),
            _make_title_question("p_01", 2.2),
            _make_dates_question("p_01", 2.3),
            {
                "id": "p_02",
                "order": 3,
                "category": "background",
                "text": "Warum haben Sie eine Pause gemacht? (Kinder, Gesundheit, Pflege, Umzug — alles ist in Ordnung.)",
                "hint": "Sie müssen nicht viel erklären. Sagen Sie kurz den Grund und was Sie in der Pause gemacht haben.",
                "examples": {
                    "good": "Ich habe 4 Jahre pausiert, um meine zwei Kinder zu betreuen. Ich habe den Haushalt organisiert, Termine koordiniert und mich um alle bürokratischen Angelegenheiten der Familie gekümmert.",
                    "bad": "Ich habe nicht gearbeitet."
                },
                "quick_fill": [
                    "Ich habe pausiert wegen meiner Kinder.",
                    "Ich habe pausiert wegen Gesundheitsproblemen.",
                    "Ich bin ins Ausland umgezogen und musste neu anfangen.",
                    "Ich habe Familienmitglieder gepflegt.",
                    "Ich habe mich um den Haushalt gekümmert.",
                ],
                "helper_tip": "Eine Pause aus familiären Gründen zu nehmen ist eine Stärke, keine Schwäche — das zeigen wir im Lebenslauf.",
                "min_length": 15,
                "flags": ["stability", "motivation"]
            },
            {
                "id": "p_03",
                "order": 4,
                "category": "skills",
                "text": "Was haben Sie während der Pause gemacht? Auch Haushaltsführung, Kinderbetreuung oder Pflege ist echte Arbeit.",
                "hint": "Organisation, Kochen für viele, Arzttermine, Buchhaltung zu Hause, Schulaufgaben begleiten — das sind alles Fähigkeiten.",
                "examples": {
                    "good": "Während der Pause habe ich den gesamten Familienhaushalt organisiert: Finanzen, Arzttermine, Schule der Kinder und Einkäufe für 5 Personen. Das hat mir Organisations- und Planungsfähigkeiten gegeben.",
                    "bad": "Ich habe zu Hause gelebt."
                },
                "quick_fill": [
                    "Ich habe den Familienhaushalt organisiert.",
                    "Ich habe Kinder betreut und ihnen bei der Schule geholfen.",
                    "Ich habe einen kranken Angehörigen gepflegt.",
                    "Ich habe die Familienfinanzen verwaltet.",
                    "Ich habe ehrenamtlich geholfen bei ",
                ],
                "helper_tip": "Haushalt führen, Kinder betreuen, Pflege leisten — das sind echte Kompetenzen für den Arbeitsmarkt.",
                "min_length": 15,
                "flags": ["soft_skills", "practical_skills"]
            },
            {
                "id": "p_04",
                "order": 5,
                "category": "training",
                "text": "Haben Sie in der Pause etwas gelernt oder sich weitergebildet — auch selbst?",
                "hint": "Kurse, Sprachen, YouTube-Tutorials, Bücher, AMS-Kurse, Nachbarschaftshilfe — alles zählt.",
                "examples": {
                    "good": "Ich habe in der Pause einen Deutsch-Kurs beim AMS gemacht und am Computer geübt. Ich habe auch einen Online-Kurs in Erste Hilfe abgeschlossen.",
                    "bad": "Ich habe nichts gemacht."
                },
                "quick_fill": [
                    "Ich habe einen Kurs beim AMS gemacht.",
                    "Ich habe Deutsch gelernt / verbessert.",
                    "Ich habe Computer-Grundkenntnisse gelernt.",
                    "Ich habe noch keine Kurse gemacht, bin aber bereit.",
                ],
                "helper_tip": "Auch ein einziger Kurs oder Deutschkenntnisse verbessern zeigen echten Einsatz.",
                "min_length": 10,
                "flags": ["training", "education"]
            },
            {
                "id": "p_05",
                "order": 6,
                "category": "skills",
                "text": "Welche Fähigkeiten haben Sie — aus früherer Arbeit, Haushalt, Hobbys oder Sprachen?",
                "hint": "Denken Sie breit: Kommunikation, Sprachen, körperliche Arbeit, Organisationstalent, Geduld, Genauigkeit.",
                "examples": {
                    "good": "Ich spreche Deutsch und Arabisch fließend. Ich bin sehr organisiert und gewohnt, viele Dinge gleichzeitig zu koordinieren. Ich bin geduldig und einfühlsam — besonders im Umgang mit Menschen.",
                    "bad": "Ich habe ein paar Fähigkeiten."
                },
                "quick_fill": [
                    "Ich bin zuverlässig und pünktlich.",
                    "Ich bin organisiert und plane gerne.",
                    "Ich bin geduldig und ruhig auch unter Druck.",
                    "Ich spreche mehrere Sprachen.",
                    "Ich bin körperlich fit und kann schwer arbeiten.",
                    "Ich lerne schnell neue Dinge.",
                ],
                "helper_tip": "Jeder hat Stärken — manchmal sieht man sie selbst am wenigsten. Wir helfen Ihnen dabei.",
                "min_length": 15,
                "flags": ["skills_transfer", "soft_skills", "languages"]
            },
            {
                "id": "p_06",
                "order": 7,
                "category": "experience",
                "text": "Haben Sie in der Pause anderen geholfen — in der Nachbarschaft, Familie, Kirche, Verein?",
                "hint": "Ehrenamt, Nachbarschaftshilfe, Elternabend, Flüchtlingshilfe, Kirchengruppe — alles ist echte Erfahrung.",
                "examples": {
                    "good": "Ich habe 2 Jahre lang bei einer Nachbarschaftshilfe Einkäufe für ältere Menschen gemacht und bei der lokalen Moschee bei Veranstaltungen geholfen.",
                    "bad": "Nein, ich habe zu Hause gelebt."
                },
                "quick_fill": [
                    "Ich habe ehrenamtlich geholfen bei ",
                    "Ich war im Elternverein aktiv.",
                    "Ich habe Nachbarn geholfen mit ",
                    "Ich habe in der Kirchengemeinde mitgemacht.",
                    "Ich habe keine Ehrenamtsarbeit gemacht.",
                ],
                "helper_tip": "Nachbarschaftshilfe und Ehrenamt zählen als echte Berufserfahrung im Lebenslauf.",
                "min_length": 10,
                "flags": ["teamwork", "community"]
            },
            {
                "id": "p_07",
                "order": 8,
                "category": "motivation",
                "text": "Was suchen Sie jetzt bei der Rückkehr in die Arbeit? Was ist Ihnen wichtig?",
                "hint": "Stabile Zeiten, Vollzeit oder Teilzeit, Art der Arbeit, Nähe zur Wohnung, Teamumgebung — was passt zu Ihnen?",
                "examples": {
                    "good": "Ich möchte mit Teilzeit beginnen, zum Beispiel 20-25 Stunden pro Woche. Mir ist wichtig, dass die Arbeitszeiten zu meinen Betreuungszeiten passen. Ich möchte gerne im Bereich Handel oder Pflege arbeiten.",
                    "bad": "Ich möchte arbeiten."
                },
                "quick_fill": [
                    "Ich suche Teilzeitarbeit.",
                    "Ich bin bereit für Vollzeitarbeit.",
                    "Mir ist wichtig, dass die Zeiten zu meinen Kindern passen.",
                    "Ich möchte körperliche Arbeit machen.",
                    "Ich möchte mit Menschen arbeiten.",
                    "Ich möchte in der Nähe meines Wohnorts arbeiten.",
                ],
                "helper_tip": "Es ist völlig normal, mit Teilzeit zu beginnen — das zeigt Verantwortungsbewusstsein.",
                "min_length": 15,
                "flags": ["future_goals", "motivation"]
            },
        ]
    },

    # =========================================================================
    # PATH 5: SONSTIGES
    # For: freelancers, migrants, older workers, non-standard situations
    # Key challenge: "My situation doesn't fit any box" → make them feel seen
    # =========================================================================
    "other": {
        "label": "Sonstiges",
        "description": "Meine Situation ist etwas anders",
        "questions": _IDENTITY_QUESTIONS + [_TARGET_JOB_QUESTION] + [
            {
                "id": "o_01",
                "order": 2,
                "category": "background",
                "text": "Erzählen Sie uns kurz Ihre Geschichte. Was haben Sie bisher in Ihrem Berufsleben gemacht?",
                "hint": "Keine Angst, wenn Ihr Lebenslauf 'ungewöhnlich' aussieht — hier ist jede Geschichte willkommen.",
                "examples": {
                    "good": "Ich bin vor 3 Jahren aus Syrien nach Österreich gekommen. In Syrien war ich Elektriker. Hier habe ich Deutsch gelernt und ein paar Monate in der Produktion gearbeitet.",
                    "bad": "Ich habe verschiedene Dinge gemacht."
                },
                "quick_fill": [
                    "Ich bin zugewandert und komme ursprünglich aus ",
                    "Ich war selbständig / freiberuflich tätig als ",
                    "Ich habe in verschiedenen Bereichen gearbeitet.",
                    "Ich habe lange Zeit im Ausland gearbeitet.",
                    "Mein Beruf aus dem Heimatland wird hier nicht anerkannt.",
                ],
                "helper_tip": "Auch ungewöhnliche Lebensläufe sind wertvoll — wir helfen Ihnen, Ihre Erfahrung zu zeigen.",
                "min_length": 20,
                "flags": ["work_experience", "background"]
            },
            {
                "id": "o_02",
                "order": 3,
                "category": "experience",
                "text": "Was war Ihre Hauptarbeit oder Hauptaufgabe in den letzten Jahren?",
                "hint": "Auch wenn es schwer ist zu erklären — versuchen Sie zu beschreiben, was Sie jeden Tag gemacht haben.",
                "examples": {
                    "good": "In Rumänien war ich 10 Jahre lang LKW-Fahrer. Ich habe Waren in ganz Europa geliefert, Frachtdokumente ausgefüllt und die Routen selbst geplant.",
                    "bad": "Ich habe gearbeitet."
                },
                "quick_fill": [
                    "Ich habe täglich ",
                    "Meine Hauptaufgabe war ",
                    "Ich habe Verantwortung getragen für ",
                ],
                "helper_tip": "Erzählen Sie es ruhig wie einem Freund — wir formieren das dann professionell für Ihren Lebenslauf.",
                "min_length": 20,
                "flags": ["work_experience"]
            },
            _make_employer_question("o_02", 3.1),
            _make_title_question("o_02", 3.2),
            _make_dates_question("o_02", 3.3),
            {
                "id": "o_03",
                "order": 4,
                "category": "skills",
                "text": "Was können Sie besonders gut? Was sagen andere über Sie?",
                "hint": "Denken Sie an Fähigkeiten, Sprachen, körperliche Stärken, Genauigkeit, Geduld, Verantwortungsbewusstsein.",
                "examples": {
                    "good": "Ich bin sehr genau und fehlerfrei. Meine früheren Chefs haben immer gesagt, ich bin der Zuverlässigste im Team. Ich spreche vier Sprachen und lerne schnell.",
                    "bad": "Ich bin gut in meiner Arbeit."
                },
                "quick_fill": [
                    "Ich bin zuverlässig und pünktlich.",
                    "Ich lerne sehr schnell neue Dinge.",
                    "Ich bin sehr genau und fehlerbewusst.",
                    "Ich kann gut unter Druck arbeiten.",
                    "Ich bin ein guter Teamplayer.",
                    "Ich spreche mehrere Sprachen.",
                    "Ich habe körperliche Stärke und Belastbarkeit.",
                ],
                "helper_tip": "Was sagen Freunde, Familie oder frühere Chefs über Sie? Das ist oft Ihre wahre Stärke.",
                "min_length": 15,
                "flags": ["soft_skills", "technical_skills"]
            },
            {
                "id": "o_04",
                "order": 5,
                "category": "skills",
                "text": "Welche Sprachen sprechen Sie? Auch Grundkenntnisse sind wichtig zu erwähnen.",
                "hint": "Jede Sprache ist ein Vorteil auf dem österreichischen Arbeitsmarkt.",
                "examples": {
                    "good": "Ich spreche Russisch (Muttersprache), Deutsch (B2-Niveau), Englisch (gut) und ein bisschen Polnisch.",
                    "bad": "Ich spreche Russisch und Deutsch."
                },
                "quick_fill": [
                    "Meine Muttersprache ist ",
                    "Ich spreche Deutsch (Grundkenntnisse / B1 / B2 / fließend).",
                    "Ich spreche Englisch (ein bisschen / gut / fließend).",
                    "Ich spreche außerdem ",
                ],
                "helper_tip": "In Wien und anderen Großstädten ist Mehrsprachigkeit sehr gefragt — schreiben Sie alle Sprachen auf!",
                "min_length": 5,
                "flags": ["languages"]
            },
            {
                "id": "o_05",
                "order": 6,
                "category": "training",
                "text": "Welche Ausbildung oder Zertifikate haben Sie — aus Österreich oder aus dem Ausland?",
                "hint": "Schulabschluss, Berufsabschluss, Zertifikate, Führerschein, Meisterbrief, Sicherheitsschulung — alles davon.",
                "examples": {
                    "good": "In Ägypten habe ich einen Abschluss als Elektroingenieur gemacht. In Österreich habe ich den Elektro-Befähigungsschein Klasse 1 erworben und einen AMS-Kurs in Sicherheitsvorschriften abgeschlossen.",
                    "bad": "Ich habe Ausbildung gemacht."
                },
                "quick_fill": [
                    "Ich habe im Ausland folgenden Abschluss: ",
                    "Mein Abschluss wurde in Österreich anerkannt / noch nicht anerkannt.",
                    "Ich habe einen AMS-Kurs abgeschlossen.",
                    "Ich habe einen Führerschein Klasse B / C / D.",
                    "Ich habe keine formale Ausbildung, aber viel praktische Erfahrung.",
                ],
                "helper_tip": "Auch ausländische Abschlüsse können im Lebenslauf erwähnt werden — selbst wenn sie noch nicht anerkannt sind.",
                "min_length": 10,
                "flags": ["education", "training"]
            },
            {
                "id": "o_06",
                "order": 7,
                "category": "experience",
                "text": "Gab es eine Situation, in der Sie etwas Schwieriges geschafft haben? Egal ob bei der Arbeit oder privat.",
                "hint": "Umzug in ein neues Land, schwieriger Job, Krankheit überwunden, Familie alleine aufgezogen — das zählt alles.",
                "examples": {
                    "good": "Ich bin mit meiner Familie nach Österreich gekommen und musste in 2 Jahren eine neue Sprache lernen, Arbeit finden und unsere Kinder in die Schule eingewöhnen. Das war schwierig, aber ich habe alles gemeistert.",
                    "bad": "Das Leben ist manchmal schwierig."
                },
                "quick_fill": [
                    "Ich habe als Zugewanderter / Zugewanderte neu angefangen.",
                    "Ich habe eine schwierige Zeit überwunden, nämlich ",
                    "Ich habe etwas alleine geschafft, was viele nicht schaffen: ",
                ],
                "helper_tip": "Diese Stärken — Mut, Ausdauer, Anpassungsfähigkeit — sind am Arbeitsmarkt sehr gefragt.",
                "min_length": 20,
                "flags": ["resilience", "soft_skills"]
            },
            {
                "id": "o_07",
                "order": 8,
                "category": "motivation",
                "text": "Was suchen Sie jetzt? Was ist Ihr nächster Schritt?",
                "hint": "Art der Arbeit, Branche, Vollzeit oder Teilzeit, nahe der Wohnung — was wünschen Sie sich?",
                "examples": {
                    "good": "Ich suche eine Stelle in der Produktion oder im Lager, Vollzeit, gerne auch Schichtarbeit. Mir ist wichtig, dass mein Deutsch kein Hindernis ist — ich verstehe Anweisungen gut.",
                    "bad": "Ich möchte einen guten Job."
                },
                "quick_fill": [
                    "Ich suche Arbeit in der Produktion / im Lager.",
                    "Ich suche Arbeit im Dienstleistungsbereich.",
                    "Ich bin für jede Arbeit offen.",
                    "Ich möchte in meinem gelernten Beruf arbeiten.",
                    "Mir ist Stabilität und feste Zeiten wichtig.",
                ],
                "helper_tip": "Sagen Sie ruhig, was Sie sich vorstellen — wir formulieren es professionell für Ihren Lebenslauf.",
                "min_length": 15,
                "flags": ["future_goals", "motivation"]
            },
        ]
    }
}

def get_interview_path(path_key: str) -> dict:
    """Get interview path configuration by key."""
    return INTERVIEW_PATHS.get(path_key)


def get_question(path_key: str, question_id: str) -> dict:
    """Get a specific question from a path."""
    path = get_interview_path(path_key)
    if not path:
        return None
    for q in path["questions"]:
        if q["id"] == question_id:
            return q
    return None


def get_all_question_ids(path_key: str) -> list:
    """Get all question IDs for a path in order."""
    path = get_interview_path(path_key)
    if not path:
        return []
    return [q["id"] for q in sorted(path["questions"], key=lambda x: x["order"])]


def get_question_by_order(path_key: str, order: int) -> dict:
    """Get question by its order number in the path."""
    path = get_interview_path(path_key)
    if not path:
        return None
    for q in path["questions"]:
        if q["order"] == order:
            return q
    return None


def get_localized_question(question: dict, language: str) -> dict:
    """
    Return a copy of *question* with text/hint/examples/quick_fill replaced by
    the requested language translation, if one exists.

    Checks translations.py QUESTION_TRANSLATIONS first (external translations file),
    then falls back to inline "translations" key in the question dict,
    then falls back to the original German fields.

    Args:
        question: Raw question dict from INTERVIEW_PATHS (German by default).
        language: ISO 639-1 code requested by the frontend (e.g. "de", "en", "tr").

    Returns:
        Dict with the same keys as the input but with localized string fields.
        The original dict is never mutated.
    """
    # German is the base language — no translation needed
    if language == "de":
        return question

    # Capture original German text for subtitle display in non-German UIs
    german_text = question.get("text", "")

    # Try external translations file first
    try:
        from interview.translations import get_question_translation
        lang_data = get_question_translation(question.get("id", ""), language)
        if lang_data:
            result = dict(question)
            result["text"] = lang_data.get("text", question["text"])
            result["hint"] = lang_data.get("hint", question["hint"])
            result["examples"] = lang_data.get("examples", question["examples"])
            result["quick_fill"] = lang_data.get("quick_fill", question.get("quick_fill", []))
            result["german_text"] = german_text
            return result
    except ImportError:
        pass

    # Fall back to inline translations dict if present
    if "translations" not in question:
        result = dict(question)
        result["german_text"] = german_text
        return result

    trans = question.get("translations", {})
    lang_data = trans.get(language) or trans.get("en")

    if not lang_data:
        result = dict(question)
        result["german_text"] = german_text
        return result

    result = dict(question)
    result["text"] = lang_data.get("text", question["text"])
    result["hint"] = lang_data.get("hint", question["hint"])
    result["examples"] = lang_data.get("examples", question["examples"])
    result["quick_fill"] = lang_data.get("quick_fill", question.get("quick_fill", []))
    result["german_text"] = german_text
    return result
