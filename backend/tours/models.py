"""
Tour models for Peykan Tourism Platform.
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from core.models import BaseProductModel, BaseVariantModel, BaseScheduleModel, BaseOptionModel, BaseModel, BaseTranslatableModel, BaseBookingModel
from parler.models import TranslatedFields


class TourGallery(BaseModel):
    """Model for tour gallery images."""
    
    tour = models.ForeignKey(
        'Tour',
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name=_('Tour')
    )
    image = models.ImageField(
        upload_to='tours/gallery/',
        verbose_name=_('Image')
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Image Title')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Image Description')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display Order')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    
    class Meta:
        verbose_name = _('Tour Gallery Image')
        verbose_name_plural = _('Tour Gallery Images')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.tour.title} - {self.title or 'Gallery Image'}"
    
    @property
    def image_url(self):
        """Get the image URL."""
        if self.image:
            return self.image.url
        return None


class TourCancellationPolicy(BaseModel):
    """
    Cancellation policy for tours.
    Allows multiple policies per tour with different time frames.
    """
    tour = models.ForeignKey(
        'Tour',
        on_delete=models.CASCADE,
        related_name='cancellation_policies',
        verbose_name=_('Tour')
    )
    
    hours_before = models.PositiveIntegerField(
        verbose_name=_('Hours before tour start'),
        help_text=_('Number of hours before tour start when this policy applies')
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
        verbose_name = _('Tour Cancellation Policy')
        verbose_name_plural = _('Tour Cancellation Policies')
        ordering = ['-hours_before']  # Order by hours_before descending
        unique_together = ['tour', 'hours_before']
    
    def __str__(self):
        return f"{self.tour} - {self.hours_before}h: {self.refund_percentage}%"


class TourCategory(BaseTranslatableModel):
    """
    Tour categories (historical, recreational, etc.).
    """
    
    # Translatable fields
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_('Name')),
        description=models.TextField(verbose_name=_('Description')),
    )
    
    # Category specific fields
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Icon'))
    color = models.CharField(max_length=7, default='#007bff', verbose_name=_('Color'))
    
    class Meta:
        verbose_name = _('Tour Category')
        verbose_name_plural = _('Tour Categories')
    
    def __str__(self):
        try:
            return self.name or self.slug
        except:
            return self.slug


class Tour(BaseProductModel):
    """
    Tour model with all required features.
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
    
    # Tour specific fields
    category = models.ForeignKey(
        TourCategory, 
        on_delete=models.CASCADE, 
        related_name='tours',
        verbose_name=_('Category')
    )
    
    # Tour attributes
    TOUR_TYPE_CHOICES = [
        ('day', _('Day tour')),
        ('night', _('Night tour')),
    ]
    tour_type = models.CharField(
        max_length=10, 
        choices=TOUR_TYPE_CHOICES, 
        default='day',
        verbose_name=_('Tour type')
    )
    
    TRANSPORT_TYPE_CHOICES = [
        ('boat', _('Boat')),
        ('land', _('Land')),
        ('air', _('Air')),
    ]
    transport_type = models.CharField(
        max_length=10, 
        choices=TRANSPORT_TYPE_CHOICES, 
        default='land',
        verbose_name=_('Transport type')
    )
    
    # Duration and timing
    duration_hours = models.PositiveIntegerField(verbose_name=_('Duration (hours)'))
    pickup_time = models.TimeField(verbose_name=_('Pickup time'))
    start_time = models.TimeField(verbose_name=_('Start time'))
    end_time = models.TimeField(verbose_name=_('End time'))
    
    # Booking settings
    min_participants = models.PositiveIntegerField(default=1, verbose_name=_('Minimum participants'))
    max_participants = models.PositiveIntegerField(verbose_name=_('Maximum participants'))
    booking_cutoff_hours = models.PositiveIntegerField(default=8, verbose_name=_('Booking cutoff (hours)'))
    
    # Cancellation policy
    cancellation_hours = models.PositiveIntegerField(default=48, verbose_name=_('Cancellation hours'))
    refund_percentage = models.PositiveIntegerField(
        default=50, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Refund percentage')
    )
    
    # Services included
    includes_transfer = models.BooleanField(default=True, verbose_name=_('Includes transfer'))
    includes_guide = models.BooleanField(default=True, verbose_name=_('Includes guide'))
    includes_meal = models.BooleanField(default=True, verbose_name=_('Includes meal'))
    includes_photographer = models.BooleanField(default=False, verbose_name=_('Includes photographer'))

    # Additional status fields for tour promotion
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
    
    def get_gallery_images(self):
        """Get gallery images as a list of image objects."""
        return self.gallery_images.all().order_by('order', 'created_at')
    
    class Meta:
        verbose_name = _('Tour')
        verbose_name_plural = _('Tours')
    
    def __str__(self):
        try:
            return self.title or self.slug
        except:
            return self.slug
    
    @property
    def is_available_today(self):
        """Check if tour has available schedules in the future."""
        from datetime import date
        today = date.today()
        return self.schedules.filter(
            start_date__gte=today,
            is_available=True
        ).exists()
    
    def create_default_schedule(self):
        """Create a default schedule for the tour if none exists."""
        from datetime import date, timedelta
        from django.utils import timezone
        from django.db import transaction
        
        # If schedules already exist, don't create a default one
        if self.schedules.exists():
            return None
            
        # Find the next available date starting from tomorrow
        tomorrow = date.today() + timedelta(days=1)
        next_date = tomorrow
        
        # Try up to 7 days in the future to find an available date
        for i in range(7):
            if not self.schedules.filter(start_date=next_date).exists():
                try:
                    with transaction.atomic():
                        default_schedule = TourSchedule(
                            tour=self,
                            start_date=next_date,
                            end_date=next_date,
                            start_time=self.start_time,
                            end_time=self.end_time,
                            day_of_week=next_date.weekday(),
                            is_available=True,
                            max_capacity=self.max_participants
                        )
                        default_schedule.full_clean()  # Validate before saving
                        default_schedule.save()
                        return default_schedule
                except Exception as e:
                    if not transaction.get_autocommit():
                        raise
                    print(f"Error creating default schedule for {next_date}: {str(e)}")
            next_date += timedelta(days=1)
            
        return None
    
    def clean(self):
        """Custom validation for Tour model."""
        super().clean()
        
        # Validate required fields (only non-translatable fields)
        if not self.category:
            raise ValidationError(_('Category is required.'))
        
        if not self.city:
            raise ValidationError(_('City is required.'))
        
        if not self.country:
            raise ValidationError(_('Country is required.'))
        
        if not self.price:
            raise ValidationError(_('Price is required.'))
        
        if not self.duration_hours:
            raise ValidationError(_('Duration is required.'))
        
        if not self.start_time:
            raise ValidationError(_('Start time is required.'))
        
        if not self.end_time:
            raise ValidationError(_('End time is required.'))
        
        if not self.max_participants:
            raise ValidationError(_('Maximum participants is required.'))
        
        # Validate timing logic
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(_('End time must be after start time.'))
        
        # Validate capacity logic
        if self.min_participants and self.max_participants and self.min_participants > self.max_participants:
            raise ValidationError(_('Minimum participants cannot exceed maximum participants.'))
        
        # Validate duration logic
        if self.duration_hours and self.duration_hours <= 0:
            raise ValidationError(_('Duration must be greater than zero.'))
        
        # Validate pickup time logic
        if self.pickup_time and self.start_time and self.pickup_time >= self.start_time:
            raise ValidationError(_('Pickup time must be before start time.'))
        
        # Validate that at least one variant exists
        if self.pk and not self.variants.exists():
            raise ValidationError(_('Tour must have at least one variant.'))
    
    def validate_schedules(self):
        """Validate that tour schedules don't have conflicts."""
        from django.core.exceptions import ValidationError
        
        if not self.pk:
            return  # Can't validate schedules for unsaved tours
        
        schedules = self.schedules.all()
        for i, schedule1 in enumerate(schedules):
            for j, schedule2 in enumerate(schedules):
                if i != j:
                    # Check for overlapping dates
                    if (schedule1.start_date <= schedule2.end_date and 
                        schedule2.start_date <= schedule1.end_date):
                        raise ValidationError({
                            'schedules': f'Schedule conflict detected between {schedule1.start_date} and {schedule2.start_date}'
                        })
    
    def get_available_schedules(self, start_date=None, end_date=None):
        """Get available schedules within a date range."""
        from datetime import date
        
        if not start_date:
            start_date = date.today()
        
        schedules = self.schedules.filter(
            start_date__gte=start_date,
            is_available=True
        )
        
        if end_date:
            schedules = schedules.filter(start_date__lte=end_date)
        
        return schedules.order_by('start_date')
    
    def get_next_available_schedule(self):
        """Get the next available schedule."""
        from datetime import date
        
        return self.schedules.filter(
            start_date__gte=date.today(),
            is_available=True
        ).order_by('start_date').first()
    
    def get_total_capacity(self):
        """Get total capacity across all variants."""
        return sum(variant.capacity for variant in self.variants.filter(is_active=True))
    
    def get_available_capacity(self, date):
        """Get available capacity for a specific date."""
        schedule = self.schedules.filter(start_date=date, is_available=True).first()
        if schedule:
            return schedule.available_capacity
        return 0
    
    def is_available_on_date(self, date):
        """Check if tour is available on a specific date."""
        return self.schedules.filter(
            start_date=date,
            is_available=True
        ).exists()
    
    def get_completion_status(self):
        """
        Get comprehensive completion status for tour setup.
        Returns dict with completion details and missing items.
        """
        status = {
            'is_complete': True,
            'completion_percentage': 0,
            'missing_items': [],
            'warnings': [],
            'details': {}
        }
        
        total_checks = 0
        passed_checks = 0
        
        # 1. Basic Information Check
        total_checks += 1
        basic_info_complete = all([
            self.title,
            self.description,
            self.category,
            self.city,
            self.country,
            self.duration_hours,
            self.start_time,
            self.end_time,
            self.max_participants
        ])
        if basic_info_complete:
            passed_checks += 1
            status['details']['basic_info'] = {'status': 'complete', 'message': 'All basic information is provided'}
        else:
            status['is_complete'] = False
            status['missing_items'].append('Basic tour information (title, description, category, location, timing)')
            status['details']['basic_info'] = {'status': 'incomplete', 'message': 'Missing basic information'}
        
        # 2. Variants Check
        total_checks += 1
        variants = self.variants.filter(is_active=True)
        if variants.exists():
            passed_checks += 1
            status['details']['variants'] = {
                'status': 'complete', 
                'message': f'{variants.count()} active variants configured',
                'count': variants.count()
            }
            
            # Check if variants have proper pricing
            variants_with_pricing = 0
            for variant in variants:
                if variant.pricing.exists():
                    variants_with_pricing += 1
            
            if variants_with_pricing < variants.count():
                status['warnings'].append(f'Some variants ({variants.count() - variants_with_pricing}) are missing pricing configuration')
        else:
            status['is_complete'] = False
            status['missing_items'].append('Tour variants (at least one active variant required)')
            status['details']['variants'] = {'status': 'incomplete', 'message': 'No active variants configured'}
        
        # 3. Schedules Check
        total_checks += 1
        schedules = self.schedules.filter(is_available=True)
        if schedules.exists():
            passed_checks += 1
            status['details']['schedules'] = {
                'status': 'complete',
                'message': f'{schedules.count()} available schedules configured',
                'count': schedules.count()
            }
            
            # Check if schedules have variant capacities
            schedules_with_capacities = 0
            for schedule in schedules:
                if schedule.variant_capacities.exists():
                    schedules_with_capacities += 1
            
            if schedules_with_capacities < schedules.count():
                status['warnings'].append(f'Some schedules ({schedules.count() - schedules_with_capacities}) are missing variant capacity configuration')
        else:
            status['is_complete'] = False
            status['missing_items'].append('Tour schedules (at least one available schedule required)')
            status['details']['schedules'] = {'status': 'incomplete', 'message': 'No available schedules configured'}
        
        # 4. Pricing Check
        total_checks += 1
        pricing_complete = True
        for variant in variants:
            if not variant.pricing.exists():
                pricing_complete = False
                break
        
        if pricing_complete and variants.exists():
            passed_checks += 1
            status['details']['pricing'] = {'status': 'complete', 'message': 'All variants have pricing configured'}
        else:
            status['is_complete'] = False
            status['missing_items'].append('Pricing configuration for all variants')
            status['details']['pricing'] = {'status': 'incomplete', 'message': 'Some variants missing pricing'}
        
        # 5. Capacity Check
        total_checks += 1
        capacity_complete = True
        for schedule in schedules:
            if not schedule.variant_capacities.exists():
                capacity_complete = False
                break
        
        if capacity_complete and schedules.exists():
            passed_checks += 1
            status['details']['capacity'] = {'status': 'complete', 'message': 'All schedules have capacity configured'}
        else:
            status['is_complete'] = False
            status['missing_items'].append('Capacity configuration for all schedules')
            status['details']['capacity'] = {'status': 'incomplete', 'message': 'Some schedules missing capacity'}
        
        # 6. Gallery Check (Optional but recommended)
        total_checks += 1
        gallery_images = self.gallery_images.filter(is_active=True)
        if gallery_images.exists():
            passed_checks += 1
            status['details']['gallery'] = {
                'status': 'complete',
                'message': f'{gallery_images.count()} gallery images configured',
                'count': gallery_images.count()
            }
        else:
            status['warnings'].append('No gallery images configured (recommended for better presentation)')
            status['details']['gallery'] = {'status': 'warning', 'message': 'No gallery images configured'}
        
        # 7. Itinerary Check (Optional but recommended)
        total_checks += 1
        itinerary_items = self.itinerary.all()
        if itinerary_items.exists():
            passed_checks += 1
            status['details']['itinerary'] = {
                'status': 'complete',
                'message': f'{itinerary_items.count()} itinerary items configured',
                'count': itinerary_items.count()
            }
        else:
            status['warnings'].append('No itinerary configured (recommended for better tour description)')
            status['details']['itinerary'] = {'status': 'warning', 'message': 'No itinerary configured'}
        
        # Calculate completion percentage
        status['completion_percentage'] = round((passed_checks / total_checks) * 100, 1)
        
        return status
    
    def get_setup_recommendations(self):
        """
        Get specific recommendations for completing tour setup.
        """
        recommendations = []
        status = self.get_completion_status()
        
        if not status['is_complete']:
            recommendations.extend([
                {
                    'type': 'error',
                    'title': 'Required Setup Items',
                    'items': status['missing_items']
                }
            ])
        
        if status['warnings']:
            recommendations.append({
                'type': 'warning',
                'title': 'Recommended Improvements',
                'items': status['warnings']
            })
        
        # Specific recommendations based on current state
        if not self.variants.filter(is_active=True).exists():
            recommendations.append({
                'type': 'action',
                'title': 'Create Tour Variants',
                'description': 'Create at least one variant (e.g., Standard, VIP) with different pricing and services',
                'action': 'create_variants'
            })
        
        if not self.schedules.filter(is_available=True).exists():
            recommendations.append({
                'type': 'action',
                'title': 'Create Tour Schedules',
                'description': 'Create available schedules with specific dates and times',
                'action': 'create_schedules'
            })
        
        variants = self.variants.filter(is_active=True)
        for variant in variants:
            if not variant.pricing.exists():
                recommendations.append({
                    'type': 'action',
                    'title': f'Configure Pricing for {variant.name}',
                    'description': 'Set up age-based pricing (adult, child, infant) for this variant',
                    'action': 'configure_pricing',
                    'variant_id': variant.id
                })
        
        schedules = self.schedules.filter(is_available=True)
        for schedule in schedules:
            if not schedule.variant_capacities.exists():
                recommendations.append({
                    'type': 'action',
                    'title': f'Configure Capacity for {schedule.start_date}',
                    'description': 'Set up capacity limits for each variant on this schedule',
                    'action': 'configure_capacity',
                    'schedule_id': schedule.id
                })
        
        return recommendations


