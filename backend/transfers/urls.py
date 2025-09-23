"""
URL patterns for Transfers app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransferRouteViewSet, TransferBookingViewSet, TransferOptionViewSet, TransferLocationViewSet,
    TransferBookingAPIView
)

# Main router
router = DefaultRouter()
router.register(r'routes', TransferRouteViewSet, basename='transfer-route')
router.register(r'bookings', TransferBookingViewSet, basename='transfer-booking')
router.register(r'options', TransferOptionViewSet, basename='transfer-option')
router.register(r'locations', TransferLocationViewSet, basename='transfer-location')

urlpatterns = [
    # Main API routes
    path('', include(router.urls)),
    
    # Additional transfer-specific routes
    path('routes/by-slug/<slug:slug>/', 
         TransferRouteViewSet.as_view({'get': 'by_slug'}), 
         name='transfer-route-detail-by-slug'),
    
    # Public price calculation endpoint
    path('calculate-price/', 
         TransferRouteViewSet.as_view({'post': 'calculate_price_public'}), 
         name='transfer-calculate-price-public'),
    
    # Custom route price calculation endpoint
    path('calculate-custom-route-price/', 
         TransferRouteViewSet.as_view({'post': 'calculate_custom_route_price'}), 
         name='transfer-calculate-custom-route-price'),
    
    # Agent-only booking endpoint using unified booking service
    path('book/', TransferBookingAPIView.as_view(), name='transfer-book'),
] 