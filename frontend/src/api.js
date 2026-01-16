/**
 * API.js - API Client
 * Handles communication with backend APIs
 */

class APIClient {
    constructor() {
        this.baseURL = process.env.NODE_ENV === 'production'
            ? 'https://api.hublievents.com'
            : 'http://localhost:8000';
        this.timeout = 10000; // 10 seconds
        this.retries = 3;
    }

    init() {
        console.log('🔗 API client initialized');
    }

    // Core request method with error handling and retries
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

        let lastError;

        for (let attempt = 1; attempt <= this.retries; attempt++) {
            try {
                const response = await fetch(url, config);
                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                return data;
            } catch (error) {
                lastError = error;

                if (attempt === this.retries || error.name === 'AbortError') {
                    break;
                }

                // Exponential backoff
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
            }
        }

        throw lastError;
    }

    // Authentication methods
    async login(credentials) {
        try {
            const response = await this.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify(credentials)
            });

            if (response.token) {
                this.setAuthToken(response.token);
            }

            return response;
        } catch (error) {
            throw new Error('Login failed: ' + error.message);
        }
    }

    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' });
        } catch (error) {
            console.warn('Logout request failed:', error);
        } finally {
            this.clearAuthToken();
        }
    }

    // Enquiry/Contact methods
    async submitEnquiry(enquiryData) {
        return this.request('/enquiries', {
            method: 'POST',
            body: JSON.stringify(enquiryData)
        });
    }

    async getEnquiries(filters = {}) {
        const queryParams = new URLSearchParams(filters);
        return this.request(`/enquiries?${queryParams}`);
    }

    // Design methods
    async getDesigns(category = null) {
        const endpoint = category ? `/designs?category=${category}` : '/designs';
        return this.request(endpoint);
    }

    async getDesign(designId) {
        return this.request(`/designs/${designId}`);
    }

    async saveCustomDesign(designData) {
        return this.request('/designs', {
            method: 'POST',
            body: JSON.stringify(designData)
        });
    }

    // Gallery methods
    async getGalleryImages(filters = {}) {
        const queryParams = new URLSearchParams(filters);
        return this.request(`/gallery?${queryParams}`);
    }

    async uploadGalleryImage(formData) {
        return this.request('/gallery', {
            method: 'POST',
            body: formData,
            headers: {
                // Let browser set content-type for FormData
                ...Object.fromEntries(
                    Object.entries(this.request.headers || {}).filter(([key]) => key !== 'Content-Type')
                )
            }
        });
    }

    // Newsletter methods
    async subscribeNewsletter(email) {
        return this.request('/newsletter/subscribe', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    }

    // Admin methods (protected)
    async getAdminStats() {
        return this.request('/admin/stats');
    }

    async getAdminEnquiries() {
        return this.request('/admin/enquiries');
    }

    // Utility methods
    getAuthToken() {
        return localStorage.getItem('hublievents_token');
    }

    setAuthToken(token) {
        localStorage.setItem('hublievents_token', token);
    }

    clearAuthToken() {
        localStorage.removeItem('hublievents_token');
    }

    isAuthenticated() {
        const token = this.getAuthToken();
        if (!token) return false;

        try {
            // Basic JWT validation (you might want more sophisticated validation)
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Date.now() / 1000;

            return payload.exp > currentTime;
        } catch (error) {
            this.clearAuthToken();
            return false;
        }
    }

    // Mock data for development/demo purposes
    async getMockData(endpoint) {
        const mockData = {
            '/designs': [
                { id: 1, title: 'Royal Wedding Collection', category: 'wedding', price: 50000 },
                { id: 2, title: 'Corporate Excellence', category: 'corporate', price: 75000 },
                { id: 3, title: 'Garden Celebrations', category: 'outdoor', price: 40000 }
            ],
            '/gallery': [
                { id: 1, url: 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=400&h=300&fit=crop&crop=center', title: 'Elegant Reception' },
                { id: 2, url: 'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=400&h=300&fit=crop&crop=center', title: 'Grand Setup' },
                { id: 3, url: 'https://images.unsplash.com/photo-1464047736614-af63643285bf?w=400&h=300&fit=crop&crop=center', title: 'Garden Party' }
            ]
        };

        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(mockData[endpoint] || []);
            }, 500); // Simulate network delay
        });
    }

    // Development mode wrapper
    async makeRequest(endpoint, options = {}) {
        if (process.env.NODE_ENV === 'development' && !this.baseURL.includes('localhost')) {
            // Use mock data in development
            return this.getMockData(endpoint);
        }

        return this.request(endpoint, options);
    }
}

// Global error handler for API calls
window.addEventListener('unhandledrejection', (event) => {
    if (event.reason && event.reason.message && event.reason.message.includes('HTTP')) {
        // Handle API errors globally
        console.error('API Error:', event.reason);

        // Could show user-friendly error message
        if (window.Hublievents && window.Hublievents.app && window.Hublievents.app.state) {
            window.Hublievents.app.state.addNotification(
                'Something went wrong. Please try again later.',
                'error'
            );
        }
    }
});
