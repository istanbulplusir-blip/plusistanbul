"""
Django Admin configuration for Cart app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline admin for CartItem."""
    
    model = CartItem
    extra = 0
    readonly_fields = [
        'product_type', 'product_id', 'booking_date', 'booking_time',
        'variant_name', 'quantity', 'unit_price', 'total_price', 'currency',
        'is_reserved', 'reservation_expires_at'
    ]
    fields = [
        'product_type', 'variant_name', 'quantity', 'unit_price', 
        'total_price', 'is_reserved', 'reservation_expires_at'
    ]
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart model."""
    
    list_display = [
        'session_id', 'user', 'currency', 'total_items', 'subtotal', 
        'is_active', 'is_expired', 'created_at'
    ]
    list_filter = [
        'currency', 'is_active', 'created_at', 'expires_at'
    ]
    search_fields = [
        'session_id', 'user__username', 'user__email'
    ]
    ordering = ['-created_at']
    readonly_fields = ['id', 'session_id', 'created_at', 'updated_at']
    
    inlines = [CartItemInline]
    
    fieldsets = (
        (_('Cart Information'), {
            'fields': ('id', 'session_id', 'user')
        }),
        (_('Details'), {
            'fields': ('currency', 'is_active', 'expires_at')
        }),
        (_('System Limits'), {
            'fields': (),
            'description': _('Cart limits are managed in System Settings. Current limits: Guest max items: 5, Guest max total: $1000, Rate limit: 30/min')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_items(self, obj):
        """Get total number of items in cart."""
        return obj.total_items
    total_items.short_description = _('Total Items')
    
    def subtotal(self, obj):
        """Get cart subtotal."""
        return f"${obj.subtotal:.2f}"
    subtotal.short_description = _('Subtotal')
    
    def is_expired(self, obj):
        """Check if cart has expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = _('Expired')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('user').prefetch_related('items')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for CartItem model."""
    
    list_display = [
        'cart', 'product_type', 'variant_name', 'quantity', 'unit_price',
        'total_price', 'currency', 'is_reserved', 'is_reservation_expired', 'created_at'
    ]
    list_filter = [
        'product_type', 'currency', 'is_reserved', 'booking_date', 'created_at'
    ]
    search_fields = [
        'cart__session_id', 'cart__user__username', 'cart__user__email',
        'variant_name', 'booking_data'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'cart', 'product_type', 'product_id', 'booking_date', 'booking_time',
        'variant_id', 'variant_name', 'quantity', 'unit_price', 'total_price',
        'currency', 'selected_options', 'options_total', 'booking_data',
        'is_reserved', 'reservation_expires_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Cart Information'), {
            'fields': ('cart',)
        }),
        (_('Product Information'), {
            'fields': ('product_type', 'product_id', 'variant_id', 'variant_name')
        }),
        (_('Booking Details'), {
            'fields': ('booking_date', 'booking_time', 'booking_data')
        }),
        (_('Car Rental Details'), {
            'fields': (
                'pickup_date', 'dropoff_date', 'pickup_time', 'dropoff_time',
                'pickup_location_type', 'pickup_location_id', 'pickup_location_custom',
                'dropoff_location_type', 'dropoff_location_id', 'dropoff_location_custom'
            ),
            'classes': ('collapse',)
        }),
        (_('Pricing'), {
            'fields': ('quantity', 'unit_price', 'total_price', 'currency')
        }),
        (_('Options'), {
            'fields': ('selected_options', 'options_total')
        }),
        (_('Reservation'), {
            'fields': ('is_reserved', 'reservation_expires_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_reservation_expired(self, obj):
        """Check if reservation has expired."""
        return obj.is_reservation_expired()
    is_reservation_expired.boolean = True
    is_reservation_expired.short_description = _('Reservation Expired')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('cart__user') 