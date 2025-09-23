#!/usr/bin/env python
"""
Automated test for all real transfer products in the database.
Covers all active routes and vehicle types, with and without options.
"""

import os
import django
from decimal import Decimal
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption


def test_transfer_products():
    print("\n==== REAL TRANSFER PRODUCTS TEST ====")
    routes = TransferRoute.objects.filter(is_active=True)
    pricings = TransferRoutePricing.objects.filter(is_active=True)
    options = list(TransferOption.objects.filter(is_active=True))
    
    if not routes or not pricings:
        print("No active transfer routes or pricings found!")
        return
    
    print(f"Found {routes.count()} active routes and {pricings.count()} active pricings.")
    print(f"Found {len(options)} active options.")
    print("\n--- Testing all route/vehicle combinations ---\n")
    
    for pricing in pricings:
        route = pricing.route
        print(f"Route: {route.origin} → {route.destination} | Vehicle: {pricing.vehicle_type} | Base: ${pricing.base_price}")
        # One-way, no options
        try:
            result = pricing.calculate_price(hour=12, is_round_trip=False, selected_options=[])
            print(f"  [One-way] Final: ${result['final_price']} | Base: ${result['base_price']} | Surcharge: ${result['time_surcharge']} | Discount: ${result['round_trip_discount']} | Options: ${result['options_total']}")
        except Exception as e:
            print(f"  [One-way] ERROR: {e}")
        # Round-trip, no options
        try:
            result = pricing.calculate_price(hour=12, is_round_trip=True, selected_options=[])
            print(f"  [Round-trip] Final: ${result['final_price']} | Base: ${result['base_price']} | Surcharge: ${result['time_surcharge']} | Discount: ${result['round_trip_discount']} | Options: ${result['options_total']}")
        except Exception as e:
            print(f"  [Round-trip] ERROR: {e}")
        # With options (if any)
        if options:
            selected_options = [{
                'option_id': str(options[0].id),
                'quantity': 1
            }]
            try:
                result = pricing.calculate_price(hour=12, is_round_trip=False, selected_options=selected_options)
                print(f"  [One-way + 1 Option] Final: ${result['final_price']} | Options: ${result['options_total']} | Option Name: {result['options_breakdown'][0]['name'] if result['options_breakdown'] else '-'}")
            except Exception as e:
                print(f"  [One-way + 1 Option] ERROR: {e}")
        print("-")
    print("\n==== END OF TEST ====")

def main():
    test_transfer_products()

if __name__ == '__main__':
    main() 