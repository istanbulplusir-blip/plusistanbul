#!/usr/bin/env python
"""
Script to update existing transfer pricing data with pricing_metadata.
This ensures all existing pricing records have proper metadata for the new pricing system.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoutePricing


def update_pricing_metadata():
    """Update all existing TransferRoutePricing records with pricing_metadata."""
    
    print("Updating transfer pricing metadata...")
    
    # Get all pricing records
    pricing_records = TransferRoutePricing.objects.all()
    updated_count = 0
    
    for pricing in pricing_records:
        # Check if pricing_metadata already exists and is valid
        if not pricing.pricing_metadata or 'pricing_type' not in pricing.pricing_metadata:
            # Set default pricing metadata for transfers
            pricing.pricing_metadata = {
                'pricing_type': 'transfer',
                'calculation_method': 'base_plus_surcharges',
                'includes_time_surcharges': True,
                'includes_round_trip_discount': True,
                'includes_options': True,
                'currency': 'USD',
                'price_components': [
                    'base_price',
                    'time_surcharge',
                    'options_total',
                    'round_trip_discount'
                ]
            }
            
            try:
                pricing.save()
                updated_count += 1
                print(f"✓ Updated pricing for {pricing.route} - {pricing.vehicle_type}")
            except Exception as e:
                print(f"✗ Error updating {pricing.route} - {pricing.vehicle_type}: {e}")
        else:
            print(f"- Skipping {pricing.route} - {pricing.vehicle_type} (already has metadata)")
    
    print(f"\nUpdate complete! Updated {updated_count} pricing records.")


def test_pricing_calculation():
    """Test the new pricing calculation system."""
    
    print("\nTesting pricing calculation...")
    
    # Get a sample pricing record
    try:
        pricing = TransferRoutePricing.objects.first()
        if not pricing:
            print("No pricing records found to test.")
            return
        
        print(f"Testing with: {pricing.route} - {pricing.vehicle_type}")
        
        # Test different scenarios
        test_cases = [
            {
                'name': 'Basic pricing (no surcharges)',
                'params': {'hour': 12, 'is_round_trip': False, 'selected_options': []}
            },
            {
                'name': 'Peak hour pricing',
                'params': {'hour': 8, 'is_round_trip': False, 'selected_options': []}
            },
            {
                'name': 'Round trip with discount',
                'params': {'hour': 14, 'is_round_trip': True, 'selected_options': []}
            },
            {
                'name': 'With options',
                'params': {
                    'hour': 10, 
                    'is_round_trip': False, 
                    'selected_options': [
                        {'option_id': '1', 'quantity': 1, 'price': 15.00},
                        {'option_id': '2', 'quantity': 2, 'price': 10.00}
                    ]
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                result = pricing.calculate_price(**test_case['params'])
                print(f"✓ {test_case['name']}:")
                print(f"  Base: ${result['base_price']}")
                print(f"  Surcharge: ${result['time_surcharge']}")
                print(f"  Options: ${result['options_total']}")
                print(f"  Discount: ${result['round_trip_discount']}")
                print(f"  Final: ${result['final_price']}")
                print()
            except Exception as e:
                print(f"✗ {test_case['name']}: Error - {e}")
        
    except Exception as e:
        print(f"Error during testing: {e}")


def main():
    """Main function."""
    print("Transfer Pricing Metadata Update Script")
    print("=" * 50)
    
    # Update metadata
    update_pricing_metadata()
    
    # Test calculation
    test_pricing_calculation()
    
    print("\nScript completed successfully!")


if __name__ == '__main__':
    main() 