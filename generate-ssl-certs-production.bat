@echo off
REM SSL Certificate Generation Script for Production (Windows)
REM This script generates SSL certificates for peykantravelistanbul.com

echo 🔐 Generating SSL certificates for peykantravelistanbul.com...

REM Create SSL directory if it doesn't exist
if not exist "nginx\ssl" mkdir nginx\ssl

REM Check if we're using Let's Encrypt or self-signed
if "%1"=="letsencrypt" (
    echo 📜 Using Let's Encrypt for SSL certificates...
    
    REM Check if certbot is available
    certbot --version >nul 2>&1
    if errorlevel 1 (
        echo Installing certbot...
        echo Please install certbot manually from https://certbot.eff.org/
        echo Or use WSL with the Linux version of this script
        pause
        exit /b 1
    )
    
    REM Generate Let's Encrypt certificate
    certbot certonly --standalone ^
        -d peykantravelistanbul.com ^
        -d www.peykantravelistanbul.com ^
        --email admin@peykantravelistanbul.com ^
        --agree-tos ^
        --non-interactive
    
    REM Copy certificates to nginx directory
    copy "C:\Certbot\live\peykantravelistanbul.com\fullchain.pem" "nginx\ssl\cert.pem"
    copy "C:\Certbot\live\peykantravelistanbul.com\privkey.pem" "nginx\ssl\key.pem"
    
    echo ✅ Let's Encrypt certificates generated successfully!
    
) else (
    echo 🔧 Generating self-signed certificates for development/testing...
    
    REM Generate self-signed certificate using OpenSSL
    REM Note: You need OpenSSL installed on Windows
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 ^
        -keyout nginx\ssl\key.pem ^
        -out nginx\ssl\cert.pem ^
        -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/OU=IT Department/CN=peykantravelistanbul.com" ^
        -addext "subjectAltName=DNS:peykantravelistanbul.com,DNS:www.peykantravelistanbul.com"
    
    echo ✅ Self-signed certificates generated successfully!
    echo ⚠️  WARNING: Self-signed certificates are not trusted by browsers!
    echo    Use Let's Encrypt for production: generate-ssl-certs-production.bat letsencrypt
)

echo 📁 SSL certificates are now available in nginx\ssl\
echo 🔒 Certificate: nginx\ssl\cert.pem
echo 🔑 Private Key: nginx\ssl\key.pem

echo 🎉 SSL setup complete!
pause
