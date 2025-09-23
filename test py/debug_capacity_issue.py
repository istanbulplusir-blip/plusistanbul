#!/usr/bin/env python
"""
Debug script to investigate capacity management issue
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import Order
from tours.models import TourSchedule, TourVariant
from tours.services import TourCapacityService
from django.utils import timezone

def debug_capacity_issue():
    """Debug the capacity management issue"""
    print("🔍 Debugging Capacity Management Issue")
    print("=" * 50)
    
    # Find the order
    try:
        order = Order.objects.get(order_number='ORD2DCE3F8B')
        print(f"✅ Found order: {order.order_number}")
        print(f"   Status: {order.status}")
        print(f"   Payment Status: {order.payment_status}")
        print(f"   Created: {order.created_at}")
        print(f"   Is Capacity Reserved: {order.is_capacity_reserved}")
        print(f"   Capacity Reserved At: {order.capacity_reserved_at}")
        
        # Check order items
        print(f"\n📦 Order Items ({order.items.count()}):")
        for item in order.items.all():
            print(f"   - {item.product_title}")
            print(f"     Product Type: {item.product_type}")
            print(f"     Variant ID: {item.variant_id}")
            print(f"     Quantity: {item.quantity}")
            print(f"     Booking Data: {item.booking_data}")
            
            if item.product_type == 'tour':
                schedule_id = item.booking_data.get('schedule_id')
                variant_id = str(item.variant_id) if item.variant_id else None
                
                print(f"     Schedule ID: {schedule_id}")
                print(f"     Variant ID: {variant_id}")
                
                if schedule_id:
                    try:
                        schedule = TourSchedule.objects.get(id=schedule_id)
                        print(f"     Schedule: {schedule.start_date} - {schedule.start_time}")
                        print(f"     Tour: {schedule.tour.title}")
                        
                        # Check variant capacities
                        print(f"     Variant Capacities: {schedule.variant_capacities}")
                        
                        if variant_id:
                            variant_capacity = schedule.variant_capacities.get(variant_id)
                            if variant_capacity:
                                print(f"     Variant Capacity: {variant_capacity}")
                            else:
                                print(f"     ❌ Variant {variant_id} not found in capacities")
                                
                                # Check if variant exists
                                try:
                                    variant = TourVariant.objects.get(id=variant_id)
                                    print(f"     Variant exists: {variant.name} (capacity: {variant.capacity})")
                                except TourVariant.DoesNotExist:
                                    print(f"     ❌ Variant {variant_id} does not exist")
                        
                    except TourSchedule.DoesNotExist:
                        print(f"     ❌ Schedule {schedule_id} not found")
        
        # Test capacity confirmation manually
        print(f"\n🧪 Testing Manual Capacity Confirmation:")
        for item in order.items.all():
            if item.product_type == 'tour':
                schedule_id = item.booking_data.get('schedule_id')
                variant_id = str(item.variant_id) if item.variant_id else None
                
                if schedule_id and variant_id:
                    participants = item.booking_data.get('participants', {}) or {}
                    adult_count = int(participants.get('adult', 0))
                    child_count = int(participants.get('child', 0))
                    qty_for_capacity = adult_count + child_count
                    
                    print(f"   Testing capacity confirmation:")
                    print(f"     Schedule: {schedule_id}")
                    print(f"     Variant: {variant_id}")
                    print(f"     Quantity: {qty_for_capacity}")
                    
                    if qty_for_capacity > 0:
                        success, error = TourCapacityService.confirm_capacity(
                            schedule_id, variant_id, qty_for_capacity
                        )
                        print(f"     Result: {success}")
                        if not success:
                            print(f"     Error: {error}")
                        else:
                            print(f"     ✅ Capacity confirmed successfully")
                            
                            # Check updated capacities
                            schedule = TourSchedule.objects.get(id=schedule_id)
                            print(f"     Updated capacities: {schedule.variant_capacities}")
                    else:
                        print(f"     ⚠️ No capacity to confirm (quantity: {qty_for_capacity})")
        
        # Test order status change
        print(f"\n🔄 Testing Order Status Change:")
        print(f"   Current status: {order.status}")
        
        if order.status == 'pending':
            print(f"   Attempting to mark as paid...")
            success, message = order.mark_as_paid()
            print(f"   Result: {success}")
            print(f"   Message: {message}")
            
            if success:
                order.refresh_from_db()
                print(f"   New status: {order.status}")
                print(f"   Is Capacity Reserved: {order.is_capacity_reserved}")
                print(f"   Capacity Reserved At: {order.capacity_reserved_at}")
        
    except Order.DoesNotExist:
        print("❌ Order ORD2DCE3F8B not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_capacity_issue()
