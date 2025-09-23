"""
Django Admin configuration for Payments app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model."""
    
    list_display = [
        'payment_id', 'order', 'amount', 'currency', 'payment_method',
        'status', 'is_successful', 'created_at'
    ]
    list_filter = [
        'status', 'payment_method', 'currency', 'created_at'
    ]
    search_fields = [
        'payment_id', 'order__order_number', 'customer_name', 'customer_email',
        'gateway_transaction_id'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'payment_id', 'order', 'amount', 'currency', 'payment_method',
        'gateway_transaction_id', 'metadata', 'error_message',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('payment_id', 'order')
        }),
        (_('Payment Details'), {
            'fields': ('amount', 'currency', 'payment_method')
        }),
        (_('Customer Information'), {
            'fields': ('customer_name', 'customer_email')
        }),
        (_('Transaction'), {
            'fields': ('gateway_transaction_id', 'status', 'gateway')
        }),
        (_('Error Information'), {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        (_('Additional Data'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_successful(self, obj):
        """Check if payment was successful."""
        return obj.is_successful
    is_successful.boolean = True
    is_successful.short_description = _('Successful')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('order') 