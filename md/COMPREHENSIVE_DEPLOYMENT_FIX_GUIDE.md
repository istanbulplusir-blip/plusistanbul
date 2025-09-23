# Comprehensive Deployment Fix Guide

## Issues Identified

1. **Backend Logging Error**: Django can't configure file handler for logs
2. **Frontend Connection Error**: Frontend trying to connect to `::1:8000` instead of backend service
3. **Missing Health Check**: Docker health check endpoint doesn't exist

## Solutions Implemented

### 1. Backend Logging Fix
- Modified `backend/peykan/settings_production.py` to ensure logs directory exists
- Added proper file handler configuration with append mode
- Directory creation happens before logging configuration

### 2. Frontend API Proxy Fix
- Updated `frontend/next.config.js` to use environment-aware API URLs
- Production: `http://backend:8000` (Docker service name)
- Development: `http://localhost:8000` (Local development)

### 3. Health Check Endpoint
- Added health check endpoint at `/api/v1/health/` in `backend/peykan/urls.py`
- Docker health check can now properly verify backend status

## Deployment Steps

### Step 1: Upload Updated Files to Server

```bash
# Upload the updated files to your server
scp backend/peykan/settings_production.py djangouser@your-server:/home/djangouser/peykan-tourism/backend/peykan/
scp frontend/next.config.js djangouser@your-server:/home/djangouser/peykan-tourism/frontend/
scp backend/peykan/urls.py djangouser@your-server:/home/djangouser/peykan-tourism/backend/peykan/
scp fix-perms-and-deploy.sh djangouser@your-server:/home/djangouser/peykan-tourism/
```

### Step 2: Run the Deployment Script

```bash
# SSH into your server
ssh djangouser@your-server

# Navigate to project directory
cd /home/djangouser/peykan-tourism

# Make script executable
chmod +x fix-perms-and-deploy.sh

# Run the deployment script
sudo ./fix-perms-and-deploy.sh
```

### Step 3: Manual Verification (if needed)

If you prefer to run the steps manually:

```bash
# 1. Stop containers
docker-compose -f docker-compose.production.yml down

# 2. Remove logs directory
rm -rf logs

# 3. Rebuild frontend with new config
docker-compose -f docker-compose.production.yml build frontend

# 4. Start containers
docker-compose -f docker-compose.production.yml up -d

# 5. Wait for initialization
sleep 15

# 6. Check status
docker-compose -f docker-compose.production.yml ps
```

## Expected Results

After deployment, you should see:

### ✅ Backend Container
- Status: `Up (healthy)`
- No more `ValueError: Unable to configure handler 'file'`
- Health check passes: `curl http://localhost:8000/api/v1/health/`

### ✅ Frontend Container
- Status: `Up (healthy)`
- No more `ECONNREFUSED ::1:8000` errors
- Can successfully proxy API requests to backend

### ✅ Nginx Container
- Status: `Up (healthy)`
- Properly routing requests to frontend and backend

## Verification Commands

```bash
# Check all container statuses
docker-compose -f docker-compose.production.yml ps

# Test backend health
curl http://localhost:8000/api/v1/health/

# Check backend logs
docker-compose -f docker-compose.production.yml logs --tail=20 backend

# Check frontend logs
docker-compose -f docker-compose.production.yml logs --tail=20 frontend

# Check nginx logs
docker-compose -f docker-compose.production.yml logs --tail=20 nginx

# Test frontend-backend communication
curl http://localhost:3000/api/v1/health/
```

## Troubleshooting

### If Backend Still Fails

1. **Check logs directory permissions:**
   ```bash
   ls -la logs/
   ```

2. **Verify Django user in container:**
   ```bash
   docker-compose -f docker-compose.production.yml exec backend id
   ```

3. **Check if logs directory exists in container:**
   ```bash
   docker-compose -f docker-compose.production.yml exec backend ls -la /app/logs/
   ```

### If Frontend Still Can't Connect

1. **Check if backend service is reachable:**
   ```bash
   docker-compose -f docker-compose.production.yml exec frontend curl http://backend:8000/api/v1/health/
   ```

2. **Verify network connectivity:**
   ```bash
   docker network ls
   docker network inspect peykan_network
   ```

### If Nginx Fails

1. **Check SSL certificates:**
   ```bash
   ls -la nginx/ssl/
   ```

2. **Generate self-signed certificates if needed:**
   ```bash
   mkdir -p nginx/ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/nginx.key \
     -out nginx/ssl/nginx.crt
   ```

## File Changes Summary

### Modified Files:
1. `backend/peykan/settings_production.py` - Fixed logging configuration
2. `frontend/next.config.js` - Updated API proxy configuration
3. `backend/peykan/urls.py` - Added health check endpoint
4. `fix-perms-and-deploy.sh` - Enhanced deployment script

### Key Changes:
- **Logging**: Ensures logs directory exists before configuring handlers
- **API Proxy**: Uses Docker service names in production environment
- **Health Check**: Provides endpoint for Docker health monitoring
- **Deployment**: Comprehensive script that handles all issues

## Success Indicators

When everything is working correctly:

1. **All containers show `(healthy)` status**
2. **Backend logs show successful startup without permission errors**
3. **Frontend logs show successful API connections**
4. **Health check endpoint returns 200 OK**
5. **Application is accessible via nginx**

## Next Steps

After successful deployment:

1. **Monitor logs** for any remaining issues
2. **Test all major functionality** (auth, tours, cart, etc.)
3. **Set up SSL certificates** for production domain
4. **Configure monitoring and alerting**
5. **Set up automated backups**

This comprehensive fix addresses all the identified issues and should result in a fully functional deployment. 