class TourVariant(BaseVariantModel):
    """
    Tour variants (Eco, Normal, VIP, VVIP).
    """
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='variants',
        verbose_name=_('Tour')
    )
    
    # Base price for this variant (replaces price_modifier)
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name=_('Base price (USD)')
    )
    
    # Variant specific fields
    includes_transfer = models.BooleanField(default=True, verbose_name=_('Includes transfer'))
    includes_guide = models.BooleanField(default=True, verbose_name=_('Includes guide'))
    includes_meal = models.BooleanField(default=True, verbose_name=_('Includes meal'))
    includes_photographer = models.BooleanField(default=False, verbose_name=_('Includes photographer'))
    
    # Extended services
    extended_hours = models.PositiveIntegerField(default=0, verbose_name=_('Extended hours'))
    private_transfer = models.BooleanField(default=False, verbose_name=_('Private transfer'))
    expert_guide = models.BooleanField(default=False, verbose_name=_('Expert guide'))
    special_meal = models.BooleanField(default=False, verbose_name=_('Special meal'))
    
    class Meta:
        verbose_name = _('Tour Variant')
        verbose_name_plural = _('Tour Variants')
        unique_together = ['tour', 'name']
    
    def __str__(self):
        try:
            return f"{self.tour.title} - {self.name}"
        except:
            return f"{self.tour.slug} - {self.name}"
    
    def clean(self):
        """Validate variant data."""
        from django.core.exceptions import ValidationError
        
        # Validate base_price
        if self.base_price is None or self.base_price <= 0:
            raise ValidationError({
                'base_price': 'Base price must be greater than zero.'
            })
        
        # Validate name uniqueness within tour
        if self.pk is None:  # Only check on creation
            if TourVariant.objects.filter(tour=self.tour, name=self.name).exists():
                raise ValidationError({
                    'name': 'A variant with this name already exists for this tour.'
                })
        
        # Validate that total variant capacity doesn't exceed tour max_participants
        if self.tour and self.capacity:
            total_capacity = sum(
                v.capacity for v in self.tour.variants.all() if v.pk != self.pk
            ) + self.capacity
            
            if total_capacity > self.tour.max_participants:
                raise ValidationError({
                    'capacity': f'Total variant capacity ({total_capacity}) cannot exceed tour maximum participants ({self.tour.max_participants})'
                })
    
    def validate_pricing(self):
        """Validate that variant has proper pricing for all age groups."""
        from django.core.exceptions import ValidationError
        
        if not self.pk:
            return  # Can't validate pricing for unsaved variants
        
        # Check if pricing exists for all age groups
        age_groups = ['infant', 'child', 'adult']
        existing_pricing = set(self.pricing.values_list('age_group', flat=True))
        
        missing_groups = set(age_groups) - existing_pricing
        if missing_groups:
            raise ValidationError({
                'pricing': f'Missing pricing for age groups: {", ".join(missing_groups)}'
            })
    
    def get_price_for_age_group(self, age_group):
        """Get price for a specific age group."""
        pricing = self.pricing.filter(age_group=age_group).first()
        if pricing:
            return pricing.final_price
        return self.base_price
    
    def get_total_price_for_participants(self, adult_count=0, child_count=0, infant_count=0):
        """Calculate total price for given participant counts."""
        total = 0
        
        if adult_count > 0:
            total += self.get_price_for_age_group('adult') * adult_count
        
        if child_count > 0:
            total += self.get_price_for_age_group('child') * child_count
        
        if infant_count > 0:
            total += self.get_price_for_age_group('infant') * infant_count
        
        return total
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation."""
        self.full_clean()
        super().save(*args, **kwargs)


class TourSchedule(BaseScheduleModel):
    """
    Tour schedules with availability tracking.
    """
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='schedules',
        verbose_name=_('Tour')
    )
    
    # Schedule specific fields
    day_of_week = models.PositiveIntegerField(
        choices=[
            (0, _('Monday')),
            (1, _('Tuesday')),
            (2, _('Wednesday')),
            (3, _('Thursday')),
            (4, _('Friday')),
            (5, _('Saturday')),
            (6, _('Sunday')),
        ],
        verbose_name=_('Day of week')
    )
    
    # Schedule-specific variants (new field)
    available_variants = models.ManyToManyField(
        'TourVariant',
        blank=True,
        related_name='schedules',
        verbose_name=_('Available Variants'),
        help_text=_('Variants available for this specific schedule. If empty, all tour variants are available.')
    )

    # Availability settings
    availability_override = models.BooleanField(
        default=False,
        verbose_name=_('Override availability')
    )
    availability_note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Availability Note')
    )

    # New capacity tracking fields for better performance and atomicity
    total_reserved_capacity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Reserved Capacity'),
        help_text=_('Total capacity currently reserved in carts and pending orders')
    )
    total_confirmed_capacity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Confirmed Capacity'),
        help_text=_('Total capacity confirmed in paid orders')
    )
    
    # Price adjustment for specific dates
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Price Adjustment')
    )
    price_adjustment_type = models.CharField(
        max_length=10,
        choices=[
            ('fixed', _('Fixed Amount')),
            ('percentage', _('Percentage')),
        ],
        default='fixed',
        verbose_name=_('Adjustment Type')
    )

    # Legacy JSON field - will be removed after migration
    variant_capacities_raw = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_('Variant capacities (Legacy)'),
        help_text=_('Legacy field - will be removed after migration to relational model')
    )
    
    class Meta:
        verbose_name = _('Tour Schedule')
        verbose_name_plural = _('Tour Schedules')
        unique_together = ['tour', 'start_date']
    
    def __str__(self):
        return f"{self.tour.title} - {self.start_date}"
    
    def clean(self):
        """Validate schedule data."""
        from django.core.exceptions import ValidationError
        
        # Ensure end_date is not before start_date
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'End date cannot be before start date.'
            })
        
        # Ensure end_time is not before start_time if dates are the same
        if (self.end_date == self.start_date and 
            self.end_time and self.start_time and 
            self.end_time < self.start_time):
            raise ValidationError({
                'end_time': 'End time cannot be before start time for the same date.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-calculate day of week from start_date
        if self.start_date:
            self.day_of_week = self.start_date.weekday()

        # Ensure variant_capacities_raw keys are strings before saving
        if self.variant_capacities_raw:
            self.variant_capacities_raw = {str(k): v for k, v in self.variant_capacities_raw.items()}
        
        # Auto-set end_date if not provided (same as start_date for single-day tours)
        if not self.end_date:
            self.end_date = self.start_date
            
        # Auto-set end_time if not provided (same as start_time for single-day tours)
        if not self.end_time:
            self.end_time = self.start_time

        # Check for existing schedule with same tour and date
        from django.db import IntegrityError
        try:
            if self.pk:  # If this is an update
                existing = TourSchedule.objects.filter(
                    tour=self.tour,
                    start_date=self.start_date
                ).exclude(pk=self.pk).exists()
            else:  # If this is a new schedule
                existing = TourSchedule.objects.filter(
                    tour=self.tour,
                    start_date=self.start_date
                ).exists()
                
            if existing:
                raise IntegrityError("A schedule already exists for this tour and date")
                
            super().save(*args, **kwargs)
        except IntegrityError as e:
            from django.core.exceptions import ValidationError
            raise ValidationError(str(e))

    @property
    def variant_capacities(self):
        """Safe property that always returns string keys."""
        orig = self.variant_capacities_raw
        if not isinstance(orig, dict):
            return {}
        return {str(k): v for k, v in orig.items()}

    def initialize_variant_capacities(self):
        """Ensure variant capacities JSON has totals per active variant.
        Structure per variant_id: { 'total': capacity, 'booked': 0, 'available': capacity }
        Only initializes variants that are already in variant_capacities_raw or are explicitly added.
        """
        from .models import TourVariant  # local import to avoid circulars
        capacities = self.variant_capacities_raw or {}
        changed = False
        
        # Only process variants that are already in capacities or explicitly added
        for variant in self.tour.variants.filter(is_active=True):
            key = str(variant.id)
            if key in capacities:
                # Update existing variant capacity if needed
                if not isinstance(capacities.get(key), dict):
                    capacities[key] = {
                        'total': int(getattr(variant, 'capacity', 0) or 0),
                        'booked': 0,
                        'available': int(getattr(variant, 'capacity', 0) or 0),
                    }
                    changed = True
                else:
                    total = int(getattr(variant, 'capacity', 0) or capacities[key].get('total', 0))
                    if capacities[key].get('total') != total:
                        # Adjust available relative to new total
                        booked = int(capacities[key].get('booked', 0))
                        capacities[key]['total'] = total
                        capacities[key]['available'] = max(0, total - booked)
                        changed = True
        
        if changed:
            self.variant_capacities_raw = {str(k): v for k, v in capacities.items()}
            self.save()

    def add_variant_capacity(self, variant_id: str, capacity: int):
        """Add a specific variant to this schedule's capacity."""
        capacities = self.variant_capacities_raw or {}
        capacities[str(variant_id)] = {
            'total': capacity,
            'booked': 0,
            'available': capacity,
        }
        self.variant_capacities_raw = capacities
        self.save()

    def remove_variant_capacity(self, variant_id: str):
        """Remove a specific variant from this schedule's capacity."""
        capacities = self.variant_capacities_raw or {}
        if str(variant_id) in capacities:
            del capacities[str(variant_id)]
            self.variant_capacities_raw = capacities
            self.save()
    
    def sync_variant_capacities(self):
        """Sync variant_capacities_raw with available_variants to prevent inconsistencies."""
        available_variant_ids = set(str(v.id) for v in self.get_available_variants())
        capacity_variant_ids = set(self.variant_capacities_raw.keys())

        # Remove variants that are no longer available
        for variant_id in capacity_variant_ids - available_variant_ids:
            if variant_id in self.variant_capacities_raw:
                del self.variant_capacities_raw[variant_id]

        # Add missing variants
        for variant in self.get_available_variants():
            variant_id = str(variant.id)
            if variant_id not in self.variant_capacities_raw:
                self.variant_capacities_raw[variant_id] = {
                    'total': variant.capacity,
                    'booked': 0,
                    'available': variant.capacity,
                }

        self.save()

    def validate_capacity_consistency(self) -> dict:
        """
        Validate consistency between variant_capacities and computed values.
        Returns dict with validation results.
        """
        result = {
            'is_consistent': True,
            'issues': [],
            'computed_total_capacity': self.compute_total_capacity(),
            'stored_available_capacity': self.available_capacity,
            'stored_booked_capacity': self.current_capacity,
        }

        # Check if stored capacities match computed values
        capacities = self.variant_capacities
        if capacities:
            stored_total = sum(v.get('total', 0) for v in capacities.values())
            stored_available = sum(v.get('available', 0) for v in capacities.values())
            stored_booked = sum(v.get('booked', 0) for v in capacities.values())

            if stored_total != result['computed_total_capacity']:
                result['is_consistent'] = False
                result['issues'].append(f'Total capacity mismatch: stored={stored_total}, computed={result["computed_total_capacity"]}')

            if stored_available != result['stored_available_capacity']:
                result['is_consistent'] = False
                result['issues'].append(f'Available capacity mismatch: stored={stored_available}, property={result["stored_available_capacity"]}')

            # Check booked vs available consistency per variant
            for variant_id, data in capacities.items():
                total = data.get('total', 0)
                booked = data.get('booked', 0)
                available = data.get('available', 0)

                if total != (booked + available):
                    result['is_consistent'] = False
                    result['issues'].append(f'Variant {variant_id}: total({total}) != booked({booked}) + available({available})')

        return result

    def compute_total_capacity(self) -> int:
        """Compute total capacity from new relational model."""
        try:
            # Use new relational model
            total = self.variant_capacities.aggregate(
                total=models.Sum('total_capacity')
            )['total'] or 0
            return int(total)
        except Exception:
            # Fallback to legacy data
            caps = self.variant_capacities_raw or {}
            if not caps:
                return 0
            return sum(int(v.get('total', 0) or 0) for v in caps.values())

    def book_variant_capacity(self, variant_id: str, qty: int) -> None:
        """Book capacity for a specific variant; adults+children only logic handled upstream."""
        if qty <= 0:
            return
        self.initialize_variant_capacities()
        key = str(variant_id)
        capacities = self.variant_capacities_raw or {}
        if key not in capacities:
            # Initialize with zeros to avoid KeyError
            capacities[key] = {'total': 0, 'booked': 0, 'available': 0}
        available = int(capacities[key].get('available', 0))
        if qty > available:
            raise ValueError("Insufficient capacity for the selected variant")
        capacities[key]['booked'] = int(capacities[key].get('booked', 0)) + qty
        capacities[key]['available'] = int(capacities[key].get('total', 0)) - int(capacities[key]['booked'])
        self.variant_capacities_raw = capacities
        self.save()

    def release_variant_capacity(self, variant_id: str, qty: int) -> None:
        if qty <= 0:
            return
        self.initialize_variant_capacities()
        key = str(variant_id)
        capacities = self.variant_capacities_raw or {}
        if key not in capacities:
            return
        booked = int(capacities[key].get('booked', 0))
        booked = max(0, booked - qty)
        capacities[key]['booked'] = booked
        capacities[key]['available'] = int(capacities[key].get('total', 0)) - booked
        self.variant_capacities_raw = capacities
        self.save()

    @property
    def available_capacity(self):
        """Get total available capacity from new relational model."""
        try:
            # Use new relational model - calculate manually since available_capacity is a property
            total_available = 0
            for capacity_obj in self.variant_capacities.all():
                total_available += capacity_obj.available_capacity
            return int(total_available)
        except Exception:
            # Fallback to legacy data
            try:
                capacities = self.variant_capacities_raw or {}
                if not capacities:
                    return self.compute_total_capacity()

                # Sum available capacity from all variants
                total_available = 0
                for variant_data in capacities.values():
                    available = variant_data.get('available', 0)
                    total_available += int(available) if available else 0

                return max(0, total_available)
            except Exception:
                # Final fallback: return total capacity (no bookings)
                return self.compute_total_capacity()
    @property
    def is_full(self):
        """Check if all variants are fully booked."""
        return self.available_capacity <= 0
    
    @property
    def utilization_percentage(self):
        """Calculate utilization percentage for the schedule."""
        total_capacity = self.compute_total_capacity()
        if total_capacity == 0:
            return 0
        
        used_capacity = (self.total_reserved_capacity or 0) + (self.total_confirmed_capacity or 0)
        return (used_capacity / total_capacity) * 100

    @property
    def current_capacity(self):
        """Get total current (booked) capacity across all variants."""
        total_booked = 0
        for variant_data in self.variant_capacities.values():
            total_booked += variant_data.get('booked', 0)
        return total_booked

    @property
    def max_capacity(self):
        """Get total maximum capacity across all variants."""
        return self.compute_total_capacity()

    def reserve_capacity_atomic(self, variant_id: str, quantity: int) -> bool:
        """
        Atomically reserve capacity for a variant.
        Returns True if successful, False if insufficient capacity.
        """
        from django.db import transaction
        from django.core.exceptions import ValidationError

        if quantity <= 0:
            return True

        with transaction.atomic():
            # Lock the schedule for update
            schedule = TourSchedule.objects.select_for_update().get(id=self.id)
            variant_id_str = str(variant_id)

            # Get current capacity data
            capacities = schedule.variant_capacities_raw or {}
            if variant_id_str not in capacities:
                # Initialize if missing
                from tours.models import TourVariant
                try:
                    variant = TourVariant.objects.get(id=variant_id, tour=schedule.tour)
                    capacities[variant_id_str] = {
                        'total': variant.capacity,
                        'booked': 0,
                        'available': variant.capacity
                    }
                except TourVariant.DoesNotExist:
                    return False

            available = capacities[variant_id_str].get('available', 0)
            if available < quantity:
                return False

            # Update capacity
            capacities[variant_id_str]['booked'] = capacities[variant_id_str].get('booked', 0) + quantity
            capacities[variant_id_str]['available'] = capacities[variant_id_str]['total'] - capacities[variant_id_str]['booked']

            schedule.variant_capacities_raw = capacities
            schedule.total_reserved_capacity += quantity
            schedule.save()

            return True

    def release_capacity_atomic(self, variant_id: str, quantity: int) -> bool:
        """
        Atomically release capacity for a variant.
        Returns True if successful.
        """
        from django.db import transaction

        if quantity <= 0:
            return True

        with transaction.atomic():
            # Lock the schedule for update
            schedule = TourSchedule.objects.select_for_update().get(id=self.id)
            variant_id_str = str(variant_id)

            capacities = schedule.variant_capacities_raw or {}
            if variant_id_str not in capacities:
                return False

            booked = capacities[variant_id_str].get('booked', 0)
            if booked < quantity:
                return False

            # Update capacity
            capacities[variant_id_str]['booked'] = booked - quantity
            capacities[variant_id_str]['available'] = capacities[variant_id_str]['total'] - capacities[variant_id_str]['booked']

            schedule.variant_capacities_raw = capacities
            schedule.total_reserved_capacity = max(0, schedule.total_reserved_capacity - quantity)
            schedule.save()

            return True

    def confirm_capacity_atomic(self, variant_id: str, quantity: int) -> bool:
        """
        Convert reserved capacity to confirmed capacity using new relational model.
        """
        from django.db import transaction

        if quantity <= 0:
            return True

        with transaction.atomic():
            schedule = TourSchedule.objects.select_for_update().get(id=self.id)
            
            try:
                # Use new relational model
                from .models import TourScheduleVariantCapacity
                capacity_obj = TourScheduleVariantCapacity.objects.select_for_update().get(
                    schedule=schedule, 
                    variant__id=variant_id
                )
                
                # Check if there's enough reserved capacity to confirm
                reserved = capacity_obj.reserved_capacity or 0
                if reserved < quantity:
                    # If not enough reserved, just add to confirmed (for direct confirmations)
                    capacity_obj.confirmed_capacity = (capacity_obj.confirmed_capacity or 0) + quantity
                else:
                    # Move from reserved to confirmed
                    capacity_obj.reserved_capacity = reserved - quantity
                    capacity_obj.confirmed_capacity = (capacity_obj.confirmed_capacity or 0) + quantity
                
                capacity_obj.save()
                
                # Update total counters
                schedule.total_reserved_capacity = max(0, (schedule.total_reserved_capacity or 0) - quantity)
                schedule.total_confirmed_capacity = (schedule.total_confirmed_capacity or 0) + quantity
                schedule.save()
                
                return True
                
            except TourScheduleVariantCapacity.DoesNotExist:
                # Fallback: create capacity object if it doesn't exist
                try:
                    from .models import TourVariant
                    variant = TourVariant.objects.get(id=variant_id, tour=schedule.tour)
                    
                    capacity_obj = TourScheduleVariantCapacity.objects.create(
                        schedule=schedule,
                        variant=variant,
                        total_capacity=variant.capacity,
                        reserved_capacity=0,
                        confirmed_capacity=quantity,
                        is_available=True
                    )
                    
                    # Update total counters
                    schedule.total_confirmed_capacity = (schedule.total_confirmed_capacity or 0) + quantity
                    schedule.save()
                    
                    return True
                    
                except TourVariant.DoesNotExist:
                    return False

    def cancel_capacity_atomic(self, variant_id: str, quantity: int) -> bool:
        """
        Release confirmed capacity (e.g., when order is cancelled).
        """
        from django.db import transaction

        if quantity <= 0:
            return True

        with transaction.atomic():
            schedule = TourSchedule.objects.select_for_update().get(id=self.id)
            variant_id_str = str(variant_id)

            # Get current capacity data
            capacities = schedule.variant_capacities_raw or {}
            if variant_id_str in capacities:
                # Update variant level capacity
                capacities[variant_id_str]['booked'] = max(0, capacities[variant_id_str].get('booked', 0) - quantity)
                capacities[variant_id_str]['available'] = capacities[variant_id_str]['total'] - capacities[variant_id_str]['booked']
                schedule.variant_capacities_raw = capacities

            # Release confirmed capacity at total level
            schedule.total_confirmed_capacity = max(0, schedule.total_confirmed_capacity - quantity)
            schedule.save()

            return True
    
    def get_available_variants(self):
        """Get variants available for this schedule."""
        if self.available_variants.exists():
            # Return only schedule-specific variants
            return self.available_variants.filter(is_active=True)
        else:
            # Return all tour variants if no specific variants are set
            return self.tour.variants.filter(is_active=True)
    
    def is_variant_available(self, variant):
        """Check if a variant is available for this schedule."""
        if self.available_variants.exists():
            return self.available_variants.filter(id=variant.id).exists()
        else:
            return True  # All variants available if none specified


