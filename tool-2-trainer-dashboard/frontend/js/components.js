/**
 * Components - Reusable UI building blocks
 */

class Components {
    /**
     * Create a participant row for the table
     */
    static createParticipantRow(participant, isSelected) {
        const row = document.createElement('tr');
        row.dataset.participantId = participant.participant_id;

        const statusClass = `status-${participant.status}`;
        const lastUpdated = new Date(participant.last_updated_at).toLocaleDateString();
        // overall_quality is a 0–1 score — show as percent ("72 %"), matching Tool 1.
        // (Was rendered "0.7/10", which read like a catastrophic score to trainers.)
        const quality = Math.round((participant.latest_submission?.overall_quality || 0) * 100);

        // B3: Completion badge
        const completionBadge = participant.completed_at
            ? '<span class="badge-done">✓ Fertig</span>'
            : '<span class="badge-inprogress">⏳</span>';

        row.innerHTML = `
            <td>
                <input type="checkbox" class="select-row" ${isSelected ? 'checked' : ''}>
            </td>
            <td><strong>${participant.name || 'Unbekannt'}</strong></td>
            <td>${participant.email || '—'}</td>
            <td><span class="status-badge ${statusClass}">${Components._statusLabel(participant.status)}</span>${completionBadge}</td>
            <td>${quality} %</td>
            <td>${lastUpdated}</td>
            <td>
                <button class="btn btn-small" data-action="view">Ansehen</button>
                <button class="btn btn-small" data-action="approve">Freigeben</button>
            </td>
        `;

        return row;
    }

    /**
     * Create a CV section for display
     */
    static createCVSection(question, answer, isOriginal = false, isEditable = false, sectionKey = '') {
        const section = document.createElement('div');
        section.className = 'cv-section';

        const answerClass = isOriginal ? 'cv-answer original' : 'cv-answer';
        const editableClass = isEditable && !isOriginal ? 'editable' : '';
        const keyAttr = sectionKey ? ` data-section-key="${sectionKey}"` : '';

        section.innerHTML = `
            <div class="cv-question">${question}</div>
            <div class="${answerClass} ${editableClass}" data-editable="${isEditable && !isOriginal}"${keyAttr}>
                ${answer || '(Keine Antwort)'}
            </div>
        `;

        return section;
    }

    /**
     * Create metric card
     */
    static createMetricCard(label, value, percentage = null) {
        const card = document.createElement('div');
        card.className = 'metric-card';

        let percentageHTML = '';
        if (percentage) {
            percentageHTML = `<div class="metric-percentage">${percentage}%</div>`;
        }

        card.innerHTML = `
            <div class="metric-label">${label}</div>
            <div class="metric-value">${value}</div>
            ${percentageHTML}
        `;

        return card;
    }

    /**
     * Create activity item
     */
    static createActivityItem(action, details, timestamp) {
        const item = document.createElement('div');
        item.className = 'activity-item';

        const time = new Date(timestamp).toLocaleString();

        item.innerHTML = `
            <div>${action}: ${details}</div>
            <div class="activity-time">${time}</div>
        `;

        return item;
    }

    /**
     * Show status message
     */
    static showMessage(element, message, type = 'success', duration = 3000) {
        element.textContent = message;
        element.className = `message ${type}`;
        element.style.display = 'block';

        if (duration > 0) {
            setTimeout(() => {
                element.style.display = 'none';
            }, duration);
        }
    }

    /**
     * Show loading spinner
     */
    static showLoading(container) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem;">Wird geladen…</p>';
    }

    /**
     * Show empty state
     */
    static showEmpty(container, message = 'Keine Daten vorhanden') {
        container.innerHTML = `<p class="empty-state">${message}</p>`;
    }

    /**
     * Format date for display
     */
    static formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('de-DE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    /**
     * Get status badge HTML
     */
    static getStatusBadge(status) {
        const label = Components._statusLabel(status);
        return `<span class="status-badge status-${status}">${label}</span>`;
    }

    static _statusLabel(status) {
        const labels = {
            pending:        'Ausstehend',
            approved:       'Freigegeben',
            rejected:       'Abgelehnt',
            needs_changes:  'Überarbeitung nötig',
        };
        return labels[status] || status;
    }
}
