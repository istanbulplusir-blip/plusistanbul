"""
Management command to create fully orderable transfer routes/products for testing.
It ensures:
- Active locations and routes
- Active pricing for multiple vehicle types with required pricing_metadata
- Active options applicable to all vehicles
- Outputs created routes with pricing vehicle types for quick testing
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from transfers.models import (
    TransferLocation,
    TransferRoute,
    TransferRoutePricing,
    TransferOption,
    TransferCancellationPolicy,
)


class Command(BaseCommand):
    help = 'Create fully orderable transfer products (routes + pricing + options) for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing transfer data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing transfer data...')
            self.clear_all()

        with transaction.atomic():
            locations = self.ensure_locations()
            routes = self.ensure_routes(locations)
            self.ensure_pricing(routes)
            self.ensure_options()
            self.ensure_cancellation_policies(routes)

        self.print_summary(routes)

    # --- helpers ---
    def clear_all(self):
        TransferCancellationPolicy.objects.all().delete()
        TransferRoutePricing.objects.all().delete()
        TransferOption.objects.all().delete()
        TransferRoute.objects.all().delete()
        TransferLocation.objects.all().delete()

    def ensure_locations(self):
        data = [
            {
                'name': 'Istanbul Airport (IST)',
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
                'name': 'Taksim Square',
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
                'name': 'Sultanahmet Square',
                'address': 'Sultan Ahmet, 34122 Fatih/İstanbul',
                'city': 'Istanbul',
                'country': 'Turkey',
                'latitude': Decimal('41.0055'),
                'longitude': Decimal('28.9769'),
                'location_type': 'landmark',
                'is_active': True,
                'is_popular': True,
            },
        ]

        created = {}
        for item in data:
            obj, _ = TransferLocation.objects.get_or_create(
                address=item['address'], defaults=item
            )
            # Resolve a reliable key name for mapping
            key_name = item.get('name') or getattr(obj, 'name', None) or item['address']
            created[str(key_name)] = obj
        return created

    def ensure_routes(self, locations_by_name):
        routes_specs = [
            ('Istanbul Airport (IST)', 'Taksim Square', 50, True, Decimal('15.00')),
            ('Istanbul Airport (IST)', 'Sultanahmet Square', 45, True, Decimal('15.00')),
            ('Sabiha Gokcen Airport (SAW)', 'Taksim Square', 65, True, Decimal('15.00')),
        ]

        routes = []
        for origin_name, dest_name, duration, round_enabled, round_pct in routes_specs:
            origin_loc = locations_by_name[origin_name]
            dest_loc = locations_by_name[dest_name]

            defaults = {
                'name': f'{origin_name} to {dest_name}',
                'description': f'Transfer from {origin_name} to {dest_name}',
                'origin': origin_name,
                'destination': dest_name,
                'origin_location': origin_loc,
                'destination_location': dest_loc,
                'estimated_duration_minutes': duration,
                'round_trip_discount_enabled': round_enabled,
                'round_trip_discount_percentage': round_pct,
                'peak_hour_surcharge': Decimal('20.00'),
                'midnight_surcharge': Decimal('10.00'),
                'is_active': True,
                'is_popular': True,
            }

            route, _ = TransferRoute.objects.get_or_create(
                origin=origin_name, destination=dest_name, defaults=defaults
            )
            routes.append(route)
        return routes

    def ensure_pricing(self, routes):
        vehicles = [
            {
                'vehicle_type': 'sedan',
                'vehicle_name': 'Economy Sedan',
                'vehicle_description': 'Comfortable 4-seater sedan',
                'base_price': Decimal('35.00'),
                'max_passengers': 4,
                'max_luggage': 2,
                'features': ['Air Conditioning', 'WiFi'],
                'amenities': ['Professional Driver', 'Meet & Greet'],
            },
            {
                'vehicle_type': 'suv',
                'vehicle_name': 'Premium SUV',
                'vehicle_description': 'Spacious 6-seater SUV',
                'base_price': Decimal('55.00'),
                'max_passengers': 6,
                'max_luggage': 4,
                'features': ['Air Conditioning', 'WiFi', 'Charging Ports'],
                'amenities': ['Professional Driver', 'Meet & Greet', 'Flight Monitoring'],
            },
            {
                'vehicle_type': 'van',
                'vehicle_name': 'Family Van',
                'vehicle_description': 'Large 8-seater van',
                'base_price': Decimal('70.00'),
                'max_passengers': 8,
                'max_luggage': 6,
                'features': ['Air Conditioning', 'WiFi', 'Child Seats'],
                'amenities': ['Professional Driver', 'Meet & Greet'],
            },
        ]

        for route in routes:
            for v in vehicles:
                pricing_data = {
                    'route': route,
                    'vehicle_type': v['vehicle_type'],
                    'vehicle_name': v['vehicle_name'],
                    'vehicle_description': v['vehicle_description'],
                    'base_price': v['base_price'],
                    'currency': 'USD',
                    'pricing_metadata': {
                        'pricing_type': 'transfer',
                        'calculation_method': 'base_plus_surcharges',
                    },
                    'max_passengers': v['max_passengers'],
                    'max_luggage': v['max_luggage'],
                    'features': v['features'],
                    'amenities': v['amenities'],
                    'is_active': True,
                }

                TransferRoutePricing.objects.get_or_create(
                    route=route,
                    vehicle_type=v['vehicle_type'],
                    defaults=pricing_data,
                )

    def ensure_options(self):
        options = [
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
                'price': Decimal('7.00'),
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
        ]

        for opt in options:
            TransferOption.objects.get_or_create(
                option_type=opt['option_type'], defaults=opt
            )

    def ensure_cancellation_policies(self, routes):
        policies = [
            {'hours_before': 24, 'refund_percentage': 100, 'description': 'Full refund 24h+'},
            {'hours_before': 12, 'refund_percentage': 75, 'description': '75% refund 12-24h'},
            {'hours_before': 6, 'refund_percentage': 50, 'description': '50% refund 6-12h'},
            {'hours_before': 2, 'refund_percentage': 25, 'description': '25% refund 2-6h'},
        ]
        for route in routes:
            for p in policies:
                TransferCancellationPolicy.objects.get_or_create(
                    route=route,
                    hours_before=p['hours_before'],
                    defaults=p,
                )

    def print_summary(self, routes):
        self.stdout.write(self.style.SUCCESS('Orderable transfer products are ready.'))
        for route in routes:
            vehicle_types = list(
                route.pricing.filter(is_active=True).values_list('vehicle_type', flat=True)
            )
            self.stdout.write(f"- Route: {route.origin} -> {route.destination} | id={route.id}")
            self.stdout.write(f"  Vehicles: {', '.join(vehicle_types)}")


