#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, EventSection, SectionTicketType, TicketType
from events.pricing_service import EventPriceCalculator

def debug_pricing():
    try:
        # Get the event that's failing
        event_id = "0f54db9b-0b4d-4a16-8c68-0c38fd6f7c34"
        event = Event.objects.get(id=event_id)
        print(f"Event found: {event.title}")
        
        # Get performances
        performances = event.performances.all()
        print(f"Performances: {list(performances.values_list('id', 'date'))}")
        
        if performances.exists():
            performance = performances.first()
            print(f"Using performance: {performance.id} on {performance.date}")
            
            # Get sections
            sections = performance.sections.all()
            print(f"Sections: {list(sections.values_list('id', 'name'))}")
            
            if sections.exists():
                section = sections.first()
                print(f"Using section: {section.name}")
                
                # Get ticket types for this section
                section_ticket_types = section.ticket_types.all()
                print(f"Section ticket types: {list(section_ticket_types.values_list('id', 'ticket_type__id', 'ticket_type__name'))}")
                
                if section_ticket_types.exists():
                    section_ticket_type = section_ticket_types.first()
                    ticket_type_id = section_ticket_type.ticket_type.id
                    print(f"Using ticket type: {ticket_type_id} ({section_ticket_type.ticket_type.name})")
                    
                    # Test the pricing calculator
                    print("\n=== Testing Pricing Calculator ===")
                    calculator = EventPriceCalculator(event, performance)
                    
                    try:
                        result = calculator.calculate_ticket_price(
                            section_name=section.name,
                            ticket_type_id=str(ticket_type_id),
                            quantity=1,
                            selected_options=[],
                            discount_code=''
                        )
                        print("Pricing calculation successful!")
                        print(f"Result: {result}")
                    except Exception as e:
                        print(f"Pricing calculation failed: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("No ticket types found for this section")
            else:
                print("No sections found for this performance")
        else:
            print("No performances found for this event")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pricing()
