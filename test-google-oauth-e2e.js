/**
 * Google OAuth End-to-End Test Script
 * 
 * This script tests the complete Google OAuth authentication flow
 * from frontend button click to backend authentication and user creation.
 * 
 * Usage:
 * 1. Open https://peykantravelistanbul.com/en/login in browser
 * 2. Open browser developer tools (F12)
 * 3. Copy and paste this script into the console
 * 4. Run: testGoogleOAuthE2E()
 */

(function () {
    'use strict';

    const E2E_CONFIG = {
        apiBaseUrl: 'https://peykantravelistanbul.com/api/v1',
        googleAuthEndpoint: '/auth/social/google/',
        expectedClientId: '728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com',
        testTimeout: 30000
    };

    let e2eResults = {
        frontend: {},
        backend: {},
        integration: {},
        overall: null
    };

    // Utility functions
    function log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = type === 'error' ? '❌' : type === 'warning' ? '⚠️' : type === 'success' ? '✅' : 'ℹ️';
        console.log(`${prefix} [${timestamp}] ${message}`);
    }

    function waitFor(condition, timeout = 5000) {
        return new Promise((resolve) => {
            const startTime = Date.now();
            const check = () => {
                if (condition()) {
                    resolve(true);
                } else if (Date.now() - startTime > timeout) {
                    resolve(false);
                } else {
                    setTimeout(check, 100);
                }
            };
            check();
        });
    }

    // Test 1: Frontend Google OAuth Setup
    async function testFrontendSetup() {
        log('Testing frontend Google OAuth setup...');

        const results = {
            googleScriptLoaded: false,
            googleApiAvailable: false,
            buttonFound: false,
            clientIdConfigured: false,
            timestamp: new Date().toISOString()
        };

        // Check if Google script is loaded
        results.googleScriptLoaded = !!document.querySelector('script[src*="accounts.google.com"]');

        // Wait for Google API to be available
        if (results.googleScriptLoaded) {
            results.googleApiAvailable = await waitFor(() =>
                window.google && window.google.accounts && window.google.accounts.id, 10000
            );
        }

        // Check for Google Sign-In buttons
        const buttonSelectors = [
            'div[role="button"]',
            '[data-testid="google-signin-button"]',
            '.google-signin-button'
        ];

        for (const selector of buttonSelectors) {
            const buttons = document.querySelectorAll(selector);
            for (const button of buttons) {
                if (button.textContent && button.textContent.toLowerCase().includes('google')) {
                    results.buttonFound = true;
                    break;
                }
            }
            if (results.buttonFound) break;
        }

        // Check client ID configuration
        const scripts = Array.from(document.scripts);
        results.clientIdConfigured = scripts.some(script =>
            script.textContent && script.textContent.includes(E2E_CONFIG.expectedClientId)
        );

        e2eResults.frontend = results;

        if (results.googleApiAvailable && results.buttonFound && results.clientIdConfigured) {
            log('✅ Frontend setup complete and working', 'success');
        } else {
            log('❌ Frontend setup issues detected', 'error');
            if (!results.googleApiAvailable) log('   - Google API not available');
            if (!results.buttonFound) log('   - Google button not found');
            if (!results.clientIdConfigured) log('   - Client ID not configured');
        }

        return results;
    }

    // Test 2: Backend API Endpoint
    async function testBackendEndpoint() {
        log('Testing backend Google OAuth endpoint...');

        const results = {
            endpointAccessible: false,
            correctErrorResponse: false,
            corsConfigured: false,
            timestamp: new Date().toISOString()
        };

        try {
            const url = E2E_CONFIG.apiBaseUrl + E2E_CONFIG.googleAuthEndpoint;

            // Test OPTIONS request (CORS preflight)
            const optionsResponse = await fetch(url, {
                method: 'OPTIONS',
                headers: {
                    'Origin': window.location.origin,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                }
            });

            results.corsConfigured = optionsResponse.ok;

            // Test POST request with empty body (should return 400 with proper error)
            const postResponse = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Origin': window.location.origin
                },
                body: JSON.stringify({})
            });

            results.endpointAccessible = postResponse.status === 400;

            if (postResponse.status === 400) {
                const errorData = await postResponse.json();
                results.correctErrorResponse = errorData.hasOwnProperty('id_token') ||
                    errorData.hasOwnProperty('error');
                results.errorData = errorData;
            }

        } catch (error) {
            results.error = error.message;
            log(`❌ Backend endpoint test failed: ${error.message}`, 'error');
        }

        e2eResults.backend = results;

        if (results.endpointAccessible && results.corsConfigured) {
            log('✅ Backend endpoint accessible and properly configured', 'success');
        } else {
            log('❌ Backend endpoint issues detected', 'error');
            if (!results.endpointAccessible) log('   - Endpoint not accessible or wrong response');
            if (!results.corsConfigured) log('   - CORS not properly configured');
        }

        return results;
    }

    // Test 3: Mock Authentication Flow
    async function testMockAuthFlow() {
        log('Testing mock authentication flow...');

        const results = {
            canCreateMockToken: false,
            backendAcceptsMockToken: false,
            userCreationWorks: false,
            jwtTokensReturned: false,
            timestamp: new Date().toISOString()
        };

        try {
            // Create a mock Google ID token structure (for testing purposes only)
            // Note: This won't work with real Google verification, but tests the flow
            const mockTokenPayload = {
                iss: 'accounts.google.com',
                aud: E2E_CONFIG.expectedClientId,
                sub: '123456789',
                email: 'test@example.com',
                email_verified: true,
                name: 'Test User',
                given_name: 'Test',
                family_name: 'User',
                iat: Math.floor(Date.now() / 1000),
                exp: Math.floor(Date.now() / 1000) + 3600
            };

            results.canCreateMockToken = true;

            // Note: We can't actually test with a real token without user interaction
            // But we can test the endpoint structure
            log('ℹ️ Mock token created (structure test only)');
            log('ℹ️ Real authentication requires user interaction with Google OAuth popup');

        } catch (error) {
            results.error = error.message;
            log(`❌ Mock auth flow test failed: ${error.message}`, 'error');
        }

        e2eResults.integration = results;
        return results;
    }

    // Test 4: Real Authentication Flow (Interactive)
    async function testRealAuthFlow() {
        log('Testing real authentication flow (requires user interaction)...');

        if (!window.google || !window.google.accounts || !window.google.accounts.id) {
            log('❌ Google API not available for real auth test', 'error');
            return { available: false, reason: 'Google API not loaded' };
        }

        return new Promise((resolve) => {
            const results = {
                initiated: false,
                userInteractionRequired: true,
                timestamp: new Date().toISOString()
            };

            try {
                // Create a test container for the authentication
                const testContainer = document.createElement('div');
                testContainer.id = 'e2e-auth-test';
                testContainer.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border: 2px solid #007bff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    z-index: 10000;
                    max-width: 300px;
                `;

                testContainer.innerHTML = `
                    <h3 style="margin: 0 0 10px 0; color: #007bff;">E2E Auth Test</h3>
                    <p style="margin: 0 0 15px 0; font-size: 14px;">Click the button below to test the complete Google OAuth flow:</p>
                    <div id="e2e-google-button"></div>
                    <button id="e2e-close" style="margin-top: 10px; padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Close Test</button>
                `;

                document.body.appendChild(testContainer);

                // Initialize Google Sign-In for testing
                window.google.accounts.id.initialize({
                    client_id: E2E_CONFIG.expectedClientId,
                    callback: async (response) => {
                        log('🎉 Google OAuth callback triggered!', 'success');

                        try {
                            // Test the backend with the real token
                            const backendResponse = await fetch(E2E_CONFIG.apiBaseUrl + E2E_CONFIG.googleAuthEndpoint, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    id_token: response.credential
                                })
                            });

                            const responseData = await backendResponse.json();

                            if (backendResponse.ok) {
                                log('✅ Backend authentication successful!', 'success');
                                log(`✅ User: ${responseData.user?.email || 'Unknown'}`);
                                log('✅ JWT tokens received');

                                results.backendSuccess = true;
                                results.userData = responseData.user;
                                results.hasTokens = !!(responseData.tokens?.access && responseData.tokens?.refresh);
                            } else {
                                log(`❌ Backend authentication failed: ${responseData.error || 'Unknown error'}`, 'error');
                                results.backendError = responseData;
                            }

                        } catch (error) {
                            log(`❌ Backend request failed: ${error.message}`, 'error');
                            results.backendError = error.message;
                        }

                        // Clean up test container
                        document.body.removeChild(testContainer);
                        resolve(results);
                    }
                });

                // Render the test button
                window.google.accounts.id.renderButton(
                    document.getElementById('e2e-google-button'),
                    {
                        theme: 'outline',
                        size: 'large',
                        text: 'signin_with',
                        shape: 'pill'
                    }
                );

                results.initiated = true;
                log('✅ Real auth test initiated - please click the Google button in the test panel', 'success');

                // Close button handler
                document.getElementById('e2e-close').onclick = () => {
                    document.body.removeChild(testContainer);
                    results.userCancelled = true;
                    resolve(results);
                };

                // Auto-close after timeout
                setTimeout(() => {
                    if (document.body.contains(testContainer)) {
                        document.body.removeChild(testContainer);
                        results.timeout = true;
                        resolve(results);
                    }
                }, E2E_CONFIG.testTimeout);

            } catch (error) {
                log(`❌ Real auth test setup failed: ${error.message}`, 'error');
                results.error = error.message;
                resolve(results);
            }
        });
    }

    // Generate comprehensive E2E report
    function generateE2EReport() {
        console.log('\n📊 GOOGLE OAUTH END-TO-END TEST REPORT');
        console.log('=====================================');

        const frontend = e2eResults.frontend;
        const backend = e2eResults.backend;
        const integration = e2eResults.integration;

        console.log('\n1. Frontend Setup:');
        console.log(`   Google Script Loaded: ${frontend.googleScriptLoaded ? 'YES' : 'NO'}`);
        console.log(`   Google API Available: ${frontend.googleApiAvailable ? 'YES' : 'NO'}`);
        console.log(`   Button Found: ${frontend.buttonFound ? 'YES' : 'NO'}`);
        console.log(`   Client ID Configured: ${frontend.clientIdConfigured ? 'YES' : 'NO'}`);

        console.log('\n2. Backend Endpoint:');
        console.log(`   Endpoint Accessible: ${backend.endpointAccessible ? 'YES' : 'NO'}`);
        console.log(`   CORS Configured: ${backend.corsConfigured ? 'YES' : 'NO'}`);
        console.log(`   Correct Error Response: ${backend.correctErrorResponse ? 'YES' : 'NO'}`);

        console.log('\n3. Integration:');
        console.log(`   Mock Token Creation: ${integration.canCreateMockToken ? 'YES' : 'NO'}`);

        // Overall assessment
        const frontendOk = frontend.googleApiAvailable && frontend.buttonFound && frontend.clientIdConfigured;
        const backendOk = backend.endpointAccessible && backend.corsConfigured;

        console.log('\n4. Overall Assessment:');
        if (frontendOk && backendOk) {
            console.log('   ✅ READY - Google OAuth flow is properly configured');
            console.log('   ℹ️ Run testRealAuthFlow() to test with real user interaction');
            e2eResults.overall = 'READY';
        } else {
            console.log('   ❌ ISSUES DETECTED:');
            if (!frontendOk) console.log('      - Frontend configuration issues');
            if (!backendOk) console.log('      - Backend endpoint issues');
            e2eResults.overall = 'ISSUES';
        }

        console.log(`\n📅 Test completed at: ${new Date().toISOString()}`);
        console.log('=====================================\n');

        return e2eResults;
    }

    // Main E2E test function
    async function testGoogleOAuthE2E() {
        console.log('🚀 Starting Google OAuth End-to-End Tests...\n');

        try {
            await testFrontendSetup();
            await testBackendEndpoint();
            await testMockAuthFlow();

            const report = generateE2EReport();

            // Make results available globally
            window.googleOAuthE2EResults = e2eResults;
            console.log('💡 E2E test results available in: window.googleOAuthE2EResults');

            return report;

        } catch (error) {
            log(`❌ E2E test execution failed: ${error.message}`, 'error');
            console.error('Full error:', error);
            return { error: error.message };
        }
    }

    // Real authentication test function (separate for user interaction)
    async function testRealAuthFlow() {
        console.log('🔐 Starting Real Authentication Flow Test...\n');

        const result = await testRealAuthFlow();

        console.log('\n📊 REAL AUTHENTICATION TEST RESULT');
        console.log('==================================');

        if (result.backendSuccess) {
            console.log('✅ COMPLETE SUCCESS - Full OAuth flow working!');
            console.log(`   User: ${result.userData?.email}`);
            console.log(`   Tokens: ${result.hasTokens ? 'Received' : 'Missing'}`);
        } else if (result.userCancelled) {
            console.log('⚠️ User cancelled the test');
        } else if (result.timeout) {
            console.log('⚠️ Test timed out waiting for user interaction');
        } else if (result.error) {
            console.log(`❌ Test failed: ${result.error}`);
        } else {
            console.log('ℹ️ Test requires user interaction - please try again');
        }

        return result;
    }

    // Export functions globally
    window.testGoogleOAuthE2E = testGoogleOAuthE2E;
    window.testRealAuthFlow = testRealAuthFlow;

    // Auto-run basic tests
    testGoogleOAuthE2E();

})();

console.log(`
📋 GOOGLE OAUTH E2E TESTING INSTRUCTIONS:
========================================

Automated tests have been run. For complete testing:

1. Review the automated test results above
2. Run manual authentication test:
   testRealAuthFlow()

3. Test on different pages:
   - /en/login
   - /en/register
   - /tr/login (Turkish)
   - /fa/login (Persian)

4. Expected complete flow:
   ✅ Button renders correctly
   ✅ Clicking opens Google OAuth popup
   ✅ User authenticates with Google
   ✅ Backend receives and validates token
   ✅ User is created/logged in
   ✅ JWT tokens are returned
   ✅ User is redirected appropriately

5. Error scenarios to test:
   - Network failures
   - Invalid tokens
   - Unverified Google accounts
   - Backend API errors
`);