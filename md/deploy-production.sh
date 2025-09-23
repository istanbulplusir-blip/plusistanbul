#!/bin/bash

# Peykan Tourism Platform - Production Deployment Script
# For Hetzner Ubuntu Server
# 
# This script will:
# 1. Install Docker and Docker Compose
# 2. Install Nginx
# 3. Install Certbot for SSL certificates
# 4. Configure UFW firewall
# 5. Set up the project and deploy
# 6. Configure SSL certificates
# 7. Set up auto-renewal

set -e  # Exit on any error

# Configuration Variables
DOMAIN_NAME="your-domain.com"  # Replace with your actual domain
GIT_REPO_URL="https://github.com/yourusername/peykan-tourism.git"  # Replace with your repo URL
PROJECT_DIR="/opt/peykan-tourism"
NGINX_SITE_CONFIG="/etc/nginx/sites-available/peykan-tourism"
NGINX_SITE_ENABLED="/etc/nginx/sites-enabled/peykan-tourism"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Update system
update_system() {
    log "Updating system packages..."
    apt update && apt upgrade -y
    log "System updated successfully"
}

# Install Docker
install_docker() {
    log "Installing Docker..."
    
    # Remove old versions
    apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Install prerequisites
    apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    # Add current user to docker group
    usermod -aG docker $SUDO_USER
    
    log "Docker installed successfully"
}

# Install Docker Compose
install_docker_compose() {
    log "Installing Docker Compose..."
    
    # Install Docker Compose v2 (included with Docker)
    ln -sf /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose
    
    # Verify installation
    docker-compose --version
    log "Docker Compose installed successfully"
}

# Install Nginx
install_nginx() {
    log "Installing Nginx..."
    apt install -y nginx
    
    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx
    
    log "Nginx installed successfully"
}

# Install Certbot
install_certbot() {
    log "Installing Certbot..."
    
    # Install Certbot and Nginx plugin
    apt install -y certbot python3-certbot-nginx
    
    log "Certbot installed successfully"
}

# Configure UFW firewall
configure_firewall() {
    log "Configuring UFW firewall..."
    
    # Reset UFW
    ufw --force reset
    
    # Set default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH
    ufw allow ssh
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Enable UFW
    ufw --force enable
    
    log "Firewall configured successfully"
}

# Create project directories
create_directories() {
    log "Creating project directories..."
    
    mkdir -p $PROJECT_DIR
    mkdir -p /var/log/peykan-tourism
    mkdir -p /etc/nginx/ssl
    
    # Set proper permissions
    chown -R $SUDO_USER:$SUDO_USER $PROJECT_DIR
    chmod -R 755 $PROJECT_DIR
    
    log "Directories created successfully"
}

# Clone repository
clone_repository() {
    log "Cloning Git repository..."
    
    cd $PROJECT_DIR
    
    # Check if directory is already a git repository
    if [ -d ".git" ]; then
        warn "Git repository already exists, pulling latest changes..."
        git pull origin main
    else
        git clone $GIT_REPO_URL .
    fi
    
    # Set proper ownership
    chown -R $SUDO_USER:$SUDO_USER $PROJECT_DIR
    
    log "Repository cloned successfully"
}

# Create production environment file
setup_environment() {
    log "Setting up environment configuration..."
    
    cd $PROJECT_DIR
    
    # Copy production environment template
    if [ -f "backend/env.production" ]; then
        cp backend/env.production backend/.env
        log "Production environment template copied"
        warn "Please edit backend/.env with your actual values before continuing"
    else
        error "Production environment template not found"
    fi
}

