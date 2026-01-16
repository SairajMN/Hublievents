/**
 * Admin API Client
 * Handles communication with backend admin APIs
 */

class AdminAPI {
    constructor() {
        this.baseURL = window.location.hostname === 'localhost'
            ? 'http://localhost:8000/api/v1'
            : 'https://api.hublievents.com/api/v1';
        this.timeout = 10000; // 10 seconds
        this.authToken = null;
    }

    /**
     * Set authentication token
     */
    setAuthToken(token) {
        this.authToken = token;
        if (token) {
            localStorage.setItem('admin_token', token);
        } else {
            localStorage.removeItem('admin_token');
        }
    }

    /**
     * Get authentication token
     */
    getAuthToken() {
        return this.authToken || localStorage.getItem('admin_token');
    }

    /**
     * Make authenticated request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add auth token if available
        const token = this.getAuthToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        config.signal = controller.signal;

        try {
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            let data;
            try {
                data = await response.json();
            } catch (e) {
                data = null;
            }

            return {
                ok: response.ok,
                status: response.status,
                data: data,
                message: data?.message || response.statusText
            };
        } catch (error) {
            console.error('API request failed:', error);
            return {
                ok: false,
                status: 0,
                data: null,
                message: error.message || 'Network error'
            };
        }
    }

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data = null) {
        const options = { method: 'POST' };
        if (data) {
            options.body = JSON.stringify(data);
        }
        return this.request(endpoint, options);
    }

    /**
     * PUT request
     */
    async put(endpoint, data = null) {
        const options = { method: 'PUT' };
        if (data) {
            options.body = JSON.stringify(data);
        }
        return this.request(endpoint, options);
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    /**
     * Log admin action
     */
    async logAction(action, targetId = null, metadata = {}) {
        const logData = {
            action: action,
            target_id: targetId,
            metadata: metadata,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
            ip_address: null // Will be set by backend
        };

        try {
            await this.post('/admin/logs', logData);
        } catch (error) {
            console.warn('Failed to log action:', error);
        }
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        const token = this.getAuthToken();
        if (!token) return false;

        try {
            // Basic JWT validation
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Date.now() / 1000;
            return payload.exp > currentTime;
        } catch (error) {
            this.setAuthToken(null);
            return false;
        }
    }
}

// Initialize global AdminAPI instance
window.AdminAPI = new AdminAPI();
