#!/usr/bin/env python
"""
Create test data for homepage sections
"""
import os
import sys
import django
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import (
    AboutSection, AboutStatistic, AboutFeature,
    CTASection, CTAButton, CTAFeature,
    Footer, FooterLink,
    TransferBookingSection,
    FAQSettings
)
from django.core.files import File


def create_about_section():
    """Create About Section test data"""
    print("Creating About Section...")

    # Create About Section
    about_section = AboutSection.objects.create(
        slug='about-section',
        button_url='/about',
        is_active=True
    )

    # Set translated fields
    for lang_code, _ in [('en', 'English'), ('fa', 'Persian')]:
        about_section.set_current_language(lang_code)
        about_section.title = "Your Trusted Travel Partner" if lang_code == 'en' else "شریک سفر مورد اعتماد شما"
        about_section.subtitle = "Since 2004" if lang_code == 'en' else "از سال ۲۰۰۴"
        about_section.description = "With over two decades of experience in the travel industry, we have been creating unforgettable memories for travelers from around the world." if lang_code == 'en' else "با بیش از دو دهه تجربه در صنعت گردشگری، ما خاطرات فراموش نشدنی برای مسافران از سراسر جهان ایجاد کرده ایم."
        about_section.button_text = "Learn More" if lang_code == 'en' else "بیشتر بدانید"
        about_section.save()

    # Create About Statistics
    stats_data = [
        {"value": "20+", "label_en": "Years Experience", "label_fa": "سال تجربه", "icon": "🎯", "slug": "years-experience"},
        {"value": "100+", "label_en": "Countries Served", "label_fa": "کشور ارائه شده", "icon": "🌍", "slug": "countries-served"},
    ]

    for i, stat_data in enumerate(stats_data):
        stat = AboutStatistic.objects.create(
            slug=stat_data["slug"],
            value=stat_data["value"],
            icon=stat_data["icon"],
            order=i,
            is_active=True
        )

        stat.set_current_language('en')
        stat.label = stat_data["label_en"]
        stat.save()

        stat.set_current_language('fa')
        stat.label = stat_data["label_fa"]
        stat.save()

    # Create About Features
    features_data = [
        {"title_en": "Expert Local Guides", "title_fa": "راهنمایان محلی متخصص", "description_en": "Professional guides with deep local knowledge", "description_fa": "راهنمایان حرفه ای با دانش عمیق محلی", "icon": "👥", "slug": "expert-local-guides"},
        {"title_en": "Unique Cultural Experiences", "title_fa": "تجربیات فرهنگی منحصر به فرد", "description_en": "Authentic cultural immersion experiences", "description_fa": "تجربیات غوطه ور فرهنگی واقعی", "icon": "🎭", "slug": "unique-cultural-experiences"},
        {"title_en": "Sustainable Tourism", "title_fa": "گردشگری پایدار", "description_en": "Committed to environmental conservation", "description_fa": "متعهد به حفاظت محیط زیست", "icon": "🌱", "slug": "sustainable-tourism"},
    ]

    for i, feature_data in enumerate(features_data):
        feature = AboutFeature.objects.create(
            slug=feature_data["slug"],
            icon=feature_data["icon"],
            order=i,
            is_active=True
        )

        feature.set_current_language('en')
        feature.title = feature_data["title_en"]
        feature.description = feature_data["description_en"]
        feature.save()

        feature.set_current_language('fa')
        feature.title = feature_data["title_fa"]
        feature.description = feature_data["description_fa"]
        feature.save()

    print(f"✅ Created About Section with {len(stats_data)} statistics and {len(features_data)} features")


