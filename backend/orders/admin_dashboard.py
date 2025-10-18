"""
Admin dashboard views for order management.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Order


@staff_member_required
def order_dashboard(request):
    """Order management dashboard."""
    
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    paid_orders = Order.objects.filter(status='paid').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Orders by status (for chart)
    status_counts = Order.objects.values('status').annotate(count=Count('id'))
    
    # Revenue statistics
    total_revenue = Order.objects.filter(
        status__in=['confirmed', 'paid', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    week_revenue = Order.objects.filter(
        status__in=['confirmed', 'paid', 'completed'],
        created_at__date__gte=week_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    month_revenue = Order.objects.filter(
        status__in=['confirmed', 'paid', 'completed'],
        created_at__date__gte=month_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Orders requiring attention
    attention_orders = Order.objects.filter(
        Q(status='pending') | Q(status='confirmed', payment_status='pending')
    ).select_related('user').order_by('created_at')[:20]
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'paid_orders': paid_orders,
        'cancelled_orders': cancelled_orders,
        'recent_orders': recent_orders,
        'status_counts': status_counts,
        'total_revenue': total_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'attention_orders': attention_orders,
        'today': today,
        'week_ago': week_ago,
        'month_ago': month_ago,
    }
    
    return render(request, 'admin/orders/dashboard.html', context)
