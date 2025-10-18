"""
Django Admin configuration for Orders app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import Order, OrderItem, OrderHistory


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem."""
    
    model = OrderItem
    extra = 0
    readonly_fields = [
        'product_type', 'product_title', 'variant_name', 'quantity',
        'unit_price', 'total_price', 'status'
    ]
    fields = [
        'product_type', 'product_title', 'variant_name', 'quantity',
        'unit_price', 'total_price', 'status'
    ]
    
    def has_add_permission(self, request, obj=None):
        return False


class OrderHistoryInline(admin.TabularInline):
    """Inline admin for OrderHistory."""
    
    model = OrderHistory
    extra = 0
    readonly_fields = [
        'user', 'field_name', 'old_value', 'new_value', 'change_reason', 'created_at'
    ]
    fields = ['field_name', 'old_value', 'new_value', 'change_reason', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model."""
    
    list_display = [
        'order_number', 'user', 'status', 'payment_status', 'total_items',
        'total_amount', 'currency', 'agent', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'currency', 'commission_paid', 'created_at'
    ]
    search_fields = [
        'order_number', 'user__username', 'user__email', 'customer_name',
        'customer_email', 'customer_phone'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'order_number', 'created_at', 'updated_at'
    ]
    
    # Add bulk actions
    actions = ['bulk_confirm_orders', 'bulk_cancel_orders', 'bulk_mark_paid']
    
    inlines = [OrderItemInline]  # Only OrderItemInline for now
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('order_number', 'user', 'agent')
        }),
        (_('Order Status'), {
            'fields': ('status', 'payment_status', 'payment_method')
        }),
        (_('Pricing'), {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'currency')
        }),
        (_('Agent Commission'), {
            'fields': ('agent_commission_rate', 'agent_commission_amount', 'commission_paid'),
            'classes': ('collapse',)
        }),
        (_('Customer Information'), {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        (_('Billing Information'), {
            'fields': ('billing_address', 'billing_city', 'billing_country'),
            'classes': ('collapse',)
        }),
        (_('System Limits'), {
            'fields': (),
            'description': _('Order limits are managed in System Settings. Current limits: Max pending orders per user: 3, Max pending orders per product: 1')
        }),
        (_('Notes'), {
            'fields': ('customer_notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_items(self, obj):
        """Get total number of items in order."""
        return obj.total_items
    total_items.short_description = _('Total Items')
    
    def total_amount(self, obj):
        """Get total amount."""
        return f"${obj.total_amount:.2f}"
    total_amount.short_description = _('Total Amount')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('user', 'agent').prefetch_related('items', 'history')
    
    def save_model(self, request, obj, form, change):
        """Override save to track changes."""
        if change:
            # Track changes for existing orders
            old_obj = Order.objects.get(pk=obj.pk)
            for field in form.changed_data:
                if field not in ['updated_at']:  # Skip automatic fields
                    old_value = getattr(old_obj, field)
                    new_value = getattr(obj, field)
                    if old_value != new_value:
                        OrderHistory.objects.create(
                            order=obj,
                            user=request.user,
                            field_name=field,
                            old_value=str(old_value) if old_value is not None else '',
                            new_value=str(new_value) if new_value is not None else '',
                            change_reason=f"Changed by {request.user.username}"
                        )
        
        super().save_model(request, obj, form, change)
    
    def bulk_confirm_orders(self, request, queryset):
        """Bulk confirm selected orders."""
        from .models import OrderService
        
        confirmed_count = 0
        failed_count = 0
        
        for order in queryset:
            if order.status == 'pending':
                try:
                    success, message = order.confirm_order()
                    if success:
                        confirmed_count += 1
                        # Log the change
                        OrderHistory.objects.create(
                            order=order,
                            user=request.user,
                            field_name='status',
                            old_value='pending',
                            new_value='confirmed',
                            change_reason=f"Bulk confirmed by {request.user.username}"
                        )
                    else:
                        failed_count += 1
                        self.message_user(request, f"Failed to confirm order {order.order_number}: {message}", level='ERROR')
                except Exception as e:
                    failed_count += 1
                    self.message_user(request, f"Error confirming order {order.order_number}: {str(e)}", level='ERROR')
            else:
                failed_count += 1
                self.message_user(request, f"Order {order.order_number} is not pending", level='WARNING')
        
        if confirmed_count > 0:
            self.message_user(request, f"Successfully confirmed {confirmed_count} orders.", level='SUCCESS')
        if failed_count > 0:
            self.message_user(request, f"Failed to confirm {failed_count} orders.", level='WARNING')
    
    bulk_confirm_orders.short_description = _("Confirm selected orders")
    
    def bulk_cancel_orders(self, request, queryset):
        """Bulk cancel selected orders."""
        cancelled_count = 0
        failed_count = 0
        
        for order in queryset:
            if order.status in ['pending', 'confirmed']:
                try:
                    success = order.cancel_order(f"Bulk cancelled by {request.user.username}")
                    if success:
                        cancelled_count += 1
                        # Log the change
                        OrderHistory.objects.create(
                            order=order,
                            user=request.user,
                            field_name='status',
                            old_value=order.status,
                            new_value='cancelled',
                            change_reason=f"Bulk cancelled by {request.user.username}"
                        )
                    else:
                        failed_count += 1
                        self.message_user(request, f"Failed to cancel order {order.order_number}", level='ERROR')
                except Exception as e:
                    failed_count += 1
                    self.message_user(request, f"Error cancelling order {order.order_number}: {str(e)}", level='ERROR')
            else:
                failed_count += 1
                self.message_user(request, f"Order {order.order_number} cannot be cancelled", level='WARNING')
        
        if cancelled_count > 0:
            self.message_user(request, f"Successfully cancelled {cancelled_count} orders.", level='SUCCESS')
        if failed_count > 0:
            self.message_user(request, f"Failed to cancel {failed_count} orders.", level='WARNING')
    
    bulk_cancel_orders.short_description = _("Cancel selected orders")
    
    def bulk_mark_paid(self, request, queryset):
        """Bulk mark selected orders as paid."""
        paid_count = 0
        failed_count = 0
        
        for order in queryset:
            if order.status in ['pending', 'confirmed']:
                try:
                    old_status = order.status
                    order.status = 'paid'
                    order.payment_status = 'paid'
                    order.save()
                    
                    paid_count += 1
                    # Log the change
                    OrderHistory.objects.create(
                        order=order,
                        user=request.user,
                        field_name='status',
                        old_value=old_status,
                        new_value='paid',
                        change_reason=f"Bulk marked as paid by {request.user.username}"
                    )
                except Exception as e:
                    failed_count += 1
                    self.message_user(request, f"Error marking order {order.order_number} as paid: {str(e)}", level='ERROR')
            else:
                failed_count += 1
                self.message_user(request, f"Order {order.order_number} cannot be marked as paid", level='WARNING')
        
        if paid_count > 0:
            self.message_user(request, f"Successfully marked {paid_count} orders as paid.", level='SUCCESS')
        if failed_count > 0:
            self.message_user(request, f"Failed to mark {failed_count} orders as paid.", level='WARNING')
    
    bulk_mark_paid.short_description = _("Mark selected orders as paid")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for OrderItem model."""
    
    list_display = [
        'order', 'product_type', 'product_title', 'variant_name', 'quantity',
        'unit_price', 'total_price', 'currency', 'status', 'created_at'
    ]
    list_filter = [
        'product_type', 'currency', 'status', 'booking_date', 'created_at'
    ]
    search_fields = [
        'order__order_number', 'product_title', 'variant_name', 'booking_data'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'order', 'product_type', 'product_id', 'product_title', 'product_slug',
        'booking_date', 'booking_time', 'variant_id', 'variant_name',
        'quantity', 'unit_price', 'total_price', 'currency',
        'selected_options', 'options_total', 'booking_data', 'status',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('order',)
        }),
        (_('Product Information'), {
            'fields': ('product_type', 'product_id', 'product_title', 'product_slug')
        }),
        (_('Booking Details'), {
            'fields': ('booking_date', 'booking_time', 'variant_id', 'variant_name')
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
        (_('Additional Data'), {
            'fields': ('booking_data',)
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('order')


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    """Admin for OrderHistory model."""
    
    list_display = [
        'order', 'user', 'field_name', 'old_value', 'new_value', 'created_at'
    ]
    list_filter = [
        'field_name', 'created_at'
    ]
    search_fields = [
        'order__order_number', 'user__username', 'field_name', 'change_reason'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'order', 'user', 'field_name', 'old_value', 'new_value', 
        'change_reason', 'created_at'
    ]
    
    fieldsets = (
        (_('History Information'), {
            'fields': ('order', 'user', 'field_name')
        }),
        (_('Change Details'), {
            'fields': ('old_value', 'new_value', 'change_reason')
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('order', 'user') 