/**
 * CustomizeUI.js - UI Controller for Customization Interface
 * Handles user interactions and connects controls to the design engine
 */

class CustomizeUI {
    constructor() {
        this.controls = new Map();
        this.eventListeners = new Set();
        this.isInitialized = false;
    }

    init() {
        this.cacheElements();
        this.setupControls();
        this.bindEvents();
        this.initializeUI();
        this.isInitialized = true;
        console.log('🎛️ UI controller initialized');
    }

    cacheElements() {
        // Control elements
        this.presetSelect = document.getElementById('preset-select');
        this.saveBtn = document.getElementById('save-design');
        this.shareBtn = document.getElementById('share-design');
        this.resetBtn = document.getElementById('reset-design');
        this.undoBtn = document.getElementById('undo-btn');
        this.redoBtn = document.getElementById('redo-btn');
        this.getQuoteBtn = document.getElementById('get-quote');
        this.bookConsultationBtn = document.getElementById('book-consultation');

        // Control sections
        this.controlSections = document.querySelectorAll('.control-section');
    }

    setupControls() {
        // Setup option buttons
        const optionButtons = document.querySelectorAll('.option-btn[data-control]');
        optionButtons.forEach(button => {
            const control = button.dataset.control;
            const value = button.dataset.value;

            if (!this.controls.has(control)) {
                this.controls.set(control, new Set());
            }
            this.controls.get(control).add(button);

            // Mark active button based on current design
            const currentDesign = designEngine.getCurrentDesign();
            if (currentDesign[control] === value) {
                button.classList.add('active');
            }
        });

        // Setup color swatches
        const colorSwatches = document.querySelectorAll('.color-swatch[data-control]');
        colorSwatches.forEach(swatch => {
            const control = swatch.dataset.control;
            const value = swatch.dataset.value;

            if (!this.controls.has(control)) {
                this.controls.set(control, new Set());
            }
            this.controls.get(control).add(swatch);

            // Mark active swatch
            const currentDesign = designEngine.getCurrentDesign();
            if (currentDesign[control] === value) {
                swatch.classList.add('active');
            }
        });

        // Setup slider
        const floralSlider = document.getElementById('floral-density');
        if (floralSlider) {
            floralSlider.value = designEngine.getCurrentDesign().floral || 3;
            this.setupSlider(floralSlider);
        }
    }

    setupSlider(slider) {
        const updateSlider = (e) => {
            const value = parseInt(e.target.value);
            designEngine.updateDesign({ floral: value });

            // Update accessibility
            slider.setAttribute('aria-valuenow', value);
            slider.setAttribute('aria-valuetext', `Floral density: ${value} out of 5`);
        };

        this.addEventListener(slider, 'input', updateSlider);
        this.addEventListener(slider, 'change', updateSlider);
    }

