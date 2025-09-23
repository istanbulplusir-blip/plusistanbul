#!/usr/bin/env python
"""
Create sample transfer data for testing.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from django.utils.translation import activate

def create_sample_data():
    """Create sample transfer data."""
    print("🚀 Creating sample transfer data...")
    
    # Create transfer routes with translations
    routes_data = [
        {
            'origin': 'Tehran Airport',
            'destination': 'Tehran City Center',
            'translations': {
                'fa': {
                    'name': 'فرودگاه تهران به مرکز شهر',
                    'description': 'انتقال راحت و سریع از فرودگاه امام خمینی به مرکز تهران'
                },
                'en': {
                    'name': 'Tehran Airport to City Center',
                    'description': 'Comfortable and fast transfer from Imam Khomeini Airport to Tehran city center'
                },
                'tr': {
                    'name': 'Tahran Havalimanından Şehir Merkezine',
                    'description': 'İmam Humeyni Havalimanından Tahran şehir merkezine konforlu ve hızlı transfer'
                }
            },
            'is_popular': True,
            'is_admin_selected': True,
            'popularity_score': 95
        },
        {
            'origin': 'Shiraz Airport',
            'destination': 'Shiraz City Center',
            'translations': {
                'fa': {
                    'name': 'فرودگاه شیراز به مرکز شهر',
                    'description': 'انتقال مستقیم از فرودگاه شیراز به مرکز تاریخی شهر'
                },
                'en': {
                    'name': 'Shiraz Airport to City Center',
                    'description': 'Direct transfer from Shiraz Airport to the historic city center'
                },
                'tr': {
                    'name': 'Şiraz Havalimanından Şehir Merkezine',
                    'description': 'Şiraz Havalimanından tarihi şehir merkezine direkt transfer'
                }
            },
            'is_popular': True,
            'is_admin_selected': False,
            'popularity_score': 85
        },
        {
            'origin': 'Isfahan Airport',
            'destination': 'Isfahan City Center',
            'translations': {
                'fa': {
                    'name': 'فرودگاه اصفهان به مرکز شهر',
                    'description': 'انتقال راحت به مرکز تاریخی اصفهان'
                },
                'en': {
                    'name': 'Isfahan Airport to City Center',
                    'description': 'Comfortable transfer to the historic center of Isfahan'
                },
                'tr': {
                    'name': 'İsfahan Havalimanından Şehir Merkezine',
                    'description': 'İsfahan\'ın tarihi merkezine konforlu transfer'
                }
            },
            'is_popular': False,
            'is_admin_selected': False,
            'popularity_score': 70
        }
    ]
    
    # Create routes
    created_routes = []
    for route_data in routes_data:
        route = TransferRoute.objects.create(
            origin=route_data['origin'],
            destination=route_data['destination'],
            is_popular=route_data['is_popular'],
            is_admin_selected=route_data['is_admin_selected'],
            popularity_score=route_data['popularity_score'],
            peak_hour_surcharge=Decimal('15.00'),
            midnight_surcharge=Decimal('10.00'),
            round_trip_discount_enabled=True,
            round_trip_discount_percentage=Decimal('10.00')
        )
        
        # Add translations
        for lang_code, translation in route_data['translations'].items():
            activate(lang_code)
            route.set_current_language(lang_code)
            route.name = translation['name']
            route.description = translation['description']
            route.save()
        
        created_routes.append(route)
        print(f"✅ Created route: {route_data['origin']} → {route_data['destination']}")
    
    # Create pricing for each route
    vehicle_types = [
        ('sedan', 'Sedan', 25.00, 4, 2),
        ('suv', 'SUV', 35.00, 6, 4),
        ('van', 'Van', 45.00, 8, 6),
        ('sprinter', 'Sprinter', 60.00, 12, 8),
    ]
    
    for route in created_routes:
        for vehicle_type, vehicle_name, base_price, max_passengers, max_luggage in vehicle_types:
            pricing = TransferRoutePricing.objects.create(
                route=route,
                vehicle_type=vehicle_type,
                vehicle_name=vehicle_name,
                vehicle_description=f"Comfortable {vehicle_name} for {max_passengers} passengers",
                base_price=Decimal(str(base_price)),
                max_passengers=max_passengers,
                max_luggage=max_luggage,
                features=['AC', 'WiFi', 'GPS'],
                amenities=['Water', 'Snacks']
            )
            print(f"✅ Created pricing: {route.origin} → {route.destination} - {vehicle_name}")
    
    # Create transfer options with translations
    options_data = [
        {
            'option_type': 'wheelchair',
            'translations': {
                'fa': {
                    'name': 'صندلی چرخدار',
                    'description': 'صندلی چرخدار برای مسافران با نیازهای ویژه'
                },
                'en': {
                    'name': 'Wheelchair',
                    'description': 'Wheelchair for passengers with special needs'
                },
                'tr': {
                    'name': 'Tekerlekli Sandalye',
                    'description': 'Özel ihtiyaçları olan yolcular için tekerlekli sandalye'
                }
            },
            'price_type': 'fixed',
            'price': Decimal('15.00'),
            'price_percentage': Decimal('0.00')
        },
        {
            'option_type': 'english_driver',
            'translations': {
                'fa': {
                    'name': 'راننده انگلیسی‌زبان',
                    'description': 'راننده مسلط به زبان انگلیسی'
                },
                'en': {
                    'name': 'English Speaking Driver',
                    'description': 'Driver fluent in English'
                },
                'tr': {
                    'name': 'İngilizce Konuşan Sürücü',
                    'description': 'İngilizce konuşabilen sürücü'
                }
            },
            'price_type': 'percentage',
            'price': Decimal('0.00'),
            'price_percentage': Decimal('10.00')
        },
        {
            'option_type': 'meet_greet',
            'translations': {
                'fa': {
                    'name': 'خدمات استقبال',
                    'description': 'استقبال در فرودگاه با تابلو نام'
                },
                'en': {
                    'name': 'Meet & Greet',
                    'description': 'Airport pickup with name sign'
                },
                'tr': {
                    'name': 'Karşılama Hizmeti',
                    'description': 'İsim tabelası ile havalimanında karşılama'
                }
            },
            'price_type': 'fixed',
            'price': Decimal('20.00'),
            'price_percentage': Decimal('0.00')
        }
    ]
    
    for option_data in options_data:
        option = TransferOption.objects.create(
            option_type=option_data['option_type'],
            price_type=option_data['price_type'],
            price=option_data['price'],
            price_percentage=option_data['price_percentage'],
            max_quantity=5
        )
        
        # Add translations
        for lang_code, translation in option_data['translations'].items():
            activate(lang_code)
            option.set_current_language(lang_code)
            option.name = translation['name']
            option.description = translation['description']
            option.save()
        
        print(f"✅ Created option: {option_data['option_type']}")
    
    print("\n🎉 Sample transfer data created successfully!")
    print(f"📊 Created {len(created_routes)} routes with pricing and options")
    
    return created_routes

if __name__ == '__main__':
    try:
        routes = create_sample_data()
        print("\n✅ Transfer data creation completed!")
    except Exception as e:
        print(f"\n❌ Error creating transfer data: {str(e)}")
        import traceback
        traceback.print_exc() 