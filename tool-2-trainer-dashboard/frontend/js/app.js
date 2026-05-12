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
            const response = await api.listParticipants();
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
            this._showErrorInElement('participants-tbody', `Error loading dashboard: ${error.message}`);
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
            Components.showEmpty(feed, 'No recent activity');
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
            const response = await api.listParticipants(
                appState.filters.cohort || null,
                appState.filters.status || null,
                this.currentPage
            );

            // Handle paginated response
            const participants = response.items || response;
            this.totalPages = response.total_pages || 1;
            this.currentPage = response.page || 1;

            appState.setParticipants(participants);
            this.updateCohortSelectors();
            this.renderParticipantsList();
        } catch (error) {
            console.error('Participants load error:', error);
            this._showErrorInElement('participants-tbody', `Error loading participants: ${error.message}`);
        } finally {
            appState.setLoading('participants', false);
        }
    }

    renderParticipantsList() {
        const tbody = document.getElementById('participants-tbody');
        if (!tbody) return;

        const filtered = appState.getFilteredParticipants();

        if (filtered.length === 0) {
            Components.showEmpty(tbody, 'No participants match filters');
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
    }

    async bulkApprove() {
        const count = appState.selectedParticipants.size;
        if (count === 0) return;
        if (!confirm(`Approve ${count} participants?`)) return;

        const trainerName = appState.currentUser.name;
        if (!trainerName || trainerName === 'Trainer') {
            alert('Please set your trainer name in Settings first.');
            return;
        }

        appState.setLoading('approval', true);
        let successCount = 0;

        for (const participantId of appState.selectedParticipants) {
            try {
                await api.approveSubmission(participantId, {
                    approval_status: 'approved',
                    feedback: 'Approved via bulk action',
                    approved_by: trainerName
                });
                successCount++;
            } catch (error) {
                console.error(`Error approving participant ${participantId}:`, error);
            }
        }

        appState.clearSelections();
        appState.setLoading('approval', false);
        this.loadParticipants();
        alert(`Approved ${successCount} out of ${count} participants`);
    }

    async bulkReject() {
        const count = appState.selectedParticipants.size;
        if (count === 0) return;

        const reason = prompt(`Reject ${count} participants? Reason:`, '');
        if (!reason) return;

        const trainerName = appState.currentUser.name;
        if (!trainerName || trainerName === 'Trainer') {
            alert('Please set your trainer name in Settings first.');
            return;
        }

        appState.setLoading('approval', true);
        let successCount = 0;

        for (const participantId of appState.selectedParticipants) {
            try {
                await api.approveSubmission(participantId, {
                    approval_status: 'rejected',
                    feedback: reason,
                    approved_by: trainerName
                });
                successCount++;
            } catch (error) {
                console.error(`Error rejecting participant ${participantId}:`, error);
            }
        }

        appState.clearSelections();
        appState.setLoading('approval', false);
        this.loadParticipants();
        alert(`Rejected ${successCount} out of ${count} participants`);
    }

    async bulkExport() {
        const ids = Array.from(appState.selectedParticipants);
        if (ids.length === 0) {
            alert('Bitte wählen Sie mindestens einen Teilnehmer aus.');
            return;
        }

        const format = prompt(`Export-Format wählen für ${ids.length} Teilnehmer:\npdf / docx / json`, 'pdf');
        if (!format || !['pdf', 'docx', 'json'].includes(format.trim().toLowerCase())) return;
        const fmt = format.trim().toLowerCase();

        try {
            const resp = await fetch('/api/bulk-export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
            const resp = await fetch('/api/bulk-export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
        } catch (error) {
            console.error('Detail load error:', error);
            alert(`Error loading participant details: ${error.message}`);
        } finally {
            appState.setLoading('detail', false);
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
            this._safeSetText('detail-quality',
                (participant.latest_submission.overall_quality || 0).toFixed(1) + '/10');
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

        if (Array.isArray(cvData.sections) && cvData.sections.length > 0) {
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
            alert('No participant selected');
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
            Components.showMessage(messageEl, 'Please select a status', 'error');
            return;
        }
        if (!trainerName || trainerName === 'Trainer') {
            Components.showMessage(messageEl, 'Please set your name in Settings first', 'error', 5000);
            return;
        }

        appState.setLoading('approval', true);

        try {
            await api.approveSubmission(participantId, {
                approval_status: status,
                feedback: feedback,
                approved_by: trainerName
            });

            Components.showMessage(messageEl, 'Approval saved', 'success');
            await this.loadParticipantDetail(participantId);
        } catch (error) {
            console.error('Approval save error:', error);
            Components.showMessage(messageEl, `Error: ${error.message}`, 'error', 5000);
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
                alert('Please select a file');
                return;
            }

            if (!cohort) {
                alert('Please enter a cohort name');
                return;
            }

            await this.performImport(file, cohort);
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        const isValid = file.name.endsWith('.json') || file.name.endsWith('.zip');
        if (!isValid) {
            alert('Please select a .json or .zip file');
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
                if (msgEl) msgEl.textContent = `Success: ${result.message}`;
                if (detailEl) detailEl.textContent = `Imported: ${result.imported} CVs`;

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
                if (confirm('Clear all cached data?')) {
                    localStorage.clear();
                    alert('Cache cleared. Reload the page to refresh.');
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
