"""
Management command to create test locations for Istanbul.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from transfers.models import TransferLocation
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create test transfer locations for Istanbul'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test locations for Istanbul...'))

        locations_data = [
            {
                'name_en': 'Istanbul Airport (IST)',
                'name_fa': 'فرودگاه استانبول (IST)',
                'description_en': 'Istanbul Airport - Main international airport',
                'description_fa': 'فرودگاه استانبول - فرودگاه بین‌المللی اصلی',
                'address': 'Tayakadın, Terminal Caddesi No:1, 34283 Arnavutköy/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.275300'),
                'longitude': Decimal('28.751900'),
                'location_type': 'airport',
                'is_popular': True,
            },
            {
                'name_en': 'Sabiha Gökçen Airport (SAW)',
                'name_fa': 'فرودگاه صبیحه گوکچن (SAW)',
                'description_en': 'Sabiha Gökçen International Airport',
                'description_fa': 'فرودگاه بین‌المللی صبیحه گوکچن',
                'address': 'Sanayi, 34906 Pendik/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('40.898600'),
                'longitude': Decimal('29.309200'),
                'location_type': 'airport',
                'is_popular': True,
            },
            {
                'name_en': 'Taksim Square',
                'name_fa': 'میدان تکسیم',
                'description_en': 'Famous square in the heart of modern Istanbul',
                'description_fa': 'میدان معروف در قلب استانبول مدرن',
                'address': 'Gümüşsuyu, Taksim Square, 34437 Beyoğlu/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.037000'),
                'longitude': Decimal('28.985000'),
                'location_type': 'landmark',
                'is_popular': True,
            },
            {
                'name_en': 'Sultanahmet (Blue Mosque)',
                'name_fa': 'سلطان احمد (مسجد آبی)',
                'description_en': 'Historic area with Blue Mosque and Hagia Sophia',
                'description_fa': 'منطقه تاریخی با مسجد آبی و ایاصوفیه',
                'address': 'Sultanahmet, Atmeydanı Cd. No:7, 34122 Fatih/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.005400'),
                'longitude': Decimal('28.976800'),
                'location_type': 'landmark',
                'is_popular': True,
            },
            {
                'name_en': 'Besiktas',
                'name_fa': 'بشیکتاش',
                'description_en': 'Vibrant district on the European side',
                'description_fa': 'منطقه پرجنب‌وجوش در سمت اروپایی',
                'address': 'Beşiktaş, 34353 Beşiktaş/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.042900'),
                'longitude': Decimal('29.007600'),
                'location_type': 'landmark',
                'is_popular': False,
            },
            {
                'name_en': 'Kadikoy',
                'name_fa': 'کادیکوی',
                'description_en': 'Popular district on the Asian side',
                'description_fa': 'منطقه محبوب در سمت آسیایی',
                'address': 'Kadıköy, 34710 Kadıköy/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('40.990500'),
                'longitude': Decimal('29.025000'),
                'location_type': 'landmark',
                'is_popular': False,
            },
            {
                'name_en': 'Grand Bazaar',
                'name_fa': 'بازار بزرگ',
                'description_en': 'Historic covered market',
                'description_fa': 'بازار سرپوشیده تاریخی',
                'address': 'Beyazıt, Kalpakçılar Cd., 34126 Fatih/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.010700'),
                'longitude': Decimal('28.968100'),
                'location_type': 'landmark',
                'is_popular': True,
            },
            {
                'name_en': 'Galata Tower',
                'name_fa': 'برج گالاتا',
                'description_en': 'Medieval stone tower with panoramic views',
                'description_fa': 'برج سنگی قرون وسطایی با چشم‌انداز پانورامیک',
                'address': 'Bereketzade, Galata Tower, 34421 Beyoğlu/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.025600'),
                'longitude': Decimal('28.974200'),
                'location_type': 'landmark',
                'is_popular': True,
            },
            {
                'name_en': 'Hilton Istanbul Bosphorus',
                'name_fa': 'هتل هیلتون استانبول بسفر',
                'description_en': 'Luxury hotel with Bosphorus views',
                'description_fa': 'هتل لوکس با چشم‌انداز بسفر',
                'address': 'Harbiye, Cumhuriyet Cd. No:50, 34367 Şişli/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.046700'),
                'longitude': Decimal('28.995000'),
                'location_type': 'hotel',
                'is_popular': False,
            },
            {
                'name_en': 'Four Seasons Sultanahmet',
                'name_fa': 'هتل فورسیزنز سلطان احمد',
                'description_en': 'Historic luxury hotel in old city',
                'description_fa': 'هتل لوکس تاریخی در شهر قدیمی',
                'address': 'Sultanahmet, Tevkifhane Sk. No:1, 34110 Fatih/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.006200'),
                'longitude': Decimal('28.978500'),
                'location_type': 'hotel',
                'is_popular': False,
            },
        ]

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for loc_data in locations_data:
                # Extract translation data
                name_en = loc_data.pop('name_en')
                name_fa = loc_data.pop('name_fa')
                description_en = loc_data.pop('description_en')
                description_fa = loc_data.pop('description_fa')

                # Check if location already exists
                location, created = TransferLocation.objects.get_or_create(
                    city=loc_data['city'],
                    latitude=loc_data['latitude'],
                    longitude=loc_data['longitude'],
                    defaults=loc_data
                )

                # Set translations
                location.set_current_language('en')
                location.name = name_en
                location.description = description_en
                location.save()

                location.set_current_language('fa')
                location.name = name_fa
                location.description = description_fa
                location.save()

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {name_en}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⟳ Updated: {name_en}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created: {created_count}, Updated: {updated_count}'
            )
        )
