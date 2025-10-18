"""
Management command to create test transfer data.
Creates sample locations, routes, pricing, and options for testing.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from transfers.models import (
    TransferLocation, TransferRoute, TransferRoutePricing, 
    TransferOption, TransferCancellationPolicy
)


class Command(BaseCommand):
    help = 'Create test transfer data (locations, routes, pricing, options)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing transfer data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing transfer data...')
            self.clear_existing_data()

        self.stdout.write('Creating test transfer data...')
        
        with transaction.atomic():
            # Create locations
            locations = self.create_locations()
            
            # Create routes
            routes = self.create_routes(locations)
            
            # Create pricing for routes
            self.create_pricing(routes)
            
            # Create options
            self.create_options()
            
            # Create cancellation policies
            self.create_cancellation_policies(routes)

        self.stdout.write(
            self.style.SUCCESS('Test transfer data created successfully!')
        )

    def clear_existing_data(self):
        """Clear existing transfer data."""
        TransferCancellationPolicy.objects.all().delete()
        TransferRoutePricing.objects.all().delete()
        TransferOption.objects.all().delete()
        TransferRoute.objects.all().delete()
        TransferLocation.objects.all().delete()
        self.stdout.write('Existing transfer data cleared.')

    def create_locations(self):
        """Create test transfer locations."""
        locations_data = [
            {
                'name': 'Istanbul Airport (IST)',
                'description': 'Istanbul Airport - Main international airport',
                'address': 'Tayakadın, Terminal Caddesi No:1, 34283 Arnavutköy/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.2753'),
                'longitude': Decimal('28.7519'),
                'location_type': 'airport',
                'is_active': True,
                'is_popular': True,
            },
            {
                'name': 'Sabiha Gokcen Airport (SAW)',
                'description': 'Sabiha Gokcen Airport - Secondary airport',
                'address': 'Sanayi, 34906 Pendik/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('40.8986'),
                'longitude': Decimal('29.3092'),
                'location_type': 'airport',
                'is_active': True,
                'is_popular': True,
            },
            {
                'name': 'Sultanahmet Square',
                'description': 'Historic center of Istanbul',
                'address': 'Sultan Ahmet, 34122 Fatih/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.0055'),
                'longitude': Decimal('28.9769'),
                'location_type': 'landmark',
                'is_active': True,
                'is_popular': True,
            },
            {
                'name': 'Taksim Square',
                'description': 'Modern center of Istanbul',
                'address': 'Gümüşsuyu, 34437 Beyoğlu/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.0370'),
                'longitude': Decimal('28.9850'),
                'location_type': 'landmark',
                'is_active': True,
                'is_popular': True,
            },
            {
                'name': 'Kadıköy',
                'description': 'Asian side district',
                'address': 'Kadıköy, İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('40.9906'),
                'longitude': Decimal('29.0250'),
                'location_type': 'landmark',
                'is_active': True,
                'is_popular': False,
            },
        ]

        locations = []
        for data in locations_data:
            location, created = TransferLocation.objects.get_or_create(
                address=data['address'],
                defaults=data
            )
            if created:
                self.stdout.write('Created location')
            locations.append(location)

        return locations

    def create_routes(self, locations):
        """Create test transfer routes."""
        routes_data = [
            {
                'name': 'Istanbul Airport to Sultanahmet',
                'description': 'Transfer from Istanbul Airport to historic center',
                'origin': 'Istanbul Airport (IST)',
                'destination': 'Sultanahmet Square',
                'origin_location': locations[0],  # IST Airport
                'destination_location': locations[2],  # Sultanahmet
                'estimated_duration_minutes': 45,
                'round_trip_discount_enabled': True,
                'round_trip_discount_percentage': Decimal('15.00'),
                'peak_hour_surcharge': Decimal('20.00'),
                'midnight_surcharge': Decimal('10.00'),
                'is_active': True,
                'is_popular': True,
            },
            {
                'name': 'Istanbul Airport to Taksim',
                'description': 'Transfer from Istanbul Airport to modern center',
                'origin': 'Istanbul Airport (IST)',
                'destination': 'Taksim Square',
                'origin_location': locations[0],  # IST Airport
                'destination_location': locations[3],  # Taksim
                'estimated_duration_minutes': 50,
                'round_trip_discount_enabled': True,
                'round_trip_discount_percentage': Decimal('15.00'),
                'peak_hour_surcharge': Decimal('20.00'),
                'midnight_surcharge': Decimal('10.00'),
                'is_active': True,
                'is_popular': True,
            },
            {
                'name': 'Sabiha Gokcen to Sultanahmet',
                'description': 'Transfer from Sabiha Gokcen Airport to historic center',
                'origin': 'Sabiha Gokcen Airport (SAW)',
                'destination': 'Sultanahmet Square',
                'origin_location': locations[1],  # SAW Airport
                'destination_location': locations[2],  # Sultanahmet
                'estimated_duration_minutes': 60,
                'round_trip_discount_enabled': True,
                'round_trip_discount_percentage': Decimal('15.00'),
                'peak_hour_surcharge': Decimal('20.00'),
                'midnight_surcharge': Decimal('10.00'),
                'is_active': True,
                'is_popular': True,
            },
            {
                'name': 'Sultanahmet to Taksim',
                'description': 'Transfer between historic and modern centers',
                'origin': 'Sultanahmet Square',
                'destination': 'Taksim Square',
                'origin_location': locations[2],  # Sultanahmet
                'destination_location': locations[3],  # Taksim
                'estimated_duration_minutes': 15,
                'round_trip_discount_enabled': False,
                'round_trip_discount_percentage': Decimal('0.00'),
                'peak_hour_surcharge': Decimal('10.00'),
                'midnight_surcharge': Decimal('5.00'),
                'is_active': True,
                'is_popular': False,
            },
        ]

        routes = []
        for data in routes_data:
            route, created = TransferRoute.objects.get_or_create(
                origin=data['origin'],
                destination=data['destination'],
                defaults=data
            )
            if created:
                self.stdout.write('Created route')
            routes.append(route)

        return routes

    def create_pricing(self, routes):
        """Create pricing for routes."""
        vehicle_types = [
            {
                'vehicle_type': 'sedan',
                'vehicle_name': 'Economy Sedan',
                'vehicle_description': 'Comfortable 4-seater sedan',
                'base_price': Decimal('25.00'),
                'max_passengers': 4,
                'max_luggage': 2,
                'features': ['Air Conditioning', 'WiFi', 'Water'],
                'amenities': ['Professional Driver', 'Meet & Greet'],
            },
            {
                'vehicle_type': 'suv',
                'vehicle_name': 'Premium SUV',
                'vehicle_description': 'Spacious 6-seater SUV',
                'base_price': Decimal('35.00'),
                'max_passengers': 6,
                'max_luggage': 4,
                'features': ['Air Conditioning', 'WiFi', 'Water', 'Charging Ports'],
                'amenities': ['Professional Driver', 'Meet & Greet', 'Flight Monitoring'],
            },
            {
                'vehicle_type': 'van',
                'vehicle_name': 'Family Van',
                'vehicle_description': 'Large 8-seater van for families',
                'base_price': Decimal('45.00'),
                'max_passengers': 8,
                'max_luggage': 6,
                'features': ['Air Conditioning', 'WiFi', 'Water', 'Charging Ports', 'Child Seats'],
                'amenities': ['Professional Driver', 'Meet & Greet', 'Flight Monitoring'],
            },
        ]

        for route in routes:
            for vehicle_data in vehicle_types:
                # Adjust base price based on route distance
                base_price = vehicle_data['base_price']
                if 'Airport' in route.origin and 'Sultanahmet' in route.destination:
                    base_price = base_price * Decimal('1.2')  # 20% more for airport transfers
                elif 'Sabiha Gökçen' in route.origin:
                    base_price = base_price * Decimal('1.3')  # 30% more for SAW transfers

                pricing_data = {
                    'route': route,
                    'vehicle_type': vehicle_data['vehicle_type'],
                    'vehicle_name': vehicle_data['vehicle_name'],
                    'vehicle_description': vehicle_data['vehicle_description'],
                    'base_price': base_price,
                    'currency': 'USD',
                    'pricing_metadata': {
                        'pricing_type': 'transfer',
                        'calculation_method': 'base_plus_surcharges'
                    },
                    'max_passengers': vehicle_data['max_passengers'],
                    'max_luggage': vehicle_data['max_luggage'],
                    'features': vehicle_data['features'],
                    'amenities': vehicle_data['amenities'],
                    'is_active': True,
                }

                pricing, created = TransferRoutePricing.objects.get_or_create(
                    route=route,
                    vehicle_type=vehicle_data['vehicle_type'],
                    defaults=pricing_data
                )
                if created:
                    self.stdout.write('Created pricing')

    def create_options(self):
        """Create transfer options."""
        options_data = [
            {
                'name': 'Wheelchair Accessible Vehicle',
                'description': 'Vehicle equipped with wheelchair accessibility',
                'option_type': 'wheelchair',
                'price_type': 'fixed',
                'price': Decimal('10.00'),
                'price_percentage': Decimal('0.00'),
                'is_active': True,
            },
            {
                'name': 'Extra Stop',
                'description': 'Additional stop during the journey',
                'option_type': 'extra_stop',
                'price_type': 'fixed',
                'price': Decimal('15.00'),
                'price_percentage': Decimal('0.00'),
                'is_active': True,
            },
            {
                'name': 'Extra Luggage',
                'description': 'Additional luggage space',
                'option_type': 'extra_luggage',
                'price_type': 'fixed',
                'price': Decimal('5.00'),
                'price_percentage': Decimal('0.00'),
                'is_active': True,
            },
            {
                'name': 'English Speaking Driver',
                'description': 'Driver who speaks English fluently',
                'option_type': 'english_driver',
                'price_type': 'percentage',
                'price': Decimal('0.00'),
                'price_percentage': Decimal('10.00'),
                'is_active': True,
            },
            {
                'name': 'Meet & Greet Service',
                'description': 'Driver will meet you at the arrival gate',
                'option_type': 'meet_greet',
                'price_type': 'fixed',
                'price': Decimal('20.00'),
                'price_percentage': Decimal('0.00'),
                'is_active': True,
            },
            {
                'name': 'Flight Monitoring',
                'description': 'Real-time flight tracking and updates',
                'option_type': 'flight_monitoring',
                'price_type': 'fixed',
                'price': Decimal('8.00'),
                'price_percentage': Decimal('0.00'),
                'is_active': True,
            },
        ]

        for data in options_data:
            option, created = TransferOption.objects.get_or_create(
                option_type=data['option_type'],
                defaults=data
            )
            if created:
                self.stdout.write('Created option')

    def create_cancellation_policies(self, routes):
        """Create cancellation policies for routes."""
        policies_data = [
            {
                'hours_before': 24,
                'refund_percentage': 100,
                'description': 'Full refund if cancelled 24+ hours before departure',
            },
            {
                'hours_before': 12,
                'refund_percentage': 75,
                'description': '75% refund if cancelled 12-24 hours before departure',
            },
            {
                'hours_before': 6,
                'refund_percentage': 50,
                'description': '50% refund if cancelled 6-12 hours before departure',
            },
            {
                'hours_before': 2,
                'refund_percentage': 25,
                'description': '25% refund if cancelled 2-6 hours before departure',
            },
        ]

        for route in routes:
            for policy_data in policies_data:
                policy, created = TransferCancellationPolicy.objects.get_or_create(
                    route=route,
                    hours_before=policy_data['hours_before'],
                    defaults=policy_data
                )
                if created:
                    self.stdout.write('Created policy')
