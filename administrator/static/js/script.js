// NDMA Reporting - Standalone App
class NdmaReportingApp {
	constructor() {
		this.storageKey = 'ndmaReports';
		this.reports = JSON.parse(localStorage.getItem(this.storageKey)) || [];
		this.init();
	}

	init() {
		this.bindEvents();
		this.renderReports();
	}

	bindEvents() {
		const form = document.getElementById('ndmaForm');
		if (form) {
			form.addEventListener('submit', (e) => {
				e.preventDefault();
				this.submitReport();
			});
		}

		const toastClose = document.getElementById('toastClose');
		if (toastClose) {
			toastClose.addEventListener('click', () => this.hideToast());
		}
	}

	submitReport() {
		const form = document.getElementById('ndmaForm');
		const data = new FormData(form);

		const report = {
			id: Date.now().toString(),
			collegeName: data.get('collegeName'),
			collegeCode: data.get('collegeCode'),
			contactPerson: data.get('contactPerson'),
			contactEmail: data.get('contactEmail'),
			disasterType: data.get('disasterType'),
			severity: data.get('severity'),
			affectedCount: Number(data.get('affectedCount') || 0),
			safeCount: Number(data.get('safeCount') || 0),
			resourcesNeeded: data.get('resourcesNeeded'),
			situationSummary: data.get('situationSummary'),
			student: {
				name: data.get('studentName'),
				id: data.get('studentId'),
				phone: data.get('studentPhone'),
				email: data.get('studentEmail')
			},
			createdAt: new Date().toISOString()
		};

		this.reports.unshift(report);
		this.saveReports();
		this.renderReports();

		// Simulate sending to NDMA endpoint
		setTimeout(() => {
			console.log('Report sent to NDMA:', report);
		}, 50);

		this.showToast('Report submitted to NDMA');
		form.reset();
	}

	renderReports() {
		const container = document.getElementById('reportsList');
		if (!container) return;

		if (this.reports.length === 0) {
			container.innerHTML = `
				<div class="no-notifications">
					<i class="fas fa-bell-slash"></i>
					<p>No reports submitted yet</p>
				</div>
			`;
			return;
		}

		container.innerHTML = this.reports.map(r => `
			<div class="notification-item fade-in" data-id="${r.id}">
				<div class="notification-header">
					<div class="notification-title">${r.collegeName} • ${r.disasterType} (${r.severity})</div>
					<div class="notification-time">${this.formatTime(r.createdAt)}</div>
				</div>
				<div class="notification-message">${r.situationSummary}</div>
				<div class="notification-participants">Officer: ${r.contactPerson} &lt;${r.contactEmail}&gt;</div>
				<div class="notification-participants">Students: affected ${r.affectedCount}, safe ${r.safeCount}</div>
				${r.resourcesNeeded ? `<div class="notification-participants">Needs: ${r.resourcesNeeded}</div>` : ''}
				<div class="notification-participants">Reporting student: ${r.student.name}${r.student.id ? ` (${r.student.id})` : ''}${r.student.email ? ` • ${r.student.email}` : ''}</div>
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

	saveReports() {
		localStorage.setItem(this.storageKey, JSON.stringify(this.reports));
	}
}

document.addEventListener('DOMContentLoaded', () => {
	new NdmaReportingApp();
});


