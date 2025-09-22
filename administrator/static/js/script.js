// Parent Safety Notification - Standalone App
class ParentNotificationApp {
	constructor() {
		this.storageKey = 'parentNotifications';
		this.notifications = JSON.parse(localStorage.getItem(this.storageKey)) || [];
		this.init();
	}

	init() {
		this.bindEvents();
		this.renderNotifications();
	}

	bindEvents() {
		const parentForm = document.getElementById('parentForm');
		if (parentForm) {
			parentForm.addEventListener('submit', (e) => {
				e.preventDefault();
				this.sendParentSafetyUpdate();
			});
		}

		const toastClose = document.getElementById('toastClose');
		if (toastClose) {
			toastClose.addEventListener('click', () => this.hideToast());
		}
	}

	sendParentSafetyUpdate() {
		const form = document.getElementById('parentForm');
		const formData = new FormData(form);

		const studentName = formData.get('studentName');
		const status = formData.get('studentStatus');
		const location = formData.get('currentLocation');
		const additional = formData.get('additionalMessage');
		const parents = (formData.get('parentContacts') || '')
			.split(',')
			.map(e => e.trim())
			.filter(Boolean);

		if (parents.length === 0) {
			this.showToast('Please enter at least one parent contact');
			return;
		}

		const messageParts = [
			`${studentName} status: ${status}.`,
			location ? `Location: ${location}.` : '',
			additional ? `Note: ${additional}` : ''
		].filter(Boolean);

		const notification = {
			id: Date.now().toString(),
			title: `Safety Update: ${studentName}`,
			message: messageParts.join(' '),
			type: 'student_safety_update',
			createdAt: new Date().toISOString(),
			participants: parents
		};

		this.notifications.unshift(notification);
		this.saveNotifications();
		this.renderNotifications();

		parents.forEach((email, index) => {
			setTimeout(() => console.log(`Parent update sent to: ${email}`), index * 100);
		});

		this.showToast(`Safety update sent to ${parents.length} parent(s).`);
		form.reset();
	}

	renderNotifications() {
		const container = document.getElementById('notificationsList');
		if (!container) return;

		if (this.notifications.length === 0) {
			container.innerHTML = `
				<div class="no-notifications">
					<i class="fas fa-bell-slash"></i>
					<p>No notifications yet</p>
				</div>
			`;
			return;
		}

		container.innerHTML = this.notifications.map(n => `
			<div class="notification-item fade-in" data-id="${n.id}">
				<div class="notification-header">
					<div class="notification-title">${n.title}</div>
					<div class="notification-time">${this.formatTime(n.createdAt)}</div>
				</div>
				<div class="notification-message">${n.message}</div>
				${n.participants ? `<div class="notification-participants">Sent to: ${n.participants.join(', ')}</div>` : ''}
			</div>
		`).join('');
	}

	showToast(message) {
		const toast = document.getElementById('toast');
		const messageElement = document.getElementById('toastMessage');
		messageElement.textContent = message;
		toast.classList.add('show');
		setTimeout(() => this.hideToast(), 5000);
	}

	hideToast() {
		const toast = document.getElementById('toast');
		toast.classList.remove('show');
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
		localStorage.setItem(this.storageKey, JSON.stringify(this.notifications));
	}
}

document.addEventListener('DOMContentLoaded', () => {
	new ParentNotificationApp();
});


