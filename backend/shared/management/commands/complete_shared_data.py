"""
Management command to complete all shared app data.
Checks what's missing and creates it.
"""

from django.core.management.base import BaseCommand
from shared.models import (
    ContactInfo, StaticPage, FAQ, FAQCategory, SupportFAQ,
    HeroSlider, Banner, SiteSettings, AboutSection, AboutStatistic, AboutFeature,
    CTASection, CTAButton, CTAFeature, Footer, FooterLink,
    TransferBookingSection, NavigationMenu, FAQSettings, CatalogFile
)


class Command(BaseCommand):
    help = 'Complete all shared app data by checking and creating missing items'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking shared app data...")
        self.stdout.write("="*80)
        
        # Check and create each model
        self._check_contact_info()
        self._check_site_settings()
        self._check_static_pages()
        self._check_faq_categories()
        self._check_faqs()
        self._check_support_faqs()
        self._check_hero_sliders()
        self._check_about_section()
        self._check_cta_section()
        self._check_footer()
        self._check_transfer_section()
        self._check_navigation_menu()
        self._check_faq_settings()
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("✅ Shared data check complete!"))
    
    def _check_contact_info(self):
        """Check and create ContactInfo"""
        self.stdout.write("\n📞 Checking ContactInfo...")
        
        if ContactInfo.objects.exists():
            self.stdout.write("  ✅ ContactInfo exists")
            return
        
        contact = ContactInfo.objects.create(
            company_name='Peykan Tourism',
            address='Istanbul, Turkey',
            phone_primary='+90 212 555 0123',
            phone_secondary='+90 212 555 0124',
            email_general='info@peykantravelistanbul.com',
            email_support='support@peykantravelistanbul.com',
            email_sales='sales@peykantravelistanbul.com',
            working_hours='9:00 AM - 6:00 PM',
            working_days='Monday - Friday',
            latitude=41.0082,
            longitude=28.9784,
            instagram_url='https://instagram.com/peykantravel',
            telegram_url='https://t.me/peykansupport',
            whatsapp_number='+90 555 123 4567',
            facebook_url='https://facebook.com/peykantravel',
            is_active=True
        )
        self.stdout.write(self.style.SUCCESS("  ✅ Created ContactInfo"))
