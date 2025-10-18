"""
Order models for Peykan Tourism Platform.
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from core.models import BaseModel


class Order(BaseModel):
    """
    Order model for completed bookings.
    """
    
    # Order identification
    order_number = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name=_('Order number')
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name=_('User')
    )
    agent = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        related_name='agent_orders',
        null=True, 
        blank=True,
        verbose_name=_('Agent')
    )
    
    # Order details
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('paid', _('Paid')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    
    # New fields for pending order system
    is_capacity_reserved = models.BooleanField(
        default=False,
        verbose_name=_('Is capacity reserved')
    )
    capacity_reserved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Capacity reserved at')
    )
    
    # Payment information
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Payment status')
    )
    payment_method = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_('Payment method')
    )
    
    # Pricing
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Subtotal')
    )
    service_fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Service fee amount')
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Tax amount')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Discount amount')
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Total amount')
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))

    # Agent commission
    agent_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Agent commission rate (%)')
    )
    agent_commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Agent commission amount')
    )
    commission_paid = models.BooleanField(default=False, verbose_name=_('Commission paid'))
    
    # Customer information
    customer_name = models.CharField(max_length=255, verbose_name=_('Customer name'))
    customer_email = models.EmailField(verbose_name=_('Customer email'))
    customer_phone = models.CharField(max_length=20, verbose_name=_('Customer phone'))
    
    # Billing information
    billing_address = models.TextField(default='', verbose_name=_('Billing address'))
    billing_city = models.CharField(max_length=100, default='', verbose_name=_('Billing city'))
    billing_country = models.CharField(max_length=100, default='', verbose_name=_('Billing country'))
    
    # Notes
    customer_notes = models.TextField(default='', verbose_name=_('Customer notes'))
    internal_notes = models.TextField(default='', verbose_name=_('Internal notes'))
    admin_notes = models.TextField(default='', verbose_name=_('Admin notes'))
    
    # Payment tracking
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Payment date'))
    payment_reference = models.CharField(max_length=100, default='', verbose_name=_('Payment reference/Transaction ID'))
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        # Generate order number if not provided
        if not self.order_number:
            import uuid
            self.order_number = f"ORD{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total
        self.total_amount = self.subtotal + self.service_fee_amount + self.tax_amount - self.discount_amount
        
        # Calculate agent commission
        if self.agent and self.agent_commission_rate > 0:
            self.agent_commission_amount = self.total_amount * (self.agent_commission_rate / 100)
        
        super().save(*args, **kwargs)
    
    @property
    def total_items(self):
        """Get total number of items in order."""
        return self.items.count()
    
    @property
    def is_paid(self):
        """Check if order is paid."""
        return self.payment_status == 'paid'
    
    @property
    def is_completed(self):
        """Check if order is completed."""
        return self.status == 'completed'
    
    @property
    def is_cancelled(self):
        """Check if order is cancelled."""
        return self.status == 'cancelled'
    
    @property
    def is_pending(self):
        """Check if order is pending."""
        return self.status == 'pending'
    
    def can_cancel(self):
        """Check if order can be cancelled."""
        return self.status in ['pending', 'confirmed'] and not self.is_paid
    
    def can_confirm(self):
        """Check if order can be confirmed."""
        return self.status == 'pending' and not self.is_capacity_reserved
    
    def cancel_order(self, reason=None):
        """Cancel the order."""
        if self.can_cancel():
            self.status = 'cancelled'
            if reason:
                self.internal_notes += f"\nCancelled: {reason}"
            
            # Release capacity if it was reserved
            if self.is_capacity_reserved:
                self.release_capacity()
            
            self.save()
            return True
        return False
    
    def confirm_order(self):
        """Confirm the order and reduce capacity."""
        if not self.can_confirm():
            return False, "Order cannot be confirmed"
        
        try:
            with transaction.atomic():
                # Check capacity availability
                capacity_available, error = self.check_capacity_availability()
                if not capacity_available:
                    return False, error
                
                # Confirm capacity for each item (this reduces actual capacity)
                for item in self.items.all():
                    if item.product_type == 'tour':
                        schedule_id = item.booking_data.get('schedule_id')
                        variant_id = str(item.variant_id) if item.variant_id else None
                        
                        if schedule_id:
                            # Calculate quantity for capacity (adults + children only)
                            participants = item.booking_data.get('participants', {}) or {}
                            adult_count = int(participants.get('adult', 0))
                            child_count = int(participants.get('child', 0))
                            qty_for_capacity = adult_count + child_count
                            
                            if qty_for_capacity > 0:
                                from tours.services import TourCapacityService
                                success, error = TourCapacityService.confirm_capacity(
                                    schedule_id, variant_id, qty_for_capacity
                                )
                                if not success:
                                    return False, f"Capacity confirmation failed: {error}"
                
                # Update status
                self.status = 'confirmed'
                self.is_capacity_reserved = True
                self.capacity_reserved_at = timezone.now()
                self.save()
                
                return True, "Order confirmed successfully"
                
        except Exception as e:
            return False, f"Confirmation failed: {str(e)}"
    
    def mark_as_paid(self):
        """Mark order as paid and confirm capacity (reduce actual capacity)."""
        if self.status != 'pending':
            return False, "Order must be pending to mark as paid"
        
        try:
            with transaction.atomic():
                # Check capacity availability
                capacity_available, error = self.check_capacity_availability()
                if not capacity_available:
                    return False, error
                
                # Confirm capacity for each item (this reduces actual capacity)
                for item in self.items.all():
                    if item.product_type == 'tour':
                        schedule_id = item.booking_data.get('schedule_id')
                        variant_id = str(item.variant_id) if item.variant_id else None
                        
                        if schedule_id:
                            # Calculate quantity for capacity (adults + children only)
                            participants = item.booking_data.get('participants', {}) or {}
                            adult_count = int(participants.get('adult', 0))
                            child_count = int(participants.get('child', 0))
                            qty_for_capacity = adult_count + child_count
                            
                            if qty_for_capacity > 0:
                                from tours.services import TourCapacityService
                                success, error = TourCapacityService.confirm_capacity(
                                    schedule_id, variant_id, qty_for_capacity
                                )
                                if not success:
                                    return False, f"Capacity confirmation failed: {error}"
                
                # Update status
                self.status = 'paid'
                self.is_capacity_reserved = True
                self.capacity_reserved_at = timezone.now()
                self.save()
                
                return True, "Order marked as paid successfully"
                
        except Exception as e:
            return False, f"Payment marking failed: {str(e)}"
    
    def check_capacity_availability(self):
        """Check if capacity is available for all items."""
        for item in self.items.all():
            if item.product_type == 'tour':
                available, error = item.check_tour_capacity()
                if not available:
                    return False, error
            elif item.product_type == 'event':
                available, error = item.check_event_capacity()
                if not available:
                    return False, error
        
        return True, None
    
    def reserve_capacity(self):
        """Reserve capacity for all items."""
        for item in self.items.all():
            if item.product_type == 'tour':
                item.reserve_tour_capacity()
            elif item.product_type == 'event':
                item.reserve_event_capacity()
    
    def release_capacity(self):
        """Release capacity for all items."""
        for item in self.items.all():
            if item.product_type == 'tour':
                item.release_tour_capacity()
            elif item.product_type == 'event':
                item.release_event_capacity()
    
    @classmethod
    def get_pending_count_for_user(cls, user):
        """Get count of pending orders for a user."""
        return cls.objects.filter(user=user, status='pending').count()
    
    @classmethod
    def has_duplicate_pending(cls, user, product_type, product_id, booking_date):
        """Check if user has duplicate pending order."""
        return cls.objects.filter(
            user=user,
            status='pending',
            items__product_type=product_type,
            items__product_id=product_id,
            items__booking_date=booking_date
        ).exists()


class OrderItem(BaseModel):
    """
    Individual items in an order.
    """
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_('Order')
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
    product_title = models.CharField(max_length=255, verbose_name=_('Product title'))
    product_slug = models.CharField(max_length=255, verbose_name=_('Product slug'))
    
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
    variant_id = models.UUIDField(
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
    
    # Status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product_title}"
    
    def save(self, *args, **kwargs):
        # Fix variant_id if it's None but variant_name exists
        if self.variant_id is None and self.variant_name and self.product_id:
            try:
                from tours.models import TourVariant
                variant = TourVariant.objects.get(
                    name=self.variant_name,
                    tour_id=self.product_id
                )
                self.variant_id = variant.id
                print(f"Fixed variant_id for OrderItem {self.id}: {self.variant_id}")
            except TourVariant.DoesNotExist:
                print(f"Warning: Could not find variant '{self.variant_name}' for product {self.product_id}")

        # Always recalculate options_total from selected_options
        from decimal import Decimal
        options_total = Decimal('0.00')
        if self.selected_options:
            for option in self.selected_options:
                if isinstance(option, dict):
                    option_price_raw = option.get('price')
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

        # Calculate total price
        if self.product_type == 'car_rental' and self.booking_data:
            # For car rentals, ensure insurance is included in total_price
            try:
                # Get insurance total from booking_data
                insurance_total = Decimal(str(self.booking_data.get('insurance_total', '0.00')))
                unit_price_decimal = Decimal(str(self.unit_price))
                quantity_decimal = Decimal(str(self.quantity))
                calculated_total = (unit_price_decimal * quantity_decimal) + self.options_total + insurance_total

                # Update total_price to include insurance
                if self.total_price != calculated_total:
                    self.total_price = calculated_total
            except (ValueError, TypeError):
                # Fallback to basic calculation if insurance_total is invalid
                unit_price_decimal = Decimal(str(self.unit_price))
                quantity_decimal = Decimal(str(self.quantity))
                calculated_total = (unit_price_decimal * quantity_decimal) + self.options_total
                self.total_price = calculated_total

        elif self.product_type == 'tour' and self.booking_data:
            # For tours, calculate price based on participants and TourPricing
            try:
                from tours.models import Tour, TourVariant, TourPricing
                tour = Tour.objects.get(id=self.product_id)
                variant = TourVariant.objects.get(id=self.variant_id, tour=tour)
                participants = self.booking_data.get('participants', {}) or {}
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
                self.total_price = tour_total + self.options_total

            except (Tour.DoesNotExist, TourVariant.DoesNotExist):
                # Fallback to simple calculation based on participants
                participants = self.booking_data.get('participants', {}) or {}
                adult_count = int(participants.get('adult', 0))
                child_count = int(participants.get('child', 0))
                infant_count = int(participants.get('infant', 0))

                adult_price = Decimal(str(self.unit_price))
                child_price = adult_price * Decimal('0.7')  # Child price is 70% of adult
                infant_price = Decimal('0.00')  # Infant is free

                participants_total = (adult_price * adult_count) + (child_price * child_count) + (infant_price * infant_count)
                self.total_price = participants_total + self.options_total

        elif self.product_type == 'transfer' and self.booking_data:
            # For transfers, calculate price based on transfer pricing and store detailed info
            try:
                from transfers.models import TransferRoutePricing
                pricing = TransferRoutePricing.objects.get(
                    route_id=self.product_id,
                    vehicle_type=self.variant_id  # vehicle_type is stored in variant_id
                )

                # Get passenger count from booking_data
                passenger_count = int(self.booking_data.get('passenger_count', 1))
                luggage_count = int(self.booking_data.get('luggage_count', 0))

                # Calculate comprehensive transfer pricing including surcharges
                booking_time = self.booking_time
                hour = booking_time.hour if booking_time else None
                is_round_trip = self.booking_data.get('trip_type') == 'round_trip'
                return_time = self.booking_data.get('return_time')
                return_hour = None
                if return_time and isinstance(return_time, str):
                    try:
                        from datetime import datetime
                        return_hour = datetime.strptime(return_time, '%H:%M').hour
                    except:
                        pass

                # Use the pricing service to calculate comprehensive price
                price_data = pricing._calculate_transfer_price(
                    hour=hour,
                    return_hour=return_hour,
                    is_round_trip=is_round_trip,
                    selected_options=self.selected_options
                )

                # Calculate total for all passengers
                base_price_per_passenger = Decimal(str(price_data['base_price']))
                outbound_surcharge_per_passenger = Decimal(str(price_data['outbound_surcharge']))
                return_surcharge_per_passenger = Decimal(str(price_data['return_surcharge']))
                round_trip_discount_total = Decimal(str(price_data['round_trip_discount']))
                
                # Total price per passenger (base + surcharges)
                price_per_passenger = base_price_per_passenger + outbound_surcharge_per_passenger + return_surcharge_per_passenger
                
                # Total for all passengers
                transfer_total = price_per_passenger * passenger_count
                
                # Apply round trip discount (already calculated for total, not per passenger)
                transfer_total -= round_trip_discount_total

                # Update quantity to match passenger count
                self.quantity = passenger_count
                self.unit_price = price_per_passenger
                self.total_price = transfer_total + self.options_total

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
                    # Store comprehensive pricing breakdown
                    'pricing_breakdown': {
                        'base_price': str(base_price_per_passenger),
                        'outbound_surcharge': str(outbound_surcharge_per_passenger),
                        'return_surcharge': str(return_surcharge_per_passenger),
                        'round_trip_discount': str(round_trip_discount_total),
                        'price_per_passenger': str(price_per_passenger),
                        'transfer_total': str(transfer_total),
                        'options_total': str(self.options_total),
                        'final_total': str(transfer_total + self.options_total)
                    },
                    'calculated_total': str(transfer_total + self.options_total)
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
                    'options_total': str(self.options_total),
                    'final_price': str(transfer_total + self.options_total),
                    'surcharges': self.booking_data.get('surcharges', {}),
                    'discounts': self.booking_data.get('discounts', {}),
                }

                detailed_booking_data.update(trip_details)
                detailed_booking_data.update(pricing_breakdown)

                # Update booking_data with comprehensive information
                self.booking_data = detailed_booking_data

            except TransferRoutePricing.DoesNotExist:
                # Fallback to unit_price * quantity
                self.total_price = (self.unit_price * self.quantity) + self.options_total
        else:
            # Default calculation for other product types
            self.total_price = (self.unit_price * self.quantity) + self.options_total

        super().save(*args, **kwargs)
    
    @property
    def grand_total(self):
        """Calculate grand total including options."""
        return self.total_price
    
    def check_tour_capacity(self):
        """Check if tour capacity is available."""
        try:
            if self.product_type == 'tour':
                from tours.services import TourCapacityService
                schedule_id = self.booking_data.get('schedule_id')
                variant_id = str(self.variant_id) if self.variant_id else None
                
                if schedule_id:
                    # Calculate quantity for capacity (adults + children only)
                    participants = self.booking_data.get('participants', {}) or {}
                    adult_count = int(participants.get('adult', 0))
                    child_count = int(participants.get('child', 0))
                    qty_for_capacity = adult_count + child_count
                    
                    if qty_for_capacity > 0:
                        available = TourCapacityService.get_available_capacity(schedule_id, variant_id)
                        if available < qty_for_capacity:
                            return False, f"Insufficient capacity. Available: {available}, Required: {qty_for_capacity}"
                
                return True, None
            return True, None
        except Exception as e:
            return False, f"Capacity check failed: {str(e)}"
    
    def check_event_capacity(self):
        """Check if event capacity is available."""
        try:
            if self.product_type == 'event':
                schedule_id = self.booking_data.get('schedule_id')
                if schedule_id:
                    from events.models import EventPerformance as EventSchedule
                    schedule = EventSchedule.objects.get(id=schedule_id)
                    if schedule.current_capacity < self.quantity:
                        return False, f"Insufficient capacity. Available: {schedule.current_capacity}, Required: {self.quantity}"
                return True, None
            return True, None
        except Exception as e:
            return False, f"Event capacity check failed: {str(e)}"
    
    def reserve_tour_capacity(self):
        """Reserve tour capacity."""
        try:
            if self.product_type == 'tour':
                from tours.services import TourCapacityService
                schedule_id = self.booking_data.get('schedule_id')
                variant_id = str(self.variant_id) if self.variant_id else None
                
                if schedule_id:
                    # Calculate quantity for capacity (adults + children only)
                    participants = self.booking_data.get('participants', {}) or {}
                    adult_count = int(participants.get('adult', 0))
                    child_count = int(participants.get('child', 0))
                    qty_for_capacity = adult_count + child_count
                    
                    if qty_for_capacity > 0:
                        success, error = TourCapacityService.reserve_capacity(
                            schedule_id, variant_id, qty_for_capacity
                        )
                        if not success:
                            raise ValueError(f"Capacity reservation failed: {error}")
        except Exception as e:
            raise ValueError(f"Tour capacity reservation failed: {str(e)}")
    
    def reserve_event_capacity(self):
        """Reserve event capacity."""
        try:
            if self.product_type == 'event':
                schedule_id = self.booking_data.get('schedule_id')
                if schedule_id:
                    from events.models import EventPerformance as EventSchedule
                    schedule = EventSchedule.objects.select_for_update().get(id=schedule_id)
                    if schedule.current_capacity < self.quantity:
                        raise ValueError("Insufficient capacity for event")
                    
                    schedule.current_capacity -= self.quantity
                    schedule.save()
        except Exception as e:
            raise ValueError(f"Event capacity reservation failed: {str(e)}")
    
    def release_tour_capacity(self):
        """Release tour capacity."""
        try:
            if self.product_type == 'tour':
                from tours.services import TourCapacityService
                schedule_id = self.booking_data.get('schedule_id')
                variant_id = str(self.variant_id) if self.variant_id else None
                
                if schedule_id:
                    # Calculate quantity for capacity (adults + children only)
                    participants = self.booking_data.get('participants', {}) or {}
                    adult_count = int(participants.get('adult', 0))
                    child_count = int(participants.get('child', 0))
                    qty_for_capacity = adult_count + child_count
                    
                    if qty_for_capacity > 0:
                        TourCapacityService.release_capacity(schedule_id, variant_id, qty_for_capacity)
        except Exception as e:
            print(f"Error releasing tour capacity: {e}")
    
    def release_event_capacity(self):
        """Release event capacity."""
        try:
            if self.product_type == 'event':
                schedule_id = self.booking_data.get('schedule_id')
                if schedule_id:
                    from events.models import EventPerformance as EventSchedule
                    schedule = EventSchedule.objects.select_for_update().get(id=schedule_id)
                    schedule.current_capacity += self.quantity
                    schedule.save()
        except Exception as e:
            print(f"Error releasing event capacity: {e}")
    
    def release_inventory(self):
        """Release inventory when order is cancelled."""
        try:
            if self.product_type == 'tour':
                from tours.models import TourSchedule
                schedule = TourSchedule.objects.get(id=self.booking_data.get('schedule_id'))
                schedule.release_capacity(self.quantity)
            
            elif self.product_type == 'event':
                from events.models import EventPerformance
                performance = EventPerformance.objects.get(id=self.booking_data.get('performance_id'))
                performance.release_capacity(self.quantity)
            
            # Remove all usages of TransferSchedule
        
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Error releasing inventory: {e}")


class OrderHistory(BaseModel):
    """
    Order status history for tracking changes.
    """
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='history',
        verbose_name=_('Order')
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('User')
    )
    
    # Change details
    field_name = models.CharField(max_length=100, verbose_name=_('Field name'))
    old_value = models.TextField(blank=True, verbose_name=_('Old value'))
    new_value = models.TextField(blank=True, verbose_name=_('New value'))
    change_reason = models.TextField(blank=True, verbose_name=_('Change reason'))
    
    class Meta:
        verbose_name = _('Order History')
        verbose_name_plural = _('Order History')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.field_name}"


class OrderService:
    """
    Service class for order operations.
    """
    
    @staticmethod
    def create_order_from_cart(cart, user, payment_data=None, agent=None):
        """Create order from cart items with transaction safety."""
        from decimal import Decimal
        from django.db import transaction
        from tours.models import TourSchedule
        from .services import OrderFieldMapper, OrderItemFieldMapper
        # Remove: from transfers.models import TransferSchedule
        
        with transaction.atomic():
            # Check cart limits before creating order
            from core.models import SystemSettings
            settings = SystemSettings.get_settings()
            
            # Check item count limit
            cart_items_count = cart.items.count()
            if cart_items_count > settings.cart_max_items_user:
                raise ValueError(f"Cart exceeds maximum {settings.cart_max_items_user} items limit.")
            
            # Check total amount limit
            cart_total = sum(Decimal(str(item.total_price)) for item in cart.items.all() if item.total_price)
            if cart_total > settings.cart_max_total_user:
                raise ValueError(f"Cart exceeds maximum ${settings.cart_max_total_user} total limit.")
            
            # Map order fields properly
            order_data = OrderFieldMapper.map_order_fields_from_cart(cart, user, payment_data)
            
            # Override agent if provided
            if agent:
                order_data['agent'] = agent
                order_data['agent_commission_rate'] = agent.commission_rate
            
            # Create order
            order = Order.objects.create(**order_data)
            
            # Create order items (NO capacity update - only on status change)
            for cart_item in cart.items.all():
                # Validate capacity for transfers before creating order item
                if cart_item.product_type == 'transfer':
                    OrderService._validate_transfer_capacity(cart_item)
                
                # Map order item fields properly
                item_data = OrderItemFieldMapper.map_order_item_fields_from_cart_item(cart_item, order)

                order_item = OrderItem.objects.create(**item_data)
            
            # If order is created with confirmed status, update capacity accordingly
            if order.status == 'confirmed':
                OrderService._update_capacity_for_order_status_change(order, 'pending', 'confirmed')
            
            # Set agent commission if applicable
            if agent and agent.is_agent:
                order.agent_commission_rate = agent.commission_rate
                order.save()
            
            # Clear cart
            from cart.models import CartService
            CartService.clear_cart(cart)
            
            return order
    
    @staticmethod
    def _update_capacity(cart_item):
        """Update capacity with proper locking to prevent overbooking."""
        try:
            if cart_item.product_type == 'tour':
                from tours.services import TourCapacityService
                schedule_id = cart_item.booking_data.get('schedule_id')
                variant_id = str(cart_item.variant_id)

                if schedule_id and variant_id:
                    # Calculate quantity for capacity (adults + children only)
                    participants = cart_item.booking_data.get('participants', {}) or {}
                    adult_count = int(participants.get('adult', 0))
                    child_count = int(participants.get('child', 0))
                    qty_for_capacity = adult_count + child_count

                    if qty_for_capacity > 0:
                        success, error = TourCapacityService.reserve_capacity(
                            schedule_id, variant_id, qty_for_capacity
                        )
                        if not success:
                            raise ValueError(f"Capacity reservation failed: {error}")
            
            elif cart_item.product_type == 'event':
                schedule_id = cart_item.booking_data.get('schedule_id')
                if schedule_id:
                    from events.models import EventPerformance as EventSchedule
                    schedule = EventSchedule.objects.select_for_update().get(id=schedule_id)
                    if schedule.current_capacity < cart_item.quantity:
                        raise ValueError("Insufficient capacity for event")
                    
                    schedule.current_capacity -= cart_item.quantity
                    schedule.save()
            
            # Remove all usages of TransferSchedule
        
        except Exception as e:
            raise ValueError(f"Capacity update failed: {str(e)}")
    
    @staticmethod
    def _validate_transfer_capacity(cart_item):
        """Validate transfer capacity before creating order."""
        try:
            from transfers.models import TransferRoutePricing
            
            route_id = cart_item.booking_data.get('route_id')
            pricing_id = cart_item.booking_data.get('pricing_id')
            passenger_count = cart_item.booking_data.get('passenger_count', 1)
            
            if route_id and pricing_id:
                # Get pricing to check max capacity
                try:
                    pricing = TransferRoutePricing.objects.get(id=pricing_id)
                    if passenger_count > pricing.max_passengers:
                        raise ValueError(f"Passenger count ({passenger_count}) exceeds vehicle capacity ({pricing.max_passengers})")
                except TransferRoutePricing.DoesNotExist:
                    raise ValueError("Transfer pricing not found")
                
                # Check capacity availability (placeholder - implement proper capacity service)
                # For now, we'll just validate the basic constraints
                # In a real implementation, you'd check against actual bookings
                
        except Exception as e:
            raise ValueError(f"Transfer capacity validation failed: {str(e)}")
    
    @staticmethod
    def _get_product_details(cart_item):
        """Get product details for order item."""
        try:
            if cart_item.product_type == 'tour':
                from tours.models import Tour
                tour = Tour.objects.get(id=cart_item.product_id)
                return {
                    'title': tour.title,
                    'slug': tour.slug,
                }
            
            elif cart_item.product_type == 'event':
                from events.models import Event
                event = Event.objects.get(id=cart_item.product_id)
                return {
                    'title': event.title,
                    'slug': event.slug,
                }
            
            elif cart_item.product_type == 'transfer':
                from transfers.models import TransferRoute
                route = TransferRoute.objects.get(id=cart_item.product_id)
                return {
                    'title': route.name or f"{route.origin} → {route.destination}",
                    'slug': route.slug,
                }
            
        except Exception as e:
            print(f"Error getting product details: {e}")
            return {'title': '', 'slug': ''}
    
    @staticmethod
    def update_order_status(order, new_status, user=None, reason=None):
        """Update order status and log change."""
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Update capacity when order status changes
        if old_status != new_status:
            OrderService._update_capacity_for_order_status_change(order, old_status, new_status)
        
        # Log the change
        OrderHistory.objects.create(
            order=order,
            user=user,
            field_name='status',
            old_value=old_status,
            new_value=new_status,
            change_reason=reason,
        )
    
    @staticmethod
    def _update_capacity_for_order_status_change(order, old_status, new_status):
        """Update capacity when order status changes."""
        try:
            from tours.services import TourCapacityService

            # Only update capacity for tour orders
            for item in order.items.filter(product_type='tour'):
                schedule_id = item.booking_data.get('schedule_id')

                if not schedule_id:
                    continue

                # Calculate quantity for capacity (adults + children only)
                participants = item.booking_data.get('participants', {}) or {}
                adult_count = int(participants.get('adult', 0))
                child_count = int(participants.get('child', 0))
                qty_for_capacity = adult_count + child_count

                if qty_for_capacity <= 0:
                    continue

                # Update capacity based on status change
                if old_status == 'pending' and new_status in ['confirmed', 'paid', 'completed']:
                    # Order confirmed/paid - confirm capacity
                    if item.variant_id is None:
                        print(f"WARNING: OrderItem {item.id} has variant_id=None, skipping capacity confirmation")
                        continue

                    variant_id = str(item.variant_id)
                    print(f"DEBUG: Confirming capacity for schedule {schedule_id}, variant {variant_id}, qty {qty_for_capacity}")
                    success, error = TourCapacityService.confirm_capacity(schedule_id, variant_id, qty_for_capacity)
                    print(f"DEBUG: Confirm result: {success}, error: {error}")
                    if not success:
                        print(f"DEBUG: Capacity confirmation FAILED: {error}")
                elif old_status in ['confirmed', 'pending'] and new_status == 'paid':
                    # Order paid - reserve capacity (if not already reserved)
                    if item.variant_id is None:
                        print(f"WARNING: OrderItem {item.id} has variant_id=None, skipping capacity reservation")
                        continue

                    variant_id = str(item.variant_id)
                    print(f"DEBUG: Reserving capacity for schedule {schedule_id}, variant {variant_id}, qty {qty_for_capacity}")
                    success, error = TourCapacityService.reserve_capacity(schedule_id, variant_id, qty_for_capacity)
                    print(f"DEBUG: Reserve result: {success}, error: {error}")
                    if not success:
                        print(f"DEBUG: Capacity reservation FAILED: {error}")
                elif old_status in ['confirmed', 'paid', 'completed'] and new_status == 'cancelled':
                    # Order cancelled - release confirmed capacity
                    if item.variant_id is None:
                        print(f"WARNING: OrderItem {item.id} has variant_id=None, skipping capacity release")
                        continue

                    variant_id = str(item.variant_id)
                    TourCapacityService.release_capacity(schedule_id, variant_id, qty_for_capacity)
                elif old_status == 'pending' and new_status == 'cancelled':
                    # Pending order cancelled - no capacity to release (wasn't reserved yet)
                    pass

        except Exception as e:
            print(f"Error updating capacity for order status change: {e}")
    
    @staticmethod
    def update_payment_status(order, new_status, payment_method=None):
        """Update payment status."""
        old_status = order.payment_status
        order.payment_status = new_status
        if payment_method:
            order.payment_method = payment_method
        order.save()
        
        # Log the change
        OrderHistory.objects.create(
            order=order,
            field_name='payment_status',
            old_value=old_status,
            new_value=new_status,
        )
    
    @staticmethod
    def get_order_summary(order):
        """Get order summary with details."""
        items = order.items.all()
        
        summary = {
            'order_number': order.order_number,
            'status': order.status,
            'payment_status': order.payment_status,
            'total_items': len(items),
            'subtotal': float(order.subtotal),
            'tax_amount': float(order.tax_amount),
            'discount_amount': float(order.discount_amount),
            'total_amount': float(order.total_amount),
            'currency': order.currency,
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'created_at': order.created_at.isoformat(),
            'items': []
        }
        
        for item in items:
            summary['items'].append({
                'id': str(item.id),
                'product_type': item.product_type,
                'product_title': item.product_title,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price),
                'variant_name': item.variant_name,
                'booking_date': item.booking_date.isoformat(),
                'booking_time': item.booking_time.isoformat(),
                'status': item.status,
            })
        
        return summary 