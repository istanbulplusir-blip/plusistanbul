/**
 * End-to-End Tests for Transfer Booking Flow
 * Tests complete frontend booking simulation including agent and customer flows
 */

import { test, expect, Page } from '@playwright/test';

// Test data
const testRoute = {
  id: 1,
  name: 'Tehran to Isfahan',
  from_location: 'Tehran',
  to_location: 'Isfahan',
  distance: 450
};

const testPricing = {
  id: 1,
  vehicle_type: 'sedan',
  base_price: 150.00,
  night_surcharge: 25.00,
  return_discount: 0.20,
  max_capacity: 4
};

const testOption = {
  id: 1,
  name: 'Extra Luggage',
  price: 10.00
};

// Helper functions
async function loginAsAgent(page: Page) {
  await page.goto('/agent/login');
  await page.fill('[data-testid="username"]', 'testagent');
  await page.fill('[data-testid="password"]', 'testpass123');
  await page.click('[data-testid="login-button"]');
  await expect(page).toHaveURL('/agent/dashboard');
}

async function loginAsCustomer(page: Page) {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'customer@test.com');
  await page.fill('[data-testid="password"]', 'testpass123');
  await page.click('[data-testid="login-button"]');
  await expect(page).toHaveURL('/dashboard');
}

async function mockApiResponses(page: Page) {
  // Mock transfer routes API
  await page.route('**/api/transfers/routes/', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: [testRoute],
        count: 1
      })
    });
  });

  // Mock transfer pricing API
  await page.route('**/api/transfers/pricing/**', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        pricing: {
          base_price: testPricing.base_price,
          night_surcharge: 0,
          options_total: 0,
          return_price: 0,
          return_discount: 0,
          final_price: testPricing.base_price,
          agent_commission: testPricing.base_price * 0.10,
          customer_price: testPricing.base_price
        },
        capacity_info: {
          is_valid: true,
          passenger_count: 2,
          max_capacity: testPricing.max_capacity
        },
        trip_info: {
          route_name: testRoute.name,
          from_location: testRoute.from_location,
          to_location: testRoute.to_location,
          vehicle_type: testPricing.vehicle_type,
          trip_type: 'one_way',
          passenger_count: 2,
          booking_time: '14:00',
          return_time: null
        }
      })
    });
  });

  // Mock transfer options API
  await page.route('**/api/transfers/options/**', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: [testOption],
        count: 1
      })
    });
  });

  // Mock agent booking API
  await page.route('**/api/agents/book/transfer/', async route => {
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        order_id: 123,
        message: 'Transfer booking created successfully'
      })
    });
  });
}

