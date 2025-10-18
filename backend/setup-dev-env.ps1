# PowerShell script to set up development environment for Peykan Tourism Platform

Write-Host "Setting up development environment for Peykan Tourism Platform..." -ForegroundColor Green

# Copy development environment file to .env
if (-not (Test-Path ".env")) {
    Copy-Item "env.development" ".env"
    Write-Host "Created .env file from env.development" -ForegroundColor Yellow
}
else {
    Write-Host ".env file already exists" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "CORS Configuration:" -ForegroundColor Cyan
Write-Host "- Allowed Origins: http://localhost:3000, http://localhost:3001, http://localhost:3002" -ForegroundColor White
Write-Host "- Also includes: http://127.0.0.1:3000, http://127.0.0.1:3001, http://127.0.0.1:3002" -ForegroundColor White
Write-Host ""
Write-Host "You can now run the Django development server on any of these ports:" -ForegroundColor Cyan
Write-Host "- Port 3000 (default frontend)" -ForegroundColor White
Write-Host "- Port 3001 (alternative frontend instance)" -ForegroundColor White
Write-Host "- Port 3002 (alternative frontend instance)" -ForegroundColor White
Write-Host ""
Write-Host "To start the development server:" -ForegroundColor Green
Write-Host "python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "To start with a specific port:" -ForegroundColor Green
Write-Host "python manage.py runserver 8000" -ForegroundColor White
Write-Host ""
Write-Host "Setup complete! Press any key to continue..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
