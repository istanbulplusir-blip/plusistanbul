"""
Shared serializer mixins and utilities for Peykan Tourism Platform.
"""

from rest_framework import serializers
from django.conf import settings
from .utils import get_image_url


class ImageFieldSerializerMixin:
    """
    Mixin to automatically convert ImageField to absolute URLs with fallbacks.
    """
    
    def get_default_image_url(self, model_type='product'):
        """Get default image URL based on model type."""
        defaults = {
            'product': '/media/defaults/no-image.png',
            'tour': '/media/defaults/tour-default.png',
            'event': '/media/defaults/event-default.png',
            'venue': '/media/defaults/venue-default.png',
            'artist': '/media/defaults/artist-default.png',
            'transfer': '/media/defaults/transfer-default.png',
            'about': '/media/defaults/no-image.png',
            'cta': '/media/defaults/no-image.png',
            'logo': '/media/defaults/no-image.png',
            'hero': '/media/defaults/no-image.png',
            'banner': '/media/defaults/no-image.png',
        }
        return defaults.get(model_type, defaults['product'])
    
    def get_image_url(self, obj, field_name='image', model_type='product'):
        """
        Get absolute URL for an image field with fallback.
        
        Args:
            obj: Model instance
            field_name: Name of the image field
            model_type: Type of model for default image selection
        
        Returns:
            str: Absolute URL to the image or default fallback
        """
        image_field = getattr(obj, field_name, None)
        if not image_field:
            # Return default image URL
            return self.get_default_image_url(model_type)
        
        request = self.context.get('request')
        return get_image_url(image_field, request)
    
    def get_image_urls(self, obj, field_names=None, model_type='product'):
        """
        Get absolute URLs for multiple image fields with fallbacks.
        
        Args:
            obj: Model instance
            field_names: List of image field names
            model_type: Type of model for default image selection
        
        Returns:
            dict: Dictionary of field_name: absolute_url
        """
        if field_names is None:
            field_names = ['image']
        
        urls = {}
        for field_name in field_names:
            urls[field_name] = self.get_image_url(obj, field_name, model_type)
        
        return urls


class OptimizedImageSerializerMixin:
    """
    Mixin to provide optimized image URLs with different sizes.
    """
    
    def get_optimized_image_urls(self, obj, field_name='image'):
        """
        Get optimized image URLs for different sizes.
        
        Args:
            obj: Model instance
            field_name: Name of the image field
        
        Returns:
            dict: Dictionary of size: optimized_url
        """
        base_url = self.get_image_url(obj, field_name)
        if not base_url:
            return None
        
        # In production, you might want to use a CDN or image processing service
        # For now, return the base URL with size hints
        return {
            'original': base_url,
            'large': base_url,  # 900x600
            'medium': base_url,  # 600x400
            'small': base_url,   # 300x200
            'thumbnail': base_url,  # 150x100
        }


class ImageValidationMixin:
    """
    Mixin to validate image fields.
    """
    
    def validate_image(self, value):
        """
        Validate uploaded image.
        
        Args:
            value: Uploaded file
        
        Returns:
            UploadedFile: Validated file
        
        Raises:
            ValidationError: If image is invalid
        """
        if not value:
            return value
        
        from .utils import validate_image_file
        
        is_valid, error_message = validate_image_file(
            value,
            max_size_mb=settings.MAX_IMAGE_SIZE_MB,
            allowed_formats=settings.IMAGE_FORMATS
        )
        
        if not is_valid:
            raise serializers.ValidationError(error_message)
        
        return value


class BaseModelSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """
    Base serializer with image URL support.
    """
    
    class Meta:
        abstract = True
    
    def to_representation(self, instance):
        """
        Convert model instance to representation with absolute image URLs.
        """
        data = super().to_representation(instance)
        
        # Add image URLs for all ImageField fields
        for field in instance._meta.get_fields():
            if hasattr(field, 'get_internal_type') and field.get_internal_type() == 'ImageField':
                field_name = field.name
                data[f'{field_name}_url'] = self.get_image_url(instance, field_name)
        
        return data