class TourScheduleVariantCapacity(BaseModel):
    """
    Relational model for managing variant capacities in each schedule.
    Replaces the JSONField approach with proper relational structure.
    """
    
    schedule = models.ForeignKey(
        TourSchedule, 
        on_delete=models.CASCADE,
        related_name='variant_capacities',
        verbose_name=_('Schedule')
    )
    variant = models.ForeignKey(
        TourVariant,
        on_delete=models.CASCADE,
        related_name='schedule_capacities',
        verbose_name=_('Variant')
    )
    
    # Capacity fields
    total_capacity = models.PositiveIntegerField(
        verbose_name=_('Total Capacity'),
        help_text=_('Maximum capacity for this variant on this schedule')
    )
    reserved_capacity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Reserved Capacity'),
        help_text=_('Capacity currently reserved in carts and pending orders')
    )
    confirmed_capacity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Confirmed Capacity'),
        help_text=_('Capacity confirmed in paid orders')
    )
    
    # Schedule-specific pricing adjustments
    price_adjustment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Price Adjustment'),
        help_text=_('Additional price adjustment for this variant on this schedule')
    )
    price_adjustment_type = models.CharField(
        max_length=10,
        choices=[
            ('fixed', _('Fixed Amount')),
            ('percentage', _('Percentage')),
        ],
        default='fixed',
        verbose_name=_('Adjustment Type')
    )
    
    # Availability settings
    is_available = models.BooleanField(
        default=True, 
        verbose_name=_('Available'),
        help_text=_('Whether this variant is available for this schedule')
    )
    availability_note = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name=_('Availability Note'),
        help_text=_('Optional note about availability (e.g., "Few seats left")')
    )
    
    class Meta:
        verbose_name = _('Schedule Variant Capacity')
        verbose_name_plural = _('Schedule Variant Capacities')
        unique_together = ['schedule', 'variant']
        ordering = ['schedule', 'variant__name']
    
    def __str__(self):
        return f"{self.schedule.tour.title} - {self.schedule.start_date} - {self.variant.name}"
    
    def clean(self):
        """Validate capacity data."""
        from django.core.exceptions import ValidationError
        
        # Validate capacity values
        if self.total_capacity < 0:
            raise ValidationError(_('Total capacity cannot be negative.'))
        
        if self.reserved_capacity < 0:
            raise ValidationError(_('Reserved capacity cannot be negative.'))
        
        if self.confirmed_capacity < 0:
            raise ValidationError(_('Confirmed capacity cannot be negative.'))
        
        # Validate that reserved + confirmed doesn't exceed total
        if (self.reserved_capacity + self.confirmed_capacity) > self.total_capacity:
            raise ValidationError(_('Reserved and confirmed capacity cannot exceed total capacity.'))
        
        # Validate price adjustment
        if self.price_adjustment < 0:
            raise ValidationError(_('Price adjustment cannot be negative.'))
        
        if self.price_adjustment_type == 'percentage' and self.price_adjustment > 100:
            raise ValidationError(_('Percentage adjustment cannot exceed 100%.'))
    
    @property
    def available_capacity(self):
        """Calculate available capacity."""
        total = self.total_capacity or 0
        reserved = self.reserved_capacity or 0
        confirmed = self.confirmed_capacity or 0
        return max(0, total - reserved - confirmed)
    
    @property
    def utilization_percentage(self):
        """Calculate utilization percentage."""
        total = self.total_capacity or 0
        if total == 0:
            return 0
        reserved = self.reserved_capacity or 0
        confirmed = self.confirmed_capacity or 0
        return ((reserved + confirmed) / total) * 100
    
    @property
    def is_full(self):
        """Check if this variant is fully booked."""
        return self.available_capacity <= 0
    
    def can_book(self, quantity=1):
        """Check if the specified quantity can be booked."""
        return self.is_available and self.available_capacity >= quantity
    
    def book_capacity(self, quantity=1):
        """Book capacity for this variant."""
        if self.can_book(quantity):
            self.reserved_capacity = (self.reserved_capacity or 0) + quantity
            self.save(update_fields=['reserved_capacity'])
            return True
        return False
    
    def release_capacity(self, quantity=1):
        """Release reserved capacity."""
        reserved = self.reserved_capacity or 0
        if reserved >= quantity:
            self.reserved_capacity = reserved - quantity
            self.save(update_fields=['reserved_capacity'])
            return True
        return False
    
    def confirm_capacity(self, quantity=1):
        """Convert reserved capacity to confirmed capacity."""
        reserved = self.reserved_capacity or 0
        if reserved >= quantity:
            self.reserved_capacity = reserved - quantity
            self.confirmed_capacity = (self.confirmed_capacity or 0) + quantity
            self.save(update_fields=['reserved_capacity', 'confirmed_capacity'])
            return True
        return False
    
    def cancel_capacity(self, quantity=1):
        """Cancel confirmed capacity."""
        confirmed = self.confirmed_capacity or 0
        if confirmed >= quantity:
            self.confirmed_capacity = confirmed - quantity
            self.save(update_fields=['confirmed_capacity'])
            return True
        return False
    
    def get_final_price(self):
        """Calculate final price with adjustments."""
        base_price = self.variant.base_price or 0
        adjustment = self.price_adjustment or 0
        
        if self.price_adjustment_type == 'percentage':
            return base_price * (1 + adjustment / 100)
        else:
            return base_price + adjustment


