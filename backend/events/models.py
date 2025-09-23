"""
Event models for Peykan Tourism Platform.
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseProductModel, BaseVariantModel, BaseScheduleModel, BaseOptionModel, BaseModel, BaseBookingModel, BaseTranslatableModel
from parler.models import TranslatedFields
from django.core.exceptions import ValidationError


class EventCancellationPolicy(BaseModel):
    """
    Cancellation policy for events.
    Allows multiple policies per event with different time frames.
    """
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='cancellation_policies',
        verbose_name=_('Event')
    )
    
    hours_before = models.PositiveIntegerField(
        verbose_name=_('Hours before event start'),
        help_text=_('Number of hours before event start when this policy applies')
    )
    
    refund_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Refund percentage'),
        help_text=_('Percentage of refund for cancellations within this time frame')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Human-readable description of this policy')
    )
    
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    
    class Meta:
        verbose_name = _('Event Cancellation Policy')
        verbose_name_plural = _('Event Cancellation Policies')
        ordering = ['-hours_before']  # Order by hours_before descending
        unique_together = ['event', 'hours_before']
    
    def __str__(self):
        return f"{self.event} - {self.hours_before}h: {self.refund_percentage}%"


class EventCategory(BaseTranslatableModel):
    """
    Event categories (music, sports, theater, festival, etc.).
    """
    
    # Translatable fields
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_('Name')),
        description=models.TextField(verbose_name=_('Description')),
    )
    
    # Category specific fields
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Icon'))
    color = models.CharField(max_length=7, default='#28a745', verbose_name=_('Color'))
    
    class Meta:
        verbose_name = _('Event Category')
        verbose_name_plural = _('Event Categories')
    
    def __str__(self):
        try:
            return getattr(self, 'name', '') or self.slug
        except:
            return self.slug


class Venue(BaseTranslatableModel):
    """
    Event venues with location and capacity information.
    """
    
    # Translatable fields
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_('Name')),
        description=models.TextField(verbose_name=_('Description')),
        address=models.TextField(verbose_name=_('Address')),
    )
    
    # Venue details
    image = models.ImageField(upload_to='venues/', verbose_name=_('Image'))
    website = models.URLField(blank=True, verbose_name=_('Website'))
    
    # Location
    city = models.CharField(max_length=100, verbose_name=_('City'))
    country = models.CharField(max_length=100, verbose_name=_('Country'))
    coordinates = models.JSONField(null=True, blank=True, verbose_name=_('Coordinates'))
    
    # Capacity
    total_capacity = models.PositiveIntegerField(verbose_name=_('Total capacity'))
    
    # Facilities
    facilities = models.JSONField(default=list, blank=True, verbose_name=_('Facilities'))
    
    class Meta:
        verbose_name = _('Venue')
        verbose_name_plural = _('Venues')
    
    def __str__(self):
        try:
            return getattr(self, 'name', '') or self.slug
        except:
            return self.slug


class Artist(BaseTranslatableModel):
    """
    Event artists and performers.
    """
    
    # Translatable fields
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_('Name')),
        bio=models.TextField(verbose_name=_('Bio')),
    )
    
    # Artist details
    image = models.ImageField(upload_to='artists/', verbose_name=_('Image'))
    website = models.URLField(blank=True, verbose_name=_('Website'))
    
    # Social media
    social_media = models.JSONField(default=dict, blank=True, verbose_name=_('Social media'))
    
    class Meta:
        verbose_name = _('Artist')
        verbose_name_plural = _('Artists')
    
    def __str__(self):
        try:
            return getattr(self, 'name', '') or str(self.id)
        except:
            return str(self.id)


class Event(BaseProductModel):
    """
    Event model with all required features.
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
    
    # Cancellation policy
    cancellation_hours = models.PositiveIntegerField(default=48, verbose_name=_('Cancellation hours'))
    refund_percentage = models.PositiveIntegerField(
        default=50, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Refund percentage')
    )
    
    # Event specific fields
    category = models.ForeignKey(
        EventCategory, 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name=_('Category')
    )
    venue = models.ForeignKey(
        Venue, 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name=_('Venue')
    )
    artists = models.ManyToManyField(
        Artist, 
        related_name='events',
        verbose_name=_('Artists')
    )
    
    # Event details
    EVENT_STYLE_CHOICES = [
        ('music', _('Music')),
        ('sports', _('Sports')),
        ('theater', _('Theater')),
        ('festival', _('Festival')),
        ('conference', _('Conference')),
        ('exhibition', _('Exhibition')),
    ]
    style = models.CharField(
        max_length=20, 
        choices=EVENT_STYLE_CHOICES,
        verbose_name=_('Style')
    )
    
    # Timing
    door_open_time = models.TimeField(verbose_name=_('Door open time'))
    start_time = models.TimeField(verbose_name=_('Start time'))
    end_time = models.TimeField(verbose_name=_('End time'))
    
    # Age restrictions
    age_restriction = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name=_('Age restriction')
    )
    
    # Additional images
    gallery = models.JSONField(default=list, blank=True, verbose_name=_('Gallery'))

    # Additional status fields for event promotion
    is_special = models.BooleanField(
        default=False,
        verbose_name=_('Is special'),
        help_text=_('Mark as special event for premium display on homepage')
    )
    is_seasonal = models.BooleanField(
        default=False,
        verbose_name=_('Is seasonal'),
        help_text=_('Mark as seasonal event (summer/winter specials, holidays, etc.)')
    )

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
    
    def __str__(self):
        try:
            return getattr(self, 'title', '') or self.slug
        except:
            return self.slug
    
    @property
    def is_available_today(self):
        """Check if event has available performances in the future."""
        from datetime import date
        today = date.today()
        return self.performances.filter(
            date__gte=today,
            is_available=True
        ).exists()


