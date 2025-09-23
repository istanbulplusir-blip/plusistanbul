// Simple test for profile update API
const axios = require('axios');

async function testProfileUpdate() {
  try {
    // Test 1: Direct API call to Django backend
    console.log('Testing direct API call to Django backend...');
    
    const directResponse = await axios.patch('http://localhost:8000/api/v1/auth/profile/', {
      first_name: 'Test User',
      last_name: 'Updated'
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN_HERE' // Replace with actual token
      }
    });
    
    console.log('✅ Direct API call successful:', directResponse.status);
    
    // Test 2: API call through Next.js proxy
    console.log('\nTesting API call through Next.js proxy...');
    
    const proxyResponse = await axios.patch('http://localhost:3000/api/v1/auth/profile/', {
      first_name: 'Test User',
      last_name: 'Updated via Proxy'
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN_HERE' // Replace with actual token
      },
      withCredentials: true
    });
    
    console.log('✅ Proxy API call successful:', proxyResponse.status);
    
  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
    console.error('Status:', error.response?.status);
    console.error('Headers:', error.response?.headers);
  }
}

// Run the test
testProfileUpdate(); 