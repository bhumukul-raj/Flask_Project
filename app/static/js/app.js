/**
 * Main Application JavaScript
 */

const App = {
    init() {
        this.initializeTooltips();
        this.initializePopovers();
        this.setupDarkMode();
        this.setupFormValidation();
    },

    /**
     * Initialize Bootstrap tooltips
     */
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    /**
     * Initialize Bootstrap popovers
     */
    initializePopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },

    /**
     * Setup dark mode functionality
     */
    setupDarkMode() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            // Check for saved dark mode preference
            const darkMode = localStorage.getItem('darkMode') === 'true';
            document.body.classList.toggle('dark-mode', darkMode);
            darkModeToggle.checked = darkMode;

            // Handle dark mode toggle
            darkModeToggle.addEventListener('change', (e) => {
                document.body.classList.toggle('dark-mode', e.target.checked);
                localStorage.setItem('darkMode', e.target.checked);
            });
        }
    },

    /**
     * Setup form validation
     */
    setupFormValidation() {
        // Add custom validation styles
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });

        // Add custom validation messages
        document.addEventListener('invalid', (function(){
            return function(e) {
                e.preventDefault();
                const target = e.target;
                if (!target.validationMessage) return;
                
                ErrorHandler.handleFormErrors(target.form, {
                    [target.name]: target.validationMessage
                });
            };
        })(), true);
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    App.init();
}); 