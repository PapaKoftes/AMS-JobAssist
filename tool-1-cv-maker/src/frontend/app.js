/**
 * AMS JobAssist - CV Maker Frontend
 * Interview flow management and API integration
 */

// ============================================================================
// Constants
// ============================================================================

const SESSION_STORAGE_KEY  = 'ams_session_id';
const USER_STORAGE_KEY     = 'ams_user_id';
const TOKEN_STORAGE_KEY    = 'ams_session_token';   // per-session ownership proof
const COMPLETED_SESSION_KEY = 'ams_session_completed';
const LANGUAGE_STORAGE_KEY = 'ams_language';
const PREVIEW_DEBOUNCE_MS  = 600;
const AI_CHECK_INTERVAL_MS = 60_000; // re-check AI mode every minute

// Questions whose answers are legitimately short (a name, a city, a company,
// a job title, a date). These must NOT trigger "too short" warnings or
// follow-up probes. Keyed off the question's flags.
const SHORT_ANSWER_FLAGS = new Set([
    'identity', 'optional', 'employer_name', 'job_title',
    'date_range', 'target_job', 'photo',
]);

// Whether the current question accepts a short answer (name/city/company/etc.)
function isShortAnswerQuestion(question) {
    const flags = question?.flags ?? [];
    return flags.some(f => SHORT_ANSWER_FLAGS.has(f));
}

// Minimum characters before the Continue button enables, per question.
// Short-answer questions only need 1 char (or 0 if optional). Content
// questions use a gentle floor so people aren't blocked, while the backend
// still does the real quality re-ask.
function effectiveMinChars(question) {
    const flags = question?.flags ?? [];
    if (flags.includes('optional')) return 0;
    if (isShortAnswerQuestion(question)) return 1;
    return 3; // content questions: just require a few characters, not a full sentence
}

// Gentle follow-up probes (PHILOSOPHY.md: "If an answer is vague, the system
// asks a follow-up — once, gently. Not three times.").
// The old bug fired one after EVERY answer (structural questions weren't being
// skipped because flags weren't sent to the frontend). With flags fixed, the
// probe is gated tightly: only for genuinely vague CONTENT answers, and capped
// per interview so it never nags.
const ENABLE_FOLLOWUPS = true;
const FOLLOWUP_MAX_WORDS = 9;      // only probe answers shorter than this (vague)
const FOLLOWUP_SESSION_CAP = 2;    // never probe more than this many times total

// ============================================================================
// Living CV document — the interview happens ON a growing sheet of paper.
// As the participant answers, their words are "typed" onto the CV: the header
// fills with name / target job / contact / photo, and content sections
// (Über mich, Berufserfahrung, Ausbildung, Kenntnisse…) grow below. The current
// question is shown as a warm AMS-advisor prompt at the active "typing line".
// Reuses the interview engine — these helpers only render the document.
// ============================================================================
function _escapeHtml(s) {
    return String(s ?? '').replace(/[&<>"']/g, c => (
        {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]
    ));
}

function _scrollSheetToActive() {
    // Keep the newest CV content visible in the (scrolling) top pane.
    const pane = document.getElementById('cvTopPane');
    if (pane) requestAnimationFrame(() => { pane.scrollTop = pane.scrollHeight; });
}

function _hideSheetEmpty() {
    const e = document.getElementById('cvSheetEmpty');
    if (e) e.style.display = 'none';
}

// Section order on the CV sheet and the heading each one shows.
const _CV_SECTION_ORDER = ['profile', 'experience', 'education', 'skills', 'more'];
const _CV_SECTION_TITLES = {
    profile: 'Über mich',
    experience: 'Berufserfahrung',
    education: 'Ausbildung & Weiterbildung',
    skills: 'Kenntnisse & Stärken',
    more: 'Weitere Angaben',
};

// Map an interview question to a CV document section.
function _cvSectionFor(question) {
    const flags = question?.flags ?? [];
    const cat = question?.category ?? '';
    const has = f => flags.includes(f);
    if (has('work_experience') || has('previous_career') || has('teamwork') || cat === 'experience') return 'experience';
    if (has('education') || has('training') || has('internship') || cat === 'training' || cat === 'background') return 'education';
    if (has('technical_skills') || has('practical_skills') || has('soft_skills') ||
        has('languages') || has('interests') || cat === 'skills') return 'skills';
    if (has('motivation') || has('future_goals') || has('stability') ||
        has('resilience') || has('problem_solving') || cat === 'motivation') return 'profile';
    return 'more';
}

// Ensure a section block exists in the sheet body and return its entries node.
function _cvEnsureSection(key) {
    const body = document.getElementById('cvSheetBody');
    if (!body) return null;
    let block = body.querySelector(`.cv-doc-section[data-sec="${key}"]`);
    if (!block) {
        block = document.createElement('section');
        block.className = 'cv-doc-section';
        block.dataset.sec = key;
        block.innerHTML = `<h3 class="cv-doc-heading">${_escapeHtml(_CV_SECTION_TITLES[key] || '')}</h3>` +
                          `<div class="cv-doc-entries"></div>`;
        // Insert in canonical order
        const order = _CV_SECTION_ORDER.indexOf(key);
        const siblings = [...body.querySelectorAll('.cv-doc-section')];
        const after = siblings.find(s => _CV_SECTION_ORDER.indexOf(s.dataset.sec) > order);
        body.insertBefore(block, after || null);
    }
    return block.querySelector('.cv-doc-entries');
}

// Type text into an element, character by character (typewriter effect).
function _typeInto(el, text) {
    if (!el) return;
    const full = String(text || '');
    el.textContent = '';
    el.classList.add('cv-typing');
    let i = 0;
    const step = Math.max(6, Math.min(22, Math.round(700 / Math.max(full.length, 1))));
    const tick = () => {
        el.textContent = full.slice(0, i);
        i++;
        if (i <= full.length) {
            setTimeout(tick, step);
        } else {
            el.classList.remove('cv-typing');
            _scrollSheetToActive();   // settle the view once typing finishes
        }
    };
    tick();
    _scrollSheetToActive();
}

// Reset the whole sheet for a fresh interview.
function cvDocReset() {
    const body = document.getElementById('cvSheetBody');
    if (body) body.innerHTML = `<p class="cv-sheet-empty" id="cvSheetEmpty">${t('cvSheetEmpty') || 'Ihr Lebenslauf entsteht hier, während wir uns unterhalten…'}</p>`;
    const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
    set('cvDocName', t('cvDocNamePlaceholder') || 'Ihr Name');
    set('cvDocSubtitle', '');
    set('cvDocContact', '');
    document.getElementById('cvSheetHeader')?.classList.remove('has-name');
    const img = document.getElementById('cvPhotoImg');
    if (img) { img.style.display = 'none'; img.src = ''; }
    const plus = document.getElementById('cvPhotoPlus');
    if (plus) plus.style.display = '';
}

// Show the current question as a warm advisor prompt at the active line.
function cvDocSetPrompt(question, opts = {}) {
    const adv = document.getElementById('advisorText');
    const hintEl = document.getElementById('advisorHint');
    const exWrap = document.getElementById('advisorExample');
    if (adv) adv.textContent = question.text ?? '';
    if (hintEl) {
        hintEl.textContent = question.hint ?? '';
        hintEl.style.display = question.hint ? 'block' : 'none';
    }
    if (exWrap) {
        const ex = question.examples?.good;
        if (ex) {
            exWrap.querySelector('span').textContent = ex;
            exWrap.style.display = 'block';
        } else {
            exWrap.style.display = 'none';
        }
    }
    const prompt = document.getElementById('cvActivePrompt');
    if (prompt) prompt.classList.toggle('cv-prompt-reask', !!opts.reask);
    _scrollSheetToActive();
}

// Commit an answer onto the CV: header fields for identity, else a typed entry.
function cvDocAddAnswer(question, rawText, polishedText) {
    const qid = question?.id ?? '';
    const text = (polishedText && polishedText.trim()) ? polishedText.trim() : (rawText || '').trim();

    // Identity / header fields
    if (qid === 'id_name') {
        const e = document.getElementById('cvDocName');
        if (e) e.textContent = rawText || text;
        document.getElementById('cvSheetHeader')?.classList.add('has-name');
        return;
    }
    if (qid === 'id_target_job') {
        const e = document.getElementById('cvDocSubtitle');
        if (e) e.textContent = rawText || text;
        return;
    }
    if (qid === 'id_contact') {
        // One combined contact line (city, phone, email) — show it as-is,
        // tidied to " · " separators.
        const e = document.getElementById('cvDocContact');
        if (e) e.textContent = (rawText || text).split(/[,\n;]+/).map(s => s.trim()).filter(Boolean).join(' · ');
        return;
    }
    if (qid === 'id_location' || qid === 'id_phone' || qid === 'id_email') {
        const e = document.getElementById('cvDocContact');
        if (e) {
            const parts = e.textContent ? e.textContent.split(' · ') : [];
            const val = (rawText || text);
            if (val && !parts.includes(val)) parts.push(val);
            e.textContent = parts.join(' · ');
        }
        return;
    }
    if ((question?.flags || []).includes('photo')) {
        return; // photo handled by the header slot
    }

    // Content → a typed CV entry under the right section.
    _hideSheetEmpty();
    const entries = _cvEnsureSection(_cvSectionFor(question));
    if (!entries) return;
    const entry = document.createElement('div');
    entry.className = 'cv-doc-entry';
    entries.appendChild(entry);
    _typeInto(entry, text);
}

// ---- Conversation thread (bottom pane) -------------------------------------
function _convScroll() {
    const m = document.getElementById('convMessages');
    if (m) requestAnimationFrame(() => { m.scrollTop = m.scrollHeight; });
}
/** Append the participant's message to the conversation. */
function convAddUser(text) {
    const m = document.getElementById('convMessages');
    if (!m) return;
    const row = document.createElement('div');
    row.className = 'conv-row conv-user';
    row.innerHTML = `<div class="conv-user-bubble">${_escapeHtml(text)}</div>`;
    m.appendChild(row);
    _convScroll();
}
/** Append an assistant message (question / guidance) to the conversation. */
function convAddAI(text, hint) {
    const m = document.getElementById('convMessages');
    if (!m) return;
    const row = document.createElement('div');
    row.className = 'conv-row conv-ai';
    row.innerHTML = `<span class="advisor-avatar" aria-hidden="true">🧑‍💼</span>` +
        `<div class="advisor-bubble"><div class="advisor-text">${_escapeHtml(text)}</div>` +
        (hint ? `<div class="advisor-hint">${_escapeHtml(hint)}</div>` : '') + `</div>`;
    m.appendChild(row);
    _convScroll();
}
function convThinking(on) {
    const m = document.getElementById('convMessages');
    if (!m) return;
    let t = document.getElementById('convThinking');
    if (on) {
        if (!t) {
            t = document.createElement('div');
            t.id = 'convThinking'; t.className = 'conv-row conv-ai';
            t.innerHTML = `<span class="advisor-avatar">🧑‍💼</span><div class="advisor-bubble advisor-thinking">…</div>`;
            m.appendChild(t); _convScroll();
        }
    } else if (t) {
        t.remove();
    }
}

// ============================================================================
// i18n — UI label translations for 12 languages
// Interview questions come from the backend already translated.
// This covers all static UI chrome: buttons, labels, placeholders, hints.
// ============================================================================

