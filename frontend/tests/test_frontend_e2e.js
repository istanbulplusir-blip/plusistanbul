/**
 * Frontend E2E Test Script
 * Tests the complete user journey from guest to authenticated user
 * Tests all pages and components related to the cart and order flow
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

class FrontendE2ETester {
    constructor() {
        this.browser = null;
        this.page = null;
        this.baseUrl = 'http://localhost:3000';
        this.apiUrl = 'http://127.0.0.1:8000';
        this.testResults = [];
        this.screenshots = [];
    }

    async setup() {
        console.log('🚀 Starting Frontend E2E Test...');
        
        this.browser = await puppeteer.launch({
            headless: false, // Set to true for CI/CD
            defaultViewport: { width: 1280, height: 720 },
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        this.page = await this.browser.newPage();
        
        // Enable request interception to monitor API calls
        await this.page.setRequestInterception(true);
        this.page.on('request', request => {
            if (request.url().includes('/api/')) {
                console.log(`📡 API Request: ${request.method()} ${request.url()}`);
            }
            request.continue();
        });
        
        // Monitor console logs
        this.page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log(`❌ Console Error: ${msg.text()}`);
            }
        });
        
        // Monitor network errors
        this.page.on('response', response => {
            if (!response.ok() && response.url().includes('/api/')) {
                console.log(`❌ API Error: ${response.status()} ${response.url()}`);
            }
        });
    }

    async takeScreenshot(name) {
        const screenshotPath = path.join(__dirname, 'screenshots', `${name}.png`);
        await this.page.screenshot({ path: screenshotPath, fullPage: true });
        this.screenshots.push(screenshotPath);
        console.log(`📸 Screenshot saved: ${name}`);
    }

    async testHomePage() {
        console.log('\n🧪 Testing Home Page...');
        
        try {
            await this.page.goto(`${this.baseUrl}/en`, { waitUntil: 'networkidle0' });
            await this.takeScreenshot('home-page');
            
            // Check if page loaded correctly
            const title = await this.page.title();
            if (title.includes('Peykan Tourism')) {
                console.log('✅ Home page loaded successfully');
                this.testResults.push({ test: 'Home Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Home page title incorrect');
                this.testResults.push({ test: 'Home Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Home page test failed: ${error.message}`);
            this.testResults.push({ test: 'Home Page', status: 'FAIL' });
            return false;
        }
    }

    async testToursPage() {
        console.log('\n🧪 Testing Tours Page...');
        
        try {
            await this.page.goto(`${this.baseUrl}/en/tours`, { waitUntil: 'networkidle0' });
            await this.takeScreenshot('tours-page');
            
            // Wait for tours to load
            await this.page.waitForSelector('[data-testid="tour-card"], .tour-card, .product-card', { timeout: 10000 });
            
            // Check if tours are displayed
            const tourCards = await this.page.$$('[data-testid="tour-card"], .tour-card, .product-card');
            if (tourCards.length > 0) {
                console.log(`✅ Tours page loaded with ${tourCards.length} tours`);
                this.testResults.push({ test: 'Tours Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ No tours found on tours page');
                this.testResults.push({ test: 'Tours Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Tours page test failed: ${error.message}`);
            this.testResults.push({ test: 'Tours Page', status: 'FAIL' });
            return false;
        }
    }

    async testTourDetailPage() {
        console.log('\n🧪 Testing Tour Detail Page...');
        
        try {
            // Click on first tour
            const firstTour = await this.page.$('[data-testid="tour-card"], .tour-card, .product-card');
            if (!firstTour) {
                console.log('❌ No tour found to click');
                this.testResults.push({ test: 'Tour Detail Page', status: 'FAIL' });
                return false;
            }
            
            await firstTour.click();
            await this.page.waitForNavigation({ waitUntil: 'networkidle0' });
            await this.takeScreenshot('tour-detail-page');
            
            // Check if tour detail page loaded
            const url = this.page.url();
            if (url.includes('/tours/')) {
                console.log('✅ Tour detail page loaded successfully');
                
                // Check for key elements
                const hasTitle = await this.page.$('h1, .tour-title, .product-title');
                const hasPrice = await this.page.$('.price, .tour-price, .product-price');
                const hasBookButton = await this.page.$('button[data-testid="book-button"], .book-button, .add-to-cart');
                
                if (hasTitle && hasPrice && hasBookButton) {
                    console.log('✅ Tour detail page has all required elements');
                    this.testResults.push({ test: 'Tour Detail Page', status: 'PASS' });
                    return true;
                } else {
                    console.log('❌ Tour detail page missing required elements');
                    this.testResults.push({ test: 'Tour Detail Page', status: 'FAIL' });
                    return false;
                }
            } else {
                console.log('❌ Tour detail page URL incorrect');
                this.testResults.push({ test: 'Tour Detail Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Tour detail page test failed: ${error.message}`);
            this.testResults.push({ test: 'Tour Detail Page', status: 'FAIL' });
            return false;
        }
    }

    async testAddToCart() {
        console.log('\n🧪 Testing Add to Cart...');
        
        try {
            // Find and click add to cart button
            const addToCartButton = await this.page.$('button[data-testid="book-button"], .book-button, .add-to-cart');
            if (!addToCartButton) {
                console.log('❌ Add to cart button not found');
                this.testResults.push({ test: 'Add to Cart', status: 'FAIL' });
                return false;
            }
            
            await addToCartButton.click();
            
            // Wait for cart update or modal
            await this.page.waitForTimeout(2000);
            await this.takeScreenshot('add-to-cart');
            
            // Check for success message or cart update
            const hasSuccessMessage = await this.page.$('.success-message, .toast-success, [data-testid="success-message"]');
            const hasCartUpdate = await this.page.$('.cart-count, .cart-badge, [data-testid="cart-count"]');
            
            if (hasSuccessMessage || hasCartUpdate) {
                console.log('✅ Add to cart successful');
                this.testResults.push({ test: 'Add to Cart', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Add to cart failed - no success indication');
                this.testResults.push({ test: 'Add to Cart', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Add to cart test failed: ${error.message}`);
            this.testResults.push({ test: 'Add to Cart', status: 'FAIL' });
            return false;
        }
    }

    async testCartPage() {
        console.log('\n🧪 Testing Cart Page...');
        
        try {
            // Navigate to cart page
            await this.page.goto(`${this.baseUrl}/en/cart`, { waitUntil: 'networkidle0' });
            await this.takeScreenshot('cart-page');
            
            // Check if cart page loaded
            const hasCartItems = await this.page.$('.cart-item, .cart-product, [data-testid="cart-item"]');
            const hasCheckoutButton = await this.page.$('button[data-testid="checkout-button"], .checkout-button, .proceed-to-checkout');
            
            if (hasCartItems && hasCheckoutButton) {
                console.log('✅ Cart page loaded with items and checkout button');
                this.testResults.push({ test: 'Cart Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Cart page missing items or checkout button');
                this.testResults.push({ test: 'Cart Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Cart page test failed: ${error.message}`);
            this.testResults.push({ test: 'Cart Page', status: 'FAIL' });
            return false;
        }
    }

    async testCheckoutPage() {
        console.log('\n🧪 Testing Checkout Page...');
        
        try {
            // Click checkout button
            const checkoutButton = await this.page.$('button[data-testid="checkout-button"], .checkout-button, .proceed-to-checkout');
            if (!checkoutButton) {
                console.log('❌ Checkout button not found');
                this.testResults.push({ test: 'Checkout Page', status: 'FAIL' });
                return false;
            }
            
            await checkoutButton.click();
            await this.page.waitForNavigation({ waitUntil: 'networkidle0' });
            await this.takeScreenshot('checkout-page');
            
            // Check if checkout page loaded
            const url = this.page.url();
            if (url.includes('/checkout')) {
                console.log('✅ Checkout page loaded successfully');
                
                // Check for required form elements
                const hasCustomerForm = await this.page.$('.customer-form, .checkout-form, [data-testid="customer-form"]');
                const hasPaymentMethod = await this.page.$('.payment-method, [data-testid="payment-method"]');
                const hasPlaceOrderButton = await this.page.$('button[data-testid="place-order"], .place-order-button');
                
                if (hasCustomerForm && hasPaymentMethod && hasPlaceOrderButton) {
                    console.log('✅ Checkout page has all required elements');
                    this.testResults.push({ test: 'Checkout Page', status: 'PASS' });
                    return true;
                } else {
                    console.log('❌ Checkout page missing required elements');
                    this.testResults.push({ test: 'Checkout Page', status: 'FAIL' });
                    return false;
                }
            } else {
                console.log('❌ Checkout page URL incorrect');
                this.testResults.push({ test: 'Checkout Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Checkout page test failed: ${error.message}`);
            this.testResults.push({ test: 'Checkout Page', status: 'FAIL' });
            return false;
        }
    }

    async testLoginPage() {
        console.log('\n🧪 Testing Login Page...');
        
        try {
            // Navigate to login page
            await this.page.goto(`${this.baseUrl}/en/login`, { waitUntil: 'networkidle0' });
            await this.takeScreenshot('login-page');
            
            // Check if login page loaded
            const hasLoginForm = await this.page.$('.login-form, [data-testid="login-form"]');
            const hasUsernameField = await this.page.$('input[name="username"], input[type="email"], [data-testid="username"]');
            const hasPasswordField = await this.page.$('input[name="password"], input[type="password"], [data-testid="password"]');
            const hasLoginButton = await this.page.$('button[type="submit"], .login-button, [data-testid="login-button"]');
            
            if (hasLoginForm && hasUsernameField && hasPasswordField && hasLoginButton) {
                console.log('✅ Login page loaded with all required elements');
                this.testResults.push({ test: 'Login Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Login page missing required elements');
                this.testResults.push({ test: 'Login Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Login page test failed: ${error.message}`);
            this.testResults.push({ test: 'Login Page', status: 'FAIL' });
            return false;
        }
    }

    async testUserLogin() {
        console.log('\n🧪 Testing User Login...');
        
        try {
            // Fill login form
            await this.page.type('input[name="username"], input[type="email"], [data-testid="username"]', 'test_simple');
            await this.page.type('input[name="password"], input[type="password"], [data-testid="password"]', 'testpass123');
            
            // Click login button
            const loginButton = await this.page.$('button[type="submit"], .login-button, [data-testid="login-button"]');
            if (!loginButton) {
                console.log('❌ Login button not found');
                this.testResults.push({ test: 'User Login', status: 'FAIL' });
                return false;
            }
            
            await loginButton.click();
            await this.page.waitForNavigation({ waitUntil: 'networkidle0' });
            await this.takeScreenshot('user-logged-in');
            
            // Check if login was successful
            const url = this.page.url();
            if (url.includes('/dashboard') || url.includes('/profile') || url.includes('/account')) {
                console.log('✅ User login successful');
                this.testResults.push({ test: 'User Login', status: 'PASS' });
                return true;
            } else {
                console.log('❌ User login failed - redirected to wrong page');
                this.testResults.push({ test: 'User Login', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ User login test failed: ${error.message}`);
            this.testResults.push({ test: 'User Login', status: 'FAIL' });
            return false;
        }
    }

    async testOrderPage() {
        console.log('\n🧪 Testing Order Page...');
        
        try {
            // Navigate to orders page
            await this.page.goto(`${this.baseUrl}/en/orders`, { waitUntil: 'networkidle0' });
            await this.takeScreenshot('orders-page');
            
            // Check if orders page loaded
            const hasOrdersList = await this.page.$('.orders-list, .order-item, [data-testid="order-item"]');
            const hasOrderDetails = await this.page.$('.order-details, .order-info, [data-testid="order-details"]');
            
            if (hasOrdersList || hasOrderDetails) {
                console.log('✅ Orders page loaded successfully');
                this.testResults.push({ test: 'Order Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Orders page missing order information');
                this.testResults.push({ test: 'Order Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Order page test failed: ${error.message}`);
            this.testResults.push({ test: 'Order Page', status: 'FAIL' });
            return false;
        }
    }

    async testResponsiveDesign() {
        console.log('\n🧪 Testing Responsive Design...');
        
        try {
            const viewports = [
                { width: 375, height: 667, name: 'Mobile' },
                { width: 768, height: 1024, name: 'Tablet' },
                { width: 1280, height: 720, name: 'Desktop' }
            ];
            
            let passed = 0;
            
            for (const viewport of viewports) {
                await this.page.setViewport(viewport);
                await this.page.goto(`${this.baseUrl}/en`, { waitUntil: 'networkidle0' });
                await this.takeScreenshot(`responsive-${viewport.name.toLowerCase()}`);
                
                // Check if page is responsive
                const bodyWidth = await this.page.evaluate(() => document.body.scrollWidth);
                const viewportWidth = viewport.width;
                
                if (bodyWidth <= viewportWidth + 50) { // Allow some margin
                    console.log(`✅ ${viewport.name} responsive design working`);
                    passed++;
                } else {
                    console.log(`❌ ${viewport.name} responsive design issue`);
                }
            }
            
            if (passed === viewports.length) {
                console.log('✅ All responsive design tests passed');
                this.testResults.push({ test: 'Responsive Design', status: 'PASS' });
                return true;
            } else {
                console.log(`❌ ${passed}/${viewports.length} responsive design tests passed`);
                this.testResults.push({ test: 'Responsive Design', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Responsive design test failed: ${error.message}`);
            this.testResults.push({ test: 'Responsive Design', status: 'FAIL' });
            return false;
        }
    }

    async testImageLoading() {
        console.log('\n🧪 Testing Image Loading...');
        
        try {
            await this.page.goto(`${this.baseUrl}/en/tours`, { waitUntil: 'networkidle0' });
            
            // Check if images are loading
            const images = await this.page.$$('img');
            let loadedImages = 0;
            
            for (const img of images) {
                const isLoaded = await img.evaluate(el => el.complete && el.naturalHeight !== 0);
                if (isLoaded) {
                    loadedImages++;
                }
            }
            
            if (images.length > 0 && loadedImages === images.length) {
                console.log(`✅ All ${images.length} images loaded successfully`);
                this.testResults.push({ test: 'Image Loading', status: 'PASS' });
                return true;
            } else {
                console.log(`❌ ${loadedImages}/${images.length} images loaded`);
                this.testResults.push({ test: 'Image Loading', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Image loading test failed: ${error.message}`);
            this.testResults.push({ test: 'Image Loading', status: 'FAIL' });
            return false;
        }
    }

    async runAllTests() {
        await this.setup();
        
        // Create screenshots directory
        const screenshotsDir = path.join(__dirname, 'screenshots');
        if (!fs.existsSync(screenshotsDir)) {
            fs.mkdirSync(screenshotsDir, { recursive: true });
        }
        
        const tests = [
            { name: 'Home Page', fn: () => this.testHomePage() },
            { name: 'Tours Page', fn: () => this.testToursPage() },
            { name: 'Tour Detail Page', fn: () => this.testTourDetailPage() },
            { name: 'Add to Cart', fn: () => this.testAddToCart() },
            { name: 'Cart Page', fn: () => this.testCartPage() },
            { name: 'Checkout Page', fn: () => this.testCheckoutPage() },
            { name: 'Login Page', fn: () => this.testLoginPage() },
            { name: 'User Login', fn: () => this.testUserLogin() },
            { name: 'Order Page', fn: () => this.testOrderPage() },
            { name: 'Responsive Design', fn: () => this.testResponsiveDesign() },
            { name: 'Image Loading', fn: () => this.testImageLoading() }
        ];
        
        for (const test of tests) {
            try {
                await test.fn();
            } catch (error) {
                console.log(`❌ ${test.name} failed with exception: ${error.message}`);
                this.testResults.push({ test: test.name, status: 'FAIL' });
            }
        }
        
        await this.generateReport();
        await this.cleanup();
    }

    async generateReport() {
        console.log('\n📊 Frontend E2E Test Results Summary:');
        
        const passed = this.testResults.filter(r => r.status === 'PASS').length;
        const total = this.testResults.length;
        
        console.log(`\n🎯 Overall: ${passed}/${total} tests passed`);
        
        for (const result of this.testResults) {
            const status = result.status === 'PASS' ? '✅' : '❌';
            console.log(`   ${result.test}: ${status} ${result.status}`);
        }
        
        // Generate HTML report
        const htmlReport = `
<!DOCTYPE html>
<html>
<head>
    <title>Frontend E2E Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .test-result { margin: 10px 0; padding: 10px; border-radius: 3px; }
        .pass { background: #d4edda; color: #155724; }
        .fail { background: #f8d7da; color: #721c24; }
        .screenshots { margin-top: 20px; }
        .screenshot { margin: 10px 0; }
        .screenshot img { max-width: 100%; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Frontend E2E Test Report</h1>
        <p>Generated on: ${new Date().toLocaleString()}</p>
        <p>Overall Result: ${passed}/${total} tests passed</p>
    </div>
    
    <h2>Test Results</h2>
    ${this.testResults.map(result => `
        <div class="test-result ${result.status.toLowerCase()}">
            <strong>${result.test}:</strong> ${result.status}
        </div>
    `).join('')}
    
    <div class="screenshots">
        <h2>Screenshots</h2>
        ${this.screenshots.map(screenshot => `
            <div class="screenshot">
                <h3>${path.basename(screenshot, '.png')}</h3>
                <img src="${screenshot}" alt="${path.basename(screenshot, '.png')}" />
            </div>
        `).join('')}
    </div>
</body>
</html>`;
        
        const reportPath = path.join(__dirname, 'frontend-e2e-report.html');
        fs.writeFileSync(reportPath, htmlReport);
        console.log(`\n📄 HTML report generated: ${reportPath}`);
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
        }
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    const tester = new FrontendE2ETester();
    tester.runAllTests().catch(console.error);
}

module.exports = FrontendE2ETester;
