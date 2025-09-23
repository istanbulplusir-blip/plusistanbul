"""
Shared models for Peykan Tourism Platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import EmailValidator
from core.models import BaseModel, BaseTranslatableModel
from parler.models import TranslatedFields


class StaticPage(BaseTranslatableModel):
    """
    Model for static pages like About Us, Terms, Privacy Policy.
    """
    
    PAGE_TYPES = [
        ('about', _('About Us')),
        ('terms', _('Terms & Conditions')),
        ('privacy', _('Privacy Policy')),
        ('faq', _('FAQ')),
        ('contact', _('Contact')),
    ]
    
    page_type = models.CharField(
        max_length=20, 
        choices=PAGE_TYPES, 
        unique=True,
        verbose_name=_('Page Type')
    )
    
    image = models.ImageField(
        upload_to='static_pages/', 
        null=True, 
        blank=True, 
        verbose_name=_('Page Image')
    )
    
    # SEO fields
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
        verbose_name=_('Meta Description')
    )
    meta_keywords = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name=_('Meta Keywords')
    )
    
    # Translatable fields
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_('Title')),
        content=models.TextField(verbose_name=_('Content')),
        excerpt=models.TextField(
            max_length=300, 
            blank=True, 
            verbose_name=_('Excerpt')
        ),
    )
    
    class Meta:
        verbose_name = _('Static Page')
        verbose_name_plural = _('Static Pages')
        db_table = 'shared_static_page'
        ordering = ['page_type']
    
    def __str__(self):
        return f"{self.get_page_type_display()}"


class ContactInfo(BaseModel):
    """
    Model for contact information.
    """
    
    # Basic contact info
    company_name = models.CharField(max_length=200, verbose_name=_('Company Name'))
    address = models.TextField(verbose_name=_('Address'))
    phone_primary = models.CharField(max_length=20, verbose_name=_('Primary Phone'))
    phone_secondary = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name=_('Secondary Phone')
    )
    email_general = models.EmailField(verbose_name=_('General Email'))
    email_support = models.EmailField(
        blank=True, 
        verbose_name=_('Support Email')
    )
    email_sales = models.EmailField(
        blank=True, 
        verbose_name=_('Sales Email')
    )
    
    # Working hours
    working_hours = models.CharField(
        max_length=100, 
        default='9:00 AM - 6:00 PM', 
        verbose_name=_('Working Hours')
    )
    working_days = models.CharField(
        max_length=100, 
        default='Monday - Friday', 
        verbose_name=_('Working Days')
    )
    
    # Location
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Latitude')
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Longitude')
    )
    
    # Social media
    instagram_url = models.URLField(blank=True, verbose_name=_('Instagram'))
    telegram_url = models.URLField(blank=True, verbose_name=_('Telegram'))
    whatsapp_number = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name=_('WhatsApp Number')
    )
    facebook_url = models.URLField(blank=True, verbose_name=_('Facebook'))
    twitter_url = models.URLField(blank=True, verbose_name=_('Twitter'))
    linkedin_url = models.URLField(blank=True, verbose_name=_('LinkedIn'))
    
    class Meta:
        verbose_name = _('Contact Information')
        verbose_name_plural = _('Contact Information')
        db_table = 'shared_contact_info'
    
    def __str__(self):
        return self.company_name


class ContactMessage(BaseModel):
    """
    Model for contact form messages from users.
    """
    
    STATUS_CHOICES = [
        ('new', _('New')),
        ('read', _('Read')),
        ('replied', _('Replied')),
        ('closed', _('Closed')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    # Sender information
    full_name = models.CharField(max_length=200, verbose_name=_('Full Name'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name=_('Phone Number')
    )
    
    # Message content
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message'))
    
    # Status and priority
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name=_('Status')
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name=_('Priority')
    )
    
    # Admin response
    admin_response = models.TextField(
        blank=True, 
        verbose_name=_('Admin Response')
    )
    responded_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_('Responded At')
    )
    responded_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='contact_responses',
        verbose_name=_('Responded By')
    )
    
    # IP tracking for security
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True, 
        verbose_name=_('IP Address')
    )
    
    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        db_table = 'shared_contact_message'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class FAQCategory(BaseTranslatableModel):
    """
    FAQ Category model for organizing FAQs.
    """
    
    # Translatable fields
    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name=_('Category Name')),
        description=models.TextField(
            blank=True, 
            verbose_name=_('Category Description')
        ),
    )
    
    # Category specific fields
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name=_('Icon Class'),
        help_text=_('CSS class for icon (e.g., fas fa-question-circle)')
    )
    color = models.CharField(
        max_length=7, 
        default='#007bff', 
        verbose_name=_('Color'),
        help_text=_('Hex color code for category')
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name=_('Display Order')
    )
    
    class Meta:
        verbose_name = _('FAQ Category')
        verbose_name_plural = _('FAQ Categories')
        db_table = 'shared_faq_category'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        try:
            return self.name or self.slug
        except:
            return self.slug


class FAQ(BaseModel):
    """
    Enhanced FAQ model with better organization and features.
    """
    
    # Basic fields (keeping compatibility with existing data)
    question = models.CharField(max_length=500, verbose_name=_('Question'))
    answer = models.TextField(verbose_name=_('Answer'))
    
    # Enhanced fields
    keywords = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name=_('Search Keywords'),
        help_text=_('Keywords to help users find this FAQ')
    )
    
    # Category relationship (nullable for migration)
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True,
        verbose_name=_('Category')
    )
    
    # Organization fields
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name=_('Display Order')
    )
    
    # Engagement tracking
    view_count = models.PositiveIntegerField(
        default=0, 
        verbose_name=_('View Count')
    )
    is_featured = models.BooleanField(
        default=False, 
        verbose_name=_('Is Featured'),
        help_text=_('Featured FAQs appear at the top')
    )
    
    # Status
    is_published = models.BooleanField(
        default=True, 
        verbose_name=_('Is Published')
    )
    
    # Tags for better searchability
    tags = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name=_('Tags'),
        help_text=_('Comma-separated tags for categorization')
    )
    
    class Meta:
        ordering = ['category__order', 'order', '-is_featured', 'created_at']
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        db_table = 'shared_faq'
        indexes = [
            models.Index(fields=['category', 'order']),
            models.Index(fields=['is_featured', 'is_published']),
            models.Index(fields=['view_count']),
        ]
    
    def __str__(self):
        return self.question
    
    def increment_view_count(self):
        """Increment the view count for this FAQ."""
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])
    
    def get_tags_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []


class SupportFAQ(BaseModel):
    """
    Model for predefined support questions that users can select from.
    """
    
    CATEGORY_CHOICES = [
        ('booking', _('Booking')),
        ('cancellation', _('Cancellation')),
        ('transfer', _('Transfer')),
        ('general', _('General Support')),
    ]
    
    # Question details
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name=_('Category')
    )
    
    question = models.CharField(
        max_length=500,
        verbose_name=_('Question')
    )
    
    # Pre-filled message for WhatsApp
    whatsapp_message = models.TextField(
        verbose_name=_('WhatsApp Message'),
        help_text=_('Pre-filled message that will be sent to WhatsApp')
    )
    
    # Display order
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display Order')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    
    class Meta:
        verbose_name = _('Support FAQ')
        verbose_name_plural = _('Support FAQs')
        db_table = 'shared_support_faq'
        ordering = ['category', 'order', 'created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.question}"
    
    def get_whatsapp_link(self, phone_number, custom_message=""):
        """
        Generate WhatsApp link with pre-filled message.
        
        Args:
            phone_number (str): WhatsApp phone number
            custom_message (str): Optional custom message to append
        
        Returns:
            str: WhatsApp URL
        """
        import urllib.parse
        
        # Combine predefined message with custom message
        full_message = self.whatsapp_message
        if custom_message:
            full_message += f"\n\n{custom_message}"
        
        # Encode message for URL
        encoded_message = urllib.parse.quote(full_message)
        
        # Format phone number (remove non-digits)
        formatted_phone = ''.join(filter(str.isdigit, phone_number))
        
        return f"https://wa.me/{formatted_phone}?text={encoded_message}"


class HeroSlider(BaseTranslatableModel):
    """
    Dynamic hero slider management for homepage.
    """

    # Translatable fields
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_('Title')),
        subtitle=models.CharField(max_length=300, verbose_name=_('Subtitle')),
        description=models.TextField(blank=True, verbose_name=_('Description')),
        button_text=models.CharField(max_length=50, default='Learn More', verbose_name=_('Button Text')),
    )

    # Images for different screen sizes
    desktop_image = models.ImageField(
        upload_to='hero/desktop/',
        blank=True,
        null=True,
        verbose_name=_('Desktop Image (1920x1080)'),
        help_text=_('Recommended size: 1920x1080px for desktop screens')
    )
    tablet_image = models.ImageField(
        upload_to='hero/tablet/',
        blank=True,
        null=True,
        verbose_name=_('Tablet Image (1024x768)'),
        help_text=_('Recommended size: 1024x768px for tablet screens')
    )
    mobile_image = models.ImageField(
        upload_to='hero/mobile/',
        blank=True,
        null=True,
        verbose_name=_('Mobile Image (768x1024)'),
        help_text=_('Recommended size: 768x1024px for mobile screens')
    )

    # Video support
    VIDEO_TYPES = [
        ('none', _('No Video')),
        ('file', _('Upload Video File')),
        ('url', _('External Video URL')),
    ]

    video_type = models.CharField(
        max_length=10,
        choices=VIDEO_TYPES,
        default='none',
        verbose_name=_('Video Type'),
        help_text=_('Choose whether to use a video file or external video URL')
    )

    video_file = models.FileField(
        upload_to='hero/videos/',
        blank=True,
        null=True,
        verbose_name=_('Video File'),
        help_text=_('Upload MP4, WebM, or OGV video file (max 50MB)')
    )

    video_url = models.URLField(
        blank=True,
        verbose_name=_('Video URL'),
        help_text=_('YouTube, Vimeo, or direct video URL')
    )

    video_thumbnail = models.ImageField(
        upload_to='hero/video_thumbnails/',
        blank=True,
        null=True,
        verbose_name=_('Video Thumbnail'),
        help_text=_('Custom thumbnail image for video (optional)')
    )

    autoplay_video = models.BooleanField(
        default=False,
        verbose_name=_('Autoplay Video'),
        help_text=_('Automatically play video when slide is active')
    )

    video_muted = models.BooleanField(
        default=True,
        verbose_name=_('Video Muted'),
        help_text=_('Start video muted (recommended for autoplay)')
    )

    show_video_controls = models.BooleanField(
        default=False,
        verbose_name=_('Show Video Controls'),
        help_text=_('Show video player controls (play, pause, volume, etc.)')
    )

    video_loop = models.BooleanField(
        default=True,
        verbose_name=_('Loop Video'),
        help_text=_('Loop video playback continuously')
    )

    # Content
    button_url = models.URLField(verbose_name=_('Button URL'))
    button_type = models.CharField(
        max_length=20,
        choices=[
            ('primary', _('Primary')),
            ('secondary', _('Secondary')),
            ('outline', _('Outline')),
        ],
        default='primary',
        verbose_name=_('Button Type')
    )

    # Display settings
    order = models.PositiveIntegerField(default=0, verbose_name=_('Display Order'))
    display_duration = models.PositiveIntegerField(
        default=5000,
        verbose_name=_('Display Duration (ms)'),
        help_text=_('How long this slide should be displayed in milliseconds')
    )

    # Targeting and conditions
    show_for_authenticated = models.BooleanField(default=True, verbose_name=_('Show for Authenticated Users'))
    show_for_anonymous = models.BooleanField(default=True, verbose_name=_('Show for Anonymous Users'))

    # Seasonal display
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Start Date'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('End Date'))

    # Analytics
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('View Count'))
    click_count = models.PositiveIntegerField(default=0, verbose_name=_('Click Count'))

    class Meta:
        verbose_name = _('Hero Slide')
        verbose_name_plural = _('Hero Slides')
        ordering = ['order', 'created_at']

    def __str__(self):
        return getattr(self, 'title', '') or f"Hero Slide {self.id}"

    def is_active_now(self):
        """Check if slide should be active based on dates."""
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    @property
    def click_rate(self):
        """Calculate click rate."""
        if self.view_count == 0:
            return 0
        return (self.click_count / self.view_count) * 100

    def has_video(self):
        """Check if slide has video content."""
        return self.video_type != 'none' and (self.video_file or self.video_url)

    def get_video_url(self):
        """Get the appropriate video URL based on video type."""
        if self.video_type == 'file' and self.video_file:
            return self.video_file.url
        elif self.video_type == 'url' and self.video_url:
            return self.video_url
        return None

    def get_video_thumbnail_url(self):
        """Get video thumbnail URL, fallback to desktop image."""
        if self.video_thumbnail:
            return self.video_thumbnail.url
        elif self.desktop_image:
            return self.desktop_image.url
        return None

    def is_video_autoplay_allowed(self):
        """Check if video autoplay is allowed (muted videos can autoplay)."""
        return self.autoplay_video and self.video_muted

    @property
    def video_display_name(self):
        """Get display name for video type."""
        video_type_map = {
            'none': _('No Video'),
            'file': _('Video File'),
            'url': _('External Video'),
        }
        return video_type_map.get(self.video_type, _('Unknown'))


class Banner(BaseTranslatableModel):
    """
    Dynamic banner management for different sections.
    """

    BANNER_TYPES = [
        ('homepage_top', _('Homepage Top')),
        ('homepage_bottom', _('Homepage Bottom')),
        ('tour_detail', _('Tour Detail Page')),
        ('event_detail', _('Event Detail Page')),
        ('seasonal', _('Seasonal Banner')),
        ('promotion', _('Promotional Banner')),
        ('sidebar', _('Sidebar Banner')),
    ]

    BANNER_POSITIONS = [
        ('top', _('Top')),
        ('middle', _('Middle')),
        ('bottom', _('Bottom')),
        ('sidebar', _('Sidebar')),
        ('popup', _('Popup')),
    ]

    # Translatable fields
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_('Title')),
        alt_text=models.CharField(max_length=200, verbose_name=_('Alt Text')),
    )

    # Banner details
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, verbose_name=_('Banner Type'))
    position = models.CharField(max_length=20, choices=BANNER_POSITIONS, default='top', verbose_name=_('Position'))

    # Images
    image = models.ImageField(
        upload_to='banners/',
        verbose_name=_('Banner Image'),
        help_text=_('Recommended size: 1200x400px for banners')
    )
    mobile_image = models.ImageField(
        upload_to='banners/mobile/',
        blank=True,
        null=True,
        verbose_name=_('Mobile Banner Image'),
        help_text=_('Optional mobile-specific image')
    )

    # Content
    link_url = models.URLField(blank=True, verbose_name=_('Link URL'))
    link_target = models.CharField(
        max_length=20,
        choices=[
            ('_self', _('Same Window')),
            ('_blank', _('New Window')),
        ],
        default='_self',
        verbose_name=_('Link Target')
    )

    # Display settings
    display_order = models.PositiveIntegerField(default=0, verbose_name=_('Display Order'))

    # Date restrictions
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Start Date'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('End Date'))

    # Targeting
    show_on_pages = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Show on Pages'),
        help_text=_('List of page URLs or patterns where this banner should appear')
    )

    # User targeting
    show_for_authenticated = models.BooleanField(default=True, verbose_name=_('Show for Authenticated Users'))
    show_for_anonymous = models.BooleanField(default=True, verbose_name=_('Show for Anonymous Users'))

    # Analytics
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('View Count'))
    click_count = models.PositiveIntegerField(default=0, verbose_name=_('Click Count'))

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return getattr(self, 'title', '') or f"{self.get_banner_type_display()} Banner"

    def is_active_now(self):
        """Check if banner should be active."""
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    @property
    def click_rate(self):
        """Calculate click rate."""
        if self.view_count == 0:
            return 0
        return (self.click_count / self.view_count) * 100


class SiteSettings(BaseModel):
    """
    Global site settings and defaults.
    Singleton model - only one instance allowed.
    """

    # Basic site information
    site_name = models.CharField(
        max_length=100,
        default='Peykan Tourism',
        verbose_name=_('Site Name')
    )
    site_description = models.TextField(
        blank=True,
        verbose_name=_('Site Description')
    )
    default_language = models.CharField(
        max_length=10,
        default='fa',
        verbose_name=_('Default Language')
    )

    # Contact defaults
    default_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Default Phone Number')
    )
    default_email = models.EmailField(
        blank=True,
        verbose_name=_('Default Email')
    )

    # Default images
    default_hero_image = models.ImageField(
        upload_to='defaults/hero/',
        blank=True,
        null=True,
        verbose_name=_('Default Hero Image'),
        help_text=_('Fallback image for hero section')
    )
    default_tour_image = models.ImageField(
        upload_to='defaults/tours/',
        blank=True,
        null=True,
        verbose_name=_('Default Tour Image'),
        help_text=_('Fallback image for tours')
    )
    default_event_image = models.ImageField(
        upload_to='defaults/events/',
        blank=True,
        null=True,
        verbose_name=_('Default Event Image'),
        help_text=_('Fallback image for events')
    )

    # Social media defaults
    default_meta_image = models.ImageField(
        upload_to='defaults/meta/',
        blank=True,
        null=True,
        verbose_name=_('Default Meta Image'),
        help_text=_('Default image for social media sharing')
    )

    # Maintenance mode
    maintenance_mode = models.BooleanField(
        default=False,
        verbose_name=_('Maintenance Mode')
    )
    maintenance_message = models.TextField(
        blank=True,
        verbose_name=_('Maintenance Message'),
        help_text=_('Message to show when site is in maintenance mode')
    )

    # SEO defaults
    default_meta_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=_('Default Meta Title')
    )
    default_meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_('Default Meta Description')
    )

    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            # Update existing instance instead of creating new one
            existing = SiteSettings.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the site settings instance."""
        settings, created = cls.objects.get_or_create(
            defaults={
                'site_name': 'Peykan Tourism',
                'default_language': 'fa'
            }
        )
        return settings


