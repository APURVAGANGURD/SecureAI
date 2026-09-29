/**
 * SecureAI Main JavaScript - Complete Version
 * Contains all frontend functionality for the cybersecurity toolkit
 */

// Main Application State
const SecureAI = {
    state: {
        currentTool: null,
        userPreferences: {},
        chatHistory: [],
        securityScore: null,
        darkMode: false
    },
    
    init: function() {
        this.initNavigation();
        this.initForms();
        this.initTooltips();
        this.initPasswordStrengthMeter();
        this.initTheme();
        this.initLocalStorage();
        this.initEventListeners();
        
        console.log('SecureAI initialized successfully');
    },
    
    // Navigation functionality
    initNavigation: function() {
        // Mobile navigation toggle
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', function() {
                navMenu.classList.toggle('active');
                this.setAttribute('aria-expanded', navMenu.classList.contains('active'));
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(event) {
                if (!event.target.closest('.navbar') && navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    navToggle.setAttribute('aria-expanded', 'false');
                }
            });
            
            // Close menu on escape key
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape' && navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    navToggle.setAttribute('aria-expanded', 'false');
                }
            });
        }
        
        // Update active nav link based on current page
        this.updateActiveNavLink();
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    },
    
    updateActiveNavLink: function() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link, .nav-dropdown-content a');
        
        navLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            if (linkPath && currentPath.includes(linkPath.replace('/', ''))) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    },
    
    // Form initialization and handling
    initForms: function() {
        // Password visibility toggle
        document.querySelectorAll('.password-toggle input[type="checkbox"]').forEach(toggle => {
            toggle.addEventListener('change', function() {
                const passwordInput = this.closest('.form-group').querySelector('.password-input');
                if (passwordInput) {
                    passwordInput.type = this.checked ? 'text' : 'password';
                }
            });
        });
        
        // Form validation
        document.querySelectorAll('form[novalidate]').forEach(form => {
            form.setAttribute('novalidate', 'novalidate');
            form.addEventListener('submit', this.validateForm.bind(this));
        });
        
        // Auto-save form data
        document.querySelectorAll('input, textarea, select').forEach(input => {
            input.addEventListener('change', this.autoSaveFormData.bind(this));
        });
        
        // Character counters for textareas
        document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
            this.initCharacterCounter(textarea);
        });
    },
    
    validateForm: function(event) {
        const form = event.target;
        let isValid = true;
        
        // Clear previous error messages
        form.querySelectorAll('.error-message').forEach(error => error.remove());
        form.querySelectorAll('.has-error').forEach(element => {
            element.classList.remove('has-error');
        });
        
        // Validate required fields
        form.querySelectorAll('[required]').forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                this.showFieldError(input, 'This field is required');
            }
        });
        
        // Validate email fields
        form.querySelectorAll('input[type="email"]').forEach(input => {
            if (input.value && !this.isValidEmail(input.value)) {
                isValid = false;
                this.showFieldError(input, 'Please enter a valid email address');
            }
        });
        
        // Validate URL fields
        form.querySelectorAll('input[type="url"]').forEach(input => {
            if (input.value && !this.isValidUrl(input.value)) {
                isValid = false;
                this.showFieldError(input, 'Please enter a valid URL');
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            event.stopPropagation();
            
            // Focus on first error field
            const firstError = form.querySelector('.has-error');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }
        
        return isValid;
    },
    
    showFieldError: function(input, message) {
        input.classList.add('has-error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = 'var(--danger-color)';
        errorDiv.style.fontSize = '0.85rem';
        errorDiv.style.marginTop = '0.25rem';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        
        input.parentNode.appendChild(errorDiv);
    },
    
    isValidEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    isValidUrl: function(url) {
        try {
            new URL(url);
            return true;
        } catch (_) {
            return false;
        }
    },
    
    initCharacterCounter: function(textarea) {
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.style.fontSize = '0.85rem';
        counter.style.color = 'var(--gray-color)';
        counter.style.textAlign = 'right';
        counter.style.marginTop = '0.25rem';
        
        textarea.parentNode.appendChild(counter);
        
        const updateCounter = () => {
            const currentLength = textarea.value.length;
            counter.textContent = `${currentLength}/${maxLength}`;
            
            if (currentLength > maxLength * 0.9) {
                counter.style.color = 'var(--warning-color)';
            } else if (currentLength > maxLength) {
                counter.style.color = 'var(--danger-color)';
            } else {
                counter.style.color = 'var(--gray-color)';
            }
        };
        
        textarea.addEventListener('input', updateCounter);
        updateCounter();
    },
    
    autoSaveFormData: function(event) {
        const input = event.target;
        const form = input.closest('form');
        
        if (form && form.id) {
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            
            localStorage.setItem(`secureai_form_${form.id}`, JSON.stringify(data));
            this.showNotification('Form data saved locally', 'success');
        }
    },
    
    // Tooltip functionality
    initTooltips: function() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip.bind(this));
            element.addEventListener('mouseleave', this.hideTooltip.bind(this));
            element.addEventListener('focus', this.showTooltip.bind(this));
            element.addEventListener('blur', this.hideTooltip.bind(this));
        });
    },
    
    showTooltip: function(event) {
        const element = event.target;
        const tooltipText = element.getAttribute('data-tooltip');
        
        if (!tooltipText) return;
        
        // Remove existing tooltip
        this.hideTooltip(event);
        
        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        tooltip.id = 'current-tooltip';
        
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        tooltip.style.position = 'absolute';
        tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
        tooltip.style.top = `${rect.top + scrollTop - tooltip.offsetHeight - 10}px`;
        
        // Show tooltip
        setTimeout(() => {
            tooltip.style.opacity = '1';
        }, 10);
        
        element.tooltipElement = tooltip;
    },
    
    hideTooltip: function(event) {
        const element = event.target;
        if (element.tooltipElement) {
            element.tooltipElement.remove();
            element.tooltipElement = null;
        }
        
        // Also remove any orphaned tooltips
        const orphanedTooltip = document.getElementById('current-tooltip');
        if (orphanedTooltip) {
            orphanedTooltip.remove();
        }
    },
    
    // Password strength meter
    initPasswordStrengthMeter: function() {
        document.querySelectorAll('.password-input').forEach(input => {
            if (input.hasAttribute('data-strength-meter')) {
                this.createPasswordStrengthMeter(input);
            }
        });
    },
    
    createPasswordStrengthMeter: function(passwordInput) {
        const container = document.createElement('div');
        container.className = 'password-strength-meter';
        
        const meterBar = document.createElement('div');
        meterBar.className = 'password-strength-meter-bar';
        
        const meterText = document.createElement('div');
        meterText.className = 'password-strength-meter-text';
        
        container.appendChild(meterBar);
        container.appendChild(meterText);
        
        passwordInput.parentNode.insertBefore(container, passwordInput.nextSibling);
        
        passwordInput.addEventListener('input', () => {
            this.updatePasswordStrengthMeter(passwordInput.value, meterBar, meterText);
        });
        
        // Initial update
        this.updatePasswordStrengthMeter(passwordInput.value, meterBar, meterText);
    },
    
    updatePasswordStrengthMeter: function(password, meterBar, meterText) {
        let score = 0;
        let feedback = '';
        let color = '#e74c3c'; // Red
        
        if (!password) {
            meterBar.style.width = '0%';
            meterText.textContent = 'Enter password';
            meterText.style.color = 'var(--gray-color)';
            return;
        }
        
        // Length check (max 30 points)
        if (password.length >= 12) score += 30;
        else if (password.length >= 8) score += 20;
        else if (password.length >= 6) score += 10;
        
        // Character variety (max 70 points)
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecial = /[^A-Za-z0-9]/.test(password);
        
        if (hasUpper && hasLower) score += 20;
        if (hasDigit) score += 20;
        if (hasSpecial) score += 30;
        
        // Deduct for common patterns
        const commonPatterns = [
            /(.)\1{2,}/, // Repeated characters
            /(123|abc|qwerty|password)/i, // Common sequences
            /^\d+$/, // Only numbers
            /^[a-zA-Z]+$/ // Only letters
        ];
        
        commonPatterns.forEach(pattern => {
            if (pattern.test(password)) {
                score = Math.max(0, score - 10);
            }
        });
        
        // Cap score at 100
        score = Math.min(100, score);
        
        // Update display
        meterBar.style.width = `${score}%`;
        
        // Determine strength level
        if (score >= 80) {
            color = '#27ae60'; // Green
            feedback = 'Strong password';
        } else if (score >= 60) {
            color = '#f39c12'; // Orange
            feedback = 'Medium strength';
        } else if (score >= 40) {
            color = '#e67e22'; // Dark orange
            feedback = 'Weak password';
        } else {
            feedback = 'Very weak password';
        }
        
        meterBar.style.backgroundColor = color;
        meterBar.style.transition = 'width 0.3s ease, background-color 0.3s ease';
        meterText.textContent = feedback;
        meterText.style.color = color;
    },
    
    // Theme management
    initTheme: function() {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('secureai_theme');
        if (savedTheme === 'dark') {
            this.enableDarkMode();
        }
        
        // Theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    },
    
    toggleTheme: function() {
        if (this.state.darkMode) {
            this.disableDarkMode();
        } else {
            this.enableDarkMode();
        }
    },
    
    enableDarkMode: function() {
        document.documentElement.setAttribute('data-theme', 'dark');
        this.state.darkMode = true;
        localStorage.setItem('secureai_theme', 'dark');
        this.showNotification('Dark mode enabled', 'success');
    },
    
    disableDarkMode: function() {
        document.documentElement.removeAttribute('data-theme');
        this.state.darkMode = false;
        localStorage.setItem('secureai_theme', 'light');
        this.showNotification('Light mode enabled', 'success');
    },
    
    // Local storage management
    initLocalStorage: function() {
        // Load saved preferences
        const savedPreferences = localStorage.getItem('secureai_preferences');
        if (savedPreferences) {
            this.state.userPreferences = JSON.parse(savedPreferences);
        }
        
        // Load chat history
        const savedChatHistory = localStorage.getItem('secureai_chat_history');
        if (savedChatHistory) {
            this.state.chatHistory = JSON.parse(savedChatHistory);
        }
        
        // Load security score
        const savedScore = localStorage.getItem('secureai_security_score');
        if (savedScore) {
            this.state.securityScore = JSON.parse(savedScore);
        }
    },
    
    saveToLocalStorage: function(key, data) {
        try {
            localStorage.setItem(`secureai_${key}`, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            this.showNotification('Could not save data', 'error');
            return false;
        }
    },
    
    // Event listeners
    initEventListeners: function() {
        // Window resize handling
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            this.handleKeyboardShortcuts(event);
        });
        
        // Before unload - save state
        window.addEventListener('beforeunload', () => {
            this.saveToLocalStorage('preferences', this.state.userPreferences);
            this.saveToLocalStorage('chat_history', this.state.chatHistory);
            this.saveToLocalStorage('security_score', this.state.securityScore);
        });
        
        // Online/offline detection
        window.addEventListener('online', () => {
            this.showNotification('You are back online', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.showNotification('You are offline. Some features may not work.', 'warning');
        });
    },
    
    handleResize: function() {
        // Close mobile menu on resize to desktop
        const navMenu = document.querySelector('.nav-menu');
        const navToggle = document.getElementById('navToggle');
        
        if (window.innerWidth > 768 && navMenu && navMenu.classList.contains('active')) {
            navMenu.classList.remove('active');
            if (navToggle) {
                navToggle.setAttribute('aria-expanded', 'false');
            }
        }
    },
    
    handleKeyboardShortcuts: function(event) {
        // Don't trigger shortcuts when user is typing in input fields
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }
        
        // Ctrl/Cmd + S to save
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            event.preventDefault();
            this.saveCurrentToolData();
        }
        
        // Ctrl/Cmd + K to focus search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (event.key === 'Escape') {
            this.closeAllModals();
        }
    },
    
    // API functions
    async analyzePasswordAPI(password) {
        try {
            const response = await fetch('/api/analyze-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password: password })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Password analysis error:', error);
            this.showNotification('Failed to analyze password. Please try again.', 'error');
            return null;
        }
    },
    
    async analyzePhishingAPI(message, sender = '') {
        try {
            const response = await fetch('/api/analyze-phishing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    sender: sender
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Phishing analysis error:', error);
            this.showNotification('Failed to analyze message. Please try again.', 'error');
            return null;
        }
    },
    
    async chatWithAI(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Chat error:', error);
            return 'Sorry, I encountered an error. Please try again.';
        }
    },
    
    async generateSecurePassword(length = 16) {
        try {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
            let password = '';
            const array = new Uint8Array(length);
            window.crypto.getRandomValues(array);
            
            for (let i = 0; i < length; i++) {
                password += chars[array[i] % chars.length];
            }
            
            return password;
        } catch (error) {
            console.error('Password generation error:', error);
            // Fallback to simpler method
            return this.generateSimplePassword(length);
        }
    },
    
    generateSimplePassword: function(length = 16) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
        let password = '';
        for (let i = 0; i < length; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return password;
    },
    
    // Utility functions
    copyToClipboard: function(text) {
        if (!navigator.clipboard) {
            // Fallback for older browsers
            return this.copyToClipboardFallback(text);
        }
        
        return navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard!', 'success');
            return true;
        }).catch(err => {
            console.error('Failed to copy: ', err);
            this.showNotification('Failed to copy to clipboard', 'error');
            return false;
        });
    },
    
    copyToClipboardFallback: function(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (successful) {
                this.showNotification('Copied to clipboard!', 'success');
                return true;
            } else {
                this.showNotification('Failed to copy to clipboard', 'error');
                return false;
            }
        } catch (err) {
            console.error('Fallback copy failed: ', err);
            document.body.removeChild(textArea);
            this.showNotification('Failed to copy to clipboard', 'error');
            return false;
        }
    },
    
    showNotification: function(message, type = 'info') {
        // Remove existing notifications
        document.querySelectorAll('.notification').forEach(notification => {
            notification.remove();
        });
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" aria-label="Close notification">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Add styles if not already present
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = this.getNotificationStyles();
            document.head.appendChild(style);
        }
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }
        }, 5000);
    },
    
    getNotificationIcon: function(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },
    
    getNotificationStyles: function() {
        return `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: var(--border-radius);
                color: white;
                font-weight: 500;
                transform: translateX(150%);
                transition: transform 0.3s ease;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                max-width: 400px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: inherit;
                cursor: pointer;
                padding: 0.25rem;
                margin-left: 1rem;
                opacity: 0.7;
                transition: opacity 0.2s ease;
            }
            
            .notification-close:hover {
                opacity: 1;
            }
            
            .notification-success {
                background-color: var(--success-color);
            }
            
            .notification-error {
                background-color: var(--danger-color);
            }
            
            .notification-warning {
                background-color: var(--warning-color);
            }
            
            .notification-info {
                background-color: var(--info-color);
            }
        `;
    },
    
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    formatBytes: function(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },
    
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Modal management
    showModal: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
            modal.setAttribute('aria-hidden', 'false');
            
            // Focus trap
            this.setupFocusTrap(modal);
            
            // Close on escape
            const closeOnEscape = (e) => {
                if (e.key === 'Escape') {
                    this.closeModal(modalId);
                }
            };
            modal.closeOnEscape = closeOnEscape;
            document.addEventListener('keydown', closeOnEscape);
        }
    },
    
    closeModal: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            modal.setAttribute('aria-hidden', 'true');
            
            // Remove escape listener
            if (modal.closeOnEscape) {
                document.removeEventListener('keydown', modal.closeOnEscape);
            }
        }
    },
    
    closeAllModals: function() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            modal.setAttribute('aria-hidden', 'true');
        });
    },
    
    setupFocusTrap: function(modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === firstElement) {
                            lastElement.focus();
                            e.preventDefault();
                        }
                    } else {
                        if (document.activeElement === lastElement) {
                            firstElement.focus();
                            e.preventDefault();
                        }
                    }
                }
            });
            
            firstElement.focus();
        }
    },
    
    // Export/import functionality
    exportData: function(data, filename = 'secureai-data.json') {
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        if (window.navigator.msSaveOrOpenBlob) {
            // IE/Edge
            window.navigator.msSaveOrOpenBlob(dataBlob, filename);
        } else {
            // Other browsers
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);
        }
        
        this.showNotification('Data exported successfully', 'success');
    },
    
    importData: function(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    resolve(data);
                    this.showNotification('Data imported successfully', 'success');
                } catch (error) {
                    reject(new Error('Invalid file format'));
                    this.showNotification('Invalid file format', 'error');
                }
            };
            
            reader.onerror = () => {
                reject(new Error('Failed to read file'));
                this.showNotification('Failed to read file', 'error');
            };
            
            reader.readAsText(file);
        });
    },
    
    // Security scoring
    calculateSecurityScore: function(answers) {
        // This is a simplified version - the actual logic is in the backend
        let score = 0;
        const maxScore = 50; // 10 questions * 5 max points
        
        // Calculate based on answers (1-5 scale, where 1 is best)
        Object.values(answers).forEach(answer => {
            const value = parseInt(answer);
            // Invert the score (1 becomes 5 points, 5 becomes 1 point)
            score += (6 - value);
        });
        
        // Convert to percentage
        const percentage = (score / maxScore) * 100;
        return Math.round(percentage);
    },
    
    // Accessibility features
    initAccessibility: function() {
        // Skip to main content link
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-to-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.style.position = 'absolute';
        skipLink.style.top = '-40px';
        skipLink.style.left = '0';
        skipLink.style.background = 'var(--primary-color)';
        skipLink.style.color = 'white';
        skipLink.style.padding = '8px';
        skipLink.style.zIndex = '1001';
        skipLink.style.textDecoration = 'none';
        
        skipLink.addEventListener('focus', function() {
            this.style.top = '0';
        });
        
        skipLink.addEventListener('blur', function() {
            this.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Add aria labels to icons without text
        document.querySelectorAll('i[aria-hidden="true"]').forEach(icon => {
            const parent = icon.parentElement;
            if (parent && !parent.getAttribute('aria-label')) {
                // Try to infer label from context
                if (parent.classList.contains('btn')) {
                    const text = parent.textContent.trim();
                    if (!text) {
                        parent.setAttribute('aria-label', icon.className.replace('fas fa-', '').replace('-', ' ') + ' button');
                    }
                }
            }
        });
    },
    
    // Analytics (anonymous, for improvement purposes only)
    trackEvent: function(category, action, label = null) {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                'event_category': category,
                'event_label': label
            });
        }
        
        // Also log to console in development
        if (process.env.NODE_ENV === 'development') {
            console.log(`Event: ${category} - ${action}${label ? ` - ${label}` : ''}`);
        }
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    SecureAI.init();
    
    // Additional tool-specific initializations
    initializeToolSpecificFeatures();
});

