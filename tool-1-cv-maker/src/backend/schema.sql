-- AMS JobAssist - Tool 1 Database Schema
-- SQLite database for CV Maker (Tool 1)
-- Complete schema with 8 tables, indexes, and constraints for DatabaseManager

PRAGMA foreign_keys = ON;

-- Users table: stores job seekers
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table: interview sessions for each user
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    interview_path TEXT NOT NULL CHECK (interview_path IN ('unemployed', 'career-switch', 'student', 'pause', 'other')),
    language TEXT DEFAULT 'de',
    user_native_language TEXT,
    current_question INTEGER DEFAULT 1,
    progress_percent INTEGER DEFAULT 0,
    completed INTEGER DEFAULT 0,       -- 1 once the interview is finished
    approved INTEGER DEFAULT 0,        -- 1 after trainer approves the CV
    approved_at TEXT,                  -- ISO-8601 timestamp of trainer approval
    locked INTEGER DEFAULT 0,          -- 1 when trainer locks further edits
    needs_review INTEGER DEFAULT 0,    -- 1 when vague date inputs are detected
    access_token TEXT,                 -- high-entropy per-session ownership proof (DSGVO data-subject access)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Interview questions: questions and examples for each interview path
CREATE TABLE IF NOT EXISTS interview_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL UNIQUE,
    question_text TEXT NOT NULL,
    category TEXT NOT NULL,
    interview_path TEXT NOT NULL,
    question_order INTEGER NOT NULL,
    hint TEXT,
    good_example TEXT NOT NULL,
    bad_example TEXT NOT NULL,
    min_length INTEGER DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Answers: user responses during interview (raw input)
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_id TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, question_id),
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(question_id) REFERENCES interview_questions(question_id)
);

-- CV data: final polished CV and raw answers (JSON)
CREATE TABLE IF NOT EXISTS cv_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL UNIQUE,
    raw_answers TEXT,
    polished_output TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Exports: exported CVs (PDF, DOCX, JSON)
CREATE TABLE IF NOT EXISTS exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    export_type TEXT NOT NULL CHECK (export_type IN ('pdf', 'docx', 'json', 'europass', 'cover-letter')),
    file_path TEXT,
    file_size INTEGER,
    export_language TEXT DEFAULT 'de',
    export_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Cover letters: generated cover letters persisted for trainer review and iteration
CREATE TABLE IF NOT EXISTS cover_letters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    text TEXT NOT NULL,                 -- Full letter text
    language TEXT DEFAULT 'de',
    tone TEXT DEFAULT 'formal',
    job_title TEXT,
    employer_name TEXT,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- ATS scores: stored ATS analysis results so trainers can review and compare
CREATE TABLE IF NOT EXISTS ats_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    score REAL NOT NULL,                -- 0.0–1.0
    grade TEXT,                         -- Sehr gut / Gut / Ausreichend / Verbesserungsbedarf
    matched_keywords TEXT,              -- JSON array of matched keyword names
    missing_keywords TEXT,              -- JSON array of missing keyword names
    suggestions TEXT,                   -- JSON array of suggestion strings
    job_description_snippet TEXT,       -- First 200 chars of JD used (if any)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Consent records: DSGVO Art. 7 demonstrable consent. One row per interview
-- start, capturing WHO consented, WHEN, to WHICH text version, in which language.
CREATE TABLE IF NOT EXISTS consent_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    consent_given INTEGER NOT NULL,     -- 1 = given, 0 = refused (should not start)
    consent_text_version TEXT,          -- version/hash of the consent text shown
    language TEXT DEFAULT 'de',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cover_letters_session ON cover_letters(session_id);
CREATE INDEX IF NOT EXISTS idx_ats_scores_session ON ats_scores(session_id);
CREATE INDEX IF NOT EXISTS idx_consent_session ON consent_records(session_id);

