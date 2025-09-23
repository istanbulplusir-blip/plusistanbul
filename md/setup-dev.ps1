# Peykan Tourism Development Environment Setup Script (PowerShell)
# اسکریپت راه‌اندازی خودکار محیط توسعه برای ویندوز

param(
    [switch]$SkipSuperuser,
    [switch]$Force
)

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is installed
function Test-Docker {
    try {
        $dockerVersion = docker --version
        $dockerComposeVersion = docker-compose --version
        Write-Success "Docker and Docker Compose are installed"
        Write-Host "  $dockerVersion" -ForegroundColor Gray
        Write-Host "  $dockerComposeVersion" -ForegroundColor Gray
        return $true
    }
    catch {
        Write-Error "Docker is not installed or not in PATH. Please install Docker Desktop first."
        return $false
    }
}

# Check if Git is installed
function Test-Git {
    try {
        $gitVersion = git --version
        Write-Success "Git is installed: $gitVersion"
        return $true
    }
    catch {
        Write-Error "Git is not installed. Please install Git first."
        return $false
    }
}

# Setup environment files
function Setup-EnvironmentFiles {
    Write-Status "Setting up environment files..."
    
    # Backend environment
    if (-not (Test-Path "backend\.env")) {
        if (Test-Path "backend\env.example") {
            Copy-Item "backend\env.example" "backend\.env"
            Write-Success "Created backend\.env from env.example"
        } else {
            Write-Error "backend\env.example not found"
            return $false
        }
    } else {
        Write-Warning "backend\.env already exists, skipping..."
    }
    
    # Frontend environment
    if (-not (Test-Path "frontend\.env.local")) {
        if (Test-Path "frontend\.env.example") {
            Copy-Item "frontend\.env.example" "frontend\.env.local"
            Write-Success "Created frontend\.env.local from .env.example"
        } else {
            # Create default frontend environment file
            @"
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NODE_ENV=development
"@ | Out-File -FilePath "frontend\.env.local" -Encoding UTF8
            Write-Success "Created frontend\.env.local with default settings"
        }
    } else {
        Write-Warning "frontend\.env.local already exists, skipping..."
    }
    
    return $true
}

# Build and start Docker services
function Start-DockerServices {
    Write-Status "Building and starting Docker services..."
    
    try {
        # Build images
        docker-compose build
        
        # Start services
        docker-compose up -d
        
        Write-Success "Docker services started successfully"
        return $true
    }
    catch {
        Write-Error "Failed to start Docker services: $($_.Exception.Message)"
        return $false
    }
}

# Wait for services to be ready
function Wait-ForServices {
    Write-Status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    Write-Status "Waiting for PostgreSQL..."
    $maxAttempts = 30
    $attempt = 0
    do {
        $attempt++
        try {
            $result = docker-compose exec -T postgres pg_isready -U peykan_user -d peykan 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "PostgreSQL is ready"
                break
            }
        }
        catch {
            # Ignore errors during startup
        }
        Start-Sleep -Seconds 2
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        Write-Warning "PostgreSQL may not be fully ready, continuing..."
    }
    
    # Wait for Redis
    Write-Status "Waiting for Redis..."
    $attempt = 0
    do {
        $attempt++
        try {
            $result = docker-compose exec -T redis redis-cli ping 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Redis is ready"
                break
            }
        }
        catch {
            # Ignore errors during startup
        }
        Start-Sleep -Seconds 2
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        Write-Warning "Redis may not be fully ready, continuing..."
    }
    
    # Wait for backend
    Write-Status "Waiting for backend..."
    $attempt = 0
    do {
        $attempt++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health/" -UseBasicParsing -TimeoutSec 5 2>$null
            if ($response.StatusCode -eq 200) {
                Write-Success "Backend is ready"
                break
            }
        }
        catch {
            # Ignore errors during startup
        }
        Start-Sleep -Seconds 5
    } while ($attempt -lt 12)
    
    if ($attempt -eq 12) {
        Write-Warning "Backend may not be fully ready, continuing..."
    }
    
    # Wait for frontend
    Write-Status "Waiting for frontend..."
    $attempt = 0
    do {
        $attempt++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5 2>$null
            if ($response.StatusCode -eq 200) {
                Write-Success "Frontend is ready"
                break
            }
        }
        catch {
            # Ignore errors during startup
        }
        Start-Sleep -Seconds 5
    } while ($attempt -lt 12)
    
    if ($attempt -eq 12) {
        Write-Warning "Frontend may not be fully ready, continuing..."
    }
}

# Run database migrations
function Invoke-Migrations {
    Write-Status "Running database migrations..."
    try {
        docker-compose exec backend python manage.py migrate
        Write-Success "Database migrations completed"
        return $true
    }
    catch {
        Write-Error "Failed to run migrations: $($_.Exception.Message)"
        return $false
    }
}

# Collect static files
function Invoke-CollectStatic {
    Write-Status "Collecting static files..."
    try {
        docker-compose exec backend python manage.py collectstatic --noinput
        Write-Success "Static files collected"
        return $true
    }
    catch {
        Write-Error "Failed to collect static files: $($_.Exception.Message)"
        return $false
    }
}

# Create superuser
function New-Superuser {
    Write-Status "Creating superuser..."
    try {
        docker-compose exec backend python manage.py createsuperuser
        Write-Success "Superuser created"
        return $true
    }
    catch {
        Write-Error "Failed to create superuser: $($_.Exception.Message)"
        return $false
    }
}

# Show service status
function Show-ServiceStatus {
    Write-Status "Service Status:"
    docker-compose ps
    
    Write-Host ""
    Write-Success "Development environment is ready!"
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Cyan
    Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  - PostgreSQL: localhost:5432" -ForegroundColor White
    Write-Host "  - Redis: localhost:6379" -ForegroundColor White
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Cyan
    Write-Host "  - View logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "  - Stop services: docker-compose down" -ForegroundColor White
    Write-Host "  - Restart services: docker-compose restart" -ForegroundColor White
    Write-Host ""
}

# Main setup function
function Start-DevelopmentSetup {
    Write-Host "🚀 Peykan Tourism Development Environment Setup" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check prerequisites
    if (-not (Test-Docker)) {
        exit 1
    }
    
    if (-not (Test-Git)) {
        exit 1
    }
    
    # Setup environment files
    if (-not (Setup-EnvironmentFiles)) {
        exit 1
    }
    
    # Start services
    if (-not (Start-DockerServices)) {
        exit 1
    }
    
    # Wait for services
    Wait-ForServices
    
    # Setup database
    if (-not (Invoke-Migrations)) {
        Write-Warning "Migrations failed, but continuing..."
    }
    
    if (-not (Invoke-CollectStatic)) {
        Write-Warning "Static collection failed, but continuing..."
    }
    
    # Create superuser (optional)
    if (-not $SkipSuperuser) {
        $createSuperuser = Read-Host "Do you want to create a superuser? (y/n)"
        if ($createSuperuser -eq 'y' -or $createSuperuser -eq 'Y') {
            New-Superuser
        }
    }
    
    # Show final status
    Show-ServiceStatus
}

# Run main function
Start-DevelopmentSetup 