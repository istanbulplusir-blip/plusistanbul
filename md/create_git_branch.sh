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
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we can write to Git
if ! git status >/dev/null 2>&1; then
    print_error "Git repository is not accessible or has permission issues"
    print_warning "Please fix Git permissions before running this script"
    exit 1
fi

# Create new branch
print_status "Creating new branch: server-snapshot-20250725_142708"
git checkout -b "server-snapshot-20250725_142708"

# Add all files
print_status "Adding all files to Git..."
git add .

# Commit
print_status "Committing current state..."
git commit -m "Server snapshot backup - Fri Jul 25 02:27:12 PM UTC 2025

This commit represents the exact state of the server at Fri Jul 25 02:27:12 PM UTC 2025.
Includes all current changes, configurations, and server-specific modifications.

Backup timestamp: 20250725_142708
Branch: server-snapshot-20250725_142708"

# Push to remote
print_status "Pushing to remote repository..."
git push -u origin "server-snapshot-20250725_142708"

print_success "Git branch created and pushed successfully!"
print_success "Branch: server-snapshot-20250725_142708"
