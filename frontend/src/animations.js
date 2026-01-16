/**
 * Animations.js - Animation Engine
 * Handles all scroll-triggered and interactive animations
 */

class AnimationEngine {
    constructor() {
        this.observer = null;
        this.animatedElements = new Set();
        this.initialAnimationsPlayed = false;
    }

    init() {
        this.setupIntersectionObserver();
        this.bindEvents();
        console.log('🎬 Animation engine initialized');
    }

    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '0px 0px -50px 0px', // Trigger 50px before element enters viewport
            threshold: 0.1
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateElement(entry.target);
                }
            });
        }, options);

        // Observe all elements with scroll animation classes
        this.observeScrollElements();
    }

    observeScrollElements() {
        const scrollElements = document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right, .scroll-scale');
        scrollElements.forEach(element => {
            this.observer.observe(element);
        });
    }

    animateElement(element) {
        if (this.animatedElements.has(element)) return;

        // Add revealed class to trigger CSS animation
        element.classList.add('revealed');
        this.animatedElements.add(element);

        // Optional: Add custom animation logic here
        this.handleSpecialAnimations(element);
    }

    handleSpecialAnimations(element) {
        // Handle elements that need special animation treatment
        if (element.classList.contains('animate-stagger-children')) {
            this.animateChildrenStaggered(element);
        }

        if (element.classList.contains('animate-counter')) {
            this.animateCounter(element);
        }

        if (element.classList.contains('animate-text-typewriter')) {
            this.animateTypewriter(element);
        }
    }

    animateChildrenStaggered(parent) {
        const children = parent.children;
        Array.from(children).forEach((child, index) => {
            setTimeout(() => {
                child.classList.add('revealed');
            }, index * 100); // 100ms stagger
        });
    }

    animateCounter(element) {
        const target = parseInt(element.dataset.target || element.textContent);
        const duration = parseInt(element.dataset.duration || 2000);
        const start = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(target * easeOutQuart);

            element.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    animateTypewriter(element) {
        const text = element.dataset.text || element.textContent;
        element.textContent = '';
        element.style.borderRight = '2px solid var(--color-accent)';

        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            } else {
                // Remove cursor after typing
                setTimeout(() => {
                    element.style.borderRight = 'none';
                }, 500);
            }
        };

        typeWriter();
    }

    playInitialSequence() {
        if (this.initialAnimationsPlayed) return;

        // Play hero section animations
        const heroTitle = document.getElementById('hero-title');
        const heroSubtitle = document.querySelector('.lead');
        const heroButtons = document.querySelectorAll('.btn');

        // Sequence the animations
        setTimeout(() => {
            if (heroTitle) heroTitle.classList.add('animate-text-reveal');
        }, 200);

        setTimeout(() => {
            if (heroSubtitle) heroSubtitle.classList.add('animate-fade-in-up');
        }, 600);

        setTimeout(() => {
            heroButtons.forEach((btn, index) => {
                setTimeout(() => {
                    btn.classList.add('animate-fade-in-up');
                }, index * 200);
            });
        }, 1000);

        this.initialAnimationsPlayed = true;
    }

    bindEvents() {
        // Handle hover animations
        document.addEventListener('mouseenter', this.handleHoverStart.bind(this), true);
        document.addEventListener('mouseleave', this.handleHoverEnd.bind(this), true);

        // Handle click animations
        document.addEventListener('click', this.handleClick.bind(this), true);
    }

    handleHoverStart(e) {
        const element = e.target.closest('.hover-lift, .hover-scale, .hover-rotate');
        if (!element) return;

        // Add hover animation classes
        if (element.classList.contains('hover-lift')) {
            element.style.transform = 'translateY(-8px)';
        }
        if (element.classList.contains('hover-scale')) {
            element.style.transform = 'scale(1.05)';
        }
        if (element.classList.contains('hover-rotate')) {
            element.style.transform = 'rotate(5deg)';
        }
    }

    handleHoverEnd(e) {
        const element = e.target.closest('.hover-lift, .hover-scale, .hover-rotate');
        if (!element) return;

        // Reset transforms
        element.style.transform = '';
    }

    handleClick(e) {
        const button = e.target.closest('.btn');
        if (!button) return;

        // Add click ripple effect
        this.createRippleEffect(e, button);
    }

    createRippleEffect(e, button) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
        `;

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    updateViewport() {
        // Update any viewport-dependent animations
        // This is called on resize
    }

    // Utility method to manually trigger animations
    triggerAnimation(selector) {
        const element = document.querySelector(selector);
        if (element) {
            this.animateElement(element);
        }
    }

    // Method to reset all animations (useful for page transitions)
    resetAnimations() {
        this.animatedElements.clear();
        document.querySelectorAll('.revealed').forEach(el => {
            el.classList.remove('revealed');
        });
        this.observeScrollElements();
    }
}

// Add ripple keyframe if not already in CSS
if (!document.querySelector('#ripple-keyframes')) {
    const style = document.createElement('style');
    style.id = 'ripple-keyframes';
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}
