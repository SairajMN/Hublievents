/**
 * Scroll.js - Scroll System
 * Handles scroll-based interactions, parallax effects, and scroll triggers
 */

class ScrollSystem {
    constructor() {
        this.navbar = null;
        this.navbarVisible = false;
        this.lastScrollY = 0;
        this.scrollDirection = 'down';
        this.parallaxElements = [];
        this.sections = [];
        this.currentSection = null;
    }

    init() {
        this.cacheElements();
        this.bindEvents();
        this.setupParallax();
        this.updateViewport();
        console.log('📜 Scroll system initialized');
    }

    cacheElements() {
        this.navbar = document.querySelector('.navbar');
        this.sections = Array.from(document.querySelectorAll('section[id]'));
    }

    bindEvents() {
        // Throttled scroll handler
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        });

        // Smooth scroll for anchor links
        document.addEventListener('click', this.handleAnchorClick.bind(this));
    }

    handleScroll() {
        const currentScrollY = window.scrollY;
        this.scrollDirection = currentScrollY > this.lastScrollY ? 'down' : 'up';
        this.lastScrollY = currentScrollY;

        this.updateNavbarVisibility();
        this.updateParallax();
        this.updateActiveSection();
        this.handleScrollProgress();
    }

    updateNavbarVisibility() {
        if (!this.navbar) return;

        const scrollThreshold = 100;
        const shouldShow = window.scrollY > scrollThreshold;

        if (shouldShow !== this.navbarVisible) {
            this.navbarVisible = shouldShow;
            this.navbar.classList.toggle('visible', shouldShow);
        }
    }

    setupParallax() {
        // Find all parallax elements
        this.parallaxElements = Array.from(document.querySelectorAll('[data-parallax]'));

        // Add parallax to hero background
        const heroSection = document.querySelector('.section-hero');
        if (heroSection) {
            this.parallaxElements.push({
                element: heroSection,
                speed: 0.5,
                type: 'background'
            });
        }
    }

    updateParallax() {
        const scrolled = window.scrollY;

        this.parallaxElements.forEach(item => {
            const element = item.element || item;
            const speed = item.speed || parseFloat(element.dataset.parallax) || 0.5;
            const type = item.type || element.dataset.parallaxType || 'transform';

            if (type === 'background') {
                const yPos = -(scrolled * speed);
                element.style.backgroundPosition = `center ${yPos}px`;
            } else if (type === 'transform') {
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            }
        });
    }

    updateActiveSection() {
        const scrollY = window.scrollY + window.innerHeight / 2;

        // Find the current section
        let newCurrentSection = null;
        for (const section of this.sections) {
            const rect = section.getBoundingClientRect();
            const sectionTop = rect.top + window.scrollY;

            if (scrollY >= sectionTop) {
                newCurrentSection = section;
            } else {
                break;
            }
        }

        if (newCurrentSection !== this.currentSection) {
            this.currentSection = newCurrentSection;
            this.updateNavigationActiveState();
        }
    }

    updateNavigationActiveState() {
        if (!this.currentSection) return;

        const currentId = this.currentSection.id;
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            const isActive = href === `#${currentId}`;

            link.classList.toggle('active', isActive);
        });
    }

    handleScrollProgress() {
        // Update scroll progress indicator if exists
        const progressBar = document.querySelector('.scroll-progress');
        if (progressBar) {
            const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
            progressBar.style.width = `${scrolled}%`;
        }
    }

    handleAnchorClick(e) {
        const link = e.target.closest('a[href^="#"]');
        if (!link) return;

        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            this.smoothScrollTo(targetElement);
        }
    }

    smoothScrollTo(element, offset = 0) {
        const elementPosition = element.getBoundingClientRect().top + window.scrollY;
        const offsetPosition = elementPosition - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    updateViewport() {
        // Update any viewport calculations
        this.viewportHeight = window.innerHeight;
        this.viewportWidth = window.innerWidth;
    }

    // Utility method to scroll to specific section
    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            this.smoothScrollTo(section, this.navbar ? this.navbar.offsetHeight : 0);
        }
    }

    // Method to get scroll progress
    getScrollProgress() {
        return {
            scrolled: window.scrollY,
            total: document.documentElement.scrollHeight - window.innerHeight,
            percentage: (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
        };
    }

    // Method to check if element is in viewport
    isElementInViewport(element, threshold = 0) {
        const rect = element.getBoundingClientRect();
        const elementTop = rect.top;
        const elementBottom = rect.bottom;
        const viewportTop = 0;
        const viewportBottom = window.innerHeight;

        return elementBottom >= viewportTop + threshold && elementTop <= viewportBottom - threshold;
    }

    // Method to add scroll-triggered callbacks
    addScrollCallback(callback, triggerPoint = 0.5) {
        const wrappedCallback = () => {
            const scrollProgress = this.getScrollProgress().percentage / 100;
            if (scrollProgress >= triggerPoint) {
                callback();
                window.removeEventListener('scroll', wrappedCallback);
            }
        };

        window.addEventListener('scroll', wrappedCallback);
        // Check if already scrolled past trigger point
        wrappedCallback();
    }

    // Method to create scroll-based animations
    createScrollAnimation(element, animationClass, triggerPoint = 0.8) {
        if (!element) return;

        const callback = () => {
            if (this.isElementInViewport(element, window.innerHeight * (1 - triggerPoint))) {
                element.classList.add(animationClass);
            }
        };

        window.addEventListener('scroll', callback);
        // Initial check
        callback();
    }

    // Method to enable/disable scroll
    setScrollEnabled(enabled) {
        document.body.style.overflow = enabled ? '' : 'hidden';
    }

    // Method to get scroll direction
    getScrollDirection() {
        return this.scrollDirection;
    }
}
