"""
URL patterns for Orders app.
"""

from django.urls import path
from . import views
from . import admin_dashboard

app_name = 'orders'

urlpatterns = [
    # Specific URLs first (before pattern matching)
    path('pending/', views.get_pending_orders, name='pending-orders'),
    path('summary/', views.get_order_status_summary, name='order-summary'),
    path('add/', views.AddToOrderView.as_view(), name='add-to-order'),
    path('cart/', views.CreateOrderView.as_view(), name='create-from-cart'),
    
    # Admin dashboard
    path('admin/dashboard/', admin_dashboard.order_dashboard, name='admin-dashboard'),
    
    # Pattern matching URLs last
    path('<str:order_number>/confirm/', views.ConfirmOrderView.as_view(), name='confirm-order'),
    path('<str:order_number>/cancel/', views.CancelOrderView.as_view(), name='cancel-order'),
    path('<str:order_number>/actions/cancel/', views.CancelOrderView.as_view(), name='cancel-order-action'),
    path('<str:order_number>/whatsapp/', views.OrderWhatsAppView.as_view(), name='order-whatsapp'),
    path('<str:order_number>/<str:action>/', views.OrderActionView.as_view(), name='order-action'),
    path('<str:order_number>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('', views.OrdersRootView.as_view(), name='order-list-create'),
] 