document.addEventListener('DOMContentLoaded', function () {
    const signupForm = document.getElementById('signupForm');
    const API_BASE_URL = 'http://localhost:5001/api/auth';

    // Show/hide admin fields based on user type selection
    document.querySelectorAll('input[name="userType"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const adminFields = document.getElementById('adminFields');
            const phoneInput = document.getElementById('phoneNumber');
            const departmentInput = document.getElementById('department');
            const floorInput = document.getElementById('floor');

            if (this.value === 'admin') {
                adminFields.style.display = 'block';
                phoneInput.required = true;
                departmentInput.required = true;
                floorInput.required = true;
            } else {
                adminFields.style.display = 'none';
                phoneInput.required = false;
                departmentInput.required = false;
                floorInput.required = false;
            }
        });
    });

    signupForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const firstName = document.getElementById('firstName').value;
        const lastName = document.getElementById('lastName').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const institution = document.getElementById('institution').value;
        const userType = document.querySelector('input[name="userType"]:checked').value;
        const agreeTerms = document.getElementById('agreeTerms').checked;

        // Validation
        if (!firstName || !lastName || !email || !password || !confirmPassword || !institution) {
            alert('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }

        if (!agreeTerms) {
            alert('You must agree to the terms and conditions');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    firstName,
                    lastName,
                    email,
                    password,
                    institution,
                    userType,
                    ...(userType === 'admin' && {
                        phoneNumber: document.getElementById('phoneNumber').value || undefined,
                        department: document.getElementById('department').value || undefined,
                        floor: document.getElementById('floor').value ? parseInt(document.getElementById('floor').value) : 0
                    })
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Store token and user data
                localStorage.setItem('resq_token', data.token);
                localStorage.setItem('resq_user', JSON.stringify(data.user));

                alert('Account created successfully! Please login to access your dashboard :D');

                // Redirect based on user type
                if (userType === 'student') {
                    window.location.href = 'login.html';
                } else {
                    // window.location.href = 'admin-dashboard.html';
                }
            } else {
                alert(data.message || 'Registration failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Network error. Please try again.');
        }
    });
});