// Emergency Management System JavaScript

// Global variables
let emergencyMap;
let incidentMarkers = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize charts if on dashboard
    if (document.getElementById('incidentChart')) {
        initializeCharts();
    }

    // Initialize map if present
    if (document.getElementById('incidentMap')) {
        initializeMap();
    }

    // Auto-refresh dashboard stats
    if (window.location.pathname === '/dashboard') {
        setInterval(updateDashboardStats, 30000); // Update every 30 seconds
    }
}

// Emergency submission
function submitEmergency() {
    const form = document.getElementById('emergencyForm');
    const formData = new FormData(form);
    
    const emergencyData = {
        type: formData.get('type'),
        location: formData.get('location'),
        description: formData.get('description'),
        severity: formData.get('severity')
    };

    // Get user's location if available
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            emergencyData.latitude = position.coords.latitude;
            emergencyData.longitude = position.coords.longitude;
            sendEmergencyReport(emergencyData);
        }, function() {
            sendEmergencyReport(emergencyData);
        });
    } else {
        sendEmergencyReport(emergencyData);
    }
}

function sendEmergencyReport(data) {
    fetch('/api/incidents', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Emergency reported successfully! Authorities have been notified.', 'success');
            document.getElementById('emergencyForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('emergencyModal')).hide();
        } else {
            showAlert('Error reporting emergency. Please try again.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error reporting emergency. Please try again.', 'danger');
    });
}

// Quick check-in functionality
function quickCheckin(status) {
    const data = {
        status: status,
        location: 'Current Location'
    };

    fetch('/checkin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert(`Status updated: ${status.toUpperCase()}`, 'success');
        } else {
            showAlert('Error updating status. Please try again.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error updating status. Please try again.', 'danger');
    });
}

