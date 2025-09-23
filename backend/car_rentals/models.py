"""
Car Rental models for Peykan Tourism Platform.
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel, BaseTranslatableModel, BaseProductModel, BaseVariantModel, BaseBookingModel
from parler.models import TranslatedFields
import uuid


class CarRentalCategory(BaseTranslatableModel):
    """
    Car rental categories (Economy, Luxury, SUV, etc.).
    """
    
    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name=_('Name')),
        description=models.TextField(blank=True, verbose_name=_('Description')),
    )
    
    # Category settings
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    
    class Meta:
        verbose_name = _('Car Rental Category')
        verbose_name_plural = _('Car Rental Categories')
        ordering = ['sort_order', 'id']
    
    def __str__(self):
        try:
            return self.name
        except:
            return self.slug


class CarRentalLocation(BaseTranslatableModel):
    """
    Predefined car rental pickup/dropoff locations (airports, hotels, etc.).
    """
    
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_('Location name')),
        description=models.TextField(blank=True, verbose_name=_('Description')),
        address=models.TextField(verbose_name=_('Address')),
    )
    
    # Location details
    city = models.CharField(max_length=100, verbose_name=_('City'))
    country = models.CharField(max_length=100, verbose_name=_('Country'))
    
    # Coordinates for map display
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Latitude')
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Longitude')
    )
    
    # Location type
    LOCATION_TYPE_CHOICES = [
        ('airport', _('Airport')),
        ('hotel', _('Hotel')),
        ('station', _('Train/Bus Station')),
        ('city_center', _('City Center')),
        ('port', _('Port')),
        ('other', _('Other')),
    ]
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default='other',
        verbose_name=_('Location type')
    )
    
    # Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort order'))
    
    # Operating hours (optional)
    operating_hours_start = models.TimeField(
        null=True, 
        blank=True,
        verbose_name=_('Operating hours start')
    )
    operating_hours_end = models.TimeField(
        null=True, 
        blank=True,
        verbose_name=_('Operating hours end')
    )
    
    class Meta:
        verbose_name = _('Car Rental Location')
        verbose_name_plural = _('Car Rental Locations')
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['location_type', 'is_active']),
        ]
    
    def __str__(self):
        try:
            return f"{self.name} - {self.city}, {self.country}"
        except:
            return self.slug


class CarRental(BaseProductModel):
    """
    Car rental product model.
    """
    
    # Translatable fields
    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_('Title')),
        description=models.TextField(verbose_name=_('Description')),
        short_description=models.TextField(max_length=500, verbose_name=_('Short description')),
        highlights=models.TextField(blank=True, verbose_name=_('Highlights')),
        rules=models.TextField(blank=True, verbose_name=_('Rules and regulations')),
        required_items=models.TextField(blank=True, verbose_name=_('Required items')),
    )
    
    # Car details
    category = models.ForeignKey(
        CarRentalCategory,
        on_delete=models.CASCADE,
        related_name='car_rentals',
        verbose_name=_('Category')
    )
    
    # Vehicle specifications
    brand = models.CharField(max_length=100, verbose_name=_('Brand'))
    model = models.CharField(max_length=100, verbose_name=_('Model'))
    year = models.PositiveIntegerField(verbose_name=_('Year'))
    seats = models.PositiveIntegerField(verbose_name=_('Number of seats'))
    
    FUEL_TYPE_CHOICES = [
        ('gasoline', _('Gasoline')),
        ('diesel', _('Diesel')),
        ('hybrid', _('Hybrid')),
        ('electric', _('Electric')),
        ('lpg', _('LPG')),
    ]
    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_TYPE_CHOICES,
        verbose_name=_('Fuel type')
    )
    
    TRANSMISSION_CHOICES = [
        ('manual', _('Manual')),
        ('automatic', _('Automatic')),
        ('semi_automatic', _('Semi-automatic')),
    ]
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        verbose_name=_('Transmission')
    )
    
    # Rental settings
    min_rent_days = models.PositiveIntegerField(default=1, verbose_name=_('Minimum rental days'))
    max_rent_days = models.PositiveIntegerField(default=365, verbose_name=_('Maximum rental days'))
    
    # Hourly rental settings
    allow_hourly_rental = models.BooleanField(
        default=True,
        verbose_name=_('Allow hourly rental'),
        help_text=_('Allow rentals for less than 24 hours')
    )
    min_rent_hours = models.PositiveIntegerField(
        default=8, 
        verbose_name=_('Minimum rental hours'),
        help_text=_('Minimum rental period in hours (for same-day rentals)')
    )
    max_hourly_rental_hours = models.PositiveIntegerField(
        default=23,
        verbose_name=_('Maximum hourly rental hours'),
        help_text=_('Maximum hours for hourly rental (before switching to daily)')
    )
    
    mileage_limit_per_day = models.PositiveIntegerField(
        default=200,
        verbose_name=_('Mileage limit per day (km)'),
        help_text=_('Daily mileage limit in kilometers')
    )
    advance_booking_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_('Advance booking days'),
        help_text=_('How many days in advance can this car be booked')
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Deposit amount')
    )
    
    # Pricing
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Price per day')
    )
    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Price per hour')
    )
    
    # Discounts for long-term rentals
    weekly_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name=_('Weekly discount (%)')
    )
    monthly_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name=_('Monthly discount (%)')
    )
    
    # Location settings
    pickup_location = models.CharField(max_length=255, verbose_name=_('Pickup location'))
    dropoff_location = models.CharField(max_length=255, verbose_name=_('Dropoff location'))
    pickup_instructions = models.TextField(blank=True, verbose_name=_('Pickup instructions'))
    dropoff_instructions = models.TextField(blank=True, verbose_name=_('Dropoff instructions'))
    
    # Default locations for this car rental
    default_pickup_locations = models.ManyToManyField(
        CarRentalLocation,
        related_name='car_rentals_pickup',
        blank=True,
        verbose_name=_('Default pickup locations'),
        help_text=_('Predefined locations where this car can be picked up')
    )
    default_dropoff_locations = models.ManyToManyField(
        CarRentalLocation,
        related_name='car_rentals_dropoff',
        blank=True,
        verbose_name=_('Default dropoff locations'),
        help_text=_('Predefined locations where this car can be dropped off')
    )
    
    # Custom location settings
    allow_custom_pickup_location = models.BooleanField(
        default=True,
        verbose_name=_('Allow custom pickup location'),
        help_text=_('Allow customers to choose custom pickup location')
    )
    allow_custom_dropoff_location = models.BooleanField(
        default=True,
        verbose_name=_('Allow custom dropoff location'),
        help_text=_('Allow customers to choose custom dropoff location')
    )
    
    # Insurance options
    basic_insurance_included = models.BooleanField(default=True, verbose_name=_('Basic insurance included'))
    comprehensive_insurance_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Comprehensive insurance price per day')
    )
    
    # Availability settings
    is_available = models.BooleanField(default=True, verbose_name=_('Is available'))
    advance_booking_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_('Advance booking days'),
        help_text=_('How many days in advance can this car be booked')
    )
    
    # Agent ownership
    agent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='car_rentals',
        verbose_name=_('Agent'),
        help_text=_('Agent who owns this car rental')
    )
    
    class Meta:
        verbose_name = _('Car Rental')
        verbose_name_plural = _('Car Rentals')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'model']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['agent', 'is_active']),
            models.Index(fields=['city', 'country']),
        ]
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
    
    def get_daily_price_with_discount(self, days):
        """Calculate daily price with long-term discounts."""
        base_price = self.price_per_day
        
        if days >= 30 and self.monthly_discount_percentage > 0:
            discount = base_price * (self.monthly_discount_percentage / 100)
            return base_price - discount
        elif days >= 7 and self.weekly_discount_percentage > 0:
            discount = base_price * (self.weekly_discount_percentage / 100)
            return base_price - discount
        
        return base_price
    
    def calculate_total_price(self, days, hours=0, include_insurance=False):
        """Calculate total rental price with simplified hourly/daily logic."""
        total = Decimal('0.00')
        
        # محاسبه ساعتی (فقط ساعت)
        if days == 0 and hours > 0:
            if not self.allow_hourly_rental:
                raise ValidationError("Hourly rental not allowed for this car")
            
            if hours < self.min_rent_hours:
                raise ValidationError(f"Minimum rental period is {self.min_rent_hours} hours")
            
            if hours > self.max_hourly_rental_hours:
                raise ValidationError(f"Maximum hourly rental is {self.max_hourly_rental_hours} hours")
            
            if not self.price_per_hour:
                raise ValidationError("Hourly pricing not available for this car")
            
            total += self.price_per_hour * hours
        
        # محاسبه روزانه (فقط روز - ساعت‌های اضافی نادیده گرفته می‌شوند)
        elif days > 0:
            if days < self.min_rent_days:
                raise ValidationError(f"Minimum rental period is {self.min_rent_days} days")
            
            if days > self.max_rent_days:
                raise ValidationError(f"Maximum rental period is {self.max_rent_days} days")
            
            daily_price = self.get_daily_price_with_discount(days)
            total += daily_price * days
        
        # بیمه
        if include_insurance and self.comprehensive_insurance_price > 0:
            # برای رنت ساعتی، بیمه بر اساس حداقل 1 روز محاسبه می‌شود
            insurance_days = days if days > 0 else 1
            total += self.comprehensive_insurance_price * insurance_days
        
        return total
    
    def calculate_rental_duration(self, pickup_date, dropoff_date, pickup_time, dropoff_time):
        """Calculate rental duration with simplified logic."""
        from datetime import datetime, time, timedelta, date
        
        # Convert string dates to date objects if needed
        if isinstance(pickup_date, str):
            pickup_date = datetime.strptime(pickup_date, "%Y-%m-%d").date()
        if isinstance(dropoff_date, str):
            dropoff_date = datetime.strptime(dropoff_date, "%Y-%m-%d").date()
        
        # Convert time objects to string format if needed
        if isinstance(pickup_time, time):
            pickup_time_str = pickup_time.strftime('%H:%M')
        else:
            pickup_time_str = str(pickup_time)
            
        if isinstance(dropoff_time, time):
            dropoff_time_str = dropoff_time.strftime('%H:%M')
        else:
            dropoff_time_str = str(dropoff_time)
        
        # Handle both HH:MM and HH:MM:SS formats
        pickup_time_formatted = pickup_time_str if len(pickup_time_str.split(':')) == 3 else f"{pickup_time_str}:00"
        dropoff_time_formatted = dropoff_time_str if len(dropoff_time_str.split(':')) == 3 else f"{dropoff_time_str}:00"
        
        pickup_dt = datetime.strptime(f"{pickup_date} {pickup_time_formatted}", "%Y-%m-%d %H:%M:%S")
        dropoff_dt = datetime.strptime(f"{dropoff_date} {dropoff_time_formatted}", "%Y-%m-%d %H:%M:%S")
        
        # Calculate total hours
        duration = dropoff_dt - pickup_dt
        total_hours = duration.total_seconds() / 3600
        
        # Simplified logic:
        # - If same day: hourly rental (days=0, hours=total_hours)
        # - If different days: daily rental (days=calendar_days, hours=0)
        if pickup_date == dropoff_date:
            # Same day = hourly rental
            days = 0
            hours = int(total_hours)
        else:
            # Different days = daily rental
            # Calculate days as the difference between dates (not including the dropoff day if it's the same time)
            days = (dropoff_date - pickup_date).days
            hours = 0  # No extra hours for daily rentals
        
        return days, hours, total_hours


class CarRentalImage(BaseModel):
    """
    Additional images for car rentals.
    """
    
    car_rental = models.ForeignKey(
        CarRental,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Car rental')
    )
    image = models.ImageField(
        upload_to='car_rentals/',
        verbose_name=_('Image')
    )
    caption = models.CharField(max_length=255, blank=True, verbose_name=_('Caption'))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort order'))
    is_primary = models.BooleanField(default=False, verbose_name=_('Is primary image'))
    
    class Meta:
        verbose_name = _('Car Rental Image')
        verbose_name_plural = _('Car Rental Images')
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.car_rental} - Image {self.sort_order}"


class CarRentalOption(BaseTranslatableModel):
    """
    Car rental options and add-ons (GPS, baby seat, driver service, etc.).
    """
    
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_('Name')),
        description=models.TextField(verbose_name=_('Description')),
    )
    
    # Option type
    OPTION_TYPE_CHOICES = [
        ('gps', _('GPS Navigation')),
        ('baby_seat', _('Baby Seat')),
        ('child_seat', _('Child Seat')),
        ('driver_service', _('Driver Service')),
        ('additional_driver', _('Additional Driver')),
        ('roof_rack', _('Roof Rack')),
        ('bike_rack', _('Bike Rack')),
        ('winter_tires', _('Winter Tires')),
        ('premium_insurance', _('Premium Insurance')),
        ('roadside_assistance', _('Roadside Assistance')),
    ]
    option_type = models.CharField(
        max_length=30,
        choices=OPTION_TYPE_CHOICES,
        verbose_name=_('Option type')
    )
    
    # Pricing
    price_type = models.CharField(
        max_length=20,
        choices=[
            ('fixed', _('Fixed Amount')),
            ('daily', _('Per Day')),
            ('percentage', _('Percentage of Base Price')),
        ],
        default='daily',
        verbose_name=_('Price type')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Price')
    )
    price_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name=_('Price percentage')
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    
    # Availability
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    max_quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Maximum quantity'),
        help_text=_('Maximum number of this option that can be selected')
    )
    
    class Meta:
        verbose_name = _('Car Rental Option')
        verbose_name_plural = _('Car Rental Options')
        ordering = ['option_type', 'id']
    
    def __str__(self):
        try:
            return self.name
        except:
            return self.slug
    
    def calculate_price(self, base_price, days=1, quantity=1):
        """Calculate option price."""
        if self.price_type == 'fixed':
            # For fixed price options, price is constant regardless of rental duration
            return self.price * quantity
        elif self.price_type == 'daily':
            return self.price * days * quantity
        elif self.price_type == 'percentage':
            return (base_price * (self.price_percentage / 100)) * quantity
        return Decimal('0.00')


class CarRentalAvailability(BaseModel):
    """
    Car rental availability calendar.
    """
    
    car_rental = models.ForeignKey(
        CarRental,
        on_delete=models.CASCADE,
        related_name='availability',
        verbose_name=_('Car rental')
    )
    
    # Date range
    start_date = models.DateField(verbose_name=_('Start date'))
    end_date = models.DateField(verbose_name=_('End date'))
    
    # Availability settings
    is_available = models.BooleanField(default=True, verbose_name=_('Is available'))
    max_quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Maximum quantity'),
        help_text=_('Maximum number of cars available for this period')
    )
    booked_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Booked quantity')
    )
    
    # Pricing overrides
    price_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Price override'),
        help_text=_('Override default daily price for this period')
    )
    
    # Notes
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    
    class Meta:
        verbose_name = _('Car Rental Availability')
        verbose_name_plural = _('Car Rental Availability')
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['car_rental', 'start_date']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.car_rental} - {self.start_date} to {self.end_date}"
    
    @property
    def available_quantity(self):
        """Get available quantity for this period."""
        return max(0, self.max_quantity - self.booked_quantity)
    
    def is_available_for_booking(self, quantity=1):
        """Check if available for booking."""
        return self.is_available and self.available_quantity >= quantity
    
    def reserve_quantity(self, quantity):
        """Reserve quantity (atomic operation)."""
        if not self.is_available_for_booking(quantity):
            return False
        
        self.booked_quantity += quantity
        self.save(update_fields=['booked_quantity'])
        return True
    
    def release_quantity(self, quantity):
        """Release reserved quantity."""
        if self.booked_quantity >= quantity:
            self.booked_quantity = max(0, self.booked_quantity - quantity)
            self.save(update_fields=['booked_quantity'])
            return True
        return False


class CarRentalBooking(BaseBookingModel):
    """
    Car rental booking model.
    """
    
    car_rental = models.ForeignKey(
        CarRental,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Car rental')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='car_rental_bookings',
        verbose_name=_('User')
    )
    
    # Booking details
    booking_reference = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('Booking reference')
    )
    
    # Rental period
    pickup_date = models.DateField(verbose_name=_('Pickup date'))
    dropoff_date = models.DateField(verbose_name=_('Dropoff date'))
    pickup_time = models.TimeField(verbose_name=_('Pickup time'))
    dropoff_time = models.TimeField(verbose_name=_('Dropoff time'))
    
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
    pickup_location_id = models.ForeignKey(
        CarRentalLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickup_bookings',
        verbose_name=_('Pickup location')
    )
    pickup_location_custom = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Custom pickup location')
    )
    pickup_location_coordinates = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Pickup location coordinates'),
        help_text=_('Latitude and longitude for custom pickup location')
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
    dropoff_location_id = models.ForeignKey(
        CarRentalLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dropoff_bookings',
        verbose_name=_('Dropoff location')
    )
    dropoff_location_custom = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Custom dropoff location')
    )
    dropoff_location_coordinates = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Dropoff location coordinates'),
        help_text=_('Latitude and longitude for custom dropoff location')
    )
    
    # Rental duration
    total_days = models.PositiveIntegerField(verbose_name=_('Total days'))
    total_hours = models.PositiveIntegerField(default=0, verbose_name=_('Total hours'))
    
    # Pricing details
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Daily rate')
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Hourly rate')
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Base price')
    )
    options_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Options total')
    )
    insurance_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Insurance total')
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Deposit amount')
    )
    
    # Customer details
    driver_name = models.CharField(max_length=255, verbose_name=_('Driver name'))
    driver_license = models.CharField(max_length=50, verbose_name=_('Driver license number'))
    driver_phone = models.CharField(max_length=20, verbose_name=_('Driver phone'))
    driver_email = models.EmailField(verbose_name=_('Driver email'))
    
    # Additional drivers
    additional_drivers = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Additional drivers')
    )
    
    # Selected options
    selected_options = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Selected options')
    )
    
    # Insurance
    basic_insurance = models.BooleanField(default=True, verbose_name=_('Basic insurance'))
    comprehensive_insurance = models.BooleanField(default=False, verbose_name=_('Comprehensive insurance'))
    
    # Special requirements
    special_requirements = models.TextField(blank=True, verbose_name=_('Special requirements'))
    
    # Status tracking
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('picked_up', _('Picked Up')),
        ('returned', _('Returned')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Availability reference
    availability = models.ForeignKey(
        CarRentalAvailability,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        verbose_name=_('Availability period')
    )
    
    class Meta:
        verbose_name = _('Car Rental Booking')
        verbose_name_plural = _('Car Rental Bookings')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['car_rental', 'pickup_date']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['booking_reference']),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_reference} - {self.car_rental}"
    
    def clean(self):
        """Validate booking data."""
        from datetime import datetime, date, time
        
        # Validate pickup time (minimum 6 hours from now)
        if self.pickup_date and self.pickup_time:
            pickup_datetime = datetime.combine(self.pickup_date, self.pickup_time)
            now = datetime.now()
            min_pickup_time = now.replace(hour=now.hour + 6, minute=0, second=0, microsecond=0)
            
            if pickup_datetime < min_pickup_time:
                raise ValidationError({
                    'pickup_time': _('Pickup time must be at least 6 hours from now.')
                })
        
        # Validate dropoff time (minimum 24 hours after pickup)
        if (self.pickup_date and self.pickup_time and 
            self.dropoff_date and self.dropoff_time):
            
            pickup_datetime = datetime.combine(self.pickup_date, self.pickup_time)
            dropoff_datetime = datetime.combine(self.dropoff_date, self.dropoff_time)
            
            # Calculate minimum dropoff time (24 hours after pickup)
            min_dropoff_datetime = pickup_datetime.replace(
                hour=pickup_datetime.hour + 24,
                minute=pickup_datetime.minute,
                second=0,
                microsecond=0
            )
            
            if dropoff_datetime < min_dropoff_datetime:
                raise ValidationError({
                    'dropoff_time': _('Dropoff time must be at least 24 hours after pickup time.')
                })
        
        # Validate location data
        if self.pickup_location_type == 'predefined' and not self.pickup_location_id:
            raise ValidationError({
                'pickup_location_id': _('Pickup location is required when using predefined location.')
            })
        
        if self.pickup_location_type == 'custom' and not self.pickup_location_custom:
            raise ValidationError({
                'pickup_location_custom': _('Custom pickup location is required.')
            })
        
        if self.dropoff_location_type == 'predefined' and not self.dropoff_location_id:
            raise ValidationError({
                'dropoff_location_id': _('Dropoff location is required when using predefined location.')
            })
        
        if self.dropoff_location_type == 'custom' and not self.dropoff_location_custom:
            raise ValidationError({
                'dropoff_location_custom': _('Custom dropoff location is required.')
            })
    
    def save(self, *args, **kwargs):
        # Validate data before saving
        self.clean()
        
        # Generate booking reference if not provided
        if not self.booking_reference:
            self.booking_reference = f"CR{str(uuid.uuid4().hex[:8].upper())}"
        
        # Calculate total price
        self.total_price = self.base_price + self.options_total + self.insurance_total
        
        super().save(*args, **kwargs)
    
    @property
    def total_rental_days(self):
        """Calculate total rental days including partial days."""
        from datetime import datetime, date
        
        if isinstance(self.pickup_date, str):
            pickup = datetime.strptime(self.pickup_date, '%Y-%m-%d').date()
        else:
            pickup = self.pickup_date
            
        if isinstance(self.dropoff_date, str):
            dropoff = datetime.strptime(self.dropoff_date, '%Y-%m-%d').date()
        else:
            dropoff = self.dropoff_date
        
        delta = dropoff - pickup
        return delta.days + (1 if self.total_hours > 0 else 0)
    
    def calculate_final_price(self):
        """Calculate final price including all components."""
        return self.base_price + self.options_total + self.insurance_total
    
    @property
    def pickup_location_display(self):
        """Get display name for pickup location."""
        if self.pickup_location_type == 'predefined' and self.pickup_location_id:
            return str(self.pickup_location_id)
        elif self.pickup_location_type == 'custom':
            return self.pickup_location_custom
        return _('Not specified')
    
    @property
    def dropoff_location_display(self):
        """Get display name for dropoff location."""
        if self.dropoff_location_type == 'same_as_pickup':
            return self.pickup_location_display
        elif self.dropoff_location_type == 'predefined' and self.dropoff_location_id:
            return str(self.dropoff_location_id)
        elif self.dropoff_location_type == 'custom':
            return self.dropoff_location_custom
        return _('Not specified')
