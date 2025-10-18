"""
URL patterns for Shared app.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

app_name = 'shared'

# Create router for ViewSets - using SimpleRouter to avoid trailing slash issues
router = SimpleRouter()
router.register(r'faqs', views.FAQViewSet, basename='faq')
router.register(r'pages', views.StaticPageViewSet, basename='staticpage')
router.register(r'contact-info', views.ContactInfoViewSet, basename='contactinfo')
router.register(r'contact-messages', views.ContactMessageViewSet, basename='contactmessage')
router.register(r'support-faqs', views.SupportFAQViewSet, basename='supportfaq')
router.register(r'hero-slides', views.HeroSliderViewSet, basename='heroslider')
router.register(r'banners', views.BannerViewSet, basename='banner')
router.register(r'site-settings', views.SiteSettingsViewSet, basename='sitesettings')
router.register(r'image-optimization', views.ImageOptimizationViewSet, basename='imageoptimization')

# New homepage section routers
router.register(r'about-section', views.AboutSectionViewSet, basename='aboutsection')
router.register(r'about-statistics', views.AboutStatisticViewSet, basename='aboutstatistic')
router.register(r'about-features', views.AboutFeatureViewSet, basename='aboutfeature')
router.register(r'cta-section', views.CTASectionViewSet, basename='ctasection')
router.register(r'cta-buttons', views.CTAButtonViewSet, basename='ctabutton')
router.register(r'cta-features', views.CTAFeatureViewSet, basename='ctafeature')
router.register(r'footer', views.FooterViewSet, basename='footer')
router.register(r'footer-links', views.FooterLinkViewSet, basename='footerlink')
router.register(r'transfer-booking-section', views.TransferBookingSectionViewSet, basename='transferbookingsection')
router.register(r'faq-settings', views.FAQSettingsViewSet, basename='faqsettings')
router.register(r'whatsapp-info', views.WhatsAppInfoViewSet, basename='whatsappinfo')
router.register(r'navigation-menu', views.NavigationMenuViewSet, basename='navigationmenu')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
