/**
 * COBS Bread Research Application
 * Frontend JavaScript
 */

class COBSResearchApp {
    constructor() {
        this.form = document.getElementById('research-form');
        this.submitBtn = document.getElementById('submit-btn');
        this.locationInput = document.getElementById('location');

        this.progressSection = document.getElementById('progress-section');
        this.resultsSection = document.getElementById('results-section');
        this.errorSection = document.getElementById('error-section');

        this.progressBar = document.getElementById('progress-bar');
        this.progressStatus = document.getElementById('progress-status');
        this.taskIdEl = document.getElementById('task-id');
        this.elapsedTimeEl = document.getElementById('elapsed-time');
        this.statusBadge = document.getElementById('status-badge');

        this.statLength = document.getElementById('stat-length');
        this.statTime = document.getElementById('stat-time');
        this.downloadBtn = document.getElementById('download-btn');
        this.newResearchBtn = document.getElementById('new-research-btn');
        this.retryBtn = document.getElementById('retry-btn');
        this.errorMessage = document.getElementById('error-message');

        this.platformTags = document.querySelectorAll('.platform-tag');

        this.taskId = null;
        this.pollInterval = null;
        this.startTime = null;
        this.elapsedInterval = null;

        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.newResearchBtn.addEventListener('click', () => this.resetForm());
        this.retryBtn.addEventListener('click', () => this.resetForm());
    }

    async handleSubmit(e) {
        e.preventDefault();

        const location = this.locationInput.value.trim();
        if (!location) return;

        this.setLoading(true);
        this.hideAllSections();

        try {
            const response = await fetch('/api/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ location }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to start research');
            }

            this.taskId = data.task_id;
            this.showProgress();
            this.startPolling();

        } catch (error) {
            this.showError(error.message);
            this.setLoading(false);
        }
    }

    showProgress() {
        this.progressSection.classList.remove('hidden');
        this.taskIdEl.textContent = this.taskId ? this.taskId.substring(0, 12) + '...' : '-';
        this.startTime = Date.now();
        this.updateElapsedTime();
        this.elapsedInterval = setInterval(() => this.updateElapsedTime(), 1000);
        this.animatePlatformTags();
    }

    updateElapsedTime() {
        if (!this.startTime) return;
        const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
        const mins = Math.floor(elapsed / 60);
        const secs = elapsed % 60;
        this.elapsedTimeEl.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    animatePlatformTags() {
        let index = 0;
        const animate = () => {
            if (!this.progressSection.classList.contains('hidden')) {
                this.platformTags.forEach((tag, i) => {
                    tag.classList.toggle('active', i === index % this.platformTags.length);
                });
                index++;
                setTimeout(animate, 800);
            }
        };
        animate();
    }

    startPolling() {
        this.pollInterval = setInterval(() => this.checkStatus(), 3000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        if (this.elapsedInterval) {
            clearInterval(this.elapsedInterval);
            this.elapsedInterval = null;
        }
    }

    async checkStatus() {
        try {
            const response = await fetch(`/api/research/${this.taskId}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to check status');
            }

            this.updateProgressUI(data);

            if (data.status === 'completed') {
                this.stopPolling();
                this.showResults(data);
            } else if (data.status === 'failed') {
                this.stopPolling();
                this.showError(data.error || 'Research failed');
            }

        } catch (error) {
            console.error('Polling error:', error);
        }
    }

    updateProgressUI(data) {
        const statusMessages = {
            'pending': 'Initializing research agent...',
            'running': 'Analyzing reviews across platforms...',
            'processing': 'Processing and synthesizing findings...',
            'completed': 'Research complete!',
            'failed': 'Research failed'
        };

        this.progressStatus.textContent = statusMessages[data.status] || data.status;
        this.statusBadge.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);

        // Estimate progress based on elapsed time (max ~20 mins typical)
        const elapsed = (Date.now() - this.startTime) / 1000;
        const estimatedProgress = Math.min(95, (elapsed / 1200) * 100);
        this.progressBar.style.width = `${estimatedProgress}%`;
    }

    showResults(data) {
        this.setLoading(false);
        this.progressSection.classList.add('hidden');
        this.resultsSection.classList.remove('hidden');

        const elapsed = Math.floor((Date.now() - this.startTime) / 1000 / 60);
        this.statLength.textContent = data.report_length ? data.report_length.toLocaleString() : '-';
        this.statTime.textContent = elapsed || '-';

        this.downloadBtn.href = `/api/download/${this.taskId}`;
        this.progressBar.style.width = '100%';
    }

    showError(message) {
        this.setLoading(false);
        this.progressSection.classList.add('hidden');
        this.errorSection.classList.remove('hidden');
        this.errorMessage.textContent = message;
    }

    hideAllSections() {
        this.progressSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
        this.errorSection.classList.add('hidden');
    }

    resetForm() {
        this.stopPolling();
        this.hideAllSections();
        this.setLoading(false);
        this.locationInput.value = '';
        this.progressBar.style.width = '0%';
        this.taskId = null;
        this.startTime = null;
        this.form.scrollIntoView({ behavior: 'smooth' });
    }

    setLoading(loading) {
        this.submitBtn.disabled = loading;
        this.submitBtn.classList.toggle('loading', loading);
        this.locationInput.disabled = loading;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new COBSResearchApp();
});
