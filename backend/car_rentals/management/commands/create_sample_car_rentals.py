"""
Management command to create sample car rental data for testing.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from car_rentals.models import (
    CarRentalCategory, CarRental, CarRentalOption, 
    CarRentalAvailability, CarRentalImage
)

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample car rental data for testing"

    def handle(self, *args, **options):
        self.stdout.write("🚗 Creating sample car rental data...")
        
        # Create agent user if not exists
        agent, created = User.objects.get_or_create(
            username='car_agent',
            defaults={
                'email': 'car_agent@example.com',
                'first_name': 'Car',
                'last_name': 'Agent',
                'is_active': True,
                'role': 'agent'
            }
        )
        if created:
            agent.set_password('Test@123456')
            agent.save()
            self.stdout.write(f"✅ Created agent: {agent.username}")
        else:
            self.stdout.write(f"✅ Using existing agent: {agent.username}")
        
        # Create categories
        categories_data = [
            {'name': 'Economy', 'description': 'Budget-friendly cars for everyday use'},
            {'name': 'Luxury', 'description': 'Premium vehicles with high-end features'},
            {'name': 'SUV', 'description': 'Sport Utility Vehicles for family trips'},
            {'name': 'Convertible', 'description': 'Open-top cars for scenic drives'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = CarRentalCategory.objects.get_or_create(
                slug=cat_data['name'].lower().replace(' ', '-'),
                defaults={
                    'description': cat_data['description'],
                    'sort_order': len(categories) + 1,
                    'is_active': True
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f"✅ Created category: {category.name}")
        
        # Create car rental options
        options_data = [
            {
                'name': 'GPS Navigation',
                'description': 'GPS navigation system with real-time traffic updates',
                'option_type': 'gps',
                'price_type': 'daily',
                'price': Decimal('10.00'),
                'max_quantity': 1
            },
            {
                'name': 'Child Safety Seat',
                'description': 'Child safety seat for infants and toddlers',
                'option_type': 'safety',
                'price_type': 'fixed',
                'price': Decimal('25.00'),
                'max_quantity': 2
            },
            {
                'name': 'Premium Insurance',
                'description': 'Comprehensive insurance coverage with zero deductible',
                'option_type': 'premium_insurance',
                'price_type': 'percentage',
                'price_percentage': Decimal('15.00'),
                'max_quantity': 1
            },
            {
                'name': 'Additional Driver',
                'description': 'Add an additional authorized driver',
                'option_type': 'driver',
                'price_type': 'fixed',
                'price': Decimal('15.00'),
                'max_quantity': 3
            },
            {
                'name': 'WiFi Hotspot',
                'description': 'Mobile WiFi hotspot for internet access',
                'option_type': 'connectivity',
                'price_type': 'daily',
                'price': Decimal('8.00'),
                'max_quantity': 1
            }
        ]
        
        options = {}
        for opt_data in options_data:
            option_name = opt_data.pop('name')
            option, created = CarRentalOption.objects.get_or_create(
                slug=option_name.lower().replace(' ', '-').replace('&', 'and'),
                defaults={
                    **opt_data,
                    'name': option_name
                }
            )
            options[option_name] = option
            if created:
                self.stdout.write(f"✅ Created option: {option.name}")
        
        # Create car rentals
        cars_data = [
            {
                'title': 'BMW 3 Series',
                'description': 'Luxury sedan with premium features and excellent performance',
                'short_description': 'Comfortable luxury sedan perfect for business trips',
                'brand': 'BMW',
                'model': '3 Series',
                'year': 2023,
                'seats': 5,
                'fuel_type': 'gasoline',
                'transmission': 'automatic',
                'category': 'Luxury',
                'price_per_day': Decimal('120.00'),
                'price_per_hour': Decimal('20.00'),
                'weekly_discount_percentage': Decimal('10.00'),
                'monthly_discount_percentage': Decimal('20.00'),
                'city': 'Istanbul',
                'country': 'Turkey',
                'pickup_location': 'Istanbul Airport',
                'dropoff_location': 'Istanbul Airport',
                'is_featured': True,
                'is_popular': True
            },
            {
                'title': 'Mercedes S-Class',
                'description': 'Ultra-luxury sedan with cutting-edge technology and comfort',
                'short_description': 'The pinnacle of luxury and innovation',
                'brand': 'Mercedes',
                'model': 'S-Class',
                'year': 2023,
                'seats': 5,
                'fuel_type': 'gasoline',
                'transmission': 'automatic',
                'category': 'Luxury',
                'price_per_day': Decimal('200.00'),
                'price_per_hour': Decimal('35.00'),
                'weekly_discount_percentage': Decimal('15.00'),
                'monthly_discount_percentage': Decimal('25.00'),
                'city': 'Istanbul',
                'country': 'Turkey',
                'pickup_location': 'Istanbul Airport',
                'dropoff_location': 'Istanbul Airport',
                'is_featured': True
            },
            {
                'title': 'Toyota Corolla',
                'description': 'Reliable and fuel-efficient compact sedan',
                'short_description': 'Perfect for city driving and short trips',
                'brand': 'Toyota',
                'model': 'Corolla',
                'year': 2022,
                'seats': 5,
                'fuel_type': 'hybrid',
                'transmission': 'automatic',
                'category': 'Economy',
                'price_per_day': Decimal('60.00'),
                'price_per_hour': Decimal('12.00'),
                'weekly_discount_percentage': Decimal('5.00'),
                'monthly_discount_percentage': Decimal('15.00'),
                'city': 'Istanbul',
                'country': 'Turkey',
                'pickup_location': 'Istanbul Airport',
                'dropoff_location': 'Istanbul Airport',
                'is_popular': True
            },
            {
                'title': 'Audi Q5',
                'description': 'Premium SUV with excellent handling and spacious interior',
                'short_description': 'Perfect for family trips and outdoor adventures',
                'brand': 'Audi',
                'model': 'Q5',
                'year': 2023,
                'seats': 5,
                'fuel_type': 'gasoline',
                'transmission': 'automatic',
                'category': 'SUV',
                'price_per_day': Decimal('150.00'),
                'price_per_hour': Decimal('25.00'),
                'weekly_discount_percentage': Decimal('12.00'),
                'monthly_discount_percentage': Decimal('22.00'),
                'city': 'Istanbul',
                'country': 'Turkey',
                'pickup_location': 'Istanbul Airport',
                'dropoff_location': 'Istanbul Airport',
                'is_featured': True
            },
            {
                'title': 'BMW Z4',
                'description': 'Sporty convertible for an exhilarating driving experience',
                'short_description': 'Open-top driving pleasure with BMW performance',
                'brand': 'BMW',
                'model': 'Z4',
                'year': 2023,
                'seats': 2,
                'fuel_type': 'gasoline',
                'transmission': 'automatic',
                'category': 'Convertible',
                'price_per_day': Decimal('180.00'),
                'price_per_hour': Decimal('30.00'),
                'weekly_discount_percentage': Decimal('8.00'),
                'monthly_discount_percentage': Decimal('18.00'),
                'city': 'Istanbul',
                'country': 'Turkey',
                'pickup_location': 'Istanbul Airport',
                'dropoff_location': 'Istanbul Airport',
                'is_special': True
            }
        ]
        
        cars = {}
        for car_data in cars_data:
            category = categories[car_data.pop('category')]
            car_title = car_data.pop('title')
            car, created = CarRental.objects.get_or_create(
                slug=car_title.lower().replace(' ', '-').replace('&', 'and'),
                defaults={
                    **car_data,
                    'title': car_title,
                    'category': category,
                    'agent': agent,
                    'currency': 'USD',
                    'price': car_data['price_per_day'],  # Set base price from price_per_day
                    'min_rent_days': 1,
                    'max_rent_days': 30,
                    'mileage_limit_per_day': 200,
                    'deposit_amount': Decimal('500.00'),
                    'basic_insurance_included': True,
                    'comprehensive_insurance_price': Decimal('25.00'),
                    'is_available': True,
                    'advance_booking_days': 30,
                    'is_active': True
                }
            )
            cars[car_title] = car
            if created:
                self.stdout.write(f"✅ Created car: {car.title}")
        
        # Create availability for each car
        today = date.today()
        for car in cars.values():
            # Create availability for next 90 days
            availability, created = CarRentalAvailability.objects.get_or_create(
                car_rental=car,
                start_date=today,
                end_date=today + timedelta(days=90),
                defaults={
                    'is_available': True,
                    'max_quantity': 2,
                    'booked_quantity': 0
                }
            )
            if created:
                self.stdout.write(f"✅ Created availability for {car.title}")
        
        self.stdout.write("\n🎉 Sample car rental data created successfully!")
        self.stdout.write(f"📊 Created:")
        self.stdout.write(f"   - {len(categories)} categories")
        self.stdout.write(f"   - {len(options)} options")
        self.stdout.write(f"   - {len(cars)} car rentals")
        self.stdout.write(f"   - {len(cars)} availability periods")
        self.stdout.write(f"\n🔑 Test credentials:")
        self.stdout.write(f"   Agent: car_agent / Test@123456")
        self.stdout.write(f"\n🌐 Test the API at:")
        self.stdout.write(f"   http://localhost:8000/api/v1/car-rentals/")
