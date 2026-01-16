/**
 * Admin Dashboard Application
 * Main application entry point for Hublievents Admin Dashboard
 */

class AdminApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.currentUser = null;
        this.isLoggedIn = false;
        this.sidebarCollapsed = false;

        this.init();
    }

    /**
     * Initialize the admin application
     */
    async init() {
        try {
            // Show loading screen
            this.showLoadingScreen();

            // Initialize components
            await this.initAuth();
            this.initRouter();
            this.initEventListeners();
            this.initState();

            // Check authentication status
            await this.checkAuthStatus();

        } catch (error) {
            console.error('Admin app initialization failed:', error);
            this.showError('Failed to initialize admin dashboard');
        }
    }

    /**
     * Initialize authentication
     */
    async initAuth() {
        // Check for existing token
        const token = localStorage.getItem('admin_token');
        if (token) {
            // Set token in API
            window.AdminAPI.setAuthToken(token);
            this.isLoggedIn = true;
        }
    }

    /**
     * Initialize router
     */
    initRouter() {
        window.AdminRouter.init(this);
    }

    /**
     * Initialize event listeners
     */
    initEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Logout button
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Login form
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Handle browser back/forward
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.page) {
                this.navigateToPage(e.state.page, false);
            }
        });

        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));

        // Handle window resize for responsive sidebar
        window.addEventListener('resize', () => this.handleResize());
    }

    /**
     * Initialize application state
     */
    initState() {
        // Initialize AdminState
        if (window.AdminState) {
            window.AdminState.init();
        }

        // Load sidebar collapsed state
        const collapsed = localStorage.getItem('sidebar_collapsed') === 'true';
        this.sidebarCollapsed = collapsed;
        this.updateSidebarState();

        // Load last visited page
        const lastPage = localStorage.getItem('last_page') || 'dashboard';
        if (this.isLoggedIn && window.location.hash) {
            const hashPage = window.location.hash.substring(1);
            this.navigateToPage(hashPage, false);
        } else if (this.isLoggedIn) {
            this.navigateToPage(lastPage, false);
        }
    }

    /**
     * Check authentication status
     */
    async checkAuthStatus() {
        if (!this.isLoggedIn) {
            this.showLoginScreen();
            return;
        }

        try {
            // Verify token with backend
            const response = await window.AdminAPI.get('/auth/verify');
            if (response.ok) {
                this.currentUser = response.data.user;
                this.showAdminInterface();
                this.updateUserInfo();
            } else {
                this.logout();
            }
        } catch (error) {
            console.error('Auth verification failed:', error);
            this.logout();
        }
    }

    /**
     * Handle login form submission
     */
    async handleLogin(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const credentials = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            this.showLoginLoading(true);

            const response = await window.AdminAPI.post('/auth/login', credentials);

            if (response.ok) {
                // Store token
                localStorage.setItem('admin_token', response.data.token);
                window.AdminAPI.setAuthToken(response.data.token);

                this.currentUser = response.data.user;
                this.isLoggedIn = true;

                this.showAdminInterface();
                this.updateUserInfo();
                this.navigateToPage('dashboard');

                // Log successful login
                window.AdminAPI.logAction('login_attempt', null, {
                    success: true,
                    user_id: this.currentUser.id
                });

            } else {
                this.showLoginError(response.message || 'Login failed');
            }

        } catch (error) {
            console.error('Login error:', error);
            this.showLoginError('Login failed. Please try again.');
        } finally {
            this.showLoginLoading(false);
        }
    }

    /**
     * Logout user
     */
    logout() {
        // Clear stored data
        localStorage.removeItem('admin_token');
        localStorage.removeItem('last_page');

        // Clear API token
        window.AdminAPI.setAuthToken(null);

        // Reset state
        this.currentUser = null;
        this.isLoggedIn = false;
        this.currentPage = 'dashboard';

        // Show login screen
        this.showLoginScreen();

        // Clear URL hash
        window.history.replaceState(null, null, window.location.pathname);
    }

    /**
     * Navigate to a specific page
     */
    navigateToPage(page, updateHistory = true) {
        if (!this.isLoggedIn) {
            this.showLoginScreen();
            return;
        }

        // Update current page
        this.currentPage = page;

        // Update navigation
        this.updateNavigation(page);

        // Load page content
        window.AdminRouter.loadPage(page);

        // Update URL
        if (updateHistory) {
            const url = `#${page}`;
            window.history.pushState({ page }, page, url);
            localStorage.setItem('last_page', page);
        }
    }

    /**
     * Update navigation active state
     */
    updateNavigation(activePage) {
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to current page link
        const activeLink = document.querySelector(`[data-page="${activePage}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    /**
     * Toggle sidebar collapsed state
     */
    toggleSidebar() {
        this.sidebarCollapsed = !this.sidebarCollapsed;
        this.updateSidebarState();

        // Save state
        localStorage.setItem('sidebar_collapsed', this.sidebarCollapsed);
    }

    /**
     * Update sidebar visual state
     */
    updateSidebarState() {
        const sidebar = document.getElementById('sidebar');
        const header = document.getElementById('admin-header');
        const mainContent = document.getElementById('main-content');

        if (!sidebar || !header || !mainContent) return;

        if (this.sidebarCollapsed) {
            sidebar.classList.add('collapsed');
            header.classList.add('sidebar-collapsed');
        } else {
            sidebar.classList.remove('collapsed');
            header.classList.remove('sidebar-collapsed');
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboard(event) {
        // Ctrl/Cmd + B: Toggle sidebar
        if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
            event.preventDefault();
            this.toggleSidebar();
        }

        // Ctrl/Cmd + L: Logout
        if ((event.ctrlKey || event.metaKey) && event.key === 'l') {
            event.preventDefault();
            this.logout();
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Close mobile sidebar on resize if screen becomes larger
        if (window.innerWidth >= 768) {
            const sidebar = document.getElementById('sidebar');
            if (sidebar) {
                sidebar.classList.remove('open');
            }
        }
    }

    /**
     * Update user information in UI
     */
    updateUserInfo() {
        const userNameElement = document.getElementById('admin-name');
        if (userNameElement && this.currentUser) {
            userNameElement.textContent = this.currentUser.name || this.currentUser.email;
        }
    }

    /**
     * Show loading screen
     */
    showLoadingScreen() {
        this.showElement('loading-screen');
        this.hideElement('login-screen');
        this.hideElement('admin-interface');
    }

    /**
     * Show login screen
     */
    showLoginScreen() {
        this.hideElement('loading-screen');
        this.showElement('login-screen');
        this.hideElement('admin-interface');
    }

    /**
     * Show admin interface
     */
    showAdminInterface() {
        this.hideElement('loading-screen');
        this.hideElement('login-screen');
        this.showElement('admin-interface');
    }

    /**
     * Show login loading state
     */
    showLoginLoading(loading) {
        const submitBtn = document.querySelector('#login-form button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = loading;
            submitBtn.textContent = loading ? 'Logging in...' : 'Login';
        }
    }

    /**
     * Show login error
     */
    showLoginError(message) {
        const errorElement = document.getElementById('login-error');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error(message);
        // You could implement a toast notification system here
        alert(message); // Fallback
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        console.log(message);
        // You could implement a toast notification system here
    }

    /**
     * Utility: Show element
     */
    showElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('hidden');
        }
    }

    /**
     * Utility: Hide element
     */
    hideElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add('hidden');
        }
    }

    /**
     * Get current user
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * Check if user has permission
     */
    hasPermission(permission) {
        if (!this.currentUser) return false;

        // Super admin has all permissions
        if (this.currentUser.role === 'super_admin') return true;

        // Admin permissions
        if (this.currentUser.role === 'admin') {
            const adminPermissions = [
                'view_dashboard',
                'manage_enquiries',
                'manage_designs',
                'manage_gallery',
                'view_users',
                'manage_settings'
            ];
            return adminPermissions.includes(permission);
        }

        return false;
    }
}

// Initialize admin app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.AdminApp = new AdminApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminApp;
}