test.describe('Transfer Booking E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiResponses(page);
  });

  test('Agent Transfer Booking Flow - Complete Journey', async ({ page }) => {
    // Step 1: Login as agent
    await loginAsAgent(page);

    // Step 2: Navigate to transfer booking page
    await page.goto('/agent/book/transfer');
    await expect(page).toHaveURL('/agent/book/transfer');

    // Step 3: Select route
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await expect(page.locator('[data-testid="selected-route"]')).toContainText(testRoute.name);

    // Step 4: Select vehicle type
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);
    await expect(page.locator('[data-testid="selected-vehicle"]')).toContainText(testPricing.vehicle_type);

    // Step 5: Set passenger count
    await page.fill('[data-testid="passenger-count"]', '2');
    await expect(page.locator('[data-testid="passenger-count"]')).toHaveValue('2');

    // Step 6: Select trip type
    await page.click('[data-testid="trip-type-one-way"]');
    await expect(page.locator('[data-testid="trip-type-one-way"]')).toBeChecked();

    // Step 7: Set booking date
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);

    // Step 8: Set booking time
    await page.fill('[data-testid="booking-time"]', '14:00');
    await expect(page.locator('[data-testid="booking-time"]')).toHaveValue('14:00');

    // Step 9: Calculate pricing
    await page.click('[data-testid="calculate-pricing-button"]');
    await expect(page.locator('[data-testid="pricing-loading"]')).toBeVisible();
    await expect(page.locator('[data-testid="pricing-result"]')).toBeVisible({ timeout: 10000 });

    // Step 10: Verify pricing display
    await expect(page.locator('[data-testid="base-price"]')).toContainText('150.00');
    await expect(page.locator('[data-testid="final-price"]')).toContainText('150.00');
    await expect(page.locator('[data-testid="agent-commission"]')).toContainText('15.00');

    // Step 11: Add customer information
    await page.fill('[data-testid="customer-name"]', 'Test Customer');
    await page.fill('[data-testid="customer-phone"]', '09123456789');
    await page.fill('[data-testid="customer-email"]', 'customer@test.com');

    // Step 12: Select payment method
    await page.click('[data-testid="payment-method-whatsapp"]');
    await expect(page.locator('[data-testid="payment-method-whatsapp"]')).toBeChecked();

    // Step 13: Submit booking
    await page.click('[data-testid="submit-booking-button"]');
    await expect(page.locator('[data-testid="booking-success"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="order-id"]')).toContainText('123');
  });

  test('Agent Transfer Booking - Round Trip with Options', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Select route and vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    // Set passenger count
    await page.fill('[data-testid="passenger-count"]', '3');

    // Select round trip
    await page.click('[data-testid="trip-type-round-trip"]');
    await expect(page.locator('[data-testid="trip-type-round-trip"]')).toBeChecked();

    // Set dates and times
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '14:00');
    await page.fill('[data-testid="return-time"]', '16:00');

    // Add option
    await page.click('[data-testid="option-extra-luggage"]');
    await expect(page.locator('[data-testid="option-extra-luggage"]')).toBeChecked();

    // Calculate pricing
    await page.click('[data-testid="calculate-pricing-button"]');
    await expect(page.locator('[data-testid="pricing-result"]')).toBeVisible({ timeout: 10000 });

    // Verify round trip pricing
    await expect(page.locator('[data-testid="base-price"]')).toContainText('150.00');
    await expect(page.locator('[data-testid="return-price"]')).toContainText('120.00');
    await expect(page.locator('[data-testid="return-discount"]')).toContainText('30.00');
    await expect(page.locator('[data-testid="options-total"]')).toContainText('10.00');
    await expect(page.locator('[data-testid="final-price"]')).toContainText('280.00'); // 150 + 120 + 10
  });

  test('Agent Transfer Booking - Night Surcharge', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Select route and vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    // Set passenger count
    await page.fill('[data-testid="passenger-count"]', '2');

    // Set night time
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '23:00'); // Night time

    // Calculate pricing
    await page.click('[data-testid="calculate-pricing-button"]');
    await expect(page.locator('[data-testid="pricing-result"]')).toBeVisible({ timeout: 10000 });

    // Verify night surcharge
    await expect(page.locator('[data-testid="base-price"]')).toContainText('150.00');
    await expect(page.locator('[data-testid="night-surcharge"]')).toContainText('25.00');
    await expect(page.locator('[data-testid="final-price"]')).toContainText('175.00');
  });

  test('Agent Transfer Booking - Capacity Validation', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Select route and vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    // Set passenger count exceeding capacity
    await page.fill('[data-testid="passenger-count"]', '5'); // Exceeds max capacity of 4

    // Set date and time
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '14:00');

    // Try to calculate pricing
    await page.click('[data-testid="calculate-pricing-button"]');
    await expect(page.locator('[data-testid="capacity-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="capacity-error"]')).toContainText('capacity');
  });

  test('Agent Transfer Booking - Validation Errors', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Try to submit without selecting route
    await page.click('[data-testid="submit-booking-button"]');
    await expect(page.locator('[data-testid="route-error"]')).toBeVisible();

    // Select route but not vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="submit-booking-button"]');
    await expect(page.locator('[data-testid="vehicle-error"]')).toBeVisible();

    // Select vehicle but no passenger count
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);
    await page.click('[data-testid="submit-booking-button"]');
    await expect(page.locator('[data-testid="passenger-error"]')).toBeVisible();

    // Set invalid passenger count
    await page.fill('[data-testid="passenger-count"]', '0');
    await page.click('[data-testid="submit-booking-button"]');
    await expect(page.locator('[data-testid="passenger-error"]')).toContainText('valid');
  });

  test('Customer Transfer Booking Flow', async ({ page }) => {
    // Step 1: Login as customer
    await loginAsCustomer(page);

    // Step 2: Navigate to transfer booking
    await page.goto('/book/transfer');
    await expect(page).toHaveURL('/book/transfer');

    // Step 3: Select route
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);

    // Step 4: Select vehicle type
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    // Step 5: Set passenger count
    await page.fill('[data-testid="passenger-count"]', '2');

    // Step 6: Set date and time
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '14:00');

    // Step 7: Calculate pricing
    await page.click('[data-testid="calculate-pricing-button"]');
    await expect(page.locator('[data-testid="pricing-result"]')).toBeVisible({ timeout: 10000 });

    // Step 8: Verify pricing (customer sees final price, not commission)
    await expect(page.locator('[data-testid="final-price"]')).toContainText('150.00');
    await expect(page.locator('[data-testid="agent-commission"]')).not.toBeVisible();

    // Step 9: Add contact information
    await page.fill('[data-testid="contact-name"]', 'Test Customer');
    await page.fill('[data-testid="contact-phone"]', '09123456789');
    await page.fill('[data-testid="contact-email"]', 'customer@test.com');

    // Step 10: Submit booking
    await page.click('[data-testid="submit-booking-button"]');
    await expect(page.locator('[data-testid="booking-success"]')).toBeVisible({ timeout: 10000 });
  });

  test('Transfer Booking - Error Handling', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Mock API error
    await page.route('**/api/transfers/pricing/**', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal server error'
        })
      });
    });

    // Select route and vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    // Set passenger count
    await page.fill('[data-testid="passenger-count"]', '2');

    // Set date and time
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '14:00');

    // Try to calculate pricing
    await page.click('[data-testid="calculate-pricing-button"]');
    await expect(page.locator('[data-testid="pricing-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="pricing-error"]')).toContainText('error');
  });

  test('Transfer Booking - Responsive Design', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Verify mobile layout
    await expect(page.locator('[data-testid="mobile-layout"]')).toBeVisible();
    await expect(page.locator('[data-testid="desktop-layout"]')).not.toBeVisible();

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();

    // Verify tablet layout
    await expect(page.locator('[data-testid="tablet-layout"]')).toBeVisible();

    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.reload();

    // Verify desktop layout
    await expect(page.locator('[data-testid="desktop-layout"]')).toBeVisible();
    await expect(page.locator('[data-testid="mobile-layout"]')).not.toBeVisible();
  });

  test('Transfer Booking - Accessibility', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="route-selector"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="vehicle-type-selector"]')).toBeFocused();

    // Test ARIA labels
    await expect(page.locator('[data-testid="route-selector"]')).toHaveAttribute('aria-label');
    await expect(page.locator('[data-testid="vehicle-type-selector"]')).toHaveAttribute('aria-label');
    await expect(page.locator('[data-testid="passenger-count"]')).toHaveAttribute('aria-label');

    // Test screen reader support
    await expect(page.locator('[data-testid="pricing-result"]')).toHaveAttribute('role', 'region');
    await expect(page.locator('[data-testid="pricing-result"]')).toHaveAttribute('aria-live', 'polite');
  });

  test('Transfer Booking - Step Navigation', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Test step navigation
    await expect(page.locator('[data-testid="step-0"]')).toHaveClass(/bg-blue-600/);
    await expect(page.locator('[data-testid="step-title-0"]')).toContainText('Route');

    // Complete first step
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="next-step-button"]');

    // Verify step 2 is active
    await expect(page.locator('[data-testid="step-1"]')).toHaveClass(/bg-blue-600/);
    await expect(page.locator('[data-testid="step-title-1"]')).toContainText('Vehicle');

    // Go back to previous step
    await page.click('[data-testid="previous-step-button"]');
    await expect(page.locator('[data-testid="step-0"]')).toHaveClass(/bg-blue-600/);
  });

  test('Transfer Booking - Validation Messages', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Try to proceed without selecting route
    await page.click('[data-testid="next-step-button"]');
    await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="validation-error"]')).toContainText('Route selection is required');

    // Select route and try to proceed without vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="next-step-button"]');
    await page.click('[data-testid="next-step-button"]');
    await expect(page.locator('[data-testid="validation-error"]')).toContainText('Vehicle type selection is required');
  });

  test('Transfer Booking - Time Surcharge Warnings', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Select route and vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    // Set night time
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '23:00'); // Night time

    // Check for night surcharge warning
    await expect(page.locator('[data-testid="night-surcharge-warning"]')).toBeVisible();
    await expect(page.locator('[data-testid="night-surcharge-warning"]')).toContainText('Night hour surcharge applies');
  });

  test('Transfer Booking - Round Trip Discount Validation', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Select route and vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    // Select round trip
    await page.click('[data-testid="trip-type-round-trip"]');

    // Set dates with more than 7 days difference
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 10);
    
    await page.fill('[data-testid="booking-date"]', tomorrow.toISOString().split('T')[0]);
    await page.fill('[data-testid="return-date"]', nextWeek.toISOString().split('T')[0]);

    // Check for discount warning
    await expect(page.locator('[data-testid="discount-warning"]')).toBeVisible();
    await expect(page.locator('[data-testid="discount-warning"]')).toContainText('Round trip discount not available');
  });

  test('Transfer Booking - Capacity Validation', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Select route and vehicle
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    // Set passenger count exceeding capacity
    await page.fill('[data-testid="passenger-count"]', '5'); // Exceeds sedan capacity of 4

    // Check for capacity error
    await expect(page.locator('[data-testid="capacity-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="capacity-error"]')).toContainText('Exceeds maximum capacity');
  });

  test('Transfer Booking - WhatsApp Payment Flow', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Complete full booking flow
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '14:00');

    await page.fill('[data-testid="passenger-count"]', '2');
    await page.fill('[data-testid="customer-name"]', 'Test Customer');
    await page.fill('[data-testid="customer-phone"]', '09123456789');

    // Verify WhatsApp payment is selected by default
    await expect(page.locator('[data-testid="payment-method-whatsapp"]')).toBeChecked();

    // Submit booking
    await page.click('[data-testid="submit-booking-button"]');
    await expect(page.locator('[data-testid="booking-success"]')).toBeVisible();
    await expect(page.locator('[data-testid="order-id"]')).toContainText('123');
  });

  test('Transfer Booking - Commission Display', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Complete booking setup
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '14:00');

    // Calculate pricing
    await page.click('[data-testid="calculate-pricing-button"]');
    await expect(page.locator('[data-testid="pricing-result"]')).toBeVisible();

    // Verify commission is displayed
    await expect(page.locator('[data-testid="agent-commission"]')).toBeVisible();
    await expect(page.locator('[data-testid="agent-commission"]')).toContainText('15.00');
  });

  test('Transfer Booking - Form Reset After Success', async ({ page }) => {
    await loginAsAgent(page);
    await page.goto('/agent/book/transfer');

    // Complete booking
    await page.click('[data-testid="route-selector"]');
    await page.click(`[data-testid="route-option-${testRoute.id}"]`);
    await page.click('[data-testid="vehicle-type-selector"]');
    await page.click(`[data-testid="vehicle-option-${testPricing.vehicle_type}"]`);

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    await page.fill('[data-testid="booking-date"]', dateString);
    await page.fill('[data-testid="booking-time"]', '14:00');
    await page.fill('[data-testid="passenger-count"]', '2');
    await page.fill('[data-testid="customer-name"]', 'Test Customer');
    await page.fill('[data-testid="customer-phone"]', '09123456789');

    await page.click('[data-testid="submit-booking-button"]');
    await expect(page.locator('[data-testid="booking-success"]')).toBeVisible();

    // Verify form is reset
    await expect(page.locator('[data-testid="route-selector"]')).not.toHaveValue();
    await expect(page.locator('[data-testid="passenger-count"]')).toHaveValue('1');
    await expect(page.locator('[data-testid="customer-name"]')).toHaveValue('');
  });
});
