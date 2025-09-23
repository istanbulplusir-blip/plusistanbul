// Test script for Next.js API routing
// This script tests if the Next.js rewrite rules are working correctly

async function testAPIRouting() {
  console.log('🧪 Testing Next.js API Routing...\n');
  
  const tests = [
    {
      name: 'Contact Info API',
      url: '/api/v1/shared/contact-info/',
      expected: 'Should return contact information'
    },
    {
      name: 'Support FAQs API',
      url: '/api/v1/shared/support-faqs/',
      expected: 'Should return support FAQs'
    },
    {
      name: 'General API Route',
      url: '/api/v1/shared/faqs/',
      expected: 'Should return general FAQs'
    }
  ];
  
  for (const test of tests) {
    console.log(`Testing: ${test.name}`);
    console.log(`URL: ${test.url}`);
    console.log(`Expected: ${test.expected}`);
    
    try {
      const response = await fetch(test.url);
      console.log(`Status: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Success! Data received:`, data);
      } else {
        console.log(`❌ Failed with status: ${response.status}`);
      }
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
    }
    
    console.log('---\n');
  }
  
  console.log('✨ API routing test completed!');
}

// Test direct backend calls to verify backend is working
async function testDirectBackend() {
  console.log('🔗 Testing Direct Backend Calls...\n');
  
  const backendTests = [
    {
      name: 'Backend Contact Info',
      url: 'http://localhost:8000/api/v1/shared/contact-info/',
      expected: 'Should return contact information from Django'
    },
    {
      name: 'Backend Support FAQs',
      url: 'http://localhost:8000/api/v1/shared/support-faqs/',
      expected: 'Should return support FAQs from Django'
    }
  ];
  
  for (const test of backendTests) {
    console.log(`Testing: ${test.name}`);
    console.log(`URL: ${test.url}`);
    console.log(`Expected: ${test.expected}`);
    
    try {
      const response = await fetch(test.url);
      console.log(`Status: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Success! Data received:`, data);
      } else {
        console.log(`❌ Failed with status: ${response.status}`);
      }
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
    }
    
    console.log('---\n');
  }
  
  console.log('✨ Direct backend test completed!');
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Starting API Routing Tests...\n');
  
  await testDirectBackend();
  await testAPIRouting();
  
  console.log('\n🎯 All tests completed!');
}

// Run tests when script is loaded
runAllTests();
