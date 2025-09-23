/**
 * Debug script for Agent Customer Creation
 * Run this in browser console on the agent customers page
 */

console.log('🔍 Starting Agent Customer Creation Debug...');

// Check if user is authenticated
function checkAuthentication() {
    console.log('📋 Checking Authentication...');
    
    // Check localStorage for tokens
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const userData = localStorage.getItem('user_data');
    
    console.log('Access Token:', accessToken ? '✅ Found' : '❌ Missing');
    console.log('Refresh Token:', refreshToken ? '✅ Found' : '❌ Missing');
    console.log('User Data:', userData ? '✅ Found' : '❌ Missing');
    
    if (userData) {
        try {
            const user = JSON.parse(userData);
            console.log('User Role:', user.role);
            console.log('Is Agent:', user.role === 'agent');
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
    
    return { accessToken, refreshToken, userData };
}

// Test API call directly
async function testApiCall() {
    console.log('🧪 Testing API Call...');
    
    const auth = checkAuthentication();
    
    if (!auth.accessToken) {
        console.error('❌ No access token found. Please login first.');
        return;
    }
    
    const customerData = {
        email: 'debug-test@example.com',
        first_name: 'Debug',
        last_name: 'Test',
        phone: '+1234567890',
        address: 'Debug Address',
        city: 'Debug City',
        country: 'Debug Country',
        customer_status: 'active',
        customer_tier: 'bronze',
        relationship_notes: 'Debug test customer'
    };
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${auth.accessToken}`
    };
    
    console.log('Request URL:', 'http://localhost:8000/api/v1/agents/customers/');
    console.log('Request Headers:', headers);
    console.log('Request Data:', customerData);
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/agents/customers/', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(customerData)
        });
        
        console.log('Response Status:', response.status);
        console.log('Response Headers:', Object.fromEntries(response.headers.entries()));
        
        const responseText = await response.text();
        console.log('Response Body:', responseText);
        
        if (response.ok) {
            console.log('✅ API call successful!');
            try {
                const data = JSON.parse(responseText);
                console.log('Parsed Response:', data);
            } catch (e) {
                console.log('Response is not JSON');
            }
        } else {
            console.error('❌ API call failed');
            try {
                const errorData = JSON.parse(responseText);
                console.error('Error Details:', errorData);
            } catch (e) {
                console.error('Error response is not JSON');
            }
        }
        
    } catch (error) {
        console.error('❌ Network Error:', error);
    }
}

// Check current page state
function checkPageState() {
    console.log('📄 Checking Page State...');
    
    // Check if we're on the right page
    const currentPath = window.location.pathname;
    console.log('Current Path:', currentPath);
    
    // Check for form elements
    const form = document.querySelector('form');
    const emailInput = document.querySelector('input[name="email"]');
    const firstNameInput = document.querySelector('input[name="first_name"]');
    const lastNameInput = document.querySelector('input[name="last_name"]');
    
    console.log('Form Element:', form ? '✅ Found' : '❌ Missing');
    console.log('Email Input:', emailInput ? '✅ Found' : '❌ Missing');
    console.log('First Name Input:', firstNameInput ? '✅ Found' : '❌ Missing');
    console.log('Last Name Input:', lastNameInput ? '✅ Found' : '❌ Missing');
    
    // Check for create button
    const createButton = document.querySelector('button[type="submit"]');
    console.log('Create Button:', createButton ? '✅ Found' : '❌ Missing');
    
    return { form, emailInput, firstNameInput, lastNameInput, createButton };
}

// Simulate form submission
function simulateFormSubmission() {
    console.log('🎭 Simulating Form Submission...');
    
    const pageState = checkPageState();
    
    if (!pageState.emailInput || !pageState.firstNameInput || !pageState.lastNameInput) {
        console.error('❌ Required form inputs not found');
        return;
    }
    
    // Fill form
    pageState.emailInput.value = 'simulation-test@example.com';
    pageState.firstNameInput.value = 'Simulation';
    pageState.lastNameInput.value = 'Test';
    
    console.log('✅ Form filled with test data');
    
    // Trigger form submission
    if (pageState.createButton) {
        console.log('🔄 Triggering form submission...');
        pageState.createButton.click();
    } else {
        console.error('❌ Create button not found');
    }
}

// Main debug function
async function runDebug() {
    console.log('🚀 Running Agent Customer Creation Debug...');
    console.log('='.repeat(50));
    
    // Step 1: Check authentication
    checkAuthentication();
    console.log('-'.repeat(30));
    
    // Step 2: Check page state
    checkPageState();
    console.log('-'.repeat(30));
    
    // Step 3: Test API call
    await testApiCall();
    console.log('-'.repeat(30));
    
    console.log('✅ Debug completed!');
    console.log('='.repeat(50));
}

// Export functions for manual testing
window.debugAgentCustomer = {
    runDebug,
    checkAuthentication,
    testApiCall,
    checkPageState,
    simulateFormSubmission
};

// Auto-run debug
runDebug();

console.log('💡 Available functions:');
console.log('- window.debugAgentCustomer.runDebug()');
console.log('- window.debugAgentCustomer.checkAuthentication()');
console.log('- window.debugAgentCustomer.testApiCall()');
console.log('- window.debugAgentCustomer.checkPageState()');
console.log('- window.debugAgentCustomer.simulateFormSubmission()');
