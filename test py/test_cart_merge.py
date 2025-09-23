#!/usr/bin/env python
"""
Test script for cart merge functionality
"""
import os
import sys
import django
from datetime import date

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
from cart.models import Cart, CartItem
from tours.models import Tour, TourSchedule, TourVariant
from users.models import User

def test_cart_merge():
    """Test cart merge functionality"""

    print("🧪 Testing Cart Merge Functionality")
    print("="*50)

    try:
        # Create test user
        user, created = User.objects.get_or_create(
            username='test_merge',
            defaults={
                'email': 'test_merge@example.com',
                'first_name': 'Test',
                'last_name': 'Merge'
            }
        )
        print(f"✅ Test user: {user.username}")

        # Create unique test session
        import uuid
        unique_session_key = f'test_session_merge_{uuid.uuid4().hex[:8]}'

        session = Session.objects.create(
            session_key=unique_session_key,
            session_data='{}',
            expire_date=datetime.now() + timedelta(hours=24)
        )

        # Create guest cart
        guest_cart = Cart.objects.create(
            session_id=unique_session_key,
            expires_at=datetime.now() + timedelta(hours=24)
        )
        print(f"✅ Guest cart created: {guest_cart.id}")

        # Find test tour
        tours = Tour.objects.filter(is_active=True)
        if not tours.exists():
            print("❌ No tours found")
            return

        tour = tours.first()
        schedule = tour.schedules.first()
        variant = tour.variants.first()

        if not schedule or not variant:
            print("❌ Tour missing schedule or variant")
            return

        # Create cart item in guest cart
        cart_item = CartItem.objects.create(
            cart=guest_cart,
            product_type='tour',
            product_id=str(tour.id),
            variant_id=str(variant.id),
            quantity=2,
            unit_price=100.00,
            total_price=200.00,
            currency='USD',
            booking_date=schedule.start_date,
            booking_time=schedule.start_time,
            booking_data={
                'schedule_id': str(schedule.id),
                'participants': {
                    'adult': 1,
                    'child': 1,
                    'infant': 0
                }
            }
        )
        print(f"✅ Guest cart item created: {cart_item.id}")

        # Test merge
        from cart.models import CartService
        result = CartService.migrate_session_cart_to_user(unique_session_key, user)

        if result:
            print(f"✅ Cart merged successfully: {result.id}")
            print(f"   Items in merged cart: {result.items.count()}")

            # Verify items
            items = result.items.all()
            for item in items:
                print(f"   Item: {item.product_type} - {item.quantity} qty")

            # Check that guest cart is gone
            guest_cart_exists = Cart.objects.filter(
                session_id='test_session_merge_123',
                user__isnull=True
            ).exists()

            if not guest_cart_exists:
                print("✅ Guest cart removed after merge")
            else:
                print("❌ Guest cart still exists")

        else:
            print("❌ Cart merge failed")

        # Cleanup
        try:
            Cart.objects.filter(session_id='test_session_merge_123').delete()
            Session.objects.filter(session_key='test_session_merge_123').delete()
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_cart_merge()
