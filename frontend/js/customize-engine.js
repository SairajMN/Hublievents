/**
 * CustomizeEngine.js - Design State Management Engine
 * Core logic for managing design configurations, presets, and state
 */

class DesignEngine {
    constructor() {
        this.currentDesign = {};
        this.history = [];
        this.historyIndex = -1;
        this.maxHistory = 50;
        this.presets = {};
        this.isInitialized = false;
    }

    init() {
        this.loadPresets();
        this.resetToDefault();
        this.isInitialized = true;
        console.log('🎨 Design engine initialized');
    }

    // Core state management
    getCurrentDesign() {
        return { ...this.currentDesign };
    }

    updateDesign(updates) {
        // Create immutable update
        const newDesign = { ...this.currentDesign };

        // Deep merge updates
        this.deepMerge(newDesign, updates);

        // Validate the design
        if (!this.validateDesign(newDesign)) {
            console.warn('Invalid design update:', updates);
            return false;
        }

        // Save to history before updating
        this.saveToHistory();

        // Update current design
        this.currentDesign = newDesign;

        // Notify listeners
        this.notifyDesignChange(newDesign, updates);

        return true;
    }

    deepMerge(target, source) {
        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                if (!(key in target)) {
                    target[key] = {};
                }
                this.deepMerge(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
    }

    validateDesign(design) {
        // Basic validation rules
        const required = ['stage', 'colors', 'lighting', 'fabric', 'arch', 'seating', 'floor'];
        const validOptions = {
            stage: ['classic-rectangular', 'royal-arch', 'circular', 'hexagonal'],
            colors: ['ivory-gold', 'maroon-gold', 'navy-silver', 'rose-gold'],
            lighting: ['warm', 'cool', 'dramatic'],
            fabric: ['silk', 'velvet', 'satin'],
            arch: ['classic', 'floral', 'modern'],
            seating: ['classic', 'luxury', 'contemporary'],
            floor: ['plain', 'floral', 'geometric']
        };

        // Check required fields
        for (const field of required) {
            if (!(field in design)) {
                console.error(`Missing required field: ${field}`);
                return false;
            }
        }

        // Check valid options
        for (const [field, options] of Object.entries(validOptions)) {
            if (!options.includes(design[field])) {
                console.error(`Invalid value for ${field}: ${design[field]}`);
                return false;
            }
        }

        // Validate floral density
        if (design.floral < 0 || design.floral > 5) {
            console.error(`Invalid floral density: ${design.floral}`);
            return false;
        }

        return true;
    }

    // History management for undo/redo
    saveToHistory() {
        // Remove any history after current index (for when user made new changes after undo)
        this.history = this.history.slice(0, this.historyIndex + 1);

        // Add current design to history
        this.history.push({ ...this.currentDesign });

        // Limit history size
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        } else {
            this.historyIndex++;
        }
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.currentDesign = { ...this.history[this.historyIndex] };
            this.notifyDesignChange(this.currentDesign, {}, 'undo');
            return true;
        }
        return false;
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.currentDesign = { ...this.history[this.historyIndex] };
            this.notifyDesignChange(this.currentDesign, {}, 'redo');
            return true;
        }
        return false;
    }

    canUndo() {
        return this.historyIndex > 0;
    }

    canRedo() {
        return this.historyIndex < this.history.length - 1;
    }

    // Preset system
    loadPresets() {
        this.presets = {
            'blank': {
                stage: 'royal-arch',
                colors: 'maroon-gold',
                floral: 3,
                lighting: 'cool',
                fabric: 'silk',
                arch: 'classic',
                seating: 'classic',
                floor: 'floral'
            },
            'royal-wedding': {
                stage: 'royal-arch',
                colors: 'maroon-gold',
                floral: 5,
                lighting: 'warm',
                fabric: 'silk',
                arch: 'floral',
                seating: 'luxury',
                floor: 'floral'
            },
            'corporate-elegant': {
                stage: 'classic-rectangular',
                colors: 'navy-silver',
                floral: 1,
                lighting: 'cool',
                fabric: 'satin',
                arch: 'modern',
                seating: 'contemporary',
                floor: 'geometric'
            },
            'garden-romance': {
                stage: 'circular',
                colors: 'rose-gold',
                floral: 4,
                lighting: 'warm',
                fabric: 'silk',
                arch: 'floral',
                seating: 'classic',
                floor: 'floral'
            },
            'modern-luxury': {
                stage: 'hexagonal',
                colors: 'ivory-gold',
                floral: 2,
                lighting: 'dramatic',
                fabric: 'velvet',
                arch: 'modern',
                seating: 'luxury',
                floor: 'plain'
            }
        };
    }

    loadPreset(presetName) {
        if (this.presets[presetName]) {
            this.updateDesign(this.presets[presetName]);
            return true;
        }
        return false;
    }

    getPresets() {
        return { ...this.presets };
    }

    // Save/Load functionality
    saveDesign(name = null) {
        const designData = {
            name: name || `Design ${Date.now()}`,
            design: this.getCurrentDesign(),
            timestamp: Date.now(),
            version: '1.0'
        };

        try {
            const savedDesigns = this.getSavedDesigns();
            savedDesigns.push(designData);

            // Keep only last 10 designs
            if (savedDesigns.length > 10) {
                savedDesigns.shift();
            }

            localStorage.setItem('hublievents_saved_designs', JSON.stringify(savedDesigns));
            return designData;
        } catch (error) {
            console.error('Failed to save design:', error);
            return null;
        }
    }

    loadDesign(designData) {
        if (designData && designData.design) {
            this.updateDesign(designData.design);
            return true;
        }
        return false;
    }

    getSavedDesigns() {
        try {
            const saved = localStorage.getItem('hublievents_saved_designs');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Failed to load saved designs:', error);
            return [];
        }
    }

    deleteSavedDesign(index) {
        try {
            const savedDesigns = this.getSavedDesigns();
            savedDesigns.splice(index, 1);
            localStorage.setItem('hublievents_saved_designs', JSON.stringify(savedDesigns));
            return true;
        } catch (error) {
            console.error('Failed to delete design:', error);
            return false;
        }
    }

    // Share functionality
    generateShareLink() {
        const designData = btoa(JSON.stringify(this.getCurrentDesign()));
        const baseUrl = window.location.origin + window.location.pathname;
        return `${baseUrl}?design=${designData}`;
    }

    loadFromShareLink() {
        const urlParams = new URLSearchParams(window.location.search);
        const designParam = urlParams.get('design');

        if (designParam) {
            try {
                const designData = JSON.parse(atob(designParam));
                this.updateDesign(designData);
                // Clean URL
                window.history.replaceState({}, '', window.location.pathname);
                return true;
            } catch (error) {
                console.error('Failed to load design from URL:', error);
                return false;
            }
        }
        return false;
    }

    // Export/Import
    exportDesign() {
        const designData = {
            version: '1.0',
            design: this.getCurrentDesign(),
            metadata: {
                exportedAt: Date.now(),
                userAgent: navigator.userAgent
            }
        };

        const dataStr = JSON.stringify(designData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });

        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `hublievents-design-${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    importDesign(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const designData = JSON.parse(e.target.result);
                    if (designData.design) {
                        this.updateDesign(designData.design);
                        resolve(designData);
                    } else {
                        reject(new Error('Invalid design file format'));
                    }
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    // Reset functionality
    resetToDefault() {
        this.resetToPreset('blank');
    }

    resetToPreset(presetName) {
        if (this.presets[presetName]) {
            this.currentDesign = { ...this.presets[presetName] };
            this.history = [{ ...this.currentDesign }];
            this.historyIndex = 0;
            this.notifyDesignChange(this.currentDesign, {}, 'reset');
        }
    }

    // Observer pattern for design changes
    addChangeListener(callback) {
        if (!this.changeListeners) {
            this.changeListeners = new Set();
        }
        this.changeListeners.add(callback);
    }

    removeChangeListener(callback) {
        if (this.changeListeners) {
            this.changeListeners.delete(callback);
        }
    }

    notifyDesignChange(newDesign, changes, action = 'update') {
        if (this.changeListeners) {
            this.changeListeners.forEach(callback => {
                callback(newDesign, changes, action);
            });
        }

        // Emit custom event for other parts of the app
        window.dispatchEvent(new CustomEvent('designChange', {
            detail: { design: newDesign, changes, action }
        }));
    }

    // Utility methods
    getDesignSummary() {
        const design = this.getCurrentDesign();
        return {
            stage: design.stage,
            theme: design.colors,
            lighting: design.lighting,
            style: design.arch,
            complexity: design.floral > 3 ? 'ornate' : design.floral > 1 ? 'moderate' : 'simple'
        };
    }

    calculateEstimatedCost() {
        // Mock cost calculation based on design choices
        const design = this.getCurrentDesign();
        let baseCost = 50000; // Base cost in INR

        // Add costs based on choices
        const costs = {
            stage: { 'royal-arch': 15000, 'hexagonal': 12000, 'circular': 10000, 'classic-rectangular': 8000 },
            fabric: { 'silk': 8000, 'velvet': 12000, 'satin': 6000 },
            floral: design.floral * 2000,
            lighting: { 'dramatic': 8000, 'warm': 5000, 'cool': 4000 },
            seating: { 'luxury': 10000, 'contemporary': 7000, 'classic': 5000 }
        };

        baseCost += costs.stage[design.stage] || 0;
        baseCost += costs.fabric[design.fabric] || 0;
        baseCost += costs.floral;
        baseCost += costs.lighting[design.lighting] || 0;
        baseCost += costs.seating[design.seating] || 0;

        return {
            base: baseCost,
            currency: 'INR',
            formatted: `₹${baseCost.toLocaleString('en-IN')}`
        };
    }
}

// Global instance
const designEngine = new DesignEngine();
