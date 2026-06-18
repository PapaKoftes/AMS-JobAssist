/**
 * API Client - Wrapper around Trainer Dashboard API
 *
 * Features:
 * - Automatic error handling with user-friendly messages
 * - Request timeout (30s default)
 * - API key header injection (when configured)
 * - Structured error responses
 */

class TrainerAPI {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.timeoutMs = 30000;  // 30 second timeout
        this.apiKey = localStorage.getItem('apiKey') || '';
    }

    /**
     * Generic fetch wrapper with error handling and timeout
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Inject API key if configured
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        // Remove Content-Type for FormData (browser sets it with boundary)
        if (options.body instanceof FormData) {
            delete headers['Content-Type'];
        }

        const config = {
            ...options,
            headers,
        };

        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs);
        config.signal = controller.signal;

        try {
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            if (!response.ok) {
                let errorDetail;
                try {
                    const errorBody = await response.json();
                    errorDetail = errorBody.detail || errorBody.message || response.statusText;
                } catch {
                    errorDetail = response.statusText;
                }

                const error = new Error(errorDetail);
                error.status = response.status;
                error.endpoint = endpoint;
                throw error;
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
                const timeoutError = new Error(`Request timed out after ${this.timeoutMs / 1000}s`);
                timeoutError.status = 408;
                timeoutError.endpoint = endpoint;
                console.error(`API Timeout: ${endpoint}`);
                throw timeoutError;
            }

            console.error(`API Error [${error.status || 'NETWORK'}]: ${endpoint}`, error.message);
            throw error;
        }
    }

    /**
     * List all participants with optional filtering and pagination
     */
    async listParticipants(cohort_id = null, status = null, page = 1, pageSize = 50) {
        const params = new URLSearchParams();

        if (cohort_id) params.append('cohort_id', cohort_id);
        if (status) params.append('status', status);
        params.append('page', String(page));
        params.append('page_size', String(pageSize));

        let endpoint = `/participants?${params.toString()}`;
        return this.request(endpoint);
    }

    /**
     * Get a specific participant's details
     */
    async getParticipant(participantId) {
        if (!participantId || participantId <= 0) {
            throw new Error('Invalid participant ID');
        }
        return this.request(`/participants/${participantId}`);
    }

    /**
     * Approve or reject a participant's submission
     */
    async approveSubmission(participantId, approvalData) {
        if (!participantId || participantId <= 0) {
            throw new Error('Invalid participant ID');
        }
        if (!approvalData || !approvalData.approval_status) {
            throw new Error('Missing approval_status');
        }
        if (!approvalData.approved_by) {
            throw new Error('Missing approved_by');
        }

        return this.request(`/participants/${participantId}/approve`, {
            method: 'POST',
            body: JSON.stringify(approvalData)
        });
    }

    /**
     * Bulk approve/reject multiple participants
     */
    async bulkApprove(bulkData) {
        if (!bulkData || !bulkData.participant_ids || bulkData.participant_ids.length === 0) {
            throw new Error('No participants selected');
        }
        return this.request('/participants/bulk-approve', {
            method: 'POST',
            body: JSON.stringify(bulkData)
        });
    }

    /**
     * Get cohort metrics/summary
     */
    async getCohortMetrics(cohortId) {
        return this.request(`/cohorts/${encodeURIComponent(cohortId)}/metrics`);
    }

    /**
     * Import CVs (file upload)
     */
    async importCVs(file, cohortId) {
        if (!file) throw new Error('No file provided');
        if (!cohortId || !cohortId.trim()) throw new Error('No cohort ID provided');

        // Client-side file size check (50 MB)
        const maxSizeMB = 50;
        if (file.size > maxSizeMB * 1024 * 1024) {
            throw new Error(`File too large (${(file.size / (1024*1024)).toFixed(1)} MB). Max: ${maxSizeMB} MB`);
        }

        const formData = new FormData();
        formData.append('file', file);

        let endpoint = `/import-cvs?cohort_id=${encodeURIComponent(cohortId.trim())}`;

        return this.request(endpoint, {
            method: 'POST',
            headers: {},  // Let browser set Content-Type with boundary
            body: formData
        });
    }

    /**
     * Export multiple CVs
     */
    async bulkExport(exportData) {
        if (!exportData || !exportData.participant_ids || exportData.participant_ids.length === 0) {
            throw new Error('No participants selected for export');
        }
        return this.request('/bulk-export', {
            method: 'POST',
            body: JSON.stringify(exportData)
        });
    }

    /**
     * Persist a trainer's inline edit to a single CV section.
     * questionId must match a question_id in the participant's cv_data_json.
     */
    async updateCVSection(participantId, questionId, editedText, language = 'de') {
        if (!participantId || participantId <= 0) throw new Error('Invalid participant ID');
        if (!questionId) throw new Error('Missing question_id');
        return this.request(`/participants/${participantId}/cv-section`, {
            method: 'PATCH',
            body: JSON.stringify({ question_id: questionId, edited_text: editedText, language }),
        });
    }

    /**
     * Get approval + lock status for a participant's latest CV.
     */
    async getParticipantStatus(participantId) {
        if (!participantId || participantId <= 0) throw new Error('Invalid participant ID');
        return this.request(`/participants/${participantId}/status`);
    }

    /**
     * Lock a participant's CV (prevents further participant edits).
     */
    async lockParticipant(participantId, lockedBy) {
        if (!participantId || participantId <= 0) throw new Error('Invalid participant ID');
        if (!lockedBy) throw new Error('Missing locked_by');
        return this.request(`/participants/${participantId}/lock`, {
            method: 'POST',
            body: JSON.stringify({ locked_by: lockedBy })
        });
    }

    /**
     * Unlock a previously locked CV.
     */
    async unlockParticipant(participantId, lockedBy) {
        if (!participantId || participantId <= 0) throw new Error('Invalid participant ID');
        if (!lockedBy) throw new Error('Missing locked_by');
        return this.request(`/participants/${participantId}/unlock`, {
            method: 'POST',
            body: JSON.stringify({ locked_by: lockedBy })
        });
    }

    /**
     * Set API key for authentication
     */
    setApiKey(key) {
        this.apiKey = key;
        localStorage.setItem('apiKey', key);
    }
}

// Create global instance
const api = new TrainerAPI();
