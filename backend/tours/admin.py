"""
Django Admin configuration for Tours app.
"""

from django.contrib import admin, messages
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django.db import transaction, IntegrityError, models
from parler.admin import TranslatableAdmin, TranslatableModelForm
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.shortcuts import render


class CapacityStatusFilter(SimpleListFilter):
    """Custom filter for capacity status."""
    title = _('Capacity Status')
    parameter_name = 'capacity_status'

    def lookups(self, request, model_admin):
        return [
            ('low', _('Low Capacity (< 20%)')),
            ('medium', _('Medium Capacity (20-50%)')),
            ('high', _('High Capacity (50-80%)')),
            ('full', _('Full/Over Capacity (> 80%)')),
            ('needs_sync', _('Needs Capacity Sync')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(
                models.Q(total_reserved_capacity__isnull=True) |
                models.Q(total_confirmed_capacity__lt=models.F('tour__variants__capacity') * 0.2)
            ).distinct()
        elif self.value() == 'medium':
            return queryset.filter(
                total_confirmed_capacity__gte=models.F('tour__variants__capacity') * 0.2,
                total_confirmed_capacity__lt=models.F('tour__variants__capacity') * 0.5
            ).distinct()
        elif self.value() == 'high':
            return queryset.filter(
                total_confirmed_capacity__gte=models.F('tour__variants__capacity') * 0.5,
                total_confirmed_capacity__lt=models.F('tour__variants__capacity') * 0.8
            ).distinct()
        elif self.value() == 'full':
            return queryset.filter(
                total_confirmed_capacity__gte=models.F('tour__variants__capacity') * 0.8
            ).distinct()
        elif self.value() == 'needs_sync':
            # Schedules that might have inconsistent capacity data
            return queryset.filter(
                models.Q(total_reserved_capacity__isnull=True) |
                models.Q(total_confirmed_capacity__isnull=True) |
                models.Q(variant_capacities_raw__isnull=True)
            ).distinct()
        return queryset


class DayOfWeekFilter(SimpleListFilter):
    """Custom filter for day of week."""
    title = _('Day of Week')
    parameter_name = 'day_of_week'

    def lookups(self, request, model_admin):
        return [
            (0, _('Monday')),
            (1, _('Tuesday')),
            (2, _('Wednesday')),
            (3, _('Thursday')),
            (4, _('Friday')),
            (5, _('Saturday')),
            (6, _('Sunday')),
        ]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(day_of_week=self.value())
        return queryset


from .models import (
    TourCategory, Tour, TourVariant, TourSchedule, TourScheduleVariantCapacity, TourItinerary, 
    TourPricing, TourOption, TourReview, TourBooking, ReviewReport, ReviewResponse, TourCancellationPolicy, TourGallery
)
from django.forms import inlineformset_factory


class TourVariantFormSet(inlineformset_factory(Tour, TourVariant, fields=['name', 'base_price', 'capacity', 'is_active'], extra=1)):
    """Custom formset for TourVariant that handles unsaved parent objects."""
    
    def __init__(self, *args, **kwargs):
        # If parent object doesn't exist yet, don't try to access its related objects
        if 'instance' in kwargs and (kwargs['instance'] is None or not kwargs['instance'].pk):
            kwargs['queryset'] = TourVariant.objects.none()
        super().__init__(*args, **kwargs)


class TourVariantInline(admin.TabularInline):
    """Inline admin for TourVariant."""
    
    model = TourVariant
    extra = 1
    fields = ['name', 'base_price', 'capacity', 'is_active']
    formset = TourVariantFormSet
    
    # Allow inlines to be used without a saved parent object
    can_delete = True
    show_change_link = False
    
    def get_formset(self, request, obj=None, **kwargs):
        """Customize formset to handle translatable fields and unsaved parent objects."""
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Add help text for translatable fields
        if hasattr(form.base_fields, 'name'):
            form.base_fields['name'].help_text = 'Name is translatable and will be managed in language tabs'
        
        return formset


class TourScheduleVariantCapacityInline(admin.TabularInline):
    """Inline admin for TourScheduleVariantCapacity with enhanced display."""
    
    model = TourScheduleVariantCapacity
    extra = 0
    fields = [
        'variant', 'total_capacity', 'reserved_capacity', 'confirmed_capacity', 
        'available_capacity_display', 'utilization_display', 'price_adjustment', 
        'price_adjustment_type', 'is_available', 'availability_note'
    ]
    readonly_fields = ['available_capacity_display', 'utilization_display']
    verbose_name = _('Variant Capacity')
    verbose_name_plural = _('Variant Capacities')
    
    def available_capacity_display(self, obj):
        """Display available capacity with color coding."""
        if obj.pk:
            available = obj.available_capacity
            if available <= 0:
                return format_html('<span style="color: red; font-weight: bold;">{}</span>', available)
            elif available <= 2:
                return format_html('<span style="color: orange; font-weight: bold;">{}</span>', available)
            else:
                return format_html('<span style="color: green;">{}</span>', available)
        return '-'
    available_capacity_display.short_description = _('Available')
    
    def utilization_display(self, obj):
        """Display utilization percentage with color coding."""
        if obj.pk:
            utilization = obj.utilization_percentage
            if utilization >= 90:
                color = 'red'
            elif utilization >= 70:
                color = 'orange'
            else:
                color = 'green'
            return format_html('<span style="color: {};">{}%</span>', color, f"{utilization:.1f}")
        return '-'
    utilization_display.short_description = _('Utilization')
    
    def get_formset(self, request, obj=None, **kwargs):
        """Customize formset to add help text and validation."""
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Add help text for fields
        if hasattr(form.base_fields, 'total_capacity'):
            form.base_fields['total_capacity'].help_text = _('Maximum capacity for this variant on this schedule')
        if hasattr(form.base_fields, 'reserved_capacity'):
            form.base_fields['reserved_capacity'].help_text = _('Capacity currently reserved in carts')
        if hasattr(form.base_fields, 'confirmed_capacity'):
            form.base_fields['confirmed_capacity'].help_text = _('Capacity confirmed in paid orders')
        if hasattr(form.base_fields, 'price_adjustment'):
            form.base_fields['price_adjustment'].help_text = _('Additional price adjustment for this variant')
        if hasattr(form.base_fields, 'availability_note'):
            form.base_fields['availability_note'].help_text = _('Optional note about availability')
            
        return formset


class TourScheduleInlineForm(forms.ModelForm):
    """Custom form for TourSchedule inline."""
    
    class Meta:
        model = TourSchedule
        fields = '__all__'
        widgets = {
            'day_of_week': forms.Select(choices=[
                (0, _('Monday')),
                (1, _('Tuesday')),
                (2, _('Wednesday')),
                (3, _('Thursday')),
                (4, _('Friday')),
                (5, _('Saturday')),
                (6, _('Sunday')),
            ]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Auto-populate day_of_week from start_date if not set
        if self.instance and self.instance.start_date and not self.instance.day_of_week:
            self.instance.day_of_week = self.instance.start_date.weekday()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        day_of_week = cleaned_data.get('day_of_week')
        
        # Auto-populate day_of_week if start_date is provided but day_of_week is not
        if start_date and day_of_week is None:
            cleaned_data['day_of_week'] = start_date.weekday()
        
        return cleaned_data


class TourScheduleInline(admin.StackedInline):
    """Inline admin for TourSchedule with enhanced capacity management."""
    
    model = TourSchedule
    form = TourScheduleInlineForm
    extra = 1
    verbose_name = _('Tour Schedule')
    verbose_name_plural = _('Tour Schedules')
    fields = [
        ('start_date', 'end_date'), ('start_time', 'end_time'), 'day_of_week', 'day_of_week_display',
        'available_variants', 'is_available', 'availability_override', 'availability_note',
        'total_capacity_display', 'available_capacity_display'
    ]
    readonly_fields = ['total_capacity_display', 'available_capacity_display', 'day_of_week_display']
    inlines = [TourScheduleVariantCapacityInline]
    
    def day_of_week_display(self, obj):
        """Display day of week with better formatting."""
        if obj.day_of_week is not None:
            day_names = {
                0: _('Monday'),
                1: _('Tuesday'),
                2: _('Wednesday'),
                3: _('Thursday'),
                4: _('Friday'),
                5: _('Saturday'),
                6: _('Sunday'),
            }
            return day_names.get(obj.day_of_week, _('Unknown'))
        return _('Not set')
    day_of_week_display.short_description = _('Day')
    
    def get_formset(self, request, obj=None, **kwargs):
        """Customize formset to add help text."""
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Add help text for fields
        form.base_fields['start_date'].help_text = _('Select the date - day of week will be calculated automatically')
        if hasattr(form.base_fields, 'end_date'):
            form.base_fields['end_date'].help_text = _('Leave empty for single-day tours (same as start date)')
        if hasattr(form.base_fields, 'end_time'):
            form.base_fields['end_time'].help_text = _('Leave empty for single-day tours (same as start time)')
        if hasattr(form.base_fields, 'day_of_week'):
            form.base_fields['day_of_week'].help_text = _('Day of week - can be auto-populated from start date')
        if hasattr(form.base_fields, 'available_variants'):
            form.base_fields['available_variants'].help_text = _('Select specific variants for this schedule. Leave empty to make all tour variants available.')
        if hasattr(form.base_fields, 'availability_note'):
            form.base_fields['availability_note'].help_text = _('Optional note about availability (e.g., "Few seats left")')
            
        return formset
        
    def total_capacity_display(self, obj):
        """Display total capacity with fallback text."""
        if obj and obj.pk:
            total, available = _compute_schedule_caps(obj)
            return total if total else 'Not set'
        return 'Not set'
    total_capacity_display.short_description = _('Total capacity')

    def available_capacity_display(self, obj):
        """Display available capacity with fallback text."""
        if obj and obj.pk:
            total, available = _compute_schedule_caps(obj)
            return available if available is not None else 'Not set'
        return 'Not set'
    available_capacity_display.short_description = _('Available capacity')


class TourCategoryFilter(SimpleListFilter):
    """Custom filter for TourCategory that handles translatable fields safely."""
    
    title = _('Category')
    parameter_name = 'category_filter'
    
    def lookups(self, request, model_admin):
        """Return list of tuples for filter options."""
        try:
            categories = TourCategory.objects.filter(is_active=True)
            result = []
            for cat in categories:
                try:
                    name = cat.name or cat.slug
                except:
                    name = cat.slug
                result.append((cat.id, name))
            return result
        except:
            return []
    
    def queryset(self, request, queryset):
        """Filter queryset based on selected category."""
        if self.value():
            return queryset.filter(category_id=self.value())
        return queryset


from parler.admin import TranslatableStackedInline

class TourItineraryInline(TranslatableStackedInline):
    """Inline admin for TourItinerary."""
    
    model = TourItinerary
    extra = 1
    fields = [
        ('order', 'duration_minutes'),
        'location',
        'title',
        'description',
        'image',
        'coordinates'
    ]
    
    def get_formset(self, request, obj=None, **kwargs):
        """Customize formset to handle translatable fields."""
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Add help text for translatable fields
        if hasattr(form.base_fields, 'title'):
            form.base_fields['title'].help_text = _('Title is translatable and will be managed in language tabs')
        if hasattr(form.base_fields, 'description'):
            form.base_fields['description'].help_text = _('Description is translatable and will be managed in language tabs')
            
        return formset


class TourGalleryInline(admin.TabularInline):
    """Inline admin for TourGallery with enhanced display."""
    
    model = TourGallery
    extra = 1
    fields = ['image_preview', 'image', 'title', 'description', 'order', 'is_active']
    verbose_name = _('Gallery Image')
    verbose_name_plural = _('Gallery Images')
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    ordering = ['order', 'created_at']
    
    def image_preview(self, obj):
        """Display image preview in admin."""
        if obj and obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 100px; max-height: 100px; border-radius: 4px;" />'
        return '<span style="color: #999;">No image</span>'
    image_preview.short_description = _('Preview')
    image_preview.allow_tags = True


class TourCancellationPolicyInline(admin.TabularInline):
    """Inline admin for TourCancellationPolicy."""
    
    model = TourCancellationPolicy
    extra = 1
    fields = ['hours_before', 'refund_percentage', 'description', 'is_active']
    ordering = ['-hours_before']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Set default values for new policies
        if not obj:  # Creating new tour
            form.base_fields['is_active'].initial = True
        
        return formset


class TourPricingInline(admin.TabularInline):
    """Inline admin for TourPricing."""
    
    model = TourPricing
    extra = 1
    fields = ['variant', 'age_group', 'factor', 'is_free']


class TourOptionInline(admin.TabularInline):
    """Inline admin for TourOption."""
    
    model = TourOption
    extra = 1
    fields = ['name', 'price', 'price_percentage', 'option_type', 'is_active']
    
    def get_formset(self, request, obj=None, **kwargs):
        """Customize formset to handle translatable fields."""
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Add help text for translatable fields
        if hasattr(form.base_fields, 'name'):
            form.base_fields['name'].help_text = 'Name is translatable and will be managed in language tabs'
        
        return formset


class TourAdminForm(TranslatableModelForm):
    """Custom form for Tour admin with enhanced validation."""
    
    class Meta:
        model = Tour
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check required fields (only non-translatable fields)
        required_fields = ['category', 'city', 'country', 'price', 'duration_hours', 'start_time', 'end_time', 'max_participants']
        missing_fields = []
        
        for field in required_fields:
            if not cleaned_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            raise forms.ValidationError(
                _('The following fields are required: %(fields)s') % {
                    'fields': ', '.join(missing_fields)
                }
            )
        
        # Validate price
        price = cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError(_('Price cannot be negative.'))
        
        # Validate duration
        duration_hours = cleaned_data.get('duration_hours')
        if duration_hours is not None and duration_hours <= 0:
            raise forms.ValidationError(_('Duration must be greater than zero.'))
        
        # Validate timing
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        pickup_time = cleaned_data.get('pickup_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(_('End time must be after start time.'))
        
        if pickup_time and start_time and pickup_time >= start_time:
            raise forms.ValidationError(_('Pickup time must be before start time.'))
        
        # Validate capacity
        min_participants = cleaned_data.get('min_participants')
        max_participants = cleaned_data.get('max_participants')
        if min_participants and max_participants and min_participants > max_participants:
            raise forms.ValidationError(_('Minimum participants cannot exceed maximum participants.'))
        
        return cleaned_data


@admin.register(TourCategory)
class TourCategoryAdmin(TranslatableAdmin):
    """Admin for TourCategory model."""

    list_display = ['get_name', 'icon', 'color', 'tour_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['translations__name', 'slug']  # Required for autocomplete_fields
    list_per_page = 20  # Limit results for better performance
    list_editable = ['is_active']  # Allow editing is_active directly in list view
    
    # Fix popup issues with enhanced approach
    def response_add(self, request, obj, post_url_continue=None):
        """Fix popup response for adding new categories."""
        if request.GET.get('_popup'):
            from django.http import HttpResponse
            from django.utils.html import format_html
            return HttpResponse(
                format_html(
                    '<script type="text/javascript">'
                    'if (window.opener && window.opener.dismissAddRelatedObjectPopup) {'
                    '  window.opener.dismissAddRelatedObjectPopup(window, "{}", "{}");'
                    '} else {'
                    '  window.close();'
                    '}'
                    '</script>',
                    obj.pk,
                    str(obj)
                )
            )
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        """Fix popup response for changing categories."""
        if request.GET.get('_popup'):
            from django.http import HttpResponse
            from django.utils.html import format_html
            return HttpResponse(
                format_html(
                    '<script type="text/javascript">'
                    'if (window.opener && window.opener.dismissChangeRelatedObjectPopup) {'
                    '  window.opener.dismissChangeRelatedObjectPopup(window, "{}", "{}");'
                    '} else {'
                    '  window.close();'
                    '}'
                    '</script>',
                    obj.pk,
                    str(obj)
                )
            )
        return super().response_change(request, obj)
    
    def get_queryset(self, request):
        """Override to show only active categories."""
        qs = super().get_queryset(request)
        # Show only active categories
        return qs.filter(is_active=True)
    
    def get_form(self, request, obj=None, **kwargs):
        """Custom form to ensure category field works properly."""
        form = super().get_form(request, obj, **kwargs)
        if 'category' in form.base_fields:
            form.base_fields['category'].help_text = "Select an existing category or create a new one"
            # Ensure the field is not disabled
            form.base_fields['category'].disabled = False
        return form
    
    def get_readonly_fields(self, request, obj=None):
        """Custom readonly fields."""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        # Ensure category is not readonly
        if 'category' in readonly_fields:
            readonly_fields.remove('category')
        return readonly_fields
    
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug',),
            'description': _('Name and description are managed in language tabs.')
        }),
        (_('Styling'), {
            'fields': ('icon', 'color'),
            'description': _('Visual styling for the category.')
        }),
        (_('Status'), {
            'fields': ('is_active',),
            'description': _('Control category visibility.')
        }),
    )
    
    def get_name(self, obj):
        """Get the translated name for display in list."""
        try:
            return obj.name or obj.slug
        except:
            return obj.slug
    get_name.short_description = _('Name')
    get_name.admin_order_field = 'translations__name'
    
    def tour_count(self, obj):
        """Get number of tours in this category."""
        return obj.tours.count()
    tour_count.short_description = _('Tour Count')


class TourAdmin(TranslatableAdmin):
    """Admin for Tour model."""
    
    form = TourAdminForm
    

    
    list_display = [
        'get_title', 'get_category', 'tour_type', 'transport_type', 'duration_hours',
        'price', 'completion_status_display', 'total_capacity_display', 'next_schedule_display', 
        'is_featured', 'is_popular', 'is_special', 'is_seasonal', 'is_active', 'booking_count'
    ]
    list_filter = [
        TourCategoryFilter, 'tour_type', 'transport_type', 'is_featured',
        'is_popular', 'is_special', 'is_seasonal', 'is_active', 'includes_transfer', 'includes_guide',
        'includes_meal', 'created_at'
    ]
    search_fields = [
        'city', 'country', 'slug'
    ]
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completion_status_display', 'setup_recommendations_display']

    # Enhanced solution: Use default dropdown with better configuration
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Custom formfield for category selection."""
        if db_field.name == "category":
            kwargs["queryset"] = TourCategory.objects.filter(is_active=True)
            kwargs["empty_label"] = "Select a category..."
            # Force widget refresh
            kwargs["widget"] = None
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        """Custom form to ensure category field works properly."""
        form = super().get_form(request, obj, **kwargs)
        if 'category' in form.base_fields:
            form.base_fields['category'].help_text = "Select an existing category or create a new one"
            # Ensure the field is not disabled
            form.base_fields['category'].disabled = False
        return form

    # Enable save as feature to duplicate tours
    save_as = True
    save_as_continue = True
    
    # Temporarily remove TourVariantInline to fix primary key issue
    # Users can add variants after creating the tour
    inlines = [
        TourItineraryInline,
        TourGalleryInline,
        TourCancellationPolicyInline
    ]
    
    # فیلدهای غیر قابل ترجمه را مشخص کنیم (فیلدهای ترجمه‌پذیر در زبان‌ها مدیریت می‌شوند)
    fieldsets = (
        (_('Setup Status'), {
            'fields': ('completion_status_display', 'setup_recommendations_display'),
            'description': _('Tour setup completion status and recommendations.'),
            'classes': ('wide',)
        }),
        (_('Basic Information'), {
            'fields': ('id', 'slug'),
            'description': _('Basic tour information. After creating the tour, you can add variants, schedules, pricing, and options from their respective admin pages.')
        }),
        (_('Translatable Content'), {
            'fields': ('title', 'description', 'short_description', 'highlights', 'rules', 'required_items'),
            'description': _('Translatable content fields. These fields can be translated in different languages.')
        }),
        (_('Category & Type'), {
            'fields': ('category', 'tour_type', 'transport_type'),
            'description': _('Category is a required field.')
        }),
        (_('Location'), {
            'fields': ('city', 'country'),
            'description': _('City and country are required fields.')
        }),
        (_('Pricing'), {
            'fields': ('price', 'currency'),
            'description': _('Price is a required field and must be greater than zero.')
        }),
        (_('Timing'), {
            'fields': ('duration_hours', 'pickup_time', 'start_time', 'end_time'),
            'description': _('All timing fields are required.')
        }),
        (_('Capacity & Booking'), {
            'fields': ('min_participants', 'max_participants', 'booking_cutoff_hours'),
            'description': _('Capacity fields are required.')
        }),
        (_('Cancellation Policy'), {
            'fields': ('cancellation_hours', 'refund_percentage'),
            'description': _('Cancellation policy fields are required.')
        }),
        (_('Services Included'), {
            'fields': ('includes_transfer', 'includes_guide', 'includes_meal', 'includes_photographer'),
            'description': _('Select which services are included in the tour.')
        }),
        (_('Content'), {
            'fields': ('image',),
            'description': _('Main tour image and gallery images are managed in the Tour Gallery Images section below.')
        }),
        (_('Status'), {
            'fields': ('is_featured', 'is_popular', 'is_special', 'is_seasonal', 'is_active'),
            'description': _('Control tour visibility and promotion.')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': _('Automatically managed timestamps.')
        }),
    )
    
    # تنظیمات زبان‌ها برای django-parler
    def get_fieldsets(self, request, obj=None):
        """Get fieldsets with proper language configuration."""
        fieldsets = super().get_fieldsets(request, obj)
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        """Get form with proper field configuration."""
        form = super().get_form(request, obj, **kwargs)
        return form
    
    def get_prepopulated_fields(self, request, obj=None):
        """Get prepopulated fields for slug generation."""
        return {}
    
    # Removed slug prepopulation from translatable title to avoid KeyError.

    actions = [
        'initialize_schedule_capacities',
        'validate_tour_schedules',
        'validate_tour_variants',
        'create_default_variant',
        'create_default_schedule',
        'setup_complete_tour',
        'auto_complete_tour_setup',
        'check_tour_completion_status'
    ]

    def initialize_schedule_capacities(self, request, queryset):
        """Admin action: initialize variant capacities for all schedules of selected tours."""
        initialized = 0
        for tour in queryset:
            for sched in tour.schedules.all():
                try:
                    sched.initialize_variant_capacities()
                    initialized += 1
                except Exception:
                    continue
        self.message_user(request, _(f"Initialized capacities for {initialized} schedules."))
    initialize_schedule_capacities.short_description = _('Initialize schedule capacities from variants')
    
    def validate_tour_schedules(self, request, queryset):
        """Admin action: validate schedules for conflicts."""
        validated = 0
        errors = 0
        for tour in queryset:
            try:
                tour.validate_schedules()
                validated += 1
            except Exception as e:
                errors += 1
                self.message_user(request, f"Schedule validation failed for {tour}: {str(e)}", level='ERROR')
        
        if validated > 0:
            self.message_user(request, _(f"Validated schedules for {validated} tours."))
        if errors > 0:
            self.message_user(request, _(f"{errors} tours have schedule conflicts."), level='WARNING')
    validate_tour_schedules.short_description = _('Validate tour schedules for conflicts')
    
    def validate_tour_variants(self, request, queryset):
        """Admin action: validate variants and their pricing."""
        validated = 0
        errors = 0
        for tour in queryset:
            for variant in tour.variants.all():
                try:
                    variant.validate_pricing()
                    validated += 1
                except Exception as e:
                    errors += 1
                    self.message_user(request, f"Variant validation failed for {variant}: {str(e)}", level='ERROR')
        
        if validated > 0:
            self.message_user(request, _(f"Validated {validated} variants."))
        if errors > 0:
            self.message_user(request, _(f"{errors} variants have pricing issues."), level='WARNING')
    validate_tour_variants.short_description = _('Validate tour variants and pricing')
    
    def booking_count(self, obj):
        """Get number of bookings for this tour."""
        return obj.bookings.count()
    booking_count.short_description = _('Bookings')
    
    def total_capacity_display(self, obj):
        """Display total capacity across all variants."""
        try:
            return obj.get_total_capacity()
        except Exception:
            return 0
    total_capacity_display.short_description = _('Total Capacity')
    
    def next_schedule_display(self, obj):
        """Display next available schedule."""
        try:
            next_schedule = obj.get_next_available_schedule()
            if next_schedule:
                return next_schedule.start_date.strftime('%Y-%m-%d')
            return _('None')
        except Exception:
            return _('Error')
    next_schedule_display.short_description = _('Next Schedule')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('category').prefetch_related('bookings')
    

    
    def save_model(self, request, obj, form, change):
        """On save, create default schedule and variant if this is a new tour."""
        try:
            with transaction.atomic():
                # Set flag to skip variant validation during initial creation
                if not change:  # New tour
                    obj._skip_variant_validation = True
                
                super().save_model(request, obj, form, change)
                
                # Create default schedule and variant if this is a new tour
                if not change:  # New tour
                    try:
                        # Create default schedule
                        obj.create_default_schedule()
                    except IntegrityError:
                        # Schedule already exists, ignore
                        pass
                    except Exception as e:
                        # Log other errors but don't block tour creation
                        print(f"Error creating default schedule: {str(e)}")
                    
                    # Create default variant if none exist
                    if not obj.variants.exists():
                        try:
                            from .models import TourVariant
                            # Set a flag to indicate we're creating variants
                            obj._creating_variants = True
                            TourVariant.objects.create(
                                tour=obj,
                                name='Standard',
                                base_price=obj.price or 0,
                                capacity=obj.max_participants or 10,
                                is_active=True
                            )
                        except Exception as e:
                            # Log error but don't block tour creation
                            print(f"Error creating default variant: {str(e)}")
                    
                    # Final validation: ensure tour has at least one variant
                    if not obj.variants.exists():
                        from django.contrib import messages
                        messages.warning(request, "Warning: Tour was created without variants. Please add variants manually.")
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f"Error saving tour: {str(e)}")
            raise
    
    def get_title(self, obj):
        """Get the translated title for display in list."""
        try:
            return obj.title or obj.slug
        except:
            return obj.slug
    get_title.short_description = _('Title')
    get_title.admin_order_field = 'translations__title'
    
    def get_category(self, obj):
        """Get the translated category name for display in list."""
        try:
            return getattr(obj.category, 'name', '') or obj.category.slug
        except:
            return obj.category.slug if obj.category else _('No Category')
    get_category.short_description = _('Category')
    get_category.admin_order_field = 'category__slug'
    
    def completion_status_display(self, obj):
        """Display tour completion status with color coding."""
        try:
            status = obj.get_completion_status()
            percentage = status['completion_percentage']
            
            if percentage == 100:
                color = 'green'
                icon = '✓'
                text = 'Complete'
            elif percentage >= 80:
                color = 'orange'
                icon = '⚠'
                text = f'{percentage}%'
            else:
                color = 'red'
                icon = '✗'
                text = f'{percentage}%'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;" title="{}">{} {}</span>',
                color,
                f"Completion: {percentage}% - {'Complete' if status['is_complete'] else 'Incomplete'}",
                icon,
                text
            )
        except Exception as e:
            return format_html('<span style="color: red;">Error</span>')
    completion_status_display.short_description = _('Setup Status')
    completion_status_display.admin_order_field = 'id'
    
    def setup_recommendations_display(self, obj):
        """Display setup recommendations and missing items."""
        try:
            recommendations = obj.get_setup_recommendations()
            
            if not recommendations:
                return format_html('<span style="color: green;">✓ Tour setup is complete!</span>')
            
            html_parts = []
            
            for rec in recommendations:
                if rec['type'] == 'error':
                    html_parts.append('<div style="margin-bottom: 10px;">')
                    html_parts.append('<strong style="color: red;">❌ Required Items:</strong>')
                    html_parts.append('<ul style="margin: 5px 0; padding-left: 20px;">')
                    for item in rec['items']:
                        html_parts.append(f'<li style="color: red;">{item}</li>')
                    html_parts.append('</ul>')
                    html_parts.append('</div>')
                
                elif rec['type'] == 'warning':
                    html_parts.append('<div style="margin-bottom: 10px;">')
                    html_parts.append('<strong style="color: orange;">⚠️ Recommendations:</strong>')
                    html_parts.append('<ul style="margin: 5px 0; padding-left: 20px;">')
                    for item in rec['items']:
                        html_parts.append(f'<li style="color: orange;">{item}</li>')
                    html_parts.append('</ul>')
                    html_parts.append('</div>')
                
                elif rec['type'] == 'action':
                    html_parts.append('<div style="margin-bottom: 10px;">')
                    html_parts.append(f'<strong style="color: blue;">🔧 {rec["title"]}:</strong>')
                    html_parts.append(f'<p style="margin: 5px 0; color: #666;">{rec["description"]}</p>')
                    html_parts.append('</div>')
            
            return format_html(''.join(html_parts))
            
        except Exception as e:
            return format_html('<span style="color: red;">Error loading recommendations</span>')
    setup_recommendations_display.short_description = _('Setup Recommendations')
    
    def save_formset(self, request, form, formset, change):
        """Save formset and validate schedules."""
        if formset.model == TourSchedule:
            instances = formset.save(commit=False)
            for instance in instances:
                try:
                    # Check if a schedule already exists for this date
                    existing = TourSchedule.objects.filter(
                        tour=instance.tour,
                        start_date=instance.start_date
                    ).exclude(pk=instance.pk).exists()
                    
                    if not existing:
                        instance.full_clean()
                        instance.save()
                except Exception as e:
                    from django.contrib import messages
                    messages.warning(
                        request,
                        f"Could not save schedule for {instance.start_date}: {str(e)}"
                    )
            # Handle deletions
            for obj in formset.deleted_objects:
                obj.delete()
        else:
            super().save_formset(request, form, formset, change)


@admin.register(TourVariant)
class TourVariantAdmin(admin.ModelAdmin):
    """Admin for TourVariant model."""

    autocomplete_fields = ['tour']

    list_display = [
        'name', 'tour', 'base_price', 'capacity', 'pricing_status', 'is_active', 'booking_count'
    ]
    list_filter = [
        'is_active', 'includes_transfer', 'includes_guide',
        'includes_meal', 'includes_photographer'
    ]
    search_fields = [
        'name', 'description', 'tour__slug', 'tour__translations__title'
    ]
    ordering = ['tour', 'name']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('tour', 'name', 'description')
        }),
        (_('Pricing & Capacity'), {
            'fields': ('base_price', 'capacity')
        }),
        (_('Services Included'), {
            'fields': ('includes_transfer', 'includes_guide', 'includes_meal', 'includes_photographer')
        }),
        (_('Extended Services'), {
            'fields': ('extended_hours', 'private_transfer', 'expert_guide', 'special_meal')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def booking_count(self, obj):
        """Get number of bookings for this variant."""
        return obj.bookings.count()
    booking_count.short_description = _('Bookings')
    
    def pricing_status(self, obj):
        """Display pricing status for this variant."""
        try:
            obj.validate_pricing()
            return format_html('<span style="color: green;">✓ Complete</span>')
        except Exception as e:
            return format_html('<span style="color: red;">✗ {}</span>', str(e)[:30])
    pricing_status.short_description = _('Pricing Status')
    pricing_status.allow_tags = True
    
    actions = ['validate_variant_pricing']
    
    def validate_variant_pricing(self, request, queryset):
        """Admin action: validate pricing for selected variants."""
        validated = 0
        errors = 0
        for variant in queryset:
            try:
                variant.validate_pricing()
                validated += 1
            except Exception as e:
                errors += 1
                self.message_user(request, f"Pricing validation failed for {variant}: {str(e)}", level='ERROR')
        
        if validated > 0:
            self.message_user(request, _(f"Validated pricing for {validated} variants."))
        if errors > 0:
            self.message_user(request, _(f"{errors} variants have pricing issues."), level='WARNING')
    validate_variant_pricing.short_description = _('Validate variant pricing')

    def create_default_variant(self, request, queryset):
        """Admin action: Create a default variant for selected tours."""
        from .models import TourVariant
        created = 0
        skipped = 0

        for tour in queryset:
            if not tour.variants.exists():
                try:
                    # Create a default variant
                    variant = TourVariant.objects.create(
                        tour=tour,
                        name='Standard',
                        base_price=tour.price or 0,
                        capacity=tour.max_participants or 10,
                        is_active=True
                    )
                    created += 1
                except Exception as e:
                    self.message_user(request, f"Error creating variant for {tour}: {str(e)}", level='ERROR')
            else:
                skipped += 1

        self.message_user(request, f"Created {created} default variants. Skipped {skipped} tours that already have variants.")
    create_default_variant.short_description = _('Create default variant for selected tours')

    def create_default_schedule(self, request, queryset):
        """Admin action: Create a default schedule for selected tours."""
        from datetime import date, timedelta
        from .models import TourSchedule

        created = 0
        skipped = 0

        for tour in queryset:
            try:
                # Check if tour has variants
                if not tour.variants.exists():
                    self.message_user(request, f"Cannot create schedule for {tour}: No variants exist. Create variants first.", level='WARNING')
                    continue

                # Create a default schedule for next week
                next_week = date.today() + timedelta(days=7)
                schedule = TourSchedule.objects.create(
                    tour=tour,
                    start_date=next_week,
                    end_date=next_week,
                    start_time=tour.start_time,
                    end_time=tour.end_time,
                    is_available=True,
                    max_capacity=tour.max_participants
                )

                # Initialize capacities for all variants
                for variant in tour.variants.filter(is_active=True):
                    schedule.add_variant_capacity(variant.id, variant.capacity)

                created += 1
            except Exception as e:
                self.message_user(request, f"Error creating schedule for {tour}: {str(e)}", level='ERROR')

        self.message_user(request, f"Created {created} default schedules.")
    create_default_schedule.short_description = _('Create default schedule for selected tours')

    def setup_complete_tour(self, request, queryset):
        """Admin action: Set up a complete tour with default variant and schedule."""
        from datetime import date, timedelta
        from .models import TourVariant, TourSchedule

        completed = 0
        for tour in queryset:
            try:
                with transaction.atomic():
                    # Create default variant if none exists
                    if not tour.variants.exists():
                        variant = TourVariant.objects.create(
                            tour=tour,
                            name='Standard',
                            base_price=tour.price or 0,
                            capacity=tour.max_participants or 10,
                            is_active=True
                        )

                    # Create default schedule if none exists
                    if not tour.schedules.exists():
                        next_week = date.today() + timedelta(days=7)
                        schedule = TourSchedule.objects.create(
                            tour=tour,
                            start_date=next_week,
                            end_date=next_week,
                            start_time=tour.start_time,
                            end_time=tour.end_time,
                            is_available=True,
                            max_capacity=tour.max_participants
                        )

                        # Initialize capacities for all variants
                        for variant in tour.variants.filter(is_active=True):
                            schedule.add_variant_capacity(variant.id, variant.capacity)

                    completed += 1
            except Exception as e:
                self.message_user(request, f"Error setting up {tour}: {str(e)}", level='ERROR')

        self.message_user(request, f"Successfully set up {completed} complete tours.")
    setup_complete_tour.short_description = _('Set up complete tour with default variant and schedule')
    
    def auto_complete_tour_setup(self, request, queryset):
        """Admin action: Automatically complete tour setup based on recommendations."""
        completed = 0
        errors = 0
        
        for tour in queryset:
            try:
                recommendations = tour.get_setup_recommendations()
                actions_taken = []
                
                for rec in recommendations:
                    if rec['type'] == 'action':
                        if rec['action'] == 'create_variants':
                            # Create default variant
                            from .models import TourVariant
                            variant = TourVariant.objects.create(
                                tour=tour,
                                name='Standard',
                                base_price=tour.price or 100,
                                capacity=tour.max_participants or 10,
                                is_active=True
                            )
                            actions_taken.append(f"Created variant: {variant.name}")
                            
                        elif rec['action'] == 'create_schedules':
                            # Create default schedule
                            from datetime import date, timedelta
                            from .models import TourSchedule
                            next_week = date.today() + timedelta(days=7)
                            schedule = TourSchedule.objects.create(
                                tour=tour,
                                start_date=next_week,
                                end_date=next_week,
                                start_time=tour.start_time,
                                end_time=tour.end_time,
                                is_available=True,
                                max_capacity=tour.max_participants
                            )
                            actions_taken.append(f"Created schedule: {schedule.start_date}")
                            
                        elif rec['action'] == 'configure_pricing':
                            # Create default pricing
                            from .models import TourPricing
                            variant = tour.variants.get(id=rec['variant_id'])
                            for age_group in ['adult', 'child', 'infant']:
                                factor = 1.0 if age_group == 'adult' else 0.7 if age_group == 'child' else 0.0
                                TourPricing.objects.get_or_create(
                                    tour=tour,
                                    variant=variant,
                                    age_group=age_group,
                                    defaults={
                                        'factor': factor,
                                        'is_free': age_group == 'infant',
                                        'requires_services': True
                                    }
                                )
                            actions_taken.append(f"Configured pricing for {variant.name}")
                            
                        elif rec['action'] == 'configure_capacity':
                            # Create default capacity
                            schedule = tour.schedules.get(id=rec['schedule_id'])
                            for variant in tour.variants.filter(is_active=True):
                                from .models import TourScheduleVariantCapacity
                                TourScheduleVariantCapacity.objects.get_or_create(
                                    schedule=schedule,
                                    variant=variant,
                                    defaults={
                                        'total_capacity': variant.capacity,
                                        'reserved_capacity': 0,
                                        'confirmed_capacity': 0,
                                        'is_available': True
                                    }
                                )
                            actions_taken.append(f"Configured capacity for {schedule.start_date}")
                
                if actions_taken:
                    completed += 1
                    self.message_user(
                        request, 
                        f"Tour '{tour.title}': {', '.join(actions_taken)}", 
                        level='SUCCESS'
                    )
                else:
                    self.message_user(
                        request, 
                        f"Tour '{tour.title}': No actions needed", 
                        level='INFO'
                    )
                    
            except Exception as e:
                errors += 1
                self.message_user(
                    request, 
                    f"Error completing setup for '{tour.title}': {str(e)}", 
                    level='ERROR'
                )
        
        if completed > 0:
            self.message_user(request, f"Auto-completed setup for {completed} tours.")
        if errors > 0:
            self.message_user(request, f"Errors occurred for {errors} tours.", level='WARNING')
    auto_complete_tour_setup.short_description = _('Auto-complete tour setup based on recommendations')
    
    def check_tour_completion_status(self, request, queryset):
        """Admin action: Check and display completion status for selected tours."""
        for tour in queryset:
            try:
                status = tour.get_completion_status()
                recommendations = tour.get_setup_recommendations()
                
                message_parts = [f"Tour '{tour.title}':"]
                message_parts.append(f"Completion: {status['completion_percentage']}%")
                
                if status['missing_items']:
                    message_parts.append(f"Missing: {', '.join(status['missing_items'])}")
                
                if status['warnings']:
                    message_parts.append(f"Warnings: {', '.join(status['warnings'])}")
                
                if not recommendations:
                    message_parts.append("✓ Setup is complete!")
                
                self.message_user(request, ' | '.join(message_parts))
                
            except Exception as e:
                self.message_user(
                    request, 
                    f"Error checking status for '{tour.title}': {str(e)}", 
                    level='ERROR'
                )
    check_tour_completion_status.short_description = _('Check tour completion status')

    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('tour').prefetch_related('bookings')


class TourScheduleAdminForm(forms.ModelForm):
    """Custom form for TourSchedule with enhanced capacity management."""

    class Meta:
        model = TourSchedule
        fields = '__all__'
        widgets = {
            'day_of_week': forms.Select(choices=[
                (0, _('Monday')),
                (1, _('Tuesday')),
                (2, _('Wednesday')),
                (3, _('Thursday')),
                (4, _('Friday')),
                (5, _('Saturday')),
                (6, _('Sunday')),
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add help text for capacity fields
        self.fields['variant_capacities_raw'].help_text = _(
            'JSON field containing variant capacities. '
            'Use the actions below to manage capacities automatically.'
        )
        
        # Add help text for day_of_week
        self.fields['day_of_week'].help_text = _(
            'Select the day of the week for this schedule. '
            'This helps organize schedules by recurring days. '
            'You can also auto-populate this field based on the start date.'
        )
        
        # Auto-populate day_of_week from start_date if not set
        if self.instance and self.instance.start_date and not self.instance.day_of_week:
            self.instance.day_of_week = self.instance.start_date.weekday()

    def clean_variant_capacities_raw(self):
        """Validate variant_capacities_raw JSON structure."""
        data = self.cleaned_data.get('variant_capacities_raw')
        if data:
            try:
                import json
                parsed = json.loads(data) if isinstance(data, str) else data

                # Validate structure
                if not isinstance(parsed, dict):
                    raise forms.ValidationError("Must be a valid JSON object")

                for variant_id, variant_data in parsed.items():
                    if not isinstance(variant_data, dict):
                        raise forms.ValidationError(f"Variant {variant_id} data must be an object")
                    required_keys = ['total', 'available', 'booked']
                    for key in required_keys:
                        if key not in variant_data:
                            raise forms.ValidationError(f"Variant {variant_id} missing required key: {key}")

                return data
            except (ValueError, TypeError) as e:
                raise forms.ValidationError(f"Invalid JSON format: {str(e)}")

        return data


@admin.register(TourSchedule)
class TourScheduleAdmin(admin.ModelAdmin):
    """Admin for TourSchedule model with enhanced capacity management."""

    form = TourScheduleAdminForm
    autocomplete_fields = ['tour', 'available_variants']
    inlines = [TourScheduleVariantCapacityInline]

    list_display = [
        'tour', 'start_date', 'day_of_week_display', 'is_available',
        'total_capacity_display', 'reserved_capacity_display', 'confirmed_capacity_display', 'available_capacity_display'
    ]
    list_filter = [
        'is_available', 'start_date', DayOfWeekFilter, CapacityStatusFilter, 'tour'
    ]
    search_fields = [
        'tour__slug', 'tour__city', 'tour__title', 'tour__translations__title'
    ]
    ordering = ['tour', 'day_of_week', 'start_date']

    actions = [
        'auto_initialize_variant_capacities',
        'sync_capacities_from_variants',
        'validate_capacity_consistency',
        'export_capacity_report',
        'bulk_set_day_of_week',
        'auto_populate_day_of_week',
        'migrate_legacy_capacities'
    ]

    fieldsets = (
        (_('Schedule Information'), {
            'fields': ('tour', 'start_date', 'end_date', 'start_time', 'end_time', 'day_of_week'),
            'description': _('Basic schedule information. Day of week can be auto-populated from start date.')
        }),
        (_('Capacity Overview'), {
            'fields': (
                'total_capacity_display',
                'reserved_capacity_display',
                'confirmed_capacity_display',
                'available_capacity_display',
                'capacity_status_display'
            ),
            'description': _('Overall capacity statistics for this schedule.')
        }),
        (_('Pricing Adjustments'), {
            'fields': ('price_adjustment', 'price_adjustment_type'),
            'classes': ('collapse',),
            'description': _('Optional price adjustments for this specific schedule.')
        }),
        (_('Status & Availability'), {
            'fields': ('is_available', 'availability_override', 'availability_note')
        }),
        (_('Legacy Data (Deprecated)'), {
            'fields': ('variant_capacities_raw',),
            'classes': ('collapse',),
            'description': _('Legacy JSON field - will be removed after migration. Use the Variant Capacities section below.')
        }),
    )
    readonly_fields = [
        'total_capacity_display',
        'reserved_capacity_display',
        'confirmed_capacity_display',
        'available_capacity_display',
        'capacity_status_display'
    ]

    def total_capacity_display(self, obj):
        total, available = _compute_schedule_caps(obj)
        return total
    total_capacity_display.short_description = _('Total capacity')

    def available_capacity_display(self, obj):
        total, available = _compute_schedule_caps(obj)
        return available
    available_capacity_display.short_description = _('Available capacity')

    def reserved_capacity_display(self, obj):
        """Display reserved capacity using TourCapacityService."""
        if obj and obj.pk:
            try:
                from tours.services import TourCapacityService
                # Get reserved capacity from TourCapacityService
                return obj.total_reserved_capacity
            except Exception:
                # Fallback to old method
                return 0
        return 0
    reserved_capacity_display.short_description = _('Reserved')

    def confirmed_capacity_display(self, obj):
        """Display confirmed capacity using TourCapacityService."""
        if obj and obj.pk:
            try:
                from tours.services import TourCapacityService
                # Get confirmed capacity from TourCapacityService
                return obj.total_confirmed_capacity
            except Exception:
                # Fallback to old method
                return 0
        return 0
    confirmed_capacity_display.short_description = _('Confirmed')

    def capacity_status_display(self, obj):
        """Display comprehensive capacity status."""
        if obj and obj.pk:
            try:
                from tours.services import TourCapacityService
                total = obj.compute_total_capacity()
                reserved = obj.total_reserved_capacity
                confirmed = obj.total_confirmed_capacity
                available = max(0, total - reserved - confirmed)

                status_html = f"""
                <div style="font-family: monospace; font-size: 11px;">
                    <strong>Total:</strong> {total}<br>
                    <strong>Reserved:</strong> {reserved}<br>
                    <strong>Confirmed:</strong> {confirmed}<br>
                    <strong>Available:</strong> {available}<br>
                    <strong>Utilization:</strong> {((total - available) / total * 100):.1f}%
                </div>
                """
                return format_html(status_html)
            except Exception as e:
                return f"Error: {str(e)}"
        return "Not available"
    capacity_status_display.short_description = _('Capacity Status')

    def variant_capacity_table(self, obj):
        """Display variant capacities in a formatted table."""
        if obj and obj.pk and obj.variant_capacities:
            try:
                from tours.services import TourCapacityService

                table_html = """
                <table style="border-collapse: collapse; font-size: 11px; width: 100%;">
                <thead>
                    <tr style="background: #f5f5f5;">
                        <th style="border: 1px solid #ddd; padding: 4px;">Variant</th>
                        <th style="border: 1px solid #ddd; padding: 4px;">Total</th>
                        <th style="border: 1px solid #ddd; padding: 4px;">Booked</th>
                        <th style="border: 1px solid #ddd; padding: 4px;">Available</th>
                        <th style="border: 1px solid #ddd; padding: 4px;">Utilization</th>
                    </tr>
                </thead>
                <tbody>
                """

                for variant_id, data in obj.variant_capacities.items():
                    total = data.get('total', 0)
                    booked = data.get('booked', 0)
                    available = data.get('available', 0)
                    utilization = (booked / total * 100) if total > 0 else 0

                    # Get variant name
                    try:
                        variant = obj.tour.variants.filter(id=variant_id).first()
                        variant_name = variant.name if variant else variant_id
                    except:
                        variant_name = variant_id

                    table_html += f"""
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 4px;">{variant_name}</td>
                        <td style="border: 1px solid #ddd; padding: 4px; text-align: center;">{total}</td>
                        <td style="border: 1px solid #ddd; padding: 4px; text-align: center;">{booked}</td>
                        <td style="border: 1px solid #ddd; padding: 4px; text-align: center;">{available}</td>
                        <td style="border: 1px solid #ddd; padding: 4px; text-align: center;">{utilization:.1f}%</td>
                    </tr>
                    """

                table_html += "</tbody></table>"
                return format_html(table_html)

            except Exception as e:
                return f"Error: {str(e)}"

        return "No variant data"
    variant_capacity_table.short_description = _('Variant Capacities')

    def save_model(self, request, obj, form, change):
        """On save, ensure capacities are initialized if empty."""
        # Validate the model before saving
        obj.full_clean()
        super().save_model(request, obj, form, change)
        try:
            obj.initialize_variant_capacities()
        except Exception:
            pass

    # Admin Actions
    def auto_initialize_variant_capacities(self, request, queryset):
        """Admin action: Initialize variant capacities from tour variants."""
        initialized = 0
        for schedule in queryset:
            for variant in schedule.tour.variants.filter(is_active=True):
                capacity, created = TourScheduleVariantCapacity.objects.get_or_create(
                    schedule=schedule,
                    variant=variant,
                    defaults={
                        'total_capacity': variant.capacity,
                        'reserved_capacity': 0,
                        'confirmed_capacity': 0,
                        'is_available': True,
                    }
                )
                if created:
                    initialized += 1
        
        self.message_user(request, f"Initialized {initialized} variant capacities.")
    auto_initialize_variant_capacities.short_description = _('Auto-initialize variant capacities from tour variants')
    
    def sync_capacities_from_variants(self, request, queryset):
        """Admin action: Sync capacities with tour variant defaults."""
        synced = 0
        for schedule in queryset:
            for capacity in schedule.variant_capacities.all():
                if capacity.variant.capacity != capacity.total_capacity:
                    capacity.total_capacity = capacity.variant.capacity
                    capacity.save(update_fields=['total_capacity'])
                    synced += 1
        
        self.message_user(request, f"Synced {synced} capacity records with variant defaults.")
    sync_capacities_from_variants.short_description = _('Sync capacities with variant defaults')
    
    def migrate_legacy_capacities(self, request, queryset):
        """Admin action: Migrate legacy JSON capacities to relational model."""
        migrated = 0
        for schedule in queryset:
            if schedule.variant_capacities_raw:
                try:
                    capacities_data = schedule.variant_capacities_raw
                    if isinstance(capacities_data, dict):
                        for variant_id_str, capacity_data in capacities_data.items():
                            try:
                                variant = schedule.tour.variants.get(id=variant_id_str)
                                total_capacity = capacity_data.get('total', variant.capacity)
                                booked_capacity = capacity_data.get('booked', 0)
                                
                                capacity, created = TourScheduleVariantCapacity.objects.get_or_create(
                                    schedule=schedule,
                                    variant=variant,
                                    defaults={
                                        'total_capacity': total_capacity,
                                        'reserved_capacity': 0,
                                        'confirmed_capacity': booked_capacity,
                                        'is_available': True,
                                    }
                                )
                                if created:
                                    migrated += 1
                            except Exception as e:
                                self.message_user(request, f"Error migrating variant {variant_id_str}: {e}", level='ERROR')
                except Exception as e:
                    self.message_user(request, f"Error processing schedule {schedule.id}: {e}", level='ERROR')
        
        self.message_user(request, f"Migrated {migrated} legacy capacity records.")
    migrate_legacy_capacities.short_description = _('Migrate legacy JSON capacities to relational model')

    def refresh_capacities(self, request, queryset):
        """Admin action: Refresh capacity data from database."""
        from tours.services import TourCapacityService

        updated = 0
        errors = 0

        for schedule in queryset:
            try:
                # Force refresh from database
                schedule.refresh_from_db()

                # Update capacity tracking
                available = TourCapacityService.get_available_capacity(schedule.id)
                if available is not None:
                    updated += 1
                else:
                    errors += 1

            except Exception as e:
                self.message_user(
                    request,
                    f"Error refreshing capacity for {schedule}: {str(e)}",
                    level='error'
                )
                errors += 1

        if updated > 0:
            self.message_user(request, f"Successfully refreshed {updated} schedules.")
        if errors > 0:
            self.message_user(request, f"Errors occurred for {errors} schedules.", level='warning')
    refresh_capacities.short_description = _('Refresh capacity data from database')

    def reset_capacities(self, request, queryset):
        """Admin action: Reset capacity tracking to initial state."""
        from tours.services import TourCapacityService

        reset_count = 0
        for schedule in queryset:
            try:
                # Reset capacity tracking fields
                schedule.total_reserved_capacity = 0
                schedule.total_confirmed_capacity = 0
                schedule.save(update_fields=['total_reserved_capacity', 'total_confirmed_capacity'])

                # Re-initialize variant capacities
                schedule.initialize_variant_capacities()
                reset_count += 1

            except Exception as e:
                self.message_user(
                    request,
                    f"Error resetting capacity for {schedule}: {str(e)}",
                    level='error'
                )

        self.message_user(request, f"Reset capacity tracking for {reset_count} schedules.")
    reset_capacities.short_description = _('Reset capacity tracking to initial state')

    def show_capacity_details(self, request, queryset):
        """Admin action: Show detailed capacity information."""
        from tours.services import TourCapacityService
        from orders.models import OrderItem
        from cart.models import CartItem

        details = []
        for schedule in queryset:
            try:
                total = schedule.compute_total_capacity()
                reserved = schedule.total_reserved_capacity
                confirmed = schedule.total_confirmed_capacity
                available = max(0, total - reserved - confirmed)

                # Count active bookings
                cart_bookings = CartItem.objects.filter(
                    product_type='tour',
                    product_id=schedule.tour.id,
                    booking_date=schedule.start_date
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                order_bookings = OrderItem.objects.filter(
                    product_type='tour',
                    product_id=schedule.tour.id,
                    booking_date=schedule.start_date,
                    order__status__in=['pending', 'confirmed', 'paid', 'completed']
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                details.append(f"""
                Schedule: {schedule.tour.title} - {schedule.start_date}
                Total Capacity: {total}
                Reserved (TourCapacityService): {reserved}
                Confirmed (TourCapacityService): {confirmed}
                Available (TourCapacityService): {available}
                Cart Bookings: {cart_bookings}
                Order Bookings: {order_bookings}
                -------------------
                """)

            except Exception as e:
                details.append(f"Error for {schedule}: {str(e)}")

        # Show details in a message
        full_details = "\n".join(details)
        self.message_user(request, f"Capacity Details:\n{full_details}")
    show_capacity_details.short_description = _('Show detailed capacity information')

    def sync_with_capacity_service(self, request, queryset):
        """Admin action: Synchronize variant_capacities_raw with TourCapacityService."""
        from tours.services import TourCapacityService

        synced = 0
        for schedule in queryset:
            try:
                # Get current capacity data
                total = schedule.compute_total_capacity()
                reserved = schedule.total_reserved_capacity
                confirmed = schedule.total_confirmed_capacity

                # Update variant_capacities_raw to reflect current state
                if schedule.variant_capacities:
                    for variant_id, data in schedule.variant_capacities.items():
                        variant_total = data.get('total', 0)
                        # Distribute confirmed capacity proportionally
                        if total > 0:
                            variant_confirmed = int((confirmed / total) * variant_total)
                            data['booked'] = variant_confirmed
                            data['available'] = max(0, variant_total - variant_confirmed)

                    schedule.save(update_fields=['variant_capacities_raw'])

                synced += 1

            except Exception as e:
                self.message_user(
                    request,
                    f"Error syncing {schedule}: {str(e)}",
                    level='error'
                )

        self.message_user(request, f"Synchronized {synced} schedules with capacity service.")
    sync_with_capacity_service.short_description = _('Sync variant_capacities_raw with TourCapacityService')

    def force_capacity_update(self, request, queryset):
        """Admin action: Force update capacity using TourCapacityService directly."""
        from tours.services import TourCapacityService

        updated = 0
        errors = 0

        for schedule in queryset:
            try:
                # Get all confirmed bookings for this schedule
                from orders.models import OrderItem
                confirmed_bookings = OrderItem.objects.filter(
                    product_type='tour',
                    product_id=schedule.tour.id,
                    booking_date=schedule.start_date,
                    order__status__in=['confirmed', 'paid', 'completed']
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                # Reset and update capacity tracking
                schedule.total_reserved_capacity = 0
                schedule.total_confirmed_capacity = confirmed_bookings
                schedule.save(update_fields=['total_reserved_capacity', 'total_confirmed_capacity'])

                # Update variant_capacities_raw proportionally
                if schedule.variant_capacities:
                    total_capacity = schedule.compute_total_capacity()
                    if total_capacity > 0:
                        for variant_id, data in schedule.variant_capacities.items():
                            variant_total = data.get('total', 0)
                            if variant_total > 0:
                                # Distribute confirmed bookings proportionally
                                variant_confirmed = int((confirmed_bookings / total_capacity) * variant_total)
                                data['booked'] = variant_confirmed
                                data['available'] = max(0, variant_total - variant_confirmed)

                        schedule.save(update_fields=['variant_capacities_raw'])

                updated += 1

            except Exception as e:
                self.message_user(
                    request,
                    f"Error force updating {schedule}: {str(e)}",
                    level='error'
                )
                errors += 1

        if updated > 0:
            self.message_user(request, f"Force updated {updated} schedules.")
        if errors > 0:
            self.message_user(request, f"Errors occurred for {errors} schedules.", level='warning')
    force_capacity_update.short_description = _('Force capacity update from confirmed bookings')

    def validate_capacity_consistency(self, request, queryset):
        """Admin action: Validate capacity consistency between different tracking methods."""
        from tours.services import TourCapacityService
        from orders.models import OrderItem
        from cart.models import CartItem

        inconsistencies = []

        for schedule in queryset:
            try:
                # Method 1: TourCapacityService
                service_available = TourCapacityService.get_available_capacity(schedule.id) or 0

                # Method 2: Direct calculation from orders/cart
                total_capacity = schedule.compute_total_capacity()

                cart_bookings = CartItem.objects.filter(
                    product_type='tour',
                    product_id=schedule.tour.id,
                    booking_date=schedule.start_date
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                order_bookings = OrderItem.objects.filter(
                    product_type='tour',
                    product_id=schedule.tour.id,
                    booking_date=schedule.start_date,
                    order__status__in=['pending', 'confirmed', 'paid', 'completed']
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                direct_available = total_capacity - cart_bookings - order_bookings

                # Method 3: Model fields
                model_available = schedule.available_capacity

                # Check consistency
                if abs(service_available - direct_available) > 1 or abs(service_available - model_available) > 1:
                    inconsistencies.append(f"""
                    Schedule: {schedule.tour.title} - {schedule.start_date}
                    Service Available: {service_available}
                    Direct Available: {direct_available}
                    Model Available: {model_available}
                    Difference: {abs(service_available - direct_available)}
                    -------------------
                    """)

            except Exception as e:
                inconsistencies.append(f"Error validating {schedule}: {str(e)}")

        if inconsistencies:
            full_report = "\n".join(inconsistencies)
            self.message_user(request, f"Capacity Inconsistencies Found:\n{full_report}")
        else:
            self.message_user(request, "All schedules have consistent capacity data.")
    validate_capacity_consistency.short_description = _('Validate capacity consistency')

    def bulk_initialize_capacities(self, request, queryset):
        """Admin action: Bulk initialize capacities for multiple schedules."""
        initialized = 0
        skipped = 0

        for schedule in queryset:
            try:
                # Check if already initialized
                if not schedule.variant_capacities or not any(schedule.variant_capacities.values()):
                    schedule.initialize_variant_capacities()
                    initialized += 1
                else:
                    skipped += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error initializing {schedule}: {str(e)}",
                    level='error'
                )

        self.message_user(
            request,
            f"Initialized capacities for {initialized} schedules. Skipped {skipped} already initialized."
        )
    bulk_initialize_capacities.short_description = _('Bulk initialize variant capacities')

    def export_capacity_report(self, request, queryset):
        """Admin action: Export capacity report as CSV."""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tour_capacity_report.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Tour', 'Schedule Date', 'Total Capacity', 'Reserved', 'Confirmed',
            'Available', 'Utilization %', 'Cart Bookings', 'Order Bookings'
        ])

        for schedule in queryset:
            try:
                from orders.models import OrderItem
                from cart.models import CartItem

                total = schedule.compute_total_capacity()
                reserved = schedule.total_reserved_capacity
                confirmed = schedule.total_confirmed_capacity
                available = max(0, total - reserved - confirmed)
                utilization = ((total - available) / total * 100) if total > 0 else 0

                cart_bookings = CartItem.objects.filter(
                    product_type='tour',
                    product_id=schedule.tour.id,
                    booking_date=schedule.start_date
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                order_bookings = OrderItem.objects.filter(
                    product_type='tour',
                    product_id=schedule.tour.id,
                    booking_date=schedule.start_date,
                    order__status__in=['pending', 'confirmed', 'paid', 'completed']
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                writer.writerow([
                    str(schedule.tour.title),
                    str(schedule.start_date),
                    total,
                    reserved,
                    confirmed,
                    available,
                    f"{utilization:.1f}",
                    cart_bookings,
                    order_bookings
                ])

            except Exception as e:
                writer.writerow([str(schedule), 'ERROR', str(e)])

        return response
    export_capacity_report.short_description = _('Export capacity report as CSV')

    def bulk_set_day_of_week(self, request, queryset):
        """Bulk set day of week for selected schedules."""
        if request.POST.get('post'):
            day_of_week = request.POST.get('day_of_week')
            if day_of_week is not None:
                day_of_week = int(day_of_week)
                updated = queryset.update(day_of_week=day_of_week)
                self.message_user(
                    request,
                    _('Successfully updated day of week for %(count)d schedules.') % {'count': updated},
                    level=messages.SUCCESS
                )
                return HttpResponseRedirect(request.get_full_path())
        else:
            # Show form
            context = {
                'title': _('Set Day of Week'),
                'queryset': queryset,
                'day_choices': [
                    (0, _('Monday')),
                    (1, _('Tuesday')),
                    (2, _('Wednesday')),
                    (3, _('Thursday')),
                    (4, _('Friday')),
                    (5, _('Saturday')),
                    (6, _('Sunday')),
                ],
                'action_name': 'bulk_set_day_of_week',
            }
            return render(request, 'admin/tours/tourschedule/bulk_set_day_of_week.html', context)
    bulk_set_day_of_week.short_description = _('Set day of week for selected schedules')

    def auto_populate_day_of_week(self, request, queryset):
        """Auto-populate day of week based on start date."""
        updated_count = 0
        for schedule in queryset:
            if schedule.start_date:
                old_day = schedule.day_of_week
                schedule.day_of_week = schedule.start_date.weekday()
                if old_day != schedule.day_of_week:
                    schedule.save()
                    updated_count += 1
        
        if updated_count > 0:
            self.message_user(
                request,
                _('Successfully auto-populated day of week for %(count)d schedules.') % {'count': updated_count},
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                _('No schedules needed day of week updates.'),
                level=messages.INFO
            )
    auto_populate_day_of_week.short_description = _('Auto-populate day of week from start date')

    def day_of_week_display(self, obj):
        """Display day of week with better formatting."""
        if obj.day_of_week is not None:
            day_names = {
                0: _('Monday'),
                1: _('Tuesday'),
                2: _('Wednesday'),
                3: _('Thursday'),
                4: _('Friday'),
                5: _('Saturday'),
                6: _('Sunday'),
            }
            return day_names.get(obj.day_of_week, _('Unknown'))
        return _('Not set')
    day_of_week_display.short_description = _('Day of Week')
    day_of_week_display.admin_order_field = 'day_of_week'

    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('tour').prefetch_related('bookings')


def _compute_schedule_caps(schedule: TourSchedule):
    """Compute (total, available) for a schedule with robust fallbacks."""
    try:
        schedule.initialize_variant_capacities()
        caps = schedule.variant_capacities
        total = sum(int(v.get('total', 0) or 0) for v in caps.values())
        available = sum(int(v.get('available', 0) or 0) for v in caps.values())
        if total == 0:
            # Fallback to schedule-level fields
            try:
                sched_total = int(getattr(schedule, 'max_capacity', 0) or 0)
                sched_current = int(getattr(schedule, 'current_capacity', 0) or 0)
                if sched_total > 0:
                    total = sched_total
                    available = max(0, sched_total - sched_current)
            except Exception:
                pass
        if total == 0:
            # Derive from variants and bookings
            try:
                variant_total = sum(int(v.capacity or 0) for v in schedule.tour.variants.filter(is_active=True))
                if variant_total > 0:
                    total = variant_total
                    from cart.models import CartItem
                    from orders.models import OrderItem
                    cart_bookings = CartItem.objects.filter(
                        product_type='tour', product_id=schedule.tour.id, booking_date=schedule.start_date
                    ).aggregate(total=Sum('quantity'))['total'] or 0
                    order_bookings = OrderItem.objects.filter(
                        product_type='tour', product_id=schedule.tour.id, booking_date=schedule.start_date,
                        order__status__in=['confirmed', 'paid', 'completed']
                    ).aggregate(total=Sum('quantity'))['total'] or 0
                    booked = int(cart_bookings) + int(order_bookings)
                    available = max(0, total - booked)
            except Exception:
                pass
        return total, available
    except Exception:
        return 0, 0
    
    def booking_count(self, obj):
        """Get number of bookings for this schedule."""
        return obj.bookings.count()
    booking_count.short_description = _('Bookings')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('tour').prefetch_related('bookings')


@admin.register(TourScheduleVariantCapacity)
class TourScheduleVariantCapacityAdmin(admin.ModelAdmin):
    """Admin for TourScheduleVariantCapacity model."""
    
    list_display = [
        'schedule', 'variant', 'total_capacity', 'reserved_capacity', 
        'confirmed_capacity', 'available_capacity_display', 'utilization_display',
        'price_adjustment', 'is_available', 'created_at'
    ]
    list_filter = [
        'is_available', 'price_adjustment_type', 'schedule__tour', 'variant',
        'created_at', 'updated_at'
    ]
    search_fields = [
        'schedule__tour__title', 'schedule__tour__slug', 'variant__name',
        'availability_note'
    ]
    ordering = ['schedule', 'variant__name']
    autocomplete_fields = ['schedule', 'variant']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('schedule', 'variant')
        }),
        (_('Capacity Management'), {
            'fields': (
                'total_capacity', 'reserved_capacity', 'confirmed_capacity',
                'available_capacity_display', 'utilization_display'
            )
        }),
        (_('Pricing'), {
            'fields': ('price_adjustment', 'price_adjustment_type')
        }),
        (_('Availability'), {
            'fields': ('is_available', 'availability_note')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['available_capacity_display', 'utilization_display']
    
    def available_capacity_display(self, obj):
        """Display available capacity with color coding."""
        if obj.pk:
            available = obj.available_capacity
            if available <= 0:
                return format_html('<span style="color: red; font-weight: bold;">{}</span>', available)
            elif available <= 2:
                return format_html('<span style="color: orange; font-weight: bold;">{}</span>', available)
            else:
                return format_html('<span style="color: green;">{}</span>', available)
        return '-'
    available_capacity_display.short_description = _('Available')
    
    def utilization_display(self, obj):
        """Display utilization percentage with color coding."""
        if obj.pk:
            utilization = obj.utilization_percentage
            if utilization >= 90:
                color = 'red'
            elif utilization >= 70:
                color = 'orange'
            else:
                color = 'green'
            return format_html('<span style="color: {};">{}%</span>', color, f"{utilization:.1f}")
        return '-'
    utilization_display.short_description = _('Utilization')
    
    actions = [
        'reset_reserved_capacity',
        'sync_with_variant_defaults',
        'export_capacity_report'
    ]
    
    def reset_reserved_capacity(self, request, queryset):
        """Reset reserved capacity to 0."""
        updated = queryset.update(reserved_capacity=0)
        self.message_user(request, f"Reset reserved capacity for {updated} records.")
    reset_reserved_capacity.short_description = _('Reset reserved capacity to 0')
    
    def sync_with_variant_defaults(self, request, queryset):
        """Sync total capacity with variant defaults."""
        synced = 0
        for capacity in queryset:
            if capacity.variant.capacity != capacity.total_capacity:
                capacity.total_capacity = capacity.variant.capacity
                capacity.save(update_fields=['total_capacity'])
                synced += 1
        
        self.message_user(request, f"Synced {synced} capacity records with variant defaults.")
    sync_with_variant_defaults.short_description = _('Sync with variant defaults')
    
    def export_capacity_report(self, request, queryset):
        """Export capacity report as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="variant_capacity_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Tour', 'Schedule Date', 'Variant', 'Total Capacity', 'Reserved', 
            'Confirmed', 'Available', 'Utilization %', 'Price Adjustment', 'Available'
        ])
        
        for capacity in queryset:
            writer.writerow([
                str(capacity.schedule.tour.title),
                str(capacity.schedule.start_date),
                str(capacity.variant.name),
                capacity.total_capacity,
                capacity.reserved_capacity,
                capacity.confirmed_capacity,
                capacity.available_capacity,
                f"{capacity.utilization_percentage:.1f}",
                capacity.price_adjustment,
                capacity.is_available
            ])
        
        return response
    export_capacity_report.short_description = _('Export capacity report as CSV')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('schedule__tour', 'variant')


@admin.register(TourItinerary)
class TourItineraryAdmin(TranslatableAdmin):
    """Admin for TourItinerary model."""
    

    
    list_display = [
        'tour', 'order', 'get_title', 'duration_minutes', 'location'
    ]
    list_filter = [
        'tour__tour_type'
    ]
    search_fields = [
        'translations__title', 'translations__description', 'location', 'tour__slug'
    ]
    ordering = ['tour', 'order']
    
    def get_title(self, obj):
        """Get the translated title for display in list."""
        try:
            return obj.title if obj.title else f"Itinerary {obj.order}"
        except:
            return f"Itinerary {obj.order}"
    get_title.short_description = _('Title')
    get_title.admin_order_field = 'translations__title'
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('tour', 'order'),
            'description': _('Core information about the itinerary item.')
        }),
        (_('Details'), {
            'fields': ('duration_minutes', 'location', 'image', 'coordinates'),
            'description': _('Additional details about the itinerary stop.')
        }),
    )
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('tour')


