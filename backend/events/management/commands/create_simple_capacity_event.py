"""
Django management command to create a simple event with capacity-based ticketing.
No individual seats - just ticket types with capacities.
Usage: python manage.py create_simple_capacity_event
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
    help = 'Create a simple event with capacity-based ticketing (no individual seats)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating simple capacity-based event...'))

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

        # 5. Create Ticket Types (capacity-based, no seats)
        self.stdout.write('Creating ticket types...')
        ticket_types = self.create_ticket_types(event)

        # 6. Create Event Options
        self.stdout.write('Creating event options...')
        self.create_event_options(event)

        # 7. Create Cancellation Policies
        self.stdout.write('Creating cancellation policies...')
        self.create_cancellation_policies(event)

        # 8. Create Performances (capacity-based, no seats)
        self.stdout.write('Creating performances...')
        performances = self.create_performances(event, ticket_types)

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created event: {event.slug}'))
        self.stdout.write(self.style.SUCCESS(f'Event ID: {event.id}'))
        self.stdout.write(self.style.SUCCESS(f'Total Performances: {len(performances)}'))
        self.stdout.write(self.style.SUCCESS(f'Ticket Types: {len(ticket_types)}'))
        self.stdout.write(self.style.SUCCESS('\n⚡ This event uses capacity-based ticketing (no individual seats)'))
        self.stdout.write(self.style.SUCCESS('Much faster and more efficient!'))

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
                'gallery': []
            }
        )

        # Persian
        with switch_language(event, 'fa'):
            event.title = 'جشنواره موسیقی استانبول ۲۰۲۵'
            event.short_description = 'شبی فراموش‌نشدنی با بهترین خوانندگان جهان'
            event.description = 'جشنواره موسیقی استانبول یکی از بزرگترین رویدادهای موسیقی در خاورمیانه است. این رویداد با حضور هنرمندان مطرح بین‌المللی برگزار می‌شود.'
            event.highlights = '• اجرای زنده سامی یوسف و ماهر زین\n• سیستم صوتی حرفه‌ای\n• امکانات ویژه\n• پارکینگ رایگان'
            event.rules = '• ورود با بلیط معتبر\n• دوربین حرفه‌ای ممنوع\n• سیگار ممنوع'
            event.required_items = '• بلیط\n• کارت شناسایی\n• ماسک (در صورت نیاز)'
            event.save()

        # English
        with switch_language(event, 'en'):
            event.title = 'Istanbul Music Festival 2025'
            event.short_description = 'An unforgettable night with the world\'s best singers'
            event.description = 'Istanbul Music Festival is one of the largest music events in the Middle East. This event features renowned international artists.'
            event.highlights = '• Live performance by Sami Yusuf and Maher Zain\n• Professional sound system\n• Special facilities\n• Free parking'
            event.rules = '• Entry with valid ticket\n• Professional cameras not allowed\n• Smoking prohibited'
            event.required_items = '• Ticket\n• Valid ID\n• Mask (if required)'
            event.save()

        # Arabic
        with switch_language(event, 'ar'):
            event.title = 'مهرجان اسطنبول الموسيقي ٢٠٢٥'
            event.short_description = 'ليلة لا تُنسى مع أفضل المغنين في العالم'
            event.description = 'مهرجان اسطنبول الموسيقي هو واحد من أكبر الفعاليات الموسيقية في الشرق الأوسط. يضم هذا الحدث فنانين دوليين مشهورين.'
            event.highlights = '• أداء مباشر من سامي يوسف وماهر زين\n• نظام صوت احترافي\n• مرافق خاصة\n• موقف سيارات مجاني'
            event.rules = '• الدخول بتذكرة صالحة\n• الكاميرات الاحترافية غير مسموح بها\n• التدخين ممنوع'
            event.required_items = '• تذكرة\n• بطاقة هوية صالحة\n• قناع (إذا لزم الأمر)'
            event.save()

        return event

    def create_ticket_types(self, event):
        """Create ticket types with capacity (no individual seats)."""
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

        # Economy Ticket
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

        return ticket_types

    def create_event_options(self, event):
        """Create event options."""
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
        policies = [
            (48, 80, 'Full refund minus service fee'),
            (24, 50, 'Half refund'),
            (0, 0, 'No refund'),
        ]

        for hours, refund, desc in policies:
            EventCancellationPolicy.objects.get_or_create(
                event=event,
                hours_before=hours,
                defaults={
                    'refund_percentage': refund,
                    'description': desc,
                    'is_active': True
                }
            )

    def create_performances(self, event, ticket_types):
        """Create performances with capacity tracking (no individual seats)."""
        performances = []
        today = timezone.now().date()

        for i in range(7):
            performance_date = today + timedelta(days=i)
            
            # Initialize ticket capacities
            ticket_capacities = {}
            for ticket_type in ticket_types:
                ticket_capacities[ticket_type.ticket_type] = {
                    'total': ticket_type.capacity,
                    'available': ticket_type.capacity,
                    'sold': 0,
                    'reserved': 0
                }
            
            performance, created = EventPerformance.objects.get_or_create(
                event=event,
                date=performance_date,
                defaults={
                    'start_date': performance_date,
                    'end_date': performance_date,
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'is_available': True,
                    'is_special': i == 0,
                    'max_capacity': sum(tt.capacity for tt in ticket_types),
                    'current_capacity': 0,
                    'ticket_capacities': ticket_capacities
                }
            )
            performances.append(performance)

        return performances
