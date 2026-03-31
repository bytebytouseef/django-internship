/**
 * Auth Management
 * Handles JWT tokens, login/logout, and token refresh
 */

const auth = {
    // Token storage keys
    ACCESS_TOKEN_KEY: 'access_token',
    REFRESH_TOKEN_KEY: 'refresh_token',
    API_BASE: 'http://localhost:8000/api',
    currentUser: null,

    /**
     * Set access token in localStorage
     */
    setAccessToken(token) {
        localStorage.setItem(this.ACCESS_TOKEN_KEY, token);
    },

    /**
     * Get access token from localStorage
     */
    getAccessToken() {
        return localStorage.getItem(this.ACCESS_TOKEN_KEY);
    },

    /**
     * Clear all tokens
     */
    clearTokens() {
        localStorage.removeItem(this.ACCESS_TOKEN_KEY);
        this.currentUser = null;
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getAccessToken();
    },

    /**
     * Get Authorization header
     */
    getAuthHeader() {
        const token = this.getAccessToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    },

    async parseErrorResponse(response, fallbackMessage) {
        try {
            const error = await response.json();
            return this.flattenError(error) || fallbackMessage;
        } catch (parseError) {
            return fallbackMessage;
        }
    },

    flattenError(error) {
        if (!error) return '';
        if (typeof error === 'string') return error;
        if (Array.isArray(error)) return error.map((item) => this.flattenError(item)).filter(Boolean).join(' ');
        if (typeof error === 'object') {
            if (typeof error.detail === 'string') return error.detail;
            return Object.entries(error)
                .map(([field, value]) => {
                    const message = this.flattenError(value);
                    return message ? `${field.replace(/_/g, ' ')}: ${message}` : '';
                })
                .filter(Boolean)
                .join(' ');
        }
        return '';
    },

    /**
     * Login user with email and password
     */
    async login(email, password) {
        try {
            const response = await fetch(`${this.API_BASE}/auth/login/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                throw new Error(await this.parseErrorResponse(response, 'Login failed'));
            }

            const data = await response.json();
            this.setAccessToken(data.access);
            this.currentUser = null;
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    /**
     * Register new user
     */
    async register(email, username, password, passwordConfirm, firstName, lastName) {
        try {
            const response = await fetch(`${this.API_BASE}/auth/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    username,
                    password,
                    password_confirm: passwordConfirm,
                    first_name: firstName,
                    last_name: lastName
                })
            });

            if (!response.ok) {
                throw new Error(await this.parseErrorResponse(response, 'Registration failed'));
            }

            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    /**
     * Refresh access token
     */
    async refreshAccessToken() {
        try {
            const response = await fetch(`${this.API_BASE}/auth/refresh/`, {
                method: 'POST',
                credentials: 'include'
            });

            if (!response.ok) {
                this.clearTokens();
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            this.setAccessToken(data.access);
            this.currentUser = null;
            return true;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    },

    /**
     * Logout user
     */
    async logout() {
        this.clearTokens();
        window.location.hash = '#login';
    },

    async fetchCurrentUser(force = false) {
        if (!this.isAuthenticated()) {
            this.currentUser = null;
            return null;
        }

        if (this.currentUser && !force) {
            return this.currentUser;
        }

        try {
            const response = await fetch(`${this.API_BASE}/auth/me/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeader()
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Unable to load current user');
            }

            this.currentUser = await response.json();
            return this.currentUser;
        } catch (error) {
            console.error('Current user error:', error);
            return null;
        }
    }
};