// Tool-specific initializations
function initializeToolSpecificFeatures() {
    // Password generator button
    const generatePasswordBtn = document.getElementById('generatePassword');
    if (generatePasswordBtn) {
        generatePasswordBtn.addEventListener('click', async function() {
            const passwordInput = document.getElementById('password');
            if (passwordInput) {
                const password = await SecureAI.generateSecurePassword(16);
                passwordInput.value = password;
                passwordInput.type = 'text';
                
                // Check the show password checkbox
                const showPasswordCheckbox = document.getElementById('showPassword');
                if (showPasswordCheckbox) {
                    showPasswordCheckbox.checked = true;
                }
                
                SecureAI.showNotification('Secure password generated', 'success');
                SecureAI.trackEvent('password_tool', 'generate_password');
            }
        });
    }
    
    // Load example buttons
    document.querySelectorAll('[id^="loadExample"]').forEach(button => {
        button.addEventListener('click', function() {
            const tool = this.closest('.tool-container').querySelector('h1').textContent;
            SecureAI.trackEvent('examples', 'load_example', tool);
        });
    });
    
    // Copy buttons
    document.querySelectorAll('.btn[onclick*="copyToClipboard"]').forEach(button => {
        const originalOnClick = button.getAttribute('onclick');
        button.removeAttribute('onclick');
        button.addEventListener('click', function() {
            const elementId = originalOnClick.match(/copyToClipboard\('([^']+)'\)/)[1];
            const element = document.getElementById(elementId);
            if (element) {
                SecureAI.copyToClipboard(element.textContent);
            }
        });
    });
    
    // Risk score calculation
    const calculateScoreBtn = document.getElementById('calculateScore');
    if (calculateScoreBtn) {
        calculateScoreBtn.addEventListener('click', function() {
            SecureAI.trackEvent('risk_assessment', 'calculate_score');
        });
    }
    
    // Chat functionality
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (message) {
                SecureAI.trackEvent('chat', 'send_message');
            }
        });
    }
    
    // Print functionality
    const printButtons = document.querySelectorAll('[onclick*="window.print"]');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            SecureAI.trackEvent('tools', 'print_page');
        });
    });
}

// Make SecureAI available globally for debugging
window.SecureAI = SecureAI;

// Service Worker registration for PWA capabilities
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js').then(function(registration) {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }, function(err) {
            console.log('ServiceWorker registration failed: ', err);
        });
    });
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    
    // Don't show error notification for development
    if (process.env.NODE_ENV !== 'development') {
        SecureAI.showNotification('An error occurred. Please try again.', 'error');
    }
});

// Unhandled promise rejection handling
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});