-- Skills dictionary: maps user terms to normalized skills
CREATE TABLE IF NOT EXISTS skills_dictionary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_term TEXT NOT NULL UNIQUE,
    normalized_skill TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    language TEXT DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verb replacements: maps weak verbs to strong verbs
CREATE TABLE IF NOT EXISTS verb_replacements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weak_verb TEXT NOT NULL UNIQUE,
    strong_verb TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_interview_path ON sessions(interview_path);
CREATE INDEX IF NOT EXISTS idx_answers_session_id ON answers(session_id);
CREATE INDEX IF NOT EXISTS idx_interview_questions_path ON interview_questions(interview_path);
CREATE INDEX IF NOT EXISTS idx_cv_data_session_id ON cv_data(session_id);
CREATE INDEX IF NOT EXISTS idx_exports_session_id ON exports(session_id);

-- ============================================================================
-- Verb replacements — English
-- ============================================================================
INSERT OR IGNORE INTO verb_replacements (weak_verb, strong_verb, language) VALUES
('did', 'executed', 'en'),
('helped', 'supported', 'en'),
('worked', 'managed', 'en'),
('used', 'leveraged', 'en'),
('made', 'created', 'en'),
('tried', 'attempted', 'en'),
('said', 'communicated', 'en'),
('got', 'obtained', 'en'),
('went', 'proceeded', 'en'),
('came', 'arrived', 'en'),
('handled', 'managed', 'en'),
('ran', 'directed', 'en'),
('looked at', 'analyzed', 'en'),
('talked to', 'consulted', 'en'),
('set up', 'established', 'en'),
('took care of', 'administered', 'en'),
('checked', 'verified', 'en'),
('fixed', 'resolved', 'en'),
('built', 'constructed', 'en'),
('showed', 'presented', 'en');

-- ============================================================================
-- Verb replacements — Deutsch (German)
-- ============================================================================
INSERT OR IGNORE INTO verb_replacements (weak_verb, strong_verb, language) VALUES
-- Allgemeine schwache Verben → starke Alternativen
('gemacht', 'umgesetzt', 'de'),
('geholfen', 'unterstützt', 'de'),
('benutzt', 'angewendet', 'de'),
('gemacht haben', 'realisiert', 'de'),
('kontrolliert', 'überwacht', 'de'),
('bedient', 'betreut', 'de'),
('geführt', 'geleitet', 'de'),
('durchgeführt', 'koordiniert', 'de'),
('erklärt', 'vermittelt', 'de'),
('verkauft', 'vertrieben', 'de'),
('eingekauft', 'beschafft', 'de'),
('geplant', 'konzipiert', 'de'),
('geschrieben', 'verfasst', 'de'),
('geprüft', 'analysiert', 'de'),
('verbessert', 'optimiert', 'de'),
('verwaltet', 'administriert', 'de'),
('aufgebaut', 'etabliert', 'de'),
('verändert', 'transformiert', 'de'),
('angepasst', 'modifiziert', 'de'),
('gezeigt', 'präsentiert', 'de'),
('gelernt', 'erworben', 'de'),
('bekommen', 'erhalten', 'de'),
('gebracht', 'erzielt', 'de'),
('gearbeitet', 'mitgewirkt', 'de'),
('geredet', 'kommuniziert', 'de'),
('gemacht mit', 'eingesetzt', 'de'),
('gesehen', 'identifiziert', 'de'),
('gemessen', 'evaluiert', 'de'),
('zusammengestellt', 'konsolidiert', 'de'),
('gerechnet', 'kalkuliert', 'de');

