#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute

def check_transfer_products():
    routes = TransferRoute.objects.all()
    print(f"Found {routes.count()} transfer routes:")

    for route in routes[:5]:  # Show first 5
        print(f"\nRoute: {route.origin} → {route.destination}")
        print(f"Slug: {route.slug}")

        # Get pricing
        pricing = route.pricing.all()
        print(f"Pricing options: {pricing.count()}")

        for p in pricing:
            print(f"  - {p.vehicle_type}: ${p.base_price} (max {p.max_passengers} passengers)")

if __name__ == '__main__':
    check_transfer_products()