def create_cta_section():
    """Create CTA Section test data"""
    print("Creating CTA Section...")

    # Create CTA Section
    cta_section = CTASection.objects.create(slug='cta-section', is_active=True)

    # Set translated fields
    for lang_code, _ in [('en', 'English'), ('fa', 'Persian')]:
        cta_section.set_current_language(lang_code)
        cta_section.title = "Ready to Start Your Journey?" if lang_code == 'en' else "آماده شروع سفر خود هستید؟"
        cta_section.subtitle = "Explore Amazing Destinations" if lang_code == 'en' else "مقاصد شگفت انگیز را کاوش کنید"
        cta_section.description = "Discover amazing tours, events, and transfers with our comprehensive booking platform." if lang_code == 'en' else "تورهای شگفت انگیز، رویدادها و انتقال ها را با پلتفرم رزرو جامع ما کشف کنید."
        cta_section.save()

    # Create CTA Buttons
    buttons_data = [
        {"text_en": "Explore Tours", "text_fa": "تورها را کاوش کنید", "url": "/tours", "button_type": "primary", "slug": "explore-tours"},
        {"text_en": "Discover Events", "text_fa": "رویدادها را کشف کنید", "url": "/events", "button_type": "secondary", "slug": "discover-events"},
        {"text_en": "Book Transfers", "text_fa": "انتقال رزرو کنید", "url": "/transfers/booking", "button_type": "outline", "slug": "book-transfers"},
    ]

    for i, button_data in enumerate(buttons_data):
        button = CTAButton.objects.create(
            slug=button_data["slug"],
            cta_section=cta_section,
            url=button_data["url"],
            button_type=button_data["button_type"],
            order=i,
            is_active=True
        )

        button.set_current_language('en')
        button.text = button_data["text_en"]
        button.save()

        button.set_current_language('fa')
        button.text = button_data["text_fa"]
        button.save()

    # Create CTA Features
    features_data = [
        {"text_en": "24/7 Support", "text_fa": "پشتیبانی ۲۴/۷", "icon": "🕒", "slug": "24-7-support"},
        {"text_en": "Best Price Guarantee", "text_fa": "تضمین بهترین قیمت", "icon": "💰", "slug": "best-price-guarantee"},
        {"text_en": "Secure Payment", "text_fa": "پرداخت امن", "icon": "🔒", "slug": "secure-payment"},
    ]

    for i, feature_data in enumerate(features_data):
        feature = CTAFeature.objects.create(
            slug=feature_data["slug"],
            cta_section=cta_section,
            icon=feature_data["icon"],
            order=i,
            is_active=True
        )

        feature.set_current_language('en')
        feature.text = feature_data["text_en"]
        feature.save()

        feature.set_current_language('fa')
        feature.text = feature_data["text_fa"]
        feature.save()

    print(f"✅ Created CTA Section with {len(buttons_data)} buttons and {len(features_data)} features")


def create_footer():
    """Create Footer test data"""
    print("Creating Footer...")

    # Create Footer
    footer = Footer.objects.create(
        slug='footer',
        default_phone="+1-555-0123",
        default_email="info@peykantourism.com",
        instagram_url="https://instagram.com/peykantourism",
        telegram_url="https://t.me/peykantourism",
        whatsapp_number="+1-555-0123",
        facebook_url="https://facebook.com/peykantourism",
        is_active=True
    )

    # Set translated fields
    for lang_code, _ in [('en', 'English'), ('fa', 'Persian')]:
        footer.set_current_language(lang_code)
        footer.newsletter_title = "Newsletter" if lang_code == 'en' else "خبرنامه"
        footer.newsletter_description = "Get exclusive deals, travel tips, and destination highlights." if lang_code == 'en' else "معاملات انحصاری، نکات سفر و نکات برجسته مقصد دریافت کنید."
        footer.company_name = "Peykan Tourism" if lang_code == 'en' else "گردشگری پکان"
        footer.company_description = "Your travel companion since 2004" if lang_code == 'en' else "همراه سفر شما از سال ۲۰۰۴"
        footer.copyright_text = "© 2024 Peykan Tourism. All rights reserved." if lang_code == 'en' else "© ۲۰۲۴ گردشگری پکان. تمامی حقوق محفوظ است."
        footer.newsletter_placeholder = "Enter your email address" if lang_code == 'en' else "آدرس ایمیل خود را وارد کنید"
        footer.trusted_by_text = "Trusted by 50K+ travelers" if lang_code == 'en' else "توسط بیش از ۵۰ هزار مسافر اعتماد شده"
        footer.save()

    # Create Footer Links
    links_data = [
        {"label_en": "Tours", "label_fa": "تورها", "url": "/tours", "slug": "tours"},
        {"label_en": "Events", "label_fa": "رویدادها", "url": "/events", "slug": "events"},
        {"label_en": "Transfers", "label_fa": "انتقال", "url": "/transfers/booking", "slug": "transfers"},
        {"label_en": "FAQ", "label_fa": "سوالات متداول", "url": "/faq", "slug": "faq"},
        {"label_en": "About", "label_fa": "درباره ما", "url": "/about", "slug": "about"},
        {"label_en": "Contact", "label_fa": "تماس با ما", "url": "/contact", "slug": "contact"},
        {"label_en": "Privacy Policy", "label_fa": "سیاست حفظ حریم خصوصی", "url": "/privacy", "slug": "privacy"},
        {"label_en": "Terms of Service", "label_fa": "شرایط استفاده", "url": "/terms", "slug": "terms"},
    ]

    for i, link_data in enumerate(links_data):
        link = FooterLink.objects.create(
            slug=link_data["slug"],
            footer=footer,
            url=link_data["url"],
            link_type='internal',
            order=i,
            is_active=True
        )

        link.set_current_language('en')
        link.label = link_data["label_en"]
        link.save()

        link.set_current_language('fa')
        link.label = link_data["label_fa"]
        link.save()

    print(f"✅ Created Footer with {len(links_data)} links")