const TRANSLATIONS = {
    de: {
        answerLabel:          'Ihre Antwort — schreiben Sie in jeder Sprache, die Sie möchten:',
        answerPlaceholder:    'Erzählen Sie einfach drauf los — so viel Sie möchten, in jeder Sprache. Ich ordne es für Sie.',
        cvSheetEmpty:         'Ihr Lebenslauf entsteht hier, während wir uns unterhalten…',
        cvDocNamePlaceholder: 'Ihr Name',
        dumpPrompt:           'Erzählen Sie mir alles über sich.',
        dumpHint:             'Ihr Name, wo Sie wohnen, Ihre Arbeit, Ausbildung, Fähigkeiten — schreiben Sie so viel Sie möchten, in jeder Sprache. Ich ordne alles für Ihren Lebenslauf.',
        // Path-aware openings — the chosen path changes what we ask for first.
        dumpPromptUnemployed:   'Erzählen Sie mir alles über sich — beginnen Sie am besten mit Ihrer letzten Arbeit.',
        dumpPromptCareerSwitch: 'Erzählen Sie mir alles über sich — was haben Sie bisher gearbeitet, und was möchten Sie jetzt machen?',
        dumpPromptStudent:      'Erzählen Sie mir alles über sich — Ihre Ausbildung, Praktika und Nebenjobs zuerst.',
        dumpPromptPause:        'Erzählen Sie mir alles über sich — auch, was Sie vor Ihrer Pause gearbeitet haben. Die Pause ist völlig in Ordnung.',
        // Interview mode switch (free conversation ↔ guided step-by-step)
        modeSwitchToGuided:   'Lieber Schritt für Schritt?',
        modeSwitchToFree:     'Lieber frei erzählen?',
        guidedSwitchMsg:      'Gern! Ich stelle Ihnen einfache Fragen — eine nach der anderen. Sie können jederzeit zurückwechseln.',
        freeSwitchMsg:        'Gern! Erzählen Sie einfach frei — ich ordne alles für Sie.',
        // Application email (the ready-to-send Bewerbungs-E-Mail)
        appEmailBtn:          '📧 Bewerbungs-E-Mail erstellen',
        appEmailHeading:      '📧 Ihre Bewerbungs-E-Mail',
        appEmailToLabel:      'An (E-Mail der Firma, optional):',
        appEmailSubjLabel:    'Betreff:',
        appEmailHint:         (hasCL) => hasCL
            ? 'Wichtig: Hängen Sie den heruntergeladenen Lebenslauf (PDF) an. Ihr Anschreiben können Sie zusätzlich anhängen.'
            : 'Wichtig: Hängen Sie den heruntergeladenen Lebenslauf (PDF) an die E-Mail an.',
        appEmailOpen:         'In E-Mail-Programm öffnen ↗',
        appEmailCopy:         'Text kopieren',
        appEmailCopied:       '✓ Kopiert',
        appEmailClose:        'Schließen',
        appEmailFallbackJob:  'die ausgeschriebene Stelle',
        appEmailSubject:      (job, name) => `Bewerbung als ${job}` + (name ? ` – ${name}` : ''),
        appEmailBody: (job, name, contact) =>
            `Sehr geehrte Damen und Herren,\n\n` +
            `mit großem Interesse bewerbe ich mich um die Stelle als ${job}. ` +
            `Meine Qualifikationen und meine bisherige Erfahrung entnehmen Sie bitte dem beigefügten Lebenslauf.\n\n` +
            `Über eine Einladung zu einem persönlichen Gespräch freue ich mich sehr.\n\n` +
            `Mit freundlichen Grüßen\n${name || ''}` + (contact ? `\n${contact}` : ''),
        dumpPlaceholder:      'z.B. Ich heiße Maria, wohne in Wien, habe 5 Jahre in einer Bäckerei gearbeitet…',
        dumpThinking:         'Einen Moment — ich ordne das für Ihren Lebenslauf…',
        dumpKeepGoing:        'Oder erzählen Sie einfach weiter.',
        dumpAnythingElse:     'Super! Möchten Sie noch etwas ergänzen? Wenn nicht, klicken Sie auf „Lebenslauf erstellen".',
        dumpError:            'Das hat nicht ganz geklappt — erzählen Sie es einfach noch einmal.',
        dumpFinishLabel:      'Lebenslauf erstellen',
        dumpSend:             'Senden →',
        // Conversational gap questions (use {job} placeholder where supported).
        dumpGaps: {
            experience_detail: { text: 'Erzählen Sie mir mehr über Ihre Arbeit als {job} — wo haben Sie gearbeitet, wie lange, und was waren Ihre Aufgaben?',
                                 textNoJob: 'Erzählen Sie mir mehr über Ihre letzte Arbeit — wo, wie lange, und was haben Sie gemacht?',
                                 hint: 'Firma, Zeitraum und Ihre wichtigsten Aufgaben.', expect: 'experience_detail' },
            experience: { text: 'Erzählen Sie mir von Ihrer Berufserfahrung — wo haben Sie gearbeitet und was haben Sie gemacht?',
                          hint: 'Auch kurze oder ältere Jobs zählen.', expect: 'experience' },
            education:  { text: 'Welche Ausbildung, Kurse oder Abschlüsse haben Sie?',
                          hint: 'Schule, Lehre, Kurse, Zertifikate — alles zählt.', expect: 'education' },
            skills:     { text: 'Welche Stärken und Kenntnisse haben Sie noch?',
                          hint: 'Sprachen, Computer, Maschinen, Soft Skills…', expect: 'skills' },
            target_job: { text: 'Und welche Stelle suchen Sie jetzt?',
                          hint: 'Berufsbezeichnung oder Bereich reicht.', expect: 'target_job' },
            contact:    { text: 'Wie kann man Sie erreichen?',
                          hint: 'Stadt, Telefon, E-Mail — was Sie angeben möchten.', expect: 'contact' },
            name:       { text: 'Wie heißen Sie? (Vor- und Nachname)', hint: '', expect: 'name' },
        },
        dumpEnrichment: [
            { key: 'languages',  expect: 'skills',     text: 'Welche Sprachen sprechen Sie — und wie gut?', hint: 'z.B. Deutsch B1, Bosnisch Muttersprache, Englisch Grundkenntnisse.' },
            { key: 'tools',      expect: 'skills',     text: 'Welche Computerprogramme, Werkzeuge oder Maschinen können Sie bedienen?', hint: 'z.B. MS Office, Stapler, CNC, Kassensystem…' },
            { key: 'certs',      expect: 'education',   text: 'Haben Sie Zertifikate, einen Führerschein oder andere Nachweise?', hint: 'z.B. Führerschein B, Staplerschein, Erste-Hilfe-Kurs.' },
            { key: 'strengths',  expect: 'skills',     text: 'Was sind Ihre größten persönlichen Stärken?', hint: 'z.B. zuverlässig, teamfähig, lernbereit, belastbar.' },
            { key: 'motivation', expect: 'motivation', text: 'Zum Schluss: Warum interessiert Sie diese Art von Arbeit?', hint: 'Ein, zwei Sätze genügen — das macht Ihre Bewerbung persönlich.' },
        ],
        // ✓ acknowledgement labels for captured fields (joined into "✓ Übernommen: …").
        dumpAckPrefix: '✓ Übernommen:',
        dumpAckName: 'Name', dumpAckTarget: 'Zielberuf', dumpAckContact: 'Kontakt',
        dumpAckExperience: 'Berufserfahrung', dumpAckEducation: 'Ausbildung', dumpAckSkills: 'Kenntnisse',
        dumpAckNoted: '✓ Notiert.',
        askName:              'Wie heißen Sie? (Vor- und Nachname)',
        askContact:           'Wo wohnen Sie, und wie kann man Sie erreichen? (Stadt, Telefon, E-Mail)',
        askTarget:            'Welche Stelle suchen Sie?',
        askSkills:            'Welche Stärken oder Kenntnisse haben Sie? (z.B. Sprachen, Computer, Maschinen)',
        submitBtn:            'Weiter →',
        skipBtn:              'Frage überspringen',
        previewTitle:         'So sieht es in Ihrem Lebenslauf aus',
        previewRawLabel:      'Was Sie geschrieben haben',
        previewPolishedLabel: 'In Ihrem Lebenslauf',
        previewLoading:       'Wird verbessert…',
        wordSingular:         'Wort',
        wordPlural:           'Wörter',
        qualityShort:         'Etwas kurz — fügen Sie noch ein Detail hinzu',
        qualityShortA:        'Ein wenig knapp — was haben Sie konkret gemacht?',
        qualityShortB:        'Vielleicht ein Beispiel oder ein Werkzeug ergänzen?',
        qualityOk:            'Guter Anfang — ein bisschen mehr würde helfen',
        qualityOkA:           'Schön — vielleicht noch ein Detail dazu?',
        qualityOkB:           'Gut so weit — eine Aufgabe oder ein Werkzeug erwähnen?',
        qualityGood:          'Sehr gut, das reicht!',
        qualityGoodA:         'Stark — genug Information für den Lebenslauf!',
        qualityGoodB:         'Ausgezeichnet — wir haben genug zum Verbessern.',
        langNote:             'Sie können immer mehrsprachig schreiben — das System erkennt jede Sprache automatisch.',
        step1Text:            'Was beschreibt Ihre aktuelle Situation am besten?',
        step2Text:            'Wie heißen Sie?',
        namePlaceholder:      'Ihren Vornamen eingeben — z.B. Maria',
        startBtn:             'Meinen Lebenslauf erstellen →',
        startHintReady:       'Alles bereit — klicken Sie auf die Schaltfläche!',
        startHintBoth:        'Bitte wählen Sie oben Ihre Situation aus und geben Sie Ihren Namen ein.',
        startHintPath:        'Bitte wählen Sie oben Ihre Situation aus.',
        startHintName:        'Bitte geben Sie Ihren Vornamen ein.',
        startHintConsent:     '☑ Bitte bestätigen Sie das Kästchen oben (Datenschutz).',
        progressLabel:        (cur, tot) => `Frage ${cur} von ${tot}`,
        cvProgressLabel:      'Ihr Lebenslauf',
        fieldName: 'Name', fieldAddress: 'Adresse', fieldPhone: 'Telefon', fieldEmail: 'E-Mail',
        fieldExperience: 'Berufserfahrung', fieldEducation: 'Ausbildung', fieldSkills: 'Kenntnisse', fieldTarget: 'Zielberuf',
        stillMissing: 'Noch offen', allFieldsDone: 'Alle Felder ausgefüllt',
        detectedLang:         (lang) => `Erkannte Sprache: ${lang}`,
        resumeWelcomeStrong:  'Willkommen zurück!',
        resumeBtn:            'Weiter wo ich aufgehört habe',
        dismissResumeBtn:     'Neu beginnen',
        resumeWelcome:        (name) => name ? `Willkommen zurück, ${name}! Ihr Lebenslauf wartet auf Sie.` : 'Sie haben ein Interview in Bearbeitung.',
        appSubtitle:          'Ihr professioneller Lebenslauf — in jeder Sprache',
        trustHeadline:        'Wir verwandeln Ihre Antworten automatisch in einen professionellen Lebenslauf.',
        trustDetail1:         '⏱ Etwa 10–15 Minuten',
        trustDetail2:         '💾 Fortschritt nach jeder Antwort gespeichert',
        trustDetail3:         '🌐 Schreiben Sie in jeder Sprache',
        exampleGoodTitle:     '✅ Gutes Beispiel',
        exampleBadTitle:      '❌ Weniger hilfreich',
        quickFillLabel:       'Schnellstart — klicken zum Einfügen:',
        reaskTip:             'Tipp',
        pathUnemployedLabel:  'Jobsuchend',
        pathUnemployedDesc:   'Auf der Suche nach Arbeit oder Wiedereinstieg',
        pathCareerLabel:      'Berufswechsel',
        pathCareerDesc:       'Wechsel in ein neues Berufsfeld oder eine andere Branche',
        pathStudentLabel:     'Schüler/in oder Student/in',
        pathStudentDesc:      'In Ausbildung oder kurz vor dem Abschluss',
        pathPauseLabel:       'Berufliche Pause',
        pathPauseDesc:        'Rückkehr nach einer Zeit ohne Arbeit',
        pathOtherLabel:       'Sonstiges',
        pathOtherDesc:        'Meine Situation ist etwas anders',
        completionHeading:    'Ihr Lebenslauf ist fertig 🎉',
        completionSubtitle:   'Ihre Antworten wurden verbessert und gespeichert. Laden Sie Ihren Lebenslauf unten herunter.',
        completionStats:      (ans, skipped) => `${ans} beantwortet · ${skipped} übersprungen`,
        exportPdf:            '⬇ PDF herunterladen',
        exportDocx:           '⬇ Word herunterladen (.docx)',
        exportJson:           '⬇ Daten exportieren (für Trainer)',
        exportRetry:          'Erneut versuchen',
        atsHeading:           '🎯 Wie gut passt Ihr Lebenslauf?',
        atsMatchedLabel:      'Gefundene Schlüsselwörter',
        atsMissingLabel:      'Fehlende Schlüsselwörter',
        atsBtn:               '🎯 Lebenslauf analysieren',
        atsAnalyzing:         'Wird analysiert...',
        jobSearchBtn:         '🔎 Passende Jobs beim AMS finden',
        jobSearchNotice:      (occ) => `Wir öffnen die AMS-Jobbörse in Ihrem Browser` +
                              (occ ? ` mit der Suche „${occ}“` : '') +
                              `. Dabei wird NUR Ihr Suchbegriff an das AMS übermittelt — ` +
                              `Ihr Name, Ihre Kontaktdaten und Ihr Lebenslauf werden NICHT gesendet.`,
        jobSearchOpen:        'Beim AMS suchen ↗',
        jobSearchCancel:      'Abbrechen',
        jobSearchLoopHint:    'Tipp: Kopieren Sie eine passende Stelle und fügen Sie sie ' +
                              'oben bei „Stellenanzeige einfügen“ ein — dann sehen Sie, ' +
                              'wie gut Ihr Lebenslauf dazu passt.',
        coverLetterHeading:   '✉️ Ihr Anschreiben',
        coverLetterBtn:       '✉️ Anschreiben erstellen',
        coverLetterCreating:  'Wird erstellt...',
        downloadTxt:          'Als .txt speichern',
        copyToClipboard:      'Kopieren',
        copied:               'Kopiert!',
        cvPanelEmpty:         'Ihr Lebenslauf wird hier aufgebaut…',
        reviewEmpty:          'Noch keine Antworten zum Überprüfen.',
        reviewBtn:            '📋 Vorher & Nachher ansehen',
        startOverBtn:         'Neuen Lebenslauf beginnen',
        reviewHeading:        'Vorher & Nachher — Ihre Antworten verbessert',
        reviewSubtitle:       'Das sieht Ihr Trainer, wenn er Ihre Arbeit überprüft.',
        closeReviewBtn:       '← Zurück zu meinem Lebenslauf',
        reviewColRaw:         'Was Sie geschrieben haben',
        reviewColPolished:    'In Ihrem Lebenslauf',
        confirmStartOver:     'Dadurch wird Ihr aktueller Fortschritt gelöscht.\n\nMöchten Sie wirklich einen neuen Lebenslauf beginnen?',
        profileSummaryLoading: 'Ihr Profil wird analysiert…',
        profileSummaryHeading: '💡 Ihr Stärkenprofil',
        consentText: 'Ich verstehe, dass meine Antworten nur auf diesem Computer gespeichert werden und nicht ins Internet übertragen werden.',
        qualityHighText:      'Starker Lebenslauf — das hinterlässt einen guten Eindruck.',
        qualityHighTip:       'Jetzt herunterladen und teilen!',
        qualityMedText:       'Guter Lebenslauf — ein paar kleine Ergänzungen würden ihn noch besser machen.',
        qualityMedTip1:       'Fügen Sie noch ein Detail zu Ihrer Erfahrung hinzu',
        qualityMedTip2:       'Erwähnen Sie verwendete Werkzeuge oder Software',
        qualityLowText:       'Ein solider Anfang — mehr Details würden ihn stärken.',
        qualityLowTip1:       'Beschreiben Sie einen typischen Arbeitstag bei Ihrem letzten Job',
        qualityLowTip2:       'Nennen Sie Fähigkeiten oder Werkzeuge, die Sie kennen',
        qualityLowTip3:       'Erwähnen Sie Kurse oder Zertifikate',
        qualityBaseText:      'Ihr Lebenslauf hat die Grundlagen — etwas mehr Detail würde wirklich helfen.',
        qualityBaseTip1:      'Ergänzen Sie übersprungene Fragen',
        qualityBaseTip2:      'Schon ein Satz pro Abschnitt macht einen Unterschied',
        statusSaving:         'Wird gespeichert…',
        statusSaved:          'Gespeichert ✓',
        statusReady:          'Bereit',
        statusError:          'Fehler',
        statusStarting:       'Wird gestartet…',
        statusResuming:       'Wird fortgesetzt…',
        statusSkipping:       'Wird übersprungen…',
        statusBuilding:       'Lebenslauf wird erstellt…',
        statusDone:           'Fertig ✓',
        noSessionError:       'Keine aktive Sitzung — bitte schließen Sie zuerst das Interview ab.',
        exportPreparing:      (fmt) => `${fmt}-Download wird vorbereitet…`,
        exportSuccess:        (name) => `${name} heruntergeladen.`,
        exportFailed:         (msg) => `Download fehlgeschlagen: ${msg}`,
        coverLetterError:     (msg) => `Anschreiben konnte nicht erstellt werden: ${msg}`,
        // ATS input
        atsInputHeading:      '🎯 Stellenanzeige einfügen — so vergleichen wir Ihren Lebenslauf',
        atsInputDesc:         'Kopieren Sie die Stellenanzeige in das Feld unten. Das System findet automatisch die passenden Schlüsselwörter.',
        jobDescPlaceholder:   'Stellenanzeige hier einfügen — zum Beispiel von AMS, karriere.at oder dem Unternehmen direkt...',
        runAtsBtn:            'Lebenslauf analysieren →',
        cancelAtsBtn:         'Abbrechen',
        // Cover letter input
        clInputHeading:       '✉️ Anschreiben personalisieren',
        clCompanyLabel:       'Unternehmen / Arbeitgeber:',
        clCompanyPlaceholder: 'z.B. BILLA AG, Huber GmbH, AMS Wien',
        clPositionLabel:      'Stelle / Berufsbezeichnung:',
        clPositionPlaceholder:'z.B. Lagermitarbeiter/in, Reinigungskraft, Bürokauffrau',
        generateCLBtn:        'Anschreiben erstellen →',
        cancelCLBtn:          'Abbrechen',
        // Photo upload
        photoUploadLabel:     'Foto auswählen (optional)',
        photoHint:            'Professionelles Foto — optional. Österreichische Arbeitgeber erwarten oft ein Foto im Lebenslauf.',
        photoSkipLabel:       'Ohne Foto fortfahren',
        // Date helper
        dateFromLabel:        'Von:',
        dateToLabel:          'Bis:',
        dateFromPlaceholder:  'z.B. Jän 2019, 2019, ca. 2019',
        dateToPlaceholder:    'z.B. März 2022, heute, noch nicht beendet',
        dateHelperInsertBtn:  'In Antwortfeld einfügen ↓',
        dateHelperCompose:    (from, to) => `Von ${from} bis ${to}`,
        confirmDiscard:        'Wirklich neu beginnen?',
        previewPlaceholderHint:'Schreiben Sie weiter — hier sehen Sie das Ergebnis',
        typeMoreHint:          'Bitte etwas mehr schreiben…',
        midwayEncouragement:   'Sie haben den schwierigsten Teil bereits geschafft.',
        finishLaterBtn:        'Später weitermachen',
        finishLaterHint:       'Ihr Fortschritt ist gespeichert. Sie können jederzeit zurückkehren.',
        completionMoreSummary: 'Weitere Optionen',
    },
    en: {
        answerLabel:          'Your answer — write in any language you like:',
        answerPlaceholder:    'Just start writing — even rough notes are fine. We\'ll improve it automatically.',
        submitBtn:            'Next →',
        skipBtn:              'Skip question',
        previewTitle:         'This is how it looks in your CV',
        previewRawLabel:      'What you wrote',
        previewPolishedLabel: 'In your CV',
        previewLoading:       'Improving…',
        wordSingular:         'word',
        wordPlural:           'words',
        qualityShort:         'A bit short — add one more detail',
        qualityShortA:        'Slightly brief — what exactly did you do?',
        qualityShortB:        'Could you add an example or a tool you used?',
        qualityOk:            'Good start — a little more would help',
        qualityOkA:           'Nice — maybe one more detail?',
        qualityOkB:           'Looking good — a task or tool to mention?',
        qualityGood:          'Great — that\'s enough!',
        qualityGoodA:         'Strong — plenty for the CV!',
        qualityGoodB:         'Excellent — we have enough to polish.',
        langNote:             'You can always write in multiple languages — the system detects each language automatically.',
        step1Text:            'What best describes your current situation?',
        step2Text:            'What is your name?',
        namePlaceholder:      'Enter your first name — e.g. Maria',
        startBtn:             'Create my CV →',
        startHintReady:       'All ready — click the button!',
        startHintBoth:        'Please select your situation above and enter your name.',
        startHintPath:        'Please select your situation above.',
        startHintName:        'Please enter your first name.',
        startHintConsent:     '☑ Please tick the box above (data privacy).',
        progressLabel:        (cur, tot) => `Question ${cur} of ${tot}`,
        detectedLang:         (lang) => `Detected language: ${lang}`,
        resumeWelcomeStrong:  'Welcome back!',
        resumeBtn:            'Continue where I left off',
        dismissResumeBtn:     'Start fresh',
        resumeWelcome:        (name) => name ? `Welcome back, ${name}! Your CV is waiting for you.` : 'You have an interview in progress.',
        // Free-form dump flow (English)
        dumpPrompt:           'Tell me everything about yourself.',
        dumpHint:             'Your name, where you live, your work, education, skills — write as much as you like, in any language. I will organise it all for your CV.',
        dumpPromptUnemployed:   'Tell me everything about yourself — best to start with your most recent job.',
        dumpPromptCareerSwitch: 'Tell me everything about yourself — what have you worked as so far, and what would you like to do now?',
        dumpPromptStudent:      'Tell me everything about yourself — your education, internships and side jobs first.',
        dumpPromptPause:        'Tell me everything about yourself — including what you worked before your break. The break is completely fine.',
        modeSwitchToGuided:   'Prefer step by step?',
        modeSwitchToFree:     'Prefer to tell it freely?',
        guidedSwitchMsg:      'Sure! I will ask you simple questions — one at a time. You can switch back anytime.',
        freeSwitchMsg:        'Sure! Just tell your story freely — I will organise everything for you.',
        appEmailBtn:          '📧 Create application email',
        appEmailHeading:      '📧 Your application email',
        appEmailToLabel:      'To (company email, optional):',
        appEmailSubjLabel:    'Subject:',
        appEmailHint:         (hasCL) => hasCL
            ? 'Important: attach the downloaded CV (PDF). You can also attach your cover letter.'
            : 'Important: attach the downloaded CV (PDF) to the email.',
        appEmailOpen:         'Open in email program ↗',
        appEmailCopy:         'Copy text',
        appEmailCopied:       '✓ Copied',
        appEmailClose:        'Close',
        appEmailFallbackJob:  'the advertised position',
        appEmailSubject:      (job, name) => `Application for ${job}` + (name ? ` – ${name}` : ''),
        appEmailBody: (job, name, contact) =>
            `Dear Sir or Madam,\n\n` +
            `I am writing to apply with great interest for the position of ${job}. ` +
            `Please find my qualifications and experience in the attached CV.\n\n` +
            `I would be delighted to be invited to a personal interview.\n\n` +
            `Kind regards\n${name || ''}` + (contact ? `\n${contact}` : ''),
        dumpPlaceholder:      'e.g. My name is Maria, I live in Vienna, I worked 5 years in a bakery…',
        dumpThinking:         'One moment — I am organising this for your CV…',
        dumpKeepGoing:        'Or just keep telling me more.',
        dumpAnythingElse:     'Great! Would you like to add anything else? If not, click “Create CV”.',
        dumpError:            'That didn’t quite work — your text is still here, just send it again.',
        dumpFinishLabel:      'Create CV',
        dumpSend:             'Send →',
        dumpGaps: {
            experience_detail: { text: 'Tell me more about your work as {job} — where did you work, for how long, and what were your tasks?',
                                 textNoJob: 'Tell me more about your last job — where, how long, and what did you do?',
                                 hint: 'Company, time period and your main tasks.', expect: 'experience_detail' },
            experience: { text: 'Tell me about your work experience — where did you work and what did you do?',
                          hint: 'Short or older jobs count too.', expect: 'experience' },
            education:  { text: 'What education, courses or qualifications do you have?',
                          hint: 'School, apprenticeship, courses, certificates — it all counts.', expect: 'education' },
            skills:     { text: 'What other strengths and skills do you have?',
                          hint: 'Languages, computer, machines, soft skills…', expect: 'skills' },
            target_job: { text: 'And what job are you looking for now?',
                          hint: 'A job title or field is enough.', expect: 'target_job' },
            contact:    { text: 'How can people reach you?',
                          hint: 'City, phone, email — whatever you’d like to share.', expect: 'contact' },
            name:       { text: 'What is your name? (First and last name)', hint: '', expect: 'name' },
        },
        dumpEnrichment: [
            { key: 'languages',  expect: 'skills',     text: 'Which languages do you speak — and how well?', hint: 'e.g. German B1, Bosnian native, English basic.' },
            { key: 'tools',      expect: 'skills',     text: 'Which computer programs, tools or machines can you operate?', hint: 'e.g. MS Office, forklift, CNC, POS system…' },
            { key: 'certs',      expect: 'education',   text: 'Do you have any certificates, a driving licence or other proof?', hint: 'e.g. Driving licence B, forklift licence, first-aid course.' },
            { key: 'strengths',  expect: 'skills',     text: 'What are your greatest personal strengths?', hint: 'e.g. reliable, team player, eager to learn, resilient.' },
            { key: 'motivation', expect: 'motivation', text: 'Finally: why does this kind of work interest you?', hint: 'One or two sentences is enough — it makes your application personal.' },
        ],
        dumpAckPrefix: '✓ Captured:',
        dumpAckName: 'Name', dumpAckTarget: 'Target job', dumpAckContact: 'Contact',
        dumpAckExperience: 'Work experience', dumpAckEducation: 'Education', dumpAckSkills: 'Skills',
        dumpAckNoted: '✓ Noted.',
        appSubtitle:          'Your professional CV — in any language',
        cvProgressLabel:      'Your CV',
        fieldName: 'Name', fieldAddress: 'Address', fieldPhone: 'Phone', fieldEmail: 'Email',
        fieldExperience: 'Work experience', fieldEducation: 'Education', fieldSkills: 'Skills', fieldTarget: 'Target job',
        stillMissing: 'Still needed', allFieldsDone: 'All fields complete',
        trustHeadline:        'We automatically turn your answers into a professional CV.',
        trustDetail1:         '⏱ About 10–15 minutes',
        trustDetail2:         '💾 Progress saved after every answer',
        trustDetail3:         '🌐 Write in any language',
        exampleGoodTitle:     '✅ Good example',
        exampleBadTitle:      '❌ Less helpful',
        quickFillLabel:       'Quick start — click to insert:',
        reaskTip:             'Tip',
        pathUnemployedLabel:  'Job Seeking',
        pathUnemployedDesc:   'Looking for work or returning to employment',
        pathCareerLabel:      'Career Change',
        pathCareerDesc:       'Moving to a new field or industry',
        pathStudentLabel:     'Student or Apprentice',
        pathStudentDesc:      'In education or about to finish',
        pathPauseLabel:       'Career Break',
        pathPauseDesc:        'Returning after time away from work',
        pathOtherLabel:       'Other',
        pathOtherDesc:        'My situation is a bit different',
        completionHeading:    'Your CV is ready 🎉',
        completionSubtitle:   'Your answers have been improved and saved. Download your CV below.',
        completionStats:      (ans, skipped) => `${ans} answered · ${skipped} skipped`,
        exportPdf:            '⬇ Download PDF',
        exportDocx:           '⬇ Download Word (.docx)',
        exportJson:           '⬇ Export data (for trainer)',
        exportRetry:          'Try again',
        atsHeading:           '🎯 How well does your CV match?',
        atsMatchedLabel:      'Matched keywords',
        atsMissingLabel:      'Missing keywords',
        atsBtn:               '🎯 Analyse CV',
        atsAnalyzing:         'Analysing...',
        jobSearchBtn:         '🔎 Find matching jobs at the AMS',
        jobSearchNotice:      (occ) => `We will open the AMS job portal in your browser` +
                              (occ ? ` with the search “${occ}”` : '') +
                              `. Only your search term is sent to the AMS — ` +
                              `your name, contact details and CV are NOT sent.`,
        jobSearchOpen:        'Search at the AMS ↗',
        jobSearchCancel:      'Cancel',
        jobSearchLoopHint:    'Tip: copy a job you like and paste it above under ' +
                              '“Paste job posting” to see how well your CV matches it.',
        coverLetterHeading:   '✉️ Your cover letter',
        coverLetterBtn:       '✉️ Create cover letter',
        coverLetterCreating:  'Creating...',
        downloadTxt:          'Save as .txt',
        copyToClipboard:      'Copy',
        copied:               'Copied!',
        cvPanelEmpty:         'Your CV is being built here…',
        reviewEmpty:          'No answers to review yet.',
        reviewBtn:            '📋 View Before & After',
        startOverBtn:         'Start a new CV',
        reviewHeading:        'Before & After — Your answers improved',
        reviewSubtitle:       'This is what your trainer sees when reviewing your work.',
        closeReviewBtn:       '← Back to my CV',
        reviewColRaw:         'What you wrote',
        reviewColPolished:    'In your CV',
        confirmStartOver:     'This will delete your current progress.\n\nDo you really want to start a new CV?',
        consentText: 'I understand that my answers are saved on this computer only and are not transmitted to the internet.',
        profileSummaryLoading: 'Analysing your profile…',
        profileSummaryHeading: '💡 Your strengths profile',
        qualityHighText:      'Strong CV — this will make a great impression.',
        qualityHighTip:       'Download and share it now!',
        qualityMedText:       'Good CV — a few small additions would make it even better.',
        qualityMedTip1:       'Add one more detail to your experience',
        qualityMedTip2:       'Mention tools or software you used',
        qualityLowText:       'A solid start — more details would strengthen it.',
        qualityLowTip1:       'Describe a typical day at your last job',
        qualityLowTip2:       'Name skills or tools you know',
        qualityLowTip3:       'Mention courses or certificates',
        qualityBaseText:      'Your CV has the basics — a bit more detail would really help.',
        qualityBaseTip1:      'Fill in any questions you skipped',
        qualityBaseTip2:      'Even one sentence per section makes a difference',
        statusSaving:         'Saving…',
        statusSaved:          'Saved ✓',
        statusReady:          'Ready',
        statusError:          'Error',
        statusStarting:       'Starting…',
        statusResuming:       'Resuming…',
        statusSkipping:       'Skipping…',
        statusBuilding:       'Building CV…',
        statusDone:           'Done ✓',
        noSessionError:       'No active session — please complete the interview first.',
        exportPreparing:      (fmt) => `Preparing ${fmt} download…`,
        exportSuccess:        (name) => `${name} downloaded.`,
        exportFailed:         (msg) => `Download failed: ${msg}`,
        coverLetterError:     (msg) => `Could not create cover letter: ${msg}`,
        atsInputHeading:      '🎯 Paste job listing — we\'ll compare it with your CV',
        atsInputDesc:         'Paste the job ad you want to apply for below. The system will automatically find matching keywords.',
        jobDescPlaceholder:   'Paste job listing here — e.g. from AMS, karriere.at or directly from the company...',
        runAtsBtn:            'Analyse CV →',
        cancelAtsBtn:         'Cancel',
        clInputHeading:       '✉️ Personalise cover letter',
        clCompanyLabel:       'Company / Employer:',
        clCompanyPlaceholder: 'e.g. BILLA AG, Huber GmbH, AMS Wien',
        clPositionLabel:      'Position / Job title:',
        clPositionPlaceholder:'e.g. Warehouse worker, Cleaner, Office administrator',
        generateCLBtn:        'Create cover letter →',
        cancelCLBtn:          'Cancel',
        photoUploadLabel:     'Choose photo (optional)',
        photoHint:            'Professional photo — optional. Austrian employers often expect a photo in the CV.',
        photoSkipLabel:       'Continue without photo',
        dateFromLabel:        'From:',
        dateToLabel:          'To:',
        dateFromPlaceholder:  'e.g. Jan 2019, 2019, approx. 2019',
        dateToPlaceholder:    'e.g. Mar 2022, present, not yet finished',
        dateHelperInsertBtn:  'Insert into answer field ↓',
        dateHelperCompose:    (from, to) => `From ${from} to ${to}`,
        confirmDiscard:        'Really start fresh?',
        previewPlaceholderHint:'Keep writing — you\'ll see the result here',
        typeMoreHint:          'Please write a bit more…',
        midwayEncouragement:   'You\'re past the hardest part already.',
        finishLaterBtn:        'Continue later',
        finishLaterHint:       'Your progress is saved. You can return any time.',
        completionMoreSummary: 'More options',
    },
    bs: {
        dumpPromptUnemployed:   "Ispričajte mi sve o sebi — najbolje počnite od posljednjeg posla.",
        dumpPromptCareerSwitch: "Ispričajte mi sve o sebi — šta ste do sada radili i šta želite raditi sada?",
        dumpPromptStudent:      "Ispričajte mi sve o sebi — prvo školovanje, prakse i poslovi uz školu.",
        dumpPromptPause:        "Ispričajte mi sve o sebi — i šta ste radili prije pauze. Pauza je sasvim u redu.",
        modeSwitchToGuided:   "Radije korak po korak?",
        modeSwitchToFree:     "Radije slobodno pričati?",
        guidedSwitchMsg:      "Rado! Postavljaću vam jednostavna pitanja — jedno po jedno. Možete se vratiti kad god želite.",
        freeSwitchMsg:        "Rado! Samo slobodno pričajte — ja ću sve srediti za vas.",
        jobSearchBtn:         "🔎 Pronađite odgovarajuće poslove na AMS-u",
        jobSearchNotice:      (occ) => `Otvorićemo AMS berzu poslova u vašem pregledniku${occ ? ` sa pretragom „${occ}“` : ""}. AMS-u se šalje SAMO vaš pojam pretrage — vaše ime, kontakti i CV se NE šalju.`,
        jobSearchOpen:        "Traži na AMS-u ↗",
        jobSearchCancel:      "Odustani",
        jobSearchLoopHint:    "Savjet: kopirajte oglas koji vam se sviđa i zalijepite ga gore — vidjećete koliko vaš CV odgovara.",
        appEmailBtn:          "📧 Kreiraj e-mail za prijavu",
        appEmailHeading:      "📧 Vaš e-mail za prijavu",
        appEmailToLabel:      "Prima (e-mail firme, opcionalno):",
        appEmailSubjLabel:    "Predmet:",
        appEmailHint:         (hasCL) => hasCL ? "Važno: priložite preuzeti CV (PDF). Možete priložiti i propratno pismo." : "Važno: priložite preuzeti CV (PDF) uz e-mail.",
        appEmailOpen:         "Otvori u e-mail programu ↗",
        appEmailCopy:         "Kopiraj tekst",
        appEmailCopied:       "✓ Kopirano",
        appEmailClose:        "Zatvori",
        answerLabel:          'Vaš odgovor — pišite na bilo kom jeziku:',
        answerPlaceholder:    'Samo počnite pisati — i grube bilješke su u redu. Mi ćemo to poboljšati automatski.',
        submitBtn:            'Dalje →',
        skipBtn:              'Preskoči pitanje',
        previewTitle:         'Ovako izgleda u vašem CV-u',
        previewRawLabel:      'Što ste napisali',
        previewPolishedLabel: 'U vašem CV-u',
        previewLoading:       'Poboljšavamo…',
        wordSingular:         'riječ',
        wordPlural:           'riječi',
        qualityShort:         'Malo kratko — dodajte još jedan detalj',
        qualityOk:            'Dobar početak — malo više bi pomoglo',
        qualityGood:          'Odlično — to je dovoljno!',
        langNote:             'Uvijek možete pisati na više jezika — sistem automatski prepoznaje svaki jezik.',
        step1Text:            'Šta najbolje opisuje vašu trenutnu situaciju?',
        step2Text:            'Kako se zovete?',
        startBtn:             'Kreirajte moj CV →',
        startHintReady:       'Sve je spremno — kliknite dugme!',
        startHintBoth:        'Odaberite svoju situaciju gore i unesite svoje ime.',
        startHintPath:        'Odaberite svoju situaciju gore.',
        startHintName:        'Unesite svoje ime.',
        progressLabel:        (cur, tot) => `Pitanje ${cur} od ${tot}`,
        detectedLang:         (lang) => `Otkriveni jezik: ${lang}`,
        resumeWelcomeStrong:  'Dobrodošli nazad!',
        resumeBtn:            'Nastavi gdje sam stao/la',
        dismissResumeBtn:     'Počni iznova',
        resumeWelcome:        (name) => name ? `Dobrodošli nazad, ${name}! Vaš CV čeka.` : 'Imate intervju u toku.',
        namePlaceholder:      'Unesite ime — npr. Maria',
        appSubtitle:          'Vaš profesionalni CV — na svakom jeziku',
        trustHeadline:        'Automatski pretvaramo vaše odgovore u profesionalni CV.',
        trustDetail1:         '⏱ Oko 10–15 minuta',
        trustDetail2:         '💾 Napredak se čuva nakon svakog odgovora',
        trustDetail3:         '🌐 Pišite na bilo kom jeziku',
        exampleGoodTitle:     '✅ Dobar primjer',
        exampleBadTitle:      '❌ Manje korisno',
        quickFillLabel:       'Brzi start — kliknite za umetanje:',
        reaskTip:             'Savjet',
        pathUnemployedLabel:  'Tražim posao',
        pathUnemployedDesc:   'Tražim posao ili se vraćam na tržište rada',
        pathCareerLabel:      'Promjena karijere',
        pathCareerDesc:       'Prelazak u novo područje ili industrijsku granu',
        pathStudentLabel:     'Učenik/ca ili student/ica',
        pathStudentDesc:      'U obrazovanju ili blizu završetka',
        pathPauseLabel:       'Pauza u karijeri',
        pathPauseDesc:        'Povratak nakon perioda bez posla',
        pathOtherLabel:       'Ostalo',
        pathOtherDesc:        'Moja situacija je malo drugačija',
        completionHeading:    'Vaš CV je gotov 🎉',
        completionSubtitle:   'Vaši odgovori su poboljšani i sačuvani. Preuzmite CV ispod.',
        completionStats:      (ans, skipped) => `${ans} odgovoreno · ${skipped} preskočeno`,
        exportPdf:            '⬇ Preuzmi PDF',
        exportDocx:           '⬇ Preuzmi Word (.docx)',
        exportJson:           '⬇ Izvezi podatke (za trenera)',
        exportRetry:          'Pokušaj ponovo',
        atsHeading:           '🎯 Koliko dobro odgovara vaš CV?',
        atsMatchedLabel:      'Pronađene ključne riječi',
        atsMissingLabel:      'Nedostajuće ključne riječi',
        atsBtn:               '🎯 Analiziraj CV',
        atsAnalyzing:         'Analizira se...',
        coverLetterHeading:   '✉️ Vaše propratno pismo',
        coverLetterBtn:       '✉️ Kreiraj propratno pismo',
        coverLetterCreating:  'Kreira se...',
        reviewBtn:            '📋 Pogledaj Prije & Poslije',
        startOverBtn:         'Počni novi CV',
        reviewHeading:        'Prije & Poslije — Vaši odgovori poboljšani',
        reviewSubtitle:       'Ovo vidi vaš trener kada pregledava vaš rad.',
        closeReviewBtn:       '← Nazad na moj CV',
        reviewColRaw:         'Što ste napisali',
        reviewColPolished:    'U vašem CV-u',
        confirmStartOver:     'Ovo će izbrisati vaš trenutni napredak.\n\nŽelite li zaista početi novi CV?',
        consentText: 'Razumijem da su moji odgovori sačuvani samo na ovom računaru i nisu prenijeti na internet.',
        profileSummaryLoading: 'Analizira se vaš profil…',
        profileSummaryHeading: '💡 Vaš profil snaga',
        qualityHighText:      'Jak CV — ostavit će dobar dojam.',
        qualityHighTip:       'Preuzmite i podijelite ga sada!',
        qualityMedText:       'Dobar CV — nekoliko malih dopuna bi ga učinilo još boljim.',
        qualityMedTip1:       'Dodajte još jedan detalj o svom iskustvu',
        qualityMedTip2:       'Spomenite alate ili softver koji ste koristili',
        qualityLowText:       'Solidan početak — više detalja bi ga ojačalo.',
        qualityLowTip1:       'Opišite tipičan radni dan na vašem posljednjem poslu',
        qualityLowTip2:       'Navedite vještine ili alate koje poznajete',
        qualityLowTip3:       'Spomenite kurseve ili certifikate',
        qualityBaseText:      'Vaš CV ima osnove — malo više detalja bi stvarno pomoglo.',
        qualityBaseTip1:      'Popunite pitanja koja ste preskočili',
        qualityBaseTip2:      'Čak i jedna rečenica po odjeljku čini razliku',
        statusSaving: 'Čuvanje…', statusSaved: 'Sačuvano ✓', statusReady: 'Spreman',
        statusError: 'Greška', statusStarting: 'Pokretanje…', statusResuming: 'Nastavak…',
        statusSkipping: 'Preskakanje…', statusBuilding: 'Kreiranje CV-a…', statusDone: 'Gotovo ✓',
        noSessionError: 'Nema aktivne sesije — molimo završite intervju.',
        exportPreparing: (fmt) => `Priprema ${fmt} preuzimanja…`,
        exportSuccess: (name) => `${name} preuzeto.`,
        exportFailed: (msg) => `Preuzimanje nije uspjelo: ${msg}`,
        coverLetterError: (msg) => `Propratno pismo nije moglo biti kreirano: ${msg}`,
        atsInputHeading:      '🎯 Zalijepite oglas za posao — poređat ćemo s vašim CV-om',
        atsInputDesc:         'Zalijepite oglas za posao ispod. Sistem će automatski pronaći odgovarajuće ključne riječi.',
        jobDescPlaceholder:   'Zalijepite oglas za posao ovdje...',
        runAtsBtn:            'Analiziraj CV →',
        cancelAtsBtn:         'Odustani',
        clInputHeading:       '✉️ Personaliziraj propratno pismo',
        clCompanyLabel:       'Kompanija / Poslodavac:',
        clCompanyPlaceholder: 'npr. BILLA AG, Huber GmbH',
        clPositionLabel:      'Pozicija / Naziv posla:',
        clPositionPlaceholder:'npr. Skladištar, Čistač/ica',
        generateCLBtn:        'Kreiraj propratno pismo →',
        cancelCLBtn:          'Odustani',
        photoUploadLabel:     'Odaberi fotografiju (opciono)',
        photoHint:            'Profesionalna fotografija — opciono.',
        photoSkipLabel:       'Nastavi bez fotografije',
        dateFromLabel:        'Od:',
        dateToLabel:          'Do:',
        dateFromPlaceholder:  'npr. jan 2019, 2019',
        dateToPlaceholder:    'npr. mar 2022, danas',
        dateHelperInsertBtn:  'Ubaci u polje za odgovor ↓',
        dateHelperCompose:    (from, to) => `Od ${from} do ${to}`,
        confirmDiscard:        'Stvarno početi iznova?',
        previewPlaceholderHint:'Nastavite pisati — ovdje ćete vidjeti rezultat',
        typeMoreHint:          'Molimo napišite nešto više…',
    },
    hr: {
        dumpPromptUnemployed:   "Ispričajte mi sve o sebi — najbolje počnite od posljednjeg posla.",
        dumpPromptCareerSwitch: "Ispričajte mi sve o sebi — što ste dosad radili i što biste sada željeli raditi?",
        dumpPromptStudent:      "Ispričajte mi sve o sebi — najprije školovanje, prakse i honorarni poslovi.",
        dumpPromptPause:        "Ispričajte mi sve o sebi — i što ste radili prije stanke. Stanka je sasvim u redu.",
        modeSwitchToGuided:   "Radije korak po korak?",
        modeSwitchToFree:     "Radije slobodno pričati?",
        guidedSwitchMsg:      "Rado! Postavljat ću vam jednostavna pitanja — jedno po jedno. Možete se vratiti bilo kada.",
        freeSwitchMsg:        "Rado! Samo slobodno pričajte — ja ću sve posložiti za vas.",
        jobSearchBtn:         "🔎 Pronađite odgovarajuće poslove na AMS-u",
        jobSearchNotice:      (occ) => `Otvorit ćemo AMS burzu poslova u vašem pregledniku${occ ? ` s pretragom „${occ}“` : ""}. AMS-u se šalje SAMO vaš pojam pretrage — vaše ime, kontakti i životopis se NE šalju.`,
        jobSearchOpen:        "Traži na AMS-u ↗",
        jobSearchCancel:      "Odustani",
        jobSearchLoopHint:    "Savjet: kopirajte oglas koji vam se sviđa i zalijepite ga gore — vidjet ćete koliko vaš životopis odgovara.",
        appEmailBtn:          "📧 Izradi e-mail za prijavu",
        appEmailHeading:      "📧 Vaš e-mail za prijavu",
        appEmailToLabel:      "Prima (e-mail tvrtke, neobavezno):",
        appEmailSubjLabel:    "Predmet:",
        appEmailHint:         (hasCL) => hasCL ? "Važno: priložite preuzeti životopis (PDF). Možete priložiti i zamolbu." : "Važno: priložite preuzeti životopis (PDF) uz e-mail.",
        appEmailOpen:         "Otvori u programu e-pošte ↗",
        appEmailCopy:         "Kopiraj tekst",
        appEmailCopied:       "✓ Kopirano",
        appEmailClose:        "Zatvori",
        answerLabel:          'Vaš odgovor — pišite na bilo kojem jeziku:',
        answerPlaceholder:    'Samo počnite pisati — i grube bilješke su u redu. Poboljšat ćemo ih automatski.',
        submitBtn:            'Dalje →',
        skipBtn:              'Preskoči pitanje',
        previewTitle:         'Ovako izgleda u vašem životopisu',
        previewRawLabel:      'Što ste napisali',
        previewPolishedLabel: 'U vašem životopisu',
        previewLoading:       'Poboljšavamo…',
        wordSingular:         'riječ',
        wordPlural:           'riječi',
        qualityShort:         'Malo kratko — dodajte još jedan detalj',
        qualityOk:            'Dobar početak — malo više bi pomoglo',
        qualityGood:          'Odlično — to je dovoljno!',
        langNote:             'Uvijek možete pisati na više jezika — sustav automatski prepoznaje svaki jezik.',
        step1Text:            'Što najbolje opisuje vašu trenutnu situaciju?',
        step2Text:            'Kako se zovete?',
        startBtn:             'Kreirajte moj životopis →',
        startHintReady:       'Sve je spremno — kliknite gumb!',
        startHintBoth:        'Odaberite svoju situaciju gore i unesite ime.',
        startHintPath:        'Odaberite svoju situaciju gore.',
        startHintName:        'Unesite svoje ime.',
        progressLabel:        (cur, tot) => `Pitanje ${cur} od ${tot}`,
        detectedLang:         (lang) => `Prepoznati jezik: ${lang}`,
        resumeWelcomeStrong:  'Dobrodošli natrag!',
        resumeBtn:            'Nastavi gdje sam stao/la',
        dismissResumeBtn:     'Počni iznova',
        resumeWelcome:        (name) => name ? `Dobrodošli natrag, ${name}! Vaš životopis čeka.` : 'Imate intervju u tijeku.',
        namePlaceholder:      'Unesite ime — npr. Maria',
        appSubtitle:          'Vaš profesionalni životopis — na svakom jeziku',
        trustHeadline:        'Automatski pretvaramo vaše odgovore u profesionalni životopis.',
        trustDetail1:         '⏱ Oko 10–15 minuta',
        trustDetail2:         '💾 Napredak se sprema nakon svakog odgovora',
        trustDetail3:         '🌐 Pišite na bilo kojem jeziku',
        exampleGoodTitle:     '✅ Dobar primjer',
        exampleBadTitle:      '❌ Manje korisno',
        quickFillLabel:       'Brzi start — kliknite za umetanje:',
        reaskTip:             'Savjet',
        pathUnemployedLabel:  'Tražim posao',
        pathUnemployedDesc:   'Tražim posao ili se vraćam na tržište rada',
        pathCareerLabel:      'Promjena karijere',
        pathCareerDesc:       'Prelazak u novo područje ili industrijsku granu',
        pathStudentLabel:     'Učenik/ca ili student/ica',
        pathStudentDesc:      'U obrazovanju ili blizu završetka',
        pathPauseLabel:       'Pauza u karijeri',
        pathPauseDesc:        'Povratak nakon razdoblja bez posla',
        pathOtherLabel:       'Ostalo',
        pathOtherDesc:        'Moja situacija je malo drugačija',
        completionHeading:    'Vaš životopis je gotov 🎉',
        completionSubtitle:   'Vaši odgovori su poboljšani i spremljeni. Preuzmite životopis ispod.',
        completionStats:      (ans, skipped) => `${ans} odgovoreno · ${skipped} preskočeno`,
        exportPdf:            '⬇ Preuzmi PDF',
        exportDocx:           '⬇ Preuzmi Word (.docx)',
        exportJson:           '⬇ Izvezi podatke (za trenera)',
        exportRetry:          'Pokušaj ponovo',
        atsHeading:           '🎯 Koliko dobro odgovara vaš životopis?',
        atsMatchedLabel:      'Pronađene ključne riječi',
        atsMissingLabel:      'Nedostajuće ključne riječi',
        atsBtn:               '🎯 Analiziraj životopis',
        atsAnalyzing:         'Analizira se...',
        coverLetterHeading:   '✉️ Vaše propratno pismo',
        coverLetterBtn:       '✉️ Kreiraj propratno pismo',
        coverLetterCreating:  'Kreira se...',
        reviewBtn:            '📋 Pogledaj Prije & Poslije',
        startOverBtn:         'Počni novi životopis',
        reviewHeading:        'Prije & Poslije — Vaši odgovori poboljšani',
        reviewSubtitle:       'Ovo vidi vaš trener kada pregledava vaš rad.',
        closeReviewBtn:       '← Natrag na moj životopis',
        reviewColRaw:         'Što ste napisali',
        reviewColPolished:    'U vašem životopisu',
        confirmStartOver:     'Time ćete izbrisati trenutni napredak.\n\nŽelite li zaista početi novi životopis?',
        consentText: 'Razumijem da su moji odgovori pohranjeni samo na ovom računalu i ne prenose se na internet.',
        profileSummaryLoading: 'Analizira se vaš profil…',
        profileSummaryHeading: '💡 Vaš profil snaga',
        qualityHighText: 'Jak životopis — ostavit će dobar dojam.', qualityHighTip: 'Preuzmite i podijelite!',
        qualityMedText: 'Dobar životopis — nekoliko malih dopuna bi ga poboljšalo.',
        qualityMedTip1: 'Dodajte još jedan detalj o iskustvu', qualityMedTip2: 'Navedite alate ili softver',
        qualityLowText: 'Solidan početak — više detalja bi ga ojačalo.',
        qualityLowTip1: 'Opišite tipičan radni dan', qualityLowTip2: 'Navedite vještine i alate',
        qualityLowTip3: 'Navedite kurseve ili certifikate',
        qualityBaseText: 'Životopis ima osnove — malo više detalja bi pomoglo.',
        qualityBaseTip1: 'Popunite preskočena pitanja', qualityBaseTip2: 'I jedna rečenica čini razliku',
        statusSaving: 'Snimanje…', statusSaved: 'Snimljeno ✓', statusReady: 'Spreman',
        statusError: 'Greška', statusStarting: 'Pokretanje…', statusResuming: 'Nastavak…',
        statusSkipping: 'Preskakanje…', statusBuilding: 'Izrada životopisa…', statusDone: 'Gotovo ✓',
        noSessionError: 'Nema aktivne sesije.',
        exportPreparing: (fmt) => `Priprema ${fmt}…`, exportSuccess: (name) => `${name} preuzeto.`,
        exportFailed: (msg) => `Preuzimanje nije uspjelo: ${msg}`,
        coverLetterError: (msg) => `Propratno pismo nije izrađeno: ${msg}`,
        atsInputHeading:      '🎯 Zalijepite oglas za posao — usporedimo s vašim životopisom',
        atsInputDesc:         'Zalijepite oglas za posao ispod. Sustav će automatski pronaći odgovarajuće ključne riječi.',
        jobDescPlaceholder:   'Zalijepite oglas za posao ovdje...',
        runAtsBtn:            'Analiziraj životopis →',
        cancelAtsBtn:         'Odustani',
        clInputHeading:       '✉️ Personaliziraj propratno pismo',
        clCompanyLabel:       'Tvrtka / Poslodavac:',
        clCompanyPlaceholder: 'npr. BILLA AG, Huber GmbH',
        clPositionLabel:      'Pozicija / Naziv posla:',
        clPositionPlaceholder:'npr. Skladištar, Čistač/ica',
        generateCLBtn:        'Kreiraj propratno pismo →',
        cancelCLBtn:          'Odustani',
        photoUploadLabel:     'Odaberi fotografiju (neobavezno)',
        photoHint:            'Profesionalna fotografija — neobavezno.',
        photoSkipLabel:       'Nastavi bez fotografije',
        dateFromLabel:        'Od:',
        dateToLabel:          'Do:',
        dateFromPlaceholder:  'npr. sij 2019, 2019',
        dateToPlaceholder:    'npr. ožu 2022, danas',
        dateHelperInsertBtn:  'Ubaci u polje za odgovor ↓',
        dateHelperCompose:    (from, to) => `Od ${from} do ${to}`,
        confirmDiscard:        'Stvarno početi iznova?',
        previewPlaceholderHint:'Nastavite pisati — ovdje ćete vidjeti rezultat',
        typeMoreHint:          'Molimo napišite nešto više…',
    },
    sr: {
        dumpPromptUnemployed:   "Ispričajte mi sve o sebi — najbolje počnite od poslednjeg posla.",
        dumpPromptCareerSwitch: "Ispričajte mi sve o sebi — šta ste do sada radili i šta želite da radite sada?",
        dumpPromptStudent:      "Ispričajte mi sve o sebi — prvo školovanje, prakse i poslove.",
        dumpPromptPause:        "Ispričajte mi sve o sebi — i šta ste radili pre pauze. Pauza je sasvim u redu.",
        modeSwitchToGuided:   "Radije korak po korak?",
        modeSwitchToFree:     "Radije slobodno pričati?",
        guidedSwitchMsg:      "Rado! Postavljaću vam jednostavna pitanja — jedno po jedno. Možete se vratiti kad god želite.",
        freeSwitchMsg:        "Rado! Samo slobodno pričajte — ja ću sve srediti za vas.",
        jobSearchBtn:         "🔎 Pronađite odgovarajuće poslove na AMS-u",
        jobSearchNotice:      (occ) => `Otvorićemo AMS berzu poslova u vašem pregledaču${occ ? ` sa pretragom „${occ}“` : ""}. AMS-u se šalje SAMO pojam pretrage — vaše ime, kontakt i CV se NE šalju.`,
        jobSearchOpen:        "Traži na AMS-u ↗",
        jobSearchCancel:      "Odustani",
        jobSearchLoopHint:    "Savet: kopirajte oglas koji vam se sviđa i nalepite ga gore — videćete koliko vaš CV odgovara.",
        appEmailBtn:          "📧 Napravi e-mail za prijavu",
        appEmailHeading:      "📧 Vaš e-mail za prijavu",
        appEmailToLabel:      "Prima (e-mail firme, opciono):",
        appEmailSubjLabel:    "Predmet:",
        appEmailHint:         (hasCL) => hasCL ? "Važno: priložite preuzeti CV (PDF). Možete priložiti i propratno pismo." : "Važno: priložite preuzeti CV (PDF) uz e-mail.",
        appEmailOpen:         "Otvori u e-mail programu ↗",
        appEmailCopy:         "Kopiraj tekst",
        appEmailCopied:       "✓ Kopirano",
        appEmailClose:        "Zatvori",
        answerLabel:          'Vaš odgovor — pišite na bilo kom jeziku:',
        answerPlaceholder:    'Samo počnite pisati — i grube beleške su u redu. Mi ćemo to poboljšati automatski.',
        submitBtn:            'Dalje →',
        skipBtn:              'Preskoči pitanje',
        previewTitle:         'Ovako izgleda u vašem CV-u',
        previewRawLabel:      'Šta ste napisali',
        previewPolishedLabel: 'U vašem CV-u',
        previewLoading:       'Poboljšavamo…',
        wordSingular:         'reč',
        wordPlural:           'reči',
        qualityShort:         'Malo kratko — dodajte još jedan detalj',
        qualityOk:            'Dobar početak — malo više bi pomoglo',
        qualityGood:          'Odlično — to je dovoljno!',
        langNote:             'Uvek možete pisati na više jezika — sistem automatski prepoznaje svaki jezik.',
        step1Text:            'Šta najbolje opisuje vašu trenutnu situaciju?',
        step2Text:            'Kako se zovete?',
        startBtn:             'Kreirajte moj CV →',
        startHintReady:       'Sve je spremno — kliknite dugme!',
        startHintBoth:        'Izaberite svoju situaciju gore i unesite ime.',
        startHintPath:        'Izaberite svoju situaciju gore.',
        startHintName:        'Unesite svoje ime.',
        progressLabel:        (cur, tot) => `Pitanje ${cur} od ${tot}`,
        detectedLang:         (lang) => `Prepoznati jezik: ${lang}`,
        resumeWelcomeStrong:  'Dobrodošli nazad!',
        resumeBtn:            'Nastavi gde sam stao/la',
        dismissResumeBtn:     'Počni iznova',
        resumeWelcome:        (name) => name ? `Dobrodošli nazad, ${name}! Vaš CV čeka.` : 'Imate intervju u toku.',
        namePlaceholder:      'Unesite ime — npr. Maria',
        appSubtitle:          'Vaš profesionalni CV — na svakom jeziku',
        trustHeadline:        'Automatski pretvaramo vaše odgovore u profesionalni CV.',
        trustDetail1:         '⏱ Oko 10–15 minuta',
        trustDetail2:         '💾 Napredak se čuva posle svakog odgovora',
        trustDetail3:         '🌐 Pišite na bilo kom jeziku',
        exampleGoodTitle:     '✅ Dobar primer',
        exampleBadTitle:      '❌ Manje korisno',
        quickFillLabel:       'Brzi start — kliknite za umetanje:',
        reaskTip:             'Savet',
        pathUnemployedLabel:  'Tražim posao',
        pathUnemployedDesc:   'Tražim posao ili se vraćam na tržište rada',
        pathCareerLabel:      'Promena karijere',
        pathCareerDesc:       'Prelaz u novo područje ili industrijsku granu',
        pathStudentLabel:     'Učenik/ca ili student/kinja',
        pathStudentDesc:      'U obrazovanju ili blizu završetka',
        pathPauseLabel:       'Pauza u karijeri',
        pathPauseDesc:        'Povratak nakon perioda bez posla',
        pathOtherLabel:       'Ostalo',
        pathOtherDesc:        'Moja situacija je malo drugačija',
        completionHeading:    'Vaš CV je gotov 🎉',
        completionSubtitle:   'Vaši odgovori su poboljšani i sačuvani. Preuzmite CV ispod.',
        completionStats:      (ans, skipped) => `${ans} odgovoreno · ${skipped} preskočeno`,
        exportPdf:            '⬇ Preuzmi PDF',
        exportDocx:           '⬇ Preuzmi Word (.docx)',
        exportJson:           '⬇ Izvezi podatke (za trenera)',
        exportRetry:          'Pokušaj ponovo',
        atsHeading:           '🎯 Koliko dobro odgovara vaš CV?',
        atsMatchedLabel:      'Pronađene ključne reči',
        atsMissingLabel:      'Nedostajuće ključne reči',
        atsBtn:               '🎯 Analiziraj CV',
        atsAnalyzing:         'Analizira se...',
        coverLetterHeading:   '✉️ Vaše propratno pismo',
        coverLetterBtn:       '✉️ Kreiraj propratno pismo',
        coverLetterCreating:  'Kreira se...',
        reviewBtn:            '📋 Pogledaj Pre & Posle',
        startOverBtn:         'Počni novi CV',
        reviewHeading:        'Pre & Posle — Vaši odgovori poboljšani',
        reviewSubtitle:       'Ovo vidi vaš trener kada pregleda vaš rad.',
        closeReviewBtn:       '← Nazad na moj CV',
        reviewColRaw:         'Šta ste napisali',
        reviewColPolished:    'U vašem CV-u',
        confirmStartOver:     'Ovo će izbrisati vaš trenutni napredak.\n\nŽelite li zaista početi novi CV?',
        consentText: 'Razumem da su moji odgovori sačuvani samo na ovom računaru i nisu preneti na internet.',
        profileSummaryLoading: 'Analizira se vaš profil…',
        profileSummaryHeading: '💡 Vaš profil snaga',
        qualityHighText: 'Jak CV — ostavit će dobar utisak.', qualityHighTip: 'Preuzmite i podelite!',
        qualityMedText: 'Dobar CV — nekoliko malih dopuna bi ga poboljšalo.',
        qualityMedTip1: 'Dodajte još jedan detalj o iskustvu', qualityMedTip2: 'Navedite alate ili softver',
        qualityLowText: 'Solidan početak — više detalja bi ga ojačalo.',
        qualityLowTip1: 'Opišite tipičan radni dan', qualityLowTip2: 'Navedite veštine i alate',
        qualityLowTip3: 'Navedite kurseve ili sertifikate',
        qualityBaseText: 'CV ima osnove — malo više detalja bi pomoglo.',
        qualityBaseTip1: 'Popunite preskočena pitanja', qualityBaseTip2: 'I jedna rečenica čini razliku',
        statusSaving: 'Čuvanje…', statusSaved: 'Sačuvano ✓', statusReady: 'Spreman',
        statusError: 'Greška', statusStarting: 'Pokretanje…', statusResuming: 'Nastavak…',
        statusSkipping: 'Preskakanje…', statusBuilding: 'Pravljenje CV-a…', statusDone: 'Gotovo ✓',
        noSessionError: 'Nema aktivne sesije.',
        exportPreparing: (fmt) => `Priprema ${fmt}…`, exportSuccess: (name) => `${name} preuzeto.`,
        exportFailed: (msg) => `Preuzimanje nije uspelo: ${msg}`,
        coverLetterError: (msg) => `Propratno pismo nije napravljeno: ${msg}`,
        atsInputHeading:      '🎯 Zalepite oglas za posao — poredićemo s vašim CV-om',
        atsInputDesc:         'Zalepite oglas za posao ispod. Sistem će automatski pronaći odgovarajuće ključne reči.',
        jobDescPlaceholder:   'Zalepite oglas za posao ovde...',
        runAtsBtn:            'Analiziraj CV →',
        cancelAtsBtn:         'Odustani',
        clInputHeading:       '✉️ Personalizuj propratno pismo',
        clCompanyLabel:       'Kompanija / Poslodavac:',
        clCompanyPlaceholder: 'npr. BILLA AG, Huber GmbH',
        clPositionLabel:      'Pozicija / Naziv posla:',
        clPositionPlaceholder:'npr. Skladištar, Čistač/ica',
        generateCLBtn:        'Kreiraj propratno pismo →',
        cancelCLBtn:          'Odustani',
        photoUploadLabel:     'Izaberi fotografiju (opciono)',
        photoHint:            'Profesionalna fotografija — opciono.',
        photoSkipLabel:       'Nastavi bez fotografije',
        dateFromLabel:        'Od:',
        dateToLabel:          'Do:',
        dateFromPlaceholder:  'npr. jan 2019, 2019',
        dateToPlaceholder:    'npr. mar 2022, danas',
        dateHelperInsertBtn:  'Ubaci u polje za odgovor ↓',
        dateHelperCompose:    (from, to) => `Od ${from} do ${to}`,
        confirmDiscard:        'Stvarno početi ispočetka?',
        previewPlaceholderHint:'Nastavite da pišete — ovde ćete videti rezultat',
        typeMoreHint:          'Molimo napišite nešto više…',
    },
    tr: {
        dumpPromptUnemployed:   "Bana kendinizden bahsedin — en iyisi son işinizden başlayın.",
        dumpPromptCareerSwitch: "Bana kendinizden bahsedin — şimdiye kadar ne çalıştınız, şimdi ne yapmak istiyorsunuz?",
        dumpPromptStudent:      "Bana kendinizden bahsedin — önce eğitiminiz, stajlarınız ve ek işleriniz.",
        dumpPromptPause:        "Bana kendinizden bahsedin — aradan önce ne çalıştığınızı da. Ara vermek gayet normaldir.",
        modeSwitchToGuided:   "Adım adım mı tercih edersiniz?",
        modeSwitchToFree:     "Serbestçe anlatmak mı istersiniz?",
        guidedSwitchMsg:      "Memnuniyetle! Size basit sorular soracağım — teker teker. İstediğiniz zaman geri dönebilirsiniz.",
        freeSwitchMsg:        "Memnuniyetle! Serbestçe anlatın — her şeyi sizin için düzenlerim.",
        jobSearchBtn:         "🔎 AMS'de uygun işler bulun",
        jobSearchNotice:      (occ) => `AMS iş portalını tarayıcınızda açacağız${occ ? ` „${occ}“ aramasıyla` : ""}. AMS'ye SADECE arama teriminiz gönderilir — adınız, iletişim bilgileriniz ve CV'niz GÖNDERİLMEZ.`,
        jobSearchOpen:        "AMS'de ara ↗",
        jobSearchCancel:      "İptal",
        jobSearchLoopHint:    "İpucu: beğendiğiniz bir ilanı kopyalayıp yukarıya yapıştırın — CV'nizin ne kadar uygun olduğunu görürsünüz.",
        appEmailBtn:          "📧 Başvuru e-postası oluştur",
        appEmailHeading:      "📧 Başvuru e-postanız",
        appEmailToLabel:      "Alıcı (firmanın e-postası, isteğe bağlı):",
        appEmailSubjLabel:    "Konu:",
        appEmailHint:         (hasCL) => hasCL ? "Önemli: indirdiğiniz CV'yi (PDF) ekleyin. Ön yazınızı da ekleyebilirsiniz." : "Önemli: indirdiğiniz CV'yi (PDF) e-postaya ekleyin.",
        appEmailOpen:         "E-posta programında aç ↗",
        appEmailCopy:         "Metni kopyala",
        appEmailCopied:       "✓ Kopyalandı",
        appEmailClose:        "Kapat",
        answerLabel:          'Yanıtınız — istediğiniz dilde yazabilirsiniz:',
        answerPlaceholder:    'Sadece yazmaya başlayın — kaba notlar bile olur. Otomatik olarak geliştireceğiz.',
        submitBtn:            'İleri →',
        skipBtn:              'Soruyu geç',
        previewTitle:         'CV\'nizde böyle görünür',
        previewRawLabel:      'Yazdığınız',
        previewPolishedLabel: 'CV\'nizde',
        previewLoading:       'Geliştiriliyor…',
        wordSingular:         'kelime',
        wordPlural:           'kelime',
        qualityShort:         'Biraz kısa — bir ayrıntı daha ekleyin',
        qualityOk:            'İyi başlangıç — biraz daha yardımcı olur',
        qualityGood:          'Harika — bu yeterli!',
        langNote:             'Her zaman birden fazla dilde yazabilirsiniz — sistem her dili otomatik tanır.',
        step1Text:            'Mevcut durumunuzu en iyi ne tanımlar?',
        step2Text:            'Adınız nedir?',
        startBtn:             'CV\'mi oluştur →',
        startHintReady:       'Hazır — butona tıklayın!',
        startHintBoth:        'Lütfen yukarıdan durumunuzu seçin ve adınızı girin.',
        startHintPath:        'Lütfen yukarıdan durumunuzu seçin.',
        startHintName:        'Lütfen adınızı girin.',
        progressLabel:        (cur, tot) => `Soru ${cur} / ${tot}`,
        detectedLang:         (lang) => `Tespit edilen dil: ${lang}`,
        resumeWelcomeStrong:  'Tekrar hoş geldiniz!',
        resumeBtn:            'Kaldığım yerden devam et',
        dismissResumeBtn:     'Yeniden başla',
        resumeWelcome:        (name) => name ? `Tekrar hoş geldiniz, ${name}! CV'niz sizi bekliyor.` : 'Devam eden bir mülakatınız var.',
        namePlaceholder:      'Adınızı girin — ör. Maria',
        appSubtitle:          'Profesyonel CV\'niz — her dilde',
        trustHeadline:        'Yanıtlarınızı otomatik olarak profesyonel bir CV\'ye dönüştürüyoruz.',
        trustDetail1:         '⏱ Yaklaşık 10–15 dakika',
        trustDetail2:         '💾 Her yanıttan sonra ilerleme kaydedilir',
        trustDetail3:         '🌐 İstediğiniz dilde yazın',
        exampleGoodTitle:     '✅ İyi örnek',
        exampleBadTitle:      '❌ Daha az yardımcı',
        quickFillLabel:       'Hızlı başlangıç — eklemek için tıklayın:',
        reaskTip:             'İpucu',
        pathUnemployedLabel:  'İş arıyorum',
        pathUnemployedDesc:   'İş arıyor veya iş hayatına geri dönüyorum',
        pathCareerLabel:      'Kariyer değişikliği',
        pathCareerDesc:       'Yeni bir alana veya sektöre geçiş',
        pathStudentLabel:     'Öğrenci veya stajyer',
        pathStudentDesc:      'Eğitimdeyim veya bitirmek üzereyim',
        pathPauseLabel:       'Kariyer molası',
        pathPauseDesc:        'İş dışı geçen bir sürecin ardından geri dönüş',
        pathOtherLabel:       'Diğer',
        pathOtherDesc:        'Durumum biraz farklı',
        completionHeading:    'CV\'niz hazır 🎉',
        completionSubtitle:   'Yanıtlarınız iyileştirildi ve kaydedildi. CV\'nizi aşağıdan indirin.',
        completionStats:      (ans, skipped) => `${ans} yanıtlandı · ${skipped} atlandı`,
        exportPdf:            '⬇ PDF indir',
        exportDocx:           '⬇ Word indir (.docx)',
        exportJson:           '⬇ Verileri dışa aktar (eğitmen için)',
        exportRetry:          'Tekrar dene',
        atsHeading:           '🎯 CV\'niz ne kadar uyuyor?',
        atsMatchedLabel:      'Bulunan anahtar kelimeler',
        atsMissingLabel:      'Eksik anahtar kelimeler',
        atsBtn:               '🎯 CV\'yi analiz et',
        atsAnalyzing:         'Analiz ediliyor...',
        coverLetterHeading:   '✉️ Ön yazınız',
        coverLetterBtn:       '✉️ Ön yazı oluştur',
        coverLetterCreating:  'Oluşturuluyor...',
        reviewBtn:            '📋 Önce & Sonra görüntüle',
        startOverBtn:         'Yeni CV başlat',
        reviewHeading:        'Önce & Sonra — Yanıtlarınız iyileştirildi',
        reviewSubtitle:       'Eğitmeniniz çalışmanızı incelerken bunu görür.',
        closeReviewBtn:       '← CV\'me geri dön',
        reviewColRaw:         'Yazdığınız',
        reviewColPolished:    'CV\'nizde',
        confirmStartOver:     'Bu işlem mevcut ilerlemenizi siler.\n\nYeni bir CV başlatmak istiyor musunuz?',
        consentText: 'Yanıtlarımın yalnızca bu bilgisayarda kaydedildiğini ve internete iletilmediğini anlıyorum.',
        profileSummaryLoading: 'Profiliniz analiz ediliyor…',
        profileSummaryHeading: '💡 Güçlü yönler profiliniz',
        qualityHighText: 'Güçlü CV — harika bir izlenim bırakacak.', qualityHighTip: 'Şimdi indirin ve paylaşın!',
        qualityMedText: 'İyi CV — birkaç küçük ekleme daha da iyi yapar.',
        qualityMedTip1: 'Deneyiminize bir ayrıntı daha ekleyin', qualityMedTip2: 'Kullandığınız araçları belirtin',
        qualityLowText: 'Sağlam bir başlangıç — daha fazla ayrıntı güçlendirir.',
        qualityLowTip1: 'Son işinizdeki tipik bir günü anlatın', qualityLowTip2: 'Bildiğiniz becerileri listeleyin',
        qualityLowTip3: 'Kurs veya sertifikaları belirtin',
        qualityBaseText: 'CV temel bilgileri içeriyor — biraz daha ayrıntı gerçekten yardımcı olur.',
        qualityBaseTip1: 'Atladığınız soruları doldurun', qualityBaseTip2: 'Her bölüm için tek cümle bile fark yaratır',
        statusSaving: 'Kaydediliyor…', statusSaved: 'Kaydedildi ✓', statusReady: 'Hazır',
        statusError: 'Hata', statusStarting: 'Başlatılıyor…', statusResuming: 'Devam ediliyor…',
        statusSkipping: 'Atlanıyor…', statusBuilding: 'CV oluşturuluyor…', statusDone: 'Tamamlandı ✓',
        noSessionError: 'Aktif oturum yok.',
        exportPreparing: (fmt) => `${fmt} indirme hazırlanıyor…`, exportSuccess: (name) => `${name} indirildi.`,
        exportFailed: (msg) => `İndirme başarısız: ${msg}`,
        coverLetterError: (msg) => `Ön yazı oluşturulamadı: ${msg}`,
        atsInputHeading:      '🎯 İş ilanını yapıştırın — CV\'nizle karşılaştıralım',
        atsInputDesc:         'Başvurmak istediğiniz iş ilanını aşağıya yapıştırın. Sistem eşleşen anahtar kelimeleri otomatik bulacaktır.',
        jobDescPlaceholder:   'İş ilanını buraya yapıştırın...',
        runAtsBtn:            'CV\'yi analiz et →',
        cancelAtsBtn:         'İptal',
        clInputHeading:       '✉️ Ön yazıyı kişiselleştir',
        clCompanyLabel:       'Şirket / İşveren:',
        clCompanyPlaceholder: 'örn. BILLA AG, Huber GmbH',
        clPositionLabel:      'Pozisyon / İş unvanı:',
        clPositionPlaceholder:'örn. Depo görevlisi, Temizlikçi',
        generateCLBtn:        'Ön yazı oluştur →',
        cancelCLBtn:          'İptal',
        photoUploadLabel:     'Fotoğraf seç (isteğe bağlı)',
        photoHint:            'Profesyonel fotoğraf — isteğe bağlı.',
        photoSkipLabel:       'Fotoğrafsız devam et',
        dateFromLabel:        'Başlangıç:',
        dateToLabel:          'Bitiş:',
        dateFromPlaceholder:  'örn. Oca 2019, 2019',
        dateToPlaceholder:    'örn. Mar 2022, bugün',
        dateHelperInsertBtn:  'Cevap alanına ekle ↓',
        dateHelperCompose:    (from, to) => `${from} tarihinden ${to} tarihine`,
        confirmDiscard:        'Gerçekten yeniden başlamak istiyor musunuz?',
        previewPlaceholderHint:'Yazmaya devam edin — sonucu burada göreceksiniz',
        typeMoreHint:          'Lütfen biraz daha yazın…',
    },
    pl: {
        dumpPromptUnemployed:   "Opowiedz mi wszystko o sobie — najlepiej zacznij od ostatniej pracy.",
        dumpPromptCareerSwitch: "Opowiedz mi wszystko o sobie — co robiłeś/aś do tej pory i co chcesz robić teraz?",
        dumpPromptStudent:      "Opowiedz mi wszystko o sobie — najpierw wykształcenie, praktyki i prace dorywcze.",
        dumpPromptPause:        "Opowiedz mi wszystko o sobie — także o pracy przed przerwą. Przerwa jest zupełnie w porządku.",
        modeSwitchToGuided:   "Wolisz krok po kroku?",
        modeSwitchToFree:     "Wolisz opowiadać swobodnie?",
        guidedSwitchMsg:      "Chętnie! Będę zadawać proste pytania — jedno po drugim. Możesz wrócić w każdej chwili.",
        freeSwitchMsg:        "Chętnie! Po prostu opowiadaj — wszystko uporządkuję.",
        jobSearchBtn:         "🔎 Znajdź pasujące oferty w AMS",
        jobSearchNotice:      (occ) => `Otworzymy giełdę pracy AMS w Twojej przeglądarce${occ ? ` z wyszukiwaniem „${occ}”` : ""}. Do AMS trafia TYLKO hasło wyszukiwania — Twoje imię, dane kontaktowe i CV NIE są wysyłane.`,
        jobSearchOpen:        "Szukaj w AMS ↗",
        jobSearchCancel:      "Anuluj",
        jobSearchLoopHint:    "Wskazówka: skopiuj ogłoszenie, które Ci się podoba, i wklej je powyżej — zobaczysz, jak dobrze pasuje Twoje CV.",
        appEmailBtn:          "📧 Utwórz e-mail aplikacyjny",
        appEmailHeading:      "📧 Twój e-mail aplikacyjny",
        appEmailToLabel:      "Do (e-mail firmy, opcjonalnie):",
        appEmailSubjLabel:    "Temat:",
        appEmailHint:         (hasCL) => hasCL ? "Ważne: załącz pobrane CV (PDF). Możesz też załączyć list motywacyjny." : "Ważne: załącz pobrane CV (PDF) do e-maila.",
        appEmailOpen:         "Otwórz w programie pocztowym ↗",
        appEmailCopy:         "Kopiuj tekst",
        appEmailCopied:       "✓ Skopiowano",
        appEmailClose:        "Zamknij",
        answerLabel:          'Twoja odpowiedź — pisz w dowolnym języku:',
        answerPlaceholder:    'Po prostu zacznij pisać — nawet szkice są w porządku. Automatycznie to poprawimy.',
        submitBtn:            'Dalej →',
        skipBtn:              'Pomiń pytanie',
        previewTitle:         'Tak wygląda to w Twoim CV',
        previewRawLabel:      'Co napisałeś/aś',
        previewPolishedLabel: 'W Twoim CV',
        previewLoading:       'Poprawiamy…',
        wordSingular:         'słowo',
        wordPlural:           'słów',
        qualityShort:         'Trochę krótko — dodaj jeszcze jeden szczegół',
        qualityOk:            'Dobry początek — trochę więcej by pomogło',
        qualityGood:          'Świetnie — to wystarczy!',
        langNote:             'Zawsze możesz pisać w wielu językach — system automatycznie rozpoznaje każdy język.',
        step1Text:            'Co najlepiej opisuje Twoją obecną sytuację?',
        step2Text:            'Jak masz na imię?',
        startBtn:             'Utwórz moje CV →',
        startHintReady:       'Wszystko gotowe — kliknij przycisk!',
        startHintBoth:        'Wybierz swoją sytuację powyżej i wpisz swoje imię.',
        startHintPath:        'Wybierz swoją sytuację powyżej.',
        startHintName:        'Wpisz swoje imię.',
        progressLabel:        (cur, tot) => `Pytanie ${cur} z ${tot}`,
        detectedLang:         (lang) => `Wykryty język: ${lang}`,
        resumeWelcomeStrong:  'Witaj z powrotem!',
        resumeBtn:            'Kontynuuj od miejsca, w którym skończyłem/am',
        dismissResumeBtn:     'Zacznij od nowa',
        resumeWelcome:        (name) => name ? `Witaj z powrotem, ${name}! Twoje CV czeka.` : 'Masz wywiad w toku.',
        namePlaceholder:      'Wpisz swoje imię — np. Maria',
        appSubtitle:          'Twoje profesjonalne CV — w każdym języku',
        trustHeadline:        'Automatycznie zamieniamy Twoje odpowiedzi w profesjonalne CV.',
        trustDetail1:         '⏱ Około 10–15 minut',
        trustDetail2:         '💾 Postęp zapisywany po każdej odpowiedzi',
        trustDetail3:         '🌐 Pisz w dowolnym języku',
        exampleGoodTitle:     '✅ Dobry przykład',
        exampleBadTitle:      '❌ Mniej pomocne',
        quickFillLabel:       'Szybki start — kliknij aby wstawić:',
        reaskTip:             'Wskazówka',
        pathUnemployedLabel:  'Szukam pracy',
        pathUnemployedDesc:   'Szukam pracy lub wracam na rynek pracy',
        pathCareerLabel:      'Zmiana kariery',
        pathCareerDesc:       'Przejście do nowej branży lub dziedziny',
        pathStudentLabel:     'Uczeń/Uczennica lub student/ka',
        pathStudentDesc:      'W trakcie edukacji lub blisko jej ukończenia',
        pathPauseLabel:       'Przerwa w karierze',
        pathPauseDesc:        'Powrót po czasie bez pracy',
        pathOtherLabel:       'Inne',
        pathOtherDesc:        'Moja sytuacja jest nieco inna',
        completionHeading:    'Twoje CV jest gotowe 🎉',
        completionSubtitle:   'Twoje odpowiedzi zostały poprawione i zapisane. Pobierz CV poniżej.',
        completionStats:      (ans, skipped) => `${ans} odpowiedziano · ${skipped} pominięto`,
        exportPdf:            '⬇ Pobierz PDF',
        exportDocx:           '⬇ Pobierz Word (.docx)',
        exportJson:           '⬇ Eksportuj dane (dla trenera)',
        exportRetry:          'Spróbuj ponownie',
        atsHeading:           '🎯 Jak dobrze pasuje Twoje CV?',
        atsMatchedLabel:      'Znalezione słowa kluczowe',
        atsMissingLabel:      'Brakujące słowa kluczowe',
        atsBtn:               '🎯 Analizuj CV',
        atsAnalyzing:         'Analizowanie...',
        coverLetterHeading:   '✉️ Twój list motywacyjny',
        coverLetterBtn:       '✉️ Utwórz list motywacyjny',
        coverLetterCreating:  'Tworzenie...',
        reviewBtn:            '📋 Zobacz Przed & Po',
        startOverBtn:         'Zacznij nowe CV',
        reviewHeading:        'Przed & Po — Twoje odpowiedzi poprawione',
        reviewSubtitle:       'To widzi Twój trener podczas przeglądania Twojej pracy.',
        closeReviewBtn:       '← Wróć do mojego CV',
        reviewColRaw:         'Co napisałeś/aś',
        reviewColPolished:    'W Twoim CV',
        confirmStartOver:     'Spowoduje to usunięcie bieżącego postępu.\n\nCzy naprawdę chcesz zacząć nowe CV?',
        consentText: 'Rozumiem, że moje odpowiedzi są zapisywane tylko na tym komputerze i nie są przesyłane do internetu.',
        profileSummaryLoading: 'Analizowanie profilu…',
        profileSummaryHeading: '💡 Twój profil mocnych stron',
        qualityHighText: 'Mocne CV — zrobi świetne wrażenie.', qualityHighTip: 'Pobierz i udostępnij teraz!',
        qualityMedText: 'Dobre CV — kilka małych uzupełnień uczyniłoby je jeszcze lepszym.',
        qualityMedTip1: 'Dodaj jeszcze jeden szczegół o doświadczeniu', qualityMedTip2: 'Wspomnij o używanych narzędziach',
        qualityLowText: 'Solidny początek — więcej szczegółów wzmocni CV.',
        qualityLowTip1: 'Opisz typowy dzień w ostatniej pracy', qualityLowTip2: 'Wymień znane umiejętności',
        qualityLowTip3: 'Wspomnij o kursach lub certyfikatach',
        qualityBaseText: 'CV zawiera podstawy — trochę więcej szczegółów naprawdę pomoże.',
        qualityBaseTip1: 'Uzupełnij pominięte pytania', qualityBaseTip2: 'Nawet jedno zdanie w sekcji robi różnicę',
        statusSaving: 'Zapisywanie…', statusSaved: 'Zapisano ✓', statusReady: 'Gotowy',
        statusError: 'Błąd', statusStarting: 'Uruchamianie…', statusResuming: 'Wznawianie…',
        statusSkipping: 'Pomijanie…', statusBuilding: 'Tworzenie CV…', statusDone: 'Gotowe ✓',
        noSessionError: 'Brak aktywnej sesji.',
        exportPreparing: (fmt) => `Przygotowywanie ${fmt}…`, exportSuccess: (name) => `${name} pobrano.`,
        exportFailed: (msg) => `Pobieranie nie powiodło się: ${msg}`,
        coverLetterError: (msg) => `Nie można utworzyć listu: ${msg}`,
        atsInputHeading:      '🎯 Wklej ogłoszenie o pracę — porównamy je z Twoim CV',
        atsInputDesc:         'Wklej ogłoszenie o pracę poniżej. System automatycznie znajdzie pasujące słowa kluczowe.',
        jobDescPlaceholder:   'Wklej ogłoszenie o pracę tutaj...',
        runAtsBtn:            'Analizuj CV →',
        cancelAtsBtn:         'Anuluj',
        clInputHeading:       '✉️ Personalizuj list motywacyjny',
        clCompanyLabel:       'Firma / Pracodawca:',
        clCompanyPlaceholder: 'np. BILLA AG, Huber GmbH',
        clPositionLabel:      'Stanowisko / Tytuł zawodowy:',
        clPositionPlaceholder:'np. Pracownik magazynu, Sprzątacz/ka',
        generateCLBtn:        'Utwórz list motywacyjny →',
        cancelCLBtn:          'Anuluj',
        photoUploadLabel:     'Wybierz zdjęcie (opcjonalnie)',
        photoHint:            'Profesjonalne zdjęcie — opcjonalnie.',
        photoSkipLabel:       'Kontynuuj bez zdjęcia',
        dateFromLabel:        'Od:',
        dateToLabel:          'Do:',
        dateFromPlaceholder:  'np. sty 2019, 2019',
        dateToPlaceholder:    'np. mar 2022, obecnie',
        dateHelperInsertBtn:  'Wstaw do pola odpowiedzi ↓',
        dateHelperCompose:    (from, to) => `Od ${from} do ${to}`,
        confirmDiscard:        'Naprawdę zacząć od nowa?',
        previewPlaceholderHint:'Pisz dalej — wynik zobaczysz tutaj',
        typeMoreHint:          'Proszę napisać trochę więcej…',
    },
    ro: {
        dumpPromptUnemployed:   "Povestiți-mi totul despre dvs. — cel mai bine începeți cu ultimul loc de muncă.",
        dumpPromptCareerSwitch: "Povestiți-mi totul despre dvs. — ce ați lucrat până acum și ce doriți să faceți acum?",
        dumpPromptStudent:      "Povestiți-mi totul despre dvs. — mai întâi studiile, practica și joburile ocazionale.",
        dumpPromptPause:        "Povestiți-mi totul despre dvs. — și ce ați lucrat înainte de pauză. Pauza este absolut în regulă.",
        modeSwitchToGuided:   "Preferați pas cu pas?",
        modeSwitchToFree:     "Preferați să povestiți liber?",
        guidedSwitchMsg:      "Cu plăcere! Vă pun întrebări simple — una câte una. Puteți reveni oricând.",
        freeSwitchMsg:        "Cu plăcere! Povestiți liber — eu ordonez totul pentru dvs.",
        jobSearchBtn:         "🔎 Găsiți joburi potrivite la AMS",
        jobSearchNotice:      (occ) => `Vom deschide bursa de locuri de muncă AMS în browserul dvs.${occ ? ` cu căutarea „${occ}”` : ""}. Către AMS se trimite DOAR termenul de căutare — numele, contactele și CV-ul dvs. NU se trimit.`,
        jobSearchOpen:        "Caută la AMS ↗",
        jobSearchCancel:      "Anulează",
        jobSearchLoopHint:    "Sfat: copiați un anunț care vă place și lipiți-l mai sus — veți vedea cât de bine se potrivește CV-ul.",
        appEmailBtn:          "📧 Creați e-mailul de candidatură",
        appEmailHeading:      "📧 E-mailul dvs. de candidatură",
        appEmailToLabel:      "Către (e-mailul firmei, opțional):",
        appEmailSubjLabel:    "Subiect:",
        appEmailHint:         (hasCL) => hasCL ? "Important: atașați CV-ul descărcat (PDF). Puteți atașa și scrisoarea de intenție." : "Important: atașați CV-ul descărcat (PDF) la e-mail.",
        appEmailOpen:         "Deschide în programul de e-mail ↗",
        appEmailCopy:         "Copiază textul",
        appEmailCopied:       "✓ Copiat",
        appEmailClose:        "Închide",
        answerLabel:          'Răspunsul dvs. — scrieți în orice limbă doriți:',
        answerPlaceholder:    'Scrieți liber — și notele brute sunt în regulă. Vom îmbunătăți automat.',
        submitBtn:            'Înainte →',
        skipBtn:              'Sări peste întrebare',
        previewTitle:         'Așa arată în CV-ul dvs.',
        previewRawLabel:      'Ce ați scris',
        previewPolishedLabel: 'În CV-ul dvs.',
        previewLoading:       'Se îmbunătățește…',
        wordSingular:         'cuvânt',
        wordPlural:           'cuvinte',
        qualityShort:         'Puțin scurt — adăugați un detaliu',
        qualityOk:            'Bun început — puțin mai mult ar ajuta',
        qualityGood:          'Excelent — este suficient!',
        langNote:             'Puteți scrie mereu în mai multe limbi — sistemul detectează automat fiecare limbă.',
        step1Text:            'Ce descrie cel mai bine situația dvs. actuală?',
        step2Text:            'Cum vă numiți?',
        startBtn:             'Creați CV-ul meu →',
        startHintReady:       'Totul e gata — apăsați butonul!',
        startHintBoth:        'Selectați situația dvs. de mai sus și introduceți numele.',
        startHintPath:        'Selectați situația dvs. de mai sus.',
        startHintName:        'Introduceți prenumele dvs.',
        progressLabel:        (cur, tot) => `Întrebarea ${cur} din ${tot}`,
        detectedLang:         (lang) => `Limbă detectată: ${lang}`,
        resumeWelcomeStrong:  'Bine ați revenit!',
        resumeBtn:            'Continuați de unde ați rămas',
        dismissResumeBtn:     'Începeți din nou',
        resumeWelcome:        (name) => name ? `Bine ați revenit, ${name}! CV-ul dvs. vă așteaptă.` : 'Aveți un interviu în desfășurare.',
        namePlaceholder:      'Introduceți prenumele — ex. Maria',
        appSubtitle:          'CV-ul dvs. profesional — în orice limbă',
        trustHeadline:        'Transformăm automat răspunsurile dvs. într-un CV profesional.',
        trustDetail1:         '⏱ Aproximativ 10–15 minute',
        trustDetail2:         '💾 Progresul salvat după fiecare răspuns',
        trustDetail3:         '🌐 Scrieți în orice limbă',
        exampleGoodTitle:     '✅ Exemplu bun',
        exampleBadTitle:      '❌ Mai puțin util',
        quickFillLabel:       'Start rapid — faceți clic pentru a insera:',
        reaskTip:             'Sfat',
        pathUnemployedLabel:  'Caut un loc de muncă',
        pathUnemployedDesc:   'Caut de lucru sau mă întorc pe piața muncii',
        pathCareerLabel:      'Schimbare de carieră',
        pathCareerDesc:       'Trecere la un nou domeniu sau industrie',
        pathStudentLabel:     'Elev/ă sau student/ă',
        pathStudentDesc:      'În formare sau aproape de finalizare',
        pathPauseLabel:       'Pauză profesională',
        pathPauseDesc:        'Întoarcere după o perioadă fără muncă',
        pathOtherLabel:       'Altele',
        pathOtherDesc:        'Situația mea este puțin diferită',
        completionHeading:    'CV-ul dvs. este gata 🎉',
        completionSubtitle:   'Răspunsurile dvs. au fost îmbunătățite și salvate. Descărcați CV-ul mai jos.',
        completionStats:      (ans, skipped) => `${ans} răspunse · ${skipped} omise`,
        exportPdf:            '⬇ Descarcă PDF',
        exportDocx:           '⬇ Descarcă Word (.docx)',
        exportJson:           '⬇ Exportă date (pentru formator)',
        exportRetry:          'Încearcă din nou',
        atsHeading:           '🎯 Cât de bine se potrivește CV-ul dvs.?',
        atsMatchedLabel:      'Cuvinte cheie găsite',
        atsMissingLabel:      'Cuvinte cheie lipsă',
        atsBtn:               '🎯 Analizează CV',
        atsAnalyzing:         'Se analizează...',
        coverLetterHeading:   '✉️ Scrisoarea dvs. de intenție',
        coverLetterBtn:       '✉️ Creează scrisoare de intenție',
        coverLetterCreating:  'Se creează...',
        reviewBtn:            '📋 Vezi Înainte & După',
        startOverBtn:         'Începe un CV nou',
        reviewHeading:        'Înainte & După — Răspunsurile dvs. îmbunătățite',
        reviewSubtitle:       'Acesta este ce vede formatorul dvs. la revizuire.',
        closeReviewBtn:       '← Înapoi la CV-ul meu',
        reviewColRaw:         'Ce ați scris',
        reviewColPolished:    'În CV-ul dvs.',
        confirmStartOver:     'Aceasta va șterge progresul curent.\n\nDoriți cu adevărat să începeți un CV nou?',
        consentText: 'Înțeleg că răspunsurile mele sunt salvate doar pe acest computer și nu sunt transmise pe internet.',
        profileSummaryLoading: 'Profilul dvs. este analizat…',
        profileSummaryHeading: '💡 Profilul dvs. de puncte forte',
        qualityHighText: 'CV puternic — va lăsa o impresie excelentă.', qualityHighTip: 'Descărcați și partajați acum!',
        qualityMedText: 'CV bun — câteva completări ar face-o și mai bun.',
        qualityMedTip1: 'Adăugați un detaliu la experiență', qualityMedTip2: 'Menționați instrumentele utilizate',
        qualityLowText: 'Un început solid — mai multe detalii ar consolida CV-ul.',
        qualityLowTip1: 'Descrieți o zi tipică la ultimul loc de muncă', qualityLowTip2: 'Enumerați abilitățile cunoscute',
        qualityLowTip3: 'Menționați cursuri sau certificate',
        qualityBaseText: 'CV-ul conține elementele de bază — puțin mai mult ar ajuta cu adevărat.',
        qualityBaseTip1: 'Completați întrebările omise', qualityBaseTip2: 'Chiar și o propoziție pe secțiune face diferența',
        statusSaving: 'Se salvează…', statusSaved: 'Salvat ✓', statusReady: 'Gata',
        statusError: 'Eroare', statusStarting: 'Se pornește…', statusResuming: 'Se reia…',
        statusSkipping: 'Se omite…', statusBuilding: 'Se creează CV-ul…', statusDone: 'Finalizat ✓',
        noSessionError: 'Nicio sesiune activă.',
        exportPreparing: (fmt) => `Se pregătește descărcarea ${fmt}…`, exportSuccess: (name) => `${name} descărcat.`,
        exportFailed: (msg) => `Descărcarea a eșuat: ${msg}`,
        coverLetterError: (msg) => `Nu s-a putut crea scrisoarea: ${msg}`,
        atsInputHeading:      '🎯 Inserați anunțul de angajare — îl vom compara cu CV-ul dvs.',
        atsInputDesc:         'Inserați anunțul de angajare mai jos. Sistemul va găsi automat cuvintele cheie potrivite.',
        jobDescPlaceholder:   'Inserați anunțul de angajare aici...',
        runAtsBtn:            'Analizează CV →',
        cancelAtsBtn:         'Anulează',
        clInputHeading:       '✉️ Personalizează scrisoarea de intenție',
        clCompanyLabel:       'Companie / Angajator:',
        clCompanyPlaceholder: 'ex. BILLA AG, Huber GmbH',
        clPositionLabel:      'Poziție / Titlu profesional:',
        clPositionPlaceholder:'ex. Lucrător depozit, Curățenie',
        generateCLBtn:        'Creează scrisoare de intenție →',
        cancelCLBtn:          'Anulează',
        photoUploadLabel:     'Alege fotografie (opțional)',
        photoHint:            'Fotografie profesională — opțional.',
        photoSkipLabel:       'Continuă fără fotografie',
        dateFromLabel:        'De la:',
        dateToLabel:          'Până la:',
        dateFromPlaceholder:  'ex. ian 2019, 2019',
        dateToPlaceholder:    'ex. mar 2022, prezent',
        dateHelperInsertBtn:  'Inserează în câmpul de răspuns ↓',
        dateHelperCompose:    (from, to) => `De la ${from} până la ${to}`,
        confirmDiscard:        'Chiar doriți să începeți din nou?',
        previewPlaceholderHint:'Continuați să scrieți — veți vedea rezultatul aici',
        typeMoreHint:          'Vă rugăm să scrieți puțin mai mult…',
    },
    uk: {
        dumpPromptUnemployed:   "Розкажіть мені все про себе — найкраще почніть з останньої роботи.",
        dumpPromptCareerSwitch: "Розкажіть мені все про себе — ким ви працювали досі та що хочете робити тепер?",
        dumpPromptStudent:      "Розкажіть мені все про себе — спершу освіта, практика та підробітки.",
        dumpPromptPause:        "Розкажіть мені все про себе — також про роботу до перерви. Перерва — це цілком нормально.",
        modeSwitchToGuided:   "Краще крок за кроком?",
        modeSwitchToFree:     "Краще розповідати вільно?",
        guidedSwitchMsg:      "Залюбки! Я ставитиму прості запитання — одне за одним. Ви можете повернутися будь-коли.",
        freeSwitchMsg:        "Залюбки! Просто розповідайте — я все впорядкую за вас.",
        jobSearchBtn:         "🔎 Знайти відповідні вакансії в AMS",
        jobSearchNotice:      (occ) => `Ми відкриємо біржу вакансій AMS у вашому браузері${occ ? ` з пошуком «${occ}»` : ""}. До AMS надсилається ЛИШЕ пошуковий запит — ваше ім'я, контакти та резюме НЕ надсилаються.`,
        jobSearchOpen:        "Шукати в AMS ↗",
        jobSearchCancel:      "Скасувати",
        jobSearchLoopHint:    "Порада: скопіюйте вакансію, що сподобалась, і вставте її вище — побачите, наскільки підходить ваше резюме.",
        appEmailBtn:          "📧 Створити лист для подачі заявки",
        appEmailHeading:      "📧 Ваш лист-заявка",
        appEmailToLabel:      "Кому (e-mail фірми, необов'язково):",
        appEmailSubjLabel:    "Тема:",
        appEmailHint:         (hasCL) => hasCL ? "Важливо: додайте завантажене резюме (PDF). Можете додати й супровідний лист." : "Важливо: додайте завантажене резюме (PDF) до листа.",
        appEmailOpen:         "Відкрити в поштовій програмі ↗",
        appEmailCopy:         "Копіювати текст",
        appEmailCopied:       "✓ Скопійовано",
        appEmailClose:        "Закрити",
        answerLabel:          'Ваша відповідь — пишіть будь-якою мовою:',
        answerPlaceholder:    'Просто починайте писати — навіть чернетки підійдуть. Ми автоматично покращимо.',
        submitBtn:            'Далі →',
        skipBtn:              'Пропустити питання',
        previewTitle:         'Ось як це виглядає у вашому резюме',
        previewRawLabel:      'Що ви написали',
        previewPolishedLabel: 'У вашому резюме',
        previewLoading:       'Покращуємо…',
        wordSingular:         'слово',
        wordPlural:           'слів',
        qualityShort:         'Трохи коротко — додайте ще одну деталь',
        qualityOk:            'Гарний початок — трохи більше допоможе',
        qualityGood:          'Чудово — цього достатньо!',
        langNote:             'Ви завжди можете писати кількома мовами — система автоматично розпізнає кожну мову.',
        step1Text:            'Що найкраще описує вашу поточну ситуацію?',
        step2Text:            'Як вас звати?',
        startBtn:             'Створити моє резюме →',
        startHintReady:       'Все готово — натисніть кнопку!',
        startHintBoth:        'Виберіть свою ситуацію вище і введіть ім\'я.',
        startHintPath:        'Виберіть свою ситуацію вище.',
        startHintName:        'Введіть своє ім\'я.',
        progressLabel:        (cur, tot) => `Питання ${cur} з ${tot}`,
        detectedLang:         (lang) => `Визначена мова: ${lang}`,
        resumeWelcomeStrong:  'Ласкаво просимо назад!',
        resumeBtn:            'Продовжити з того місця',
        dismissResumeBtn:     'Почати знову',
        resumeWelcome:        (name) => name ? `Ласкаво просимо назад, ${name}! Ваше резюме чекає.` : 'У вас є інтерв\'ю в процесі.',
        namePlaceholder:      'Введіть ваше ім\'я — напр. Марія',
        appSubtitle:          'Ваше професійне резюме — будь-якою мовою',
        trustHeadline:        'Ми автоматично перетворюємо ваші відповіді на професійне резюме.',
        trustDetail1:         '⏱ Приблизно 10–15 хвилин',
        trustDetail2:         '💾 Прогрес зберігається після кожної відповіді',
        trustDetail3:         '🌐 Пишіть будь-якою мовою',
        exampleGoodTitle:     '✅ Хороший приклад',
        exampleBadTitle:      '❌ Менш корисно',
        quickFillLabel:       'Швидкий старт — натисніть для вставки:',
        reaskTip:             'Порада',
        pathUnemployedLabel:  'Шукаю роботу',
        pathUnemployedDesc:   'Шукаю роботу або повертаюся на ринок праці',
        pathCareerLabel:      'Зміна кар\'єри',
        pathCareerDesc:       'Перехід до нової галузі або сфери',
        pathStudentLabel:     'Учень/учениця або студент/ка',
        pathStudentDesc:      'У процесі навчання або близько до закінчення',
        pathPauseLabel:       'Перерва в кар\'єрі',
        pathPauseDesc:        'Повернення після часу без роботи',
        pathOtherLabel:       'Інше',
        pathOtherDesc:        'Моя ситуація дещо інша',
        completionHeading:    'Ваше резюме готове 🎉',
        completionSubtitle:   'Ваші відповіді покращені та збережені. Завантажте резюме нижче.',
        completionStats:      (ans, skipped) => `${ans} відповіді · ${skipped} пропущено`,
        exportPdf:            '⬇ Завантажити PDF',
        exportDocx:           '⬇ Завантажити Word (.docx)',
        exportJson:           '⬇ Експортувати дані (для тренера)',
        exportRetry:          'Спробувати знову',
        atsHeading:           '🎯 Наскільки відповідає ваше резюме?',
        atsMatchedLabel:      'Знайдені ключові слова',
        atsMissingLabel:      'Відсутні ключові слова',
        atsBtn:               '🎯 Аналізувати резюме',
        atsAnalyzing:         'Аналізується...',
        coverLetterHeading:   '✉️ Ваш супровідний лист',
        coverLetterBtn:       '✉️ Створити супровідний лист',
        coverLetterCreating:  'Створюється...',
        reviewBtn:            '📋 До і Після',
        startOverBtn:         'Почати нове резюме',
        reviewHeading:        'До і Після — Ваші відповіді покращені',
        reviewSubtitle:       'Це бачить ваш тренер під час перевірки.',
        closeReviewBtn:       '← Повернутися до резюме',
        reviewColRaw:         'Що ви написали',
        reviewColPolished:    'У вашому резюме',
        confirmStartOver:     'Це видалить поточний прогрес.\n\nВи дійсно хочете почати нове резюме?',
        consentText: 'Я розумію, що мої відповіді зберігаються лише на цьому комп\'ютері і не передаються в інтернет.',
        profileSummaryLoading: 'Аналізується ваш профіль…',
        profileSummaryHeading: '💡 Ваш профіль сильних сторін',
        qualityHighText: 'Сильне резюме — справить чудове враження.', qualityHighTip: 'Завантажте та поділіться зараз!',
        qualityMedText: 'Гарне резюме — кілька доповнень зроблять його ще кращим.',
        qualityMedTip1: 'Додайте деталь про досвід', qualityMedTip2: 'Вкажіть інструменти або програми',
        qualityLowText: 'Добрий початок — більше деталей зміцнить резюме.',
        qualityLowTip1: 'Опишіть типовий робочий день', qualityLowTip2: 'Перерахуйте відомі навички',
        qualityLowTip3: 'Вкажіть курси або сертифікати',
        qualityBaseText: 'Резюме має основи — ще трохи деталей дійсно допоможе.',
        qualityBaseTip1: 'Заповніть пропущені запитання', qualityBaseTip2: 'Навіть одне речення на розділ має значення',
        statusSaving: 'Збереження…', statusSaved: 'Збережено ✓', statusReady: 'Готово',
        statusError: 'Помилка', statusStarting: 'Запуск…', statusResuming: 'Відновлення…',
        statusSkipping: 'Пропуск…', statusBuilding: 'Створення резюме…', statusDone: 'Готово ✓',
        noSessionError: 'Немає активної сесії.',
        exportPreparing: (fmt) => `Підготовка ${fmt}…`, exportSuccess: (name) => `${name} завантажено.`,
        exportFailed: (msg) => `Завантаження не вдалося: ${msg}`,
        coverLetterError: (msg) => `Не вдалося створити листа: ${msg}`,
        atsInputHeading:      '🎯 Вставте оголошення про вакансію — порівняємо з вашим резюме',
        atsInputDesc:         'Вставте оголошення про вакансію нижче. Система автоматично знайде відповідні ключові слова.',
        jobDescPlaceholder:   'Вставте оголошення про вакансію тут...',
        runAtsBtn:            'Аналізувати резюме →',
        cancelAtsBtn:         'Скасувати',
        clInputHeading:       '✉️ Персоналізувати супровідний лист',
        clCompanyLabel:       'Компанія / Роботодавець:',
        clCompanyPlaceholder: 'напр. BILLA AG, Huber GmbH',
        clPositionLabel:      'Посада / Назва роботи:',
        clPositionPlaceholder:'напр. Складський працівник',
        generateCLBtn:        'Створити супровідний лист →',
        cancelCLBtn:          'Скасувати',
        photoUploadLabel:     'Вибрати фото (необов\'язково)',
        photoHint:            'Професійне фото — необов\'язково.',
        photoSkipLabel:       'Продовжити без фото',
        dateFromLabel:        'З:',
        dateToLabel:          'По:',
        dateFromPlaceholder:  'напр. січ 2019, 2019',
        dateToPlaceholder:    'напр. бер 2022, зараз',
        dateHelperInsertBtn:  'Вставити в поле відповіді ↓',
        dateHelperCompose:    (from, to) => `З ${from} по ${to}`,
        confirmDiscard:        'Справді почати спочатку?',
        previewPlaceholderHint:'Продовжуйте писати — тут побачите результат',
        typeMoreHint:          'Будь ласка, напишіть трохи більше…',
    },
    ru: {
        dumpPromptUnemployed:   "Расскажите мне всё о себе — лучше всего начните с последней работы.",
        dumpPromptCareerSwitch: "Расскажите мне всё о себе — кем вы работали раньше и чем хотите заниматься теперь?",
        dumpPromptStudent:      "Расскажите мне всё о себе — сначала образование, практика и подработки.",
        dumpPromptPause:        "Расскажите мне всё о себе — в том числе о работе до перерыва. Перерыв — это совершенно нормально.",
        modeSwitchToGuided:   "Лучше шаг за шагом?",
        modeSwitchToFree:     "Лучше рассказать свободно?",
        guidedSwitchMsg:      "С удовольствием! Я буду задавать простые вопросы — по одному. Вернуться можно в любой момент.",
        freeSwitchMsg:        "С удовольствием! Просто рассказывайте — я всё упорядочу.",
        jobSearchBtn:         "🔎 Найти подходящие вакансии в AMS",
        jobSearchNotice:      (occ) => `Мы откроем биржу вакансий AMS в вашем браузере${occ ? ` с поиском «${occ}»` : ""}. В AMS отправляется ТОЛЬКО поисковый запрос — ваше имя, контакты и резюме НЕ отправляются.`,
        jobSearchOpen:        "Искать в AMS ↗",
        jobSearchCancel:      "Отмена",
        jobSearchLoopHint:    "Совет: скопируйте понравившуюся вакансию и вставьте её выше — увидите, насколько подходит ваше резюме.",
        appEmailBtn:          "📧 Создать письмо для отклика",
        appEmailHeading:      "📧 Ваше письмо-отклик",
        appEmailToLabel:      "Кому (e-mail фирмы, необязательно):",
        appEmailSubjLabel:    "Тема:",
        appEmailHint:         (hasCL) => hasCL ? "Важно: приложите скачанное резюме (PDF). Можно приложить и сопроводительное письмо." : "Важно: приложите скачанное резюме (PDF) к письму.",
        appEmailOpen:         "Открыть в почтовой программе ↗",
        appEmailCopy:         "Копировать текст",
        appEmailCopied:       "✓ Скопировано",
        appEmailClose:        "Закрыть",
        answerLabel:          'Ваш ответ — пишите на любом языке:',
        answerPlaceholder:    'Просто начните писать — черновики тоже подойдут. Мы автоматически улучшим.',
        submitBtn:            'Далее →',
        skipBtn:              'Пропустить вопрос',
        previewTitle:         'Так это выглядит в вашем резюме',
        previewRawLabel:      'Что вы написали',
        previewPolishedLabel: 'В вашем резюме',
        previewLoading:       'Улучшаем…',
        wordSingular:         'слово',
        wordPlural:           'слов',
        qualityShort:         'Немного коротко — добавьте ещё одну деталь',
        qualityOk:            'Хорошее начало — чуть больше было бы лучше',
        qualityGood:          'Отлично — этого достаточно!',
        langNote:             'Вы всегда можете писать на нескольких языках — система автоматически определяет каждый язык.',
        step1Text:            'Что лучше всего описывает вашу текущую ситуацию?',
        step2Text:            'Как вас зовут?',
        startBtn:             'Создать моё резюме →',
        startHintReady:       'Всё готово — нажмите кнопку!',
        startHintBoth:        'Пожалуйста, выберите ситуацию выше и введите имя.',
        startHintPath:        'Пожалуйста, выберите ситуацию выше.',
        startHintName:        'Пожалуйста, введите ваше имя.',
        progressLabel:        (cur, tot) => `Вопрос ${cur} из ${tot}`,
        detectedLang:         (lang) => `Определённый язык: ${lang}`,
        resumeWelcomeStrong:  'С возвращением!',
        resumeBtn:            'Продолжить с того места',
        dismissResumeBtn:     'Начать заново',
        resumeWelcome:        (name) => name ? `С возвращением, ${name}! Ваше резюме ждёт.` : 'У вас есть незавершённое интервью.',
        namePlaceholder:      'Введите ваше имя — напр. Мария',
        appSubtitle:          'Ваше профессиональное резюме — на любом языке',
        trustHeadline:        'Мы автоматически превращаем ваши ответы в профессиональное резюме.',
        trustDetail1:         '⏱ Примерно 10–15 минут',
        trustDetail2:         '💾 Прогресс сохраняется после каждого ответа',
        trustDetail3:         '🌐 Пишите на любом языке',
        exampleGoodTitle:     '✅ Хороший пример',
        exampleBadTitle:      '❌ Менее полезно',
        quickFillLabel:       'Быстрый старт — нажмите для вставки:',
        reaskTip:             'Совет',
        pathUnemployedLabel:  'Ищу работу',
        pathUnemployedDesc:   'Ищу работу или возвращаюсь на рынок труда',
        pathCareerLabel:      'Смена карьеры',
        pathCareerDesc:       'Переход в новую отрасль или сферу',
        pathStudentLabel:     'Ученик/ученица или студент/ка',
        pathStudentDesc:      'В процессе обучения или близко к окончанию',
        pathPauseLabel:       'Перерыв в карьере',
        pathPauseDesc:        'Возвращение после времени без работы',
        pathOtherLabel:       'Другое',
        pathOtherDesc:        'Моя ситуация немного иная',
        completionHeading:    'Ваше резюме готово 🎉',
        completionSubtitle:   'Ваши ответы улучшены и сохранены. Скачайте резюме ниже.',
        completionStats:      (ans, skipped) => `${ans} ответов · ${skipped} пропущено`,
        exportPdf:            '⬇ Скачать PDF',
        exportDocx:           '⬇ Скачать Word (.docx)',
        exportJson:           '⬇ Экспорт данных (для тренера)',
        exportRetry:          'Попробовать снова',
        atsHeading:           '🎯 Насколько подходит ваше резюме?',
        atsMatchedLabel:      'Найденные ключевые слова',
        atsMissingLabel:      'Отсутствующие ключевые слова',
        atsBtn:               '🎯 Анализировать резюме',
        atsAnalyzing:         'Анализируется...',
        coverLetterHeading:   '✉️ Ваше сопроводительное письмо',
        coverLetterBtn:       '✉️ Создать сопроводительное письмо',
        coverLetterCreating:  'Создаётся...',
        reviewBtn:            '📋 До и После',
        startOverBtn:         'Начать новое резюме',
        reviewHeading:        'До и После — Ваши ответы улучшены',
        reviewSubtitle:       'Это видит ваш тренер при проверке.',
        closeReviewBtn:       '← Вернуться к резюме',
        reviewColRaw:         'Что вы написали',
        reviewColPolished:    'В вашем резюме',
        confirmStartOver:     'Это удалит ваш текущий прогресс.\n\nВы действительно хотите начать новое резюме?',
        consentText: 'Я понимаю, что мои ответы хранятся только на этом компьютере и не передаются в интернет.',
        profileSummaryLoading: 'Анализируется ваш профиль…',
        profileSummaryHeading: '💡 Ваш профиль сильных сторон',
        qualityHighText: 'Сильное резюме — произведёт отличное впечатление.', qualityHighTip: 'Скачайте и поделитесь!',
        qualityMedText: 'Хорошее резюме — несколько дополнений сделают его ещё лучше.',
        qualityMedTip1: 'Добавьте деталь об опыте', qualityMedTip2: 'Упомяните используемые инструменты',
        qualityLowText: 'Хорошее начало — больше деталей укрепит резюме.',
        qualityLowTip1: 'Опишите типичный рабочий день', qualityLowTip2: 'Перечислите известные навыки',
        qualityLowTip3: 'Упомяните курсы или сертификаты',
        qualityBaseText: 'Резюме содержит основы — ещё немного деталей действительно поможет.',
        qualityBaseTip1: 'Заполните пропущенные вопросы', qualityBaseTip2: 'Даже одно предложение на раздел имеет значение',
        statusSaving: 'Сохранение…', statusSaved: 'Сохранено ✓', statusReady: 'Готово',
        statusError: 'Ошибка', statusStarting: 'Запуск…', statusResuming: 'Возобновление…',
        statusSkipping: 'Пропуск…', statusBuilding: 'Создание резюме…', statusDone: 'Завершено ✓',
        noSessionError: 'Нет активной сессии.',
        exportPreparing: (fmt) => `Подготовка ${fmt}…`, exportSuccess: (name) => `${name} скачано.`,
        exportFailed: (msg) => `Скачивание не удалось: ${msg}`,
        coverLetterError: (msg) => `Не удалось создать письмо: ${msg}`,
        atsInputHeading:      '🎯 Вставьте вакансию — сравним с вашим резюме',
        atsInputDesc:         'Вставьте объявление о вакансии ниже. Система автоматически найдёт подходящие ключевые слова.',
        jobDescPlaceholder:   'Вставьте вакансию сюда...',
        runAtsBtn:            'Анализировать резюме →',
        cancelAtsBtn:         'Отмена',
        clInputHeading:       '✉️ Персонализировать сопроводительное письмо',
        clCompanyLabel:       'Компания / Работодатель:',
        clCompanyPlaceholder: 'напр. BILLA AG, Huber GmbH',
        clPositionLabel:      'Должность / Название работы:',
        clPositionPlaceholder:'напр. Работник склада, Уборщик/ца',
        generateCLBtn:        'Создать сопроводительное письмо →',
        cancelCLBtn:          'Отмена',
        photoUploadLabel:     'Выбрать фото (необязательно)',
        photoHint:            'Профессиональное фото — необязательно.',
        photoSkipLabel:       'Продолжить без фото',
        dateFromLabel:        'С:',
        dateToLabel:          'По:',
        dateFromPlaceholder:  'напр. янв 2019, 2019',
        dateToPlaceholder:    'напр. мар 2022, сейчас',
        dateHelperInsertBtn:  'Вставить в поле ответа ↓',
        dateHelperCompose:    (from, to) => `С ${from} по ${to}`,
        confirmDiscard:        'Действительно начать заново?',
        previewPlaceholderHint:'Продолжайте писать — здесь увидите результат',
        typeMoreHint:          'Пожалуйста, напишите немного больше…',
    },
    ar: {
        dumpPromptUnemployed:   "أخبرني كل شيء عن نفسك — من الأفضل أن تبدأ بآخر عمل لك.",
        dumpPromptCareerSwitch: "أخبرني كل شيء عن نفسك — ماذا عملت حتى الآن وماذا تريد أن تعمل الآن؟",
        dumpPromptStudent:      "أخبرني كل شيء عن نفسك — التعليم والتدريب والأعمال الجانبية أولاً.",
        dumpPromptPause:        "أخبرني كل شيء عن نفسك — وأيضاً ماذا عملت قبل فترة التوقف. التوقف أمر طبيعي تماماً.",
        modeSwitchToGuided:   "هل تفضّل خطوة بخطوة؟",
        modeSwitchToFree:     "هل تفضّل أن تحكي بحرية؟",
        guidedSwitchMsg:      "بكل سرور! سأطرح عليك أسئلة بسيطة — واحداً تلو الآخر. يمكنك العودة في أي وقت.",
        freeSwitchMsg:        "بكل سرور! احكِ بحرية — وسأرتب كل شيء من أجلك.",
        jobSearchBtn:         "🔎 ابحث عن وظائف مناسبة لدى AMS",
        jobSearchNotice:      (occ) => `سنفتح بورصة وظائف AMS في متصفحك${occ ? ` مع البحث عن «${occ}»` : ""}. يُرسل إلى AMS مصطلح البحث فقط — اسمك وبياناتك وسيرتك الذاتية لا تُرسل.`,
        jobSearchOpen:        "ابحث لدى AMS ↗",
        jobSearchCancel:      "إلغاء",
        jobSearchLoopHint:    "نصيحة: انسخ إعلان وظيفة يعجبك والصقه في الأعلى — سترى مدى تطابق سيرتك الذاتية.",
        appEmailBtn:          "📧 إنشاء بريد التقديم",
        appEmailHeading:      "📧 بريد التقديم الخاص بك",
        appEmailToLabel:      "إلى (بريد الشركة، اختياري):",
        appEmailSubjLabel:    "الموضوع:",
        appEmailHint:         (hasCL) => hasCL ? "مهم: أرفق السيرة الذاتية (PDF) التي نزّلتها. يمكنك أيضاً إرفاق رسالة التقديم." : "مهم: أرفق السيرة الذاتية (PDF) التي نزّلتها بالبريد.",
        appEmailOpen:         "افتح في برنامج البريد ↗",
        appEmailCopy:         "نسخ النص",
        appEmailCopied:       "✓ تم النسخ",
        appEmailClose:        "إغلاق",
        answerLabel:          'إجابتك — اكتب بأي لغة تريد:',
        answerPlaceholder:    'فقط ابدأ الكتابة — حتى الملاحظات التقريبية مقبولة. سنحسنها تلقائيًا.',
        submitBtn:            'التالي →',
        skipBtn:              'تخطي السؤال',
        previewTitle:         'هكذا يبدو في سيرتك الذاتية',
        previewRawLabel:      'ما كتبته',
        previewPolishedLabel: 'في سيرتك الذاتية',
        previewLoading:       'جارٍ التحسين…',
        wordSingular:         'كلمة',
        wordPlural:           'كلمات',
        qualityShort:         'قصير قليلاً — أضف تفصيلاً واحداً',
        qualityOk:            'بداية جيدة — المزيد قليلاً سيساعد',
        qualityGood:          'ممتاز — هذا كافٍ!',
        langNote:             'يمكنك دائماً الكتابة بلغات متعددة — يتعرف النظام على كل لغة تلقائياً.',
        step1Text:            'ما الذي يصف وضعك الحالي بشكل أفضل؟',
        step2Text:            'ما اسمك؟',
        startBtn:             'أنشئ سيرتي الذاتية →',
        startHintReady:       'كل شيء جاهز — انقر الزر!',
        startHintBoth:        'الرجاء اختيار وضعك أعلاه وإدخال اسمك.',
        startHintPath:        'الرجاء اختيار وضعك أعلاه.',
        startHintName:        'الرجاء إدخال اسمك.',
        progressLabel:        (cur, tot) => `السؤال ${cur} من ${tot}`,
        detectedLang:         (lang) => `اللغة المكتشفة: ${lang}`,
        resumeWelcomeStrong:  'مرحباً بعودتك!',
        resumeBtn:            'متابعة من حيث توقفت',
        dismissResumeBtn:     'البدء من جديد',
        resumeWelcome:        (name) => name ? `مرحباً بعودتك، ${name}! سيرتك الذاتية تنتظرك.` : 'لديك مقابلة قيد التقدم.',
        namePlaceholder:      'أدخل اسمك — مثال: ماريا',
        appSubtitle:          'سيرتك الذاتية المهنية — بأي لغة',
        trustHeadline:        'نحوّل إجاباتك تلقائياً إلى سيرة ذاتية احترافية.',
        trustDetail1:         '⏱ حوالي 10–15 دقيقة',
        trustDetail2:         '💾 يتم حفظ التقدم بعد كل إجابة',
        trustDetail3:         '🌐 اكتب بأي لغة',
        exampleGoodTitle:     '✅ مثال جيد',
        exampleBadTitle:      '❌ أقل فائدة',
        quickFillLabel:       'بداية سريعة — انقر للإدراج:',
        reaskTip:             'نصيحة',
        pathUnemployedLabel:  'أبحث عن عمل',
        pathUnemployedDesc:   'أبحث عن عمل أو أعود إلى سوق العمل',
        pathCareerLabel:      'تغيير مسار مهني',
        pathCareerDesc:       'الانتقال إلى مجال أو قطاع جديد',
        pathStudentLabel:     'طالب/ة أو متدرب/ة',
        pathStudentDesc:      'في التعليم أو على وشك الانتهاء',
        pathPauseLabel:       'استراحة مهنية',
        pathPauseDesc:        'العودة بعد فترة بعيداً عن العمل',
        pathOtherLabel:       'أخرى',
        pathOtherDesc:        'وضعي مختلف قليلاً',
        completionHeading:    'سيرتك الذاتية جاهزة 🎉',
        completionSubtitle:   'تم تحسين إجاباتك وحفظها. قم بتنزيل سيرتك الذاتية أدناه.',
        completionStats:      (ans, skipped) => `${ans} أجوبة · ${skipped} مُتخطاة`,
        exportPdf:            '⬇ تنزيل PDF',
        exportDocx:           '⬇ تنزيل Word (.docx)',
        exportJson:           '⬇ تصدير البيانات (للمدرب)',
        exportRetry:          'حاول مرة أخرى',
        atsHeading:           '🎯 مدى ملاءمة سيرتك الذاتية',
        atsMatchedLabel:      'الكلمات المفتاحية الموجودة',
        atsMissingLabel:      'الكلمات المفتاحية المفقودة',
        atsBtn:               '🎯 تحليل السيرة الذاتية',
        atsAnalyzing:         'جارٍ التحليل...',
        coverLetterHeading:   '✉️ خطاب التقديم',
        coverLetterBtn:       '✉️ إنشاء خطاب تقديم',
        coverLetterCreating:  'جارٍ الإنشاء...',
        reviewBtn:            '📋 قبل وبعد',
        startOverBtn:         'ابدأ سيرة ذاتية جديدة',
        reviewHeading:        'قبل وبعد — إجاباتك المحسّنة',
        reviewSubtitle:       'هذا ما يراه مدربك عند مراجعة عملك.',
        closeReviewBtn:       '← العودة إلى سيرتي الذاتية',
        reviewColRaw:         'ما كتبته',
        reviewColPolished:    'في سيرتك الذاتية',
        confirmStartOver:     'سيؤدي هذا إلى حذف تقدمك الحالي.\n\nهل تريد فعلاً بدء سيرة ذاتية جديدة؟',
        consentText: 'أفهم أن إجاباتي محفوظة فقط على هذا الكمبيوتر ولا يتم نقلها إلى الإنترنت.',
        profileSummaryLoading: 'جاري تحليل ملفك الشخصي…',
        profileSummaryHeading: '💡 ملف نقاط قوتك',
        qualityHighText: 'سيرة ذاتية قوية — ستترك انطباعاً رائعاً.', qualityHighTip: 'قم بتنزيلها ومشاركتها الآن!',
        qualityMedText: 'سيرة ذاتية جيدة — بعض الإضافات الصغيرة ستجعلها أفضل.',
        qualityMedTip1: 'أضف تفصيلاً عن الخبرة', qualityMedTip2: 'اذكر الأدوات أو البرامج المستخدمة',
        qualityLowText: 'بداية متينة — المزيد من التفاصيل سيقوي السيرة الذاتية.',
        qualityLowTip1: 'صف يوماً عملياً نموذجياً', qualityLowTip2: 'اذكر المهارات والأدوات التي تعرفها',
        qualityLowTip3: 'اذكر الدورات أو الشهادات',
        qualityBaseText: 'تحتوي السيرة الذاتية على الأساسيات — مزيد من التفاصيل سيساعد حقاً.',
        qualityBaseTip1: 'أكمل الأسئلة التي تخطيتها', qualityBaseTip2: 'حتى جملة واحدة في كل قسم تحدث فرقاً',
        statusSaving: 'جارٍ الحفظ…', statusSaved: 'تم الحفظ ✓', statusReady: 'جاهز',
        statusError: 'خطأ', statusStarting: 'جارٍ البدء…', statusResuming: 'جارٍ الاستئناف…',
        statusSkipping: 'جارٍ التخطي…', statusBuilding: 'جارٍ إنشاء السيرة…', statusDone: 'تم ✓',
        noSessionError: 'لا توجد جلسة نشطة.',
        exportPreparing: (fmt) => `جارٍ تحضير ${fmt}…`, exportSuccess: (name) => `تم تنزيل ${name}.`,
        exportFailed: (msg) => `فشل التنزيل: ${msg}`,
        coverLetterError: (msg) => `تعذّر إنشاء الخطاب: ${msg}`,
        atsInputHeading:      '🎯 الصق إعلان الوظيفة — سنقارنه بسيرتك الذاتية',
        atsInputDesc:         'الصق إعلان الوظيفة أدناه. سيجد النظام تلقائياً الكلمات المفتاحية المناسبة.',
        jobDescPlaceholder:   'الصق إعلان الوظيفة هنا...',
        runAtsBtn:            'تحليل السيرة الذاتية →',
        cancelAtsBtn:         'إلغاء',
        clInputHeading:       '✉️ تخصيص خطاب التقديم',
        clCompanyLabel:       'الشركة / صاحب العمل:',
        clCompanyPlaceholder: 'مثال: BILLA AG، Huber GmbH',
        clPositionLabel:      'المنصب / المسمى الوظيفي:',
        clPositionPlaceholder:'مثال: عامل مستودع، عامل نظافة',
        generateCLBtn:        'إنشاء خطاب تقديم →',
        cancelCLBtn:          'إلغاء',
        photoUploadLabel:     'اختر صورة (اختياري)',
        photoHint:            'صورة احترافية — اختيارية.',
        photoSkipLabel:       'المتابعة بدون صورة',
        dateFromLabel:        'من:',
        dateToLabel:          'إلى:',
        dateFromPlaceholder:  'مثال: يناير 2019، 2019',
        dateToPlaceholder:    'مثال: مارس 2022، حاليًا',
        dateHelperInsertBtn:  'إدراج في حقل الإجابة ↓',
        dateHelperCompose:    (from, to) => `من ${from} إلى ${to}`,
        confirmDiscard:        'هل تريد حقاً البدء من جديد؟',
        previewPlaceholderHint:'واصل الكتابة — ستظهر النتيجة هنا',
        typeMoreHint:          'يرجى الكتابة أكثر قليلاً…',
    },
    sk: {
        dumpPromptUnemployed:   "Porozprávajte mi všetko o sebe — najlepšie začnite poslednou prácou.",
        dumpPromptCareerSwitch: "Porozprávajte mi všetko o sebe — čo ste doteraz robili a čo chcete robiť teraz?",
        dumpPromptStudent:      "Porozprávajte mi všetko o sebe — najprv vzdelanie, prax a brigády.",
        dumpPromptPause:        "Porozprávajte mi všetko o sebe — aj o práci pred prestávkou. Prestávka je úplne v poriadku.",
        modeSwitchToGuided:   "Radšej krok za krokom?",
        modeSwitchToFree:     "Radšej rozprávať voľne?",
        guidedSwitchMsg:      "Rád! Budem vám klásť jednoduché otázky — jednu po druhej. Kedykoľvek sa môžete vrátiť.",
        freeSwitchMsg:        "Rád! Jednoducho rozprávajte — všetko za vás usporiadam.",
        jobSearchBtn:         "🔎 Nájdite vhodné pracovné miesta na AMS",
        jobSearchNotice:      (occ) => `Otvoríme burzu práce AMS vo vašom prehliadači${occ ? ` s vyhľadávaním „${occ}“` : ""}. Do AMS sa odošle IBA hľadaný výraz — vaše meno, kontakty a životopis sa NEODOSIELAJÚ.`,
        jobSearchOpen:        "Hľadať na AMS ↗",
        jobSearchCancel:      "Zrušiť",
        jobSearchLoopHint:    "Tip: skopírujte inzerát, ktorý sa vám páči, a vložte ho vyššie — uvidíte, ako dobre váš životopis sedí.",
        appEmailBtn:          "📧 Vytvoriť e-mail so žiadosťou",
        appEmailHeading:      "📧 Váš e-mail so žiadosťou",
        appEmailToLabel:      "Komu (e-mail firmy, voliteľné):",
        appEmailSubjLabel:    "Predmet:",
        appEmailHint:         (hasCL) => hasCL ? "Dôležité: priložte stiahnutý životopis (PDF). Môžete priložiť aj motivačný list." : "Dôležité: priložte stiahnutý životopis (PDF) k e-mailu.",
        appEmailOpen:         "Otvoriť v e-mailovom programe ↗",
        appEmailCopy:         "Kopírovať text",
        appEmailCopied:       "✓ Skopírované",
        appEmailClose:        "Zavrieť",
        answerLabel:          'Vaša odpoveď — píšte v akomkoľvek jazyku:',
        answerPlaceholder:    'Len začnite písať — aj hrubé poznámky sú v poriadku. Automaticky to vylepšíme.',
        submitBtn:            'Ďalej →',
        skipBtn:              'Preskočiť otázku',
        previewTitle:         'Takto to vyzerá vo vašom životopise',
        previewRawLabel:      'Čo ste napísali',
        previewPolishedLabel: 'Vo vašom životopise',
        previewLoading:       'Vylepšujeme…',
        wordSingular:         'slovo',
        wordPlural:           'slov',
        qualityShort:         'Trochu krátke — pridajte ešte jeden detail',
        qualityOk:            'Dobrý začiatok — trochu viac by pomohlo',
        qualityGood:          'Výborne — to stačí!',
        langNote:             'Vždy môžete písať vo viacerých jazykoch — systém automaticky rozpozná každý jazyk.',
        step1Text:            'Čo najlepšie opisuje vašu aktuálnu situáciu?',
        step2Text:            'Ako sa voláte?',
        startBtn:             'Vytvoriť môj životopis →',
        startHintReady:       'Všetko pripravené — kliknite na tlačidlo!',
        startHintBoth:        'Vyberte svoju situáciu vyššie a zadajte meno.',
        startHintPath:        'Vyberte svoju situáciu vyššie.',
        startHintName:        'Zadajte svoje krstné meno.',
        progressLabel:        (cur, tot) => `Otázka ${cur} z ${tot}`,
        detectedLang:         (lang) => `Rozpoznaný jazyk: ${lang}`,
        resumeWelcomeStrong:  'Vitajte späť!',
        resumeBtn:            'Pokračovať od miesta, kde som skončil/a',
        dismissResumeBtn:     'Začať odznova',
        resumeWelcome:        (name) => name ? `Vitajte späť, ${name}! Váš životopis čaká.` : 'Máte nedokončený pohovor.',
        namePlaceholder:      'Zadajte meno — napr. Maria',
        appSubtitle:          'Váš profesionálny životopis — v akomkoľvek jazyku',
        trustHeadline:        'Automaticky pretvárame vaše odpovede na profesionálny životopis.',
        trustDetail1:         '⏱ Približne 10–15 minút',
        trustDetail2:         '💾 Postup uložený po každej odpovedi',
        trustDetail3:         '🌐 Píšte v akomkoľvek jazyku',
        exampleGoodTitle:     '✅ Dobrý príklad',
        exampleBadTitle:      '❌ Menej užitočné',
        quickFillLabel:       'Rýchly štart — kliknite na vloženie:',
        reaskTip:             'Tip',
        pathUnemployedLabel:  'Hľadám prácu',
        pathUnemployedDesc:   'Hľadám prácu alebo sa vraciam na trh práce',
        pathCareerLabel:      'Zmena kariéry',
        pathCareerDesc:       'Prechod do nového odvetvia alebo oblasti',
        pathStudentLabel:     'Žiak/žiačka alebo študent/ka',
        pathStudentDesc:      'Vo vzdelávaní alebo blízko ukončenia',
        pathPauseLabel:       'Kariérna prestávka',
        pathPauseDesc:        'Návrat po období bez práce',
        pathOtherLabel:       'Iné',
        pathOtherDesc:        'Moja situácia je trochu iná',
        completionHeading:    'Váš životopis je hotový 🎉',
        completionSubtitle:   'Vaše odpovede boli vylepšené a uložené. Stiahnite životopis nižšie.',
        completionStats:      (ans, skipped) => `${ans} zodpovedaných · ${skipped} preskočených`,
        exportPdf:            '⬇ Stiahnuť PDF',
        exportDocx:           '⬇ Stiahnuť Word (.docx)',
        exportJson:           '⬇ Exportovať dáta (pre trénera)',
        exportRetry:          'Skúsiť znova',
        atsHeading:           '🎯 Ako dobre zodpovedá váš životopis?',
        atsMatchedLabel:      'Nájdené kľúčové slová',
        atsMissingLabel:      'Chýbajúce kľúčové slová',
        atsBtn:               '🎯 Analyzovať životopis',
        atsAnalyzing:         'Analyzuje sa...',
        coverLetterHeading:   '✉️ Váš motivačný list',
        coverLetterBtn:       '✉️ Vytvoriť motivačný list',
        coverLetterCreating:  'Vytvára sa...',
        reviewBtn:            '📋 Pred & Po',
        startOverBtn:         'Začať nový životopis',
        reviewHeading:        'Pred & Po — Vaše odpovede vylepšené',
        reviewSubtitle:       'Toto vidí váš tréner pri kontrole vašej práce.',
        closeReviewBtn:       '← Späť na môj životopis',
        reviewColRaw:         'Čo ste napísali',
        reviewColPolished:    'Vo vašom životopise',
        confirmStartOver:     'Tým sa vymaže váš súčasný postup.\n\nNaozaj chcete začať nový životopis?',
        consentText: 'Chápem, že moje odpovede sú uložené iba na tomto počítači a nie sú odosielané na internet.',
        profileSummaryLoading: 'Analyzuje sa váš profil…',
        profileSummaryHeading: '💡 Váš profil silných stránok',
        qualityHighText: 'Silný životopis — zanechá výborný dojem.', qualityHighTip: 'Stiahnite a zdieľajte teraz!',
        qualityMedText: 'Dobrý životopis — niekoľko malých doplnení by ho ešte zlepšilo.',
        qualityMedTip1: 'Pridajte detail k skúsenosti', qualityMedTip2: 'Uveďte nástroje alebo softvér',
        qualityLowText: 'Solídny začiatok — viac detailov by ho posilnilo.',
        qualityLowTip1: 'Opíšte typický pracovný deň', qualityLowTip2: 'Uveďte zručnosti a nástroje',
        qualityLowTip3: 'Uveďte kurzy alebo certifikáty',
        qualityBaseText: 'Životopis má základy — trochu viac detailov by skutočne pomohlo.',
        qualityBaseTip1: 'Doplňte preskočené otázky', qualityBaseTip2: 'Aj jedna veta v sekcii robí rozdiel',
        statusSaving: 'Ukladanie…', statusSaved: 'Uložené ✓', statusReady: 'Pripravený',
        statusError: 'Chyba', statusStarting: 'Spúšťanie…', statusResuming: 'Pokračovanie…',
        statusSkipping: 'Preskakuje sa…', statusBuilding: 'Vytvára sa životopis…', statusDone: 'Hotovo ✓',
        noSessionError: 'Žiadna aktívna relácia.',
        exportPreparing: (fmt) => `Pripravuje sa ${fmt}…`, exportSuccess: (name) => `${name} stiahnuté.`,
        exportFailed: (msg) => `Stiahnutie zlyhalo: ${msg}`,
        coverLetterError: (msg) => `Motivačný list sa nepodarilo vytvoriť: ${msg}`,
        atsInputHeading:      '🎯 Vložte pracovnú ponuku — porovnáme ju s vaším životopisom',
        atsInputDesc:         'Vložte pracovnú ponuku nižšie. Systém automaticky nájde zodpovedajúce kľúčové slová.',
        jobDescPlaceholder:   'Vložte pracovnú ponuku sem...',
        runAtsBtn:            'Analyzovať životopis →',
        cancelAtsBtn:         'Zrušiť',
        clInputHeading:       '✉️ Personalizovať motivačný list',
        clCompanyLabel:       'Spoločnosť / Zamestnávateľ:',
        clCompanyPlaceholder: 'napr. BILLA AG, Huber GmbH',
        clPositionLabel:      'Pozícia / Pracovný titul:',
        clPositionPlaceholder:'napr. Skladník/ačka, Upratovač/ka',
        generateCLBtn:        'Vytvoriť motivačný list →',
        cancelCLBtn:          'Zrušiť',
        photoUploadLabel:     'Vybrať fotografiu (voliteľné)',
        photoHint:            'Profesionálna fotografia — voliteľné.',
        photoSkipLabel:       'Pokračovať bez fotografie',
        dateFromLabel:        'Od:',
        dateToLabel:          'Do:',
        dateFromPlaceholder:  'napr. jan 2019, 2019',
        dateToPlaceholder:    'napr. mar 2022, dnes',
        dateHelperInsertBtn:  'Vložiť do poľa odpovede ↓',
        dateHelperCompose:    (from, to) => `Od ${from} do ${to}`,
        confirmDiscard:        'Naozaj chcete začať odznova?',
        previewPlaceholderHint:'Pokračujte v písaní — výsledok uvidíte tu',
        typeMoreHint:          'Prosím napíšte trochu viac…',
    },
};

