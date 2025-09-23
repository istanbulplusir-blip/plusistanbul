#!/usr/bin/env python
"""
Fix variant_id issue in order items
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

def fix_variant_id_issue():
    """Fix the variant_id issue in order items"""
    print("🔧 Fixing Variant ID Issue")
    print("=" * 50)
    
    try:
        order = Order.objects.get(order_number='ORD2DCE3F8B')
        print(f"✅ Found order: {order.order_number}")
        
        # Find the correct variant ID
        schedule_id = 'dd87c0e3-9fc5-4f0d-a497-7bd2344b52dc'
        schedule = TourSchedule.objects.get(id=schedule_id)
        
        print(f"📅 Schedule: {schedule.start_date} - {schedule.tour.title}")
        print(f"🎯 Available variants:")
        
        for variant in schedule.tour.variants.all():
            print(f"   - {variant.id}: {variant.name} (capacity: {variant.capacity})")
        
        # Find the VIP variant
        vip_variant = schedule.tour.variants.filter(name__icontains='VIP').first()
        if vip_variant:
            print(f"✅ Found VIP variant: {vip_variant.id} - {vip_variant.name}")
            
            # Update the order item
            for item in order.items.all():
                if item.product_type == 'tour' and item.variant_id is None:
                    print(f"🔧 Updating order item variant_id from None to {vip_variant.id}")
                    item.variant_id = vip_variant.id
                    item.save()
                    
                    print(f"✅ Order item updated")
                    
                    # Now test capacity confirmation
                    print(f"\n🧪 Testing Capacity Confirmation:")
                    participants = item.booking_data.get('participants', {}) or {}
                    adult_count = int(participants.get('adult', 0))
                    child_count = int(participants.get('child', 0))
                    qty_for_capacity = adult_count + child_count
                    
                    print(f"   Schedule: {schedule_id}")
                    print(f"   Variant: {vip_variant.id}")
                    print(f"   Quantity: {qty_for_capacity}")
                    
                    if qty_for_capacity > 0:
                        success, error = TourCapacityService.confirm_capacity(
                            schedule_id, str(vip_variant.id), qty_for_capacity
                        )
                        print(f"   Result: {success}")
                        if not success:
                            print(f"   Error: {error}")
                        else:
                            print(f"   ✅ Capacity confirmed successfully")
                            
                            # Check updated capacities
                            schedule.refresh_from_db()
                            print(f"   Updated capacities: {schedule.variant_capacities}")
                            
                            # Update order status
                            order.is_capacity_reserved = True
                            order.capacity_reserved_at = timezone.now()
                            order.save()
                            print(f"   ✅ Order updated with capacity reservation")
        else:
            print(f"❌ VIP variant not found")
            
    except Order.DoesNotExist:
        print("❌ Order ORD2DCE3F8B not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_variant_id_issue()