class ProductImageSerializer(BaseModelSerializer):
    """
    Serializer for products with image support.
    """
    
    image_url = serializers.SerializerMethodField()
    image_thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        abstract = True
    
    def get_image_url(self, obj):
        """Get absolute URL for product image."""
        if not hasattr(self, '_image_mixin'):
            self._image_mixin = ImageFieldSerializerMixin()
            self._image_mixin.context = self.context
        return self._image_mixin.get_image_url(obj, 'image')
    
    def get_image_thumbnail(self, obj):
        """Get thumbnail URL for product image."""
        if not hasattr(self, '_image_mixin'):
            self._image_mixin = ImageFieldSerializerMixin()
            self._image_mixin.context = self.context
        base_url = self._image_mixin.get_image_url(obj, 'image')
        if base_url:
            # In production, you might want to use a CDN for thumbnails
            return base_url
        return None


class UserAvatarSerializer(BaseModelSerializer):
    """
    Serializer for user avatars with image support.
    """
    
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        abstract = True
    
    def get_avatar_url(self, obj):
        """Get absolute URL for user avatar."""
        return self.get_image_url(obj, 'avatar')


class FAQSerializer(serializers.ModelSerializer):
    """
    Serializer for FAQ model.
    """
    
    class Meta:
        model = None  # Will be set dynamically
        fields = ['id', 'question', 'answer', 'category', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import FAQ
        self.Meta.model = FAQ


class FAQListSerializer(serializers.ModelSerializer):
    """
    Serializer for FAQ list view (public).
    """
    
    class Meta:
        model = None  # Will be set dynamically
        fields = ['id', 'question', 'answer', 'category', 'order']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import FAQ
        self.Meta.model = FAQ


class StaticPageSerializer(BaseModelSerializer):
    """
    Serializer for StaticPage model.
    """
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'id', 'page_type', 'slug', 'title', 'content', 'excerpt',
            'image', 'image_url', 'meta_description', 'meta_keywords',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import StaticPage
        self.Meta.model = StaticPage
    
    def get_image_url(self, obj):
        """Get absolute URL for page image."""
        if not hasattr(self, '_image_mixin'):
            self._image_mixin = ImageFieldSerializerMixin()
            self._image_mixin.context = self.context
        return self._image_mixin.get_image_url(obj, 'image', 'page')


class StaticPageListSerializer(serializers.ModelSerializer):
    """
    Serializer for StaticPage list view (public).
    """
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'id', 'page_type', 'slug', 'title', 'excerpt',
            'image_url', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import StaticPage
        self.Meta.model = StaticPage
    
    def get_image_url(self, obj):
        """Get absolute URL for page image."""
        if not hasattr(self, '_image_mixin'):
            self._image_mixin = ImageFieldSerializerMixin()
            self._image_mixin.context = self.context
        return self._image_mixin.get_image_url(obj, 'image', 'page')


class ContactInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for ContactInfo model.
    """
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'id', 'company_name', 'address', 'phone_primary', 'phone_secondary',
            'email_general', 'email_support', 'email_sales',
            'working_hours', 'working_days', 'latitude', 'longitude',
            'instagram_url', 'telegram_url', 'whatsapp_number',
            'facebook_url', 'twitter_url', 'linkedin_url',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import ContactInfo
        self.Meta.model = ContactInfo


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ContactMessage model (admin view).
    """
    
    responded_by_name = serializers.CharField(
        source='responded_by.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'id', 'full_name', 'email', 'phone', 'subject', 'message',
            'status', 'priority', 'admin_response', 'responded_at',
            'responded_by', 'responded_by_name', 'ip_address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'ip_address', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import ContactMessage
        self.Meta.model = ContactMessage


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ContactMessage (public form).
    """
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'full_name', 'email', 'phone', 'subject', 'message'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import ContactMessage
        self.Meta.model = ContactMessage
    
    def create(self, validated_data):
        """Create contact message with IP tracking."""
        request = self.context.get('request')
        if request:
            # Get client IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            validated_data['ip_address'] = ip
        
        return super().create(validated_data)


class ContactMessageListSerializer(serializers.ModelSerializer):
    """
    Serializer for ContactMessage list view (admin).
    """
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'id', 'full_name', 'email', 'subject', 'status', 'priority',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import ContactMessage
        self.Meta.model = ContactMessage


class SupportFAQSerializer(serializers.ModelSerializer):
    """
    Serializer for SupportFAQ model.
    """
    
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    
    whatsapp_link = serializers.SerializerMethodField()
    
    class Meta:
        model = None  # Will be set dynamically
        fields = [
            'id', 'category', 'category_display', 'question', 
            'whatsapp_message', 'order', 'is_active', 'whatsapp_link',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import SupportFAQ
        self.Meta.model = SupportFAQ
    
    def get_whatsapp_link(self, obj):
        """Generate WhatsApp link for this FAQ."""
        try:
            from .whatsapp_service import CentralizedWhatsAppService
            whatsapp_number = CentralizedWhatsAppService.get_whatsapp_number()
            return obj.get_whatsapp_link(whatsapp_number)
        except:
            return None


class HeroSliderSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """
    Serializer for HeroSlider model.
    """

    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    button_text = serializers.SerializerMethodField()

    desktop_image_url = serializers.SerializerMethodField()
    tablet_image_url = serializers.SerializerMethodField()
    mobile_image_url = serializers.SerializerMethodField()

    # Video fields
    video_file_url = serializers.SerializerMethodField()
    video_thumbnail_url = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    video_display_name = serializers.SerializerMethodField()
    is_video_autoplay_allowed = serializers.SerializerMethodField()

    is_active_now = serializers.SerializerMethodField()
    click_rate = serializers.SerializerMethodField()

    class Meta:
        from .models import HeroSlider
        model = None  # Will be set dynamically
        fields = [
            'id', 'title', 'subtitle', 'description', 'button_text', 'button_url', 'button_type',
            'desktop_image', 'tablet_image', 'mobile_image',
            'desktop_image_url', 'tablet_image_url', 'mobile_image_url',
            # Video fields
            'video_type', 'video_file', 'video_url', 'video_thumbnail',
            'video_file_url', 'video_thumbnail_url', 'has_video', 'video_display_name',
            'autoplay_video', 'video_muted', 'show_video_controls', 'video_loop',
            'is_video_autoplay_allowed',
            'order', 'display_duration', 'show_for_authenticated', 'show_for_anonymous',
            'start_date', 'end_date', 'is_active', 'is_active_now',
            'view_count', 'click_count', 'click_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count', 'click_count', 'click_rate']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import HeroSlider
        self.Meta.model = HeroSlider

    def get_title(self, obj):
        return obj.title

    def get_subtitle(self, obj):
        return obj.subtitle

    def get_description(self, obj):
        return obj.description

    def get_button_text(self, obj):
        return obj.button_text

    def get_desktop_image_url(self, obj):
        return self.get_image_url(obj, 'desktop_image', 'hero')

    def get_tablet_image_url(self, obj):
        return self.get_image_url(obj, 'tablet_image', 'hero')

    def get_mobile_image_url(self, obj):
        return self.get_image_url(obj, 'mobile_image', 'hero')

    def get_is_active_now(self, obj):
        return obj.is_active_now()

    def get_click_rate(self, obj):
        return obj.click_rate

    # Video methods
    def get_video_file_url(self, obj):
        """Get video file URL."""
        if obj.video_file:
            return self.get_image_url(obj, 'video_file', 'video')
        return None

    def get_video_thumbnail_url(self, obj):
        """Get video thumbnail URL."""
        if obj.video_thumbnail:
            return self.get_image_url(obj, 'video_thumbnail', 'hero')
        return obj.get_video_thumbnail_url()

    def get_has_video(self, obj):
        """Check if slide has video."""
        return obj.has_video()

    def get_video_display_name(self, obj):
        """Get video type display name."""
        return obj.video_display_name

    def get_is_video_autoplay_allowed(self, obj):
        """Check if video autoplay is allowed."""
        return obj.is_video_autoplay_allowed()


class BannerSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """
    Serializer for Banner model.
    """

    title = serializers.SerializerMethodField()
    alt_text = serializers.SerializerMethodField()

    image_url_field = serializers.SerializerMethodField()
    mobile_image_url = serializers.SerializerMethodField()

    is_active_now = serializers.SerializerMethodField()
    click_rate = serializers.SerializerMethodField()

    class Meta:
        from .models import Banner
        model = None  # Will be set dynamically
        fields = [
            'id', 'title', 'alt_text', 'banner_type', 'position',
            'image', 'mobile_image', 'image_url_field', 'mobile_image_url',
            'link_url', 'link_target', 'display_order',
            'start_date', 'end_date', 'show_on_pages',
            'show_for_authenticated', 'show_for_anonymous',
            'is_active', 'is_active_now', 'view_count', 'click_count', 'click_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count', 'click_count', 'click_rate']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import Banner
        self.Meta.model = Banner

    def get_title(self, obj):
        return obj.title

    def get_alt_text(self, obj):
        return obj.alt_text

    def get_image_url_field(self, obj):
        return self.get_image_url(obj, 'image', 'banner')

    def get_mobile_image_url(self, obj):
        if obj.mobile_image:
            return self.get_image_url(obj, 'mobile_image', 'banner')
        return None

    def get_is_active_now(self, obj):
        return obj.is_active_now()

    def get_click_rate(self, obj):
        return obj.click_rate


class SiteSettingsSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """
    Serializer for SiteSettings model.
    """

    default_hero_image_url = serializers.SerializerMethodField()
    default_tour_image_url = serializers.SerializerMethodField()
    default_event_image_url = serializers.SerializerMethodField()
    default_meta_image_url = serializers.SerializerMethodField()

    class Meta:
        from .models import SiteSettings
        model = None  # Will be set dynamically
        fields = [
            'id', 'site_name', 'site_description', 'default_language',
            'default_phone', 'default_email',
            'default_hero_image', 'default_tour_image', 'default_event_image', 'default_meta_image',
            'default_hero_image_url', 'default_tour_image_url', 'default_event_image_url', 'default_meta_image_url',
            'maintenance_mode', 'maintenance_message',
            'default_meta_title', 'default_meta_description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import SiteSettings
        self.Meta.model = SiteSettings

    def get_default_hero_image_url(self, obj):
        return self.get_image_url(obj, 'default_hero_image', 'hero')

    def get_default_tour_image_url(self, obj):
        return self.get_image_url(obj, 'default_tour_image', 'tour')

    def get_default_event_image_url(self, obj):
        return self.get_image_url(obj, 'default_event_image', 'event')

    def get_default_meta_image_url(self, obj):
        return self.get_image_url(obj, 'default_meta_image', 'meta')


class ImageOptimizationSerializer(serializers.ModelSerializer):
    """
    Serializer for ImageOptimization model.
    """

    compression_ratio = serializers.SerializerMethodField()

    class Meta:
        from .models import ImageOptimization
        model = None  # Will be set dynamically
        fields = [
            'id', 'original_image', 'image_type',
            'desktop_version', 'tablet_version', 'mobile_version', 'thumbnail',
            'original_width', 'original_height', 'original_size',
            'quality_desktop', 'quality_tablet', 'quality_mobile',
            'optimized_size_desktop', 'optimized_size_tablet', 'optimized_size_mobile',
            'optimization_completed', 'compression_ratio',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'compression_ratio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set model dynamically to avoid circular imports
        from .models import ImageOptimization
        self.Meta.model = ImageOptimization

    def get_compression_ratio(self, obj):
        return obj.compression_ratio


class AboutSectionSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Serializer for About Section"""

    title = serializers.CharField()
    subtitle = serializers.CharField()
    description = serializers.CharField()
    button_text = serializers.CharField()

    hero_image_url = serializers.SerializerMethodField()

    class Meta:
        from .models import AboutSection
        model = AboutSection
        fields = [
            'id', 'title', 'subtitle', 'description', 'button_text',
            'button_url', 'hero_image', 'hero_image_url', 'is_active', 'created_at', 'updated_at'
        ]

    def get_hero_image_url(self, obj):
        return self.get_image_url(obj, 'hero_image', 'about')


class AboutStatisticSerializer(serializers.ModelSerializer):
    """Serializer for About Statistics"""

    label = serializers.CharField()
    description = serializers.CharField(required=False)

    class Meta:
        from .models import AboutStatistic
        model = AboutStatistic
        fields = [
            'id', 'label', 'description', 'value', 'icon', 'order', 'is_active'
        ]


class AboutFeatureSerializer(serializers.ModelSerializer):
    """Serializer for About Features"""

    title = serializers.CharField()
    description = serializers.CharField(required=False)

    class Meta:
        from .models import AboutFeature
        model = AboutFeature
        fields = [
            'id', 'title', 'description', 'icon', 'order', 'is_active'
        ]


class CTASectionSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Serializer for CTA Section"""

    title = serializers.CharField()
    subtitle = serializers.CharField()
    description = serializers.CharField()

    buttons = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        from .models import CTASection
        model = CTASection
        fields = [
            'id', 'title', 'subtitle', 'description', 'background_image',
            'background_image_url', 'buttons', 'features', 'is_active', 'created_at', 'updated_at'
        ]

    def get_buttons(self, obj):
        buttons = obj.buttons.filter(is_active=True)
        return CTAButtonSerializer(buttons, many=True).data

    def get_features(self, obj):
        features = obj.features.filter(is_active=True)
        return CTAFeatureSerializer(features, many=True).data

    def get_background_image_url(self, obj):
        return self.get_image_url(obj, 'background_image', 'cta')


class CTAButtonSerializer(serializers.ModelSerializer):
    """Serializer for CTA Buttons"""

    text = serializers.CharField()

    class Meta:
        from .models import CTAButton
        model = CTAButton
        fields = [
            'id', 'text', 'url', 'button_type', 'order', 'is_active'
        ]


class CTAFeatureSerializer(serializers.ModelSerializer):
    """Serializer for CTA Features"""

    text = serializers.CharField()

    class Meta:
        from .models import CTAFeature
        model = CTAFeature
        fields = [
            'id', 'text', 'icon', 'order', 'is_active'
        ]


class FooterSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Serializer for Footer"""

    newsletter_title = serializers.CharField()
    newsletter_description = serializers.CharField()
    company_name = serializers.CharField()
    company_description = serializers.CharField()
    copyright_text = serializers.CharField()
    newsletter_placeholder = serializers.CharField()
    trusted_by_text = serializers.CharField()

    navigation_links = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()

    class Meta:
        from .models import Footer
        model = Footer
        fields = [
            'id', 'newsletter_title', 'newsletter_description', 'company_name',
            'company_description', 'copyright_text', 'newsletter_placeholder',
            'trusted_by_text', 'logo', 'logo_url', 'default_phone', 'default_email',
            'instagram_url', 'telegram_url', 'whatsapp_number', 'facebook_url',
            'navigation_links', 'is_active', 'created_at', 'updated_at'
        ]

    def get_navigation_links(self, obj):
        links = obj.navigation_links.filter(is_active=True)
        return FooterLinkSerializer(links, many=True).data

    def get_logo_url(self, obj):
        return self.get_image_url(obj, 'logo', 'logo')


class FooterLinkSerializer(serializers.ModelSerializer):
    """Serializer for Footer Links"""

    label = serializers.CharField()

    class Meta:
        from .models import FooterLink
        model = FooterLink
        fields = [
            'id', 'label', 'url', 'link_type', 'order', 'is_active'
        ]


class TransferBookingSectionSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Serializer for Transfer Booking Section"""

    title = serializers.CharField()
    subtitle = serializers.CharField()
    description = serializers.CharField()
    button_text = serializers.CharField()
    feature_1 = serializers.CharField()
    feature_2 = serializers.CharField()
    feature_3 = serializers.CharField()
    feature_4 = serializers.CharField()

    background_image_url = serializers.SerializerMethodField()

    class Meta:
        from .models import TransferBookingSection
        model = TransferBookingSection
        fields = [
            'id', 'title', 'subtitle', 'description', 'button_text', 'button_url',
            'background_image', 'background_image_url', 'experience_years', 'countries_served',
            'feature_1', 'feature_2', 'feature_3', 'feature_4',
            'is_active', 'created_at', 'updated_at'
        ]

    def get_background_image_url(self, obj):
        return self.get_image_url(obj, 'background_image', 'transfer')


class FAQSettingsSerializer(serializers.ModelSerializer):
    """Serializer for FAQ Settings"""

    title = serializers.CharField()
    subtitle = serializers.CharField()

    class Meta:
        from .models import FAQSettings
        model = FAQSettings
        fields = [
            'id', 'title', 'subtitle', 'items_per_page', 'show_categories',
            'show_search', 'is_active', 'created_at', 'updated_at'
        ]