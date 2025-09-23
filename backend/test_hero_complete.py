#!/usr/bin/env python
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider
from shared.serializers import HeroSliderSerializer
from django.test import RequestFactory

def main():
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/v1/shared/hero-slides/active/', HTTP_HOST='localhost:8000')

    slides = HeroSlider.objects.filter(is_active=True)
    print('Number of active hero slides:', slides.count())
    print()

    for slide in slides:
        print(f'Slide ID: {slide.id}')
        print(f'Title: {slide.title}')

        # Check if slide has images
        has_desktop = bool(slide.desktop_image)
        has_tablet = bool(slide.tablet_image)
        has_mobile = bool(slide.mobile_image)

        print(f'Has desktop image: {has_desktop}')
        print(f'Has tablet image: {has_tablet}')
        print(f'Has mobile image: {has_mobile}')

        # Serialize the slide
        serializer = HeroSliderSerializer(slide, context={'request': request})
        data = serializer.data

        print(f'Desktop image URL: {data.get("desktop_image_url")}')
        print(f'Tablet image URL: {data.get("tablet_image_url")}')
        print(f'Mobile image URL: {data.get("mobile_image_url")}')
        print('---')

    print('\n=== Testing fallback scenario ===')
    # Test with a slide that has no images
    fallback_slide = HeroSlider.objects.filter(desktop_image='').first()
    if fallback_slide:
        print(f'Testing fallback for slide: {fallback_slide.title}')
        serializer = HeroSliderSerializer(fallback_slide, context={'request': request})
        data = serializer.data
        print(f'Fallback desktop image URL: {data.get("desktop_image_url")}')

if __name__ == '__main__':
    main()
