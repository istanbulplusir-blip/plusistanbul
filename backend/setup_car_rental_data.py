#!/usr/bin/env python
"""
Setup script for car rental data with new location and time features.
"""

import os
import sys
import django
from datetime import datetime, time, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from car_rentals.models import CarRental, CarRentalLocation, CarRentalCategory, CarRentalOption
from agents.models import Agent
from django.utils.translation import activate
from django.utils.text import slugify


def create_car_rental_locations():
    """Create predefined car rental locations."""
    print("Creating car rental locations...")
    
    locations_data = [
        {
            'name': 'Istanbul Airport (IST)',
            'description': 'Istanbul Airport - Main Terminal',
            'address': 'Istanbul Airport, Terminal 1, Arnavutköy, Istanbul',
            'city': 'Istanbul',
            'country': 'Turkey',
            'latitude': Decimal('41.2753'),
            'longitude': Decimal('28.7519'),
            'location_type': 'airport',
            'sort_order': 1,
            'operating_hours_start': time(6, 0),
            'operating_hours_end': time(23, 0),
        },
        {
            'name': 'Sabiha Gökçen Airport (SAW)',
            'description': 'Sabiha Gökçen Airport - Domestic Terminal',
            'address': 'Sabiha Gökçen Airport, Pendik, Istanbul',
            'city': 'Istanbul',
            'country': 'Turkey',
            'latitude': Decimal('40.8986'),
            'longitude': Decimal('29.3092'),
            'location_type': 'airport',
            'sort_order': 2,
            'operating_hours_start': time(5, 30),
            'operating_hours_end': time(22, 30),
        },
        {
            'name': 'Taksim Square',
            'description': 'Taksim Square - City Center',
            'address': 'Taksim Square, Beyoğlu, Istanbul',
            'city': 'Istanbul',
            'country': 'Turkey',
            'latitude': Decimal('41.0370'),
            'longitude': Decimal('28.9850'),
            'location_type': 'city_center',
            'sort_order': 3,
            'operating_hours_start': time(8, 0),
            'operating_hours_end': time(20, 0),
        },
        {
            'name': 'Kadıköy Ferry Terminal',
            'description': 'Kadıköy Ferry Terminal',
            'address': 'Kadıköy Ferry Terminal, Kadıköy, Istanbul',
            'city': 'Istanbul',
            'country': 'Turkey',
            'latitude': Decimal('40.9906'),
            'longitude': Decimal('29.0250'),
            'location_type': 'port',
            'sort_order': 4,
            'operating_hours_start': time(6, 0),
            'operating_hours_end': time(23, 0),
        },
        {
            'name': 'Antalya Airport (AYT)',
            'description': 'Antalya Airport - International Terminal',
            'address': 'Antalya Airport, Antalya',
            'city': 'Antalya',
            'country': 'Turkey',
            'latitude': Decimal('36.8981'),
            'longitude': Decimal('30.8005'),
            'location_type': 'airport',
            'sort_order': 5,
            'operating_hours_start': time(5, 0),
            'operating_hours_end': time(23, 59),
        },
        {
            'name': 'Cappadocia - Göreme',
            'description': 'Göreme Village Center',
            'address': 'Göreme Village, Nevşehir',
            'city': 'Nevşehir',
            'country': 'Turkey',
            'latitude': Decimal('38.6431'),
            'longitude': Decimal('34.8306'),
            'location_type': 'other',
            'sort_order': 6,
            'operating_hours_start': time(8, 0),
            'operating_hours_end': time(18, 0),
        },
    ]
    
    created_locations = []
    for location_data in locations_data:
        location, created = CarRentalLocation.objects.get_or_create(
            slug=slugify(location_data['name']),
            defaults=location_data
        )
        if created:
            print(f"Created location: {location.name}")
            created_locations.append(location)
        else:
            print(f"Location already exists: {location.name}")
            created_locations.append(location)
    
    return created_locations


def create_car_rental_categories():
    """Create car rental categories."""
    print("Creating car rental categories...")
    
    categories_data = [
        {
            'name': 'Economy Cars',
            'description': 'Budget-friendly cars for city driving',
            'sort_order': 1,
        },
        {
            'name': 'Compact Cars',
            'description': 'Small and efficient cars',
            'sort_order': 2,
        },
        {
            'name': 'Mid-size Cars',
            'description': 'Comfortable cars for longer trips',
            'sort_order': 3,
        },
        {
            'name': 'Luxury Cars',
            'description': 'Premium cars with advanced features',
            'sort_order': 4,
        },
        {
            'name': 'SUVs',
            'description': 'Large vehicles for families and groups',
            'sort_order': 5,
        },
    ]
    
    created_categories = []
    for category_data in categories_data:
        category, created = CarRentalCategory.objects.get_or_create(
            slug=slugify(category_data['name']),
            defaults=category_data
        )
        if created:
            print(f"Created category: {category.name}")
            created_categories.append(category)
        else:
            print(f"Category already exists: {category.name}")
            created_categories.append(category)
    
    return created_categories


