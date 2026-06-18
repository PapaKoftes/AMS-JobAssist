/**
 * AMS JobAssist Trainer Dashboard - Main App
 *
 * Fixes applied:
 * - Input validation before all API calls
 * - Proper error display to user
 * - Fixed file input event handler (e.target.files not e.files)
 * - Pagination support
 * - Frontend logging
 */

class TrainerApp {
    constructor() {
        this.currentView = 'dashboard';
        this.currentPage = 1;
        this.totalPages = 1;
        // Classroom-scale: load the whole cohort in one page so "select all"
        // is never silently lossy. Backend caps page_size at MAX_PAGE_SIZE (200),
        // so we page-loop in loadParticipants() to gather everything.
        this.pageSize = 200;
        this.init();
    }

    /**
     * Initialize the app
     */
    init() {
        console.log('Initializing Trainer Dashboard...');

        // Update user name display
        const userNameEl = document.getElementById('user-name');
        if (userNameEl) {
            userNameEl.textContent = appState.currentUser.name;
        }

        // Restore last cohort input value
        const lastCohort = localStorage.getItem('ams_last_cohort');
        const cohortInput = document.getElementById('import-cohort');
        if (cohortInput && lastCohort) cohortInput.value = lastCohort;

        // Set up event listeners
        this.setupNavigation();
        this.setupDashboard();
        this.setupParticipants();
        this.setupDetail();
        this.setupImport();
        this.setupSettings();

        // Load initial data
        this.loadDashboard();
    }