-- ============================================================================
-- Skills dictionary — English
-- ============================================================================
INSERT OR IGNORE INTO skills_dictionary (key_term, normalized_skill, category, language) VALUES
('excel', 'Microsoft Excel', 'Office', 'en'),
('word', 'Microsoft Word', 'Office', 'en'),
('outlook', 'Microsoft Outlook', 'Office', 'en'),
('powerpoint', 'Microsoft PowerPoint', 'Office', 'en'),
('python', 'Python', 'Technical', 'en'),
('javascript', 'JavaScript', 'Technical', 'en'),
('java', 'Java', 'Technical', 'en'),
('sql', 'SQL', 'Technical', 'en'),
('teamwork', 'Teamwork', 'Soft', 'en'),
('leadership', 'Leadership', 'Soft', 'en'),
('communication', 'Communication', 'Soft', 'en'),
('german', 'German Language', 'Language', 'en'),
('english', 'English Language', 'Language', 'en'),
('cash register', 'Cash Register Operation', 'Retail', 'en'),
('customer service', 'Customer Service', 'Soft', 'en'),
('forklift', 'Forklift Operation', 'Technical', 'en'),
('hygiene', 'Food Hygiene (HACCP)', 'Compliance', 'en'),
('driving license', 'Driving Licence (Class B)', 'Qualification', 'en');

-- ============================================================================
-- Skills dictionary — Deutsch (German)
-- ============================================================================
INSERT OR IGNORE INTO skills_dictionary (key_term, normalized_skill, category, language) VALUES
-- Büro & IT
('excel', 'Microsoft Excel', 'Office', 'de'),
('word', 'Microsoft Word', 'Office', 'de'),
('outlook', 'Microsoft Outlook', 'Office', 'de'),
('powerpoint', 'Microsoft PowerPoint', 'Office', 'de'),
('office', 'Microsoft Office (Word, Excel, Outlook)', 'Office', 'de'),
('büroarbeit', 'Microsoft Office (Word, Excel, Outlook)', 'Office', 'de'),
('computer', 'PC-Kenntnisse (MS Office)', 'Office', 'de'),
('pc', 'PC-Kenntnisse (MS Office)', 'Office', 'de'),
('sap', 'SAP', 'ERP', 'de'),
('internet', 'Internet & E-Mail', 'Office', 'de'),
('email', 'E-Mail-Kommunikation', 'Office', 'de'),
('e-mail', 'E-Mail-Kommunikation', 'Office', 'de'),
-- Einzelhandel & Gastronomie
('kasse', 'Kassenführung', 'Retail', 'de'),
('kassieren', 'Kassenführung', 'Retail', 'de'),
('kunden', 'Kundenbetreuung', 'Soft', 'de'),
('kundenberatung', 'Kundenberatung', 'Soft', 'de'),
('kundenbetreuung', 'Kundenbetreuung', 'Soft', 'de'),
('kundenkontakt', 'Kundenkontakt', 'Soft', 'de'),
('kassenführung', 'Kassenführung', 'Retail', 'de'),
('lager', 'Lagerverwaltung', 'Logistics', 'de'),
('lagerhaltung', 'Lagerverwaltung', 'Logistics', 'de'),
('inventur', 'Inventurmanagement', 'Logistics', 'de'),
('wareneingang', 'Wareneingang & -ausgabe', 'Logistics', 'de'),
('kochen', 'Kochen & Küche', 'Gastronomy', 'de'),
('küche', 'Kochen & Küche', 'Gastronomy', 'de'),
('haccp', 'HACCP-Kenntnisse (Lebensmittelhygiene)', 'Compliance', 'de'),
('hygienevorschriften', 'HACCP-Kenntnisse (Lebensmittelhygiene)', 'Compliance', 'de'),
('lebensmittel', 'Lebensmittelhygiene', 'Compliance', 'de'),
('kellner', 'Service & Bedienung', 'Gastronomy', 'de'),
('service', 'Service & Bedienung', 'Gastronomy', 'de'),
('bedienung', 'Service & Bedienung', 'Gastronomy', 'de'),
-- Handwerk & Technik
('stapler', 'Gabelstaplerschein', 'Technical', 'de'),
('gabelstapler', 'Gabelstaplerschein', 'Technical', 'de'),
('schweißen', 'Schweißtechnik', 'Technical', 'de'),
('elektriker', 'Elektrotechnik', 'Technical', 'de'),
('montage', 'Montagetätigkeiten', 'Technical', 'de'),
('qualitätskontrolle', 'Qualitätskontrolle', 'Technical', 'de'),
('qualitätssicherung', 'Qualitätssicherung (QS)', 'Technical', 'de'),
-- Führerschein & Transport
('führerschein', 'Führerschein Klasse B', 'Qualification', 'de'),
('führerschein b', 'Führerschein Klasse B', 'Qualification', 'de'),
('führerschein c', 'Führerschein Klasse C (LKW)', 'Qualification', 'de'),
('lkw', 'LKW-Führerschein Klasse C', 'Qualification', 'de'),
-- Sozial & Pflege
('pflege', 'Pflegetätigkeiten', 'Healthcare', 'de'),
('betreuung', 'Betreuung & Pflege', 'Healthcare', 'de'),
('kinderbetreuung', 'Kinderbetreuung', 'Healthcare', 'de'),
('erste hilfe', 'Erste Hilfe', 'Qualification', 'de'),
-- Soft Skills
('teamarbeit', 'Teamfähigkeit', 'Soft', 'de'),
('teamfähigkeit', 'Teamfähigkeit', 'Soft', 'de'),
('deutsch', 'Deutschkenntnisse', 'Language', 'de'),
('englisch', 'Englischkenntnisse', 'Language', 'de'),
('kommunikation', 'Kommunikationsfähigkeit', 'Soft', 'de'),
('zuverlässigkeit', 'Zuverlässigkeit', 'Soft', 'de'),
('selbstständig', 'Selbstständige Arbeitsweise', 'Soft', 'de'),
('organisieren', 'Organisationstalent', 'Soft', 'de');

