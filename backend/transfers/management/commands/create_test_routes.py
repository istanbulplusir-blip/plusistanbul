from django.core.management.base import BaseCommand
from transfers.models import TransferLocation, TransferRoute, TransferRoutePricing, TransferOption
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = _('Creates test transfer routes with vehicles and pricing.')

    def handle(self, *args, **options):
        # Get locations by city and coordinates
        ist_airport = TransferLocation.objects.filter(
            city='Istanbul',
            latitude=41.2753,
            longitude=28.7519
        ).first()
        saw_airport = TransferLocation.objects.filter(
            city='Istanbul',
            latitude=40.8986,
            longitude=29.3092
        ).first()
        golden_age = TransferLocation.objects.filter(
            city='Istanbul',
            latitude=41.0370,
            longitude=28.9850
        ).first()
        dora_pera = TransferLocation.objects.filter(
            city='Istanbul',
            latitude=41.0300,
            longitude=28.9800
        ).first()
        dora_hotel = TransferLocation.objects.filter(
            city='Istanbul',
            latitude=41.0600,
            longitude=28.9900
        ).first()
        
        if not all([ist_airport, saw_airport, golden_age, dora_pera, dora_hotel]):
            self.stdout.write(
                self.style.ERROR('Some locations are missing. Please run create_istanbul_locations first.')
            )
            return

        # Test routes
        test_routes = [
            {
                'name': 'Istanbul Airport to Golden Age Hotel Taksim',
                'description': 'Direct transfer from Istanbul New Airport to Golden Age Hotel in Taksim',
                'origin_location': ist_airport,
                'destination_location': golden_age,
                'origin': 'Istanbul New Airport (IST)',
                'destination': 'Golden Age Hotel Taksim',
                'distance_km': 45,
                'estimated_duration_minutes': 60,
                'is_active': True,
                'is_popular': True
            },
            {
                'name': 'Istanbul Airport to Dora Hotel Pera',
                'description': 'Direct transfer from Istanbul New Airport to Dora Hotel Pera',
                'origin_location': ist_airport,
                'destination_location': dora_pera,
                'origin': 'Istanbul New Airport (IST)',
                'destination': 'Dora Hotel Pera',
                'distance_km': 42,
                'estimated_duration_minutes': 55,
                'is_active': True,
                'is_popular': True
            },
            {
                'name': 'Istanbul Airport to Dora Hotel',
                'description': 'Direct transfer from Istanbul New Airport to Dora Hotel',
                'origin_location': ist_airport,
                'destination_location': dora_hotel,
                'origin': 'Istanbul New Airport (IST)',
                'destination': 'Dora Hotel',
                'distance_km': 40,
                'estimated_duration_minutes': 50,
                'is_active': True,
                'is_popular': True
            },
            {
                'name': 'Sabiha Gökçen Airport to Golden Age Hotel Taksim',
                'description': 'Direct transfer from Sabiha Gökçen Airport to Golden Age Hotel in Taksim',
                'origin_location': saw_airport,
                'destination_location': golden_age,
                'origin': 'Sabiha Gökçen Airport (SAW)',
                'destination': 'Golden Age Hotel Taksim',
                'distance_km': 35,
                'estimated_duration_minutes': 45,
                'is_active': True,
                'is_popular': True
            },
            {
                'name': 'Sabiha Gökçen Airport to Dora Hotel Pera',
                'description': 'Direct transfer from Sabiha Gökçen Airport to Dora Hotel Pera',
                'origin_location': saw_airport,
                'destination_location': dora_pera,
                'origin': 'Sabiha Gökçen Airport (SAW)',
                'destination': 'Dora Hotel Pera',
                'distance_km': 38,
                'estimated_duration_minutes': 50,
                'is_active': True,
                'is_popular': True
            }
        ]

        # Vehicle types and pricing
        vehicle_configs = [
            {
                'vehicle_type': 'sedan',
                'vehicle_name': 'Economy Sedan',
                'vehicle_description': 'Comfortable sedan for up to 4 passengers',
                'max_passengers': 4,
                'max_luggage': 2,
                'base_price': 50,
                'features': ['Air Conditioning', 'Radio'],
                'amenities': ['Mineral Water']
            },
            {
                'vehicle_type': 'suv',
                'vehicle_name': 'Comfort SUV',
                'vehicle_description': 'Spacious SUV for up to 6 passengers',
                'max_passengers': 6,
                'max_luggage': 4,
                'base_price': 80,
                'features': ['Air Conditioning', 'Radio', 'Charger'],
                'amenities': ['Mineral Water', 'Snacks']
            },
            {
                'vehicle_type': 'van',
                'vehicle_name': 'Business Van',
                'vehicle_description': 'Premium van for up to 8 passengers',
                'max_passengers': 8,
                'max_luggage': 6,
                'base_price': 120,
                'features': ['Air Conditioning', 'Radio', 'Charger', 'WiFi'],
                'amenities': ['Mineral Water', 'Snacks', 'Newspaper']
            }
        ]

        created_routes = 0
        created_pricing = 0

        for route_data in test_routes:
            # Check if route exists
            existing_route = TransferRoute.objects.filter(
                origin_location=route_data['origin_location'],
                destination_location=route_data['destination_location']
            ).first()

            if not existing_route:
                # Create route
                route = TransferRoute.objects.create(
                    origin_location=route_data['origin_location'],
                    destination_location=route_data['destination_location'],
                    origin=route_data['origin'],
                    destination=route_data['destination'],
                    estimated_duration_minutes=route_data['estimated_duration_minutes'],
                    is_active=route_data['is_active']
                )
                
                # Set translatable fields
                route.set_current_language('en')
                route.name = route_data['name']
                route.description = route_data['description']
                route.save()

                # Create pricing for each vehicle type
                for vehicle_config in vehicle_configs:
                    # Calculate price based on distance (base price + distance factor)
                    distance_factor = route_data['distance_km'] * 0.5
                    final_price = vehicle_config['base_price'] + distance_factor

                    TransferRoutePricing.objects.create(
                        route=route,
                        vehicle_type=vehicle_config['vehicle_type'],
                        vehicle_name=vehicle_config['vehicle_name'],
                        vehicle_description=vehicle_config['vehicle_description'],
                        max_passengers=vehicle_config['max_passengers'],
                        max_luggage=vehicle_config['max_luggage'],
                        base_price=final_price,
                        currency='USD',
                        features=vehicle_config['features'],
                        amenities=vehicle_config['amenities']
                    )
                    created_pricing += 1

                created_routes += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created route: {route_data["name"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Route already exists: {route_data["name"]}')
                )

        # Create test options
        test_options = [
            {
                'name': 'Child Seat',
                'description': 'Child safety seat for children under 4 years',
                'price': 15,
                'option_type': 'extra_luggage',
                'price_type': 'fixed',
                'is_active': True
            },
            {
                'name': 'Extra Luggage',
                'description': 'Additional luggage space for oversized bags',
                'price': 20,
                'option_type': 'extra_luggage',
                'price_type': 'fixed',
                'is_active': True
            }
        ]

        created_options = 0
        for option_data in test_options:
            # Check if option exists by checking if any option has this name
            existing_option = None
            for option in TransferOption.objects.all():
                try:
                    if option.name == option_data['name']:
                        existing_option = option
                        break
                except:
                    continue

            if not existing_option:
                option = TransferOption.objects.create(
                    price=option_data['price'],
                    option_type=option_data['option_type'],
                    price_type=option_data['price_type'],
                    is_active=option_data['is_active']
                )
                # Set translatable fields
                option.set_current_language('en')
                option.name = option_data['name']
                option.description = option_data['description']
                option.save()
                
                created_options += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created option: {option_data["name"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_routes} routes, {created_pricing} pricing entries, and {created_options} options'
            )
        )
