/**
 * National Assembly e-Library - Main JavaScript
 * Frontend functionality for the parliamentary document management system
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
        
        toastContainer.innerHTML = `
            <div id="${toastId}" class="toast ${bgClass} text-white" role="alert">
                <div class="toast-header ${bgClass} text-white">
                    <strong class="me-auto">
                        <i class="bi bi-${this.getToastIcon(type)}"></i>
                        ${type.charAt(0).toUpperCase() + type.slice(1)}
                    </strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        document.body.appendChild(toastContainer);
        
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
        
        toast.show();
        
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastContainer.remove();
        });
    },
    
    getToastIcon: function(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'x-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
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
    },
    
    // Perform search
    performSearch: function(query) {
        if (!query || query.length < 2) {
            this.clearResults();
            return;
        }
        
        const resultsContainer = document.getElementById('searchResults');
        if (!resultsContainer) return;
        
        ELibrary.showLoading(resultsContainer);
        
        fetch(`/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.text())
            .then(html => {
                resultsContainer.innerHTML = html;
            })
            .catch(err => {
                resultsContainer.innerHTML = '<p class="text-center text-muted">Search failed. Please try again.</p>';
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
        
        // Show file info
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            fileInfo.innerHTML = `
                <div class="alert alert-success mb-0">
                    <i class="bi bi-file-earmark"></i>
                    <strong>${file.name}</strong>
                    (${ELibrary.formatFileSize(file.size)})
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
            <div class="progress">
                <div class="progress-bar" role="progressbar" style="width: 0%">0%</div>
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
                const percent = (completed / total) * 100;
                
                progressContainer.querySelector('.progress-bar').style.width = percent + '%';
                progressContainer.querySelector('.progress-bar').textContent = percent.toFixed(0) + '%';
                
                if (completed === total) {
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
        // Add backdrop click handler to close modals
        document.querySelectorAll('.modal').forEach(modal => {
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
// Initialize on DOM Ready
// ============================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    DarkModeManager.init();
    
    // Initialize search
    SearchManager.init();
    
    // Initialize upload
    UploadManager.init();
    
    // Initialize modals
    ModalManager.init();
    
    // Add animation to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-2px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
    
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
    
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            const alertInstance = bootstrap.Alert.getInstance(alert);
            if (alertInstance) {
                alertInstance.close();
            }
        }, 5000);
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
