# Database Reset Script for Windows PowerShell
Write-Host "🗑️  Resetting Database - Peykan Tourism Platform" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend")) {
    Write-Host "[ERROR] Please run this script from the project root directory!" -ForegroundColor Red
    exit 1
}

Set-Location backend

Write-Host "[INFO] Step 1: Stopping all services..." -ForegroundColor Blue
docker-compose -f ../docker-compose.production-secure.yml down 2>$null

Write-Host "[INFO] Step 2: Removing database volumes..." -ForegroundColor Blue
$volumes = docker volume ls -q | Where-Object { $_ -match "postgres|redis" }
foreach ($volume in $volumes) {
    docker volume rm $volume 2>$null
}

Write-Host "[INFO] Step 3: Cleaning up migration files..." -ForegroundColor Blue

# Remove all migration files except __init__.py
Get-ChildItem -Recurse -Path . -Filter "*.py" | Where-Object {
    $_.Directory.Name -eq "migrations" -and $_.Name -ne "__init__.py"
} | Remove-Item -Force

# Remove Python cache files
Get-ChildItem -Recurse -Path . -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Path . -Filter "*.pyc" | Remove-Item -Force

Write-Host "[INFO] Step 4: Removing database files..." -ForegroundColor Blue
Remove-Item -Path "db.sqlite3" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*.db" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*.sqlite" -Force -ErrorAction SilentlyContinue

Write-Host "[INFO] Step 5: Creating fresh migrations..." -ForegroundColor Blue
python manage.py makemigrations

Write-Host "[INFO] Step 6: Starting database services..." -ForegroundColor Blue
Set-Location ..
docker-compose -f docker-compose.production-secure.yml up -d postgres redis

Write-Host "[INFO] Waiting for database to be ready..." -ForegroundColor Blue
Start-Sleep -Seconds 15

Set-Location backend

Write-Host "[INFO] Step 7: Running migrations..." -ForegroundColor Blue
python manage.py migrate

Write-Host "[INFO] Step 8: Collecting static files..." -ForegroundColor Blue
python manage.py collectstatic --noinput

Write-Host "✅ Database reset completed successfully!" -ForegroundColor Green

Write-Host "[INFO] Next steps:" -ForegroundColor Blue
Write-Host "1. Start all services: docker-compose -f ../docker-compose.production-secure.yml up -d"
Write-Host "2. Check logs: docker-compose -f ../docker-compose.production-secure.yml logs"
Write-Host "3. Test the application"

Write-Host "[WARNING] Important notes:" -ForegroundColor Yellow
Write-Host "- All data has been permanently deleted"
Write-Host "- You may need to recreate test data"
Write-Host "- Check your models for any issues"

Set-Location ..
