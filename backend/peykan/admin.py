"""
Django Admin configuration for Peykan Tourism Platform.
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType


class PeykanAdminSite(AdminSite):
    """Custom admin site for Peykan Tourism Platform."""
    
    site_header = _('Peykan Tourism Administration')
    site_title = _('Peykan Tourism')
    index_title = _('Welcome to Peykan Tourism Admin')
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)
        
        # Customize app ordering
        app_ordering = {
            'users': 1,
            'tours': 2,
            'events': 3,
            'transfers': 4,
            'cart': 5,
            'orders': 6,
            'payments': 7,
            'agents': 8,
        }
        
        # Sort apps by custom ordering
        app_list.sort(key=lambda x: app_ordering.get(x['app_label'], 999))
        
        return app_list


# Create custom admin site instance
admin_site = PeykanAdminSite(name='peykan_admin')


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Admin for LogEntry model to track admin actions."""
    
    list_display = [
        'action_time', 'user', 'content_type', 'object_repr', 'action_flag',
        'change_message'
    ]
    list_filter = [
        'action_flag', 'action_time', 'content_type'
    ]
    search_fields = [
        'user__username', 'object_repr', 'change_message'
    ]
    ordering = ['-action_time']
    readonly_fields = [
        'action_time', 'user', 'content_type', 'object_id', 'object_repr',
        'action_flag', 'change_message'
    ]
    
    fieldsets = (
        (_('Action Information'), {
            'fields': ('action_time', 'user', 'action_flag')
        }),
        (_('Object Information'), {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        (_('Change Details'), {
            'fields': ('change_message',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def action_flag_display(self, obj):
        """Display action flag as human readable text."""
        flags = {
            ADDITION: _('Addition'),
            CHANGE: _('Change'),
            DELETION: _('Deletion'),
        }
        return flags.get(obj.action_flag, obj.action_flag)
    action_flag_display.short_description = _('Action')


# Custom admin actions
@admin.action(description=_('Mark selected items as active'))
def make_active(modeladmin, request, queryset):
    """Mark selected items as active."""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        _('Successfully marked %(count)d items as active.') % {'count': updated}
    )


@admin.action(description=_('Mark selected items as inactive'))
def make_inactive(modeladmin, request, queryset):
    """Mark selected items as inactive."""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        _('Successfully marked %(count)d items as inactive.') % {'count': updated}
    )


@admin.action(description=_('Mark selected items as featured'))
def make_featured(modeladmin, request, queryset):
    """Mark selected items as featured."""
    updated = queryset.update(is_featured=True)
    modeladmin.message_user(
        request,
        _('Successfully marked %(count)d items as featured.') % {'count': updated}
    )


@admin.action(description=_('Mark selected items as popular'))
def make_popular(modeladmin, request, queryset):
    """Mark selected items as popular."""
    updated = queryset.update(is_popular=True)
    modeladmin.message_user(
        request,
        _('Successfully marked %(count)d items as popular.') % {'count': updated}
    )


# Custom admin filters
class IsActiveFilter(admin.SimpleListFilter):
    """Filter for active/inactive items."""
    
    title = _('Status')
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('1', _('Active')),
            ('0', _('Inactive')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_active=True)
        if self.value() == '0':
            return queryset.filter(is_active=False)


class DateRangeFilter(admin.SimpleListFilter):
    """Filter for date ranges."""
    
    title = _('Date Range')
    parameter_name = 'date_range'
    
    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('yesterday', _('Yesterday')),
            ('this_week', _('This Week')),
            ('this_month', _('This Month')),
            ('this_year', _('This Year')),
        )
    
    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        if self.value() == 'yesterday':
            yesterday = now.date() - timedelta(days=1)
            return queryset.filter(created_at__date=yesterday)
        if self.value() == 'this_week':
            start_of_week = now.date() - timedelta(days=now.weekday())
            return queryset.filter(created_at__date__gte=start_of_week)
        if self.value() == 'this_month':
            return queryset.filter(created_at__month=now.month, created_at__year=now.year)
        if self.value() == 'this_year':
            return queryset.filter(created_at__year=now.year)


# Admin site customization
admin.site.site_header = _('Peykan Tourism Administration')
admin.site.site_title = _('Peykan Tourism')
admin.site.index_title = _('Welcome to Peykan Tourism Admin')

# Add custom CSS and JS
class Media:
    css = {
        'all': ('admin/css/custom_admin.css',)
    }
    js = ('admin/js/custom_admin.js',)


# Register admin actions globally
admin.site.add_action(make_active)
admin.site.add_action(make_inactive)
admin.site.add_action(make_featured)
admin.site.add_action(make_popular) 