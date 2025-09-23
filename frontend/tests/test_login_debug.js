/**
 * Debug Login Test
 */

const axios = require('axios');

async function debugLogin() {
    console.log('🔍 Debugging Login...');

    const apiUrl = 'http://127.0.0.1:8000';

    try {
        // First register a user
        const uniqueEmail = `test_user_${Date.now()}@example.com`;
        const username = `testuser_${Date.now()}`;

        const registerData = {
            username: username,
            email: uniqueEmail,
            password: 'testpass123',
            password_confirm: 'testpass123',
            first_name: 'Test',
            last_name: 'User',
            phone_number: `+1${Date.now().toString().slice(-9)}`
        };

        console.log('\\n1. Registering user...');
        const registerResponse = await axios.post(`${apiUrl}/api/v1/auth/register/`, registerData);
        console.log('Registration status:', registerResponse.status);

        if (registerResponse.status === 201) {
            console.log('\\n2. Testing login with email...');
            const loginData1 = {
                email: uniqueEmail,
                password: 'testpass123'
            };

            try {
                const loginResponse1 = await axios.post(`${apiUrl}/api/v1/auth/login/`, loginData1);
                console.log('Login with email - Status:', loginResponse1.status);
                if (loginResponse1.status === 200) {
                    console.log('✅ Login with email successful');
                }
            } catch (error) {
                console.log('❌ Login with email failed:', error.response?.data?.message || error.message);
            }

            console.log('\\n3. Testing login with username...');
            const loginData2 = {
                username: username,
                password: 'testpass123'
            };

            try {
                const loginResponse2 = await axios.post(`${apiUrl}/api/v1/auth/login/`, loginData2);
                console.log('Login with username - Status:', loginResponse2.status);
                if (loginResponse2.status === 200) {
                    console.log('✅ Login with username successful');
                }
            } catch (error) {
                console.log('❌ Login with username failed:', error.response?.data?.message || error.message);
            }
        }

    } catch (error) {
        console.log('\\n❌ Registration failed:');
        console.log('Status:', error.response?.status);
        console.log('Data:', error.response?.data);
    }
}

debugLogin().catch(console.error);
