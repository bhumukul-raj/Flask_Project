(function() {
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize Bootstrap components
        const navbarToggler = document.getElementById('navbarToggler');
        if (navbarToggler) {
            navbarToggler.addEventListener('click', function() {
                const navbarNav = document.getElementById('navbarNav');
                const bsCollapse = new bootstrap.Collapse(navbarNav, {
                    toggle: true
                });
            });
        }

        const userDropdown = document.getElementById('userDropdown');
        if (userDropdown) {
            new bootstrap.Dropdown(userDropdown);
        }

        // Initialize loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('d-none');
        }

        // Initialize error handler
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.init();
        }
        
        // Initialize Bootstrap toasts
        const toastElList = document.querySelectorAll('.toast');
        toastElList.forEach(toast => {
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: 5000
            });
            bsToast.show();

            // Handle close button
            const closeBtn = toast.querySelector('#toastClose');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    bsToast.hide();
                });
            }
        });

        // Track AJAX requests
        let activeRequests = 0;
        
        function updateLoadingOverlay() {
            if (loadingOverlay) {
                if (activeRequests > 0) {
                    loadingOverlay.classList.remove('d-none');
                } else {
                    loadingOverlay.classList.add('d-none');
                }
            }
        }

        // Track XMLHttpRequest
        const originalXHR = window.XMLHttpRequest;
        function newXHR() {
            const xhr = new originalXHR();
            xhr.addEventListener('loadstart', function() {
                activeRequests++;
                updateLoadingOverlay();
            });
            xhr.addEventListener('loadend', function() {
                activeRequests = Math.max(0, activeRequests - 1);
                updateLoadingOverlay();
            });
            return xhr;
        }
        window.XMLHttpRequest = newXHR;
    });
})(); 