/** Get a translated string for the current inputLanguage. Falls back to German. */
function t(key, ...args) {
    const lang = state?.inputLanguage || 'de';
    const dict = TRANSLATIONS[lang] || TRANSLATIONS.de;
    const val  = dict[key] ?? TRANSLATIONS.de[key] ?? key;
    return typeof val === 'function' ? val(...args) : val;
}

/** The free-form opening, flavoured by the chosen interview path — so the path
 *  selection actually changes the conversation, not just a stored label. */
function dumpPromptForPath() {
    const map = {
        'unemployed':    'dumpPromptUnemployed',
        'career-switch': 'dumpPromptCareerSwitch',
        'student':       'dumpPromptStudent',
        'pause':         'dumpPromptPause',
    };
    const key = map[state?.interviewPath];
    if (key) {
        const v = t(key);
        if (v && v !== key) return v;  // t() returns the raw key when missing
    }
    return t('dumpPrompt');
}

/**
 * Push all translated strings into the DOM.
 * Called whenever the user switches language.
 */
function applyTranslations() {
    const lang = state.inputLanguage;

    // RTL support for Arabic
    document.documentElement.dir = (lang === 'ar') ? 'rtl' : 'ltr';

    // Helper — set text if element exists
    const setText = (id, key) => { const el = document.getElementById(id); if (el) el.textContent = t(key); };
    const setPlaceholder = (id, key) => { const el = document.getElementById(id); if (el) el.placeholder = t(key); };

    // --- Header ---
    setText('appSubtitle', 'appSubtitle');

    // --- Trust block ---
    setText('trustHeadline', 'trustHeadline');
    setText('trustDetail1',  'trustDetail1');
    setText('trustDetail2',  'trustDetail2');
    setText('trustDetail3',  'trustDetail3');

    // --- Resume banner ---
    setText('resumeWelcomeStrong', 'resumeWelcomeStrong');
    setText('resumeBtn',           'resumeBtn');
    setText('dismissResumeBtn',    'dismissResumeBtn');

    // --- Welcome screen steps ---
    setText('step1Text', 'step1Text');
    setText('step2Text', 'step2Text');
    setText('langNote',  'langNote');
    setPlaceholder('userIdInput', 'namePlaceholder');

    // --- Path buttons (by data-path) ---
    const pathMap = {
        'unemployed':    ['pathUnemployedLabel', 'pathUnemployedDesc'],
        'career-switch': ['pathCareerLabel',      'pathCareerDesc'],
        'student':       ['pathStudentLabel',      'pathStudentDesc'],
        'pause':         ['pathPauseLabel',        'pathPauseDesc'],
        'other':         ['pathOtherLabel',        'pathOtherDesc'],
    };
    document.querySelectorAll('.path-button').forEach(btn => {
        const keys = pathMap[btn.dataset.path];
        if (!keys) return;
        const labelEl = btn.querySelector('.path-label');
        const descEl  = btn.querySelector('.path-desc');
        if (labelEl) labelEl.textContent = t(keys[0]);
        if (descEl)  descEl.textContent  = t(keys[1]);
    });

    // --- Start button & hint ---
    const startBtnEl = document.getElementById('startBtn');
    if (startBtnEl) startBtnEl.textContent = t('startBtn');

    // --- Interview screen ---
    setText('answerLabel',          'answerLabel');
    setPlaceholder('answerInput',   'answerPlaceholder');
    setText('submitBtn',            'submitBtn');
    setText('skipBtn',              'skipBtn');
    setText('previewTitle',         'previewTitle');
    setText('previewRawLabel',      'previewRawLabel');
    setText('previewPolishedLabel', 'previewPolishedLabel');
    setText('previewLoadingSpan',   'previewLoading');
    setText('exampleGoodTitle',     'exampleGoodTitle');
    setText('exampleBadTitle',      'exampleBadTitle');

    // --- Completion screen ---
    setText('completionHeading',  'completionHeading');
    setText('completionSubtitle', 'completionSubtitle');
    setText('exportBtn',          'exportPdf');
    setText('exportDocxBtn',      'exportDocx');
    setText('exportJsonBtn',      'exportJson');
    setText('exportRetryBtn',     'exportRetry');
    setText('completionMoreSummary', 'completionMoreSummary');

    // --- Finish-later row ---
    setText('finishLaterLabel', 'finishLaterBtn');
    setText('finishLaterHint',  'finishLaterHint');
    setText('atsHeading',         'atsHeading');
    setText('atsMatchedLabel',    'atsMatchedLabel');
    setText('atsMissingLabel',    'atsMissingLabel');
    setText('atsBtn',             'atsBtn');
    setText('amsJobsBtn',         'jobSearchBtn');
    setText('amsJobsCancelBtn',   'jobSearchCancel');
    setText('appEmailBtn',        'appEmailBtn');
    setText('appEmailHeading',    'appEmailHeading');
    setText('appEmailToLabel',    'appEmailToLabel');
    setText('appEmailSubjLabel',  'appEmailSubjLabel');
    setText('appEmailOpenBtn',    'appEmailOpen');
    setText('appEmailCopyBtn',    'appEmailCopy');
    setText('appEmailCancelBtn',  'appEmailClose');
    setText('coverLetterHeading', 'coverLetterHeading');
    setText('coverLetterBtn',     'coverLetterBtn');
    setText('reviewBtn',          'reviewBtn');
    setText('startOverBtn',       'startOverBtn');

    // --- Review panel ---
    setText('reviewHeading',   'reviewHeading');
    setText('reviewSubtitle',  'reviewSubtitle');
    setText('closeReviewBtn',  'closeReviewBtn');
    setText('consentText',     'consentText');

    // --- ATS input section ---
    setText('atsInputHeading',    'atsInputHeading');
    setText('atsInputDesc',       'atsInputDesc');
    setPlaceholder('jobDescInput','jobDescPlaceholder');
    setText('runAtsBtnLabel',     'runAtsBtn');
    setText('cancelAtsBtnLabel',  'cancelAtsBtn');

    // --- Cover letter input section ---
    setText('clInputHeading',         'clInputHeading');
    setText('clCompanyLabelText',     'clCompanyLabel');
    setPlaceholder('clCompanyInput',  'clCompanyPlaceholder');
    setText('clPositionLabelText',    'clPositionLabel');
    setPlaceholder('clPositionInput', 'clPositionPlaceholder');
    setText('generateCLBtnLabel',     'generateCLBtn');
    setText('cancelCLBtnLabel',       'cancelCLBtn');

    // --- Photo upload ---
    setText('photoUploadLabelText', 'photoUploadLabel');
    setText('photoHint',            'photoHint');
    setText('photoSkipLabel',       'photoSkipLabel');

    // --- Date helper ---
    setText('dateFromLabel',            'dateFromLabel');
    setText('dateToLabel',              'dateToLabel');
    setPlaceholder('dateFromInput',     'dateFromPlaceholder');
    setPlaceholder('dateToInput',       'dateToPlaceholder');
    setText('dateHelperInsertBtn',      'dateHelperInsertBtn');

    // Re-render dynamic strings that depend on current state
    ui?.updateStartButton();
    ui?.updateWordCount();
    ui?.updateQualityIndicator();

}

