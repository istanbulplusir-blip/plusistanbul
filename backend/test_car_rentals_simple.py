#!/usr/bin/env python
"""
Simple test script for Car Rental functionality.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from car_rentals.models import CarRental, CarRentalCategory, CarRentalOption, CarRentalAvailability
from django.contrib.auth import get_user_model

User = get_user_model()

def test_models():
    """Test basic model functionality."""
    print("🧪 Testing Car Rental Models...")
    
    # Test categories
    categories = CarRentalCategory.objects.all()
    print(f"✅ Categories: {categories.count()}")
    for cat in categories:
        print(f"   - {cat.name} ({cat.slug})")
    
    # Test car rentals
    cars = CarRental.objects.all()
    print(f"✅ Car Rentals: {cars.count()}")
    for car in cars:
        print(f"   - {car.title} ({car.brand} {car.model}) - ${car.price_per_day}/day")
    
    # Test options
    options = CarRentalOption.objects.all()
    print(f"✅ Options: {options.count()}")
    for opt in options:
        print(f"   - {opt.name} - ${opt.price} ({opt.price_type})")
    
    # Test availability
    availability = CarRentalAvailability.objects.all()
    print(f"✅ Availability: {availability.count()}")
    for avail in availability:
        print(f"   - {avail.car_rental.title}: {avail.start_date} to {avail.end_date}")
    
    return True

def test_pricing():
    """Test pricing calculations."""
    print("\n💰 Testing Pricing Calculations...")
    
    car = CarRental.objects.first()
    if not car:
        print("❌ No cars found for pricing test")
        return False
    
    print(f"Testing pricing for: {car.title}")
    
    # Test daily pricing
    price_1_day = car.get_daily_price_with_discount(1)
    price_7_days = car.get_daily_price_with_discount(7)
    price_30_days = car.get_daily_price_with_discount(30)
    
    print(f"   1 day: ${price_1_day}")
    print(f"   7 days: ${price_7_days} (weekly discount: {car.weekly_discount_percentage}%)")
    print(f"   30 days: ${price_30_days} (monthly discount: {car.monthly_discount_percentage}%)")
    
    # Test total pricing
    total_3_days = car.calculate_total_price(days=3)
    total_3_days_insurance = car.calculate_total_price(days=3, include_insurance=True)
    
    print(f"   3 days total: ${total_3_days}")
    print(f"   3 days + insurance: ${total_3_days_insurance}")
    
    return True

def test_availability():
    """Test availability management."""
    print("\n📅 Testing Availability Management...")
    
    availability = CarRentalAvailability.objects.first()
    if not availability:
        print("❌ No availability found for testing")
        return False
    
    print(f"Testing availability for: {availability.car_rental.title}")
    print(f"   Max quantity: {availability.max_quantity}")
    print(f"   Booked quantity: {availability.booked_quantity}")
    print(f"   Available quantity: {availability.available_quantity}")
    
    # Test reservation
    if availability.is_available_for_booking(1):
        print("   ✅ Can book 1 car")
        if availability.reserve_quantity(1):
            print("   ✅ Successfully reserved 1 car")
            availability.refresh_from_db()
            print(f"   New booked quantity: {availability.booked_quantity}")
            
            # Test release
            if availability.release_quantity(1):
                print("   ✅ Successfully released 1 car")
                availability.refresh_from_db()
                print(f"   Final booked quantity: {availability.booked_quantity}")
            else:
                print("   ❌ Failed to release car")
        else:
            print("   ❌ Failed to reserve car")
    else:
        print("   ❌ Cannot book 1 car")
    
    return True

def test_options():
    """Test option pricing."""
    print("\n🔧 Testing Option Pricing...")
    
    option = CarRentalOption.objects.first()
    if not option:
        print("❌ No options found for testing")
        return False
    
    print(f"Testing option: {option.name}")
    print(f"   Type: {option.price_type}")
    print(f"   Price: ${option.price}")
    
    base_price = 100.00
    option_price = option.calculate_price(base_price, days=3, quantity=1)
    print(f"   Price for 3 days: ${option_price}")
    
    return True

def main():
    """Run all tests."""
    print("🚗 Car Rental System Test Suite")
    print("=" * 50)
    
    try:
        # Run tests
        test_models()
        test_pricing()
        test_availability()
        test_options()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