class ImageOptimization(BaseModel):
    """
    Track image optimizations and generate responsive versions.
    """

    IMAGE_TYPES = [
        ('hero', _('Hero Image')),
        ('tour', _('Tour Image')),
        ('event', _('Event Image')),
        ('banner', _('Banner Image')),
        ('profile', _('Profile Image')),
        ('gallery', _('Gallery Image')),
    ]

    # Original image
    original_image = models.ImageField(
        upload_to='originals/',
        verbose_name=_('Original Image')
    )
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPES,
        verbose_name=_('Image Type')
    )

    # Generated responsive versions
    desktop_version = models.ImageField(
        upload_to='optimized/desktop/',
        blank=True,
        null=True,
        verbose_name=_('Desktop Version')
    )
    tablet_version = models.ImageField(
        upload_to='optimized/tablet/',
        blank=True,
        null=True,
        verbose_name=_('Tablet Version')
    )
    mobile_version = models.ImageField(
        upload_to='optimized/mobile/',
        blank=True,
        null=True,
        verbose_name=_('Mobile Version')
    )
    thumbnail = models.ImageField(
        upload_to='optimized/thumbnail/',
        blank=True,
        null=True,
        verbose_name=_('Thumbnail')
    )

    # Metadata
    original_width = models.PositiveIntegerField(verbose_name=_('Original Width'))
    original_height = models.PositiveIntegerField(verbose_name=_('Original Height'))
    original_size = models.PositiveIntegerField(verbose_name=_('Original Size (bytes)'))

    # Optimization settings
    quality_desktop = models.PositiveIntegerField(default=85, verbose_name=_('Desktop Quality'))
    quality_tablet = models.PositiveIntegerField(default=80, verbose_name=_('Tablet Quality'))
    quality_mobile = models.PositiveIntegerField(default=75, verbose_name=_('Mobile Quality'))

    # Results
    optimized_size_desktop = models.PositiveIntegerField(default=0, verbose_name=_('Optimized Desktop Size'))
    optimized_size_tablet = models.PositiveIntegerField(default=0, verbose_name=_('Optimized Tablet Size'))
    optimized_size_mobile = models.PositiveIntegerField(default=0, verbose_name=_('Optimized Mobile Size'))

    # Status
    optimization_completed = models.BooleanField(default=False, verbose_name=_('Optimization Completed'))

    class Meta:
        verbose_name = _('Image Optimization')
        verbose_name_plural = _('Image Optimizations')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_image_type_display()} - {self.original_image.name}"

    @property
    def total_optimized_size(self):
        """Calculate total optimized size."""
        return (self.optimized_size_desktop +
                self.optimized_size_tablet +
                self.optimized_size_mobile)

    @property
    def compression_ratio(self):
        """Calculate compression ratio."""
        if self.original_size == 0:
            return 0
        return ((self.original_size - self.total_optimized_size) / self.original_size) * 100


