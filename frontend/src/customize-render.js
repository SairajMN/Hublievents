/**
 * CustomizeRender.js - Real-time Design Rendering Engine
 * Handles visual updates to the design canvas based on state changes
 */

class DesignRenderer {
    constructor() {
        this.canvas = null;
        this.layers = new Map();
        this.currentDesign = {};
        this.isRendering = false;
        this.renderQueue = [];
        this.lastRenderTime = 0;
        this.targetFPS = 60;
        this.frameInterval = 1000 / this.targetFPS;
    }

    init() {
        this.cacheElements();
        this.setupLayers();
        this.bindEvents();
        console.log('🎭 Design renderer initialized');
    }

    cacheElements() {
        this.canvas = document.getElementById('design-canvas');
        if (!this.canvas) {
            console.error('Design canvas not found');
            return;
        }

        // Cache layer elements
        this.layers.set('stage', this.canvas.querySelector('.stage-base'));
        this.layers.set('backdrop', this.canvas.querySelector('.backdrop'));
        this.layers.set('floral', this.canvas.querySelector('.floral'));
        this.layers.set('lighting', this.canvas.querySelector('.lighting'));
        this.layers.set('props', this.canvas.querySelector('.props'));
        this.layers.set('floor', this.canvas.querySelector('.floor'));
    }

    setupLayers() {
        // Initialize layer styles and data attributes
        this.layers.forEach((element, layerName) => {
            if (element) {
                element.dataset.layer = layerName;
                element.style.zIndex = this.getLayerZIndex(layerName);
            }
        });
    }

    getLayerZIndex(layerName) {
        const zIndices = {
            'floor': 1,
            'stage': 2,
            'backdrop': 3,
            'props': 4,
            'floral': 5,
            'lighting': 6
        };
        return zIndices[layerName] || 1;
    }

    bindEvents() {
        // Listen for design changes
        window.addEventListener('designChange', (e) => {
            this.handleDesignChange(e.detail.design, e.detail.changes, e.detail.action);
        });

        // Listen for window resize
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    handleDesignChange(newDesign, changes, action) {
        this.currentDesign = { ...newDesign };

        // Queue render update
        this.queueRender();

        // Handle special cases
        if (action === 'reset') {
            this.handleReset();
        }
    }

    queueRender() {
        if (!this.isRendering) {
            this.isRendering = true;
            requestAnimationFrame(this.render.bind(this));
        }
    }

    render(currentTime) {
        // Throttle rendering to target FPS
        if (currentTime - this.lastRenderTime < this.frameInterval) {
            requestAnimationFrame(this.render.bind(this));
            return;
        }

        this.lastRenderTime = currentTime;
        this.isRendering = false;

        // Update all layers based on current design
        this.updateStageLayer();
        this.updateBackdropLayer();
        this.updateFloralLayer();
        this.updateLightingLayer();
        this.updatePropsLayer();
        this.updateFloorLayer();

        // Update canvas attributes for accessibility
        this.updateCanvasAccessibility();
    }

    updateStageLayer() {
        const stageLayer = this.layers.get('stage');
        if (!stageLayer) return;

        const stage = this.currentDesign.stage;

        // Remove all stage classes
        stageLayer.className = 'layer stage-base';

        // Add stage-specific class
        stageLayer.classList.add(`stage-${stage}`);

        // Update styles based on stage type
        const stageStyles = this.getStageStyles(stage);
        Object.assign(stageLayer.style, stageStyles);
    }

    getStageStyles(stage) {
        const styles = {};

        switch (stage) {
            case 'royal-arch':
                styles.borderRadius = 'var(--radius-lg)';
                styles.background = 'linear-gradient(145deg, var(--color-bg), rgba(139, 21, 56, 0.1))';
                break;
            case 'classic-rectangular':
                styles.borderRadius = 'var(--radius-md)';
                styles.background = 'linear-gradient(145deg, var(--color-bg), rgba(139, 21, 56, 0.05))';
                break;
            case 'circular':
                styles.borderRadius = '50%';
                styles.background = 'radial-gradient(circle, var(--color-bg) 70%, rgba(139, 21, 56, 0.1) 100%)';
                break;
            case 'hexagonal':
                styles.borderRadius = 'var(--radius-lg)';
                styles.clipPath = 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)';
                styles.background = 'linear-gradient(145deg, var(--color-bg), rgba(139, 21, 56, 0.08))';
                break;
        }

        return styles;
    }

    updateBackdropLayer() {
        const backdropLayer = this.layers.get('backdrop');
        if (!backdropLayer) return;

        const colors = this.currentDesign.colors;

        // Update backdrop based on color theme
        const backdropStyles = this.getBackdropStyles(colors);
        Object.assign(backdropLayer.style, backdropStyles);
    }

