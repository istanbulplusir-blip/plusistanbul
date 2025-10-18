"""
Admin configuration for Car Rentals.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from .models import (
    CarRentalCategory,
    CarRentalLocation,
    CarRental,
    CarRentalImage,
    CarRentalOption,
    CarRentalAvailability,
    CarRentalBooking
)


@admin.register(CarRentalCategory)
class CarRentalCategoryAdmin(TranslatableAdmin):
    list_display = ['name', 'sort_order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['translations__name', 'translations__description']
    ordering = ['sort_order', 'id']


@admin.register(CarRentalLocation)
class CarRentalLocationAdmin(TranslatableAdmin):
    list_display = ['name', 'city', 'country', 'location_type', 'is_active', 'sort_order']
    list_filter = ['location_type', 'city', 'country', 'is_active']
    search_fields = ['translations__name', 'translations__address', 'city', 'country']
    ordering = ['sort_order', 'id']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'address', 'city', 'country')
        }),
        (_('Location Details'), {
            'fields': ('location_type', 'latitude', 'longitude')
        }),
        (_('Settings'), {
            'fields': ('is_active', 'sort_order')
        }),
        (_('Operating Hours'), {
            'fields': ('operating_hours_start', 'operating_hours_end'),
            'classes': ('collapse',)
        }),
    )


class CarRentalImageInline(admin.TabularInline):
    model = CarRentalImage
    extra = 1
    fields = ['image', 'caption', 'sort_order', 'is_primary']


@admin.register(CarRental)
class CarRentalAdmin(TranslatableAdmin):
    list_display = [
        'title', 'brand', 'model', 'year', 'seats', 
        'price_per_day', 'price_per_hour', 'allow_hourly_rental', 
        'is_available', 'agent', 'created_at'
    ]
    list_filter = [
        'brand', 'fuel_type', 'transmission', 'allow_hourly_rental', 
        'is_available', 'is_featured', 'is_popular', 'agent', 'created_at'
    ]
    search_fields = [
        'translations__title', 'brand', 'model', 'agent__username'
    ]
    inlines = [CarRentalImageInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'description', 'short_description', 'category', 'agent')
        }),
        (_('Vehicle Details'), {
            'fields': ('brand', 'model', 'year', 'seats', 'fuel_type', 'transmission')
        }),
        (_('Rental Settings'), {
            'fields': (
                'min_rent_days', 'max_rent_days', 'allow_hourly_rental', 
                'min_rent_hours', 'max_hourly_rental_hours', 'mileage_limit_per_day', 
                'deposit_amount', 'advance_booking_days'
            )
        }),
        (_('Pricing'), {
            'fields': (
                'price_per_day', 'price_per_hour', 'weekly_discount_percentage', 
                'monthly_discount_percentage', 'currency'
            )
        }),
        (_('Location'), {
            'fields': (
                'city', 'country', 'pickup_location', 'dropoff_location',
                'pickup_instructions', 'dropoff_instructions'
            )
        }),
        (_('Default Locations'), {
            'fields': (
                'default_pickup_locations', 'default_dropoff_locations',
                'allow_custom_pickup_location', 'allow_custom_dropoff_location'
            ),
            'classes': ('collapse',)
        }),
        (_('Insurance'), {
            'fields': ('basic_insurance_included', 'comprehensive_insurance_price')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_available', 'is_featured', 'is_popular', 'is_special', 'is_seasonal')
        }),
    )


@admin.register(CarRentalOption)
class CarRentalOptionAdmin(TranslatableAdmin):
    list_display = ['name', 'option_type', 'price_type', 'price', 'is_active']
    list_filter = ['option_type', 'price_type', 'is_active']
    search_fields = ['translations__name', 'translations__description']


@admin.register(CarRentalAvailability)
class CarRentalAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['car_rental', 'start_date', 'end_date', 'is_available', 'available_quantity']
    list_filter = ['is_available', 'start_date', 'end_date']
    search_fields = ['car_rental__brand', 'car_rental__model']
    date_hierarchy = 'start_date'


@admin.register(CarRentalBooking)
class CarRentalBookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_reference', 'car_rental', 'driver_name', 
        'pickup_date', 'dropoff_date', 'status', 'total_price'
    ]
    list_filter = ['status', 'pickup_date', 'created_at']
    search_fields = ['booking_reference', 'driver_name', 'driver_email', 'car_rental__brand']
    date_hierarchy = 'pickup_date'
    
    fieldsets = (
        (_('Booking Information'), {
            'fields': ('booking_reference', 'car_rental', 'user', 'status')
        }),
        (_('Rental Period'), {
            'fields': ('pickup_date', 'dropoff_date', 'pickup_time', 'dropoff_time', 'total_days', 'total_hours')
        }),
        (_('Pickup Location'), {
            'fields': (
                'pickup_location_type', 'pickup_location_id', 'pickup_location_custom', 
                'pickup_location_coordinates'
            )
        }),
        (_('Dropoff Location'), {
            'fields': (
                'dropoff_location_type', 'dropoff_location_id', 'dropoff_location_custom', 
                'dropoff_location_coordinates'
            )
        }),
        (_('Pricing'), {
            'fields': ('daily_rate', 'hourly_rate', 'base_price', 'options_total', 'insurance_total', 'total_price', 'currency')
        }),
        (_('Driver Information'), {
            'fields': ('driver_name', 'driver_license', 'driver_phone', 'driver_email', 'additional_drivers')
        }),
        (_('Options & Insurance'), {
            'fields': ('selected_options', 'basic_insurance', 'comprehensive_insurance', 'special_requirements')
        }),
        (_('Deposit'), {
            'fields': ('deposit_amount',)
        }),
    )