class AboutSection(BaseTranslatableModel):
    """
    مدیریت بخش About در صفحه خانگی
    """

    # Translatable fields
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_('Title')),
        subtitle=models.CharField(max_length=300, verbose_name=_('Subtitle')),
        description=models.TextField(verbose_name=_('Description')),
        button_text=models.CharField(max_length=50, default='Learn More', verbose_name=_('Button Text')),
    )

    # Content
    button_url = models.URLField(verbose_name=_('Button URL'))
    hero_image = models.ImageField(
        upload_to='about/',
        verbose_name=_('Hero Image'),
        help_text=_('Main image for about section')
    )

    # Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('About Section')
        verbose_name_plural = _('About Section')

    def __str__(self):
        return "About Section"


class AboutStatistic(BaseTranslatableModel):
    """
    آمارهای بخش About
    """

    translations = TranslatedFields(
        label=models.CharField(max_length=100, verbose_name=_('Label')),
        description=models.TextField(blank=True, verbose_name=_('Description')),
    )

    value = models.CharField(max_length=50, verbose_name=_('Value'))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Icon'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Display Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('About Statistic')
        verbose_name_plural = _('About Statistics')
        ordering = ['order']

    def __str__(self):
        return f"{self.label} - {self.value}"


class AboutFeature(BaseTranslatableModel):
    """
    ویژگی‌های بخش About
    """

    translations = TranslatedFields(
        title=models.CharField(max_length=100, verbose_name=_('Title')),
        description=models.TextField(blank=True, verbose_name=_('Description')),
    )

    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Icon'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Display Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('About Feature')
        verbose_name_plural = _('About Features')
        ordering = ['order']

    def __str__(self):
        return self.title