// ============================================================================
// State Management
// ============================================================================

const state = {
    // Session
    sessionId: null,
    userId: null,
    interviewPath: null,
    language: 'de',
    inputLanguage: 'de',  // UI display + input hint language (set by language picker)

    // Current question
    currentQuestion: null,
    currentQuestionIndex: 0,
    totalQuestions: 5,

    // Progress
    answersSubmitted: 0,

    // Answer tracking
    answers: {},           // raw text by question_id
    polishedAnswers: {},   // polished versions by question_id (for review panel)
    cvEntries: [],         // [{label, raw, polished}] — feeds the live CV panel
    overallQuality: null,
    photoDataUrl: null,    // base64 photo selected during interview
    followUpPending: false, // true while waiting for user to respond to follow-up

    // UI
    isWaitingForResponse: false,
    currentScreen: 'welcome',
    previewDebounceTimer: null,

    // Test/dev capture mode (for the trainer collecting test cases). Hidden from
    // participants; toggled with Ctrl+Shift+T. When on, the completion screen
    // offers a one-click "save this case as a test file" (raw input + result).
    testMode: false,
    testInputs: [],   // {type, q?, text} raw inputs typed this session
};

// ============================================================================
// API Client
// ============================================================================

class APIClient {
    constructor() {
        this.interviewBase = '/api/interview';
        this.exportBase    = '/api/export';
    }

