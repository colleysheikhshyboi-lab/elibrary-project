/**
 * National Assembly e-Library - Main JavaScript
 * Modern frontend functionality with animations, skeleton loaders, and enhanced UX
 */

// ============================
// Utility Functions
// ============================

const ELibrary = {
    // API endpoint base
    API_BASE: '/api/v1/',
    
    // Toast notification system
    showToast: function(message, type = 'info') {
        const toastContainer = document.createElement('div');
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1100';
        
        const toastId = 'toast-' + Date.now();
        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-info'
        }[type] || 'bg-info';
        
        const iconClass = {
            'success': 'check-circle-fill',
            'error': 'exclamation-circle-fill',
            'warning': 'exclamation-triangle-fill',
            'info': 'info-circle-fill'
        }[type] || 'info-circle-fill';
        
        toastContainer.innerHTML = `
            <div id="${toastId}" class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header ${bgClass} text-white">
                    <i class="bi bi-${iconClass} me-2"></i>
                    <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body bg-white text-dark">
                    ${message}
                </div>
            </div>
        `;
        
        document.body.appendChild(toastContainer);
        
        const toastEl = document.getElementById(toastId);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toastEl.classList.remove('show');
            setTimeout(() => toastContainer.remove(), 300);
        }, 5000);
        
        // Manual close
        toastEl.querySelector('.btn-close').addEventListener('click', () => {
            toastEl.classList.remove('show');
            setTimeout(() => toastContainer.remove(), 300);
        });
    },
    
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Debounce function for search
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
    
    // Copy text to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copied to clipboard!', 'success');
        }).catch(err => {
            this.showToast('Failed to copy text', 'error');
        });
    },
    
    // Show loading indicator
    showLoading: function(container) {
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="loading-spinner mb-3"></div>
                <p class="text-muted">Loading...</p>
            </div>
        `;
    },
    
    // Show skeleton loader
    showSkeleton: function(container, type = 'card', count = 1) {
        let html = '';
        for (let i = 0; i < count; i++) {
            switch(type) {
                case 'card':
                    html += `
                        <div class="col">
                            <div class="card">
                                <div class="skeleton skeleton-image"></div>
                                <div class="card-body">
                                    <div class="skeleton skeleton-title"></div>
                                    <div class="skeleton skeleton-text" style="width: 80%"></div>
                                    <div class="skeleton skeleton-text" style="width: 60%"></div>
                                </div>
                            </div>
                        </div>
                    `;
                    break;
                case 'list':
                    html += `
                        <div class="skeleton" style="height: 60px; margin-bottom: 10px; border-radius: 10px;"></div>
                    `;
                    break;
                case 'table':
                    html += `
                        <div class="skeleton" style="height: 40px; margin-bottom: 8px; border-radius: 6px;"></div>
                        <div class="skeleton" style="height: 40px; margin-bottom: 8px; border-radius: 6px;"></div>
                        <div class="skeleton" style="height: 40px; margin-bottom: 8px; border-radius: 6px;"></div>
                    `;
                    break;
            }
        }
        container.innerHTML = html;
    },
    
    // Confirm action
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Get URL parameter
    getUrlParam: function(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    },
    
    // Set URL parameter
    setUrlParam: function(name, value) {
        const url = new URL(window.location);
        url.searchParams.set(name, value);
        window.history.pushState({}, '', url);
    },
    
    // Remove URL parameter
    removeUrlParam: function(name) {
        const url = new URL(window.location);
        url.searchParams.delete(name);
        window.history.pushState({}, '', url);
    },
    
    // Smooth scroll to element
    smoothScrollTo: function(element, offset = 0) {
        const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    },
    
    // Initialize animations
    initAnimations: function() {
        // Fade up animation on scroll
        const fadeElements = document.querySelectorAll('.fade-up');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });
        
        fadeElements.forEach(el => observer.observe(el));
    }
};

// ============================
// Document Functions
// ============================

const DocumentManager = {
    // Track document view
    trackView: function(documentId) {
        fetch(`/documents/${documentId}/view/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCsrfToken(),
                'Content-Type': 'application/json'
            }
        }).catch(err => console.log('View tracking failed:', err));
    },
    
    // Track document download
    trackDownload: function(documentId) {
        fetch(`/documents/${documentId}/download/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCsrfToken(),
                'Content-Type': 'application/json'
            }
        }).catch(err => console.log('Download tracking failed:', err));
    },
    
    // Share document
    shareDocument: function(documentId, method) {
        const url = window.location.origin + '/documents/' + documentId + '/';
        
        switch(method) {
            case 'copy':
                ELibrary.copyToClipboard(url);
                break;
            case 'email':
                window.location.href = `mailto:?subject=National Assembly Document&body=${encodeURIComponent(url)}`;
                break;
            case 'twitter':
                window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}`, '_blank');
                break;
            case 'facebook':
                window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
                break;
        }
    },
    
    // Get CSRF token
    getCsrfToken: function() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }
};

