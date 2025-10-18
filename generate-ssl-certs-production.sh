#!/bin/bash

# SSL Certificate Generation Script for Production
# This script generates SSL certificates for peykantravelistanbul.com

set -e

echo "🔐 Generating SSL certificates for peykantravelistanbul.com..."

# Create SSL directory if it doesn't exist
mkdir -p nginx/ssl

# Check if we're using Let's Encrypt or self-signed
if [ "$1" = "letsencrypt" ]; then
    echo "📜 Using Let's Encrypt for SSL certificates..."
    
    # Install certbot if not available
    if ! command -v certbot &> /dev/null; then
        echo "Installing certbot..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update
            sudo apt-get install -y certbot
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install certbot
        else
            echo "Please install certbot manually for your OS"
            exit 1
        fi
    fi
    
    # Generate Let's Encrypt certificate
    sudo certbot certonly --standalone \
        -d peykantravelistanbul.com \
        -d www.peykantravelistanbul.com \
        --email admin@peykantravelistanbul.com \
        --agree-tos \
        --non-interactive
    
    # Copy certificates to nginx directory
    sudo cp /etc/letsencrypt/live/peykantravelistanbul.com/fullchain.pem nginx/ssl/cert.pem
    sudo cp /etc/letsencrypt/live/peykantravelistanbul.com/privkey.pem nginx/ssl/key.pem
    sudo chown $USER:$USER nginx/ssl/cert.pem nginx/ssl/key.pem
    
    echo "✅ Let's Encrypt certificates generated successfully!"
    
else
    echo "🔧 Generating self-signed certificates for development/testing..."
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/OU=IT Department/CN=peykantravelistanbul.com" \
        -addext "subjectAltName=DNS:peykantravelistanbul.com,DNS:www.peykantravelistanbul.com"
    
    echo "✅ Self-signed certificates generated successfully!"
    echo "⚠️  WARNING: Self-signed certificates are not trusted by browsers!"
    echo "   Use Let's Encrypt for production: ./generate-ssl-certs-production.sh letsencrypt"
fi

echo "📁 SSL certificates are now available in nginx/ssl/"
echo "🔒 Certificate: nginx/ssl/cert.pem"
echo "🔑 Private Key: nginx/ssl/key.pem"

# Set proper permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem

echo "🎉 SSL setup complete!"