def create_car_rental_options():
    """Create car rental options."""
    print("Creating car rental options...")
    
    options_data = [
        {
            'name': 'GPS Navigation',
            'description': 'GPS navigation system',
            'option_type': 'gps',
            'price': Decimal('10.00'),
            'price_type': 'daily',
            'is_active': True,
        },
        {
            'name': 'Child Safety Seat',
            'description': 'Child safety seat for children',
            'option_type': 'child_seat',
            'price': Decimal('15.00'),
            'price_type': 'daily',
            'is_active': True,
        },
        {
            'name': 'Additional Driver',
            'description': 'Additional driver authorization',
            'option_type': 'additional_driver',
            'price': Decimal('25.00'),
            'price_type': 'fixed',
            'is_active': True,
        },
        {
            'name': 'Premium Insurance',
            'description': 'Premium insurance coverage',
            'option_type': 'premium_insurance',
            'price': Decimal('50.00'),
            'price_type': 'fixed',
            'is_active': True,
        },
        {
            'name': 'Roadside Assistance',
            'description': '24/7 roadside assistance service',
            'option_type': 'roadside_assistance',
            'price': Decimal('30.00'),
            'price_type': 'fixed',
            'is_active': True,
        },
    ]
    
    created_options = []
    for option_data in options_data:
        option, created = CarRentalOption.objects.get_or_create(
            slug=slugify(option_data['name']),
            defaults=option_data
        )
        if created:
            print(f"Created option: {option.name}")
            created_options.append(option)
        else:
            print(f"Option already exists: {option.name}")
            created_options.append(option)
    
    return created_options


