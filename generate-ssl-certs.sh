#!/bin/bash

# Generate SSL certificates for development
# This script creates self-signed certificates for local development

echo "Generating SSL certificates for development..."

# Create SSL directory if it doesn't exist
mkdir -p nginx/ssl

# Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/OU=IT Department/CN=localhost"

# Set proper permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem

echo "SSL certificates generated successfully!"
echo "Certificate: nginx/ssl/cert.pem"
echo "Private Key: nginx/ssl/key.pem"
echo ""
echo "Note: These are self-signed certificates for development only."
echo "For production, use certificates from a trusted CA."
