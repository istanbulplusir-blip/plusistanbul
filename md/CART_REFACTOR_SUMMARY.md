# Cart System Refactor Summary

## Overview

The cart system has been completely refactored to support dynamic multi-product rendering with discriminated union types for different product types (tour, event, transfer).

## Key Changes

### 1. **TypeScript Types** (`frontend/types/cart.ts`)

- **BaseCartItem**: Common interface for all cart items
- **TourCartItem**: Tour-specific interface with participant breakdown
- **EventCartItem**: Event-specific interface with performance and seat info
- **TransferCartItem**: Transfer-specific interface with route and vehicle info
- **Discriminated Union**: `CartItem = TourCartItem | EventCartItem | TransferCartItem`

### 2. **Component Architecture**

#### **Main Cart Page** (`frontend/app/[locale]/cart/page.tsx`)

- **Dynamic Rendering**: Uses `renderCartItem()` function to switch on `item.product_type`
- **API Integration**: Properly integrates with backend cart API
- **State Management**: Handles loading states and error handling
- **Authentication**: Redirects to login if not authenticated

#### **Product-Specific Components**

##### **TourCartItem** (`frontend/components/cart/TourCartItem.tsx`)

- **Participant Breakdown**: Shows adult/child/infant counts with +/- controls
- **Tour Details**: Displays tour title, variant, date/time
- **Options Display**: Shows selected options with pricing
- **Pricing**: Displays unit price, options total, and final price

##### **EventCartItem** (`frontend/components/cart/EventCartItem.tsx`)

- **Performance Info**: Shows event title, performance date/time, section
- **Seat Numbers**: Displays selected seat numbers as badges
- **Ticket Details**: Shows variant name and quantity
- **Options**: Displays selected options with pricing

##### **TransferCartItem** (`frontend/components/cart/TransferCartItem.tsx`)

- **Route Display**: Shows origin → destination with arrow
- **Vehicle Info**: Displays vehicle type and trip type (one-way/round-trip)
- **Passenger/Luggage**: Shows passenger and luggage counts
- **Addresses**: Displays pickup and dropoff addresses if available
- **Time Info**: Shows outbound and return times

### 3. **Features Implemented**

#### **Dynamic Product Rendering**

- ✅ Switch on `item.product_type` to render appropriate component
- ✅ Each component shows product-specific information
- ✅ Consistent UI patterns across all product types

#### **Pricing Display**

- ✅ **unit_price**: Base price per item/person
- ✅ **options_total**: Sum of all selected options
- ✅ **total_price**: Final price from backend API
- ✅ No frontend price calculation - uses backend as source of truth

#### **Selected Options**

- ✅ **name**: Option display name
- ✅ **price**: Individual option price
- ✅ **quantity**: Option quantity
- ✅ **total**: Option price × quantity
- ✅ Proper formatting and display

#### **Editing Controls**

- ✅ **Tour**: Participant breakdown (A/C/I) قابل ویرایش درجا؛ PATCH به `booking_data.participants`
- ✅ **Event**: مودال ساده برای ویرایش آپشن‌ها و درخواست‌ها؛ PATCH به `selected_options`/`booking_data`
- ✅ **Transfer**: مودال ساده برای ویرایش زمان/مسافر/چمدان؛ PATCH به `booking_data`
- ✅ **API Integration**: به‌روزرسانی‌ها به بک‌اند ارسال و UI Sync می‌شود

#### **Order Summary**

- ✅ **cart.subtotal**: Sum of all item total_price values
- ✅ **cart.tax_amount**: Calculated tax (10% of subtotal)
- ✅ **cart.total_amount**: Final total with tax
- ✅ No frontend recalculation - uses backend values

### 4. **Translation Support**

- ✅ **English**: Complete translation keys for all new fields
- ✅ **Persian**: Complete translation keys for all new fields
- ✅ **New Keys Added**:
  - `vehicleType`, `tripType`, `oneWay`, `roundTrip`
  - `passengers`, `luggage`, `pickupAddress`, `dropoffAddress`
  - `seatNumbers`, `variant`, `perPerson`
  - `return`, `clearCartWarning`

### 5. **API Integration**

#### **Cart Operations**

- ✅ **Add to Cart**: Works for all product types
- ✅ **Update**: Quantity/participants/options/booking_data via PATCH
- ✅ **Remove Item**: Removes items from cart
- ✅ **Clear Cart**: Clears entire cart

#### **Data Flow**

- ✅ **Backend → Frontend**: Cart data flows from backend API
- ✅ **Frontend → Backend**: Updates sent to backend API
- ✅ **Consistent State**: Frontend always reflects backend state

### 6. **Error Handling**

- ✅ **Authentication**: Redirects to login if not authenticated
- ✅ **API Errors**: Displays user-friendly error messages
- ✅ **Loading States**: Shows loading indicators during operations
- ✅ **Validation**: Prevents invalid operations (negative quantities, etc.)

### 7. **UI/UX Improvements**

- ✅ **Consistent Design**: All components follow same design patterns
- ✅ **Responsive Layout**: Works on mobile and desktop
- ✅ **Accessibility**: Proper ARIA labels and keyboard navigation
- ✅ **Visual Feedback**: Loading states and success/error messages

## File Structure

```
frontend/
├── types/
│   └── cart.ts                    # TypeScript interfaces
├── components/cart/
│   ├── TourCartItem.tsx          # Tour cart item component
│   ├── EventCartItem.tsx         # Event cart item component
│   └── TransferCartItem.tsx      # Transfer cart item component
├── app/[locale]/cart/
│   └── page.tsx                  # Main cart page (refactored)
└── i18n/
    ├── en.json                   # English translations
    └── fa.json                   # Persian translations
```

## Benefits

### **Type Safety**

- Discriminated union ensures type safety
- TypeScript catches errors at compile time
- Proper autocomplete and IntelliSense

### **Maintainability**

- Modular component architecture
- Clear separation of concerns
- Easy to add new product types

### **User Experience**

- Product-specific information display
- Consistent interaction patterns
- Clear pricing breakdown

### **Developer Experience**

- Type-safe development
- Reusable components
- Clear API contracts

## Future Enhancements

- Add support for more product types
- Implement real-time cart updates
- Add cart item comparison features
- Implement cart sharing functionality
- Add bulk operations (select multiple items)

## Testing

- All components are ready for unit testing
- API integration points are clearly defined
- Error scenarios are handled
- Loading states are implemented

The refactored cart system provides a robust, type-safe, and user-friendly experience for managing multiple product types in a single cart interface.
