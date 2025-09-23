# Script to improve production environment security
Write-Host "Improving production environment security..." -ForegroundColor Blue

# Function to generate secure random strings
function Generate-SecureKey {
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
    $random = ""
    for ($i = 0; $i -lt 64; $i++) {
        $random += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $random
}

# Read current environment file
$envContent = Get-Content "backend\.env.production" -Raw

# Generate secure keys
$secureSecretKey = Generate-SecureKey
$secureJwtKey = Generate-SecureKey

# Replace insecure keys
$envContent = $envContent -replace "SECRET_KEY=django-insecure-peykan-tourism-prod-2024", "SECRET_KEY=$secureSecretKey"
$envContent = $envContent -replace "JWT_SECRET_KEY=jwt-secret-key-change-this", "JWT_SECRET_KEY=$secureJwtKey"

# Prompt for missing API keys
Write-Host ""
Write-Host "Please provide the missing API keys:" -ForegroundColor Yellow

# Kavenegar API Key
$kavenegarKey = Read-Host "Enter KAVENEGAR_API_KEY (SMS service)" -AsSecureString
if ($kavenegarKey.Length -gt 0) {
    $kavenegarPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($kavenegarKey))
    $envContent = $envContent -replace "KAVENEGAR_API_KEY=", "KAVENEGAR_API_KEY=$kavenegarPlain"
}

# Payment Secret Key
$paymentKey = Read-Host "Enter PAYMENT_SECRET_KEY (Stripe secret key starting with sk_)" -AsSecureString
if ($paymentKey.Length -gt 0) {
    $paymentPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($paymentKey))
    $envContent = $envContent -replace "PAYMENT_SECRET_KEY=", "PAYMENT_SECRET_KEY=$paymentPlain"
}

# Update DEFAULT_FROM_EMAIL to match EMAIL_HOST_USER
$envContent = $envContent -replace "DEFAULT_FROM_EMAIL=noreply@peykantravelistanbul.com", "DEFAULT_FROM_EMAIL=peykantravels@gmail.com"

# Write updated content
$envContent | Out-File -FilePath "backend\.env.production" -Encoding UTF8

Write-Host ""
Write-Host "✅ Security improvements completed!" -ForegroundColor Green
Write-Host "✅ Generated secure SECRET_KEY and JWT_SECRET_KEY" -ForegroundColor Green
Write-Host "✅ Updated DEFAULT_FROM_EMAIL" -ForegroundColor Green
Write-Host ""
Write-Host "Current configuration:" -ForegroundColor Blue
Write-Host "- Email: peykantravels@gmail.com" -ForegroundColor White
Write-Host "- Domain: peykantravelistanbul.com" -ForegroundColor White
Write-Host "- Database: PostgreSQL" -ForegroundColor White
Write-Host "- Security: HTTPS, HSTS, Secure Cookies enabled" -ForegroundColor White
Write-Host ""
Write-Host "Ready for deployment!" -ForegroundColor Green 