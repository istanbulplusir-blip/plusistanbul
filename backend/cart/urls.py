"""
URL patterns for Cart app.
"""

from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Cart management
    path('', views.CartView.as_view(), name='cart_detail'),
    path('summary/', views.CartSummaryView.as_view(), name='cart_summary'),
    path('count/', views.cart_count_view, name='cart_count'),
    path('check-capacity/', views.CheckCapacityView.as_view(), name='check_capacity'),
    
    # Cart items
    path('add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('items/<uuid:item_id>/update/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('items/<uuid:item_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item_direct'),
    path('items/<uuid:item_id>/remove/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear/', views.ClearCartView.as_view(), name='clear_cart'),
    
    # Event-specific endpoints
    path('events/seats/', views.AddEventSeatsToCartView.as_view(), name='add_event_seats_to_cart'),
    
    # Cart operations
    path('merge/', views.merge_cart_view, name='merge_cart'),
] 