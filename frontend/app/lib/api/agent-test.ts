/**
 * Agent API Test
 * Simple test to verify API integration
 */

import { getAgentDashboard, getAgentCustomers, getAgentTours } from './agents';

export const testAgentAPI = async () => {
  console.log('🧪 Testing Agent API Integration...');
  
  try {
    // Test dashboard API
    console.log('📊 Testing dashboard API...');
    const dashboardResponse = await getAgentDashboard();
    console.log('✅ Dashboard API:', (dashboardResponse as Record<string, unknown>)?.data);
    
    // Test customers API
    console.log('👥 Testing customers API...');
    const customersResponse = await getAgentCustomers();
    console.log('✅ Customers API:', (customersResponse as Record<string, unknown>)?.data);
    
    // Test tours API
    console.log('🏛️ Testing tours API...');
    const toursResponse = await getAgentTours();
    console.log('✅ Tours API:', (toursResponse as Record<string, unknown>)?.data);
    
    console.log('🎉 All Agent API tests passed!');
    return true;
    
  } catch (error) {
    console.error('❌ Agent API test failed:', error);
    return false;
  }
};

// Export for use in browser console or testing
if (typeof window !== 'undefined') {
  (window as unknown as Record<string, unknown>).testAgentAPI = testAgentAPI;
}
