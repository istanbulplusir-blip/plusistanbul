"""
Django management command to create a complete sample event with 3 languages.
Usage: python manage.py create_sample_event
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from events.models import (
    Event, EventCategory, Venue, Artist, TicketType,
    EventPerformance, EventSection, SectionTicketType, Seat,
    EventOption, EventCancellationPolicy
)
from parler.utils.context import switch_language


class Command(BaseCommand):
    help = 'Create a complete sample event with 3 languages (Persian, English, Arabic)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample event with 3 languages...'))

        # 1. Create Event Category
        self.stdout.write('Creating event category...')
        category = self.create_category()

        # 2. Create Venue
        self.stdout.write('Creating venue...')
        venue = self.create_venue()

        # 3. Create Artists
        self.stdout.write('Creating artists...')
        artist1, artist2 = self.create_artists()

        # 4. Create Event
        self.stdout.write('Creating event...')
        event = self.create_event(category, venue)
        event.artists.add(artist1, artist2)

        # 5. Create Ticket Types
        self.stdout.write('Creating ticket types...')
        ticket_types = self.create_ticket_types(event)

        # 6. Create Event Options
        self.stdout.write('Creating event options...')
        self.create_event_options(event)

        # 7. Create Cancellation Policies
        self.stdout.write('Creating cancellation policies...')
        self.create_cancellation_policies(event)

        # 8. Create Performances
        self.stdout.write('Creating performances...')
        performances = self.create_performances(event)

        # 9. Create Sections and Seats for each performance
        self.stdout.write('Creating sections and seats...')
        for performance in performances:
            self.create_sections_and_seats(performance, ticket_types)

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created event: {event.slug}'))
        self.stdout.write(self.style.SUCCESS(f'Event ID: {event.id}'))
        self.stdout.write(self.style.SUCCESS(f'Total Performances: {len(performances)}'))
        self.stdout.write(self.style.SUCCESS('\nYou can now view this event in the admin panel or API.'))

    def create_category(self):
        """Create event category with 3 languages."""
        category, created = EventCategory.objects.get_or_create(
            slug='music-concert',
            defaults={
                'icon': 'music',
                'color': '#FF6B6B',
                'is_active': True
            }
        )

        # Persian
        with switch_language(category, 'fa'):
            category.name = 'کنسرت موسیقی'
            category.description = 'کنسرت‌های موسیقی زنده با هنرمندان برجسته'
            category.save()

        # English
        with switch_language(category, 'en'):
            category.name = 'Music Concert'
            category.description = 'Live music concerts with renowned artists'
            category.save()

        # Arabic
        with switch_language(category, 'ar'):
            category.name = 'حفلة موسيقية'
            category.description = 'حفلات موسيقية حية مع فنانين مشهورين'
            category.save()

        return category

    def create_venue(self):
        """Create venue with 3 languages."""
        venue, created = Venue.objects.get_or_create(
            slug='grand-hall-istanbul',
            defaults={
                'city': 'Istanbul',
                'country': 'Turkey',
                'total_capacity': 5000,
                'coordinates': {'lat': 41.0082, 'lng': 28.9784},
                'facilities': ['parking', 'restaurant', 'wheelchair_access', 'vip_lounge'],
                'website': 'https://grandhall-istanbul.com'
            }
        )

        # Persian
        with switch_language(venue, 'fa'):
            venue.name = 'سالن بزرگ استانبول'
            venue.description = 'یکی از بهترین سالن‌های کنسرت در استانبول با امکانات مدرن'
            venue.address = 'میدان تقسیم، خیابان استقلال، استانبول، ترکیه'
            venue.save()

        # English
        with switch_language(venue, 'en'):
            venue.name = 'Grand Hall Istanbul'
            venue.description = 'One of the best concert halls in Istanbul with modern facilities'
            venue.address = 'Taksim Square, Istiklal Street, Istanbul, Turkey'
            venue.save()

        # Arabic
        with switch_language(venue, 'ar'):
            venue.name = 'القاعة الكبرى اسطنبول'
            venue.description = 'واحدة من أفضل قاعات الحفلات الموسيقية في اسطنبول مع مرافق حديثة'
            venue.address = 'ميدان تقسيم، شارع الاستقلال، اسطنبول، تركيا'
            venue.save()

        return venue

    def create_artists(self):
        """Create artists with 3 languages."""
        # Artist 1
        artist1, created = Artist.objects.get_or_create(
            slug='sami-yusuf',
            defaults={
                'website': 'https://samiyusuf.com',
                'social_media': {
                    'instagram': '@samiyusuf',
                    'twitter': '@samiyusuf',
                    'facebook': 'samiyusufofficial'
                }
            }
        )

        # Persian
        with switch_language(artist1, 'fa'):
            artist1.name = 'سامی یوسف'
            artist1.bio = 'خواننده و آهنگساز بریتانیایی-ایرانی، برنده جوایز متعدد بین‌المللی'
            artist1.save()

        # English
        with switch_language(artist1, 'en'):
            artist1.name = 'Sami Yusuf'
            artist1.bio = 'British-Iranian singer and composer, winner of multiple international awards'
            artist1.save()

        # Arabic
        with switch_language(artist1, 'ar'):
            artist1.name = 'سامي يوسف'
            artist1.bio = 'مغني وملحن بريطاني-إيراني، حائز على جوائز دولية متعددة'
            artist1.save()

        # Artist 2
        artist2, created = Artist.objects.get_or_create(
            slug='maher-zain',
            defaults={
                'website': 'https://maherzain.com',
                'social_media': {
                    'instagram': '@maherzainofficial',
                    'twitter': '@maherzain',
                    'facebook': 'maherzainofficial'
                }
            }
        )

        # Persian
        with switch_language(artist2, 'fa'):
            artist2.name = 'ماهر زین'
            artist2.bio = 'خواننده و ترانه‌سرای سوئدی-لبنانی با شهرت جهانی'
            artist2.save()

        # English
        with switch_language(artist2, 'en'):
            artist2.name = 'Maher Zain'
            artist2.bio = 'Swedish-Lebanese singer and songwriter with worldwide fame'
            artist2.save()

        # Arabic
        with switch_language(artist2, 'ar'):
            artist2.name = 'ماهر زين'
            artist2.bio = 'مغني وكاتب أغاني سويدي-لبناني ذو شهرة عالمية'
            artist2.save()

        return artist1, artist2

    def create_event(self, category, venue):
        """Create event with 3 languages."""
        event, created = Event.objects.get_or_create(
            slug='istanbul-music-festival-2025',
            defaults={
                'category': category,
                'venue': venue,
                'style': 'music',
                'price': Decimal('150.00'),
                'currency': 'USD',
                'door_open_time': '18:00:00',
                'start_time': '20:00:00',
                'end_time': '23:00:00',
                'age_restriction': 12,
                'is_active': True,
                'is_featured': True,
                'is_popular': True,
                'is_special': True,
                'is_seasonal': False,
                'cancellation_hours': 48,
                'refund_percentage': 80,
                'gallery': [
                    '/media/events/gallery1.jpg',
                    '/media/events/gallery2.jpg',
                    '/media/events/gallery3.jpg'
                ]
            }
        )

        # Persian
        with switch_language(event, 'fa'):
            event.title = 'جشنواره موسیقی استانبول ۲۰۲۵'
            event.short_description = 'شبی فراموش‌نشدنی با بهترین خوانندگان جهان'
            event.description = '''
جشنواره موسیقی استانبول یکی از بزرگترین رویدادهای موسیقی در خاورمیانه است.
این رویداد با حضور هنرمندان مطرح بین‌المللی برگزار می‌شود و تجربه‌ای بی‌نظیر
از موسیقی زنده را برای شما به ارمغان می‌آورد.
            '''
            event.highlights = '''
• اجرای زنده توسط سامی یوسف و ماهر زین
• سیستم صوتی و نورپردازی حرفه‌ای
• امکانات ویژه برای معلولین
• رستوران و کافی‌شاپ در محل
• پارکینگ رایگان
            '''
            event.rules = '''
• ورود با بلیط معتبر الزامی است
• دوربین‌های حرفه‌ای مجاز نیستند
• سیگار کشیدن ممنوع است
• لطفاً به موقع حاضر شوید
            '''
            event.required_items = '''
• بلیط چاپی یا الکترونیکی
• کارت شناسایی معتبر
• ماسک (در صورت نیاز)
            '''
            event.save()

        # English
        with switch_language(event, 'en'):
            event.title = 'Istanbul Music Festival 2025'
            event.short_description = 'An unforgettable night with the world\'s best singers'
            event.description = '''
Istanbul Music Festival is one of the largest music events in the Middle East.
This event features renowned international artists and brings you an unparalleled
experience of live music.
            '''
            event.highlights = '''
• Live performance by Sami Yusuf and Maher Zain
• Professional sound and lighting system
• Special facilities for disabled persons
• On-site restaurant and coffee shop
• Free parking
            '''
            event.rules = '''
• Entry with valid ticket is mandatory
• Professional cameras are not allowed
• Smoking is prohibited
• Please arrive on time
            '''
            event.required_items = '''
• Printed or electronic ticket
• Valid ID card
• Mask (if required)
            '''
            event.save()

        # Arabic
        with switch_language(event, 'ar'):
            event.title = 'مهرجان اسطنبول الموسيقي ٢٠٢٥'
            event.short_description = 'ليلة لا تُنسى مع أفضل المغنين في العالم'
            event.description = '''
مهرجان اسطنبول الموسيقي هو واحد من أكبر الفعاليات الموسيقية في الشرق الأوسط.
يضم هذا الحدث فنانين دوليين مشهورين ويقدم لك تجربة لا مثيل لها
من الموسيقى الحية.
            '''
            event.highlights = '''
• أداء مباشر من سامي يوسف وماهر زين
• نظام صوت وإضاءة احترافي
• مرافق خاصة للمعاقين
• مطعم ومقهى في الموقع
• موقف سيارات مجاني
            '''
            event.rules = '''
• الدخول بتذكرة صالحة إلزامي
• الكاميرات الاحترافية غير مسموح بها
• التدخين ممنوع
• يرجى الحضور في الوقت المحدد
            '''
            event.required_items = '''
• تذكرة مطبوعة أو إلكترونية
• بطاقة هوية صالحة
• قناع (إذا لزم الأمر)
            '''
            event.save()

        return event

    def create_ticket_types(self, event):
        """Create ticket types (simple, no translations)."""
        ticket_types = []

        # VIP Ticket
        vip_ticket, created = TicketType.objects.get_or_create(
            event=event,
            ticket_type='vip',
            defaults={
                'name': 'VIP Ticket',
                'description': 'Premium ticket with exclusive facilities',
                'price_modifier': Decimal('2.0'),
                'capacity': 500,
                'is_active': True,
                'benefits': [
                    'Front row seats',
                    'VIP lounge access',
                    'Free drinks',
                    'Meet & greet opportunity'
                ]
            }
        )
        ticket_types.append(vip_ticket)

        # Normal Ticket
        normal_ticket, created = TicketType.objects.get_or_create(
            event=event,
            ticket_type='normal',
            defaults={
                'name': 'Normal Ticket',
                'description': 'Standard ticket with access to all facilities',
                'price_modifier': Decimal('1.0'),
                'capacity': 3000,
                'is_active': True,
                'benefits': [
                    'Standard seating',
                    'Access to all facilities'
                ]
            }
        )
        ticket_types.append(normal_ticket)

        # Eco Ticket
        eco_ticket, created = TicketType.objects.get_or_create(
            event=event,
            ticket_type='eco',
            defaults={
                'name': 'Economy Ticket',
                'description': 'Affordable ticket with basic facilities',
                'price_modifier': Decimal('0.7'),
                'capacity': 1000,
                'is_active': True,
                'benefits': [
                    'Economy seating',
                    'Basic facilities'
                ]
            }
        )
        ticket_types.append(eco_ticket)

        # Wheelchair Ticket
        wheelchair_ticket, created = TicketType.objects.get_or_create(
            event=event,
            ticket_type='wheelchair',
            defaults={
                'name': 'Wheelchair Ticket',
                'description': 'Special ticket for persons with mobility disabilities',
                'price_modifier': Decimal('1.0'),
                'capacity': 50,
                'is_active': True,
                'benefits': [
                    'Wheelchair accessible seating',
                    'Companion seat included',
                    'Easy access to facilities'
                ]
            }
        )
        ticket_types.append(wheelchair_ticket)

        return ticket_types

    def create_event_options(self, event):
        """Create event options (simple, no translations)."""
        # Parking Option
        EventOption.objects.get_or_create(
            event=event,
            option_type='parking',
            defaults={
                'name': 'Parking',
                'description': 'Dedicated parking at the event venue',
                'price': Decimal('10.00'),
                'currency': 'USD',
                'is_available': True,
                'max_quantity': 500
            }
        )

        # Food Package
        EventOption.objects.get_or_create(
            event=event,
            option_type='food',
            defaults={
                'name': 'Food Package',
                'description': 'Includes drinks and snacks',
                'price': Decimal('25.00'),
                'currency': 'USD',
                'is_available': True,
                'max_quantity': 1000
            }
        )

    def create_cancellation_policies(self, event):
        """Create cancellation policies."""
        # 48 hours before - 80% refund
        EventCancellationPolicy.objects.get_or_create(
            event=event,
            hours_before=48,
            defaults={
                'refund_percentage': 80,
                'description': 'Full refund minus service fee',
                'is_active': True
            }
        )

        # 24 hours before - 50% refund
        EventCancellationPolicy.objects.get_or_create(
            event=event,
            hours_before=24,
            defaults={
                'refund_percentage': 50,
                'description': 'Half refund',
                'is_active': True
            }
        )

        # Less than 24 hours - No refund
        EventCancellationPolicy.objects.get_or_create(
            event=event,
            hours_before=0,
            defaults={
                'refund_percentage': 0,
                'description': 'No refund',
                'is_active': True
            }
        )

    def create_performances(self, event):
        """Create performances for the next 7 days."""
        performances = []
        today = timezone.now().date()

        for i in range(7):
            performance_date = today + timedelta(days=i)
            performance, created = EventPerformance.objects.get_or_create(
                event=event,
                date=performance_date,
                defaults={
                    'start_date': performance_date,
                    'end_date': performance_date,
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'is_available': True,
                    'is_special': i == 0,  # First performance is special
                    'max_capacity': 5000,
                    'current_capacity': 0,
                    'ticket_capacities': {}
                }
            )
            performances.append(performance)

        return performances

    def create_sections_and_seats(self, performance, ticket_types):
        """Create sections and seats for a performance."""
        sections_config = [
            {
                'name': 'VIP Section',
                'capacity': 500,
                'base_price': Decimal('300.00'),
                'is_premium': True,
                'rows': 10,
                'seats_per_row': 50
            },
            {
                'name': 'Section A',
                'capacity': 1500,
                'base_price': Decimal('150.00'),
                'is_premium': False,
                'rows': 30,
                'seats_per_row': 50
            },
            {
                'name': 'Section B',
                'capacity': 2000,
                'base_price': Decimal('100.00'),
                'is_premium': False,
                'rows': 40,
                'seats_per_row': 50
            },
            {
                'name': 'Section C',
                'capacity': 1000,
                'base_price': Decimal('70.00'),
                'is_premium': False,
                'rows': 20,
                'seats_per_row': 50
            }
        ]

        for section_config in sections_config:
            # Create section
            section, created = EventSection.objects.get_or_create(
                performance=performance,
                name=section_config['name'],
                defaults={
                    'description': f'{section_config["name"]} with {section_config["capacity"]} seats',
                    'total_capacity': section_config['capacity'],
                    'base_price': section_config['base_price'],
                    'currency': 'USD',
                    'is_premium': section_config['is_premium'],
                    'is_wheelchair_accessible': section_config['name'] == 'Section A'
                }
            )

            # Create section ticket types
            for ticket_type in ticket_types:
                SectionTicketType.objects.get_or_create(
                    section=section,
                    ticket_type=ticket_type,
                    defaults={
                        'price_modifier': ticket_type.price_modifier
                    }
                )

            # Create seats
            if created:
                seat_number = 1
                for row in range(1, section_config['rows'] + 1):
                    for seat in range(1, section_config['seats_per_row'] + 1):
                        # Determine ticket type for this seat
                        if section_config['name'] == 'VIP Section':
                            ticket_type = ticket_types[0]  # VIP
                        elif section_config['name'] == 'Section C':
                            ticket_type = ticket_types[2]  # Eco
                        else:
                            ticket_type = ticket_types[1]  # Normal

                        # Calculate seat price
                        seat_price = section_config['base_price'] * ticket_type.price_modifier

                        # Create seat
                        Seat.objects.get_or_create(
                            performance=performance,
                            section=section_config['name'],
                            row_number=f'R{row:02d}',
                            seat_number=f'S{seat:02d}',
                            defaults={
                                'ticket_type': ticket_type,
                                'status': 'available',
                                'price': seat_price,
                                'currency': 'USD',
                                'is_premium': section_config['is_premium'],
                                'is_wheelchair_accessible': (
                                    section_config['name'] == 'Section A' and row <= 2
                                )
                            }
                        )
                        seat_number += 1
