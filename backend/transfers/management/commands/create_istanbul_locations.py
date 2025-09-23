from django.core.management.base import BaseCommand
from transfers.models import TransferLocation


class Command(BaseCommand):
    help = 'Create Istanbul test locations'

    def handle(self, *args, **options):
        # مکان‌های تستی استانبول
        test_locations = [
            {
                'name': 'Istanbul New Airport (IST)',
                'address': 'Tayakadın, Terminal Caddesi No:1, 34283 Arnavutköy/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.2753,
                'longitude': 28.7519,
                'location_type': 'airport',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Sabiha Gökçen Airport (SAW)',
                'address': 'Sanayi Mahallesi, Sabiha Gökçen Havalimanı, 34912 Pendik/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 40.8986,
                'longitude': 29.3092,
                'location_type': 'airport',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Hilton Istanbul Bomonti',
                'address': 'Silahşör Caddesi No:42, 34381 Şişli/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.0608,
                'longitude': 28.9856,
                'location_type': 'hotel',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Hilton Istanbul Bosphorus',
                'address': 'Cumhuriyet Caddesi No:50, 34367 Harbiye/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.0478,
                'longitude': 28.9856,
                'location_type': 'hotel',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Taksim Square',
                'address': 'Taksim Meydanı, 34437 Beyoğlu/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.0370,
                'longitude': 28.9850,
                'location_type': 'landmark',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Beşiktaş',
                'address': 'Beşiktaş, İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.0425,
                'longitude': 29.0086,
                'location_type': 'district',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Kadıköy',
                'address': 'Kadıköy, İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 40.9900,
                'longitude': 29.0244,
                'location_type': 'district',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Sultanahmet',
                'address': 'Sultanahmet, Fatih/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.0082,
                'longitude': 28.9784,
                'location_type': 'landmark',
                'is_popular': True,
                'is_active': True
            },
            # Hotels requested by user
            {
                'name': 'Golden Age Hotel Taksim',
                'address': 'Taksim Square, Beyoğlu, Istanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.0370,
                'longitude': 28.9850,
                'location_type': 'hotel',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Dora Hotel Pera',
                'address': 'Pera, Beyoğlu, Istanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.0300,
                'longitude': 28.9800,
                'location_type': 'hotel',
                'is_popular': True,
                'is_active': True
            },
            {
                'name': 'Dora Hotel',
                'address': 'Şişli, Istanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': 41.0600,
                'longitude': 28.9900,
                'location_type': 'hotel',
                'is_popular': True,
                'is_active': True
            }
        ]
        
        created_count = 0
        for location_data in test_locations:
            # بررسی وجود مکان
            existing_location = TransferLocation.objects.filter(
                city=location_data['city'],
                latitude=location_data['latitude'],
                longitude=location_data['longitude']
            ).first()
            
            if not existing_location:
                location = TransferLocation.objects.create(
                    address=location_data['address'],
                    city=location_data['city'],
                    country=location_data['country'],
                    latitude=location_data['latitude'],
                    longitude=location_data['longitude'],
                    location_type=location_data['location_type'],
                    is_popular=location_data['is_popular'],
                    is_active=location_data['is_active']
                )
                # تنظیم نام ترجمه شده
                location.set_current_language('en')
                location.name = location_data['name']
                location.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created location: {location_data["name"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Location already exists: {location_data["name"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} Istanbul locations')
        )
