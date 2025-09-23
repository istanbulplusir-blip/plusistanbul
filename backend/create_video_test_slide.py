#!/usr/bin/env python
"""
Create a test hero slide with video.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider

def create_video_slide():
    """Create a test slide with video."""
    print("=== Creating Video Test Slide ===")

    # Create a video test slide
    slide = HeroSlider.objects.create(
        title='ویدیو تست',
        subtitle='تست قابلیت ویدیو در اسلایدر',
        description='این اسلایدر برای تست قابلیت ویدیو ایجاد شده است.',
        button_text='مشاهده ویدیو',
        button_url='/videos',
        button_type='primary',
        order=5,
        display_duration=10000,
        show_for_authenticated=True,
        show_for_anonymous=True,
        is_active=True,
        # Video fields
        video_type='url',
        video_url='https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        autoplay_video=True,
        video_muted=True,
        show_video_controls=True,
        video_loop=True
    )

    print("Created video test slide:")
    print(f"  Title: {slide.title}")
    print(f"  Video Type: {slide.video_type}")
    print(f"  Video URL: {slide.video_url}")
    print(f"  Autoplay: {slide.autoplay_video}")
    print(f"  Muted: {slide.video_muted}")
    print(f"  Controls: {slide.show_video_controls}")
    print(f"  Loop: {slide.video_loop}")
    print(f"  Has Video: {slide.has_video()}")
    print(f"  Autoplay Allowed: {slide.is_video_autoplay_allowed()}")

    return slide

if __name__ == '__main__':
    create_video_slide()
