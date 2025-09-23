#!/usr/bin/env python
"""
Script to update existing event cart items with missing booking_data and selected_options.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from cart.models import CartItem
from events.models import Event, EventPerformance, TicketType

def update_event_cart_items():
    """Update existing event cart items with proper booking_data structure."""
    
    # Get all event cart items
    event_items = CartItem.objects.filter(product_type='event')
    
    print(f"Found {event_items.count()} event cart items to update")
    
    updated_count = 0
    
    for item in event_items:
        try:
            # Skip if already has proper booking_data
            if item.booking_data and isinstance(item.booking_data, dict) and item.booking_data.get('seats'):
                print(f"Item {item.id} already has proper booking_data, skipping...")
                continue
            
            # Get event details
            event = Event.objects.get(id=item.product_id)
            
            # Create basic booking_data structure
            booking_data = {
                'performance_id': None,  # We don't have this for old items
                'ticket_type_id': item.variant_id,
                'performance_date': item.booking_date.isoformat() if item.booking_date else None,
                'performance_time': item.booking_time.isoformat() if item.booking_time else None,
                'venue_name': event.venue.name if event.venue else None,
                'venue_address': event.venue.address if event.venue else None,
                'seats': [],  # We don't have seat data for old items
                'section': '',
                'selected_options': [],
                'special_requests': ''
            }
            
            # Create basic selected_options structure
            selected_options = [{
                'performance_id': None,
                'seats': [],
                'section': '',
                'options': []
            }]
            
            # Update the item
            item.booking_data = booking_data
            item.selected_options = selected_options
            item.save()
            
            updated_count += 1
            print(f"Updated item {item.id} for event: {event.title}")
            
        except Exception as e:
            print(f"Error updating item {item.id}: {str(e)}")
            continue
    
    print(f"\nUpdated {updated_count} event cart items")
    print("Note: Old items may not have complete seat information as it was not stored previously.")

if __name__ == '__main__':
    update_event_cart_items() 