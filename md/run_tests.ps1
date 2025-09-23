# PowerShell script to run tests for Tour Booking System
# Run this script from the project root directory

Write-Host "🚀 Tour Booking System - Test Runner" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "frontend" -PathType Container) -or -not (Test-Path "backend" -PathType Container)) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Function to run command and capture output
function Run-Command {
    param(
        [string]$Command,
        [string]$WorkingDirectory = ".",
        [string]$Description = ""
    )
    
    Write-Host "`n🔧 $Description" -ForegroundColor Yellow
    Write-Host "Running: $Command" -ForegroundColor Gray
    
    try {
        $result = Invoke-Expression "cd '$WorkingDirectory'; $Command" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Success" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ Failed with exit code: $LASTEXITCODE" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test results tracking
$testResults = @()

# 1. Frontend Type Check
$testResults += @{
    Name    = "Frontend Type Check"
    Success = (Run-Command "npm run type-check" "frontend" "Checking TypeScript types")
}

# 2. Frontend Build
$testResults += @{
    Name    = "Frontend Build"
    Success = (Run-Command "npm run build" "frontend" "Building frontend for production")
}

# 3. Backend Check
$testResults += @{
    Name    = "Backend Check"
    Success = (Run-Command "python manage.py check" "backend" "Checking Django configuration")
}

# 4. Backend Migrations
$testResults += @{
    Name    = "Backend Migrations"
    Success = (Run-Command "python manage.py makemigrations --dry-run" "backend" "Checking for pending migrations")
}

# 5. Quick API Test (if backend is running)
Write-Host "`n🧪 Testing API Endpoints..." -ForegroundColor Yellow
try {
    $apiTest = python quick_test.py
    $testResults += @{
        Name    = "API Endpoints Test"
        Success = $apiTest
    }
}
catch {
    Write-Host "⚠️  API test skipped (backend might not be running)" -ForegroundColor Yellow
    $testResults += @{
        Name    = "API Endpoints Test"
        Success = $false
    }
}

# Summary
Write-Host "`n📊 Test Results Summary:" -ForegroundColor Green
Write-Host "=" * 30 -ForegroundColor Green

$passedTests = 0
$totalTests = $testResults.Count

foreach ($result in $testResults) {
    $status = if ($result.Success) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($result.Success) { "Green" } else { "Red" }
    Write-Host "$status $($result.Name)" -ForegroundColor $color
    if ($result.Success) { $passedTests++ }
}

Write-Host "`nTotal Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $($totalTests - $passedTests)" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($passedTests / $totalTests) * 100, 1))%" -ForegroundColor White

# Final recommendation
if ($passedTests -eq $totalTests) {
    Write-Host "`n🎉 All tests passed! System is ready for manual testing." -ForegroundColor Green
    Write-Host "📖 Please refer to manual_test_guide.md for manual testing scenarios." -ForegroundColor Cyan
}
else {
    Write-Host "`n⚠️  Some tests failed. Please fix the issues before proceeding to manual testing." -ForegroundColor Yellow
}

# Instructions for manual testing
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start the backend server: cd backend && python manage.py runserver" -ForegroundColor White
Write-Host "2. Start the frontend server: cd frontend && npm run dev" -ForegroundColor White
Write-Host "3. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "4. Follow the manual testing guide in manual_test_guide.md" -ForegroundColor White

exit $(if ($passedTests -eq $totalTests) { 0 } else { 1 })
