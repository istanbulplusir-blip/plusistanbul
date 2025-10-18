#!/bin/bash

echo "========================================"
echo "Creating Sample Event with 3 Languages"
echo "========================================"
echo ""

cd backend

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Running create_sample_event command..."
python manage.py create_sample_event

echo ""
echo "========================================"
echo "Done!"
echo "========================================"
echo ""
echo "You can now access the event at:"
echo "- Admin Panel: http://localhost:8000/admin/events/event/"
echo "- API: http://localhost:8000/api/events/istanbul-music-festival-2025/"
echo ""
echo "To change language, use Accept-Language header:"
echo "- Persian: fa"
echo "- English: en"
echo "- Arabic: ar"
echo ""
echo "Example:"
echo "curl -H \"Accept-Language: fa\" http://localhost:8000/api/events/istanbul-music-festival-2025/"
echo ""
