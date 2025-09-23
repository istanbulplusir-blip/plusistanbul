#!/usr/bin/env python
"""
Test hero slides API.
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.views import HeroSliderViewSet
from shared.models import HeroSlider

def test_hero_api():
    """Test hero slides API."""
    print("=== Testing Hero Slides API ===")

    # Create request factory
    factory = RequestFactory()

    # Create viewset instance
    viewset = HeroSliderViewSet()

    # Create request for active slides
    request = factory.get('/api/v1/shared/hero-slides/active/', HTTP_HOST='localhost:8000')
    request.user = AnonymousUser()

    # Set request in viewset
    viewset.request = request

    # Call active action
    try:
        response = viewset.active(request)
        print("API Response Status:", response.status_code)
        print("Response Data:", response.data)

        if response.data:
            print(f"\nFound {len(response.data)} active slides:")
            for i, slide in enumerate(response.data):
                print(f"\nSlide {i+1}:")
                print(f"  Title: {slide.get('title', 'N/A')}")
                print(f"  Desktop Image: {slide.get('desktop_image_url', 'N/A')}")
                print(f"  Tablet Image: {slide.get('tablet_image_url', 'N/A')}")
                print(f"  Mobile Image: {slide.get('mobile_image_url', 'N/A')}")

    except Exception as e:
        print(f"Error calling API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_hero_api()