// Test script to verify API endpoints
console.log('Testing API endpoints...');

// Function to make authenticated requests
async function testApi(endpoint) {
    const token = localStorage.getItem('resq_token');
    if (!token) {
        console.error('No auth token found. Please log in first.');
        return null;
    }

    try {
        const response = await fetch(`http://localhost:5003/api/${endpoint}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Error testing ${endpoint}:`, error);
        return null;
    }
}

// Test all endpoints
async function runTests() {
    console.log('1. Testing teachers endpoint...');
    const teachers = await testApi('admin/teachers');
    if (teachers) {
        console.log('✅ Teachers endpoint working');
        console.log('Teachers by floor:', teachers);
    }

    console.log('\n2. Testing departments endpoint...');
    const departments = await testApi('admin/departments');
    if (departments) {
        console.log('✅ Departments endpoint working');
        console.log('Available departments:', departments);
    }

    console.log('\n3. Testing current user endpoint...');
    const currentUser = await testApi('auth/current');
    if (currentUser) {
        console.log('✅ Current user endpoint working');
        console.log('Current user:', currentUser);
    }
}

// Add a test button to the page
const testButton = document.createElement('button');
testButton.textContent = 'Test API Connections';
testButton.style.position = 'fixed';
testButton.style.bottom = '20px';
testButton.style.right = '20px';
testButton.style.zIndex = '9999';
testButton.style.padding = '10px 20px';
testButton.style.backgroundColor = '#1a73e8';
testButton.style.color = 'white';
testButton.style.border = 'none';
testButton.style.borderRadius = '5px';
testButton.style.cursor = 'pointer';

testButton.addEventListener('click', runTests);
document.body.appendChild(testButton);

// Also expose the test function globally
window.testApiConnections = runTests;