# Build and start Docker containers
deploy_application() {
    log "Building and deploying application..."
    
    cd $PROJECT_DIR
    
    # Build images
    log "Building Docker images..."
    docker-compose build
    
    # Start services (without nginx profile for now)
    log "Starting application services..."
    docker-compose up -d postgres redis backend frontend
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Run database migrations
    log "Running database migrations..."
    docker-compose exec -T backend python manage.py migrate
    
    # Create superuser if needed
    log "Creating superuser..."
    docker-compose exec -T backend python manage.py createsuperuser --noinput || true
    
    # Collect static files
    log "Collecting static files..."
    docker-compose exec -T backend python manage.py collectstatic --noinput
    
    log "Application deployed successfully"
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    # Create Nginx configuration
    cat > $NGINX_SITE_CONFIG << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # Redirect all HTTP traffic to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # SSL configuration will be added by Certbot
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'self';" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;
    
    # API routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Admin routes
    location /admin/ {
        limit_req zone=api burst=10 nodelay;
        
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
    
    # Static files (Django)
    location /static/ {
        proxy_pass http://localhost:8000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files (Django)
    location /media/ {
        proxy_pass http://localhost:8000;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Frontend routes
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    # Enable the site
    ln -sf $NGINX_SITE_CONFIG $NGINX_SITE_ENABLED
    
    # Test Nginx configuration
    nginx -t
    
    # Reload Nginx
    systemctl reload nginx
    
    log "Nginx configured successfully"
}

# Obtain SSL certificates
obtain_ssl_certificates() {
    log "Obtaining SSL certificates..."
    
    # Stop Nginx temporarily
    systemctl stop nginx
    
    # Obtain certificates
    certbot certonly --standalone \
        --email admin@$DOMAIN_NAME \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN_NAME \
        -d www.$DOMAIN_NAME
    
    # Start Nginx again
    systemctl start nginx
    
    log "SSL certificates obtained successfully"
}

# Configure SSL auto-renewal
setup_ssl_renewal() {
    log "Setting up SSL certificate auto-renewal..."
    
    # Create renewal script
    cat > /usr/local/bin/renew-ssl.sh << 'EOF'
#!/bin/bash
certbot renew --quiet --post-hook "systemctl reload nginx"
EOF
    
    chmod +x /usr/local/bin/renew-ssl.sh
    
    # Add to crontab (run twice daily)
    (crontab -l 2>/dev/null; echo "0 2,14 * * * /usr/local/bin/renew-ssl.sh") | crontab -
    
    log "SSL auto-renewal configured successfully"
}

# Final configuration
final_setup() {
    log "Performing final configuration..."
    
    # Reload Nginx with SSL configuration
    systemctl reload nginx
    
    # Test the application
    log "Testing application..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        log "All services are running successfully"
    else
        warn "Some services may not be running properly"
    fi
    
    log "Deployment completed successfully!"
}

# Main execution
main() {
    log "Starting production deployment for Peykan Tourism Platform..."
    log "Domain: $DOMAIN_NAME"
    log "Project directory: $PROJECT_DIR"
    
    # Check if running as root
    check_root
    
    # Execute deployment steps
    update_system
    install_docker
    install_docker_compose
    install_nginx
    install_certbot
    configure_firewall
    create_directories
    clone_repository
    setup_environment
    deploy_application
    configure_nginx
    obtain_ssl_certificates
    setup_ssl_renewal
    final_setup
    
    log "Production deployment completed successfully!"
    
    # Display final instructions
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  DEPLOYMENT COMPLETED SUCCESSFULLY!  ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Edit environment variables: nano $PROJECT_DIR/backend/.env"
    echo "2. Restart services: cd $PROJECT_DIR && docker-compose restart"
    echo "3. Test your application: https://$DOMAIN_NAME"
    echo "4. Create admin user: cd $PROJECT_DIR && docker-compose exec backend python manage.py createsuperuser"
    echo ""
    echo -e "${YELLOW}Important URLs:${NC}"
    echo "- Application: https://$DOMAIN_NAME"
    echo "- Admin Panel: https://$DOMAIN_NAME/admin/"
    echo "- API Documentation: https://$DOMAIN_NAME/api/v1/schema/"
    echo ""
    echo -e "${YELLOW}Monitoring Commands:${NC}"
    echo "- View logs: cd $PROJECT_DIR && docker-compose logs -f"
    echo "- Check status: cd $PROJECT_DIR && docker-compose ps"
    echo "- Monitor resources: docker stats"
    echo ""
    echo -e "${YELLOW}SSL Certificate Renewal:${NC}"
    echo "- Auto-renewal is configured via cron"
    echo "- Manual renewal: certbot renew"
    echo ""
    echo -e "${GREEN}Your Peykan Tourism Platform is now live!${NC}"
}

# Run main function
main "$@" 