/**
 * Simple Frontend Capacity Test
 * Tests basic capacity display and API calls
 */

const axios = require('axios');

class SimpleCapacityTester {
    constructor() {
        this.apiUrl = 'http://127.0.0.1:8000';
        this.userToken = null;
        this.testTour = null;
    }

    async testCapacityDisplay() {
        console.log('🧪 Testing Frontend Capacity Display...');

        try {
            // Get tours without authentication (public API)
            const response = await axios.get(`${this.apiUrl}/api/v1/tours/`);
            const tours = response.data.results || response.data;

            if (!tours.length) {
                console.log('❌ No tours found');
                return false;
            }

            console.log(`✅ Found ${tours.length} tours`);

            // Find tour with schedules
            const tourWithSchedules = tours.find(t =>
                t.schedules && t.schedules.length > 0 &&
                t.variants && t.variants.length > 0
            );

            if (!tourWithSchedules) {
                console.log('❌ No tour with schedules found');
                return false;
            }

            console.log(`✅ Found tour with schedules: ${tourWithSchedules.title}`);
            this.testTour = tourWithSchedules;

            // Check schedule capacity data
            const schedule = tourWithSchedules.schedules[0];
            console.log('\\n📅 Schedule capacity data:');
            console.log(`   • Available capacity: ${schedule.available_capacity}`);
            console.log(`   • Max capacity: ${schedule.max_capacity}`);
            console.log(`   • Current capacity: ${schedule.current_capacity}`);
            console.log(`   • Is full: ${schedule.is_full}`);

            // Check variant capacity data
            if (schedule.variant_capacities) {
                console.log('\\n🏷️ Variant capacity data:');
                Object.entries(schedule.variant_capacities).forEach(([variantId, capacity]) => {
                    console.log(`   • Variant ${variantId}:`);
                    console.log(`     - Total: ${capacity.total}`);
                    console.log(`     - Available: ${capacity.available}`);
                    console.log(`     - Booked: ${capacity.booked}`);
                });
            }

            return true;
        } catch (error) {
            console.log(`❌ Capacity display test failed: ${error.response?.status || error.message}`);
            return false;
        }
    }

    async testTourDetailAPI() {
        console.log('\\n🧪 Testing Tour Detail API...');

        try {
            if (!this.testTour) {
                console.log('❌ No test tour available');
                return false;
            }

            const response = await axios.get(`${this.apiUrl}/api/v1/tours/${this.testTour.slug}/`);
            const tour = response.data;

            console.log('✅ Tour detail API working');
            console.log(`   • Tour: ${tour.title}`);
            console.log(`   • Schedules: ${tour.schedules.length}`);
            console.log(`   • Variants: ${tour.variants.length}`);

            // Check if capacity data is included
            const schedule = tour.schedules[0];
            if (schedule.available_capacity !== undefined &&
                schedule.variant_capacities) {
                console.log('✅ Capacity data included in tour detail');
                return true;
            } else {
                console.log('❌ Capacity data missing in tour detail');
                return false;
            }
        } catch (error) {
            console.log(`❌ Tour detail API test failed: ${error.response?.status || error.message}`);
            return false;
        }
    }

    async testCapacityConsistency() {
        console.log('\\n🧪 Testing Capacity Consistency...');

        try {
            if (!this.testTour) {
                console.log('❌ No test tour available');
                return false;
            }

            // Get tour data
            const response = await axios.get(`${this.apiUrl}/api/v1/tours/${this.testTour.slug}/`);
            const tour = response.data;
            const schedule = tour.schedules[0];

            console.log('🔍 Checking capacity consistency:');

            // Check schedule capacity consistency
            const scheduleAvailable = schedule.available_capacity;
            const scheduleMax = schedule.max_capacity;
            const scheduleCurrent = schedule.current_capacity;

            console.log(`   • Schedule: available=${scheduleAvailable}, max=${scheduleMax}, current=${scheduleCurrent}`);

            // Check variant capacity consistency
            let totalVariantAvailable = 0;
            let totalVariantBooked = 0;

            if (schedule.variant_capacities) {
                Object.values(schedule.variant_capacities).forEach(capacity => {
                    totalVariantAvailable += capacity.available;
                    totalVariantBooked += capacity.booked;

                    const variantTotal = capacity.total;
                    const variantAvailable = capacity.available;
                    const variantBooked = capacity.booked;

                    console.log(`   • Variant: total=${variantTotal}, available=${variantAvailable}, booked=${variantBooked}`);

                    if (variantTotal !== (variantAvailable + variantBooked)) {
                        console.log('❌ Variant capacity inconsistency detected!');
                        return false;
                    }
                });

                console.log(`   • Total variant available: ${totalVariantAvailable}`);
                console.log(`   • Total variant booked: ${totalVariantBooked}`);

                // Check if schedule available matches total variant available
                if (scheduleAvailable === totalVariantAvailable) {
                    console.log('✅ Schedule and variant capacities are consistent');
                    return true;
                } else {
                    console.log(`❌ Capacity mismatch: schedule=${scheduleAvailable}, variants=${totalVariantAvailable}`);
                    return false;
                }
            } else {
                console.log('❌ No variant capacity data found');
                return false;
            }
        } catch (error) {
            console.log(`❌ Capacity consistency test failed: ${error.response?.status || error.message}`);
            return false;
        }
    }

