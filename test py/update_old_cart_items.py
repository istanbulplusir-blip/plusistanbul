#!/usr/bin/env python
"""
Script to update old cart items to use the new pricing system.
This ensures all existing cart items have correct pricing calculations.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from cart.models import CartItem
from transfers.models import TransferRoutePricing, TransferOption


def update_old_cart_items():
    """Update old cart items to use the new pricing system."""
    
    print("Updating old cart items...")
    
    # Get all transfer cart items
    transfer_items = CartItem.objects.filter(product_type='transfer')
    updated_count = 0
    
    for item in transfer_items:
        try:
            # Get the pricing object
            pricing = TransferRoutePricing.objects.get(id=item.variant_id)
            
            # Get booking data
            booking_data = item.booking_data or {}
            outbound_time = booking_data.get('outbound_time')
            trip_type = booking_data.get('trip_type', 'one_way')
            
            # Calculate new price using pricing_metadata
            if outbound_time:
                from datetime import datetime
                if isinstance(outbound_time, str):
                    try:
                        booking_time = datetime.strptime(outbound_time, '%H:%M').time()
                        hour = booking_time.hour
                    except ValueError:
                        hour = 12  # Default to noon if time parsing fails
                else:
                    hour = outbound_time.hour
            else:
                hour = 12  # Default to noon
            
            is_round_trip = trip_type == 'round_trip'
            
            # Calculate price using new system
            price_result = pricing.calculate_price(
                hour=hour,
                is_round_trip=is_round_trip,
                selected_options=item.selected_options
            )
            
            # Update item with new pricing
            item.unit_price = price_result['final_price']
            item.total_price = price_result['final_price']
            item.options_total = price_result['options_total']
            item.save()
            
            updated_count += 1
            print(f"✓ Updated cart item {item.id}: ${item.total_price}")
            
        except TransferRoutePricing.DoesNotExist:
            print(f"✗ Cart item {item.id}: Pricing not found")
        except Exception as e:
            print(f"✗ Cart item {item.id}: Error - {e}")
    
    print(f"\nUpdate complete! Updated {updated_count} cart items.")


def validate_cart_items():
    """Validate that all cart items have correct pricing."""
    
    print("\nValidating cart items...")
    
    transfer_items = CartItem.objects.filter(product_type='transfer')
    valid_count = 0
    
    for item in transfer_items:
        try:
            # Check if total_price = unit_price + options_total
            expected_total = item.unit_price + item.options_total
            if abs(item.total_price - expected_total) < 0.01:
                valid_count += 1
                print(f"✓ Cart item {item.id}: Pricing is correct")
            else:
                print(f"✗ Cart item {item.id}: Pricing mismatch")
                print(f"  Expected: ${expected_total}, Got: ${item.total_price}")
                
        except Exception as e:
            print(f"✗ Cart item {item.id}: Error - {e}")
    
    print(f"\nValidation complete! {valid_count}/{transfer_items.count()} items are valid.")


def main():
    """Main function."""
    print("Cart Items Update Script")
    print("=" * 50)
    
    # Update old cart items
    update_old_cart_items()
    
    # Validate cart items
    validate_cart_items()
    
    print("\nScript completed successfully!")


if __name__ == '__main__':
    main() 