def create_transfer_booking_section():
    """Create Transfer Booking Section test data"""
    print("Creating Transfer Booking Section...")

    # Create Transfer Booking Section
    transfer_section = TransferBookingSection.objects.create(
        slug='transfer-booking-section',
        button_url='/transfers/booking',
        experience_years=20,
        countries_served=100,
        is_active=True
    )

    # Set translated fields
    for lang_code, _ in [('en', 'English'), ('fa', 'Persian')]:
        transfer_section.set_current_language(lang_code)
        transfer_section.title = "Seamless Travel Experience" if lang_code == 'en' else "تجربه سفر بی دردسر"
        transfer_section.subtitle = "Premium Private Transfers" if lang_code == 'en' else "انتقال خصوصی پرمیوم"
        transfer_section.description = "Private airport transfer is one of the most common transfers organized by foreign tour operators for direct transportation of guests from the airport to the tour accommodation." if lang_code == 'en' else "انتقال فرودگاهی خصوصی یکی از متداول ترین انتقال هایی است که توسط اپراتورهای تورهای خارجی برای انتقال مستقیم مهمانان از فرودگاه به محل اقامت تور برگزار می‌شود."
        transfer_section.button_text = "Book Transfer" if lang_code == 'en' else "رزرو انتقال"
        transfer_section.feature_1 = "Luxury vehicles" if lang_code == 'en' else "خودروهای لوکس"
        transfer_section.feature_2 = "Professional drivers" if lang_code == 'en' else "رانندگان حرفه ای"
        transfer_section.feature_3 = "24/7 tracking" if lang_code == 'en' else "پیگیری ۲۴/۷"
        transfer_section.feature_4 = "Complete safety" if lang_code == 'en' else "ایمنی کامل"
        transfer_section.save()

    print("✅ Created Transfer Booking Section")


def create_faq_settings():
    """Create FAQ Settings test data"""
    print("Creating FAQ Settings...")

    # Create FAQ Settings
    faq_settings = FAQSettings.objects.create(
        slug='faq-settings',
        items_per_page=5,
        show_categories=True,
        show_search=True,
        is_active=True
    )

    # Set translated fields
    for lang_code, _ in [('en', 'English'), ('fa', 'Persian')]:
        faq_settings.set_current_language(lang_code)
        faq_settings.title = "Frequently Asked Questions" if lang_code == 'en' else "سوالات متداول"
        faq_settings.subtitle = "Find answers to common questions about our tours, events, and travel services." if lang_code == 'en' else "پاسخ سوالات رایج در مورد تورها، رویدادها و خدمات مسافرتی ما را بیابید."
        faq_settings.save()

    print("✅ Created FAQ Settings")


def main():
    """Main function to create all test data"""
    print("🚀 Creating homepage test data...")
    print("=" * 50)

    try:
        create_about_section()
        print()

        create_cta_section()
        print()

        create_footer()
        print()

        create_transfer_booking_section()
        print()

        create_faq_settings()
        print()

        print("=" * 50)
        print("🎉 All homepage test data created successfully!")
        print("\n📋 Available API endpoints:")
        print("- GET /api/v1/shared/about-section/active/ - About Section")
        print("- GET /api/v1/shared/about-statistics/ - About Statistics")
        print("- GET /api/v1/shared/about-features/ - About Features")
        print("- GET /api/v1/shared/cta-section/active/ - CTA Section")
        print("- GET /api/v1/shared/footer/active/ - Footer")
        print("- GET /api/v1/shared/transfer-booking-section/active/ - Transfer Section")
        print("- GET /api/v1/shared/faq-settings/active/ - FAQ Settings")

    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
