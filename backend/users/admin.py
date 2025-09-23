"""
Django Admin configuration for Users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import User, UserActivity, OTPCode


class UserActivityInline(admin.TabularInline):
    """Inline admin for UserActivity."""
    
    model = UserActivity
    extra = 0
    readonly_fields = ['activity_type', 'description', 'ip_address', 'user_agent', 'created_at']
    fields = ['activity_type', 'description', 'ip_address', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


class OTPCodeInline(admin.TabularInline):
    """Inline admin for OTPCode."""
    
    model = OTPCode
    extra = 0
    readonly_fields = ['code', 'otp_type', 'is_used', 'expires_at', 'created_at']
    fields = ['code', 'otp_type', 'is_used', 'expires_at']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for User model."""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'role', 
        'is_active', 'is_verified', 'created_at', 'last_login'
    ]
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser', 
        'is_phone_verified', 'is_email_verified', 'preferred_language',
        'preferred_currency', 'created_at', 'last_login'
    ]
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 
        'phone_number', 'agent_code'
    ]
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    inlines = [UserActivityInline, OTPCodeInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('id', 'username', 'email', 'password')
        }),
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'nationality')
        }),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Agent Information'), {
            'fields': ('agent_code', 'commission_rate'),
            'classes': ('collapse',)
        }),
        (_('Preferences'), {
            'fields': ('preferred_language', 'preferred_currency')
        }),
        (_('Verification'), {
            'fields': ('is_phone_verified', 'is_email_verified')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    def is_verified(self, obj):
        """Check if user is verified."""
        return obj.is_phone_verified and obj.is_email_verified
    is_verified.boolean = True
    is_verified.short_description = _('Verified')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related()
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for existing users."""
        if obj:  # Editing existing user
            return self.readonly_fields + ('id',)
        return self.readonly_fields


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin for UserActivity model."""
    
    list_display = [
        'user', 'activity_type', 'description', 'ip_address', 
        'created_at'
    ]
    list_filter = [
        'activity_type', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'description', 'ip_address'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'user', 'activity_type', 'description', 'ip_address', 
        'user_agent', 'created_at'
    ]
    
    fieldsets = (
        (_('Activity Information'), {
            'fields': ('user', 'activity_type', 'description')
        }),
        (_('Technical Details'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
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
        return super().get_queryset(request).select_related('user')


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """Admin for OTPCode model."""
    
    list_display = [
        'user', 'code', 'otp_type', 'is_used', 'is_expired', 
        'created_at', 'expires_at'
    ]
    list_filter = [
        'otp_type', 'is_used', 'created_at', 'expires_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'code'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'user', 'code', 'otp_type', 'is_used', 'expires_at', 'created_at'
    ]
    
    fieldsets = (
        (_('OTP Information'), {
            'fields': ('user', 'code', 'otp_type', 'is_used')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        """Check if OTP is expired."""
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = _('Expired')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('user')


# Customize admin site
admin.site.site_header = _('Peykan Tourism Admin')
admin.site.site_title = _('Peykan Tourism')
admin.site.index_title = _('User Management') 