class CTASection(BaseTranslatableModel):
    """
    مدیریت بخش Call-to-Action در صفحه خانگی
    """

    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_('Title')),
        subtitle=models.CharField(max_length=300, verbose_name=_('Subtitle')),
        description=models.TextField(verbose_name=_('Description')),
    )

    # Background
    background_image = models.ImageField(
        upload_to='cta/',
        blank=True,
        null=True,
        verbose_name=_('Background Image')
    )

    # Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('CTA Section')
        verbose_name_plural = _('CTA Section')

    def __str__(self):
        return "CTA Section"


class CTAButton(BaseTranslatableModel):
    """
    دکمه‌های بخش CTA
    """

    translations = TranslatedFields(
        text=models.CharField(max_length=100, verbose_name=_('Button Text')),
    )

    cta_section = models.ForeignKey(
        CTASection,
        on_delete=models.CASCADE,
        related_name='buttons',
        verbose_name=_('CTA Section')
    )

    url = models.URLField(verbose_name=_('URL'))
    button_type = models.CharField(
        max_length=20,
        choices=[
            ('primary', _('Primary')),
            ('secondary', _('Secondary')),
            ('outline', _('Outline')),
        ],
        default='primary',
        verbose_name=_('Button Type')
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Display Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('CTA Button')
        verbose_name_plural = _('CTA Buttons')
        ordering = ['order']

    def __str__(self):
        return f"{self.text} ({self.get_button_type_display()})"


class CTAFeature(BaseTranslatableModel):
    """
    ویژگی‌های بخش CTA
    """

    translations = TranslatedFields(
        text=models.CharField(max_length=100, verbose_name=_('Feature Text')),
    )

    cta_section = models.ForeignKey(
        CTASection,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name=_('CTA Section')
    )

    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Icon'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Display Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('CTA Feature')
        verbose_name_plural = _('CTA Features')
        ordering = ['order']

    def __str__(self):
        return self.text


class Footer(BaseTranslatableModel):
    """
    مدیریت Footer (singleton model)
    """

    translations = TranslatedFields(
        newsletter_title=models.CharField(max_length=200, default='Newsletter', verbose_name=_('Newsletter Title')),
        newsletter_description=models.TextField(default='Get exclusive deals...', verbose_name=_('Newsletter Description')),
        company_name=models.CharField(max_length=200, default='Peykan Tourism', verbose_name=_('Company Name')),
        company_description=models.TextField(default='Your travel companion', verbose_name=_('Company Description')),
        copyright_text=models.CharField(max_length=200, default='© 2024 Peykan Tourism', verbose_name=_('Copyright Text')),
        newsletter_placeholder=models.CharField(max_length=200, default='Enter your email', verbose_name=_('Newsletter Placeholder')),
        trusted_by_text=models.CharField(max_length=200, default='Trusted by 50K+ travelers', verbose_name=_('Trusted By Text')),
    )

    # Images
    logo = models.ImageField(
        upload_to='footer/',
        blank=True,
        null=True,
        verbose_name=_('Company Logo')
    )

    # Contact info
    default_phone = models.CharField(max_length=20, blank=True, verbose_name=_('Default Phone'))
    default_email = models.EmailField(blank=True, verbose_name=_('Default Email'))

    # Social media
    instagram_url = models.URLField(blank=True, verbose_name=_('Instagram'))
    telegram_url = models.URLField(blank=True, verbose_name=_('Telegram'))
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name=_('WhatsApp'))
    facebook_url = models.URLField(blank=True, verbose_name=_('Facebook'))

    # Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('Footer')
        verbose_name_plural = _('Footer')

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and Footer.objects.exists():
            existing = Footer.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return
        super().save(*args, **kwargs)

    @classmethod
    def get_footer(cls):
        """Get the footer instance."""
        footer, created = cls.objects.get_or_create(
            defaults={
                'company_name': 'Peykan Tourism',
            }
        )
        return footer

    def __str__(self):
        return "Footer"


