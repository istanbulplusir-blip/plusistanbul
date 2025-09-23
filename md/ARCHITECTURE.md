# Architecture Documentation - Peykan Tourism

## 🏗️ System Overview

Peykan Tourism is built using a modern, scalable architecture that follows Domain-Driven Design (DDD) principles and Clean Architecture patterns. The system is designed to handle high traffic, support multiple languages and currencies, and provide a seamless user experience.

## 📐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  Third-party Integrations      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  Next.js Frontend  │  Nginx Reverse Proxy  │  Admin Panel     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Django REST API  │  Authentication  │  Authorization          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Domain Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic  │  Domain Services  │  Value Objects          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis  │  File Storage  │  External Services   │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Architectural Principles

### **۱. Domain-Driven Design (DDD)**
- **Bounded Contexts**: Clear boundaries between different domains
- **Aggregate Roots**: Tour, Order, Cart as main entities
- **Value Objects**: UUID, Currency, Slug as immutable objects
- **Domain Services**: Business logic encapsulated in services

### **۲. Clean Architecture**
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Separation of Concerns**: Clear separation between layers
- **Testability**: Easy to test each layer independently
- **Maintainability**: Changes in one layer don't affect others

### **۳. Microservices Ready**
- **Service Boundaries**: Clear service boundaries for future microservices
- **API-First Design**: All functionality exposed through APIs
- **Stateless Services**: Services don't maintain state
- **Event-Driven**: Loose coupling through events

## 🏢 System Components

### **Frontend (Next.js 14)**

#### **Architecture**
```
frontend/
├── app/                    # App Router (Next.js 14)
│   ├── components/         # Reusable UI components
│   ├── lib/               # Utilities and configurations
│   │   ├── api/           # API client and utilities
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript type definitions
│   ├── i18n/              # Internationalization
│   └── [routes]/          # Page components
├── public/                # Static assets
└── types/                 # Global type definitions
```

#### **Key Features**
- **App Router**: Next.js 14 App Router for better performance
- **TypeScript**: Full type safety throughout the application
- **TailwindCSS**: Utility-first CSS framework
- **SWR**: Data fetching and caching
- **React Hook Form**: Form management with validation
- **Zod**: Schema validation
- **next-intl**: Internationalization support

#### **State Management**
- **React Context**: For global state (auth, cart, currency)
- **SWR**: For server state management
- **Local Storage**: For persistent client state
- **URL State**: For shareable state

### **Backend (Django 5 + DRF)**

#### **Architecture**
```
backend/
├── core/                  # Core domain models
├── shared/                # Shared services and utilities
├── users/                 # User management domain
├── tours/                 # Tour products domain
├── events/                # Event products domain
├── transfers/             # Transfer products domain
├── cart/                  # Shopping cart domain
├── orders/                # Order management domain
├── payments/              # Payment processing domain
├── agents/                # Agent-specific functionality
└── peykan/               # Django project settings
```

#### **Domain Structure**
Each domain follows the same structure:
```
domain_name/
├── __init__.py
├── admin.py              # Django admin configuration
├── apps.py               # Django app configuration
├── models.py             # Domain models
├── serializers.py        # API serializers
├── views.py              # API views
├── urls.py               # URL routing
├── services.py           # Business logic services
├── repositories.py       # Data access layer
└── migrations/           # Database migrations
```

#### **Key Features**
- **Django 5.0**: Latest Django version with modern features
- **Django REST Framework**: Powerful API framework
- **PostgreSQL**: Primary database with advanced features
- **Redis**: Caching and session storage
- **Celery**: Background task processing
- **JWT Authentication**: Secure token-based authentication
- **CORS Support**: Cross-origin resource sharing

### **Database (PostgreSQL)**

#### **Schema Design**
```sql
-- Core tables
users_user              # User accounts and profiles
core_currency           # Supported currencies
core_language           # Supported languages

-- Product tables
tours_tour              # Tour products
tours_tourvariant       # Tour variants (packages)
tours_touroption        # Tour options/add-ons
events_event            # Event products
transfers_transfer      # Transfer products

-- Booking tables
cart_cart               # Shopping cart
cart_cartitem           # Cart items
orders_order            # Orders
orders_orderitem        # Order items
payments_payment        # Payment records

-- Agent tables
agents_agent            # Agent accounts
agents_commission       # Commission tracking
```

