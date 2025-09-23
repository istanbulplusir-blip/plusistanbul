#!/usr/bin/env python
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from cart.models import Cart, CartItem
from users.models import User
from cart.services import EventCartService

def test_event_cart_logic():
    """Test the new event cart logic."""
    
    # Get test user
    user = User.objects.get(username='testuser')
    print(f"Testing with user: {user.username}")
    
    # Get or create cart
    from cart.models import CartService
    session_id = f"test_session_{user.id}"
    cart = CartService.get_or_create_cart(session_id=session_id, user=user)
    print(f"Using cart: {cart.id}")
    
    # Test data
    event_id = "e535c9e4-a079-4e6f-bbd4-10ab31d2fbb7"  # Spring Festival
    performance_id = "1de92f6c-4467-478a-85a9-247c0fc62837"
    ticket_type_id = "7fdd2b27-481d-46ce-9d14-325d8428d73d"  # Normal
    
    # First batch of seats
    seats_1 = [
        {
            "seat_id": "test_seat_1",
            "seat_number": "01",
            "row_number": "1",
            "section": "A",
            "price": 100
        },
        {
            "seat_id": "test_seat_2", 
            "seat_number": "02",
            "row_number": "1",
            "section": "A",
            "price": 100
        }
    ]
    
    print("\n=== Test 1: Adding first batch of seats ===")
    cart_item_1, is_new_1 = EventCartService.add_event_seats_to_cart(
        cart=cart,
        event_id=event_id,
        performance_id=performance_id,
        ticket_type_id=ticket_type_id,
        seats=seats_1
    )
    print(f"New item: {is_new_1}")
    print(f"Total seats: {len(cart_item_1.booking_data.get('seats', []))}")
    print(f"Total price: {cart_item_1.total_price}")
    
    # Second batch of seats (should merge)
    seats_2 = [
        {
            "seat_id": "test_seat_3",
            "seat_number": "03", 
            "row_number": "1",
            "section": "A",
            "price": 100
        }
    ]
    
    print("\n=== Test 2: Adding second batch of seats (should merge) ===")
    cart_item_2, is_new_2 = EventCartService.add_event_seats_to_cart(
        cart=cart,
        event_id=event_id,
        performance_id=performance_id,
        ticket_type_id=ticket_type_id,
        seats=seats_2
    )
    print(f"New item: {is_new_2}")
    print(f"Total seats: {len(cart_item_2.booking_data.get('seats', []))}")
    print(f"Total price: {cart_item_2.total_price}")
    
    # Third batch with duplicate seat (should not add)
    seats_3 = [
        {
            "seat_id": "test_seat_1",  # Duplicate
            "seat_number": "01",
            "row_number": "1", 
            "section": "A",
            "price": 100
        }
    ]
    
    print("\n=== Test 3: Adding duplicate seat (should not add) ===")
    cart_item_3, is_new_3 = EventCartService.add_event_seats_to_cart(
        cart=cart,
        event_id=event_id,
        performance_id=performance_id,
        ticket_type_id=ticket_type_id,
        seats=seats_3
    )
    print(f"New item: {is_new_3}")
    print(f"Total seats: {len(cart_item_3.booking_data.get('seats', []))}")
    print(f"Total price: {cart_item_3.total_price}")
    
    # Check final state
    print("\n=== Final Cart State ===")
    all_items = cart.items.all()
    print(f"Total cart items: {all_items.count()}")
    for item in all_items:
        print(f"Item {item.id}: {item.product_type} - {item.total_price}")
        if item.product_type == 'event':
            seats = item.booking_data.get('seats', [])
            print(f"  Seats: {len(seats)}")
            for seat in seats:
                print(f"    {seat.get('seat_number')} (Row {seat.get('row_number')})")

if __name__ == "__main__":
    test_event_cart_logic() 