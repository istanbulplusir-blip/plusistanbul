"""
Enhanced Django Admin configuration for Agents app with comprehensive management capabilities.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import AgentProfile, AgentCustomer, AgentCommission, AgentPricingRule


# =============================================================================
# INLINE ADMIN CLASSES
# =============================================================================

class AgentCustomerInline(admin.TabularInline):
    """Inline admin for AgentCustomer."""
    model = AgentCustomer
    extra = 0
    readonly_fields = ['id', 'created_at']
    fields = [
        'customer', 'customer_name', 'customer_email', 'customer_phone',
        'customer_status', 'customer_tier', 'total_orders', 'total_spent',
        'is_active', 'created_at'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')


class AgentCommissionInline(admin.TabularInline):
    """Inline admin for AgentCommission."""
    model = AgentCommission
    extra = 0
    readonly_fields = ['id', 'created_at', 'commission_amount']
    fields = [
        'order', 'commission_rate', 'order_amount', 'commission_amount',
        'status', 'created_at'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')


class AgentPricingRuleInline(admin.TabularInline):
    """Inline admin for AgentPricingRule."""
    model = AgentPricingRule
    extra = 0
    fields = [
        'product_type', 'pricing_method', 'discount_percentage',
        'fixed_price', 'markup_percentage', 'custom_factor',
        'is_active', 'priority'
    ]


# =============================================================================
# MAIN ADMIN CLASSES
# =============================================================================

@admin.register(AgentProfile)
class EnhancedAgentAdmin(admin.ModelAdmin):
    """Enhanced admin for AgentProfile with comprehensive management."""
    
    list_display = [
        'user', 'company_name', 'license_number', 'commission_rate',
        'is_verified', 'total_customers', 'total_orders', 'total_revenue',
        'total_commission_earned', 'performance_score', 'created_at'
    ]
    list_filter = [
        'is_verified', 'is_active', 'commission_rate', 'created_at',
        ('user__date_joined', admin.DateFieldListFilter),
    ]
    search_fields = [
        'user__username', 'user__email', 'company_name', 'license_number',
        'business_email', 'business_phone'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'total_customers', 'total_orders',
        'total_revenue', 'total_commission_earned', 'performance_score'
    ]
    
    # Add bulk actions
    actions = ['bulk_verify_agents', 'bulk_activate_agents', 'bulk_deactivate_agents']
    
    # Add inlines (removed due to ForeignKey constraints)
    # inlines = [AgentCustomerInline, AgentCommissionInline, AgentPricingRuleInline]
    
    fieldsets = (
        (_('Agent Information'), {
            'fields': ('id', 'user', 'company_name', 'license_number')
        }),
        (_('Business Contact'), {
            'fields': ('business_address', 'business_phone', 'business_email', 'website')
        }),
        (_('Commission Settings'), {
            'fields': ('commission_rate', 'min_commission', 'max_commission')
        }),
        (_('Performance Metrics'), {
            'fields': (
                'total_customers', 'total_orders', 'total_revenue',
                'total_commission_earned', 'total_commission_paid', 'average_commission',
                'performance_score'
            ),
            'classes': ('collapse',)
        }),
        (_('Status & Verification'), {
            'fields': ('is_active', 'is_verified')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_customers(self, obj):
        """Get total number of customers for this agent."""
        count = obj.user.agent_customers.count()
        if count > 0:
            url = reverse('admin:agents_agentcustomer_changelist') + f'?agent__id__exact={obj.user.id}'
            return format_html('<a href="{}">{} customers</a>', url, count)
        return '0 customers'
    total_customers.short_description = _('Total Customers')
    
    def total_orders(self, obj):
        """Get total number of orders for this agent."""
        count = obj.user.agent_orders.count()
        if count > 0:
            url = reverse('admin:orders_order_changelist') + f'?agent__id__exact={obj.user.id}'
            return format_html('<a href="{}">{} orders</a>', url, count)
        return '0 orders'
    total_orders.short_description = _('Total Orders')
    
    def total_revenue(self, obj):
        """Get total revenue for this agent."""
        total = obj.user.agent_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        return f"${total:.2f}"
    total_revenue.short_description = _('Total Revenue')
    
    def total_commission_earned(self, obj):
        """Get total commission earned."""
        return f"${obj.total_commission_earned:.2f}"
    total_commission_earned.short_description = _('Commission Earned')
    
    def performance_score(self, obj):
        """Calculate performance score based on various metrics."""
        # Simple performance calculation
        score = 0
        
        # Commission rate bonus
        if obj.commission_rate >= 15:
            score += 20
        elif obj.commission_rate >= 10:
            score += 15
        elif obj.commission_rate >= 5:
            score += 10
        
        # Verification bonus
        if obj.is_verified:
            score += 30
        
        # Activity bonus
        if obj.total_orders > 50:
            score += 25
        elif obj.total_orders > 20:
            score += 15
        elif obj.total_orders > 5:
            score += 10
        
        # Customer count bonus
        customer_count = obj.user.agent_customers.count()
        if customer_count > 100:
            score += 25
        elif customer_count > 50:
            score += 15
        elif customer_count > 10:
            score += 10
        
        # Color coding
        if score >= 80:
            color = 'green'
        elif score >= 60:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/100</span>',
            color, score
        )
    performance_score.short_description = _('Performance Score')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('user').prefetch_related(
            'user__agent_customers', 'user__agent_orders'
        )
    
    # Bulk actions
    def bulk_verify_agents(self, request, queryset):
        """Bulk verify agents."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} agents verified successfully.')
    bulk_verify_agents.short_description = _('Verify selected agents')
    
    def bulk_activate_agents(self, request, queryset):
        """Bulk activate agents."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} agents activated successfully.')
    bulk_activate_agents.short_description = _('Activate selected agents')
    
    def bulk_deactivate_agents(self, request, queryset):
        """Bulk deactivate agents."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} agents deactivated successfully.')
    bulk_deactivate_agents.short_description = _('Deactivate selected agents')


