"""
Order field mapping services for proper data population.
"""

from django.utils import timezone
from decimal import Decimal
from users.models import User


class OrderFieldMapper:
    """
    Service to map order fields from various sources (user, product, request data).
    """
    
    @staticmethod
    def get_customer_info_from_user(user):
        """Extract customer information from user object."""
        return {
            'user': user,
            'customer_name': user.get_full_name() or user.username,
            'customer_email': user.email,
            'customer_phone': user.phone_number or '',
        }
    
    @staticmethod
    def get_billing_info_from_request(request_data, user=None):
        """Extract billing information from request data or user profile."""
        customer_info = request_data.get('customer_info', {})
        
        # For services, we only need city and country (no address/postal_code)
        billing_info = {
            'billing_address': '',  # Removed - not needed for services
            'billing_city': customer_info.get('city', ''),
            'billing_country': customer_info.get('country', ''),
        }
        
        # If user has profile with billing info, use as fallback
        if user:
            try:
                profile = user.profile
                # billing_address removed - not needed for services
                if not billing_info['billing_city'] and profile.city:
                    billing_info['billing_city'] = profile.city
                if not billing_info['billing_country'] and profile.country:
                    billing_info['billing_country'] = profile.country
            except User.profile.RelatedObjectDoesNotExist:
                # Create profile if it doesn't exist
                from users.services import UserDataService
                profile = UserDataService.get_or_create_user_profile(user)
                # billing_address removed - not needed for services
                if not billing_info['billing_city'] and profile.city:
                    billing_info['billing_city'] = profile.city
                if not billing_info['billing_country'] and profile.country:
                    billing_info['billing_country'] = profile.country
        
        return billing_info
    
    @staticmethod
    def get_notes_from_request(request_data):
        """Extract notes from request data."""
        customer_info = request_data.get('customer_info', {})
        
        return {
            'customer_notes': customer_info.get('special_requests', ''),
            'internal_notes': '',  # Always empty for new orders
            'admin_notes': '',     # Always empty for new orders
        }
    
    @staticmethod
    def get_payment_info_from_request(request_data, payment_method='whatsapp'):
        """Extract payment information from request data."""
        return {
            'payment_method': request_data.get('payment_method', payment_method),
            'payment_reference': '',  # Will be set when payment is processed
            'payment_date': None,     # Will be set when payment is confirmed
        }
    
    @staticmethod
    def get_pricing_info_from_cart(cart):
        """Extract pricing information from cart with calculated tax and fees."""
        from cart.models import CartService

        # Calculate totals with fees and taxes applied
        cart_totals = CartService.calculate_totals(cart, apply_fees=True, apply_taxes=True)

        # Convert float values to Decimal for precision
        return {
            'subtotal': Decimal(str(cart_totals['subtotal'])),
            'service_fee_amount': Decimal(str(cart_totals['fees_total'])),
            'total_amount': Decimal(str(cart_totals['grand_total'])),
            'currency': cart.currency,
            'tax_amount': Decimal(str(cart_totals['tax_total'])),
            'discount_amount': Decimal(str(cart_totals['discounts_total'])),
            'agent_commission_amount': Decimal('0.00'),  # Will be set if agent exists
        }
    
    @staticmethod
    def get_pricing_info_from_request(request_data):
        """Extract pricing information from request data."""
        # Get the individual pricing components from request
        subtotal = Decimal(str(request_data.get('subtotal', 0)))
        tax_amount = Decimal(str(request_data.get('tax_amount', 0)))
        discount_amount = Decimal(str(request_data.get('discount_amount', 0)))
        service_fee_amount = Decimal(str(request_data.get('service_fee_amount', 0)))

        # Calculate total_amount from components if not provided
        total_amount = Decimal(str(request_data.get('total_amount', 0)))
        if total_amount == 0 and subtotal > 0:
            total_amount = subtotal + service_fee_amount + tax_amount - discount_amount

        return {
            'subtotal': subtotal,
            'service_fee_amount': service_fee_amount,
            'total_amount': total_amount,
            'currency': request_data.get('currency', 'USD'),
            'tax_amount': tax_amount,
            'discount_amount': discount_amount,
            'agent_commission_amount': Decimal('0.00'),  # Will be set if agent exists
        }
    
    @staticmethod
    def get_agent_info_from_request(request_data, user=None):
        """Extract agent information from request data or user."""
        agent_id = request_data.get('agent_id')
        agent = None
        
        if agent_id:
            try:
                from users.models import User
                agent = User.objects.get(id=agent_id, is_agent=True)
            except User.DoesNotExist:
                agent = None
        
        return {
            'agent': agent,
            'agent_commission_rate': agent.commission_rate if agent else Decimal('0.00'),
            'agent_commission_amount': Decimal('0.00'),  # Will be calculated
            'commission_paid': False,
        }
    
    @staticmethod
    def get_capacity_info():
        """Get default capacity reservation info."""
        return {
            'is_capacity_reserved': False,
            'capacity_reserved_at': None,
        }
    
    @classmethod
    def map_order_fields_from_cart(cls, cart, user, request_data=None):
        """Map all order fields from cart and user data."""
        if request_data is None:
            request_data = {}

        # Combine all field mappings
        order_data = {}

        # Customer info from user
        order_data.update(cls.get_customer_info_from_user(user))

        # Billing info from request or user profile
        order_data.update(cls.get_billing_info_from_request(request_data, user))

        # Notes from request
        order_data.update(cls.get_notes_from_request(request_data))

        # Payment info
        order_data.update(cls.get_payment_info_from_request(request_data))

        # Agent info (before pricing to set commission)
        agent_info = cls.get_agent_info_from_request(request_data, user)
        order_data.update(agent_info)

        # Pricing info from cart (after agent info to include commission)
        pricing_info = cls.get_pricing_info_from_cart(cart)

        # Calculate agent commission if agent exists
        if agent_info.get('agent'):
            agent = agent_info['agent']
            commission_rate = getattr(agent, 'commission_rate', Decimal('0.00'))
            subtotal = pricing_info['subtotal']
            pricing_info['agent_commission_amount'] = (subtotal * commission_rate / 100).quantize(Decimal('0.01'))

        order_data.update(pricing_info)

        # Capacity info
        order_data.update(cls.get_capacity_info())

        # Status
        order_data['status'] = 'pending'

        return order_data
    
    @classmethod
    def map_order_fields_from_request(cls, request_data, user):
        """Map all order fields from request data and user."""
        # Combine all field mappings
        order_data = {}
        
        # Customer info from user
        order_data.update(cls.get_customer_info_from_user(user))
        
        # Billing info from request or user profile
        order_data.update(cls.get_billing_info_from_request(request_data, user))
        
        # Notes from request
        order_data.update(cls.get_notes_from_request(request_data))
        
        # Payment info
        order_data.update(cls.get_payment_info_from_request(request_data))
        
        # Pricing info from request
        order_data.update(cls.get_pricing_info_from_request(request_data))
        
        # Agent info
        order_data.update(cls.get_agent_info_from_request(request_data, user))
        
        # Capacity info
        order_data.update(cls.get_capacity_info())
        
        # Status
        order_data['status'] = 'pending'
        
        return order_data


