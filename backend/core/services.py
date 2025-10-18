"""
Centralized limit validation service for the Peykan Tourism Platform.
This service provides consistent limit checking across all modules.
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from django.core.cache import cache
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import SystemSettings

User = get_user_model()


class LimitValidationService:
    """
    Centralized service for validating all system limits.
    """
    
    @staticmethod
    def get_settings() -> SystemSettings:
        """Get current system settings."""
        return SystemSettings.get_settings()
    
    @staticmethod
    def validate_cart_limits(user: Optional[User], cart_items_count: int, cart_total: Decimal, 
                           new_item_total: Decimal = Decimal('0')) -> Tuple[bool, Optional[str]]:
        """
        Validate cart limits for both guest and authenticated users.
        
        Args:
            user: User object (None for guests)
            cart_items_count: Current number of items in cart
            cart_total: Current total amount in cart
            new_item_total: Total amount of new item being added
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        settings = LimitValidationService.get_settings()
        
        if user and user.is_authenticated:
            max_items = settings.cart_max_items_user
            max_total = settings.cart_max_total_user
            user_type = "authenticated"
        else:
            max_items = settings.cart_max_items_guest
            max_total = settings.cart_max_total_guest
            user_type = "guest"
        
        # Check item count limit
        if cart_items_count >= max_items:
            return False, f"{user_type.capitalize()} users can add maximum {max_items} items to cart."
        
        # Check total amount limit
        if cart_total + new_item_total > max_total:
            return False, f"{user_type.capitalize()} cart total cannot exceed ${max_total}."
        
        return True, None
    
    @staticmethod
    def validate_merge_limits(user: User, user_cart_items: int, user_cart_total: Decimal,
                             guest_cart_items: int, guest_cart_total: Decimal) -> Tuple[bool, Optional[str], str]:
        """
        Validate limits when merging guest cart with user cart.
        
        Returns:
            Tuple of (is_valid, error_message, error_code)
        """
        settings = LimitValidationService.get_settings()
        
        # Check if merge would exceed user limits
        if user_cart_items + guest_cart_items > settings.cart_max_items_user:
            return False, f"Cannot merge: would exceed maximum {settings.cart_max_items_user} items limit.", "MERGE_LIMIT_EXCEEDED"
        
        if user_cart_total + guest_cart_total > settings.cart_max_total_user:
            return False, f"Cannot merge: would exceed maximum ${settings.cart_max_total_user} total limit.", "MERGE_TOTAL_EXCEEDED"
        
        # Check if guest cart itself exceeds guest limits (security check)
        if guest_cart_items > settings.cart_max_items_guest:
            return False, f"Guest cart exceeds maximum {settings.cart_max_items_guest} items limit.", "GUEST_CART_LIMIT_EXCEEDED"
        
        if guest_cart_total > settings.cart_max_total_guest:
            return False, f"Guest cart exceeds maximum ${settings.cart_max_total_guest} total limit.", "GUEST_CART_TOTAL_EXCEEDED"
        
        return True, None, None
    
    @staticmethod
    def validate_order_limits(user: User, cart_items_count: int, cart_total: Decimal) -> Tuple[bool, Optional[str]]:
        """
        Validate limits before creating order.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        settings = LimitValidationService.get_settings()
        
        # Check item count limit
        if cart_items_count > settings.cart_max_items_user:
            return False, f"Cart exceeds maximum {settings.cart_max_items_user} items limit."
        
        # Check total amount limit
        if cart_total > settings.cart_max_total_user:
            return False, f"Cart exceeds maximum ${settings.cart_max_total_user} total limit."
        
        # Check pending order limit
        from orders.models import Order
        pending_count = Order.objects.filter(user=user, status='pending').count()
        if pending_count >= settings.order_max_pending_per_user:
            return False, f"You can have maximum {settings.order_max_pending_per_user} pending orders."
        
        return True, None
    
    @staticmethod
    def validate_rate_limit(user: Optional[User], request_type: str = 'cart') -> Tuple[bool, Optional[str]]:
        """
        Validate rate limiting for requests.
        
        Args:
            user: User object (None for guests)
            request_type: Type of request ('cart', 'order', etc.)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        settings = LimitValidationService.get_settings()
        
        if user and user.is_authenticated:
            rate_limit = settings.cart_rate_limit_user
            client_id = f"user_{user.id}"
        else:
            rate_limit = settings.cart_rate_limit_guest
            client_id = f"ip_guest"  # In real implementation, use IP address
        
        cache_key = f"{request_type}_rate_limit_{client_id}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= rate_limit:
            return False, f"Too many requests. Please wait before trying again."
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 60)  # 60 seconds
        return True, None
    
    @staticmethod
    def validate_duplicate_booking(user: User, product_type: str, product_id: str, 
                                 variant_id: Optional[str], booking_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate against duplicate bookings.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        from orders.models import Order
        from cart.models import Cart
        
        # Check pending orders
        if product_type == 'tour':
            schedule_id = booking_data.get('schedule_id')
            if schedule_id:
                existing_pending = Order.objects.filter(
                    user=user,
                    items__product_type='tour',
                    items__product_id=product_id,
                    items__variant_id=variant_id,
                    items__booking_data__schedule_id=schedule_id,
                    status='pending'
                ).exists()
                
                if existing_pending:
                    return False, "شما قبلاً این تور را رزرو کرده‌اید. ابتدا سفارش قبلی را تکمیل کنید."
        else:
            booking_date = booking_data.get('booking_date')
            if booking_date:
                existing_pending = Order.objects.filter(
                    user=user,
                    items__product_type=product_type,
                    items__product_id=product_id,
                    items__variant_id=variant_id,
                    items__booking_date=booking_date,
                    status='pending'
                ).exists()
                
                if existing_pending:
                    return False, "شما قبلاً این محصول را رزرو کرده‌اید. ابتدا سفارش قبلی را تکمیل کنید."
        
        return True, None


class LimitValidationMixin:
    """
    Mixin class to add limit validation to views.
    """
    
    def validate_cart_limits(self, request, cart, data):
        """Validate cart limits using the centralized service."""
        return LimitValidationService.validate_cart_limits(
            request.user,
            cart.items.count(),
            sum(Decimal(str(item.total_price)) for item in cart.items.all() if item.total_price),
            Decimal(str(data.get('total_price', 0)))
        )
    
    def validate_rate_limit(self, request, request_type='cart'):
        """Validate rate limits using the centralized service."""
        return LimitValidationService.validate_rate_limit(request.user, request_type)
    
    def validate_duplicate_booking(self, request, product_data):
        """Validate duplicate booking using the centralized service."""
        if request.user and request.user.is_authenticated:
            return LimitValidationService.validate_duplicate_booking(
                request.user,
                product_data.get('product_type'),
                product_data.get('product_id'),
                product_data.get('variant_id'),
                product_data.get('booking_data', {})
            )
        return True, None
