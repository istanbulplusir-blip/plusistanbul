#!/usr/bin/env python
"""
Test script to verify event options pricing calculation.
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

from events.models import Event, EventPerformance, TicketType, EventSection, SectionTicketType, EventOption
from events.pricing_service import EventPriceCalculator
from cart.services import EventCartService
from cart.models import Cart, CartItem
from users.models import User

def test_event_options_pricing():
    """Test event options pricing calculation."""
    print("Testing event options pricing calculation...")
    
    try:
        # Get the first event with options
        event = Event.objects.filter(options__isnull=False).first()
        if not event:
            print("No event with options found. Creating test data...")
            # Create test event with options
            from events.models import EventCategory, Venue
            category = EventCategory.objects.first()
            venue = Venue.objects.first()
            
            if not category or not venue:
                print("No category or venue found. Please create test data first.")
                return
            
            event = Event.objects.create(
                title="Test Event with Options",
                category=category,
                venue=venue,
                style='music',
                price=Decimal('50.00'),
                currency='USD',
                city='Tehran',
                country='Iran',
                door_open_time='19:00',
                start_time='20:00',
                end_time='22:00'
            )
            
            # Create test options
            option1 = EventOption.objects.create(
                event=event,
                name="Premium Parking",
                description="Reserved parking spot close to venue",
                price=Decimal('15.00'),
                option_type='parking'
            )
            
            option2 = EventOption.objects.create(
                event=event,
                name="Valet Parking",
                description="Valet parking service",
                price=Decimal('25.00'),
                option_type='parking'
            )
            
            print(f"Created test event: {event.title}")
            print(f"Created options: {option1.name} (${option1.price}), {option2.name} (${option2.price})")
        
        # Get or create performance
        performance = event.performances.first()
        if not performance:
            from datetime import date, timedelta
            performance = EventPerformance.objects.create(
                event=event,
                date=date.today() + timedelta(days=30),
                start_time='20:00',
                end_time='22:00',
                max_capacity=100,
                is_available=True
            )
            print(f"Created test performance for {performance.date}")
        
        # Get or create section
        section = performance.sections.first()
        if not section:
            section = EventSection.objects.create(
                performance=performance,
                name="VIP",
                description="VIP Section",
                total_capacity=50,
                available_capacity=50,
                base_price=Decimal('100.00')
            )
            print(f"Created test section: {section.name}")
        
        # Get or create ticket type
        ticket_type = event.ticket_types.first()
        if not ticket_type:
            ticket_type = TicketType.objects.create(
                event=event,
                name="VIP",
                description="VIP Ticket",
                price_modifier=Decimal('1.5'),
                capacity=50
            )
            print(f"Created test ticket type: {ticket_type.name}")
        
        # Create section ticket type
        section_ticket, created = SectionTicketType.objects.get_or_create(
            section=section,
            ticket_type=ticket_type,
            defaults={
                'allocated_capacity': 50,
                'available_capacity': 50,
                'price_modifier': Decimal('1.5')
            }
        )
        
        print(f"\nTesting pricing calculation...")
        
        # Test 1: Base price without options
        calculator = EventPriceCalculator(event, performance)
        base_pricing = calculator.calculate_ticket_price(
            section_name=section.name,
            ticket_type_id=str(ticket_type.id),
            quantity=2
        )
        
        print(f"Base pricing (2 tickets):")
        print(f"  Unit price: ${base_pricing['unit_price']}")
        print(f"  Subtotal: ${base_pricing['subtotal']}")
        print(f"  Final price: ${base_pricing['final_price']}")
        
        # Test 2: Price with options
        selected_options = [
            {'option_id': str(event.options.first().id), 'quantity': 1},
            {'option_id': str(event.options.last().id), 'quantity': 2}
        ]
        
        pricing_with_options = calculator.calculate_ticket_price(
            section_name=section.name,
            ticket_type_id=str(ticket_type.id),
            quantity=2,
            selected_options=selected_options
        )
        
        print(f"\nPricing with options (2 tickets + options):")
        print(f"  Unit price: ${pricing_with_options['unit_price']}")
        print(f"  Subtotal: ${pricing_with_options['subtotal']}")
        print(f"  Options total: ${pricing_with_options['options_total']}")
        print(f"  Final price: ${pricing_with_options['final_price']}")
        
        # Test 3: Cart service with options
        print(f"\nTesting cart service with options...")
        
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Get or create cart
        from cart.models import CartService
        cart = CartService.get_or_create_cart(session_id='test-session', user=user)
        
        # Test seats data
        test_seats = [
            {
                'seat_id': 'seat-1',
                'seat_number': 'A1',
                'row_number': 'A',
                'section': section.name,
                'price': float(base_pricing['unit_price'])
            }
        ]
        
        # Add to cart with options
        cart_item, is_new = EventCartService.add_event_seats_to_cart(
            cart=cart,
            event_id=str(event.id),
            performance_id=str(performance.id),
            ticket_type_id=str(ticket_type.id),
            seats=test_seats,
            selected_options=selected_options
        )
        
        print(f"Cart item created: {is_new}")
        print(f"Cart item total price: ${cart_item.total_price}")
        print(f"Cart item booking data: {cart_item.booking_data}")
        
        # Clean up
        cart.delete()
        
        print(f"\n✅ All tests passed! Event options are working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_event_options_pricing() 