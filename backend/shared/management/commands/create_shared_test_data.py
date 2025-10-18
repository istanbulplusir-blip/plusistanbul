from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta

from shared.models import (
    StaticPage, ContactInfo, ContactMessage, FAQCategory, FAQ,
    SupportFAQ, HeroSlider, Banner, SiteSettings, AboutSection,
    AboutStatistic, AboutFeature, CTASection, CTAButton, CTAFeature,
    Footer, FooterLink, TransferBookingSection, NavigationMenu, FAQSettings
)

User = get_user_model()


class Command(BaseCommand):
    help = "Create comprehensive test data for all shared models in 3 languages"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating shared test data in 3 languages...")
        
        # Create test data for each model
        self._create_static_pages()
        self._create_contact_info()
        self._create_contact_messages()
        self._create_faq_data()
        self._create_support_faqs()
        self._create_hero_sliders()
        self._create_banners()
        self._create_site_settings()
        self._create_about_section()
        self._create_cta_section()
        self._create_footer()
        self._create_transfer_booking_section()
        self._create_navigation_menu()
        self._create_faq_settings()
        
        self.stdout.write(self.style.SUCCESS("\n✅ All shared test data created successfully!"))

    def _create_static_pages(self):
        """Create static pages in 3 languages"""
        self.stdout.write("\n📄 Creating Static Pages...")
        
        pages_data = [
            ('about', 'About Us', 'درباره ما', 'Hakkımızda'),
            ('terms', 'Terms & Conditions', 'شرایط و قوانین', 'Şartlar ve Koşullar'),
            ('privacy', 'Privacy Policy', 'حریم خصوصی', 'Gizlilik Politikası'),
            ('faq', 'FAQ', 'سوالات متداول', 'SSS'),
            ('contact', 'Contact', 'تماس با ما', 'İletişim'),
        ]
        
        for page_type, en_title, fa_title, tr_title in pages_data:
            page, created = StaticPage.objects.get_or_create(
                page_type=page_type,
                defaults={'meta_description': f'{en_title} page', 'meta_keywords': page_type}
            )
            
            # English
            page.set_current_language('en')
            page.title = en_title
            page.content = f"This is the {en_title} page content. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            page.excerpt = f"Brief description of {en_title}"
            page.save()
            
            # Persian
            page.set_current_language('fa')
            page.title = fa_title
            page.content = f"این محتوای صفحه {fa_title} است. لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم."
            page.excerpt = f"توضیح مختصر {fa_title}"
            page.save()
            
            # Turkish
            page.set_current_language('tr')
            page.title = tr_title
            page.content = f"Bu {tr_title} sayfa içeriğidir. Lorem ipsum dolor sit amet."
            page.excerpt = f"{tr_title} kısa açıklama"
            page.save()
            
            self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} {page_type}")

    def _create_contact_info(self):
        """Create contact information"""
        self.stdout.write("\n📞 Creating Contact Info...")
        
        contact, created = ContactInfo.objects.get_or_create(
            company_name="Peykan Tourism",
            defaults={
                'address': 'Tehran, Iran - Valiasr Street, No. 123',
                'phone_primary': '+98 21 1234 5678',
                'phone_secondary': '+98 21 8765 4321',
                'email_general': 'info@peykantourism.com',
                'email_support': 'support@peykantourism.com',
                'email_sales': 'sales@peykantourism.com',
                'working_hours': '9:00 AM - 6:00 PM',
                'working_days': 'Saturday - Thursday',
                'latitude': Decimal('35.6892'),
                'longitude': Decimal('51.3890'),
                'instagram_url': 'https://instagram.com/peykantourism',
                'telegram_url': 'https://t.me/peykantourism',
                'whatsapp_number': '+989123456789',
                'facebook_url': 'https://facebook.com/peykantourism',
                'twitter_url': 'https://twitter.com/peykantourism',
                'linkedin_url': 'https://linkedin.com/company/peykantourism',
            }
        )
        self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} contact info")

    def _create_contact_messages(self):
        """Create sample contact messages"""
        self.stdout.write("\n💬 Creating Contact Messages...")
        
        # Get or create test users
        users = []
        for i in range(3):
            user, _ = User.objects.get_or_create(
                username=f'contact_user_{i+1}',
                defaults={
                    'email': f'contact{i+1}@example.com',
                    'first_name': f'Contact',
                    'last_name': f'User{i+1}',
                }
            )
            users.append(user)
        
        messages_data = [
            ('Booking Question', 'I have a question about booking a tour', 'new', 'high'),
            ('Cancellation Request', 'I need to cancel my booking', 'read', 'urgent'),
            ('General Inquiry', 'What tours do you offer?', 'replied', 'medium'),
        ]
        
        for i, (subject, message, status, priority) in enumerate(messages_data):
            msg, created = ContactMessage.objects.get_or_create(
                email=f'contact{i+1}@example.com',
                subject=subject,
                defaults={
                    'full_name': f'Contact User {i+1}',
                    'phone': f'+9891234567{i}',
                    'message': message,
                    'status': status,
                    'priority': priority,
                    'ip_address': '127.0.0.1',
                }
            )
            if created:
                self.stdout.write(f"  ✅ Created message: {subject}")

    def _create_faq_data(self):
        """Create FAQ categories and questions in 3 languages"""
        self.stdout.write("\n❓ Creating FAQ Data...")
        
        # Create categories
        categories_data = [
            ('booking', 'Booking', 'رزرو', 'Rezervasyon', 'fas fa-calendar-check', '#007bff'),
            ('payment', 'Payment', 'پرداخت', 'Ödeme', 'fas fa-credit-card', '#28a745'),
            ('cancellation', 'Cancellation', 'لغو', 'İptal', 'fas fa-times-circle', '#dc3545'),
            ('general', 'General', 'عمومی', 'Genel', 'fas fa-question-circle', '#6c757d'),
        ]
        
        categories = {}
        for slug, en_name, fa_name, tr_name, icon, color in categories_data:
            cat, created = FAQCategory.objects.get_or_create(
                slug=slug,
                defaults={'icon': icon, 'color': color, 'order': len(categories)}
            )
            
            cat.set_current_language('en')
            cat.name = en_name
            cat.description = f'{en_name} related questions'
            cat.save()
            
            cat.set_current_language('fa')
            cat.name = fa_name
            cat.description = f'سوالات مربوط به {fa_name}'
            cat.save()
            
            cat.set_current_language('tr')
            cat.name = tr_name
            cat.description = f'{tr_name} ile ilgili sorular'
            cat.save()
            
            categories[slug] = cat
            self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} category: {slug}")
        
        # Create FAQs
        faqs_data = [
            ('booking', 'How do I book a tour?', 'چگونه تور رزرو کنم؟', 'Nasıl tur rezervasyonu yaparım?',
             'You can book through our website or contact us.', 'از طریق وبسایت یا تماس با ما رزرو کنید.', 'Web sitemizden veya bize ulaşarak rezervasyon yapabilirsiniz.'),
            ('payment', 'What payment methods do you accept?', 'چه روش‌های پرداخت قبول می‌کنید؟', 'Hangi ödeme yöntemlerini kabul ediyorsunuz?',
             'We accept credit cards, bank transfer, and cash.', 'کارت اعتباری، انتقال بانکی و نقدی قبول می‌کنیم.', 'Kredi kartı, banka havalesi ve nakit kabul ediyoruz.'),
            ('cancellation', 'What is your cancellation policy?', 'سیاست لغو شما چیست؟', 'İptal politikanız nedir?',
             'Free cancellation up to 48 hours before tour.', 'لغو رایگان تا ۴۸ ساعت قبل از تور.', 'Turdan 48 saat öncesine kadar ücretsiz iptal.'),
        ]
        
        for cat_slug, en_q, fa_q, tr_q, en_a, fa_a, tr_a in faqs_data:
            # Create FAQ with English
            faq = FAQ.objects.create(
                category=categories[cat_slug],
                question=en_q,
                answer=en_a,
                is_featured=True,
                is_published=True,
            )
            self.stdout.write(f"  ✅ Created FAQ: {en_q[:50]}")

    def _create_support_faqs(self):
        """Create support FAQs"""
        self.stdout.write("\n🆘 Creating Support FAQs...")
        
        support_data = [
            ('booking', 'I need help with booking', 'Hello, I need help with booking a tour.', 1),
            ('cancellation', 'I want to cancel my booking', 'Hello, I would like to cancel my booking.', 2),
            ('transfer', 'Question about transfer service', 'Hello, I have a question about transfer service.', 3),
            ('general', 'General inquiry', 'Hello, I have a general question.', 4),
        ]
        
        for category, question, message, order in support_data:
            faq, created = SupportFAQ.objects.get_or_create(
                category=category,
                question=question,
                defaults={
                    'whatsapp_message': message,
                    'order': order,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f"  ✅ Created support FAQ: {question}")

    def _create_hero_sliders(self):
        """Create hero sliders in 3 languages"""
        self.stdout.write("\n🎬 Creating Hero Sliders...")
        
        # Clear existing sliders first
        HeroSlider.objects.all().delete()
        
        sliders_data = [
            ('Discover Amazing Tours', 'کشف تورهای شگفت‌انگیز', 'Harika Turları Keşfedin',
             'Explore the world with us', 'دنیا را با ما کشف کنید', 'Dünyayı bizimle keşfedin',
             '/tours', 'Explore Tours', 'مشاهده تورها', 'Turları Keşfet', 1),
            ('Adventure Awaits', 'ماجراجویی در انتظار شماست', 'Macera Sizi Bekliyor',
             'Join our exciting adventures', 'به ماجراجویی‌های هیجان‌انگیز ما بپیوندید', 'Heyecan verici maceralarımıza katılın',
             '/tours', 'Book Now', 'رزرو کنید', 'Şimdi Rezervasyon Yap', 2),
            ('Cultural Experiences', 'تجربیات فرهنگی', 'Kültürel Deneyimler',
             'Immerse in local culture', 'در فرهنگ محلی غرق شوید', 'Yerel kültüre dalın',
             '/tours', 'Learn More', 'بیشتر بدانید', 'Daha Fazla Bilgi', 3),
        ]
        
        for en_title, fa_title, tr_title, en_sub, fa_sub, tr_sub, url, en_btn, fa_btn, tr_btn, order in sliders_data:
            slider = HeroSlider.objects.create(
                order=order,
                button_url=url,
                button_type='primary',
                display_duration=5000,
                show_for_authenticated=True,
                show_for_anonymous=True,
            )
            created = True
            
            # English
            slider.set_current_language('en')
            slider.title = en_title
            slider.subtitle = en_sub
            slider.description = f'Experience {en_title.lower()} with our expert guides'
            slider.button_text = en_btn
            slider.save()
            
            # Persian
            slider.set_current_language('fa')
            slider.title = fa_title
            slider.subtitle = fa_sub
            slider.description = f'{fa_title} را با راهنمایان متخصص ما تجربه کنید'
            slider.button_text = fa_btn
            slider.save()
            
            # Turkish
            slider.set_current_language('tr')
            slider.title = tr_title
            slider.subtitle = tr_sub
            slider.description = f'Uzman rehberlerimizle {tr_title.lower()} deneyimleyin'
            slider.button_text = tr_btn
            slider.save()
            
            self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} slider {order}")

    def _create_banners(self):
        """Create banners in 3 languages"""
        self.stdout.write("\n🎨 Creating Banners...")
        
        banners_data = [
            ('homepage_top', 'top', 'Summer Special Offer', 'پیشنهاد ویژه تابستان', 'Yaz Özel Teklifi', '/tours'),
            ('homepage_bottom', 'bottom', 'Book Now & Save', 'همین حالا رزرو کنید', 'Şimdi Rezervasyon Yapın', '/tours'),
            ('sidebar', 'sidebar', 'Popular Tours', 'تورهای محبوب', 'Popüler Turlar', '/tours'),
        ]
        
        for banner_type, position, en_title, fa_title, tr_title, url in banners_data:
            banner, created = Banner.objects.get_or_create(
                banner_type=banner_type,
                position=position,
                defaults={
                    'link_url': url,
                    'link_target': '_self',
                    'display_order': 0,
                    'show_for_authenticated': True,
                    'show_for_anonymous': True,
                }
            )
            
            # English
            banner.set_current_language('en')
            banner.title = en_title
            banner.alt_text = en_title
            banner.save()
            
            # Persian
            banner.set_current_language('fa')
            banner.title = fa_title
            banner.alt_text = fa_title
            banner.save()
            
            # Turkish
            banner.set_current_language('tr')
            banner.title = tr_title
            banner.alt_text = tr_title
            banner.save()
            
            self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} banner: {banner_type}")

    def _create_site_settings(self):
        """Create or update site settings"""
        self.stdout.write("\n⚙️ Creating Site Settings...")
        
        settings = SiteSettings.get_settings()
        settings.site_name = 'Peykan Tourism'
        settings.site_description = 'Your gateway to amazing travel experiences in Iran'
        settings.default_language = 'fa'
        settings.default_phone = '+98 21 1234 5678'
        settings.default_email = 'info@peykantourism.com'
        settings.default_hero_title = 'Welcome to Peykan Tourism'
        settings.default_hero_subtitle = 'Discover Amazing Places'
        settings.default_hero_description = 'Your gateway to amazing travel experiences'
        settings.default_hero_button_text = 'Explore Tours'
        settings.default_hero_button_url = '/tours'
        settings.default_meta_title = 'Peykan Tourism - Travel Agency in Iran'
        settings.default_meta_description = 'Discover Iran with Peykan Tourism. Book tours, transfers, and experiences.'
        settings.maintenance_mode = False
        settings.save()
        
        self.stdout.write("  ✅ Site settings updated")

    def _create_about_section(self):
        """Create About section with statistics and features"""
        self.stdout.write("\n📖 Creating About Section...")
        
        # Create About Section
        about, created = AboutSection.objects.get_or_create(
            slug='main-about',
            defaults={
                'button_url': '/about',
                'is_active': True,
            }
        )
        
        # English
        about.set_current_language('en')
        about.title = 'About Peykan Tourism'
        about.subtitle = 'Your Trusted Travel Partner'
        about.description = 'We are a leading travel agency in Iran, offering exceptional tours and experiences since 2010.'
        about.button_text = 'Learn More'
        about.save()
        
        # Persian
        about.set_current_language('fa')
        about.title = 'درباره پیکان توریسم'
        about.subtitle = 'شریک مطمئن سفر شما'
        about.description = 'ما یک آژانس مسافرتی پیشرو در ایران هستیم که از سال ۱۳۸۹ تورها و تجربیات استثنایی ارائه می‌دهیم.'
        about.button_text = 'بیشتر بدانید'
        about.save()
        
        # Turkish
        about.set_current_language('tr')
        about.title = 'Peykan Tourism Hakkında'
        about.subtitle = 'Güvenilir Seyahat Ortağınız'
        about.description = '2010 yılından beri İran\'da lider bir seyahat acentesiyiz ve olağanüstü turlar sunuyoruz.'
        about.button_text = 'Daha Fazla Bilgi'
        about.save()
        
        self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} about section")
        
        # Create Statistics
        stats_data = [
            ('stat-customers', '10000+', 'Happy Customers', 'مشتری راضی', 'Mutlu Müşteri', 1),
            ('stat-tours', '500+', 'Tours Completed', 'تور انجام شده', 'Tamamlanan Tur', 2),
            ('stat-experience', '15+', 'Years Experience', 'سال تجربه', 'Yıl Deneyim', 3),
            ('stat-destinations', '50+', 'Destinations', 'مقصد', 'Destinasyon', 4),
        ]
        
        for slug, value, en_label, fa_label, tr_label, order in stats_data:
            stat, created = AboutStatistic.objects.get_or_create(
                slug=slug,
                defaults={'value': value, 'order': order}
            )
            
            stat.set_current_language('en')
            stat.label = en_label
            stat.save()
            
            stat.set_current_language('fa')
            stat.label = fa_label
            stat.save()
            
            stat.set_current_language('tr')
            stat.label = tr_label
            stat.save()
            
            if created:
                self.stdout.write(f"  ✅ Created statistic: {value}")
        
        # Create Features
        features_data = [
            ('feature-guides', 'Expert Guides', 'راهنمایان متخصص', 'Uzman Rehberler', 'fas fa-user-tie', 1),
            ('feature-prices', 'Best Prices', 'بهترین قیمت‌ها', 'En İyi Fiyatlar', 'fas fa-dollar-sign', 2),
            ('feature-support', '24/7 Support', 'پشتیبانی ۲۴/۷', '7/24 Destek', 'fas fa-headset', 3),
        ]
        
        for slug, en_title, fa_title, tr_title, icon, order in features_data:
            feature, created = AboutFeature.objects.get_or_create(
                slug=slug,
                defaults={'icon': icon, 'order': order}
            )
            
            feature.set_current_language('en')
            feature.title = en_title
            feature.description = f'We provide {en_title.lower()} for all our customers'
            feature.save()
            
            feature.set_current_language('fa')
            feature.title = fa_title
            feature.description = f'ما {fa_title} را برای همه مشتریان خود فراهم می‌کنیم'
            feature.save()
            
            feature.set_current_language('tr')
            feature.title = tr_title
            feature.description = f'Tüm müşterilerimize {tr_title.lower()} sağlıyoruz'
            feature.save()
            
            if created:
                self.stdout.write(f"  ✅ Created feature: {en_title}")

    def _create_cta_section(self):
        """Create CTA section with buttons and features"""
        self.stdout.write("\n📣 Creating CTA Section...")
        
        # Create CTA Section
        cta, created = CTASection.objects.get_or_create(
            slug='main-cta',
            defaults={
                'is_active': True,
            }
        )
        
        # English
        cta.set_current_language('en')
        cta.title = 'Ready for Your Next Adventure?'
        cta.subtitle = 'Book your dream tour today'
        cta.description = 'Join thousands of happy travelers and create unforgettable memories'
        cta.save()
        
        # Persian
        cta.set_current_language('fa')
        cta.title = 'آماده ماجراجویی بعدی خود هستید؟'
        cta.subtitle = 'تور رویایی خود را امروز رزرو کنید'
        cta.description = 'به هزاران مسافر خوشحال بپیوندید و خاطرات فراموش‌نشدنی بسازید'
        cta.save()
        
        # Turkish
        cta.set_current_language('tr')
        cta.title = 'Bir Sonraki Maceranız İçin Hazır mısınız?'
        cta.subtitle = 'Hayalinizdeki turu bugün rezerve edin'
        cta.description = 'Binlerce mutlu gezgine katılın ve unutulmaz anılar yaratın'
        cta.save()
        
        self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} CTA section")
        
        # Create CTA Buttons
        buttons_data = [
            ('cta-btn-tours', 'Browse Tours', 'مشاهده تورها', 'Turları İncele', '/tours', 'primary', 1),
            ('cta-btn-contact', 'Contact Us', 'تماس با ما', 'Bize Ulaşın', '/contact', 'secondary', 2),
        ]
        
        for slug, en_text, fa_text, tr_text, url, btn_type, order in buttons_data:
            button, created = CTAButton.objects.get_or_create(
                slug=slug,
                defaults={'cta_section': cta, 'url': url, 'button_type': btn_type, 'order': order}
            )
            
            button.set_current_language('en')
            button.text = en_text
            button.save()
            
            button.set_current_language('fa')
            button.text = fa_text
            button.save()
            
            button.set_current_language('tr')
            button.text = tr_text
            button.save()
            
            if created:
                self.stdout.write(f"  ✅ Created CTA button: {en_text}")
        
        # Create CTA Features
        features_data = [
            ('cta-feat-price', 'Best Price Guarantee', 'تضمین بهترین قیمت', 'En İyi Fiyat Garantisi', 'fas fa-check-circle', 1),
            ('cta-feat-cancel', 'Free Cancellation', 'لغو رایگان', 'Ücretsiz İptal', 'fas fa-times-circle', 2),
            ('cta-feat-support', '24/7 Support', 'پشتیبانی ۲۴/۷', '7/24 Destek', 'fas fa-headset', 3),
        ]
        
        for slug, en_text, fa_text, tr_text, icon, order in features_data:
            feature, created = CTAFeature.objects.get_or_create(
                slug=slug,
                defaults={'cta_section': cta, 'icon': icon, 'order': order}
            )
            
            feature.set_current_language('en')
            feature.text = en_text
            feature.save()
            
            feature.set_current_language('fa')
            feature.text = fa_text
            feature.save()
            
            feature.set_current_language('tr')
            feature.text = tr_text
            feature.save()
            
            if created:
                self.stdout.write(f"  ✅ Created CTA feature: {en_text}")

    def _create_footer(self):
        """Create footer with links"""
        self.stdout.write("\n🦶 Creating Footer...")
        
        # Create Footer
        footer, created = Footer.objects.get_or_create(
            slug='main-footer',
            defaults={
                'default_phone': '+98 21 1234 5678',
                'default_email': 'info@peykantourism.com',
                'is_active': True,
            }
        )
        
        # English
        footer.set_current_language('en')
        footer.copyright_text = '© 2024 Peykan Tourism. All rights reserved.'
        footer.company_name = 'Peykan Tourism'
        footer.company_description = 'Your trusted travel partner in Iran'
        footer.newsletter_title = 'Subscribe to Newsletter'
        footer.newsletter_description = 'Get latest tours and offers'
        footer.newsletter_placeholder = 'Enter your email'
        footer.trusted_by_text = 'Trusted by 50K+ travelers'
        footer.save()
        
        # Persian
        footer.set_current_language('fa')
        footer.copyright_text = '© ۱۴۰۳ پیکان توریسم. تمامی حقوق محفوظ است.'
        footer.company_name = 'پیکان توریسم'
        footer.company_description = 'شریک مطمئن سفر شما در ایران'
        footer.newsletter_title = 'عضویت در خبرنامه'
        footer.newsletter_description = 'آخرین تورها و پیشنهادات را دریافت کنید'
        footer.newsletter_placeholder = 'ایمیل خود را وارد کنید'
        footer.trusted_by_text = 'مورد اعتماد بیش از ۵۰ هزار مسافر'
        footer.save()
        
        # Turkish
        footer.set_current_language('tr')
        footer.copyright_text = '© 2024 Peykan Tourism. Tüm hakları saklıdır.'
        footer.company_name = 'Peykan Tourism'
        footer.company_description = 'İran\'daki güvenilir seyahat ortağınız'
        footer.newsletter_title = 'Bültene Abone Ol'
        footer.newsletter_description = 'En son turları ve teklifleri alın'
        footer.newsletter_placeholder = 'E-postanızı girin'
        footer.trusted_by_text = '50K+ gezgin tarafından güvenilir'
        footer.save()
        
        self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} footer")
        
        # Create Footer Links
        links_data = [
            ('footer-about', 'About Us', 'درباره ما', 'Hakkımızda', '/about', 'internal', 1),
            ('footer-tours', 'Tours', 'تورها', 'Turlar', '/tours', 'internal', 2),
            ('footer-contact', 'Contact', 'تماس', 'İletişim', '/contact', 'internal', 3),
            ('footer-terms', 'Terms', 'قوانین', 'Şartlar', '/terms', 'internal', 4),
            ('footer-privacy', 'Privacy', 'حریم خصوصی', 'Gizlilik', '/privacy', 'internal', 5),
            ('footer-faq', 'FAQ', 'سوالات', 'SSS', '/faq', 'internal', 6),
        ]
        
        for slug, en_text, fa_text, tr_text, url, link_type, order in links_data:
            link, created = FooterLink.objects.get_or_create(
                slug=slug,
                defaults={'footer': footer, 'url': url, 'link_type': link_type, 'order': order}
            )
            
            link.set_current_language('en')
            link.label = en_text
            link.save()
            
            link.set_current_language('fa')
            link.label = fa_text
            link.save()
            
            link.set_current_language('tr')
            link.label = tr_text
            link.save()
            
            if created:
                self.stdout.write(f"  ✅ Created footer link: {en_text}")

    def _create_transfer_booking_section(self):
        """Create transfer booking section"""
        self.stdout.write("\n🚗 Creating Transfer Booking Section...")
        
        transfer, created = TransferBookingSection.objects.get_or_create(
            slug='main-transfer',
            defaults={
                'button_url': '/transfers/booking',
                'experience_years': 20,
                'countries_served': 100,
                'is_active': True,
            }
        )
        
        # English
        transfer.set_current_language('en')
        transfer.title = 'Book Your Transfer'
        transfer.subtitle = 'Comfortable and reliable transportation'
        transfer.description = 'Book airport transfers and city transportation with ease'
        transfer.button_text = 'Book Transfer'
        transfer.feature_1 = 'Luxury vehicles'
        transfer.feature_2 = 'Professional drivers'
        transfer.feature_3 = '24/7 tracking'
        transfer.feature_4 = 'Complete safety'
        transfer.save()
        
        # Persian
        transfer.set_current_language('fa')
        transfer.title = 'رزرو ترانسفر'
        transfer.subtitle = 'حمل و نقل راحت و قابل اعتماد'
        transfer.description = 'ترانسفر فرودگاه و حمل و نقل شهری را به راحتی رزرو کنید'
        transfer.button_text = 'رزرو ترانسفر'
        transfer.feature_1 = 'خودروهای لوکس'
        transfer.feature_2 = 'رانندگان حرفه‌ای'
        transfer.feature_3 = 'ردیابی ۲۴/۷'
        transfer.feature_4 = 'ایمنی کامل'
        transfer.save()
        
        # Turkish
        transfer.set_current_language('tr')
        transfer.title = 'Transfer Rezervasyonu'
        transfer.subtitle = 'Konforlu ve güvenilir ulaşım'
        transfer.description = 'Havaalanı transferi ve şehir içi ulaşımı kolayca rezerve edin'
        transfer.button_text = 'Transfer Rezerve Et'
        transfer.feature_1 = 'Lüks araçlar'
        transfer.feature_2 = 'Profesyonel sürücüler'
        transfer.feature_3 = '7/24 takip'
        transfer.feature_4 = 'Tam güvenlik'
        transfer.save()
        
        self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} transfer section")

    def _create_navigation_menu(self):
        """Create navigation menu"""
        self.stdout.write("\n🧭 Creating Navigation Menu...")
        
        menu_items = [
            ('Home', 'خانه', 'Ana Sayfa', '/', 1),
            ('Tours', 'تورها', 'Turlar', '/tours', 2),
            ('About', 'درباره ما', 'Hakkımızda', '/about', 3),
            ('Contact', 'تماس', 'İletişim', '/contact', 4),
        ]
        
        for en_title, fa_title, tr_title, url, order in menu_items:
            menu, created = NavigationMenu.objects.get_or_create(
                slug=en_title.lower(),
                defaults={
                    'url': url,
                    'order': order,
                    'is_active': True,
                    'target_blank': False,
                    'is_external': False,
                }
            )
            
            menu.set_current_language('en')
            menu.label = en_title
            menu.save()
            
            menu.set_current_language('fa')
            menu.label = fa_title
            menu.save()
            
            menu.set_current_language('tr')
            menu.label = tr_title
            menu.save()
            
            self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} menu: {en_title}")

    def _create_faq_settings(self):
        """Create FAQ settings"""
        self.stdout.write("\n❓ Creating FAQ Settings...")
        
        faq_settings, created = FAQSettings.objects.get_or_create(
            slug='main-faq',
            defaults={
                'show_search': True,
                'show_categories': True,
                'items_per_page': 10,
                'is_active': True,
            }
        )
        
        # English
        faq_settings.set_current_language('en')
        faq_settings.title = 'Frequently Asked Questions'
        faq_settings.subtitle = 'Find answers to common questions'
        faq_settings.save()
        
        # Persian
        faq_settings.set_current_language('fa')
        faq_settings.title = 'سوالات متداول'
        faq_settings.subtitle = 'پاسخ سوالات رایج را پیدا کنید'
        faq_settings.save()
        
        # Turkish
        faq_settings.set_current_language('tr')
        faq_settings.title = 'Sık Sorulan Sorular'
        faq_settings.subtitle = 'Yaygın soruların cevaplarını bulun'
        faq_settings.save()
        
        self.stdout.write(f"  {'✅ Created' if created else '📋 Updated'} FAQ settings")
