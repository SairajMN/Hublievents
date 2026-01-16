/**
 * Admin Router
 * Handles page navigation and content loading for the admin dashboard
 */

class AdminRouter {
    constructor() {
        this.app = null;
        this.currentPage = null;
        this.pages = {
            'dashboard': 'pages/dashboard.html',
            'enquiries': 'pages/enquiries.html',
            'designs': 'pages/designs.html',
            'gallery': 'pages/gallery.html',
            'users': 'pages/users.html',
            'settings': 'pages/settings.html'
        };
    }

    /**
     * Initialize router with app reference
     */
    init(app) {
        this.app = app;
    }

    /**
     * Load a page by name
     */
    async loadPage(pageName) {
        if (!this.pages[pageName]) {
            console.error(`Page '${pageName}' not found`);
            this.loadPage('dashboard');
            return;
        }

        try {
            // Show loading state
            this.showPageLoading(true);

            // Load page content
            const response = await fetch(this.pages[pageName]);
            if (!response.ok) {
                throw new Error(`Failed to load page: ${response.status}`);
            }

            const html = await response.text();

            // Update main content
            const mainContent = document.getElementById('main-content');
            if (mainContent) {
                mainContent.innerHTML = html;
            }

            // Update current page
            this.currentPage = pageName;

            // Initialize page-specific functionality
            await this.initPage(pageName);

        } catch (error) {
            console.error('Error loading page:', error);
            this.showPageError('Failed to load page content');
        } finally {
            this.showPageLoading(false);
        }
    }

    /**
     * Initialize page-specific functionality
     */
    async initPage(pageName) {
        switch (pageName) {
            case 'dashboard':
                await this.initDashboard();
                break;
            case 'enquiries':
                await this.initEnquiries();
                break;
            case 'designs':
                await this.initDesigns();
                break;
            case 'gallery':
                await this.initGallery();
                break;
            case 'users':
                await this.initUsers();
                break;
            case 'settings':
                await this.initSettings();
                break;
            default:
                console.warn(`No initialization function for page: ${pageName}`);
        }
    }

    /**
     * Initialize dashboard page
     */
    async initDashboard() {
        try {
            // Load dashboard statistics
            await this.loadDashboardStats();

            // Initialize charts
            this.initDashboardCharts();

            // Load recent activity
            await this.loadRecentActivity();

            // Load pending items
            await this.loadPendingItems();

        } catch (error) {
            console.error('Error initializing dashboard:', error);
        }
    }

    /**
     * Initialize enquiries page
     */
    async initEnquiries() {
        // Initialize filters
        this.initEnquiryFilters();

        // Load enquiries
        await this.loadEnquiries();

        // Initialize modals
        this.initEnquiryModals();
    }

    /**
     * Initialize designs page
     */
    async initDesigns() {
        // Initialize view toggle
        this.initDesignViewToggle();

        // Initialize filters
        this.initDesignFilters();

        // Load designs
        await this.loadDesigns();

        // Initialize modals
        this.initDesignModals();
    }

    /**
     * Initialize gallery page
     */
    async initGallery() {
        // Initialize filters
        this.initGalleryFilters();

        // Initialize bulk actions
        this.initGalleryBulkActions();

        // Load gallery images
        await this.loadGallery();

        // Initialize upload functionality
        this.initGalleryUpload();

        // Initialize modals
        this.initGalleryModals();
    }

    /**
     * Initialize users page
     */
    async initUsers() {
        // Initialize filters
        this.initUserFilters();

        // Load users
        await this.loadUsers();

        // Initialize modals
        this.initUserModals();
    }

    /**
     * Initialize settings page
     */
    async initSettings() {
        // Load current settings
        await this.loadSettings();

        // Initialize form handlers
        this.initSettingsForms();

        // Initialize maintenance actions
        this.initMaintenanceActions();
    }

