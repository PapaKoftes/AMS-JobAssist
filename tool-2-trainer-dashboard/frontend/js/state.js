/**
 * State Management - Handles app-wide state with localStorage persistence
 *
 * Persists:
 * - Trainer name
 * - Current filter selections (cohort, status, search)
 * - API key (for authenticated deployments)
 */

class AppState {
    constructor() {
        this.currentUser = {
            name: localStorage.getItem('trainerName') || 'Trainer'
        };

        this.participants = [];
        this.currentParticipant = null;
        this.selectedParticipants = new Set();
        this.cohorts = new Set();

        this.filters = {
            cohort: '',
            status: '',
            search: ''
        };

        this.loading = {
            participants: false,
            detail: false,
            approval: false,
            import: false,
            export: false
        };

        this.loadFromStorage();
    }

    /**
     * Load settings from localStorage
     */
    loadFromStorage() {
        try {
            const saved = localStorage.getItem('appState');
            if (saved) {
                const state = JSON.parse(saved);
                if (state.filters) this.filters = { ...this.filters, ...state.filters };
                if (state.currentUser) this.currentUser = { ...this.currentUser, ...state.currentUser };
            }
        } catch (e) {
            console.warn('Failed to load saved state:', e);
            // Corrupted storage — clear it
            localStorage.removeItem('appState');
        }
    }

    /**
     * Save settings to localStorage
     */
    saveToStorage() {
        try {
            localStorage.setItem('appState', JSON.stringify({
                filters: this.filters,
                currentUser: this.currentUser
            }));
        } catch (e) {
            console.warn('Failed to save state:', e);
        }
    }

    /**
     * Set participants list
     */
    setParticipants(participants) {
        if (!Array.isArray(participants)) {
            console.warn('setParticipants: expected array, got', typeof participants);
            this.participants = [];
            return;
        }
        this.participants = participants;
        this.cohorts = new Set(
            participants
                .map(p => p.cohort_id)
                .filter(Boolean)
        );
    }

    /**
     * Set current participant for detail view
     */
    setCurrentParticipant(participant) {
        this.currentParticipant = participant;
    }

    /**
     * Toggle participant selection
     */
    toggleParticipantSelection(participantId) {
        if (this.selectedParticipants.has(participantId)) {
            this.selectedParticipants.delete(participantId);
        } else {
            this.selectedParticipants.add(participantId);
        }
    }

    /**
     * Select all participants
     */
    selectAllParticipants(participants) {
        if (!Array.isArray(participants)) return;
        participants.forEach(p => {
            if (p && p.participant_id) {
                this.selectedParticipants.add(p.participant_id);
            }
        });
    }

    /**
     * Clear all selections
     */
    clearSelections() {
        this.selectedParticipants.clear();
    }

    /**
     * Get filtered participants based on current filters
     */
    getFilteredParticipants() {
        let filtered = this.participants;

        if (this.filters.cohort) {
            filtered = filtered.filter(p => p.cohort_id === this.filters.cohort);
        }

        if (this.filters.status) {
            filtered = filtered.filter(p => p.status === this.filters.status);
        }

        if (this.filters.search) {
            const search = this.filters.search.toLowerCase();
            filtered = filtered.filter(p =>
                (p.name && p.name.toLowerCase().includes(search)) ||
                (p.email && p.email.toLowerCase().includes(search)) ||
                (p.user_id && p.user_id.toLowerCase().includes(search))
            );
        }

        return filtered;
    }

    /**
     * Set loading state
     */
    setLoading(key, value) {
        if (key in this.loading) {
            this.loading[key] = value;
        }
    }

    /**
     * Set filter and persist
     */
    setFilter(key, value) {
        if (key in this.filters) {
            this.filters[key] = value;
            this.saveToStorage();
        }
    }

    /**
     * Update trainer name and persist
     */
    setTrainerName(name) {
        if (!name || typeof name !== 'string') return;
        name = name.trim().substring(0, 255);
        this.currentUser.name = name;
        localStorage.setItem('trainerName', name);
        this.saveToStorage();
    }
}

// Global state instance
const appState = new AppState();