class TourItinerary(BaseTranslatableModel):
    """
    Tour itinerary stops and activities.
    """
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='itinerary',
        verbose_name=_('Tour')
    )
    
    # Translatable fields
    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_('Title')),
        description=models.TextField(verbose_name=_('Description')),
    )
    
    # Itinerary details
    order = models.PositiveIntegerField(verbose_name=_('Order'))
    duration_minutes = models.PositiveIntegerField(verbose_name=_('Duration (minutes)'))
    location = models.CharField(max_length=255, verbose_name=_('Location'))
    
    # Optional fields
    image = models.ImageField(
        upload_to='itinerary/', 
        null=True, 
        blank=True,
        verbose_name=_('Image')
    )
    coordinates = models.JSONField(
        null=True, 
        blank=True,
        verbose_name=_('Coordinates')
    )
    
    class Meta:
        verbose_name = _('Tour Itinerary')
        verbose_name_plural = _('Tour Itinerary')
        ordering = ['order']
    
    def __str__(self):
        try:
            return f"{self.tour.title} - {self.title}"
        except:
            return f"{self.tour.slug} - {self.title}"


class TourPricing(BaseModel):
    """
    Age-based pricing for tour variants.
    """
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='pricing',
        verbose_name=_('Tour')
    )
    variant = models.ForeignKey(
        TourVariant, 
        on_delete=models.CASCADE, 
        related_name='pricing',
        verbose_name=_('Variant')
    )
    
    # Age groups
    AGE_GROUP_CHOICES = [
        ('infant', _('Infant (0-2)')),
        ('child', _('Child (2-10)')),
        ('adult', _('Adult (11+)')),
    ]
    age_group = models.CharField(
        max_length=10, 
        choices=AGE_GROUP_CHOICES,
        verbose_name=_('Age group')
    )
    
    # Pricing factor (replaces base_price and discount_percentage)
    factor = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=1.00,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('2.00'))],
        verbose_name=_('Price factor')
    )
    
    # Conditions
    is_free = models.BooleanField(default=False, verbose_name=_('Is free'))
    requires_services = models.BooleanField(default=True, verbose_name=_('Requires services'))
    
    class Meta:
        verbose_name = _('Tour Pricing')
        verbose_name_plural = _('Tour Pricing')
        unique_together = ['tour', 'variant', 'age_group']
    
    def __str__(self):
        try:
            return f"{self.tour.title} - {self.variant.name} - {self.get_age_group_display()}"
        except:
            return f"{self.tour.slug} - {self.variant.name} - {self.get_age_group_display()}"
    
    @property
    def final_price(self):
        """Calculate final price based on variant base price and factor."""
        if self.is_free:
            return Decimal('0.00')
        
        # Use variant base_price instead of tour price
        base_price = self.variant.base_price
        
        # Validate base_price and factor
        if not base_price or base_price <= 0:
            return Decimal('0.00')
        
        if not self.factor or self.factor <= 0:
            return Decimal('0.00')
        
        try:
            return base_price * self.factor
        except (TypeError, ValueError):
            return Decimal('0.00')