-- ============================================================================
-- Skills dictionary — Türkçe (Turkish key terms → German normalized)
-- ============================================================================
INSERT OR IGNORE INTO skills_dictionary (key_term, normalized_skill, category, language) VALUES
('kasa', 'Kassenführung', 'Retail', 'tr'),
('müşteri', 'Kundenbetreuung', 'Soft', 'tr'),
('bilgisayar', 'PC-Kenntnisse (MS Office)', 'Office', 'tr'),
('depo', 'Lagerverwaltung', 'Logistics', 'tr'),
('ekip çalışması', 'Teamfähigkeit', 'Soft', 'tr'),
('sürücü belgesi', 'Führerschein Klasse B', 'Qualification', 'tr'),
('mutfak', 'Kochen & Küche', 'Gastronomy', 'tr'),
('excel', 'Microsoft Excel', 'Office', 'tr'),
('almanca', 'Deutschkenntnisse', 'Language', 'tr'),
('ingilizce', 'Englischkenntnisse', 'Language', 'tr');

-- ============================================================================
-- Skills dictionary — عربي (Arabic key terms → German normalized)
-- ============================================================================
INSERT OR IGNORE INTO skills_dictionary (key_term, normalized_skill, category, language) VALUES
('خدمة العملاء', 'Kundenbetreuung', 'Soft', 'ar'),
('الحاسوب', 'PC-Kenntnisse (MS Office)', 'Office', 'ar'),
('المستودع', 'Lagerverwaltung', 'Logistics', 'ar'),
('العمل الجماعي', 'Teamfähigkeit', 'Soft', 'ar'),
('رخصة القيادة', 'Führerschein Klasse B', 'Qualification', 'ar'),
('الطبخ', 'Kochen & Küche', 'Gastronomy', 'ar'),
('الكمبيوتر', 'PC-Kenntnisse (MS Office)', 'Office', 'ar'),
('اللغة الألمانية', 'Deutschkenntnisse', 'Language', 'ar'),
('الإنجليزية', 'Englischkenntnisse', 'Language', 'ar'),
('التمريض', 'Pflegetätigkeiten', 'Healthcare', 'ar');
