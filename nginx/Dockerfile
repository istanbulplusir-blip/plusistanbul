FROM nginx:alpine

# Install openssl for certificate generation
RUN apk add --no-cache openssl

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Generate self-signed certificate for development
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create log directories
RUN mkdir -p /var/log/nginx

# Expose ports
EXPOSE 80 443

# Health check (use HTTPS to avoid 301 from HTTP redirect)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider --no-check-certificate https://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 