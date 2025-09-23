/**
 * Frontend Browser Test Script
 * Tests the complete user journey using Puppeteer
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

class FrontendBrowserTester {
    constructor() {
        this.browser = null;
        this.page = null;
        this.baseUrl = 'http://localhost:3000';
        this.testResults = [];
        this.screenshots = [];
    }

    async setup() {
        console.log('🚀 Starting Frontend Browser Tests...');
        
        this.browser = await puppeteer.launch({
            headless: true, // Set to false to see browser
            defaultViewport: { width: 1280, height: 720 },
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        this.page = await this.browser.newPage();
        
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
            await this.page.goto(`${this.baseUrl}/en`, { waitUntil: 'networkidle0', timeout: 30000 });
            await this.takeScreenshot('home-page');
            
            // Check if page loaded correctly
            const title = await this.page.title();
            if (title && title.length > 0) {
                console.log('✅ Home page loaded successfully');
                this.testResults.push({ test: 'Home Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Home page title empty');
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
            await this.page.goto(`${this.baseUrl}/en/tours`, { waitUntil: 'networkidle0', timeout: 30000 });
            await this.takeScreenshot('tours-page');
            
            // Wait for content to load
            await this.page.waitForTimeout(3000);
            
            // Check if page has content
            const hasContent = await this.page.evaluate(() => {
                return document.body.innerText.length > 100;
            });
            
            if (hasContent) {
                console.log('✅ Tours page loaded with content');
                this.testResults.push({ test: 'Tours Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Tours page has no content');
                this.testResults.push({ test: 'Tours Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Tours page test failed: ${error.message}`);
            this.testResults.push({ test: 'Tours Page', status: 'FAIL' });
            return false;
        }
    }

    async testLoginPage() {
        console.log('\n🧪 Testing Login Page...');
        
        try {
            await this.page.goto(`${this.baseUrl}/en/login`, { waitUntil: 'networkidle0', timeout: 30000 });
            await this.takeScreenshot('login-page');
            
            // Check if login page loaded
            const hasForm = await this.page.evaluate(() => {
                return document.querySelector('form') !== null || 
                       document.querySelector('input[type="password"]') !== null;
            });
            
            if (hasForm) {
                console.log('✅ Login page loaded with form');
                this.testResults.push({ test: 'Login Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Login page missing form');
                this.testResults.push({ test: 'Login Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Login page test failed: ${error.message}`);
            this.testResults.push({ test: 'Login Page', status: 'FAIL' });
            return false;
        }
    }

    async testCartPage() {
        console.log('\n🧪 Testing Cart Page...');
        
        try {
            await this.page.goto(`${this.baseUrl}/en/cart`, { waitUntil: 'networkidle0', timeout: 30000 });
            await this.takeScreenshot('cart-page');
            
            // Check if cart page loaded
            const hasContent = await this.page.evaluate(() => {
                return document.body.innerText.length > 50;
            });
            
            if (hasContent) {
                console.log('✅ Cart page loaded');
                this.testResults.push({ test: 'Cart Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Cart page has no content');
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
            await this.page.goto(`${this.baseUrl}/en/checkout`, { waitUntil: 'networkidle0', timeout: 30000 });
            await this.takeScreenshot('checkout-page');
            
            // Check if checkout page loaded
            const hasContent = await this.page.evaluate(() => {
                return document.body.innerText.length > 50;
            });
            
            if (hasContent) {
                console.log('✅ Checkout page loaded');
                this.testResults.push({ test: 'Checkout Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Checkout page has no content');
                this.testResults.push({ test: 'Checkout Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Checkout page test failed: ${error.message}`);
            this.testResults.push({ test: 'Checkout Page', status: 'FAIL' });
            return false;
        }
    }

    async testOrdersPage() {
        console.log('\n🧪 Testing Orders Page...');
        
        try {
            await this.page.goto(`${this.baseUrl}/en/orders`, { waitUntil: 'networkidle0', timeout: 30000 });
            await this.takeScreenshot('orders-page');
            
            // Check if orders page loaded
            const hasContent = await this.page.evaluate(() => {
                return document.body.innerText.length > 50;
            });
            
            if (hasContent) {
                console.log('✅ Orders page loaded');
                this.testResults.push({ test: 'Orders Page', status: 'PASS' });
                return true;
            } else {
                console.log('❌ Orders page has no content');
                this.testResults.push({ test: 'Orders Page', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Orders page test failed: ${error.message}`);
            this.testResults.push({ test: 'Orders Page', status: 'FAIL' });
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
                await this.page.goto(`${this.baseUrl}/en`, { waitUntil: 'networkidle0', timeout: 30000 });
                await this.takeScreenshot(`responsive-${viewport.name.toLowerCase()}`);
                
                // Check if page is responsive
                const bodyWidth = await this.page.evaluate(() => document.body.scrollWidth);
                const viewportWidth = viewport.width;
                
                if (bodyWidth <= viewportWidth + 100) { // Allow some margin
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
            await this.page.goto(`${this.baseUrl}/en/tours`, { waitUntil: 'networkidle0', timeout: 30000 });
            
            // Wait for images to load
            await this.page.waitForTimeout(5000);
            
            // Check if images are loading
            const imageStats = await this.page.evaluate(() => {
                const images = document.querySelectorAll('img');
                let loadedImages = 0;
                let totalImages = images.length;
                
                images.forEach(img => {
                    if (img.complete && img.naturalHeight !== 0) {
                        loadedImages++;
                    }
                });
                
                return { loaded: loadedImages, total: totalImages };
            });
            
            if (imageStats.total > 0 && imageStats.loaded === imageStats.total) {
                console.log(`✅ All ${imageStats.total} images loaded successfully`);
                this.testResults.push({ test: 'Image Loading', status: 'PASS' });
                return true;
            } else {
                console.log(`❌ ${imageStats.loaded}/${imageStats.total} images loaded`);
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
            { name: 'Login Page', fn: () => this.testLoginPage() },
            { name: 'Cart Page', fn: () => this.testCartPage() },
            { name: 'Checkout Page', fn: () => this.testCheckoutPage() },
            { name: 'Orders Page', fn: () => this.testOrdersPage() },
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
        console.log('\n📊 Frontend Browser Test Results Summary:');
        
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
    <title>Frontend Browser Test Report</title>
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
        <h1>Frontend Browser Test Report</h1>
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
        
        const reportPath = path.join(__dirname, 'frontend-browser-report.html');
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
    const tester = new FrontendBrowserTester();
    tester.runAllTests().catch(console.error);
}

module.exports = FrontendBrowserTester;
