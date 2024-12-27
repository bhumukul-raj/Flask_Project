/**
 * Global error handling and logging utilities
 */

const ErrorHandler = {
    // Error types
    ERROR_TYPES: {
        VALIDATION: 'validation',
        NETWORK: 'network',
        AUTH: 'authentication',
        SERVER: 'server',
        CLIENT: 'client',
        DOM: 'dom'
    },

    // Error messages
    MESSAGES: {
        NETWORK_ERROR: 'Network connection error. Please check your connection.',
        SERVER_ERROR: 'Server error occurred. Please try again later.',
        AUTH_ERROR: 'Authentication error. Please log in again.',
        VALIDATION_ERROR: 'Please check your input and try again.',
        DOM_ERROR: 'UI rendering error. Please refresh the page.',
        UNKNOWN_ERROR: 'An unexpected error occurred.'
    },

    /**
     * Initialize error handling for the application
     */
    init() {
        // Global error handler
        window.onerror = (msg, url, lineNo, columnNo, error) => {
            this.logError('GLOBAL', error || msg, { url, lineNo, columnNo });
            return false;
        };

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.logError('PROMISE', event.reason);
        });

        // Handle network errors
        window.addEventListener('offline', () => {
            this.showError(this.MESSAGES.NETWORK_ERROR, this.ERROR_TYPES.NETWORK);
        });
    },

    /**
     * Log error to console and server
     * @param {string} type - Error type
     * @param {Error|string} error - Error object or message
     * @param {Object} context - Additional context
     */
    logError(type, error, context = {}) {
        const errorData = {
            type,
            timestamp: new Date().toISOString(),
            message: error.message || error,
            stack: error.stack,
            url: window.location.href,
            userAgent: navigator.userAgent,
            ...context
        };

        // Log to console in development
        if (process.env.NODE_ENV === 'development') {
            console.error('Error:', errorData);
        }

        // Send to server for logging
        this.sendErrorToServer(errorData);
    },

    /**
     * Send error to server for logging
     * @param {Object} errorData - Error data to send
     */
    async sendErrorToServer(errorData) {
        try {
            const response = await fetch('/api/log/error', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content
                },
                body: JSON.stringify(errorData)
            });

            if (!response.ok) {
                console.error('Failed to send error to server:', response.statusText);
            }
        } catch (e) {
            console.error('Error sending error to server:', e);
        }
    },

    /**
     * Show error message to user
     * @param {string} message - Error message to display
     * @param {string} type - Error type
     * @param {Object} options - Display options
     */
    showError(message, type = 'client', options = {}) {
        const {
            duration = 5000,
            isHTML = false,
            position = 'top-right'
        } = options;

        // Try to find existing toast container or create new one
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = `toast-container position-fixed ${position}`;
            document.body.appendChild(toastContainer);
        }

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast show alert alert-danger ${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        // Set content
        if (isHTML) {
            toast.innerHTML = message;
        } else {
            toast.textContent = message;
        }

        // Add close button
        const closeButton = document.createElement('button');
        closeButton.className = 'btn-close';
        closeButton.setAttribute('data-bs-dismiss', 'toast');
        closeButton.setAttribute('aria-label', 'Close');
        toast.appendChild(closeButton);

        // Add to container
        toastContainer.appendChild(toast);

        // Remove after duration
        setTimeout(() => {
            toast.remove();
            if (toastContainer.children.length === 0) {
                toastContainer.remove();
            }
        }, duration);
    },

    /**
     * Handle form validation errors
     * @param {HTMLFormElement} form - Form element
     * @param {Object} errors - Validation errors
     */
    handleFormErrors(form, errors) {
        // Clear existing errors
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(el => {
            el.remove();
        });

        // Add new error messages
        Object.entries(errors).forEach(([field, message]) => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = message;
                
                input.parentNode.appendChild(feedback);
            }
        });

        // Focus first error field
        form.querySelector('.is-invalid')?.focus();
    },

    /**
     * Handle AJAX request errors
     * @param {Error} error - Error object
     * @param {Function} callback - Optional callback function
     */
    handleAjaxError(error, callback = null) {
        let message = this.MESSAGES.UNKNOWN_ERROR;
        let type = this.ERROR_TYPES.NETWORK;

        if (error.response) {
            // Server responded with error
            const status = error.response.status;
            if (status === 401) {
                message = this.MESSAGES.AUTH_ERROR;
                type = this.ERROR_TYPES.AUTH;
                // Redirect to login if needed
                if (window.location.pathname !== '/login') {
                    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
                }
            } else if (status === 422) {
                message = this.MESSAGES.VALIDATION_ERROR;
                type = this.ERROR_TYPES.VALIDATION;
            } else if (status >= 500) {
                message = this.MESSAGES.SERVER_ERROR;
                type = this.ERROR_TYPES.SERVER;
            }
        } else if (error.request) {
            // Request made but no response
            message = this.MESSAGES.NETWORK_ERROR;
        }

        this.showError(message, type);
        this.logError(type, error);

        if (callback) {
            callback(error);
        }
    },

    /**
     * Safe DOM manipulation with error handling
     * @param {Function} operation - DOM operation to perform
     * @param {string} errorMessage - Error message if operation fails
     */
    safeDOMOperation(operation, errorMessage = 'DOM operation failed') {
        try {
            return operation();
        } catch (error) {
            this.logError(this.ERROR_TYPES.DOM, error);
            this.showError(errorMessage, this.ERROR_TYPES.DOM);
            return null;
        }
    }
}; 