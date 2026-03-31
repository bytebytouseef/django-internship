window.appUtils = {
    escapeHtml(value) {
        return String(value ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    },

    formatDate(value, options = {}) {
        if (!value) return 'Not set';
        const date = new Date(value);
        return Number.isNaN(date.getTime())
            ? 'Invalid date'
            : date.toLocaleDateString([], options);
    },

    formatDateTime(value) {
        if (!value) return 'Not available';
        const date = new Date(value);
        return Number.isNaN(date.getTime())
            ? 'Invalid date'
            : date.toLocaleString([], {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit'
            });
    },

    truncate(value, length = 80) {
        const text = String(value ?? '');
        return text.length > length ? `${text.slice(0, length).trim()}...` : text;
    },

    statusTone(status) {
        const tones = {
            pending: 'neutral',
            submitted: 'info',
            reviewed: 'warning',
            approved: 'success',
            rejected: 'danger',
            pending_review: 'warning'
        };
        return tones[status] || 'neutral';
    },

    statusLabel(status) {
        return String(status ?? 'unknown').replace(/_/g, ' ');
    }
};

/**
 * Main Router
 * Handles client-side routing and component mounting
 */

const app = {
    init() {
        window.addEventListener('hashchange', () => this.route());
        this.route();
    },

    route() {
        const hash = window.location.hash.slice(1) || 'login';
        
        if (!auth.isAuthenticated() && hash !== 'login') {
            window.location.hash = '#login';
            return;
        }

        if (auth.isAuthenticated() && hash === 'login') {
            window.location.hash = '#dashboard';
            return;
        }

        switch (hash) {
            case 'login':
                loginComponent.mount();
                break;
            case 'dashboard':
            default:
                dashboardComponent.mount();
                break;
        }
    }
};

// Start the app
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