@admin.register(AgentCustomer)
class AgentCustomerAdmin(admin.ModelAdmin):
    """Admin for AgentCustomer with detailed customer management."""
    
    list_display = [
        'customer_name', 'customer_email', 'agent', 'customer_status',
        'customer_tier', 'total_orders', 'total_spent', 'last_order_date',
        'is_active', 'created_at'
    ]
    list_filter = [
        'customer_status', 'customer_tier', 'is_active', 'created_by_agent',
        'preferred_language', 'preferred_contact_method', 'created_at',
        'agent',
    ]
    search_fields = [
        'customer_name', 'customer_email', 'customer_phone',
        'agent__username', 'agent__email'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'total_orders', 'total_spent',
        'last_order_date', 'login_count'
    ]
    
    # Add bulk actions
    actions = ['bulk_activate_customers', 'bulk_deactivate_customers', 'bulk_upgrade_tier']
    
    fieldsets = (
        (_('Customer Information'), {
            'fields': (
                'id', 'agent', 'customer', 'customer_name', 'customer_email', 'customer_phone'
            )
        }),
        (_('Customer Details'), {
            'fields': (
                'customer_address', 'customer_city', 'customer_country',
                'customer_birth_date', 'customer_gender'
            )
        }),
        (_('Preferences'), {
            'fields': (
                'preferred_language', 'preferred_contact_method',
                'customer_status', 'customer_tier'
            )
        }),
        (_('Relationship & Notes'), {
            'fields': (
                'relationship_notes', 'special_requirements', 'marketing_consent'
            )
        }),
        (_('Statistics'), {
            'fields': (
                'total_orders', 'total_spent', 'last_order_date'
            ),
            'classes': ('collapse',)
        }),
        (_('Authentication'), {
            'fields': (
                'requires_verification', 'credentials_sent', 'credentials_sent_at',
                'last_login_at', 'login_count'
            ),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_by_agent')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_orders(self, obj):
        """Get total number of orders for this customer."""
        count = obj.customer.orders.count()
        if count > 0:
            url = reverse('admin:orders_order_changelist') + f'?user__id__exact={obj.customer.id}'
            return format_html('<a href="{}">{} orders</a>', url, count)
        return '0 orders'
    total_orders.short_description = _('Total Orders')
    
    def total_spent(self, obj):
        """Get total amount spent by customer."""
        return f"${obj.total_spent:.2f}"
    total_spent.short_description = _('Total Spent')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('agent', 'customer')
    
    # Bulk actions
    def bulk_activate_customers(self, request, queryset):
        """Bulk activate customers."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} customers activated successfully.')
    bulk_activate_customers.short_description = _('Activate selected customers')
    
    def bulk_deactivate_customers(self, request, queryset):
        """Bulk deactivate customers."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} customers deactivated successfully.')
    bulk_deactivate_customers.short_description = _('Deactivate selected customers')
    
    def bulk_upgrade_tier(self, request, queryset):
        """Bulk upgrade customer tier."""
        updated = queryset.update(customer_tier='gold')
        self.message_user(request, f'{updated} customers upgraded to gold tier.')
    bulk_upgrade_tier.short_description = _('Upgrade to gold tier')


@admin.register(AgentCommission)
class AgentCommissionAdmin(admin.ModelAdmin):
    """Admin for AgentCommission with comprehensive commission tracking."""
    
    list_display = [
        'agent', 'order', 'commission_rate', 'order_amount', 'commission_amount',
        'status', 'approved_by', 'paid_at', 'created_at'
    ]
    list_filter = [
        'status', 'currency', 'created_at', 'approved_at', 'paid_at',
        'agent',
    ]
    search_fields = [
        'agent__username', 'order__order_number', 'payment_reference'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'commission_amount'
    ]
    
    # Add bulk actions
    actions = ['bulk_approve_commissions', 'bulk_reject_commissions', 'bulk_mark_paid']
    
    fieldsets = (
        (_('Commission Information'), {
            'fields': ('id', 'agent', 'order', 'commission_rate', 'order_amount', 'commission_amount', 'currency')
        }),
        (_('Status & Approval'), {
            'fields': (
                'status', 'approved_at', 'approved_by', 'rejected_at', 'rejected_by', 'rejection_reason'
            )
        }),
        (_('Payment Details'), {
            'fields': (
                'paid_at', 'paid_by', 'payment_method', 'payment_reference'
            )
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related(
            'agent', 'order', 'approved_by', 'rejected_by', 'paid_by'
        )
    
    # Bulk actions
    def bulk_approve_commissions(self, request, queryset):
        """Bulk approve commissions."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_at=timezone.now(),
            approved_by=request.user
        )
        self.message_user(request, f'{updated} commissions approved successfully.')
    bulk_approve_commissions.short_description = _('Approve selected commissions')
    
    def bulk_reject_commissions(self, request, queryset):
        """Bulk reject commissions."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='rejected',
            rejected_at=timezone.now(),
            rejected_by=request.user,
            rejection_reason='Bulk rejection by admin'
        )
        self.message_user(request, f'{updated} commissions rejected successfully.')
    bulk_reject_commissions.short_description = _('Reject selected commissions')
    
    def bulk_mark_paid(self, request, queryset):
        """Bulk mark commissions as paid."""
        from django.utils import timezone
        updated = queryset.filter(status='approved').update(
            status='paid',
            paid_at=timezone.now(),
            paid_by=request.user,
            payment_method='Bulk payment'
        )
        self.message_user(request, f'{updated} commissions marked as paid.')
    bulk_mark_paid.short_description = _('Mark selected commissions as paid')


@admin.register(AgentPricingRule)
class AgentPricingRuleAdmin(admin.ModelAdmin):
    """Admin for AgentPricingRule."""
    
    list_display = [
        'agent', 'product_type', 'pricing_method', 'discount_percentage',
        'fixed_price', 'markup_percentage', 'is_active', 'priority'
    ]
    list_filter = [
        'product_type', 'pricing_method', 'is_active', 'priority',
        'agent',
    ]
    search_fields = [
        'agent__username', 'description'
    ]
    ordering = ['-priority', '-created_at']
    
    fieldsets = (
        (_('Rule Information'), {
            'fields': ('agent', 'product_type', 'pricing_method', 'description')
        }),
        (_('Pricing Values'), {
            'fields': (
                'discount_percentage', 'fixed_price', 'markup_percentage', 'custom_factor'
            )
        }),
        (_('Limits'), {
            'fields': ('min_price', 'max_price')
        }),
        (_('Settings'), {
            'fields': ('is_active', 'priority')
        }),
    )


# =============================================================================
# ADMIN SITE CUSTOMIZATION
# =============================================================================

# Customize admin site
admin.site.site_header = "Peykan Tourism - Agent Management"
admin.site.site_title = "Agent Admin"
admin.site.index_title = "Agent Management Dashboard" 