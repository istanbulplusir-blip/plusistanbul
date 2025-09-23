"""
Django Admin configuration for Core app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin for SystemSettings model."""
    
    list_display = [
        'id', 'cart_max_items_guest', 'cart_max_total_guest', 
        'order_max_pending_per_user', 'capacity_check_enabled'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Cart Limits'), {
            'fields': (
                'cart_max_items_guest', 'cart_max_total_guest', 
                'cart_max_carts_guest', 'cart_rate_limit_guest', 
                'cart_rate_limit_user'
            ),
            'description': _('Configure limits for guest and authenticated user carts.')
        }),
        (_('Order Limits'), {
            'fields': (
                'order_max_pending_per_user', 'order_max_pending_per_product'
            ),
            'description': _('Configure limits for pending orders.')
        }),
        (_('Capacity Management'), {
            'fields': (
                'capacity_check_enabled', 'capacity_reservation_duration'
            ),
            'description': _('Configure capacity checking and reservation settings.')
        }),
        (_('Guest User Limits'), {
            'fields': (
                'guest_infant_max', 'guest_booking_timeout'
            ),
            'description': _('Configure specific limits for guest users.')
        }),
        (_('System Information'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': _('System information and timestamps.')
        }),
    )
    
    def has_add_permission(self, request):
        """Only allow one system settings instance."""
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of system settings."""
        return False
    
    actions = ['reset_to_defaults']
    
    def reset_to_defaults(self, request, queryset):
        """Reset settings to default values."""
        for settings in queryset:
            settings.cart_max_items_guest = 3
            settings.cart_max_total_guest = 500.00
            settings.cart_max_carts_guest = 20
            settings.cart_rate_limit_guest = 30
            settings.cart_rate_limit_user = 20
            settings.order_max_pending_per_user = 3
            settings.order_max_pending_per_product = 1
            settings.capacity_check_enabled = True
            settings.capacity_reservation_duration = 30
            settings.guest_infant_max = 2
            settings.guest_booking_timeout = 15
            settings.save()
        
        self.message_user(
            request, 
            f"Reset {queryset.count()} system settings to default values."
        )
    reset_to_defaults.short_description = _('Reset to default values')



