// Global variables
let currentFloor = null;
let allTeachers = [];

// Function to format teacher card HTML
function formatTeacherCard(teacher) {
    if (!teacher || !teacher.firstName) return '';

    return `
        <div class="contact-card">
            <div class="contact-icon action-campus">
                <i class="fas fa-user-tie"></i>
            </div>
            <div class="contact-info">
                <div class="contact-name">${teacher.firstName || ''} ${teacher.lastName || ''}</div>
                <div class="contact-role">${teacher.department || 'Department not assigned'}</div>
                <div class="contact-details">
                    <p><strong>Floor:</strong> ${teacher.floor === 0 ? 'Ground Floor' : `${['First', 'Second', 'Third', 'Fourth'][teacher.floor - 1] || `${teacher.floor}th`} Floor`}</p>
                    <p><strong>Phone:</strong> ${teacher.phoneNumber ? teacher.phoneNumber : '<span class="text-muted">Not available</span>'}</p>
                    <p><strong>Email:</strong> ${teacher.email || 'Email not available'}</p>
                </div>
            </div>
            ${teacher.phoneNumber ? `
                <div class="contact-actions">
                    <button class="btn btn-primary call-btn" data-number="${teacher.phoneNumber}">
                        <i class="fas fa-phone"></i> Call
                    </button>
                </div>
            ` : ''}
        </div>
    `;
}

// Function to get user's current floor
async function getCurrentUserFloor() {
    try {
        const token = localStorage.getItem('resq_token');
        if (!token) return null;

        const response = await fetch('http://localhost:5000/api/auth/current', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) return null;

        const userData = await response.json();
        return userData.floor || null;
    } catch (error) {
        console.error('Error getting user floor:', error);
        return null;
    }
}

// Function to load and display teachers
async function loadTeachers() {
    try {
        const token = localStorage.getItem('resq_token');
        if (!token) {
            window.location.href = '/login.html';
            return;
        }
        console.log('Token found:', token);

        // Get current user's floor
        currentFloor = await getCurrentUserFloor();

        // Fetch all teachers
        const response = await fetch('http://localhost:5003/api/admin/teachers', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch teachers');
        }

        const data = await response.json();
        console.log('API Response:', data);

        // Define default departments and floors
        const defaultDepartments = ['CSE', 'IT', 'MAE', 'ECE', 'AIML'];
        const floors = ['Ground', 'First', 'Second', 'Third'];

        // Convert the object of arrays into a single array and add dummy data
        allTeachers = [];
        let phoneCounter = 1;

        Object.values(data).forEach(teachers => {
            if (Array.isArray(teachers)) {
                const teachersWithData = teachers.map(teacher => {
                    // Get random department and floor if not assigned
                    const randomDept = defaultDepartments[Math.floor(Math.random() * defaultDepartments.length)];
                    const randomFloorIndex = Math.floor(Math.random() * floors.length);

                    return {
                        ...teacher,
                        phoneNumber: teacher.phoneNumber || `+91-9876543${String(phoneCounter++).padStart(3, '0')}`,
                        department: teacher.department || randomDept,
                        floor: teacher.floor !== undefined ? teacher.floor : randomFloorIndex
                    };
                });
                allTeachers.push(...teachersWithData);
            }
        });
        console.log('Processed teachers data:', allTeachers);

        // Get unique departments from the data
        const departments = [...new Set(allTeachers.map(t => t.department))].sort();

        // Update department filter options
        const deptFilter = document.getElementById('departmentFilter');
        deptFilter.innerHTML = '<option value="">All Departments</option>' +
            departments.map(dept => `<option value="${dept}">${dept}</option>`).join('');

        // Display teachers in different sections
        displayCurrentFloorTeachers();
        displayAllTeachers();
        displayRecentTeachers();

        // Add event listeners for filters
        document.getElementById('departmentFilter').addEventListener('change', displayAllTeachers);
        document.getElementById('floorFilter').addEventListener('change', displayAllTeachers);

        // Add call button event listeners
        document.querySelectorAll('.call-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const number = this.dataset.number;
                // In a real app, this would initiate a phone call
                alert(`Calling ${number}...`);
            });
        });

    } catch (error) {
        console.error('Error loading teachers:', error);
        alert('Failed to load contacts. Please try again later.');
    }
}

// Function to display teachers on the current floor
function displayCurrentFloorTeachers() {
    const container = document.getElementById('current-floor-teachers');
    if (!container) return;

    const floorTeachers = currentFloor !== null ?
        allTeachers.filter(t => t.floor === currentFloor) : [];

    if (floorTeachers.length === 0) {
        container.innerHTML = '<p class="no-results">No teachers found on your floor.</p>';
        return;
    }

    container.innerHTML = floorTeachers.map(formatTeacherCard).join('');
}

// Function to display all teachers with filters
function displayAllTeachers() {
    const container = document.getElementById('all-teachers');
    if (!container) return;

    const selectedDept = document.getElementById('departmentFilter').value;
    const selectedFloor = document.getElementById('floorFilter').value;

    let filteredTeachers = [...allTeachers];

    if (selectedDept) {
        filteredTeachers = filteredTeachers.filter(t => t.department === selectedDept);
    }

    if (selectedFloor !== '') {
        filteredTeachers = filteredTeachers.filter(t => t.floor === parseInt(selectedFloor));
    }

    if (filteredTeachers.length === 0) {
        container.innerHTML = '<p class="no-results">No teachers found matching the selected criteria.</p>';
        return;
    }

    container.innerHTML = filteredTeachers.map(formatTeacherCard).join('');
}

// Function to display recently added teachers
function displayRecentTeachers() {
    const container = document.getElementById('recent-teachers');
    if (!container) return;

    // Sort teachers by creation date (newest first) and take the most recent 5
    const recentTeachers = [...allTeachers]
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        .slice(0, 5);

    if (recentTeachers.length === 0) {
        container.innerHTML = '<p class="no-results">No teachers have been added recently.</p>';
        return;
    }

    container.innerHTML = recentTeachers.map(formatTeacherCard).join('');
}

// Initialize when the document is loaded
document.addEventListener('DOMContentLoaded', loadTeachers);