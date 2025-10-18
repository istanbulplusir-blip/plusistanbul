#!/bin/bash

echo "🚀 Starting backend package updates..."

# Update backend packages only
echo "📦 Updating backend packages..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install/update requirements
echo "Installing backend requirements..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements.dev.txt

echo "✅ Backend packages updated successfully!"

echo "🎉 Backend update completed!"
echo ""
echo "Next steps:"
echo "1. Test the backend to ensure everything works"
echo "2. Run migrations if needed: python manage.py migrate"
echo "3. Start the backend server: python manage.py runserver"