// ============================
// Search Functions
// ============================

const SearchManager = {
    // Initialize search
    init: function() {
        const searchInput = document.getElementById('documentSearch');
        if (!searchInput) return;
        
        searchInput.addEventListener('input', ELibrary.debounce((e) => {
            this.performSearch(e.target.value);
        }, 300));
        
        // Clear search on escape
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clearResults();
                searchInput.value = '';
            }
        });
    },
    
    // Perform search
    performSearch: function(query) {
        if (!query || query.length < 2) {
            this.clearResults();
            return;
        }
        
        const resultsContainer = document.getElementById('searchResults');
        if (!resultsContainer) return;
        
        // Show skeleton
        ELibrary.showSkeleton(resultsContainer, 'list', 5);
        
        fetch(`/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.text())
            .then(html => {
                // Fade in results
                resultsContainer.style.opacity = '0';
                resultsContainer.innerHTML = html;
                setTimeout(() => {
                    resultsContainer.style.transition = 'opacity 0.3s ease';
                    resultsContainer.style.opacity = '1';
                }, 50);
            })
            .catch(err => {
                resultsContainer.innerHTML = '<p class="text-center text-muted p-3">Search failed. Please try again.</p>';
            });
    },
    
    // Clear search results
    clearResults: function() {
        const resultsContainer = document.getElementById('searchResults');
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }
    }
};

// ============================
// Upload Functions
// ============================

const UploadManager = {
    // Initialize file upload
    init: function() {
        const fileInput = document.getElementById('documentFile');
        if (!fileInput) return;
        
        fileInput.addEventListener('change', (e) => {
            this.validateFile(e.target.files[0]);
        });
        
        // Drag and drop
        const dropZone = fileInput.closest('.drop-zone') || document.body;
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                this.validateFile(e.dataTransfer.files[0]);
            }
        });
    },
    
    // Validate file
    validateFile: function(file) {
        if (!file) return;
        
        const maxSize = 100 * 1024 * 1024; // 100MB
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
            'application/rtf',
            'image/jpeg',
            'image/png',
            'image/tiff'
        ];
        
        if (file.size > maxSize) {
            ELibrary.showToast('File size exceeds 100MB limit', 'error');
            this.resetFile();
            return;
        }
        
        if (!allowedTypes.includes(file.type)) {
            ELibrary.showToast('Invalid file type. Please upload PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, RTF, JPG, PNG, or TIFF files.', 'error');
            this.resetFile();
            return;
        }
        
        // Show file info with animation
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            fileInfo.innerHTML = `
                <div class="alert alert-success mb-0 animate-scale-in">
                    <i class="bi bi-file-earmark-check me-2"></i>
                    <strong>${file.name}</strong>
                    <span class="text-muted">(${ELibrary.formatFileSize(file.size)})</span>
                    <button type="button" class="btn-close float-end" onclick="UploadManager.resetFile()"></button>
                </div>
            `;
        }
    },
    
    // Reset file input
    resetFile: function() {
        const fileInput = document.getElementById('documentFile');
        if (fileInput) {
            fileInput.value = '';
        }
        
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            fileInfo.innerHTML = '';
        }
    },
    
    // Bulk upload
    bulkUpload: function(files) {
        const progressContainer = document.getElementById('uploadProgress');
        if (!progressContainer) return;
        
        progressContainer.innerHTML = `
            <div class="progress" style="height: 20px; border-radius: 10px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%">0%</div>
            </div>
        `;
        
        let completed = 0;
        const total = files.length;
        
        Array.from(files).forEach((file, index) => {
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/documents/upload/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': DocumentManager.getCsrfToken()
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                completed++;
                const percent = Math.round((completed / total) * 100);
                
                const progressBar = progressContainer.querySelector('.progress-bar');
                progressBar.style.width = percent + '%';
                progressBar.textContent = percent + '%';
                
                if (completed === total) {
                    progressBar.classList.remove('progress-bar-striped', 'progress-bar-animated');
                    progressBar.classList.add('bg-success');
                    ELibrary.showToast('All files uploaded successfully!', 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            })
            .catch(err => {
                ELibrary.showToast(`Failed to upload ${file.name}`, 'error');
                completed++;
            });
        });
    }
};

// ============================
// User Functions
// ============================

const UserManager = {
    // Update profile
    updateProfile: function(formData) {
        fetch('/accounts/profile/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': DocumentManager.getCsrfToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(formData))
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                ELibrary.showToast('Profile updated successfully!', 'success');
            } else {
                ELibrary.showToast('Failed to update profile', 'error');
            }
        })
        .catch(err => {
            ELibrary.showToast('An error occurred', 'error');
        });
    },
    
    // Change password
    changePassword: function(oldPassword, newPassword, confirmPassword) {
        if (newPassword !== confirmPassword) {
            ELibrary.showToast('Passwords do not match', 'error');
            return;
        }
        
        if (newPassword.length < 12) {
            ELibrary.showToast('Password must be at least 12 characters', 'error');
            return;
        }
        
        fetch('/accounts/change-password/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': DocumentManager.getCsrfToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password1: newPassword,
                new_password2: confirmPassword
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                ELibrary.showToast('Password changed successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/accounts/login/';
                }, 2000);
            } else {
                ELibrary.showToast(data.error || 'Failed to change password', 'error');
            }
        })
        .catch(err => {
            ELibrary.showToast('An error occurred', 'error');
        });
    }
};

// ============================
// Modal Functions
// ============================

const ModalManager = {
    // Initialize all modals
    init: function() {
        // Add animation to modals
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                modal.querySelector('.modal-content').classList.add('animate-scale-in');
            });
            
            // Close on backdrop click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    bootstrap.Modal.getInstance(modal)?.hide();
                }
            });
        });
    },
    
    // Show modal by ID
    show: function(modalId) {
        const modalEl = document.getElementById(modalId);
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    },
    
    // Hide modal by ID
    hide: function(modalId) {
        const modalEl = document.getElementById(modalId);
        if (modalEl) {
            bootstrap.Modal.getInstance(modalEl)?.hide();
        }
    }
};

// ============================
// Dark Mode Manager
// ============================

const DarkModeManager = {
    // Storage key
    STORAGE_KEY: 'elibrary-dark-mode',
    
    // Initialize dark mode
    init: function() {
        // Load saved preference or check system preference
        const savedPreference = localStorage.getItem(this.STORAGE_KEY);
        
        if (savedPreference !== null) {
            // Use saved preference
            if (savedPreference === 'true') {
                this.enable();
            } else {
                this.disable();
            }
        } else {
            // Check system preference
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.enable();
            } else {
                this.disable();
            }
        }
        
        // Listen for system preference changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                // Only change if user hasn't set a preference
                if (localStorage.getItem(this.STORAGE_KEY) === null) {
                    if (e.matches) {
                        this.enable();
                    } else {
                        this.disable();
                    }
                }
            });
        }
    },
    
    // Enable dark mode
    enable: function() {
        document.body.classList.add('dark-mode');
        this.updateToggleIcon(true);
    },
    
    // Disable dark mode
    disable: function() {
        document.body.classList.remove('dark-mode');
        this.updateToggleIcon(false);
    },
    
    // Toggle dark mode
    toggle: function() {
        if (document.body.classList.contains('dark-mode')) {
            this.disable();
            localStorage.setItem(this.STORAGE_KEY, 'false');
        } else {
            this.enable();
            localStorage.setItem(this.STORAGE_KEY, 'true');
        }
    },
    
    // Update toggle button icon based on current mode
    updateToggleIcon: function(isDark) {
        const toggleBtn = document.getElementById('darkModeToggle');
        if (!toggleBtn) return;
        
        const sunIcon = toggleBtn.querySelector('.bi-sun-fill');
        const moonIcon = toggleBtn.querySelector('.bi-moon-fill');
        
        if (isDark) {
            if (sunIcon) sunIcon.style.display = 'inline-block';
            if (moonIcon) moonIcon.style.display = 'none';
        } else {
            if (sunIcon) sunIcon.style.display = 'none';
            if (moonIcon) moonIcon.style.display = 'inline-block';
        }
    },
    
    // Check if dark mode is enabled
    isEnabled: function() {
        return document.body.classList.contains('dark-mode');
    }
};

// ============================
// Navbar Scroll Effect
// ============================

const NavbarManager = {
    init: function() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
};

// ============================
// Card Hover Effects
// ============================

const CardAnimation = {
    init: function() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {
            // Only add effect if card doesn't already have custom hover
            if (!card.classList.contains('no-hover-effect')) {
                card.addEventListener('mouseenter', () => {
                    card.style.transform = 'translateY(-4px)';
                });
                card.addEventListener('mouseleave', () => {
                    card.style.transform = '';
                });
            }
        });
    }
};

// ============================
// Chart Initialization
// ============================

const ChartManager = {
    // Initialize charts if Chart.js is loaded
    init: function() {
        if (typeof Chart === 'undefined') return;
        
        // Set default options
        Chart.defaults.font.family = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif";
        Chart.defaults.color = '#6c757d';
        
        // Gender distribution chart
        const genderChart = document.getElementById('genderChart');
        if (genderChart && genderChart.dataset.values) {
            const values = JSON.parse(genderChart.dataset.values);
            new Chart(genderChart, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(values),
                    datasets: [{
                        data: Object.values(values),
                        backgroundColor: ['#0c2340', '#ce1126', '#6c757d'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // Party breakdown chart
        const partyChart = document.getElementById('partyChart');
        if (partyChart && partyChart.dataset.values) {
            const values = JSON.parse(partyChart.dataset.values);
            const colors = ['#0c2340', '#ce1126', '#3c8d2f', '#ffc107', '#6f42c1', '#17a2b8'];
            new Chart(partyChart, {
                type: 'bar',
                data: {
                    labels: Object.keys(values),
                    datasets: [{
                        label: 'Members',
                        data: Object.values(values),
                        backgroundColor: colors.slice(0, Object.keys(values).length),
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }
    }
};

// ============================
// Back to Top Button
// ============================

const BackToTop = {
    init: function() {
        // Create button
        const btn = document.createElement('button');
        btn.id = 'backToTop';
        btn.className = 'btn btn-primary position-fixed';
        btn.style.cssText = 'bottom: 30px; right: 30px; z-index: 1000; width: 50px; height: 50px; border-radius: 50%; display: none; box-shadow: 0 4px 15px rgba(12, 35, 64, 0.3);';
        btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        document.body.appendChild(btn);
        
        // Show/hide on scroll
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                btn.style.display = 'block';
                btn.style.animation = 'fadeIn 0.3s ease';
            } else {
                btn.style.display = 'none';
            }
        });
        
        // Scroll to top on click
        btn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
};

// ============================
// Copy to Clipboard
// ============================

const ClipboardManager = {
    init: function() {
        // Add click to copy functionality
        document.querySelectorAll('[data-copy]').forEach(el => {
            el.style.cursor = 'pointer';
            el.addEventListener('click', () => {
                const text = el.dataset.copy || el.textContent;
                ELibrary.copyToClipboard(text.trim());
            });
        });
    }
};

// ============================
// Initialize on DOM Ready
// ============================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    DarkModeManager.init();
    
    // Initialize navbar scroll effect
    NavbarManager.init();
    
    // Initialize search
    SearchManager.init();
    
    // Initialize upload
    UploadManager.init();
    
    // Initialize modals
    ModalManager.init();
    
    // Initialize card animations
    CardAnimation.init();
    
    // Initialize charts
    ChartManager.init();
    
    // Initialize back to top button
    BackToTop.init();
    
    // Initialize clipboard
    ClipboardManager.init();
    
    // Initialize animations
    ELibrary.initAnimations();
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    popoverTriggerList.forEach(popoverTriggerEl => {
        new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds with animation
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                const alertInstance = bootstrap.Alert.getInstance(alert);
                if (alertInstance) {
                    alertInstance.close();
                }
            }, 300);
        }, 5000);
    });
    
    // Add staggered animation to cards
    const cards = document.querySelectorAll('.row .col, .feature-card, .stat-card');
    cards.forEach((card, index) => {
        card.classList.add('fade-up');
        card.style.animationDelay = (index * 0.1) + 's';
    });
});

// ============================
// Export for global use
// ============================

window.ELibrary = ELibrary;
window.DocumentManager = DocumentManager;
window.SearchManager = SearchManager;
window.UploadManager = UploadManager;
window.UserManager = UserManager;
window.ModalManager = ModalManager;
window.DarkModeManager = DarkModeManager;
window.NavbarManager = NavbarManager;
window.CardAnimation = CardAnimation;
window.ChartManager = ChartManager;
window.BackToTop = BackToTop;
window.ClipboardManager = ClipboardManager;

