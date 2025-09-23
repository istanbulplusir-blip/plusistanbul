#!/usr/bin/env python
"""
Check the status of hero slides.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider

def check_slides_status():
    """Check which slides are active."""
    print("=== Hero Slides Status ===")

    slides = HeroSlider.objects.all().order_by('order')
    active_slides = slides.filter(is_active=True)

    print(f"Total slides: {len(slides)}")
    print(f"Active slides: {len(active_slides)}")
    print()

    for slide in slides:
        status = "✅ ACTIVE" if slide.is_active else "❌ INACTIVE"
        video_info = f" (Video: {slide.video_type})" if slide.video_type != 'none' else ""
        print(f"{slide.order}: {slide.title} - {status}{video_info}")

    print()
    print("Active slides that will be shown:")
    for slide in active_slides:
        video_info = f" [Video: {slide.video_type}]" if slide.video_type != 'none' else ""
        print(f"  - {slide.title}{video_info}")

if __name__ == '__main__':
    check_slides_status()
