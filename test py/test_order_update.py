#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import Order, OrderItem
from orders.services import OrderFieldMapper

def test_order_update():
    # پیدا کردن order
    order = Order.objects.filter(items__product_type='tour').first()
    if order:
        print(f'=== Order ID: {order.id} ===')
        print(f'Order Number: {order.order_number}')
        print(f'Current Subtotal: {order.subtotal}')
        print(f'Current Total: {order.total_amount}')
        print(f'Status: {order.status}')

        # نمایش آیتم‌ها
        print('\nOrder Items:')
        for item in order.items.all():
            print(f'  - {item.product_title}: ${item.total_price} (qty: {item.quantity})')

        # بروزرسانی order pricing
        print('\n=== Updating Order Pricing ===')
        old_subtotal = order.subtotal
        old_total = order.total_amount

        # بروزرسانی subtotal بر اساس آیتم‌ها
        new_subtotal = sum(item.total_price for item in order.items.all())
        order.subtotal = new_subtotal
        order.save()

        print(f'Old Subtotal: ${old_subtotal}')
        print(f'New Subtotal: ${order.subtotal}')
        print(f'Old Total: ${old_total}')
        print(f'New Total: ${order.total_amount}')
        print(f'Subtotal Change: ${float(order.subtotal) - float(old_subtotal)}')
        print(f'Total Change: ${float(order.total_amount) - float(old_total)}')

    else:
        print('No order with tour items found')

if __name__ == '__main__':
    test_order_update()
