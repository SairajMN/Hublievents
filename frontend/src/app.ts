/**
 * App.ts - Main Application Entry Point
 * Initializes the application and coordinates all modules
 */

interface AppModules {
    animations: any;
    scroll: any;
    router: any;
    state: any;
    api: any;
}

class App {
    private animations: any;
    private scroll: any;
    private router: any;
    private state: any;
    private api: any;
    private resizeTimeout: number | NodeJS.Timeout | undefined;
    private scrollThrottled: boolean = false;

    constructor() {
        this.init();
    }

    private init(): void {
        // Initialize all modules when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeModules();
            this.bindEvents();
            this.startApplication();
        });
    }

    private initializeModules(): void {
        // Initialize core modules
        this.animations = new (window as any).AnimationEngine();
        this.scroll = new (window as any).ScrollSystem();
        this.router = new (window as any).Router();
        this.state = new (window as any).StateManager();
        this.api = new (window as any).APIClient();
    }

    private bindEvents(): void {
        // Global event listeners
        window.addEventListener('resize', this.handleResize.bind(this));
        window.addEventListener('scroll', this.handleScroll.bind(this));

        // Performance monitoring
        if ('PerformanceObserver' in window) {
            this.setupPerformanceMonitoring();
        }
    }

    private startApplication(): void {
        // Start all systems
        this.animations.init();
        this.scroll.init();
        this.router.init();
        this.state.init();

        // Initial page setup
        this.handleInitialLoad();

        console.log('🚀 Hublievents application started successfully');
    }

    private handleInitialLoad(): void {
        // Handle initial page load animations
        setTimeout(() => {
            document.body?.classList.add('loaded');

            // Trigger initial animations
            this.animations.playInitialSequence();
        }, 100);
    }

    private handleResize(): void {
        // Debounced resize handler
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            this.scroll.updateViewport();
            this.animations.updateViewport();
        }, 250);
    }

    private handleScroll(): void {
        // Throttled scroll handler for performance
        if (!this.scrollThrottled) {
            requestAnimationFrame(() => {
                this.scroll.handleScroll();
                this.scrollThrottled = false;
            });
            this.scrollThrottled = true;
        }
    }

    private setupPerformanceMonitoring(): void {
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
window.addEventListener('error', (e: ErrorEvent) => {
    console.error('Application Error:', e.error);
    // Could send to error reporting service
});

window.addEventListener('unhandledrejection', (e: PromiseRejectionEvent) => {
    console.error('Unhandled Promise Rejection:', e.reason);
    // Could send to error reporting service
});

// Initialize the application
const app = new App();

// Export for debugging
(window as any).Hublievents = { app };

// Export for ES modules
export default App;
