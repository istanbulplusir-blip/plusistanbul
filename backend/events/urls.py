"""
URL patterns for Events app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    EventViewSet, EventCategoryViewSet, VenueViewSet, ArtistViewSet,
    EventReviewViewSet, EventSectionViewSet, SectionTicketTypeViewSet, EventCapacityViewSet,
    EventPricingViewSet, EventDiscountViewSet, EventFeeViewSet, EventPricingRuleViewSet,
    event_filters
)

# Main router
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'categories', EventCategoryViewSet, basename='event-category')
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'artists', ArtistViewSet, basename='artist')

# Add new URL patterns for capacity management
router.register(r'sections', EventSectionViewSet, basename='event-section')
router.register(r'section-ticket-types', SectionTicketTypeViewSet, basename='section-ticket-type')
router.register(r'capacity', EventCapacityViewSet, basename='event-capacity')

# Add new URL patterns for pricing management
router.register(r'pricing', EventPricingViewSet, basename='event-pricing')
router.register(r'discounts', EventDiscountViewSet, basename='event-discount')
router.register(r'fees', EventFeeViewSet, basename='event-fee')
router.register(r'pricing-rules', EventPricingRuleViewSet, basename='event-pricing-rule')

# Nested router for event reviews
events_router = routers.NestedDefaultRouter(router, r'events', lookup='event')
events_router.register(r'reviews', EventReviewViewSet, basename='event-reviews')

urlpatterns = [
    # Main API routes
    path('', include(router.urls)),
    
    # Nested routes
    path('', include(events_router.urls)),
    
    # Enhanced event-specific routes
    path('events/<uuid:pk>/by-slug/<slug:slug>/', 
         EventViewSet.as_view({'get': 'retrieve'}), 
         name='event-detail-by-slug'),
    
    # New enhanced API endpoints
    path('events/<uuid:pk>/performances-detailed/', 
         EventViewSet.as_view({'get': 'performances_detailed'}), 
         name='event-performances-detailed'),
    
    path('events/<uuid:pk>/calculate-pricing/', 
         EventViewSet.as_view({'post': 'calculate_pricing'}), 
         name='event-calculate-pricing'),
    
    path('events/<uuid:pk>/available-options/', 
         EventViewSet.as_view({'get': 'available_options'}), 
         name='event-available-options'),
    
    path('events/<uuid:pk>/seat-map/', 
         EventViewSet.as_view({'get': 'seat_map'}), 
         name='event-seat-map'),
    
    path('events/<uuid:pk>/availability-calendar/', 
         EventViewSet.as_view({'get': 'availability_calendar'}), 
         name='event-availability-calendar'),
    
    path('events/<uuid:pk>/reserve-seats/', 
         EventViewSet.as_view({'post': 'reserve_seats'}), 
         name='event-reserve-seats'),
    
    # Performance-specific routes
    path('performances/<uuid:pk>/capacity-summary/', 
         EventCapacityViewSet.as_view({'get': 'summary'}), 
         name='performance-capacity-summary'),
    
    path('performances/<uuid:pk>/available-seats/', 
         EventCapacityViewSet.as_view({'get': 'available_seats'}), 
         name='performance-available-seats'),
    
    # Performance seats endpoint - using EventViewSet with nested action
    path('events/<uuid:event_pk>/performances/<uuid:performance_pk>/seats/', 
         EventViewSet.as_view({'get': 'performance_seats'}), 
         name='performance-seats'),
    
    # Performance seat management endpoints
    path('performances/<uuid:performance_id>/hold/', 
         EventViewSet.as_view({'post': 'hold_seats'}), 
         name='performance-hold-seats'),
    
    path('performances/<uuid:performance_id>/release/', 
         EventViewSet.as_view({'post': 'release_seats'}), 
         name='performance-release-seats'),
    
    # Quick access routes for frontend
    path('events/<slug:slug>/quick-info/', 
         EventViewSet.as_view({'get': 'retrieve'}), 
         name='event-quick-info'),
    
    # Home page events endpoint
    path('home-events/',
         EventViewSet.as_view({'get': 'home_events'}),
         name='events-home-events'),
] 

urlpatterns += [
    path('filters/', event_filters, name='event-filters'),
] 