"""
Django management command to create a COMPLETE event with all required data.
Usage: python manage.py create_complete_event
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
    help = 'Create a complete event with all required data (3 languages)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating COMPLETE event...'))

        # 1. Category
        category, _ = EventCategory.objects.get_or_create(
            slug='music-concert',
            defaults={'icon': 'music', 'color': '#FF6B6B', 'is_active': True}
        )
        with switch_language(category, 'fa'):
            category.name = 'کنسرت موسیقی'
            category.description = 'کنسرت‌های موسیقی زنده'
            category.save()
        with switch_language(category, 'en'):
            category.name = 'Music Concert'
            category.description = 'Live music concerts'
            category.save()
        with switch_language(category, 'ar'):
            category.name = 'حفلة موسيقية'
            category.description = 'حفلات موسيقية حية'
            category.save()

        # 2. Venue
        venue, _ = Venue.objects.get_or_create(
            slug='concert-hall',
            defaults={
                'city': 'Istanbul',
                'country': 'Turkey',
                'total_capacity': 300,
                'coordinates': {'lat': 41.0082, 'lng': 28.9784},
                'facilities': ['parking', 'restaurant'],
            }
        )
        with switch_language(venue, 'fa'):
            venue.name = 'سالن کنسرت'
            venue.description = 'سالن کنسرت مدرن'
            venue.address = 'استانبول، ترکیه'
            venue.save()
        with switch_language(venue, 'en'):
            venue.name = 'Concert Hall'
            venue.description = 'Modern concert hall'
            venue.address = 'Istanbul, Turkey'
            venue.save()
        with switch_language(venue, 'ar'):
            venue.name = 'قاعة الحفلات'
            venue.description = 'قاعة حفلات حديثة'
            venue.address = 'اسطنبول، تركيا'
            venue.save()

        # 3. Artist
        artist, _ = Artist.objects.get_or_create(
            slug='top-artist',
            defaults={'website': 'https://example.com'}
        )
        with switch_language(artist, 'fa'):
            artist.name = 'هنرمند برتر'
            artist.bio = 'خواننده معروف بین‌المللی'
            artist.save()
        with switch_language(artist, 'en'):
            artist.name = 'Top Artist'
            artist.bio = 'Famous international singer'
            artist.save()
        with switch_language(artist, 'ar'):
            artist.name = 'فنان كبير'
            artist.bio = 'مغني دولي مشهور'
            artist.save()

        # 4. Event
        event, _ = Event.objects.get_or_create(
            slug='complete-concert-2025',
            defaults={
                'category': category,
                'venue': venue,
                'style': 'music',
                'price': Decimal('100.00'),
                'currency': 'USD',
                'city': 'Istanbul',
                'country': 'Turkey',
                'door_open_time': '18:00:00',
                'start_time': '20:00:00',
                'end_time': '22:00:00',
                'age_restriction': 12,
                'is_active': True,
                'is_featured': True,
                'cancellation_hours': 24,
                'refund_percentage': 50,
            }
        )
        
        with switch_language(event, 'fa'):
            event.title = 'کنسرت کامل ۲۰۲۵'
            event.short_description = 'یک کنسرت فوق‌العاده با تمام امکانات'
            event.description = 'کنسرت موسیقی زنده با هنرمندان برتر جهان'
            event.highlights = '• اجرای زنده\n• صدای عالی\n• فضای دنج\n• امکانات VIP'
            event.rules = '• ورود با بلیط\n• ممنوعیت سیگار\n• ممنوعیت دوربین حرفه‌ای'
            event.required_items = '• بلیط\n• کارت شناسایی\n• ماسک (در صورت نیاز)'
            event.save()
            
        with switch_language(event, 'en'):
            event.title = 'Complete Concert 2025'
            event.short_description = 'An amazing concert with all facilities'
            event.description = 'Live music concert with world top artists'
            event.highlights = '• Live performance\n• Great sound\n• Cozy atmosphere\n• VIP facilities'
            event.rules = '• Entry with ticket\n• No smoking\n• No professional cameras'
            event.required_items = '• Ticket\n• ID card\n• Mask (if needed)'
            event.save()
            
        with switch_language(event, 'ar'):
            event.title = 'حفلة كاملة ٢٠٢٥'
            event.short_description = 'حفلة رائعة مع جميع المرافق'
            event.description = 'حفلة موسيقية حية مع أفضل الفنانين في العالم'
            event.highlights = '• أداء مباشر\n• صوت رائع\n• جو مريح\n• مرافق VIP'
            event.rules = '• الدخول بتذكرة\n• ممنوع التدخين\n• ممنوع الكاميرات الاحترافية'
            event.required_items = '• تذكرة\n• بطاقة هوية\n• قناع (إذا لزم الأمر)'
            event.save()

        event.artists.add(artist)

        # 5. Ticket Types (3 types)
        vip_ticket, _ = TicketType.objects.get_or_create(
            event=event,
            ticket_type='vip',
            defaults={
                'name': 'VIP Ticket',
                'description': 'Premium VIP ticket with best seats',
                'price_modifier': Decimal('2.0'),
                'capacity': 100,
                'is_active': True,
                'benefits': ['Front seats', 'VIP lounge', 'Free drinks']
            }
        )
        
        normal_ticket, _ = TicketType.objects.get_or_create(
            event=event,
            ticket_type='normal',
            defaults={
                'name': 'Normal Ticket',
                'description': 'Standard ticket',
                'price_modifier': Decimal('1.0'),
                'capacity': 150,
                'is_active': True,
                'benefits': ['Standard seating']
            }
        )
        
        eco_ticket, _ = TicketType.objects.get_or_create(
            event=event,
            ticket_type='eco',
            defaults={
                'name': 'Economy Ticket',
                'description': 'Budget-friendly ticket',
                'price_modifier': Decimal('0.7'),
                'capacity': 50,
                'is_active': True,
                'benefits': ['Economy seating']
            }
        )

        # 6. Options (1 option)
        EventOption.objects.get_or_create(
            event=event,
            option_type='parking',
            defaults={
                'name': 'Parking',
                'description': 'Reserved parking space',
                'price': Decimal('10.00'),
                'currency': 'USD',
                'is_available': True,
                'max_quantity': 100
            }
        )

        # 7. Cancellation Policy
        EventCancellationPolicy.objects.get_or_create(
            event=event,
            hours_before=24,
            defaults={
                'refund_percentage': 50,
                'description': '50% refund if cancelled 24h before',
                'is_active': True
            }
        )

        # 8. Performance (1 performance)
        today = timezone.now().date()
        performance_date = today + timedelta(days=7)
        
        performance, _ = EventPerformance.objects.get_or_create(
            event=event,
            date=performance_date,
            defaults={
                'start_date': performance_date,
                'end_date': performance_date,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'is_available': True,
                'is_special': False,
                'max_capacity': 300,
                'current_capacity': 0,
            }
        )

        # 9. Sections (3 sections)
        sections_config = [
            {'name': 'VIP Section', 'capacity': 100, 'price': Decimal('200.00'), 'is_premium': True},
            {'name': 'Section A', 'capacity': 150, 'price': Decimal('100.00'), 'is_premium': False},
            {'name': 'Section B', 'capacity': 50, 'price': Decimal('70.00'), 'is_premium': False},
        ]

        for section_config in sections_config:
            section, _ = EventSection.objects.get_or_create(
                performance=performance,
                name=section_config['name'],
                defaults={
                    'description': f'{section_config["name"]} with {section_config["capacity"]} seats',
                    'total_capacity': section_config['capacity'],
                    'base_price': section_config['price'],
                    'currency': 'USD',
                    'is_premium': section_config['is_premium'],
                    'is_wheelchair_accessible': section_config['name'] == 'Section A'
                }
            )

            # Link ticket types to sections
            if section_config['name'] == 'VIP Section':
                SectionTicketType.objects.get_or_create(
                    section=section,
                    ticket_type=vip_ticket,
                    defaults={'price_modifier': vip_ticket.price_modifier}
                )
            elif section_config['name'] == 'Section A':
                SectionTicketType.objects.get_or_create(
                    section=section,
                    ticket_type=normal_ticket,
                    defaults={'price_modifier': normal_ticket.price_modifier}
                )
            else:  # Section B
                SectionTicketType.objects.get_or_create(
                    section=section,
                    ticket_type=eco_ticket,
                    defaults={'price_modifier': eco_ticket.price_modifier}
                )

            # 10. Create Seats (10 seats per section = 30 total)
            for i in range(1, 11):
                row = f'R{(i-1)//5 + 1}'  # 2 rows: R1, R2
                seat_num = f'S{(i-1)%5 + 1}'  # 5 seats per row: S1-S5
                
                # Determine ticket type and price
                if section_config['name'] == 'VIP Section':
                    ticket_type = vip_ticket
                    seat_price = section_config['price'] * vip_ticket.price_modifier
                elif section_config['name'] == 'Section A':
                    ticket_type = normal_ticket
                    seat_price = section_config['price'] * normal_ticket.price_modifier
                else:
                    ticket_type = eco_ticket
                    seat_price = section_config['price'] * eco_ticket.price_modifier

                Seat.objects.get_or_create(
                    performance=performance,
                    section=section_config['name'],
                    row_number=row,
                    seat_number=seat_num,
                    defaults={
                        'ticket_type': ticket_type,
                        'status': 'available',
                        'price': seat_price,
                        'currency': 'USD',
                        'is_premium': section_config['is_premium'],
                        'is_wheelchair_accessible': (section_config['name'] == 'Section A' and i <= 2)
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created COMPLETE event: {event.slug}'))
        self.stdout.write(self.style.SUCCESS(f'Event ID: {event.id}'))
        self.stdout.write(self.style.SUCCESS(f'- 1 Performance on {performance_date}'))
        self.stdout.write(self.style.SUCCESS(f'- 3 Sections (VIP, A, B)'))
        self.stdout.write(self.style.SUCCESS(f'- 30 Seats (10 per section)'))
        self.stdout.write(self.style.SUCCESS(f'- 3 Ticket Types (VIP, Normal, Economy)'))
        self.stdout.write(self.style.SUCCESS(f'- 1 Option (Parking)'))
        self.stdout.write(self.style.SUCCESS('\nYou can now view this event in the admin panel or API.'))
