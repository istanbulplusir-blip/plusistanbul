# Peykan Tourism Ecommerce Platform

A modern, multilingual, multi-currency booking platform built with Django 5 and Next.js 14, following Domain-Driven Design (DDD) principles and Clean Architecture.

## 🎯 MVP Product Flow

The platform implements a complete **Select → Add to Cart → Checkout** flow with the following features:

### 1. Product Selection (`/tours/[slug]`)

- **Slug-based routing** for SEO-friendly URLs
- **Multi-currency pricing** with real-time conversion
- **Variant selection** (different tour packages)
- **Date picker** for availability
- **Options/add-ons** selection
- **Quantity selector**
- **Real-time price calculation**
- **Add to Cart** and **Book Now** buttons

### 2. Shopping Cart (`/cart`)

- **Live cart summary** with multi-currency display
- **Quantity updates** with +/- controls
- **Item removal** and **cart clearing**
- **Product details** including variants, dates, and options
- **Order summary** with total calculation
- **Proceed to Checkout** button

### 3. Checkout Process (`/checkout`)

- **Customer information** form (pre-filled for logged-in users)
- **Billing address** collection
- **Special requests** field
- **Payment method** selection (Credit Card, Bank Transfer, PayPal)
- **Terms and conditions** acceptance
- **Order summary** with real-time currency conversion
- **Order creation** and redirect to payment/confirmation

### 4. Order Confirmation (`/orders/[orderNumber]`)

- **Order details** with status tracking
- **Payment information** and status
- **Customer details** and billing address
- **Order items** with all selections
- **Order summary** with breakdown

## 🏗️ Architecture

### Backend (Django 5 + DRF)

```
backend/
├── core/           # Core domain models (User, Currency, etc.)
├── shared/         # Shared services (CurrencyConverter, etc.)
├── users/          # User management with roles (Guest, Customer, Agent)
├── tours/          # Tour products with variants and options
├── events/         # Event products
├── transfers/      # Transfer products
├── cart/           # Shopping cart with temporary reservations
├── orders/         # Order management
├── payments/       # Payment processing
└── agents/         # Agent-specific functionality
```

### Frontend (Next.js 14 + TypeScript)

```
frontend/
├── app/
│   ├── components/     # Reusable UI components
│   ├── lib/
│   │   ├── api/        # API utilities with type safety
│   │   ├── hooks/      # SWR hooks for data fetching
│   │   └── types/      # TypeScript type definitions
│   ├── i18n/           # Internationalization (EN, FA, TR)
│   ├── tours/[slug]/   # Product detail pages
│   ├── cart/           # Shopping cart
│   ├── checkout/       # Checkout process
│   └── orders/         # Order management
```

## 🔧 Environment & CORS (Guest Cart via Session)

Frontend API base URL:

```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

Backend development settings:

```env
# backend/.env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Notes:

- The frontend API client (`frontend/lib/api/client.ts`) uses `withCredentials: true` so session cookies are sent for guest carts.
- In production, restrict origins (`CORS_ALLOW_ALL_ORIGINS=False`) and review `SESSION_COOKIE_SAMESITE` according to your domains.

## ✅ Phase 1 (MVP) Status

- All product pages read from real APIs (no mock data)
- Cart integrated with backend for guest (session) and authenticated users
- Checkout uses `/api/v1/orders/create/` to create orders
- Events seat-map connected to backend seat endpoints

See `ROADMAP.md` for QA checklist and next phases.

## 🚀 Key Features

### ✅ Domain-Driven Design (DDD)

- **Bounded Contexts**: Each app represents a domain boundary
- **Aggregate Roots**: Tour, Order, Cart as main entities
- **Value Objects**: UUID primary keys, slugs, currency codes
- **Domain Services**: Currency conversion, availability checking

### ✅ Multi-Currency Support

- **Real-time conversion** using CurrencyConverterService
- **Currency context** in frontend for user preference
- **Price display** in user's preferred currency
- **Order storage** in original currency with conversion tracking

### ✅ Internationalization (i18n)

- **Three languages**: English, Persian (Farsi), Turkish
- **Slug-based routing** with language prefixes
- **Translated content** for all UI elements
- **RTL support** for Persian language

### ✅ UUID & Slug Implementation

- **UUID primary keys** for all models
- **Slug-based URLs** for SEO and user-friendly navigation
- **Auto-generated slugs** from titles
- **Unique constraints** on slugs within categories

### ✅ Authentication & Authorization

- **JWT-based authentication** with refresh tokens
- **Role-based access**: Guest, Customer, Agent
- **OTP verification** for secure login
- **Profile management** with extended user data

### ✅ Cart & Order System

- **Temporary reservations** for inventory management
- **Multi-product support**: Tours, Events, Transfers
- **Variant and option selection**
- **Date-based availability**
- **Order status tracking**

