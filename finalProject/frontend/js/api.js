/**
 * Central API Client
 * Handles all API calls with automatic token refresh on 401
 */

const api = {
    BASE_URL: 'http://localhost:8000/api',
    MAX_RETRIES: 1,

    /**
     * Make an API call
     */
    async call(endpoint, options = {}) {
        try {
            const url = `${this.BASE_URL}${endpoint}`;
            const method = options.method || 'GET';
            const headers = {
                'Content-Type': 'application/json',
                ...auth.getAuthHeader(),
                ...options.headers
            };

            const response = await fetch(url, {
                method,
                headers,
                credentials: 'include',
                body: options.body ? JSON.stringify(options.body) : undefined
            });

            // Handle 401 - try refreshing token
            if (response.status === 401 && !options.retried) {
                const refreshed = await auth.refreshAccessToken();
                if (refreshed) {
                    // Retry request with new token
                    return this.call(endpoint, { ...options, retried: true });
                } else {
                    // Refresh failed, clear and redirect to login
                    auth.clearTokens();
                    window.location.hash = '#login';
                    throw new Error('Session expired. Please login again.');
                }
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API error [${endpoint}]:`, error.message);
            throw error;
        }
    },

    // Convenience methods
    get(endpoint, options = {}) {
        return this.call(endpoint, { ...options, method: 'GET' });
    },

    post(endpoint, body, options = {}) {
        return this.call(endpoint, { ...options, method: 'POST', body });
    },

    put(endpoint, body, options = {}) {
        return this.call(endpoint, { ...options, method: 'PUT', body });
    },

    patch(endpoint, body, options = {}) {
        return this.call(endpoint, { ...options, method: 'PATCH', body });
    },

    delete(endpoint, options = {}) {
        return this.call(endpoint, { ...options, method: 'DELETE' });
    }
};
