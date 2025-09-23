#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import Order, OrderItem

def update_old_orders():
    print("=== Updating Old Order Items ===\n")

    # بروزرسانی همه OrderItemهای قدیمی
    updated_count = 0
    for item in OrderItem.objects.filter(product_type='tour'):
        old_total = item.total_price
        item.save()  # این باعث recalculate می‌شود
        if item.total_price != old_total:
            print(f"Updated {item.id}: ${old_total} → ${item.total_price}")
            updated_count += 1

    print(f"\n✅ Updated {updated_count} OrderItems")

    # بروزرسانی Order subtotalها
    updated_orders = 0
    for order in Order.objects.all():
        old_subtotal = order.subtotal
        new_subtotal = sum(item.total_price for item in order.items.all())
        if new_subtotal != old_subtotal:
            order.subtotal = new_subtotal
            order.save()
            print(f"Updated Order {order.order_number}: ${old_subtotal} → ${order.subtotal}")
            updated_orders += 1

    print(f"\n✅ Updated {updated_orders} Orders")
    print("\n🎉 All pricing has been corrected!")

if __name__ == '__main__':
    update_old_orders()
