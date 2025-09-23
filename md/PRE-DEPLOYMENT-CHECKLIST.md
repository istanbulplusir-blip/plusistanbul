# Pre-Deployment Checklist - Hetzner Ubuntu Server

## 🚀 Before Running the Deployment Script

### 1. Server Requirements ✅
- [ ] **Ubuntu 20.04 LTS or 22.04 LTS** server
- [ ] **Minimum 2GB RAM** (4GB recommended)
- [ ] **20GB free disk space** (50GB recommended)
- [ ] **Root access** or sudo privileges
- [ ] **Static IP address** assigned

### 2. Domain Configuration ✅
- [ ] **Domain name purchased** and active
- [ ] **DNS records configured**:
  - A record: `your-domain.com` → Server IP
  - A record: `www.your-domain.com` → Server IP
  - CNAME record: `www` → `your-domain.com` (optional)
- [ ] **DNS propagation** completed (can take up to 48 hours)

### 3. Git Repository Setup ✅
- [ ] **Repository created** on GitHub/GitLab
- [ ] **Code pushed** to repository
- [ ] **Repository is public** or access tokens configured
- [ ] **Main branch** contains all production code

### 4. Environment Variables ✅
- [ ] **Email credentials** ready (Gmail app password)
- [ ] **Payment gateway keys** (Stripe, PayPal, etc.)
- [ ] **SMS API keys** (Kavenegar, Twilio, etc.)
- [ ] **Database credentials** (if using external database)
- [ ] **Secret keys** generated for Django

### 5. SSL Certificate Requirements ✅
- [ ] **Domain points to server** (DNS propagation complete)
- [ ] **Port 80 and 443** accessible from internet
- [ ] **Valid email address** for certificate notifications

## 🔧 Script Configuration

### Edit the Deployment Script

Before running the script, edit these variables in `deploy-production.sh`:

```bash
# Line 15-16: Update with your actual values
DOMAIN_NAME="your-domain.com"  # Replace with your actual domain
GIT_REPO_URL="https://github.com/yourusername/peykan-tourism.git"  # Replace with your repo URL
```

### Example Configuration:
```bash
DOMAIN_NAME="peykan-tourism.com"
GIT_REPO_URL="https://github.com/yourusername/peykan-tourism.git"
```

## 📋 Deployment Steps

### Step 1: Upload Script to Server
```bash
# On your local machine, upload the script
scp deploy-production.sh root@your-server-ip:/root/

# Or use SFTP to upload the file
```

### Step 2: Connect to Server
```bash
# SSH into your server
ssh root@your-server-ip
```

### Step 3: Make Script Executable
```bash
# Make the script executable
chmod +x /root/deploy-production.sh
```

### Step 4: Run Deployment Script
```bash
# Run the deployment script
sudo /root/deploy-production.sh
```

## ⚠️ Important Notes

### During Deployment
- **Don't interrupt** the script execution
- **Keep SSH connection** active
- **Monitor output** for any errors
- **Script will take 10-15 minutes** to complete

### After Deployment
- **Edit environment variables** before testing
- **Create admin user** for Django admin
- **Test all functionality** thoroughly
- **Monitor logs** for any issues

## 🔒 Security Considerations

### Before Deployment
- [ ] **Change default SSH port** (optional but recommended)
- [ ] **Set up SSH key authentication**
- [ ] **Disable root login** (after deployment)
- [ ] **Configure fail2ban** (after deployment)

### After Deployment
- [ ] **Update all passwords** and API keys
- [ ] **Review firewall rules**
- [ ] **Set up monitoring** and alerting
- [ ] **Configure backups**

## 🚨 Troubleshooting

### Common Issues

#### DNS Issues
```bash
# Check DNS propagation
nslookup your-domain.com
dig your-domain.com

# Test from different locations
curl -I http://your-domain.com
```

#### SSL Certificate Issues
```bash
# Check certificate status
certbot certificates

# Manual renewal
certbot renew --dry-run
```

#### Docker Issues
```bash
# Check Docker status
systemctl status docker

# View container logs
docker-compose logs -f
```

#### Nginx Issues
```bash
# Check Nginx configuration
nginx -t

# View Nginx logs
tail -f /var/log/nginx/error.log
```

## 📞 Support

### If Script Fails
1. **Check the error message** in the output
2. **Review logs** for specific issues
3. **Verify prerequisites** are met
4. **Check internet connectivity** on server
5. **Ensure sufficient disk space**

### Manual Recovery
```bash
# Stop all services
docker-compose down

# Remove containers and images
docker-compose down --rmi all

# Clean up and restart
docker system prune -a
```

## 🎯 Success Criteria

After successful deployment, you should have:

- [ ] **Application accessible** at `https://your-domain.com`
- [ ] **SSL certificate** valid and working
- [ ] **All Docker containers** running
- [ ] **Database migrations** completed
- [ ] **Static files** collected
- [ ] **Admin panel** accessible
- [ ] **API endpoints** responding
- [ ] **Firewall** properly configured
- [ ] **SSL auto-renewal** scheduled

## 📊 Post-Deployment Checklist

### Immediate Actions
- [ ] **Test application functionality**
- [ ] **Create admin user**
- [ ] **Configure email settings**
- [ ] **Test payment integration**
- [ ] **Verify SSL certificate**

### Ongoing Maintenance
- [ ] **Set up monitoring**
- [ ] **Configure backups**
- [ ] **Set up log rotation**
- [ ] **Monitor resource usage**
- [ ] **Regular security updates**

---

**Ready to Deploy?** ✅
**Estimated Time**: 15-20 minutes
**Risk Level**: Low (automated script with error handling)

---

*This checklist ensures a smooth deployment process. Follow each step carefully and verify completion before proceeding to the next.* 