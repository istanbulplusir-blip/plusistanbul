"""
URL patterns for Tours app.
"""

from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    # Test view
    path('test/', views.test_tours_view, name='test_tours'),

    # Home tours endpoint
    path('home-tours/', views.home_tours_view, name='home_tours'),

    # Categories
    path('categories/', views.TourCategoryListView.as_view(), name='category_list'),
    
    # Tours
    path('', views.TourListView.as_view(), name='tour_list'),
    path('tours/', views.TourListView.as_view(), name='tour_list_alt'),  # Alternative endpoint
    path('search/', views.TourSearchView.as_view(), name='tour_search'),
    path('<slug:slug>/', views.TourDetailView.as_view(), name='tour_detail'),
    path('<slug:slug>/availability/', views.tour_availability_view, name='tour_availability'),
    path('<slug:slug>/stats/', views.tour_stats_view, name='tour_stats'),
    
    # New booking flow endpoints
    path('<uuid:tour_id>/schedules/', views.tour_schedules_view, name='tour_schedules'),
    path('check-availability/', views.check_tour_availability_view, name='check_availability'),
    
    # Schedules
    path('<slug:tour_slug>/schedules/', views.TourScheduleListView.as_view(), name='schedule_list'),
    
    # Variants
    path('<slug:tour_slug>/variants/', views.TourVariantListView.as_view(), name='variant_list'),
    path('<slug:tour_slug>/variants/<uuid:variant_id>/', views.TourVariantDetailView.as_view(), name='variant_detail'),
    
    # Options
    path('<slug:tour_slug>/options/', views.TourOptionListView.as_view(), name='option_list'),
    path('<slug:tour_slug>/options/<uuid:option_id>/', views.TourOptionDetailView.as_view(), name='option_detail'),
    
    # Itinerary
    path('<slug:tour_slug>/itinerary/', views.TourItineraryListView.as_view(), name='itinerary_list'),
    
    # Booking Steps
    path('<slug:tour_slug>/booking-steps/', views.TourBookingStepsView.as_view(), name='booking_steps'),
    
    # Reviews
    path('<slug:tour_slug>/reviews/', views.TourReviewListView.as_view(), name='review_list'),
    path('<slug:tour_slug>/reviews/create/', views.TourReviewCreateView.as_view(), name='review_create'),
    path('<slug:tour_slug>/reviews/guest/', views.GuestReviewCreateView.as_view(), name='guest_review_create'),
    
    # Review Management
    path('reviews/<int:review_id>/edit/', views.TourReviewEditView.as_view(), name='review_edit'),
    path('reviews/<int:review_id>/delete/', views.TourReviewDeleteView.as_view(), name='review_delete'),
    path('reviews/<int:review_id>/detail/', views.TourReviewDetailView.as_view(), name='review_detail'),
    
    # Review Reporting
    path('reviews/<int:review_id>/report/', views.ReviewReportCreateView.as_view(), name='review_report'),
    path('reports/', views.ReviewReportListView.as_view(), name='report_list'),
    path('reports/<int:report_id>/', views.ReviewReportDetailView.as_view(), name='report_detail'),
    
    # Review Responses
    path('reviews/<int:review_id>/respond/', views.ReviewResponseCreateView.as_view(), name='review_respond'),
    path('responses/<int:response_id>/edit/', views.ReviewResponseUpdateView.as_view(), name='response_edit'),
    path('responses/<int:response_id>/delete/', views.ReviewResponseDeleteView.as_view(), name='response_delete'),
    
    # Review Management Dashboard
    path('reviews/dashboard/', views.ReviewManagementDashboardView.as_view(), name='review_dashboard'),
    
    # Purchase Check for Reviews
    path('<slug:tour_slug>/purchase-check/', views.TourPurchaseCheckView.as_view(), name='tour_purchase_check'),

    # User pending orders for duplicate booking prevention
    path('<slug:tour_slug>/user-pending-orders/', views.UserPendingOrdersView.as_view(), name='user_pending_orders'),

    # Booking
    path('booking/', views.TourBookingView.as_view(), name='tour_booking'),
] 