## 🛠️ Technology Stack

### Backend

- **Django 5.0** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Database
- **Redis** - Caching and sessions
- **Celery** - Background tasks
- **Django Modeltranslation** - Multi-language fields
- **Django CORS Headers** - Cross-origin requests

### Frontend

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **SWR** - Data fetching and caching
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **next-intl** - Internationalization
- **Lucide React** - Icons

## 📦 Installation & Setup

### راه‌اندازی سریع لوکال (ویندوز/لینوکس)

1. **PostgreSQL را نصب کنید** و یک دیتابیس با نام `peykan_tourism` بسازید (مثلاً با pgAdmin یا دستور SQL).
2. فایل `backend/env.example` را به `backend/.env` کپی کنید (مقادیر پیش‌فرض برای لوکال آماده است).
3. مطمئن شوید فایل `.env` با encoding UTF-8 ذخیره شده باشد.
4. محیط مجازی را فعال کنید و پکیج‌ها را نصب کنید:
   ```sh
   cd backend
   python -m venv venv
   venv\Scripts\activate  # ویندوز
   # یا
   source venv/bin/activate  # لینوکس/مک
   pip install -r requirements.txt
   # اگر خطای psycopg2-binary داشتید:
   pip install psycopg2-binary
   ```
5. مهاجرت دیتابیس:
   ```sh
   python manage.py migrate
   ```
6. اجرای سرور:
   ```sh
   python manage.py runserver
   ```

> **نکته مهم:**
>
> - اگر با خطای encoding یا psycopg2 مواجه شدید، راهنما را در بخش FAQ و DEVELOPMENT_GUIDE.md ببینید.
> - فقط کافیست PostgreSQL نصب باشد و دیتابیس ساخته شود. نیازی به تغییر دیگر نیست.

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Create `.env` files based on `env.example` in the backend directory.

## 📚 Documentation

### 🚀 Quick Start

- **[setup-dev.sh](setup-dev.sh)** - اسکریپت راه‌اندازی خودکار (Linux/Mac)
- **[setup-dev.ps1](setup-dev.ps1)** - اسکریپت راه‌اندازی خودکار (Windows)

### 📖 Development Guides

- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - راهنمای کامل توسعه و استقرار
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - راهنمای مشارکت در پروژه
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - چک‌لیست استقرار تولید

### 📋 Additional Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - تاریخچه تغییرات پروژه
- **[frontend/DESIGN_SYSTEM.md](frontend/DESIGN_SYSTEM.md)** - راهنمای Design System

## 🎨 Design System

این پروژه از یک Design System منسجم استفاده می‌کند که شامل:

- **کامپوننت‌های پایه**: Button, Card, Input, Loading
- **سیستم رنگ‌بندی**: Primary, Secondary, Semantic colors
- **تایپوگرافی**: Font families, sizes, weights
- **فاصله‌گذاری**: 4px grid system
- **ریسپانسیو**: Mobile-first approach

برای اطلاعات بیشتر، فایل `frontend/DESIGN_SYSTEM.md` را مطالعه کنید.

- **[CONTRIBUTORS.md](CONTRIBUTORS.md)** - لیست مشارکت‌کنندگان
- **[SECURITY.md](SECURITY.md)** - سیاست‌های امنیتی
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - قوانین رفتار
- **[SUPPORT.md](SUPPORT.md)** - راهنمای پشتیبانی

## 🚀 Deployment

### Production Deployment

```bash
# Deploy to production server
./deploy.sh

# Or manually:
git pull origin main
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
```

### Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Execute commands in containers
docker-compose exec backend python manage.py shell
docker-compose exec frontend npm run build

