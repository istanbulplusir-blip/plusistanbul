# Transfer Booking API Examples

This document provides complete API examples for the transfer booking flow in the Peykan Tourism Platform.

## 🚀 Complete Transfer Booking Flow

### 1. Get Available Routes

**Endpoint:** `GET /api/transfers/routes/`

**Response:**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Airport to City Center",
      "description": "Convenient transfer from Istanbul Airport to city center",
      "origin": "Istanbul Airport (IST)",
      "destination": "Taksim Square",
      "peak_hour_surcharge": 25.00,
      "midnight_surcharge": 50.00,
      "round_trip_discount_enabled": true,
      "round_trip_discount_percentage": 15.00,
      "is_active": true,
      "pricing": [
        {
          "id": "660e8400-e29b-41d4-a716-446655440001",
          "vehicle_type": "sedan",
          "vehicle_type_display": "Sedan",
          "base_price": 45.00,
          "max_passengers": 4,
          "max_luggage": 3,
          "is_active": true
        },
        {
          "id": "660e8400-e29b-41d4-a716-446655440002",
          "vehicle_type": "van",
          "vehicle_type_display": "Van",
          "base_price": 65.00,
          "max_passengers": 8,
          "max_luggage": 6,
          "is_active": true
        }
      ],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 2. Get Popular Routes