#### **Key Features**
- **UUID Primary Keys**: Globally unique identifiers
- **Slug Fields**: SEO-friendly URLs
- **JSON Fields**: Flexible data storage
- **Indexes**: Optimized query performance
- **Foreign Keys**: Referential integrity
- **Constraints**: Data validation rules

### **Caching (Redis)**

#### **Cache Strategy**
```python
# Cache keys structure
"tour:{tour_id}:details"           # Tour details
"tour:{tour_id}:pricing"           # Tour pricing
"user:{user_id}:cart"              # User cart
"currency:{from}:{to}:rate"        # Currency rates
"session:{session_id}:data"        # Session data
```

#### **Cache Patterns**
- **Cache-Aside**: Read from cache, update on miss
- **Write-Through**: Update cache and database together
- **Cache-Aside with TTL**: Automatic cache expiration
- **Cache Invalidation**: Manual cache clearing

### **File Storage**

#### **Storage Strategy**
```
media/
├── tours/              # Tour images
├── events/             # Event images
├── transfers/          # Transfer images
├── users/              # User avatars
└── uploads/            # General uploads
```

#### **Features**
- **Image Optimization**: Automatic resizing and compression
- **CDN Ready**: Static file serving through CDN
- **Backup Strategy**: Regular backups to cloud storage
- **Access Control**: Secure file access

## 🔄 Data Flow

### **۱. User Registration Flow**
```
1. User fills registration form (Frontend)
2. Form validation (Frontend + Zod)
3. API request to /api/v1/auth/register/ (Backend)
4. User creation (Domain Service)
5. Email verification (Background Task)
6. Response with JWT tokens (Backend)
7. Token storage and redirect (Frontend)
```

### **۲. Tour Booking Flow**
```
1. User browses tours (Frontend)
2. Tour data fetched from API (Backend)
3. User selects tour, date, options (Frontend)
4. Price calculation (Domain Service)
5. Add to cart (Cart Service)
6. Cart data cached in Redis
7. Checkout process (Order Service)
8. Payment processing (Payment Service)
9. Order confirmation (Email Service)
```

### **۳. Payment Processing Flow**
```
1. User submits payment (Frontend)
2. Payment validation (Payment Service)
3. External payment API call (Payment Gateway)
4. Payment confirmation (Webhook)
5. Order status update (Order Service)
6. Email notification (Email Service)
7. Inventory update (Inventory Service)
```

## 🔒 Security Architecture

### **Authentication & Authorization**
- **JWT Tokens**: Secure token-based authentication
- **Refresh Tokens**: Long-term session management
- **Role-Based Access**: User, Agent, Admin roles
- **Permission System**: Granular permissions
- **Session Management**: Secure session handling

### **Data Protection**
- **HTTPS**: All communications encrypted
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Protection**: ORM and parameterized queries
- **XSS Protection**: Content Security Policy
- **CSRF Protection**: Cross-site request forgery prevention

### **Infrastructure Security**
- **Docker Security**: Container isolation
- **Network Security**: Firewall and access control
- **Database Security**: Encrypted connections
- **Backup Security**: Encrypted backups
- **Monitoring**: Security event monitoring

## 📊 Performance Architecture

### **Frontend Performance**
- **Code Splitting**: Dynamic imports for smaller bundles
- **Image Optimization**: Next.js automatic image optimization
- **Caching**: SWR caching for API responses
- **Lazy Loading**: Components loaded on demand
- **Service Worker**: Offline functionality

### **Backend Performance**
- **Database Optimization**: Query optimization and indexing
- **Caching Strategy**: Multi-level caching
- **Connection Pooling**: Database connection management
- **Background Tasks**: Async processing with Celery
- **Load Balancing**: Horizontal scaling support

### **Infrastructure Performance**
- **CDN**: Global content delivery
- **Load Balancer**: Traffic distribution
- **Auto Scaling**: Automatic resource scaling
- **Monitoring**: Performance metrics tracking
- **Alerting**: Automated performance alerts

