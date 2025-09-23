/**
 * E2E Test Utilities
 * Common functions and helpers for transfer booking tests
 */

import { Page, expect } from '@playwright/test';

// Test data
export const testRoute = {
  id: 1,
  name: 'Tehran to Isfahan',
  from_location: 'Tehran',
  to_location: 'Isfahan',
  distance: 450
};

export const testPricing = {
  id: 1,
  vehicle_type: 'sedan',
  base_price: 150.00,
  night_surcharge: 25.00,
  return_discount: 0.20,
  max_capacity: 4
};

export const testOption = {
  id: 1,
  name: 'Extra Luggage',
  price: 10.00
};

// Helper functions
export async function loginAsAgent(page: Page) {
  await page.goto('/agent/login');
  await page.fill('[data-testid="username"]', 'testagent');
  await page.fill('[data-testid="password"]', 'testpass123');
  await page.click('[data-testid="login-button"]');
  await expect(page).toHaveURL('/agent/dashboard');
}

export async function loginAsCustomer(page: Page) {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'customer@test.com');
  await page.fill('[data-testid="password"]', 'testpass123');
  await page.click('[data-testid="login-button"]');
  await expect(page).toHaveURL('/dashboard');
}

export async function mockApiResponses(page: Page) {
  // Mock transfer routes API
  await page.route('**/api/agents/transfers/routes/', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        routes: [testRoute],
        count: 1
      })
    });
  });

  // Mock transfer pricing API
  await page.route('**/api/agents/pricing/transfer/', async route => {
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
        success: true,
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

export async function selectRoute(page: Page, routeId: number = testRoute.id) {
  await page.click('[data-testid="route-selector"]');
  await page.click(`[data-testid="route-option-${routeId}"]`);
  await expect(page.locator('[data-testid="selected-route"]')).toContainText(testRoute.name);
}

export async function selectVehicle(page: Page, vehicleType: string = testPricing.vehicle_type) {
  await page.click('[data-testid="vehicle-type-selector"]');
  await page.click(`[data-testid="vehicle-option-${vehicleType}"]`);
  await expect(page.locator('[data-testid="selected-vehicle"]')).toContainText(vehicleType);
}

export async function setBookingDateTime(page: Page, daysFromNow: number = 1, time: string = '14:00') {
  const bookingDate = new Date();
  bookingDate.setDate(bookingDate.getDate() + daysFromNow);
  const dateString = bookingDate.toISOString().split('T')[0];
  
  await page.fill('[data-testid="booking-date"]', dateString);
  await page.fill('[data-testid="booking-time"]', time);
}

export async function setPassengerCount(page: Page, count: number = 2) {
  await page.fill('[data-testid="passenger-count"]', count.toString());
  await expect(page.locator('[data-testid="passenger-count"]')).toHaveValue(count.toString());
}

export async function setCustomerInfo(page: Page, customerData: {
  name?: string;
  phone?: string;
  email?: string;
} = {}) {
  const defaultData = {
    name: 'Test Customer',
    phone: '09123456789',
    email: 'customer@test.com'
  };
  
  const data = { ...defaultData, ...customerData };
  
  if (data.name) {
    await page.fill('[data-testid="customer-name"]', data.name);
  }
  if (data.phone) {
    await page.fill('[data-testid="customer-phone"]', data.phone);
  }
  if (data.email) {
    await page.fill('[data-testid="customer-email"]', data.email);
  }
}

export async function calculatePricing(page: Page) {
  await page.click('[data-testid="calculate-pricing-button"]');
  await expect(page.locator('[data-testid="pricing-loading"]')).toBeVisible();
  await expect(page.locator('[data-testid="pricing-result"]')).toBeVisible({ timeout: 10000 });
}

export async function submitBooking(page: Page) {
  await page.click('[data-testid="submit-booking-button"]');
  await expect(page.locator('[data-testid="booking-success"]')).toBeVisible({ timeout: 10000 });
}

export async function completeBasicBooking(page: Page) {
  await selectRoute(page);
  await selectVehicle(page);
  await setBookingDateTime(page);
  await setPassengerCount(page);
  await setCustomerInfo(page);
  await calculatePricing(page);
}

export async function navigateToStep(page: Page, stepIndex: number) {
  // Navigate through steps by clicking next button
  for (let i = 0; i < stepIndex; i++) {
    await page.click('[data-testid="next-step-button"]');
  }
}

export async function goToPreviousStep(page: Page) {
  await page.click('[data-testid="previous-step-button"]');
}

export async function expectValidationError(page: Page, errorText: string) {
  await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
  await expect(page.locator('[data-testid="validation-error"]')).toContainText(errorText);
}

export async function expectValidationWarning(page: Page, warningText: string) {
  await expect(page.locator('[data-testid="validation-warning"]')).toBeVisible();
  await expect(page.locator('[data-testid="validation-warning"]')).toContainText(warningText);
}

export async function expectPricingDisplay(page: Page, expectedPrice: number) {
  await expect(page.locator('[data-testid="final-price"]')).toContainText(expectedPrice.toString());
}

export async function expectCommissionDisplay(page: Page, expectedCommission: number) {
  await expect(page.locator('[data-testid="agent-commission"]')).toContainText(expectedCommission.toString());
}

export async function expectFormReset(page: Page) {
  await expect(page.locator('[data-testid="route-selector"]')).not.toHaveValue();
  await expect(page.locator('[data-testid="passenger-count"]')).toHaveValue('1');
  await expect(page.locator('[data-testid="customer-name"]')).toHaveValue('');
}

// Test scenarios
export const testScenarios = {
  dayTrip: {
    name: 'Day Trip Booking',
    time: '14:00',
    expectedSurcharge: 0
  },
  nightTrip: {
    name: 'Night Trip Booking',
    time: '23:00',
    expectedSurcharge: 25.00
  },
  roundTrip: {
    name: 'Round Trip Booking',
    tripType: 'round_trip',
    expectedDiscount: 0.20
  },
  capacityExceeded: {
    name: 'Capacity Exceeded',
    passengerCount: 5,
    expectedError: 'Exceeds maximum capacity'
  },
  invalidDate: {
    name: 'Invalid Date',
    daysFromNow: -1,
    expectedError: 'Booking date cannot be in the past'
  }
};

// Mock data generators
export function generateMockRoute(overrides: Partial<typeof testRoute> = {}) {
  return { ...testRoute, ...overrides };
}

export function generateMockPricing(overrides: Partial<typeof testPricing> = {}) {
  return { ...testPricing, ...overrides };
}

export function generateMockOption(overrides: Partial<typeof testOption> = {}) {
  return { ...testOption, ...overrides };
}

// Wait utilities
export async function waitForApiCall(page: Page, urlPattern: string, timeout: number = 10000) {
  return page.waitForResponse(response => 
    response.url().includes(urlPattern) && response.status() === 200,
    { timeout }
  );
}

export async function waitForElementToBeVisible(page: Page, selector: string, timeout: number = 10000) {
  await page.waitForSelector(selector, { state: 'visible', timeout });
}

export async function waitForElementToBeHidden(page: Page, selector: string, timeout: number = 10000) {
  await page.waitForSelector(selector, { state: 'hidden', timeout });
}
