"""
Unified transfer booking service for both regular users and agents.
"""

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal

from .models import TransferRoute, TransferRoutePricing, TransferBooking
from cart.services import CartService
from orders.services import OrderService


class TransferBookingService:
    """Unified service for transfer bookings"""
    
    @staticmethod
    def book_transfer(user, transfer_data, agent=None):
        """
        Book a transfer for a user (regular or agent booking)
        
        Args:
            user: User making the booking
            transfer_data: Dictionary containing booking details
            agent: Agent object if this is an agent booking (optional)
        
        Returns:
            Dictionary with booking result
        """
        try:
            with transaction.atomic():
                # Validate required fields
                required_fields = ['route_id', 'vehicle_type', 'booking_date', 'booking_time', 'passenger_count']
                for field in required_fields:
                    if not transfer_data.get(field):
                        raise ValidationError(f'{field} is required')
                
                # Get route and pricing
                route = TransferRoute.objects.get(id=transfer_data['route_id'], is_active=True)
                pricing = TransferRoutePricing.objects.get(
                    route=route,
                    vehicle_type=transfer_data['vehicle_type'],
                    is_active=True
                )
                
                # Validate capacity
                passenger_count = transfer_data['passenger_count']
                if passenger_count > pricing.max_passengers:
                    raise ValidationError(f"Passenger count ({passenger_count}) exceeds vehicle capacity ({pricing.max_passengers})")
                
                # Validate booking time (minimum 2 hours in advance)
                booking_datetime = datetime.combine(
                    transfer_data['booking_date'], 
                    transfer_data['booking_time']
                )
                if booking_datetime <= timezone.now() + timedelta(hours=2):
                    raise ValidationError("Booking must be at least 2 hours in advance")
                
                # Calculate pricing
                if agent:
                    # Use agent pricing service
                    from agents.pricing_service import AgentPricingService
                    pricing_result = AgentPricingService.calculate_transfer_price_for_agent(
                        route=route,
                        vehicle_type=transfer_data['vehicle_type'],
                        agent=agent,
                        passenger_count=passenger_count,
                        trip_type=transfer_data.get('trip_type', 'one_way'),
                        hour=transfer_data['booking_time'].hour if isinstance(transfer_data['booking_time'], datetime) else None,
                        return_hour=transfer_data.get('return_time', {}).get('hour') if transfer_data.get('return_time') else None,
                        selected_options=transfer_data.get('selected_options', [])
                    )
                    final_price = pricing_result['agent_total']
                else:
                    # Use regular pricing
                    pricing_result = pricing.calculate_price(
                        hour=transfer_data['booking_time'].hour if isinstance(transfer_data['booking_time'], datetime) else None,
                        return_hour=transfer_data.get('return_time', {}).get('hour') if transfer_data.get('return_time') else None,
                        is_round_trip=transfer_data.get('trip_type') == 'round_trip',
                        selected_options=transfer_data.get('selected_options', [])
                    )
                    final_price = pricing_result['final_price']
                
                # Create cart for user
                cart = CartService.get_or_create_cart(
                    session_id=f"{'agent' if agent else 'user'}_{user.id}_{timezone.now().timestamp()}",
                    user=user
                )
                
                # Add transfer to cart
                cart_item_data = {
                    'product_type': 'transfer',
                    'product_id': str(route.id),
                    'variant_id': transfer_data['vehicle_type'],
                    'variant_name': pricing.vehicle_name,
                    'booking_date': transfer_data['booking_date'],
                    'booking_time': transfer_data['booking_time'],
                    'quantity': 1,  # Transfer is per vehicle, not per passenger
                    'unit_price': pricing_result['base_price'] if agent else pricing.base_price,
                    'total_price': final_price,
                    'selected_options': transfer_data.get('selected_options', []),
                    'options_total': pricing_result.get('options_total', 0),
                    'booking_data': {
                        'route_id': str(route.id),
                        'pricing_id': str(pricing.id),
                        'trip_type': transfer_data.get('trip_type', 'one_way'),
                        'passenger_count': passenger_count,
                        'vehicle_type': transfer_data['vehicle_type'],
                        'pickup_address': transfer_data.get('pickup_address', ''),
                        'dropoff_address': transfer_data.get('dropoff_address', ''),
                        'return_date': transfer_data.get('return_date'),
                        'return_time': transfer_data.get('return_time'),
                        'agent_booking': bool(agent),
                        'agent_id': str(agent.id) if agent else None,
                        'pricing_info': pricing_result if agent else {
                            'base_price': pricing.base_price,
                            'final_price': final_price,
                            'options_total': pricing_result.get('options_total', 0)
                        }
                    }
                }
                
                cart_item = CartService.add_to_cart(cart, cart_item_data)
                
                # Create order
                order = OrderService.create_order_from_cart(
                    cart=cart,
                    user=user,
                    agent=agent
                )
                
                # Handle payment method and order status
                payment_method = transfer_data.get('payment_method', 'whatsapp')
                if payment_method == 'direct_payment':
                    order.status = 'paid'
                    order.payment_status = 'paid'
                    order.payment_method = 'bank_gateway'
                elif payment_method == 'agent_credit':
                    order.status = 'paid'
                    order.payment_status = 'paid'
                    order.payment_method = 'agent_credit'
                else:  # whatsapp
                    order.status = 'pending'
                    order.payment_status = 'pending'
                    order.payment_method = 'whatsapp'
                
                order.save()
                
                # Create commission record if agent booking
                if agent:
                    from agents.models import AgentCommission
                    commission = AgentCommission.objects.create(
                        agent=agent,
                        order=order,
                        commission_amount=pricing_result.get('commission_amount', 0),
                        commission_rate=pricing_result.get('commission_rate', 0),
                        status='pending' if payment_method == 'whatsapp' else 'confirmed'
                    )
                
                return {
                    'success': True,
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                    'total_amount': float(order.total_amount),
                    'commission_amount': float(commission.commission_amount) if agent else 0,
                    'pricing_info': pricing_result if agent else {
                        'base_price': pricing.base_price,
                        'final_price': final_price,
                        'options_total': pricing_result.get('options_total', 0)
                    },
                    'message': 'Transfer booked successfully'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error booking transfer'
            }
    
    @staticmethod
    def create_transfer_booking_record(user, transfer_data, order):
        """
        Create a TransferBooking record for tracking purposes
        This is optional and can be used for transfer-specific tracking
        """
        try:
            route = TransferRoute.objects.get(id=transfer_data['route_id'])
            pricing = TransferRoutePricing.objects.get(
                route=route,
                vehicle_type=transfer_data['vehicle_type']
            )
            
            # Generate booking reference
            booking_reference = f"TRF{order.id:06d}"
            
            # Create TransferBooking record
            transfer_booking = TransferBooking.objects.create(
                route=route,
                pricing=pricing,
                user=user,
                booking_reference=booking_reference,
                trip_type=transfer_data.get('trip_type', 'one_way'),
                outbound_date=transfer_data['booking_date'],
                outbound_time=transfer_data['booking_time'],
                return_date=transfer_data.get('return_date'),
                return_time=transfer_data.get('return_time'),
                passenger_count=transfer_data['passenger_count'],
                luggage_count=transfer_data.get('luggage_count', 0),
                pickup_address=transfer_data.get('pickup_address', ''),
                pickup_instructions=transfer_data.get('pickup_instructions', ''),
                dropoff_address=transfer_data.get('dropoff_address', ''),
                dropoff_instructions=transfer_data.get('dropoff_instructions', ''),
                contact_name=transfer_data.get('contact_name', user.get_full_name() or user.username),
                contact_phone=transfer_data.get('contact_phone', ''),
                selected_options=transfer_data.get('selected_options', []),
                special_requirements=transfer_data.get('special_requirements', ''),
                final_price=order.total_amount,
                status='pending'
            )
            
            return transfer_booking
            
        except Exception as e:
            # Log error but don't fail the main booking process
            print(f"Error creating TransferBooking record: {e}")
            return None
