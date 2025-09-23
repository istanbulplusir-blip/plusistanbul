# 🚀 Production Deployment Guide - Peykan Tourism Platform

## Overview

This guide provides complete instructions for deploying the Peykan Tourism Platform to a Hetzner Ubuntu server with full production configuration including SSL certificates, security hardening, and automated maintenance.

## 📋 Prerequisites

### Server Requirements
- **Ubuntu 20.04 LTS or 22.04 LTS**
- **Minimum 2GB RAM** (4GB recommended)
- **20GB free disk space** (50GB recommended)
- **Root access** or sudo privileges
- **Static IP address**

### Domain Requirements
- **Domain name** pointing to your server
- **DNS records** configured:
  ```
  A    your-domain.com     → Server IP
  A    www.your-domain.com → Server IP
  ```

### Git Repository
- **Code pushed** to GitHub/GitLab
- **Repository accessible** from server

## 🛠️ Quick Deployment

### Step 1: Prepare Your Server

1. **Connect to your server:**
   ```bash
   ssh root@your-server-ip
   ```

2. **Upload the deployment script:**
   ```bash
   # From your local machine
   scp deploy-production.sh root@your-server-ip:/root/
   ```

3. **Make script executable:**
   ```bash
   chmod +x /root/deploy-production.sh
   ```

### Step 2: Configure the Script

Edit the deployment script with your details:

```bash
nano /root/deploy-production.sh
```

Update these lines:
```bash
DOMAIN_NAME="your-domain.com"  # Your actual domain
GIT_REPO_URL="https://github.com/yourusername/peykan-tourism.git"  # Your repo URL
```

### Step 3: Run Deployment

```bash
sudo /root/deploy-production.sh
```

**The script will automatically:**
- ✅ Install Docker and Docker Compose
- ✅ Install Nginx and Certbot
- ✅ Configure UFW firewall
- ✅ Clone your repository
- ✅ Build and deploy the application
- ✅ Configure SSL certificates
- ✅ Set up auto-renewal

### Step 4: Configure Environment Variables

After deployment, configure your environment:

```bash
cd /opt/peykan-tourism
chmod +x setup-env.sh
./setup-env.sh
```

## 📁 File Structure

```
/opt/peykan-tourism/
├── backend/                 # Django application
│   ├── .env                # Environment variables
│   ├── Dockerfile          # Backend container
│   └── peykan/
│       ├── settings.py     # Development settings
│       └── settings_production.py  # Production settings
├── frontend/               # Next.js application
│   ├── Dockerfile          # Frontend container
│   └── next.config.js      # Next.js configuration
├── nginx/                  # Nginx configuration
│   ├── Dockerfile          # Nginx container
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Docker services
├── deploy-production.sh    # Deployment script
├── setup-env.sh           # Environment setup
└── DEPLOYMENT.md          # Detailed deployment guide
```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://peykan_user:password@postgres:5432/peykan

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway
PAYMENT_SECRET_KEY=your-stripe-secret-key

# SMS
KAVENEGAR_API_KEY=your-kavenegar-api-key
```

### SSL Certificates

SSL certificates are automatically obtained and renewed:
- **Provider**: Let's Encrypt
- **Auto-renewal**: Twice daily via cron
- **Domains**: `your-domain.com` and `www.your-domain.com`

## 🚀 Services

### Application Services
- **Backend**: Django API on port 8000
- **Frontend**: Next.js on port 3000
- **Database**: PostgreSQL on port 5432
- **Cache**: Redis on port 6379

### Infrastructure Services
- **Nginx**: Reverse proxy on ports 80/443
- **Docker**: Container orchestration
- **UFW**: Firewall management

## 🔒 Security Features

### Network Security
- ✅ UFW firewall configured
- ✅ Only SSH, HTTP, HTTPS ports open
- ✅ Rate limiting on API endpoints
- ✅ DDoS protection via Nginx

### Application Security
- ✅ CSRF protection enabled
- ✅ XSS protection headers
- ✅ Content Security Policy
- ✅ HSTS enabled
- ✅ Secure cookies
- ✅ Input validation

### Container Security
- ✅ Non-root users
- ✅ Minimal base images
- ✅ Health checks
- ✅ Resource limits

## 📊 Monitoring

### Health Checks
```bash
# Check application health
curl https://your-domain.com/health

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Resource Monitoring
```bash
# Monitor Docker resources
docker stats

# Check disk usage
df -h

# Monitor memory usage
free -h
```

## 🔄 Maintenance

### Regular Tasks

#### Daily
```bash
# Check service health
docker-compose ps

# Monitor logs
docker-compose logs --tail=100
```

#### Weekly
```bash
# Update system packages
apt update && apt upgrade -y

# Clean Docker images
docker system prune -a
```

#### Monthly
```bash
# Renew SSL certificates (automatic)
certbot renew

# Backup database
docker-compose exec postgres pg_dump -U peykan_user peykan > backup.sql
```

### Backup Strategy

#### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U peykan_user peykan > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U peykan_user peykan < backup_file.sql
```

#### Application Backup
```bash
# Backup entire project
tar -czf peykan-backup-$(date +%Y%m%d).tar.gz /opt/peykan-tourism/

# Restore project
tar -xzf peykan-backup-file.tar.gz -C /
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs service_name

# Restart service
docker-compose restart service_name

# Rebuild service
docker-compose build service_name
```

#### SSL Certificate Issues
```bash
# Check certificate status
certbot certificates

# Manual renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal
```

#### Database Issues
```bash
# Check database connection
docker-compose exec postgres pg_isready -U peykan_user

# Reset database
docker-compose exec backend python manage.py flush
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor slow queries
docker-compose exec postgres psql -U peykan_user -d peykan -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### Log Locations
```bash
# Application logs
docker-compose logs -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -u docker
journalctl -u nginx
```

## 📞 Support

### Getting Help

1. **Check logs** for error messages
2. **Verify configuration** files
3. **Test connectivity** to services
4. **Review security** settings

### Useful Commands

```bash
# Service management
docker-compose up -d          # Start services
docker-compose down           # Stop services
docker-compose restart        # Restart services
docker-compose logs -f        # View logs

# Database management
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic

# SSL management
certbot certificates          # List certificates
certbot renew                 # Renew certificates
certbot delete --cert-name domain.com  # Delete certificate

# System management
ufw status                    # Check firewall
systemctl status nginx        # Check Nginx
systemctl status docker       # Check Docker
```

## 🎯 Success Criteria

After successful deployment:

- [ ] **Application accessible** at `https://your-domain.com`
- [ ] **SSL certificate** valid and working
- [ ] **All Docker containers** running
- [ ] **Database migrations** completed
- [ ] **Admin panel** accessible
- [ ] **API endpoints** responding
- [ ] **Firewall** properly configured
- [ ] **SSL auto-renewal** scheduled

## 📈 Performance Optimization

### Docker Optimization
- Multi-stage builds for smaller images
- Non-root users for security
- Health checks for reliability
- Resource limits for stability

### Nginx Optimization
- Gzip compression enabled
- Static file caching
- Rate limiting configured
- Security headers implemented

### Database Optimization
- Connection pooling
- Query optimization
- Regular maintenance
- Automated backups

---

## 🚀 Ready to Deploy?

1. **Review prerequisites** ✅
2. **Configure domain** ✅
3. **Prepare Git repository** ✅
4. **Run deployment script** 🚀
5. **Configure environment** ⚙️
6. **Test application** 🧪

**Estimated deployment time**: 15-20 minutes

---

*This deployment guide ensures a secure, scalable, and maintainable production environment for your Peykan Tourism Platform.* 