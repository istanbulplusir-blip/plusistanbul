/**
 * Google OAuth Production Test Script
 * 
 * This script can be run in the browser console on the production site
 * to test Google OAuth button rendering and functionality.
 * 
 * Usage:
 * 1. Open https://peykantravelistanbul.com/en/login in browser
 * 2. Open browser developer tools (F12)
 * 3. Copy and paste this entire script into the console
 * 4. Press Enter to run the tests
 */

(function () {
    'use strict';

    console.log('🚀 Starting Google OAuth Production Tests...');
    console.log('=====================================');

    const TEST_CONFIG = {
        expectedClientId: '728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com',
        googleScriptUrl: 'https://accounts.google.com/gsi/client',
        testPages: [
            '/en/login',
            '/en/register',
            '/tr/login',
            '/tr/register',
            '/fa/login',
            '/fa/register'
        ]
    };

    let testResults = {
        environment: {},
        buttonRendering: {},
        functionality: {},
        translations: {},
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

    // Test 1: Environment Check
    function testEnvironment() {
        log('Testing production environment...');

        const results = {
            domain: window.location.hostname,
            protocol: window.location.protocol,
            currentPage: window.location.pathname,
            isProduction: window.location.hostname === 'peykantravelistanbul.com',
            isHTTPS: window.location.protocol === 'https:',
            timestamp: new Date().toISOString()
        };

        // Check for Next.js environment variables (they would be in the built code)
        const scripts = Array.from(document.scripts);
        const hasClientIdInScripts = scripts.some(script =>
            script.textContent && script.textContent.includes('728579658716')
        );

        results.clientIdInBuild = hasClientIdInScripts;

        testResults.environment = results;

        if (results.isProduction && results.isHTTPS) {
            log('✅ Running on production domain with HTTPS', 'success');
        } else {
            log(`⚠️ Not on production (${results.domain}) or not HTTPS`, 'warning');
        }

        if (hasClientIdInScripts) {
            log('✅ Google Client ID found in build', 'success');
        } else {
            log('❌ Google Client ID not found in build', 'error');
        }

        return results;
    }

    // Test 2: Google Script Loading
    function testGoogleScript() {
        log('Testing Google Sign-In script...');

        return new Promise((resolve) => {
            const results = {
                scriptPresent: !!document.querySelector('script[src*="accounts.google.com"]'),
                windowGoogleAvailable: !!window.google,
                accountsIdAvailable: !!(window.google && window.google.accounts && window.google.accounts.id),
                timestamp: new Date().toISOString()
            };

            if (results.accountsIdAvailable) {
                log('✅ Google Sign-In API already available', 'success');
                testResults.functionality = results;
                resolve(results);
                return;
            }

            if (results.scriptPresent) {
                log('ℹ️ Google script tag found, waiting for API to load...');

                waitFor(() => window.google && window.google.accounts && window.google.accounts.id, 10000)
                    .then((loaded) => {
                        results.accountsIdAvailable = loaded;
                        results.loadedAfterWait = loaded;

                        if (loaded) {
                            log('✅ Google Sign-In API loaded successfully', 'success');
                        } else {
                            log('❌ Google Sign-In API failed to load within timeout', 'error');
                        }

                        testResults.functionality = results;
                        resolve(results);
                    });
            } else {
                log('❌ Google Sign-In script not found on page', 'error');
                testResults.functionality = results;
                resolve(results);
            }
        });
    }

    // Test 3: Button Rendering Check
    function testButtonRendering() {
        log('Testing Google Sign-In button rendering...');

        const results = {
            buttonsFound: [],
            buttonElements: [],
            timestamp: new Date().toISOString()
        };

        // Look for Google Sign-In button containers and elements
        const possibleSelectors = [
            '[data-testid="google-signin-button"]',
            '.google-signin-button',
            'div[id*="google"]',
            'div[class*="google"]',
            'button[class*="google"]',
            // Look for the actual Google button structure
            'div[role="button"][data-idom-class]',
            'div[jsname]',
            // Look for our GoogleSignInButton component container
            'div > div[ref]'
        ];

        possibleSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                elements.forEach((element, index) => {
                    const isVisible = element.offsetWidth > 0 && element.offsetHeight > 0;
                    const hasGoogleContent = element.textContent &&
                        (element.textContent.includes('Google') ||
                            element.textContent.includes('Sign in') ||
                            element.innerHTML.includes('google'));

                    if (isVisible || hasGoogleContent) {
                        results.buttonsFound.push({
                            selector,
                            index,
                            visible: isVisible,
                            hasGoogleContent,
                            textContent: element.textContent?.substring(0, 100),
                            innerHTML: element.innerHTML?.substring(0, 200)
                        });
                        results.buttonElements.push(element);
                    }
                });
            }
        });

        // Special check for Google's rendered button
        const googleButtons = document.querySelectorAll('div[role="button"]');
        googleButtons.forEach((button, index) => {
            if (button.textContent && button.textContent.toLowerCase().includes('google')) {
                results.buttonsFound.push({
                    selector: 'div[role="button"] (Google content)',
                    index,
                    visible: button.offsetWidth > 0 && button.offsetHeight > 0,
                    hasGoogleContent: true,
                    textContent: button.textContent?.substring(0, 100)
                });
                results.buttonElements.push(button);
            }
        });

        testResults.buttonRendering = results;

        if (results.buttonsFound.length > 0) {
            log(`✅ Found ${results.buttonsFound.length} potential Google Sign-In button(s)`, 'success');
            results.buttonsFound.forEach((btn, i) => {
                log(`   Button ${i + 1}: ${btn.selector} - Visible: ${btn.visible}, Has Google content: ${btn.hasGoogleContent}`);
            });
        } else {
            log('❌ No Google Sign-In buttons found on page', 'error');
        }

        return results;
    }

    // Test 4: Translation Keys Check
    function testTranslations() {
        log('Testing translation keys...');

        const results = {
            translationFunction: typeof window.t !== 'undefined',
            keys: {},
            timestamp: new Date().toISOString()
        };

        const keysToTest = [
            'googleLoadError',
            'googleInvalidResponse',
            'googleSignInFailed'
        ];

        if (results.translationFunction) {
            keysToTest.forEach(key => {
                try {
                    const translation = window.t(`auth.${key}`);
                    results.keys[key] = {
                        available: translation && !translation.includes('MISSING_MESSAGE'),
                        value: translation
                    };
                } catch (error) {
                    results.keys[key] = {
                        available: false,
                        error: error.message
                    };
                }
            });
        } else {
            log('⚠️ Translation function not available, checking for error messages in console', 'warning');
            // Check console for MISSING_MESSAGE errors
            results.note = 'Translation function not available - manual verification needed';
        }

        testResults.translations = results;

        if (results.translationFunction) {
            const availableKeys = Object.values(results.keys).filter(k => k.available).length;
            log(`✅ Translation function available, ${availableKeys}/${keysToTest.length} keys working`, 'success');
        } else {
            log('⚠️ Translation function not available for testing', 'warning');
        }

        return results;
    }

    // Test 5: Functional Test (if possible)
    function testFunctionality() {
        log('Testing Google OAuth functionality...');

        if (!window.google || !window.google.accounts || !window.google.accounts.id) {
            log('❌ Cannot test functionality - Google API not available', 'error');
            return { available: false, reason: 'Google API not loaded' };
        }

        try {
            // Test if we can initialize (without actually doing it)
            const canInitialize = typeof window.google.accounts.id.initialize === 'function';
            const canRenderButton = typeof window.google.accounts.id.renderButton === 'function';

            const results = {
                canInitialize,
                canRenderButton,
                apiMethods: Object.keys(window.google.accounts.id),
                timestamp: new Date().toISOString()
            };

            if (canInitialize && canRenderButton) {
                log('✅ Google OAuth API methods available and functional', 'success');
            } else {
                log('❌ Google OAuth API methods missing or non-functional', 'error');
            }

            return results;
        } catch (error) {
            log(`❌ Error testing functionality: ${error.message}`, 'error');
            return { error: error.message, timestamp: new Date().toISOString() };
        }
    }

    // Generate comprehensive report
    function generateReport() {
        console.log('\n📊 GOOGLE OAUTH PRODUCTION TEST REPORT');
        console.log('=====================================');

        const env = testResults.environment;
        const func = testResults.functionality;
        const btn = testResults.buttonRendering;
        const trans = testResults.translations;

        console.log('\n1. Environment:');
        console.log(`   Domain: ${env.domain}`);
        console.log(`   Protocol: ${env.protocol}`);
        console.log(`   Current Page: ${env.currentPage}`);
        console.log(`   Is Production: ${env.isProduction ? 'YES' : 'NO'}`);
        console.log(`   Client ID in Build: ${env.clientIdInBuild ? 'YES' : 'NO'}`);

        console.log('\n2. Google API:');
        console.log(`   Script Present: ${func.scriptPresent ? 'YES' : 'NO'}`);
        console.log(`   API Available: ${func.accountsIdAvailable ? 'YES' : 'NO'}`);

        console.log('\n3. Button Rendering:');
        console.log(`   Buttons Found: ${btn.buttonsFound.length}`);
        if (btn.buttonsFound.length > 0) {
            btn.buttonsFound.forEach((button, i) => {
                console.log(`   Button ${i + 1}: ${button.selector} (Visible: ${button.visible})`);
            });
        }

        console.log('\n4. Translations:');
        if (trans.translationFunction) {
            Object.entries(trans.keys).forEach(([key, result]) => {
                console.log(`   ${key}: ${result.available ? 'AVAILABLE' : 'MISSING'}`);
            });
        } else {
            console.log('   Translation function not available');
        }

        // Overall assessment
        const envOk = env.isProduction && env.clientIdInBuild;
        const funcOk = func.accountsIdAvailable;
        const btnOk = btn.buttonsFound.length > 0;

        console.log('\n5. Overall Assessment:');
        if (envOk && funcOk && btnOk) {
            console.log('   ✅ PASS - Google OAuth appears to be working correctly');
            testResults.overall = 'PASS';
        } else {
            console.log('   ❌ ISSUES DETECTED:');
            if (!envOk) console.log('      - Environment configuration issues');
            if (!funcOk) console.log('      - Google API not available');
            if (!btnOk) console.log('      - No Google buttons found');
            testResults.overall = 'FAIL';
        }

        console.log(`\n📅 Test completed at: ${new Date().toISOString()}`);
        console.log('=====================================\n');

        // Return results for programmatic access
        return testResults;
    }

    // Main test execution
    async function runTests() {
        try {
            // Run tests in sequence
            testEnvironment();
            await testGoogleScript();
            testButtonRendering();
            testTranslations();

            // Generate final report
            setTimeout(() => {
                generateReport();

                // Make results available globally for inspection
                window.googleOAuthTestResults = testResults;
                console.log('💡 Test results available in: window.googleOAuthTestResults');
            }, 1000);

        } catch (error) {
            log(`❌ Test execution failed: ${error.message}`, 'error');
            console.error('Full error:', error);
        }
    }

    // Start tests
    runTests();

})();

// Instructions for manual testing
console.log(`
📋 MANUAL TESTING INSTRUCTIONS:
==============================

1. Navigate to: https://peykantravelistanbul.com/en/login
2. Look for the Google Sign-In button below the login form
3. Check if the button renders correctly
4. Try clicking the button to test functionality

Pages to test:
- /en/login
- /en/register  
- /tr/login
- /tr/register
- /fa/login
- /fa/register

Expected behavior:
- Button should be visible and styled correctly
- Clicking should open Google OAuth popup
- No console errors related to MISSING_MESSAGE
- No errors about missing NEXT_PUBLIC_GOOGLE_CLIENT_ID
`);