// Update incident status
function updateIncidentStatus(incidentId, status, assignedTo = null) {
    const data = { status: status };
    if (assignedTo) {
        data.assigned_to = assignedTo;
    }

    fetch(`/api/incidents/${incidentId}/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Incident status updated successfully!', 'success');
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert('Error updating incident status.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error updating incident status.', 'danger');
    });
}

// Dashboard statistics update
function updateDashboardStats() {
    fetch('/api/dashboard_stats')
    .then(response => response.json())
    .then(stats => {
        // Update stat cards
        const statElements = {
            'total-incidents': stats.total_incidents,
            'active-incidents': stats.active_incidents,
            'safe-checkins': stats.safe_checkins,
            'stuck-checkins': stats.stuck_checkins
        };

        Object.keys(statElements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = statElements[id];
            }
        });
    })
    .catch(error => {
        console.error('Error updating stats:', error);
    });
}

// Initialize charts
function initializeCharts() {
    // Incident Types Chart
    const incidentCtx = document.getElementById('incidentChart');
    if (incidentCtx) {
        new Chart(incidentCtx, {
            type: 'doughnut',
            data: {
                labels: ['Fire', 'Flood', 'Earthquake', 'Medical', 'Other'],
                datasets: [{
                    data: [12, 8, 5, 15, 10],
                    backgroundColor: [
                        '#e74c3c',
                        '#3498db',
                        '#f39c12',
                        '#27ae60',
                        '#9b59b6'
                    ],
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

    // Response Time Chart
    const responseCtx = document.getElementById('responseChart');
    if (responseCtx) {
        new Chart(responseCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Average Response Time (minutes)',
                    data: [8, 6, 7, 5, 6, 4],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Drill Participation Chart
    const drillCtx = document.getElementById('drillChart');
    if (drillCtx) {
        new Chart(drillCtx, {
            type: 'bar',
            data: {
                labels: ['Fire Drill', 'Earthquake', 'Evacuation', 'Medical'],
                datasets: [{
                    label: 'Participation %',
                    data: [85, 92, 78, 88],
                    backgroundColor: [
                        'rgba(231, 76, 60, 0.8)',
                        'rgba(243, 156, 18, 0.8)',
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(39, 174, 96, 0.8)'
                    ],
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// Initialize map
function initializeMap() {
    // This would typically use Google Maps or Mapbox
    // For now, we'll create a placeholder
    const mapContainer = document.getElementById('incidentMap');
    if (mapContainer) {
        mapContainer.innerHTML = `
            <div class="d-flex align-items-center justify-content-center h-100 bg-light">
                <div class="text-center">
                    <i class="fas fa-map-marked-alt fa-3x text-muted mb-3"></i>
                    <p class="text-muted">Interactive Map</p>
                    <small class="text-muted">Incident locations will be displayed here</small>
                </div>
            </div>
        `;
    }
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertContainer.style.cssText = 'top: 90px; right: 20px; z-index: 1060; min-width: 300px;';
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

// Filter incidents
function filterIncidents() {
    const type = document.getElementById('typeFilter').value;
    const status = document.getElementById('statusFilter').value;
    
    const url = new URL(window.location.href);
    if (type) {
        url.searchParams.set('type', type);
    } else {
        url.searchParams.delete('type');
    }
    
    if (status) {
        url.searchParams.set('status', status);
    } else {
        url.searchParams.delete('status');
    }
    
    window.location.href = url.toString();
}

// Export data
function exportData(type) {
    let endpoint = '';
    let filename = '';
    
    switch (type) {
        case 'incidents':
            endpoint = '/api/export/incidents';
            filename = 'incidents_export.csv';
            break;
        case 'checkins':
            endpoint = '/api/export/checkins';
            filename = 'checkins_export.csv';
            break;
        case 'analytics':
            endpoint = '/api/export/analytics';
            filename = 'analytics_export.csv';
            break;
        default:
            return;
    }
    
    fetch(endpoint)
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Export error:', error);
        showAlert('Error exporting data', 'danger');
    });
}

// Search functionality
function searchItems(searchTerm, items) {
    const results = items.filter(item => 
        Object.values(item).some(value => 
            value.toString().toLowerCase().includes(searchTerm.toLowerCase())
        )
    );
    return results;
}

// Notification management
function markNotificationRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/read`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById(`notification-${notificationId}`).classList.add('opacity-50');
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

// File upload handling
function handleFileUpload(inputElement, callback) {
    const file = inputElement.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            callback(result.filename);
        } else {
            showAlert('Error uploading file', 'danger');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showAlert('Error uploading file', 'danger');
    });
}

// Real-time updates (would use WebSocket in production)
function startRealTimeUpdates() {
    // Simulate real-time updates
    setInterval(() => {
        updateDashboardStats();
        // Update incident list if on incidents page
        if (window.location.pathname === '/incidents') {
            // Refresh incident list
        }
    }, 10000); // Every 10 seconds
}

// Initialize real-time updates
if (window.location.pathname === '/dashboard' || window.location.pathname === '/incidents') {
    startRealTimeUpdates();
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add event listeners for form validation
document.addEventListener('input', function(e) {
    if (e.target.required && e.target.value.trim()) {
        e.target.classList.remove('is-invalid');
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + E for emergency
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        const emergencyModal = new bootstrap.Modal(document.getElementById('emergencyModal'));
        emergencyModal.show();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            bootstrap.Modal.getInstance(modal)?.hide();
        });
    }
});

// Auto-save form data
function autoSaveForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
        });
    });
    
    // Restore data on load
    const savedData = localStorage.getItem(`autosave_${formId}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = data[key];
            }
        });
    }
}

// Initialize auto-save for forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[id]');
    forms.forEach(form => {
        autoSaveForm(form.id);
    });
});

// Print functionality
function printReport(containerId) {
    const content = document.getElementById(containerId);
    if (!content) return;
    
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Emergency Report</title>');
    printWindow.document.write('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">');
    printWindow.document.write('</head><body>');
    printWindow.document.write(content.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}

// Dark mode toggle (optional feature)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Initialize dark mode from localStorage
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
