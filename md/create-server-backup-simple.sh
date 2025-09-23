#!/bin/bash

# Peykan Tourism - Simple Server Backup Script
# This script creates a complete backup of the current server state
# without requiring Git commits (to avoid permission issues)

set -e  # Exit on any error

echo "🚀 Starting Peykan Tourism Server Backup (Simple Version)"
echo "========================================================"

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="server_backup_${TIMESTAMP}"
NEW_BRANCH_NAME="server-snapshot-${TIMESTAMP}"

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

# Step 1: Check current Git status (informational only)
print_status "Checking current Git status..."
if [ -n "$(git status --porcelain)" ]; then
    print_warning "There are uncommitted changes in the working directory:"
    git status --short
    echo ""
    print_warning "These changes will be included in the backup but not committed to Git"
else
    print_success "Working directory is clean"
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
         --exclude='BACKUP_SUMMARY_*' \
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
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "Unknown")
Git Branch: $(git branch --show-current 2>/dev/null || echo "Unknown")
Git Status: $(git status --porcelain 2>/dev/null | wc -l) uncommitted changes

Server Information:
- OS: $(uname -a)
- Current Directory: $(pwd)
- User: $(whoami)

Backup Contents:
- Complete project files (excluding .git, node_modules, venv)
- Backend media files (if exists)
- Backend static files (if exists)
- Frontend build files (if exists)
- All uncommitted changes

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

# Step 6: Create local development setup script
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
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

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

# Step 7: Create Git branch creation script
print_status "Creating Git branch creation script..."
cat > "create_git_branch.sh" << EOF
#!/bin/bash

# Script to create Git branch from backup
# Run this after fixing Git permissions

set -e

echo "🌿 Creating Git branch from backup..."
echo "===================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "\${BLUE}[INFO]\${NC} \$1"
}

print_success() {
    echo -e "\${GREEN}[SUCCESS]\${NC} \$1"
}

print_warning() {
    echo -e "\${YELLOW}[WARNING]\${NC} \$1"
}

# Check if we can write to Git
if ! git status >/dev/null 2>&1; then
    print_error "Git repository is not accessible or has permission issues"
    print_warning "Please fix Git permissions before running this script"
    exit 1
fi

# Create new branch
print_status "Creating new branch: ${NEW_BRANCH_NAME}"
git checkout -b "${NEW_BRANCH_NAME}"

# Add all files
print_status "Adding all files to Git..."
git add .

# Commit
print_status "Committing current state..."
git commit -m "Server snapshot backup - $(date)

This commit represents the exact state of the server at $(date).
Includes all current changes, configurations, and server-specific modifications.

Backup timestamp: ${TIMESTAMP}
Branch: ${NEW_BRANCH_NAME}"

# Push to remote
print_status "Pushing to remote repository..."
git push -u origin "${NEW_BRANCH_NAME}"

print_success "Git branch created and pushed successfully!"
print_success "Branch: ${NEW_BRANCH_NAME}"
EOF

chmod +x create_git_branch.sh
print_success "Git branch creation script created: create_git_branch.sh"

# Step 8: Create summary report
print_status "Creating backup summary report..."
cat > "BACKUP_SUMMARY_${TIMESTAMP}.md" << EOF
# Peykan Tourism Server Backup Summary

**Backup Date:** $(date)  
**Backup Timestamp:** ${TIMESTAMP}  
**Git Commit:** $(git rev-parse HEAD 2>/dev/null || echo "Unknown")  
**Git Branch:** $(git branch --show-current 2>/dev/null || echo "Unknown")

## What was backed up:

### 1. Complete Project Files
- All source code (excluding .git, node_modules, venv)
- Configuration files
- Documentation
- Deployment scripts
- **All uncommitted changes**

### 2. Server-Specific Files
- Backend media files (user uploads, images)
- Backend static files (collected static assets)
- Frontend build files (if present)

### 3. Backup Files Created
- **\`${BACKUP_DIR}/\`** - Complete backup directory
- **\`${BACKUP_DIR}.tar.gz\`** - Compressed backup archive
- **\`setup_local_development.sh\`** - Local development setup script
- **\`create_git_branch.sh\`** - Git branch creation script
- **\`BACKUP_SUMMARY_${TIMESTAMP}.md\`** - This summary file

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
# Run the setup script
./setup_local_development.sh
\`\`\`

### For Git Branch Creation (after fixing permissions):
\`\`\`bash
# Fix Git permissions first, then run:
./create_git_branch.sh
\`\`\`

## Important Notes:

- This backup represents the **exact state** of the server at $(date)
- **All uncommitted changes have been preserved** in the backup
- The backup includes server-specific configurations and files
- Git branch creation was skipped due to permission issues
- Use \`setup_local_development.sh\` for easy local environment setup

## Next Steps:

1. **Test the backup** by setting up a local environment
2. **Fix Git permissions** if needed
3. **Create Git branch** using \`create_git_branch.sh\`
4. **Verify all functionality** works as expected
5. **Continue development** on the new branch
6. **Keep the backup files** in a safe location

## Git Permission Issues:

The backup detected Git permission issues. To fix them:

1. Check ownership of .git directory: \`ls -la .git/\`
2. Fix permissions: \`sudo chown -R djangouser:djangouser .git/\`
3. Run the Git branch creation script: \`./create_git_branch.sh\`

---
*Backup created by Peykan Tourism Backup Script*
EOF

print_success "Backup summary report created: BACKUP_SUMMARY_${TIMESTAMP}.md"

# Step 9: Final summary
echo ""
echo "🎉 Server Backup Complete!"
echo "========================="
echo ""
echo "📁 Backup Files Created:"
echo "  • ${BACKUP_DIR}/ (complete backup directory)"
echo "  • ${BACKUP_DIR}.tar.gz (compressed backup)"
echo "  • setup_local_development.sh (local setup script)"
echo "  • create_git_branch.sh (Git branch creation script)"
echo "  • BACKUP_SUMMARY_${TIMESTAMP}.md (summary report)"
echo ""
echo "⚠️  Git Branch Creation:"
echo "  • Skipped due to permission issues"
echo "  • Run: ./create_git_branch.sh (after fixing permissions)"
echo ""
echo "🚀 Next Steps:"
echo "  1. Test the backup: ./setup_local_development.sh"
echo "  2. Fix Git permissions if needed"
echo "  3. Create Git branch: ./create_git_branch.sh"
echo "  4. Keep backup files in a safe location"
echo ""
echo "✅ Backup completed successfully!" 