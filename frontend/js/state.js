/**
 * State.js - State Management
 * Handles application state, persistence, and reactive updates
 */

class StateManager {
    constructor() {
        this.state = {};
        this.listeners = new Map();
        this.storageKey = 'hublievents_state';
        this.debounceTimers = new Map();
    }

    init() {
        this.loadPersistedState();
        this.setupDefaultState();
        this.bindEvents();
        console.log('🗃️ State manager initialized');
    }

    setupDefaultState() {
        // Set default application state
        this.setState({
            app: {
                loaded: false,
                theme: 'light',
                language: 'en',
                reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
            },
            navigation: {
                currentSection: 'home',
                menuOpen: false,
                scrollProgress: 0
            },
            ui: {
                modalOpen: false,
                notifications: [],
                loadingStates: new Set()
            },
            user: {
                preferences: {
                    newsletterSubscribed: false,
                    contactMethod: 'email'
                },
                interactions: {
                    formSubmissions: 0,
                    buttonClicks: 0
                }
            },
            forms: {
                contact: {
                    name: '',
                    email: '',
                    message: '',
                    submitted: false
                },
                newsletter: {
                    email: '',
                    subscribed: false
                }
            },
            gallery: {
                currentFilter: 'all',
                imagesLoaded: 0,
                totalImages: 0
            },
            animations: {
                enabled: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
                completed: new Set()
            }
        });
    }

    bindEvents() {
        // Listen for system preference changes
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
            this.setState({ app: { ...this.state.app, reducedMotion: e.matches } });
        });

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            this.setState({ app: { ...this.state.app, theme: e.matches ? 'dark' : 'light' } });
        });
    }

    // Core state management methods
    getState(path) {
        if (!path) return { ...this.state };

        const keys = path.split('.');
        let current = this.state;

        for (const key of keys) {
            if (current && typeof current === 'object' && key in current) {
                current = current[key];
            } else {
                return undefined;
            }
        }

        return current;
    }

    setState(updates, persist = true) {
        this.state = this.deepMerge(this.state, updates);

        // Trigger listeners for changed paths
        this.notifyListeners(updates);

        // Persist to localStorage if requested
        if (persist) {
            this.persistState();
        }

        // Debug logging in development
        if (process.env.NODE_ENV === 'development') {
            console.log('State updated:', updates);
        }
    }

    deepMerge(target, source) {
        const output = { ...target };

        if (this.isObject(target) && this.isObject(source)) {
            Object.keys(source).forEach(key => {
                if (this.isObject(source[key])) {
                    if (!(key in target)) {
                        output[key] = source[key];
                    } else {
                        output[key] = this.deepMerge(target[key], source[key]);
                    }
                } else {
                    output[key] = source[key];
                }
            });
        }

        return output;
    }

    isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }

    // Listener system for reactive updates
    subscribe(path, callback, immediate = false) {
        if (!this.listeners.has(path)) {
            this.listeners.set(path, new Set());
        }

        this.listeners.get(path).add(callback);

        // Call immediately if requested
        if (immediate) {
            callback(this.getState(path));
        }

        // Return unsubscribe function
        return () => {
            const listeners = this.listeners.get(path);
            if (listeners) {
                listeners.delete(callback);
                if (listeners.size === 0) {
                    this.listeners.delete(path);
                }
            }
        };
    }

    notifyListeners(changes) {
        const changedPaths = this.getChangedPaths(changes);

        changedPaths.forEach(path => {
            const listeners = this.listeners.get(path);
            if (listeners) {
                const value = this.getState(path);
                listeners.forEach(callback => callback(value));
            }
        });
    }

    getChangedPaths(obj, prefix = '') {
        const paths = [];

        for (const key in obj) {
            const fullPath = prefix ? `${prefix}.${key}` : key;
            paths.push(fullPath);

            if (this.isObject(obj[key])) {
                paths.push(...this.getChangedPaths(obj[key], fullPath));
            }
        }

        return paths;
    }

    // Persistence methods
    persistState() {
        try {
            const persistableState = this.getPersistableState();
            localStorage.setItem(this.storageKey, JSON.stringify(persistableState));
        } catch (error) {
            console.warn('Failed to persist state:', error);
        }
    }

    loadPersistedState() {
        try {
            const persisted = localStorage.getItem(this.storageKey);
            if (persisted) {
                const parsedState = JSON.parse(persisted);
                this.state = this.deepMerge(this.state, parsedState);
            }
        } catch (error) {
            console.warn('Failed to load persisted state:', error);
        }
    }

    getPersistableState() {
        // Return only the state that should be persisted
        const { app, user, forms } = this.state;
        return { app, user, forms };
    }

    clearPersistedState() {
        localStorage.removeItem(this.storageKey);
    }

    // Utility methods for common operations
    setLoading(key, loading) {
        const loadingStates = new Set(this.state.ui.loadingStates);

        if (loading) {
            loadingStates.add(key);
        } else {
            loadingStates.delete(key);
        }

        this.setState({
            ui: {
                ...this.state.ui,
                loadingStates
            }
        });
    }

    isLoading(key) {
        return this.state.ui.loadingStates.has(key);
    }

    addNotification(message, type = 'info', duration = 5000) {
        const notification = {
            id: Date.now(),
            message,
            type,
            duration
        };

        const notifications = [...this.state.ui.notifications, notification];

        this.setState({
            ui: {
                ...this.state.ui,
                notifications
            }
        });

        // Auto-remove notification
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification.id);
            }, duration);
        }

        return notification.id;
    }

    removeNotification(id) {
        const notifications = this.state.ui.notifications.filter(n => n.id !== id);

        this.setState({
            ui: {
                ...this.state.ui,
                notifications
            }
        });
    }

    // Debounced state updates
    setStateDebounced(updates, delay = 300) {
        const key = JSON.stringify(updates);

        clearTimeout(this.debounceTimers.get(key));
        this.debounceTimers.set(key, setTimeout(() => {
            this.setState(updates);
            this.debounceTimers.delete(key);
        }, delay));
    }

    // Form state management
    updateForm(formName, field, value) {
        this.setState({
            forms: {
                ...this.state.forms,
                [formName]: {
                    ...this.state.forms[formName],
                    [field]: value
                }
            }
        });
    }

    getFormData(formName) {
        return this.state.forms[formName] || {};
    }

    resetForm(formName) {
        const defaultForms = {
            contact: { name: '', email: '', message: '', submitted: false },
            newsletter: { email: '', subscribed: false }
        };

        if (defaultForms[formName]) {
            this.setState({
                forms: {
                    ...this.state.forms,
                    [formName]: defaultForms[formName]
                }
            });
        }
    }

    // User preference methods
    setUserPreference(key, value) {
        this.setState({
            user: {
                ...this.state.user,
                preferences: {
                    ...this.state.user.preferences,
                    [key]: value
                }
            }
        });
    }

    getUserPreference(key, defaultValue = null) {
        return this.state.user.preferences[key] ?? defaultValue;
    }

    // Analytics and tracking
    trackInteraction(type, data = {}) {
        const interactions = this.state.user.interactions;
        interactions[`${type}s`] = (interactions[`${type}s`] || 0) + 1;

        this.setState({
            user: {
                ...this.state.user,
                interactions
            }
        });

        // Send to analytics if available
        if (window.gtag) {
            window.gtag('event', type, data);
        }
    }
}
