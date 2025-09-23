#!/usr/bin/env python
"""
Test script to verify event list pricing is working correctly.
"""

import os
import sys
import django
import json

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, EventSection, SectionTicketType, TicketType
from events.serializers import EventListSerializer

def test_event_list_pricing():
    """Test event list pricing serialization."""
    print("Testing event list pricing serialization...")
    
    try:
        # Get the first event
        event = Event.objects.first()
        if not event:
            print("No events found in database.")
            return
        
        print(f"Testing event: {event.title}")
        
        # Serialize the event using EventListSerializer
        serializer = EventListSerializer(event)
        data = serializer.data
        
        print(f"\nSerialized data keys: {list(data.keys())}")
        
        # Check if pricing_summary exists
        if 'pricing_summary' in data:
            pricing_summary = data['pricing_summary']
            print(f"\nPricing summary: {json.dumps(pricing_summary, indent=2)}")
            
            if pricing_summary:
                # Get minimum price from pricing_summary
                min_price = min(item['base_price'] for item in pricing_summary.values())
                print(f"Minimum price from pricing_summary: ${min_price}")
            else:
                print("Pricing summary is empty")
        else:
            print("pricing_summary field not found in serialized data")
        
        # Check min_price field
        if 'min_price' in data:
            print(f"min_price field: ${data['min_price']}")
        else:
            print("min_price field not found")
        
        # Check performance_calendar
        if 'performance_calendar' in data:
            calendar = data['performance_calendar']
            print(f"\nPerformance calendar: {len(calendar)} performances")
            if calendar:
                print(f"First performance date: {calendar[0]['date']}")
        else:
            print("performance_calendar field not found")
        
        print(f"\n✅ Event list pricing test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_event_list_pricing() 