    /**
     * Set up navigation button listeners
     */
    setupNavigation() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const viewName = e.currentTarget.dataset.view;
                if (viewName) this.switchView(viewName);
            });
        });

        // Back button
        const backBtn = document.getElementById('back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.switchView('participants'));
        }
    }

    /**
     * Switch to a different view
     */
    switchView(viewName) {
        // Hide all views
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

        // Show selected view
        const viewElement = document.getElementById(`${viewName}-view`);
        const navBtn = document.querySelector(`[data-view="${viewName}"]`);

        if (viewElement) viewElement.classList.add('active');
        if (navBtn) navBtn.classList.add('active');

        this.currentView = viewName;

        // Load view-specific data
        if (viewName === 'dashboard') this.loadDashboard();
        if (viewName === 'participants') this.loadParticipants();
    }

    /* ========================================
       DASHBOARD VIEW
       ======================================== */

    setupDashboard() {
        const importBtn = document.getElementById('import-quick-btn');
        const exportBtn = document.getElementById('export-quick-btn');
        const refreshBtn = document.getElementById('refresh-metrics-btn');
        const cohortSelect = document.getElementById('cohort-select');

        if (importBtn) importBtn.addEventListener('click', () => this.switchView('import'));
        if (exportBtn) {
            exportBtn.addEventListener('click', async () => {
                const btn = exportBtn;
                btn.disabled = true;
                btn.textContent = '⏳ Exportiere…';
                try {
                    await this.exportAllAsPDF();
                } finally {
                    btn.disabled = false;
                    btn.textContent = '📤 Alle als PDF exportieren';
                }
            });
        }
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadDashboard());

        if (cohortSelect) {
            cohortSelect.addEventListener('change', (e) => {
                this.loadDashboardMetrics(e.target.value);
            });
        }
    }

    async loadDashboard() {
        console.log('Loading dashboard...');
        appState.setLoading('participants', true);

        try {
            const response = await api.listParticipants(null, null, 1, this.pageSize);
            // Handle paginated response
            const participants = response.items || response;
            appState.setParticipants(participants);
            this.updateCohortSelectors();

            if (appState.cohorts.size > 0) {
                const firstCohort = Array.from(appState.cohorts)[0];
                await this.loadDashboardMetrics(firstCohort);
            } else {
                this.loadDashboardMetrics('');
            }
        } catch (error) {
            console.error('Dashboard load error:', error);
            this._showErrorInElement('participants-tbody', `Fehler beim Laden der Übersicht: ${error.message}`);
        } finally {
            appState.setLoading('participants', false);
        }
    }

    async loadDashboardMetrics(cohortId) {
        try {
            // 'all' is not a valid cohort_id — skip cohort metrics when no filter selected
            if (!cohortId) {
                this.updateActivityFeed();
                return;
            }
            const metrics = await api.getCohortMetrics(cohortId);

            this._safeSetText('metric-total', metrics.total_participants);
            this._safeSetText('metric-completed', metrics.completed);
            this._safeSetText('metric-percentage', metrics.completion_rate);
            this._safeSetText('metric-quality', metrics.avg_quality);
            this._safeSetText('metric-pending', metrics.pending);

            this.updateActivityFeed();
        } catch (error) {
            console.error('Metrics load error:', error);
        }
    }

    updateActivityFeed() {
        const feed = document.getElementById('activity-feed');
        if (!feed) return;

        const recentParticipants = appState.participants
            .sort((a, b) => new Date(b.last_updated_at) - new Date(a.last_updated_at))
            .slice(0, 5);

        if (recentParticipants.length === 0) {
            Components.showEmpty(feed, 'Keine aktuellen Aktivitäten');
            return;
        }

        feed.innerHTML = '';
        recentParticipants.forEach(p => {
            const item = Components.createActivityItem(
                `Updated ${p.name || 'Unknown'}`,
                `Status: ${p.status}`,
                p.last_updated_at
            );
            feed.appendChild(item);
        });
    }

    /* ========================================
       PARTICIPANTS VIEW
       ======================================== */

    setupParticipants() {
        const searchInput = document.getElementById('search-participants');
        const filterStatus = document.getElementById('filter-status');
        const filterCohort = document.getElementById('filter-cohort');
        const selectAll = document.getElementById('select-all-participants');
        const approveBtn = document.getElementById('bulk-approve-btn');
        const exportBtn = document.getElementById('bulk-export-btn');
        const rejectBtn = document.getElementById('bulk-reject-btn');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                appState.setFilter('search', e.target.value);
                this.renderParticipantsList();
            });
        }

        if (filterStatus) {
            filterStatus.addEventListener('change', (e) => {
                appState.setFilter('status', e.target.value);
                this.renderParticipantsList();
            });
        }

        if (filterCohort) {
            filterCohort.addEventListener('change', (e) => {
                appState.setFilter('cohort', e.target.value);
                this.renderParticipantsList();
            });
        }

        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                const filtered = appState.getFilteredParticipants();
                if (e.target.checked) {
                    appState.selectAllParticipants(filtered);
                } else {
                    appState.clearSelections();
                }
                this.renderParticipantsList();
            });
        }

        if (approveBtn) approveBtn.addEventListener('click', () => this.bulkApprove());
        if (exportBtn) exportBtn.addEventListener('click', () => this.bulkExport());
        if (rejectBtn) rejectBtn.addEventListener('click', () => this.bulkReject());
    }

    async loadParticipants() {
        console.log('Loading participants...');
        appState.setLoading('participants', true);

        try {
            // Page-loop so "select all" sees the whole filtered set, not just
            // the first 50. Backend caps page_size at 200, so loop if needed.
            const cohort = appState.filters.cohort || null;
            const status = appState.filters.status || null;
            let all = [];
            let page = 1;
            let totalPages = 1;
            do {
                const response = await api.listParticipants(cohort, status, page, this.pageSize);
                const items = response.items || response;
                all = all.concat(items);
                totalPages = response.total_pages || 1;
                page += 1;
            } while (page <= totalPages);

            this.totalPages = totalPages;
            this.currentPage = 1;

            appState.setParticipants(all);
            this.updateCohortSelectors();
            this.renderParticipantsList();
        } catch (error) {
            console.error('Participants load error:', error);
            this._showErrorInElement('participants-tbody', `Fehler beim Laden der Teilnehmer: ${error.message}`);
        } finally {
            appState.setLoading('participants', false);
        }
    }

    renderParticipantsList() {
        const tbody = document.getElementById('participants-tbody');
        if (!tbody) return;

        const filtered = appState.getFilteredParticipants();

        if (filtered.length === 0) {
            Components.showEmpty(tbody, 'Keine Teilnehmer entsprechen den Filtern');
            this.updateBulkActionButtons();
            return;
        }

        tbody.innerHTML = '';
        filtered.forEach(participant => {
            const isSelected = appState.selectedParticipants.has(participant.participant_id);
            const row = Components.createParticipantRow(participant, isSelected);

            const selectBox = row.querySelector('.select-row');
            if (selectBox) {
                selectBox.addEventListener('change', () => {
                    appState.toggleParticipantSelection(participant.participant_id);
                    this.updateBulkActionButtons();
                });
            }

            const viewBtn = row.querySelector('[data-action="view"]');
            if (viewBtn) {
                viewBtn.addEventListener('click', () => {
                    this.viewParticipantDetail(participant.participant_id);
                });
            }

            const approveBtn = row.querySelector('[data-action="approve"]');
            if (approveBtn) {
                approveBtn.addEventListener('click', () => {
                    this.viewParticipantDetail(participant.participant_id);
                });
            }

            tbody.appendChild(row);
        });

        this.updateBulkActionButtons();
    }

    updateBulkActionButtons() {
        const count = appState.selectedParticipants.size;
        const buttons = ['bulk-approve-btn', 'bulk-export-btn', 'bulk-reject-btn'];

        buttons.forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.disabled = count === 0;
        });

        // Make the selection scope explicit so "select all" is never ambiguous.
        const countEl = document.getElementById('selection-count');
        if (countEl) {
            const total = appState.getFilteredParticipants().length;
            countEl.textContent = count > 0 ? `${count} von ${total} ausgewählt` : '';
        }
    }

    async bulkApprove() {
        const count = appState.selectedParticipants.size;
        if (count === 0) return;
        if (!confirm(`Approve ${count} participants?`)) return;

        const trainerName = appState.currentUser.name;
        if (!trainerName || trainerName === 'Trainer') {
            alert('Bitte legen Sie zuerst Ihren Trainer-Namen in den Einstellungen fest.');
            return;
        }

        appState.setLoading('approval', true);
        const ids = Array.from(appState.selectedParticipants);

        try {
            // Atomic bulk endpoint — one call, commits in a single transaction.
            // Empty feedback so the backend preserves any existing trainer_notes.
            const result = await api.bulkApprove({
                participant_ids: ids,
                approval_status: 'approved',
                feedback: '',
                approved_by: trainerName
            });

            appState.clearSelections();
            this.loadParticipants();

            const errors = result.errors || [];
            if (errors.length > 0) {
                alert(`${result.approved} von ${count} Teilnehmern freigegeben.\n` +
                    `Fehlgeschlagen:\n${errors.join('\n')}`);
            } else {
                alert(`${result.approved} von ${count} Teilnehmern freigegeben`);
            }
        } catch (error) {
            console.error('Bulk approve error:', error);
            alert(`Freigabe fehlgeschlagen: ${error.message}`);
        } finally {
            appState.setLoading('approval', false);
        }
    }

    async bulkReject() {
        const count = appState.selectedParticipants.size;
        if (count === 0) return;

        const reason = prompt(`Reject ${count} participants? Reason:`, '');
        if (!reason) return;

        const trainerName = appState.currentUser.name;
        if (!trainerName || trainerName === 'Trainer') {
            alert('Bitte legen Sie zuerst Ihren Trainer-Namen in den Einstellungen fest.');
            return;
        }

        appState.setLoading('approval', true);
        const ids = Array.from(appState.selectedParticipants);

        try {
            // No dedicated bulk-reject endpoint exists; the atomic bulk-approve
            // endpoint accepts any approval_status, so reuse it for rejections.
            // The reason is real feedback, so it is passed through to trainer_notes.
            const result = await api.bulkApprove({
                participant_ids: ids,
                approval_status: 'rejected',
                feedback: reason,
                approved_by: trainerName
            });

            appState.clearSelections();
            this.loadParticipants();

            const errors = result.errors || [];
            if (errors.length > 0) {
                alert(`${result.approved} von ${count} Teilnehmern abgelehnt.\n` +
                    `Fehlgeschlagen:\n${errors.join('\n')}`);
            } else {
                alert(`${result.approved} von ${count} Teilnehmern abgelehnt`);
            }
        } catch (error) {
            console.error('Bulk reject error:', error);
            alert(`Ablehnung fehlgeschlagen: ${error.message}`);
        } finally {
            appState.setLoading('approval', false);
        }
    }

    async bulkExport() {
        const ids = Array.from(appState.selectedParticipants);
        if (ids.length === 0) {
            alert('Bitte wählen Sie mindestens einen Teilnehmer aus.');
            return;
        }

        const fmt = await this._chooseExportFormat(ids.length);
        if (!fmt) return;  // cancelled

        try {
            const headers = { 'Content-Type': 'application/json' };
            if (api.apiKey) headers['X-API-Key'] = api.apiKey;
            const resp = await fetch('/api/bulk-export', {
                method: 'POST',
                headers,
                body: JSON.stringify({ participant_ids: ids, format: fmt, language: 'de' })
            });
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                alert(`Export fehlgeschlagen: ${err.detail || resp.statusText}`);
                return;
            }
            const blob = await resp.blob();
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href     = url;
            a.download = `ams_export_${ids.length}teilnehmer.${fmt === 'json' ? 'json' : 'zip'}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (err) {
            alert(`Export-Fehler: ${err.message}`);
        }
    }

    async exportAllAsPDF() {
        const ids = appState.participants.map(p => p.participant_id);
        if (ids.length === 0) {
            alert('Keine Teilnehmer zum Exportieren vorhanden.');
            return;
        }
        try {
            const headers = { 'Content-Type': 'application/json' };
            if (api.apiKey) headers['X-API-Key'] = api.apiKey;
            const resp = await fetch('/api/bulk-export', {
                method: 'POST',
                headers,
                body: JSON.stringify({ participant_ids: ids, format: 'pdf', language: 'de' })
            });
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                alert(`Export fehlgeschlagen: ${err.detail || resp.statusText}`);
                return;
            }
            const blob = await resp.blob();
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href     = url;
            a.download = `ams_export_alle_${ids.length}_teilnehmer.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (err) {
            alert(`Export-Fehler: ${err.message}`);
        }
    }

    updateCohortSelectors() {
        const selectors = ['cohort-select', 'filter-cohort'];

        selectors.forEach(selectorId => {
            const selector = document.getElementById(selectorId);
            if (!selector) return;

            const currentValue = selector.value;
            selector.innerHTML = '<option value="">All Cohorts</option>';

            appState.cohorts.forEach(cohort => {
                const option = document.createElement('option');
                option.value = cohort;
                option.textContent = cohort;
                selector.appendChild(option);
            });

            selector.value = currentValue;
        });
    }

    /* ========================================
       DETAIL VIEW
       ======================================== */

    setupDetail() {
        const refreshBtn = document.getElementById('detail-refresh-btn');
        const saveBtn = document.getElementById('save-approval-btn');
        const prevBtn = document.getElementById('detail-prev-btn');
        const nextBtn = document.getElementById('detail-next-btn');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                if (appState.currentParticipant) {
                    await this.loadParticipantDetail(appState.currentParticipant.participant_id);
                }
            });
        }

        if (saveBtn) {
            saveBtn.addEventListener('click', async () => {
                await this.saveApproval();
            });
        }

        const lockBtn = document.getElementById('detail-lock-btn');
        if (lockBtn) {
            lockBtn.addEventListener('click', async () => {
                await this.toggleLock();
            });
        }

        // B2: Prev/Next participant navigation
        if (prevBtn) {
            prevBtn.addEventListener('click', async () => {
                const participants = appState.participants || [];
                const idx = appState.currentParticipantIndex ?? -1;
                if (idx > 0) {
                    appState.currentParticipantIndex = idx - 1;
                    await this.loadParticipantDetail(participants[idx - 1].participant_id);
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', async () => {
                const participants = appState.participants || [];
                const idx = appState.currentParticipantIndex ?? -1;
                if (idx < participants.length - 1) {
                    appState.currentParticipantIndex = idx + 1;
                    await this.loadParticipantDetail(participants[idx + 1].participant_id);
                }
            });
        }
    }

    async viewParticipantDetail(participantId) {
        if (!participantId || participantId <= 0) {
            console.error('Invalid participant ID');
            return;
        }
        // B2: store the index of this participant in the current list
        const participants = appState.participants || [];
        const idx = participants.findIndex(p => p.participant_id === participantId);
        appState.currentParticipantIndex = idx;

        await this.loadParticipantDetail(participantId);
        this.switchView('detail');
    }

    async loadParticipantDetail(participantId) {
        appState.setLoading('detail', true);

        try {
            const participant = await api.getParticipant(participantId);
            appState.setCurrentParticipant(participant);
            this.renderDetailView(participant);

            // Lock state lives on the submission and is exposed via /status.
            try {
                const status = await api.getParticipantStatus(participantId);
                this.currentLocked = !!status.locked;
            } catch (e) {
                console.warn('Could not load lock status:', e);
                this.currentLocked = false;
            }
            this.renderLockButton();
        } catch (error) {
            console.error('Detail load error:', error);
            alert(`Fehler beim Laden der Teilnehmer-Details: ${error.message}`);
        } finally {
            appState.setLoading('detail', false);
        }
    }

    renderLockButton() {
        const lockBtn = document.getElementById('detail-lock-btn');
        if (!lockBtn) return;
        if (this.currentLocked) {
            lockBtn.textContent = '🔓 Entsperren';
            lockBtn.title = 'Bearbeitung durch Teilnehmer wieder erlauben';
            lockBtn.classList.add('is-locked');
        } else {
            lockBtn.textContent = '🔒 Sperren';
            lockBtn.title = 'Bearbeitung durch Teilnehmer sperren';
            lockBtn.classList.remove('is-locked');
        }
    }

    async toggleLock() {
        if (!appState.currentParticipant) {
            alert('Kein Teilnehmer ausgewählt');
            return;
        }
        const trainerName = appState.currentUser.name;
        if (!trainerName || trainerName === 'Trainer') {
            alert('Bitte legen Sie zuerst Ihren Trainer-Namen in den Einstellungen fest.');
            return;
        }

        const participantId = appState.currentParticipant.participant_id;
        const lockBtn = document.getElementById('detail-lock-btn');
        if (lockBtn) lockBtn.disabled = true;

        try {
            if (this.currentLocked) {
                await api.unlockParticipant(participantId, trainerName);
                this.currentLocked = false;
            } else {
                await api.lockParticipant(participantId, trainerName);
                this.currentLocked = true;
            }
            this.renderLockButton();
        } catch (error) {
            console.error('Lock toggle error:', error);
            alert(`Sperren/Entsperren fehlgeschlagen: ${error.message}`);
        } finally {
            if (lockBtn) lockBtn.disabled = false;
        }
    }

    renderDetailView(participant) {
        this._safeSetText('detail-name', participant.name || 'Unknown');
        this._safeSetText('detail-path', participant.interview_path || '—');

        const statusEl = document.getElementById('detail-status');
        if (statusEl) {
            statusEl.textContent = participant.status;
            statusEl.className = `status-badge status-${participant.status}`;
        }

        this._safeSetText('detail-imported', Components.formatDate(participant.first_imported_at));

        if (participant.latest_submission) {
            // 0–1 score shown as percent, consistent with the list view and Tool 1.
            this._safeSetText('detail-quality',
                Math.round((participant.latest_submission.overall_quality || 0) * 100) + ' %');
        }

        const approvalStatus = document.getElementById('approval-status');
        if (approvalStatus) approvalStatus.value = participant.status;

        const approvalFeedback = document.getElementById('approval-feedback');
        if (approvalFeedback) approvalFeedback.value = participant.trainer_notes || '';

        // B7: Show participant language
        const lang = participant.latest_submission?.cv_data?.language_input
            || participant.latest_submission?.language_primary
            || '—';
        this._safeSetText('detail-language', lang);

        this.renderCVComparison(participant);
        this.updateDetailNav();
    }

    updateDetailNav() {
        const participants = appState.participants || [];
        const idx = appState.currentParticipantIndex ?? -1;
        const navEl = document.getElementById('detail-nav');
        const labelEl = document.getElementById('detail-nav-label');
        const prevBtn = document.getElementById('detail-prev-btn');
        const nextBtn = document.getElementById('detail-next-btn');
        if (!navEl || participants.length <= 1) { if (navEl) navEl.style.display = 'none'; return; }
        navEl.style.display = 'flex';
        if (labelEl) labelEl.textContent = `${idx + 1} von ${participants.length}`;
        if (prevBtn) prevBtn.disabled = idx <= 0;
        if (nextBtn) nextBtn.disabled = idx >= participants.length - 1;
    }

    renderCVComparison(participant) {
        const original = document.getElementById('original-answers');
        const polished = document.getElementById('polished-cv');
        if (!original || !polished) return;

        original.innerHTML = '';
        polished.innerHTML = '';

        if (!participant.latest_submission || !participant.latest_submission.cv_data) {
            original.innerHTML = '<p class="empty-state">No interview data</p>';
            polished.innerHTML = '<p class="empty-state">No polished CV</p>';
            return;
        }

        const cvData = participant.latest_submission.cv_data;

        // Build sections from whatever shape Tool 1 produced.
        // Canonical export has a top-level "sections" array; legacy exports
        // may have flat keys like background/experience/skills.
        const sections = [];

        // Canonical CVDocument: basics + experience/education/skills/custom_sections.
        // Entries store text under german/english and have no question_id, so we
        // key each editable section by "<list>.<index>" (e.g. "experience.0").
        const isCanonical = cvData.schema_version !== undefined ||
            Array.isArray(cvData.experience) || Array.isArray(cvData.education) ||
            Array.isArray(cvData.custom_sections);

        if (isCanonical && !Array.isArray(cvData.sections)) {
            const LABELS = {
                experience: 'Berufserfahrung',
                education: 'Ausbildung',
                custom_sections: 'Weitere Angaben',
            };
            ['experience', 'education', 'custom_sections'].forEach(listName => {
                (cvData[listName] || []).forEach((entry, i) => {
                    if (entry && entry.hidden) return;
                    const polishedText = entry.german || entry.english ||
                        (entry.bullets || []).join(' · ') || '';
                    const raw = entry.raw_text || entry.native || entry.english || '';
                    const heading = entry.heading || entry.title || LABELS[listName] || listName;
                    sections.push({ q: heading, key: `${listName}.${i}`, raw, polishedText });
                });
            });
            // Skills: canonical SkillGroups, else all_skills list.
            const skillGroups = cvData.skills || [];
            if (Array.isArray(skillGroups) && skillGroups.length &&
                typeof skillGroups[0] === 'object') {
                skillGroups.forEach((grp, i) => {
                    const items = grp.items || grp.skills || [];
                    const text = items.length ? items.join(', ') : (grp.german || grp.name || '');
                    if (text) sections.push({ q: grp.name || 'Fähigkeiten', key: `skills.${i}`, raw: text, polishedText: text });
                });
            } else if (Array.isArray(cvData.all_skills) && cvData.all_skills.length) {
                const text = cvData.all_skills.join(', ');
                sections.push({ q: 'Fähigkeiten', key: '', raw: text, polishedText: text });
            }
        } else if (Array.isArray(cvData.sections) && cvData.sections.length > 0) {
            // Canonical shape: [{category, german, english, bullets, period, quality_score, ...}]
            cvData.sections.forEach(sec => {
                const label = sec.category || sec.question_id || 'Abschnitt';
                const raw   = sec.raw_text || sec.english || sec.german || '';
                const polishedText = sec.german || sec.english || (sec.bullets || []).join(' · ') || raw || 'N/A';
                sections.push({ q: label, key: sec.question_id || '', raw, polishedText });
            });
        } else if (cvData.content && typeof cvData.content === 'object') {
            // Legacy Shape A: content is an object of {key: string|array}
            Object.entries(cvData.content).forEach(([k, v]) => {
                const text = Array.isArray(v) ? v.join('\n') : String(v || '');
                sections.push({ q: k, raw: text, polishedText: text });
            });
        } else {
            // Legacy flat shape or unknown: render scalar string fields
            const skip = new Set(['user_id','session_id','interview_path','overall_quality',
                                   'ready_for_export','schema_version','_export_language']);
            Object.entries(cvData).forEach(([k, v]) => {
                if (skip.has(k) || typeof v === 'object') return;
                sections.push({ q: k, raw: String(v), polishedText: String(v) });
            });
        }

        if (sections.length === 0) {
            original.innerHTML = '<p class="empty-state">Keine Daten vorhanden</p>';
            polished.innerHTML = '<p class="empty-state">Keine Daten vorhanden</p>';
            return;
        }

        sections.forEach(section => {
            original.appendChild(Components.createCVSection(section.q, section.raw, true, false));
            polished.appendChild(Components.createCVSection(section.q, section.polishedText, false, true, section.key || ''));
        });

        polished.querySelectorAll('.cv-answer.editable').forEach(elem => {
            elem.addEventListener('click', (e) => {
                this.enableInlineEdit(e.target);
            });
        });
    }

    enableInlineEdit(element) {
        if (element.classList.contains('editing')) return;  // Prevent double-edit
        element.classList.add('editing');

        const originalText = element.textContent;
        element.classList.add('hidden');

        const textarea = document.createElement('textarea');
        textarea.className = 'edit-field';
        textarea.value = originalText;

        const saveBtn = document.createElement('button');
        saveBtn.className = 'btn btn-small btn-primary';
        saveBtn.textContent = 'Save';

        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn btn-small';
        cancelBtn.textContent = 'Cancel';

        const container = document.createElement('div');
        container.appendChild(textarea);

        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'edit-actions';
        actionsDiv.appendChild(saveBtn);
        actionsDiv.appendChild(cancelBtn);

        container.appendChild(actionsDiv);
        element.parentNode.insertBefore(container, element.nextSibling);

        const sectionKey = element.dataset.sectionKey || '';

        const cleanup = () => {
            element.classList.remove('hidden', 'editing');
            container.remove();
        };

        saveBtn.addEventListener('click', async () => {
            const newText = textarea.value;
            element.textContent = newText;
            cleanup();

            // Persist to backend if we have enough context
            if (sectionKey && appState.currentParticipant?.participant_id) {
                try {
                    await api.updateCVSection(
                        appState.currentParticipant.participant_id,
                        sectionKey,
                        newText
                    );
                    // Brief confirmation badge
                    const badge = document.createElement('span');
                    badge.className = 'save-confirmation';
                    badge.textContent = '✓ Gespeichert';
                    element.insertAdjacentElement('afterend', badge);
                    setTimeout(() => badge.remove(), 2500);
                } catch (err) {
                    console.warn('CV section persist failed (edit kept locally):', err);
                }
            }
        });

        cancelBtn.addEventListener('click', () => {
            cleanup();
        });

        textarea.focus();
    }

    async saveApproval() {
        // Validate state before API call
        if (!appState.currentParticipant) {
            alert('Kein Teilnehmer ausgewählt');
            return;
        }

        const participantId = appState.currentParticipant.participant_id;
        const statusEl = document.getElementById('approval-status');
        const feedbackEl = document.getElementById('approval-feedback');
        const messageEl = document.getElementById('approval-message');

        if (!statusEl) return;

        const status = statusEl.value;
        const feedback = feedbackEl ? feedbackEl.value : '';
        const trainerName = appState.currentUser.name;

        // Validate
        if (!status) {
            Components.showMessage(messageEl, 'Bitte wählen Sie einen Status', 'error');
            return;
        }
        if (!trainerName || trainerName === 'Trainer') {
            Components.showMessage(messageEl, 'Bitte legen Sie zuerst Ihren Namen in den Einstellungen fest', 'error', 5000);
            return;
        }

        appState.setLoading('approval', true);

        try {
            await api.approveSubmission(participantId, {
                approval_status: status,
                feedback: feedback,
                approved_by: trainerName
            });

            Components.showMessage(messageEl, 'Freigabe gespeichert', 'success');
            await this.loadParticipantDetail(participantId);
        } catch (error) {
            console.error('Approval save error:', error);
            Components.showMessage(messageEl, `Fehler: ${error.message}`, 'error', 5000);
        } finally {
            appState.setLoading('approval', false);
        }
    }

    /* ========================================
       IMPORT VIEW
       ======================================== */

    setupImport() {
        const fileInput = document.getElementById('import-file');
        const dropZone = document.getElementById('drop-zone');
        const cohortInput = document.getElementById('import-cohort');
        const submitBtn = document.getElementById('import-submit-btn');

        if (!fileInput || !dropZone || !submitBtn) return;

        dropZone.addEventListener('click', () => fileInput.click());

        // FIX: was e.files, should be e.target.files
        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                this.handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        submitBtn.addEventListener('click', async () => {
            const file = fileInput.files[0];
            const cohort = cohortInput ? cohortInput.value.trim() : '';

            if (!file) {
                alert('Bitte wählen Sie eine Datei');
                return;
            }

            if (!cohort) {
                alert('Bitte geben Sie einen Namen für die Kursgruppe ein');
                return;
            }

            await this.performImport(file, cohort);
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        const isValid = file.name.endsWith('.json') || file.name.endsWith('.zip');
        if (!isValid) {
            alert('Bitte wählen Sie eine .json- oder .zip-Datei');
            return;
        }

        // Client-side size check
        const maxSizeMB = 50;
        if (file.size > maxSizeMB * 1024 * 1024) {
            alert(`File too large (${(file.size / (1024*1024)).toFixed(1)} MB). Maximum: ${maxSizeMB} MB`);
            return;
        }

        const dropZone = document.getElementById('drop-zone');
        if (dropZone) {
            dropZone.innerHTML = `<p>Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)</p>`;
        }

        const fileInput = document.getElementById('import-file');
        if (fileInput) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
        }
    }

    async performImport(file, cohort) {
        const resultDiv = document.getElementById('import-result');
        appState.setLoading('import', true);

        try {
            const result = await api.importCVs(file, cohort);

            // B1: Remember the cohort for next session
            localStorage.setItem('ams_last_cohort', cohort);

            if (resultDiv) {
                resultDiv.classList.remove('hidden', 'error');
                resultDiv.classList.add('success');
                const msgEl = resultDiv.querySelector('.result-message');
                const detailEl = resultDiv.querySelector('.result-details');
                if (msgEl) msgEl.textContent = `Erfolgreich: ${result.message}`;
                if (detailEl) detailEl.textContent = `Importiert: ${result.imported} Lebenslauf/Lebensläufe`;

                setTimeout(() => {
                    const cohortInput = document.getElementById('import-cohort');
                    const fileInput = document.getElementById('import-file');
                    const dropZone = document.getElementById('drop-zone');
                    if (cohortInput) cohortInput.value = '';
                    if (fileInput) fileInput.value = '';
                    if (dropZone) dropZone.innerHTML = '<p>Drag & drop JSON or ZIP file here</p><p>or click to select</p>';
                    resultDiv.classList.add('hidden');
                }, 3000);
            }

            await this.loadParticipants();
        } catch (error) {
            console.error('Import error:', error);

            if (resultDiv) {
                resultDiv.classList.remove('hidden', 'success');
                resultDiv.classList.add('error');
                const msgEl = resultDiv.querySelector('.result-message');
                const detailEl = resultDiv.querySelector('.result-details');
                if (msgEl) msgEl.textContent = 'Import failed';
                if (detailEl) detailEl.textContent = error.message;
            }
        } finally {
            appState.setLoading('import', false);
        }
    }

    /* ========================================
       SETTINGS VIEW
       ======================================== */

    setupSettings() {
        const nameInput = document.getElementById('setting-name');
        if (nameInput) {
            nameInput.value = appState.currentUser.name;

            nameInput.addEventListener('blur', (e) => {
                const name = e.target.value.trim();
                if (name) {
                    appState.setTrainerName(name);
                    const userNameEl = document.getElementById('user-name');
                    if (userNameEl) userNameEl.textContent = name;
                }
            });
        }

        const clearCacheBtn = document.getElementById('clear-cache-btn');
        if (clearCacheBtn) {
            clearCacheBtn.addEventListener('click', () => {
                if (confirm('Alle zwischengespeicherten Daten löschen?')) {
                    localStorage.clear();
                    alert('Zwischenspeicher geleert. Bitte laden Sie die Seite neu.');
                }
            });
        }

        // API key setting
        const apiKeyInput = document.getElementById('setting-api-key');
        if (apiKeyInput) {
            apiKeyInput.value = api.apiKey || '';
            apiKeyInput.addEventListener('blur', (e) => {
                api.setApiKey(e.target.value.trim());
            });
        }
    }

    /* ========================================
       UTILITY METHODS
       ======================================== */

    /**
     * Show a small modal letting the trainer pick an export format.
     * Resolves to 'pdf' | 'docx' | 'json', or null if cancelled.
     * Replaces the old free-text prompt() so the format can't be mistyped.
     */
    _chooseExportFormat(count) {
        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';

            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <h3>Export-Format wählen</h3>
                <p>Format für ${count} Teilnehmer auswählen:</p>
                <div class="modal-actions">
                    <button class="btn btn-primary" data-format="pdf">PDF</button>
                    <button class="btn btn-secondary" data-format="docx">Word (.docx)</button>
                    <button class="btn btn-secondary" data-format="json">JSON</button>
                </div>
                <div class="modal-actions">
                    <button class="btn btn-small" data-format="">Abbrechen</button>
                </div>
            `;
            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            const finish = (value) => {
                overlay.remove();
                resolve(value || null);
            };

            modal.querySelectorAll('[data-format]').forEach(btn => {
                btn.addEventListener('click', () => finish(btn.dataset.format));
            });
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) finish('');
            });
        });
    }

    /**
     * Safely set text content of an element by ID
     */
    _safeSetText(elementId, text) {
        const el = document.getElementById(elementId);
        if (el) el.textContent = text;
    }

    /**
     * Show error message inside a container element
     */
    _showErrorInElement(elementId, message) {
        const el = document.getElementById(elementId);
        if (el) {
            Components.showEmpty(el, message);
        }
    }
}

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, starting app...');
    window.trainerApp = new TrainerApp();
});
