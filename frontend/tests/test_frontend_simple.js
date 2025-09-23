/**
 * Simple Frontend Test Script
 * Tests API endpoints and basic functionality without browser automation
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

class SimpleFrontendTester {
    constructor() {
        this.baseUrl = 'http://localhost:3000';
        this.apiUrl = 'http://127.0.0.1:8000';
        this.testResults = [];
        this.userToken = null;
    }

    async testApiEndpoints() {
        console.log('\n🧪 Testing API Endpoints...');
        
        const endpoints = [
            { url: '/api/v1/tours/', method: 'GET', name: 'Tours API' },
            { url: '/api/v1/events/', method: 'GET', name: 'Events API' },
            { url: '/api/v1/transfers/', method: 'GET', name: 'Transfers API' },
            { url: '/api/v1/cart/', method: 'GET', name: 'Cart API (Guest)' },
        ];
        
        let passed = 0;
        
        for (const endpoint of endpoints) {
            try {
                const response = await axios({
                    method: endpoint.method,
                    url: `${this.apiUrl}${endpoint.url}`,
                    timeout: 10000
                });
                
                if (response.status === 200) {
                    console.log(`✅ ${endpoint.name}: ${response.status}`);
                    passed++;
                } else {
                    console.log(`❌ ${endpoint.name}: ${response.status}`);
                }
            } catch (error) {
                console.log(`❌ ${endpoint.name}: ${error.response?.status || error.message}`);
            }
        }
        
        if (passed === endpoints.length) {
            this.testResults.push({ test: 'API Endpoints', status: 'PASS' });
            return true;
        } else {
            this.testResults.push({ test: 'API Endpoints', status: 'FAIL' });
            return false;
        }
    }

    async testUserAuthentication() {
        console.log('\n🧪 Testing User Authentication...');
        
        try {
            // Test login
            const loginResponse = await axios.post(`${this.apiUrl}/api/v1/auth/login/`, {
                username: 'test_simple',
                password: 'testpass123'
            });
            
            if (loginResponse.status === 200) {
                this.userToken = loginResponse.data.tokens?.access;
                console.log('✅ User login successful');
                
                // Test authenticated endpoints
                const authResponse = await axios.get(`${this.apiUrl}/api/v1/cart/`, {
                    headers: { 'Authorization': `Bearer ${this.userToken}` }
                });
                
                if (authResponse.status === 200) {
                    console.log('✅ Authenticated cart access successful');
                    this.testResults.push({ test: 'User Authentication', status: 'PASS' });
                    return true;
                } else {
                    console.log('❌ Authenticated cart access failed');
                    this.testResults.push({ test: 'User Authentication', status: 'FAIL' });
                    return false;
                }
            } else {
                console.log('❌ User login failed');
                this.testResults.push({ test: 'User Authentication', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ User authentication test failed: ${error.response?.status || error.message}`);
            this.testResults.push({ test: 'User Authentication', status: 'FAIL' });
            return false;
        }
    }

    async testCartOperations() {
        console.log('\n🧪 Testing Cart Operations...');
        
        try {
            if (!this.userToken) {
                console.log('❌ No user token available');
                this.testResults.push({ test: 'Cart Operations', status: 'FAIL' });
                return false;
            }
            
            // Get tours for testing
            const toursResponse = await axios.get(`${this.apiUrl}/api/v1/tours/`);
            if (toursResponse.status !== 200) {
                console.log('❌ Tours API failed');
                this.testResults.push({ test: 'Cart Operations', status: 'FAIL' });
                return false;
            }
            
            // Handle both array and paginated response formats
            let tours = [];
            if (Array.isArray(toursResponse.data)) {
                tours = toursResponse.data;
            } else if (toursResponse.data.results) {
                tours = toursResponse.data.results;
            }
            
            if (!tours.length) {
                console.log('❌ No tours available for testing');
                this.testResults.push({ test: 'Cart Operations', status: 'FAIL' });
                return false;
            }
            
            const tour = tours[0];
            const schedule = tour.schedules?.[0];
            const variant = tour.variants?.[0];
            
            if (!schedule || !variant) {
                console.log('❌ Tour missing schedule or variant');
                this.testResults.push({ test: 'Cart Operations', status: 'FAIL' });
                return false;
            }
            
            // Add item to cart
            const addToCartResponse = await axios.post(`${this.apiUrl}/api/v1/cart/add/`, {
                product_type: 'tour',
                product_id: tour.id,
                variant_id: variant.id,
                quantity: 1,
                booking_date: schedule.start_date,
                booking_data: {
                    schedule_id: schedule.id,
                    participants: {
                        adult: 2,
                        child: 1,
                        infant: 0
                    }
                }
            }, {
                headers: { 'Authorization': `Bearer ${this.userToken}` }
            });
            
            if (addToCartResponse.status === 200 || addToCartResponse.status === 201) {
                console.log('✅ Add to cart successful');
                
                // Get cart
                const cartResponse = await axios.get(`${this.apiUrl}/api/v1/cart/`, {
                    headers: { 'Authorization': `Bearer ${this.userToken}` }
                });
                
                if (cartResponse.status === 200) {
                    console.log('✅ Get cart successful');
                    this.testResults.push({ test: 'Cart Operations', status: 'PASS' });
                    return true;
                } else {
                    console.log('❌ Get cart failed');
                    this.testResults.push({ test: 'Cart Operations', status: 'FAIL' });
                    return false;
                }
            } else {
                console.log('❌ Add to cart failed');
                this.testResults.push({ test: 'Cart Operations', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Cart operations test failed: ${error.response?.status || error.message}`);
            this.testResults.push({ test: 'Cart Operations', status: 'FAIL' });
            return false;
        }
    }

    async testOrderOperations() {
        console.log('\n🧪 Testing Order Operations...');
        
        try {
            if (!this.userToken) {
                console.log('❌ No user token available');
                this.testResults.push({ test: 'Order Operations', status: 'FAIL' });
                return false;
            }
            
            // Get cart items
            const cartResponse = await axios.get(`${this.apiUrl}/api/v1/cart/`, {
                headers: { 'Authorization': `Bearer ${this.userToken}` }
            });
            
            if (cartResponse.status !== 200 || !cartResponse.data.items?.length) {
                console.log('❌ No cart items available for order');
                this.testResults.push({ test: 'Order Operations', status: 'FAIL' });
                return false;
            }
            
            // Create order
            const orderResponse = await axios.post(`${this.apiUrl}/api/v1/orders/`, {
                payment_method: 'whatsapp',
                customer_info: {
                    full_name: 'Test User',
                    email: 'test_simple@example.com',
                    phone: '+1234567890',
                    special_requests: 'Test order'
                },
                items: cartResponse.data.items,
                total_amount: cartResponse.data.total_price,
                currency: cartResponse.data.currency
            }, {
                headers: { 'Authorization': `Bearer ${this.userToken}` }
            });
            
            if (orderResponse.status === 201) {
                console.log('✅ Order creation successful');
                
                // Get orders
                const ordersResponse = await axios.get(`${this.apiUrl}/api/v1/orders/`, {
                    headers: { 'Authorization': `Bearer ${this.userToken}` }
                });
                
                if (ordersResponse.status === 200) {
                    console.log('✅ Get orders successful');
                    this.testResults.push({ test: 'Order Operations', status: 'PASS' });
                    return true;
                } else {
                    console.log('❌ Get orders failed');
                    this.testResults.push({ test: 'Order Operations', status: 'FAIL' });
                    return false;
                }
            } else {
                console.log('❌ Order creation failed');
                this.testResults.push({ test: 'Order Operations', status: 'FAIL' });
                return false;
            }
        } catch (error) {
            console.log(`❌ Order operations test failed: ${error.response?.status || error.message}`);
            this.testResults.push({ test: 'Order Operations', status: 'FAIL' });
            return false;
        }
    }

    async testFrontendBuild() {
        console.log('\n🧪 Testing Frontend Build...');
        
        try {
            const { execSync } = require('child_process');
            
            // Test if build works
            execSync('npm run build', { stdio: 'pipe' });
            console.log('✅ Frontend build successful');
            this.testResults.push({ test: 'Frontend Build', status: 'PASS' });
            return true;
        } catch (error) {
            console.log(`❌ Frontend build failed: ${error.message}`);
            this.testResults.push({ test: 'Frontend Build', status: 'FAIL' });
            return false;
        }
    }

    async testFrontendLint() {
        console.log('\n🧪 Testing Frontend Lint...');
        
        try {
            const { execSync } = require('child_process');
            
            // Test if lint passes
            execSync('npm run lint', { stdio: 'pipe' });
            console.log('✅ Frontend lint passed');
            this.testResults.push({ test: 'Frontend Lint', status: 'PASS' });
            return true;
        } catch (error) {
            console.log(`❌ Frontend lint failed: ${error.message}`);
            this.testResults.push({ test: 'Frontend Lint', status: 'FAIL' });
            return false;
        }
    }

    async testTypeScript() {
        console.log('\n🧪 Testing TypeScript...');
        
        try {
            const { execSync } = require('child_process');
            
            // Test TypeScript compilation
            execSync('npx tsc --noEmit', { stdio: 'pipe' });
            console.log('✅ TypeScript compilation successful');
            this.testResults.push({ test: 'TypeScript', status: 'PASS' });
            return true;
        } catch (error) {
            console.log(`❌ TypeScript compilation failed: ${error.message}`);
            this.testResults.push({ test: 'TypeScript', status: 'FAIL' });
            return false;
        }
    }

    async runAllTests() {
        console.log('🚀 Starting Simple Frontend Tests...');
        
        const tests = [
            { name: 'API Endpoints', fn: () => this.testApiEndpoints() },
            { name: 'User Authentication', fn: () => this.testUserAuthentication() },
            { name: 'Cart Operations', fn: () => this.testCartOperations() },
            { name: 'Order Operations', fn: () => this.testOrderOperations() },
            { name: 'Frontend Build', fn: () => this.testFrontendBuild() },
            { name: 'Frontend Lint', fn: () => this.testFrontendLint() },
            { name: 'TypeScript', fn: () => this.testTypeScript() }
        ];
        
        for (const test of tests) {
            try {
                await test.fn();
            } catch (error) {
                console.log(`❌ ${test.name} failed with exception: ${error.message}`);
                this.testResults.push({ test: test.name, status: 'FAIL' });
            }
        }
        
        this.generateReport();
    }

    generateReport() {
        console.log('\n📊 Simple Frontend Test Results Summary:');
        
        const passed = this.testResults.filter(r => r.status === 'PASS').length;
        const total = this.testResults.length;
        
        console.log(`\n🎯 Overall: ${passed}/${total} tests passed`);
        
        for (const result of this.testResults) {
            const status = result.status === 'PASS' ? '✅' : '❌';
            console.log(`   ${result.test}: ${status} ${result.status}`);
        }
        
        // Generate JSON report
        const reportData = {
            timestamp: new Date().toISOString(),
            summary: {
                total: total,
                passed: passed,
                failed: total - passed,
                successRate: `${Math.round((passed / total) * 100)}%`
            },
            results: this.testResults
        };
        
        const reportPath = path.join(__dirname, 'frontend-test-report.json');
        fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
        console.log(`\n📄 JSON report generated: ${reportPath}`);
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    const tester = new SimpleFrontendTester();
    tester.runAllTests().catch(console.error);
}

module.exports = SimpleFrontendTester;
