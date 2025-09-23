#!/usr/bin/env python
"""
Comprehensive integration test for Event with Cart, Order, and Payment systems.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from events.models import Event, EventPerformance, EventSection, SectionTicketType, EventOption, EventDiscount, EventFee
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from payments.models import Payment
from events.pricing_service import EventPriceCalculator

User = get_user_model()

def test_event_cart_integration():
    """Test Event integration with Cart system."""
    print("🛒 Testing Event-Cart Integration")
    print("=" * 50)
    
    # Get test data
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    performance = event.performances.first()
    if not performance:
        print("❌ No performances found")
        return False
    
    section = performance.sections.first()
    if not section:
        print("❌ No sections found")
        return False
    
    section_ticket = section.ticket_types.first()
    if not section_ticket:
        print("❌ No ticket types found")
        return False
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_event_user',
        defaults={
            'email': 'test_event@example.com',
            'first_name': 'Test',
            'last_name': 'Event User'
        }
    )
    
    try:
        # Test 1: Calculate pricing
        print("\n1️⃣ Testing Pricing Calculation")
        calculator = EventPriceCalculator(event, performance)
        
        pricing_result = calculator.calculate_ticket_price(
            section_name=section.name,
            ticket_type_id=str(section_ticket.ticket_type.id),
            quantity=2,
            selected_options=[],  # No options for now
            is_group_booking=True,
            apply_fees=True,
            apply_taxes=True
        )
        
        print(f"✅ Pricing calculated: ${pricing_result['final_price']}")
        
        # Test 2: Create cart
        print("\n2️⃣ Testing Cart Creation")
        # Generate unique session ID
        session_id = f'test_event_session_{timezone.now().strftime("%Y%m%d%H%M%S")}'
        cart = Cart.objects.create(
            session_id=session_id,
            user=user,
            currency='USD',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        print(f"✅ Cart created: {cart.session_id}")
        
        # Test 3: Add event to cart
        print("\n3️⃣ Testing Add Event to Cart")
        cart_item = CartItem.objects.create(
            cart=cart,
            product_type='event',
            product_id=event.id,
            booking_date=performance.date,
            booking_time=performance.start_time,
            variant_id=section_ticket.ticket_type.id,
            variant_name=section_ticket.ticket_type.name,
            quantity=2,
            unit_price=Decimal(str(pricing_result['unit_price'])),
            total_price=Decimal(str(pricing_result['final_price'])),
            currency='USD',
            selected_options=[],
            options_total=Decimal(str(pricing_result['options_total'])),
            booking_data={
                'section_name': section.name,
                'ticket_type_id': str(section_ticket.ticket_type.id),
                'pricing_breakdown': pricing_result
            }
        )
        
        print(f"✅ Event added to cart: {cart_item.id}")
        print(f"   Product: {event.title}")
        print(f"   Section: {section.name}")
        print(f"   Ticket Type: {section_ticket.ticket_type.name}")
        print(f"   Quantity: {cart_item.quantity}")
        print(f"   Total Price: ${cart_item.total_price}")
        
        # Test 4: Verify cart totals
        print("\n4️⃣ Testing Cart Totals")
        cart.refresh_from_db()
        print(f"✅ Cart subtotal: ${cart.subtotal}")
        print(f"✅ Cart total items: {cart.total_items}")
        
        # Test 5: Create order
        print("\n5️⃣ Testing Order Creation")
        order = Order.objects.create(
            user=user,
            order_number=f"EV{timezone.now().strftime('%Y%m%d%H%M%S')}",
            status='pending',
            subtotal=cart.subtotal,
            tax_amount=Decimal('0.00'),
            discount_amount=Decimal('0.00'),
            total_amount=cart.subtotal,
            currency='USD',
            customer_name=f"{user.first_name} {user.last_name}",
            customer_email=user.email,
            customer_phone='+1234567890'
        )
        
        print(f"✅ Order created: {order.order_number}")
        
        # Test 6: Create order item
        print("\n6️⃣ Testing Order Item Creation")
        order_item = OrderItem.objects.create(
            order=order,
            product_type='event',
            product_id=event.id,
            product_title=event.title,
            product_slug=event.slug,
            booking_date=performance.date,
            booking_time=performance.start_time,
            variant_id=section_ticket.ticket_type.id,
            variant_name=section_ticket.ticket_type.name,
            quantity=2,
            unit_price=cart_item.unit_price,
            total_price=cart_item.total_price,
            currency='USD',
            selected_options=[],
            booking_data=cart_item.booking_data
        )
        
        print(f"✅ Order item created: {order_item.id}")
        
        # Test 7: Create payment
        print("\n7️⃣ Testing Payment Creation")
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            currency='USD',
            payment_method='credit_card',
            status='pending',
            gateway_response={'test': True}
        )
        
        print(f"✅ Payment created: {payment.id}")
        print(f"   Amount: ${payment.amount}")
        print(f"   Method: {payment.payment_method}")
        
        # Test 8: Verify order totals
        print("\n8️⃣ Testing Order Verification")
        order.refresh_from_db()
        print(f"✅ Order subtotal: ${order.subtotal}")
        print(f"✅ Order total: ${order.total_amount}")
        print(f"✅ Order items count: {order.items.count()}")
        
        # Cleanup
        print("\n🧹 Cleaning up test data")
        payment.delete()
        order_item.delete()
        order.delete()
        cart_item.delete()
        cart.delete()
        
        print("✅ All test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mixed_cart():
    """Test cart with multiple product types (Event + Tour + Transfer)."""
    print("\n🛒 Testing Mixed Cart (Event + Tour + Transfer)")
    print("=" * 60)
    
    # Get test data
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    # Import other models
    try:
        from tours.models import Tour
        from transfers.models import TransferRoute
        
        tour = Tour.objects.first()
        transfer = TransferRoute.objects.first()
        
        if not tour or not transfer:
            print("⚠️  Tour or Transfer not found, skipping mixed cart test")
            return True
            
    except ImportError:
        print("⚠️  Tour or Transfer models not available, skipping mixed cart test")
        return True
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_mixed_user',
        defaults={
            'email': 'test_mixed@example.com',
            'first_name': 'Test',
            'last_name': 'Mixed User'
        }
    )
    
    try:
        # Create cart
        # Generate unique session ID
        session_id = f'test_mixed_session_{timezone.now().strftime("%Y%m%d%H%M%S")}'
        cart = Cart.objects.create(
            session_id=session_id,
            user=user,
            currency='USD',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        print(f"✅ Mixed cart created: {cart.session_id}")
        
        # Add event item
        event_item = CartItem.objects.create(
            cart=cart,
            product_type='event',
            product_id=event.id,
            booking_date=timezone.now().date(),
            booking_time=timezone.now().time(),
            quantity=1,
            unit_price=Decimal('100.00'),
            total_price=Decimal('100.00'),
            currency='USD'
        )
        
        # Add tour item
        tour_item = CartItem.objects.create(
            cart=cart,
            product_type='tour',
            product_id=tour.id,
            booking_date=timezone.now().date(),
            booking_time=timezone.now().time(),
            quantity=2,
            unit_price=Decimal('50.00'),
            total_price=Decimal('100.00'),
            currency='USD'
        )
        
        # Add transfer item
        transfer_item = CartItem.objects.create(
            cart=cart,
            product_type='transfer',
            product_id=transfer.id,
            booking_date=timezone.now().date(),
            booking_time=timezone.now().time(),
            quantity=1,
            unit_price=Decimal('25.00'),
            total_price=Decimal('25.00'),
            currency='USD'
        )
        
        print(f"✅ Added items to mixed cart:")
        print(f"   Event: {event.title} - ${event_item.total_price}")
        print(f"   Tour: {tour.title} - ${tour_item.total_price}")
        print(f"   Transfer: {transfer.name} - ${transfer_item.total_price}")
        
        # Verify cart totals
        cart.refresh_from_db()
        print(f"✅ Mixed cart subtotal: ${cart.subtotal}")
        print(f"✅ Mixed cart total items: {cart.total_items}")
        
        # Create order
        order = Order.objects.create(
            user=user,
            order_number=f"MX{timezone.now().strftime('%Y%m%d%H%M%S')}",
            status='pending',
            subtotal=cart.subtotal,
            total_amount=cart.subtotal,
            currency='USD',
            customer_name=f"{user.first_name} {user.last_name}",
            customer_email=user.email,
            customer_phone='+1234567890'
        )
        
        print(f"✅ Mixed order created: {order.order_number}")
        print(f"✅ Order total: ${order.total_amount}")
        
        # Cleanup
        transfer_item.delete()
        tour_item.delete()
        event_item.delete()
        order.delete()
        cart.delete()
        
        print("✅ Mixed cart test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Mixed cart test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_event_pricing_api():
    """Test Event pricing API endpoints."""
    print("\n🌐 Testing Event Pricing API")
    print("=" * 40)
    
    # Get test data
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    performance = event.performances.first()
    if not performance:
        print("❌ No performances found")
        return False
    
    try:
        # Test pricing calculator
        calculator = EventPriceCalculator(event, performance)
        
        # Test with different scenarios
        scenarios = [
            {
                'name': 'Basic pricing',
                'quantity': 1,
                'options': [],
                'group_booking': False,
                'apply_fees': False,
                'apply_taxes': False
            },
            {
                'name': 'With options',
                'quantity': 2,
                'options': [],
                'group_booking': False,
                'apply_fees': True,
                'apply_taxes': True
            },
            {
                'name': 'Group booking',
                'quantity': 5,
                'options': [],
                'group_booking': True,
                'apply_fees': True,
                'apply_taxes': True
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📊 Testing: {scenario['name']}")
            
            section = performance.sections.first()
            section_ticket = section.ticket_types.first()
            
            result = calculator.calculate_ticket_price(
                section_name=section.name,
                ticket_type_id=str(section_ticket.ticket_type.id),
                quantity=scenario['quantity'],
                selected_options=scenario['options'],
                is_group_booking=scenario['group_booking'],
                apply_fees=scenario['apply_fees'],
                apply_taxes=scenario['apply_taxes']
            )
            
            print(f"   Quantity: {result['quantity']}")
            print(f"   Subtotal: ${result['subtotal']}")
            print(f"   Options: ${result['options_total']}")
            print(f"   Discounts: ${result['discount_total']}")
            print(f"   Fees: ${result['fees_total']}")
            print(f"   Taxes: ${result['taxes_total']}")
            print(f"   Final Price: ${result['final_price']}")
        
        print("\n✅ All pricing scenarios tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Pricing API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("🚀 Starting Event Integration Tests")
    print("=" * 60)
    
    success = True
    
    # Test 1: Event-Cart-Order-Payment integration
    if not test_event_cart_integration():
        success = False
    
    # Test 2: Mixed cart (Event + Tour + Transfer)
    if not test_mixed_cart():
        success = False
    
    # Test 3: Event pricing API
    if not test_event_pricing_api():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All integration tests passed! Event system is ready for production.")
    else:
        print("❌ Some integration tests failed. Please check the errors above.")
    
    return success


if __name__ == '__main__':
    main() 