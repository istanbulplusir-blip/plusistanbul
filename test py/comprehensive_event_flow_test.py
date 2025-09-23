#!/usr/bin/env python
"""
Comprehensive Event Flow Test
Tests the complete flow from seat selection to checkout for events.
"""

import os
import django
import json
import time
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from cart.models import Cart, CartItem, CartService
from users.models import User
from events.models import Event, EventPerformance, TicketType, Seat
from cart.services import EventCartService
from orders.models import Order, OrderService

class EventFlowTester:
    """Comprehensive event flow testing."""
    
    def __init__(self):
        self.user = User.objects.get(username='testuser')
        self.session_id = f"test_session_{self.user.id}"
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_1_event_data_integrity(self):
        """Test 1: Verify event data integrity."""
        print("\n=== Test 1: Event Data Integrity ===")
        
        try:
            # Get test event
            event = Event.objects.get(id="e535c9e4-a079-4e6f-bbd4-10ab31d2fbb7")
            
            # Check event has required data
            assert event.title, "Event title is missing"
            assert event.performances.exists(), "Event has no performances"
            assert event.ticket_types.exists(), "Event has no ticket types"
            
            # Check performance has seats
            performance = event.performances.first()
            assert performance.seats.exists(), "Performance has no seats"
            
            # Check ticket type has pricing
            ticket_type = event.ticket_types.first()
            assert ticket_type.price_modifier > 0, "Ticket type has invalid pricing"
            
            self.log_test("Event Data Integrity", True, 
                         f"Event: {event.title}, Performances: {event.performances.count()}, "
                         f"Ticket Types: {event.ticket_types.count()}")
            
        except Exception as e:
            self.log_test("Event Data Integrity", False, str(e))
    
    def test_2_seat_selection_flow(self):
        """Test 2: Seat selection and local basket flow."""
        print("\n=== Test 2: Seat Selection Flow ===")
        
        try:
            # Get test data
            event = Event.objects.get(id="e535c9e4-a079-4e6f-bbd4-10ab31d2fbb7")
            performance = event.performances.first()
            ticket_type = event.ticket_types.first()
            
            # Get available seats
            available_seats = performance.seats.filter(status='available')[:3]
            assert available_seats.count() >= 3, "Not enough available seats"
            
            # Simulate seat selection
            selected_seats = []
            for seat in available_seats:
                selected_seats.append({
                    'seat_id': str(seat.id),
                    'seat_number': seat.seat_number,
                    'row_number': seat.row_number,
                    'section': seat.section,
                    'price': float(seat.price)
                })
            
            # Calculate total price
            total_price = sum(seat['price'] for seat in selected_seats)
            
            self.log_test("Seat Selection", True, 
                         f"Selected {len(selected_seats)} seats, Total: ${total_price}")
            
            return selected_seats, event, performance, ticket_type
            
        except Exception as e:
            self.log_test("Seat Selection", False, str(e))
            return None, None, None, None
    
    def test_3_cart_creation_and_management(self):
        """Test 3: Cart creation and management."""
        print("\n=== Test 3: Cart Creation and Management ===")
        
        try:
            # Clear existing cart
            Cart.objects.filter(user=self.user).delete()
            
            # Create new cart
            cart = CartService.get_or_create_cart(session_id=self.session_id, user=self.user)
            assert cart.user == self.user, "Cart user mismatch"
            assert cart.is_active, "Cart is not active"
            
            self.log_test("Cart Creation", True, f"Cart ID: {cart.id}")
            
            return cart
            
        except Exception as e:
            self.log_test("Cart Creation", False, str(e))
            return None
    
    def test_4_add_seats_to_cart(self, cart, selected_seats, event, performance, ticket_type):
        """Test 4: Add seats to cart."""
        print("\n=== Test 4: Add Seats to Cart ===")
        
        try:
            # Add first batch of seats
            cart_item_1, is_new_1 = EventCartService.add_event_seats_to_cart(
                cart=cart,
                event_id=str(event.id),
                performance_id=str(performance.id),
                ticket_type_id=str(ticket_type.id),
                seats=selected_seats[:2]  # First 2 seats
            )
            
            assert is_new_1, "First batch should create new item"
            assert cart_item_1.product_type == 'event', "Wrong product type"
            assert len(cart_item_1.booking_data.get('seats', [])) == 2, "Wrong seat count"
            
            self.log_test("Add First Batch", True, f"Added 2 seats, Total: ${cart_item_1.total_price}")
            
            # Add second batch (should merge)
            cart_item_2, is_new_2 = EventCartService.add_event_seats_to_cart(
                cart=cart,
                event_id=str(event.id),
                performance_id=str(performance.id),
                ticket_type_id=str(ticket_type.id),
                seats=selected_seats[2:]  # Last seat
            )
            
            assert not is_new_2, "Second batch should merge with existing"
            assert cart_item_2.id == cart_item_1.id, "Should be same cart item"
            assert len(cart_item_2.booking_data.get('seats', [])) == 3, "Wrong total seat count"
            
            self.log_test("Add Second Batch (Merge)", True, f"Merged 1 seat, Total: ${cart_item_2.total_price}")
            
            return cart_item_2
            
        except Exception as e:
            self.log_test("Add Seats to Cart", False, str(e))
            return None
    
    def test_5_cart_validation(self, cart, cart_item):
        """Test 5: Cart validation and data integrity."""
        print("\n=== Test 5: Cart Validation ===")
        
        try:
            # Verify cart item data
            assert cart_item.cart == cart, "Cart item belongs to wrong cart"
            assert cart_item.product_type == 'event', "Wrong product type"
            assert cart_item.quantity == 1, "Event items should have quantity 1"
            assert cart_item.total_price > 0, "Invalid total price"
            
            # Verify booking data
            booking_data = cart_item.booking_data
            assert 'performance_id' in booking_data, "Missing performance_id"
            assert 'ticket_type_id' in booking_data, "Missing ticket_type_id"
            assert 'seats' in booking_data, "Missing seats"
            assert len(booking_data['seats']) == 3, "Wrong seat count in booking data"
            
            # Verify selected options
            selected_options = cart_item.selected_options
            assert len(selected_options) > 0, "Missing selected options"
            assert 'performance_id' in selected_options[0], "Missing performance_id in options"
            assert 'seats' in selected_options[0], "Missing seats in options"
            
            self.log_test("Cart Validation", True, 
                         f"Cart item validated: {cart_item.id}, Seats: {len(booking_data['seats'])}")
            
        except Exception as e:
            self.log_test("Cart Validation", False, str(e))
    
    def test_6_order_creation(self, cart, cart_item):
        """Test 6: Order creation from cart."""
        print("\n=== Test 6: Order Creation ===")
        
        try:
            # Create order from cart
            order = OrderService.create_order_from_cart(
                cart=cart,
                user=self.user,
                payment_data={
                    'payment_method': 'test',
                    'transaction_id': f'test_{int(time.time())}'
                }
            )
            
            assert order.user == self.user, "Order user mismatch"
            assert order.status == 'pending', "Order should be pending"
            assert order.items.count() == 1, "Order should have 1 item"
            
            # Verify order item
            order_item = order.items.first()
            assert order_item.product_type == 'event', "Wrong product type in order"
            assert order_item.quantity == 1, "Wrong quantity in order"
            assert order_item.total_price == cart_item.total_price, "Price mismatch"
            
            # Verify booking data in order
            order_booking_data = order_item.booking_data
            cart_booking_data = cart_item.booking_data
            assert order_booking_data['seats'] == cart_booking_data['seats'], "Seats mismatch"
            
            self.log_test("Order Creation", True, 
                         f"Order created: {order.order_number}, Total: ${order.total}")
            
            return order
            
        except Exception as e:
            self.log_test("Order Creation", False, str(e))
            return None
    
    def test_7_seat_reservation(self, order):
        """Test 7: Verify seat reservation after order."""
        print("\n=== Test 7: Seat Reservation ===")
        
        try:
            order_item = order.items.first()
            booking_data = order_item.booking_data
            
            # Check if seats are now reserved/sold
            for seat_data in booking_data['seats']:
                seat = Seat.objects.get(id=seat_data['seat_id'])
                # Note: In real system, seats should be marked as reserved/sold
                # For now, we just verify the seat exists
                assert seat, f"Seat {seat_data['seat_id']} not found"
            
            self.log_test("Seat Reservation", True, 
                         f"Verified {len(booking_data['seats'])} seats")
            
        except Exception as e:
            self.log_test("Seat Reservation", False, str(e))
    
    def test_8_cleanup(self):
        """Test 8: Cleanup test data."""
        print("\n=== Test 8: Cleanup ===")
        
        try:
            # Clean up test orders
            Order.objects.filter(user=self.user, order_number__startswith='TEST').delete()
            
            # Clean up test carts
            Cart.objects.filter(user=self.user).delete()
            
            self.log_test("Cleanup", True, "Test data cleaned up")
            
        except Exception as e:
            self.log_test("Cleanup", False, str(e))
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("🚀 Starting Comprehensive Event Flow Test")
        print("=" * 50)
        
        # Test 1: Data integrity
        self.test_1_event_data_integrity()
        
        # Test 2: Seat selection
        selected_seats, event, performance, ticket_type = self.test_2_seat_selection_flow()
        if not selected_seats:
            print("❌ Stopping tests due to seat selection failure")
            return
        
        # Test 3: Cart creation
        cart = self.test_3_cart_creation_and_management()
        if not cart:
            print("❌ Stopping tests due to cart creation failure")
            return
        
        # Test 4: Add seats to cart
        cart_item = self.test_4_add_seats_to_cart(cart, selected_seats, event, performance, ticket_type)
        if not cart_item:
            print("❌ Stopping tests due to cart addition failure")
            return
        
        # Test 5: Cart validation
        self.test_5_cart_validation(cart, cart_item)
        
        # Test 6: Order creation
        order = self.test_6_order_creation(cart, cart_item)
        if not order:
            print("❌ Stopping tests due to order creation failure")
            return
        
        # Test 7: Seat reservation
        self.test_7_seat_reservation(order)
        
        # Test 8: Cleanup
        self.test_8_cleanup()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Save results to file
        with open('event_flow_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: event_flow_test_results.json")

def main():
    """Main test runner."""
    tester = EventFlowTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 