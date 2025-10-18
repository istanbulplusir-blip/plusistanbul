"""
DRF Views for Cart app.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import uuid
import logging
from decimal import Decimal
from django.db.models import Sum

logger = logging.getLogger(__name__)

from .models import Cart, CartItem, CartService
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, CartItemCreateSerializer
)
from orders.models import Order, OrderItem


class CartView(generics.RetrieveAPIView):
    """Get current user's cart."""
    
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]  # Allow guest access
    
    def get_object(self):
        user = self.request.user if self.request.user.is_authenticated else None
        
        # Get consistent session ID
        session_id = CartService.get_session_id(self.request)
        
        cart = CartService.get_or_create_cart(
            session_id=session_id,
            user=user
        )
        # Clear expired items on each fetch
        try:
            cart.clear_expired_items()
        except Exception:
            pass
        return cart


class AddToCartView(APIView):
    """Add item to cart."""
    
    permission_classes = [permissions.AllowAny]  # Allow guest access
    
    def check_overbooking_limits(self, request, user, product_data, cart=None):
        """
        Comprehensive overbooking validation for both guest and authenticated users.
        Prevents duplicate bookings for same product/date/variant across cart and orders.
        """
        try:
            from core.models import SystemSettings
            from orders.models import Order
            
            settings = SystemSettings.get_settings()
            product_type = product_data.get('product_type')
            product_id = product_data.get('product_id')
            variant_id = product_data.get('variant_id')
            
            # For tours, use schedule_id for precise matching
            if product_type == 'tour':
                schedule_id = product_data.get('booking_data', {}).get('schedule_id')
                if not schedule_id:
                    return False, "Tour schedule information missing"
                
                # Check current cart for same tour/schedule/variant
                if cart:
                    existing_cart_items = cart.items.filter(
                        product_type='tour',
                        product_id=product_id,
                        variant_id=variant_id,
                        booking_data__schedule_id=schedule_id
                    )
                    
                    if existing_cart_items.exists():
                        return True, "این تور در سبد خرید شما موجود است. ابتدا سفارش قبلی را تکمیل کنید."
                
                # For authenticated users, check pending orders
                if user and user.is_authenticated:
                    existing_pending_orders = Order.objects.filter(
                        user=user,
                        items__product_type='tour',
                        items__product_id=product_id,
                        items__variant_id=variant_id,
                        items__booking_data__schedule_id=schedule_id,
                        status='pending'
                    ).exists()
                    
                    if existing_pending_orders:
                        return True, "شما قبلاً این تور را رزرو کرده‌اید. ابتدا سفارش قبلی را تکمیل کنید."
                
                # For guest users, check session-based cart items
                if not user or not user.is_authenticated:
                    session_key = request.session.session_key
                    if session_key:
                        from cart.models import Cart
                        guest_carts = Cart.objects.filter(
                            session_id__startswith=session_key,
                            user__isnull=True,
                            is_active=True
                        )
                        
                        for guest_cart in guest_carts:
                            existing_items = guest_cart.items.filter(
                                product_type='tour',
                                product_id=product_id,
                                variant_id=variant_id,
                                booking_data__schedule_id=schedule_id
                            )
                            
                            if existing_items.exists():
                                return True, "این تور در سبد خرید شما موجود است. ابتدا سفارش قبلی را تکمیل کنید."
            
            # For events and other products, use booking_date
            else:
                booking_date = product_data.get('booking_date')
                if not booking_date:
                    return False, "Booking date information missing"
                
                # Check current cart for same product/date/variant
                if cart:
                    existing_cart_items = cart.items.filter(
                        product_type=product_type,
                        product_id=product_id,
                        variant_id=variant_id,
                        booking_date=booking_date
                    )
                    
                    if existing_cart_items.exists():
                        return True, "این محصول در سبد خرید شما موجود است. ابتدا سفارش قبلی را تکمیل کنید."
                
                # For authenticated users, check pending orders
                if user and user.is_authenticated:
                    existing_pending_orders = Order.objects.filter(
                        user=user,
                        items__product_type=product_type,
                        items__product_id=product_id,
                        items__variant_id=variant_id,
                        items__booking_date=booking_date,
                        status='pending'
                    ).exists()
                    
                    if existing_pending_orders:
                        return True, "شما قبلاً این محصول را رزرو کرده‌اید. ابتدا سفارش قبلی را تکمیل کنید."
                
                # For guest users, check session-based cart items
                if not user or not user.is_authenticated:
                    session_key = request.session.session_key
                    if session_key:
                        from cart.models import Cart
                        guest_carts = Cart.objects.filter(
                            session_id__startswith=session_key,
                            user__isnull=True,
                            is_active=True
                        )
                        
                        for guest_cart in guest_carts:
                            existing_items = guest_cart.items.filter(
                                product_type=product_type,
                                product_id=product_id,
                                variant_id=variant_id,
                                booking_date=booking_date
                            )
                            
                            if existing_items.exists():
                                return True, "این محصول در سبد خرید شما موجود است. ابتدا سفارش قبلی را تکمیل کنید."
            
            return False, None
            
        except Exception as e:
            print(f"Overbooking check failed: {e}")
            return False, f"خطا در بررسی محدودیت‌ها: {str(e)}"
    
    def check_rate_limit(self, request):
        """Check rate limiting for cart operations."""
        # Skip rate limiting for dry_run requests (pricing calculations)
        # Handle query params for both DRF and Django requests
        if hasattr(request, 'query_params'):
            query_params = request.query_params
        else:
            query_params = request.GET
            
        if query_params.get('dry_run') == '1':
            return True
        
        # Get system settings
        from core.models import SystemSettings
        settings = SystemSettings.get_settings()
        
        # Get client identifier
        if request.user.is_authenticated:
            client_id = f"user_{request.user.id}"
            rate_limit = settings.cart_rate_limit_user
        else:
            client_id = f"ip_{request.META.get('REMOTE_ADDR', 'unknown')}"
            rate_limit = settings.cart_rate_limit_guest
        
        # Rate limit based on settings
        cache_key = f"cart_rate_limit_{client_id}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= rate_limit:
            return False
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 60)  # 60 seconds
        return True
    
    def check_capacity_availability(self, product_data):
        """Check if capacity is available for the requested booking."""
        product_type = product_data.get('product_type')

        try:
            if product_type == 'tour':
                from tours.services import TourCapacityService
                schedule_id = product_data.get('booking_data', {}).get('schedule_id')
                variant_id = str(product_data.get('variant_id'))

                if not schedule_id or not variant_id:
                    return True, None

                # Calculate requested quantity (adults + children only)
                participants = product_data.get('booking_data', {}).get('participants', {})
                adult_count = int(participants.get('adult', 0))
                child_count = int(participants.get('child', 0))
                requested_qty = adult_count + child_count

                # Use the capacity service to get real-time availability
                available_capacity = TourCapacityService.get_available_capacity(schedule_id, variant_id)

                # Check if requested quantity fits
                if requested_qty > available_capacity:
                    return False, f"Insufficient capacity. Requested: {requested_qty}, Available: {available_capacity}"

                return True, None

            elif product_type == 'transfer':
                from transfers.services import TransferCapacityService

                # For transfers, we need route_id and vehicle_type
                route_id = product_data.get('product_id')
                vehicle_type = product_data.get('variant_id')  # vehicle_type is stored in variant_id

                if not route_id or not vehicle_type:
                    return True, None

                # Get passenger count from booking_data
                booking_data = product_data.get('booking_data', {})
                passenger_count = int(booking_data.get('passenger_count', 1))

                # Check capacity availability
                is_available, error_message = TransferCapacityService.check_capacity_availability(
                    route_id=route_id,
                    vehicle_type=vehicle_type,
                    passenger_count=passenger_count
                )

                return is_available, error_message

            else:
                # For other product types, no capacity check needed
                return True, None

        except Exception as e:
            return False, f"Capacity check failed: {str(e)}"
    
    def check_user_limits(self, request, cart, data):
        """Check limits for both guest and authenticated users."""
        from core.models import SystemSettings
        from decimal import Decimal
        
        settings = SystemSettings.get_settings()
        
        # Determine user type and limits
        if request.user and request.user.is_authenticated:
            max_items = settings.cart_max_items_user
            max_total = settings.cart_max_total_user
            user_type = "authenticated"
        else:
            max_items = settings.cart_max_items_guest
            max_total = settings.cart_max_total_guest
            user_type = "guest"
        
        try:
            # 1. Check cart item count limit
            current_items = cart.items.count()
            if current_items >= max_items:
                if user_type == 'guest':
                    return False, f"Guest users can add maximum {max_items} items to cart. Please register to add more items.", 'GUEST_CART_LIMIT_EXCEEDED'
                else:
                    return False, f"Authenticated users can add maximum {max_items} items to cart. Please remove some items to add more.", 'CART_ITEMS_LIMIT_EXCEEDED'
            
            # 2. Check cart total limit
            cart_total = sum(Decimal(str(item.total_price)) for item in cart.items.all() if item.total_price)

            # Use calculated total_price if available, otherwise fall back to unit_price calculation
            if data.get('total_price'):
                new_item_total = Decimal(str(data.get('total_price', 0)))
            else:
                new_item_total = Decimal(str(data.get('quantity', 1))) * Decimal(str(data.get('unit_price', 0)))

            if cart_total + new_item_total > max_total:
                if user_type == 'guest':
                    return False, f"Guest cart total cannot exceed ${max_total}. Please register to add more items.", 'GUEST_CART_TOTAL_EXCEEDED'
                else:
                    return False, f"Cart total cannot exceed ${max_total}. Please remove some items to add more.", 'CART_TOTAL_LIMIT_EXCEEDED'
            
            # 3. Additional guest-specific checks
            if user_type == "guest":
                # Check if guest has too many carts (prevent cart hoarding)
                from django.core.cache import cache
                ip_address = request.META.get('REMOTE_ADDR', 'unknown')
                guest_cart_count = cache.get(f"guest_carts_{ip_address}", 0)
                if guest_cart_count >= settings.cart_max_carts_guest:
                    return False, f"Too many guest carts created (max {settings.cart_max_carts_guest}). Please register or wait before creating new carts."
                
                # Check rate limiting for guest cart operations
                guest_rate_key = f"guest_cart_rate_{ip_address}"
                guest_requests = cache.get(guest_rate_key, 0)
                if guest_requests >= settings.cart_rate_limit_guest:
                    return False, f"Too many cart operations (max {settings.cart_rate_limit_guest}/minute). Please wait before trying again."
                
                # Increment counters
                cache.set(guest_rate_key, guest_requests + 1, 60)
            
            return True, None, None
            
        except Exception as e:
            return False, f"Guest limit check failed: {str(e)}", 'UNKNOWN_ERROR'
    
    def post(self, request):
        # Check for dry_run first - if it's a dry run, skip ALL validations
        # Handle both DRF request (has .data) and Django request (has .POST)
        if hasattr(request, 'data'):
            request_data = request.data
        else:
            # For Django WSGIRequest, parse JSON from request body
            import json
            try:
                request_data = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                request_data = request.POST
        
        # Handle query params for both DRF and Django requests
        if hasattr(request, 'query_params'):
            query_params = request.query_params
        else:
            query_params = request.GET
        
        dry_run_flag = request_data.get('dry_run') or query_params.get('dry_run') in ['1', 'true', 'True']

        # For dry_run requests, skip rate limiting and all validations
        if not dry_run_flag:
            # Check rate limiting
            if not self.check_rate_limit(request):
                return Response({
                    'error': 'Too many requests. Please wait a moment before trying again.',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Log request data safely (avoid Unicode errors)
        try:
            # Convert to safe string for logging to avoid Unicode errors
            safe_data = str(request_data).encode('ascii', 'replace').decode('ascii')
            logger.info(f"DEBUG: Raw request data: {safe_data}")
        except Exception as e:
            logger.info(f"DEBUG: Raw request data: [Error logging data: {e}]")
        serializer = AddToCartSerializer(data=request_data)
        if not serializer.is_valid():
            logger.warning(f"AddToCart validation failed: {serializer.errors}")
            # Log invalid data safely (avoid Unicode errors)
            try:
                logger.warning(f"DEBUG: Invalid data: {request_data}")
            except UnicodeEncodeError:
                # Convert to safe string for logging
                safe_data = str(request_data).encode('ascii', 'replace').decode('ascii')
                logger.warning(f"DEBUG: Invalid data: {safe_data}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Only perform validations if it's not a dry run
        if not dry_run_flag:
            # Check overbooking limits (comprehensive validation for both guest and authenticated users)
            overbooking_blocked, overbooking_message = self.check_overbooking_limits(request, request.user, serializer.validated_data)
            if overbooking_blocked:
                return Response({
                    'error': overbooking_message,
                    'code': 'OVERBOOKING_LIMIT_EXCEEDED',
                    'redirect_to': 'cart' if request.user and request.user.is_authenticated else 'checkout'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check capacity availability
            capacity_available, capacity_error = self.check_capacity_availability(serializer.validated_data)
            if not capacity_available:
                return Response({
                    'error': capacity_error,
                    'code': 'INSUFFICIENT_CAPACITY'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        # Log validated data safely (avoid Unicode errors)
        try:
            safe_data = str(data).encode('ascii', 'replace').decode('ascii')
            print(f"DEBUG: AddToCart validated data: {safe_data}")
        except Exception as e:
            print(f"DEBUG: AddToCart validated data: [Error logging data: {e}]")
        user = request.user if request.user.is_authenticated else None

        # Get consistent session ID
        session_id = CartService.get_session_id(request)
        print(f"DEBUG: Session ID: {session_id}, User: {user}")

        cart = CartService.get_or_create_cart(
            session_id=session_id,
            user=user
        )

        # Only check guest limits if it's not a dry run
        if not dry_run_flag:
            # Check guest limits will be done after pricing calculation
            pass

            # Track guest cart creation
            if not request.user.is_authenticated:
                ip_address = request.META.get('REMOTE_ADDR', 'unknown')
                guest_cart_count = cache.get(f"guest_carts_{ip_address}", 0)
                cache.set(f"guest_carts_{ip_address}", guest_cart_count + 1, 3600)  # 1 hour expiry

        # Get product instance based on product_type and product_id
        product_type = data['product_type']
        product_id = data['product_id']
        if product_type == 'tour':
            from tours.models import Tour
            product = Tour.objects.get(id=product_id)
        elif product_type == 'event':
            from events.models import Event
            product = Event.objects.get(id=product_id)
        elif product_type == 'transfer':
            from transfers.models import TransferRoute
            product = TransferRoute.objects.get(id=product_id)
        elif product_type == 'car_rental':
            from car_rentals.models import CarRental
            product = CarRental.objects.get(id=product_id)
        else:
            raise Exception('Invalid product_type')

        # Calculate accurate pricing for tours using age groups
        
        # Handle different product types
        if data['product_type'] == 'transfer':
            # For transfers, use TransferPricingService for accurate pricing
            from transfers.models import TransferRoutePricing
            from transfers.services import TransferPricingService
            from datetime import datetime
            
            # Get booking data
            booking_data = data.get('booking_data', {}) or {}
            vehicle_type = data.get('variant_id', 'sedan')  # Use variant_id from main request data
            trip_type = booking_data.get('trip_type', 'one_way')
            
            # Extract time from outbound_datetime if available
            outbound_time_str = data.get('booking_time') or booking_data.get('outbound_time')
            if not outbound_time_str and booking_data.get('outbound_datetime'):
                # Extract time from datetime string (format: "2025-07-16 16:34")
                datetime_str = booking_data.get('outbound_datetime')
                if ' ' in datetime_str:
                    outbound_time_str = datetime_str.split(' ')[1]
            
            return_time_str = booking_data.get('return_time')
            if not return_time_str and booking_data.get('return_datetime'):
                # Extract time from datetime string
                datetime_str = booking_data.get('return_datetime')
                if ' ' in datetime_str:
                    return_time_str = datetime_str.split(' ')[1]
            
            # Parse times
            outbound_time = None
            return_time = None
            
            if outbound_time_str:
                try:
                    outbound_time = datetime.strptime(outbound_time_str, '%H:%M').time()
                except:
                    try:
                        outbound_time = datetime.strptime(outbound_time_str, '%H:%M:%S').time()
                    except:
                        # Fallback to current time if parsing fails
                        outbound_time = datetime.now().time()
            
            if return_time_str and trip_type == 'round_trip':
                try:
                    return_time = datetime.strptime(return_time_str, '%H:%M').time()
                except:
                    try:
                        return_time = datetime.strptime(return_time_str, '%H:%M:%S').time()
                    except:
                        return_time = None
            
            # Validate passenger/luggage limits against selected vehicle pricing
            pricing = TransferRoutePricing.objects.filter(
                route=product,
                vehicle_type=vehicle_type,
                is_active=True
            ).first()
            
            if not pricing:
                unit_price = 0
                total_price_override = 0
            else:
                # Enforce temporal constraints
                try:
                    from datetime import datetime, timedelta
                    # Build naive datetimes from booking_data dates if present
                    outbound_date_str = booking_data.get('outbound_date')
                    return_date_str = booking_data.get('return_date')
                    # Now + 2h
                    now = datetime.now()
                    min_outbound_dt = now + timedelta(hours=2)
                    if outbound_date_str and outbound_time:
                        ob_dt = datetime.strptime(f"{outbound_date_str} {outbound_time.strftime('%H:%M')}", '%Y-%m-%d %H:%M')
                        if ob_dt < min_outbound_dt:
                            return Response({'message': 'Outbound must be at least 2 hours from now.'}, status=status.HTTP_400_BAD_REQUEST)
                        if trip_type == 'round_trip' and return_date_str and return_time:
                            rt_dt = datetime.strptime(f"{return_date_str} {return_time.strftime('%H:%M')}", '%Y-%m-%d %H:%M')
                            if rt_dt < ob_dt + timedelta(hours=2):
                                return Response({'message': 'Return must be at least 2 hours after outbound.'}, status=status.HTTP_400_BAD_REQUEST)
                            if rt_dt > ob_dt + timedelta(days=12):
                                return Response({'message': 'Return cannot be more than 12 days after outbound.'}, status=status.HTTP_400_BAD_REQUEST)
                except Exception:
                    pass

                # Validate capacities
                try:
                    passenger_count = int(booking_data.get('passenger_count', 1))
                except Exception:
                    passenger_count = 1
                try:
                    luggage_count = int(booking_data.get('luggage_count', 0))
                except Exception:
                    luggage_count = 0
                print(f"DEBUG: passenger_count: {passenger_count}, max_passengers: {pricing.max_passengers}")
                print(f"DEBUG: luggage_count: {luggage_count}, max_luggage: {pricing.max_luggage}")
                if passenger_count < 1 or passenger_count > int(pricing.max_passengers):
                    return Response({'message': 'Passenger count exceeds vehicle capacity.'}, status=status.HTTP_400_BAD_REQUEST)
                if luggage_count < 0 or luggage_count > int(pricing.max_luggage):
                    return Response({'message': 'Luggage count exceeds vehicle capacity.'}, status=status.HTTP_400_BAD_REQUEST)

                # Check if pricing_breakdown and final_price are provided from frontend
                print(f"DEBUG: pricing_breakdown: {data.get('pricing_breakdown')}")
                print(f"DEBUG: final_price: {data.get('final_price')}")
                print(f"DEBUG: All data keys: {list(data.keys())}")
                # Always calculate pricing in backend for security
                try:
                    # Use TransferPricingService for accurate calculation
                    if outbound_time:
                        price_data = TransferPricingService.calculate_price(
                            route=product,
                            pricing=pricing,
                            booking_time=outbound_time,
                            return_time=return_time,
                            selected_options=booking_data.get('selected_options', data.get('selected_options', []))
                        )
                        
                        unit_price = price_data['price_breakdown']['final_price']
                        total_price_override = price_data['price_breakdown']['final_price']
                        print(f"DEBUG: Backend calculated pricing - unit_price: {unit_price}, total_price_override: {total_price_override}")
                    else:
                        # Fallback to base price if no time available
                        unit_price = pricing.base_price
                        total_price_override = pricing.base_price
                        print(f"DEBUG: Using base price (no time) - unit_price: {unit_price}, total_price_override: {total_price_override}")
                    
                except Exception as e:
                    print(f"Transfer pricing calculation error: {e}")
                    unit_price = pricing.base_price
                    total_price_override = pricing.base_price
        else:
            unit_price = product.price  # Tour and Event have price
            total_price_override = None  # For tours, we'll calculate total separately
        
        tour_age_breakdown = None
        if data['product_type'] == 'tour' and data.get('variant_id'):
            from tours.models import TourVariant, TourPricing
            variant_id = data['variant_id']
            
            try:
                variant = TourVariant.objects.get(id=variant_id, tour=product)
                
                # Calculate tour pricing based on participants and age groups
                participants = data.get('booking_data', {}).get('participants', {})
                
                if participants:
                    tour_total = 0
                    tour_age_breakdown = {'adult': 0.0, 'child': 0.0, 'infant': 0.0}
                    for age_group, count in participants.items():
                        if count > 0:
                            try:
                                pricing = TourPricing.objects.get(
                                    tour=product, 
                                    variant=variant, 
                                    age_group=age_group
                                )
                                # Ensure infant pricing is always 0
                                if age_group == 'infant' or pricing.is_free:
                                    subtotal = Decimal('0.00')
                                else:
                                    subtotal = pricing.final_price * count
                                tour_total += subtotal
                                tour_age_breakdown[age_group] = float(subtotal)
                            except TourPricing.DoesNotExist:
                                # Fallback to variant base_price for missing age groups
                                if age_group == 'infant':
                                    fallback_subtotal = Decimal('0.00')
                                else:
                                    fallback_subtotal = variant.base_price * count
                                tour_total += fallback_subtotal
                                tour_age_breakdown[age_group] = float(fallback_subtotal)
                    
                    # Set unit_price and override total_price for tours
                    unit_price = variant.base_price  # Keep for reference
                    total_price_override = tour_total  # Accurate total
                else:
                    # Fallback to variant base_price if no participants data
                    unit_price = variant.base_price
            except TourVariant.DoesNotExist:
                pass
        elif data.get('variant_id'):
            variant_id = data['variant_id']
            if data['product_type'] == 'event':
                from events.models import TicketType
                try:
                    variant = TicketType.objects.get(id=variant_id, event=product)
                    # Check if TicketType has base_price or price_modifier
                    if hasattr(variant, 'base_price'):
                        unit_price = variant.base_price
                    elif hasattr(variant, 'price_modifier'):
                        unit_price += variant.price_modifier
                except TicketType.DoesNotExist:
                    pass
            elif data['product_type'] == 'transfer':
                from transfers.models import TransferRoutePricing
                try:
                    # For transfers, variant_id is the vehicle_type string, not a UUID
                    variant = TransferRoutePricing.objects.get(
                        route_id=product_id,
                        vehicle_type=variant_id
                    )
                    # Use pricing_metadata-based calculation
                    if hasattr(variant, 'calculate_price'):
                        # Get booking data for price calculation
                        booking_data = data.get('booking_data', {})
                        booking_time = booking_data.get('outbound_time')
                        return_time = booking_data.get('return_time')
                        selected_options = data.get('selected_options', [])
                        
                        if booking_time:
                            from datetime import datetime
                            if isinstance(booking_time, str):
                                booking_time = datetime.strptime(booking_time, '%H:%M').time()
                            
                            if return_time and isinstance(return_time, str):
                                return_time = datetime.strptime(return_time, '%H:%M').time()
                            
                            # Calculate price using pricing_metadata
                            price_result = variant.calculate_price(
                                hour=booking_time.hour,
                                is_round_trip=bool(return_time),
                                selected_options=selected_options
                            )
                            unit_price = price_result['final_price']
                            total_price_override = price_result['final_price']
                        else:
                            unit_price = variant.base_price
                    else:
                        unit_price = variant.base_price
                except TransferRoutePricing.DoesNotExist:
                    pass
        
        # Prepare selected options and options total (used also for dry-run)
        options_total = 0
        selected_options = data.get('selected_options', [])
        # For transfers, if selected_options is empty, try to get from booking_data
        if not selected_options and data.get('booking_data', {}).get('selected_options'):
            selected_options = data['booking_data']['selected_options']

        if selected_options:
            # Enforce option existence and max_quantity; resolve price if missing
            product_type = data['product_type']
            TransferOption = None
            TourOption = None

            if product_type == 'transfer':
                try:
                    from transfers.models import TransferOption
                except Exception:
                    TransferOption = None
            elif product_type == 'tour':
                try:
                    from tours.models import TourOption
                except Exception:
                    TourOption = None

            for option in selected_options:
                quantity = int(option.get('quantity', 1))
                option_id = option.get('option_id')
                unit_price = option.get('price')

                # Add option name if not present
                if option_id and not option.get('name'):
                    if TransferOption and product_type == 'transfer':
                        try:
                            opt_obj = TransferOption.objects.get(id=option_id, is_active=True)
                            option['name'] = opt_obj.name
                        except Exception:
                            option['name'] = f"Transfer Option {option_id[:8]}"
                    elif TourOption and product_type == 'tour':
                        try:
                            opt_obj = TourOption.objects.get(id=option_id, is_active=True)
                            option['name'] = opt_obj.name
                        except Exception:
                            option['name'] = f"Tour Option {option_id[:8]}"

                if TransferOption and option_id and product_type == 'transfer':
                    try:
                        opt_obj = TransferOption.objects.get(id=option_id, is_active=True)
                        # Scope check: if route/vehicle scoped, ensure match
                        if product_type == 'transfer':
                            if opt_obj.route and str(opt_obj.route_id) != str(product_id):
                                continue
                            if opt_obj.vehicle_type and opt_obj.vehicle_type != booking_data.get('vehicle_type'):
                                continue
                        # Enforce max_quantity
                        if opt_obj.max_quantity is not None and quantity > int(opt_obj.max_quantity):
                            quantity = int(opt_obj.max_quantity)
                        # Resolve price if not provided
                        if unit_price is None:
                            try:
                                base_price = pricing.base_price if product_type == 'transfer' and 'pricing' in locals() and pricing else 0
                            except Exception:
                                base_price = 0
                            unit_price = float(opt_obj.calculate_price(base_price))
                    except Exception:
                        continue
                try:
                    options_total += float(unit_price if unit_price is not None else 0) * quantity
                except Exception:
                    continue

        # Determine currency (default fallback)
        currency = 'USD'
        if product_type == 'transfer':
            # Use pricing currency when available
            try:
                from transfers.models import TransferRoutePricing
                vehicle_type_for_currency = (booking_data or {}).get('vehicle_type', 'sedan')
                pricing_for_currency = TransferRoutePricing.objects.filter(route=product, vehicle_type=vehicle_type_for_currency, is_active=True).first()
                currency = getattr(pricing_for_currency, 'currency', 'USD') if pricing_for_currency else 'USD'
            except Exception:
                currency = 'USD'
        else:
            currency = getattr(product, 'currency', 'USD')

        # DRY-RUN: allow price calculation without creating/updating cart items
        if dry_run_flag:
            # For dry run, skip duplicate booking check since this is just for pricing calculation
            # Users should be able to see pricing even if they have existing bookings
            if total_price_override is not None:
                total = Decimal(str(total_price_override)) + Decimal(str(options_total))
            else:
                total = Decimal(str(unit_price)) + Decimal(str(options_total))
            return Response({
                'dry_run': True,
                'product_type': product_type,
                'unit_price': float(unit_price) if unit_price is not None else 0.0,
                'options_total': float(options_total),
                'total': float(total),
                'currency': currency,
                'age_breakdown': tour_age_breakdown,
            })

        # Check if item already exists in cart
        # For transfers, we need to check more fields since each transfer booking is unique
        if data['product_type'] == 'transfer':
            existing_item = cart.items.filter(
                product_type=data['product_type'],
                product_id=data['product_id'],
                variant_id=data.get('variant_id'),
                booking_data__vehicle_type=data.get('booking_data', {}).get('vehicle_type'),
                booking_data__trip_type=data.get('booking_data', {}).get('trip_type'),
                booking_data__outbound_date=data.get('booking_data', {}).get('outbound_date'),
                booking_data__outbound_time=data.get('booking_data', {}).get('outbound_time')
            ).first()
        else:
            if data['product_type'] == 'tour':
                # Tours: uniqueness must include schedule_id to avoid overwriting different dates
                existing_item = cart.items.filter(
                    product_type='tour',
                    product_id=data['product_id'],
                    variant_id=data.get('variant_id'),
                    booking_data__schedule_id=data.get('booking_data', {}).get('schedule_id')
                ).first()
            else:
                existing_item = cart.items.filter(
                    product_type=data['product_type'],
                    product_id=data['product_id'],
                    variant_id=data.get('variant_id')
                ).first()
        
        if existing_item:
            # For authenticated users, prevent duplicate cart items (don't update existing cart item)
            if request.user and request.user.is_authenticated:
                print("DEBUG: Found existing cart item, preventing duplicate...")
                return Response({
                    'error': 'This item is already in your cart. Please check your cart or update the existing item.',
                    'code': 'DUPLICATE_CART_ITEM'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # For transfers, don't update quantity (it's always 1) - just update options
            if data['product_type'] == 'transfer':
                # Extract selected_options from booking_data if not directly available
                selected_options = data.get('selected_options', [])
                if not selected_options and data.get('booking_data', {}).get('selected_options'):
                    selected_options = data['booking_data']['selected_options']
                
                existing_item.selected_options = selected_options
                existing_item.booking_data = data.get('booking_data', {})
                existing_item.save()
                
                return Response({
                    'message': 'Transfer booking updated in cart.',
                    'cart_item': CartItemSerializer(existing_item).data
                })
            else:
                # Update existing item for tours and events
                if data['product_type'] == 'tour':
                    # For tours, merge participant counts and recalc price (do not replace silently)
                    from tours.models import TourVariant, TourPricing
                    # Merge selected options by option_id, summing quantities
                    incoming_options = data.get('selected_options', []) or []
                    if incoming_options:
                        # Add option names to incoming options if missing
                        for opt in incoming_options:
                            if opt.get('option_id') and not opt.get('name'):
                                try:
                                    from tours.models import TourOption
                                    tour_option = TourOption.objects.get(id=opt['option_id'], is_active=True)
                                    opt['name'] = tour_option.name
                                except Exception:
                                    opt['name'] = f"Tour Option {opt['option_id'][:8]}"

                        merged_options = {str(opt.get('option_id', i)): {**opt} for i, opt in enumerate(existing_item.selected_options or [])}
                        for opt in incoming_options:
                            key = str(opt.get('option_id', opt.get('option_name', 'unknown')))
                            if key in merged_options:
                                try:
                                    merged_options[key]['quantity'] = int(merged_options[key].get('quantity', 0)) + int(opt.get('quantity', 0))
                                except Exception:
                                    merged_options[key]['quantity'] = merged_options[key].get('quantity', 0)
                            else:
                                merged_options[key] = {**opt}
                        existing_item.selected_options = list(merged_options.values())
                    # Merge participants
                    existing_bd = existing_item.booking_data or {}
                    existing_participants = existing_bd.get('participants', {}) or {}
                    new_bd = data.get('booking_data', {}) or {}
                    new_participants = new_bd.get('participants', {}) or {}
                    merged_participants = {'adult': 0, 'child': 0, 'infant': 0}
                    for k in ['adult', 'child', 'infant']:
                        try:
                            merged_participants[k] = int(existing_participants.get(k, 0)) + int(new_participants.get(k, 0))
                        except Exception:
                            merged_participants[k] = int(existing_participants.get(k, 0))
                    # Enforce infant cap (<=2)
                    merged_participants['infant'] = min(2, merged_participants.get('infant', 0))
                    # Update booking_data, keep schedule_id, special_requests (append)
                    merged_bd = {**existing_bd, **new_bd}
                    merged_bd['participants'] = merged_participants
                    if existing_bd.get('special_requests') and new_bd.get('special_requests') and existing_bd.get('special_requests') != new_bd.get('special_requests'):
                        merged_bd['special_requests'] = f"{existing_bd.get('special_requests')} | {new_bd.get('special_requests')}"
                    existing_item.booking_data = merged_bd
                    participants = merged_participants
                    # Capacity counts only adults + children (infants excluded)
                    if isinstance(participants, dict):
                        try:
                            adult_count = int(participants.get('adult', 0))
                        except (TypeError, ValueError):
                            adult_count = 0
                        try:
                            child_count = int(participants.get('child', 0))
                        except (TypeError, ValueError):
                            child_count = 0
                        total_participants = adult_count + child_count
                    else:
                        total_participants = 0
                    try:
                        variant = TourVariant.objects.get(id=data.get('variant_id'), tour=product)
                        # Recalculate tour total by age groups
                        tour_total = Decimal('0.00')
                        if isinstance(participants, dict):
                            for age_group, count in participants.items():
                                count = int(count)
                                if count > 0:
                                    try:
                                        pricing = TourPricing.objects.get(
                                            tour=product,
                                            variant=variant,
                                            age_group=age_group
                                        )
                                        if age_group == 'infant' or pricing.is_free:
                                            subtotal = Decimal('0.00')
                                        else:
                                            subtotal = pricing.final_price * count
                                        tour_total += subtotal
                                    except TourPricing.DoesNotExist:
                                        if age_group == 'infant':
                                            subtotal = Decimal('0.00')
                                        else:
                                            subtotal = variant.base_price * count
                                        tour_total += subtotal
                        # Update fields
                        existing_item.quantity = total_participants
                        existing_item.unit_price = variant.base_price
                        # Add options_total on top of recalculated tour_total
                        existing_item.total_price = tour_total + Decimal(str(options_total))
                        existing_item.currency = getattr(product, 'currency', 'USD')
                        existing_item.save(skip_price_calculation=True)
                    except TourVariant.DoesNotExist:
                        # Fallback: keep previous variant/quantity behavior
                        existing_item.quantity = total_participants
                        existing_item.save()
                else:
                    # Events: keep additive quantity behavior
                    existing_item.quantity += data['quantity']
                    existing_item.selected_options = data.get('selected_options', [])
                    existing_item.save()
                
                return Response({
                    'message': 'Item updated in cart.',
                    'cart_item': CartItemSerializer(existing_item).data
                })
        else:
            # For transfers, if options don't have prices, get them from TransferOption model
            if data['product_type'] == 'transfer' and options_total == 0 and selected_options:
                from transfers.models import TransferOption
                
                for option in selected_options:
                    option_id = option.get('option_id')
                    option_quantity = option.get('quantity', 1)
                    
                    if option_id:
                        try:
                            option_obj = TransferOption.objects.get(id=option_id, is_active=True)
                            option_price = float(option_obj.calculate_price(unit_price or 0))
                            options_total += option_price * option_quantity
                        except TransferOption.DoesNotExist:
                            # Skip invalid options
                            continue
            
            # For transfers, quantity should always be 1 (it's a complete booking, not multiple units)
            if data['product_type'] == 'transfer':
                quantity = 1
            else:
                if data['product_type'] == 'tour':
                    # Derive quantity from participants (adults + children only)
                    booking_data = data.get('booking_data', {}) or {}
                    participants = booking_data.get('participants', {}) or {}
                    try:
                        adult_count = int(participants.get('adult', 0))
                    except (TypeError, ValueError):
                        adult_count = 0
                    try:
                        child_count = int(participants.get('child', 0))
                    except (TypeError, ValueError):
                        child_count = 0
                    quantity = adult_count + child_count
                else:
                    quantity = data['quantity']
            
            # Check tour capacity before creating cart item
            if data['product_type'] == 'tour':
                try:
                    from tours.services import TourCapacityService
                    schedule_id = data.get('booking_data', {}).get('schedule_id')
                    variant_id = str(data.get('variant_id'))
                    
                    if schedule_id:
                        # Quantity for capacity: adults + children
                        participants = (data.get('booking_data', {}) or {}).get('participants', {}) or {}
                        try:
                            qty_cap = int(participants.get('adult', 0)) + int(participants.get('child', 0))
                        except Exception:
                            qty_cap = data.get('quantity', 0)
                        
                        if qty_cap > 0:
                            # Use real-time capacity check (excludes pending orders)
                            available = TourCapacityService.get_available_capacity(schedule_id, variant_id)
                            if qty_cap > available:
                                return Response({
                                    'message': f'Insufficient capacity. Available: {available}, Requested: {qty_cap}'
                                }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'message': f'Capacity check failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            # For tours, get booking_date from schedule if not provided
            booking_date = data.get('booking_date')
            if data['product_type'] == 'tour' and not booking_date:
                schedule_id = data.get('booking_data', {}).get('schedule_id')
                if schedule_id:
                    try:
                        from tours.models import TourSchedule
                        schedule = TourSchedule.objects.get(id=schedule_id)
                        booking_date = schedule.start_date
                    except Exception:
                        booking_date = timezone.now().date()
                else:
                    booking_date = timezone.now().date()
            elif not booking_date:
                booking_date = timezone.now().date()
            
            # Check guest limits after pricing calculation (only if not dry run)
            if not dry_run_flag:
                # Calculate the actual item price for limit checking
                actual_item_price = total_price_override if total_price_override is not None else (Decimal(str(unit_price or 0)) + Decimal(str(options_total or 0)))

                # Only check guest limits if we have pricing data
                if actual_item_price and actual_item_price > 0:
                    # Create data dict with calculated pricing for limit check
                    pricing_data = data.copy()
                    pricing_data['unit_price'] = float(unit_price) if unit_price else 0
                    pricing_data['total_price'] = float(actual_item_price)

                    guest_limits_ok, guest_error, error_code = self.check_user_limits(request, cart, pricing_data)
                    if not guest_limits_ok:
                        return Response({
                            'error': guest_error,
                            'code': error_code or 'GUEST_LIMIT_EXCEEDED'
                        }, status=status.HTTP_400_BAD_REQUEST)

            # Handle car rental specific logic
            if data['product_type'] == 'car_rental':
                from .car_rental_service import CarRentalCartService
                
                try:
                    # Validate car rental booking
                    booking_data = data.get('booking_data', {})
                    is_valid, error_msg = CarRentalCartService.validate_car_rental_booking(
                        data['product_id'],
                        booking_data.get('pickup_date') or data.get('pickup_date'),
                        booking_data.get('dropoff_date') or data.get('dropoff_date'),
                        booking_data.get('pickup_time') or data.get('pickup_time'),
                        booking_data.get('dropoff_time') or data.get('dropoff_time')
                    )
                    
                    if not is_valid:
                        logger.warning(f"Car rental validation failed: {error_msg}")
                        return Response({
                            'error': error_msg,
                            'code': 'CAR_RENTAL_VALIDATION_ERROR'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Add car rental to cart using service
                    cart_item, is_new = CarRentalCartService.add_car_rental_to_cart(
                        cart=cart,
                        car_rental_id=data['product_id'],
                        pickup_date=booking_data.get('pickup_date') or data.get('pickup_date'),
                        dropoff_date=booking_data.get('dropoff_date') or data.get('dropoff_date'),
                        pickup_time=booking_data.get('pickup_time') or data.get('pickup_time'),
                        dropoff_time=booking_data.get('dropoff_time') or data.get('dropoff_time'),
                        pickup_location_type=data.get('pickup_location_type', 'predefined'),
                        pickup_location_id=data.get('pickup_location_id'),
                        pickup_location_custom=data.get('pickup_location_custom'),
                        pickup_location_coordinates=data.get('pickup_location_coordinates'),
                        dropoff_location_type=data.get('dropoff_location_type', 'same_as_pickup'),
                        dropoff_location_id=data.get('dropoff_location_id'),
                        dropoff_location_custom=data.get('dropoff_location_custom'),
                        dropoff_location_coordinates=data.get('dropoff_location_coordinates'),
                        selected_options=selected_options,
                        special_requests=data.get('special_requests', ''),
                        booking_data=booking_data
                    )
                    
                    logger.info(f"Car rental added to cart successfully: {cart_item.id}")
                    return Response({
                        'message': 'Car rental added to cart successfully.',
                        'cart_item': CartItemSerializer(cart_item).data,
                        'session_id': cart.session_id
                    }, status=status.HTTP_201_CREATED)
                    
                except Exception as e:
                    logger.error(f"Error adding car rental to cart: {str(e)}", exc_info=True)
                    return Response({
                        'error': f'Failed to add car rental to cart: {str(e)}',
                        'code': 'CAR_RENTAL_ADD_ERROR'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Create new item with accurate pricing
            print(f"DEBUG: Creating CartItem with variant_id: {data.get('variant_id')}")
            # Use total_price_override if available, otherwise calculate from unit_price + options_total
            if total_price_override is not None:
                final_total_price = total_price_override
            else:
                final_total_price = Decimal(str(unit_price or 0)) + Decimal(str(options_total or 0))
            
            cart_item = CartItem.objects.create(
                cart=cart,
                product_type=data['product_type'],
                product_id=data['product_id'],
                booking_date=booking_date,
                booking_time=data.get('booking_time', timezone.now().time()),
                variant_id=data.get('variant_id'),
                variant_name=data.get('variant_name', ''),
                quantity=quantity,
                unit_price=unit_price,
                total_price=final_total_price,  # Use the calculated final price
                options_total=options_total,
                currency=currency,
                selected_options=selected_options,  # Use the extracted selected_options
                booking_data=data.get('booking_data', {})
            )
            print(f"DEBUG: CartItem created successfully: {cart_item.id}, variant_id: {cart_item.variant_id}")

            # Check capacity availability for tours (but don't reserve yet)
            if data['product_type'] == 'tour' and cart_item.variant_id:
                from tours.services import TourCapacityService
                # Use capacity_quantity instead of total quantity for capacity checks
                capacity_quantity = cart_item.capacity_quantity
                capacity_available, capacity_error = TourCapacityService.check_capacity_availability(
                    schedule_id, cart_item.variant_id, capacity_quantity
                )
                if not capacity_available:
                    # If capacity is not available, delete the cart item and return error
                    cart_item.delete()
                    return Response({
                        'error': capacity_error or 'Insufficient capacity available.',
                        'code': 'INSUFFICIENT_CAPACITY'
                    }, status=status.HTTP_400_BAD_REQUEST)

                print(f"DEBUG: Capacity check passed for cart item {cart_item.id}")

            # Override total_price for tours and transfers if we calculated it separately
            if total_price_override is not None:
                if data['product_type'] == 'transfer':
                    # For transfers, use the calculated total and ensure currency consistency
                    cart_item.total_price = total_price_override
                    # Also update unit_price to reflect the final calculated price
                    cart_item.unit_price = total_price_override
                else:
                    # For tours, add options to the calculated total
                    cart_item.total_price = total_price_override + Decimal(str(options_total))
                cart_item.save(skip_price_calculation=True)
            else:
                # If no override, calculate total as unit_price + options_total
                cart_item.total_price = Decimal(str(unit_price)) + Decimal(str(options_total))
                cart_item.save(skip_price_calculation=True)
            
            return Response({
                'message': 'Item added to cart successfully.',
                'cart_item': CartItemSerializer(cart_item).data,
                'session_id': cart.session_id
            }, status=status.HTTP_201_CREATED)


class UpdateCartItemView(APIView):
    """Update cart item quantity and options."""
    
    permission_classes = [permissions.AllowAny]  # Allow guest access
    
    def put(self, request, item_id):
        """Update cart item with PUT method."""
        return self._update_item(request, item_id)
    
    def patch(self, request, item_id):
        """Update cart item with PATCH method."""
        return self._update_item(request, item_id)
    
    def _update_item(self, request, item_id):
        """Common update logic for both PUT and PATCH.
        Support both authenticated users and guest carts (session-based)."""
        # Resolve current cart based on session/user for consistent guest handling
        session_id = CartService.get_session_id(request)
        current_cart = CartService.get_or_create_cart(session_id=session_id, user=request.user if request.user.is_authenticated else None)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=current_cart)
        
        serializer = UpdateCartItemSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Update item fields
        if 'selected_options' in data:
            selected_options = data['selected_options']
            # Add option names if missing
            if selected_options and cart_item.product_type == 'tour':
                for option in selected_options:
                    if option.get('option_id') and not option.get('name'):
                        try:
                            from tours.models import TourOption
                            tour_option = TourOption.objects.get(id=option['option_id'], is_active=True)
                            option['name'] = tour_option.name
                        except Exception:
                            option['name'] = f"Tour Option {option['option_id'][:8]}"
            cart_item.selected_options = selected_options
        if 'booking_data' in data:
            cart_item.booking_data = data['booking_data']
        
        # Recompute options_total (used when overriding total_price)
        from decimal import Decimal as _D
        computed_options_total = _D('0.00')
        if cart_item.selected_options:
            for option in cart_item.selected_options:
                try:
                    price = _D(str(option.get('price', 0)))
                    qty = int(option.get('quantity', 1))
                except (TypeError, ValueError):
                    price = _D('0.00')
                    qty = 0
                computed_options_total += price * qty
        
        # For tours, recalculate pricing and quantity based on participants
        total_price_override = None
        if cart_item.product_type == 'tour':
            from tours.models import Tour, TourVariant, TourPricing
            
            try:
                tour = Tour.objects.get(id=cart_item.product_id)
                try:
                    variant = TourVariant.objects.get(id=cart_item.variant_id, tour=tour)
                except (TourVariant.DoesNotExist, ValueError, TypeError):
                    variant = None
                
                # Get updated participants (either from new data or existing)
                participants = cart_item.booking_data.get('participants', {})
                
                if participants and (variant is not None):
                    from decimal import Decimal as _D
                    tour_total = _D('0.00')
                    total_participants = 0
                    
                    for age_group, count in participants.items():
                        try:
                            count = int(count)
                        except (TypeError, ValueError):
                            count = 0
                        if count > 0:
                            total_participants += count
                            try:
                                pricing = TourPricing.objects.get(
                                    tour=tour, 
                                    variant=variant, 
                                    age_group=age_group
                                )
                                # Ensure infant pricing is always 0
                                if age_group == 'infant' or pricing.is_free:
                                    subtotal = _D('0.00')
                                else:
                                    subtotal = pricing.final_price * count
                                tour_total += subtotal
                            except TourPricing.DoesNotExist:
                                # Fallback to variant base_price for missing age groups
                                # But ensure infant is always free
                                if age_group == 'infant':
                                    subtotal = _D('0.00')
                                else:
                                    subtotal = variant.base_price * count
                                tour_total += subtotal
                    
                    # Update quantity to total participants and override total_price
                    cart_item.quantity = total_participants
                    cart_item.unit_price = variant.base_price
                    total_price_override = tour_total
                elif participants and variant is None:
                    # Fallback: use current unit_price when variant is missing
                    from decimal import Decimal as _D
                    tour_total = _D('0.00')
                    total_participants = 0
                    for age_group, count in participants.items():
                        try:
                            count = int(count)
                        except (TypeError, ValueError):
                            count = 0
                        if count > 0:
                            total_participants += count
                            if age_group == 'infant':
                                subtotal = _D('0.00')
                            else:
                                subtotal = _D(str(cart_item.unit_price)) * count
                            tour_total += subtotal
                    cart_item.quantity = total_participants
                    # keep existing unit_price
                    total_price_override = tour_total
            except (Tour.DoesNotExist):
                pass
        
        # For transfers, recalculate pricing based on updated booking data
        if cart_item.product_type == 'transfer':
            from transfers.models import TransferRoute, TransferRoutePricing
            
            try:
                route = TransferRoute.objects.get(id=cart_item.product_id)
                booking_data = cart_item.booking_data
                vehicle_type = booking_data.get('vehicle_type', 'sedan')
                trip_type = booking_data.get('trip_type', 'one_way')
                outbound_time = booking_data.get('outbound_time')
                return_time = booking_data.get('return_time')
                
                # Get base pricing
                pricing = TransferRoutePricing.objects.filter(
                    route=route,
                    vehicle_type=vehicle_type,
                    is_active=True
                ).first()
                
                if pricing:
                    base_price = pricing.base_price
                    
                    # Calculate time surcharges
                    outbound_surcharge = 0
                    return_surcharge = 0
                    
                    if outbound_time:
                        try:
                            if isinstance(outbound_time, str):
                                hour = int(str(outbound_time).split(':')[0])
                            else:
                                hour = int(getattr(outbound_time, 'hour', 12))
                            outbound_surcharge = route.calculate_time_surcharge(base_price, hour)
                        except Exception:
                            outbound_surcharge = 0
                    
                    if return_time and trip_type == 'round_trip':
                        try:
                            if isinstance(return_time, str):
                                hour = int(str(return_time).split(':')[0])
                            else:
                                hour = int(getattr(return_time, 'hour', 12))
                            return_surcharge = route.calculate_time_surcharge(base_price, hour)
                        except Exception:
                            return_surcharge = 0
                    
                    # Calculate round trip discount
                    round_trip_discount = 0
                    if trip_type == 'round_trip' and route.round_trip_discount_enabled:
                        total_before_discount = (base_price + outbound_surcharge) + (base_price + return_surcharge)
                        round_trip_discount = total_before_discount * (route.round_trip_discount_percentage / 100)
                    
                    # Calculate final price
                    if trip_type == 'round_trip':
                        total_price = (base_price + outbound_surcharge) + (base_price + return_surcharge) - round_trip_discount
                    else:
                        total_price = base_price + outbound_surcharge
                    
                    cart_item.unit_price = base_price
                    total_price_override = total_price
            except TransferRoute.DoesNotExist:
                pass
        
        # For non-tour products, update quantity directly if provided (but not for transfers)
        if cart_item.product_type not in ['tour', 'transfer'] and 'quantity' in data:
            cart_item.quantity = data['quantity']
        
        # Save with or without price override
        if total_price_override is not None:
            if cart_item.product_type == 'transfer':
                # For transfers, add options to the calculated total
                cart_item.total_price = total_price_override + computed_options_total
            else:
                # For tours, add options to the calculated total
                cart_item.total_price = total_price_override + computed_options_total
            cart_item.save(skip_price_calculation=True)
        else:
            cart_item.save()
        
        return Response({
            'message': 'Cart item updated successfully.',
            'cart_item': CartItemSerializer(cart_item).data
        })


class RemoveFromCartView(APIView):
    """Remove item from cart."""
    
    permission_classes = [permissions.AllowAny]  # Allow guest access
    
    def delete(self, request, item_id):
        # Resolve current cart based on session/user for consistent guest handling
        session_id = CartService.get_session_id(request)
        current_cart = CartService.get_or_create_cart(session_id=session_id, user=request.user if request.user.is_authenticated else None)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=current_cart)
        cart_item.delete()
        
        return Response({
            'message': 'Item removed from cart successfully.'
        })


class ClearCartView(APIView):
    """Clear all items from cart."""
    
    permission_classes = [permissions.AllowAny]  # Allow guest access
    
    def delete(self, request):
        user = request.user
        
        # Get consistent session ID
        session_id = CartService.get_session_id(request)
        
        cart = CartService.get_or_create_cart(
            session_id=session_id,
            user=user
        )
        cart.items.all().delete()
        return Response({
            'message': 'Cart cleared successfully.'
        })


class AddEventSeatsToCartView(APIView):
    """Add event seats to cart."""
    
    permission_classes = [permissions.AllowAny]  # Allow guest access
    
    def post(self, request):
        # Validate required fields
        required_fields = ['event_id', 'performance_id', 'ticket_type_id', 'seats']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'message': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            event_id = request.data['event_id']
            performance_id = request.data['performance_id']
            ticket_type_id = request.data['ticket_type_id']
            seats = request.data['seats']
            selected_options = request.data.get('selected_options', [])
            special_requests = request.data.get('special_requests', '')
            
            # Validate seats
            if not seats or not isinstance(seats, list):
                return Response({
                    'message': 'Seats must be a non-empty list'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create cart using CartService
            user = request.user
            session_id = CartService.get_session_id(request)
            cart = CartService.get_or_create_cart(session_id=session_id, user=user)
            
            # Use the service to add seats with proper merging logic
            from .services import EventCartService
            cart_item, is_new_item = EventCartService.add_event_seats_to_cart(
                cart=cart,
                event_id=event_id,
                performance_id=performance_id,
                ticket_type_id=ticket_type_id,
                seats=seats,
                selected_options=selected_options,
                special_requests=special_requests
            )
            
            if is_new_item:
                return Response({
                    'message': 'Event seats added to cart successfully.',
                    'cart_item': CartItemSerializer(cart_item).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Seats merged with existing cart item.',
                    'cart_item': CartItemSerializer(cart_item).data
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'Error adding seats to cart: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckCapacityView(APIView):
    """Check real-time capacity availability."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Check if capacity is available for the requested booking."""
        from tours.services import TourCapacityService

        product_type = request.data.get('product_type')
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        booking_data = request.data.get('booking_data', {})

        if product_type != 'tour':
            return Response({'available': True, 'available_capacity': 999})

        schedule_id = booking_data.get('schedule_id')
        if not schedule_id or not variant_id:
            return Response({'available': False, 'error': 'Missing schedule or variant ID'})

        # Calculate participants for capacity
        participants = booking_data.get('participants', {})
        adult_count = int(participants.get('adult', 0))
        child_count = int(participants.get('child', 0))
        requested_quantity = adult_count + child_count

        # Get real-time capacity
        available_capacity = TourCapacityService.get_available_capacity(schedule_id, variant_id)

        return Response({
            'available': requested_quantity <= available_capacity,
            'available_capacity': available_capacity,
            'requested_quantity': requested_quantity
        })


class CartSummaryView(APIView):
    """Get cart summary for checkout."""

    permission_classes = [permissions.AllowAny]  # Allow guest access

    def get(self, request):
        user = request.user

        # Get consistent session ID
        session_id = CartService.get_session_id(request)

        cart = CartService.get_or_create_cart(
            session_id=session_id,
            user=user
        )

        # Calculate totals using correct pricing logic
        total_items = sum(item.quantity for item in cart.items.all())
        distinct_items = cart.items.count()

        # Use CartSerializer methods for consistency (including fees/tax/grand total)
        cart_serializer = CartSerializer(cart)
        subtotal = cart_serializer.get_subtotal(cart)
        total_price = cart_serializer.get_total_price(cart)
        fees_total = cart_serializer.get_fees_total(cart)
        tax_total = cart_serializer.get_tax_total(cart)
        grand_total = cart_serializer.get_grand_total(cart)

        # Get currency (use first item's currency or default)
        currency = 'USD'
        if cart.items.exists():
            currency = cart.items.first().currency

        return Response({
            'total_items': total_items,
            'distinct_items': distinct_items,
            'subtotal': float(subtotal),
            'fees_total': float(fees_total),
            'tax_total': float(tax_total),
            'grand_total': float(grand_total),
            'total_price': float(total_price),
            'currency': currency,
            'items': CartItemSerializer(cart.items.all(), many=True).data
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def merge_cart_view(request):
    """Merge session cart with user cart."""
    
    user = request.user
    # Safety guard (should be enforced by permissions, but keep for clarity)
    if not user or not user.is_authenticated:
        return Response({'message': 'Authentication required to merge cart.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get the session key from request data (sent by frontend)
    session_key = None
    if request.data and request.data.get('session_key'):
        session_key = request.data.get('session_key')
    
    # Fallback to request session key if not provided in data
    if not session_key:
        session_key = request.session.session_key

    if not session_key:
        return Response({'message': 'No session cart found to merge.'})
    
    # Log guest cart identification for debugging
    print(f"🔍 Merging guest cart (session: {session_key}) with user cart (user: {user.id}, email: {user.email})")
    
    # Retry mechanism for database lock issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Get user cart using CartService with the same session key as guest cart
            user_cart = CartService.get_or_create_cart(
                session_id=session_key,
                user=user
            )
            # Lock user cart for update
            user_cart = Cart.objects.select_for_update().get(id=user_cart.id)
            break  # Success, exit retry loop
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Cart creation attempt {attempt + 1} failed: {e}")
                import time
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                continue
            else:
                print(f"❌ Failed to create/get user cart after {max_retries} attempts: {e}")
                return Response({
                    'message': 'Failed to prepare user cart for merge.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Look for session cart with the base session key
    session_cart = None
    for attempt in range(max_retries):
        try:
            # First try to find guest cart (user__isnull=True)
            session_cart = Cart.objects.select_for_update().get(session_id=session_key, user__isnull=True)
            print(f"🔍 Found guest cart with {session_cart.items.count()} items")
            break  # Success, exit retry loop
        except Cart.DoesNotExist:
            # If no guest cart found, check if there's already a user cart
            # This happens when CartService already migrated the cart
            try:
                existing_user_cart = Cart.objects.get(user=user, is_active=True)
                print(f"🔍 User cart already exists with {existing_user_cart.items.count()} items")
                return Response({
                    'message': 'Cart already merged successfully.',
                    'items_count': existing_user_cart.items.count()
                })
            except Cart.DoesNotExist:
                pass
            break  # Not a retryable error, exit loop
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Session cart lookup attempt {attempt + 1} failed: {e}")
                import time
                time.sleep(0.05 * (attempt + 1))
                continue
            else:
                print(f"❌ Failed to find session cart after {max_retries} attempts: {e}")
                return Response({
                    'message': 'Failed to access session cart.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not session_cart:
        # Try to find any guest cart for this user's session
        # This handles cases where the session key might have been modified
        for attempt in range(max_retries):
            try:
                session_cart = Cart.objects.filter(
                    session_id__startswith=session_key,
                    user__isnull=True,
                    is_active=True
                ).first()
                break  # Success or no results, exit retry loop
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Guest cart search attempt {attempt + 1} failed: {e}")
                    import time
                    time.sleep(0.05 * (attempt + 1))
                    continue
                else:
                    print(f"❌ Failed to search guest cart after {max_retries} attempts: {e}")

        if not session_cart:
            # Also try to find by session_key from request data
            if request.data and request.data.get('session_key'):
                request_session_key = request.data.get('session_key')
                for attempt in range(max_retries):
                    try:
                        session_cart = Cart.objects.select_for_update().get(session_id=request_session_key, user__isnull=True)
                        print(f"🔍 Found guest cart by request session_key with {session_cart.items.count()} items")
                        break
                    except Cart.DoesNotExist:
                        # Try partial match
                        try:
                            session_cart = Cart.objects.filter(
                                session_id__startswith=request_session_key,
                                user__isnull=True,
                                is_active=True
                            ).first()
                            if session_cart:
                                print(f"🔍 Found guest cart by partial request session_key with {session_cart.items.count()} items")
                                break
                        except Exception:
                            pass
                        break  # Not retryable, exit
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"⚠️ Request session cart lookup attempt {attempt + 1} failed: {e}")
                            import time
                            time.sleep(0.05 * (attempt + 1))
                            continue
                        else:
                            print(f"❌ Failed to find request session cart after {max_retries} attempts: {e}")

            if not session_cart:
                print(f"🔍 No guest cart found for session: {session_key}")
                return Response({
                    'message': 'No session cart found to merge.',
                    'debug_info': {
                        'session_key': session_key,
                        'user_id': user.id,
                        'user_email': user.email,
                        'request_session_key': request.data.get('session_key') if request.data else None
                    }
                })
    
    # Check limits before merging
    from core.models import SystemSettings
    from decimal import Decimal
    
    settings = SystemSettings.get_settings()
    current_items = user_cart.items.count()
    current_total = sum(Decimal(str(item.total_price)) for item in user_cart.items.all() if item.total_price)
    
    guest_items = session_cart.items.count()
    guest_total = sum(Decimal(str(item.total_price)) for item in session_cart.items.all() if item.total_price)
    
    # Check if merge would exceed limits
    if current_items + guest_items > settings.cart_max_items_user:
        return Response({
            'message': f'Cannot merge: would exceed maximum {settings.cart_max_items_user} items limit. Please remove some items first.',
            'code': 'MERGE_LIMIT_EXCEEDED',
            'current_items': current_items,
            'guest_items': guest_items,
            'max_items': settings.cart_max_items_user
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if current_total + guest_total > settings.cart_max_total_user:
        return Response({
            'message': f'Cannot merge: would exceed maximum ${settings.cart_max_total_user} total limit. Please remove some items first.',
            'code': 'MERGE_TOTAL_EXCEEDED',
            'current_total': float(current_total),
            'guest_total': float(guest_total),
            'max_total': float(settings.cart_max_total_user)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if guest cart itself exceeds guest limits (security check)
    if guest_items > settings.cart_max_items_guest:
        return Response({
            'message': f'Guest cart exceeds maximum {settings.cart_max_items_guest} items limit.',
            'code': 'GUEST_CART_LIMIT_EXCEEDED',
            'guest_items': guest_items,
            'max_guest_items': settings.cart_max_items_guest
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if guest_total > settings.cart_max_total_guest:
        return Response({
            'message': f'Guest cart exceeds maximum ${settings.cart_max_total_guest} total limit.',
            'code': 'GUEST_CART_TOTAL_EXCEEDED',
            'guest_total': float(guest_total),
            'max_guest_total': float(settings.cart_max_total_guest)
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check for overbooking conflicts before merging
    from orders.models import Order
    overbooking_conflicts = []
    
    for session_item in session_cart.items.all():
        # Check if user already has pending orders for this product/date/variant
        if session_item.product_type == 'tour':
            schedule_id = session_item.booking_data.get('schedule_id')
            if schedule_id:
                # Check pending orders
                existing_pending_orders = Order.objects.filter(
                    user=user,
                    items__product_type='tour',
                    items__product_id=session_item.product_id,
                    items__variant_id=session_item.variant_id,
                    items__booking_data__schedule_id=schedule_id,
                    status='pending'
                ).exists()
                
                if existing_pending_orders:
                    overbooking_conflicts.append({
                        'product_type': session_item.product_type,
                        'product_id': session_item.product_id,
                        'product_title': session_item.product_title,
                        'message': 'شما قبلاً این تور را رزرو کرده‌اید. ابتدا سفارش قبلی را تکمیل کنید.'
                    })
                
                # Check if user already has this item in their current cart
                existing_cart_item = user_cart.items.filter(
                    product_type='tour',
                    product_id=session_item.product_id,
                    variant_id=session_item.variant_id,
                    booking_data__schedule_id=schedule_id
                ).exists()
                
                if existing_cart_item:
                    overbooking_conflicts.append({
                        'product_type': session_item.product_type,
                        'product_id': session_item.product_id,
                        'product_title': session_item.product_title,
                        'message': 'این تور در سبد خرید شما موجود است. ابتدا سفارش قبلی را تکمیل کنید.'
                    })
        else:
            # For events and other products
            # Check pending orders
            existing_pending_orders = Order.objects.filter(
                user=user,
                items__product_type=session_item.product_type,
                items__product_id=session_item.product_id,
                items__variant_id=session_item.variant_id,
                items__booking_date=session_item.booking_date,
                status='pending'
            ).exists()
            
            if existing_pending_orders:
                overbooking_conflicts.append({
                    'product_type': session_item.product_type,
                    'product_id': session_item.product_id,
                    'product_title': session_item.product_title,
                    'message': 'شما قبلاً این محصول را رزرو کرده‌اید. ابتدا سفارش قبلی را تکمیل کنید.'
                })
            
            # Check if user already has this item in their current cart
            existing_cart_item = user_cart.items.filter(
                product_type=session_item.product_type,
                product_id=session_item.product_id,
                variant_id=session_item.variant_id,
                booking_date=session_item.booking_date
            ).exists()
            
            if existing_cart_item:
                overbooking_conflicts.append({
                    'product_type': session_item.product_type,
                    'product_id': session_item.product_id,
                    'product_title': session_item.product_title,
                    'message': 'این محصول در سبد خرید شما موجود است. ابتدا سفارش قبلی را تکمیل کنید.'
                })
    
    # If there are overbooking conflicts, return error
    if overbooking_conflicts:
        return Response({
            'message': 'Cannot merge cart due to overbooking conflicts.',
            'code': 'OVERBOOKING_CONFLICTS',
            'conflicts': overbooking_conflicts,
            'redirect_to': 'orders'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Merge items with atomic transaction
    from django.db import transaction
    
    with transaction.atomic():
        merged_items = 0
        skipped_items = 0
        
        for session_item in session_cart.items.all():
            # Check if item already exists in user cart
            # For tours, also check schedule_id to prevent duplicates
            if session_item.product_type == 'tour':
                existing_item = user_cart.items.filter(
                    product_type=session_item.product_type,
                    product_id=session_item.product_id,
                    variant_id=session_item.variant_id,
                    booking_data__schedule_id=session_item.booking_data.get('schedule_id')
                ).first()
            else:
                existing_item = user_cart.items.filter(
                    product_type=session_item.product_type,
                    product_id=session_item.product_id,
                    variant_id=session_item.variant_id
                ).first()
            
            if existing_item:
                # Check if merging quantities would exceed limits
                new_quantity = existing_item.quantity + session_item.quantity
                if new_quantity > 10:  # Max quantity per item
                    skipped_items += 1
                    print(f"🔍 Skipped item due to quantity limit: {session_item.product_type} #{session_item.product_id}")
                    continue

                # Merge with retry mechanism
                for attempt in range(max_retries):
                    try:
                        existing_item.quantity = new_quantity
                        existing_item.save()
                        print(f"🔍 Merged existing item: {session_item.product_type} #{session_item.product_id} (qty: {session_item.quantity})")
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"⚠️ Item merge attempt {attempt + 1} failed: {e}")
                            import time
                            time.sleep(0.05 * (attempt + 1))
                            continue
                        else:
                            print(f"❌ Failed to merge existing item after {max_retries} attempts: {e}")
                            skipped_items += 1
                            break
        else:
            # Move item with retry mechanism
            for attempt in range(max_retries):
                try:
                    session_item.cart = user_cart
                    session_item.save()
                    print(f"🔍 Moved guest item to user cart: {session_item.product_type} #{session_item.product_id} (qty: {session_item.quantity})")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Item move attempt {attempt + 1} failed: {e}")
                        import time
                        time.sleep(0.05 * (attempt + 1))
                        continue
                    else:
                        print(f"❌ Failed to move item after {max_retries} attempts: {e}")
                        skipped_items += 1
                        break
            
            merged_items += 1
        
        # Delete session cart with retry mechanism
        for attempt in range(max_retries):
            try:
                session_cart.delete()
                print(f"🔍 Successfully deleted session cart")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Session cart delete attempt {attempt + 1} failed: {e}")
                    import time
                    time.sleep(0.05 * (attempt + 1))
                    continue
                else:
                    print(f"⚠️ Failed to delete session cart after {max_retries} attempts: {e}")
                    # Try to clear items manually if delete fails
                    try:
                        session_cart.items.all().delete()
                        session_cart.save()
                        print(f"🔍 Cleared session cart items manually")
                    except Exception as e2:
                        print(f"⚠️ Failed to clear session cart items: {e2}")
                        # Continue anyway - the merge was successful
    
    return Response({
        'message': f'Successfully merged {merged_items} items from session cart.',
        'cart': CartSerializer(user_cart).data,
        'debug_info': {
            'guest_session_id': session_key,
            'user_id': user.id,
            'user_email': user.email,
            'merged_items_count': merged_items,
            'skipped_items_count': skipped_items
        }
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow guest access
def cart_count_view(request):
    """Get cart item count for navbar."""
    
    user = request.user
    
    # Get consistent session ID
    session_id = CartService.get_session_id(request)
    
    cart = CartService.get_or_create_cart(
        session_id=session_id,
        user=user
    )
    # Business requirement: count each cart line as 1 regardless of internal quantities
    count = cart.items.count()
    return Response({'count': count})