# API Documentation - Peykan Tourism

## 🌐 Base URL

```
Development: http://localhost:8000/api/v1
Production:  https://peykantravelistanbul.com/api/v1
```

## 🔐 Authentication

### **JWT Authentication**
All API endpoints require authentication unless specified as public.

```bash
# Include in request headers
Authorization: Bearer <access_token>
```

### **Token Types**
- **Access Token**: Short-lived (30 minutes) for API access
- **Refresh Token**: Long-lived (24 hours) for token renewal

### **Token Refresh**
```bash
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

## 📋 Common Response Format

### **Success Response**
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

### **Error Response**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  }
}
```

### **Paginated Response**
```json
{
  "success": true,
  "data": {
    "results": [],
    "count": 100,
    "next": "http://api.example.com/endpoint?page=2",
    "previous": null,
    "page": 1,
    "pages": 10
  }
}
```

---

## 👤 Authentication Endpoints

### **User Registration**
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+1234567890",
      "language": "en",
      "is_verified": false
    },
    "tokens": {
      "access": "access_token",
      "refresh": "refresh_token"
    }
  }
}
```

### **User Login**
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "customer"
    },
    "tokens": {
      "access": "access_token",
      "refresh": "refresh_token"
    }
  }
}
```

### **Email Verification**
```http
POST /api/v1/auth/verify-email/
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456"
}
```

### **Password Reset**
```http
POST /api/v1/auth/forgot-password/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

```http
POST /api/v1/auth/reset-password/
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "new_secure_password"
}
```

### **Logout**
```http
POST /api/v1/auth/logout/
Authorization: Bearer <access_token>
```

---

## 🏛️ Tours Endpoints

### **List Tours**
```http
GET /api/v1/tours/
```

**Query Parameters:**
- `category`: Tour category filter
- `location`: Location filter
- `price_min`: Minimum price
- `price_max`: Maximum price
- `duration_min`: Minimum duration (hours)
- `duration_max`: Maximum duration (hours)
- `date`: Available date (YYYY-MM-DD)
- `participants`: Number of participants
- `language`: Language filter
- `page`: Page number
- `page_size`: Items per page

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "uuid",
        "slug": "istanbul-city-tour",
        "title": "Istanbul City Tour",
        "description": "Explore the beautiful city of Istanbul",
        "category": "city_tour",
        "location": "Istanbul",
        "duration": 8,
        "max_participants": 20,
        "base_price": 50.00,
        "currency": "USD",
        "images": [
          {
            "id": "uuid",
            "url": "https://example.com/image1.jpg",
            "alt": "Istanbul City Tour"
          }
        ],
        "rating": 4.5,
        "review_count": 125,
        "is_available": true
      }
    ],
    "count": 50,
    "next": "http://api.example.com/tours/?page=2",
    "previous": null
  }
}
```

### **Get Tour Details**
```http
GET /api/v1/tours/{slug}/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "slug": "istanbul-city-tour",
    "title": "Istanbul City Tour",
    "description": "Explore the beautiful city of Istanbul",
    "category": "city_tour",
    "location": "Istanbul",
    "duration": 8,
    "max_participants": 20,
    "base_price": 50.00,
    "currency": "USD",
    "images": [],
    "variants": [
      {
        "id": "uuid",
        "name": "Standard Package",
        "description": "Basic tour package",
        "price": 50.00,
        "features": ["Guide", "Transportation", "Lunch"]
      },
      {
        "id": "uuid",
        "name": "Premium Package",
        "description": "Premium tour package",
        "price": 80.00,
        "features": ["Guide", "Transportation", "Lunch", "Hotel Pickup"]
      }
    ],
    "options": [
      {
        "id": "uuid",
        "name": "Audio Guide",
        "description": "Multilingual audio guide",
        "price": 10.00
      }
    ],
    "availability": [
      {
        "date": "2024-02-15",
        "available_slots": 15,
        "price": 50.00
      }
    ],
    "rating": 4.5,
    "review_count": 125,
    "reviews": [
      {
        "id": "uuid",
        "user": "John D.",
        "rating": 5,
        "comment": "Excellent tour!",
        "date": "2024-01-15"
      }
    ]
  }
}
```

### **Calculate Tour Price**
```http
POST /api/v1/tours/{slug}/calculate-price/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "variant_id": "uuid",
  "date": "2024-02-15",
  "participants": 2,
  "options": ["uuid1", "uuid2"],
  "currency": "EUR"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "base_price": 50.00,
    "variant_price": 80.00,
    "options_price": 20.00,
    "total_price": 100.00,
    "currency": "EUR",
    "breakdown": {
      "base": 50.00,
      "variant": 30.00,
      "options": 20.00
    }
  }
}
```

---

## 🎫 Events Endpoints

### **List Events**
```http
GET /api/v1/events/
```

