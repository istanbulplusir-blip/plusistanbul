# Tour Booking System Flow Documentation

## Overview

This document explains how our tour booking system works for both guest and registered users, from tour selection to order completion. The system handles capacity management, validation, and restrictions throughout the booking process.

## System Architecture

### Backend (Django DRF)

- **Framework**: Django REST Framework
- **Database**: PostgreSQL with complex tour-related models
- **Authentication**: JWT tokens for registered users, session-based for guests
- **Rate Limiting**: API request throttling to prevent abuse

### Frontend (Next.js)

- **Framework**: Next.js with TypeScript
- **UI**: React components with real-time validation
- **Internationalization**: Persian and English support
- **State Management**: React hooks for form state and API calls

## Core Database Models

### Tour-Related Models

```python
Tour: Main tour information (name, description, base price)
TourVariant: Different versions of a tour (Standard, Premium, etc.)
TourSchedule: Specific dates and times for tours
TourOption: Additional services (transfer, guide, meal, etc.)
TourPricing: Dynamic pricing based on participants and options
```

### Booking Models

```python
Cart: Shopping cart for users (with session_id for guests)
CartItem: Individual items in cart
Order: Completed orders with status tracking
OrderItem: Individual items in orders
```

## Complete Booking Flow

### 1. Tour Selection & Display

#### Frontend Process

1. **Tour Detail Page**: `/tours/[slug]/page.tsx`
   - Displays tour information, schedules, and pricing
   - Shows real-time capacity availability
   - Presents participant selection interface

#### Backend API

- **Endpoint**: `GET /api/v1/tours/{slug}/`
- **Response**: Tour details, schedules, current capacity
- **Capacity Calculation**: Includes pending orders in availability

### 2. Participant & Option Selection

#### Frontend Validation

```typescript
// Real-time validation with immediate feedback
- Adults + Children: Limited by tour capacity
- Infants: Maximum 2 per booking
- Options: Limited by max_quantity per option
- Total participants: Cannot exceed tour capacity
```

#### UI Behavior

- **Increment/Decrement Buttons**: Disabled when limits reached
- **Real-time Pricing**: Updates as selections change
- **Capacity Display**: Shows "X of Y Available"
- **Error Messages**: Contextual inline and toast notifications

#### Backend Validation

- **Rate Limiting**: 20 requests per minute (exempts dry_run)
- **Capacity Check**: Verifies availability before allowing cart addition
- **Duplicate Booking**: Prevents multiple bookings for same tour/date

### 3. Add to Cart Process

#### Frontend Process

1. **User clicks "Add to Cart"**
2. **Frontend validation** (client-side checks)
3. **API call** to `/api/v1/cart/add/`
4. **Success/Error handling** with user feedback

#### Backend Process

```python
def create(self, request):
    # 1. Rate limiting check
    # 2. Input validation
    # 3. Capacity availability check
    # 4. Duplicate booking check
    # 5. Cart item creation/update
    # 6. Response with success/error
```

#### Validation Layers

1. **Rate Limiting**: Prevents API abuse
2. **Capacity Check**: Ensures sufficient availability
3. **Duplicate Check**: Prevents multiple bookings
4. **Input Validation**: Validates participant counts and options

### 4. Cart Management

#### Cart Structure

```python
Cart:
  - user: User (null for guests)
  - session_id: String (for guest users)
  - created_at: DateTime
  - updated_at: DateTime

CartItem:
  - cart: Cart
  - tour_schedule: TourSchedule
  - tour_option: TourOption (optional)
  - adults: Integer
  - children: Integer
  - infants: Integer
  - special_requests: Text (optional)
  - total_price: Decimal
```

#### Guest vs Registered Users

- **Guest Users**: Identified by `session_id`
- **Registered Users**: Identified by `user` field
- **Cart Persistence**: Session-based for guests, user-based for registered

### 5. Checkout Process

#### Frontend Process

1. **Cart Review**: Display selected items and total
2. **User Information**: Collect contact details
3. **Order Creation**: Submit to `/api/v1/orders/create/`
4. **Status Handling**: Redirect to order confirmation

#### Backend Process

```python
def create(self, request):
    # 1. Authentication check
    # 2. Cart validation
    # 3. Order creation
    # 4. Capacity update
    # 5. Cart cleanup
    # 6. Order confirmation
```

### 6. Order Management

#### Order Status Flow

