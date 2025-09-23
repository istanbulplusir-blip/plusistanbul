#!/usr/bin/env python
import os
import sys
import django
import json

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing

def test_transfer_cart():
    """Test transfer cart functionality."""
    print("=== Testing Transfer Cart Integration ===\n")

    # Get a sample transfer route
    route = TransferRoute.objects.filter(pricing__isnull=False).first()
    if not route:
        print("❌ No transfer route with pricing found")
        return

    print(f"📍 Route: {route.origin} → {route.destination}")
    print(f"📋 Slug: {route.slug}")

    # Get pricing options
    pricing_options = route.pricing.all()
    print(f"💰 Available pricing options: {pricing_options.count()}")

    for i, pricing in enumerate(pricing_options):
        print(f"  {i+1}. {pricing.vehicle_type.upper()}: ${pricing.base_price} (max {pricing.max_passengers} passengers)")

    # Test capacity service
    from transfers.services import TransferCapacityService

    if pricing_options.exists():
        sample_pricing = pricing_options.first()
        capacity = TransferCapacityService.get_available_capacity(
            route_id=route.id,
            vehicle_type=sample_pricing.vehicle_type
        )
        print(f"📊 Available capacity for {sample_pricing.vehicle_type}: {capacity}")

        # Test capacity check
        is_available, error = TransferCapacityService.check_capacity_availability(
            route_id=route.id,
            vehicle_type=sample_pricing.vehicle_type,
            passenger_count=2
        )
        print(f"✅ Capacity check (2 passengers): {'Available' if is_available else 'Not Available'}")
        if error:
            print(f"❌ Error: {error}")

    # Simulate cart data structure
    print("
🛒 Simulated Cart Data Structure:")
    cart_data = {
        'product_type': 'transfer',
        'product_id': str(route.id),
        'variant_id': sample_pricing.vehicle_type if pricing_options.exists() else 'sedan',
        'quantity': 1,
        'booking_data': {
            'passenger_count': 2,
            'booking_date': '2025-09-15',
            'booking_time': '10:00:00'
        },
        'selected_options': []
    }

    print(json.dumps(cart_data, indent=2))

    # Test cart capacity check
    from cart.views import AddToCartView
    view = AddToCartView()
    capacity_available, capacity_error = view.check_capacity_availability(cart_data)

    print(f"\n🔍 Cart Capacity Check:")
    print(f"   Available: {capacity_available}")
    if capacity_error:
        print(f"   Error: {capacity_error}")

    print("
✅ Transfer cart integration test completed!")

if __name__ == '__main__':
    test_transfer_cart()
