#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import OrderItem
from tours.models import TourPricing, Tour, TourVariant

def check_order_pricing():
    # پیدا کردن order item با participants
    order_items = OrderItem.objects.filter(
        product_type='tour',
        booking_data__participants__isnull=False
    ).exclude(booking_data__participants={})

    if order_items.exists():
        for item in order_items[:3]:  # فقط ۳ تای اول
            print(f'\n=== OrderItem ID: {item.id} ===')
            print(f'Product ID: {item.product_id}')
            print(f'Variant ID: {item.variant_id}')
            print(f'Booking data: {item.booking_data}')
            print(f'Current total_price: {item.total_price}')
            print(f'Options total: {item.options_total}')
            print(f'Quantity: {item.quantity}')
            print(f'Unit price: {item.unit_price}')

            participants = item.booking_data.get('participants', {})
            print(f'Participants: Adult={participants.get("adult", 0)}, Child={participants.get("child", 0)}, Infant={participants.get("infant", 0)}')

            # محاسبه دستی
            adult_count = int(participants.get('adult', 0))
            child_count = int(participants.get('child', 0))
            infant_count = int(participants.get('infant', 0))

            expected_total = (150 * adult_count) + (105 * child_count) + (0 * infant_count) + float(item.options_total)
            print(f'Expected total (manual calc): ${expected_total}')

            # بررسی TourPricing
            try:
                tour = Tour.objects.get(id=item.product_id)
                variant = TourVariant.objects.get(id=item.variant_id, tour=tour)
                pricings = TourPricing.objects.filter(tour=tour, variant=variant)
                print(f'TourPricing found: {pricings.count()}')
                for pricing in pricings:
                    print(f'  {pricing.age_group}: {pricing.final_price} (free: {pricing.is_free})')
            except Exception as e:
                print(f'Error checking TourPricing: {e}')

            # محاسبه مجدد total_price
            print('=== Recalculating total_price ===')
            old_total = item.total_price
            item.save()  # این باعث فراخوانی متد save و محاسبه مجدد می‌شود
            print(f'Old total_price: {old_total}')
            print(f'New total_price: {item.total_price}')
            print(f'New quantity: {item.quantity}')
            print(f'Change: {float(item.total_price) - float(old_total)}')

    else:
        print('No tour OrderItem with participants found')

if __name__ == '__main__':
    check_order_pricing()