#!/usr/bin/env python
"""
Simple test for car rental API.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from car_rentals.models import CarRental, CarRentalLocation

def simple_test():
    """Simple test."""
    print("Simple Car Rental Test")
    print("=" * 30)
    
    # Test 1: Locations
    locations = CarRentalLocation.objects.all()
    print(f"1. Locations count: {locations.count()}")
    for loc in locations[:3]:
        print(f"   - {loc.name} ({loc.location_type})")
    
    print()
    
    # Test 2: Car Rentals
    cars = CarRental.objects.all()
    print(f"2. Car rentals count: {cars.count()}")
    for car in cars[:3]:
        print(f"   - {car.brand} {car.model} ({car.year}) - ${car.price_per_day}/day")
        print(f"     Pickup locations: {car.default_pickup_locations.count()}")
        print(f"     Dropoff locations: {car.default_dropoff_locations.count()}")
    
    print()
    print("Test completed!")

if __name__ == '__main__':
    simple_test()
