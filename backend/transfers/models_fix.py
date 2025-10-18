"""
اصلاح Transfer Models برای پشتیبانی بهتر از ارز
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel, BaseBookingModel, BaseTranslatableModel


class TransferRoutePricingFixed(BaseModel):
    """
    Fixed pricing for each route and vehicle type combination with enhanced currency support
    """
    
    route = models.ForeignKey(
        'TransferRoute', 
        on_delete=models.CASCADE, 
        related_name='pricing',
        verbose_name=_('Route')
    )
    
    # Vehicle type
    VEHICLE_CATEGORY_CHOICES = [
        ('sedan', _('Sedan')),
        ('suv', _('SUV')),
        ('van', _('Van')),
        ('sprinter', _('Sprinter')),
        ('bus', _('Bus')),
        ('limousine', _('Limousine')),
    ]
    vehicle_type = models.CharField(
        max_length=20, 
        choices=VEHICLE_CATEGORY_CHOICES,
        verbose_name=_('Vehicle type')
    )
    
    # Vehicle details
    vehicle_name = models.CharField(max_length=255, verbose_name=_('Vehicle name'))
    vehicle_description = models.TextField(blank=True, verbose_name=_('Vehicle description'))
    
    # Enhanced pricing with multiple currencies
    base_price_usd = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('Base price (USD)'),
        help_text=_('Base price in US Dollars')
    )
    base_price_eur = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        null=True,
        blank=True,
        verbose_name=_('Base price (EUR)'),
        help_text=_('Base price in Euros')
    )
    base_price_irr = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        null=True,
        blank=True,
        verbose_name=_('Base price (IRR)'),
        help_text=_('Base price in Iranian Rials')
    )
    base_price_try = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        null=True,
        blank=True,
        verbose_name=_('Base price (TRY)'),
        help_text=_('Base price in Turkish Lira')
    )
    
    # Legacy currency field for backward compatibility
    currency = models.CharField(
        max_length=3, 
        default='USD', 
        verbose_name=_('Primary currency'),
        help_text=_('Primary currency for this pricing')
    )
    
    # Pricing metadata for flexible pricing logic
    pricing_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Pricing metadata')
    )
    
    # Capacity
    max_passengers = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Max passengers')
    )
    max_luggage = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name=_('Max luggage')
    )
    
    # Features and amenities
    features = models.JSONField(default=list, blank=True, verbose_name=_('Features'))
    amenities = models.JSONField(default=list, blank=True, verbose_name=_('Amenities'))
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    
    class Meta:
        verbose_name = _('Transfer Route Pricing')
        verbose_name_plural = _('Transfer Route Pricing')
        unique_together = ['route', 'vehicle_type']
        constraints = [
            models.UniqueConstraint(fields=['route', 'vehicle_type'], name='unique_route_vehicle')
        ]
        indexes = [
            models.Index(fields=['route', 'vehicle_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.route} - {self.vehicle_type} - ${self.base_price_usd}"
    
    def get_price_in_currency(self, currency: str) -> Decimal:
        """
        Get base price in specified currency
        """
        currency = currency.upper()
        
        if currency == 'USD':
            return self.base_price_usd
        elif currency == 'EUR':
            return self.base_price_eur or self.base_price_usd
        elif currency == 'IRR':
            return self.base_price_irr or self.base_price_usd
        elif currency == 'TRY':
            return self.base_price_try or self.base_price_usd
        else:
            # Fallback to USD
            return self.base_price_usd
    
    def set_price_in_currency(self, currency: str, price: Decimal) -> None:
        """
        Set base price in specified currency
        """
        currency = currency.upper()
        
        if currency == 'USD':
            self.base_price_usd = price
        elif currency == 'EUR':
            self.base_price_eur = price
        elif currency == 'IRR':
            self.base_price_irr = price
        elif currency == 'TRY':
            self.base_price_try = price
        else:
            raise ValueError(f"Unsupported currency: {currency}")
    
    @property
    def base_price(self) -> Decimal:
        """
        Get base price in primary currency (for backward compatibility)
        """
        return self.get_price_in_currency(self.currency)
    
    def clean(self):
        """Custom validation."""
        super().clean()
        
        # Validate that at least USD price is set
        if self.base_price_usd <= 0:
            raise ValidationError(_('Base price in USD must be greater than zero.'))
        
        # Validate pricing metadata structure
        if not self.pricing_metadata:
            raise ValidationError(_('Pricing metadata is required.'))
        
        required_keys = ['pricing_type', 'calculation_method']
        for key in required_keys:
            if key not in self.pricing_metadata:
                raise ValidationError(_(f'Pricing metadata must contain "{key}" field.'))
        
        # Validate pricing type
        pricing_type = self.pricing_metadata.get('pricing_type')
        if pricing_type not in ['transfer', 'tour', 'event']:
            raise ValidationError(_('Invalid pricing type in metadata.'))
    
    def calculate_price(self, currency: str = None, **kwargs):
        """
        Calculate transfer price with currency support
        """
        # Use provided currency or default to primary currency
        target_currency = currency or self.currency
        
        # Get base price in target currency
        base_price = self.get_price_in_currency(target_currency)
        
        # Apply existing pricing logic with currency-aware base price
        # This would integrate with the existing _calculate_transfer_price method
        # but use the currency-specific base price
        
        # For now, return a basic structure
        return {
            'base_price': base_price,
            'currency': target_currency,
            'pricing_type': self.pricing_metadata.get('pricing_type', 'transfer'),
            'calculation_method': self.pricing_metadata.get('calculation_method', 'fixed'),
            # ... other pricing breakdown fields
        }


class TransferBookingFixed(BaseBookingModel):
    """
    Transfer bookings with enhanced currency support
    """
    
    route = models.ForeignKey(
        'TransferRoute', 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_('Route')
    )
    pricing = models.ForeignKey(
        'TransferRoutePricing', 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_('Pricing')
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='transfer_bookings',
        verbose_name=_('User')
    )
    
    # Booking details
    booking_reference = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name=_('Booking reference')
    )
    
    # Trip details
    trip_type = models.CharField(
        max_length=20,
        choices=[
            ('one_way', _('One Way')),
            ('round_trip', _('Round Trip')),
        ],
        default='one_way',
        verbose_name=_('Trip type')
    )
    
    # Outbound details
    outbound_date = models.DateField(verbose_name=_('Outbound date'))
    outbound_time = models.TimeField(verbose_name=_('Outbound time'))
    outbound_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Outbound price'))
    
    # Return details (for round trip)
    return_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('Return date')
    )
    return_time = models.TimeField(
        null=True, 
        blank=True,
        verbose_name=_('Return time')
    )
    return_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, verbose_name=_('Return price'))
    
    # Passenger details
    passenger_count = models.PositiveIntegerField(verbose_name=_('Passenger count'))
    luggage_count = models.PositiveIntegerField(default=0, verbose_name=_('Luggage count'))
    
    # Pickup details
    pickup_address = models.TextField(verbose_name=_('Pickup address'))
    pickup_instructions = models.TextField(blank=True, verbose_name=_('Pickup instructions'))
    
    # Drop-off details
    dropoff_address = models.TextField(verbose_name=_('Drop-off address'))
    dropoff_instructions = models.TextField(blank=True, verbose_name=_('Drop-off instructions'))
    
    # Contact information
    contact_name = models.CharField(max_length=255, verbose_name=_('Contact name'))
    contact_phone = models.CharField(max_length=20, verbose_name=_('Contact phone'))
    
    # Enhanced pricing breakdown with currency support
    base_currency = models.CharField(
        max_length=3, 
        default='USD',
        verbose_name=_('Base currency'),
        help_text=_('Currency used for base pricing')
    )
    display_currency = models.CharField(
        max_length=3, 
        default='USD',
        verbose_name=_('Display currency'),
        help_text=_('Currency used for display to customer')
    )
    exchange_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Exchange rate'),
        help_text=_('Exchange rate used for currency conversion')
    )
    
    # Pricing breakdown
    round_trip_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, verbose_name=_('Round trip discount'))
    options_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name=_('Options total')
    )
    final_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name=_('Final price')
    )
    
    # Options
    selected_options = models.JSONField(
        default=list,
        verbose_name=_('Selected options')
    )
    
    # Special requirements
    special_requirements = models.TextField(blank=True, verbose_name=_('Special requirements'))
    
    class Meta:
        verbose_name = _('Transfer Booking')
        verbose_name_plural = _('Transfer Bookings')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_reference']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['route', 'outbound_date']),
            models.Index(fields=['base_currency', 'display_currency']),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_reference} - {self.route}"
    
    def get_final_price_in_currency(self, currency: str) -> Decimal:
        """
        Get final price in specified currency
        """
        if currency == self.display_currency:
            return self.final_price
        
        # If we have exchange rate, use it
        if self.exchange_rate:
            if self.display_currency == 'USD' and currency == 'IRR':
                return self.final_price * self.exchange_rate
            elif self.display_currency == 'IRR' and currency == 'USD':
                return self.final_price / self.exchange_rate
            # Add more currency conversion logic as needed
        
        # Fallback to current final price
        return self.final_price
