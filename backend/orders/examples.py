"""
Examples of how to use OrderFieldMapper and OrderItemFieldMapper services.
"""

from .services import OrderFieldMapper, OrderItemFieldMapper


def example_create_order_from_cart():
    """
    Example: Create order from cart with proper field mapping.
    """
    # This is how OrderService.create_order_from_cart now works
    cart = None  # Cart object
    user = None  # User object
    payment_data = {}  # Optional payment data
    
    # Map all order fields properly
    order_data = OrderFieldMapper.map_order_fields_from_cart(cart, user, payment_data)
    
    # The order_data will contain:
    # - customer_name: from user.get_full_name() or user.username
    # - customer_email: from user.email
    # - customer_phone: from user.phone_number or ''
    # - billing_address: from payment_data['customer_info']['address'] or user.profile.address
    # - billing_city: from payment_data['customer_info']['city'] or user.profile.city
    # - billing_country: from payment_data['customer_info']['country'] or user.profile.country
    # - customer_notes: from payment_data['customer_info']['notes']
    # - payment_method: from payment_data['payment_method'] or 'whatsapp'
    # - subtotal: from cart.subtotal
    # - total_amount: from cart.total
    # - currency: from cart.currency
    # - status: 'pending'
    # - admin_notes: '' (empty for new orders)
    # - payment_reference: '' (empty for new orders)
    # - internal_notes: '' (empty for new orders)
    
    print("Order data:", order_data)


def example_create_order_from_request():
    """
    Example: Create order from request data with proper field mapping.
    """
    request_data = {
        'customer_info': {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'address': '123 Main St',
            'city': 'New York',
            'country': 'USA',
            'notes': 'Please deliver to front door'
        },
        'payment_method': 'whatsapp',
        'total_amount': 150.00,
        'currency': 'USD',
        'items': [
            {
                'product_type': 'tour',
                'product_id': 'tour-uuid-here',
                'product_title': 'City Tour',
                'product_slug': 'city-tour',
                'quantity': 2,
                'unit_price': 75.00,
                'total_price': 150.00,
                'booking_data': {
                    'date': '2025-09-15',
                    'participants': {'adult': 2, 'child': 0, 'infant': 0}
                }
            }
        ]
    }
    user = None  # User object
    
    # Map all order fields properly
    order_data = OrderFieldMapper.map_order_fields_from_request(request_data, user)
    
    # The order_data will contain:
    # - customer_name: 'John Doe' (from request)
    # - customer_email: 'john@example.com' (from request)
    # - customer_phone: '+1234567890' (from request)
    # - billing_address: '123 Main St' (from request)
    # - billing_city: 'New York' (from request)
    # - billing_country: 'USA' (from request)
    # - customer_notes: 'Please deliver to front door' (from request)
    # - payment_method: 'whatsapp' (from request)
    # - subtotal: 150.00 (from request)
    # - total_amount: 150.00 (from request)
    # - currency: 'USD' (from request)
    # - status: 'pending'
    
    print("Order data:", order_data)


def example_field_sources():
    """
    Example: Show where each field gets its value from.
    """
    print("Field Sources:")
    print("==============")
    print("Customer Information:")
    print("- customer_name: user.get_full_name() or user.username")
    print("- customer_email: user.email")
    print("- customer_phone: user.phone_number or ''")
    print()
    print("Billing Information:")
    print("- billing_address: request['customer_info']['address'] or user.profile.address")
    print("- billing_city: request['customer_info']['city'] or user.profile.city")
    print("- billing_country: request['customer_info']['country'] or user.profile.country")
    print()
    print("Notes:")
    print("- customer_notes: request['customer_info']['notes']")
    print("- internal_notes: '' (empty for new orders)")
    print("- admin_notes: '' (empty for new orders)")
    print()
    print("Payment Information:")
    print("- payment_method: request['payment_method'] or 'whatsapp'")
    print("- payment_reference: '' (set when payment is processed)")
    print("- payment_date: None (set when payment is confirmed)")
    print()
    print("Pricing Information:")
    print("- subtotal: cart.subtotal or request['total_amount']")
    print("- total_amount: cart.total or request['total_amount']")
    print("- currency: cart.currency or request['currency']")
    print("- tax_amount: 0.00 (calculated if needed)")
    print("- discount_amount: 0.00 (calculated if needed)")
    print()
    print("Agent Information:")
    print("- agent: request['agent_id'] or None")
    print("- agent_commission_rate: agent.commission_rate or 0.00")
    print("- agent_commission_amount: 0.00 (calculated)")
    print("- commission_paid: False")
    print()
    print("Capacity Information:")
    print("- is_capacity_reserved: False")
    print("- capacity_reserved_at: None")
    print()
    print("Status:")
    print("- status: 'pending' (for new orders)")


if __name__ == "__main__":
    example_field_sources()