**Query Parameters:**
- `category`: Event category
- `location`: Location filter
- `date_from`: Start date
- `date_to`: End date
- `price_min`: Minimum price
- `price_max`: Maximum price
- `capacity_min`: Minimum capacity
- `capacity_max`: Maximum capacity

### **Get Event Details**
```http
GET /api/v1/events/{slug}/
```

### **Calculate Event Price**
```http
POST /api/v1/events/{slug}/calculate-price/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "date": "2024-02-15",
  "participants": 2,
  "options": ["uuid1", "uuid2"],
  "currency": "EUR"
}
```

---

## 🚗 Transfers Endpoints

### **List Transfers**
```http
GET /api/v1/transfers/
```

**Query Parameters:**
- `from_location`: Departure location
- `to_location`: Destination location
- `date`: Transfer date
- `passengers`: Number of passengers
- `vehicle_type`: Vehicle type filter

### **Get Transfer Details**
```http
GET /api/v1/transfers/{slug}/
```

### **Calculate Transfer Price**
```http
POST /api/v1/transfers/{slug}/calculate-price/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "from_location": "Istanbul Airport",
  "to_location": "Istanbul City Center",
  "date": "2024-02-15",
  "time": "14:30",
  "passengers": 2,
  "currency": "EUR"
}
```

---

## 🛒 Cart Endpoints

### **Get Cart**
```http
GET /api/v1/cart/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "items": [
      {
        "id": "uuid",
        "product_type": "tour",
        "product_id": "uuid",
        "product_name": "Istanbul City Tour",
        "variant_id": "uuid",
        "variant_name": "Standard Package",
        "date": "2024-02-15",
        "participants": 2,
        "options": [
          {
            "id": "uuid",
            "name": "Audio Guide",
            "price": 10.00
          }
        ],
        "unit_price": 50.00,
        "total_price": 100.00,
        "currency": "USD"
      }
    ],
    "subtotal": 100.00,
    "tax": 10.00,
    "total": 110.00,
    "currency": "USD",
    "item_count": 1
  }
}
```

### **Add Item to Cart**
```http
POST /api/v1/cart/add/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product_type": "tour",
  "product_id": "uuid",
  "variant_id": "uuid",
  "date": "2024-02-15",
  "participants": 2,
  "options": ["uuid1", "uuid2"]
}
```

### **Update Cart Item**
```http
PUT /api/v1/cart/items/{item_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "participants": 3,
  "options": ["uuid1"]
}
```

### **Remove Cart Item**
```http
DELETE /api/v1/cart/items/{item_id}/
Authorization: Bearer <access_token>
```

### **Clear Cart**
```http
DELETE /api/v1/cart/clear/
Authorization: Bearer <access_token>
```

---

## 📦 Orders Endpoints

### **Create Order**
```http
POST /api/v1/orders/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "cart_id": "uuid",
  "customer_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "billing_address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US"
  },
  "special_requests": "Please provide vegetarian meals",
  "payment_method": "credit_card"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "order": {
      "id": "uuid",
      "order_number": "PT-2024-001",
      "status": "pending",
      "total": 110.00,
      "currency": "USD",
      "created_at": "2024-01-15T10:30:00Z"
    },
    "payment_url": "https://payment.example.com/pay/order_id"
  }
}
```

### **Get Orders**
```http
GET /api/v1/orders/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Order status filter
- `date_from`: Start date
- `date_to`: End date
- `page`: Page number

### **Get Order Details**
```http
GET /api/v1/orders/{order_number}/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "order_number": "PT-2024-001",
    "status": "confirmed",
    "customer": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    },
    "billing_address": {
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "US"
    },
    "items": [
      {
        "id": "uuid",
        "product_type": "tour",
        "product_name": "Istanbul City Tour",
        "variant_name": "Standard Package",
        "date": "2024-02-15",
        "participants": 2,
        "unit_price": 50.00,
        "total_price": 100.00
      }
    ],
    "subtotal": 100.00,
    "tax": 10.00,
    "total": 110.00,
    "currency": "USD",
    "payment_status": "paid",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

### **Cancel Order**
```http
POST /api/v1/orders/{order_number}/cancel/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "reason": "Change of plans"
}
```

---

## 💳 Payment Endpoints

### **Process Payment**
```http
POST /api/v1/payments/process/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "order_id": "uuid",
  "payment_method": "credit_card",
  "payment_data": {
    "card_number": "4242424242424242",
    "expiry_month": "12",
    "expiry_year": "2025",
    "cvv": "123"
  }
}
```

### **Get Payment Status**
```http
GET /api/v1/payments/{payment_id}/
Authorization: Bearer <access_token>
```

### **Refund Payment**
```http
POST /api/v1/payments/{payment_id}/refund/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 50.00,
  "reason": "Customer request"
}
```