    bindEvents() {
        // Preset selection
        if (this.presetSelect) {
            this.addEventListener(this.presetSelect, 'change', (e) => {
                const preset = e.target.value;
                if (preset !== 'blank') {
                    designEngine.loadPreset(preset);
                    this.updateUIFromDesign();
                }
            });
        }

        // Action buttons
        if (this.saveBtn) {
            this.addEventListener(this.saveBtn, 'click', () => this.handleSave());
        }

        if (this.shareBtn) {
            this.addEventListener(this.shareBtn, 'click', () => this.handleShare());
        }

        if (this.resetBtn) {
            this.addEventListener(this.resetBtn, 'click', () => this.handleReset());
        }

        if (this.undoBtn) {
            this.addEventListener(this.undoBtn, 'click', () => this.handleUndo());
        }

        if (this.redoBtn) {
            this.addEventListener(this.redoBtn, 'click', () => this.handleRedo());
        }

        if (this.getQuoteBtn) {
            this.addEventListener(this.getQuoteBtn, 'click', () => this.handleGetQuote());
        }

        if (this.bookConsultationBtn) {
            this.addEventListener(this.bookConsultationBtn, 'click', () => this.handleBookConsultation());
        }

        // Control interactions
        this.bindControlEvents();

        // Listen for design changes to update UI
        window.addEventListener('designChange', (e) => {
            this.handleDesignChange(e.detail.design, e.detail.changes, e.detail.action);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    bindControlEvents() {
        // Option buttons
        const optionButtons = document.querySelectorAll('.option-btn[data-control]');
        optionButtons.forEach(button => {
            this.addEventListener(button, 'click', () => {
                const control = button.dataset.control;
                const value = button.dataset.value;

                designEngine.updateDesign({ [control]: value });
                this.trackInteraction('control_change', { control, value });
            });
        });

        // Color swatches
        const colorSwatches = document.querySelectorAll('.color-swatch[data-control]');
        colorSwatches.forEach(swatch => {
            this.addEventListener(swatch, 'click', () => {
                const control = swatch.dataset.control;
                const value = swatch.dataset.value;

                designEngine.updateDesign({ [control]: value });
                this.trackInteraction('color_change', { control, value });
            });
        });
    }

    handleDesignChange(newDesign, changes, action) {
        // Update active states
        this.updateActiveStates(newDesign);

        // Update slider values
        const floralSlider = document.getElementById('floral-density');
        if (floralSlider && newDesign.floral !== undefined) {
            floralSlider.value = newDesign.floral;
            floralSlider.setAttribute('aria-valuenow', newDesign.floral);
        }

        // Update undo/redo buttons
        this.updateUndoRedoButtons();

        // Handle special actions
        if (action === 'reset') {
            this.showNotification('Design reset to default', 'info');
        }
    }

    updateActiveStates(design) {
        // Update option buttons
        this.controls.forEach((buttons, control) => {
            buttons.forEach(button => {
                const value = button.dataset.value;
                const isActive = design[control] === value;
                button.classList.toggle('active', isActive);
                button.setAttribute('aria-pressed', isActive);
            });
        });
    }

    updateUndoRedoButtons() {
        if (this.undoBtn) {
            const canUndo = designEngine.canUndo();
            this.undoBtn.disabled = !canUndo;
            this.undoBtn.setAttribute('aria-disabled', !canUndo);
        }

        if (this.redoBtn) {
            const canRedo = designEngine.canRedo();
            this.redoBtn.disabled = !canRedo;
            this.redoBtn.setAttribute('aria-disabled', !canRedo);
        }
    }

    handleSave() {
        try {
            const savedDesign = designEngine.saveDesign();
            if (savedDesign) {
                this.showNotification(`Design "${savedDesign.name}" saved successfully!`, 'success');
                this.trackInteraction('design_save', { designId: savedDesign.name });
            }
        } catch (error) {
            this.showNotification('Failed to save design. Please try again.', 'error');
            console.error('Save error:', error);
        }
    }

    handleShare() {
        try {
            const shareLink = designEngine.generateShareLink();
            this.copyToClipboard(shareLink).then(() => {
                this.showNotification('Share link copied to clipboard!', 'success');
                this.trackInteraction('design_share');
            }).catch(() => {
                // Fallback: show the link
                this.showShareDialog(shareLink);
            });
        } catch (error) {
            this.showNotification('Failed to generate share link.', 'error');
            console.error('Share error:', error);
        }
    }

    handleReset() {
        if (confirm('Are you sure you want to reset the design? This will lose any unsaved changes.')) {
            designEngine.resetToDefault();
            this.trackInteraction('design_reset');
        }
    }

    handleUndo() {
        if (designEngine.undo()) {
            this.showNotification('Undid last change', 'info');
        }
    }

    handleRedo() {
        if (designEngine.redo()) {
            this.showNotification('Redid last change', 'info');
        }
    }

    handleGetQuote() {
        const cost = designEngine.calculateEstimatedCost();
        this.showQuoteDialog(cost);
        this.trackInteraction('quote_request', { estimatedCost: cost.base });
    }

    handleBookConsultation() {
        // In a real app, this would open a booking modal or redirect
        this.showNotification('Opening consultation booking...', 'info');
        setTimeout(() => {
            window.location.href = '/contact?source=customizer';
        }, 1000);
        this.trackInteraction('consultation_booking');
    }

    handleKeyboard(e) {
        // Handle keyboard shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'z':
                    e.preventDefault();
                    if (e.shiftKey) {
                        this.handleRedo();
                    } else {
                        this.handleUndo();
                    }
                    break;
                case 's':
                    e.preventDefault();
                    this.handleSave();
                    break;
            }
        }
    }

    initializeUI() {
        // Set initial states
        this.updateUndoRedoButtons();

        // Initialize accessibility attributes
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            slider.setAttribute('aria-valuemin', slider.min);
            slider.setAttribute('aria-valuemax', slider.max);
            slider.setAttribute('aria-valuenow', slider.value);
        });

