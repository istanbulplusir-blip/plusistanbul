#!/usr/bin/env python
"""
Check hero sliders and their images.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider

def check_sliders():
    """Check all hero sliders and their images."""
    print("=== Hero Sliders Details ===")

    slides = HeroSlider.objects.all().order_by('order')
    for slide in slides:
        print(f"ID: {slide.id}")
        print(f"Title: {slide.title}")
        print(f"Active: {slide.is_active}")
        print(f"Order: {slide.order}")

        print(f"Desktop Image: {slide.desktop_image.name if slide.desktop_image else 'No image'}")
        print(f"Tablet Image: {slide.tablet_image.name if slide.tablet_image else 'No image'}")
        print(f"Mobile Image: {slide.mobile_image.name if slide.mobile_image else 'No image'}")

        if slide.desktop_image:
            image_path = f"media/{slide.desktop_image.name}"
            exists = os.path.exists(image_path)
            print(f"Desktop Image Exists: {exists}")

        print("-" * 50)

if __name__ == '__main__':
    check_sliders()