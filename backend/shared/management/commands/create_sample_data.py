"""
Management command to create sample data for shared models.
"""

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from shared.models import ContactInfo, AboutSection, CTASection, Footer, SupportFAQ


class Command(BaseCommand):
    help = 'Create sample data for shared models'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create ContactInfo
        contact_info, created = ContactInfo.objects.get_or_create(
            company_name='Peykan Tourism',
            defaults={
                'address': 'Istanbul, Turkey',
                'phone_primary': '+90 212 555 0123',
                'phone_secondary': '+90 212 555 0124',
                'email_general': 'info@peykantravelistanbul.com',
                'email_support': 'support@peykantravelistanbul.com',
                'email_sales': 'sales@peykantravelistanbul.com',
                'working_hours': '9:00 AM - 6:00 PM',
                'working_days': 'Monday - Friday',
                'latitude': 41.0082,
                'longitude': 28.9784,
                'instagram_url': 'https://instagram.com/peykantravel',
                'telegram_url': 'https://t.me/peykansupport',
                'whatsapp_number': '+90 555 123 4567',
                'facebook_url': 'https://facebook.com/peykantravel',
                'twitter_url': 'https://twitter.com/peykantravel',
                'linkedin_url': 'https://linkedin.com/company/peykantravel',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created ContactInfo'))
        else:
            self.stdout.write('ContactInfo already exists')
        
        # Create AboutSection
        about_section, created = AboutSection.objects.get_or_create(
            is_active=True,
            defaults={
                'button_url': 'https://peykantravelistanbul.com/about',
                'is_active': True
            }
        )
        
        if created:
            # Set translations
            about_section.set_current_language('en')
            about_section.title = 'About Peykan Tourism'
            about_section.subtitle = 'Your Trusted Travel Partner'
            about_section.description = 'We are a leading tourism company providing exceptional travel experiences in Istanbul and Turkey.'
            about_section.button_text = 'Learn More'
            about_section.save()
            
            about_section.set_current_language('fa')
            about_section.title = 'درباره پیکان توریسم'
            about_section.subtitle = 'شریک سفر قابل اعتماد شما'
            about_section.description = 'ما یک شرکت پیشرو در صنعت گردشگری هستیم که تجربیات سفر استثنایی در استانبول و ترکیه ارائه می‌دهیم.'
            about_section.button_text = 'بیشتر بدانید'
            about_section.save()
            
            about_section.set_current_language('tr')
            about_section.title = 'Peykan Turizm Hakkında'
            about_section.subtitle = 'Güvenilir Seyahat Ortağınız'
            about_section.description = 'İstanbul ve Türkiye\'de olağanüstü seyahat deneyimleri sunan önde gelen bir turizm şirketiyiz.'
            about_section.button_text = 'Daha Fazla Bilgi'
            about_section.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created AboutSection'))
        else:
            self.stdout.write('AboutSection already exists')
        
        # Create CTASection
        cta_section, created = CTASection.objects.get_or_create(
            is_active=True,
            defaults={
                'is_active': True
            }
        )
        
        if created:
            # Set translations
            cta_section.set_current_language('en')
            cta_section.title = 'Ready to Explore Istanbul?'
            cta_section.subtitle = 'Start Your Journey Today'
            cta_section.description = 'Book your perfect tour today and discover the magic of Istanbul.'
            cta_section.button_text = 'Book Now'
            cta_section.save()
            
            cta_section.set_current_language('fa')
            cta_section.title = 'آماده کشف استانبول هستید؟'
            cta_section.subtitle = 'سفر خود را امروز شروع کنید'
            cta_section.description = 'تور ایده‌آل خود را امروز رزرو کنید و جادوی استانبول را کشف کنید.'
            cta_section.button_text = 'رزرو کنید'
            cta_section.save()
            
            cta_section.set_current_language('tr')
            cta_section.title = 'İstanbul\'u Keşfetmeye Hazır mısınız?'
            cta_section.subtitle = 'Yolculuğunuza Bugün Başlayın'
            cta_section.description = 'Mükemmel turunuzu bugün rezerve edin ve İstanbul\'un büyüsünü keşfedin.'
            cta_section.button_text = 'Rezerve Et'
            cta_section.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created CTASection'))
        else:
            self.stdout.write('CTASection already exists')
        
        # Create Footer
        footer, created = Footer.objects.get_or_create(
            is_active=True,
            defaults={
                'default_phone': '+90 212 555 0123',
                'default_email': 'info@peykantravelistanbul.com',
                'instagram_url': 'https://instagram.com/peykantravel',
                'telegram_url': 'https://t.me/peykansupport',
                'whatsapp_number': '+90 555 123 4567',
                'facebook_url': 'https://facebook.com/peykantravel',
                'is_active': True
            }
        )
        
        if created:
            # Set translations
            footer.set_current_language('en')
            footer.newsletter_title = 'Newsletter'
            footer.newsletter_description = 'Get exclusive deals, travel tips, and destination highlights delivered to your inbox.'
            footer.company_name = 'Peykan Tourism'
            footer.company_description = 'Your travel companion'
            footer.copyright_text = '© 2024 Peykan Tourism'
            footer.newsletter_placeholder = 'Enter your email'
            footer.trusted_by_text = 'Trusted by 50K+ travelers'
            footer.save()
            
            footer.set_current_language('fa')
            footer.newsletter_title = 'خبرنامه'
            footer.newsletter_description = 'پیشنهادات ویژه، نکات سفر و نکات برجسته مقاصد را در صندوق ورودی خود دریافت کنید.'
            footer.company_name = 'پیکان توریسم'
            footer.company_description = 'همراه سفر شما'
            footer.copyright_text = '© 2024 پیکان توریسم'
            footer.newsletter_placeholder = 'ایمیل خود را وارد کنید'
            footer.trusted_by_text = 'مورد اعتماد بیش از 50 هزار مسافر'
            footer.save()
            
            footer.set_current_language('tr')
            footer.newsletter_title = 'Bülten'
            footer.newsletter_description = 'Özel fırsatlar, seyahat ipuçları ve destinasyon öne çıkanlarını gelen kutunuza alın.'
            footer.company_name = 'Peykan Turizm'
            footer.company_description = 'Seyahat arkadaşınız'
            footer.copyright_text = '© 2024 Peykan Turizm'
            footer.newsletter_placeholder = 'E-postanızı girin'
            footer.trusted_by_text = '50K+ gezgin tarafından güveniliyor'
            footer.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Footer'))
        else:
            self.stdout.write('Footer already exists')
        
        # Create SupportFAQs
        support_faqs_data = [
            {
                'category': 'booking',
                'order': 1,
                'is_active': True,
                'translations': {
                    'en': {
                        'category_display': 'Booking',
                        'question': 'How can I book a tour?',
                        'whatsapp_message': 'Hello, I would like to book a tour. Can you help me?'
                    },
                    'fa': {
                        'category_display': 'رزرو',
                        'question': 'چگونه می‌توانم تور رزرو کنم؟',
                        'whatsapp_message': 'سلام، می‌خواهم تور رزرو کنم. می‌توانید کمکم کنید؟'
                    },
                    'tr': {
                        'category_display': 'Rezervasyon',
                        'question': 'Nasıl tur rezerve edebilirim?',
                        'whatsapp_message': 'Merhaba, tur rezerve etmek istiyorum. Bana yardımcı olabilir misiniz?'
                    }
                }
            },
            {
                'category': 'cancellation',
                'order': 2,
                'is_active': True,
                'translations': {
                    'en': {
                        'category_display': 'Cancellation',
                        'question': 'What is your cancellation policy?',
                        'whatsapp_message': 'Hello, I need information about your cancellation policy.'
                    },
                    'fa': {
                        'category_display': 'لغو',
                        'question': 'سیاست لغو شما چیست؟',
                        'whatsapp_message': 'سلام، در مورد سیاست لغو شما اطلاعات می‌خواهم.'
                    },
                    'tr': {
                        'category_display': 'İptal',
                        'question': 'İptal politikanız nedir?',
                        'whatsapp_message': 'Merhaba, iptal politikanız hakkında bilgi almak istiyorum.'
                    }
                }
            },
            {
                'category': 'transfer',
                'order': 3,
                'is_active': True,
                'translations': {
                    'en': {
                        'category_display': 'Transfer',
                        'question': 'Do you provide airport transfers?',
                        'whatsapp_message': 'Hello, I need airport transfer service.'
                    },
                    'fa': {
                        'category_display': 'ترانسفر',
                        'question': 'آیا ترانسفر فرودگاه ارائه می‌دهید؟',
                        'whatsapp_message': 'سلام، به سرویس ترانسفر فرودگاه نیاز دارم.'
                    },
                    'tr': {
                        'category_display': 'Transfer',
                        'question': 'Havaalanı transferi sağlıyor musunuz?',
                        'whatsapp_message': 'Merhaba, havaalanı transfer hizmetine ihtiyacım var.'
                    }
                }
            },
            {
                'category': 'general',
                'order': 4,
                'is_active': True,
                'translations': {
                    'en': {
                        'category_display': 'General',
                        'question': 'What are your working hours?',
                        'whatsapp_message': 'Hello, what are your working hours?'
                    },
                    'fa': {
                        'category_display': 'عمومی',
                        'question': 'ساعات کاری شما چیست؟',
                        'whatsapp_message': 'سلام، ساعات کاری شما چیست؟'
                    },
                    'tr': {
                        'category_display': 'Genel',
                        'question': 'Çalışma saatleriniz nedir?',
                        'whatsapp_message': 'Merhaba, çalışma saatleriniz nedir?'
                    }
                }
            }
        ]
        
        for faq_data in support_faqs_data:
            # Create separate FAQ for each language
            for lang, translation in faq_data['translations'].items():
                faq, created = SupportFAQ.objects.get_or_create(
                    category=faq_data['category'],
                    question=translation['question'],
                    defaults={
                        'whatsapp_message': translation['whatsapp_message'],
                        'order': faq_data['order'],
                        'is_active': faq_data['is_active']
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created SupportFAQ ({lang}): {translation["question"]}'))
                else:
                    self.stdout.write(f'SupportFAQ already exists ({lang}): {translation["question"]}')
        
        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))
