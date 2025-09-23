"""
Django Admin configuration for Transfers app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from .models import (
    TransferRoute, TransferRoutePricing, TransferOption, TransferBooking, 
    TransferCancellationPolicy, TransferLocation
)


class TransferRoutePricingInline(admin.TabularInline):
    """Inline admin for TransferRoutePricing."""
    
    model = TransferRoutePricing
    extra = 1
    fields = [
        'vehicle_type', 'vehicle_name', 'vehicle_description',
        'base_price', 'currency', 'max_passengers', 'max_luggage', 
        'features', 'amenities', 'is_active'
    ]
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Set default values for new pricing records
        if not obj:  # Creating new route
            form.base_fields['currency'].initial = 'USD'
            form.base_fields['features'].initial = ['AC', 'WiFi', 'Professional Driver']
            form.base_fields['amenities'].initial = ['Water', 'Tissue', 'USB Charger']
        
        return formset


class TransferCancellationPolicyInline(admin.TabularInline):
    """Inline admin for TransferCancellationPolicy."""
    
    model = TransferCancellationPolicy
    extra = 1
    fields = ['hours_before', 'refund_percentage', 'description', 'is_active']
    ordering = ['-hours_before']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Set default values for new policies
        if not obj:  # Creating new route
            form.base_fields['is_active'].initial = True
        
        return formset


class TransferOptionInline(admin.TabularInline):
    """Inline admin for TransferOption."""
    
    model = TransferOption
    extra = 1
    fields = [
        'option_type', 'price_type', 
        'price', 'price_percentage', 'max_quantity', 'is_active'
    ]
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Set default values for new options
        if not obj:  # Creating new route
            form.base_fields['price_type'].initial = 'fixed'
            form.base_fields['price'].initial = 0.00
            form.base_fields['price_percentage'].initial = 0.00
            form.base_fields['max_quantity'].initial = 5
        
        return formset


@admin.register(TransferRoute)
class TransferRouteAdmin(TranslatableAdmin):
    """Admin for TransferRoute model."""
    
    list_display = [
        'origin', 'destination', 'round_trip_discount_enabled', 
        'peak_hour_surcharge', 'midnight_surcharge', 'is_active'
    ]
    list_filter = [
        'is_active', 'round_trip_discount_enabled', 'is_popular',
        'origin', 'destination'
    ]
    search_fields = ['origin', 'destination', 'translations__name', 'translations__description']
    ordering = ['origin', 'destination']
    list_editable = ['is_active']
    
    inlines = [TransferRoutePricingInline, TransferCancellationPolicyInline, TransferOptionInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'origin', 'destination', 'slug')
        }),
        (_('Location References (New)'), {
            'fields': ('origin_location', 'destination_location'),
            'description': _('Link to specific locations for map-based selection'),
            'classes': ('collapse',)
        }),
        (_('Time-based Pricing'), {
            'fields': ('peak_hour_surcharge', 'midnight_surcharge'),
            'description': _('Set surcharge percentages for peak hours (7-9 AM, 5-7 PM) and midnight (10 PM-6 AM)')
        }),
        (_('Round Trip Settings'), {
            'fields': ('round_trip_discount_enabled', 'round_trip_discount_percentage'),
            'description': _('Enable round trip discounts and set percentage')
        }),
        (_('Cancellation Policy'), {
            'fields': ('cancellation_hours', 'refund_percentage'),
            'description': _('Set hours before departure for cancellation and refund percentage')
        }),
        (_('Popularity & Status'), {
            'fields': ('is_popular', 'is_admin_selected', 'popularity_score', 'booking_count', 'is_active'),
            'description': _('Control route visibility and popularity')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-generate slug and set default values."""
        if not obj.slug:
            from django.utils.text import slugify
            base_slug = f"{obj.origin}-to-{obj.destination}"
            obj.slug = slugify(base_slug)
        
        # Set default values for new routes
        if not change:  # Creating new route
            if not obj.peak_hour_surcharge:
                obj.peak_hour_surcharge = 10.00
            if not obj.midnight_surcharge:
                obj.midnight_surcharge = 5.00
            if not obj.round_trip_discount_percentage:
                obj.round_trip_discount_percentage = 10.00
        
        super().save_model(request, obj, form, change)