    getBackdropStyles(colors) {
        const styles = {};

        switch (colors) {
            case 'maroon-gold':
                styles.background = 'linear-gradient(135deg, rgba(139, 21, 56, 0.3) 0%, rgba(212, 175, 55, 0.2) 100%)';
                break;
            case 'ivory-gold':
                styles.background = 'linear-gradient(135deg, rgba(245, 245, 220, 0.4) 0%, rgba(212, 175, 55, 0.3) 100%)';
                break;
            case 'navy-silver':
                styles.background = 'linear-gradient(135deg, rgba(26, 31, 59, 0.3) 0%, rgba(192, 192, 192, 0.2) 100%)';
                break;
            case 'rose-gold':
                styles.background = 'linear-gradient(135deg, rgba(230, 179, 197, 0.3) 0%, rgba(212, 175, 55, 0.2) 100%)';
                break;
        }

        return styles;
    }

    updateFloralLayer() {
        const floralLayer = this.layers.get('floral');
        if (!floralLayer) return;

        const density = this.currentDesign.floral || 3;

        // Clear existing floral elements
        floralLayer.innerHTML = '';

        // Generate floral elements based on density
        const floralCount = Math.max(5, density * 8);

        for (let i = 0; i < floralCount; i++) {
            const flower = this.createFlowerElement(i, density);
            floralLayer.appendChild(flower);
        }
    }

    createFlowerElement(index, density) {
        const flower = document.createElement('div');
        flower.className = 'flower';
        flower.dataset.index = index;

        // Random positioning within the floral area
        const x = Math.random() * 80 + 10; // 10% to 90%
        const y = Math.random() * 60 + 10; // 10% to 70%

        // Size based on density (higher density = smaller flowers)
        const size = Math.max(8, 20 - density * 2);

        // Random flower types
        const flowerTypes = ['🌸', '🌺', '🌹', '🌷', '🌼', '💐'];
        const flowerType = flowerTypes[Math.floor(Math.random() * flowerTypes.length)];

        Object.assign(flower.style, {
            position: 'absolute',
            left: `${x}%`,
            top: `${y}%`,
            fontSize: `${size}px`,
            opacity: Math.random() * 0.5 + 0.3, // 0.3 to 0.8
            transform: `rotate(${Math.random() * 360}deg)`,
            animationDelay: `${Math.random() * 2}s`,
            pointerEvents: 'none'
        });

        flower.textContent = flowerType;
        return flower;
    }

    updateLightingLayer() {
        const lightingLayer = this.layers.get('lighting');
        if (!lightingLayer) return;

        const lighting = this.currentDesign.lighting;

        // Clear existing lighting effects
        lightingLayer.innerHTML = '';

        // Add lighting effects based on type
        const effects = this.createLightingEffects(lighting);
        effects.forEach(effect => lightingLayer.appendChild(effect));
    }

    createLightingEffects(lighting) {
        const effects = [];

        switch (lighting) {
            case 'warm':
                // Warm golden glow
                effects.push(this.createLightGlow('#D4AF37', 0.4));
                break;
            case 'cool':
                // Cool blue-white glow
                effects.push(this.createLightGlow('#E6F3FF', 0.3));
                break;
            case 'dramatic':
                // Purple-pink dramatic lighting
                effects.push(this.createLightGlow('#8B5CF6', 0.5));
                effects.push(this.createLightGlow('#EC4899', 0.3));
                break;
        }

        return effects;
    }

