#!/bin/bash

# Peykan Tourism - Server Backup and Local Development Setup
# This script creates a complete backup of the current server state
# and sets up a new Git branch for local development

set -e  # Exit on any error

echo "🚀 Starting Peykan Tourism Server Backup and Local Development Setup"
echo "================================================================"

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="server_backup_${TIMESTAMP}"
NEW_BRANCH_NAME="server-snapshot-${TIMESTAMP}"
GIT_REMOTE="origin"

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

# Step 1: Check current Git status
print_status "Checking current Git status..."
if [ -n "$(git status --porcelain)" ]; then
    print_warning "There are uncommitted changes in the working directory:"
    git status --short
    echo ""
    read -p "Do you want to commit these changes before creating backup? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Committing current changes..."
        git add .
        git commit -m "Auto-commit before server backup - $(date)"
        print_success "Changes committed successfully"
    else
        print_warning "Proceeding without committing changes"
    fi
fi

# Step 2: Create backup directory
print_status "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Step 3: Create complete backup of current state
print_status "Creating complete backup of current server state..."

# Backup all project files (excluding .git, node_modules, etc.)
print_status "Backing up project files..."
rsync -av --exclude='.git' \
         --exclude='node_modules' \
         --exclude='venv' \
         --exclude='__pycache__' \
         --exclude='*.pyc' \
         --exclude='.DS_Store' \
         --exclude='*.log' \
         --exclude='server_backup_*' \
         ./ "$BACKUP_DIR/"

# Backup specific important directories
print_status "Backing up backend media files..."
if [ -d "backend/media" ]; then
    mkdir -p "$BACKUP_DIR/backend_media"
    rsync -av backend/media/ "$BACKUP_DIR/backend_media/"
fi

print_status "Backing up backend static files..."
if [ -d "backend/static" ]; then
    mkdir -p "$BACKUP_DIR/backend_static"
    rsync -av backend/static/ "$BACKUP_DIR/backend_static/"
fi

print_status "Backing up frontend build files..."
if [ -d "frontend/.next" ]; then
    mkdir -p "$BACKUP_DIR/frontend_build"
    rsync -av frontend/.next/ "$BACKUP_DIR/frontend_build/"
fi

# Step 4: Create backup metadata
print_status "Creating backup metadata..."
cat > "$BACKUP_DIR/backup_metadata.txt" << EOF
Peykan Tourism Server Backup
============================
Backup Date: $(date)
Git Commit: $(git rev-parse HEAD)
Git Branch: $(git branch --show-current)
Git Status: $(git status --porcelain | wc -l) uncommitted changes

Server Information:
- OS: $(uname -a)
- Current Directory: $(pwd)
- User: $(whoami)

Backup Contents:
- Complete project files (excluding .git, node_modules, venv)
- Backend media files (if exists)
- Backend static files (if exists)
- Frontend build files (if exists)

Instructions for Restoration:
1. Extract this backup to a clean directory
2. Run: git init
3. Run: git remote add origin <your-repo-url>
4. Run: git fetch origin
5. Run: git checkout -b server-snapshot-${TIMESTAMP}
6. Restore any additional server-specific configurations
EOF

# Step 5: Create compressed backup
print_status "Creating compressed backup archive..."
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
print_success "Compressed backup created: ${BACKUP_DIR}.tar.gz"

# Step 6: Create new Git branch from current state
print_status "Creating new Git branch: $NEW_BRANCH_NAME"
git checkout -b "$NEW_BRANCH_NAME"
print_success "New branch created: $NEW_BRANCH_NAME"

# Step 7: Commit current state to new branch
print_status "Committing current state to new branch..."
git add .
git commit -m "Server snapshot backup - $(date)

This commit represents the exact state of the server at $(date).
Includes all current changes, configurations, and server-specific modifications.

Backup timestamp: ${TIMESTAMP}
Branch: ${NEW_BRANCH_NAME}"

print_success "Current state committed to new branch"

# Step 8: Push new branch to remote
print_status "Pushing new branch to remote repository..."
git push -u "$GIT_REMOTE" "$NEW_BRANCH_NAME"
print_success "New branch pushed to remote: $NEW_BRANCH_NAME"

# Step 9: Create local development setup script
print_status "Creating local development setup script..."
cat > "setup_local_development.sh" << 'EOF'
#!/bin/bash

# Local Development Setup Script for Peykan Tourism
# Generated from server backup

set -e

