"""
URL patterns for Payments app.
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('create/', views.CreatePaymentView.as_view(), name='payment_create'),
    path('<str:payment_id>/', views.PaymentDetailView.as_view(), name='payment_detail'),
] 