**Endpoint:** `GET /api/transfers/routes/popular/`

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Airport to City Center",
    "origin": "Istanbul Airport (IST)",
    "destination": "Taksim Square",
    "popular_vehicle_type": "sedan",
    "base_price": 45.00,
    "card_image": "",
    "route_image": ""
  }
]
```

### 3. Get Route Details

**Endpoint:** `GET /api/transfers/routes/{id}/`

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Airport to City Center",
  "description": "Convenient transfer from Istanbul Airport to city center",
  "origin": "Istanbul Airport (IST)",
  "destination": "Taksim Square",
  "peak_hour_surcharge": 25.00,
  "midnight_surcharge": 50.00,
  "round_trip_discount_enabled": true,
  "round_trip_discount_percentage": 15.00,
  "is_active": true,
  "pricing": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "vehicle_type": "sedan",
      "vehicle_type_display": "Sedan",
      "base_price": 45.00,
      "max_passengers": 4,
      "max_luggage": 3,
      "is_active": true
    }
  ],
  "options": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440003",
      "name": "Child Seat",
      "description": "Safety child seat for children under 4 years",
      "option_type": "equipment",
      "option_type_display": "Equipment",
      "price_type": "fixed",
      "price_type_display": "Fixed Price",
      "price": 10.00,
      "price_percentage": 0.00,
      "max_quantity": 2,
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 4. Calculate Transfer Price

**Endpoint:** `POST /api/transfers/routes/{id}/calculate_price/`

**Request:**
```json
{
  "vehicle_type": "sedan",
  "booking_time": "08:30:00",
  "return_time": "18:00:00",
  "selected_options": [
    {
      "option_id": "770e8400-e29b-41d4-a716-446655440003",
      "quantity": 1
    }
  ]
}
```

**Response:**
```json
{
  "price_breakdown": {
    "base_price": 45.00,
    "outbound_price": 56.25,
    "outbound_surcharge": 11.25,
    "return_price": 45.00,
    "return_surcharge": 0.00,
    "options_total": 10.00,
    "round_trip_discount": 15.19,
    "final_price": 96.06
  },
  "trip_info": {
    "vehicle_type": "sedan",
    "is_round_trip": true,
    "booking_time": "08:30",
    "return_time": "18:00"
  },
  "route_info": {
    "origin": "Istanbul Airport (IST)",
    "destination": "Taksim Square",
    "name": "Airport to City Center"
  },
  "time_info": {
    "booking_hour": 8,
    "time_category": "peak",
    "surcharge_percentage": 25.0
  }
}
```

### 5. Add Transfer to Cart

**Endpoint:** `POST /api/cart/add/`

**Request:**
```json
{
  "product_type": "transfer",
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "booking_date": "2024-02-15",
  "booking_time": "08:30:00",
  "quantity": 1,
  "booking_data": {
    "vehicle_type": "sedan",
    "trip_type": "round_trip",
    "outbound_time": "08:30:00",
    "return_time": "18:00:00",
    "outbound_date": "2024-02-15",
    "return_date": "2024-02-15",
    "passenger_count": 2,
    "luggage_count": 3,
    "pickup_address": "Terminal 1, Istanbul Airport",
    "pickup_instructions": "Wait at arrival gate",
    "dropoff_address": "Taksim Square, Istanbul",
    "dropoff_instructions": "Drop off at main entrance",
    "contact_name": "John Doe",
    "contact_phone": "+90 555 123 4567"
  },
  "selected_options": [
    {
      "option_id": "770e8400-e29b-41d4-a716-446655440003",
      "quantity": 1,
      "price": 10.00
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transfer added to cart successfully",
  "cart_item": {
    "id": "880e8400-e29b-41d4-a716-446655440004",
    "product_type": "transfer",
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "booking_date": "2024-02-15",
    "booking_time": "08:30:00",
    "quantity": 1,
    "unit_price": 45.00,
    "total_price": 96.06,
    "currency": "USD",
    "selected_options": [
      {
        "option_id": "770e8400-e29b-41d4-a716-446655440003",
        "quantity": 1,
        "price": 10.00
      }
    ],
    "options_total": 10.00,
    "booking_data": {
      "vehicle_type": "sedan",
      "trip_type": "round_trip",
      "outbound_time": "08:30:00",
      "return_time": "18:00:00",
      "outbound_date": "2024-02-15",
      "return_date": "2024-02-15",
      "passenger_count": 2,
      "luggage_count": 3,
      "pickup_address": "Terminal 1, Istanbul Airport",
      "pickup_instructions": "Wait at arrival gate",
      "dropoff_address": "Taksim Square, Istanbul",
      "dropoff_instructions": "Drop off at main entrance",
      "contact_name": "John Doe",
      "contact_phone": "+90 555 123 4567"
    }
  }
}
```

### 6. Get Cart Summary

**Endpoint:** `GET /api/cart/`

**Response:**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440005",
  "session_id": "abc123def456",
  "user": 1,
  "currency": "USD",
  "is_active": true,
  "expires_at": "2024-02-16T10:30:00Z",
  "total_items": 1,
  "subtotal": 96.06,
  "total": 96.06,
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "product_type": "transfer",
      "product_id": "550e8400-e29b-41d4-a716-446655440000",
      "booking_date": "2024-02-15",
      "booking_time": "08:30:00",
      "variant_id": null,
      "variant_name": "Sedan",
      "quantity": 1,
      "unit_price": 45.00,
      "total_price": 96.06,
      "currency": "USD",
      "selected_options": [
        {
          "option_id": "770e8400-e29b-41d4-a716-446655440003",
          "quantity": 1,
          "price": 10.00
        }
      ],
      "options_total": 10.00,
      "booking_data": {
        "vehicle_type": "sedan",
        "trip_type": "round_trip",
        "outbound_time": "08:30:00",
        "return_time": "18:00:00",
        "outbound_date": "2024-02-15",
        "return_date": "2024-02-15",
        "passenger_count": 2,
        "luggage_count": 3,
        "pickup_address": "Terminal 1, Istanbul Airport",
        "pickup_instructions": "Wait at arrival gate",
        "dropoff_address": "Taksim Square, Istanbul",
        "dropoff_instructions": "Drop off at main entrance",
        "contact_name": "John Doe",
        "contact_phone": "+90 555 123 4567"
      },
      "is_reserved": false,
      "reservation_expires_at": null,
      "created_at": "2024-02-15T10:30:00Z"
    }
  ],
  "created_at": "2024-02-15T10:30:00Z"
}
```

### 7. Create Order from Cart

**Endpoint:** `POST /api/orders/create/`

**Request:**
```json
{
  "payment_method": "credit_card",
  "billing_address": "123 Main St, Istanbul, Turkey",
  "customer_notes": "Please call upon arrival"
}
```

**Response:**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440006",
  "order_number": "ORD2024001",
  "status": "pending",
  "payment_status": "pending",
  "payment_method": "credit_card",
  "subtotal": 96.06,
  "tax_amount": 0.00,
  "discount_amount": 0.00,
  "total_amount": 96.06,
  "currency": "USD",
  "customer_name": "John Doe",
  "customer_email": "john.doe@example.com",
  "customer_phone": "+90 555 123 4567",
  "billing_address": "123 Main St, Istanbul, Turkey",
  "customer_notes": "Please call upon arrival",
  "created_at": "2024-02-15T10:30:00Z",
  "items": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440007",
      "product_type": "transfer",
      "product_id": "550e8400-e29b-41d4-a716-446655440000",
      "product_title": "Airport to City Center",
      "product_slug": "airport-to-city-center",
      "booking_date": "2024-02-15",
      "booking_time": "08:30:00",
      "variant_id": null,
      "variant_name": "Sedan",
      "quantity": 1,
      "unit_price": 45.00,
      "total_price": 96.06,
      "currency": "USD",
      "selected_options": [
        {
          "option_id": "770e8400-e29b-41d4-a716-446655440003",
          "quantity": 1,
          "price": 10.00
        }
      ],
      "options_total": 10.00,
      "booking_data": {
        "vehicle_type": "sedan",
        "trip_type": "round_trip",
        "outbound_time": "08:30:00",
        "return_time": "18:00:00",
        "outbound_date": "2024-02-15",
        "return_date": "2024-02-15",
        "passenger_count": 2,
        "luggage_count": 3,
        "pickup_address": "Terminal 1, Istanbul Airport",
        "pickup_instructions": "Wait at arrival gate",
        "dropoff_address": "Taksim Square, Istanbul",
        "dropoff_instructions": "Drop off at main entrance",
        "contact_name": "John Doe",
        "contact_phone": "+90 555 123 4567"
      },
      "status": "pending",
      "created_at": "2024-02-15T10:30:00Z"
    }
  ]
}
```

## 🔧 Business Rules & Validations

### Transfer-Specific Rules:

1. **Unique Booking**: Only one transfer can be booked per cart (quantity is always 1)
2. **Time Validations**: 
   - Booking time must be in the future
   - Return time must be after outbound time for round trips
3. **Capacity Validations**:
   - Passenger count cannot exceed vehicle max_passengers
   - Luggage count cannot exceed vehicle max_luggage
4. **Pricing Rules**:
   - Peak hours (7-9 AM, 5-7 PM): +25% surcharge
   - Midnight hours (10 PM - 6 AM): +50% surcharge
   - Round trip discount: 15% off total base price
5. **Options**: Each option has max_quantity limit

### Error Responses:

**400 Bad Request:**
```json
{
  "error": "validation_error",
  "message": "Passenger count exceeds maximum capacity for this vehicle type.",
  "details": {
    "field": "passenger_count",
    "max_allowed": 4,
    "provided": 6
  }
}
```

**404 Not Found:**
```json
{
  "error": "not_found",
  "message": "Transfer route not found"
}
```

**409 Conflict:**
```json
{
  "error": "conflict",
  "message": "A transfer is already in your cart. Please remove it first."
}
```

## 🧪 Testing Scenarios

### 1. Basic One-Way Transfer
- Route: Airport to City
- Vehicle: Sedan
- Time: 14:00 (normal hours)
- Expected: Base price only

### 2. Round Trip with Peak Hour
- Route: Airport to City
- Vehicle: Van
- Outbound: 08:00 (peak)
- Return: 18:00 (peak)
- Expected: Base price + surcharges - round trip discount

### 3. Transfer with Options
- Route: Airport to City
- Vehicle: Sedan
- Options: Child seat (1x), Meet & Greet (1x)
- Expected: Base price + options total

### 4. Midnight Transfer
- Route: Airport to City
- Vehicle: SUV
- Time: 23:30 (midnight)
- Expected: Base price + 50% surcharge

### 5. Capacity Validation
- Route: Airport to City
- Vehicle: Sedan (max 4 passengers)
- Passengers: 6
- Expected: 400 validation error

## 📱 Frontend Integration

### JavaScript Example:

```javascript
// Calculate transfer price
const calculatePrice = async (routeId, bookingData) => {
  const response = await fetch(`/api/transfers/routes/${routeId}/calculate_price/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify(bookingData)
  });
  
  return response.json();
};

// Add to cart
const addToCart = async (transferData) => {
  const response = await fetch('/api/cart/add/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify(transferData)
  });
  
  return response.json();
};
```

## 🔐 Authentication

All endpoints require JWT authentication except:
- `GET /api/transfers/routes/` (public)
- `GET /api/transfers/routes/popular/` (public)
- `GET /api/transfers/routes/{id}/` (public)
- `POST /api/transfers/routes/{id}/calculate_price/` (public)

Include in headers:
```
Authorization: Bearer <access_token>
``` 