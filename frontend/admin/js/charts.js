/**
 * Admin Charts
 * Handles chart creation and rendering for admin dashboard
 */

class AdminCharts {
    constructor() {
        this.charts = new Map();
    }

    /**
     * Create enquiry trends chart
     */
    createEnquiryChart(canvas) {
        if (!canvas) return;

        // Clear any existing chart
        this.destroyChart(canvas.id);

        // Mock chart data - replace with real Chart.js implementation
        const ctx = canvas.getContext('2d');
        const chartId = canvas.id;

        // Store chart instance
        this.charts.set(chartId, {
            canvas: canvas,
            type: 'enquiry',
            destroy: () => this.destroyChart(chartId)
        });

        // Simple bar chart implementation
        this.renderEnquiryChart(ctx, canvas.width, canvas.height);
    }

    /**
     * Create design status chart
     */
    createDesignChart(canvas) {
        if (!canvas) return;

        // Clear any existing chart
        this.destroyChart(canvas.id);

        // Mock chart data
        const ctx = canvas.getContext('2d');
        const chartId = canvas.id;

        // Store chart instance
        this.charts.set(chartId, {
            canvas: canvas,
            type: 'design',
            destroy: () => this.destroyChart(chartId)
        });

        // Simple pie chart implementation
        this.renderDesignChart(ctx, canvas.width, canvas.height);
    }

    /**
     * Render enquiry chart (bar chart)
     */
    renderEnquiryChart(ctx, width, height) {
        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Mock data
        const data = [
            { month: 'Jan', count: 45 },
            { month: 'Feb', count: 52 },
            { month: 'Mar', count: 38 },
            { month: 'Apr', count: 61 },
            { month: 'May', count: 55 },
            { month: 'Jun', count: 67 }
        ];

        const maxCount = Math.max(...data.map(d => d.count));
        const barWidth = (width - 60) / data.length;
        const chartHeight = height - 60;

        // Draw axes
        ctx.strokeStyle = '#ddd';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(30, 20);
        ctx.lineTo(30, height - 30);
        ctx.lineTo(width - 20, height - 30);
        ctx.stroke();

        // Draw bars
        data.forEach((item, index) => {
            const x = 40 + index * barWidth;
            const barHeight = (item.count / maxCount) * (chartHeight - 20);
            const y = height - 30 - barHeight;

            // Bar
            ctx.fillStyle = '#007bff';
            ctx.fillRect(x, y, barWidth - 10, barHeight);

            // Label
            ctx.fillStyle = '#666';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(item.month, x + (barWidth - 10) / 2, height - 15);

            // Value
            ctx.fillText(item.count.toString(), x + (barWidth - 10) / 2, y - 5);
        });

        // Title
        ctx.fillStyle = '#333';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Enquiry Trends (Last 6 Months)', width / 2, 15);
    }

    /**
     * Render design chart (pie chart)
     */
    renderDesignChart(ctx, width, height) {
        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Mock data
        const data = [
            { status: 'Completed', count: 28, color: '#28a745' },
            { status: 'In Progress', count: 15, color: '#ffc107' },
            { status: 'Pending', count: 12, color: '#dc3545' },
            { status: 'Draft', count: 8, color: '#6c757d' }
        ];

        const total = data.reduce((sum, item) => sum + item.count, 0);
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 2 - 40;

        let startAngle = -Math.PI / 2; // Start from top

        // Draw pie slices
        data.forEach((item) => {
            const sliceAngle = (item.count / total) * 2 * Math.PI;
            const endAngle = startAngle + sliceAngle;

            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, endAngle);
            ctx.closePath();
            ctx.fillStyle = item.color;
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Label
            const labelAngle = startAngle + sliceAngle / 2;
            const labelX = centerX + Math.cos(labelAngle) * (radius + 20);
            const labelY = centerY + Math.sin(labelAngle) * (radius + 20);

            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`${item.status}: ${item.count}`, labelX, labelY);

            startAngle = endAngle;
        });

        // Title
        ctx.fillStyle = '#333';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Design Status Distribution', centerX, 20);
    }

    /**
     * Update chart data
     */
    updateChart(chartId, data) {
        const chart = this.charts.get(chartId);
        if (!chart) return;

        // In a real implementation, this would update the chart with new data
        console.log(`Updating chart ${chartId} with data:`, data);
    }

    /**
     * Destroy chart
     */
    destroyChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            // Clean up
            chart.destroy();
            this.charts.delete(chartId);
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }

    /**
     * Resize chart
     */
    resizeChart(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;

        // In a real implementation, this would handle canvas resizing
        console.log(`Resizing chart ${chartId}`);
    }
}

// Initialize global AdminCharts instance
window.AdminCharts = new AdminCharts();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.AdminCharts) {
        window.AdminCharts.destroyAllCharts();
    }
});