echo "🚀 Setting up local development environment..."
echo "=============================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if we're on the correct branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "server-snapshot-"* ]]; then
    echo "⚠️  Warning: You're not on a server-snapshot branch"
    echo "Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Backend setup
print_status "Setting up backend environment..."

if [ ! -d "backend/venv" ]; then
    print_status "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

print_status "Activating virtual environment and installing dependencies..."
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Frontend setup
print_status "Setting up frontend environment..."
cd frontend
npm install
cd ..

# Database setup
print_status "Setting up database..."
cd backend
source venv/bin/activate

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from example..."
    cp env.example .env
    print_warning "Please edit backend/.env with your local database settings"
fi

# Run migrations
print_status "Running database migrations..."
python manage.py migrate

# Create superuser if needed
read -p "Do you want to create a superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

cd ..

print_success "Local development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your local database settings"
echo "2. Start backend: cd backend && source venv/bin/activate && python manage.py runserver"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Access admin panel: http://localhost:8000/admin"
echo "5. Access frontend: http://localhost:3000"
EOF

chmod +x setup_local_development.sh
print_success "Local development setup script created: setup_local_development.sh"

# Step 10: Create summary report
print_status "Creating backup summary report..."
cat > "BACKUP_SUMMARY_${TIMESTAMP}.md" << EOF
# Peykan Tourism Server Backup Summary

**Backup Date:** $(date)  
**Backup Timestamp:** ${TIMESTAMP}  
**Git Branch:** ${NEW_BRANCH_NAME}  
**Git Commit:** $(git rev-parse HEAD)

## What was backed up:

### 1. Complete Project Files
- All source code (excluding .git, node_modules, venv)
- Configuration files
- Documentation
- Deployment scripts

### 2. Server-Specific Files
- Backend media files (user uploads, images)
- Backend static files (collected static assets)
- Frontend build files (if present)

### 3. Git State
- New branch created: \`${NEW_BRANCH_NAME}\`
- All current changes committed
- Branch pushed to remote repository

## Backup Files Created:

1. **\`${BACKUP_DIR}/\`** - Complete backup directory
2. **\`${BACKUP_DIR}.tar.gz\`** - Compressed backup archive
3. **\`setup_local_development.sh\`** - Local development setup script
4. **\`BACKUP_SUMMARY_${TIMESTAMP}.md\`** - This summary file

## How to use this backup:

### For Emergency Recovery:
\`\`\`bash
# Extract the backup
tar -xzf ${BACKUP_DIR}.tar.gz

# Restore to a clean directory
cp -r ${BACKUP_DIR}/* /path/to/restore/location/
\`\`\`

### For Local Development:
\`\`\`bash
# Switch to the backup branch
git checkout ${NEW_BRANCH_NAME}

# Run the setup script
./setup_local_development.sh
\`\`\`

### For Server Deployment:
\`\`\`bash
# The new branch contains the exact server state
# You can deploy this branch to any server
git checkout ${NEW_BRANCH_NAME}
# Run your deployment scripts
\`\`\`

## Important Notes:

- This backup represents the **exact state** of the server at $(date)
- All uncommitted changes have been preserved in the new branch
- The backup includes server-specific configurations and files
- Use \`setup_local_development.sh\` for easy local environment setup

## Next Steps:

1. **Test the backup** by setting up a local environment
2. **Verify all functionality** works as expected
3. **Continue development** on the new branch
4. **Keep the backup files** in a safe location

---
*Backup created by Peykan Tourism Backup Script*
EOF

print_success "Backup summary report created: BACKUP_SUMMARY_${TIMESTAMP}.md"

# Step 11: Final summary
echo ""
echo "🎉 Backup and Local Development Setup Complete!"
echo "=============================================="
echo ""
echo "📁 Backup Files Created:"
echo "  • ${BACKUP_DIR}/ (complete backup directory)"
echo "  • ${BACKUP_DIR}.tar.gz (compressed backup)"
echo "  • setup_local_development.sh (local setup script)"
echo "  • BACKUP_SUMMARY_${TIMESTAMP}.md (summary report)"
echo ""
echo "🌿 Git Branch Created:"
echo "  • Branch: ${NEW_BRANCH_NAME}"
echo "  • Status: Pushed to remote repository"
echo "  • Contains: Exact server state at $(date)"
echo ""
echo "🚀 Next Steps:"
echo "  1. Test the backup: ./setup_local_development.sh"
echo "  2. Continue development on branch: ${NEW_BRANCH_NAME}"
echo "  3. Keep backup files in a safe location"
echo ""
echo "✅ Backup completed successfully!" 