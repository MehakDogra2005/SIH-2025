document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const userType = document.querySelector('input[name="userType"]:checked').value;

        if (!email || !password) {
            alert('Please fill in all fields');
            return;
        }

        let API_BASE_URL;
        if (userType === 'student') {
            API_BASE_URL = 'http://localhost:5003/api/auth';
        } else {
            API_BASE_URL = 'http://localhost:5001/api/auth';
        }

        console.log(`🔐 Attempting ${userType} login to: ${API_BASE_URL}/login`);
        console.log(`Email: ${email}, UserType: ${userType}`);

        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, userType })
            });

            console.log('Response status:', response.status);
            console.log('Response OK:', response.ok);

            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('Non-JSON response:', text);
                alert('Server error: Invalid response format');
                return;
            }

            const data = await response.json();
            console.log('Response data:', data);

            if (response.ok) {
                localStorage.setItem('resq_token', data.token);
                localStorage.setItem('resq_user', JSON.stringify(data.user));
                alert('Login successful! Redirecting to dashboard...');

                if (userType === 'student') {
                    window.location.href = '/student/dashboard-student.html';
                } else {
                    window.location.href = 'http://localhost:5001/dashboard';
                }
            } else {
                alert(data.message || `Login failed with status: ${response.status}`);
            }
        } catch (error) {
            console.error('Network error details:', error);
            alert(`Network error: ${error.message}. Please check if server is running on port ${userType === 'student' ? '5003' : '5001'}`);
        }
    });
});