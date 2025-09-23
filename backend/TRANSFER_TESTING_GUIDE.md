# Transfer Product Testing Guide

## Overview

This guide covers comprehensive testing for the Transfer product implementation, including unit tests, integration tests, end-to-end tests, and performance tests.

## Test Structure

### 1. Unit Tests (`test_transfer_pricing_unit.py`)

- **Purpose**: Test individual pricing calculation functions
- **Coverage**: All pricing scenarios, edge cases, validation logic
- **Key Test Cases**:
  - Day/night trip pricing
  - Round trip with discounts
  - Options and surcharges
  - Capacity validation
  - Commission calculation
  - Error handling

### 2. Integration Tests (`test_transfer_agent_integration.py`)

- **Purpose**: Test complete agent order flow
- **Coverage**: End-to-end agent booking process
- **Key Test Cases**:
  - Create pending order
  - Admin confirmation
  - Payment processing
  - Order lifecycle management
  - Error scenarios

### 3. End-to-End Tests (`transfer-booking.spec.ts`)

- **Purpose**: Test complete frontend booking flow
- **Coverage**: User interface and user experience
- **Key Test Cases**:
  - Agent booking flow
  - Customer booking flow
  - Form validation
  - API integration
  - Error handling
  - Responsive design

### 4. Performance Tests (`test_transfer_performance.py`)

- **Purpose**: Test system performance under load
- **Coverage**: Response times, memory usage, concurrency
- **Key Test Cases**:
  - Single calculation performance
  - Bulk calculations
  - Concurrent load testing
  - Memory usage monitoring
  - Database performance

### 5. Test Fixtures (`test_fixtures.py`)

- **Purpose**: Reusable test data and utilities
- **Coverage**: Test data setup, helper functions
- **Components**:
  - Test data factories
  - Predefined scenarios
  - Setup utilities
  - Pytest fixtures

## Running Tests

### Backend Tests

```bash
# Run all transfer tests
python run_transfer_tests.py

# Run specific test modules
python -m pytest test_transfer_pricing_unit.py -v
python -m pytest test_transfer_agent_integration.py -v
python -m pytest test_transfer_performance.py -v

# Run with coverage
python -m pytest --cov=transfers --cov=agents --cov=orders

# Run specific test categories
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m performance
```

### Frontend Tests

```bash
# Run E2E tests
npx playwright test transfer-booking.spec.ts

# Run with specific browser
npx playwright test transfer-booking.spec.ts --project=chromium

# Run in headed mode
npx playwright test transfer-booking.spec.ts --headed

# Run with debug
npx playwright test transfer-booking.spec.ts --debug
```

## Test Data

### Routes

- Tehran to Isfahan (450km)
- Tehran to Shiraz (900km)
- Isfahan to Yazd (320km)

### Vehicle Types

- Sedan (4 passengers, $150 base)
- Van (8 passengers, $200 base)
- Bus (20 passengers, $300 base)

### Options

- Extra Luggage ($10)
- Child Seat ($15)
- WiFi Access ($5)

### Pricing Scenarios

- Day trips (6:00-22:00)
- Night trips (22:00-6:00)
- Round trips (20% discount)
- Options and surcharges

## Test Scenarios

### 1. Pricing Calculation Tests

- ✅ Day trip pricing
- ✅ Night trip with surcharge
- ✅ Round trip with discount
- ✅ Options and surcharges
- ✅ Capacity validation
- ✅ Commission calculation
- ✅ Edge cases (midnight, early morning)

### 2. Agent Order Flow Tests

- ✅ Create pending order
- ✅ Admin confirmation
- ✅ Payment processing
- ✅ Order lifecycle
- ✅ Error handling
- ✅ Rollback scenarios

### 3. Frontend Booking Tests

- ✅ Agent booking flow
- ✅ Customer booking flow
- ✅ Form validation
- ✅ API integration
- ✅ Error handling
- ✅ Responsive design
- ✅ Accessibility

### 4. Performance Tests

- ✅ Single calculation (< 100ms)
- ✅ Bulk calculations (100 in < 5s)
- ✅ Concurrent load (50 threads in < 10s)
- ✅ Memory usage (< 50MB increase)
- ✅ Database performance

## Edge Cases & Pitfalls

### 1. Time Zone Handling

- **Issue**: Different time zones for booking times
- **Test**: Verify time conversion and validation
- **Solution**: Use UTC for storage, local time for display

### 2. Capacity Overflow

- **Issue**: Passengers exceeding vehicle capacity
- **Test**: Validate capacity before order creation
- **Solution**: Real-time capacity validation

### 3. Pricing Consistency

- **Issue**: Different pricing for same parameters
- **Test**: Verify pricing calculation consistency
- **Solution**: Use deterministic pricing logic

### 4. Commission Calculation

- **Issue**: Incorrect commission rates
- **Test**: Verify commission calculation accuracy
- **Solution**: Use Decimal for precise calculations

### 5. Order Status Transitions

- **Issue**: Invalid status transitions
- **Test**: Verify status transition rules
- **Solution**: Implement state machine validation

## Test Coverage Requirements

### Backend Coverage

- **Models**: 100% coverage
- **Views**: 95% coverage
- **Services**: 100% coverage
- **Serializers**: 95% coverage
- **Utils**: 100% coverage

### Frontend Coverage

- **Components**: 90% coverage
- **Stores**: 100% coverage
- **API calls**: 100% coverage
- **Error handling**: 100% coverage

## Continuous Integration

### GitHub Actions

```yaml
name: Transfer Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run backend tests
        run: python run_transfer_tests.py
      - name: Run frontend tests
        run: npx playwright test
```

## Test Maintenance

### Regular Updates

- Update test data monthly
- Review test coverage quarterly
- Update performance benchmarks
- Maintain test documentation

### Test Data Management

- Use factories for test data
- Clean up test data after tests
- Use database transactions for isolation
- Mock external dependencies

## Troubleshooting

### Common Issues

1. **Test Database Issues**

   - Ensure test database is properly configured
   - Check database migrations
   - Verify test data setup

2. **Performance Test Failures**

   - Check system resources
   - Verify test environment
   - Review performance benchmarks

3. **E2E Test Failures**
   - Check browser compatibility
   - Verify test environment
   - Review test selectors

### Debug Commands

```bash
# Debug specific test
python -m pytest test_transfer_pricing_unit.py::TestTransferPricing::test_day_trip_pricing -v -s

# Debug with pdb
python -m pytest test_transfer_pricing_unit.py --pdb

# Debug E2E test
npx playwright test transfer-booking.spec.ts --debug
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Test Data**: Use factories and fixtures
3. **Assertions**: Use specific assertions
4. **Error Testing**: Test both success and failure cases
5. **Performance**: Monitor test execution time
6. **Documentation**: Keep tests well-documented
7. **Maintenance**: Regular test review and updates

## Conclusion

This comprehensive testing suite ensures the Transfer product works correctly, performs well, and provides a good user experience. Regular testing and maintenance are essential for maintaining product quality.
