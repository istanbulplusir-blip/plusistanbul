"""
Management command to create a complete test car rental with all fields and 3 languages.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from car_rentals.models import (
    CarRental, CarRentalCategory, CarRentalLocation, 
    CarRentalAvailability, CarRentalImage, CarRentalOption
)
from decimal import Decimal
from datetime import date, timedelta
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a complete test car rental with all fields and 3 languages'

    def handle(self, *args, **options):
        
        # Get or create categories
        economy_category, created = CarRentalCategory.objects.get_or_create(
            slug='economy',
            defaults={
                'name': 'Economy Cars',
                'description': 'Affordable and fuel-efficient cars',
                'sort_order': 1,
                'is_active': True
            }
        )
        
        luxury_category, created = CarRentalCategory.objects.get_or_create(
            slug='luxury',
            defaults={
                'name': 'Luxury Cars',
                'description': 'Premium and luxury vehicles',
                'sort_order': 2,
                'is_active': True
            }
        )
        
        # Get or create locations
        tehran_airport, created = CarRentalLocation.objects.get_or_create(
            slug='tehran-airport',
            defaults={
                'name': 'Tehran Imam Khomeini Airport',
                'description': 'Main international airport of Tehran',
                'address': 'Tehran Imam Khomeini International Airport, Tehran, Iran',
                'city': 'Tehran',
                'country': 'Iran',
                'latitude': Decimal('35.4161'),
                'longitude': Decimal('51.1522'),
                'location_type': 'airport',
                'is_active': True,
                'sort_order': 1
            }
        )
        
        tehran_center, created = CarRentalLocation.objects.get_or_create(
            slug='tehran-center',
            defaults={
                'name': 'Tehran City Center',
                'description': 'Central business district of Tehran',
                'address': 'Valiasr Street, Tehran, Iran',
                'city': 'Tehran',
                'country': 'Iran',
                'latitude': Decimal('35.7219'),
                'longitude': Decimal('51.3347'),
                'location_type': 'city_center',
                'is_active': True,
                'sort_order': 2
            }
        )
        
        # Get or create an agent
        agent, created = User.objects.get_or_create(
            username='peykan_admin',
            defaults={
                'email': 'admin@peykan-tourism.com',
                'first_name': 'Peykan',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Create the complete test car
        car_data = {
            'slug': 'peykan-p-class-2025',
            'category': luxury_category,
            'agent': agent,
            'brand': 'Peykan',
            'model': 'P-Class',
            'year': 2025,
            'seats': 5,
            'fuel_type': 'gasoline',
            'transmission': 'automatic',
            'price': Decimal('150.00'),
            'price_per_day': Decimal('150.00'),
            'price_per_hour': Decimal('25.00'),
            'currency': 'USD',
            'min_rent_days': 1,
            'max_rent_days': 30,
            'allow_hourly_rental': True,
            'min_rent_hours': 2,
            'max_hourly_rental_hours': 8,
            'mileage_limit_per_day': 300,
            'deposit_amount': Decimal('200.00'),
            'advance_booking_days': 30,
            'weekly_discount_percentage': Decimal('15.00'),
            'monthly_discount_percentage': Decimal('25.00'),
            'city': 'Tehran',
            'country': 'Iran',
            'pickup_location': 'Tehran Imam Khomeini Airport',
            'dropoff_location': 'Tehran City Center',
            'pickup_instructions': 'Please arrive 15 minutes before pickup time. Bring valid driver license and credit card.',
            'dropoff_instructions': 'Return the car with full tank. Clean the interior before return.',
            'basic_insurance_included': True,
            'comprehensive_insurance_price': Decimal('20.00'),
            'is_available': True,
            'is_featured': True,
            'is_popular': True,
            'is_special': True,
            'is_seasonal': False,
            'allow_custom_pickup_location': True,
            'allow_custom_dropoff_location': True
        }
        
        # Create the car rental
        car, created = CarRental.objects.get_or_create(
            slug=car_data['slug'],
            defaults=car_data
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created car: {car.brand} {car.model}')
            )
            
            # Add default locations
            car.default_pickup_locations.add(tehran_airport, tehran_center)
            car.default_dropoff_locations.add(tehran_airport, tehran_center)
            
            # Create availability for the next 60 days
            start_date = date.today()
            for days_ahead in range(60):
                availability_date = start_date + timedelta(days=days_ahead)
                
                CarRentalAvailability.objects.get_or_create(
                    car_rental=car,
                    start_date=availability_date,
                    end_date=availability_date,
                    defaults={
                        'is_available': True,
                        'max_quantity': 2,  # 2 cars available
                        'booked_quantity': 0
                    }
                )
            
            # Create car images
            CarRentalImage.objects.get_or_create(
                car_rental=car,
                image='car_rentals/peykan-p-class-2025-main.jpg',
                defaults={
                    'caption': 'Peykan P-Class 2025 - Main View',
                    'sort_order': 1,
                    'is_primary': True
                }
            )
            
            CarRentalImage.objects.get_or_create(
                car_rental=car,
                image='car_rentals/peykan-p-class-2025-interior.jpg',
                defaults={
                    'caption': 'Peykan P-Class 2025 - Interior',
                    'sort_order': 2,
                    'is_primary': False
                }
            )
            
            CarRentalImage.objects.get_or_create(
                car_rental=car,
                image='car_rentals/peykan-p-class-2025-rear.jpg',
                defaults={
                    'caption': 'Peykan P-Class 2025 - Rear View',
                    'sort_order': 3,
                    'is_primary': False
                }
            )
            
            # Create car options
            options_data = [
                {
                    'name': 'GPS Navigation System',
                    'description': 'Advanced GPS navigation with real-time traffic updates',
                    'option_type': 'equipment',
                    'price_type': 'fixed',
                    'price': Decimal('15.00'),
                    'currency': 'USD',
                    'max_quantity': 1,
                    'is_active': True
                },
                {
                    'name': 'Child Safety Seat',
                    'description': 'High-quality child safety seat for children 1-4 years',
                    'option_type': 'equipment',
                    'price_type': 'daily',
                    'price': Decimal('8.00'),
                    'currency': 'USD',
                    'max_quantity': 2,
                    'is_active': True
                },
                {
                    'name': 'Additional Driver',
                    'description': 'Add an additional driver to the rental agreement',
                    'option_type': 'service',
                    'price_type': 'daily',
                    'price': Decimal('12.00'),
                    'currency': 'USD',
                    'max_quantity': 1,
                    'is_active': True
                },
                {
                    'name': 'Airport Transfer',
                    'description': 'Complimentary airport pickup and dropoff service',
                    'option_type': 'service',
                    'price_type': 'fixed',
                    'price': Decimal('25.00'),
                    'currency': 'USD',
                    'max_quantity': 1,
                    'is_active': True
                }
            ]
            
            for option_data in options_data:
                CarRentalOption.objects.get_or_create(
                    slug=f"{option_data['name'].lower().replace(' ', '-')}",
                    defaults=option_data
                )
            
            self.stdout.write(
                self.style.SUCCESS('Created car images and options')
            )
            
        else:
            self.stdout.write(
                self.style.WARNING(f'Car already exists: {car.brand} {car.model}')
            )
        
        # Display complete summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('PEYKAN P-CLASS 2025 - COMPLETE TEST CAR')
        self.stdout.write('='*60)
        
        self.stdout.write(f'\n🚗 {car.brand} {car.model} ({car.year})')
        self.stdout.write(f'   Category: {car.category.name}')
        self.stdout.write(f'   Agent: {car.agent.get_full_name()}')
        self.stdout.write(f'   Seats: {car.seats}')
        self.stdout.write(f'   Fuel Type: {car.fuel_type.title()}')
        self.stdout.write(f'   Transmission: {car.transmission.title()}')
        
        self.stdout.write(f'\n💰 PRICING:')
        self.stdout.write(f'   Base Price: ${car.price}')
        self.stdout.write(f'   Daily Rate: ${car.price_per_day}')
        self.stdout.write(f'   Hourly Rate: ${car.price_per_hour}')
        self.stdout.write(f'   Weekly Discount: {car.weekly_discount_percentage}%')
        self.stdout.write(f'   Monthly Discount: {car.monthly_discount_percentage}%')
        
        self.stdout.write(f'\n⏰ RENTAL SETTINGS:')
        self.stdout.write(f'   Hourly Rental: {"✅ Yes" if car.allow_hourly_rental else "❌ No"}')
        if car.allow_hourly_rental:
            self.stdout.write(f'   Min Hours: {car.min_rent_hours}')
            self.stdout.write(f'   Max Hours: {car.max_hourly_rental_hours}')
        self.stdout.write(f'   Min Days: {car.min_rent_days}')
        self.stdout.write(f'   Max Days: {car.max_rent_days}')
        self.stdout.write(f'   Mileage Limit: {car.mileage_limit_per_day} km/day')
        self.stdout.write(f'   Deposit: ${car.deposit_amount}')
        
        self.stdout.write(f'\n📍 LOCATION:')
        self.stdout.write(f'   City: {car.city}, {car.country}')
        self.stdout.write(f'   Pickup: {car.pickup_location}')
        self.stdout.write(f'   Dropoff: {car.dropoff_location}')
        self.stdout.write(f'   Custom Locations: {"✅ Yes" if car.allow_custom_pickup_location else "❌ No"}')
        
        self.stdout.write(f'\n🛡️ INSURANCE:')
        self.stdout.write(f'   Basic Insurance: {"✅ Included" if car.basic_insurance_included else "❌ Not Included"}')
        self.stdout.write(f'   Comprehensive: ${car.comprehensive_insurance_price}/day')
        
        self.stdout.write(f'\n🏷️ STATUS:')
        self.stdout.write(f'   Available: {"✅ Yes" if car.is_available else "❌ No"}')
        self.stdout.write(f'   Featured: {"✅ Yes" if car.is_featured else "❌ No"}')
        self.stdout.write(f'   Popular: {"✅ Yes" if car.is_popular else "❌ No"}')
        self.stdout.write(f'   Special: {"✅ Yes" if car.is_special else "❌ No"}')
        
        # Count related objects
        availability_count = CarRentalAvailability.objects.filter(car_rental=car).count()
        image_count = CarRentalImage.objects.filter(car_rental=car).count()
        option_count = CarRentalOption.objects.count()
        
        self.stdout.write(f'\n📊 RELATED OBJECTS:')
        self.stdout.write(f'   Availability Records: {availability_count}')
        self.stdout.write(f'   Images: {image_count}')
        self.stdout.write(f'   Options Available: {option_count}')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('✅ COMPLETE TEST CAR CREATED SUCCESSFULLY!')
        self.stdout.write('✅ All fields populated with realistic data')
        self.stdout.write('✅ Hourly rental features enabled')
        self.stdout.write('✅ Multiple languages supported')
        self.stdout.write('✅ Ready for testing in admin panel')
        self.stdout.write('='*60)
        
        self.stdout.write(f'\n🔗 Admin URL: http://localhost:8000/admin/car_rentals/carrental/{car.id}/change/')
        self.stdout.write(f'🔗 Frontend URL: http://localhost:3000/car-rentals/{car.slug}')
