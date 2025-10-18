"""
URL patterns for Car Rentals app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    CarRentalViewSet, CarRentalCategoryViewSet, CarRentalLocationViewSet, 
    CarRentalOptionViewSet, CarRentalBookingViewSet, car_rental_filters,
    check_car_rental_availability
)

# Main router
router = DefaultRouter()
router.register(r'car-rentals', CarRentalViewSet, basename='car-rental')
router.register(r'categories', CarRentalCategoryViewSet, basename='car-rental-category')
router.register(r'locations', CarRentalLocationViewSet, basename='car-rental-location')
router.register(r'options', CarRentalOptionViewSet, basename='car-rental-option')
router.register(r'bookings', CarRentalBookingViewSet, basename='car-rental-booking')

# Nested router for car rental specific endpoints
car_rentals_router = routers.NestedDefaultRouter(router, r'car-rentals', lookup='car_rental')
# Note: CarRentalAvailabilityViewSet would need to be created if needed

urlpatterns = [
    # Main API routes
    path('', include(router.urls)),
    
    # Nested routes
    path('', include(car_rentals_router.urls)),
    
    # Enhanced car rental specific routes
    path('car-rentals/<uuid:pk>/by-slug/<slug:slug>/', 
         CarRentalViewSet.as_view({'get': 'retrieve'}), 
         name='car-rental-detail-by-slug'),
    
    # Search and filtering endpoints
    path('car-rentals/search/', 
         CarRentalViewSet.as_view({'post': 'search'}), 
         name='car-rental-search'),
    
    path('car-rentals/featured/', 
         CarRentalViewSet.as_view({'get': 'featured'}), 
         name='car-rental-featured'),
    
    path('car-rentals/popular/', 
         CarRentalViewSet.as_view({'get': 'popular'}), 
         name='car-rental-popular'),
    
    # Availability and booking endpoints
    path('car-rentals/<slug:slug>/check-availability/', 
         check_car_rental_availability, 
         name='car-rental-check-availability'),
    
    path('car-rentals/<uuid:pk>/availability-calendar/', 
         CarRentalViewSet.as_view({'get': 'availability_calendar'}), 
         name='car-rental-availability-calendar'),
    
    path('car-rentals/<uuid:pk>/options/', 
         CarRentalViewSet.as_view({'get': 'options'}), 
         name='car-rental-options'),
    
    # Filter options endpoint
    path('filters/', car_rental_filters, name='car-rental-filters'),
    
    # Quick access routes for frontend
    path('<slug:slug>/', 
         CarRentalViewSet.as_view({'get': 'retrieve'}), 
         name='car-rental-detail'),
    
    path('car-rentals/<slug:slug>/quick-info/', 
         CarRentalViewSet.as_view({'get': 'quick_info'}), 
         name='car-rental-quick-info'),
    
    # Home page car rentals endpoint
    path('home-car-rentals/',
         CarRentalViewSet.as_view({'get': 'featured'}),
         name='car-rentals-home-featured'),
]