    /**
     * Load dashboard statistics
     */
    async loadDashboardStats() {
        try {
            const response = await window.AdminAPI.get('/admin/stats');
            if (response.ok) {
                const stats = response.data;

                // Update stat cards
                this.updateStatCard('total-enquiries', stats.total_enquiries || 0);
                this.updateStatCard('active-designs', stats.total_designs || 0);
                this.updateStatCard('total-users', stats.total_users || 0);
                this.updateStatCard('monthly-revenue', `₹${stats.monthly_revenue || 0}`);

                // Update change indicators (mock data for now)
                this.updateStatChange('enquiries-change', '+12%', 'positive');
                this.updateStatChange('designs-change', '+8%', 'positive');
                this.updateStatChange('users-change', '+5%', 'positive');
                this.updateStatChange('revenue-change', '+15%', 'positive');
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    /**
     * Initialize dashboard charts
     */
    initDashboardCharts() {
        // Initialize enquiry trends chart
        const enquiryChartCanvas = document.getElementById('enquiry-chart');
        if (enquiryChartCanvas) {
            window.AdminCharts.createEnquiryChart(enquiryChartCanvas);
        }

        // Initialize design status chart
        const designChartCanvas = document.getElementById('design-chart');
        if (designChartCanvas) {
            window.AdminCharts.createDesignChart(designChartCanvas);
        }
    }

    /**
     * Load recent activity
     */
    async loadRecentActivity() {
        try {
            const response = await window.AdminAPI.get('/admin/activity?limit=10');
            if (response.ok) {
                this.renderRecentActivity(response.data.activities || []);
            }
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }

    /**
     * Load pending items
     */
    async loadPendingItems() {
        try {
            const response = await window.AdminAPI.get('/admin/pending');
            if (response.ok) {
                const pending = response.data;

                this.updatePendingItem('pending-enquiries', pending.enquiries || 0);
                this.updatePendingItem('pending-designs', pending.designs || 0);
                this.updatePendingItem('pending-gallery', pending.gallery || 0);
            }
        } catch (error) {
            console.error('Error loading pending items:', error);
        }
    }

    /**
     * Initialize enquiry filters
     */
    initEnquiryFilters() {
        // Search functionality
        const searchInput = document.getElementById('search-enquiries');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.loadEnquiries(), 300));
        }

        // Status filter
        const statusFilter = document.getElementById('status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.loadEnquiries());
        }

        // Priority filter
        const priorityFilter = document.getElementById('priority-filter');
        if (priorityFilter) {
            priorityFilter.addEventListener('change', () => this.loadEnquiries());
        }

        // Date filters
        const dateFrom = document.getElementById('date-from');
        const dateTo = document.getElementById('date-to');
        if (dateFrom) dateFrom.addEventListener('change', () => this.loadEnquiries());
        if (dateTo) dateTo.addEventListener('change', () => this.loadEnquiries());

        // Clear filters
        const clearBtn = document.getElementById('clear-filters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearEnquiryFilters());
        }

        // Sort functionality
        const sortSelect = document.getElementById('sort-by');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.loadEnquiries());
        }

