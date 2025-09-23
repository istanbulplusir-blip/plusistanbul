# Peykan Tourism Admin Guide

## Overview

This guide provides comprehensive information for superusers to manage the Peykan Tourism platform through the Django admin interface.

## Accessing the Admin Panel

1. Navigate to `/admin/` in your browser
2. Login with your superuser credentials
3. You'll see the main admin dashboard with all available apps

## App Structure

The admin panel is organized into the following main sections:

### 1. Users Management
**Location**: Users app
**Purpose**: Manage user accounts, roles, and authentication

#### Key Models:
- **User**: Main user accounts with roles (guest, customer, agent, admin)
- **UserActivity**: Track user login/logout and other activities
- **OTPCode**: One-time password codes for verification

#### Key Features:
- User role management (guest, customer, agent, admin)
- Phone and email verification status
- Agent commission rates
- User activity tracking
- OTP code management

#### Common Actions:
- Create new users with specific roles
- Verify user phone numbers and emails
- Set agent commission rates
- Monitor user activity
- Manage OTP codes

### 2. Tours Management
**Location**: Tours app
**Purpose**: Manage tour products, schedules, and bookings

#### Key Models:
- **TourCategory**: Tour categories (historical, recreational, etc.)
- **Tour**: Main tour products with details and pricing
- **TourVariant**: Tour variants (Eco, Normal, VIP, VVIP)
- **TourSchedule**: Tour availability schedules
- **TourItinerary**: Tour stops and activities
- **TourPricing**: Age-based pricing for variants
- **TourOption**: Tour add-ons and extras
- **TourReview**: Customer reviews and ratings
- **TourBooking**: Tour reservations and bookings

#### Key Features:
- Multi-language support for tour content
- Variant-based pricing system
- Age-based pricing (infant, child, adult)
- Schedule management with capacity tracking
- Itinerary management with stops and activities
- Review and rating system
- Booking management with participant breakdown

#### Common Actions:
- Create and edit tour categories
- Add new tours with variants and pricing
- Manage tour schedules and availability
- Set up tour itineraries
- Configure age-based pricing
- Add tour options and extras
- Moderate customer reviews
- View and manage tour bookings

### 3. Events Management
**Location**: Events app
**Purpose**: Manage event products, performances, and bookings

#### Key Models:
- **EventCategory**: Event categories (music, sports, theater, etc.)
- **Venue**: Event venues with location and capacity
- **Artist**: Event artists and performers
- **Event**: Main event products
- **TicketType**: Event ticket types (VIP, Eco, Normal, etc.)
- **EventPerformance**: Event performances with dates
- **Seat**: Individual seats for performances
- **EventSection**: Event sections with capacity management
- **SectionTicketType**: Ticket types available in sections
- **EventOption**: Event add-ons and extras
- **EventReview**: Customer reviews and ratings
- **EventBooking**: Event reservations and bookings
- **EventDiscount**: Event discounts and promotional codes
- **EventFee**: Event fees and charges
- **EventPricingRule**: Dynamic pricing rules

#### Key Features:
- Multi-language support for event content
- Venue and artist management
- Complex seating and capacity management
- Section-based ticket allocation
- Dynamic pricing rules
- Discount and fee management
- Review and rating system
- Booking management with seat selection

#### Common Actions:
- Create and edit event categories
- Add venues and artists
- Create events with ticket types
- Manage event performances and schedules
- Configure seating and sections
- Set up dynamic pricing rules
- Create discount codes and fees
- Moderate customer reviews
- View and manage event bookings

### 4. Transfers Management
**Location**: Transfers app
**Purpose**: Manage transfer routes, pricing, and bookings

#### Key Models:
- **TransferRoute**: Transfer routes between locations
- **TransferRoutePricing**: Pricing for different vehicle types
- **TransferOption**: Transfer add-ons and extras
- **TransferBooking**: Transfer reservations and bookings

#### Key Features:
- Route-based pricing system
- Vehicle type pricing
- Round-trip discount management
- Peak hour and midnight surcharges
- Option and add-on management
- Booking management

#### Common Actions:
- Create transfer routes between locations
- Set pricing for different vehicle types
- Configure round-trip discounts
- Set up peak hour surcharges
- Add transfer options and extras
- View and manage transfer bookings

### 5. Cart Management
**Location**: Cart app
**Purpose**: Monitor shopping carts and cart items

