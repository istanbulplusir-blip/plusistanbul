#!/usr/bin/env python
"""
Check transfer data in database
"""
import os
import sys
import django

# Add backend directory to path
sys.path.insert(0, 'peykan-tourism1/backend')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferOption, TransferRoutePricing

def check_transfer_data():
    print("=== Transfer Data Check ===")

    # Check routes
    routes = TransferRoute.objects.all()
    print(f"Total routes: {routes.count()}")

    for route in routes:
        print(f"Route: {route} (ID: {route.id})")
        print(f"  Slug: {route.slug}")
        print(f"  Options count: {route.options.count()}")

        # Check pricing
        pricing = route.pricing.all()
        print(f"  Pricing count: {pricing.count()}")

        for price in pricing:
            print(f"    Vehicle: {price.vehicle_type} - ${price.base_price}")

        # Check options
        options = route.options.all()
        for option in options:
            print(f"    Option: {option} (Slug: {option.slug})")
            print(f"      Route: {option.route}")
            print(f"      Vehicle type: {option.vehicle_type}")

    # Check all options
    all_options = TransferOption.objects.all()
    print(f"\nTotal options: {all_options.count()}")

    for option in all_options:
        print(f"Option: {option} (Slug: {option.slug})")

if __name__ == '__main__':
    check_transfer_data()