@admin.register(TourPricing)
class TourPricingAdmin(admin.ModelAdmin):
    """Admin for TourPricing model."""
    
    list_display = [
        'tour', 'variant', 'age_group', 'factor', 'is_free', 'final_price'
    ]
    list_filter = [
        'age_group', 'is_free', 'requires_services'
    ]
    search_fields = [
        'tour__slug', 'variant__name'
    ]
    ordering = ['tour', 'variant', 'age_group']
    
    fieldsets = (
        (_('Pricing Information'), {
            'fields': ('tour', 'variant', 'age_group')
        }),
        (_('Pricing Details'), {
            'fields': ('factor', 'is_free', 'requires_services')
        }),
    )
    
    def final_price(self, obj):
        """Calculate final price."""
        if obj.is_free:
            return "Free"
        return f"${obj.final_price:.2f}"
    final_price.short_description = _('Final Price')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('tour', 'variant')


@admin.register(TourOption)
class TourOptionAdmin(admin.ModelAdmin):
    """Admin for TourOption model."""
    
    list_display = [
        'name', 'tour', 'option_type', 'price', 'price_percentage', 'availability_status', 'is_active'
    ]
    list_filter = [
        'option_type', 'is_active', 'is_available'
    ]
    search_fields = [
        'name', 'description', 'tour__slug'
    ]
    ordering = ['tour', 'name']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('tour', 'name', 'description', 'option_type')
        }),
        (_('Pricing'), {
            'fields': ('price', 'price_percentage', 'currency')
        }),
        (_('Availability'), {
            'fields': ('is_available', 'max_quantity')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def availability_status(self, obj):
        """Display availability status for this option."""
        if obj.is_available_for_quantity(1):
            return format_html('<span style="color: green;">✓ Available</span>')
        else:
            return format_html('<span style="color: red;">✗ Unavailable</span>')
    availability_status.short_description = _('Availability')
    availability_status.allow_tags = True
    
    actions = ['test_option_availability']
    
    def test_option_availability(self, request, queryset):
        """Admin action: test availability for selected options."""
        available = 0
        unavailable = 0
        for option in queryset:
            try:
                if option.is_available_for_quantity(1):
                    available += 1
                else:
                    unavailable += 1
            except Exception:
                unavailable += 1
        
        self.message_user(request, _(f"Availability check: {available} available, {unavailable} unavailable options."))
    test_option_availability.short_description = _('Test option availability')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('tour')


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    """Admin interface for ReviewReport model."""
    
    list_display = [
        'id', 'review_title', 'reporter_name', 'reason', 'status', 
        'created_at', 'moderated_by', 'moderated_at'
    ]
    list_filter = [
        'status', 'reason', 'created_at', 'moderated_at'
    ]
    search_fields = [
        'review__title', 'reporter__username', 'reporter__email',
        'description', 'moderation_notes'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    fieldsets = (
        (_('Report Information'), {
            'fields': ('review', 'reporter', 'reason', 'description')
        }),
        (_('Status'), {
            'fields': ('status', 'action_taken')
        }),
        (_('Moderation'), {
            'fields': ('moderated_by', 'moderated_at', 'moderation_notes'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def review_title(self, obj):
        """Get review title."""
        return obj.review.title if obj.review else '-'
    review_title.short_description = _('Review Title')
    
    def reporter_name(self, obj):
        """Get reporter name."""
        return obj.reporter.get_full_name() or obj.reporter.username
    reporter_name.short_description = _('Reporter')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'review', 'reporter', 'moderated_by'
        )
    
    def save_model(self, request, obj, form, change):
        """Handle moderation actions."""
        if 'status' in form.changed_data and not obj.moderated_by:
            obj.moderated_by = request.user
            obj.moderated_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_investigating', 'mark_as_resolved', 'mark_as_dismissed']
    
    def mark_as_investigating(self, request, queryset):
        """Mark selected reports as investigating."""
        updated = queryset.update(
            status='investigating',
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports marked as investigating.')
    mark_as_investigating.short_description = _('Mark as investigating')
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected reports as resolved."""
        updated = queryset.update(
            status='resolved',
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports marked as resolved.')
    mark_as_resolved.short_description = _('Mark as resolved')
    
    def mark_as_dismissed(self, request, queryset):
        """Mark selected reports as dismissed."""
        updated = queryset.update(
            status='dismissed',
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports marked as dismissed.')
    mark_as_dismissed.short_description = _('Mark as dismissed')


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    """Admin interface for ReviewResponse model."""
    
    list_display = [
        'id', 'review_title', 'responder_name', 'is_public', 'is_official',
        'created_at', 'updated_at'
    ]
    list_filter = [
        'is_public', 'is_official', 'created_at', 'updated_at'
    ]
    search_fields = [
        'review__title', 'responder__username', 'responder__email', 'content'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    fieldsets = (
        (_('Response Information'), {
            'fields': ('review', 'responder', 'content')
        }),
        (_('Settings'), {
            'fields': ('is_public', 'is_official')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def review_title(self, obj):
        """Get review title."""
        return obj.review.title if obj.review else '-'
    review_title.short_description = _('Review Title')
    
    def responder_name(self, obj):
        """Get responder name."""
        return obj.responder.get_full_name() or obj.responder.username
    responder_name.short_description = _('Responder')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'review', 'responder'
        )
    
    actions = ['make_public', 'make_private', 'make_official', 'remove_official']
    
    def make_public(self, request, queryset):
        """Make selected responses public."""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} responses made public.')
    make_public.short_description = _('Make public')
    
    def make_private(self, request, queryset):
        """Make selected responses private."""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} responses made private.')
    make_private.short_description = _('Make private')
    
    def make_official(self, request, queryset):
        """Make selected responses official."""
        updated = queryset.update(is_official=True)
        self.message_user(request, f'{updated} responses made official.')
    make_official.short_description = _('Make official')
    
    def remove_official(self, request, queryset):
        """Remove official status from selected responses."""
        updated = queryset.update(is_official=False)
        self.message_user(request, f'{updated} responses no longer official.')
    remove_official.short_description = _('Remove official status')


# Update TourReviewAdmin to include new fields and functionality
class TourReviewAdmin(admin.ModelAdmin):
    """Admin interface for TourReview model."""
    
    list_display = [
        'id', 'review_title', 'user_name', 'tour_title', 'rating', 'status',
        'category', 'is_verified', 'is_helpful', 'created_at'
    ]
    list_filter = [
        'status', 'rating', 'category', 'is_verified', 'created_at'
    ]
    search_fields = [
        'title', 'comment', 'user__username', 'user__email', 'tour__slug'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    fieldsets = (
        (_('Review Information'), {
            'fields': ('user', 'tour', 'rating', 'title', 'comment', 'category')
        }),
        (_('Status & Verification'), {
            'fields': ('status', 'is_verified', 'is_helpful')
        }),
        (_('Moderation'), {
            'fields': ('moderated_by', 'moderated_at', 'moderation_notes'),
            'classes': ('collapse',)
        }),
        (_('Analytics'), {
            'fields': ('sentiment_score',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def review_title(self, obj):
        """Get review title."""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    review_title.short_description = _('Title')
    
    def user_name(self, obj):
        """Get user name."""
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = _('User')
    
    def tour_title(self, obj):
        """Get tour title."""
        return obj.tour.title[:50] + '...' if len(obj.tour.title) > 50 else obj.tour.title
    tour_title.short_description = _('Tour')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'user', 'tour', 'moderated_by'
        )
    
    actions = ['approve_reviews', 'reject_reviews', 'flag_reviews', 'verify_reviews']
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews."""
        updated = queryset.update(
            status='approved',
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = _('Approve reviews')
    
    def reject_reviews(self, request, queryset):
        """Reject selected reviews."""
        updated = queryset.update(
            status='rejected',
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} reviews rejected.')
    reject_reviews.short_description = _('Reject reviews')
    
    def flag_reviews(self, request, queryset):
        """Flag selected reviews for review."""
        updated = queryset.update(
            status='flagged',
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} reviews flagged.')
    flag_reviews.short_description = _('Flag reviews')
    
    def verify_reviews(self, request, queryset):
        """Verify selected reviews."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} reviews verified.')
    verify_reviews.short_description = _('Verify reviews')


class TourGalleryAdmin(admin.ModelAdmin):
    """Admin for TourGallery model with enhanced display."""
    
    list_display = [
        'image_preview', 'tour', 'title', 'order', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'tour', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'tour__title'
    ]
    ordering = ['tour', 'order', 'created_at']
    
    fieldsets = (
        (_('Image Information'), {
            'fields': ('tour', 'image', 'image_preview', 'title', 'description')
        }),
        (_('Display Settings'), {
            'fields': ('order', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    actions = ['activate_images', 'deactivate_images', 'reorder_images']
    
    def image_preview(self, obj):
        """Display image preview in admin."""
        if obj and obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; border: 1px solid #ddd;" />'
        return '<span style="color: #999; font-style: italic;">No image uploaded</span>'
    image_preview.short_description = _('Image Preview')
    image_preview.allow_tags = True
    
    def activate_images(self, request, queryset):
        """Activate selected images."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} images activated.')
    activate_images.short_description = _('Activate selected images')
    
    def deactivate_images(self, request, queryset):
        """Deactivate selected images."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} images deactivated.')
    deactivate_images.short_description = _('Deactivate selected images')
    
    def reorder_images(self, request, queryset):
        """Reorder images by creation date."""
        for index, image in enumerate(queryset.order_by('created_at')):
            image.order = index + 1
            image.save()
        self.message_user(request, f'{queryset.count()} images reordered.')
    reorder_images.short_description = _('Reorder images by creation date')


# Register the updated TourReviewAdmin
admin.site.register(TourReview, TourReviewAdmin)
admin.site.register(TourGallery, TourGalleryAdmin)
admin.site.register(Tour, TourAdmin)


@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
    """Admin for TourBooking model."""
    
    list_display = [
        'booking_reference', 'tour', 'variant', 'user', 'total_participants',
        'final_price', 'status', 'created_at'
    ]
    list_filter = [
        'status', 'booking_date', 'created_at'
    ]
    search_fields = [
        'booking_reference', 'tour__slug', 'user__username', 'user__email'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'booking_reference', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Booking Information'), {
            'fields': ('booking_reference', 'tour', 'variant', 'schedule', 'user')
        }),
        (_('Booking Details'), {
            'fields': ('booking_date', 'booking_time')
        }),
        (_('Participants'), {
            'fields': ('adult_count', 'child_count', 'infant_count')
        }),
        (_('Pricing'), {
            'fields': ('adult_price', 'child_price', 'infant_price', 'options_total', 'final_price')
        }),
        (_('Options'), {
            'fields': ('selected_options',)
        }),
        (_('Special Requirements'), {
            'fields': ('special_requirements',)
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_participants(self, obj):
        """Get total number of participants."""
        return obj.total_participants
    total_participants.short_description = _('Total Participants')
    
    def final_price(self, obj):
        """Get final price."""
        try:
            return f"${obj.grand_total:.2f}"
        except Exception:
            return "Error"
    final_price.short_description = _('Final Price')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('tour', 'variant', 'schedule', 'user') 