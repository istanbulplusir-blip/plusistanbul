#!/bin/bash

# Generate secure passwords and secrets for production

echo "🔐 Generating secure secrets for production..."

# Generate strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Generate Django secret key (50 characters)
SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)

# Generate JWT secret key (different from Django secret)
JWT_SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)

echo "Generated secrets:"
echo "=================="
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
echo ""
echo "⚠️  IMPORTANT: Save these secrets securely!"
echo "⚠️  Add them to your .env.production file"
echo "⚠️  Never commit these to version control!"