## 🔧 Deployment Architecture

### **Development Environment**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│  (Next.js)      │◄──►│   (Django)      │◄──►│  (PostgreSQL)   │
│  localhost:3000 │    │  localhost:8000 │    │  localhost:5432 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Production Environment**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Load Balancer │    │   CDN           │
│  (Reverse Proxy)│◄──►│   (HAProxy)     │◄──►│  (Cloudflare)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│  (Next.js)      │    │   (Django)      │    │  (PostgreSQL)   │
│   Container     │    │   Container     │    │   Container     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis         │    │   File Storage  │    │   Monitoring    │
│   (Cache)       │    │   (S3/Cloud)    │    │   (Prometheus)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 Event-Driven Architecture

### **Event Types**
```python
# Domain Events
TourCreatedEvent
TourUpdatedEvent
OrderCreatedEvent
OrderCancelledEvent
PaymentProcessedEvent
UserRegisteredEvent

# Integration Events
EmailSentEvent
SMSSentEvent
WebhookTriggeredEvent
CacheInvalidatedEvent
```

### **Event Flow**
```
1. Domain Event Triggered (Domain Service)
2. Event Published (Event Bus)
3. Event Handlers Process (Background Tasks)
4. Side Effects Executed (Email, SMS, etc.)
5. Event Stored (Event Store)
```

## 📈 Scalability Architecture

### **Horizontal Scaling**
- **Load Balancer**: Distribute traffic across multiple instances
- **Database Replication**: Read replicas for read-heavy workloads
- **Cache Clustering**: Redis cluster for high availability
- **CDN**: Global content distribution

### **Vertical Scaling**
- **Resource Optimization**: Efficient resource usage
- **Database Optimization**: Query and index optimization
- **Caching Strategy**: Multi-level caching
- **Code Optimization**: Performance-focused development

### **Microservices Migration Path**
```
Current: Monolithic Architecture
    ↓
Phase 1: API Gateway + Service Decomposition
    ↓
Phase 2: Database Per Service
    ↓
Phase 3: Event-Driven Communication
    ↓
Phase 4: Independent Deployment
```

## 🔍 Monitoring & Observability

### **Application Monitoring**
- **Health Checks**: Service health monitoring
- **Performance Metrics**: Response time, throughput
- **Error Tracking**: Error rate and types
- **User Analytics**: User behavior tracking

### **Infrastructure Monitoring**
- **Resource Usage**: CPU, memory, disk usage
- **Network Monitoring**: Bandwidth, latency
- **Database Monitoring**: Query performance, connections
- **Security Monitoring**: Security events and alerts

### **Logging Strategy**
```
Application Logs: Structured logging with correlation IDs
Access Logs: HTTP request/response logging
Error Logs: Error tracking and alerting
Audit Logs: Security and compliance logging
```

## 🧪 Testing Architecture

### **Testing Pyramid**
```
    E2E Tests (Few)
        ▲
   Integration Tests (Some)
        ▲
   Unit Tests (Many)
```

### **Test Types**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service integration testing
- **API Tests**: API endpoint testing
- **E2E Tests**: Full user journey testing
- **Performance Tests**: Load and stress testing

### **Testing Tools**
- **Backend**: pytest, Django TestCase
- **Frontend**: Jest, React Testing Library
- **API**: Postman, Newman
- **E2E**: Playwright, Cypress
- **Performance**: Locust, Artillery

---

## 📞 Architecture Team

### **Technical Leadership**
- **Architecture Lead**: [نام مسئول معماری]
- **Backend Lead**: [نام مسئول بک‌اند]
- **Frontend Lead**: [نام مسئول فرانت‌اند]
- **DevOps Lead**: [نام مسئول DevOps]

### **Contact Information**
- **Architecture Questions**: architecture@peykantravelistanbul.com
- **Technical Decisions**: tech-decisions@peykantravelistanbul.com
- **Performance Issues**: performance@peykantravelistanbul.com

---

**نکته**: این معماری انعطاف‌پذیر است و بر اساس نیازهای کسب‌وکار و پیشرفت‌های تکنولوژی به‌روزرسانی می‌شود. 