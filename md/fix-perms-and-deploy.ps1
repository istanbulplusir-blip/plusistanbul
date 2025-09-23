# PowerShell script to fix logs directory permissions and redeploy containers
# This script addresses the issue where the logs directory has incorrect ownership

Write-Host "=== Starting permission fix and deployment process ===" -ForegroundColor Green

# Navigate to project directory (adjust path as needed)
Write-Host "1. Navigating to project directory..." -ForegroundColor Yellow
Set-Location "C:\Users\shaha\Desktop\c\Pey3v\Pey3v-Before currency"

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.production.yml")) {
    Write-Host "Error: docker-compose.production.yml not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

Write-Host "2. Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml down

Write-Host "3. Removing logs directory to fix permissions..." -ForegroundColor Yellow
# Remove the logs directory so it gets recreated with correct permissions
if (Test-Path "backend\logs") {
    Remove-Item -Recurse -Force "backend\logs"
    Write-Host "Logs directory removed successfully." -ForegroundColor Green
}

Write-Host "4. Starting containers with fresh logs directory..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml up -d

Write-Host "5. Waiting for containers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "6. Checking container status..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml ps

Write-Host "7. Following backend logs..." -ForegroundColor Yellow
Write-Host "=== Backend Logs ===" -ForegroundColor Cyan
Start-Job -ScriptBlock { docker-compose -f docker-compose.production.yml logs -f backend }

Write-Host "8. Following nginx logs..." -ForegroundColor Yellow
Write-Host "=== Nginx Logs ===" -ForegroundColor Cyan
Start-Job -ScriptBlock { docker-compose -f docker-compose.production.yml logs -f nginx }

Write-Host "=== Deployment completed ===" -ForegroundColor Green
Write-Host "The logs directory has been recreated with correct permissions." -ForegroundColor Green
Write-Host "Backend should now be able to write to logs without PermissionError." -ForegroundColor Green
Write-Host ""
Write-Host "To check container status: docker-compose -f docker-compose.production.yml ps" -ForegroundColor White
Write-Host "To view logs: docker-compose -f docker-compose.production.yml logs -f [service_name]" -ForegroundColor White

# Show running jobs
Write-Host "`nLog monitoring jobs are running. To stop them:" -ForegroundColor Yellow
Write-Host "Get-Job | Stop-Job" -ForegroundColor White 