```python
Order Statuses:
  - pending: Initial state (requires admin confirmation)
  - confirmed: Admin approved
  - paid: Payment received
  - completed: Tour completed
  - cancelled: Order cancelled
  - refunded: Payment refunded
  - failed: Payment failed
```

#### Capacity Management

- **Pending Orders**: Included in capacity calculations
- **Status Changes**: Automatically update capacity when status changes
- **Capacity Field**: `variant_capacities_raw` on TourSchedule

## Security & Validation Features

### Frontend Security

- **Client-side Validation**: Immediate user feedback
- **Button States**: Disabled when limits reached
- **Debouncing**: Prevents excessive API calls
- **Error Handling**: Graceful error display

### Backend Security

- **Rate Limiting**: API abuse prevention
- **Server-side Validation**: Critical business logic validation
- **Capacity Checks**: Real-time availability verification
- **Duplicate Prevention**: Multiple booking protection
- **Authentication**: JWT and session-based auth

### Data Integrity

- **Capacity Tracking**: Accurate availability calculation
- **Order Status Management**: Proper state transitions
- **Audit Trail**: Complete booking history
- **Special Requests**: Stored and admin-visible

## Error Handling & User Experience

### Frontend Error Types

1. **Validation Errors**: Participant/option limits
2. **Capacity Errors**: Insufficient availability
3. **Duplicate Errors**: Multiple booking attempts
4. **Rate Limit Errors**: Too many requests
5. **Network Errors**: Connection issues

### Error Display

- **Toast Notifications**: Transient error messages
- **Inline Messages**: Contextual validation feedback
- **Button States**: Visual indication of limitations
- **Internationalization**: Persian and English messages

## Capacity Calculation Logic

### Real-time Capacity

```python
def calculate_available_capacity(schedule, variant):
    # Get base capacity from variant_capacities_raw
    base_capacity = schedule.variant_capacities_raw[variant.id]['capacity']

    # Sum all bookings (cart + orders)
    cart_bookings = CartItem.objects.filter(...).aggregate(Sum('adults') + Sum('children'))
    order_bookings = OrderItem.objects.filter(...).aggregate(Sum('adults') + Sum('children'))

    # Calculate available
    available = base_capacity - cart_bookings - order_bookings
    return max(0, available)
```

### Capacity Updates

- **Cart Addition**: Immediate capacity check
- **Order Creation**: Capacity reserved
- **Status Changes**: Capacity adjusted based on order status
- **Admin Actions**: Manual capacity management

## Special Features

### Guest User Support

- **Session-based Cart**: No registration required
- **Temporary Storage**: Cart items persist during session
- **Order Creation**: Guest orders with contact information

### Admin Features

- **Order Management**: Status updates and capacity control
- **Special Requests**: View and manage customer requests
- **Capacity Override**: Manual capacity adjustments
- **Order History**: Complete booking audit trail

### Internationalization

- **Multi-language**: Persian and English support
- **Dynamic Messages**: Context-aware translations
- **User Preferences**: Language selection

## Testing & Quality Assurance

### Automated Testing

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Complete booking flow testing
- **Capacity Tests**: Availability calculation verification

### Manual Testing

- **User Scenarios**: Real booking flow testing
- **Edge Cases**: Limit testing and error conditions
- **Cross-browser**: Compatibility verification
- **Mobile Testing**: Responsive design validation

## Performance Considerations

### Frontend Optimization

- **Debouncing**: API call rate limiting
- **Caching**: Tour data and pricing caching
- **Lazy Loading**: Component and data loading
- **Error Boundaries**: Graceful error handling

### Backend Optimization

- **Database Indexing**: Efficient query performance
- **Caching**: Rate limiting and session data
- **API Optimization**: Minimal data transfer
- **Background Tasks**: Async processing where possible

## Future Enhancements

### Planned Features

- **Payment Integration**: Online payment processing
- **Email Notifications**: Booking confirmations
- **Admin Dashboard**: Enhanced management interface
- **Analytics**: Booking and capacity analytics
- **Mobile App**: Native mobile application

### Scalability Considerations

- **Microservices**: Service decomposition
- **Load Balancing**: Traffic distribution
- **Database Sharding**: Data partitioning
- **CDN Integration**: Static content delivery

## Conclusion

This tour booking system provides a comprehensive solution for managing tour reservations with robust validation, capacity management, and user experience features. The system handles both guest and registered users, maintains data integrity, and provides admin tools for order management.

The architecture ensures scalability, security, and maintainability while delivering a smooth user experience for tour booking operations.
