// Test script for WhatsApp Support Component
// This script tests the API endpoint that the SupportModal component uses

async function testContactInfoAPI() {
  console.log('Testing Contact Info API...');
  
  try {
    // Test the correct API endpoint
    const response = await fetch('/api/v1/shared/contact-info/');
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ API call successful!');
      console.log('Contact Info Data:', data);
      
      // Check if required fields exist
      if (data.whatsapp_number && data.phone_primary) {
        console.log('✅ Required fields present');
        console.log('WhatsApp:', data.whatsapp_number);
        console.log('Phone:', data.phone_primary);
        console.log('Email:', data.email_support);
        console.log('Working Hours:', data.working_hours);
        console.log('Working Days:', data.working_days);
      } else {
        console.log('❌ Missing required fields');
      }
    } else {
      console.log('❌ API call failed:', response.status, response.statusText);
    }
  } catch (error) {
    console.log('❌ Error testing API:', error.message);
  }
}

// Test the old (incorrect) endpoint to confirm it fails
async function testOldEndpoint() {
  console.log('\nTesting old endpoint (should fail)...');
  
  try {
    const response = await fetch('/api/shared/contact-info/');
    
    if (response.ok) {
      console.log('❌ Old endpoint still works (unexpected)');
    } else {
      console.log('✅ Old endpoint correctly returns error:', response.status);
    }
  } catch (error) {
    console.log('✅ Old endpoint correctly throws error:', error.message);
  }
}

// Run tests
async function runTests() {
  console.log('🚀 Starting WhatsApp Support Component Tests...\n');
  
  await testContactInfoAPI();
  await testOldEndpoint();
  
  console.log('\n✨ Tests completed!');
}

// Run tests when script is loaded
runTests();
