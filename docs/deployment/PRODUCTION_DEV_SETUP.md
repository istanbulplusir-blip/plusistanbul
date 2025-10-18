# Production-like Development Environment Setup

This guide helps you set up a production-like environment on your development machine for testing the Peykan Tourism Platform before actual deployment.

## Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM available for Docker
- Ports 80, 3000, 5432, 6379, and 8000 available

## Quick Start

### Windows

```bash
# Run the setup script
.\setup-production-dev.bat
```

### Linux/macOS

```bash
# Make the script executable and run it
chmod +x setup-production-dev.sh
./setup-production-dev.sh
```

## Manual Setup

If you prefer to set up manually:

### 1. Environment Configuration

Copy the environment template:

```bash
cp backend/env.production.dev backend/.env.production.dev
```

Edit the environment variables in `backend/.env.production.dev` as needed.

### 2. Generate SSL Certificates

```bash
# Using Docker (recommended)
docker run --rm -v "$(pwd)/nginx/ssl:/ssl" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /ssl/key.pem -out /ssl/cert.pem -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/OU=IT Department/CN=localhost"
```

### 3. Start Services

```bash
# Build and start all services
docker-compose -f docker-compose.production-dev.yml up -d --build
```

## Services

The production-like environment includes:

- **Frontend (Next.js)**: http://localhost:3000
- **Backend API (Django)**: http://localhost:8000
- **Nginx Proxy**: http://localhost:80
- **PostgreSQL Database**: localhost:5432
- **Redis Cache**: localhost:6379

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  Django Backend │────│   PostgreSQL    │
│   (Port 80)     │    │   (Port 8000)   │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         └──────────────│  Next.js Frontend│
                        │   (Port 3000)   │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │     Redis       │
                        │   (Port 6379)   │
                        └─────────────────┘
```

## Configuration

### Environment Variables

Key environment variables in `backend/.env.production.dev`:

- `DEBUG=False` - Production-like debugging
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CORS_ALLOWED_ORIGINS` - Allowed frontend origins

### Database

- **Engine**: PostgreSQL 16.3
- **Database**: peykan
- **User**: peykan_user
- **Password**: dev_password_123 (change in production)

### Cache

- **Engine**: Redis 7.4
- **Password**: dev_redis_123 (change in production)

## Management Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.production-dev.yml logs -f

# Specific service
docker-compose -f docker-compose.production-dev.yml logs -f backend
```

### Restart Services

```bash
# All services
docker-compose -f docker-compose.production-dev.yml restart

# Specific service
docker-compose -f docker-compose.production-dev.yml restart backend
```

### Stop Services

```bash
docker-compose -f docker-compose.production-dev.yml down
```

### Database Management

```bash
# Access PostgreSQL
docker-compose -f docker-compose.production-dev.yml exec postgres psql -U peykan_user -d peykan

# Run Django migrations
docker-compose -f docker-compose.production-dev.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.production-dev.yml exec backend python manage.py createsuperuser
```

## Testing

### Health Checks

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/health/
- **Nginx**: http://localhost/health

### API Testing

```bash
# Test API endpoints
curl http://localhost:8000/api/v1/tours/
curl http://localhost:8000/api/v1/events/
```

## Production Differences

This development environment differs from production in:

1. **SSL**: Uses self-signed certificates (not trusted by browsers)
2. **Database**: Uses development passwords
3. **Email**: Uses console backend (emails printed to logs)
4. **Logging**: More verbose logging enabled
5. **Ports**: All services exposed for development access

## Troubleshooting

### Services Not Starting

1. Check Docker is running
2. Check ports are available
3. Check logs: `docker-compose -f docker-compose.production-dev.yml logs`

### Database Connection Issues

1. Wait for PostgreSQL to fully start (30-60 seconds)
2. Check database logs: `docker-compose -f docker-compose.production-dev.yml logs postgres`

### Frontend Not Loading

1. Check Next.js build completed
2. Check frontend logs: `docker-compose -f docker-compose.production-dev.yml logs frontend`

### API Not Responding

1. Check Django migrations completed
2. Check backend logs: `docker-compose -f docker-compose.production-dev.yml logs backend`

## Security Notes

⚠️ **Important**: This is a development environment with relaxed security:

- Default passwords are used
- Self-signed SSL certificates
- Debug information may be exposed
- Not suitable for production use

## Next Steps

After testing in this environment:

1. Update environment variables for production
2. Use real SSL certificates
3. Configure proper database passwords
4. Set up monitoring and logging
5. Deploy to production infrastructure

## Support

For issues with this setup:

1. Check Docker logs
2. Verify all services are running
3. Check port availability
4. Review environment configuration
