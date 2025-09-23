#!/bin/bash

# Peykan Tourism Development Environment Setup Script
# اسکریپت راه‌اندازی خودکار محیط توسعه

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Git is installed
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    print_success "Git is installed"
}

# Setup environment files
setup_env_files() {
    print_status "Setting up environment files..."
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        cp backend/env.example backend/.env
        print_success "Created backend/.env from env.example"
    else
        print_warning "backend/.env already exists, skipping..."
    fi
    
    # Frontend environment
    if [ ! -f "frontend/.env.local" ]; then
        cp frontend/.env.example frontend/.env.local
        print_success "Created frontend/.env.local from .env.example"
    else
        print_warning "frontend/.env.local already exists, skipping..."
    fi
}

# Build and start Docker services
start_services() {
    print_status "Building and starting Docker services..."
    
    # Build images
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    print_success "Docker services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    until docker-compose exec -T postgres pg_isready -U peykan_user -d peykan; do
        sleep 2
    done
    print_success "PostgreSQL is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    print_success "Redis is ready"
    
    # Wait for backend
    print_status "Waiting for backend..."
    until curl -f http://localhost:8000/api/v1/health/ > /dev/null 2>&1; do
        sleep 5
    done
    print_success "Backend is ready"
    
    # Wait for frontend
    print_status "Waiting for frontend..."
    until curl -f http://localhost:3000 > /dev/null 2>&1; do
        sleep 5
    done
    print_success "Frontend is ready"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    docker-compose exec backend python manage.py migrate
    print_success "Database migrations completed"
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    docker-compose exec backend python manage.py collectstatic --noinput
    print_success "Static files collected"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."
    echo "Please enter superuser credentials:"
    docker-compose exec backend python manage.py createsuperuser
    print_success "Superuser created"
}

# Show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_success "Development environment is ready!"
    echo ""
    echo "Services:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    echo "Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop services: docker-compose down"
    echo "  - Restart services: docker-compose restart"
    echo ""
}

# Main setup function
main() {
    echo "🚀 Peykan Tourism Development Environment Setup"
    echo "================================================"
    echo ""
    
    # Check prerequisites
    check_docker
    check_git
    
    # Setup environment files
    setup_env_files
    
    # Start services
    start_services
    
    # Wait for services
    wait_for_services
    
    # Setup database
    run_migrations
    collect_static
    
    # Create superuser (optional)
    read -p "Do you want to create a superuser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    # Show final status
    show_status
}

# Run main function
main "$@" 