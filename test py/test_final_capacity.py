#!/usr/bin/env python
"""
Final test to verify capacity management is working
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

def test_final_capacity():
    """Test final capacity management"""
    print("🧪 Final Capacity Management Test")
    print("=" * 50)
    
    try:
        # Find the order
        order = Order.objects.get(order_number='ORD2DCE3F8B')
        print(f"✅ Found order: {order.order_number}")
        print(f"   Status: {order.status}")
        print(f"   Payment Status: {order.payment_status}")
        print(f"   Is Capacity Reserved: {order.is_capacity_reserved}")
        
        # Check order items
        print(f"\n📦 Order Items:")
        for item in order.items.all():
            print(f"   - {item.product_title}")
            print(f"     Product Type: {item.product_type}")
            print(f"     Variant ID: {item.variant_id}")
            print(f"     Quantity: {item.quantity}")
            
            if item.product_type == 'tour':
                schedule_id = item.booking_data.get('schedule_id')
                variant_id = str(item.variant_id) if item.variant_id else None
                
                print(f"     Schedule ID: {schedule_id}")
                print(f"     Variant ID: {variant_id}")
                
                if schedule_id and variant_id:
                    try:
                        schedule = TourSchedule.objects.get(id=schedule_id)
                        print(f"     Schedule: {schedule.start_date} - {schedule.tour.title}")
                        
                        # Check variant capacities
                        print(f"     Variant Capacities: {schedule.variant_capacities}")
                        
                        if variant_id in schedule.variant_capacities:
                            variant_capacity = schedule.variant_capacities[variant_id]
                            print(f"     Variant Capacity: {variant_capacity}")
                            
                            if variant_capacity['booked'] > 0:
                                print(f"     ✅ Capacity is properly booked: {variant_capacity['booked']}")
                            else:
                                print(f"     ❌ Capacity not booked: {variant_capacity['booked']}")
                        else:
                            print(f"     ❌ Variant {variant_id} not found in capacities")
                            
                    except TourSchedule.DoesNotExist:
                        print(f"     ❌ Schedule {schedule_id} not found")
        
        # Test creating a new order to see if capacity management works
        print(f"\n🧪 Testing New Order Creation:")
        
        # Find a tour with available capacity
        from tours.models import Tour
        tour = Tour.objects.filter(is_active=True).first()
        if tour:
            print(f"   Testing with tour: {tour.title}")
            
            # Find a schedule with available capacity
            schedule = tour.schedules.filter(is_available=True).first()
            if schedule:
                print(f"   Testing with schedule: {schedule.start_date}")
                
                # Find a variant with available capacity
                for variant in tour.variants.all():
                    variant_capacity = schedule.variant_capacities.get(str(variant.id))
                    if variant_capacity and variant_capacity['available'] > 0:
                        print(f"   Testing with variant: {variant.name} (available: {variant_capacity['available']})")
                        
                        # Test capacity confirmation
                        participants = {'adult': 2, 'child': 1, 'infant': 0}
                        qty_for_capacity = participants['adult'] + participants['child']
                        
                        print(f"   Testing capacity confirmation for {qty_for_capacity} participants...")
                        
                        success, error = TourCapacityService.confirm_capacity(
                            str(schedule.id), str(variant.id), qty_for_capacity
                        )
                        
                        if success:
                            print(f"   ✅ Capacity confirmation successful")
                            
                            # Check updated capacities
                            schedule.refresh_from_db()
                            updated_capacity = schedule.variant_capacities.get(str(variant.id))
                            print(f"   Updated capacity: {updated_capacity}")
                            
                            if updated_capacity['booked'] > 0:
                                print(f"   ✅ Capacity properly updated: {updated_capacity['booked']} booked")
                            else:
                                print(f"   ❌ Capacity not updated: {updated_capacity['booked']} booked")
                        else:
                            print(f"   ❌ Capacity confirmation failed: {error}")
                        
                        break
                else:
                    print(f"   ❌ No variants with available capacity found")
            else:
                print(f"   ❌ No available schedules found")
        else:
            print(f"   ❌ No active tours found")
        
        print(f"\n✅ Test completed successfully!")
        
    except Order.DoesNotExist:
        print("❌ Order ORD2DCE3F8B not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_capacity()
