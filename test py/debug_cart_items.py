#!/usr/bin/env python
"""
Debug script to show actual data stored in event cart items.
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from cart.models import CartItem
from events.models import Event

def debug_cart_items():
    """Show actual data stored in event cart items."""
    
    # Get all event cart items
    event_items = CartItem.objects.filter(product_type='event')
    
    print(f"Found {event_items.count()} event cart items")
    print("=" * 80)
    
    for item in event_items:
        try:
            event = Event.objects.get(id=item.product_id)
            
            print(f"Item ID: {item.id}")
            print(f"Event: {event.title}")
            print(f"Product Type: {item.product_type}")
            print(f"Variant ID: {item.variant_id}")
            print(f"Variant Name: {item.variant_name}")
            print(f"Booking Date: {item.booking_date}")
            print(f"Booking Time: {item.booking_time}")
            print(f"Quantity: {item.quantity}")
            print(f"Unit Price: {item.unit_price}")
            print(f"Total Price: {item.total_price}")
            print(f"Currency: {item.currency}")
            
            print(f"Booking Data: {json.dumps(item.booking_data, indent=2, default=str) if item.booking_data else 'None'}")
            print(f"Selected Options: {json.dumps(item.selected_options, indent=2, default=str) if item.selected_options else 'None'}")
            
            print("-" * 80)
            
        except Exception as e:
            print(f"Error processing item {item.id}: {str(e)}")
            print("-" * 80)

if __name__ == '__main__':
    debug_cart_items() 