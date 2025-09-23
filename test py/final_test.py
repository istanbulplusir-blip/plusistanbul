#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import Order, OrderItem
from tours.models import TourPricing, Tour, TourVariant

def final_test():
    print("=== FINAL TEST: Order Pricing Consistency ===\n")

    # پیدا کردن همه OrderItemهای tour
    order_items = OrderItem.objects.filter(product_type='tour').order_by('-created_at')[:5]

    for item in order_items:
        print(f"OrderItem: {item.id}")
        print(f"Product: {item.product_title}")
        print(f"Participants: {item.booking_data.get('participants', {})}")

        # محاسبه قیمت صحیح
        participants = item.booking_data.get('participants', {})
        adult_count = int(participants.get('adult', 0))
        child_count = int(participants.get('child', 0))
        infant_count = int(participants.get('infant', 0))

        # گرفتن قیمت‌ها از TourPricing
        try:
            tour = Tour.objects.get(id=item.product_id)
            variant = TourVariant.objects.get(id=item.variant_id, tour=tour)

            adult_pricing = TourPricing.objects.get(tour=tour, variant=variant, age_group='adult')
            child_pricing = TourPricing.objects.get(tour=tour, variant=variant, age_group='child')
            infant_pricing = TourPricing.objects.get(tour=tour, variant=variant, age_group='infant')

            expected_total = (adult_pricing.final_price * adult_count +
                            child_pricing.final_price * child_count +
                            infant_pricing.final_price * infant_count +
                            item.options_total)

            print(f"Expected: Adult({adult_count})×${adult_pricing.final_price} + Child({child_count})×${child_pricing.final_price} + Infant({infant_count})×${infant_pricing.final_price} + Options(${item.options_total}) = ${expected_total}")
            print(f"Current: ${item.total_price}")
            print(f"Match: {'✅' if abs(float(item.total_price) - float(expected_total)) < 0.01 else '❌'}")
        except Exception as e:
            print(f"Error calculating expected: {e}")

        print("-" * 50)

    # تست Orderها
    print("\n=== Order Summary Test ===")
    orders = Order.objects.filter(items__product_type='tour').order_by('-created_at')[:3]

    for order in orders:
        print(f"\nOrder: {order.order_number}")
        items_subtotal = sum(item.total_price for item in order.items.all())
        print(f"Items Subtotal: ${items_subtotal}")
        print(f"Order Subtotal: ${order.subtotal}")
        print(f"Order Total: ${order.total_amount}")
        print(f"Subtotal Match: {'✅' if abs(float(items_subtotal) - float(order.subtotal)) < 0.01 else '❌'}")

if __name__ == '__main__':
    final_test()
