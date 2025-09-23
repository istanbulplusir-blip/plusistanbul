#!/usr/bin/env python
"""
Test script to check event pricing calculation and cart functionality.
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, TicketType, EventSection, SectionTicketType
from events.pricing_service import EventPriceCalculator
from cart.services import EventCartService
from cart.models import Cart, CartItem
from users.models import User

def test_event_pricing():
    """Test event pricing calculation."""
    print("Testing event pricing calculation...")
    
    try:
        # Get the first available event
        event = Event.objects.filter(is_active=True).first()
        if not event:
            print("No active events found")
            return
        
        print(f"Testing with event: {event.title}")
        
        # Get the first performance
        performance = event.performances.first()
        if not performance:
            print("No performances found for this event")
            return
        
        print(f"Testing with performance: {performance.date}")
        
        # Get the first section
        section = performance.sections.first()
        if not section:
            print("No sections found for this performance")
            return
        
        print(f"Testing with section: {section.name}")
        
        # Get the first ticket type
        section_ticket = section.ticket_types.first()
        if not section_ticket:
            print("No ticket types found for this section")
            return
        
        print(f"Testing with ticket type: {section_ticket.ticket_type.name}")
        
        # Test pricing calculation
        calculator = EventPriceCalculator(event, performance)
        pricing_result = calculator.calculate_ticket_price(
            section_name=section.name,
            ticket_type_id=str(section_ticket.ticket_type.id),
            quantity=2,
            selected_options=[],
            discount_code=""
        )
        
        print("Pricing calculation successful!")
        print(f"Final price: ${pricing_result['final_price']}")
        print(f"Base price: ${pricing_result['base_price']}")
        print(f"Unit price: ${pricing_result['unit_price']}")
        
        return True
        
    except Exception as e:
        print(f"Error in pricing calculation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cart_functionality():
    """Test cart functionality."""
    print("\nTesting cart functionality...")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Get or create a cart
        from cart.models import CartService
        cart = CartService.get_or_create_cart(session_id='test-session', user=user)
        
        # Get test data
        event = Event.objects.filter(is_active=True).first()
        if not event:
            print("No active events found for cart test")
            return False
        
        performance = event.performances.first()
        if not performance:
            print("No performances found for cart test")
            return False
        
        section = performance.sections.first()
        if not section:
            print("No sections found for cart test")
            return False
        
        section_ticket = section.ticket_types.first()
        if not section_ticket:
            print("No ticket types found for cart test")
            return False
        
        # Test seat data
        test_seats = [
            {
                'seat_id': f'test-seat-1-{section.name}',
                'seat_number': '1',
                'row_number': 'A',
                'section': section.name,
                'price': 50.00
            },
            {
                'seat_id': f'test-seat-2-{section.name}',
                'seat_number': '2',
                'row_number': 'A',
                'section': section.name,
                'price': 50.00
            }
        ]
        
        # Test adding seats to cart
        cart_item, is_new = EventCartService.add_event_seats_to_cart(
            cart=cart,
            event_id=str(event.id),
            performance_id=str(performance.id),
            ticket_type_id=str(section_ticket.ticket_type.id),
            seats=test_seats,
            special_requests="Test special requests"
        )
        
        print("Cart functionality test successful!")
        print(f"Cart item created: {cart_item.id}")
        print(f"Is new item: {is_new}")
        print(f"Total price: ${cart_item.total_price}")
        
        # Clean up
        cart_item.delete()
        
        return True
        
    except Exception as e:
        print(f"Error in cart functionality: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Starting event pricing and cart tests...")
    
    pricing_success = test_event_pricing()
    cart_success = test_cart_functionality()
    
    if pricing_success and cart_success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 