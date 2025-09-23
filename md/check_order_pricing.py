#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import OrderItem
from tours.models import TourPricing, Tour, TourVariant

def check_order_pricing():
    # پیدا کردن order item
    order_items = OrderItem.objects.filter(product_type='tour').first()
    if order_items:
        print('OrderItem found:')
        print(f'ID: {order_items.id}')
        print(f'Product ID: {order_items.product_id}')
        print(f'Variant ID: {order_items.variant_id}')
        print(f'Booking data: {order_items.booking_data}')
        print(f'Current total_price: {order_items.total_price}')
        print(f'Options total: {order_items.options_total}')
        print(f'Quantity: {order_items.quantity}')
        print(f'Unit price: {order_items.unit_price}')

        # بررسی TourPricing
        try:
            tour = Tour.objects.get(id=order_items.product_id)
            variant = TourVariant.objects.get(id=order_items.variant_id, tour=tour)
            pricings = TourPricing.objects.filter(tour=tour, variant=variant)
            print(f'\nTourPricing found: {pricings.count()}')
            for pricing in pricings:
                print(f'  {pricing.age_group}: {pricing.final_price} (free: {pricing.is_free})')
        except Exception as e:
            print(f'Error checking TourPricing: {e}')

        # محاسبه مجدد total_price
        print('\n=== Recalculating total_price ===')
        order_items.save()  # این باعث فراخوانی متد save و محاسبه مجدد می‌شود
        print(f'New total_price: {order_items.total_price}')
        print(f'New quantity: {order_items.quantity}')

    else:
        print('No tour OrderItem found')

if __name__ == '__main__':
    check_order_pricing()