    async testFrontendIntegration() {
        console.log('\\n🧪 Testing Frontend-Backend Integration...');

        try {
            // Test if frontend can fetch and display capacity data
            const response = await axios.get(`${this.apiUrl}/api/v1/tours/`);
            const tours = response.data.results || response.data;

            console.log('✅ Frontend can fetch tours data');

            if (tours.length > 0) {
                const tour = tours[0];
                console.log(`✅ Sample tour: ${tour.title}`);

                if (tour.next_schedule_capacity_available !== undefined) {
                    console.log(`✅ Capacity data available in list: ${tour.next_schedule_capacity_available}`);
                } else {
                    console.log('⚠️ Capacity data not in list view (this is normal)');
                }

                // Test detail view
                if (tour.slug) {
                    const detailResponse = await axios.get(`${this.apiUrl}/api/v1/tours/${tour.slug}/`);
                    const detailTour = detailResponse.data;

                    if (detailTour.schedules && detailTour.schedules.length > 0) {
                        const schedule = detailTour.schedules[0];
                        if (schedule.available_capacity !== undefined) {
                            console.log('✅ Detail view has capacity data');
                            return true;
                        }
                    }
                }
            }

            return false;
        } catch (error) {
            console.log(`❌ Frontend integration test failed: ${error.response?.status || error.message}`);
            return false;
        }
    }

    async runAllTests() {
        console.log('🚀 Starting Simple Frontend Capacity Tests...');
        console.log('=' .repeat(50));

        const tests = [
            { name: 'Capacity Display', fn: () => this.testCapacityDisplay() },
            { name: 'Tour Detail API', fn: () => this.testTourDetailAPI() },
            { name: 'Capacity Consistency', fn: () => this.testCapacityConsistency() },
            { name: 'Frontend Integration', fn: () => this.testFrontendIntegration() }
        ];

        let passed = 0;
        const results = [];

        for (const test of tests) {
            try {
                console.log(`\\n🔍 Running ${test.name}...`);
                const result = await test.fn();
                results.push({ test: test.name, status: result ? 'PASS' : 'FAIL' });

                if (result) {
                    console.log(`✅ ${test.name} passed`);
                    passed++;
                } else {
                    console.log(`❌ ${test.name} failed`);
                }
            } catch (error) {
                console.log(`❌ ${test.name} failed with exception: ${error.message}`);
                results.push({ test: test.name, status: 'FAIL' });
            }
        }

        // Summary
        console.log('\\n' + '=' .repeat(50));
        console.log('📊 Test Results Summary:');
        console.log(`🎯 Overall: ${passed}/${tests.length} tests passed (${Math.round((passed/tests.length)*100)}%)`);

        results.forEach(result => {
            const status = result.status === 'PASS' ? '✅' : '❌';
            console.log(`   ${result.test}: ${status} ${result.status}`);
        });

        if (passed === tests.length) {
            console.log('\\n🎉 ALL TESTS PASSED!');
            console.log('✅ Frontend capacity system is working correctly');
            console.log('✅ Capacity data is properly displayed');
            console.log('✅ API integration is functional');
        } else {
            console.log('\\n⚠️ SOME TESTS FAILED!');
            console.log('❌ Frontend capacity system needs attention');
        }

        return passed === tests.length;
    }
}

// Run tests
if (require.main === module) {
    const tester = new SimpleCapacityTester();
    tester.runAllTests().catch(console.error);
}

module.exports = SimpleCapacityTester;
