"""
Shared views for Peykan Tourism Platform.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from django.db.models import Q

from .models import (
    FAQ, FAQCategory, StaticPage, ContactInfo, ContactMessage, SupportFAQ,
    HeroSlider, Banner, SiteSettings, ImageOptimization,
    AboutSection, AboutStatistic, AboutFeature,
    CTASection, CTAButton, CTAFeature,
    Footer, FooterLink,
    TransferBookingSection,
    FAQSettings
)
from .whatsapp_service import CentralizedWhatsAppService

from .serializers import (
    FAQSerializer, FAQListSerializer,
    StaticPageSerializer, StaticPageListSerializer,
    ContactInfoSerializer,
    ContactMessageSerializer, ContactMessageCreateSerializer, ContactMessageListSerializer,
    HeroSliderSerializer, BannerSerializer, SiteSettingsSerializer, ImageOptimizationSerializer,
    AboutSectionSerializer, AboutStatisticSerializer, AboutFeatureSerializer,
    CTASectionSerializer, CTAButtonSerializer, CTAFeatureSerializer,
    FooterSerializer, FooterLinkSerializer,
    TransferBookingSectionSerializer,
    FAQSettingsSerializer
)


def get_faq_queryset():
    """Get FAQ queryset to avoid circular imports."""
    from .models import FAQ
    return FAQ.objects.filter(is_active=True)


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for FAQ model.
    Read-only for public access.
    """
    
    def get_queryset(self):
        """Get FAQ queryset."""
        return get_faq_queryset()
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    ordering_fields = ['order', 'created_at']
    ordering = ['order', 'created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return FAQListSerializer
        return FAQSerializer
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get list of available FAQ categories."""
        from .models import FAQ
        categories = FAQ.objects.filter(
            is_active=True
        ).values_list('category', flat=True).distinct()
        
        return Response({
            'categories': [cat for cat in categories if cat]
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get FAQs filtered by category."""
        from .models import FAQ
        # Get all active FAQs first
        all_faqs = FAQ.objects.filter(is_active=True)
        
        # Try to get category from query params
        category = request.GET.get('category', '')
        
        if category:
            faqs = all_faqs.filter(category=category)
        else:
            faqs = all_faqs
        
        serializer = self.get_serializer(faqs, many=True)
        return Response(serializer.data)


def get_static_page_queryset():
    """Get StaticPage queryset to avoid circular imports."""
    from .models import StaticPage
    return StaticPage.objects.filter(is_active=True)


def get_contact_info_queryset():
    """Get ContactInfo queryset to avoid circular imports."""
    from .models import ContactInfo
    return ContactInfo.objects.filter(is_active=True)


def get_contact_message_queryset():
    """Get ContactMessage queryset to avoid circular imports."""
    from .models import ContactMessage
    return ContactMessage.objects.all()


class StaticPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for StaticPage model.
    Read-only for public access.
    """
    
    def get_queryset(self):
        """Get StaticPage queryset."""
        return get_static_page_queryset()
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['page_type', 'is_active']
    ordering_fields = ['page_type', 'created_at']
    ordering = ['page_type']
    lookup_field = 'page_type'  # Allow lookup by page_type instead of ID
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return StaticPageListSerializer
        return StaticPageSerializer
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get specific page by type."""
        page_type = request.GET.get('type', '')
        if not page_type:
            return Response(
                {'error': 'Page type is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            page = self.get_queryset().get(page_type=page_type)
            serializer = StaticPageSerializer(page, context={'request': request})
            return Response(serializer.data)
        except self.get_queryset().model.DoesNotExist:
            return Response(
                {'error': 'Page not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ContactInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ContactInfo model.
    Read-only for public access.
    """
    
    def get_queryset(self):
        """Get ContactInfo queryset."""
        return get_contact_info_queryset()
    
    permission_classes = [permissions.AllowAny]
    serializer_class = ContactInfoSerializer
    
    def list(self, request, *args, **kwargs):
        """Return the first active contact info."""
        contact_info = self.get_queryset().first()
        if contact_info:
            serializer = self.get_serializer(contact_info)
            return Response(serializer.data)
        return Response({})


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ContactMessage model.
    Public can create, admin can manage.
    """
    
    def get_queryset(self):
        """Get ContactMessage queryset."""
        return get_contact_message_queryset()
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'priority']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'create':
            # Anyone can create a contact message
            permission_classes = [permissions.AllowAny]
        else:
            # Only staff can view/manage messages
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ContactMessageCreateSerializer
        elif self.action == 'list':
            return ContactMessageListSerializer
        return ContactMessageSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new contact message."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': 'Your message has been sent successfully. We will get back to you soon.',
                'id': serializer.instance.id
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def mark_as_read(self, request, pk=None):
        """Mark message as read."""
        message = self.get_object()
        if message.status == 'new':
            message.status = 'read'
            message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def reply(self, request, pk=None):
        """Reply to a contact message."""
        message = self.get_object()
        admin_response = request.data.get('admin_response', '')
        
        if not admin_response:
            return Response(
                {'error': 'Admin response is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message.admin_response = admin_response
        message.status = 'replied'
        message.responded_at = timezone.now()
        message.responded_by = request.user
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request):
        """Get contact message statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'new': queryset.filter(status='new').count(),
            'read': queryset.filter(status='read').count(),
            'replied': queryset.filter(status='replied').count(),
            'closed': queryset.filter(status='closed').count(),
            'high_priority': queryset.filter(priority='high').count(),
            'urgent': queryset.filter(priority='urgent').count(),
        }
        
        return Response(stats)


class SupportFAQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SupportFAQ model.
    Read-only for public access.
    """
    
    def get_queryset(self):
        """Get SupportFAQ queryset."""
        from .models import SupportFAQ
        return SupportFAQ.objects.filter(is_active=True)
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    ordering_fields = ['order', 'created_at']
    ordering = ['category', 'order', 'created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        from .serializers import SupportFAQSerializer
        return SupportFAQSerializer
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get support FAQs filtered by category."""
        category = request.GET.get('category', '')
        
        if category:
            queryset = self.get_queryset().filter(category=category)
        else:
            queryset = self.get_queryset()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get list of available support FAQ categories."""
        from .models import SupportFAQ
        categories = SupportFAQ.objects.filter(
            is_active=True
        ).values_list('category', flat=True).distinct()

        return Response({
            'categories': [cat for cat in categories if cat]
        })


class HeroSliderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HeroSlider model.
    Full CRUD operations for admin, read-only for public.
    """

    def get_queryset(self):
        """Get HeroSlider queryset."""
        from .models import HeroSlider
        queryset = HeroSlider.objects.filter(is_active=True)

        # Filter by active slides only for public access
        if self.request.user.is_authenticated and self.request.user.is_staff:
            # Admin can see all slides
            pass
        else:
            # Public can only see currently active slides
            now = timezone.now()
            queryset = queryset.filter(
                Q(start_date__isnull=True) | Q(start_date__lte=now),
                Q(end_date__isnull=True) | Q(end_date__gte=now)
            )

        return queryset.order_by('order', 'created_at')

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    serializer_class = HeroSliderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active', 'show_for_authenticated', 'show_for_anonymous']
    ordering_fields = ['order', 'created_at', 'view_count']
    ordering = ['order', 'created_at']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only currently active hero slides."""
        from .models import HeroSlider
        now = timezone.now()

        queryset = HeroSlider.objects.filter(
            is_active=True
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('order', '-created_at')

        # Check user authentication status
        is_authenticated = request.user.is_authenticated
        if is_authenticated:
            queryset = queryset.filter(show_for_authenticated=True)
        else:
            queryset = queryset.filter(show_for_anonymous=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def track_click(self, request, pk=None):
        """Track click on hero slide."""
        from .models import HeroSlider
        try:
            slide = self.get_object()
            slide.click_count += 1
            slide.save(update_fields=['click_count'])
            return Response({'success': True, 'click_count': slide.click_count})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """Track view on hero slide."""
        from .models import HeroSlider
        try:
            slide = self.get_object()
            slide.view_count += 1
            slide.save(update_fields=['view_count'])
            return Response({'success': True, 'view_count': slide.view_count})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class BannerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Banner model.
    Full CRUD operations for admin, read-only for public.
    """

    def get_queryset(self):
        """Get Banner queryset."""
        from .models import Banner
        queryset = Banner.objects.filter(is_active=True)

        # Filter by active banners only for public access
        if self.request.user.is_authenticated and self.request.user.is_staff:
            # Admin can see all banners
            pass
        else:
            # Public can only see currently active banners
            now = timezone.now()
            queryset = queryset.filter(
                Q(start_date__isnull=True) | Q(start_date__lte=now),
                Q(end_date__isnull=True) | Q(end_date__gte=now)
            )

        return queryset.order_by('display_order', 'created_at')

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    serializer_class = BannerSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['banner_type', 'position', 'is_active', 'show_for_authenticated', 'show_for_anonymous']
    ordering_fields = ['display_order', 'created_at', 'view_count']
    ordering = ['display_order', 'created_at']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only currently active banners."""
        from .models import Banner
        now = timezone.now()

        queryset = Banner.objects.filter(
            is_active=True
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('display_order', 'created_at')

        # Check user authentication status
        is_authenticated = request.user.is_authenticated
        if is_authenticated:
            queryset = queryset.filter(show_for_authenticated=True)
        else:
            queryset = queryset.filter(show_for_anonymous=True)

        # Filter by page if specified
        page_url = request.query_params.get('page')
        if page_url:
            # Check if banner should be shown on this page
            page_banners = []
            for banner in queryset:
                show_on_pages = banner.show_on_pages or []
                if not show_on_pages or any(page_url.startswith(pattern) for pattern in show_on_pages):
                    page_banners.append(banner)
            queryset = page_banners

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def track_click(self, request, pk=None):
        """Track click on banner."""
        from .models import Banner
        try:
            banner = self.get_object()
            banner.click_count += 1
            banner.save(update_fields=['click_count'])
            return Response({'success': True, 'click_count': banner.click_count})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """Track view on banner."""
        from .models import Banner
        try:
            banner = self.get_object()
            banner.view_count += 1
            banner.save(update_fields=['view_count'])
            return Response({'success': True, 'view_count': banner.view_count})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class SiteSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SiteSettings model.
    Singleton pattern - only one instance allowed.
    """

    def get_queryset(self):
        """Get SiteSettings queryset."""
        from .models import SiteSettings
        return SiteSettings.objects.all()

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    serializer_class = SiteSettingsSerializer

    def list(self, request, *args, **kwargs):
        """Return the single site settings instance."""
        from .models import SiteSettings
        settings = SiteSettings.get_settings()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve the single site settings instance."""
        from .models import SiteSettings
        settings = SiteSettings.get_settings()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update the single site settings instance."""
        from .models import SiteSettings
        settings = SiteSettings.get_settings()

        # Update fields
        for field, value in request.data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)

        settings.save()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)


class ImageOptimizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ImageOptimization model.
    """

    def get_queryset(self):
        """Get ImageOptimization queryset."""
        from .models import ImageOptimization
        return ImageOptimization.objects.all()

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    serializer_class = ImageOptimizationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['image_type', 'optimization_completed']
    ordering_fields = ['created_at', 'original_size']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def optimize(self, request, pk=None):
        """Trigger image optimization for this image."""
        from .models import ImageOptimization
        try:
            image_opt = self.get_object()

            # Here you would implement the actual image optimization logic
            # For now, just mark as completed
            image_opt.optimization_completed = True
            image_opt.save()

            return Response({
                'success': True,
                'message': 'Image optimization completed',
                'compression_ratio': image_opt.compression_ratio
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def bulk_optimize(self, request):
        """Bulk optimize images."""
        from .models import ImageOptimization
        image_type = request.data.get('image_type')
        queryset = self.get_queryset()

        if image_type:
            queryset = queryset.filter(image_type=image_type)

        # Optimize images that are not yet optimized
        unoptimized = queryset.filter(optimization_completed=False)
        count = unoptimized.count()

        # Here you would implement bulk optimization logic
        # For now, just mark them as completed
        unoptimized.update(optimization_completed=True)

        return Response({
            'success': True,
            'message': f'Optimized {count} images',
            'optimized_count': count
        })


class AboutSectionViewSet(viewsets.ModelViewSet):
    """ViewSet for About Section management"""
    queryset = AboutSection.objects.filter(is_active=True)
    serializer_class = AboutSectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return AboutSection.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active about section."""
        try:
            section = AboutSection.objects.filter(is_active=True).first()
            if section:
                serializer = self.get_serializer(section)
                return Response(serializer.data)
            return Response({'message': 'No active about section found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AboutStatisticViewSet(viewsets.ModelViewSet):
    """ViewSet for About Statistics management"""
    queryset = AboutStatistic.objects.filter(is_active=True)
    serializer_class = AboutStatisticSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return AboutStatistic.objects.filter(is_active=True).order_by('order')


class AboutFeatureViewSet(viewsets.ModelViewSet):
    """ViewSet for About Features management"""
    queryset = AboutFeature.objects.filter(is_active=True)
    serializer_class = AboutFeatureSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return AboutFeature.objects.filter(is_active=True).order_by('order')


class CTASectionViewSet(viewsets.ModelViewSet):
    """ViewSet for CTA Section management"""
    queryset = CTASection.objects.filter(is_active=True)
    serializer_class = CTASectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CTASection.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active CTA section with buttons and features."""
        try:
            section = CTASection.objects.filter(is_active=True).first()
            if section:
                serializer = self.get_serializer(section)
                return Response(serializer.data)
            return Response({'message': 'No active CTA section found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTAButtonViewSet(viewsets.ModelViewSet):
    """ViewSet for CTA Buttons management"""
    queryset = CTAButton.objects.filter(is_active=True)
    serializer_class = CTAButtonSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CTAButton.objects.filter(is_active=True).order_by('order')


class CTAFeatureViewSet(viewsets.ModelViewSet):
    """ViewSet for CTA Features management"""
    queryset = CTAFeature.objects.filter(is_active=True)
    serializer_class = CTAFeatureSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CTAFeature.objects.filter(is_active=True).order_by('order')


class FooterViewSet(viewsets.ModelViewSet):
    """ViewSet for Footer management"""
    queryset = Footer.objects.filter(is_active=True)
    serializer_class = FooterSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Footer.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active footer."""
        try:
            footer = Footer.objects.filter(is_active=True).first()
            if footer:
                serializer = self.get_serializer(footer)
                return Response(serializer.data)
            return Response({'message': 'No active footer found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FooterLinkViewSet(viewsets.ModelViewSet):
    """ViewSet for Footer Links management"""
    queryset = FooterLink.objects.filter(is_active=True)
    serializer_class = FooterLinkSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return FooterLink.objects.filter(is_active=True).order_by('order')


class TransferBookingSectionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transfer Booking Section management"""
    queryset = TransferBookingSection.objects.filter(is_active=True)
    serializer_class = TransferBookingSectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return TransferBookingSection.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active transfer booking section."""
        try:
            section = TransferBookingSection.objects.filter(is_active=True).first()
            if section:
                serializer = self.get_serializer(section)
                return Response(serializer.data)
            return Response({'message': 'No active transfer booking section found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FAQSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for FAQ Settings management"""
    queryset = FAQSettings.objects.filter(is_active=True)
    serializer_class = FAQSettingsSerializer
    permission_classes = [permissions.AllowAny]


class WhatsAppInfoViewSet(viewsets.ViewSet):
    """ViewSet for WhatsApp information"""
    permission_classes = [permissions.AllowAny]
    
    def list(self, request):
        """Get WhatsApp information from centralized service."""
        try:
            support_info = CentralizedWhatsAppService.get_support_info()
            return Response(support_info)
        except Exception as e:
            return Response(
                {'error': f'Failed to get WhatsApp info: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        return FAQSettings.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active FAQ settings."""
        try:
            settings = FAQSettings.objects.filter(is_active=True).first()
            if settings:
                serializer = self.get_serializer(settings)
                return Response(serializer.data)
            return Response({'message': 'No active FAQ settings found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