---

## 👤 User Profile Endpoints

### **Get Profile**
```http
GET /api/v1/users/profile/
Authorization: Bearer <access_token>
```

### **Update Profile**
```http
PUT /api/v1/users/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "language": "en",
  "currency": "USD"
}
```

### **Change Password**
```http
POST /api/v1/users/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "old_password",
  "new_password": "new_secure_password"
}
```

### **Upload Avatar**
```http
POST /api/v1/users/avatar/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "avatar": "file"
}
```

---

## 🌍 Localization Endpoints

### **Get Languages**
```http
GET /api/v1/languages/
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "code": "en",
      "name": "English",
      "native_name": "English",
      "is_default": true
    },
    {
      "code": "fa",
      "name": "Persian",
      "native_name": "فارسی",
      "is_default": false
    },
    {
      "code": "tr",
      "name": "Turkish",
      "native_name": "Türkçe",
      "is_default": false
    }
  ]
}
```

### **Get Currencies**
```http
GET /api/v1/currencies/
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "code": "USD",
      "name": "US Dollar",
      "symbol": "$",
      "is_default": true
    },
    {
      "code": "EUR",
      "name": "Euro",
      "symbol": "€",
      "is_default": false
    },
    {
      "code": "TRY",
      "name": "Turkish Lira",
      "symbol": "₺",
      "is_default": false
    }
  ]
}
```

### **Get Currency Rates**
```http
GET /api/v1/currencies/rates/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "base": "USD",
    "rates": {
      "EUR": 0.85,
      "TRY": 8.50,
      "IRR": 420000
    },
    "updated_at": "2024-01-15T10:00:00Z"
  }
}
```

---

## 🔍 Search Endpoints

### **Global Search**
```http
GET /api/v1/search/
```

**Query Parameters:**
- `q`: Search query
- `type`: Product type (tour, event, transfer)
- `location`: Location filter
- `date`: Date filter
- `price_min`: Minimum price
- `price_max`: Maximum price

**Response:**
```json
{
  "success": true,
  "data": {
    "tours": [
      {
        "id": "uuid",
        "slug": "istanbul-city-tour",
        "title": "Istanbul City Tour",
        "price": 50.00,
        "currency": "USD",
        "type": "tour"
      }
    ],
    "events": [],
    "transfers": [],
    "total_results": 1
  }
}
```

---

## 📊 Analytics Endpoints

### **Get Analytics** (Admin Only)
```http
GET /api/v1/analytics/
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `period`: Time period (day, week, month, year)
- `date_from`: Start date
- `date_to`: End date
- `metric`: Metric type (revenue, bookings, users)

---

## 🚨 Error Codes

### **Common Error Codes**
- `AUTHENTICATION_FAILED`: Invalid or expired token
- `PERMISSION_DENIED`: Insufficient permissions
- `VALIDATION_ERROR`: Invalid request data
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVER_ERROR`: Internal server error

### **Business Error Codes**
- `PRODUCT_NOT_AVAILABLE`: Product not available for selected date
- `INSUFFICIENT_CAPACITY`: Not enough capacity for booking
- `PAYMENT_FAILED`: Payment processing failed
- `ORDER_CANCELLED`: Order has been cancelled
- `INVALID_CURRENCY`: Unsupported currency

---

## 📝 Rate Limiting

### **Rate Limits**
- **Public endpoints**: 100 requests per minute
- **Authenticated endpoints**: 1000 requests per minute
- **Admin endpoints**: 5000 requests per minute

### **Rate Limit Headers**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642234567
```

---

## 🔧 Webhooks

### **Webhook Events**
- `order.created`: New order created
- `order.updated`: Order status updated
- `order.cancelled`: Order cancelled
- `payment.processed`: Payment completed
- `payment.failed`: Payment failed
- `user.registered`: New user registered

### **Webhook Format**
```json
{
  "event": "order.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "order_id": "uuid",
    "order_number": "PT-2024-001",
    "status": "pending"
  }
}
```

---

## 📞 Support

### **API Support**
- **Documentation**: [API Documentation](./API_DOCUMENTATION.md)
- **GitHub Issues**: [API Issues](https://github.com/PeykanTravel/peykan-tourism/issues)
- **Email**: api-support@peykantravelistanbul.com

### **SDK & Libraries**
- **JavaScript/TypeScript**: [npm package](https://npmjs.com/package/peykan-tourism-sdk)
- **Python**: [PyPI package](https://pypi.org/project/peykan-tourism/)
- **Postman Collection**: [Download](https://api.peykantravelistanbul.com/postman)

---

**نکته**: این مستندات به‌روزرسانی می‌شود. برای آخرین تغییرات، لطفاً [GitHub](https://github.com/PeykanTravel/peykan-tourism) را بررسی کنید. 