        // Export functionality
        const exportBtn = document.getElementById('export-enquiries');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportEnquiries());
        }
    }

    /**
     * Load enquiries with current filters
     */
    async loadEnquiries(page = 1) {
        try {
            const filters = this.getEnquiryFilters();
            const params = new URLSearchParams({
                page: page,
                limit: 20,
                ...filters
            });

            const response = await window.AdminAPI.get(`/admin/enquiries?${params}`);
            if (response.ok) {
                this.renderEnquiries(response.data.enquiries || []);
                this.updatePagination(response.data.pagination);
            }
        } catch (error) {
            console.error('Error loading enquiries:', error);
        }
    }

    /**
     * Initialize design view toggle
     */
    initDesignViewToggle() {
        const gridBtn = document.getElementById('grid-view');
        const listBtn = document.getElementById('list-view');

        if (gridBtn) {
            gridBtn.addEventListener('click', () => this.setDesignView('grid'));
        }

        if (listBtn) {
            listBtn.addEventListener('click', () => this.setDesignView('list'));
        }
    }

    /**
     * Initialize design filters
     */
    initDesignFilters() {
        // Similar to enquiry filters but for designs
        const searchInput = document.getElementById('search-designs');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.loadDesigns(), 300));
        }

        // Status and category filters
        const statusFilter = document.getElementById('status-filter');
        const categoryFilter = document.getElementById('category-filter');

        if (statusFilter) statusFilter.addEventListener('change', () => this.loadDesigns());
        if (categoryFilter) categoryFilter.addEventListener('change', () => this.loadDesigns());

        // Date filters
        const dateFrom = document.getElementById('date-from');
        const dateTo = document.getElementById('date-to');
        if (dateFrom) dateFrom.addEventListener('change', () => this.loadDesigns());
        if (dateTo) dateTo.addEventListener('change', () => this.loadDesigns());

        // Clear filters
        const clearBtn = document.getElementById('clear-filters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearDesignFilters());
        }
    }

    /**
     * Load designs with current filters
     */
    async loadDesigns(page = 1) {
        try {
            const filters = this.getDesignFilters();
            const params = new URLSearchParams({
                page: page,
                limit: 20,
                ...filters
            });

            const response = await window.AdminAPI.get(`/admin/designs?${params}`);
            if (response.ok) {
                this.renderDesigns(response.data.designs || []);
                this.updatePagination(response.data.pagination);
            }
        } catch (error) {
            console.error('Error loading designs:', error);
        }
    }

    /**
     * Initialize gallery filters
     */
    initGalleryFilters() {
        const searchInput = document.getElementById('search-gallery');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.loadGallery(), 300));
        }

        const statusFilter = document.getElementById('status-filter');
        const categoryFilter = document.getElementById('category-filter');

        if (statusFilter) statusFilter.addEventListener('change', () => this.loadGallery());
        if (categoryFilter) categoryFilter.addEventListener('change', () => this.loadGallery());

        const dateFrom = document.getElementById('date-from');
        const dateTo = document.getElementById('date-to');
        if (dateFrom) dateFrom.addEventListener('change', () => this.loadGallery());
        if (dateTo) dateTo.addEventListener('change', () => this.loadGallery());

        const clearBtn = document.getElementById('clear-filters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearGalleryFilters());
        }
    }

    /**
     * Initialize gallery bulk actions
     */
    initGalleryBulkActions() {
        // Select all functionality
        const selectAllBtn = document.getElementById('select-all');
        const clearSelectionBtn = document.getElementById('clear-selection');

        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => this.selectAllGalleryItems());
        }

        if (clearSelectionBtn) {
            clearSelectionBtn.addEventListener('click', () => this.clearGallerySelection());
        }

        // Bulk action buttons
        const bulkApprove = document.getElementById('bulk-approve');
        const bulkReject = document.getElementById('bulk-reject');
        const bulkDelete = document.getElementById('bulk-delete');

        if (bulkApprove) bulkApprove.addEventListener('click', () => this.bulkGalleryAction('approve'));
        if (bulkReject) bulkReject.addEventListener('click', () => this.bulkGalleryAction('reject'));
        if (bulkDelete) bulkDelete.addEventListener('click', () => this.bulkGalleryAction('delete'));
    }

    /**
     * Load gallery images
     */
    async loadGallery(page = 1) {
        try {
            const filters = this.getGalleryFilters();
            const params = new URLSearchParams({
                page: page,
                limit: 20,
                ...filters
            });

            const response = await window.AdminAPI.get(`/admin/gallery?${params}`);
            if (response.ok) {
                this.renderGallery(response.data.images || []);
                this.updatePagination(response.data.pagination);
            }
        } catch (error) {
            console.error('Error loading gallery:', error);
        }
    }

    /**
     * Initialize user filters
     */
    initUserFilters() {
        const searchInput = document.getElementById('search-users');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.loadUsers(), 300));
        }

        const roleFilter = document.getElementById('role-filter');
        const statusFilter = document.getElementById('status-filter');

        if (roleFilter) roleFilter.addEventListener('change', () => this.loadUsers());
        if (statusFilter) statusFilter.addEventListener('change', () => this.loadUsers());

        const dateFrom = document.getElementById('date-from');
        const dateTo = document.getElementById('date-to');
        if (dateFrom) dateFrom.addEventListener('change', () => this.loadUsers());
        if (dateTo) dateTo.addEventListener('change', () => this.loadUsers());

        const clearBtn = document.getElementById('clear-filters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearUserFilters());
        }

        const sortSelect = document.getElementById('sort-by');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.loadUsers());
        }
    }

    /**
     * Load users
     */
    async loadUsers(page = 1) {
        try {
            const filters = this.getUserFilters();
            const params = new URLSearchParams({
                page: page,
                limit: 20,
                ...filters
            });

            const response = await window.AdminAPI.get(`/admin/users?${params}`);
            if (response.ok) {
                this.renderUsers(response.data.users || []);
                this.updatePagination(response.data.pagination);
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    /**
     * Load settings
     */
    async loadSettings() {
        try {
            const response = await window.AdminAPI.get('/admin/settings');
            if (response.ok) {
                this.populateSettingsForm(response.data.settings);
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    /**
     * Initialize settings forms
     */
    initSettingsForms() {
        // Business info form
        const businessForm = document.getElementById('business-info-form');
        if (businessForm) {
            businessForm.addEventListener('submit', (e) => this.saveBusinessSettings(e));
        }

        // Other settings forms would be initialized here
        // For brevity, implementing only business settings in this example
    }

    /**
     * Initialize maintenance actions
     */
    initMaintenanceActions() {
        const backupBtn = document.getElementById('create-backup');
        const cacheBtn = document.getElementById('clear-cache');
        const logsBtn = document.getElementById('cleanup-logs');
        const healthBtn = document.getElementById('health-check');

        if (backupBtn) backupBtn.addEventListener('click', () => this.createBackup());
        if (cacheBtn) cacheBtn.addEventListener('click', () => this.clearCache());
        if (logsBtn) logsBtn.addEventListener('click', () => this.cleanupLogs());
        if (healthBtn) healthBtn.addEventListener('click', () => this.runHealthCheck());
    }

    /**
     * Utility: Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Show page loading state
     */
    showPageLoading(loading) {
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            if (loading) {
                mainContent.style.opacity = '0.6';
                mainContent.style.pointerEvents = 'none';
            } else {
                mainContent.style.opacity = '1';
                mainContent.style.pointerEvents = 'auto';
            }
        }
    }

    /**
     * Show page error
     */
    showPageError(message) {
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="error-state">
                    <h2>Error Loading Page</h2>
                    <p>${message}</p>
                    <button onclick="window.AdminRouter.loadPage(window.AdminRouter.currentPage)" class="btn btn-primary">
                        Try Again
                    </button>
                </div>
            `;
        }
    }

    // Placeholder methods for rendering - would be implemented based on actual data structure
    renderRecentActivity(activities) { /* Implementation */ }
    renderEnquiries(enquiries) { /* Implementation */ }
    renderDesigns(designs) { /* Implementation */ }
    renderGallery(images) { /* Implementation */ }
    renderUsers(users) { /* Implementation */ }
    updatePagination(pagination) { /* Implementation */ }
    updateStatCard(id, value) { /* Implementation */ }
    updateStatChange(id, change, type) { /* Implementation */ }
    updatePendingItem(id, count) { /* Implementation */ }

    // Filter and form methods
    getEnquiryFilters() { return {}; }
    getDesignFilters() { return {}; }
    getGalleryFilters() { return {}; }
    getUserFilters() { return {}; }
    clearEnquiryFilters() { /* Implementation */ }
    clearDesignFilters() { /* Implementation */ }
    clearGalleryFilters() { /* Implementation */ }
    clearUserFilters() { /* Implementation */ }

    // Modal initialization methods
    initEnquiryModals() { /* Implementation */ }
    initDesignModals() { /* Implementation */ }
    initGalleryModals() { /* Implementation */ }
    initUserModals() { /* Implementation */ }

    // Other utility methods
    setDesignView(view) { /* Implementation */ }
    initGalleryUpload() { /* Implementation */ }
    selectAllGalleryItems() { /* Implementation */ }
    clearGallerySelection() { /* Implementation */ }
    bulkGalleryAction(action) { /* Implementation */ }
    populateSettingsForm(settings) { /* Implementation */ }
    saveBusinessSettings(event) { /* Implementation */ }
    createBackup() { /* Implementation */ }
    clearCache() { /* Implementation */ }
    cleanupLogs() { /* Implementation */ }
    runHealthCheck() { /* Implementation */ }
    exportEnquiries() { /* Implementation */ }
}

// Initialize router
window.AdminRouter = new AdminRouter();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminRouter;
}
