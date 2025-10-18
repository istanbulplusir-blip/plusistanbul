"""
Django management command to create a simple event with 3 languages.
Usage: python manage.py create_simple_event
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from events.models import (
    Event, EventCategory, Venue, Artist, TicketType,
    EventPerformance, EventOption, EventCancellationPolicy
)
from parler.utils.context import switch_language


class Command(BaseCommand):
    help = 'Create a simple event with 3 languages (Persian, English, Arabic)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating simple event with 3 languages...'))

        # 1. Create Event Category
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

        # 2. Create Venue
        venue, _ = Venue.objects.get_or_create(
            slug='grand-hall',
            defaults={
                'city': 'Istanbul',
                'country': 'Turkey',
                'total_capacity': 1000,
                'coordinates': {'lat': 41.0082, 'lng': 28.9784},
                'facilities': ['parking', 'restaurant'],
            }
        )
        with switch_language(venue, 'fa'):
            venue.name = 'سالن بزرگ'
            venue.description = 'سالن کنسرت مدرن'
            venue.address = 'استانبول، ترکیه'
            venue.save()
        with switch_language(venue, 'en'):
            venue.name = 'Grand Hall'
            venue.description = 'Modern concert hall'
            venue.address = 'Istanbul, Turkey'
            venue.save()
        with switch_language(venue, 'ar'):
            venue.name = 'القاعة الكبرى'
            venue.description = 'قاعة حفلات حديثة'
            venue.address = 'اسطنبول، تركيا'
            venue.save()

        # 3. Create Artist
        artist, _ = Artist.objects.get_or_create(
            slug='famous-artist',
            defaults={'website': 'https://example.com'}
        )
        with switch_language(artist, 'fa'):
            artist.name = 'هنرمند مشهور'
            artist.bio = 'خواننده معروف'
            artist.save()
        with switch_language(artist, 'en'):
            artist.name = 'Famous Artist'
            artist.bio = 'Well-known singer'
            artist.save()
        with switch_language(artist, 'ar'):
            artist.name = 'فنان مشهور'
            artist.bio = 'مغني معروف'
            artist.save()

        # 4. Create Event
        event, _ = Event.objects.get_or_create(
            slug='simple-concert-2025',
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
            event.title = 'کنسرت ساده ۲۰۲۵'
            event.short_description = 'یک کنسرت فوق‌العاده'
            event.description = 'کنسرت موسیقی زنده با هنرمندان برتر'
            event.highlights = '• اجرای زنده\n• صدای عالی\n• فضای دنج'
            event.rules = '• ورود با بلیط\n• ممنوعیت سیگار'
            event.required_items = '• بلیط\n• کارت شناسایی'
            event.save()
            
        with switch_language(event, 'en'):
            event.title = 'Simple Concert 2025'
            event.short_description = 'An amazing concert'
            event.description = 'Live music concert with top artists'
            event.highlights = '• Live performance\n• Great sound\n• Cozy atmosphere'
            event.rules = '• Entry with ticket\n• No smoking'
            event.required_items = '• Ticket\n• ID card'
            event.save()
            
        with switch_language(event, 'ar'):
            event.title = 'حفلة بسيطة ٢٠٢٥'
            event.short_description = 'حفلة رائعة'
            event.description = 'حفلة موسيقية حية مع أفضل الفنانين'
            event.highlights = '• أداء مباشر\n• صوت رائع\n• جو مريح'
            event.rules = '• الدخول بتذكرة\n• ممنوع التدخين'
            event.required_items = '• تذكرة\n• بطاقة هوية'
            event.save()

        event.artists.add(artist)

        # 5. Create Ticket Types (simple, no translations needed)
        TicketType.objects.get_or_create(
            event=event,
            ticket_type='normal',
            defaults={
                'name': 'Normal Ticket',
                'description': 'Standard ticket',
                'price_modifier': Decimal('1.0'),
                'capacity': 800,
                'is_active': True,
            }
        )
        
        TicketType.objects.get_or_create(
            event=event,
            ticket_type='vip',
            defaults={
                'name': 'VIP Ticket',
                'description': 'Premium ticket',
                'price_modifier': Decimal('2.0'),
                'capacity': 200,
                'is_active': True,
            }
        )

        # 6. Create Options
        EventOption.objects.get_or_create(
            event=event,
            option_type='parking',
            defaults={
                'name': 'Parking',
                'description': 'Parking space',
                'price': Decimal('10.00'),
                'currency': 'USD',
                'is_available': True,
            }
        )

        # 7. Create Cancellation Policy
        EventCancellationPolicy.objects.get_or_create(
            event=event,
            hours_before=24,
            defaults={
                'refund_percentage': 50,
                'description': 'Half refund',
                'is_active': True
            }
        )

        # 8. Create ONE Performance (not 7!)
        today = timezone.now().date()
        performance_date = today + timedelta(days=7)
        
        EventPerformance.objects.get_or_create(
            event=event,
            date=performance_date,
            defaults={
                'start_date': performance_date,
                'end_date': performance_date,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'is_available': True,
                'is_special': False,
                'max_capacity': 1000,
                'current_capacity': 0,
            }
        )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created simple event: {event.slug}'))
        self.stdout.write(self.style.SUCCESS(f'Event ID: {event.id}'))
        self.stdout.write(self.style.SUCCESS('\nYou can now view this event in the admin panel or API.'))
