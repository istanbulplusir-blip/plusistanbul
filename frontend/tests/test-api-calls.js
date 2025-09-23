// Test script to monitor API calls and verify optimization
// Run this in the browser console to monitor API requests

(function() {
  'use strict';
  
  let apiCallCount = {};
  let lastCallTime = {};
  
  // Intercept fetch requests
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    const url = args[0];
    const method = args[1]?.method || 'GET';
    
    // Count API calls
    const key = `${method}:${url}`;
    apiCallCount[key] = (apiCallCount[key] || 0) + 1;
    lastCallTime[key] = Date.now();
    
    console.log(`API Call #${apiCallCount[key]}: ${method} ${url}`);
    
    // Log if same endpoint is called multiple times in short succession
    if (apiCallCount[key] > 1) {
      const timeDiff = Date.now() - lastCallTime[key];
      if (timeDiff < 5000) { // 5 seconds
        console.warn(`⚠️  Multiple calls to ${url} within ${timeDiff}ms (total: ${apiCallCount[key]})`);
      }
    }
    
    return originalFetch.apply(this, args);
  };
  
  // Intercept XMLHttpRequest
  const originalXHROpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url, ...args) {
    // Count API calls
    const key = `${method.toUpperCase()}:${url}`;
    apiCallCount[key] = (apiCallCount[key] || 0) + 1;
    lastCallTime[key] = Date.now();
    
    console.log(`XHR Call #${apiCallCount[key]}: ${method.toUpperCase()} ${url}`);
    
    // Log if same endpoint is called multiple times in short succession
    if (apiCallCount[key] > 1) {
      const timeDiff = Date.now() - lastCallTime[key];
      if (timeDiff < 5000) { // 5 seconds
        console.warn(`⚠️  Multiple XHR calls to ${url} within ${timeDiff}ms (total: ${apiCallCount[key]})`);
      }
    }
    
    return originalXHROpen.call(this, method, url, ...args);
  };
  
  // Function to get API call statistics
  window.getApiCallStats = function() {
    console.log('📊 API Call Statistics:');
    Object.entries(apiCallCount).forEach(([key, count]) => {
      const timeDiff = Date.now() - lastCallTime[key];
      console.log(`${key}: ${count} calls (last: ${timeDiff}ms ago)`);
    });
  };
  
  // Function to reset counters
  window.resetApiCallCounters = function() {
    apiCallCount = {};
    lastCallTime = {};
    console.log('🔄 API call counters reset');
  };
  
  console.log('🔍 API Call Monitor initialized!');
  console.log('Use getApiCallStats() to see statistics');
  console.log('Use resetApiCallCounters() to reset counters');
})();