# Stop and remove containers
docker-compose down -v
```

## 🔄 Complete User Flow

1. **Browse Products**: User visits `/tours` to see available tours
2. **Product Detail**: User clicks on a tour to view details at `/tours/[slug]`
3. **Select Options**: User chooses date, variant, options, and quantity
4. **Add to Cart**: User adds product to cart with "Add to Cart" button
5. **Review Cart**: User visits `/cart` to review items and make changes
6. **Checkout**: User proceeds to `/checkout` to complete purchase
7. **Order Confirmation**: User receives order confirmation at `/orders/[orderNumber]`

## 🎨 UI/UX Features

- **Responsive design** for all screen sizes
- **Modern, clean interface** with TailwindCSS
- **Loading states** and error handling
- **Form validation** with real-time feedback
- **Currency switching** without page reload
- **Language switching** with proper RTL support
- **Accessibility** features for screen readers

## 🔒 Security Features

- **JWT authentication** with secure token storage
- **CSRF protection** on all forms
- **Input validation** and sanitization
- **Rate limiting** on API endpoints
- **Secure payment** processing
- **Data encryption** for sensitive information

## 📈 Performance Optimizations

- **SWR caching** for API responses
- **Image optimization** with Next.js
- **Code splitting** and lazy loading
- **Database indexing** on frequently queried fields
- **Redis caching** for expensive operations
- **CDN-ready** static assets

## 🧪 Testing Strategy

- **Unit tests** for domain logic
- **Integration tests** for API endpoints
- **End-to-end tests** for complete user flows
- **Performance tests** for critical operations

## 📚 Documentation

### Development Guides

- [**DEVELOPMENT_GUIDE.md**](./DEVELOPMENT_GUIDE.md) - راهنمای کامل توسعه و استقرار
- [**CONTRIBUTING.md**](./CONTRIBUTING.md) - راهنمای مشارکت در پروژه
- [**DEPLOYMENT_CHECKLIST.md**](./DEPLOYMENT_CHECKLIST.md) - چک‌لیست استقرار تولید

### Project Documentation

- [**CHANGELOG.md**](./CHANGELOG.md) - تاریخچه تغییرات
- [**CONTRIBUTORS.md**](./CONTRIBUTORS.md) - لیست مشارکت‌کنندگان
- [**SECURITY.md**](./SECURITY.md) - سیاست‌های امنیتی
- [**CODE_OF_CONDUCT.md**](./CODE_OF_CONDUCT.md) - قوانین رفتار
- [**SUPPORT.md**](./SUPPORT.md) - راهنمای پشتیبانی

### Quick References

- [**API Documentation**](./API_DOCUMENTATION.md) - مستندات API
- [**Architecture Guide**](./ARCHITECTURE.md) - راهنمای معماری
- [**Troubleshooting**](./TROUBLESHOOTING.md) - راهنمای عیب‌یابی
- **E2E tests** for critical user flows
- **Type safety** with TypeScript
- **Linting** and code formatting

## 🚀 Deployment

### Quick Deployment

```bash
# Automated deployment
./deploy.sh
```

### Manual Deployment

```bash
# On production server
ssh djangouser@167.235.140.125
cd /home/djangouser/peykan-tourism
git pull origin main
docker-compose -f docker-compose.production.yml up -d --build
```

## 📚 Documentation

### Development Guides

- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - راهنمای کامل توسعه و استقرار
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - راهنمای مشارکت در پروژه
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - چک‌لیست استقرار

### Project Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - تاریخچه تغییرات
- **[CONTRIBUTORS.md](CONTRIBUTORS.md)** - لیست مشارکت‌کنندگان
- **[SECURITY.md](SECURITY.md)** - سیاست‌های امنیتی
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - قوانین رفتار
- **[SUPPORT.md](SUPPORT.md)** - راهنمای پشتیبانی
- **[FAQ.md](FAQ.md)** - سوالات متداول
- **[ROADMAP.md](ROADMAP.md)** - نقشه راه پروژه
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - معماری سیستم
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - مستندات API

### Setup Scripts

- **[setup-dev.sh](setup-dev.sh)** - اسکریپت راه‌اندازی محیط توسعه (Linux/Mac)
- **[setup-dev.ps1](setup-dev.ps1)** - اسکریپت راه‌اندازی محیط توسعه (Windows)
- **[deploy.sh](deploy.sh)** - اسکریپت استقرار خودکار

### Production Checklist

See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for a comprehensive deployment checklist.

### Docker Support

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.production.yml up -d
```

## 📝 API Documentation

The API follows RESTful principles with comprehensive endpoints for:

- **Authentication**: Login, register, password reset
- **Products**: Tours, events, transfers with filtering
- **Cart**: Add, update, remove items
- **Orders**: Create, view, update orders
- **Payments**: Process payments and refunds
- **Users**: Profile management and preferences

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for detailed information on how to:

1. Set up your development environment
2. Follow our coding standards
3. Submit pull requests
4. Report bugs and request features

### Quick Start for Contributors

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/peykan-tourism.git
cd peykan-tourism

# Setup development environment
.\setup-dev.ps1  # Windows
# ./setup-dev.sh  # Linux/Mac

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes and submit a PR
```

## 📚 Documentation

- [Development Guide](./DEVELOPMENT_GUIDE.md) - Complete guide for development and deployment
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md) - Production deployment checklist
- [API Documentation](./API_DOCUMENTATION.md) - Complete API documentation
- [Architecture Guide](./ARCHITECTURE.md) - System architecture documentation
- [Product Roadmap](./ROADMAP.md) - Product development roadmap
- [Security Policy](./SECURITY.md) - Security guidelines and procedures
- [Support Guide](./SUPPORT.md) - Getting help and support
- [FAQ](./FAQ.md) - Frequently asked questions
- [Code of Conduct](./CODE_OF_CONDUCT.md) - Community guidelines

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Peykan Tourism** - Building the future of travel booking with modern technology and user-centric design.
