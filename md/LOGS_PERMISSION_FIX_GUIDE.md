# Logs Permission Fix and Deployment Guide

## Problem Description
The backend service is failing because the `logs` directory on the host has root ownership, preventing the Django user inside the container from writing to it. This happens because the entire `/app` directory is mounted from the host to the container.

## Solution
We need to remove the existing `logs` directory and let the container recreate it with the correct permissions.

## Deployment Steps

### Option 1: Using the Bash Script (Recommended for Linux/Production Server)

1. **Upload the script to your server:**
   ```bash
   # Copy fix-perms-and-deploy.sh to your server
   scp fix-perms-and-deploy.sh djangouser@your-server:/home/djangouser/peykan-tourism/
   ```

2. **Make the script executable:**
   ```bash
   chmod +x fix-perms-and-deploy.sh
   ```

3. **Run the script:**
   ```bash
   sudo ./fix-perms-and-deploy.sh
   ```

### Option 2: Manual Steps

1. **SSH into your server:**
   ```bash
   ssh djangouser@your-server
   ```

2. **Navigate to project directory:**
   ```bash
   cd /home/djangouser/peykan-tourism
   ```

3. **Stop existing containers:**
   ```bash
   docker-compose -f docker-compose.production.yml down
   ```

4. **Remove the logs directory:**
   ```bash
   rm -rf logs
   ```

5. **Start containers:**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

6. **Check container status:**
   ```bash
   docker-compose -f docker-compose.production.yml ps
   ```

7. **Monitor logs:**
   ```bash
   # Backend logs
   docker-compose -f docker-compose.production.yml logs -f backend
   
   # Nginx logs
   docker-compose -f docker-compose.production.yml logs -f nginx
   ```

### Option 3: Local Testing (Windows)

If you want to test locally before deploying:

1. **Run the PowerShell script:**
   ```powershell
   .\fix-perms-and-deploy.ps1
   ```

## What the Script Does

1. **Stops all containers** to ensure clean state
2. **Removes the logs directory** that has incorrect permissions
3. **Starts containers** which recreates the logs directory with correct ownership
4. **Monitors logs** to ensure everything is working properly

## Expected Results

After running the script:
- ✅ Backend container should start without PermissionError
- ✅ Health checks should pass
- ✅ Nginx should start properly
- ✅ Application should be accessible

## Troubleshooting

### If containers still fail to start:

1. **Check container logs:**
   ```bash
   docker-compose -f docker-compose.production.yml logs backend
   ```

2. **Verify logs directory permissions:**
   ```bash
   ls -la logs/
   ```

3. **Check if Django user exists in container:**
   ```bash
   docker-compose -f docker-compose.production.yml exec backend id
   ```

### If SSL certificate issues persist:

The script fixes the logs permission issue, but if you still have SSL certificate problems:

1. **Check if SSL certificates exist:**
   ```bash
   ls -la nginx/ssl/
   ```

2. **Generate self-signed certificates for testing:**
   ```bash
   mkdir -p nginx/ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/nginx.key \
     -out nginx/ssl/nginx.crt
   ```

## Verification Commands

After deployment, verify everything is working:

```bash
# Check container status
docker-compose -f docker-compose.production.yml ps

# Check backend health
curl http://localhost:8000/health/

# Check nginx status
curl -k https://localhost/

# View real-time logs
docker-compose -f docker-compose.production.yml logs -f
```

## Notes

- The script removes the existing logs directory completely. If you need to preserve logs, backup them first.
- The container will recreate the logs directory with the correct ownership (django user).
- This fix addresses the root cause of the permission issue by ensuring the logs directory is created by the container itself. 