    async _request(url, method = 'GET', data = null, extraHeaders = null) {
        try {
            const options = { method, headers: { 'Content-Type': 'application/json', ...(extraHeaders || {}) } };
            if (data) options.body = JSON.stringify(data);
            const response = await fetch(url, options);
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error [${method} ${url}]:`, error);
            throw error;
        }
    }

    post(url, data) {
        return this._request(url, 'POST', data);
    }

    get(url) {
        return this._request(url, 'GET');
    }

    startInterview(userId, path, language = 'de', consentGiven = false) {
        return this._request(`${this.interviewBase}/start`, 'POST', {
            user_id: userId,
            interview_path: path,
            language,
            consent_given: !!consentGiven,
            consent_text_version: 'v1',
        });
    }

    getNextQuestion(sessionId) {
        return this._request(`${this.interviewBase}/next-question/${sessionId}`);
    }

    submitAnswer(sessionId, questionId, answerText) {
        return this._request(`${this.interviewBase}/submit-answer`, 'POST', {
            session_id: sessionId,
            question_id: questionId,
            answer_text: answerText,
        });
    }

    skipQuestion(sessionId, questionId) {
        return this._request(`${this.interviewBase}/skip-question`, 'POST', {
            session_id: sessionId,
            question_id: questionId,
        });
    }

    resumeInterview(sessionId) {
        return this._request(`${this.interviewBase}/resume`, 'POST', { session_id: sessionId });
    }

    getStatus(sessionId) {
        return this._request(`${this.interviewBase}/status/${sessionId}`);
    }

    completeInterview(sessionId) {
        return this._request(`${this.interviewBase}/complete/${sessionId}`, 'POST');
    }

    // Live preview — no session required
    previewAnswer(answerText, category = 'experience', language = '') {
        return this._request(`${this.interviewBase}/preview`, 'POST', {
            answer_text: answerText,
            category,
            language,
        });
    }

    // DSGVO Art. 17 — permanently erase all of the participant's data.
    // Ownership proof goes in HEADERS, never the URL (avoids leaking the token to
    // access logs / browser history).
    eraseMyData(sessionId, userId, token) {
        return this._request(`/api/cv/${sessionId}/erase`, 'DELETE', null,
            { 'X-Session-Token': token || '', 'X-User-Id': userId || '' });
    }

    // DSGVO Art. 20 — download all stored data as a JSON blob (token in header).
    async downloadMyData(sessionId, userId, token) {
        const resp = await fetch(`/api/cv/${sessionId}/my-data`, {
            headers: { 'X-Session-Token': token || '', 'X-User-Id': userId || '' },
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = `meine-daten-${sessionId}.json`;
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    // Export — returns raw Response so caller can stream the blob
    async exportFile(format, sessionId, language = 'de', photoDataUrl = null) {
        const body = { session_id: sessionId, language, force: true };
        if (photoDataUrl) body.photo = photoDataUrl;
        const response = await fetch(`${this.exportBase}/${format}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Export failed (${response.status})`);
        }
        return response;
    }

    // §5 ATS scoring — reuses existing backend endpoint
    getATSScore(sessionId, jobDescription = '') {
        return this._request('/api/ats/score', 'POST', {
            session_id: sessionId,
            job_description: jobDescription,
        });
    }

    // AMS job-search bridge (Tier 0 deep-link). Backend only builds a URL string —
    // no data is transmitted; the user's own browser opens the link.
    getAmsJobLink(targetJob = '', location = '') {
        const q = new URLSearchParams({ target_job: targetJob, location });
        return this._request(`/api/jobs/ams-search?${q.toString()}`);
    }

    getAIStatus() {
        return this._request(`${this.interviewBase}/ai/status`);
    }

    refreshAI() {
        return this._request(`${this.interviewBase}/ai/refresh`, 'POST');
    }

    // Conversational follow-up — no save, just a probe question
    getFollowUp(sessionId, questionId, answerText, language = 'de') {
        return this._request(`${this.interviewBase}/follow-up`, 'POST', {
            session_id: sessionId,
            question_id: questionId,
            answer_text: answerText,
            language,
        });
    }

    // §6 Cover letter — reuses existing backend endpoint
    getCoverLetter(sessionId, options = {}) {
        return this._request(`${this.exportBase}/cover-letter`, 'POST', {
            session_id: sessionId,
            job_title: options.jobTitle || '',
            employer_name: options.employerName || '',
            tone: options.tone || 'formal',
            language: options.language || 'de',
            force: true,
        });
    }

    // Free-form "dump" extraction — structure a big block of text into CV fields.
    // `expect` (optional) tells the backend which gap a short reply answers.
    dumpExtract(sessionId, text, language = 'de', expect = null) {
        return this._request('/api/ai/dump-extract', 'POST', {
            session_id: sessionId, text, language, expect,
        });
    }

    // Reconstruct the captured/missing snapshot from stored answers (for resume).
    dumpSnapshot(sessionId) {
        return this._request(`/api/ai/dump-snapshot/${sessionId}`, 'GET');
    }

    // AI Interview Coach — context-aware help during the interview
    coachMessage(message, opts = {}) {
        return this._request('/api/ai/interview-coach', 'POST', {
            message,
            session_id: opts.sessionId ?? null,
            language: opts.language ?? 'de',
            question_id: opts.questionId ?? null,
            question_text: opts.questionText ?? null,
        });
    }
}

const api = new APIClient();

// ============================================================================
// UI Manager
// ============================================================================

class UIManager {
    constructor() {
        // Screens
        this.welcomeScreen    = document.getElementById('welcomeScreen');
        this.interviewScreen  = document.getElementById('interviewScreen');
        this.completionScreen = document.getElementById('completionScreen');
        this.reviewPanel      = document.getElementById('reviewPanel');

        // Welcome
        this.resumeBanner     = document.getElementById('resumeBanner');
        this.startBtn         = document.getElementById('startBtn');

        // Interview
        this.answerInput      = document.getElementById('answerInput');
        this.submitBtn        = document.getElementById('submitBtn');
        this.skipBtn          = document.getElementById('skipBtn');
        this.questionText     = document.getElementById('questionText');
        this.questionHint     = document.getElementById('questionHint');
        this.goodExample      = document.getElementById('goodExample');
        this.badExample       = document.getElementById('badExample');
        this.progressLabel    = document.getElementById('progressLabel');
        this.progressPercent  = document.getElementById('progressPercent');
        this.progressFill     = document.getElementById('progressFill');
        this.wordCount        = document.getElementById('wordCount');
        this.qualityIndicator = document.getElementById('qualityIndicator');
        this.reaskMessage     = document.getElementById('reaskMessage');
        this.saveStatus       = document.getElementById('saveStatus');

        // Live preview split (#2)
        this.previewSection   = document.getElementById('previewSection');
        this.previewRaw       = document.getElementById('previewRaw');
        this.previewPolished  = document.getElementById('previewPolished');

        // Completion / export feedback (#4)
        this.exportFeedback     = document.getElementById('exportFeedback');
        this.exportFeedbackText = document.getElementById('exportFeedbackText');
        this.exportRetryBtn     = document.getElementById('exportRetryBtn');

        // Before/after review panel (#7)
        this.reviewContent = document.getElementById('reviewContent');
    }

    // -------------------------------------------------------------------------
    // Screen routing
    // -------------------------------------------------------------------------

    showScreen(screenName) {
        [this.welcomeScreen, this.interviewScreen, this.completionScreen].forEach(
            s => s?.classList.remove('screen-active')
        );
        if (this.reviewPanel) this.reviewPanel.style.display = 'none';

        switch (screenName) {
            case 'welcome':    this.welcomeScreen?.classList.add('screen-active');    break;
            case 'interview':  this.interviewScreen?.classList.add('screen-active');  break;
            case 'completion': this.completionScreen?.classList.add('screen-active'); break;
            case 'review':     if (this.reviewPanel) this.reviewPanel.style.display = 'block'; break;
        }
        state.currentScreen = screenName;

    }

    // -------------------------------------------------------------------------
    // Resume banner (#6)
    // -------------------------------------------------------------------------

    showResumeBanner(sessionId, userId, progress, offline) {
        if (!this.resumeBanner) return;
        const infoEl = document.getElementById('resumeSessionInfo');
        if (infoEl) {
            let msg = t('resumeWelcome', userId);
            if (progress?.current && progress?.total) {
                msg += ` — ${progress.current} / ${progress.total}`;
            }
            infoEl.textContent = msg;
        }
        const offlineWarn = document.getElementById('resumeOfflineWarning');
        if (offlineWarn) offlineWarn.style.display = offline ? 'block' : 'none';
        this.resumeBanner.style.display = 'block';
    }

    hideResumeBanner() {
        if (this.resumeBanner) this.resumeBanner.style.display = 'none';
    }

    showCompletedBanner(sessionId) {
        const banner = document.getElementById('completedBanner');
        if (!banner) return;
        banner.style.display = 'block';
        // Wire the re-download button to RE-HYDRATE the completion screen.
        // Just toggling the screen would show empty quality/stats fields because
        // that state was lost on reload — so we re-fetch status + CV metadata.
        const btn = document.getElementById('completedRedownloadBtn');
        if (btn) {
            btn.onclick = async () => {
                state.sessionId = parseInt(sessionId, 10);
                banner.style.display = 'none';
                try {
                    const statusResp = await api.getStatus(state.sessionId);
                    const stats = statusResp?.data ?? {};
                    ui.showCompletion(stats);
                    // CV metadata carries the real overall_quality for the badge
                    let quality = stats.overall_quality ?? null;
                    try {
                        const cvResp = await api.get(`/api/cv/${state.sessionId}`);
                        quality = cvResp?.data?.overall_quality ?? quality;
                    } catch { /* metadata is best-effort */ }
                    ui.renderQualityCard(quality);
                } catch (e) {
                    console.warn('Re-download hydration failed:', e);
                }
                ui.showScreen('completion');
            };
        }
    }

    // -------------------------------------------------------------------------
    // Start button guard
    // -------------------------------------------------------------------------

    updateStartButton() {
        const userId     = document.getElementById('userIdInput')?.value.trim();
        const hasPath    = !!state.interviewPath;
        const hasName    = !!userId;
        const hasConsent = document.getElementById('consentCheck')?.checked ?? false;
        const ready      = hasPath && hasName && hasConsent;

        // Button is always clickable — handleStart() shows specific feedback
        if (this.startBtn) {
            this.startBtn.disabled = false;
            this.startBtn.style.opacity = ready ? '1' : '0.55';
        }

        const hint = document.getElementById('startHint');
        if (hint) {
            if (ready) {
                hint.textContent = t('startHintReady');
                hint.style.color = '#27ae60';
            } else if (!hasPath && !hasName) {
                hint.textContent = t('startHintBoth');
                hint.style.color = '#888';
            } else if (!hasPath) {
                hint.textContent = t('startHintPath');
                hint.style.color = '#f39c12';
            } else if (!hasName) {
                hint.textContent = t('startHintName');
                hint.style.color = '#f39c12';
            } else if (!hasConsent) {
                hint.textContent = t('startHintConsent');
                hint.style.color = '#e74c3c';
                // Visually shake the consent block so user can't miss it
                const cb = document.getElementById('consentBlock');
                if (cb) {
                    cb.style.outline = '2px solid #e74c3c';
                    cb.style.borderRadius = '4px';
                    setTimeout(() => { cb.style.outline = ''; }, 3000);
                }
            }
        }
    }

    // -------------------------------------------------------------------------
    // Interview input helpers
    // -------------------------------------------------------------------------

    updateSubmitButton() {
        const q = state.currentQuestion;
        const isPhotoQuestion = (q?.flags ?? []).includes('photo');
        const len = this.answerInput?.value.trim().length ?? 0;
        const minChars = effectiveMinChars(q);

        // Dump mode: enable the send button for any real text, no nagging.
        if (state.dumpMode) {
            if (this.submitBtn) this.submitBtn.disabled = len < 2;
            const sh = document.getElementById('submitHint');
            if (sh) sh.textContent = '';
            return;
        }

        if (isPhotoQuestion) {
            // Photo is optional — always allow submission (base64 or empty)
            if (this.submitBtn) this.submitBtn.disabled = false;
        } else {
            if (this.submitBtn) this.submitBtn.disabled = len < minChars;
        }

        // Hint below the button only when genuinely empty on a required field —
        // never nag short-answer questions (name, city, company, date).
        const submitHint = document.getElementById('submitHint');
        if (submitHint) {
            const showHint = !isPhotoQuestion && len < minChars && minChars > 0;
            submitHint.textContent = showHint ? t('typeMoreHint') : '';
        }
    }

    updateWordCount() {
        const text  = this.answerInput?.value.trim() ?? '';
        const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
        if (this.wordCount) this.wordCount.textContent = `${words} ${words === 1 ? t('wordSingular') : t('wordPlural')}`;
    }

    updateQualityIndicator() {
        const text  = this.answerInput?.value.trim() ?? '';
        const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
        if (!this.qualityIndicator) return;

        if (!text) {
            this.qualityIndicator.style.display = 'none';
            return;
        }

        // Short-answer questions (name, city, company, job title, date) are
        // valid when short — show a calm "✓ OK" instead of a length warning.
        if (isShortAnswerQuestion(state.currentQuestion)) {
            this.qualityIndicator.style.display = 'flex';
            this.qualityIndicator.className = 'quality-indicator strong';
            this.qualityIndicator.innerHTML = `<span>✓</span><span>${t('qualityGood')}</span>`;
            return;
        }

        // Rotate the label per question so the participant doesn't see the
        // exact same encouragement 5 times in a row. Seed by current question
        // index so the same question always shows the same phrasing.
        const seed = (state.currentQuestionIndex ?? 0);
        const pickVariant = (baseKey) => {
            const variants = [baseKey, baseKey + 'A', baseKey + 'B'];
            // Pick a variant that exists in the active translation, fall back to base
            for (const v of [variants[seed % 3], variants[0]]) {
                const val = t(v);
                if (val && val !== v) return val;  // t() returns key when missing
            }
            return t(baseKey);
        };

        let quality, icon, label;
        if (words < 5) {
            quality = 'weak';     icon = '⚠'; label = pickVariant('qualityShort');
        } else if (words < 15) {
            quality = 'adequate'; icon = '◎'; label = pickVariant('qualityOk');
        } else {
            quality = 'strong';   icon = '✓'; label = pickVariant('qualityGood');
        }

        this.qualityIndicator.style.display = 'flex';
        this.qualityIndicator.className = `quality-indicator ${quality}`;
        this.qualityIndicator.innerHTML = `<span>${icon}</span><span>${label}</span>`;
    }

    displayQuestion(question) {
        // Cancel any pending preview debounce from the previous question
        clearTimeout(state.previewDebounceTimer);
        state.previewDebounceTimer = null;
        if (this.qualityIndicator) this.qualityIndicator.style.display = 'none';

        // Mid-interview encouragement banner — shown once, near the halfway point
        try {
            const banner = document.getElementById('midwayBanner');
            const idx    = (state.currentQuestionIndex ?? 0);
            const total  = (state.totalQuestions ?? 0);
            if (banner && total > 4) {
                const half = Math.floor(total / 2);
                const shouldShow = (idx === half) && !sessionStorage.getItem('ams_midway_shown');
                if (shouldShow) {
                    const txt = document.getElementById('midwayText');
                    if (txt) txt.textContent = t('midwayEncouragement') || 'Sie haben den schwierigsten Teil bereits geschafft.';
                    banner.style.display = 'flex';
                    sessionStorage.setItem('ams_midway_shown', '1');
                    setTimeout(() => { banner.style.display = 'none'; }, 6000);
                } else if (idx !== half) {
                    banner.style.display = 'none';
                }
            }
        } catch (_e) { /* non-critical UI sugar */ }

        if (this.questionText) this.questionText.textContent  = question.text  ?? '';

        // Living CV: show the question as a warm advisor prompt at the active line.
        cvDocSetPrompt(question);


        // Show original German text as subtitle for non-German users
        const subtitleEl = document.getElementById('questionGermanSubtitle');
        if (subtitleEl) {
            const lang = (typeof state !== 'undefined' ? state.language : null) ?? 'de';
            const germanText = question.german_text ?? '';
            if (lang !== 'de' && germanText && germanText !== question.text) {
                subtitleEl.textContent = '🇩🇪 ' + germanText;
                subtitleEl.style.display = 'block';
            } else {
                subtitleEl.style.display = 'none';
            }
        }

        if (this.questionHint) this.questionHint.textContent  = question.hint  ?? '';
        if (this.goodExample)  this.goodExample.textContent   = question.examples?.good ?? '';
        if (this.badExample)   this.badExample.textContent    = question.examples?.bad  ?? '';

        if (this.answerInput)  this.answerInput.value = '';
        if (this.reaskMessage) this.reaskMessage.style.display = 'none';
        // Clear the detected-language badge so it doesn't carry a stale language
        // ("Detected: TR") onto the next, possibly-German, question.
        const _langBadge = document.getElementById('detectedLangBadge');
        if (_langBadge) _langBadge.style.display = 'none';

        // Helper tip
        const helperTipEl = document.getElementById('helperTip');
        if (helperTipEl) {
            const tip = question.helper_tip ?? '';
            helperTipEl.textContent = tip;
            helperTipEl.style.display = tip ? 'block' : 'none';
        }

        // Quick-fill chips
        this._renderQuickFill(question.quick_fill ?? []);

        // Vorschau zurücksetzen
        if (this.previewSection)  this.previewSection.style.display = 'none';
        if (this.previewRaw)      this.previewRaw.textContent = '';
        if (this.previewPolished) this.previewPolished.innerHTML = `<span class="preview-loading" id="previewLoadingSpan">${t('previewLoading')}</span>`;

        // Flag-based helpers
        const flags = question.flags ?? [];
        const isPhoto     = flags.includes('photo');
        const isDateRange = flags.includes('date_range');

        // Photo upload container
        const photoContainer = document.getElementById('photoUploadContainer');
        const answerSection  = this.answerInput?.closest('.answer-section');
        if (photoContainer) photoContainer.style.display = isPhoto ? 'flex' : 'none';
        if (answerSection)  answerSection.style.display  = isPhoto ? 'none' : '';

        // Date helper
        const dateHelper = document.getElementById('dateHelperContainer');
        if (dateHelper) dateHelper.style.display = isDateRange ? 'block' : 'none';
        if (isDateRange) {
            const fromInput = document.getElementById('dateFromInput');
            const toInput   = document.getElementById('dateToInput');
            if (fromInput) fromInput.value = '';
            if (toInput)   toInput.value   = '';
        }

        this.updateWordCount();
        this.updateQualityIndicator();
        this.updateSubmitButton();
        if (!isPhoto) this.answerInput?.focus();
    }

    _renderQuickFill(chips) {
        const container = document.getElementById('quickFillContainer');
        if (!container) return;
        if (!chips || chips.length === 0) {
            container.style.display = 'none';
            return;
        }

        // A chip is a "starter" if it ends with a space (trailing space convention
        // used in paths.py) or with typical German opening phrases.
        const isStarter = (chip) =>
            chip.endsWith(' ') ||
            chip.endsWith(': ') ||
            /\b(als|bei|mit|in|für|und|zum|zur)\s*$/.test(chip);

        container.style.display = 'block';
        container.innerHTML = `
            <p class="quick-fill-label">${t('quickFillLabel')}</p>
            <div class="quick-fill-chips">
              ${chips.map(c => {
                  const starter = isStarter(c);
                  // Show a ✏ indicator on starter chips so the user knows to continue typing
                  const label = starter ? this._escape(c.trimEnd()) + ' <span class="chip-continue-hint">✏</span>' : this._escape(c);
                  return `<button type="button" class="quick-fill-chip${starter ? ' chip-starter' : ''}" data-value="${this._escape(c)}">${label}</button>`;
              }).join('')}
            </div>`;

        container.querySelectorAll('.quick-fill-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!this.answerInput) return;
                // Use data-value (preserves trailing spaces) not textContent (strips them)
                const chip = btn.dataset.value ?? btn.textContent;
                // Set as starter — clear field and pre-fill so Maria can edit
                this.answerInput.value = chip;
                this.answerInput.focus();
                // Place cursor at end so user types right after the starter text
                const len = this.answerInput.value.length;
                this.answerInput.setSelectionRange(len, len);
                // Scroll textarea into view (mobile)
                this.answerInput.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                this.updateWordCount();
                this.updateQualityIndicator();
                this.updateSubmitButton();
                // Trigger live preview
                const event = new Event('input', { bubbles: true });
                this.answerInput.dispatchEvent(event);
            });
        });
    }

    updateProgress(current, total) {
        const pct = Math.round((current / total) * 100);
        if (this.progressLabel)   this.progressLabel.textContent   = t('progressLabel', current, total);
        if (this.progressPercent) this.progressPercent.textContent = `${pct}%`;
        if (this.progressFill)    this.progressFill.style.width    = `${pct}%`;
    }

    // Dump mode has no numbered questions — completeness is tracked by the set of
    // REQUIRED CV fields that have been filled (cumulative across the whole
    // conversation), not "Frage 0 von 1". `cap` is the cumulative captured object.
    updateDumpProgress(cap) {
        cap = cap || {};
        const fields = [
            ['name',       !!cap.name,                      t('fieldName')    || 'Name'],
            ['address',    !!cap.city,                      t('fieldAddress') || 'Adresse'],
            ['phone',      !!cap.phone,                     t('fieldPhone')   || 'Telefon'],
            ['email',      !!cap.email,                     t('fieldEmail')   || 'E-Mail'],
            ['experience', (cap.experiences || []).length > 0, t('fieldExperience') || 'Berufserfahrung'],
            ['education',  (cap.education || []).length > 0, t('fieldEducation') || 'Ausbildung'],
            ['skills',     (cap.skills || []).length > 0,    t('fieldSkills')  || 'Kenntnisse'],
            ['target',     !!cap.target_job,                t('fieldTarget')  || 'Zielberuf'],
        ];
        const filled  = fields.filter(f => f[1]).length;
        const total   = fields.length;
        const missing = fields.filter(f => !f[1]).map(f => f[2]);
        const pct     = Math.round((filled / total) * 100);

        const base = t('cvProgressLabel') || 'Ihr Lebenslauf';
        if (this.progressLabel)   this.progressLabel.textContent   = `${base}: ${filled}/${total}`;
        if (this.progressPercent) this.progressPercent.textContent = `${pct}%`;
        if (this.progressFill)    this.progressFill.style.width    = `${pct}%`;

        // Show what's still missing as small chips under the progress bar.
        let box = document.getElementById('cvMissingFields');
        if (!box && this.progressLabel) {
            box = document.createElement('div');
            box.id = 'cvMissingFields';
            box.className = 'cv-missing-fields';
            (this.progressLabel.closest('.progress-section') || this.progressLabel.parentElement)?.appendChild(box);
        }
        if (box) {
            if (missing.length) {
                const lead = t('stillMissing') || 'Noch offen';
                box.innerHTML = `<span class="cv-missing-lead">${lead}:</span> ` +
                    missing.map(m => `<span class="cv-missing-chip">${m}</span>`).join(' ');
                box.style.display = '';
            } else {
                box.innerHTML = `<span class="cv-missing-done">✓ ${t('allFieldsDone') || 'Alle Felder ausgefüllt'}</span>`;
            }
        }
    }

    showReaskMessage(message, suggestion) {
        if (!this.reaskMessage) return;
        this.reaskMessage.style.display = 'block';
        const textEl = document.getElementById('reaskText');
        const suggEl = document.getElementById('reaskSuggestion');
        if (textEl) textEl.textContent = message;
        if (suggEl) suggEl.textContent = `${t('reaskTip')}: ${suggestion}`;
    }

    showEncouragement(message) {
        if (!message) return;
        // Remove any existing toast first
        document.getElementById('encouragementToast')?.remove();
        const toast = document.createElement('div');
        toast.id = 'encouragementToast';
        toast.className = 'encouragement-toast';
        toast.setAttribute('role', 'status');
        toast.setAttribute('aria-live', 'polite');
        toast.textContent = message;
        document.body.appendChild(toast);
        // Fade out after 2.2 s, remove after transition
        setTimeout(() => toast.classList.add('hiding'), 2200);
        setTimeout(() => toast.remove(), 2650);
    }

    updateSaveStatus(status) {
        if (!this.saveStatus) return;
        this.saveStatus.textContent = status;
        document.getElementById('autosaveIndicator')?.classList.toggle('saving', status === 'Wird gespeichert…');
    }

    // -------------------------------------------------------------------------
    // Live preview (#2)
    // -------------------------------------------------------------------------

    showLivePreview(rawText) {
        if (!this.previewSection) return;
        if (!rawText?.trim()) {
            this.previewSection.style.display = 'none';
            return;
        }
        this.previewSection.style.display = 'block';
        if (this.previewRaw) this.previewRaw.textContent = rawText;
        if (this.previewPolished) this.previewPolished.innerHTML = `<span class="preview-loading" id="previewLoadingSpan">${t('previewLoading')}</span>`;
    }

    // §2 / §4 — render polished text + rule engine changes list
    setPreviewPolished(polishedText, changes = [], suggestions = []) {
        if (!this.previewPolished) return;
        if (!polishedText?.trim()) {
            this.previewPolished.innerHTML = `<span class="preview-loading">${t('previewLoading')}</span>`;
            return;
        }
        let html = `<div class="preview-text">${this._escape(polishedText)}</div>`;
        if (changes.length) {
            html += `<ul class="preview-changes">${changes.map(c => `<li>${this._escape(c)}</li>`).join('')}</ul>`;
        }
        if (suggestions.length) {
            html += `<ul class="preview-suggestions">${suggestions.map(s => `<li>${this._escape(s)}</li>`).join('')}</ul>`;
        }
        this.previewPolished.innerHTML = html;
    }

    // -------------------------------------------------------------------------
    // Completion screen (#3 quality card)
    // -------------------------------------------------------------------------

    showCompletion(stats) {
        const el = document.getElementById('completionSummary');
        if (el) el.textContent = t('completionStats', stats.answers_completed ?? 0, stats.answers_skipped ?? 0);
    }

    showProfileSummary(text, loading = false) {
        const card = document.getElementById('profileSummaryCard');
        const body = document.getElementById('profileSummaryText');
        if (!card || !body) return;
        if (loading) {
            card.style.display = 'block';
            body.textContent = t('profileSummaryLoading');
            return;
        }
        if (text) {
            body.textContent = text;
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    }

    renderQualityCard(overallQuality) {
        const card  = document.getElementById('qualityCard');
        const badge = document.getElementById('qualityBadge');
        const label = document.getElementById('qualityLabel');
        const tips  = document.getElementById('improvementTips');
        if (!card) return;

        const pct = overallQuality != null ? Math.round(overallQuality * 100) : 0;

        let emoji, text, tipList;
        if (pct >= 75) {
            emoji   = '&#11088;';
            text    = t('qualityHighText');
            tipList = [t('qualityHighTip')];
        } else if (pct >= 50) {
            emoji   = '&#10003;';
            text    = t('qualityMedText');
            tipList = [t('qualityMedTip1'), t('qualityMedTip2')];
        } else if (pct >= 25) {
            emoji   = '&#9888;';
            text    = t('qualityLowText');
            tipList = [t('qualityLowTip1'), t('qualityLowTip2'), t('qualityLowTip3')];
        } else {
            emoji   = '&#128221;';
            text    = t('qualityBaseText');
            tipList = [t('qualityBaseTip1'), t('qualityBaseTip2')];
        }

        if (badge) badge.innerHTML = emoji;
        if (label) label.textContent = `${text} (${pct}%)`;
        if (tips) tips.innerHTML = tipList.map(t => `<li>${t}</li>`).join('');
        card.style.display = 'block';
    }

    // -------------------------------------------------------------------------
    // Export feedback (#4) — no alert()
    // -------------------------------------------------------------------------

    setExportFeedback(type, message, retryFn = null) {
        if (!this.exportFeedback) return;
        this.exportFeedback.style.display = 'block';
        this.exportFeedback.className = `export-feedback ${type}`;
        if (this.exportFeedbackText) this.exportFeedbackText.textContent = message;
        if (this.exportRetryBtn) {
            if (retryFn) {
                this.exportRetryBtn.style.display = 'inline';
                this.exportRetryBtn.onclick = retryFn;
            } else {
                this.exportRetryBtn.style.display = 'none';
            }
        }
        if (type === 'success') {
            setTimeout(() => { if (this.exportFeedback) this.exportFeedback.style.display = 'none'; }, 4000);
        }
    }

    // -------------------------------------------------------------------------
    // Before/after review panel (#7)
    // -------------------------------------------------------------------------

    renderReviewPanel() {
        if (!this.reviewContent) return;
        const entries = Object.entries(state.answers);
        if (entries.length === 0) {
            this.reviewContent.innerHTML = `<p>${t('reviewEmpty')}</p>`;
            return;
        }
        this.reviewContent.innerHTML = entries.map(([qId, raw]) => {
            const polished = state.polishedAnswers[qId] ?? raw;
            const changed  = polished !== raw;
            return `
                <div class="review-item">
                    <div class="review-item-header">
                        <span class="review-question-id">${this._escape(qId)}</span>
                    </div>
                    <div class="review-item-body">
                        <div class="review-col">
                            <h4 class="review-col-label">${t('reviewColRaw')}</h4>
                            <div class="review-col-text">${this._escape(raw)}</div>
                        </div>
                        <div class="preview-arrow" aria-hidden="true">→</div>
                        <div class="review-col">
                            <h4 class="review-col-label">${t('reviewColPolished')}</h4>
                            <div class="review-col-text${changed ? ' review-improved' : ''}">${this._escape(polished)}</div>
                        </div>
                    </div>
                </div>`;
        }).join('');
    }

    // -------------------------------------------------------------------------
    // Live CV panel — persistent CV built up as answers come in
    // -------------------------------------------------------------------------

    updateCVPanel(entries) {
        const panel = document.getElementById('liveCVPanel');
        if (!panel) return;
        if (!entries || entries.length === 0) {
            panel.innerHTML = `<p class="cv-panel-empty">${t('cvPanelEmpty')}</p>`;
            return;
        }
        // Group: identity at top, rest as sections
        const identityIds  = new Set(['id_name', 'id_location', 'id_phone', 'id_email', 'id_target_job']);
        const identityItems = entries.filter(e => identityIds.has(e.questionId));
        const sectionItems  = entries.filter(e => !identityIds.has(e.questionId));

        let html = '';

        // Header block
        if (identityItems.length) {
            const name     = identityItems.find(e => e.questionId === 'id_name')?.raw ?? '';
            const location = identityItems.find(e => e.questionId === 'id_location')?.raw ?? '';
            const phone    = identityItems.find(e => e.questionId === 'id_phone')?.raw ?? '';
            const email    = identityItems.find(e => e.questionId === 'id_email')?.raw ?? '';
            const target   = identityItems.find(e => e.questionId === 'id_target_job')?.polished ?? '';
            const contactParts = [phone, email].filter(Boolean).map(v => this._escape(v));
            html += `<div class="cv-panel-header">
                ${name ? `<div class="cv-panel-name">${this._escape(name)}</div>` : ''}
                ${location ? `<div class="cv-panel-meta">${this._escape(location)}</div>` : ''}
                ${contactParts.length ? `<div class="cv-panel-meta">${contactParts.join(' · ')}</div>` : ''}
                ${target ? `<div class="cv-panel-target">${this._escape(target)}</div>` : ''}
            </div>`;
        }

        // Section entries — each shows polished text + detected skill chips
        if (sectionItems.length) {
            html += sectionItems.map(e => {
                const skillsHtml = (e.skills && e.skills.length > 0)
                    ? `<div class="cv-panel-skills">${e.skills.map(s =>
                        `<span class="skill-chip">${this._escape(s)}</span>`).join('')}</div>`
                    : '';
                return `
                <div class="cv-panel-entry">
                    <div class="cv-panel-entry-label">${this._escape(e.label)}</div>
                    <div class="cv-panel-entry-text">${this._escape(e.polished)}</div>
                    ${skillsHtml}
                </div>`;
            }).join('');
        }

        panel.innerHTML = html;
        // Scroll panel to bottom so latest entry is visible
        panel.scrollTop = panel.scrollHeight;
    }

    // -------------------------------------------------------------------------
    // Follow-up mini-chat prompt
    // -------------------------------------------------------------------------

    showFollowUpPrompt(followUpText, language = 'de') {
        return new Promise(resolve => {
            const container = document.getElementById('followUpContainer');
            if (!container) { resolve(null); return; }

            const _skip = { de: 'Überspringen →', en: 'Skip →', tr: 'Atla →', pl: 'Pomiń →',
                            ro: 'Sari →', uk: 'Пропустити →', ru: 'Пропустить →',
                            ar: 'تخطي →', bs: 'Preskoči →', hr: 'Preskoči →', sr: 'Preskoči →', sk: 'Preskočiť →' };
            const _submit = { de: 'Hinzufügen →', en: 'Add →', tr: 'Ekle →', pl: 'Dodaj →',
                              ro: 'Adaugă →', uk: 'Додати →', ru: 'Добавить →',
                              ar: 'أضف →', bs: 'Dodaj →', hr: 'Dodaj →', sr: 'Dodaj →', sk: 'Pridať →' };
            const skipLabel   = _skip[language]   ?? _skip.de;
            const submitLabel = _submit[language] ?? _submit.de;

            container.innerHTML = `
                <div class="followup-bubble">
                    <div class="followup-question">${this._escape(followUpText)}</div>
                    <textarea id="followUpInput" class="followup-input" rows="2"
                        placeholder="…"></textarea>
                    <div class="followup-actions">
                        <button class="btn btn-ghost btn-sm" id="followUpSkipBtn">${skipLabel}</button>
                        <button class="btn btn-primary btn-sm" id="followUpSubmitBtn">${submitLabel}</button>
                    </div>
                </div>`;
            container.style.display = 'block';

            const cleanup = (value) => {
                container.style.display = 'none';
                container.innerHTML = '';
                resolve(value);
            };

            document.getElementById('followUpSkipBtn')?.addEventListener('click', () => cleanup(null));
            document.getElementById('followUpSubmitBtn')?.addEventListener('click', () => {
                const val = document.getElementById('followUpInput')?.value.trim() ?? '';
                cleanup(val || null);
            });

            // Auto-focus
            setTimeout(() => document.getElementById('followUpInput')?.focus(), 50);
        });
    }

    updateAIStatus(status) {
        const badge = document.getElementById('aiBadge');
        if (!badge) return;
        const on = status?.ollama_available;
        badge.className  = `ai-badge ${on ? 'ai-on' : 'ai-off'}`;
        badge.title      = status?.description ?? '';
        badge.textContent = on
            ? `KI aktiv (${status.model ?? 'Ollama'})`
            : 'Regelbasiert';
        badge.style.display = 'inline-block';
    }

    _escape(text) {
        const d = document.createElement('div');
        d.textContent = String(text);
        return d.innerHTML;
    }
}

const ui = new UIManager();

// ============================================================================
// Interview Flow Manager
// ============================================================================

class InterviewManager {

    // -------------------------------------------------------------------------
    // #6 Resume flow
    // -------------------------------------------------------------------------

    checkForResumeSession() {
        // C5: Check for a previously completed session first
        const completedId = localStorage.getItem(COMPLETED_SESSION_KEY);
        if (completedId) {
            ui.showCompletedBanner(completedId);
        }

        const savedId   = localStorage.getItem(SESSION_STORAGE_KEY);
        const savedUser = localStorage.getItem(USER_STORAGE_KEY);
        if (!savedId) return;

        api.getStatus(parseInt(savedId, 10))
            .then(resp => {
                // completed = 1 means interview is done — don't show resume banner
                const done = resp?.data?.completed === 1 || resp?.data?.progress_percent >= 100;
                if (!done) {
                    const progress = resp?.data?.progress || null;
                    ui.showResumeBanner(savedId, savedUser, progress);
                } else {
                    // C5: completed session — show re-download banner
                    ui.showCompletedBanner(savedId);
                }
            })
            .catch(() => {
                // C2: Server may be temporarily offline — keep keys, show offline warning
                ui.showResumeBanner(savedId, savedUser, null, true);
            });
    }

    async handleResume() {
        const savedId   = localStorage.getItem(SESSION_STORAGE_KEY);
        const savedUser = localStorage.getItem(USER_STORAGE_KEY);
        const savedToken = localStorage.getItem(TOKEN_STORAGE_KEY) || '';
        if (!savedId) return;
        const sid = parseInt(savedId, 10);
        state.sessionToken = savedToken;

        ui.hideResumeBanner();
        try {
            ui.updateSaveStatus(t('statusResuming'));
            // Make sure the session is recoverable / consistent.
            const resp = await api.resumeInterview(sid);
            if (resp?.status !== 'success') throw new Error('resume failed');

            // Resume into the SAME free-form dump experience the participant
            // started in — not the legacy per-question UI.
            state.sessionId      = sid;
            state.userId         = savedUser ?? '';
            state.dumpMode       = true;
            state.currentGap     = null;
            state.lastJob        = '';
            state.askedGaps      = new Set();
            state.lastGapKey     = null;
            state.totalQuestions = 1;

            // Pull back everything captured so far and repaint the CV sheet.
            let cap = {}, missing = [];
            try {
                const snap = await api.dumpSnapshot(sid);
                cap     = snap?.data?.captured ?? {};
                missing = snap?.data?.missing ?? [];
                state.dumpHasContent = !!snap?.data?.has_content;
                if (cap.target_job) state.lastJob = cap.target_job;
            } catch (_e) {
                state.dumpHasContent = false;
            }

            // Rebuild the screen chrome for dump mode.
            this._enterDumpChrome();
            cvDocReset();
            const _cm = document.getElementById('convMessages');
            [...(_cm?.querySelectorAll('.conv-row:not(#cvActivePrompt)') || [])].forEach(n => n.remove());
            this._paintCaptured(cap);
            state.cvCaptured = cap || {};
            ui.updateDumpProgress(state.cvCaptured);

            // Welcome the participant back and pick up at the first open gap.
            const welcome = t('resumeWelcome') || 'Willkommen zurück! Ihr Lebenslauf ist gespeichert. Machen wir weiter.';
            const coreGap = (missing || []).find(g => this._gapQuestion(g, cap));
            let q = null;
            if (coreGap) { q = this._gapQuestion(coreGap, cap); state.askedGaps.add(coreGap); state.lastGapKey = coreGap; }
            else {
                const enr = this._nextEnrichment();
                if (enr) { q = { text: enr.text, hint: enr.hint, expect: enr.expect }; state.askedGaps.add(enr.key); state.lastGapKey = enr.key; }
            }
            if (q) {
                state.currentGap = q.expect;
                convAddAI(welcome + ' ' + q.text, q.hint);
            } else {
                state.currentGap = null;
                convAddAI(welcome + ' ' + (t('dumpAnythingElse') || 'Möchten Sie noch etwas ergänzen? Sonst klicken Sie auf „Lebenslauf erstellen".'));
            }

            ui.updateSaveStatus(t('statusReady'));
        } catch (err) {
            console.warn('Resume failed, restarting:', err);
            localStorage.removeItem(SESSION_STORAGE_KEY);
            localStorage.removeItem(USER_STORAGE_KEY);
            ui.updateSaveStatus(t('statusReady'));
        }
    }

    /** Set up the interview screen chrome for free-form dump mode (shared by start + resume). */
    _enterDumpChrome() {
        ui.showScreen('interview');
        ui.updateDumpProgress({});
        document.getElementById('dumpFinishBtn')?.style.setProperty('display', 'inline-flex');
        this.updateModeSwitchBtn();
        if (ui.answerInput) ui.answerInput.placeholder = t('dumpPlaceholder') || t('answerPlaceholder');
        document.getElementById('skipBtn')?.style.setProperty('display', 'none');
        const sb = document.getElementById('submitBtn');
        if (sb) sb.textContent = t('dumpSend') || 'Senden →';
        ui.updateSubmitButton();
    }

    handleDismissResume() {
        const btn = document.getElementById('dismissResumeBtn');
        if (btn && btn.dataset.confirming !== 'true') {
            // First click — ask for confirmation
            btn.dataset.confirming = 'true';
            const original = btn.textContent;
            btn.textContent = '⚠️ ' + (t('confirmDiscard') || 'Wirklich neu beginnen?');
            btn.classList.add('btn-danger');
            // Auto-reset after 4 seconds if not confirmed
            setTimeout(() => {
                if (btn.dataset.confirming === 'true') {
                    btn.dataset.confirming = 'false';
                    btn.textContent = original;
                    btn.classList.remove('btn-danger');
                }
            }, 4000);
            return;
        }
        // Second click — confirmed
        localStorage.removeItem(SESSION_STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);
        ui.hideResumeBanner();
    }

    // -------------------------------------------------------------------------
    // Start
    // -------------------------------------------------------------------------

    async handleStart() {
        const userId     = document.getElementById('userIdInput')?.value.trim();
        const hasConsent = document.getElementById('consentCheck')?.checked ?? false;

        // Show specific feedback instead of silently doing nothing
        if (!state.interviewPath || !userId || !hasConsent) {
            ui.updateStartButton();  // re-run hint logic to show the right message
            // Scroll to the first missing element
            if (!state.interviewPath) {
                document.querySelector('.path-options')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else if (!userId) {
                document.getElementById('userIdInput')?.focus();
            } else if (!hasConsent) {
                document.getElementById('consentCheck')?.focus();
                document.getElementById('consentBlock')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }

        try {
            ui.updateSaveStatus(t('statusStarting'));
            state.isWaitingForResponse = true;
            state.userId = userId;

            const response = await api.startInterview(userId, state.interviewPath, state.language, hasConsent);
            if (response.status !== 'success') throw new Error(response.detail || 'Start failed');

            const data = response.data;
            state.sessionId            = data.session_id;
            state.sessionToken         = data.access_token || '';
            state.currentQuestionIndex = 0;
            state.followUpsShown       = 0;   // reset gentle-probe counter per interview
            state.totalQuestions       = data.progress.total;
            state.currentQuestion      = data.question;
            state.dumpMode             = true;   // start in free-form "dump" mode
            state.currentGap           = null;   // first message is the big dump
            state.lastJob              = '';
            state.dumpHasContent       = false;
            state.cvCaptured           = {};
            state.askedGaps            = new Set();
            state.lastGapKey           = null;
            const _cm = document.getElementById('convMessages');
            // keep only the initial advisor prompt; clear any old appended turns
            [...(_cm?.querySelectorAll('.conv-row:not(#cvActivePrompt)') || [])].forEach(n => n.remove());
            cvDocReset();                      // fresh, empty CV sheet

            // Persist for resume
            localStorage.setItem(SESSION_STORAGE_KEY, String(state.sessionId));
            localStorage.setItem(USER_STORAGE_KEY, userId);
            if (state.sessionToken) localStorage.setItem(TOKEN_STORAGE_KEY, state.sessionToken);

            ui.showScreen('interview');
            // Free-form start: invite the participant to dump everything; the AI
            // structures it onto the CV, then we converse about any gaps. The
            // opening is flavoured by the chosen path (unemployed/student/…).
            cvDocSetPrompt({ text: dumpPromptForPath(), hint: t('dumpHint'), examples: {} });
            ui.updateDumpProgress({});
            document.getElementById('dumpFinishBtn')?.style.setProperty('display', 'inline-flex');
            this.updateModeSwitchBtn();
            if (ui.answerInput) ui.answerInput.placeholder = t('dumpPlaceholder') || t('answerPlaceholder');
            // Dump mode: no "skip", and the send button just sends.
            document.getElementById('skipBtn')?.style.setProperty('display', 'none');
            const sb = document.getElementById('submitBtn');
            if (sb) sb.textContent = t('dumpSend') || 'Senden →';
            ui.updateSubmitButton();
            ui.updateSaveStatus(t('statusReady'));
        } catch (err) {
            console.error('Start error:', err);
            ui.updateSaveStatus(t('statusError'));
        } finally {
            state.isWaitingForResponse = false;
        }
    }

    // -------------------------------------------------------------------------
    // #2 Live preview — debounced
    // -------------------------------------------------------------------------

    scheduleLivePreview(rawText) {
        clearTimeout(state.previewDebounceTimer);
        const wordCount = rawText.trim().split(/\s+/).filter(Boolean).length;
        if (!rawText.trim() || wordCount < 3) {
            // A4: Show placeholder instead of hiding, so users know the panel exists
            if (ui.previewSection) {
                ui.previewSection.style.display = 'block';
                if (ui.previewPolished) ui.previewPolished.innerHTML =
                    `<span class="preview-placeholder">${t('previewPlaceholderHint') || 'Schreiben Sie weiter — hier sehen Sie das Ergebnis'}</span>`;
                if (ui.previewRaw)     ui.previewRaw.textContent = rawText;
            }
            return;
        }

        ui.showLivePreview(rawText);

        state.previewDebounceTimer = setTimeout(async () => {
            try {
                const category = state.currentQuestion?.category ?? 'experience';
                const resp = await api.previewAnswer(rawText, category, state.inputLanguage);
                if (resp?.data?.polished_text) {
                    ui.setPreviewPolished(
                        resp.data.polished_text,
                        resp.data.changes    || [],
                        resp.data.suggestions || []
                    );
                    // §2 also update quality indicator with server label
                    if (resp.data.quality_label && ui.qualityIndicator) {
                        const score = resp.data.quality_score ?? 0;
                        const qClass = score >= 0.75 ? 'strong' : score >= 0.5 ? 'adequate' : 'weak';
                        ui.qualityIndicator.style.display = 'flex';
                        ui.qualityIndicator.className = `quality-indicator ${qClass}`;
                        ui.qualityIndicator.innerHTML = `<span>${score >= 0.75 ? '✓' : score >= 0.5 ? '◎' : '⚠'}</span><span>${resp.data.quality_label}</span>`;
                    }
                    // Show detected language badge if different from selected
                    const detected = resp.data.detected_language;
                    const badge = document.getElementById('detectedLangBadge');
                    if (badge && detected && detected !== state.inputLanguage) {
                        badge.textContent = t('detectedLang', detected.toUpperCase());
                        badge.style.display = 'block';
                    } else if (badge) {
                        badge.style.display = 'none';
                    }
                }
            } catch {
                // Fallback: show raw text as-is so preview never looks broken
                ui.setPreviewPolished(rawText);
                // Reset quality badge so stale rating is never shown
                if (ui.qualityIndicator) ui.qualityIndicator.style.display = 'none';
            }
        }, PREVIEW_DEBOUNCE_MS);
    }

    // -------------------------------------------------------------------------
    // Free-form dump: the participant writes everything; the AI structures it
    // onto the CV, then we converse about what's missing.
    // -------------------------------------------------------------------------
    // The gap questions the assistant asks, one at a time. `expect` tells the
    // backend how to categorise the reply. Phrased warmly, like a real advisor.
    _gapQuestion(gap, cap) {
        const job = (cap && (cap.target_job)) || state.lastJob || '';
        const map = t('dumpGaps') || {};
        const entry = map[gap];
        if (!entry) return undefined;
        if (gap === 'experience_detail') {
            // Job-aware variant: interpolate {job}, or use the no-job phrasing.
            const out = { ...entry };
            out.text = job
                ? (entry.text || '').replace('{job}', job)
                : (entry.textNoJob || entry.text || '').replace('{job}', '');
            return out;
        }
        return entry;
    }

    _paintCaptured(cap) {
        if (cap.name)       cvDocAddAnswer({ id: 'id_name' }, cap.name, cap.name);
        if (cap.target_job) { cvDocAddAnswer({ id: 'id_target_job' }, cap.target_job, cap.target_job); state.lastJob = cap.target_job; }
        const contact = [cap.city, cap.phone, cap.email].filter(Boolean).join(', ');
        if (contact)        cvDocAddAnswer({ id: 'id_contact' }, contact, contact);
        (cap.experiences || []).forEach(e => cvDocAddAnswer({ category: 'experience', flags: ['work_experience'] }, e, e));
        (cap.education   || []).forEach(e => cvDocAddAnswer({ category: 'training',    flags: ['education'] }, e, e));
        (cap.motivation  || []).forEach(e => cvDocAddAnswer({ category: 'motivation',  flags: ['motivation'] }, e, e));
        if ((cap.skills || []).length)
            cvDocAddAnswer({ category: 'skills', flags: ['soft_skills'] }, cap.skills.join(', '), cap.skills.join(', '));
    }

    // Accumulate captured fields across turns (each turn only returns what it
    // parsed). This cumulative object drives the field-based completeness meter.
    _mergeCaptured(cap) {
        const c = state.cvCaptured = state.cvCaptured || {};
        for (const k of ['name', 'city', 'phone', 'email', 'target_job']) {
            if (cap[k]) c[k] = cap[k];                       // latest non-empty wins
        }
        for (const k of ['experiences', 'education', 'skills']) {
            const cur = new Set(c[k] || []);
            (cap[k] || []).forEach(v => cur.add(v));
            c[k] = [...cur];                                 // union
        }
    }

    // Extra questions that make the CV comprehensive (drawn from the documented
    // CV sections) — asked after the core gaps, each once. Returns the next
    // un-asked enrichment question, or null when done.
    _nextEnrichment() {
        const list = t('dumpEnrichment') || [];
        state.askedGaps = state.askedGaps || new Set();
        return list.find(e => !state.askedGaps.has(e.key)) || null;
    }

    async handleDump() {
        if (state.isWaitingForResponse) return;     // guard against double-submit
        const text = ui.answerInput?.value.trim() ?? '';
        if (text.length < 2) return;
        if (state.testMode) state.testInputs.push({ type: 'dump', text });
        const expect = state.currentGap || null;   // which gap this reply answers
        try {
            state.isWaitingForResponse = true;
            if (ui.answerInput) ui.answerInput.value = '';
            ui.updateSubmitButton?.();
            convAddUser(text);                       // show the participant's message
            convThinking(true);                      // typing indicator
            ui.updateSaveStatus(t('statusBuilding') || 'Wird strukturiert…');

            const resp = await api.dumpExtract(state.sessionId, text, state.inputLanguage, expect);
            const cap = resp?.data?.captured ?? {};
            const missing = resp?.data?.missing ?? [];

            convThinking(false);
            this._paintCaptured(cap);
            this._mergeCaptured(cap);
            ui.updateDumpProgress(state.cvCaptured);
            state.dumpHasContent = true;

            // Acknowledge what just landed, then ask the next gap.
            const bits = [];
            if (cap.name) bits.push(t('dumpAckName'));
            if (cap.target_job) bits.push(t('dumpAckTarget'));
            if ([cap.city, cap.phone, cap.email].some(Boolean)) bits.push(t('dumpAckContact'));
            if ((cap.experiences || []).length) bits.push(t('dumpAckExperience'));
            if ((cap.education || []).length) bits.push(t('dumpAckEducation'));
            if ((cap.skills || []).length) bits.push(t('dumpAckSkills'));
            const ack = bits.length ? `${t('dumpAckPrefix')} ${bits.join(', ')}.` : t('dumpAckNoted');

            // Pick the next thing to ask: first the core gaps the backend
            // reports, then the enrichment questions (languages, tools, certs,
            // strengths, motivation) so the CV ends up comprehensive. Each is
            // asked once (askedGaps) to avoid loops.
            state.askedGaps = state.askedGaps || new Set();
            if (expect) state.askedGaps.add(expect);
            if (state.lastGapKey) state.askedGaps.add(state.lastGapKey);

            const coreGap = missing.find(g => this._gapQuestion(g, cap) && !state.askedGaps.has(g));
            let q = null;
            if (coreGap) { q = this._gapQuestion(coreGap, cap); state.askedGaps.add(coreGap); state.lastGapKey = coreGap; }
            else {
                const enr = this._nextEnrichment();
                if (enr) { q = { text: enr.text, hint: enr.hint, expect: enr.expect }; state.askedGaps.add(enr.key); state.lastGapKey = enr.key; }
            }
            if (q) {
                state.currentGap = q.expect;
                convAddAI(ack + ' ' + q.text, q.hint);
            } else {
                state.currentGap = null;
                state.lastGapKey = null;
                const done = t('dumpAnythingElse') || 'Super! Ihr Lebenslauf ist gut gefüllt. Möchten Sie noch etwas ergänzen? Wenn nicht, klicken Sie auf „Lebenslauf erstellen".';
                convAddAI(ack + ' ' + done);
            }
            ui.updateSaveStatus(t('statusReady'));
        } catch (err) {
            console.error('Dump error:', err);
            convThinking(false);
            // Restore the participant's text so a slow/failed AI call doesn't
            // make them retype everything.
            if (ui.answerInput && !ui.answerInput.value.trim()) {
                ui.answerInput.value = text;
                ui.updateSubmitButton?.();
            }
            convAddAI(t('dumpError') || 'Das hat nicht ganz geklappt — Ihr Text ist noch da, bitte einfach erneut senden.');
            ui.updateSaveStatus(t('statusReady'));
        } finally {
            state.isWaitingForResponse = false;
            ui.updateSubmitButton?.();
        }
    }

    // -------------------------------------------------------------------------
    // Submit
    // -------------------------------------------------------------------------

    async handleSubmit() {
        if (state.isWaitingForResponse) return;

        // Free-form dump mode: structure the text onto the CV, then keep talking.
        if (state.dumpMode) {
            return this.handleDump();
        }

        const isPhotoQuestion = (state.currentQuestion?.flags ?? []).includes('photo');
        let answerText;
        if (isPhotoQuestion) {
            // For photo questions, the "answer" is the base64 data URL.
            // If skipped, use a placeholder so the backend never receives an empty string.
            answerText = state.photoDataUrl || 'photo_skipped';
        } else {
            answerText = ui.answerInput?.value.trim() ?? '';
            if (answerText.length < effectiveMinChars(state.currentQuestion)) return;
        }
        if (state.testMode && !isPhotoQuestion) {
            state.testInputs.push({ type: 'qa', q: state.currentQuestion?.id, text: answerText });
        }

        try {
            ui.updateSaveStatus(t('statusSaving'));
            state.isWaitingForResponse = true;

            const questionId = state.currentQuestion.id;
            const response   = await api.submitAnswer(state.sessionId, questionId, answerText);
            if (response.status !== 'success') throw new Error('Submit failed');

            const data = response.data;
            state.answers[questionId] = answerText;

            // Capture polished version for review panel
            const polishedPreview = ui.previewPolished?.textContent?.trim();
            const hasPolished = polishedPreview && !ui.previewPolished?.querySelector?.('.preview-loading');
            state.polishedAnswers[questionId] = data.polished_text
                ?? (hasPolished ? polishedPreview : null)
                ?? answerText;

            if (data.status === 're_ask') {
                ui.showReaskMessage(data.message, data.suggestion);
                // Living CV: gentle re-ask shown warmly at the active line.
                cvDocSetPrompt({
                    text: data.message || (state.currentQuestion?.text ?? ''),
                    hint: data.suggestion || '',
                    examples: {},
                }, { reask: true });
                ui.updateSaveStatus(t('statusReady'));
                return;
            }

            // Update CV panel with this answer (include detected skills for inline chips)
            const polishedForPanel = data.polished_text || answerText;
            state.cvEntries.push({
                label: state.currentQuestion?.text ?? questionId,
                raw: answerText,
                polished: polishedForPanel,
                questionId,
                skills: data.extracted_skills || [],
            });
            ui.updateCVPanel(state.cvEntries);

            // Living CV: type the answer onto the growing sheet (the "oh, I
            // actually DID stuff" moment) — header for identity, a section line
            // for content.
            cvDocAddAnswer(state.currentQuestion, answerText, data.polished_text);
            // Keep the captured-fields model in sync in GUIDED mode too, so the
            // progress chips, application e-mail prefill and AMS job search work
            // identically regardless of which interview mode produced the answer.
            this._captureFromGuidedAnswer(state.currentQuestion, answerText);

            // Show brief encouraging toast (message comes from backend quality score)
            if (data.message) ui.showEncouragement(data.message);

            // Gentle follow-up (PHILOSOPHY.md: once, only for vague answers).
            // Gate tightly so it never nags: skip structural questions (name,
            // city, company, date…), only probe genuinely short/vague CONTENT
            // answers, and cap the number of probes per interview.
            const currentFlags = state.currentQuestion?.flags ?? [];
            const isStructural = currentFlags.some(f => SHORT_ANSWER_FLAGS.has(f));
            const answerWords = answerText.trim().split(/\s+/).filter(Boolean).length;
            const isVague = answerWords > 0 && answerWords < FOLLOWUP_MAX_WORDS;
            state.followUpsShown = state.followUpsShown ?? 0;
            const underCap = state.followUpsShown < FOLLOWUP_SESSION_CAP;

            if (ENABLE_FOLLOWUPS && !isStructural && isVague && underCap) {
                try {
                    const fuResp = await api.getFollowUp(
                        state.sessionId, questionId, answerText, state.inputLanguage
                    );
                    const followUpText = fuResp?.data?.follow_up;
                    if (followUpText) {
                        state.followUpsShown++;
                        const accepted = await ui.showFollowUpPrompt(followUpText, state.inputLanguage);
                        if (accepted && accepted.trim()) {
                            await api.submitAnswer(
                                state.sessionId,
                                questionId + '_followup',
                                accepted
                            ).catch(() => {}); // non-fatal
                        }
                    }
                } catch {
                    // Follow-up is non-fatal — always continue to next question
                }
            }

            state.currentQuestionIndex++;
            state.answersSubmitted++;

            const nextResponse = await api.getNextQuestion(state.sessionId);
            const nextData     = nextResponse.data;

            if (nextResponse.status === 'complete' || nextData?.status === 'complete') {
                await this.showCompletion();
            } else {
                state.currentQuestion = nextData.question;
                ui.displayQuestion(nextData.question);
                ui.updateProgress(nextData.progress.current, nextData.progress.total);
                ui.updateSaveStatus(t('statusSaved'));
            }
        } catch (err) {
            console.error('Submit error:', err);
            ui.updateSaveStatus(t('statusError'));
        } finally {
            state.isWaitingForResponse = false;
        }
    }

    // -------------------------------------------------------------------------
    // Skip
    // -------------------------------------------------------------------------

    async handleSkip() {
        if (state.isWaitingForResponse) return;

        try {
            ui.updateSaveStatus(t('statusSkipping'));
            state.isWaitingForResponse = true;

            const questionId = state.currentQuestion.id;
            const response   = await api.skipQuestion(state.sessionId, questionId);
            const nextData   = response.data;

            state.currentQuestionIndex++;

            if (response.status === 'complete' || nextData?.status === 'complete') {
                await this.showCompletion();
            } else {
                state.currentQuestion = nextData.question;
                ui.displayQuestion(nextData.question);
                ui.updateProgress(nextData.progress.current, nextData.progress.total);
                ui.updateSaveStatus(t('statusReady'));
            }
        } catch (err) {
            console.error('Skip error:', err);
            ui.updateSaveStatus(t('statusError'));
        } finally {
            state.isWaitingForResponse = false;
        }
    }

    // -------------------------------------------------------------------------
    // Completion (#3 quality card)
    // -------------------------------------------------------------------------

    async showCompletion() {
        try {
            state.dumpMode = false;   // leaving the conversation; build the CV
            ui.updateSaveStatus(t('statusBuilding'));

            let cvQuality = null;
            try {
                const completeResp = await api.completeInterview(state.sessionId);
                if (completeResp?.data?.overall_quality != null) {
                    cvQuality = completeResp.data.overall_quality;
                    state.overallQuality = cvQuality;
                }
            } catch (e) {
                console.warn('complete_interview non-fatal:', e);
            }

            const statusResp = await api.getStatus(state.sessionId);
            const stats      = statusResp.data;

            ui.showCompletion(stats);
            ui.renderQualityCard(cvQuality ?? stats.overall_quality);
            ui.showScreen('completion');
            ui.updateSaveStatus(t('statusDone'));
            // A9: Visually elevate the PDF download as the primary next action
            const pdfBtn = document.getElementById('exportBtn');
            if (pdfBtn) {
                pdfBtn.classList.add('btn-completion-primary');
                pdfBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

            // Load AI profile summary in the background (non-blocking)
            ui.showProfileSummary(null, true);  // show loading state
            api.post('/api/ai/profile-summary', { session_id: state.sessionId })
                .then(r => ui.showProfileSummary(r?.data?.summary ?? null, false))
                .catch(() => ui.showProfileSummary(null, false));

            // C5: Store completed session ID so returning users can re-download
            localStorage.setItem(COMPLETED_SESSION_KEY, String(state.sessionId));
            localStorage.removeItem(SESSION_STORAGE_KEY);
            localStorage.removeItem(USER_STORAGE_KEY);
        } catch (err) {
            console.error('Completion error:', err);
            ui.updateSaveStatus(t('statusError'));
        }
    }

    // -------------------------------------------------------------------------
    // #4 Export — inline feedback, no alert()
    // -------------------------------------------------------------------------

    async handleExport(format) {
        if (!state.sessionId) {
            ui.setExportFeedback('error', t('noSessionError'));
            return;
        }

        const doExport = async () => {
            ui.setExportFeedback('loading', t('exportPreparing', format.toUpperCase()));
            try {
                const response = await api.exportFile(format, state.sessionId, state.inputLanguage || 'de', state.photoDataUrl);
                const blob     = await response.blob();

                const disposition = response.headers.get('content-disposition') ?? '';
                const nameMatch   = disposition.match(/filename="?([^";\n]+)"?/);
                const ext         = format === 'json' ? 'json' : format === 'docx' ? 'docx' : 'pdf';
                const fileName    = nameMatch ? nameMatch[1] : `cv_${state.userId ?? 'download'}.${ext}`;

                const url = URL.createObjectURL(blob);
                const a   = document.createElement('a');
                a.href = url;
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(url);

                ui.setExportFeedback('success', t('exportSuccess', fileName));
            } catch (err) {
                ui.setExportFeedback('error', t('exportFailed', err.message), doExport);
            }
        };

        await doExport();
    }

    // -------------------------------------------------------------------------
    // #5 Start over — data loss guard
    // -------------------------------------------------------------------------

    handleStartOver() {
        const btn = document.getElementById('startOverBtn');
        if (btn && btn.dataset.confirming !== 'true') {
            btn.dataset.confirming = 'true';
            const original = btn.textContent;
            btn.textContent = '⚠️ ' + (t('confirmStartOver') || 'Wirklich löschen?');
            btn.classList.add('btn-danger');
            setTimeout(() => {
                if (btn.dataset.confirming === 'true') {
                    btn.dataset.confirming = 'false';
                    btn.textContent = original;
                    btn.classList.remove('btn-danger');
                }
            }, 4000);
            return;
        }
        localStorage.removeItem(SESSION_STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);
        localStorage.removeItem(COMPLETED_SESSION_KEY);
        location.reload();
    }

    // DSGVO Art. 17 — permanently erase ALL server-side data (not just localStorage).
    // Two-click confirm, then calls the authenticated erase endpoint.
    async handleEraseData() {
        const btn = document.getElementById('eraseDataBtn');
        if (btn && btn.dataset.confirming !== 'true') {
            btn.dataset.confirming = 'true';
            const original = btn.textContent;
            btn.textContent = '⚠️ ' + (t('confirmErase') || 'Endgültig löschen? Erneut klicken.');
            btn.classList.add('btn-danger');
            setTimeout(() => {
                if (btn && btn.dataset.confirming === 'true') {
                    btn.dataset.confirming = 'false';
                    btn.textContent = original;
                    btn.classList.remove('btn-danger');
                }
            }, 4000);
            return;
        }
        if (btn) btn.dataset.confirming = 'false';
        try {
            if (state.sessionId) {
                const tok = state.sessionToken || localStorage.getItem(TOKEN_STORAGE_KEY) || '';
                await api.eraseMyData(state.sessionId, state.userId, tok);
            }
        } catch (err) {
            console.error('Erase failed:', err);
            alert(t('eraseFailed') || 'Löschung fehlgeschlagen. Bitte erneut versuchen.');
            return;
        }
        localStorage.removeItem(SESSION_STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);
        localStorage.removeItem(COMPLETED_SESSION_KEY);
        alert(t('eraseDone') || 'Alle Ihre Daten wurden gelöscht.');
        location.reload();
    }

    // -------------------------------------------------------------------------
    // §5 ATS score — two-step: show job description input, then run analysis
    // -------------------------------------------------------------------------

    handleATSScore() {
        if (!state.sessionId) return;
        // Step 1: show the job description input section
        const inputSection = document.getElementById('atsInputSection');
        const resultsSection = document.getElementById('atsSection');
        if (inputSection) inputSection.style.display = 'block';
        if (resultsSection) resultsSection.style.display = 'none';
        // Scroll to input
        inputSection?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // AMS job-search bridge (Tier 0). Show a transparency notice, then on confirm
    // open the AMS job portal (pre-filled from the user's target job) in a NEW TAB
    // and reveal the paste-back analyzer so the CV→jobs loop is obvious. The app
    // itself transmits nothing — only the user's browser hits the AMS portal.
    async handleFindAmsJobs() {
        const cap = state.cvCaptured || {};
        const targetJob = cap.target_job || state.lastJob || '';
        const location  = cap.city || '';
        const notice    = document.getElementById('amsJobsNotice');
        const noticeText = document.getElementById('amsJobsNoticeText');
        const loopHint  = document.getElementById('amsJobsLoopHint');
        const openBtn   = document.getElementById('amsJobsOpenBtn');
        try {
            const resp = await api.getAmsJobLink(targetJob, location);
            const url  = resp?.data?.url;
            const occ  = resp?.data?.occupation || targetJob;
            if (!url) return;
            if (noticeText) noticeText.textContent = t('jobSearchNotice', occ);
            if (loopHint)   loopHint.textContent   = t('jobSearchLoopHint');
            if (openBtn) openBtn.textContent = t('jobSearchOpen');
            if (openBtn) openBtn.onclick = () => {
                window.open(url, '_blank', 'noopener');
                if (notice) notice.style.display = 'none';
                this.handleATSScore();  // reveal the paste-back match analyzer
            };
            if (notice) notice.style.display = 'block';
            notice?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } catch (err) {
            console.warn('AMS job search error:', err);
        }
    }

    _cancelAmsJobs() {
        const notice = document.getElementById('amsJobsNotice');
        if (notice) notice.style.display = 'none';
    }

    // ── Interview mode switch: free conversation ↔ guided step-by-step ────────
    // The structured 65-question interview existed all along but was unreachable;
    // this gives it a door. Some participants freeze on "tell me everything" and
    // do better with one small question at a time.
    updateModeSwitchBtn() {
        const btn = document.getElementById('modeSwitchBtn');
        const lbl = document.getElementById('modeSwitchLabel');
        if (!btn) return;
        if (!state.sessionId) { btn.style.display = 'none'; return; }
        btn.style.display = 'inline-flex';
        if (lbl) lbl.textContent = state.dumpMode ? t('modeSwitchToGuided') : t('modeSwitchToFree');
    }

    toggleInterviewMode() {
        if (state.isWaitingForResponse) return;
        if (state.dumpMode) {
            // → guided: ask the stored current question, restore skip, hide finish.
            state.dumpMode = false;
            convAddAI(t('guidedSwitchMsg'));
            if (state.currentQuestion) ui.displayQuestion(state.currentQuestion);
            document.getElementById('dumpFinishBtn')?.style.setProperty('display', 'none');
            document.getElementById('skipBtn')?.style.setProperty('display', 'inline-flex');
            if (ui.answerInput) ui.answerInput.placeholder = t('answerPlaceholder');
        } else {
            // → free: back to the (path-flavoured) dump conversation.
            state.dumpMode = true;
            convAddAI(t('freeSwitchMsg'));
            cvDocSetPrompt({ text: dumpPromptForPath(), hint: t('dumpHint'), examples: {} });
            document.getElementById('dumpFinishBtn')?.style.setProperty('display', 'inline-flex');
            document.getElementById('skipBtn')?.style.setProperty('display', 'none');
            if (ui.answerInput) ui.answerInput.placeholder = t('dumpPlaceholder') || t('answerPlaceholder');
        }
        this.updateModeSwitchBtn();
    }

    /** GUIDED-mode counterpart of the dump extractor's capture: map a direct
     *  answer onto the captured-fields model (chips, e-mail prefill, job search).
     *  Conservative — only fields where the question makes the meaning certain. */
    _captureFromGuidedAnswer(question, answerText) {
        const qid = question?.id ?? '';
        const cat = question?.category ?? '';
        const text = (answerText || '').trim();
        if (!text || text === 'photo_skipped') return;
        const cap = {};
        if (qid === 'id_name') {
            cap.name = text;
        } else if (qid === 'id_target_job') {
            cap.target_job = text;
        } else if (qid === 'id_contact') {
            const email = (text.match(/[\w.+-]+@[\w-]+\.[\w.-]+/) || [])[0];
            const phone = (text.match(/(?<!\w)(\+?\d[\d\s/()\-]{6,}\d)/) || [])[0];
            let rest = text;
            for (const piece of [email, phone]) { if (piece) rest = rest.replace(piece, ''); }
            rest = rest.replace(/[,;]+/g, ' ').replace(/\s+/g, ' ').trim();
            if (email) cap.email = email;
            if (phone) cap.phone = phone.trim();
            if (rest)  cap.city = rest;
        } else if (cat === 'experience' && !/_employer$|_title$|_dates$/.test(qid)) {
            cap.experiences = [text];
        } else if (cat === 'background' || cat === 'training') {
            cap.education = [text];
        } else if (cat === 'skills') {
            cap.skills = text.split(/\s*(?:,|\bund\b|\band\b|\n)\s*/).map(s => s.trim()).filter(s => s.length > 1);
        } else {
            return;  // motivation/photo/etc. — nothing chip-relevant
        }
        this._mergeCaptured(cap);
        ui.updateDumpProgress(state.cvCaptured);
        // Guided answers ARE content: without this, a participant who answered
        // only step-by-step could never finish via the free-mode button (its
        // handler guards on dumpHasContent and silently re-prompted instead).
        state.dumpHasContent = true;
    }

    // ── Application email: the ready-to-send Bewerbungs-E-Mail ────────────────
    // Most AMS-segment applications go out by e-mail. We already produce the CV
    // and cover letter; this assembles the actual e-mail so the participant's
    // next step is "press send", not "now write an e-mail".
    showAppEmail() {
        const cap  = state.cvCaptured || {};
        const name = cap.name || '';
        const contact = [cap.phone, cap.email].filter(Boolean).join(' · ');
        // The e-mail CONTENT is always German — it goes to an Austrian employer
        // (same rule as the CV itself). Only the surrounding UI labels translate.
        const de   = TRANSLATIONS.de;
        const job  = cap.target_job || state.lastJob || de.appEmailFallbackJob;
        const subj = document.getElementById('appEmailSubject');
        const body = document.getElementById('appEmailBody');
        if (subj && !subj.value) subj.value = de.appEmailSubject(job, name);
        if (body && !body.value) body.value = de.appEmailBody(job, name, contact);
        const hasCL = ((document.getElementById('coverLetterBody') || {}).innerText || '').trim().length > 50;
        const hint = document.getElementById('appEmailHint');
        if (hint) hint.textContent = t('appEmailHint', hasCL);
        const sec = document.getElementById('appEmailSection');
        if (sec) { sec.style.display = 'block'; sec.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
    }

    openAppEmail() {
        const to   = (document.getElementById('appEmailTo')?.value || '').trim();
        const subj = document.getElementById('appEmailSubject')?.value || '';
        const body = document.getElementById('appEmailBody')?.value || '';
        // mailto cannot attach files — the hint tells the user to attach the PDF.
        window.location.href = `mailto:${encodeURIComponent(to)}?subject=${encodeURIComponent(subj)}&body=${encodeURIComponent(body)}`;
    }

    async copyAppEmail() {
        const subj = document.getElementById('appEmailSubject')?.value || '';
        const body = document.getElementById('appEmailBody')?.value || '';
        const text = `${t('appEmailSubjLabel')} ${subj}\n\n${body}`;
        const btn  = document.getElementById('appEmailCopyBtn');
        try {
            await navigator.clipboard.writeText(text);
        } catch (e) {
            // Clipboard API can be blocked — fall back to select + execCommand.
            const ta = document.getElementById('appEmailBody');
            ta?.select();
            try { document.execCommand('copy'); } catch (e2) { /* give up quietly */ }
        }
        if (btn) {
            const old = btn.textContent;
            btn.textContent = t('appEmailCopied');
            setTimeout(() => { btn.textContent = old; }, 2000);
        }
    }

    _cancelAppEmail() {
        const sec = document.getElementById('appEmailSection');
        if (sec) sec.style.display = 'none';
    }

    // ── Test/dev capture mode (trainer test-case collection) ──────────────────
    _applyTestMode() {
        const show = state.testMode ? '' : 'none';
        const box = document.getElementById('testModeBox');
        if (box) box.style.display = state.testMode ? 'block' : 'none';
        const ind = document.getElementById('testModeIndicator');
        if (ind) ind.style.display = show;
    }

    toggleTestMode() {
        state.testMode = !state.testMode;
        try { localStorage.setItem('amsTestMode', state.testMode ? '1' : '0'); } catch (e) {}
        this._applyTestMode();
    }

    // Save the current case (raw inputs + built CV) as a replayable JSON file.
    async saveTestCase() {
        const fb = document.getElementById('saveTestCaseFeedback');
        if (fb) fb.textContent = '…';
        let cv = null;
        try {
            const r = await fetch('/api/export/json', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: state.sessionId, language: state.inputLanguage || 'de', force: true }),
            });
            if (r.ok) cv = await r.json();
        } catch (e) { /* best-effort; still save the inputs */ }
        const tc = {
            savedAt: new Date().toISOString(),
            name: (state.cvCaptured && state.cvCaptured.name) || '',
            language: state.inputLanguage || 'de',
            interview_path: state.interviewPath || '',
            inputs: state.testInputs || [],
            captured: state.cvCaptured || {},
            cv: cv,
        };
        try {
            const blob = new Blob([JSON.stringify(tc, null, 2)], { type: 'application/json' });
            const a = document.createElement('a');
            const safe = (tc.name || 'fall').replace(/[^a-z0-9]+/gi, '_').slice(0, 30) || 'fall';
            a.href = URL.createObjectURL(blob);
            a.download = `testfall_${safe}.json`;
            document.body.appendChild(a); a.click(); a.remove();
            if (fb) fb.textContent = '✓ gespeichert';
        } catch (e) {
            if (fb) fb.textContent = '✗ Fehler';
            console.warn('saveTestCase failed', e);
        }
    }

    async _runATSAnalysis() {
        if (!state.sessionId) return;
        const inputSection = document.getElementById('atsInputSection');
        const btn = document.getElementById('runAtsBtn');
        const atsBtn = document.getElementById('atsBtn');
        const jobDesc = document.getElementById('jobDescInput')?.value ?? '';

        if (btn) { btn.disabled = true; btn.textContent = t('atsAnalyzing'); }
        if (atsBtn) { atsBtn.disabled = true; }

        try {
            const resp = await api.getATSScore(state.sessionId, jobDesc);
            const d = resp?.data;
            if (!d) throw new Error('Keine Daten');

            const section    = document.getElementById('atsSection');
            const scoreBadge = document.getElementById('atsScore');
            const gradeEl    = document.getElementById('atsGrade');
            const matchedDiv = document.getElementById('atsMatched');
            const matchedRow = document.getElementById('atsMatchedRow');
            const missingDiv = document.getElementById('atsMissing');
            const missingRow = document.getElementById('atsMissingRow');
            const suggestsUl = document.getElementById('atsSuggestions');

            if (scoreBadge) scoreBadge.textContent = `${Math.round((d.score ?? 0) * 100)}%`;
            if (gradeEl)    gradeEl.textContent    = d.grade ?? '';

            if (d.matched_keywords?.length) {
                matchedDiv.innerHTML = d.matched_keywords.map(k =>
                    `<span class="ats-keyword-tag matched">${ui._escape(k)}</span>`
                ).join('');
                if (matchedRow) matchedRow.style.display = 'block';
            }

            if (d.missing_keywords?.length) {
                missingDiv.innerHTML = d.missing_keywords.slice(0, 8).map(k =>
                    `<span class="ats-keyword-tag missing">${ui._escape(k)}</span>`
                ).join('');
                if (missingRow) missingRow.style.display = 'block';
            }

            if (d.suggestions?.length) {
                suggestsUl.innerHTML = d.suggestions.slice(0, 3).map(s =>
                    `<li>${ui._escape(s)}</li>`
                ).join('');
            }

            // Hide input section, show results
            if (inputSection) inputSection.style.display = 'none';
            if (section) section.style.display = 'block';
        } catch (err) {
            console.warn('ATS score error:', err);
        } finally {
            if (btn) { btn.disabled = false; btn.textContent = t('runAtsBtn'); }
            if (atsBtn) { atsBtn.disabled = false; }
        }
    }

    _cancelATS() {
        const inputSection = document.getElementById('atsInputSection');
        if (inputSection) inputSection.style.display = 'none';
    }

    // -------------------------------------------------------------------------
    // §6 Cover letter — two-step: show company/position input, then generate
    // -------------------------------------------------------------------------

    handleCoverLetter() {
        if (!state.sessionId) return;
        // Step 1: show the input section
        const inputSection = document.getElementById('coverLetterInputSection');
        const resultsSection = document.getElementById('coverLetterSection');
        if (inputSection) inputSection.style.display = 'block';
        if (resultsSection) resultsSection.style.display = 'none';
        inputSection?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    async _generateCoverLetter() {
        if (!state.sessionId) return;
        const inputSection = document.getElementById('coverLetterInputSection');
        const clBtn = document.getElementById('coverLetterBtn');
        const genBtn = document.getElementById('generateCLBtn');
        const company  = document.getElementById('clCompanyInput')?.value.trim() ?? '';
        const position = document.getElementById('clPositionInput')?.value.trim() ?? '';

        if (genBtn) { genBtn.disabled = true; genBtn.textContent = t('coverLetterCreating'); }
        if (clBtn)  { clBtn.disabled  = true; }

        try {
            const resp = await api.getCoverLetter(state.sessionId, {
                employerName: company,
                jobTitle: position,
                language: state.inputLanguage,
            });
            const letter = resp?.data;
            if (!letter) throw new Error('Keine Daten');

            const section = document.getElementById('coverLetterSection');
            const body    = document.getElementById('coverLetterBody');
            const actions = document.getElementById('coverLetterActions');

            // CoverLetter.to_dict() returns { text, word_count, language }
            const letterText = letter.text || JSON.stringify(letter, null, 2);
            if (body) body.textContent = letterText;

            // Download + Copy buttons (rendered once; clear on re-generate)
            if (actions) {
                actions.innerHTML = '';

                const dlBtn = document.createElement('button');
                dlBtn.className = 'btn btn-secondary';
                dlBtn.textContent = '⬇️ ' + (t('downloadTxt') || 'Als .txt speichern');
                dlBtn.onclick = () => {
                    const blob = new Blob([letterText], { type: 'text/plain;charset=utf-8' });
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = 'anschreiben.txt';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(a.href);
                };

                const copyBtn = document.createElement('button');
                copyBtn.className = 'btn btn-secondary';
                copyBtn.textContent = '📋 ' + (t('copyToClipboard') || 'Kopieren');
                copyBtn.onclick = () => {
                    navigator.clipboard?.writeText(letterText).then(() => {
                        copyBtn.textContent = '✓ ' + (t('copied') || 'Kopiert!');
                        setTimeout(() => {
                            copyBtn.textContent = '📋 ' + (t('copyToClipboard') || 'Kopieren');
                        }, 2000);
                    }).catch(() => {
                        // Fallback for older browsers
                        const ta = document.createElement('textarea');
                        ta.value = letterText;
                        document.body.appendChild(ta);
                        ta.select();
                        document.execCommand('copy');
                        document.body.removeChild(ta);
                        copyBtn.textContent = '✓ ' + (t('copied') || 'Kopiert!');
                        setTimeout(() => {
                            copyBtn.textContent = '📋 ' + (t('copyToClipboard') || 'Kopieren');
                        }, 2000);
                    });
                };

                actions.appendChild(dlBtn);
                actions.appendChild(copyBtn);
            }

            // Hide input section, show results
            if (inputSection) inputSection.style.display = 'none';
            if (section) section.style.display = 'block';
        } catch (err) {
            console.warn('Cover letter error:', err);
            ui.setExportFeedback('error', t('coverLetterError', err.message));
        } finally {
            if (genBtn) { genBtn.disabled = false; genBtn.textContent = t('generateCLBtn'); }
            if (clBtn)  { clBtn.disabled  = false; }
        }
    }

    _cancelCoverLetter() {
        const inputSection = document.getElementById('coverLetterInputSection');
        if (inputSection) inputSection.style.display = 'none';
    }

    // -------------------------------------------------------------------------
    // #7 Before/after review panel
    // -------------------------------------------------------------------------

    showReview() {
        ui.renderReviewPanel();
        ui.showScreen('review');
    }

    closeReview() {
        ui.showScreen('completion');
    }
}

const interview = new InterviewManager();


// ============================================================================
// Event Wiring
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Language selection — must be wired first so translations are ready before other setup
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            state.inputLanguage = btn.dataset.lang;
            state.language      = btn.dataset.lang;   // also pass chosen language to the interview engine
            try { localStorage.setItem(LANGUAGE_STORAGE_KEY, btn.dataset.lang); } catch {}
            applyTranslations();
        });
    });

    // Restore a previously chosen language (so resume / re-download keep it
    // instead of snapping back to German).
    try {
        const savedLang = localStorage.getItem(LANGUAGE_STORAGE_KEY);
        if (savedLang) {
            state.inputLanguage = savedLang;
            state.language = savedLang;
            const activeBtn = document.querySelector(`.lang-btn[data-lang="${savedLang}"]`);
            if (activeBtn) {
                document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('selected'));
                activeBtn.classList.add('selected');
            }
            applyTranslations();
        }
    } catch {}

    // Path selection
    document.querySelectorAll('.path-button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.path-button').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            state.interviewPath = btn.dataset.path;

            // Mark step 1 done, highlight step 2
            const s1 = document.getElementById('step1Label');
            const s2 = document.getElementById('step2Label');
            if (s1) s1.classList.add('step-done');
            if (s2) s2.style.color = 'var(--secondary)';

            // Auto-advance: focus name field
            document.getElementById('userIdInput')?.focus();

            ui.updateStartButton();
        });
    });

    // Accessibility: font-size toggle (A+ button cycles normal → large → normal)
    const fontBtn = document.getElementById('fontSizeBtn');
    if (fontBtn) {
        // Restore saved preference
        if (localStorage.getItem('ams_large_text') === '1') {
            document.body.classList.add('large-text');
            fontBtn.textContent = 'A−';
            fontBtn.setAttribute('aria-label', 'Schriftgröße verkleinern');
        }
        fontBtn.addEventListener('click', () => {
            const large = document.body.classList.toggle('large-text');
            fontBtn.textContent = large ? 'A−' : 'A+';
            fontBtn.setAttribute('aria-label', large ? 'Schriftgröße verkleinern' : 'Schriftgröße vergrößern');
            localStorage.setItem('ams_large_text', large ? '1' : '0');
        });
    }

    // Name input
    document.getElementById('userIdInput')?.addEventListener('input', () => ui.updateStartButton());

    // Consent checkbox — must be checked before start button activates
    document.getElementById('consentCheck')?.addEventListener('change', () => ui.updateStartButton());

    // Welcome screen
    document.getElementById('startBtn')?.addEventListener('click',        () => interview.handleStart());
    document.getElementById('resumeBtn')?.addEventListener('click',       () => interview.handleResume());
    document.getElementById('dismissResumeBtn')?.addEventListener('click',() => interview.handleDismissResume());

    // Interview screen
    document.getElementById('answerInput')?.addEventListener('input', e => {
        ui.updateWordCount();
        ui.updateQualityIndicator();
        ui.updateSubmitButton();
        interview.scheduleLivePreview(e.target.value);
    });
    document.getElementById('submitBtn')?.addEventListener('click', () => interview.handleSubmit());
    document.getElementById('skipBtn')?.addEventListener('click',   () => interview.handleSkip());
    // Dump mode: build the CV from what's been gathered so far.
    document.getElementById('dumpFinishBtn')?.addEventListener('click', () => {
        if (state.dumpHasContent) interview.showCompletion();
        else cvDocSetPrompt({ text: dumpPromptForPath(), hint: t('dumpHint'), examples: {} });
    });

    // Completion screen
    document.getElementById('exportBtn')?.addEventListener('click',     () => interview.handleExport('pdf'));
    document.getElementById('exportDocxBtn')?.addEventListener('click', () => interview.handleExport('docx'));
    document.getElementById('exportJsonBtn')?.addEventListener('click', () => interview.handleExport('json'));
    document.getElementById('myDataBtn')?.addEventListener('click', () => {
        if (state.sessionId) {
            // The per-session token is the strong ownership proof; user_id is a
            // back-compat fallback. Sent via headers (not the URL) so the secret
            // never lands in access logs / history.
            const tok = state.sessionToken || localStorage.getItem(TOKEN_STORAGE_KEY) || '';
            api.downloadMyData(state.sessionId, state.userId, tok)
               .catch(err => { console.error('my-data failed:', err);
                               alert(t('myDataFailed') || 'Download fehlgeschlagen.'); });
        }
    });
    document.getElementById('eraseDataBtn')?.addEventListener('click', () => interview.handleEraseData());
    document.getElementById('startOverBtn')?.addEventListener('click',  () => interview.handleStartOver());

    // Test/dev capture mode: restore from localStorage, Ctrl+Shift+T toggles it,
    // and the save button writes the current case to a JSON file.
    try { state.testMode = localStorage.getItem('amsTestMode') === '1'; } catch (e) {}
    interview._applyTestMode();
    document.getElementById('saveTestCaseBtn')?.addEventListener('click', () => interview.saveTestCase());
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && (e.key === 'T' || e.key === 't')) {
            e.preventDefault();
            interview.toggleTestMode();
        }
    });

    // Save & finish later — autosave already ran on every answer; this button
    // gives explicit reassurance + an obvious exit. Returns to welcome screen,
    // resume banner shows the in-progress session.
    document.getElementById('finishLaterBtn')?.addEventListener('click', () => {
        try {
            ui.updateSaveStatus(t('statusSaved'));
            ui.showScreen('welcome');
            // Trigger the resume-banner check so the participant sees the
            // welcome-back message immediately on return.
            interview.checkForResumeSession();
        } catch (_e) { /* never block exit */ }
    });
    document.getElementById('reviewBtn')?.addEventListener('click',     () => interview.showReview());
    // §5 ATS score — two-step flow
    document.getElementById('atsBtn')?.addEventListener('click',    () => interview.handleATSScore());
    document.getElementById('runAtsBtn')?.addEventListener('click', () => interview._runATSAnalysis());
    document.getElementById('amsJobsBtn')?.addEventListener('click',     () => interview.handleFindAmsJobs());
    document.getElementById('amsJobsCancelBtn')?.addEventListener('click', () => interview._cancelAmsJobs());
    document.getElementById('modeSwitchBtn')?.addEventListener('click',  () => interview.toggleInterviewMode());
    document.getElementById('appEmailBtn')?.addEventListener('click',       () => interview.showAppEmail());
    document.getElementById('appEmailOpenBtn')?.addEventListener('click',   () => interview.openAppEmail());
    document.getElementById('appEmailCopyBtn')?.addEventListener('click',   () => interview.copyAppEmail());
    document.getElementById('appEmailCancelBtn')?.addEventListener('click', () => interview._cancelAppEmail());
    document.getElementById('cancelAtsBtn')?.addEventListener('click',() => interview._cancelATS());

    // §6 Cover letter — two-step flow
    document.getElementById('coverLetterBtn')?.addEventListener('click', () => interview.handleCoverLetter());
    document.getElementById('generateCLBtn')?.addEventListener('click',  () => interview._generateCoverLetter());
    document.getElementById('cancelCLBtn')?.addEventListener('click',    () => interview._cancelCoverLetter());

    // Photo file input
    document.getElementById('photoFileInput')?.addEventListener('change', e => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = ev => {
            const dataUrl = ev.target.result;
            state.photoDataUrl = dataUrl;
            // Show preview (legacy photo question UI)
            const preview = document.getElementById('photoPreview');
            const placeholder = document.getElementById('photoPlaceholder');
            if (preview) { preview.src = dataUrl; preview.style.display = 'block'; }
            if (placeholder) placeholder.style.display = 'none';
            // Show on the living-CV header photo slot
            const headerImg = document.getElementById('cvPhotoImg');
            const headerPlus = document.getElementById('cvPhotoPlus');
            if (headerImg) { headerImg.src = dataUrl; headerImg.style.display = 'block'; }
            if (headerPlus) headerPlus.style.display = 'none';
            // Enable submit
            ui.updateSubmitButton();
        };
        reader.readAsDataURL(file);
    });

    // Living-CV header photo slot — opens the same file picker any time.
    document.getElementById('cvPhotoSlot')?.addEventListener('click', () => {
        document.getElementById('photoFileInput')?.click();
    });

    // Photo skip button — treat as empty answer and advance
    document.getElementById('photoSkipBtn')?.addEventListener('click', () => {
        state.photoDataUrl = null;
        interview.handleSkip();
    });

    // Date helper insert button
    document.getElementById('dateHelperInsertBtn')?.addEventListener('click', () => {
        const from = document.getElementById('dateFromInput')?.value.trim() || '';
        const to   = document.getElementById('dateToInput')?.value.trim()   || '';
        if (!from && !to) return;
        const composed = t('dateHelperCompose', from || '?', to || '?');
        const answerInput = document.getElementById('answerInput');
        if (answerInput) {
            answerInput.value = composed;
            answerInput.focus();
            answerInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    });

    // Review panel
    document.getElementById('closeReviewBtn')?.addEventListener('click', () => interview.closeReview());

    // A1: Progressive reveal — hide steps 2 and 3 until user picks language/path
    (function progressiveReveal() {
        const pathSel  = document.querySelector('.path-selector');
        const userInp  = document.querySelector('.user-input');
        if (pathSel) pathSel.style.display = 'none';
        if (userInp) userInp.style.display = 'none';

        // Reveal path-selector as soon as any language button is clicked
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (pathSel) { pathSel.style.display = ''; pathSel.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
            });
        });

        // A language is pre-selected by default (German) / restored from a prior
        // visit, but no click fired — so reveal the path step immediately, else the
        // user stares at a highlighted language with no visible next step.
        if (pathSel && document.querySelector('.lang-btn.selected')) {
            pathSel.style.display = '';
        }

        // Reveal user-input as soon as a path button is clicked
        document.querySelectorAll('.path-button').forEach(btn => {
            btn.addEventListener('click', () => {
                if (userInp) {
                    userInp.style.display = '';
                    userInp.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    document.getElementById('userIdInput')?.focus();
                }
            });
        });
    })();

    // Check for resumable session on page load
    interview.checkForResumeSession();

    // AI status badge — check once at startup, refresh periodically
    const refreshAIBadge = () => {
        api.getAIStatus()
            .then(resp => ui.updateAIStatus(resp?.data))
            .catch(() => ui.updateAIStatus({ ollama_available: false }));
    };
    refreshAIBadge();
    setInterval(refreshAIBadge, AI_CHECK_INTERVAL_MS);

    // AI refresh button (if present in HTML)
    document.getElementById('aiRefreshBtn')?.addEventListener('click', () => {
        api.refreshAI().then(resp => ui.updateAIStatus(resp?.data)).catch(() => {});
    });

    console.log('[OK] AMS JobAssist UI bereit');


});
