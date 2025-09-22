// Drill Notification System JavaScript
class DrillNotificationSystem {
    constructor() {
        this.notifications = JSON.parse(localStorage.getItem('drillNotifications')) || [];
        this.scheduledDrills = JSON.parse(localStorage.getItem('scheduledDrills')) || [];
        this.notificationCount = this.notifications.filter(n => !n.read).length;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateNotificationBadge();
        this.renderNotifications();
        this.renderScheduledDrills();
        this.setMinDate();
    }

    bindEvents() {
        // Form submission
        document.getElementById('drillForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.scheduleDrill();
        });

        // Notification button
        document.getElementById('notificationBtn').addEventListener('click', () => {
            this.toggleNotifications();
        });

        // Clear notifications
        document.getElementById('clearNotifications').addEventListener('click', () => {
            this.clearAllNotifications();
        });

        // Toast close
        document.getElementById('toastClose').addEventListener('click', () => {
            this.hideToast();
        });
    }

    setMinDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('drillDate').setAttribute('min', today);
    }

    scheduleDrill() {
        const formData = new FormData(document.getElementById('drillForm'));
        const drillData = {
            id: Date.now().toString(),
            title: formData.get('drillTitle'),
            type: formData.get('drillType'),
            date: formData.get('drillDate'),
            time: formData.get('drillTime'),
            description: formData.get('drillDescription'),
            participants: formData.get('participants').split(',').map(email => email.trim()),
            createdAt: new Date().toISOString(),
            status: 'scheduled'
        };

        // Add to scheduled drills
        this.scheduledDrills.push(drillData);
        this.saveScheduledDrills();

        // Create notifications for all participants
        this.createNotificationsForDrill(drillData);

        // Show success message
        this.showToast(`Drill "${drillData.title}" scheduled successfully! Notifications sent to ${drillData.participants.length} participants.`);

        // Reset form
        document.getElementById('drillForm').reset();

        // Update UI
        this.renderScheduledDrills();
        this.renderNotifications();
        this.updateNotificationBadge();
    }

    createNotificationsForDrill(drillData) {
        const notification = {
            id: Date.now().toString(),
            title: `New Drill Scheduled: ${drillData.title}`,
            message: `A ${drillData.type} drill has been scheduled for ${this.formatDate(drillData.date)} at ${drillData.time}. ${drillData.description}`,
            type: 'drill_scheduled',
            drillId: drillData.id,
            createdAt: new Date().toISOString(),
            read: false,
            participants: drillData.participants
        };

        this.notifications.unshift(notification);
        this.saveNotifications();
        this.notificationCount++;

        // Simulate sending notifications to participants
        this.simulateNotificationSending(drillData.participants, drillData);
    }

    simulateNotificationSending(participants, drillData) {
        participants.forEach((email, index) => {
            setTimeout(() => {
                console.log(`Notification sent to: ${email}`);
                // In a real application, you would send actual notifications here
                // This could be via email, SMS, push notifications, etc.
            }, index * 100); // Stagger notifications
        });
    }

    renderNotifications() {
        const container = document.getElementById('notificationsList');
        
        if (this.notifications.length === 0) {
            container.innerHTML = `
                <div class="no-notifications">
                    <i class="fas fa-bell-slash"></i>
                    <p>No notifications yet</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.notifications.map(notification => `
            <div class="notification-item ${!notification.read ? 'unread' : ''} fade-in" data-id="${notification.id}">
                <div class="notification-header">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-time">${this.formatTime(notification.createdAt)}</div>
                </div>
                <div class="notification-message">${notification.message}</div>
                ${notification.participants ? `<div class="notification-participants">Sent to: ${notification.participants.join(', ')}</div>` : ''}
            </div>
        `).join('');

        // Add click handlers to mark as read
        container.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => {
                const notificationId = item.dataset.id;
                this.markNotificationAsRead(notificationId);
            });
        });
    }

    renderScheduledDrills() {
        const container = document.getElementById('drillsList');
        
        if (this.scheduledDrills.length === 0) {
            container.innerHTML = `
                <div class="no-drills">
                    <i class="fas fa-calendar-times"></i>
                    <p>No drills scheduled</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.scheduledDrills.map(drill => `
            <div class="drill-item fade-in">
                <div class="drill-header">
                    <div class="drill-title">${drill.title}</div>
                    <div class="drill-type">${this.getDrillTypeLabel(drill.type)}</div>
                </div>
                <div class="drill-details">
                    <div class="drill-detail">
                        <i class="fas fa-calendar"></i>
                        <span>${this.formatDate(drill.date)}</span>
                    </div>
                    <div class="drill-detail">
                        <i class="fas fa-clock"></i>
                        <span>${drill.time}</span>
                    </div>
                </div>
                ${drill.description ? `<div class="drill-description">${drill.description}</div>` : ''}
                <div class="drill-participants">
                    <i class="fas fa-users"></i>
                    <span>${drill.participants.length} participants</span>
                </div>
            </div>
        `).join('');
    }

    getDrillTypeLabel(type) {
        const labels = {
            'fire': 'Fire Drill',
            'earthquake': 'Earthquake Drill',
            'evacuation': 'Evacuation Drill',
            'security': 'Security Drill',
            'medical': 'Medical Emergency Drill'
        };
        return labels[type] || type;
    }

    markNotificationAsRead(notificationId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        if (notification && !notification.read) {
            notification.read = true;
            this.notificationCount--;
            this.saveNotifications();
            this.updateNotificationBadge();
            this.renderNotifications();
        }
    }

    clearAllNotifications() {
        this.notifications = [];
        this.notificationCount = 0;
        this.saveNotifications();
        this.updateNotificationBadge();
        this.renderNotifications();
        this.showToast('All notifications cleared');
    }

    toggleNotifications() {
        const notificationsSection = document.querySelector('.notifications-section');
        notificationsSection.scrollIntoView({ behavior: 'smooth' });
    }

    updateNotificationBadge() {
        const badge = document.getElementById('notificationBadge');
        badge.textContent = this.notificationCount;
        badge.style.display = this.notificationCount > 0 ? 'flex' : 'none';
    }

    showToast(message) {
        const toast = document.getElementById('toast');
        const messageElement = document.getElementById('toastMessage');
        
        messageElement.textContent = message;
        toast.classList.add('show');
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            this.hideToast();
        }, 5000);
    }

    hideToast() {
        const toast = document.getElementById('toast');
        toast.classList.remove('show');
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    saveNotifications() {
        localStorage.setItem('drillNotifications', JSON.stringify(this.notifications));
    }

    saveScheduledDrills() {
        localStorage.setItem('scheduledDrills', JSON.stringify(this.scheduledDrills));
    }
}

