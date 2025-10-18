# Peykan Tourism Agent System - Comprehensive Documentation

**Date**: December 2024  
**Version**: 1.0  
**Scope**: Complete Agent-User System Analysis and Documentation

## Table of Contents

1. [What is an Agent?](#1-what-is-an-agent)
2. [Agent Profile vs User Profile](#2-agent-profile-vs-user-profile)
3. [How Agents Create Users](#3-how-agents-create-users)
4. [Features of Agent-Created Users](#4-features-of-agent-created-users)
5. [Agent Capabilities & Operations](#5-agent-capabilities--operations)
6. [Interactions with System Features](#6-interactions-with-system-features)
7. [Implementation Details](#7-implementation-details)

---

## 1. What is an Agent?

### Overview

An **Agent** in the Peykan Tourism system is a specialized user role that acts as an intermediary between the platform and end customers. Agents are typically travel agencies, tour operators, or individual travel professionals who can create and manage customers on behalf of the platform.

### Key Characteristics

#### **Role Definition**

- **Role**: `agent` (one of four roles: guest, customer, agent, admin)
- **Primary Function**: Create and manage customers, place orders on their behalf
- **Business Model**: Earn commissions from successful bookings
- **Access Level**: Elevated permissions to manage multiple customers

#### **Agent vs Other Roles**

| Feature                       | Agent  | Customer | Admin  |
| ----------------------------- | ------ | -------- | ------ |
| **Create Users**              | ✅ Yes | ❌ No    | ✅ Yes |
| **Manage Multiple Customers** | ✅ Yes | ❌ No    | ✅ Yes |
| **Earn Commissions**          | ✅ Yes | ❌ No    | ❌ No  |
| **Access Agent Dashboard**    | ✅ Yes | ❌ No    | ✅ Yes |
| **Place Orders for Others**   | ✅ Yes | ❌ No    | ✅ Yes |
| **View Customer Analytics**   | ✅ Yes | ❌ No    | ✅ Yes |

#### **Key Use Cases**

1. **Customer Creation & Management**

   - Create new customer accounts
   - Link existing customers to their agency
   - Manage customer information and preferences

2. **Order Placement**

   - Book tours, transfers, car rentals, events for customers
   - Access special agent pricing (typically 15% discount)
   - Handle payment processing on behalf of customers

3. **Customer Analytics**

   - Track customer spending patterns
   - Monitor booking history
   - Generate commission reports

4. **Commission Management**
   - Earn commissions on successful bookings
   - Track commission status (pending, approved, paid)
   - View detailed commission history

---

## 2. Agent Profile vs User Profile

### User Model (Base)

The `User` model serves as the foundation for all user types, including agents:

```python
class User(AbstractUser, BaseModel):
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')

    # Agent-specific fields in User model
    agent_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Properties
    @property
    def is_agent(self):
        return self.role == 'agent'
```

### AgentProfile Model (Extended)

The `AgentProfile` model extends the User model with business-specific information:

```python
class AgentProfile(BaseModel):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='agent_profile')

    # Business Information
    company_name = models.CharField(max_length=255, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    business_address = models.TextField(blank=True)
    business_phone = models.CharField(max_length=20, blank=True)
    business_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Commission Settings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    min_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Performance Metrics
    total_orders = models.PositiveIntegerField(default=0)
    total_commission_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_commission_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    average_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Payment Settings
    payment_method = models.CharField(max_length=50, blank=True)
    payment_account = models.CharField(max_length=255, blank=True)
    payment_frequency = models.CharField(max_length=20, choices=[...], default='monthly')

    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
```

### UserProfile Model (General)

The `UserProfile` model provides general profile information for all users:

```python
class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Personal Information
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)

    # Address Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Social Media
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    # Preferences
    preferred_language = models.CharField(max_length=10, default='fa')
    timezone = models.CharField(max_length=50, default='Asia/Tehran')
    newsletter_subscription = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=True)
```

### Relationship Summary

| Model            | Purpose                         | Fields Unique to Agents         |
| ---------------- | ------------------------------- | ------------------------------- |
| **User**         | Base authentication & core data | `agent_code`, `commission_rate` |
| **UserProfile**  | General profile info            | None (shared by all users)      |
| **AgentProfile** | Business & commission data      | All fields are agent-specific   |

---

## 3. How Agents Create Users

### API Endpoints

#### **Create Customer**

```http
POST /api/agents/customers/
Authorization: Bearer <agent_jwt_token>
Content-Type: application/json

{
    "email": "customer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "birth_date": "1990-01-01",
    "gender": "male",
    "preferred_language": "en",
    "preferred_contact_method": "email",
    "customer_status": "active",
    "customer_tier": "bronze",
    "relationship_notes": "VIP customer",
    "special_requirements": "Wheelchair accessible",
    "marketing_consent": true
}
```

#### **Response**

```json
{
  "success": true,
  "customer_id": "uuid-here",
  "agent_customer_id": "uuid-here",
  "customer": {
    "id": "uuid-here",
    "name": "John Doe",
    "email": "customer@example.com",
    "phone": "+1234567890",
    "status": "active",
    "tier": "bronze"
  },
  "message": "مشتری با موفقیت ایجاد شد"
}
```

### Service Implementation

#### **AgentCustomerService.create_customer_for_agent()**

```python
@staticmethod
def create_customer_for_agent(agent, customer_data):
    """Create a customer for an agent"""

    if not agent.is_agent:
        raise ValidationError("User is not an agent")

    with transaction.atomic():
        # Check if customer already exists
        existing_customer = User.objects.filter(
            email=customer_data['email']
        ).first()

        if existing_customer:
            # Check if already linked to this agent
            agent_customer = AgentCustomer.objects.filter(
                agent=agent,
                customer=existing_customer
            ).first()

            if agent_customer:
                raise ValidationError("Customer already exists for this agent")

            # Create new relationship with existing customer
            agent_customer = AgentCustomer.objects.create(
                agent=agent,
                customer=existing_customer,
                customer_name=customer_data.get('name', f"{existing_customer.first_name} {existing_customer.last_name}".strip()),
                customer_email=existing_customer.email,
                customer_phone=customer_data.get('phone', existing_customer.phone_number or ''),
                # ... other fields
                created_by_agent=False  # Customer existed before
            )

            return existing_customer, agent_customer

        else:
            # Create new customer
            customer = User.objects.create_user(
                username=customer_data['email'],
                email=customer_data['email'],
                password=customer_data.get('password', User.objects.make_random_password()),
                first_name=customer_data.get('first_name', ''),
                last_name=customer_data.get('last_name', ''),
                phone_number=customer_data.get('phone', ''),
                role='customer',
            )

            # Create agent-customer relationship
            agent_customer = AgentCustomer.objects.create(
                agent=agent,
                customer=customer,
                customer_name=customer_data.get('name', f"{customer.first_name} {customer.last_name}".strip()),
                customer_email=customer.email,
                customer_phone=customer_data.get('phone', customer.phone_number or ''),
                # ... other fields
                created_by_agent=True
            )

            return customer, agent_customer
```

### Automatic Profile Creation

When a new user is created (either by agent or directly), the system automatically:

1. **Creates UserProfile**: A `UserProfile` record is automatically created
2. **Sets Default Values**:
   - `preferred_language`: 'fa' (Persian)
   - `timezone`: 'Asia/Tehran'
   - `newsletter_subscription`: True
   - `marketing_emails`: True

### Role Assignment

- **Agent-created users**: Always assigned `role='customer'`
- **Existing users**: Keep their existing role when linked to an agent
- **Automatic activation**: Agent-created users are automatically activated

### Ownership Tracking

The `AgentCustomer` model tracks ownership through:

```python
class AgentCustomer(BaseModel):
    agent = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='agent_customers')
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='created_by_agent')
    created_by_agent = models.BooleanField(default=True)  # Key field for tracking
```

- **`created_by_agent=True`**: Customer was created by the agent
- **`created_by_agent=False`**: Customer existed before being linked to agent

---

## 4. Features of Agent-Created Users

### User Capabilities

Agent-created users have the same capabilities as regular customers:

#### **Standard Customer Features**

- ✅ **Account Management**: Update profile, change password
- ✅ **Order History**: View their own orders
- ✅ **Cart Management**: Add/remove items from cart
- ✅ **Checkout Process**: Complete purchases
- ✅ **Payment Processing**: Handle payments
- ✅ **Communication**: Receive notifications and emails

#### **Agent-Specific Features**

- ✅ **Agent Visibility**: Their orders are visible to the creating agent
- ✅ **Commission Tracking**: Orders generate commissions for the agent
- ✅ **Agent Management**: Agent can update their information
- ✅ **Special Pricing**: May receive agent-discounted pricing

### Access Permissions

#### **Customer Self-Access**

```python
# Customers can access their own data
def get_customer_orders(customer):
    return Order.objects.filter(user=customer)
```

#### **Agent Access**

```python
# Agents can access their customers' data
def get_agent_customer_orders(agent, customer):
    return Order.objects.filter(
        user=customer,
        agent=agent
    )
```

### Cart and Checkout Flow

#### **Standard Flow**

1. **Add to Cart**: Customer adds items to cart
2. **Review Cart**: Customer reviews items and pricing
3. **Checkout**: Customer proceeds to checkout
4. **Payment**: Customer completes payment
5. **Order Creation**: Order is created with agent reference

#### **Agent-Assisted Flow**

1. **Agent Adds Items**: Agent adds items to customer's cart
2. **Agent Reviews**: Agent reviews cart and pricing
3. **Agent Checkout**: Agent initiates checkout process
4. **Payment Handling**: Agent or customer handles payment
5. **Order Creation**: Order is created with agent reference

### Order Attribution

All orders placed by agent-created users include:

```python
class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Customer
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Agent
    agent_commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
```

### Guest User Handling

#### **Temporary Users**

- Agents can create temporary users for immediate bookings
- These users can be upgraded to full accounts later
- Guest users have limited functionality until registration

#### **Guest-to-Registered Upgrade**

```python
def upgrade_guest_to_registered(guest_user, registration_data):
    """Upgrade guest user to registered customer"""
    guest_user.email = registration_data['email']
    guest_user.username = registration_data['username']
    guest_user.set_password(registration_data['password'])
    guest_user.role = 'customer'
    guest_user.is_active = True
    guest_user.save()
```

---

## 5. Agent Capabilities & Operations

### Customer Management

#### **List Customers**

```http
GET /api/agents/customers/
Authorization: Bearer <agent_jwt_token>

# Query Parameters
?status=active&tier=vip&search=john&created_after=2024-01-01
```

#### **Customer Details**

```http
GET /api/agents/customers/{customer_id}/
Authorization: Bearer <agent_jwt_token>
```

#### **Update Customer Information**

```http
PUT /api/agents/customers/{customer_id}/
Authorization: Bearer <agent_jwt_token>
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "customer_status": "vip",
    "customer_tier": "gold",
    "relationship_notes": "Updated notes"
}
```

#### **Customer Search**

```http
GET /api/agents/customers/search/?q=john&limit=20
Authorization: Bearer <agent_jwt_token>
```

### Order Management

#### **Place Orders for Customers**

##### **Book Tour**

```http
POST /api/agents/book/tour/
Authorization: Bearer <agent_jwt_token>
Content-Type: application/json

{
    "customer_id": "uuid-here",
    "tour_id": "uuid-here",
    "variant_id": "uuid-here",
    "schedule_id": "uuid-here",
    "booking_date": "2024-01-15",
    "booking_time": "09:00",
    "participants": {
        "adults": 2,
        "children": 1,
        "infants": 0
    },
    "selected_options": ["guide", "meal"]
}
```

##### **Book Transfer**

```http
POST /api/agents/book/transfer/
Authorization: Bearer <agent_jwt_token>
Content-Type: application/json

{
    "customer_id": "uuid-here",
    "route_id": "uuid-here",
    "vehicle_type": "sedan",
    "booking_date": "2024-01-15",
    "booking_time": "10:00",
    "passenger_count": 4,
    "trip_type": "one_way",
    "pickup_address": "Hotel ABC",
    "dropoff_address": "Airport"
}
```

##### **Book Car Rental**

```http
POST /api/agents/book/car-rental/
Authorization: Bearer <agent_jwt_token>
Content-Type: application/json

{
    "customer_id": "uuid-here",
    "car_id": "uuid-here",
    "pickup_date": "2024-01-15",
    "pickup_time": "09:00",
    "dropoff_date": "2024-01-17",
    "dropoff_time": "09:00",
    "days": 2,
    "include_insurance": true
}
```

##### **Book Event**

```http
POST /api/agents/book/event/
Authorization: Bearer <agent_jwt_token>
Content-Type: application/json

{
    "customer_id": "uuid-here",
    "event_id": "uuid-here",
    "performance_id": "uuid-here",
    "section": "VIP",
    "ticket_type_id": "uuid-here",
    "quantity": 2
}
```

### Analytics & Reporting

#### **Customer Statistics**

```http
GET /api/agents/customers/statistics/
Authorization: Bearer <agent_jwt_token>
```

**Response:**

```json
{
  "total_customers": 150,
  "active_customers": 120,
  "vip_customers": 25,
  "tier_stats": [
    { "customer_tier": "bronze", "count": 80 },
    { "customer_tier": "silver", "count": 45 },
    { "customer_tier": "gold", "count": 20 },
    { "customer_tier": "platinum", "count": 5 }
  ],
  "status_stats": [
    { "customer_status": "active", "count": 120 },
    { "customer_status": "inactive", "count": 20 },
    { "customer_status": "vip", "count": 25 }
  ],
  "total_spent": 125000.0,
  "average_spent": 833.33,
  "top_customers": [
    {
      "customer_name": "John Doe",
      "customer_email": "john@example.com",
      "total_spent": 5000.0,
      "total_orders": 15,
      "customer_tier": "platinum"
    }
  ]
}
```

#### **Commission Summary**

```http
GET /api/agents/commissions/summary/
Authorization: Bearer <agent_jwt_token>
```

**Response:**

```json
{
  "total_commission": 12500.0,
  "total_orders": 150,
  "status_stats": {
    "pending": { "count": 10, "amount": 1250.0 },
    "approved": { "count": 120, "amount": 12000.0 },
    "paid": { "count": 100, "amount": 10000.0 }
  },
  "product_stats": {
    "tour": { "count": 80, "amount": 8000.0 },
    "transfer": { "count": 40, "amount": 2000.0 },
    "car_rental": { "count": 20, "amount": 1500.0 },
    "event": { "count": 10, "amount": 1000.0 }
  }
}
```

### Multi-Tier Customer Management

#### **Customer Tiers**

- **Bronze**: Basic customers
- **Silver**: Regular customers with some spending
- **Gold**: High-value customers
- **Platinum**: VIP customers with significant spending

#### **Customer Status**

- **Active**: Currently active customers
- **Inactive**: Customers who haven't booked recently
- **Blocked**: Customers who are blocked for various reasons
- **VIP**: Special VIP customers

#### **Tier Management**

```http
POST /api/agents/customers/{customer_id}/tier/
Authorization: Bearer <agent_jwt_token>
Content-Type: application/json

{
    "tier": "gold"
}
```

#### **Status Management**

```http
POST /api/agents/customers/{customer_id}/status/
Authorization: Bearer <agent_jwt_token>
Content-Type: application/json

{
    "status": "vip"
}
```

---

## 6. Interactions with System Features

### OTP Verification

#### **Email Verification**

- Agent-created users receive OTP codes for email verification
- Agents can trigger verification on behalf of customers
- Verification status is tracked in the User model

#### **Phone Verification**

- Phone numbers can be verified via SMS OTP
- Agents can update customer phone numbers
- Verification is required for certain operations

### JWT Authentication

#### **Token Management**

- Agents receive JWT tokens upon login
- Tokens include role information (`role: "agent"`)
- Token expiration and refresh are handled automatically

#### **Role-Based Access**

```python
# Permission check in views
if request.user.role != 'agent':
    return Response({'error': 'User is not an agent'}, status=403)
```

### Session Management

#### **Agent Sessions**

- Agents maintain separate sessions from customers
- Session data includes agent-specific information
- Sessions are invalidated on password change

#### **Customer Sessions**

- Agent-created customers have independent sessions
- Agents cannot access customer session data directly
- Session security is maintained per user

### Cart Handling

#### **Agent Cart Operations**

- Agents can create carts for customers
- Cart items include agent-specific pricing
- Cart data is linked to both customer and agent

#### **Cart Merging**

- When customers log in, their guest cart is merged
- Agent-created carts are preserved
- Cart history is maintained for both customer and agent

### Role-Based Access Enforcement

#### **Permission Classes**

```python
# Custom permission classes
class IsAgentOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_agent

class IsAgentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_agent or request.user.is_admin)
```

#### **View-Level Protection**

```python
class AgentCustomersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=403)
        # ... rest of the view
```

### Security Considerations

#### **Data Isolation**

- Agents can only access their own customers
- Customer data is isolated between agents
- Admin users have access to all data

#### **Audit Logging**

- All agent actions are logged
- Customer creation/modification is tracked
- Order placement is recorded with agent attribution

#### **Rate Limiting**

- Agent endpoints have rate limiting
- Failed attempts are logged
- Account lockout after repeated failures

---

## 7. Implementation Details

### Models Involved

#### **Core Models**

```python
# User model (base)
class User(AbstractUser, BaseModel):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    agent_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

# AgentProfile model
class AgentProfile(BaseModel):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='agent_profile')
    company_name = models.CharField(max_length=255, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    # ... other fields

# AgentCustomer model
class AgentCustomer(BaseModel):
    agent = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='agent_customers')
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='created_by_agent')
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    created_by_agent = models.BooleanField(default=True)
    # ... other fields

# AgentCommission model
class AgentCommission(BaseModel):
    agent = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='commissions')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='agent_commissions')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # ... other fields
```

### Serializers

#### **Agent Serializers**

```python
class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'agent_code', 'commission_rate', 'is_active']

class AgentCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCustomer
        fields = ['id', 'customer_name', 'customer_email', 'customer_phone',
                 'customer_status', 'customer_tier', 'total_orders', 'total_spent']
```

### Views

#### **Main Agent Views**

```python
class AgentCustomersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=403)

        customers = AgentCustomerService.get_agent_customers(request.user, filters)
        return Response({'customers': customers})

    def post(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=403)

        customer, agent_customer = AgentCustomerService.create_customer_for_agent(
            request.user, request.data
        )
        return Response({'success': True, 'customer_id': str(customer.id)})
```

### Services

#### **AgentCustomerService**

```python
class AgentCustomerService:
    @staticmethod
    def create_customer_for_agent(agent, customer_data):
        # Implementation as shown above

    @staticmethod
    def get_agent_customers(agent, filters=None):
        # Implementation for listing customers

    @staticmethod
    def update_customer_info(agent, customer_id, customer_data):
        # Implementation for updating customer info
```

#### **AgentBookingService**

```python
class AgentBookingService:
    @staticmethod
    def book_tour_for_customer(agent, customer, tour_data):
        # Implementation for booking tours

    @staticmethod
    def book_transfer_for_customer(agent, customer, transfer_data):
        # Implementation for booking transfers
```

### Permissions

#### **Custom Permission Classes**

```python
class IsAgentOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_agent

class IsAgentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_agent or request.user.is_admin)

class IsAgentCustomerOwner(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_agent:
            return False

        customer_id = view.kwargs.get('customer_id')
        return AgentCustomer.objects.filter(
            agent=request.user,
            customer_id=customer_id
        ).exists()
```

### URL Patterns

#### **Agent API Endpoints**

```python
urlpatterns = [
    # Dashboard
    path('dashboard/', views.AgentDashboardView.as_view(), name='dashboard'),
    path('dashboard/stats/', views.AgentDashboardStatsView.as_view(), name='dashboard_stats'),

    # Customer Management
    path('customers/', views.AgentCustomersView.as_view(), name='customers'),
    path('customers/statistics/', views.AgentCustomerStatisticsView.as_view(), name='customer_statistics'),
    path('customers/search/', views.AgentCustomerSearchView.as_view(), name='customer_search'),
    path('customers/<uuid:customer_id>/', views.AgentCustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<uuid:customer_id>/orders/', views.AgentCustomerOrdersView.as_view(), name='customer_orders'),

    # Booking Services
    path('book/tour/', views.AgentBookTourView.as_view(), name='book_tour'),
    # path('book/transfer/', views.AgentBookTransferView.as_view(), name='book_transfer'),  # Removed - using unified API
    path('book/car-rental/', views.AgentBookCarRentalView.as_view(), name='book_car_rental'),
    path('book/event/', views.AgentBookEventView.as_view(), name='book_event'),

    # Commission Management
    path('commissions/', views.AgentCommissionListView.as_view(), name='commissions'),
    path('commissions/summary/', views.AgentCommissionSummaryView.as_view(), name='commission_summary'),
    path('commissions/<uuid:commission_id>/', views.AgentCommissionDetailView.as_view(), name='commission_detail'),
]
```

---

## Summary

The Peykan Tourism Agent system provides a comprehensive solution for travel agents to manage customers and bookings. Key features include:

- **Role-based access control** with agent-specific permissions
- **Customer creation and management** with detailed tracking
- **Order placement** on behalf of customers with commission tracking
- **Analytics and reporting** for business insights
- **Multi-tier customer management** with status tracking
- **Secure authentication** with JWT tokens and session management
- **Comprehensive API** with 20+ endpoints for all operations

The system is designed to be scalable, secure, and user-friendly while maintaining clear separation between agents, customers, and administrators.
