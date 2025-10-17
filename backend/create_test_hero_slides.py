"""
Script to create test Hero Slides for testing the improved frontend.
Run this script from the backend directory:
python create_test_hero_slides.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider
from django.utils import timezone

def create_test_slides():
    """Create test hero slides with images and videos."""
    
    print("Creating test hero slides...")
    
    # Clear existing slides (optional)
    # HeroSlider.objects.all().delete()
    # print("Cleared existing slides")
    
    # Slide 1: Image only
    slide1, created = HeroSlider.objects.get_or_create(
        slug='test-slide-image-1',
        defaults={
            'order': 1,
            'display_duration': 5000,
            'is_active': True,
            'show_for_authenticated': True,
            'show_for_anonymous': True,
            'button_url': '/tours',
            'button_type': 'primary',
            'video_type': 'none',
            'autoplay_video': False,
            'video_muted': True,
            'show_video_controls': False,
            'video_loop': True,
        }
    )
    
    # Set translations for slide 1
    slide1.set_current_language('en')
    slide1.title = 'Discover Amazing Places'
    slide1.subtitle = 'Book tours, events & transfers with ease'
    slide1.description = 'Experience unforgettable journeys with our premium travel services'
    slide1.button_text = 'Explore Tours'
    
    slide1.set_current_language('fa')
    slide1.title = 'کشف مکان‌های شگفت‌انگیز'
    slide1.subtitle = 'رزرو تور، رویداد و ترانسفر با سهولت'
    slide1.description = 'تجربه سفرهای فراموش‌نشدنی با خدمات ممتاز ما'
    slide1.button_text = 'مشاهده تورها'
    
    slide1.save()
    print(f"✅ Slide 1 (Image): {'Created' if created else 'Updated'}")
    
    # Slide 2: Video file (simulated - you need to upload actual video)
    slide2, created = HeroSlider.objects.get_or_create(
        slug='test-slide-video-file',
        defaults={
            'order': 2,
            'display_duration': 8000,
            'is_active': True,
            'show_for_authenticated': True,
            'show_for_anonymous': True,
            'button_url': '/tours/istanbul',
            'button_type': 'primary',
            'video_type': 'file',
            'autoplay_video': True,
            'video_muted': True,
            'show_video_controls': False,
            'video_loop': True,
        }
    )
    
    # Set translations for slide 2
    slide2.set_current_language('en')
    slide2.title = 'Explore Istanbul Magic'
    slide2.subtitle = 'Where History Meets Modernity'
    slide2.description = 'Discover the enchanting blend of Eastern and Western cultures'
    slide2.button_text = 'Discover Istanbul'
    
    slide2.set_current_language('fa')
    slide2.title = 'کشف جادوی استانبول'
    slide2.subtitle = 'جایی که تاریخ با مدرنیته ملاقات می‌کند'
    slide2.description = 'ترکیب شگفت‌انگیز فرهنگ شرق و غرب را کشف کنید'
    slide2.button_text = 'کشف استانبول'
    
    slide2.save()
    print(f"✅ Slide 2 (Video File): {'Created' if created else 'Updated'}")
    print("   ⚠️  Note: You need to upload a video file in Django admin")
    
    # Slide 3: Video URL
    slide3, created = HeroSlider.objects.get_or_create(
        slug='test-slide-video-url',
        defaults={
            'order': 3,
            'display_duration': 8000,
            'is_active': True,
            'show_for_authenticated': True,
            'show_for_anonymous': True,
            'button_url': '/events',
            'button_type': 'secondary',
            'video_type': 'url',
            'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            'autoplay_video': True,
            'video_muted': True,
            'show_video_controls': False,
            'video_loop': True,
        }
    )
    
    # Set translations for slide 3
    slide3.set_current_language('en')
    slide3.title = 'Live Music & Entertainment'
    slide3.subtitle = 'Feel the Rhythm of Istanbul'
    slide3.description = 'Experience world-class concerts and entertainment'
    slide3.button_text = 'Discover Events'
    
    slide3.set_current_language('fa')
    slide3.title = 'موسیقی زنده و سرگرمی'
    slide3.subtitle = 'ریتم استانبول را احساس کنید'
    slide3.description = 'کنسرت‌ها و سرگرمی‌های جهانی را تجربه کنید'
    slide3.button_text = 'کشف رویدادها'
    
    slide3.save()
    print(f"✅ Slide 3 (Video URL): {'Created' if created else 'Updated'}")
    
    # Slide 4: Image with different button type
    slide4, created = HeroSlider.objects.get_or_create(
        slug='test-slide-image-2',
        defaults={
            'order': 4,
            'display_duration': 5000,
            'is_active': True,
            'show_for_authenticated': True,
            'show_for_anonymous': True,
            'button_url': '/transfers/booking',
            'button_type': 'outline',
            'video_type': 'none',
            'autoplay_video': False,
            'video_muted': True,
            'show_video_controls': False,
            'video_loop': True,
        }
    )
    
    # Set translations for slide 4
    slide4.set_current_language('en')
    slide4.title = 'Premium Airport Transfers'
    slide4.subtitle = 'Seamless Travel Experience'
    slide4.description = 'Safe, reliable, and comfortable journeys to your destination'
    slide4.button_text = 'Book Transfer'
    
    slide4.set_current_language('fa')
    slide4.title = 'ترانسفر فرودگاهی ممتاز'
    slide4.subtitle = 'تجربه سفر بدون دردسر'
    slide4.description = 'سفرهای ایمن، قابل اعتماد و راحت به مقصد شما'
    slide4.button_text = 'رزرو ترانسفر'
    
    slide4.save()
    print(f"✅ Slide 4 (Image): {'Created' if created else 'Updated'}")
    
    print("\n" + "="*50)
    print("✅ Test slides created successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Go to Django admin: http://localhost:8000/admin/shared/heroslider/")
    print("2. Upload images for slides 1 and 4")
    print("3. Upload video file for slide 2 (or use video URL)")
    print("4. Check the frontend: http://localhost:3000")
    print("\nSlide 3 already has a test video URL from Google's sample videos.")
    
    # Print slide details
    print("\n" + "="*50)
    print("Slide Details:")
    print("="*50)
    
    for slide in [slide1, slide2, slide3, slide4]:
        slide.set_current_language('en')
        print(f"\n{slide.title}")
        print(f"  - Type: {slide.get_video_type_display()}")
        print(f"  - Order: {slide.order}")
        print(f"  - Button: {slide.button_text} ({slide.button_type})")
        print(f"  - Active: {slide.is_active}")
        if slide.video_type == 'url':
            print(f"  - Video URL: {slide.video_url}")

if __name__ == '__main__':
    create_test_slides()
