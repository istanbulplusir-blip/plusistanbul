# Production Deployment Guide - Peykan Tourism Platform

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Domain name configured
- SSL certificates ready
- PostgreSQL database (optional, SQLite for development)

### 1. Environment Setup

```bash
# Copy production environment template
cp backend/env.production backend/.env

# Edit environment variables
nano backend/.env
```

**Required Environment Variables:**
```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-production-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis
REDIS_URL=redis://redis:6379/1

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway
PAYMENT_SECRET_KEY=your-stripe-secret-key

# SMS
KAVENEGAR_API_KEY=your-kavenegar-api-key
```

### 2. SSL Certificate Setup

For production, replace the self-signed certificates:

```bash
# Copy your SSL certificates
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem
```

### 3. Database Setup

#### Option A: PostgreSQL (Recommended for Production)
```bash
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://peykan_user:secure_password@postgres:5432/peykan
```

#### Option B: SQLite (Development)
```bash
# Update DATABASE_URL in .env
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Build and Deploy

```bash
# Build all services
docker-compose build

# Start services in production mode
docker-compose --profile production up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Database Migrations

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### 6. Health Checks

```bash
# Check backend health
curl https://your-domain.com/api/v1/health/

# Check frontend health
curl https://your-domain.com/

# Check nginx health
curl https://your-domain.com/health
```

## 🔧 Configuration Details

### Docker Services

#### Backend (Django)
- **Port**: 8000
- **Health Check**: `/api/v1/health/`
- **Workers**: 3 (gevent)
- **Static Files**: Served by WhiteNoise
- **Logs**: `/app/logs/django.log`

#### Frontend (Next.js)
- **Port**: 3000
- **Health Check**: `/api/health`
- **Build**: Production optimized
- **Static Export**: Enabled

#### Nginx (Reverse Proxy)
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **SSL**: TLS 1.2/1.3
- **Rate Limiting**: API endpoints
- **Security Headers**: HSTS, CSP, XSS Protection
- **Gzip Compression**: Enabled

#### Database (PostgreSQL)
- **Port**: 5432
- **Health Check**: `pg_isready`
- **Backup**: Configure automated backups

#### Redis (Cache)
- **Port**: 6379
- **Health Check**: `redis-cli ping`
- **Database**: 1 (separate from session storage)

### Security Features

#### Django Security
- ✅ CSRF Protection enabled
- ✅ XSS Protection headers
- ✅ Content Type sniffing disabled
- ✅ HSTS enabled
- ✅ Secure cookies
- ✅ Rate limiting on API endpoints

#### Nginx Security
- ✅ SSL/TLS encryption
- ✅ Security headers
- ✅ Rate limiting
- ✅ Request size limits
- ✅ Gzip compression

#### Docker Security
- ✅ Non-root users
- ✅ Multi-stage builds
- ✅ Minimal base images
- ✅ Health checks
- ✅ Resource limits

## 📊 Monitoring and Logging

### Log Locations
```bash
# Django logs
docker-compose exec backend tail -f /app/logs/django.log

# Nginx logs
docker-compose logs -f nginx

# Application logs
docker-compose logs -f backend frontend
```

### Health Monitoring
```bash
# Service health
docker-compose ps

# Resource usage
docker stats

# Database connections
docker-compose exec postgres psql -U peykan_user -d peykan -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🔄 Maintenance

### Regular Tasks

#### Daily
- Check service health
- Monitor error logs
- Verify backup completion

#### Weekly
- Review security logs
- Update dependencies
- Performance analysis

#### Monthly
- Security audit
- SSL certificate renewal
- Database optimization

### Backup Strategy

#### Database Backup
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U peykan_user peykan > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U peykan_user peykan < backup_file.sql
```

#### Media Files Backup
```bash
# Backup media files
docker-compose exec backend tar -czf media_backup_$(date +%Y%m%d).tar.gz /app/media/

# Restore
docker-compose exec backend tar -xzf media_backup_file.tar.gz -C /app/
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs service_name

# Check resource usage
docker stats

# Restart service
docker-compose restart service_name
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready -U peykan_user

# Check Django database connection
docker-compose exec backend python manage.py dbshell
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect your-domain.com:443
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor slow queries
docker-compose exec postgres psql -U peykan_user -d peykan -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check cache hit rate
docker-compose exec redis redis-cli info memory
```

## 🔒 Security Checklist

### Pre-Deployment
- [ ] Environment variables secured
- [ ] SSL certificates installed
- [ ] Database credentials updated
- [ ] Secret keys generated
- [ ] CORS origins configured
- [ ] Rate limiting enabled

### Post-Deployment
- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] Security headers present
- [ ] Error pages configured
- [ ] Monitoring active
- [ ] Backups working

### Ongoing
- [ ] Regular security updates
- [ ] Log monitoring
- [ ] Performance monitoring
- [ ] SSL certificate renewal
- [ ] Database maintenance

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Test connectivity: `curl -I https://your-domain.com`
4. Review security: `curl -I -H "Host: your-domain.com" https://your-domain.com`

## 🔄 Updates and Upgrades

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose --profile production up -d

# Run migrations
docker-compose exec backend python manage.py migrate
```

### Dependency Updates
```bash
# Update Python dependencies
docker-compose exec backend pip install --upgrade -r requirements.txt

# Update Node.js dependencies
docker-compose exec frontend npm update

# Rebuild containers
docker-compose build
docker-compose --profile production up -d
```

---

**Production Status**: ✅ Ready for deployment
**Last Updated**: December 2024
**Version**: 1.0.0 