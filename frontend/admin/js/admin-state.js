/**
 * Admin State Manager
 * Handles admin application state and persistence
 */

class AdminState {
    constructor() {
        this.state = {};
        this.listeners = new Map();
        this.storageKey = 'admin_app_state';
    }

    /**
     * Initialize admin state
     */
    init() {
        this.loadPersistedState();
        this.setupDefaultState();
        console.log('🗃️ Admin state manager initialized');
    }

    /**
     * Setup default admin state
     */
    setupDefaultState() {
        this.setState({
            ui: {
                sidebarCollapsed: false,
                currentPage: 'dashboard',
                loadingStates: new Set(),
                notifications: []
            },
            user: {
                currentUser: null,
                isLoggedIn: false,
                permissions: []
            },
            data: {
                stats: {},
                enquiries: [],
                designs: [],
                gallery: [],
                users: []
            },
            filters: {
                enquiries: {},
                designs: {},
                gallery: {},
                users: {}
            },
            cache: {
                lastUpdated: {},
                ttl: 5 * 60 * 1000 // 5 minutes
            }
        });
    }

    /**
     * Get state value
     */
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

    /**
     * Set state value
     */
    setState(updates, persist = true) {
        this.state = this.deepMerge(this.state, updates);

        // Trigger listeners
        this.notifyListeners(updates);

        // Persist if requested
        if (persist) {
            this.persistState();
        }
    }

    /**
     * Deep merge objects
     */
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

    /**
     * Check if value is object
     */
    isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }

    /**
     * Subscribe to state changes
     */
    subscribe(path, callback) {
        if (!this.listeners.has(path)) {
            this.listeners.set(path, new Set());
        }
        this.listeners.get(path).add(callback);

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

    /**
     * Notify listeners of changes
     */
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

    /**
     * Get changed paths from updates
     */
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

    /**
     * Persist state to localStorage
     */
    persistState() {
        try {
            const persistableState = this.getPersistableState();
            localStorage.setItem(this.storageKey, JSON.stringify(persistableState));
        } catch (error) {
            console.warn('Failed to persist admin state:', error);
        }
    }

    /**
     * Load persisted state
     */
    loadPersistedState() {
        try {
            const persisted = localStorage.getItem(this.storageKey);
            if (persisted) {
                const parsedState = JSON.parse(persisted);
                this.state = this.deepMerge(this.state, parsedState);
            }
        } catch (error) {
            console.warn('Failed to load persisted admin state:', error);
        }
    }

    /**
     * Get persistable state (exclude sensitive data)
     */
    getPersistableState() {
        const { ui, filters } = this.state;
        return { ui, filters };
    }

    /**
     * Clear persisted state
     */
    clearPersistedState() {
        localStorage.removeItem(this.storageKey);
    }

    /**
     * Set loading state
     */
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

    /**
     * Check if loading
     */
    isLoading(key) {
        return this.state.ui.loadingStates.has(key);
    }

    /**
     * Add notification
     */
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

        // Auto-remove
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification.id);
            }, duration);
        }

        return notification.id;
    }

    /**
     * Remove notification
     */
    removeNotification(id) {
        const notifications = this.state.ui.notifications.filter(n => n.id !== id);

        this.setState({
            ui: {
                ...this.state.ui,
                notifications
            }
        });
    }

    /**
     * Set current user
     */
    setCurrentUser(user) {
        this.setState({
            user: {
                ...this.state.user,
                currentUser: user,
                isLoggedIn: !!user,
                permissions: user?.permissions || []
            }
        });
    }

    /**
     * Clear user data
     */
    clearUser() {
        this.setState({
            user: {
                currentUser: null,
                isLoggedIn: false,
                permissions: []
            }
        });
    }

    /**
     * Check permission
     */
    hasPermission(permission) {
        const user = this.state.user.currentUser;
        if (!user) return false;

        if (user.role === 'super_admin') return true;

        return this.state.user.permissions.includes(permission);
    }

    /**
     * Cache data with TTL
     */
    setCache(key, data) {
        this.setState({
            cache: {
                ...this.state.cache,
                lastUpdated: {
                    ...this.state.cache.lastUpdated,
                    [key]: Date.now()
                }
            },
            data: {
                ...this.state.data,
                [key]: data
            }
        });
    }

    /**
     * Get cached data if not expired
     */
    getCache(key) {
        const lastUpdated = this.state.cache.lastUpdated[key];
        if (!lastUpdated) return null;

        const age = Date.now() - lastUpdated;
        if (age > this.state.cache.ttl) return null;

        return this.state.data[key];
    }

    /**
     * Clear cache
     */
    clearCache(key = null) {
        if (key) {
            const lastUpdated = { ...this.state.cache.lastUpdated };
            const data = { ...this.state.data };
            delete lastUpdated[key];
            delete data[key];

            this.setState({
                cache: {
                    ...this.state.cache,
                    lastUpdated
                },
                data
            });
        } else {
            this.setState({
                cache: {
                    ...this.state.cache,
                    lastUpdated: {}
                },
                data: {
                    stats: {},
                    enquiries: [],
                    designs: [],
                    gallery: [],
                    users: []
                }
            });
        }
    }
}

// Initialize global AdminState instance
window.AdminState = new AdminState();