    createLightGlow(color, opacity) {
        const glow = document.createElement('div');
        glow.className = 'light-glow';

        Object.assign(glow.style, {
            position: 'absolute',
            top: '20%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '120%',
            height: '60%',
            background: `radial-gradient(ellipse, ${color}${Math.floor(opacity * 255).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
            borderRadius: '50%',
            pointerEvents: 'none',
            mixBlendMode: 'screen'
        });

        return glow;
    }

    updatePropsLayer() {
        const propsLayer = this.layers.get('props');
        if (!propsLayer) return;

        // Update arch
        const arch = propsLayer.querySelector('.arch');
        if (arch) {
            this.updateArchStyle(arch);
        }

        // Update seating
        const seating = propsLayer.querySelector('.seating');
        if (seating) {
            this.updateSeatingStyle(seating);
        }
    }

    updateArchStyle(arch) {
        const archType = this.currentDesign.arch;

        // Clear existing classes
        arch.className = 'prop arch';

        // Add arch-specific class
        arch.classList.add(`arch-${archType}`);

        // Update styles
        const archStyles = this.getArchStyles(archType);
        Object.assign(arch.style, archStyles);
    }

    getArchStyles(archType) {
        const styles = {};

        switch (archType) {
            case 'classic':
                styles.background = 'linear-gradient(45deg, transparent 40%, var(--color-accent) 40%, var(--color-accent) 60%, transparent 60%)';
                break;
            case 'floral':
                styles.background = 'linear-gradient(45deg, transparent 30%, var(--color-secondary) 30%, var(--color-secondary) 40%, var(--color-accent) 40%, var(--color-accent) 60%, var(--color-secondary) 60%, var(--color-secondary) 70%, transparent 70%)';
                break;
            case 'modern':
                styles.background = 'linear-gradient(45deg, transparent 35%, var(--color-dark) 35%, var(--color-dark) 45%, var(--color-accent) 45%, var(--color-accent) 55%, var(--color-dark) 55%, var(--color-dark) 65%, transparent 65%)';
                break;
        }

        return styles;
    }

    updateSeatingStyle(seating) {
        const seatingType = this.currentDesign.seating;

        // Clear existing classes
        seating.className = 'prop seating';

        // Add seating-specific class
        seating.classList.add(`seating-${seatingType}`);

        // Update styles
        const seatingStyles = this.getSeatingStyles(seatingType);
        Object.assign(seating.style, seatingStyles);
    }

    getSeatingStyles(seatingType) {
        const styles = {};

        switch (seatingType) {
            case 'classic':
                styles.setProperty('--seating-color', 'var(--color-primary)');
                break;
            case 'luxury':
                styles.setProperty('--seating-color', 'var(--color-accent)');
                break;
            case 'contemporary':
                styles.setProperty('--seating-color', 'var(--color-dark)');
                break;
        }

        return styles;
    }

    updateFloorLayer() {
        const floorLayer = this.layers.get('floor');
        if (!floorLayer) return;

        const floorType = this.currentDesign.floor;

        // Clear existing classes
        floorLayer.className = 'layer floor';

        // Add floor-specific class
        floorLayer.classList.add(`floor-${floorType}`);

        // Update background pattern
        const floorPattern = this.getFloorPattern(floorType);
        floorLayer.style.background = floorPattern;
    }

    getFloorPattern(floorType) {
        switch (floorType) {
            case 'floral':
                return `repeating-linear-gradient(
                    45deg,
                    var(--color-bg-light),
                    var(--color-bg-light) 10px,
                    transparent 10px,
                    transparent 20px,
                    var(--color-secondary) 20px,
                    var(--color-secondary) 30px,
                    transparent 30px,
                    transparent 40px
                )`;
            case 'geometric':
                return `repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 20px,
                    var(--color-bg-light) 20px,
                    var(--color-bg-light) 40px
                ),
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 20px,
                    var(--color-bg-light) 20px,
                    var(--color-bg-light) 40px
                )`;
            case 'plain':
            default:
                return 'var(--color-bg-light)';
        }
    }

    updateCanvasAccessibility() {
        if (!this.canvas) return;

        const summary = designEngine.getDesignSummary();
        const description = `Event decor design featuring ${summary.stage.replace('-', ' ')} stage, ${summary.theme.replace('-', ' ')} color theme, ${summary.lighting} lighting, and ${summary.complexity} floral arrangements.`;

        this.canvas.setAttribute('aria-label', description);
    }

    handleReset() {
        // Special handling for reset - clear any cached states
        this.layers.forEach((element) => {
            if (element) {
                element.style.transition = 'none';
                setTimeout(() => {
                    element.style.transition = '';
                }, 50);
            }
        });
    }

    handleResize() {
        // Handle canvas resizing
        this.queueRender();
    }

    // Utility methods
    takeScreenshot() {
        return new Promise((resolve, reject) => {
            if (!this.canvas) {
                reject(new Error('Canvas not found'));
                return;
            }

            // Use html2canvas or similar library in production
            // For now, return a placeholder
            resolve({
                dataUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77yQAAAABJRU5ErkJggg==',
                width: this.canvas.offsetWidth,
                height: this.canvas.offsetHeight
            });
        });
    }

    getCanvasBounds() {
        if (!this.canvas) return null;

        const rect = this.canvas.getBoundingClientRect();
        return {
            width: rect.width,
            height: rect.height,
            top: rect.top,
            left: rect.left
        };
    }

    // Performance monitoring
    getRenderStats() {
        return {
            lastRenderTime: this.lastRenderTime,
            isRendering: this.isRendering,
            targetFPS: this.targetFPS
        };
    }
}

// Global instance
const designRenderer = new DesignRenderer();