class TourOption(BaseOptionModel):
    """
    Tour options and add-ons.
    """
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='options',
        verbose_name=_('Tour')
    )
    
    # Option specific fields
    OPTION_TYPE_CHOICES = [
        ('service', _('Service')),
        ('equipment', _('Equipment')),
        ('food', _('Food')),
        ('transport', _('Transport')),
    ]
    option_type = models.CharField(
        max_length=20, 
        choices=OPTION_TYPE_CHOICES,
        default='service',
        verbose_name=_('Option type')
    )
    
    # Percentage-based pricing (new field)
    price_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        verbose_name=_('Price percentage')
    )
    
    # Availability
    is_available = models.BooleanField(default=True, verbose_name=_('Is available'))
    max_quantity = models.PositiveIntegerField(
        default=1, 
        verbose_name=_('Maximum quantity')
    )
    
    class Meta:
        verbose_name = _('Tour Option')
        verbose_name_plural = _('Tour Options')
    
    def clean(self):
        """Validate tour option data."""
        from django.core.exceptions import ValidationError
        
        # Validate price
        if self.price is None or self.price < 0:
            raise ValidationError({
                'price': 'Price cannot be negative.'
            })
        
        # Validate price_percentage
        if self.price_percentage is None or self.price_percentage < 0:
            raise ValidationError({
                'price_percentage': 'Price percentage cannot be negative.'
            })
        
        # Validate max_quantity
        if self.max_quantity is None or self.max_quantity <= 0:
            raise ValidationError({
                'max_quantity': 'Maximum quantity must be greater than zero.'
            })
    
    def is_available_for_quantity(self, quantity):
        """Check if option is available for the requested quantity."""
        return self.is_available and quantity <= self.max_quantity
    
    def get_total_price_for_quantity(self, quantity):
        """Calculate total price for a given quantity."""
        if not self.is_available_for_quantity(quantity):
            return 0
        
        # Calculate based on price and percentage
        base_price = self.price
        if self.price_percentage > 0:
            base_price = base_price * (1 + self.price_percentage / 100)
        
        return base_price * quantity
    
    def __str__(self):
        try:
            return f"{self.tour.title} - {self.name}"
        except:
            return f"{self.tour.slug} - {self.name}"


