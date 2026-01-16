/**
 * Router.js - SPA-like Navigation Router
 * Handles client-side routing and page transitions
 */

class Router {
    constructor() {
        this.routes = new Map();
        this.currentRoute = null;
        this.transitioning = false;
    }

    init() {
        this.setupRoutes();
        this.bindEvents();
        this.handleInitialRoute();
        console.log('🧭 Router initialized');
    }

    setupRoutes() {
        // Define routes for the single-page application
        this.routes.set('/', { section: 'home', title: 'Hublievents - Luxury Event Decor' });
        this.routes.set('#home', { section: 'home', title: 'Hublievents - Luxury Event Decor' });
        this.routes.set('#designs', { section: 'designs', title: 'Signature Designs - Hublievents' });
        this.routes.set('#gallery', { section: 'gallery', title: 'Inspiration Gallery - Hublievents' });
        this.routes.set('#about', { section: 'about', title: 'About Us - Hublievents' });
        this.routes.set('#contact', { section: 'contact', title: 'Contact Us - Hublievents' });
    }

    bindEvents() {
        // Handle browser back/forward buttons
        window.addEventListener('popstate', this.handlePopState.bind(this));

        // Handle navigation link clicks
        document.addEventListener('click', this.handleNavigationClick.bind(this));

        // Handle keyboard navigation
        document.addEventListener('keydown', this.handleKeyboardNavigation.bind(this));
    }

    handleInitialRoute() {
        const hash = window.location.hash || '#home';
        this.navigateTo(hash, false); // Don't update history for initial load
    }

    handleNavigationClick(e) {
        const link = e.target.closest('.nav-link, a[href^="#"]');
        if (!link) return;

        e.preventDefault();
        const href = link.getAttribute('href');

        if (this.routes.has(href)) {
            this.navigateTo(href);
        }
    }

    handlePopState(e) {
        const hash = window.location.hash || '#home';
        this.navigateTo(hash, false); // Don't update history when coming from popstate
    }

    handleKeyboardNavigation(e) {
        // Handle keyboard navigation between sections
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            this.navigateWithKeyboard(e.key === 'ArrowDown' ? 'next' : 'previous');
        }

        // Handle home/end keys
        if (e.key === 'Home') {
            e.preventDefault();
            this.navigateTo('#home');
        }
        if (e.key === 'End') {
            e.preventDefault();
            this.navigateTo('#contact');
        }
    }

    navigateTo(route, updateHistory = true) {
        if (this.transitioning) return;

        const routeConfig = this.routes.get(route);
        if (!routeConfig) return;

        this.transitioning = true;

        // Update URL without triggering popstate
        if (updateHistory) {
            history.pushState({ route }, routeConfig.title, route);
        }

        // Update page title
        document.title = routeConfig.title;

        // Update active navigation state
        this.updateNavigationState(route);

        // Scroll to section
        this.scrollToSection(routeConfig.section);

        // Handle section-specific logic
        this.handleSectionChange(routeConfig.section);

        // Reset transition flag after animation
        setTimeout(() => {
            this.transitioning = false;
        }, 600);
    }

    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (!section) return;

        // Use smooth scroll behavior
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    updateNavigationState(activeRoute) {
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            const isActive = href === activeRoute;

            link.classList.toggle('active', isActive);
            link.setAttribute('aria-current', isActive ? 'page' : 'false');
        });
    }

    handleSectionChange(sectionId) {
        // Handle section-specific behaviors
        this.updateSectionFocus(sectionId);
        this.triggerSectionAnalytics(sectionId);
    }

    updateSectionFocus(sectionId) {
        // Update focus for accessibility
        const section = document.getElementById(sectionId);
        if (section) {
            // Set focus to section heading for screen readers
            const heading = section.querySelector('h1, h2');
            if (heading) {
                heading.setAttribute('tabindex', '-1');
                heading.focus();
            }
        }
    }

    triggerSectionAnalytics(sectionId) {
        // Trigger analytics events (placeholder for future implementation)
        if (window.gtag) {
            window.gtag('event', 'section_view', {
                section_id: sectionId,
                page_location: window.location.href
            });
        }
    }

    navigateWithKeyboard(direction) {
        const routeKeys = Array.from(this.routes.keys());
        const currentIndex = routeKeys.indexOf(window.location.hash || '#home');
        let newIndex;

        if (direction === 'next') {
            newIndex = Math.min(currentIndex + 1, routeKeys.length - 1);
        } else {
            newIndex = Math.max(currentIndex - 1, 0);
        }

        const newRoute = routeKeys[newIndex];
        this.navigateTo(newRoute);
    }

    // Utility method to get current route
    getCurrentRoute() {
        return this.currentRoute;
    }

    // Method to programmatically navigate
    goTo(route) {
        this.navigateTo(route);
    }

    // Method to go back in history
    goBack() {
        window.history.back();
    }

    // Method to go forward in history
    goForward() {
        window.history.forward();
    }

    // Method to add custom route
    addRoute(path, config) {
        this.routes.set(path, config);
    }

    // Method to remove route
    removeRoute(path) {
        this.routes.delete(path);
    }

    // Method to check if route exists
    hasRoute(path) {
        return this.routes.has(path);
    }

    // Method to get all routes
    getAllRoutes() {
        return Array.from(this.routes.keys());
    }

    // Method for programmatic navigation with transition
    navigateWithTransition(route, transitionType = 'fade') {
        // Add transition class to body
        document.body.classList.add(`transition-${transitionType}`);

        this.navigateTo(route);

        // Remove transition class after animation
        setTimeout(() => {
            document.body.classList.remove(`transition-${transitionType}`);
        }, 600);
    }

    // Method to handle mobile menu navigation
    handleMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-menu-toggle');
        const navMenu = document.querySelector('.nav-menu');

        if (mobileMenu && navMenu) {
            const isExpanded = mobileMenu.getAttribute('aria-expanded') === 'true';

            mobileMenu.setAttribute('aria-expanded', !isExpanded);
            navMenu.classList.toggle('open', !isExpanded);
            document.body.classList.toggle('mobile-menu-open', !isExpanded);
        }
    }
}

// Handle mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            if (window.Hublievents && window.Hublievents.app && window.Hublievents.app.router) {
                window.Hublievents.app.router.handleMobileMenu();
            }
        });
    }
});
