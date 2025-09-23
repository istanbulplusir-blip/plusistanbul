# Peykan Tourism Platform - Production Deployment Script (PowerShell)
# This script should be run when SSH access is restored

param(
    [string]$ServerIP = "185.27.134.10",
    [string]$ServerUser = "root"
)

Write-Host "🚀 Starting Peykan Tourism Platform Deployment..." -ForegroundColor Green

# Function to test SSH connection
function Test-SSHConnection {
    param([string]$IP, [string]$User)
    
    try {
        $result = ssh -o ConnectTimeout=10 -o BatchMode=yes "${User}@${IP}" "echo 'SSH connection successful'" 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Check SSH connection
Write-Host "Checking SSH connection..." -ForegroundColor Yellow
if (-not (Test-SSHConnection -IP $ServerIP -User $ServerUser)) {
    Write-Host "❌ SSH connection failed. Please ensure SSH service is running on the server." -ForegroundColor Red
    Write-Host "⚠️  You may need to restart SSH service through your server control panel." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ SSH connection successful!" -ForegroundColor Green

# Deployment commands
$deploymentCommands = @"
set -e

echo "📁 Navigating to project directory..."
cd /opt/peykan-tourism

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

echo "🐳 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down

echo "🔨 Building new images..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "🚀 Starting services..."
docker-compose -f docker-compose.production.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "📊 Checking service status..."
docker-compose -f docker-compose.production.yml ps

echo "📋 Checking logs for any errors..."
echo "=== Backend Logs ==="
docker-compose -f docker-compose.production.yml logs --tail=20 backend

echo "=== Frontend Logs ==="
docker-compose -f docker-compose.production.yml logs --tail=20 frontend

echo "✅ Deployment completed successfully!"
echo "🌐 Your site should be available at: https://peykantravelistanbul.com"
"@

Write-Host "Connecting to server and deploying..." -ForegroundColor Yellow

# Execute deployment commands
ssh "${ServerUser}@${ServerIP}" $deploymentCommands

Write-Host "✅ Deployment script completed!" -ForegroundColor Green
Write-Host "Check the output above for any errors." -ForegroundColor Yellow
Write-Host "If everything looks good, your site should be live at: https://peykantravelistanbul.com" -ForegroundColor Green 