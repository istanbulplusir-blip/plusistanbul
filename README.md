# Peykan Travel Istanbul - Tourism E-commerce Platform

A comprehensive tourism e-commerce platform built with Django REST Framework and Next.js, offering tours, transfers, car rentals, and event bookings.

## 📚 Documentation

**📖 [Complete Documentation Index](./DOCUMENTATION_INDEX.md)**

### Quick Links
- 🚀 [Quick Start Guide](./docs/setup/QUICK_START.md)
- 🔧 [Commands Cheatsheet](./docs/development/COMMANDS_CHEATSHEET.md)
- 🖼️ [Image Optimization](./docs/features/image-optimization/)
- 🎨 [Hero Slider](./docs/features/hero-slider/)
- 🎭 [Events System](./docs/features/events/)
- 🗺️ [Tours System](./docs/features/tours/)
- 🧾 [Invoice System](./docs/features/invoices/)

## 🚀 Features

- **Multi-language Support**: English, Turkish, Persian (Farsi)
- **Product Management**: Tours, Transfers, Car Rentals, Events
- **Agent System**: Commission-based booking system for travel agents
- **Shopping Cart**: Multi-product cart with real-time pricing
- **Order Management**: Complete order lifecycle with invoice generation
- **Payment Integration**: Secure payment gateway integration
- **PDF Invoices**: Multi-language invoice generation with RTL support
- **Admin Dashboard**: Comprehensive admin panel for content management
- **Responsive Design**: Mobile-first responsive UI

## 📋 Tech Stack

### Backend
- Django 5.1.5
- Django REST Framework 3.15.2
- PostgreSQL (Production) / SQLite (Development)
- Redis (Caching & Sessions)
- Celery (Background Tasks)
- JWT Authentication
- ReportLab (PDF Generation)

### Frontend
- Next.js 15.5.4
- React 18.3.1
- TypeScript 5.9.2
- Tailwind CSS 3.4.17
- Zustand (State Management)
- SWR (Data Fetching)
- React Leaflet (Maps)

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (for production)
- Redis 6+ (for caching)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate SECRET_KEY
python generate_secret_key.py

# Copy environment file and configure
cp env.production.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

## 🚢 Production Deployment

See [PRODUCTION_DEPLOYMENT_CHECKLIST.md](PRODUCTION_DEPLOYMENT_CHECKLIST.md) for detailed deployment instructions.

### Quick Production Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn peykan.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Frontend
cd frontend
npm install
npm run build
npm start
```

## 📚 Documentation

- [Production Deployment Checklist](PRODUCTION_DEPLOYMENT_CHECKLIST.md)
- [Production Ready Checklist](PRODUCTION_READY_CHECKLIST.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [Git Setup Instructions](GIT_SETUP_INSTRUCTIONS.md)
- [Git Push Instructions](GIT_PUSH_INSTRUCTIONS.md)
- [Production Dev Setup](PRODUCTION_DEV_SETUP.md)
- [راهنمای راه‌اندازی لوکال](راهنمای_راه_اندازی_لوکال.md)
- [دستورات مهم](دستورات_مهم.md)

Additional documentation available in the [docs](docs/) directory.

## 🔒 Security

- HTTPS/SSL encryption
- CSRF protection
- JWT authentication
- Secure session management
- Rate limiting
- XSS protection
- SQL injection prevention

## 🌍 Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/1
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

## 📝 License

Proprietary - All rights reserved

## 👥 Support

For support and questions, please contact the development team.

---

Built with ❤️ by Peykan Travel Team
