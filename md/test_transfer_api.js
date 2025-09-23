// Test script for Transfer API
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000/api/v1';

async function testTransferAPI() {
  try {
    console.log('Testing Transfer API...');
    
    // Test 1: Get all transfer routes
    console.log('\n1. Testing GET /transfers/routes/');
    const routesResponse = await axios.get(`${API_BASE_URL}/transfers/routes/`);
    console.log('Status:', routesResponse.status);
    console.log('Routes count:', routesResponse.data.count);
    console.log('Routes:', routesResponse.data.results.map(r => `${r.origin} -> ${r.destination}`));
    
    // Test 2: Get a specific route
    if (routesResponse.data.results.length > 0) {
      const routeId = routesResponse.data.results[0].id;
      console.log(`\n2. Testing GET /transfers/routes/${routeId}/`);
      const routeResponse = await axios.get(`${API_BASE_URL}/transfers/routes/${routeId}/`);
      console.log('Status:', routeResponse.status);
      console.log('Route details:', {
        name: routeResponse.data.name,
        origin: routeResponse.data.origin,
        destination: routeResponse.data.destination,
        pricing_summary: Object.keys(routeResponse.data.pricing_summary || {})
      });
    }
    
    console.log('\n✅ Transfer API is working correctly!');
    
  } catch (error) {
    console.error('❌ Error testing Transfer API:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

testTransferAPI(); 