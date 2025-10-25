#!/bin/bash

echo "========================================="
echo "Fixing Hero Images and Media URLs"
echo "========================================="

# Navigate to backend directory
cd /home/djangouser/plusistanbul/backend

# Create placeholder images
echo "1. Creating placeholder images..."
python3 create_placeholders.py

# Run migrations
echo "2. Running migrations..."
python3 manage.py migrate shared

# Create sample hero slider if needed
echo "3. Creating sample hero slider..."
python3 create_sample_hero.py

# Collect static files
echo "4. Collecting static files..."
python3 manage.py collectstatic --noinput

echo ""
echo "========================================="
echo "Fix Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Restart Docker containers: docker-compose restart"
echo "2. Check admin panel: https://peykantravelistanbul.com/admin/"
echo "3. Upload images and videos for hero sliders"
echo ""