@admin.register(TransferRoutePricing)
class TransferRoutePricingAdmin(admin.ModelAdmin):
    """Admin for TransferRoutePricing model."""
    
    list_display = [
        'route', 'vehicle_type', 'vehicle_name', 'base_price', 'currency',
        'max_passengers', 'max_luggage', 'is_active'
    ]
    list_filter = ['vehicle_type', 'is_active', 'route', 'currency']
    search_fields = ['route__origin', 'route__destination', 'vehicle_name']
    ordering = ['route', 'vehicle_type']
    list_editable = ['is_active', 'base_price']
    
    fieldsets = (
        (_('Route & Vehicle'), {
            'fields': ('route', 'vehicle_type', 'vehicle_name', 'vehicle_description')
        }),
        (_('Pricing'), {
            'fields': ('base_price', 'currency', 'pricing_metadata'),
            'description': _('Set base price and currency. Pricing metadata is auto-generated.')
        }),
        (_('Capacity'), {
            'fields': ('max_passengers', 'max_luggage'),
            'description': _('Set maximum passengers and luggage capacity')
        }),
        (_('Features'), {
            'fields': ('features', 'amenities'),
            'description': _('Add features (AC, WiFi) and amenities (Water, Tissue)')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-generate pricing metadata if not provided."""
        if not obj.pricing_metadata:
            obj.pricing_metadata = {
                "pricing_type": "transfer",
                "calculation_method": "base_plus_surcharges",
                "version": "1.0",
                "features": {
                    "time_based_surcharges": True,
                    "round_trip_discounts": True,
                    "options_support": True
                }
            }
        
        # Set default values for new pricing
        if not change:  # Creating new pricing
            if not obj.currency:
                obj.currency = 'USD'
            if not obj.features:
                obj.features = ['AC', 'WiFi', 'Professional Driver']
            if not obj.amenities:
                obj.amenities = ['Water', 'Tissue', 'USB Charger']
        
        super().save_model(request, obj, form, change)


@admin.register(TransferOption)
class TransferOptionAdmin(TranslatableAdmin):
    """Admin for TransferOption model."""
    
    list_display = [
        'name', 'option_type', 'price_type', 'price', 'price_percentage', 
        'route', 'vehicle_type', 'is_active'
    ]
    list_filter = ['option_type', 'price_type', 'is_active', 'route', 'vehicle_type']
    search_fields = ['translations__name', 'translations__description']
    ordering = ['option_type', 'id']
    list_editable = ['is_active', 'price']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'option_type')
        }),
        (_('Pricing'), {
            'fields': ('price_type', 'price', 'price_percentage'),
            'description': _('Choose between fixed amount or percentage of base price')
        }),
        (_('Scope'), {
            'fields': ('route', 'vehicle_type'),
            'description': _('Leave empty to apply to all routes/vehicles, or limit to specific ones')
        }),
        (_('Restrictions'), {
            'fields': ('max_quantity',),
            'description': _('Maximum quantity a customer can select')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set default values for new options."""
        if not change:  # Creating new option
            if obj.price_type == 'fixed' and not obj.price:
                obj.price = 0.00
            elif obj.price_type == 'percentage' and not obj.price_percentage:
                obj.price_percentage = 0.00
        
        super().save_model(request, obj, form, change)


@admin.register(TransferBooking)
class TransferBookingAdmin(admin.ModelAdmin):
    """Admin for TransferBooking model."""
    
    list_display = [
        'booking_reference', 'route', 'pricing', 'trip_type', 
        'passenger_count', 'final_price', 'status', 'created_at'
    ]
    list_filter = ['trip_type', 'status', 'outbound_date', 'created_at']
    search_fields = ['booking_reference', 'contact_name', 'contact_phone']
    ordering = ['-created_at']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Booking Information'), {
            'fields': ('booking_reference', 'route', 'pricing', 'trip_type', 'user')
        }),
        (_('Trip Details'), {
            'fields': ('outbound_date', 'outbound_time', 'outbound_price', 'return_date', 'return_time', 'return_price')
        }),
        (_('Passenger Information'), {
            'fields': ('passenger_count', 'luggage_count')
        }),
        (_('Pickup Details'), {
            'fields': ('pickup_address', 'pickup_instructions')
        }),
        (_('Drop-off Details'), {
            'fields': ('dropoff_address', 'dropoff_instructions')
        }),
        (_('Contact Information'), {
            'fields': ('contact_name', 'contact_phone')
        }),
        (_('Pricing'), {
            'fields': ('round_trip_discount', 'options_total', 'final_price', 'selected_options')
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


# Customize admin site
admin.site.site_header = _('Peykan Tourism Admin')
admin.site.site_title = _('Peykan Tourism')
admin.site.index_title = _('Transfer Management')

# Add quick actions to existing admin
TransferRouteAdmin.actions = ['make_popular', 'make_inactive', 'duplicate_route']

def make_popular(self, request, queryset):
    """Mark selected routes as popular."""
    updated = queryset.update(is_popular=True)
    self.message_user(request, f'{updated} routes marked as popular.')
make_popular.short_description = "Mark selected routes as popular"

def make_inactive(self, request, queryset):
    """Mark selected routes as inactive."""
    updated = queryset.update(is_active=False)
    self.message_user(request, f'{updated} routes marked as inactive.')
make_inactive.short_description = "Mark selected routes as inactive"

def duplicate_route(self, request, queryset):
    """Duplicate selected routes."""
    for route in queryset:
        new_route = TransferRoute.objects.create(
            origin=f"{route.origin} (Copy)",
            destination=f"{route.destination} (Copy)",
            peak_hour_surcharge=route.peak_hour_surcharge,
            midnight_surcharge=route.midnight_surcharge,
            round_trip_discount_enabled=route.round_trip_discount_enabled,
            round_trip_discount_percentage=route.round_trip_discount_percentage,
            cancellation_hours=route.cancellation_hours,
            refund_percentage=route.refund_percentage,
            is_active=False  # Start as inactive for review
        )
        
        # Copy pricing
        for pricing in route.pricing.all():
            TransferRoutePricing.objects.create(
                route=new_route,
                vehicle_type=pricing.vehicle_type,
                vehicle_name=pricing.vehicle_name,
                vehicle_description=pricing.vehicle_description,
                base_price=pricing.base_price,
                currency=pricing.currency,
                max_passengers=pricing.max_passengers,
                max_luggage=pricing.max_luggage,
                features=pricing.features,
                amenities=pricing.amenities,
                pricing_metadata=pricing.pricing_metadata,
                is_active=False  # Start as inactive for review
            )
    
    self.message_user(request, f'{queryset.count()} routes duplicated successfully.')
duplicate_route.short_description = "Duplicate selected routes"

# Add methods to TransferRouteAdmin
TransferRouteAdmin.make_popular = make_popular
TransferRouteAdmin.make_inactive = make_inactive
TransferRouteAdmin.duplicate_route = duplicate_route


@admin.register(TransferLocation)
class TransferLocationAdmin(TranslatableAdmin):
    """Admin for TransferLocation model."""
    
    list_display = [
        'name', 'city', 'country', 'location_type', 'latitude', 'longitude',
        'is_popular', 'is_active'
    ]
    list_filter = [
        'location_type', 'city', 'country', 'is_popular', 'is_active'
    ]
    search_fields = [
        'translations__name', 'translations__description', 'address', 'city', 'country'
    ]
    ordering = ['city', 'country', 'id']
    list_editable = ['is_popular', 'is_active']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'address', 'city', 'country')
        }),
        (_('Location Details'), {
            'fields': ('latitude', 'longitude', 'location_type'),
            'description': _('Coordinates for map display and location categorization')
        }),
        (_('Status'), {
            'fields': ('is_popular', 'is_active'),
            'description': _('Control location visibility and popularity')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set default values for new locations."""
        if not change:  # Creating new location
            if not obj.country:
                obj.country = 'Iran'
        
        super().save_model(request, obj, form, change) 