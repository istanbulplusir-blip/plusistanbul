#!/usr/bin/env python
"""
Simple test for hero slides API.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider
from shared.serializers import HeroSliderSerializer
from django.test import RequestFactory

def test_api():
    """Test API response."""
    print("=== Testing Hero Slides API Response ===")

    factory = RequestFactory()
    request = factory.get('/api/v1/shared/hero-slides/active/', HTTP_HOST='localhost:8000')
    request.user = type('AnonymousUser', (), {'is_authenticated': False})()

    slides = HeroSlider.objects.filter(is_active=True).order_by('order')
    print(f'Found {len(slides)} active slides')

    for slide in slides:
        serializer = HeroSliderSerializer(slide, context={'request': request})
        data = serializer.data
        print(f'\nSlide: {data["title"]}')
        print(f'  Desktop URL: {data.get("desktop_image_url", "None")}')
        print(f'  Order: {data.get("order", "N/A")}')

if __name__ == '__main__':
    test_api()
