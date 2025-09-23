document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const API_BASE_URL = 'http://localhost:5000/api/auth';

    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const userType = document.querySelector('input[name="userType"]:checked').value;

        // Simple validation
        if (!email || !password) {
            alert('Please fill in all fields');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, userType })
            });

            const data = await response.json();

            if (response.ok) {
                // ✅ UPDATED: Use the redirectUrl from server response
                if (data.redirectUrl) {
                    // Store token and user data
                    localStorage.setItem('resq_token', data.token);
                    localStorage.setItem('resq_user', JSON.stringify(data.user));

                    alert('Login successful! Redirecting to dashboard...');

                    // Redirect to the URL provided by server
                    window.location.href = data.redirectUrl;
                } else {
                    // Fallback for old response format
                    localStorage.setItem('resq_token', data.token);
                    localStorage.setItem('resq_user', JSON.stringify(data.user));
                    alert('Login successful! Redirecting to dashboard...');

                    if (userType === 'student') {
                        window.location.href = '/student/dashboard-student.html';
                    } else {
                        window.location.href = 'http://localhost:5001/dashboard';
                    }
                }
            } else {
                alert(data.message || 'Login failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Network error. Please try again.');
        }
    });
});