class TourReview(BaseModel):
    """
    Tour reviews and ratings.
    """
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name=_('Tour')
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='tour_reviews',
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
    
    # New fields for enhanced functionality
    STATUS_CHOICES = [
        ('pending', _('Pending Moderation')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('flagged', _('Flagged for Review')),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    
    moderation_notes = models.TextField(
        blank=True, 
        verbose_name=_('Moderation Notes')
    )
    moderated_by = models.ForeignKey(
        'users.User', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='moderated_tour_reviews',
        verbose_name=_('Moderated By')
    )
    moderated_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_('Moderated At')
    )
    
    # Review categories for better organization
    CATEGORY_CHOICES = [
        ('general', _('General')),
        ('quality', _('Quality')),
        ('price', _('Price')),
        ('service', _('Service')),
        ('experience', _('Experience')),
    ]
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='general',
        verbose_name=_('Category')
    )
    
    # Sentiment analysis support
    sentiment_score = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_('Sentiment Score')
    )
    
    class Meta:
        verbose_name = _('Tour Review')
        verbose_name_plural = _('Tour Reviews')
        unique_together = ['tour', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        try:
            return f"{self.tour.title} - {self.user.username} - {self.rating}"
        except:
            return f"{self.tour.slug} - {self.user.username} - {self.rating}"
    
    def clean(self):
        """Validate tour review data."""
        from django.core.exceptions import ValidationError
        
        # Validate rating
        if self.rating is None or self.rating < 1 or self.rating > 5:
            raise ValidationError({
                'rating': 'Rating must be between 1 and 5.'
            })
        
        # Validate title
        if not self.title or len(self.title.strip()) == 0:
            raise ValidationError({
                'title': 'Title is required.'
            })
        
        # Validate comment
        if not self.comment or len(self.comment.strip()) == 0:
            raise ValidationError({
                'comment': 'Comment is required.'
            })
    
    def save(self, *args, **kwargs):
        """Override save to apply moderation if status is pending."""
        if self.status == 'pending' and not self.pk:
            # Apply auto-moderation for new reviews
            from .protection import ReviewModeration
            moderation = ReviewModeration()
            moderation_result = moderation.moderate_review(self)
            self = moderation.apply_moderation(self, moderation_result)
        
        super().save(*args, **kwargs)
    
    @property
    def is_approved(self):
        """Check if review is approved."""
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        """Check if review is pending moderation."""
        return self.status == 'pending'
    
    @property
    def is_rejected(self):
        """Check if review is rejected."""
        return self.status == 'rejected'
    
    @property
    def is_flagged(self):
        """Check if review is flagged."""
        return self.status == 'flagged'
    
    def can_be_edited_by(self, user):
        """Check if user can edit this review."""
        # Users can edit their own reviews within 24 hours
        from django.utils import timezone
        from datetime import timedelta
        
        if user != self.user:
            return False
        
        time_since_creation = timezone.now() - self.created_at
        return time_since_creation.total_seconds() <= 86400  # 24 hours
    
    def can_be_deleted_by(self, user):
        """Check if user can delete this review."""
        return user == self.user
    
    def mark_as_helpful(self):
        """Increment helpful votes."""
        self.is_helpful += 1
        self.save(update_fields=['is_helpful'])
    
    def mark_as_unhelpful(self):
        """Decrement helpful votes."""
        if self.is_helpful > 0:
            self.is_helpful -= 1
            self.save(update_fields=['is_helpful'])


class TourBooking(BaseBookingModel):
    """
    Tour bookings with variant and pricing details.
    """
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_('Tour')
    )
    variant = models.ForeignKey(
        TourVariant, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_('Variant')
    )
    schedule = models.ForeignKey(
        TourSchedule, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_('Schedule')
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='tour_bookings',
        verbose_name=_('User')
    )
    
    # Booking details
    booking_reference = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name=_('Booking reference')
    )
    
    # Participant breakdown
    adult_count = models.PositiveIntegerField(default=0, verbose_name=_('Adult count'))
    child_count = models.PositiveIntegerField(default=0, verbose_name=_('Child count'))
    infant_count = models.PositiveIntegerField(default=0, verbose_name=_('Infant count'))
    
    # Pricing breakdown
    adult_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Adult price')
    )
    child_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Child price')
    )
    infant_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Infant price')
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
        verbose_name = _('Tour Booking')
        verbose_name_plural = _('Tour Bookings')
        ordering = ['-created_at']
    
    def __str__(self):
        try:
            return f"{self.booking_reference} - {self.tour.title}"
        except:
            return f"{self.booking_reference} - {self.tour.slug}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        """Generate a unique booking reference."""
        import uuid
        import random
        import string
        
        # Generate a unique reference with format: TB-YYYYMMDD-XXXX
        from datetime import datetime
        date_part = datetime.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        reference = f"TB-{date_part}-{random_part}"
        
        # Ensure uniqueness
        while TourBooking.objects.filter(booking_reference=reference).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            reference = f"TB-{date_part}-{random_part}"
        
        return reference
    
    @property
    def total_participants(self):
        return self.adult_count + self.child_count + self.infant_count
    
    @property
    def subtotal(self):
        return (
            self.adult_price * self.adult_count +
            self.child_price * self.child_count +
            self.infant_price * self.infant_count
        )
    
    @property
    def grand_total(self):
        return self.subtotal + self.options_total
    
    def clean(self):
        """Validate tour booking data."""
        from django.core.exceptions import ValidationError
        
        # Validate participant counts
        if self.adult_count < 0 or self.child_count < 0 or self.infant_count < 0:
            raise ValidationError({
                'participants': 'Participant counts cannot be negative.'
            })
        
        # Validate that at least one participant exists
        if self.total_participants == 0:
            raise ValidationError({
                'participants': 'At least one participant is required.'
            })
        
        # Validate pricing
        if self.adult_price < 0 or self.child_price < 0 or self.infant_price < 0:
            raise ValidationError({
                'pricing': 'Prices cannot be negative.'
            })
        
        # Validate options total
        if self.options_total < 0:
            raise ValidationError({
                'options_total': 'Options total cannot be negative.'
            })
        
        # Validate that variant belongs to the tour
        if self.variant and self.tour and self.variant.tour != self.tour:
            raise ValidationError({
                'variant': 'Variant must belong to the selected tour.'
            })
        
        # Validate that schedule belongs to the tour
        if self.schedule and self.tour and self.schedule.tour != self.tour:
            raise ValidationError({
                'schedule': 'Schedule must belong to the selected tour.'
            }) 


class ReviewReport(BaseModel):
    """
    Model for reporting inappropriate or problematic reviews.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('investigating', _('Under Investigation')),
        ('resolved', _('Resolved')),
        ('dismissed', _('Dismissed')),
        ('escalated', _('Escalated to Admin')),
    ]
    
    REASON_CHOICES = [
        ('inappropriate', _('Inappropriate Content')),
        ('spam', _('Spam or Advertisement')),
        ('fake', _('Fake or Misleading')),
        ('harassment', _('Harassment or Bullying')),
        ('copyright', _('Copyright Violation')),
        ('other', _('Other')),
    ]
    
    review = models.ForeignKey(
        TourReview,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('Review')
    )
    reporter = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='review_reports',
        verbose_name=_('Reporter')
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        verbose_name=_('Report Reason')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Additional Details')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Moderation fields
    moderated_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='moderated_reports',
        verbose_name=_('Moderated By')
    )
    moderated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Moderated At')
    )
    moderation_notes = models.TextField(
        blank=True,
        verbose_name=_('Moderation Notes')
    )
    action_taken = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Action Taken')
    )
    
    class Meta:
        verbose_name = _('Review Report')
        verbose_name_plural = _('Review Reports')
        ordering = ['-created_at']
        unique_together = ['review', 'reporter']
    
    def __str__(self):
        try:
            return f"Report on {self.review} by {self.reporter}"
        except:
            return f"Report by {self.reporter}"
    
    def clean(self):
        """Validate report data."""
        from django.core.exceptions import ValidationError
        
        # Users cannot report their own reviews
        if self.reporter == self.review.user:
            raise ValidationError({
                'reporter': 'You cannot report your own review.'
            })
        
        # Description is required for certain reasons
        if self.reason in ['inappropriate', 'harassment', 'copyright'] and not self.description:
            raise ValidationError({
                'description': 'Description is required for this report reason.'
            })
    
    def save(self, *args, **kwargs):
        """Override save to handle status changes."""
        if self.status in ['resolved', 'dismissed'] and not self.moderated_at:
            self.moderated_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_pending(self):
        """Check if report is pending."""
        return self.status == 'pending'
    
    @property
    def is_investigating(self):
        """Check if report is under investigation."""
        return self.status == 'investigating'
    
    @property
    def is_resolved(self):
        """Check if report is resolved."""
        return self.status == 'resolved'
    
    def can_be_edited_by(self, user):
        """Check if user can edit this report."""
        return user == self.reporter and self.status == 'pending'
    
    def can_be_moderated_by(self, user):
        """Check if user can moderate this report."""
        return user.is_staff or user.has_perm('tours.can_moderate_reviews')