def create_car_rentals(categories, locations, options):
    """Create car rental products with new features."""
    print("Creating car rental products...")
    
    # Get the test agent's user
    agent = Agent.objects.first()
    if not agent:
        print("No agent found. Please create an agent first.")
        return []
    
    user = agent.user
    
    cars_data = [
        {
            'title': 'Toyota Corolla 2023',
            'description': 'Reliable and fuel-efficient economy car',
            'short_description': 'Perfect for city driving and short trips',
            'brand': 'Toyota',
            'model': 'Corolla',
            'year': 2023,
            'category': categories[0],  # Economy
            'seats': 5,
            'fuel_type': 'gasoline',
            'transmission': 'automatic',
            'min_rent_days': 1,
            'max_rent_days': 30,
            'advance_booking_days': 0,
            'price_per_day': Decimal('45.00'),
            'price': Decimal('45.00'),
            'currency': 'USD',
            'pickup_location': 'Istanbul Airport',
            'dropoff_location': 'Istanbul Airport',
            'default_pickup_locations': [locations[0], locations[1], locations[2]],  # IST, SAW, Taksim
            'default_dropoff_locations': [locations[0], locations[1], locations[2]],
            'allow_custom_pickup_location': True,
            'allow_custom_dropoff_location': True,
            'agent': user,
        },
        {
            'title': 'Honda Civic 2023',
            'description': 'Sporty and efficient compact car',
            'short_description': 'Great for city driving with sporty performance',
            'brand': 'Honda',
            'model': 'Civic',
            'year': 2023,
            'category': categories[1],  # Compact
            'seats': 5,
            'fuel_type': 'gasoline',
            'transmission': 'automatic',
            'min_rent_days': 1,
            'max_rent_days': 30,
            'advance_booking_days': 0,
            'price_per_day': Decimal('55.00'),
            'price': Decimal('55.00'),
            'currency': 'USD',
            'pickup_location': 'Istanbul Airport',
            'dropoff_location': 'Istanbul Airport',
            'default_pickup_locations': [locations[0], locations[1], locations[2]],
            'default_dropoff_locations': [locations[0], locations[1], locations[2]],
            'allow_custom_pickup_location': True,
            'allow_custom_dropoff_location': True,
            'agent': user,
        },
        {
            'title': 'BMW 3 Series 2023',
            'description': 'Luxury sedan with premium features',
            'short_description': 'Premium luxury car with advanced technology',
            'brand': 'BMW',
            'model': '3 Series',
            'year': 2023,
            'category': categories[3],  # Luxury
            'seats': 5,
            'fuel_type': 'gasoline',
            'transmission': 'automatic',
            'min_rent_days': 2,
            'max_rent_days': 30,
            'advance_booking_days': 1,
            'price_per_day': Decimal('120.00'),
            'price': Decimal('120.00'),
            'currency': 'USD',
            'pickup_location': 'Istanbul Airport',
            'dropoff_location': 'Istanbul Airport',
            'default_pickup_locations': [locations[0], locations[1], locations[2]],
            'default_dropoff_locations': [locations[0], locations[1], locations[2]],
            'allow_custom_pickup_location': True,
            'allow_custom_dropoff_location': True,
            'agent': user,
        },
        {
            'title': 'Toyota RAV4 2023',
            'description': 'Spacious SUV perfect for families',
            'short_description': 'Family-friendly SUV with ample space',
            'brand': 'Toyota',
            'model': 'RAV4',
            'year': 2023,
            'category': categories[4],  # SUV
            'seats': 7,
            'fuel_type': 'gasoline',
            'transmission': 'automatic',
            'min_rent_days': 1,
            'max_rent_days': 30,
            'advance_booking_days': 0,
            'price_per_day': Decimal('85.00'),
            'price': Decimal('85.00'),
            'currency': 'USD',
            'pickup_location': 'Istanbul Airport',
            'dropoff_location': 'Istanbul Airport',
            'default_pickup_locations': [locations[0], locations[1], locations[2]],
            'default_dropoff_locations': [locations[0], locations[1], locations[2]],
            'allow_custom_pickup_location': True,
            'allow_custom_dropoff_location': True,
            'agent': user,
        },
        {
            'title': 'Volkswagen Golf 2023',
            'description': 'German engineering in a compact package',
            'short_description': 'Reliable German compact car',
            'brand': 'Volkswagen',
            'model': 'Golf',
            'year': 2023,
            'category': categories[1],  # Compact
            'seats': 5,
            'fuel_type': 'gasoline',
            'transmission': 'manual',
            'min_rent_days': 1,
            'max_rent_days': 30,
            'advance_booking_days': 0,
            'price_per_day': Decimal('60.00'),
            'price': Decimal('60.00'),
            'currency': 'USD',
            'pickup_location': 'Istanbul Airport',
            'dropoff_location': 'Istanbul Airport',
            'default_pickup_locations': [locations[0], locations[1], locations[2]],
            'default_dropoff_locations': [locations[0], locations[1], locations[2]],
            'allow_custom_pickup_location': True,
            'allow_custom_dropoff_location': True,
            'agent': user,
        },
    ]
    
    created_cars = []
    for car_data in cars_data:
        # Extract pickup and dropoff locations
        pickup_locations = car_data.pop('default_pickup_locations')
        dropoff_locations = car_data.pop('default_dropoff_locations')
        
        car, created = CarRental.objects.get_or_create(
            slug=slugify(f"{car_data['brand']}-{car_data['model']}-{car_data['year']}"),
            defaults=car_data
        )
        
        if created:
            # Add pickup and dropoff locations
            car.default_pickup_locations.set(pickup_locations)
            car.default_dropoff_locations.set(dropoff_locations)
            
            print(f"Created car: {car.brand} {car.model} ({car.year})")
            created_cars.append(car)
        else:
            print(f"Car already exists: {car.brand} {car.model} ({car.year})")
            created_cars.append(car)
    
    return created_cars


def main():
    """Main setup function."""
    print("Setting up car rental data with new location and time features...")
    print("=" * 60)
    
    # Create locations
    locations = create_car_rental_locations()
    print(f"Created/Found {len(locations)} locations")
    print()
    
    # Create categories
    categories = create_car_rental_categories()
    print(f"Created/Found {len(categories)} categories")
    print()
    
    # Create options
    options = create_car_rental_options()
    print(f"Created/Found {len(options)} options")
    print()
    
    # Create car rentals
    cars = create_car_rentals(categories, locations, options)
    print(f"Created/Found {len(cars)} car rentals")
    print()
    
    print("=" * 60)
    print("Setup completed successfully!")
    print()
    print("Summary:")
    print(f"- Locations: {len(locations)}")
    print(f"- Categories: {len(categories)}")
    print(f"- Options: {len(options)}")
    print(f"- Car Rentals: {len(cars)}")
    print()
    print("You can now test the car rental booking system with:")
    print("- Predefined pickup/dropoff locations")
    print("- Custom location selection")
    print("- Time validation (6 hours advance for pickup, 24 hours minimum rental)")
    print("- Location-based pricing and availability")


if __name__ == '__main__':
    main()
