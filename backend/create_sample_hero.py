#!/usr/bin/env python3
"""
Create sample Hero Slider for testing
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider
from django.core.files import File

def create_sample_hero():
    """Create a sample hero slider"""
    
    print("Creating sample Hero Slider...")
    
    # Check if hero slider already exists
    if HeroSlider.objects.filter(is_active=True).exists():
        print("Active hero slider already exists!")
        return
    
    # Create hero slider with default images
    hero = HeroSlider.objects.create(
        order=1,
        is_active=True,
        display_duration=5000,
        button_url='/tours',
        button_type='primary',
        show_for_authenticated=True,
        show_for_anonymous=True,
        video_type='none',
        autoplay_video=False,
        video_muted=True,
        show_video_controls=False,
        video_loop=True
    )
    
    # Set translatable fields
    hero.set_current_language('fa')
    hero.title = 'به پیکان توریسم خوش آمدید'
    hero.subtitle = 'بهترین تورهای استانبول'
    hero.description = 'تجربه‌ای فراموش‌نشدنی در استانبول'
    hero.button_text = 'مشاهده تورها'
    hero.save()
    
    hero.set_current_language('en')
    hero.title = 'Welcome to Peykan Tourism'
    hero.subtitle = 'Best Istanbul Tours'
    hero.description = 'Unforgettable experience in Istanbul'
    hero.button_text = 'View Tours'
    hero.save()
    
    # Assign default images
    desktop_img_path = 'media/hero/desktop/PEYKAN-DEFAULT.png'
    tablet_img_path = 'media/hero/tablet/PEYKAN-DEFAULT.png'
    mobile_img_path = 'media/hero/mobile/PEYKAN-DEFAULT.png'
    
    if os.path.exists(desktop_img_path):
        with open(desktop_img_path, 'rb') as f:
            hero.desktop_image.save('PEYKAN-DEFAULT.png', File(f), save=False)
    
    if os.path.exists(tablet_img_path):
        with open(tablet_img_path, 'rb') as f:
            hero.tablet_image.save('PEYKAN-DEFAULT.png', File(f), save=False)
    
    if os.path.exists(mobile_img_path):
        with open(mobile_img_path, 'rb') as f:
            hero.mobile_image.save('PEYKAN-DEFAULT.png', File(f), save=False)
    
    hero.save()
    
    print(f"✓ Created Hero Slider: {hero.title}")
    print(f"  - ID: {hero.id}")
    print(f"  - Desktop Image: {hero.desktop_image}")
    print(f"  - Tablet Image: {hero.tablet_image}")
    print(f"  - Mobile Image: {hero.mobile_image}")
    print("\nSample hero slider created successfully!")

if __name__ == '__main__':
    create_sample_hero()
