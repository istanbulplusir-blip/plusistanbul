"""
URL patterns for Agents app.
"""

from django.urls import path
from . import views
from . import views_profile
from .credential_views import (
    AgentCustomerCredentialView,
    AgentCustomerVerificationView,
    AgentCustomerAuthStatusView,
    AgentCustomerOAuthLinkView
)

app_name = 'agents'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.AgentDashboardView.as_view(), name='dashboard'),
    path('dashboard/stats/', views.AgentDashboardStatsView.as_view(), name='dashboard_stats'),
    
    # Profile Management
    path('profile/', views_profile.get_agent_profile, name='profile'),
    path('profile/update/', views_profile.update_agent_profile, name='update_profile'),
    
    # Bookings
    path('bookings/', views.AgentBookingsView.as_view(), name='bookings'),
    
    # Customer Management
    path('customers/', views.AgentCustomersView.as_view(), name='customers'),
    path('customers/statistics/', views.AgentCustomerStatisticsView.as_view(), name='customer_statistics'),
    path('customers/search/', views.AgentCustomerSearchView.as_view(), name='customer_search'),
    path('customers/<uuid:customer_id>/', views.AgentCustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<uuid:customer_id>/orders/', views.AgentCustomerOrdersView.as_view(), name='customer_orders'),
    path('customers/<uuid:customer_id>/tier/', views.AgentCustomerTierUpdateView.as_view(), name='customer_tier_update'),
    path('customers/<uuid:customer_id>/status/', views.AgentCustomerStatusUpdateView.as_view(), name='customer_status_update'),
    
    # Credential Management Endpoints
    path('customers/<uuid:customer_id>/credentials/', AgentCustomerCredentialView.as_view(), name='customer_credentials'),
    path('customers/<uuid:customer_id>/verification/', AgentCustomerVerificationView.as_view(), name='customer_verification'),
    path('customers/<uuid:customer_id>/auth-status/', AgentCustomerAuthStatusView.as_view(), name='customer_auth_status'),
    path('customers/<uuid:customer_id>/oauth-link/', AgentCustomerOAuthLinkView.as_view(), name='customer_oauth_link'),
    
    # Order Management
    path('orders/', views.AgentOrdersView.as_view(), name='orders'),
    
    # Booking Services
    path('book/tour/', views.AgentBookTourView.as_view(), name='book_tour'),
    # path('book/transfer/', views.AgentBookTransferView.as_view(), name='book_transfer'),  # Removed - using unified API
    path('book/car-rental/', views.AgentBookCarRentalView.as_view(), name='book_car_rental'),
    path('book/event/', views.AgentBookEventView.as_view(), name='book_event'),
    
    # Pricing Management
    path('pricing/rules/', views.AgentPricingRulesView.as_view(), name='pricing_rules'),
    path('pricing/preview/', views.AgentPricingPreviewView.as_view(), name='pricing_preview'),
    
    # Commission Management
    path('commissions/', views.AgentCommissionListView.as_view(), name='commissions'),
    path('commissions/summary/', views.AgentCommissionSummaryView.as_view(), name='commission_summary'),
    path('commissions/monthly/', views.AgentCommissionMonthlyView.as_view(), name='commission_monthly'),
    path('commissions/<uuid:commission_id>/', views.AgentCommissionDetailView.as_view(), name='commission_detail'),
    
    # Tours Management
    path('tours/', views.AgentToursView.as_view(), name='tours'),
    path('tours/<uuid:tour_id>/', views.AgentTourDetailView.as_view(), name='tour_detail'),
    path('tours/<uuid:tour_id>/available-dates/', views.AgentTourAvailableDatesView.as_view(), name='tour_available_dates'),
    path('tours/<uuid:tour_id>/options/', views.AgentTourOptionsView.as_view(), name='tour_options'),
    
    # Transfer Management
    path('transfers/routes/', views.AgentTransferRoutesView.as_view(), name='transfer_routes'),
    path('pricing/transfer/', views.AgentTransferPricingView.as_view(), name='transfer_pricing'),
] 