"""
Cart models for Peykan Tourism Platform.
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from core.models import BaseModel
import uuid


class Cart(BaseModel):
    """
    Shopping cart for users.
    """
    
    # Cart identification
    session_id = models.CharField(
        max_length=40, 
        unique=True,
        verbose_name=_('Session ID')
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='carts',
        null=True, 
        blank=True,
        verbose_name=_('User')
    )
    
    # Cart details
    currency = models.CharField(
        max_length=3, 
        default='USD',
        verbose_name=_('Currency')
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    expires_at = models.DateTimeField(verbose_name=_('Expires at'))
    
    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cart {self.session_id}"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return self.items.count()
    
    @property
    def subtotal(self):
        """Calculate cart subtotal."""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total(self):
        """Calculate cart total with any fees."""
        return self.subtotal
    
    def is_expired(self):
        """Check if cart has expired."""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def clear_expired_items(self):
        """Remove expired items from cart."""
        from django.utils import timezone
        now = timezone.now()
        
        for item in self.items.all():
            if item.expires_at and now > item.expires_at:
                item.delete()


class CartItem(BaseModel):
    """
    Individual items in the shopping cart.
    """
    
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_('Cart')
    )
    
    # Product identification
    PRODUCT_TYPE_CHOICES = [
        ('tour', _('Tour')),
        ('event', _('Event')),
        ('transfer', _('Transfer')),
        ('car_rental', _('Car Rental')),
    ]
    product_type = models.CharField(
        max_length=20, 
        choices=PRODUCT_TYPE_CHOICES,
        verbose_name=_('Product type')
    )
    product_id = models.UUIDField(verbose_name=_('Product ID'))
    
    # Booking details
    booking_date = models.DateField(verbose_name=_('Booking date'))
    booking_time = models.TimeField(verbose_name=_('Booking time'))
    
    # Car rental specific fields
    pickup_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('Pickup date')
    )
    dropoff_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('Dropoff date')
    )
    pickup_time = models.TimeField(
        null=True, 
        blank=True,
        verbose_name=_('Pickup time')
    )
    dropoff_time = models.TimeField(
        null=True, 
        blank=True,
        verbose_name=_('Dropoff time')
    )
    
    # Location details
    pickup_location_type = models.CharField(
        max_length=20,
        choices=[
            ('predefined', _('Predefined Location')),
            ('custom', _('Custom Location')),
        ],
        default='predefined',
        verbose_name=_('Pickup location type')
    )
    pickup_location_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Pickup location ID')
    )
    pickup_location_custom = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Custom pickup location')
    )
    pickup_location_coordinates = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Pickup location coordinates')
    )
    
    dropoff_location_type = models.CharField(
        max_length=20,
        choices=[
            ('predefined', _('Predefined Location')),
            ('custom', _('Custom Location')),
            ('same_as_pickup', _('Same as Pickup')),
        ],
        default='same_as_pickup',
        verbose_name=_('Dropoff location type')
    )
    dropoff_location_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Dropoff location ID')
    )
    dropoff_location_custom = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Custom dropoff location')
    )
    dropoff_location_coordinates = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Dropoff location coordinates')
    )
    
    # Variant/Options
    variant_id = models.CharField(
        max_length=100,
        null=True, 
        blank=True,
        verbose_name=_('Variant ID')
    )
    variant_name = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Variant name')
    )
    
    # Quantity and pricing
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Unit price')
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Total price')
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    
    # Options
    selected_options = models.JSONField(
        default=list,
        verbose_name=_('Selected options')
    )
    options_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Options total')
    )
    
    # Booking specific data
    booking_data = models.JSONField(
        default=dict,
        verbose_name=_('Booking data')
    )
    
    # Reservation
    is_reserved = models.BooleanField(default=False, verbose_name=_('Is reserved'))
    reservation_expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_('Reservation expires at')
    )
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.cart} - {self.product_type} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Check if total_price should be manually overridden (for tours with complex pricing)
        skip_price_calculation = kwargs.pop('skip_price_calculation', False)

        # Always recalculate options_total from selected_options
        from decimal import Decimal
        options_total = Decimal('0.00')
        if self.selected_options:
            for option in self.selected_options:
                # Handle both string (option ID) and dict (option data) formats
                if isinstance(option, str):
                    # If option is just an ID string, skip price calculation
                    # The price should be calculated elsewhere
                    continue
                elif isinstance(option, dict):
                    # Use final_price if available (for car rentals), otherwise use price
                    option_price_raw = option.get('final_price') or option.get('price')
                    if option_price_raw is None or option_price_raw == '':
                        option_price = Decimal('0.00')
                    else:
                        try:
                            option_price = Decimal(str(option_price_raw))
                        except (ValueError, TypeError):
                            option_price = Decimal('0.00')
                    option_quantity = int(option.get('quantity', 1))
                    options_total += option_price * option_quantity
        self.options_total = options_total

        # Only recalculate total_price when not explicitly skipping
        if not skip_price_calculation:
            # Base calculation
            unit_price_decimal = Decimal(str(self.unit_price))
            quantity_decimal = Decimal(str(self.quantity))
            self.total_price = (unit_price_decimal * quantity_decimal) + options_total

            # For tours, calculate price based on participants if available
            if self.product_type == 'tour' and self.booking_data.get('participants'):
                try:
                    from tours.models import Tour, TourVariant, TourPricing
                    tour = Tour.objects.get(id=self.product_id)
                    variant = TourVariant.objects.get(id=self.variant_id, tour=tour)
                    participants = self.booking_data.get('participants', {})
                    tour_total = Decimal('0.00')
                    total_participants = 0
                    for age_group, count in participants.items():
                        if count > 0:
                            total_participants += count
                            try:
                                pricing = TourPricing.objects.get(
                                    tour=tour,
                                    variant=variant,
                                    age_group=age_group
                                )
                                # Use pricing.final_price (respects is_free flag)
                                if pricing.is_free:
                                    subtotal = Decimal('0.00')
                                else:
                                    subtotal = Decimal(str(pricing.final_price)) * count
                                tour_total += subtotal
                            except TourPricing.DoesNotExist:
                                # Fallback to variant base_price for missing age groups
                                # Infants are free by default in fallback
                                if age_group == 'infant':
                                    subtotal = Decimal('0.00')
                                else:
                                    subtotal = Decimal(str(variant.base_price)) * count
                                tour_total += subtotal
                    # Update quantity to match total participants
                    self.quantity = total_participants
                    self.unit_price = variant.base_price
                    self.total_price = tour_total + options_total

                except (Tour.DoesNotExist, TourVariant.DoesNotExist):
                    # Fallback to simple calculation
                    unit_price_decimal = Decimal(str(self.unit_price))
                    quantity_decimal = Decimal(str(self.quantity))
                    self.total_price = (unit_price_decimal * quantity_decimal) + options_total

            # For transfers, calculate price based on passenger count and store detailed booking info
            elif self.product_type == 'transfer' and self.booking_data:
                try:
                    from transfers.models import TransferRoutePricing, TransferOption
                    pricing = TransferRoutePricing.objects.get(
                        route_id=self.product_id,
                        vehicle_type=self.variant_id  # vehicle_type is stored in variant_id
                    )

                    # Get passenger count from booking_data
                    passenger_count = int(self.booking_data.get('passenger_count', 1))
                    luggage_count = int(self.booking_data.get('luggage_count', 0))

                    # Calculate options total for transfers
                    transfer_options_total = Decimal('0.00')
                    if self.selected_options:
                        for option in self.selected_options:
                            if isinstance(option, dict) and 'id' in option:
                                try:
                                    transfer_option = TransferOption.objects.get(id=option['id'])
                                    quantity = int(option.get('quantity', 1))
                                    transfer_options_total += transfer_option.price * quantity
                                except TransferOption.DoesNotExist:
                                    continue
                    
                    # Transfer price is per vehicle, not per passenger
                    transfer_total = Decimal(str(pricing.base_price))

                    # Update quantity to 1 (per vehicle)
                    self.quantity = 1
                    self.unit_price = pricing.base_price
                    self.total_price = transfer_total + transfer_options_total
                    self.options_total = transfer_options_total

                    # Store comprehensive transfer booking information in booking_data
                    detailed_booking_data = self.booking_data.copy()

                    # Basic vehicle and capacity info
                    detailed_booking_data.update({
                        'vehicle_type': self.variant_id,
                        'vehicle_name': pricing.vehicle_name,
                        'max_passengers': pricing.max_passengers,
                        'max_luggage': pricing.max_luggage or 0,
                        'luggage_count': luggage_count,
                        'base_price': str(pricing.base_price),
                        'currency': pricing.currency,
                        'estimated_duration': pricing.route.estimated_duration_minutes if hasattr(pricing, 'route') else 45,
                        'route_origin': pricing.route.origin if hasattr(pricing, 'route') else '',
                        'route_destination': pricing.route.destination if hasattr(pricing, 'route') else '',
                        # Store pricing metadata for detailed breakdown
                        'pricing_metadata': pricing.pricing_metadata or {},
                        'calculated_total': str(transfer_total + transfer_options_total),
                        'options_total': str(transfer_options_total),
                        'selected_options': self.selected_options
                    })

                    # Add route information
                    if hasattr(pricing, 'route'):
                        detailed_booking_data.update({
                            'route_name': pricing.route.name or '',
                            'peak_hour_surcharge': str(pricing.route.peak_hour_surcharge) if hasattr(pricing.route, 'peak_hour_surcharge') else '0.00',
                            'midnight_surcharge': str(pricing.route.midnight_surcharge) if hasattr(pricing.route, 'midnight_surcharge') else '0.00',
                            'round_trip_discount_percentage': str(pricing.route.round_trip_discount_percentage) if hasattr(pricing.route, 'round_trip_discount_percentage') else '0.00',
                        })

                    # Add trip details from booking_data
                    trip_details = {
                        'trip_type': self.booking_data.get('trip_type', 'one_way'),
                        'outbound_date': self.booking_data.get('outbound_date', ''),
                        'outbound_time': self.booking_data.get('outbound_time', ''),
                        'return_date': self.booking_data.get('return_date', ''),
                        'return_time': self.booking_data.get('return_time', ''),
                        'pickup_address': self.booking_data.get('pickup_address', ''),
                        'dropoff_address': self.booking_data.get('dropoff_address', ''),
                        'pickup_instructions': self.booking_data.get('pickup_instructions', ''),
                        'dropoff_instructions': self.booking_data.get('dropoff_instructions', ''),
                        'contact_name': self.booking_data.get('contact_name', ''),
                        'contact_phone': self.booking_data.get('contact_phone', ''),
                        'special_requirements': self.booking_data.get('special_requirements', ''),
                    }

                    # Add pricing breakdown information
                    pricing_breakdown = {
                        'outbound_price': self.booking_data.get('outbound_price', str(transfer_total)),
                        'return_price': self.booking_data.get('return_price', '0.00'),
                        'round_trip_discount': self.booking_data.get('round_trip_discount', '0.00'),
                        'options_total': str(transfer_options_total),
                        'final_price': str(transfer_total + transfer_options_total),
                        'surcharges': self.booking_data.get('surcharges', {}),
                        'discounts': self.booking_data.get('discounts', {}),
                    }

                    detailed_booking_data.update(trip_details)
                    detailed_booking_data.update(pricing_breakdown)

                    # Update booking_data with comprehensive information
                    self.booking_data = detailed_booking_data

                except TransferRoutePricing.DoesNotExist:
                    # Fallback to unit_price * quantity
                    unit_price_decimal = Decimal(str(self.unit_price))
                    quantity_decimal = Decimal(str(self.quantity))
                    self.total_price = (unit_price_decimal * quantity_decimal) + options_total
            
            # For car rentals, include insurance in total price calculation
            elif self.product_type == 'car_rental' and self.booking_data:
                try:
                    # Get insurance total from booking_data
                    insurance_total = Decimal(str(self.booking_data.get('insurance_total', '0.00')))
                    unit_price_decimal = Decimal(str(self.unit_price))
                    quantity_decimal = Decimal(str(self.quantity))

                    # Calculate the correct total including insurance
                    calculated_total = (unit_price_decimal * quantity_decimal) + options_total + insurance_total

                    # For car rentals, always ensure total_price includes insurance
                    # Override the stored value if it's different from the calculated value
                    if self.total_price != calculated_total:
                        self.total_price = calculated_total
                except (ValueError, TypeError):
                    # Fallback to basic calculation if insurance_total is invalid
                    unit_price_decimal = Decimal(str(self.unit_price))
                    quantity_decimal = Decimal(str(self.quantity))
                    calculated_total = (unit_price_decimal * quantity_decimal) + options_total

                    # Only update total_price if it's different from calculated value
                    if self.total_price != calculated_total:
                        self.total_price = calculated_total
        super().save(*args, **kwargs)
    
    @property
    def grand_total(self):
        """Calculate grand total including options."""
        return self.total_price

    @property
    def capacity_quantity(self):
        """Calculate quantity for capacity purposes (excluding infants)."""
        if not self.booking_data or 'participants' not in self.booking_data:
            return self.quantity

        participants = self.booking_data.get('participants', {})
        # Only count adults and children for capacity (infants are free and don't occupy space)
        adult_count = participants.get('adult', 0)
        child_count = participants.get('child', 0)
        return adult_count + child_count

    @property
    def total_participants(self):
        """Total number of participants including infants."""
        if not self.booking_data or 'participants' not in self.booking_data:
            return self.quantity

        participants = self.booking_data.get('participants', {})
        return (participants.get('adult', 0) +
                participants.get('child', 0) +
                participants.get('infant', 0))
    
    def is_reservation_expired(self):
        """Check if reservation has expired."""
        if not self.is_reserved or not self.reservation_expires_at:
            return False
        
        from django.utils import timezone
        return timezone.now() > self.reservation_expires_at
    
    def create_reservation(self, duration_minutes=30):
        """Create a temporary reservation."""
        from django.utils import timezone
        from datetime import timedelta
        
        self.is_reserved = True
        self.reservation_expires_at = timezone.now() + timedelta(minutes=duration_minutes)
        self.save()
        
        # Update product availability
        self._update_product_availability(reserve=True)
    
    def release_reservation(self):
        """Release the temporary reservation."""
        if self.is_reserved:
            self.is_reserved = False
            self.reservation_expires_at = None
            self.save()
            
            # Update product availability
            self._update_product_availability(reserve=False)
    
    def _update_product_availability(self, reserve=True):
        """Update product availability when reserving/releasing."""
        # This method is now disabled - we use TourCapacityService instead
        pass


class CartService:
    """
    Service class for cart operations.
    """
    
    @staticmethod
    def get_or_create_cart(session_id, user=None):
        """Get existing cart or create new one with proper user/session logic."""
        from django.utils import timezone
        from datetime import timedelta
        import time
        
        # For authenticated users, prioritize user-based cart
        if user and user.is_authenticated:
            # First, try to get existing user cart
            user_cart = Cart.objects.filter(user=user, is_active=True).first()
            
            if user_cart:
                # User has an existing cart, return it
                return user_cart
            
            # Check if there's a session cart that should be migrated
            session_cart = Cart.objects.filter(session_id=session_id, user__isnull=True, is_active=True).first()
            
            if session_cart:
                # Don't migrate automatically - let merge_cart_view handle it
                # But don't return the session cart - create a new user cart instead
                # This ensures proper separation between guest and user carts
                pass
            
            # Create new user cart with unique session_id
            # Check if session_id already exists for another user
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    existing_cart = Cart.objects.filter(session_id=session_id).first()
                    if existing_cart:
                        # Generate unique session_id
                        unique_session_id = f"{session_id}_{uuid.uuid4().hex[:8]}"
                    else:
                        unique_session_id = session_id
                    
                    cart = Cart.objects.create(
                        session_id=unique_session_id,
                        user=user,
                        expires_at=timezone.now() + timedelta(hours=24),
                    )
                    return cart
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Cart creation attempt {attempt + 1} failed: {e}")
                        time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        raise e
        
        else:
            # For guest users, use session-based cart
            try:
                cart, created = Cart.objects.get_or_create(
                    session_id=session_id,
                    user__isnull=True,
                    is_active=True,
                    defaults={
                        'expires_at': timezone.now() + timedelta(hours=24),
                    }
                )

                # If cart was found but has a user (shouldn't happen), create new one
                if not created and cart.user:
                    cart = Cart.objects.create(
                        session_id=f"{session_id}_{uuid.uuid4().hex[:8]}",
                        expires_at=timezone.now() + timedelta(hours=24),
                    )
            except Exception as e:
                # If get_or_create fails due to unique constraint, try to get existing cart
                try:
                    cart = Cart.objects.get(
                        session_id=session_id,
                        user__isnull=True,
                        is_active=True
                    )
                    created = False
                except Cart.DoesNotExist:
                    # Create new cart with unique session_id
                    cart = Cart.objects.create(
                        session_id=f"{session_id}_{uuid.uuid4().hex[:8]}",
                        expires_at=timezone.now() + timedelta(hours=24),
                    )
                    created = True
            
            return cart
    
    @staticmethod
    def migrate_session_cart_to_user(session_id, user):
        """Migrate session cart to user cart."""
        try:
            session_cart = Cart.objects.get(session_id=session_id, user__isnull=True, is_active=True)
            user_cart = Cart.objects.filter(user=user, is_active=True).first()
            
            if user_cart:
                # Merge session cart items into user cart
                for item in session_cart.items.all():
                    existing_item = user_cart.items.filter(
                        product_type=item.product_type,
                        product_id=item.product_id,
                        variant_id=item.variant_id
                    ).first()
                    
                    if existing_item:
                        # Update quantity
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        # Move item to user cart
                        item.cart = user_cart
                        item.save()
                
                # Delete session cart
                session_cart.delete()
                return user_cart
            else:
                # No user cart exists, migrate session cart
                session_cart.user = user
                session_cart.save()
                return session_cart
                
        except Cart.DoesNotExist:
            # No session cart to migrate
            return None
    
    @staticmethod
    def get_session_id(request):
        """Get consistent session ID for the request."""
        # Handle both DRF request (has .session) and Django request
        if hasattr(request, 'session'):
            # Ensure session is created
            if not request.session.session_key:
                request.session.create()
            
            # Always use the base session key for cart operations
            # This ensures guest carts can be found and merged after login
            session_id = request.session.session_key
        else:
            # For Django WSGIRequest without session middleware, use a consistent default
            # This ensures cart operations work consistently in tests
            session_id = "test_session_default"
        
        return session_id
    
    @staticmethod
    def add_to_cart(cart, product_data):
        """Add item to cart with reservation."""
        # Check if item already exists
        existing_item = cart.items.filter(
            product_type=product_data['product_type'],
            product_id=product_data['product_id'],
            booking_date=product_data['booking_date'],
            booking_time=product_data['booking_time'],
            variant_id=product_data.get('variant_id')
        ).first()
        
        if existing_item:
            # Update existing item
            existing_item.quantity += product_data.get('quantity', 1)
            existing_item.selected_options = product_data.get('selected_options', []) if isinstance(product_data.get('selected_options', []), list) else []
            existing_item.booking_data = product_data.get('booking_data', {})
            existing_item.save()
            
            # Extend reservation
            existing_item.create_reservation()
            return existing_item
        
        else:
            # Create new item
            item = CartItem.objects.create(
                cart=cart,
                product_type=product_data['product_type'],
                product_id=product_data['product_id'],
                booking_date=product_data['booking_date'],
                booking_time=product_data['booking_time'],
                variant_id=product_data.get('variant_id'),
                variant_name=product_data.get('variant_name', ''),
                quantity=product_data.get('quantity', 1),
                unit_price=product_data['unit_price'],
                selected_options=product_data.get('selected_options', []) if isinstance(product_data.get('selected_options', []), list) else [],
                options_total=product_data.get('options_total', 0),
                booking_data=product_data.get('booking_data', {}),
            )
            
            # Create reservation
            item.create_reservation()
            return item
    
    @staticmethod
    def remove_from_cart(cart, item_id):
        """Remove item from cart and release reservation."""
        try:
            item = cart.items.get(id=item_id)
            item.release_reservation()
            item.delete()
            return True
        except CartItem.DoesNotExist:
            return False
    
    @staticmethod
    def update_cart_item(cart, item_id, quantity=None, options=None):
        """Update cart item quantity or options."""
        try:
            item = cart.items.get(id=item_id)
            
            if quantity is not None:
                item.quantity = quantity
            
            if options is not None:
                item.selected_options = options
            
            item.save()
            return item
        except CartItem.DoesNotExist:
            return None
    
    @staticmethod
    def clear_cart(cart):
        """Clear all items from cart."""
        # Get all items first
        items = list(cart.items.all())
        
        # Release reservations for each item
        for item in items:
            try:
                item.release_reservation()
            except Exception as e:
                print(f"Error releasing reservation for item {item.id}: {e}")
        
        # Delete all items
        cart.items.all().delete()
        
        # Verify cart is empty
        remaining_items = cart.items.count()
        if remaining_items > 0:
            print(f"Warning: {remaining_items} items still remain in cart after clear_cart")
    
    @staticmethod
    def get_cart_summary(cart):
        """Get cart summary with totals."""
        items = cart.items.all()
        
        summary = {
            'total_items': len(items),
            'subtotal': sum(item.total_price for item in items),
            'currency': cart.currency,
            'items': []
        }
        
        for item in items:
            summary['items'].append({
                'id': str(item.id),
                'product_type': item.product_type,
                'product_id': str(item.product_id),
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price),
                'variant_name': item.variant_name,
                'booking_date': item.booking_date.isoformat(),
                'booking_time': item.booking_time.isoformat(),
            })
        
        return summary

    @staticmethod
    def calculate_totals(cart, apply_fees=True, apply_taxes=True):
        """Calculate cart-level fees and taxes using platform policy.

        Policy (can be adjusted later):
        - Service fee: 3% of subtotal when apply_fees=True
        - VAT: 9% of (subtotal - discounts + fees) when apply_taxes=True
        """
        from decimal import Decimal as _D
        subtotal = _D(str(cart.subtotal or 0))
        discounts = _D('0.00')  # placeholder for future cart-level discounts
        service_fee_rate = _D('0.03')
        vat_rate = _D('0.09')
        fees_total = _D('0.00')
        if apply_fees:
            fees_total = (subtotal * service_fee_rate).quantize(_D('0.01'))
        tax_base = subtotal - discounts + fees_total
        tax_total = _D('0.00')
        if apply_taxes:
            tax_total = (tax_base * vat_rate).quantize(_D('0.01'))
        grand_total = (subtotal - discounts + fees_total + tax_total).quantize(_D('0.01'))
        return {
            'subtotal': float(subtotal),
            'discounts_total': float(discounts),
            'fees_total': float(fees_total),
            'tax_total': float(tax_total),
            'grand_total': float(grand_total),
            'currency': cart.currency,
        }
    
    @staticmethod
    def cleanup_expired_carts():
        """Clean up expired carts and reservations."""
        from django.utils import timezone
        
        # Clear expired carts
        expired_carts = Cart.objects.filter(expires_at__lt=timezone.now())
        for cart in expired_carts:
            cart.clear_expired_items()
        
        # Clear expired reservations
        expired_items = CartItem.objects.filter(
            is_reserved=True,
            reservation_expires_at__lt=timezone.now()
        )
        for item in expired_items:
            item.release_reservation() 