#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider

def main():
    slides = HeroSlider.objects.all()
    print('Number of hero slides:', slides.count())
    print()

    for slide in slides:
        print(f'ID: {slide.id}')
        print(f'Title: {slide.title}')
        print(f'Desktop image: {slide.desktop_image}')
        print(f'Tablet image: {slide.tablet_image}')
        print(f'Mobile image: {slide.mobile_image}')
        print(f'Is active: {slide.is_active}')
        print(f'Is active now: {slide.is_active_now()}')
        print('---')

if __name__ == '__main__':
    main()