class OrderItemFieldMapper:
    """
    Service to map order item fields from cart items or request data.
    """
    
    @staticmethod
    def get_product_details_from_cart_item(cart_item):
        """Extract product details from cart item."""
        try:
            if cart_item.product_type == 'tour':
                from tours.models import Tour
                tour = Tour.objects.get(id=cart_item.product_id)
                return {
                    'product_title': tour.title,
                    'product_slug': tour.slug,
                }
            elif cart_item.product_type == 'event':
                from events.models import Event
                event = Event.objects.get(id=cart_item.product_id)
                return {
                    'product_title': event.title,
                    'product_slug': event.slug,
                }
            elif cart_item.product_type == 'transfer':
                from transfers.models import TransferRoute
                route = TransferRoute.objects.get(id=cart_item.product_id)
                return {
                    'product_title': route.name or f"{route.origin} → {route.destination}",
                    'product_slug': route.slug,
                }
            elif cart_item.product_type == 'car_rental':
                from car_rentals.models import CarRental
                car_rental = CarRental.objects.get(id=cart_item.product_id)
                return {
                    'product_title': f"{car_rental.brand} {car_rental.model} ({car_rental.year})",
                    'product_slug': car_rental.slug,
                }
        except Exception as e:
            print(f"Error getting product details: {e}")
            return {
                'product_title': 'Unknown Product',
                'product_slug': 'unknown',
            }
    
    @staticmethod
    def get_product_details_from_request(item_data):
        """Extract product details from request item data."""
        return {
            'product_title': item_data.get('product_title') or 'Unknown Product',
            'product_slug': item_data.get('product_slug') or 'unknown',
        }
    
    @classmethod
    def map_order_item_fields_from_cart_item(cls, cart_item, order):
        """Map all order item fields from cart item."""
        product_details = cls.get_product_details_from_cart_item(cart_item)
        
        # Ensure variant_name is set if variant_id exists but variant_name is empty
        variant_name = cart_item.variant_name
        if cart_item.variant_id and not variant_name:
            variant_name = cls._get_variant_name_from_id(cart_item.variant_id, cart_item.product_id)

        return {
            'order': order,
            'product_type': cart_item.product_type,
            'product_id': cart_item.product_id,
            'product_title': product_details['product_title'],
            'product_slug': product_details['product_slug'],
            'booking_date': cart_item.booking_date,
            'booking_time': cart_item.booking_time,
            'variant_id': cart_item.variant_id,
            'variant_name': variant_name,
            'quantity': cart_item.quantity,
            'unit_price': cart_item.unit_price,
            'total_price': cart_item.total_price,
            'currency': cart_item.currency,
            'selected_options': cart_item.selected_options,
            'options_total': cart_item.options_total,
            'booking_data': cart_item.booking_data,
            'status': 'pending',
            # Car rental specific fields
            'pickup_date': cart_item.pickup_date,
            'dropoff_date': cart_item.dropoff_date,
            'pickup_time': cart_item.pickup_time,
            'dropoff_time': cart_item.dropoff_time,
            'pickup_location_type': cart_item.pickup_location_type or 'predefined',
            'pickup_location_id': cart_item.pickup_location_id,
            'pickup_location_custom': cart_item.pickup_location_custom or '',
            'pickup_location_coordinates': cart_item.pickup_location_coordinates or {},
            'dropoff_location_type': cart_item.dropoff_location_type or 'same_as_pickup',
            'dropoff_location_id': cart_item.dropoff_location_id,
            'dropoff_location_custom': cart_item.dropoff_location_custom or '',
            'dropoff_location_coordinates': cart_item.dropoff_location_coordinates or {},
        }

    @staticmethod
    def _get_variant_name_from_id(variant_id, product_id):
        """Get variant name from variant_id and product_id."""
        if not variant_id:
            return ''

        try:
            from tours.models import TourVariant
            variant = TourVariant.objects.get(id=variant_id, tour_id=product_id)
            return variant.name
        except TourVariant.DoesNotExist:
            return ''

    @classmethod
    def map_order_item_fields_from_request(cls, item_data, order):
        """Map all order item fields from request item data."""
        product_details = cls.get_product_details_from_request(item_data)
        
        # Extract booking data
        booking_data = item_data.get('booking_data') or {}
        
        # Set default booking date/time
        from datetime import date, time
        booking_date = date.today()
        booking_time = time(9, 0)
        
        # Try to extract date from booking_data
        if booking_data and 'date' in booking_data:
            try:
                from datetime import datetime
                booking_date = datetime.strptime(booking_data['date'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
        
        # Extract pricing information
        total_price = Decimal(str(item_data.get('total_price') or 0))
        quantity = int(item_data.get('quantity') or 1)
        unit_price_raw = item_data.get('unit_price') or 0
        if not unit_price_raw and total_price > 0 and quantity > 0:
            unit_price_raw = total_price / quantity
        unit_price = Decimal(str(unit_price_raw))
        options_total = Decimal(str(item_data.get('options_total') or 0))

        # If options_total is 0 but we have selected_options, recalculate it
        if options_total == 0 and item_data.get('selected_options'):
            selected_options = item_data.get('selected_options', [])
            if selected_options:
                for option in selected_options:
                    if isinstance(option, dict):
                        option_price = Decimal(str(option.get('price', 0)))
                        option_quantity = int(option.get('quantity', 1))
                        options_total += option_price * option_quantity
        
        return {
            'order': order,
            'product_type': item_data.get('product_type') or 'tour',
            'product_id': item_data.get('product_id'),
            'product_title': product_details['product_title'],
            'product_slug': product_details['product_slug'],
            'booking_date': booking_date,
            'booking_time': booking_time,
            'variant_id': item_data.get('variant_id') or None,
            'variant_name': item_data.get('variant_name') or '',
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': total_price,
            'currency': order.currency or 'USD',
            'selected_options': item_data.get('selected_options') or [],
            'options_total': options_total,
            'booking_data': booking_data or {},
            'status': 'pending',
            # Car rental specific fields
            'pickup_date': booking_data.get('pickup_date'),
            'dropoff_date': booking_data.get('dropoff_date'),
            'pickup_time': booking_data.get('pickup_time'),
            'dropoff_time': booking_data.get('dropoff_time'),
            'pickup_location_type': booking_data.get('pickup_location_type', 'predefined'),
            'pickup_location_id': booking_data.get('pickup_location_id'),
            'pickup_location_custom': booking_data.get('pickup_location_custom', ''),
            'pickup_location_coordinates': booking_data.get('pickup_location_coordinates', {}),
            'dropoff_location_type': booking_data.get('dropoff_location_type', 'same_as_pickup'),
            'dropoff_location_id': booking_data.get('dropoff_location_id'),
            'dropoff_location_custom': booking_data.get('dropoff_location_custom', ''),
            'dropoff_location_coordinates': booking_data.get('dropoff_location_coordinates', {}),
        }
