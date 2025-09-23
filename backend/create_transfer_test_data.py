#!/usr/bin/env python3
"""
Script to create test data for Transfer locations and routes.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from decimal import Decimal
from transfers.models import TransferLocation, TransferRoute, TransferRoutePricing
from django.utils.text import slugify

def create_test_locations():
    """Create test locations for major Iranian cities."""
    
    locations_data = [
        # Tehran
        {
            'name': 'فرودگاه امام خمینی تهران',
            'description': 'فرودگاه اصلی تهران',
            'address': 'فرودگاه امام خمینی، تهران',
            'city': 'تهران',
            'country': 'ایران',
            'latitude': Decimal('35.6892'),
            'longitude': Decimal('51.3890'),
            'location_type': 'airport',
            'is_popular': True
        },
        {
            'name': 'هتل اسپیناس پالاس تهران',
            'description': 'هتل لوکس در مرکز تهران',
            'address': 'خیابان ولیعصر، تهران',
            'city': 'تهران',
            'country': 'ایران',
            'latitude': Decimal('35.7219'),
            'longitude': Decimal('51.4134'),
            'location_type': 'hotel',
            'is_popular': True
        },
        
        # Isfahan
        {
            'name': 'فرودگاه اصفهان',
            'description': 'فرودگاه اصفهان',
            'address': 'فرودگاه اصفهان، اصفهان',
            'city': 'اصفهان',
            'country': 'ایران',
            'latitude': Decimal('32.7508'),
            'longitude': Decimal('51.8614'),
            'location_type': 'airport',
            'is_popular': True
        },
        {
            'name': 'هتل عباسی اصفهان',
            'description': 'هتل تاریخی اصفهان',
            'address': 'خیابان چهارباغ، اصفهان',
            'city': 'اصفهان',
            'country': 'ایران',
            'latitude': Decimal('32.6546'),
            'longitude': Decimal('51.6680'),
            'location_type': 'hotel',
            'is_popular': True
        },
        
        # Shiraz
        {
            'name': 'فرودگاه شیراز',
            'description': 'فرودگاه شیراز',
            'address': 'فرودگاه شیراز، شیراز',
            'city': 'شیراز',
            'country': 'ایران',
            'latitude': Decimal('29.5392'),
            'longitude': Decimal('52.5900'),
            'location_type': 'airport',
            'is_popular': True
        },
        {
            'name': 'هتل هما شیراز',
            'description': 'هتل معروف شیراز',
            'address': 'خیابان زند، شیراز',
            'city': 'شیراز',
            'country': 'ایران',
            'latitude': Decimal('29.5918'),
            'longitude': Decimal('52.5837'),
            'location_type': 'hotel',
            'is_popular': True
        },
        
        # Mashhad
        {
            'name': 'فرودگاه مشهد',
            'description': 'فرودگاه مشهد',
            'address': 'فرودگاه مشهد، مشهد',
            'city': 'مشهد',
            'country': 'ایران',
            'latitude': Decimal('36.2350'),
            'longitude': Decimal('59.6412'),
            'location_type': 'airport',
            'is_popular': True
        },
        {
            'name': 'هتل پارس مشهد',
            'description': 'هتل نزدیک حرم امام رضا',
            'address': 'خیابان امام رضا، مشهد',
            'city': 'مشهد',
            'country': 'ایران',
            'latitude': Decimal('36.2890'),
            'longitude': Decimal('59.6069'),
            'location_type': 'hotel',
            'is_popular': True
        },
        
        # Tabriz
        {
            'name': 'فرودگاه تبریز',
            'description': 'فرودگاه تبریز',
            'address': 'فرودگاه تبریز، تبریز',
            'city': 'تبریز',
            'country': 'ایران',
            'latitude': Decimal('38.1339'),
            'longitude': Decimal('46.2350'),
            'location_type': 'airport',
            'is_popular': False
        },
        
        # Yazd
        {
            'name': 'فرودگاه یزد',
            'description': 'فرودگاه یزد',
            'address': 'فرودگاه یزد، یزد',
            'city': 'یزد',
            'country': 'ایران',
            'latitude': Decimal('31.8974'),
            'longitude': Decimal('54.2771'),
            'location_type': 'airport',
            'is_popular': False
        }
    ]
    
    created_locations = []
    for location_data in locations_data:
        # Check if location exists by city and coordinates
        existing_location = TransferLocation.objects.filter(
            city=location_data['city'],
            latitude=location_data['latitude'],
            longitude=location_data['longitude']
        ).first()
        
        if existing_location:
            print(f"Location already exists: {existing_location}")
            created_locations.append(existing_location)
        else:
            location = TransferLocation.objects.create(**location_data)
            print(f"Created location: {location}")
            created_locations.append(location)
    
    return created_locations

def create_test_routes(locations):
    """Create test routes between locations."""
    
    # Create routes between major cities
    route_combinations = [
        # Tehran routes
        ('فرودگاه امام خمینی تهران', 'هتل اسپیناس پالاس تهران'),
        ('هتل اسپیناس پالاس تهران', 'فرودگاه امام خمینی تهران'),
        
        # Tehran to other cities
        ('فرودگاه امام خمینی تهران', 'فرودگاه اصفهان'),
        ('فرودگاه اصفهان', 'فرودگاه امام خمینی تهران'),
        ('فرودگاه امام خمینی تهران', 'فرودگاه شیراز'),
        ('فرودگاه شیراز', 'فرودگاه امام خمینی تهران'),
        ('فرودگاه امام خمینی تهران', 'فرودگاه مشهد'),
        ('فرودگاه مشهد', 'فرودگاه امام خمینی تهران'),
        
        # Isfahan routes
        ('فرودگاه اصفهان', 'هتل عباسی اصفهان'),
        ('هتل عباسی اصفهان', 'فرودگاه اصفهان'),
        
        # Shiraz routes
        ('فرودگاه شیراز', 'هتل هما شیراز'),
        ('هتل هما شیراز', 'فرودگاه شیراز'),
        
        # Mashhad routes
        ('فرودگاه مشهد', 'هتل پارس مشهد'),
        ('هتل پارس مشهد', 'فرودگاه مشهد'),
        
        # Inter-city routes
        ('فرودگاه اصفهان', 'فرودگاه شیراز'),
        ('فرودگاه شیراز', 'فرودگاه اصفهان'),
        ('فرودگاه اصفهان', 'فرودگاه مشهد'),
        ('فرودگاه مشهد', 'فرودگاه اصفهان'),
    ]
    
    created_routes = []
    for origin_name, destination_name in route_combinations:
        try:
            # Find locations by searching in translations
            origin_location = None
            destination_location = None
            
            for location in TransferLocation.objects.all():
                if hasattr(location, 'name') and location.name == origin_name:
                    origin_location = location
                if hasattr(location, 'name') and location.name == destination_name:
                    destination_location = location
            
            if not origin_location or not destination_location:
                print(f"Location not found: {origin_name} or {destination_name}")
                continue
            
            route, created = TransferRoute.objects.get_or_create(
                origin=origin_name,
                destination=destination_name,
                defaults={
                    'origin_location': origin_location,
                    'destination_location': destination_location,
                    'estimated_duration_minutes': 45 if 'فرودگاه' in origin_name and 'فرودگاه' in destination_name else 30,
                    'peak_hour_surcharge': Decimal('15.00'),
                    'midnight_surcharge': Decimal('10.00'),
                    'round_trip_discount_enabled': True,
                    'round_trip_discount_percentage': Decimal('10.00'),
                    'is_popular': True if origin_location.is_popular and destination_location.is_popular else False,
                    'is_active': True
                }
            )
            
            if created:
                print(f"Created route: {route.origin} → {route.destination}")
                created_routes.append(route)
            else:
                print(f"Route already exists: {route.origin} → {route.destination}")
                created_routes.append(route)
                
        except TransferLocation.DoesNotExist as e:
            print(f"Location not found: {e}")
    
    return created_routes

def create_test_pricing(routes):
    """Create pricing for routes with different vehicle types."""
    
    vehicle_types = [
        ('sedan', 'سدان', 4, 2),
        ('suv', 'SUV', 6, 4),
        ('van', 'ون', 8, 6),
        ('sprinter', 'اسپرینتر', 12, 8),
    ]
    
    base_prices = {
        'sedan': Decimal('50.00'),
        'suv': Decimal('70.00'),
        'van': Decimal('90.00'),
        'sprinter': Decimal('120.00'),
    }
    
    created_pricings = []
    for route in routes:
        for vehicle_type, vehicle_name, max_passengers, max_luggage in vehicle_types:
            base_price = base_prices[vehicle_type]
            
            # Adjust price based on distance (simple logic)
            if 'تهران' in route.origin and 'تهران' in route.destination:
                # Local route
                price_multiplier = Decimal('1.0')
            elif 'تهران' in route.origin or 'تهران' in route.destination:
                # To/from Tehran
                price_multiplier = Decimal('1.5')
            else:
                # Inter-city
                price_multiplier = Decimal('1.3')
            
            final_price = base_price * price_multiplier
            
            pricing, created = TransferRoutePricing.objects.get_or_create(
                route=route,
                vehicle_type=vehicle_type,
                defaults={
                    'vehicle_name': vehicle_name,
                    'vehicle_description': f'خودرو {vehicle_name} برای {max_passengers} نفر',
                    'base_price': final_price,
                    'currency': 'USD',
                    'max_passengers': max_passengers,
                    'max_luggage': max_luggage,
                    'features': ['AC', 'WiFi', 'Professional Driver'],
                    'amenities': ['Water', 'Tissue', 'USB Charger'],
                    'pricing_metadata': {
                        "pricing_type": "transfer",
                        "calculation_method": "base_plus_surcharges",
                        "version": "1.0",
                        "features": {
                            "time_based_surcharges": True,
                            "round_trip_discounts": True,
                            "options_support": True
                        }
                    },
                    'is_active': True
                }
            )
            
            if created:
                print(f"Created pricing: {route.origin} → {route.destination} ({vehicle_type}): ${final_price}")
                created_pricings.append(pricing)
            else:
                print(f"Pricing already exists: {route.origin} → {route.destination} ({vehicle_type})")
                created_pricings.append(pricing)
    
    return created_pricings

def main():
    """Main function to create all test data."""
    print("Creating transfer test data...")
    
    # Create locations
    print("\n1. Creating locations...")
    locations = create_test_locations()
    
    # Create routes
    print("\n2. Creating routes...")
    routes = create_test_routes(locations)
    
    # Create pricing
    print("\n3. Creating pricing...")
    pricings = create_test_pricing(routes)
    
    print(f"\n✅ Test data creation completed!")
    print(f"   - {len(locations)} locations")
    print(f"   - {len(routes)} routes")
    print(f"   - {len(pricings)} pricing records")
    
    print("\n📊 Summary:")
    print(f"   - Popular locations: {TransferLocation.objects.filter(is_popular=True).count()}")
    print(f"   - Active routes: {TransferRoute.objects.filter(is_active=True).count()}")
    print(f"   - Active pricing: {TransferRoutePricing.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    main()
