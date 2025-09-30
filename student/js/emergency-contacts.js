document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch and display teachers
    async function fetchTeachers() {
        try {
            const response = await fetch('http://localhost:5000/api/auth/teachers');
            const data = await response.json();

            // Get the floor teachers container
            const floorTeachersContainer = document.getElementById('floorTeachers');
            const allContactsContainer = document.getElementById('collegeContacts');

            if (data.teachers && data.teachers.length > 0) {
                // Group teachers by floor
                const teachersByFloor = data.teachers.reduce((acc, teacher) => {
                    const floor = teacher.floor || 'Unspecified';
                    if (!acc[floor]) acc[floor] = [];
                    acc[floor].push(teacher);
                    return acc;
                }, {});

                // Display teachers on the current floor
                const currentFloor = 1; // You can make this dynamic based on user's location
                const floorTeachers = teachersByFloor[currentFloor] || [];

                floorTeachersContainer.innerHTML = floorTeachers.map(teacher => `
                    <div class="contact-card">
                        <div class="contact-icon teacher">
                            <i class="fas fa-chalkboard-teacher"></i>
                        </div>
                        <div class="contact-info">
                            <h3>${teacher.firstName} ${teacher.lastName}</h3>
                            <p class="department">${teacher.department || 'Department not specified'}</p>
                            <p class="phone">${teacher.phoneNumber}</p>
                        </div>
                    </div>
                `).join('');

                // Display all college contacts
                allContactsContainer.innerHTML = data.teachers.map(teacher => `
                    <div class="contact-card">
                        <div class="contact-icon teacher">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <div class="contact-info">
                            <h3>${teacher.firstName} ${teacher.lastName}</h3>
                            <p class="department">${teacher.department || 'Department not specified'}</p>
                            <p class="floor">Floor: ${teacher.floor || 'Not specified'}</p>
                            <p class="phone">${teacher.phoneNumber}</p>
                        </div>
                    </div>
                `).join('');
            } else {
                floorTeachersContainer.innerHTML = '<p class="no-contacts">No teachers found on this floor</p>';
                allContactsContainer.innerHTML = '<p class="no-contacts">No college contacts available</p>';
            }
        } catch (error) {
            console.error('Error fetching teachers:', error);
            document.getElementById('floorTeachers').innerHTML = '<p class="error">Error loading contacts</p>';
            document.getElementById('collegeContacts').innerHTML = '<p class="error">Error loading contacts</p>';
        }
    }

    // Initial load
    fetchTeachers();

    // Refresh contacts every 5 minutes
    setInterval(fetchTeachers, 5 * 60 * 1000);
});