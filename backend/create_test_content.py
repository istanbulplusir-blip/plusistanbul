#!/usr/bin/env python
"""
Create test data for the new content management system.
This script creates sample data for HeroSlider, Banner, SiteSettings, and ImageOptimization models.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import HeroSlider, Banner, SiteSettings, ImageOptimization
from django.core.files.base import ContentFile
from django.utils import timezone

def create_hero_slides():
    """Create sample hero slides."""
    print("Creating hero slides...")

    # Delete existing slides
    HeroSlider.objects.all().delete()

    slides_data = [
        {
            'title_en': 'Discover Amazing Places',
            'title_fa': 'مکان‌های شگفت‌انگیز را کشف کنید',
            'subtitle_en': 'Book tours, events & transfers with ease',
            'subtitle_fa': 'تورها، رویدادها و ترنسفرها را به راحتی رزرو کنید',
            'description_en': 'Experience unforgettable journeys with our premium travel services',
            'description_fa': 'با خدمات مسافرتی برتر ما، سفرهای فراموش‌نشدنی را تجربه کنید',
            'button_text_en': 'Explore Tours',
            'button_text_fa': 'تورها را مشاهده کنید',
            'button_url': '/tours',
            'button_type': 'primary',
            'order': 1,
            'display_duration': 5000,
        },
        {
            'title_en': 'Explore Istanbul\'s Magic',
            'title_fa': 'جادوی استانبول را کشف کنید',
            'subtitle_en': 'Where History Meets Modernity',
            'subtitle_fa': 'جایی که تاریخ با مدرنیته ملاقات می‌کند',
            'description_en': 'Discover the enchanting city of Istanbul with our curated experiences',
            'description_fa': 'شهر جادویی استانبول را با تجربیات دستچین شده ما کشف کنید',
            'button_text_en': 'View Events',
            'button_text_fa': 'رویدادها را مشاهده کنید',
            'button_url': '/events',
            'button_type': 'secondary',
            'order': 2,
            'display_duration': 6000,
        },
        {
            'title_en': 'Live Music & Entertainment',
            'title_fa': 'موسیقی زنده و سرگرمی',
            'subtitle_en': 'Feel the Rhythm of Istanbul',
            'subtitle_fa': 'ریتم استانبول را احساس کنید',
            'description_en': 'Experience world-class concerts and entertainment in iconic venues',
            'description_fa': 'کنسرت‌ها و سرگرمی‌های درجه جهانی را در مکان‌های نمادین تجربه کنید',
            'button_text_en': 'Book Now',
            'button_text_fa': 'همین حالا رزرو کنید',
            'button_url': '/events',
            'button_type': 'outline',
            'order': 3,
            'display_duration': 5500,
        }
    ]

    created_slides = []
    for slide_data in slides_data:
        slide = HeroSlider.objects.create(
            title=slide_data['title_en'],
            subtitle=slide_data['subtitle_en'],
            description=slide_data['description_en'],
            button_text=slide_data['button_text_en'],
            button_url=slide_data['button_url'],
            button_type=slide_data['button_type'],
            order=slide_data['order'],
            display_duration=slide_data['display_duration'],
            show_for_authenticated=True,
            show_for_anonymous=True,
            is_active=True,
        )

        # Create translations
        slide.set_current_language('fa')
        slide.title = slide_data['title_fa']
        slide.subtitle = slide_data['subtitle_fa']
        slide.description = slide_data['description_fa']
        slide.button_text = slide_data['button_text_fa']
        slide.save()

        created_slides.append(slide)
        print(f"Created hero slide: {slide.title}")

    return created_slides

def create_banners():
    """Create sample banners."""
    print("Creating banners...")

    # Delete existing banners
    Banner.objects.all().delete()

    banners_data = [
        {
            'title_en': 'Special Winter Offer',
            'title_fa': 'پیشنهاد ویژه زمستانی',
            'banner_type': 'homepage_top',
            'position': 'top',
            'link_url': '/tours?seasonal=winter',
            'link_target': '_self',
            'display_order': 1,
        },
        {
            'title_en': 'Book Your Istanbul Tour',
            'title_fa': 'تور استانبول خود را رزرو کنید',
            'banner_type': 'homepage_bottom',
            'position': 'bottom',
            'link_url': '/tours?city=istanbul',
            'link_target': '_self',
            'display_order': 2,
        },
        {
            'title_en': 'Live Music Events',
            'title_fa': 'رویدادهای موسیقی زنده',
            'banner_type': 'sidebar',
            'position': 'sidebar',
            'link_url': '/events?type=music',
            'link_target': '_blank',
            'display_order': 3,
        },
        {
            'title_en': 'Premium Transfer Service',
            'title_fa': 'خدمات ترنسفر پرمیوم',
            'banner_type': 'tour_detail',
            'position': 'middle',
            'link_url': '/transfers',
            'link_target': '_self',
            'display_order': 4,
        }
    ]

    created_banners = []
    for banner_data in banners_data:
        banner = Banner.objects.create(
            title=banner_data['title_en'],
            banner_type=banner_data['banner_type'],
            position=banner_data['position'],
            link_url=banner_data['link_url'],
            link_target=banner_data['link_target'],
            display_order=banner_data['display_order'],
            show_for_authenticated=True,
            show_for_anonymous=True,
            is_active=True,
        )

        # Create translations
        banner.set_current_language('fa')
        banner.title = banner_data['title_fa']
        banner.save()

        created_banners.append(banner)
        print(f"Created banner: {banner.title}")

    return created_banners

def create_site_settings():
    """Create site settings."""
    print("Creating site settings...")

    # Delete existing settings
    SiteSettings.objects.all().delete()

    settings = SiteSettings.objects.create(
        site_name='Peykan Tourism',
        site_description='Your gateway to amazing travel experiences in Turkey and beyond',
        default_language='fa',
        default_phone='+90 216 555 0123',
        default_email='info@peykan-tourism.com',
        maintenance_mode=False,
        maintenance_message='We are currently updating our website. Please check back soon.',
        default_meta_title='Peykan Tourism - Amazing Travel Experiences',
        default_meta_description='Discover amazing places with Peykan Tourism. Book tours, events and transfers with ease.',
    )

    print(f"Created site settings: {settings.site_name}")
    return settings

def create_image_optimization_samples():
    """Create sample image optimization records."""
    print("Creating image optimization samples...")

    # Delete existing records
    ImageOptimization.objects.all().delete()

    # Sample images for different types
    sample_images = [
        {
            'image_type': 'hero',
            'original_width': 1920,
            'original_height': 1080,
            'original_size': 245760,  # ~245KB
            'quality_desktop': 85,
            'quality_tablet': 80,
            'quality_mobile': 75,
            'optimized_size_desktop': 184320,  # ~184KB (25% reduction)
            'optimized_size_tablet': 122880,  # ~122KB (50% reduction)
            'optimized_size_mobile': 61440,   # ~61KB (75% reduction)
            'optimization_completed': True,
        },
        {
            'image_type': 'tour',
            'original_width': 800,
            'original_height': 600,
            'original_size': 153600,  # ~153KB
            'quality_desktop': 85,
            'quality_tablet': 80,
            'quality_mobile': 75,
            'optimized_size_desktop': 122880,  # ~122KB (20% reduction)
            'optimized_size_tablet': 92160,    # ~92KB (40% reduction)
            'optimized_size_mobile': 46080,    # ~46KB (70% reduction)
            'optimization_completed': True,
        },
        {
            'image_type': 'event',
            'original_width': 600,
            'original_height': 400,
            'original_size': 76800,   # ~76KB
            'quality_desktop': 85,
            'quality_tablet': 80,
            'quality_mobile': 75,
            'optimized_size_desktop': 61440,   # ~61KB (20% reduction)
            'optimized_size_tablet': 46080,    # ~46KB (40% reduction)
            'optimized_size_mobile': 23040,    # ~23KB (70% reduction)
            'optimization_completed': True,
        },
        {
            'image_type': 'banner',
            'original_width': 1200,
            'original_height': 400,
            'original_size': 153600,  # ~153KB
            'quality_desktop': 85,
            'quality_tablet': 80,
            'quality_mobile': 75,
            'optimized_size_desktop': 122880,  # ~122KB (20% reduction)
            'optimized_size_tablet': 92160,    # ~92KB (40% reduction)
            'optimized_size_mobile': 46080,    # ~46KB (70% reduction)
            'optimization_completed': True,
        },
        {
            'image_type': 'gallery',
            'original_width': 1000,
            'original_height': 750,
            'original_size': 225000,  # ~225KB
            'quality_desktop': 85,
            'quality_tablet': 80,
            'quality_mobile': 75,
            'optimized_size_desktop': 180000,  # ~180KB (20% reduction)
            'optimized_size_tablet': 135000,   # ~135KB (40% reduction)
            'optimized_size_mobile': 67500,    # ~67KB (70% reduction)
            'optimization_completed': False,  # Still processing
        }
    ]

    created_images = []
    for image_data in sample_images:
        image_opt = ImageOptimization.objects.create(
            image_type=image_data['image_type'],
            original_width=image_data['original_width'],
            original_height=image_data['original_height'],
            original_size=image_data['original_size'],
            quality_desktop=image_data['quality_desktop'],
            quality_tablet=image_data['quality_tablet'],
            quality_mobile=image_data['quality_mobile'],
            optimized_size_desktop=image_data['optimized_size_desktop'],
            optimized_size_tablet=image_data['optimized_size_tablet'],
            optimized_size_mobile=image_data['optimized_size_mobile'],
            optimization_completed=image_data['optimization_completed'],
        )

        created_images.append(image_opt)
        print(f"Created image optimization record: {image_opt.get_image_type_display()} - {image_opt.compression_ratio:.1f}% compression")

    return created_images

def main():
    """Main function to create all test data."""
    print("🚀 Creating test data for Peykan Tourism Content Management System")
    print("=" * 70)

    try:
        # Create hero slides
        hero_slides = create_hero_slides()
        print(f"✅ Created {len(hero_slides)} hero slides")
        print()

        # Create banners
        banners = create_banners()
        print(f"✅ Created {len(banners)} banners")
        print()

        # Create site settings
        site_settings = create_site_settings()
        print("✅ Created site settings")
        print()

        # Create image optimization samples
        image_records = create_image_optimization_samples()
        print(f"✅ Created {len(image_records)} image optimization records")
        print()

        print("=" * 70)
        print("🎉 All test data created successfully!")
        print()
        print("📊 Summary:")
        print(f"   • Hero Slides: {len(hero_slides)}")
        print(f"   • Banners: {len(banners)}")
        print(f"   • Site Settings: 1")
        print(f"   • Image Optimization Records: {len(image_records)}")
        print()
        print("🌐 Test the APIs:")
        print("   GET /shared/hero-slides/active/")
        print("   GET /shared/banners/active/")
        print("   GET /shared/site-settings/")
        print("   GET /shared/image-optimization/")
        print()
        print("👨‍💼 Admin Panel:")
        print("   http://localhost:8000/admin/shared/")
        print()

    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