#### Key Models:
- **Cart**: User shopping carts
- **CartItem**: Individual items in carts

#### Key Features:
- Session-based and user-based carts
- Cart expiration management
- Reservation system for items
- Multi-product support (tours, events, transfers)

#### Common Actions:
- View active shopping carts
- Monitor cart items and reservations
- Clean up expired carts
- Track cart conversion rates

### 6. Orders Management
**Location**: Orders app
**Purpose**: Manage completed orders and order history

#### Key Models:
- **Order**: Completed orders with status tracking
- **OrderItem**: Individual items in orders
- **OrderHistory**: Order status change history

#### Key Features:
- Order status management (pending, confirmed, paid, etc.)
- Payment status tracking
- Agent commission calculation
- Order history and audit trail
- Customer information management

#### Common Actions:
- View and update order status
- Track payment status
- Manage agent commissions
- View order history and changes
- Handle customer information

### 7. Payments Management
**Location**: Payments app
**Purpose**: Track payment transactions

#### Key Models:
- **Payment**: Payment transactions and status

#### Key Features:
- Payment status tracking
- Transaction ID management
- Error message tracking
- Payment method tracking

#### Common Actions:
- View payment transactions
- Track payment status
- Monitor failed payments
- View payment errors

### 8. Agents Management
**Location**: Agents app
**Purpose**: Manage travel agent accounts and performance

#### Key Models:
- **Agent**: Agent accounts
- **AgentProfile**: Extended agent information

#### Key Features:
- Agent account management
- Commission rate configuration
- Performance metrics tracking
- Agent verification system

#### Common Actions:
- Create and manage agent accounts
- Set commission rates
- Track agent performance
- Verify agent accounts

## Common Admin Actions

### Bulk Actions
The admin panel includes several bulk actions for efficient management:

1. **Make Active/Inactive**: Toggle active status for multiple items
2. **Make Featured/Popular**: Mark items as featured or popular
3. **Delete**: Remove multiple items (use with caution)

### Filtering and Search
- Use the filter sidebar to narrow down results
- Use the search box to find specific items
- Combine filters for precise results

### Inline Editing
Many models support inline editing for related objects:
- Tour variants can be edited within the tour form
- Event performances can be managed within the event form
- Cart items are displayed inline with carts

## Best Practices

### User Management
1. Always verify user information before approving accounts
2. Set appropriate commission rates for agents
3. Monitor user activity for suspicious behavior
4. Regularly clean up inactive accounts

### Product Management
1. Use descriptive titles and detailed descriptions
2. Set appropriate pricing for all variants
3. Configure capacity limits carefully
4. Test booking flows before making products active

### Order Management
1. Monitor order status regularly
2. Update payment status promptly
3. Track agent commissions accurately
4. Maintain detailed order history

### Content Management
1. Use high-quality images for products
2. Write engaging descriptions
3. Set up proper categories and tags
4. Keep content up-to-date

## Security Considerations

1. **Access Control**: Only grant admin access to trusted users
2. **Password Policy**: Enforce strong passwords for admin accounts
3. **Session Management**: Monitor admin sessions
4. **Audit Trail**: All admin actions are logged
5. **Data Backup**: Regularly backup admin data

## Troubleshooting

### Common Issues

1. **User Cannot Login**
   - Check if user account is active
   - Verify email/phone verification status
   - Reset password if necessary

2. **Product Not Showing**
   - Check if product is marked as active
   - Verify category settings
   - Check featured/popular status

3. **Booking Issues**
   - Verify product availability
   - Check capacity limits
   - Review pricing configuration

4. **Payment Problems**
   - Check payment status
   - Review transaction logs
   - Verify payment method settings

### Getting Help

1. Check the Django admin documentation
2. Review the model documentation
3. Contact the development team
4. Check system logs for errors

## Advanced Features

### Custom Admin Actions
The admin panel includes custom actions for:
- Bulk status updates
- Data export
- Mass operations

### Admin Logs
All admin actions are logged and can be viewed in the LogEntry model.

### Performance Optimization
- Use filters to reduce query load
- Limit inline objects for better performance
- Use search instead of browsing large lists

## Conclusion

The Peykan Tourism admin panel provides comprehensive management capabilities for all aspects of the platform. Regular monitoring and maintenance will ensure smooth operation and optimal user experience. 