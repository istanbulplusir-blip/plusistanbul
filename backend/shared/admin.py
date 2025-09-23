"""
Admin configuration for Shared app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from .models import (
    FAQ, FAQCategory, StaticPage, ContactInfo, ContactMessage, SupportFAQ,
    HeroSlider, Banner, SiteSettings, ImageOptimization,
    AboutSection, AboutStatistic, AboutFeature,
    CTASection, CTAButton, CTAFeature,
    Footer, FooterLink,
    TransferBookingSection,
    FAQSettings
)


@admin.register(FAQCategory)
class FAQCategoryAdmin(TranslatableAdmin):
    """
    Admin interface for FAQ Category model.
    """
    
    list_display = ['name', 'icon', 'color_preview', 'order', 'faq_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['translations__name', 'translations__description']
    ordering = ['order', 'created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'order', 'is_active')
        }),
        (_('Category Details'), {
            'fields': ('name', 'description'),
        }),
        (_('Appearance'), {
            'fields': ('icon', 'color'),
        }),
    )
    
    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('name',)}
    
    def color_preview(self, obj):
        """Display color as a preview."""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div> {}',
            obj.color,
            obj.color
        )
    color_preview.short_description = _('Color')
    
    def faq_count(self, obj):
        """Display number of FAQs in this category."""
        return obj.faqs.count()
    faq_count.short_description = _('FAQ Count')
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).prefetch_related('faqs')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for FAQ model.
    """
    
    list_display = ['question', 'category', 'order', 'is_featured', 'is_published', 'view_count', 'created_at']
    list_filter = ['category', 'is_featured', 'is_published', 'is_active', 'created_at']
    list_editable = ['order', 'is_featured', 'is_published']
    search_fields = ['question', 'answer', 'keywords', 'tags']
    ordering = ['category__order', 'order', '-is_featured']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('category', 'order', 'is_active')
        }),
        (_('Question & Answer'), {
            'fields': ('question', 'answer', 'keywords'),
        }),
        (_('Settings'), {
            'fields': ('is_featured', 'is_published', 'tags'),
        }),
        (_('Statistics'), {
            'fields': ('view_count',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['view_count']
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('category')
    
    actions = ['mark_as_featured', 'unmark_as_featured', 'publish', 'unpublish']
    
    def mark_as_featured(self, request, queryset):
        """Mark selected FAQs as featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} FAQs marked as featured.')
    mark_as_featured.short_description = _('Mark selected FAQs as featured')
    
    def unmark_as_featured(self, request, queryset):
        """Unmark selected FAQs as featured."""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} FAQs unmarked as featured.')
    unmark_as_featured.short_description = _('Unmark selected FAQs as featured')
    
    def publish(self, request, queryset):
        """Publish selected FAQs."""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} FAQs published.')
    publish.short_description = _('Publish selected FAQs')
    
    def unpublish(self, request, queryset):
        """Unpublish selected FAQs."""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} FAQs unpublished.')
    unpublish.short_description = _('Unpublish selected FAQs')


@admin.register(StaticPage)
class StaticPageAdmin(TranslatableAdmin):
    """
    Enhanced admin interface for StaticPage model.
    """
    
    list_display = ['page_type', 'title', 'has_image', 'word_count', 'is_active', 'updated_at']
    list_filter = ['page_type', 'is_active', 'created_at', 'updated_at']
    list_editable = ['is_active']
    search_fields = ['translations__title', 'translations__content', 'translations__excerpt', 'page_type']
    ordering = ['page_type']
    readonly_fields = ['id', 'created_at', 'updated_at', 'word_count']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('page_type', 'slug', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'excerpt', 'content'),
        }),
        (_('Media'), {
            'fields': ('image',),
        }),
        (_('SEO'), {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        (_('Statistics'), {
            'fields': ('word_count',),
            'classes': ('collapse',),
        }),
        (_('System Information'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('title',)}
    
    def has_image(self, obj):
        """Display if page has an image."""
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = _('Has Image')
    
    def word_count(self, obj):
        """Display word count of content."""
        try:
            if obj.content:
                return len(obj.content.split())
            return 0
        except:
            return 0
    word_count.short_description = _('Word Count')
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request)
    
    actions = ['publish', 'unpublish']
    
    def publish(self, request, queryset):
        """Publish selected pages."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} pages published.')
    publish.short_description = _('Publish selected pages')
    
    def unpublish(self, request, queryset):
        """Unpublish selected pages."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} pages unpublished.')
    unpublish.short_description = _('Unpublish selected pages')


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for ContactInfo model.
    """
    
    list_display = ['company_name', 'phone_primary', 'email_general', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['company_name', 'address', 'phone_primary', 'email_general']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Company Information'), {
            'fields': ('company_name', 'address', 'is_active')
        }),
        (_('Contact Details'), {
            'fields': ('phone_primary', 'phone_secondary', 'email_general', 'email_support', 'email_sales'),
        }),
        (_('Working Hours'), {
            'fields': ('working_hours', 'working_days'),
        }),
        (_('Location'), {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        (_('Social Media'), {
            'fields': ('instagram_url', 'telegram_url', 'whatsapp_number', 'facebook_url', 'twitter_url', 'linkedin_url'),
            'classes': ('collapse',),
        }),
        (_('System Information'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for ContactMessage model.
    """
    
    list_display = [
        'full_name', 'email', 'subject_truncated', 'status', 'priority', 
        'status_colored', 'priority_colored', 'response_time', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'created_at', 'responded_at', 'responded_by'
    ]
    list_editable = ['status', 'priority']
    search_fields = ['full_name', 'email', 'subject', 'message', 'phone']
    readonly_fields = [
        'id', 'ip_address', 'created_at', 'updated_at', 'responded_at', 
        'response_time', 'message_length'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Sender Information'), {
            'fields': ('full_name', 'email', 'phone', 'ip_address')
        }),
        (_('Message Details'), {
            'fields': ('subject', 'message', 'message_length'),
        }),
        (_('Status & Priority'), {
            'fields': ('status', 'priority'),
        }),
        (_('Admin Response'), {
            'fields': ('admin_response', 'responded_by', 'responded_at', 'response_time'),
        }),
        (_('System Information'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def subject_truncated(self, obj):
        """Display truncated subject."""
        if len(obj.subject) > 50:
            return f"{obj.subject[:50]}..."
        return obj.subject
    subject_truncated.short_description = _('Subject')
    
    def message_length(self, obj):
        """Display message character count."""
        return len(obj.message) if obj.message else 0
    message_length.short_description = _('Message Length')
    
    def response_time(self, obj):
        """Calculate and display response time."""
        if obj.responded_at and obj.created_at:
            delta = obj.responded_at - obj.created_at
            hours = delta.total_seconds() / 3600
            if hours < 24:
                return f"{hours:.1f} hours"
            else:
                days = hours / 24
                return f"{days:.1f} days"
        return "-"
    response_time.short_description = _('Response Time')
    
    def status_colored(self, obj):
        """Display status with color coding."""
        colors = {
            'new': '#dc3545',      # Red
            'read': '#fd7e14',     # Orange  
            'replied': '#28a745',  # Green
            'closed': '#6c757d',   # Gray
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = _('Status')
    
    def priority_colored(self, obj):
        """Display priority with color coding."""
        colors = {
            'low': '#28a745',      # Green
            'medium': '#ffc107',   # Yellow
            'high': '#fd7e14',     # Orange
            'urgent': '#dc3545',   # Red
        }
        color = colors.get(obj.priority, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_colored.short_description = _('Priority')
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('responded_by')
    
    actions = [
        'mark_as_read', 'mark_as_replied', 'mark_as_closed', 
        'set_high_priority', 'set_urgent_priority', 'export_as_csv'
    ]
    
    def mark_as_read(self, request, queryset):
        """Mark selected messages as read."""
        updated = queryset.filter(status='new').update(status='read')
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = _('Mark selected messages as read')
    
    def mark_as_replied(self, request, queryset):
        """Mark selected messages as replied."""
        from django.utils import timezone
        updated = queryset.exclude(status='replied').update(
            status='replied',
            responded_at=timezone.now(),
            responded_by=request.user
        )
        self.message_user(request, f'{updated} messages marked as replied.')
    mark_as_replied.short_description = _('Mark selected messages as replied')
    
    def mark_as_closed(self, request, queryset):
        """Mark selected messages as closed."""
        updated = queryset.exclude(status='closed').update(status='closed')
        self.message_user(request, f'{updated} messages marked as closed.')
    mark_as_closed.short_description = _('Mark selected messages as closed')
    
    def set_high_priority(self, request, queryset):
        """Set selected messages to high priority."""
        updated = queryset.update(priority='high')
        self.message_user(request, f'{updated} messages set to high priority.')
    set_high_priority.short_description = _('Set to high priority')
    
    def set_urgent_priority(self, request, queryset):
        """Set selected messages to urgent priority."""
        updated = queryset.update(priority='urgent')
        self.message_user(request, f'{updated} messages set to urgent priority.')
    set_urgent_priority.short_description = _('Set to urgent priority')
    
    def export_as_csv(self, request, queryset):
        """Export selected messages as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_messages.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Full Name', 'Email', 'Phone', 'Subject', 'Message', 
            'Status', 'Priority', 'Created At', 'Responded At'
        ])
        
        for message in queryset:
            writer.writerow([
                message.full_name,
                message.email,
                message.phone or '',
                message.subject,
                message.message,
                message.get_status_display(),
                message.get_priority_display(),
                message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                message.responded_at.strftime('%Y-%m-%d %H:%M:%S') if message.responded_at else '',
            ])
        
        return response
    export_as_csv.short_description = _('Export selected messages as CSV')


@admin.register(SupportFAQ)
class SupportFAQAdmin(admin.ModelAdmin):
    """
    Admin interface for SupportFAQ model.
    """
    
    list_display = ['question', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['question', 'whatsapp_message']
    ordering = ['category', 'order', 'created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('category', 'order', 'is_active')
        }),
        (_('Question & Message'), {
            'fields': ('question', 'whatsapp_message'),
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request)
    
    actions = ['activate', 'deactivate']
    
    def activate(self, request, queryset):
        """Activate selected support FAQs."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} support FAQs activated.')
    activate.short_description = _('Activate selected support FAQs')
    
    def deactivate(self, request, queryset):
        """Deactivate selected support FAQs."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} support FAQs deactivated.')
    deactivate.short_description = _('Deactivate selected support FAQs')


@admin.register(HeroSlider)
class HeroSliderAdmin(TranslatableAdmin):
    """
    Admin interface for HeroSlider model.
    """

    list_display = [
        'title', 'video_display_name', 'order', 'button_type', 'display_duration', 'is_active',
        'is_active_now', 'view_count', 'click_count', 'click_rate',
        'start_date', 'end_date', 'created_at'
    ]
    list_filter = [
        'is_active', 'button_type', 'video_type', 'show_for_authenticated', 'show_for_anonymous',
        'autoplay_video', 'video_muted', 'show_video_controls', 'video_loop',
        'start_date', 'end_date', 'created_at'
    ]
    list_editable = ['order', 'is_active']
    search_fields = ['translations__title', 'translations__subtitle']
    ordering = ['order', 'created_at']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('order', 'is_active', 'display_duration')
        }),
        (_('Content'), {
            'fields': ('title', 'subtitle', 'description', 'button_text', 'button_url', 'button_type'),
        }),
        (_('Images'), {
            'fields': ('desktop_image', 'tablet_image', 'mobile_image'),
            'description': _('Upload images for different screen sizes. Desktop: 1920x1080, Tablet: 1024x768, Mobile: 768x1024'),
            'classes': ('collapse',)
        }),
        (_('Video Settings'), {
            'fields': ('video_type', 'video_file', 'video_url', 'video_thumbnail'),
            'description': _('Configure video content for this slide. You can either upload a video file or provide an external video URL.')
        }),
        (_('Video Controls'), {
            'fields': ('autoplay_video', 'video_muted', 'show_video_controls', 'video_loop'),
            'description': _('Control video playback behavior. Note: Autoplay works best when video is muted.')
        }),
        (_('Targeting'), {
            'fields': ('show_for_authenticated', 'show_for_anonymous'),
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'end_date'),
            'description': _('Optional date range for displaying this slide')
        }),
        (_('Analytics'), {
            'fields': ('view_count', 'click_count'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['view_count', 'click_count', 'click_rate']

    def click_rate(self, obj):
        """Display click rate in admin."""
        return f"{obj.click_rate:.1f}%" if obj.click_rate > 0 else "0%"
    click_rate.short_description = _('Click Rate')

    def is_active_now(self, obj):
        """Display current active status."""
        return obj.is_active_now()
    is_active_now.boolean = True
    is_active_now.short_description = _('Currently Active')

    def video_display_name(self, obj):
        """Display video type in admin list."""
        return obj.video_display_name
    video_display_name.short_description = _('Video Type')

    def has_video_indicator(self, obj):
        """Show if slide has video content."""
        return obj.has_video()
    has_video_indicator.boolean = True
    has_video_indicator.short_description = _('Has Video')

    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).prefetch_related('translations')


@admin.register(Banner)
class BannerAdmin(TranslatableAdmin):
    """
    Admin interface for Banner model.
    """

    list_display = [
        'title', 'banner_type', 'position', 'display_order', 'is_active',
        'is_active_now', 'view_count', 'click_count', 'click_rate',
        'start_date', 'end_date', 'created_at'
    ]
    list_filter = [
        'banner_type', 'position', 'is_active', 'show_for_authenticated', 'show_for_anonymous',
        'start_date', 'end_date', 'created_at'
    ]
    list_editable = ['display_order', 'is_active']
    search_fields = ['translations__title', 'translations__alt_text']
    ordering = ['display_order', 'created_at']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('banner_type', 'position', 'display_order', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'alt_text', 'link_url', 'link_target'),
        }),
        (_('Images'), {
            'fields': ('image', 'mobile_image'),
            'description': _('Upload banner image and optional mobile-specific image')
        }),
        (_('Targeting'), {
            'fields': ('show_on_pages', 'show_for_authenticated', 'show_for_anonymous'),
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'end_date'),
            'description': _('Optional date range for displaying this banner')
        }),
        (_('Analytics'), {
            'fields': ('view_count', 'click_count'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['view_count', 'click_count', 'click_rate']

    def click_rate(self, obj):
        """Display click rate in admin."""
        return f"{obj.click_rate:.1f}%" if obj.click_rate > 0 else "0%"
    click_rate.short_description = _('Click Rate')

    def is_active_now(self, obj):
        """Display current active status."""
        return obj.is_active_now()
    is_active_now.boolean = True
    is_active_now.short_description = _('Currently Active')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for SiteSettings model (singleton).
    """

    list_display = ['site_name', 'default_language', 'maintenance_mode', 'created_at', 'updated_at']
    search_fields = ['site_name', 'site_description']

    fieldsets = (
        (_('Basic Site Information'), {
            'fields': ('site_name', 'site_description', 'default_language')
        }),
        (_('Contact Defaults'), {
            'fields': ('default_phone', 'default_email')
        }),
        (_('Default Images'), {
            'fields': ('default_hero_image', 'default_tour_image', 'default_event_image', 'default_meta_image'),
            'description': _('These images will be used as fallbacks when no specific image is available')
        }),
        (_('Maintenance Mode'), {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'description': _('When maintenance mode is enabled, the site will show the maintenance message')
        }),
        (_('SEO Defaults'), {
            'fields': ('default_meta_title', 'default_meta_description'),
        }),
    )

    def has_add_permission(self, request):
        """Prevent adding multiple instances."""
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the single instance."""
        return False

    def changelist_view(self, request, extra_context=None):
        """Redirect to change view if instance exists."""
        if SiteSettings.objects.exists():
            settings = SiteSettings.objects.first()
            return self.change_view(request, str(settings.pk), extra_context=extra_context)
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ImageOptimization)
class ImageOptimizationAdmin(admin.ModelAdmin):
    """
    Admin interface for ImageOptimization model.
    """

    list_display = [
        'image_type', 'original_size_display', 'compression_ratio_display',
        'optimization_completed', 'created_at'
    ]
    list_filter = ['image_type', 'optimization_completed', 'created_at']
    search_fields = ['original_image']
    ordering = ['-created_at']

    fieldsets = (
        (_('Original Image'), {
            'fields': ('original_image', 'image_type'),
        }),
        (_('Image Metadata'), {
            'fields': ('original_width', 'original_height', 'original_size'),
        }),
        (_('Optimization Settings'), {
            'fields': ('quality_desktop', 'quality_tablet', 'quality_mobile'),
        }),
        (_('Optimized Versions'), {
            'fields': ('desktop_version', 'tablet_version', 'mobile_version', 'thumbnail'),
        }),
        (_('Results'), {
            'fields': ('optimized_size_desktop', 'optimized_size_tablet', 'optimized_size_mobile', 'optimization_completed'),
        }),
    )

    readonly_fields = [
        'original_width', 'original_height', 'original_size',
        'optimized_size_desktop', 'optimized_size_tablet', 'optimized_size_mobile',
        'compression_ratio'
    ]

    def original_size_display(self, obj):
        """Display original size in human readable format."""
        size_mb = obj.original_size / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    original_size_display.short_description = _('Original Size')

    def compression_ratio_display(self, obj):
        """Display compression ratio."""
        return f"{obj.compression_ratio:.1f}%" if obj.compression_ratio > 0 else "0%"
    compression_ratio_display.short_description = _('Compression Ratio')

    actions = ['mark_as_optimized', 'mark_as_unoptimized']

    def mark_as_optimized(self, request, queryset):
        """Mark selected images as optimized."""
        updated = queryset.update(optimization_completed=True)
        self.message_user(request, f'{updated} images marked as optimized.')
    mark_as_optimized.short_description = _('Mark selected images as optimized')

    def mark_as_unoptimized(self, request, queryset):
        """Mark selected images as unoptimized."""
        updated = queryset.update(optimization_completed=False)
        self.message_user(request, f'{updated} images marked as unoptimized.')
    mark_as_unoptimized.short_description = _('Mark selected images as unoptimized')


# New homepage section admin interfaces

@admin.register(AboutSection)
class AboutSectionAdmin(TranslatableAdmin):
    """
    Admin interface for AboutSection model.
    """

    list_display = ['title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['translations__title', 'translations__subtitle']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'subtitle', 'description', 'button_text', 'button_url'),
        }),
        (_('Media'), {
            'fields': ('hero_image',),
        }),
        (_('System Information'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('title',)}


@admin.register(AboutStatistic)
class AboutStatisticAdmin(TranslatableAdmin):
    """
    Admin interface for AboutStatistic model.
    """

    list_display = ['label', 'value', 'icon', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['translations__label']
    ordering = ['order']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'order', 'is_active')
        }),
        (_('Content'), {
            'fields': ('label', 'description', 'value', 'icon'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('label',)}


@admin.register(AboutFeature)
class AboutFeatureAdmin(TranslatableAdmin):
    """
    Admin interface for AboutFeature model.
    """

    list_display = ['title', 'icon', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['translations__title']
    ordering = ['order']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'order', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'description', 'icon'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('title',)}


@admin.register(CTASection)
class CTASectionAdmin(TranslatableAdmin):
    """
    Admin interface for CTASection model.
    """

    list_display = ['title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['translations__title', 'translations__subtitle']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'subtitle', 'description'),
        }),
        (_('Media'), {
            'fields': ('background_image',),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('title',)}


@admin.register(CTAButton)
class CTAButtonAdmin(TranslatableAdmin):
    """
    Admin interface for CTAButton model.
    """

    list_display = ['text', 'button_type', 'url', 'order', 'is_active']
    list_filter = ['button_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['translations__text']
    ordering = ['order']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'cta_section', 'order', 'is_active')
        }),
        (_('Content'), {
            'fields': ('text', 'url', 'button_type'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('text',)}


@admin.register(CTAFeature)
class CTAFeatureAdmin(TranslatableAdmin):
    """
    Admin interface for CTAFeature model.
    """

    list_display = ['text', 'icon', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['translations__text']
    ordering = ['order']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'cta_section', 'order', 'is_active')
        }),
        (_('Content'), {
            'fields': ('text', 'icon'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('text',)}


@admin.register(Footer)
class FooterAdmin(TranslatableAdmin):
    """
    Admin interface for Footer model (singleton).
    """

    list_display = ['company_name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['translations__company_name']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'is_active')
        }),
        (_('Company Information'), {
            'fields': ('company_name', 'company_description', 'logo'),
        }),
        (_('Newsletter'), {
            'fields': ('newsletter_title', 'newsletter_description', 'newsletter_placeholder'),
        }),
        (_('Contact Information'), {
            'fields': ('default_phone', 'default_email'),
        }),
        (_('Social Media'), {
            'fields': ('instagram_url', 'telegram_url', 'whatsapp_number', 'facebook_url'),
        }),
        (_('Additional Content'), {
            'fields': ('copyright_text', 'trusted_by_text'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('company_name',)}

    def has_add_permission(self, request):
        """Prevent adding multiple instances."""
        return not Footer.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the single instance."""
        return False

    def changelist_view(self, request, extra_context=None):
        """Redirect to change view if instance exists."""
        if Footer.objects.exists():
            footer = Footer.objects.first()
            return self.change_view(request, str(footer.pk), extra_context=extra_context)
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(FooterLink)
class FooterLinkAdmin(TranslatableAdmin):
    """
    Admin interface for FooterLink model.
    """

    list_display = ['label', 'url', 'link_type', 'order', 'is_active']
    list_filter = ['link_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['translations__label']
    ordering = ['order']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'footer', 'order', 'is_active')
        }),
        (_('Link Details'), {
            'fields': ('label', 'url', 'link_type'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('label',)}


@admin.register(TransferBookingSection)
class TransferBookingSectionAdmin(TranslatableAdmin):
    """
    Admin interface for TransferBookingSection model.
    """

    list_display = ['title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['translations__title']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'subtitle', 'description', 'button_text', 'button_url'),
        }),
        (_('Statistics'), {
            'fields': ('experience_years', 'countries_served'),
        }),
        (_('Features'), {
            'fields': ('feature_1', 'feature_2', 'feature_3', 'feature_4'),
        }),
        (_('Media'), {
            'fields': ('background_image',),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('title',)}


@admin.register(FAQSettings)
class FAQSettingsAdmin(TranslatableAdmin):
    """
    Admin interface for FAQSettings model (singleton).
    """

    list_display = ['title', 'items_per_page', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['translations__title']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'subtitle'),
        }),
        (_('Display Settings'), {
            'fields': ('items_per_page', 'show_categories', 'show_search'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        """Auto-populate slug field."""
        return {'slug': ('title',)}

    def has_add_permission(self, request):
        """Prevent adding multiple instances."""
        return not FAQSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the single instance."""
        return False

    def changelist_view(self, request, extra_context=None):
        """Redirect to change view if instance exists."""
        if FAQSettings.objects.exists():
            settings = FAQSettings.objects.first()
            return self.change_view(request, str(settings.pk), extra_context=extra_context)
        return super().changelist_view(request, extra_context=extra_context)
