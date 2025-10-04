from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date, timedelta, time
from decimal import Decimal
from events.models import (
    EventCategory,
    Venue,
    Artist,
    Event,
    TicketType,
    EventPerformance,
    EventSection,
    SectionTicketType,
    EventOption,
    Seat,
)
from django.db import transaction
from django.utils.translation import activate


class Command(BaseCommand):
    help = 'Create a complete test Event with 2 performances, 3 sections, 10 seats per section, options, and multilingual support'

    def add_arguments(self, parser):
        parser.add_argument('--slug', default='complete-test-event', help='Event slug')
        parser.add_argument('--title', default='Complete Test Event', help='Event title')
        parser.add_argument('--style', default='music', help='Event style (music/sports/theater/...)')
        parser.add_argument('--base-price', type=float, default=50.0, help='Base price per section')
        parser.add_argument('--currency', default='USD', help='Currency')

    @transaction.atomic
    def handle(self, *args, **options):
        slug = options['slug']
        title = options['title']
        style = options['style']
        base_price = Decimal(str(options['base_price']))
        currency = options['currency']

        # Create or get category
        category, _ = EventCategory.objects.get_or_create(
            slug='test-category',
            defaults={}
        )
        
        # Set category translations
        for lang_code, lang_name in [('en', 'Concert'), ('fa', 'کنسرت'), ('tr', 'Konser')]:
            category.set_current_language(lang_code)
            category.name = lang_name
            category.description = f'{lang_name} events'
            category.save()

        # Create or get venue
        venue, _ = Venue.objects.get_or_create(
            slug='test-venue',
            defaults={
                'address': '123 Test Street',
                'city': 'Tehran',
                'country': 'Iran',
                'total_capacity': 1000,
                'coordinates': {'lat': 35.6892, 'lng': 51.3890},
                'facilities': ['parking', 'restaurant', 'bar', 'wifi', 'air_conditioning'],
            }
        )
        
        # Set venue translations
        venue_translations = {
            'en': {'name': 'Grand Concert Hall', 'description': 'A magnificent venue for concerts and events'},
            'fa': {'name': 'تالار بزرگ کنسرت', 'description': 'محل برگزاری مجلل برای کنسرت‌ها و رویدادها'},
            'tr': {'name': 'Buyuk Konser Salonu', 'description': 'Konserler ve etkinlikler icin muhtesem bir mekan'}
        }
        
        for lang_code, translation in venue_translations.items():
            venue.set_current_language(lang_code)
            venue.name = translation['name']
            venue.description = translation['description']
            venue.save()

        # Create or get artists
        artists = []
        artist_data = [
            {
                'slug': 'test-artist-1',
                'translations': {
                    'en': {'name': 'John Smith', 'bio': 'Renowned musician with 20 years of experience'},
                    'fa': {'name': 'جان اسمیت', 'bio': 'موسیقیدان مشهور با ۲۰ سال تجربه'},
                    'tr': {'name': 'John Smith', 'bio': '20 yıllık deneyime sahip ünlü müzisyen'}
                }
            },
            {
                'slug': 'test-artist-2',
                'translations': {
                    'en': {'name': 'Sarah Johnson', 'bio': 'Award-winning vocalist and songwriter'},
                    'fa': {'name': 'سارا جانسون', 'bio': 'خواننده و ترانه‌سرای برنده جایزه'},
                    'tr': {'name': 'Sarah Johnson', 'bio': 'Ödüllü vokalist ve şarkı yazarı'}
                }
            }
        ]
        
        for artist_info in artist_data:
            artist, _ = Artist.objects.get_or_create(
                slug=artist_info['slug'],
                defaults={}
            )
            
            for lang_code, translation in artist_info['translations'].items():
                artist.set_current_language(lang_code)
                artist.name = translation['name']
                artist.bio = translation['bio']
                artist.save()
            
            artists.append(artist)

        # Create event
        event, created = Event.objects.get_or_create(
            slug=slug,
            defaults={
                'style': style,
                'category': category,
                'venue': venue,
                'door_open_time': time(18, 0),
                'start_time': time(19, 0),
                'end_time': time(22, 0),
                'price': base_price,
                'currency': currency,
                'city': 'Tehran',
                'country': 'Iran',
                'age_restriction': 16,
                'is_featured': True,
                'is_popular': True,
                'is_special': True,
                'is_seasonal': False,
            }
        )
        
        # Add artists to event
        event.artists.set(artists)
        
        # Set event translations
        event_translations = {
            'en': {
                'title': 'Complete Test Event',
                'description': 'A comprehensive test event featuring amazing performances, multiple sections, and various options. This event includes everything needed to test the booking system.',
                'short_description': 'Comprehensive test event with multiple sections and options',
                'highlights': '• Live music performance\n• Multiple seating sections\n• Various ticket options\n• Food and beverage options\n• Parking available',
                'rules': '• No smoking in the venue\n• Photography allowed\n• Age restriction: 16+\n• Valid ID required\n• No outside food or drinks',
                'required_items': '• Valid ID\n• Ticket confirmation\n• Face mask (recommended)'
            },
            'fa': {
                'title': 'رویداد تست کامل',
                'description': 'یک رویداد تست جامع با اجراهای فوق‌العاده، بخش‌های متعدد و گزینه‌های مختلف. این رویداد شامل همه چیزهای مورد نیاز برای تست سیستم رزرو است.',
                'short_description': 'رویداد تست جامع با بخش‌های متعدد و گزینه‌ها',
                'highlights': '• اجرای موسیقی زنده\n• بخش‌های نشست متعدد\n• گزینه‌های بلیط مختلف\n• گزینه‌های غذا و نوشیدنی\n• پارکینگ موجود',
                'rules': '• ممنوعیت سیگار در محل\n• عکاسی مجاز\n• محدودیت سنی: ۱۶+\n• کارت شناسایی معتبر\n• ممنوعیت غذا و نوشیدنی خارجی',
                'required_items': '• کارت شناسایی معتبر\n• تأیید بلیط\n• ماسک صورت (توصیه می‌شود)'
            },
            'tr': {
                'title': 'Tam Test Etkinliği',
                'description': 'Harika performanslar, çoklu bölümler ve çeşitli seçenekler içeren kapsamlı bir test etkinliği. Bu etkinlik rezervasyon sistemini test etmek için gereken her şeyi içerir.',
                'short_description': 'Çoklu bölümler ve seçeneklerle kapsamlı test etkinliği',
                'highlights': '• Canlı müzik performansı\n• Çoklu oturma bölümleri\n• Çeşitli bilet seçenekleri\n• Yemek ve içecek seçenekleri\n• Otopark mevcut',
                'rules': '• Mekanda sigara yasak\n• Fotoğraf çekimi serbest\n• Yaş sınırı: 16+\n• Geçerli kimlik gerekli\n• Dışarıdan yiyecek/içecek yasak',
                'required_items': '• Geçerli kimlik\n• Bilet onayı\n• Yüz maskesi (önerilen)'
            }
        }
        
        for lang_code, translation in event_translations.items():
            event.set_current_language(lang_code)
            for field, value in translation.items():
                setattr(event, field, value)
            event.save()

        # Create ticket types
        ticket_type_specs = [
            {
                'name': 'VIP',
                'code': 'vip',
                'multiplier': Decimal('2.5'),
                'capacity': 200,
                'translations': {
                    'en': {'description': 'Premium VIP experience with exclusive benefits'},
                    'fa': {'description': 'تجربه VIP پریمیوم با مزایای انحصاری'},
                    'tr': {'description': 'Özel avantajlarla premium VIP deneyimi'}
                }
            },
            {
                'name': 'Normal',
                'code': 'normal',
                'multiplier': Decimal('1.0'),
                'capacity': 500,
                'translations': {
                    'en': {'description': 'Standard seating with good view'},
                    'fa': {'description': 'نشست استاندارد با دید خوب'},
                    'tr': {'description': 'İyi manzaralı standart oturma'}
                }
            },
            {
                'name': 'Economy',
                'code': 'economy',
                'multiplier': Decimal('0.7'),
                'capacity': 300,
                'translations': {
                    'en': {'description': 'Budget-friendly seating option'},
                    'fa': {'description': 'گزینه نشست مقرون به صرفه'},
                    'tr': {'description': 'Bütçe dostu oturma seçeneği'}
                }
            }
        ]
        
        ticket_types = []
        for spec in ticket_type_specs:
            tt, _ = TicketType.objects.get_or_create(
                event=event,
                name=spec['name'],
                defaults={
                    'ticket_type': spec['code'],
                    'benefits': ['Standard amenities', 'Event access'],
                    'price_modifier': spec['multiplier'],
                    'capacity': spec['capacity'],
                    'is_active': True,
                    'description': spec['translations']['en']['description'],  # Use English description
                }
            )
            
            ticket_types.append(tt)

        # Create event options
        option_specs = [
            {
                'name': 'Parking Pass',
                'code': 'parking',
                'price': Decimal('15.00'),
                'option_type': 'service',
                'translations': {
                    'en': {'description': 'Reserved parking space for the event'},
                    'fa': {'description': 'جای پارک رزرو شده برای رویداد'},
                    'tr': {'description': 'Etkinlik için ayrılmış otopark yeri'}
                }
            },
            {
                'name': 'Food Package',
                'code': 'food',
                'price': Decimal('25.00'),
                'option_type': 'food',
                'translations': {
                    'en': {'description': 'Delicious meal package with drinks'},
                    'fa': {'description': 'بسته غذای خوشمزه با نوشیدنی'},
                    'tr': {'description': 'İçeceklerle birlikte lezzetli yemek paketi'}
                }
            },
            {
                'name': 'Merchandise Bundle',
                'code': 'merch',
                'price': Decimal('35.00'),
                'option_type': 'merchandise',
                'translations': {
                    'en': {'description': 'Exclusive merchandise bundle'},
                    'fa': {'description': 'بسته کالای انحصاری'},
                    'tr': {'description': 'Özel ürün paketi'}
                }
            },
            {
                'name': 'Meet & Greet',
                'code': 'meet_greet',
                'price': Decimal('50.00'),
                'option_type': 'experience',
                'translations': {
                    'en': {'description': 'Meet the artists after the show'},
                    'fa': {'description': 'ملاقات با هنرمندان بعد از نمایش'},
                    'tr': {'description': 'Gösteri sonrası sanatçılarla tanışma'}
                }
            }
        ]
        
        for spec in option_specs:
            option, _ = EventOption.objects.get_or_create(
                event=event,
                name=spec['name'],
                defaults={
                    'price': spec['price'],
                    'currency': currency,
                    'option_type': spec['option_type'],
                    'is_available': True,
                    'max_quantity': 5,
                    'description': spec['translations']['en']['description'],  # Use English description
                }
            )

        # Create performances (2 performances)
        performances = []
        for i in range(1, 3):
            perf_date = date.today() + timedelta(days=i)
            perf, _ = EventPerformance.objects.get_or_create(
                event=event,
                date=perf_date,
                defaults={
                    'start_date': perf_date,
                    'end_date': perf_date,
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'is_available': True,
                    'max_capacity': 1000,
                    'current_capacity': 0,
                    'is_special': i == 1,  # First performance is special
                }
            )
            performances.append(perf)

        # Create sections (3 sections per performance)
        section_names = ['A', 'B', 'C']
        seats_per_section = 10
        
        for perf in performances:
            for sec_name in section_names:
                # Create section
                section, _ = EventSection.objects.get_or_create(
                    performance=perf,
                    name=sec_name,
                    defaults={
                        'description': f'Section {sec_name}',
                        'total_capacity': seats_per_section * len(ticket_types),
                        'base_price': base_price,
                        'currency': currency,
                        'is_wheelchair_accessible': sec_name == 'A',  # Section A is wheelchair accessible
                        'is_premium': sec_name == 'A',  # Section A is premium
                    },
                )

                # Create ticket allocations for each section
                for tt in ticket_types:
                    SectionTicketType.objects.get_or_create(
                        section=section,
                        ticket_type=tt,
                        defaults={
                            'price_modifier': Decimal('1.00'),
                        },
                    )

                # Generate seats for this section
                for seat_num in range(1, seats_per_section + 1):
                    Seat.objects.get_or_create(
                        performance=perf,
                        seat_number=str(seat_num),
                        row_number='1',
                        section=sec_name,
                        defaults={
                            'price': base_price,
                            'currency': currency,
                            'is_premium': sec_name == 'A',
                            'is_wheelchair_accessible': sec_name == 'A',
                            'status': 'available',
                        },
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Created complete test event with slug '{slug}'")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(performances)} performances")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(ticket_types)} ticket types")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(option_specs)} event options")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created venue: Grand Concert Hall")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(artists)} artists")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Added translations for EN, FA, TR")
        )
        self.stdout.write(
            self.style.SUCCESS("Event is ready for testing with complete multilingual support!")
        )
