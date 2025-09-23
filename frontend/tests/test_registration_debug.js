/**
 * Debug Registration Test
 */

const axios = require('axios');

async function debugRegistration() {
    console.log('🔍 Debugging Registration...');

    const apiUrl = 'http://127.0.0.1:8000';

    try {
        // First check what registration endpoint expects
        console.log('\\n1. Checking registration endpoint...');

        const uniqueEmail = `test_user_${Date.now()}@example.com`;

        const registerData = {
            username: `testuser_${Date.now()}`,
            email: uniqueEmail,
            password: 'testpass123',
            password_confirm: 'testpass123',
            first_name: 'Test',
            last_name: 'User',
            phone_number: `+1${Date.now().toString().slice(-9)}`
        };

        console.log('Registration data:', registerData);

        const response = await axios.post(`${apiUrl}/api/v1/auth/register/`, registerData);

        console.log('Response status:', response.status);
        console.log('Response data:', response.data);

    } catch (error) {
        console.log('\\n❌ Registration failed:');
        console.log('Status:', error.response?.status);
        console.log('Data:', error.response?.data);
        console.log('Message:', error.message);

        // Check if endpoint exists
        if (error.response?.status === 404) {
            console.log('\\n🔍 Checking available auth endpoints...');

            try {
                const optionsResponse = await axios.options(`${apiUrl}/api/v1/auth/`);
                console.log('Auth endpoints:', optionsResponse.data);
            } catch (e) {
                console.log('Could not get auth endpoints');
            }
        }
    }
}

debugRegistration().catch(console.error);