class TicketType(BaseVariantModel):
    """
    Event ticket types (VIP, Eco, Normal, Wheelchair).
    """
    
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='ticket_types',
        verbose_name=_('Event')
    )
    
    # Ticket type specific fields
    TICKET_TYPE_CHOICES = [
        ('vip', _('VIP')),
        ('eco', _('Eco')),
        ('normal', _('Normal')),
        ('wheelchair', _('Wheelchair')),
        ('student', _('Student')),
        ('senior', _('Senior')),
    ]
    ticket_type = models.CharField(
        max_length=20, 
        choices=TICKET_TYPE_CHOICES,
        verbose_name=_('Ticket type')
    )
    
    # Benefits
    benefits = models.JSONField(default=list, blank=True, verbose_name=_('Benefits'))
    
    # Restrictions
    age_min = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Minimum age'))
    age_max = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Maximum age'))
    
    class Meta:
        verbose_name = _('Ticket Type')
        verbose_name_plural = _('Ticket Types')
        unique_together = ['event', 'name']
    
    def __str__(self):
        try:
            event_title = getattr(self.event, 'title', '') if self.event else ''
            return f"{event_title} - {self.name}"
        except:
            return f"Event - {self.name}"


class EventPerformance(BaseScheduleModel):
    """
    Event performances with specific dates and seat availability.
    """
    
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='performances',
        verbose_name=_('Event')
    )
    
    # Performance specific fields
    date = models.DateField(verbose_name=_('Date'))
    is_special = models.BooleanField(default=False, verbose_name=_('Is special performance'))
    
    # Ticket type capacities
    ticket_capacities = models.JSONField(
        default=dict,
        verbose_name=_('Ticket type capacities')
    )
    
    class Meta:
        verbose_name = _('Event Performance')
        verbose_name_plural = _('Event Performances')
        unique_together = ['event', 'date']
    
    def __str__(self):
        try:
            event_title = getattr(self.event, 'title', '') if self.event else ''
            return f"{event_title} - {self.date}"
        except:
            return f"Event - {self.date}"


