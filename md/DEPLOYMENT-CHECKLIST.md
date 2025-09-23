# Peykan Tourism Platform - Production Deployment Checklist

## 🔍 Critical Issues Found & Fixed

### ✅ Fixed Issues
1. **Missing frontend/lib directory** - Fixed .gitignore to allow lib/ directory
2. **Missing PostgreSQL driver** - Uncommented psycopg2-binary in requirements.txt
3. **Missing critical frontend files** - Added lib/hooks, lib/contexts, lib/services

### ⚠️ Issues Requiring Attention
1. **SSL Certificates** - Need to generate/provide SSL certificates for domain
2. **Environment Variables** - Need actual SMTP, payment, and API keys
3. **Database Migration** - Need to ensure all migrations are applied
4. **Static Files** - Need to collect static files in production

## 📁 Files Required for Production Deployment

### Core Application Files
- ✅ `backend/` - Django application
- ✅ `frontend/` - Next.js application  
- ✅ `nginx/` - Reverse proxy configuration
- ✅ `docker-compose.yml` - Container orchestration
- ✅ `backend/Dockerfile` - Backend container
- ✅ `frontend/Dockerfile` - Frontend container
- ✅ `nginx/Dockerfile` - Nginx container

### Configuration Files
- ✅ `backend/env.production` - Production environment template
- ✅ `backend/peykan/settings_production.py` - Production Django settings
- ✅ `nginx/nginx.conf` - Nginx configuration
- ✅ `backend/requirements.txt` - Python dependencies
- ✅ `frontend/package.json` - Node.js dependencies

### Critical Frontend Files (Now Fixed)
- ✅ `frontend/lib/hooks/useCart.ts`
- ✅ `frontend/lib/hooks/useEvents.ts`
- ✅ `frontend/lib/hooks/useTransfers.ts`
- ✅ `frontend/lib/contexts/AuthContext.tsx`
- ✅ `frontend/lib/contexts/CartContext.tsx`
- ✅ `frontend/lib/services/tokenService.ts`
- ✅ `frontend/lib/services/profileService.ts`
- ✅ `frontend/lib/services/orderService.ts`

## 🔧 Pre-Deployment Configuration Required

### 1. Environment Variables (Critical)
```bash
# Update backend/env.production with actual values:
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=your-actual-app-password
KAVENEGAR_API_KEY=your-actual-kavenegar-key
PAYMENT_SECRET_KEY=your-actual-stripe-key
SECRET_KEY=your-actual-secret-key
JWT_SECRET_KEY=your-actual-jwt-secret
```

### 2. SSL Certificates (Critical)
```bash
# Generate SSL certificates for peykantravelistanbul.com
# Place in nginx/ssl/ directory:
# - cert.pem
# - key.pem
```

### 3. Database Setup
```bash
# Ensure PostgreSQL is running
# Run migrations: python manage.py migrate
# Create superuser: python manage.py createsuperuser
```

### 4. Static Files
```bash
# Collect static files: python manage.py collectstatic
```

## 🚀 Deployment Steps

### Step 1: Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER

# Clone repository
git clone https://github.com/PeykanTravel/peykan-tourism.git
cd peykan-tourism
```

### Step 2: Configure Environment
```bash
# Copy and edit environment file
cp backend/env.production backend/.env
# Edit backend/.env with actual values
```

### Step 3: Setup SSL Certificates
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificates (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=TR/ST=Istanbul/L=Istanbul/O=PeykanTravel/CN=peykantravelistanbul.com"

# For production, use Let's Encrypt or commercial certificates
```

### Step 4: Build and Deploy
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Step 5: Database Setup
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

## 🔒 Security Checklist

### ✅ Implemented Security Measures
- [x] HTTPS redirect in nginx
- [x] Security headers in nginx
- [x] Rate limiting for API endpoints
- [x] CORS configuration for production
- [x] Secure cookie settings
- [x] HSTS headers
- [x] XSS protection
- [x] Content type sniffing protection

### ⚠️ Additional Security Required
- [ ] SSL certificate installation
- [ ] Firewall configuration
- [ ] Database backup strategy
- [ ] Monitoring and logging setup
- [ ] Regular security updates

## 📊 Monitoring & Maintenance

### Health Checks
- [ ] API health endpoint: `/health`
- [ ] Database connectivity
- [ ] Redis connectivity
- [ ] Static file serving
- [ ] SSL certificate validity

### Logging
- [ ] Nginx access/error logs
- [ ] Django application logs
- [ ] Docker container logs
- [ ] System resource monitoring

### Backup Strategy
- [ ] Database backups
- [ ] Media file backups
- [ ] Configuration backups
- [ ] Disaster recovery plan

## 🐛 Troubleshooting

### Common Issues
1. **Frontend build fails** - Check if all lib/ files are present
2. **Backend container exits** - Check environment variables and database connection
3. **SSL errors** - Verify certificate paths and permissions
4. **Database connection fails** - Check PostgreSQL service and credentials
5. **Static files not served** - Run collectstatic and check nginx configuration

### Debug Commands
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# Check environment variables
docker-compose exec backend env

# Test database connection
docker-compose exec backend python manage.py dbshell

# Check static files
docker-compose exec backend python manage.py collectstatic --dry-run
```

## 📞 Support & Documentation

### Key Files for Reference
- `DEPLOYMENT-README.md` - Detailed deployment guide
- `backend/ADMIN_GUIDE.md` - Admin panel setup
- `AUTHENTICATION_GUIDE.md` - Authentication system guide
- `README.md` - General project documentation

### Contact Information
- Repository: https://github.com/PeykanTravel/peykan-tourism
- Domain: peykantravelistanbul.com
- Support: [Add support contact information]

---

**Status**: ✅ Ready for deployment with proper configuration
**Last Updated**: [Current Date]
**Next Review**: [Add review schedule] 