class ReviewResponse(BaseModel):
    """
    Model for responding to reviews (by product owners or staff).
    """
    
    review = models.ForeignKey(
        TourReview,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('Review')
    )
    responder = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='review_responses',
        verbose_name=_('Responder')
    )
    content = models.TextField(
        verbose_name=_('Response Content')
    )
    
    # Response metadata
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Public Response')
    )
    is_official = models.BooleanField(
        default=False,
        verbose_name=_('Official Response')
    )
    
    class Meta:
        verbose_name = _('Review Response')
        verbose_name_plural = _('Review Responses')
        ordering = ['-created_at']
        unique_together = ['review', 'responder']
    
    def __str__(self):
        try:
            return f"Response to {self.review} by {self.responder}"
        except:
            return f"Response by {self.responder}"
    
    def clean(self):
        """Validate response data."""
        from django.core.exceptions import ValidationError
        
        # Content is required
        if not self.content or len(self.content.strip()) == 0:
            raise ValidationError({
                'content': 'Response content is required.'
            })
        
        # Content length validation
        if len(self.content) < 10:
            raise ValidationError({
                'content': 'Response must be at least 10 characters long.'
            })
        
        if len(self.content) > 2000:
            raise ValidationError({
                'content': 'Response cannot exceed 2000 characters.'
            })
    
    @property
    def is_visible(self):
        """Check if response is visible to public."""
        return self.is_public and self.review.is_approved
    
    def can_be_edited_by(self, user):
        """Check if user can edit this response."""
        if user == self.responder:
            # Users can edit their own responses within 1 hour
            from django.utils import timezone
            from datetime import timedelta
            
            time_since_creation = timezone.now() - self.created_at
            return time_since_creation.total_seconds() <= 3600  # 1 hour
        
        return False
    
    def can_be_deleted_by(self, user):
        """Check if user can delete this response."""
        return user == self.responder or user.is_staff 