class Seat(BaseModel):
    """
    Individual seats for event performances.
    """
    
    performance = models.ForeignKey(
        EventPerformance, 
        on_delete=models.CASCADE, 
        related_name='seats',
        verbose_name=_('Performance')
    )
    ticket_type = models.ForeignKey(
        TicketType, 
        on_delete=models.CASCADE, 
        related_name='seats',
        verbose_name=_('Ticket type'),
        null=True,
        blank=True
    )
    
    # Seat details
    seat_number = models.CharField(max_length=20, verbose_name=_('Seat number'))
    row_number = models.CharField(max_length=10, verbose_name=_('Row number'))
    section = models.CharField(max_length=50, verbose_name=_('Section'))
    
    # Status
    STATUS_CHOICES = [
        ('available', _('Available')),
        ('reserved', _('Reserved')),
        ('sold', _('Sold')),
        ('blocked', _('Blocked')),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available',
        verbose_name=_('Status')
    )

    # Reservation (temporary hold)
    reservation_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('Reservation ID')
    )
    reservation_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Reservation expires at')
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Price')
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    
    # Special features
    is_wheelchair_accessible = models.BooleanField(default=False, verbose_name=_('Wheelchair accessible'))
    is_premium = models.BooleanField(default=False, verbose_name=_('Premium seat'))
    
    class Meta:
        verbose_name = _('Seat')
        verbose_name_plural = _('Seats')
        unique_together = ['performance', 'seat_number', 'row_number', 'section']
    
    def __str__(self):
        return f"{self.performance.event.title} - {self.section} {self.row_number} {self.seat_number}"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    @property
    def is_bookable(self):
        return self.status in ['available', 'reserved']


class EventOption(BaseOptionModel):
    """
    Event options and add-ons.
    """
    
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='options',
        verbose_name=_('Event')
    )
    
    # Option specific fields
    OPTION_TYPE_CHOICES = [
        ('service', _('Service')),
        ('equipment', _('Equipment')),
        ('food', _('Food')),
        ('transport', _('Transport')),
        ('parking', _('Parking')),
    ]
    option_type = models.CharField(
        max_length=20, 
        choices=OPTION_TYPE_CHOICES,
        default='service',
        verbose_name=_('Option type')
    )
    
    # Availability
    is_available = models.BooleanField(default=True, verbose_name=_('Is available'))
    max_quantity = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name=_('Maximum quantity')
    )
    
    class Meta:
        verbose_name = _('Event Option')
        verbose_name_plural = _('Event Options')
    
    def __str__(self):
        return f"{self.event.title} - {self.name}"


class EventReview(BaseModel):
    """
    Event reviews and ratings.
    """
    
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name=_('Event')
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='event_reviews',
        verbose_name=_('User')
    )
    
    # Review content
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Rating')
    )
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    comment = models.TextField(verbose_name=_('Comment'))
    
    # Review metadata
    is_verified = models.BooleanField(default=False, verbose_name=_('Is verified'))
    is_helpful = models.PositiveIntegerField(default=0, verbose_name=_('Helpful votes'))
    
    class Meta:
        verbose_name = _('Event Review')
        verbose_name_plural = _('Event Reviews')
        unique_together = ['event', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event.title} - {self.user.username} - {self.rating}"


class EventBooking(BaseBookingModel):
    """
    Event bookings with seat selection and ticket details.
    """
    
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_('Event')
    )
    performance = models.ForeignKey(
        EventPerformance, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_('Performance')
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='event_bookings',
        verbose_name=_('User')
    )
    
    # Booking details
    booking_reference = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name=_('Booking reference')
    )
    
    # Seat selection
    selected_seats = models.JSONField(
        default=list,
        verbose_name=_('Selected seats')
    )
    
    # Ticket breakdown
    ticket_breakdown = models.JSONField(
        default=list,
        verbose_name=_('Ticket breakdown')
    )
    
    # Options
    selected_options = models.JSONField(
        default=list,
        verbose_name=_('Selected options')
    )
    options_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name=_('Options total')
    )
    
    # Special requirements
    special_requirements = models.TextField(blank=True, verbose_name=_('Special requirements'))
    
    class Meta:
        verbose_name = _('Event Booking')
        verbose_name_plural = _('Event Bookings')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking_reference} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"EB{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def total_tickets(self):
        return len(self.selected_seats)
    
    @property
    def subtotal(self):
        return sum(ticket['price'] for ticket in self.ticket_breakdown)
    
    @property
    def grand_total(self):
        return self.subtotal + self.options_total 


