#!/usr/bin/env python
"""
Test video features for HeroSlider.
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

def test_video_features():
    """Test video features."""
    print("=== Testing Video Features ===")

    factory = RequestFactory()
    request = factory.get('/api/v1/shared/hero-slides/active/', HTTP_HOST='localhost:8000')
    request.user = type('AnonymousUser', (), {'is_authenticated': False})()

    slides = HeroSlider.objects.all()
    print(f'Found {len(slides)} slides')

    for slide in slides:
        print(f'\nSlide: {slide.title}')
        print(f'  Video Type: {slide.video_type}')
        print(f'  Has Video: {slide.has_video()}')
        print(f'  Video URL: {slide.get_video_url()}')
        print(f'  Thumbnail URL: {slide.get_video_thumbnail_url()}')
        print(f'  Autoplay Allowed: {slide.is_video_autoplay_allowed()}')
        print(f'  Video Display Name: {slide.video_display_name}')

        # Test serializer
        serializer = HeroSliderSerializer(slide, context={'request': request})
        data = serializer.data
        print(f'  Serialized Video Type: {data.get("video_type")}')
        print(f'  Serialized Has Video: {data.get("has_video")}')
        print(f'  Serialized Video URL: {data.get("video_file_url") or data.get("video_url")}')

if __name__ == '__main__':
    test_video_features()
