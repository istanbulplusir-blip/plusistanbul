// Test script to check authentication status
// Run this in browser console

console.log('=== Authentication Status Check ===');

// Check localStorage
console.log('localStorage keys:', Object.keys(localStorage));
console.log('access_token exists:', !!localStorage.getItem('access_token'));
console.log('refresh_token exists:', !!localStorage.getItem('refresh_token'));
console.log('user exists:', !!localStorage.getItem('user'));

// Check token content
const token = localStorage.getItem('access_token');
if (token) {
  console.log('Token length:', token.length);
  console.log('Token preview:', token.substring(0, 20) + '...');
  
  // Try to decode JWT (if it's a JWT)
  try {
    const parts = token.split('.');
    if (parts.length === 3) {
      const payload = JSON.parse(atob(parts[1]));
      console.log('Token payload:', payload);
    }
  } catch (e) {
    console.log('Token is not a valid JWT');
  }
}

// Check user data
const userData = localStorage.getItem('user');
if (userData) {
  try {
    const user = JSON.parse(userData);
    console.log('User data:', user);
  } catch (e) {
    console.log('Invalid user data in localStorage');
  }
}

// Test API call
console.log('\n=== Testing API Call ===');
fetch('http://localhost:8000/api/v1/auth/profile/', {
  headers: {
    'Authorization': `Bearer ${token || ''}`,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('API Response status:', response.status);
  return response.json();
})
.then(data => {
  console.log('API Response data:', data);
})
.catch(error => {
  console.log('API Error:', error);
});

console.log('=== End Check ==='); 