class EventSection(BaseModel):
    """
    Event sections (A, B, C, VIP, etc.) with capacity management.
    """
    
    performance = models.ForeignKey(
        EventPerformance, 
        on_delete=models.CASCADE, 
        related_name='sections',
        verbose_name=_('Performance')
    )
    
    name = models.CharField(max_length=50, verbose_name=_('Section name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    # Capacity management - REMOVED DUPLICATE FIELDS
    # available_capacity, reserved_capacity, sold_capacity removed
    total_capacity = models.PositiveIntegerField(verbose_name=_('Total capacity'))
    
    # Pricing
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Base price')
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    
    # Features
    is_wheelchair_accessible = models.BooleanField(default=False, verbose_name=_('Wheelchair accessible'))
    is_premium = models.BooleanField(default=False, verbose_name=_('Premium section'))
    
    class Meta:
        verbose_name = _('Event Section')
        verbose_name_plural = _('Event Sections')
        unique_together = ['performance', 'name']
        ordering = ['name']
    
    def __str__(self):
        try:
            event_title = getattr(self.performance.event, 'title', '') if self.performance and self.performance.event else ''
            return f"{event_title} - {self.name}"
        except:
            return f"Section - {self.name}"
    
    def clean(self):
        super().clean()
        # Validate capacity consistency using computed properties
        if self.available_capacity + self.reserved_capacity + self.sold_capacity != self.total_capacity:
            raise ValidationError(_('Capacity components must sum to total capacity'))
        
        if self.available_capacity < 0:
            raise ValidationError(_('Available capacity cannot be negative'))
    
    @property
    def available_capacity(self):
        """Calculate available capacity from SectionTicketType with caching."""
        if not hasattr(self, '_cached_available_capacity'):
            self._cached_available_capacity = sum(
                stt.available_capacity for stt in self.ticket_types.all()
            )
        return self._cached_available_capacity
    
    @property
    def reserved_capacity(self):
        """Calculate reserved capacity from SectionTicketType with caching."""
        if not hasattr(self, '_cached_reserved_capacity'):
            self._cached_reserved_capacity = sum(
                stt.reserved_capacity for stt in self.ticket_types.all()
            )
        return self._cached_reserved_capacity
    
    @property
    def sold_capacity(self):
        """Calculate sold capacity from SectionTicketType with caching."""
        if not hasattr(self, '_cached_sold_capacity'):
            self._cached_sold_capacity = sum(
                stt.sold_capacity for stt in self.ticket_types.all()
            )
        return self._cached_sold_capacity
    
    def clear_capacity_cache(self):
        """Clear cached capacity values."""
        if hasattr(self, '_cached_available_capacity'):
            delattr(self, '_cached_available_capacity')
        if hasattr(self, '_cached_reserved_capacity'):
            delattr(self, '_cached_reserved_capacity')
        if hasattr(self, '_cached_sold_capacity'):
            delattr(self, '_cached_sold_capacity')
    
    @property
    def occupancy_rate(self):
        """Calculate occupancy rate as percentage."""
        if self.total_capacity == 0:
            return 0
        return ((self.reserved_capacity + self.sold_capacity) / self.total_capacity) * 100
    
    @property
    def is_full(self):
        """Check if section is full."""
        return self.available_capacity == 0
    
    def can_reserve(self, count=1):
        """Check if section can reserve specified number of seats."""
        return self.available_capacity >= count
    
    def reserve_capacity(self, count=1):
        """Reserve capacity in this section - DEPRECATED, use SectionTicketType instead."""
        raise ValidationError(_('Direct section capacity reservation is deprecated. Use SectionTicketType.reserve_capacity() instead.'))
    
    def release_capacity(self, count=1):
        """Release reserved capacity - DEPRECATED, use SectionTicketType instead."""
        raise ValidationError(_('Direct section capacity release is deprecated. Use SectionTicketType.release_capacity() instead.'))
    
    def sell_capacity(self, count=1):
        """Sell capacity - DEPRECATED, use SectionTicketType instead."""
        raise ValidationError(_('Direct section capacity selling is deprecated. Use SectionTicketType.sell_capacity() instead.'))


class SectionTicketType(BaseModel):
    """
    Ticket types available in each section with capacity allocation.
    """
    
    section = models.ForeignKey(
        EventSection,
        on_delete=models.CASCADE,
        related_name='ticket_types',
        verbose_name=_('Section')
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        related_name='section_allocations',
        verbose_name=_('Ticket type')
    )
    
    # Capacity allocation - REMOVED STORED FIELDS, USE COMPUTED PROPERTIES
    # allocated_capacity, available_capacity, reserved_capacity, sold_capacity removed
    
    # Pricing
    price_modifier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        verbose_name=_('Price modifier')
    )
    
    class Meta:
        verbose_name = _('Section Ticket Type')
        verbose_name_plural = _('Section Ticket Types')
        unique_together = ['section', 'ticket_type']
    
    def __str__(self):
        return f"{self.section.name} - {self.ticket_type.name}"
    
    @property
    def allocated_capacity(self):
        """Calculate allocated capacity from actual seats."""
        # First try to find seats with this specific ticket type
        specific_seats = Seat.objects.filter(
            performance=self.section.performance,
            section=self.section.name,
            ticket_type=self.ticket_type
        ).count()
        
        # If no specific seats found, look for unassigned seats in this section
        if specific_seats == 0:
            unassigned_seats = Seat.objects.filter(
                performance=self.section.performance,
                section=self.section.name,
                ticket_type__isnull=True  # Seats without ticket type assignment
            ).count()
            return unassigned_seats
        
        return specific_seats
    
    @property
    def available_capacity(self):
        """Calculate available capacity from actual seats."""
        # First try to find seats with this specific ticket type
        specific_seats = Seat.objects.filter(
            performance=self.section.performance,
            section=self.section.name,
            ticket_type=self.ticket_type,
            status='available'
        ).count()
        
        # If no specific seats found, look for unassigned seats in this section
        if specific_seats == 0:
            unassigned_seats = Seat.objects.filter(
                performance=self.section.performance,
                section=self.section.name,
                ticket_type__isnull=True,  # Seats without ticket type assignment
                status='available'
            ).count()
            return unassigned_seats
        
        return specific_seats
    
    @property
    def reserved_capacity(self):
        """Calculate reserved capacity from actual seats."""
        # First try to find seats with this specific ticket type
        specific_seats = Seat.objects.filter(
            performance=self.section.performance,
            section=self.section.name,
            ticket_type=self.ticket_type,
            status='reserved'
        ).count()
        
        # If no specific seats found, look for unassigned seats in this section
        if specific_seats == 0:
            unassigned_seats = Seat.objects.filter(
                performance=self.section.performance,
                section=self.section.name,
                ticket_type__isnull=True,  # Seats without ticket type assignment
                status='reserved'
            ).count()
            return unassigned_seats
        
        return specific_seats
    
    @property
    def sold_capacity(self):
        """Calculate sold capacity from actual seats."""
        # First try to find seats with this specific ticket type
        specific_seats = Seat.objects.filter(
            performance=self.section.performance,
            section=self.section.name,
            ticket_type=self.ticket_type,
            status='sold'
        ).count()
        
        # If no specific seats found, look for unassigned seats in this section
        if specific_seats == 0:
            unassigned_seats = Seat.objects.filter(
                performance=self.section.performance,
                section=self.section.name,
                ticket_type__isnull=True,  # Seats without ticket type assignment
                status='sold'
            ).count()
            return unassigned_seats
        
        return specific_seats
    
    def clean(self):
        super().clean()
        # Validate price modifier
        if self.price_modifier <= 0:
            raise ValidationError(_('Price modifier must be positive'))
        
        if self.price_modifier > 10:  # Maximum 10x price
            raise ValidationError(_('Price modifier cannot exceed 10'))
    
    @property
    def final_price(self):
        """Calculate final price for this ticket type in this section with validation."""
        try:
            base_price = self.section.base_price
            if base_price is None or base_price <= 0:
                return Decimal('0.00')
            
            price_modifier = self.price_modifier
            if price_modifier is None or price_modifier <= 0:
                return base_price
            
            final_price = base_price * price_modifier
            
            # Ensure final price is not negative
            if final_price < 0:
                return Decimal('0.00')
            
            return final_price
            
        except (TypeError, ValueError, AttributeError):
            # Fallback to base price if calculation fails
            return getattr(self.section, 'base_price', Decimal('0.00'))
    
    def can_reserve(self, count=1):
        """Check if this ticket type can reserve specified number of seats."""
        return self.available_capacity >= count
    
    def reserve_capacity(self, count=1):
        """Reserve capacity for this ticket type."""
        if not self.can_reserve(count):
            raise ValidationError(f'Cannot reserve {count} seats. Only {self.available_capacity} available.')
        
        # This method is now deprecated - use seat-level reservation instead
        # Capacity is calculated from actual seat status
        pass
    
    def release_capacity(self, count=1):
        """Release reserved capacity for this ticket type."""
        # This method is now deprecated - use seat-level release instead
        # Capacity is calculated from actual seat status
        pass
    
    def sell_capacity(self, count=1):
        """Sell capacity for this ticket type."""
        # This method is now deprecated - use seat-level sale instead
        # Capacity is calculated from actual seat status
        pass


class EventDiscount(BaseModel):
    """
    Event discounts and promotional codes.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='discounts',
        verbose_name=_('Event')
    )
    
    # Discount details
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Discount code'))
    name = models.CharField(max_length=255, verbose_name=_('Discount name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    # Discount type
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
        ('early_bird', _('Early Bird')),
        ('group', _('Group Booking')),
        ('loyalty', _('Loyalty')),
    ]
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
        verbose_name=_('Discount type')
    )
    
    # Discount value
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Discount value')
    )
    
    # Conditions
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Minimum amount')
    )
    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Maximum discount')
    )
    
    # Usage limits
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Maximum uses')
    )
    current_uses = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Current uses')
    )
    
    # Validity
    valid_from = models.DateTimeField(verbose_name=_('Valid from'))
    valid_until = models.DateTimeField(verbose_name=_('Valid until'))
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    
    class Meta:
        verbose_name = _('Event Discount')
        verbose_name_plural = _('Event Discounts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid(self):
        """Check if discount is valid."""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_until:
            return False
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        
        return True
    
    def calculate_discount(self, amount):
        """Calculate discount amount."""
        if not self.is_valid():
            return Decimal('0.00')
        
        if amount < self.min_amount:
            return Decimal('0.00')
        
        if self.discount_type == 'percentage':
            discount = amount * (self.discount_value / Decimal('100'))
        elif self.discount_type == 'fixed':
            discount = self.discount_value
        else:
            discount = Decimal('0.00')
        
        # Apply maximum discount limit
        if self.max_discount and discount > self.max_discount:
            discount = self.max_discount
        
        return discount
    
    def use_discount(self):
        """Mark discount as used."""
        if self.max_uses:
            self.current_uses += 1
            self.save()


class EventFee(BaseModel):
    """
    Event fees and charges.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='fees',
        verbose_name=_('Event')
    )
    
    # Fee details
    name = models.CharField(max_length=255, verbose_name=_('Fee name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    # Fee type
    FEE_TYPE_CHOICES = [
        ('service', _('Service Fee')),
        ('booking', _('Booking Fee')),
        ('processing', _('Processing Fee')),
        ('convenience', _('Convenience Fee')),
        ('tax', _('Tax')),
        ('vat', _('VAT')),
    ]
    fee_type = models.CharField(
        max_length=20,
        choices=FEE_TYPE_CHOICES,
        default='service',
        verbose_name=_('Fee type')
    )
    
    # Fee calculation
    FEE_CALCULATION_CHOICES = [
        ('percentage', _('Percentage of Amount')),
        ('fixed', _('Fixed Amount')),
        ('per_ticket', _('Per Ticket')),
        ('per_booking', _('Per Booking')),
    ]
    calculation_type = models.CharField(
        max_length=20,
        choices=FEE_CALCULATION_CHOICES,
        default='percentage',
        verbose_name=_('Calculation type')
    )
    
    # Fee value
    fee_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Fee value')
    )
    
    # Conditions
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Minimum amount')
    )
    max_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Maximum fee')
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    is_mandatory = models.BooleanField(default=True, verbose_name=_('Is mandatory'))
    
    class Meta:
        verbose_name = _('Event Fee')
        verbose_name_plural = _('Event Fees')
        ordering = ['fee_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_fee_type_display()})"
    
    def calculate_fee(self, amount, quantity=1):
        """Calculate fee amount."""
        if not self.is_active:
            return Decimal('0.00')
        
        if amount < self.min_amount:
            return Decimal('0.00')
        
        if self.calculation_type == 'percentage':
            fee = amount * (self.fee_value / Decimal('100'))
        elif self.calculation_type == 'fixed':
            fee = self.fee_value
        elif self.calculation_type == 'per_ticket':
            fee = self.fee_value * quantity
        elif self.calculation_type == 'per_booking':
            fee = self.fee_value
        else:
            fee = Decimal('0.00')
        
        # Apply maximum fee limit
        if self.max_fee and fee > self.max_fee:
            fee = self.max_fee
        
        return fee


class EventPricingRule(BaseModel):
    """
    Dynamic pricing rules for events.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='pricing_rules',
        verbose_name=_('Event')
    )
    
    # Rule details
    name = models.CharField(max_length=255, verbose_name=_('Rule name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    # Rule type
    RULE_TYPE_CHOICES = [
        ('early_bird', _('Early Bird')),
        ('last_minute', _('Last Minute')),
        ('peak_hour', _('Peak Hour')),
        ('off_peak', _('Off Peak')),
        ('weekend', _('Weekend')),
        ('holiday', _('Holiday')),
        ('capacity_based', _('Capacity Based')),
    ]
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPE_CHOICES,
        default='early_bird',
        verbose_name=_('Rule type')
    )
    
    # Price adjustment
    ADJUSTMENT_TYPE_CHOICES = [
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
        ('multiplier', _('Multiplier')),
    ]
    adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPE_CHOICES,
        default='percentage',
        verbose_name=_('Adjustment type')
    )
    
    adjustment_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Adjustment value')
    )
    
    # Conditions
    conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Conditions')
    )
    
    # Priority (higher number = higher priority)
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Priority')
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    
    class Meta:
        verbose_name = _('Event Pricing Rule')
        verbose_name_plural = _('Event Pricing Rules')
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"
    
    def applies_to(self, performance, **kwargs):
        """Check if rule applies to given performance."""
        if not self.is_active:
            return False
        
        # Check rule-specific conditions
        if self.rule_type == 'early_bird':
            return self._check_early_bird_conditions(performance)
        elif self.rule_type == 'last_minute':
            return self._check_last_minute_conditions(performance)
        elif self.rule_type == 'capacity_based':
            return self._check_capacity_conditions(performance)
        # Add more rule types as needed
        
        return True
    
    def calculate_adjustment(self, base_price):
        """Calculate price adjustment."""
        if self.adjustment_type == 'percentage':
            return base_price * (self.adjustment_value / Decimal('100'))
        elif self.adjustment_type == 'fixed':
            return self.adjustment_value
        elif self.adjustment_type == 'multiplier':
            return base_price * self.adjustment_value
        else:
            return Decimal('0.00')
    
    def _check_early_bird_conditions(self, performance):
        """Check early bird conditions."""
        from datetime import timedelta
        from django.utils import timezone
        
        days_before = self.conditions.get('days_before', 30)
        cutoff_date = performance.date - timedelta(days=days_before)
        
        return timezone.now().date() <= cutoff_date
    
    def _check_last_minute_conditions(self, performance):
        """Check last minute conditions."""
        from datetime import timedelta
        from django.utils import timezone
        
        days_before = self.conditions.get('days_before', 7)
        cutoff_date = performance.date - timedelta(days=days_before)
        
        return timezone.now().date() > cutoff_date
    
    def _check_capacity_conditions(self, performance):
        """Check capacity-based conditions."""
        occupancy_rate = performance.occupancy_rate
        min_occupancy = self.conditions.get('min_occupancy', 0)
        max_occupancy = self.conditions.get('max_occupancy', 100)
        
        return min_occupancy <= occupancy_rate <= max_occupancy 