        // Load from URL if present
        designEngine.loadFromShareLink();
    }

    updateUIFromDesign() {
        const design = designEngine.getCurrentDesign();
        this.updateActiveStates(design);
        this.updateUndoRedoButtons();
    }

    // Utility methods
    addEventListener(element, event, handler) {
        if (element) {
            element.addEventListener(event, handler);
            this.eventListeners.add({ element, event, handler });
        }
    }

    showNotification(message, type = 'info') {
        // Use the main app's notification system if available
        if (window.Hublievents && window.Hublievents.app && window.Hublievents.app.state) {
            window.Hublievents.app.state.addNotification(message, type);
        } else {
            // Fallback notification
            console.log(`[${type.toUpperCase()}] ${message}`);
            // You could implement a simple toast notification here
        }
    }

    async copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            return new Promise((resolve, reject) => {
                if (document.execCommand('copy')) {
                    resolve();
                } else {
                    reject(new Error('Copy failed'));
                }
                document.body.removeChild(textArea);
            });
        }
    }

    showShareDialog(link) {
        const dialog = document.createElement('div');
        dialog.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 10000; display: flex; align-items: center; justify-content: center;">
                <div style="background: white; padding: 2rem; border-radius: 8px; max-width: 500px; margin: 1rem;">
                    <h3>Share Your Design</h3>
                    <p>Copy this link to share your design:</p>
                    <input type="text" value="${link}" readonly style="width: 100%; padding: 0.5rem; margin: 1rem 0; border: 1px solid #ddd; border-radius: 4px;">
                    <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                        <button onclick="this.closest('div').parentElement.remove()">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    }

    showQuoteDialog(cost) {
        const dialog = document.createElement('div');
        dialog.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 10000; display: flex; align-items: center; justify-content: center;">
                <div style="background: white; padding: 2rem; border-radius: 8px; max-width: 500px; margin: 1rem;">
                    <h3>Estimated Quote</h3>
                    <div style="text-align: center; margin: 2rem 0;">
                        <div style="font-size: 2rem; font-weight: bold; color: var(--color-primary);">${cost.formatted}</div>
                        <p style="color: #666; margin-top: 0.5rem;">Estimated starting price</p>
                    </div>
                    <p style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                        This is an estimate based on your current design choices. Final pricing may vary based on specific requirements, location, and customization details.
                    </p>
                    <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                        <button onclick="this.closest('div').parentElement.remove()">Close</button>
                        <button onclick="window.location.href='/contact?quote=true'" style="background: var(--color-primary); color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px;">Get Exact Quote</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    }

    trackInteraction(type, data = {}) {
        if (window.Hublievents && window.Hublievents.app && window.Hublievents.app.state) {
            window.Hublievents.app.state.trackInteraction(type, data);
        }
    }

    // Cleanup method
    destroy() {
        // Remove all event listeners
        this.eventListeners.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.eventListeners.clear();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all customize modules
    designEngine.init();
    designRenderer.init();

    // Initialize UI controller last so other modules are ready
    const customizeUI = new CustomizeUI();
    customizeUI.init();

    // Make globally available for debugging
    window.customizeUI = customizeUI;
});
