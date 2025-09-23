"""
Core models for Peykan Tourism Platform.
Following Clean Architecture and DDD principles.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from parler.models import TranslatableModel, TranslatedFields


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and common fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    class Meta:
        abstract = True
        ordering = ['-created_at']


class BaseTranslatableModel(BaseModel, TranslatableModel):
    """
    Abstract base model with translation support and slug field.
    """
    slug = models.SlugField(unique=True, max_length=255, verbose_name=_('Slug'))
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from title/name field
            title_field = getattr(self, 'title', None) or getattr(self, 'name', None)
            if title_field:
                self.slug = slugify(title_field, allow_unicode=True)
        super().save(*args, **kwargs)


class BaseProductModel(BaseTranslatableModel):
    """
    Abstract base model for all product types (tours, events, transfers).
    """
    # Common fields
    image = models.ImageField(
        upload_to='products/', 
        null=True, 
        blank=True, 
        verbose_name=_('Image')
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Base price (USD)'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    
    # Location fields
    city = models.CharField(max_length=100, verbose_name=_('City'))
    country = models.CharField(max_length=100, verbose_name=_('Country'))
    
    # Status fields
    is_featured = models.BooleanField(default=False, verbose_name=_('Is featured'))
    is_popular = models.BooleanField(default=False, verbose_name=_('Is popular'))
    is_special = models.BooleanField(
        default=False,
        verbose_name=_('Is special'),
        help_text=_('Mark as special tour for premium display on homepage')
    )
    is_seasonal = models.BooleanField(
        default=False,
        verbose_name=_('Is seasonal'),
        help_text=_('Mark as seasonal tour (summer/winter specials, holidays, etc.)')
    )
    
    class Meta:
        abstract = True

    def __str__(self):
        return self.title or self.slug

    def get_image_url(self, request=None):
        """Get image URL with fallback to default image."""
        if self.image:
            if request:
                return request.build_absolute_uri(self.image.url)
            return self.image.url
        return '/media/defaults/no-image.png'

    def clean(self):
        super().clean()
        if self.price is not None and self.price < 0:
            raise ValidationError(_('Price cannot be negative.'))


class BaseVariantModel(BaseModel):
    """
    Abstract base model for product variants (ticket types, vehicle types, etc.).
    """
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    price_modifier = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=0.00, 
        verbose_name=_('Price modifier')
    )
    capacity = models.PositiveIntegerField(verbose_name=_('Capacity'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class BaseBookingModel(BaseModel):
    """
    Abstract base model for booking-related models.
    """
    # Booking details
    booking_date = models.DateField(verbose_name=_('Booking date'))
    booking_time = models.TimeField(verbose_name=_('Booking time'))
    participants_count = models.PositiveIntegerField(default=1, verbose_name=_('Participants count'))
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Unit price'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total price'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    
    # Status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * self.participants_count
        super().save(*args, **kwargs)


class BaseOptionModel(BaseModel):
    """
    Abstract base model for product options (extras, add-ons).
    """
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class BaseScheduleModel(BaseModel):
    """
    Abstract base model for scheduling (performances, availability).
    """
    start_date = models.DateField(verbose_name=_('Start date'))
    end_date = models.DateField(verbose_name=_('End date'))
    start_time = models.TimeField(verbose_name=_('Start time'))
    end_time = models.TimeField(verbose_name=_('End time'))
    
    # Availability
    is_available = models.BooleanField(default=True, verbose_name=_('Is available'))
    max_capacity = models.PositiveIntegerField(verbose_name=_('Maximum capacity'))
    current_capacity = models.PositiveIntegerField(default=0, verbose_name=_('Current capacity'))

    class Meta:
        abstract = True

    @property
    def available_capacity(self):
        return self.max_capacity - self.current_capacity

    @property
    def is_full(self):
        return self.current_capacity >= self.max_capacity

    def can_book(self, count=1):
        return self.is_available and self.available_capacity >= count

    def book_capacity(self, count=1):
        if self.can_book(count):
            self.current_capacity += count
            self.save()
            return True
        return False

    def release_capacity(self, count=1):
        if self.current_capacity >= count:
            self.current_capacity -= count
            self.save()
            return True
        return False 


class SystemSettings(BaseModel):
    """
    System-wide settings for cart and order management.
    """
    
    # Cart limits
    cart_max_items_guest = models.PositiveIntegerField(
        default=3,
        verbose_name=_('Guest cart max items')
    )
    cart_max_total_guest = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500.00,
        verbose_name=_('Guest cart max total (USD)')
    )
    cart_max_items_user = models.PositiveIntegerField(
        default=10,
        verbose_name=_('User cart max items')
    )
    cart_max_total_user = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5000.00,
        verbose_name=_('User cart max total (USD)')
    )
    cart_max_carts_guest = models.PositiveIntegerField(
        default=20,
        verbose_name=_('Guest max carts')
    )
    cart_rate_limit_guest = models.PositiveIntegerField(
        default=30,
        verbose_name=_('Guest rate limit (requests/minute)')
    )
    cart_rate_limit_user = models.PositiveIntegerField(
        default=20,
        verbose_name=_('User rate limit (requests/minute)')
    )
    
    # Order limits
    order_max_pending_per_user = models.PositiveIntegerField(
        default=3,
        verbose_name=_('Max pending orders per user')
    )
    order_max_pending_per_product = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Max pending orders per product')
    )
    
    # Capacity management
    capacity_check_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Enable capacity checks')
    )
    capacity_reservation_duration = models.PositiveIntegerField(
        default=30,
        verbose_name=_('Capacity reservation duration (minutes)')
    )
    
    # Guest user limits
    guest_infant_max = models.PositiveIntegerField(
        default=2,
        verbose_name=_('Max infants per booking')
    )
    guest_booking_timeout = models.PositiveIntegerField(
        default=15,
        verbose_name=_('Guest booking timeout (minutes)')
    )
    
    class Meta:
        verbose_name = _('System Settings')
        verbose_name_plural = _('System Settings')
    
    def __str__(self):
        return f"System Settings (ID: {self.id})"
    
    @classmethod
    def get_settings(cls):
        """Get current system settings, create default if none exists."""
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'cart_max_items_guest': 3,
                'cart_max_total_guest': 1000.00,
                'cart_max_carts_guest': 20,
                'cart_rate_limit_guest': 30,
                'cart_rate_limit_user': 20,
                'order_max_pending_per_user': 3,
                'order_max_pending_per_product': 1,
                'capacity_check_enabled': True,
                'capacity_reservation_duration': 30,
                'guest_infant_max': 2,
                'guest_booking_timeout': 15,
            }
        )
        return settings 