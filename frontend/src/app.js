/**
 * App.js - Main Application Entry Point
 * Initializes the application and coordinates all modules
 */

class App {
    constructor() {
        this.init();
    }

    init() {
        // Initialize all modules when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeModules();
            this.bindEvents();
            this.startApplication();
        });
    }

    initializeModules() {
        // Initialize core modules
        this.animations = new AnimationEngine();
        this.scroll = new ScrollSystem();
        this.router = new Router();
        this.state = new StateManager();
        this.api = new APIClient();
    }

    bindEvents() {
        // Global event listeners
        window.addEventListener('resize', this.handleResize.bind(this));
        window.addEventListener('scroll', this.handleScroll.bind(this));

        // Performance monitoring
        if ('PerformanceObserver' in window) {
            this.setupPerformanceMonitoring();
        }
    }

    startApplication() {
        // Start all systems
        this.animations.init();
        this.scroll.init();
        this.router.init();
        this.state.init();

        // Initial page setup
        this.handleInitialLoad();

        console.log('🚀 Hublievents application started successfully');
    }

    handleInitialLoad() {
        // Handle initial page load animations
        setTimeout(() => {
            document.body.classList.add('loaded');

            // Trigger initial animations
            this.animations.playInitialSequence();
        }, 100);
    }

    handleResize() {
        // Debounced resize handler
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            this.scroll.updateViewport();
            this.animations.updateViewport();
        }, 250);
    }

    handleScroll() {
        // Throttled scroll handler for performance
        if (!this.scrollThrottled) {
            requestAnimationFrame(() => {
                this.scroll.handleScroll();
                this.scrollThrottled = false;
            });
            this.scrollThrottled = true;
        }
    }

    setupPerformanceMonitoring() {
        // Monitor Core Web Vitals
        try {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'measure') {
                        console.log(`${entry.name}: ${entry.duration}ms`);
                    }
                }
            });

            observer.observe({ entryTypes: ['measure'] });
        } catch (e) {
            console.warn('Performance monitoring not fully supported');
        }
    }
}

// Error handling
window.addEventListener('error', (e) => {
    console.error('Application Error:', e.error);
    // Could send to error reporting service
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled Promise Rejection:', e.reason);
    // Could send to error reporting service
});

// Initialize the application
const app = new App();

// Export for debugging
window.Hublievents = { app };
