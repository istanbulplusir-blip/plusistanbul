#!/usr/bin/env python
"""
Test script to check pricing API with options.
"""

import os
import sys
import django
from datetime import datetime, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferOption, TransferRoutePricing
from transfers.services import TransferPricingService

def test_pricing_with_options():
    """Test pricing calculation with options."""
    try:
        # Get first available route
        route = TransferRoute.objects.filter(is_active=True).first()
        if not route:
            print("No active routes found")
            return
        
        # Get first pricing for this route
        pricing = TransferRoutePricing.objects.filter(route=route, is_active=True).first()
        if not pricing:
            print("No active pricing found for route")
            return
        
        # Get available options
        options = TransferOption.objects.filter(is_active=True)[:2]
        if not options:
            print("No active options found")
            return
        
        print(f"Testing pricing for route: {route.origin} → {route.destination}")
        print(f"Vehicle: {pricing.vehicle_type}")
        print(f"Base price: {pricing.base_price}")
        print(f"Available options: {[opt.name for opt in options]}")
        
        # Create selected options
        selected_options = [
            {'option_id': str(opt.id), 'quantity': 1}
            for opt in options
        ]
        
        # Test booking time
        booking_time = datetime.now().replace(hour=14, minute=30)
        
        # Calculate price
        result = TransferPricingService.calculate_price(
            route=route,
            pricing=pricing,
            booking_time=booking_time,
            selected_options=selected_options
        )
        
        print("\n=== PRICING RESULT ===")
        print(f"Base price: ${result['price_breakdown']['base_price']}")
        print(f"Options total: ${result['price_breakdown']['options_total']}")
        print(f"Final price: ${result['price_breakdown']['final_price']}")
        
        print("\n=== OPTIONS BREAKDOWN ===")
        for option in result['options_breakdown']:
            print(f"- {option['name']}: ${option['price']} x {option['quantity']} = ${option['total']}")
        
        return result
        
    except Exception as e:
        print(f"Error testing pricing: {e}")
        return None

if __name__ == '__main__':
    test_pricing_with_options() 