class FooterLink(BaseTranslatableModel):
    """
    لینک‌های ناوبری Footer
    """

    translations = TranslatedFields(
        label=models.CharField(max_length=100, verbose_name=_('Label')),
    )

    footer = models.ForeignKey(
        Footer,
        on_delete=models.CASCADE,
        related_name='navigation_links',
        verbose_name=_('Footer')
    )

    url = models.URLField(verbose_name=_('URL'))
    link_type = models.CharField(
        max_length=20,
        choices=[
            ('internal', _('Internal')),
            ('external', _('External')),
        ],
        default='internal',
        verbose_name=_('Link Type')
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Display Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('Footer Link')
        verbose_name_plural = _('Footer Links')
        ordering = ['order']

    def __str__(self):
        return self.label


class TransferBookingSection(BaseTranslatableModel):
    """
    مدیریت بخش Transfer Booking در صفحه خانگی
    """

    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_('Title')),
        subtitle=models.CharField(max_length=300, verbose_name=_('Subtitle')),
        description=models.TextField(verbose_name=_('Description')),
        button_text=models.CharField(max_length=50, default='Book Transfer', verbose_name=_('Button Text')),
        feature_1=models.CharField(max_length=100, default='Luxury vehicles', verbose_name=_('Feature 1')),
        feature_2=models.CharField(max_length=100, default='Professional drivers', verbose_name=_('Feature 2')),
        feature_3=models.CharField(max_length=100, default='24/7 tracking', verbose_name=_('Feature 3')),
        feature_4=models.CharField(max_length=100, default='Complete safety', verbose_name=_('Feature 4')),
    )

    # Content
    button_url = models.URLField(default='/transfers/booking', verbose_name=_('Button URL'))
    background_image = models.ImageField(
        upload_to='transfer/',
        blank=True,
        null=True,
        verbose_name=_('Background Image')
    )

    # Statistics
    experience_years = models.PositiveIntegerField(default=20, verbose_name=_('Years of Experience'))
    countries_served = models.PositiveIntegerField(default=100, verbose_name=_('Countries Served'))

    # Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('Transfer Booking Section')
        verbose_name_plural = _('Transfer Booking Section')

    def __str__(self):
        return "Transfer Booking Section"


class FAQSettings(BaseTranslatableModel):
    """
    تنظیمات بخش FAQ در صفحه خانگی
    """

    translations = TranslatedFields(
        title=models.CharField(max_length=200, default='Frequently Asked Questions', verbose_name=_('Title')),
        subtitle=models.CharField(max_length=300, default='Find answers to common questions', verbose_name=_('Subtitle')),
    )

    # Display settings
    items_per_page = models.PositiveIntegerField(default=5, verbose_name=_('Items per page'))
    show_categories = models.BooleanField(default=True, verbose_name=_('Show categories'))
    show_search = models.BooleanField(default=True, verbose_name=_('Show search'))

    # Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('FAQ Settings')
        verbose_name_plural = _('FAQ Settings')

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and FAQSettings.objects.exists():
            existing = FAQSettings.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get FAQ settings instance."""
        settings, created = cls.objects.get_or_create(
            defaults={
                'title': 'Frequently Asked Questions',
                'items_per_page': 5,
            }
        )
        return settings

    def __str__(self):
        return "FAQ Settings"