// Real-time notification simulation
class RealTimeNotificationSimulator {
    constructor(notificationSystem) {
        this.notificationSystem = notificationSystem;
        this.startSimulation();
    }

    startSimulation() {
        // Simulate random drill notifications every 30-60 seconds
        setInterval(() => {
            if (Math.random() < 0.3) { // 30% chance
                this.simulateRandomDrill();
            }
        }, 30000 + Math.random() * 30000);
    }

    simulateRandomDrill() {
        const drillTypes = ['fire', 'earthquake', 'evacuation', 'security', 'medical'];
        const randomType = drillTypes[Math.floor(Math.random() * drillTypes.length)];
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + Math.floor(Math.random() * 7) + 1);
        
        const drillData = {
            id: Date.now().toString(),
            title: `Emergency ${this.getDrillTypeLabel(randomType)}`,
            type: randomType,
            date: futureDate.toISOString().split('T')[0],
            time: `${String(Math.floor(Math.random() * 12) + 8).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
            description: 'Automated emergency drill notification for safety preparedness.',
            participants: ['admin@company.com', 'safety@company.com', 'manager@company.com'],
            createdAt: new Date().toISOString(),
            status: 'scheduled'
        };

        this.notificationSystem.scheduledDrills.push(drillData);
        this.notificationSystem.saveScheduledDrills();
        this.notificationSystem.createNotificationsForDrill(drillData);
        this.notificationSystem.renderScheduledDrills();
        this.notificationSystem.renderNotifications();
        this.notificationSystem.updateNotificationBadge();
        
        this.notificationSystem.showToast(`New ${this.getDrillTypeLabel(randomType)} scheduled automatically!`);
    }

    getDrillTypeLabel(type) {
        const labels = {
            'fire': 'Fire Drill',
            'earthquake': 'Earthquake Drill',
            'evacuation': 'Evacuation Drill',
            'security': 'Security Drill',
            'medical': 'Medical Emergency Drill'
        };
        return labels[type] || type;
    }
}

// Real-time notification handler
class RealTimeNotificationHandler {
    constructor(notificationSystem) {
        this.notificationSystem = notificationSystem;
        this.eventSource = null;
        this.init();
    }

    init() {
        // Check if we're in a server environment
        if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
            this.connectToServer();
        }
    }

    connectToServer() {
        try {
            this.eventSource = new EventSource('/events');
            
            this.eventSource.onopen = () => {
                console.log('Connected to real-time notification server');
            };

            this.eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleRealTimeNotification(data);
                } catch (error) {
                    console.error('Error parsing SSE data:', error);
                }
            };

            this.eventSource.onerror = (error) => {
                console.error('SSE connection error:', error);
                // Attempt to reconnect after 5 seconds
                setTimeout(() => {
                    if (this.eventSource.readyState === EventSource.CLOSED) {
                        this.connectToServer();
                    }
                }, 5000);
            };
        } catch (error) {
            console.error('Failed to connect to SSE:', error);
        }
    }

    handleRealTimeNotification(data) {
        if (data.type === 'connection') {
            console.log('Connected to notification system');
            return;
        }

        // Add notification to the system
        const notification = {
            id: data.id || Date.now().toString(),
            title: data.title,
            message: data.message,
            type: data.type || 'notification',
            drillId: data.drillId,
            createdAt: data.timestamp || new Date().toISOString(),
            read: false,
            participants: data.participants || []
        };

        this.notificationSystem.notifications.unshift(notification);
        this.notificationSystem.notificationCount++;
        this.notificationSystem.saveNotifications();
        this.notificationSystem.updateNotificationBadge();
        this.notificationSystem.renderNotifications();
        this.notificationSystem.showToast(`New notification: ${notification.title}`);

        // Show browser notification if permission is granted
        if (Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/favicon.ico'
            });
        }
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
        }
    }
}

// Initialize the system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const notificationSystem = new DrillNotificationSystem();
    
    // Initialize real-time notifications
    const realTimeHandler = new RealTimeNotificationHandler(notificationSystem);
    
    // Start real-time simulation (optional - for demo purposes)
    if (window.location.search.includes('demo=true')) {
        new RealTimeNotificationSimulator(notificationSystem);
    }
    
    // Add some demo data if no data exists
    if (notificationSystem.scheduledDrills.length === 0) {
        const demoDrill = {
            id: 'demo-1',
            title: 'Monthly Fire Safety Drill',
            type: 'fire',
            date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            time: '10:00',
            description: 'Regular monthly fire safety drill to ensure all staff are familiar with evacuation procedures.',
            participants: ['john@company.com', 'jane@company.com', 'mike@company.com'],
            createdAt: new Date().toISOString(),
            status: 'scheduled'
        };
        
        notificationSystem.scheduledDrills.push(demoDrill);
        notificationSystem.saveScheduledDrills();
        notificationSystem.createNotificationsForDrill(demoDrill);
        notificationSystem.renderScheduledDrills();
        notificationSystem.renderNotifications();
        notificationSystem.updateNotificationBadge();
    }
});

// Browser notification permission request
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            console.log('Browser notifications enabled');
        }
    });
}

// Service Worker registration for push notifications (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
