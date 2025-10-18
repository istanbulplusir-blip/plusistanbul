"""
Management command to create car rentals with hourly rental capabilities.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from car_rentals.models import CarRental, CarRentalCategory, CarRentalAvailability
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample car rentals with hourly rental capabilities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Number of car rentals to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get or create a category
        category, created = CarRentalCategory.objects.get_or_create(
            slug='economy',
            defaults={
                'name': 'Economy Cars',
                'description': 'Affordable and fuel-efficient cars for short trips',
                'sort_order': 1,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created category: {category.name}')
            )
        
        # Get or create an agent
        agent, created = User.objects.get_or_create(
            username='car_agent',
            defaults={
                'email': 'car_agent@example.com',
                'first_name': 'Car',
                'last_name': 'Agent',
                'is_staff': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created agent: {agent.username}')
            )
        
        # Create car rentals with hourly capabilities
        cars_data = [
            {
                'title': 'Toyota Corolla - Hourly Rental',
                'description': 'Perfect for city trips and short rentals. Fuel-efficient and easy to drive.',
                'short_description': 'Economy car ideal for hourly rentals',
                'brand': 'Toyota',
                'model': 'Corolla',
                'year': 2023,
                'seats': 5,
                'fuel_type': 'gasoline',
                'transmission': 'automatic',
                'price': Decimal('45.00'),  # Base price (required field)
                'price_per_day': Decimal('45.00'),
                'price_per_hour': Decimal('8.00'),  # Hourly rate
                'allow_hourly_rental': True,
                'min_rent_hours': 4,  # Minimum 4 hours
                'max_hourly_rental_hours': 12,  # Maximum 12 hours for hourly rental
                'min_rent_days': 1,
                'max_rent_days': 30,
                'city': 'Tehran',
                'country': 'Iran',
                'pickup_location': 'Tehran Airport',
                'dropoff_location': 'Tehran Airport',
                'is_available': True,
                'is_featured': True
            },
            {
                'title': 'BMW 3 Series - Premium Hourly',
                'description': 'Luxury sedan perfect for business meetings and special occasions.',
                'short_description': 'Premium car with hourly rental option',
                'brand': 'BMW',
                'model': '3 Series',
                'year': 2024,
                'seats': 5,
                'fuel_type': 'gasoline',
                'transmission': 'automatic',
                'price': Decimal('120.00'),  # Base price (required field)
                'price_per_day': Decimal('120.00'),
                'price_per_hour': Decimal('25.00'),  # Higher hourly rate
                'allow_hourly_rental': True,
                'min_rent_hours': 2,  # Minimum 2 hours
                'max_hourly_rental_hours': 8,  # Maximum 8 hours for hourly rental
                'min_rent_days': 1,
                'max_rent_days': 30,
                'city': 'Tehran',
                'country': 'Iran',
                'pickup_location': 'Tehran City Center',
                'dropoff_location': 'Tehran City Center',
                'is_available': True,
                'is_popular': True
            },
            {
                'title': 'Mercedes S-Class - Daily Only',
                'description': 'Ultra-luxury sedan for long-term rentals and special events.',
                'short_description': 'Luxury car for daily rentals only',
                'brand': 'Mercedes',
                'model': 'S-Class',
                'year': 2024,
                'seats': 5,
                'fuel_type': 'gasoline',
                'transmission': 'automatic',
                'price': Decimal('200.00'),  # Base price (required field)
                'price_per_day': Decimal('200.00'),
                'price_per_hour': Decimal('0.00'),  # No hourly rate
                'allow_hourly_rental': False,  # No hourly rental
                'min_rent_hours': 0,  # Not applicable
                'max_hourly_rental_hours': 0,  # Not applicable
                'min_rent_days': 2,  # Minimum 2 days
                'max_rent_days': 30,
                'city': 'Tehran',
                'country': 'Iran',
                'pickup_location': 'Tehran Luxury District',
                'dropoff_location': 'Tehran Luxury District',
                'is_available': True,
                'is_special': True
            }
        ]
        
        created_cars = []
        
        for i, car_data in enumerate(cars_data[:count]):
            car, created = CarRental.objects.get_or_create(
                slug=f"{car_data['brand'].lower()}-{car_data['model'].lower().replace(' ', '-')}-{i+1}",
                defaults={
                    **car_data,
                    'category': category,
                    'agent': agent,
                    'currency': 'USD',
                    'basic_insurance_included': True,
                    'comprehensive_insurance_price': Decimal('15.00'),
                    'mileage_limit_per_day': 200,
                    'deposit_amount': Decimal('100.00'),
                    'advance_booking_days': 30,
                    'weekly_discount_percentage': Decimal('10.00'),
                    'monthly_discount_percentage': Decimal('20.00'),
                    'allow_custom_pickup_location': True,
                    'allow_custom_dropoff_location': True,
                    'is_seasonal': False
                }
            )
            
            if created:
                created_cars.append(car)
                self.stdout.write(
                    self.style.SUCCESS(f'Created car: {car.title}')
                )
                
                # Create availability for the next 30 days
                start_date = date.today()
                for days_ahead in range(30):
                    availability_date = start_date + timedelta(days=days_ahead)
                    
                    CarRentalAvailability.objects.get_or_create(
                        car_rental=car,
                        start_date=availability_date,
                        end_date=availability_date,
                        defaults={
                            'is_available': True,
                            'max_quantity': 1,
                            'booked_quantity': 0
                        }
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created availability for {car.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Car already exists: {car.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_cars)} car rentals with hourly rental capabilities!'
            )
        )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CREATED CARS SUMMARY:')
        self.stdout.write('='*50)
        
        for car in created_cars:
            self.stdout.write(f'\n🚗 {car.title}')
            self.stdout.write(f'   Brand: {car.brand} {car.model} ({car.year})')
            self.stdout.write(f'   Daily Rate: ${car.price_per_day}')
            if car.price_per_hour:
                self.stdout.write(f'   Hourly Rate: ${car.price_per_hour}')
            self.stdout.write(f'   Hourly Rental: {"✅ Yes" if car.allow_hourly_rental else "❌ No"}')
            if car.allow_hourly_rental:
                self.stdout.write(f'   Min Hours: {car.min_rent_hours}')
                self.stdout.write(f'   Max Hours: {car.max_hourly_rental_hours}')
            self.stdout.write(f'   Min Days: {car.min_rent_days}')
            self.stdout.write(f'   Max Days: {car.max_rent_days}')
            self.stdout.write(f'   Available: {"✅ Yes" if car.is_available else "❌ No"}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('You can now test the hourly rental features!')
        self.stdout.write('='*50)
