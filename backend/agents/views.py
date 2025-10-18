"""
DRF Views for Agents app.
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
import os
from django.conf import settings

from .models import Agent, AgentCommission, AgentProfile, AgentPricingRule, AgentCustomer
from .serializers import AgentSerializer, AgentSummarySerializer
from .services import AgentBookingService
from .pricing_service import AgentPricingService
from .commission_service import AgentCommissionService
from .customer_service import AgentCustomerService


def get_safe_image_url(image_field):
    """Safely get image URL, returning default if image doesn't exist"""
    if not image_field:
        return '/media/defaults/no-image.png'
    
    try:
        # Check if the file actually exists
        if hasattr(image_field, 'url'):
            image_path = os.path.join(settings.MEDIA_ROOT, image_field.name)
            if os.path.exists(image_path):
                return image_field.url
    except (ValueError, AttributeError):
        pass
    
    return '/media/defaults/no-image.png'


class AgentDashboardView(APIView):
    """داشبورد ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        # دریافت آمار ایجنت
        from .models import AgentService
        summary = AgentService.get_agent_summary(request.user)
        
        return Response({
            'agent': {
                'id': str(request.user.id),
                'username': request.user.username,
                'email': request.user.email,
                'agent_code': request.user.agent_code,
                'commission_rate': float(request.user.commission_rate)
            },
            'summary': summary
        })


class AgentDashboardStatsView(APIView):
    """آمار داشبورد ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        # دریافت آمار واقعی از دیتابیس
        from django.db.models import Count, Sum, Avg
        from orders.models import Order
        from agents.models import AgentCommission, AgentCustomer
        
        # آمار مشتریان
        total_customers = AgentCustomer.objects.filter(agent=request.user).count()
        active_customers = AgentCustomer.objects.filter(
            agent=request.user, 
            customer_status='active'
        ).count()
        
        # آمار سفارشات
        total_orders = Order.objects.filter(agent=request.user).count()
        confirmed_orders = Order.objects.filter(
            agent=request.user, 
            status='confirmed'
        ).count()
        
        # آمار کمیسیون
        total_commission = AgentCommission.objects.filter(
            agent=request.user
        ).aggregate(total=Sum('commission_amount'))['total'] or 0
        
        # نرخ تبدیل (درصد سفارشات تایید شده)
        conversion_rate = (confirmed_orders / total_orders * 100) if total_orders > 0 else 0
        
        # آمار ماهانه فروش (آخرین 6 ماه)
        from django.utils import timezone
        from datetime import timedelta
        import calendar
        
        monthly_sales = []
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])
            
            month_orders = Order.objects.filter(
                agent=request.user,
                created_at__gte=month_start,
                created_at__lte=month_end,
                status='confirmed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            monthly_sales.append({
                'month': month_start.strftime('%Y-%m'),
                'amount': float(month_orders)
            })
        
        monthly_sales.reverse()  # مرتب کردن از قدیمی به جدید
        
        # محصولات برتر
        from orders.models import OrderItem
        top_products = OrderItem.objects.filter(
            order__agent=request.user,
            order__status='confirmed'
        ).values('product_type').annotate(
            bookings=Count('id'),
            revenue=Sum('total_price')
        ).order_by('-revenue')[:5]
        
        top_products_list = []
        for product in top_products:
            top_products_list.append({
                'name': product['product_type'].replace('_', ' ').title(),
                'bookings': product['bookings'],
                'revenue': float(product['revenue'] or 0)
            })
        
        # فعالیت‌های اخیر
        recent_activities = []
        
        # آخرین سفارشات
        recent_orders = Order.objects.filter(
            agent=request.user
        ).order_by('-created_at')[:3]
        
        for order in recent_orders:
            recent_activities.append({
                'type': 'order',
                'description': f'سفارش جدید {order.order_number} برای {order.customer_name}',
                'created_at': order.created_at.isoformat()
            })
        
        # آخرین کمیسیون‌ها
        recent_commissions = AgentCommission.objects.filter(
            agent=request.user
        ).order_by('-created_at')[:2]
        
        for commission in recent_commissions:
            recent_activities.append({
                'type': 'commission',
                'description': f'کمیسیون ${commission.commission_amount} برای سفارش {commission.order.order_number}',
                'created_at': commission.created_at.isoformat()
            })
        
        # مرتب کردن بر اساس تاریخ
        recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
        recent_activities = recent_activities[:5]
        
        stats = {
            'total_commission': float(total_commission),
            'total_orders': total_orders,
            'total_customers': total_customers,
            'active_customers': active_customers,
            'conversion_rate': round(conversion_rate, 1),
            'monthly_sales': monthly_sales,
            'top_products': top_products_list,
            'recent_activities': recent_activities
        }
        
        return Response(stats)


class AgentBookingsView(APIView):
    """لیست رزروهای ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        # لیست رزروهای اخیر
        bookings = [
            {
                'id': '1',
                'type': 'tour',
                'title': 'تور باغ‌های ایرانی',
                'customer': 'احمد محمدی',
                'date': '2024-01-15',
                'status': 'confirmed',
                'commission': 125.50
            },
            {
                'id': '2',
                'type': 'transfer',
                'title': 'ترانسفر فرودگاه',
                'customer': 'فاطمه احمدی',
                'date': '2024-01-14',
                'status': 'pending',
                'commission': 45.00
            }
        ]
        
        return Response(bookings)


class AgentCustomersView(APIView):
    """مدیریت مشتریان ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """دریافت لیست مشتریان"""
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        # دریافت پارامترهای فیلتر
        filters = {
            'status': request.GET.get('status'),
            'tier': request.GET.get('tier'),
            'search': request.GET.get('search'),
            'created_after': request.GET.get('created_after'),
            'created_before': request.GET.get('created_before')
        }
        
        # حذف فیلترهای خالی
        filters = {k: v for k, v in filters.items() if v}
        
        customers = AgentCustomerService.get_agent_customers(request.user, filters)
        
        # تبدیل به لیست
        customer_list = []
        for agent_customer in customers:
            customer_list.append({
                'id': str(agent_customer.customer.id),
                'agent_customer_id': str(agent_customer.id),
                'name': agent_customer.customer_name,
                'email': agent_customer.customer_email,
                'phone': agent_customer.customer_phone,
                'address': agent_customer.customer_address,
                'city': agent_customer.customer_city,
                'country': agent_customer.customer_country,
                'birth_date': agent_customer.customer_birth_date.isoformat() if agent_customer.customer_birth_date else None,
                'gender': agent_customer.customer_gender,
                'preferred_language': agent_customer.preferred_language,
                'preferred_contact_method': agent_customer.preferred_contact_method,
                'status': agent_customer.customer_status,
                'status_display': agent_customer.get_customer_status_display(),
                'tier': agent_customer.customer_tier,
                'tier_display': agent_customer.get_customer_tier_display(),
                'total_orders': agent_customer.total_orders,
                'total_spent': float(agent_customer.total_spent),
                'last_order_date': agent_customer.last_order_date.isoformat() if agent_customer.last_order_date else None,
                'created_at': agent_customer.created_at.isoformat(),
                'is_active': agent_customer.is_active,
                'created_by_agent': agent_customer.created_by_agent
            })
        
        return Response({
            'customers': customer_list,
            'total_count': len(customer_list)
        })
    
    def post(self, request):
        """ایجاد مشتری جدید"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        customer_data = request.data
        required_fields = ['email', 'first_name', 'last_name']
        
        for field in required_fields:
            if not customer_data.get(field):
                return Response(
                    {'error': f'{field} is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            customer, agent_customer = AgentCustomerService.create_customer_for_agent(
                request.user, customer_data
            )
            
            return Response({
                'success': True,
                'data': {
                    'customer': {
                        'id': str(customer.id),
                        'name': agent_customer.customer_name,
                        'email': customer.email,
                        'phone': customer.phone_number,
                        'status': agent_customer.customer_status,
                        'tier': agent_customer.customer_tier,
                        'created_at': customer.created_at.isoformat() if hasattr(customer, 'created_at') else None
                    }
                },
                'message': 'مشتری با موفقیت ایجاد شد'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentOrdersView(APIView):
    """مدیریت سفارشات ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """دریافت لیست سفارشات"""
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        status_filter = request.GET.get('status')
        orders = AgentBookingService.get_agent_orders(request.user, status_filter)
        
        return Response({'orders': orders})


class AgentBookTourView(APIView):
    """ثبت تور برای مشتری"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        tour_data = request.data
        
        required_fields = ['customer_id', 'tour_id', 'variant_id', 'schedule_id', 'booking_date', 'booking_time', 'participants']
        
        for field in required_fields:
            if not tour_data.get(field):
                return Response(
                    {'error': f'{field} is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Add payment method to tour_data
        tour_data['payment_method'] = tour_data.get('payment_method', 'whatsapp')
        
        try:
            # Find customer by customer user ID
            customer_id = tour_data['customer_id']
            customer = request.user.agent_customers.filter(customer__id=customer_id).first()
            if not customer:
                return Response(
                    {'error': 'Customer not found or not associated with this agent'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            result = AgentBookingService.book_tour_for_customer(
                request.user, customer.customer, tour_data
            )
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentTransferPricingView(APIView):
    """Calculate transfer pricing for agents"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        from transfers.models import TransferRoute
        
        try:
            data = request.data
            required_fields = ['route_id', 'vehicle_type', 'passenger_count']
            
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get route
            route = TransferRoute.objects.get(id=data['route_id'], is_active=True)
            
            # Parse booking time
            booking_time = data.get('booking_time')
            if isinstance(booking_time, str):
                from datetime import datetime
                try:
                    booking_time = datetime.strptime(booking_time, '%H:%M').time()
                except ValueError:
                    return Response(
                        {'error': 'Invalid booking_time format. Use HH:MM'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Parse return time if provided
            return_time = data.get('return_time')
            if return_time and isinstance(return_time, str):
                try:
                    return_time = datetime.strptime(return_time, '%H:%M').time()
                except ValueError:
                    return Response(
                        {'error': 'Invalid return_time format. Use HH:MM'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Calculate pricing using agent pricing service
            from .pricing_service import AgentPricingService
            pricing_result = AgentPricingService.calculate_transfer_price_for_agent(
                route=route,
                vehicle_type=data['vehicle_type'],
                agent=request.user,
                passenger_count=data['passenger_count'],
                trip_type=data.get('trip_type', 'one_way'),
                hour=booking_time.hour if booking_time else None,
                return_hour=return_time.hour if return_time else None,
                selected_options=data.get('selected_options', [])
            )
            
            return Response({
                'success': True,
                'pricing': pricing_result
            })
            
        except TransferRoute.DoesNotExist:
            return Response(
                {'error': 'Transfer route not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


# AgentBookTransferView removed - now using unified TransferBookingAPIView in transfers app


class AgentBookCarRentalView(APIView):
    """ثبت اجاره ماشین برای مشتری"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        car_data = request.data
        required_fields = ['customer_id', 'car_id', 'pickup_date', 'pickup_time', 'dropoff_date', 'dropoff_time', 'days']
        
        for field in required_fields:
            if not car_data.get(field):
                return Response(
                    {'error': f'{field} is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # پیدا کردن مشتری
            customer_id = car_data['customer_id']
            customer = request.user.agent_customers.filter(customer__id=customer_id).first()
            if not customer:
                return Response(
                    {'error': 'Customer not found or not associated with this agent'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            result = AgentBookingService.book_car_rental_for_customer(
                request.user, customer.customer, car_data
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentBookEventView(APIView):
    """ثبت رویداد برای مشتری"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        event_data = request.data
        required_fields = ['customer_id', 'event_id', 'performance_id', 'section', 'ticket_type_id', 'quantity']
        
        for field in required_fields:
            if not event_data.get(field):
                return Response(
                    {'error': f'{field} is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # پیدا کردن مشتری
            customer_id = event_data['customer_id']
            customer = request.user.agent_customers.filter(customer__id=customer_id).first()
            if not customer:
                return Response(
                    {'error': 'Customer not found or not associated with this agent'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            result = AgentBookingService.book_event_for_customer(
                request.user, customer.customer, event_data
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentTransferRoutesView(APIView):
    """دریافت لیست مسیرهای ترانسفر برای ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from transfers.models import TransferRoute, TransferRoutePricing
            
            routes = TransferRoute.objects.filter(is_active=True)
            routes_data = []
            
            for route in routes:
                # Get pricing for this route
                pricing_options = TransferRoutePricing.objects.filter(route=route, is_active=True)
                vehicle_types = []
                
                for pricing in pricing_options:
                    vehicle_types.append({
                        'id': pricing.id,
                        'type': pricing.vehicle_type,
                        'name': pricing.vehicle_name,
                        'description': pricing.vehicle_description or f'{pricing.max_passengers} passengers, {pricing.max_luggage} luggage',
                        'base_price': float(pricing.base_price),
                        'capacity': pricing.max_passengers,
                        'max_passengers': pricing.max_passengers,
                        'max_luggage': pricing.max_luggage,
                        'features': pricing.features or [],
                        'amenities': pricing.amenities or [],
                        'currency': pricing.currency
                    })
                
                # Get options for this route (same as customer API)
                from transfers.models import TransferOption
                from django.db.models import Q
                route_options = TransferOption.objects.filter(
                    Q(route=route, is_active=True) | Q(route__isnull=True, is_active=True)
                )
                options_data = []
                for option in route_options:
                    try:
                        # Handle translation errors gracefully
                        name = getattr(option, 'name', None) or f"Option {option.id}"
                        description = getattr(option, 'description', None) or ""
                        
                        options_data.append({
                            'id': str(option.id),
                            'name': name,
                            'description': description,
                            'price': float(option.price),
                            'option_type': option.option_type,
                            'price_type': option.price_type,
                            'max_quantity': option.max_quantity,
                            'is_active': option.is_active
                        })
                    except Exception as e:
                        # Skip options with errors
                        continue
                
                routes_data.append({
                    'id': str(route.id),
                    'name': route.origin + ' -> ' + route.destination,  # Use non-translatable fields
                    'origin': route.origin,
                    'destination': route.destination,
                    'estimated_duration': route.estimated_duration_minutes,
                    'pricing': vehicle_types,  # Use same structure as customer API
                    'vehicle_types': vehicle_types,  # Keep for backward compatibility
                    'options': options_data,  # Add options like customer API
                    'round_trip_discount_enabled': route.round_trip_discount_enabled,
                    'round_trip_discount_percentage': float(route.round_trip_discount_percentage),
                    'peak_hour_surcharge': float(route.peak_hour_surcharge),
                    'midnight_surcharge': float(route.midnight_surcharge),
                    'is_active': route.is_active
                })
            
            return Response({
                'success': True,
                'routes': routes_data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentPricingRulesView(APIView):
    """مدیریت قوانین قیمت‌گذاری ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """دریافت قوانین قیمت‌گذاری"""
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        rules = AgentPricingRule.objects.filter(agent=request.user, is_active=True)
        
        rules_data = []
        for rule in rules:
            rules_data.append({
                'id': str(rule.id),
                'product_type': rule.product_type,
                'product_type_display': rule.get_product_type_display(),
                'pricing_method': rule.pricing_method,
                'pricing_method_display': rule.get_pricing_method_display(),
                'discount_percentage': float(rule.discount_percentage) if rule.discount_percentage else None,
                'fixed_price': float(rule.fixed_price) if rule.fixed_price else None,
                'markup_percentage': float(rule.markup_percentage) if rule.markup_percentage else None,
                'custom_factor': float(rule.custom_factor) if rule.custom_factor else None,
                'min_price': float(rule.min_price) if rule.min_price else None,
                'max_price': float(rule.max_price) if rule.max_price else None,
                'description': rule.description,
                'priority': rule.priority,
                'created_at': rule.created_at.isoformat()
            })
        
        # خلاصه قوانین
        summary = AgentPricingService.get_agent_pricing_summary(request.user)
        
        return Response({
            'rules': rules_data,
            'summary': summary
        })
    
    def post(self, request):
        """ایجاد یا به‌روزرسانی قانون قیمت‌گذاری"""
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        required_fields = ['product_type', 'pricing_method']
        
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'error': f'{field} is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            rule = AgentPricingService.create_pricing_rule(
                agent=request.user,
                product_type=data['product_type'],
                pricing_method=data['pricing_method'],
                discount_percentage=data.get('discount_percentage'),
                fixed_price=data.get('fixed_price'),
                markup_percentage=data.get('markup_percentage'),
                custom_factor=data.get('custom_factor'),
                min_price=data.get('min_price'),
                max_price=data.get('max_price'),
                description=data.get('description', ''),
                is_active=data.get('is_active', True)
            )
            
            return Response({
                'success': True,
                'rule': {
                    'id': str(rule.id),
                    'product_type': rule.product_type,
                    'pricing_method': rule.pricing_method,
                    'description': rule.description
                },
                'message': 'قانون قیمت‌گذاری با موفقیت ذخیره شد'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentPricingPreviewView(APIView):
    """پیش‌نمایش قیمت برای ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """محاسبه قیمت پیش‌نمایش"""
        # Handle both DRF and WSGI requests for user
        user = getattr(request, 'user', None)
        if not user or not hasattr(user, 'role') or user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        # Handle both DRF and WSGI requests
        if hasattr(request, 'data'):
            data = request.data
        else:
            # Try JSON first
            import json
            try:
                data = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fallback to form data
                try:
                    data = request.POST.dict()
                except:
                    return Response({'error': 'Invalid request data format'}, status=status.HTTP_400_BAD_REQUEST)
        product_type = data.get('product_type')
        
        try:
            if product_type == 'tour':
                # پیش‌نمایش قیمت تور
                tour_id = data.get('tour_id')
                variant_id = data.get('variant_id')
                participants = data.get('participants', {})
                
                if not all([tour_id, variant_id, participants]):
                    return Response(
                        {'error': 'tour_id, variant_id, and participants are required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                from tours.models import Tour, TourVariant
                tour = Tour.objects.get(id=tour_id)
                variant = TourVariant.objects.get(id=variant_id)
                
                pricing_result = AgentPricingService.calculate_tour_price_for_agent(
                    tour=tour,
                    variant=variant,
                    agent=user,
                    participants=participants,
                    selected_options=data.get('options', data.get('selected_options', []))
                )
                
            elif product_type == 'transfer':
                # پیش‌نمایش قیمت ترانسفر
                route_id = data.get('route_id')
                vehicle_type = data.get('vehicle_type')
                passenger_count = data.get('passenger_count', 1)
                
                if not all([route_id, vehicle_type]):
                    return Response(
                        {'error': 'route_id and vehicle_type are required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                from transfers.models import TransferRoute
                import uuid
                
                # Convert string route_id to UUID if needed
                if isinstance(route_id, str):
                    try:
                        route_id = uuid.UUID(route_id)
                    except ValueError:
                        return Response(
                            {'error': 'Invalid route_id format'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                try:
                    route = TransferRoute.objects.get(id=route_id)
                except TransferRoute.DoesNotExist:
                    return Response(
                        {'error': 'Route not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Parse hour from booking_time if provided
                hour = None
                return_hour = None
                if data.get('booking_time'):
                    try:
                        from datetime import datetime
                        booking_time = datetime.strptime(data['booking_time'], '%H:%M')
                        hour = booking_time.hour
                    except:
                        pass
                
                if data.get('return_time'):
                    try:
                        from datetime import datetime
                        return_time = datetime.strptime(data['return_time'], '%H:%M')
                        return_hour = return_time.hour
                    except:
                        pass
                
                pricing_result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=route,
                    vehicle_type=vehicle_type,
                    agent=user,
                    passenger_count=passenger_count,
                    trip_type=data.get('trip_type', 'one_way'),
                    hour=hour,
                    return_hour=return_hour,
                    selected_options=data.get('selected_options', [])
                )
                
            elif product_type == 'car_rental':
                # پیش‌نمایش قیمت اجاره ماشین
                car_id = data.get('car_id')
                days = data.get('days', 1)
                hours = data.get('hours', 0)
                
                if not car_id:
                    return Response(
                        {'error': 'car_id is required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                from car_rentals.models import CarRental
                car = CarRental.objects.get(id=car_id)
                
                pricing_result = AgentPricingService.calculate_car_rental_price_for_agent(
                    car=car,
                    agent=user,
                    days=days,
                    hours=hours,
                    include_insurance=data.get('include_insurance', False)
                )
                
            else:
                return Response(
                    {'error': 'Invalid product_type'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'success': True,
                'pricing': pricing_result
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentCommissionListView(APIView):
    """لیست کمیسیون‌های ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        # دریافت پارامترهای فیلتر
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        status_filter = request.GET.get('status')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # دریافت تاریخچه کمیسیون
        history = AgentCommissionService.get_commission_history(
            agent=request.user,
            limit=limit,
            offset=offset
        )
        
        # فیلتر بر اساس وضعیت
        commissions = history['commissions']
        if status_filter:
            commissions = commissions.filter(status=status_filter)
        
        # فیلتر بر اساس تاریخ
        if start_date:
            commissions = commissions.filter(created_at__gte=start_date)
        if end_date:
            commissions = commissions.filter(created_at__lte=end_date)
        
        # تبدیل به لیست
        commission_list = []
        for commission in commissions:
            commission_list.append({
                'id': str(commission.id),
                'order_number': commission.order.order_number,
                'order_amount': float(commission.order_amount),
                'commission_rate': float(commission.commission_rate),
                'commission_amount': float(commission.commission_amount),
                'status': commission.status,
                'status_display': commission.get_status_display(),
                'created_at': commission.created_at.isoformat(),
                'approved_at': commission.approved_at.isoformat() if commission.approved_at else None,
                'paid_at': commission.paid_at.isoformat() if commission.paid_at else None,
                'notes': commission.notes,
                'currency': commission.currency
            })
        
        return Response({
            'commissions': commission_list,
            'total_count': history['total_count'],
            'has_more': history['has_more']
        })


class AgentCommissionSummaryView(APIView):
    """خلاصه کمیسیون ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        # دریافت پارامترهای تاریخ
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # دریافت خلاصه کمیسیون
        summary = AgentCommissionService.get_agent_commission_summary(
            agent=request.user,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({
            'total_commission': float(summary['total_commission']),
            'total_orders': summary['total_orders'],
            'status_stats': {
                status: {
                    'count': stats['count'],
                    'amount': float(stats['amount']) if stats['amount'] else 0.0
                }
                for status, stats in summary['status_stats'].items()
            },
            'product_stats': {
                product_type: {
                    'count': stats['count'],
                    'amount': float(stats['amount']) if stats['amount'] else 0.0
                }
                for product_type, stats in summary['product_stats'].items()
            },
            'period': summary['period']
        })


class AgentCommissionDetailView(APIView):
    """جزئیات کمیسیون"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, commission_id):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            commission = AgentCommission.objects.get(
                id=commission_id,
                agent=request.user
            )
            
            return Response({
                'id': str(commission.id),
                'order_number': commission.order.order_number,
                'order_amount': float(commission.order_amount),
                'commission_rate': float(commission.commission_rate),
                'commission_amount': float(commission.commission_amount),
                'status': commission.status,
                'status_display': commission.get_status_display(),
                'created_at': commission.created_at.isoformat(),
                'approved_at': commission.approved_at.isoformat() if commission.approved_at else None,
                'approved_by': commission.approved_by.username if commission.approved_by else None,
                'rejected_at': commission.rejected_at.isoformat() if commission.rejected_at else None,
                'rejected_by': commission.rejected_by.username if commission.rejected_by else None,
                'rejection_reason': commission.rejection_reason,
                'paid_at': commission.paid_at.isoformat() if commission.paid_at else None,
                'paid_by': commission.paid_by.username if commission.paid_by else None,
                'payment_method': commission.payment_method,
                'payment_reference': commission.payment_reference,
                'notes': commission.notes,
                'currency': commission.currency
            })
            
        except AgentCommission.DoesNotExist:
            return Response({'error': 'Commission not found'}, status=status.HTTP_404_NOT_FOUND)


class AgentCommissionMonthlyView(APIView):
    """کمیسیون ماهانه ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        # دریافت پارامترهای تاریخ
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
        
        # محاسبه کمیسیون ماهانه
        monthly_data = AgentCommissionService.calculate_monthly_commission(
            agent=request.user,
            year=year,
            month=month
        )
        
        return Response({
            'year': monthly_data['year'],
            'month': monthly_data['month'],
            'total_commission': float(monthly_data['total_commission']),
            'total_orders': monthly_data['total_orders'],
            'pending_commission': float(monthly_data['pending_commission']),
            'paid_commission': float(monthly_data['paid_commission'])
        })


class AgentCustomerDetailView(APIView):
    """جزئیات مشتری"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, customer_id):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            customer_data = AgentCustomerService.get_customer_detail(request.user, customer_id)
            
            return Response({
                'customer': {
                    'id': str(customer_data['customer'].id),
                    'name': customer_data['agent_customer'].customer_name,
                    'email': customer_data['customer'].email,
                    'phone': customer_data['customer'].phone_number,
                    'address': customer_data['agent_customer'].customer_address,
                    'city': customer_data['agent_customer'].customer_city,
                    'country': customer_data['agent_customer'].customer_country,
                    'birth_date': customer_data['agent_customer'].customer_birth_date.isoformat() if customer_data['agent_customer'].customer_birth_date else None,
                    'gender': customer_data['agent_customer'].customer_gender,
                    'preferred_language': customer_data['agent_customer'].preferred_language,
                    'preferred_contact_method': customer_data['agent_customer'].preferred_contact_method,
                    'status': customer_data['agent_customer'].customer_status,
                    'status_display': customer_data['agent_customer'].get_customer_status_display(),
                    'tier': customer_data['agent_customer'].customer_tier,
                    'tier_display': customer_data['agent_customer'].get_customer_tier_display(),
                    'relationship_notes': customer_data['agent_customer'].relationship_notes,
                    'special_requirements': customer_data['agent_customer'].special_requirements,
                    'marketing_consent': customer_data['agent_customer'].marketing_consent,
                    'created_at': customer_data['agent_customer'].created_at.isoformat(),
                    'is_active': customer_data['agent_customer'].is_active,
                    'created_by_agent': customer_data['agent_customer'].created_by_agent
                },
                'statistics': {
                    'total_orders': customer_data['total_orders'],
                    'total_spent': float(customer_data['total_spent']),
                    'last_order_date': customer_data['last_order_date'].isoformat() if customer_data['last_order_date'] else None
                },
                'recent_orders': [
                    {
                        'id': str(order.id),
                        'order_number': order.order_number,
                        'total_amount': float(order.total_amount),
                        'status': order.status,
                        'created_at': order.created_at.isoformat()
                    }
                    for order in customer_data['orders']
                ]
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, customer_id):
        """به‌روزرسانی اطلاعات مشتری"""
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            customer_data = request.data
            agent_customer = AgentCustomerService.update_customer_info(
                request.user, 
                customer_id, 
                customer_data
            )
            
            return Response({
                'success': True,
                'message': 'اطلاعات مشتری با موفقیت به‌روزرسانی شد',
                'customer': {
                    'id': str(agent_customer.customer.id),
                    'name': agent_customer.customer_name,
                    'email': agent_customer.customer_email,
                    'phone': agent_customer.customer_phone,
                    'status': agent_customer.customer_status,
                    'tier': agent_customer.customer_tier
                }
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, customer_id):
        """حذف مشتری"""
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            result = AgentCustomerService.delete_customer_relationship(request.user, customer_id)
            return Response(result)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentCustomerStatisticsView(APIView):
    """آمار مشتریان ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            stats = AgentCustomerService.get_customer_statistics(request.user)
            
            return Response({
                'total_customers': stats['total_customers'],
                'active_customers': stats['active_customers'],
                'vip_customers': stats['vip_customers'],
                'tier_stats': stats['tier_stats'],
                'status_stats': stats['status_stats'],
                'language_stats': stats['language_stats'],
                'contact_stats': stats['contact_stats'],
                'total_spent': float(stats['total_spent']),
                'average_spent': float(stats['average_spent']),
                'top_customers': stats['top_customers']
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentCustomerOrdersView(APIView):
    """سفارشات مشتری"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, customer_id):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
            
            orders_data = AgentCustomerService.get_customer_orders(
                request.user, 
                customer_id, 
                limit, 
                offset
            )
            
            orders_list = []
            for order in orders_data['orders']:
                orders_list.append({
                    'id': str(order.id),
                    'order_number': order.order_number,
                    'total_amount': float(order.total_amount),
                    'status': order.status,
                    'status_display': order.get_status_display(),
                    'created_at': order.created_at.isoformat(),
                    'currency': order.currency
                })
            
            return Response({
                'orders': orders_list,
                'total_count': orders_data['total_count'],
                'has_more': orders_data['has_more']
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentCustomerSearchView(APIView):
    """جستجوی مشتریان"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        search_term = request.GET.get('q', '')
        if not search_term:
            return Response({'error': 'Search term is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            limit = int(request.GET.get('limit', 20))
            customers = AgentCustomerService.search_customers(request.user, search_term, limit)
            
            customer_list = []
            for agent_customer in customers:
                customer_list.append({
                    'id': str(agent_customer.customer.id),
                    'name': agent_customer.customer_name,
                    'email': agent_customer.customer_email,
                    'phone': agent_customer.customer_phone,
                    'status': agent_customer.customer_status,
                    'tier': agent_customer.customer_tier,
                    'total_orders': agent_customer.total_orders,
                    'total_spent': float(agent_customer.total_spent)
                })
            
            return Response({
                'customers': customer_list,
                'total_count': len(customer_list)
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentCustomerTierUpdateView(APIView):
    """به‌روزرسانی تیر مشتری"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, customer_id):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        new_tier = request.data.get('tier')
        if not new_tier:
            return Response({'error': 'Tier is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AgentCustomerService.update_customer_tier(request.user, customer_id, new_tier)
            return Response(result)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentCustomerStatusUpdateView(APIView):
    """به‌روزرسانی وضعیت مشتری"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, customer_id):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AgentCustomerService.update_customer_status(request.user, customer_id, new_status)
            return Response(result)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentToursView(APIView):
    """لیست تورهای قابل رزرو برای ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from tours.models import Tour
            
            # Get active tours available for agents
            tours = Tour.objects.filter(
                is_active=True
            ).select_related('category').prefetch_related('variants')
            
            # Apply filters if provided
            category = request.GET.get('category')
            if category:
                tours = tours.filter(category__slug=category)
            
            location = request.GET.get('location')
            if location:
                tours = tours.filter(location__icontains=location)
            
            search = request.GET.get('search')
            if search:
                tours = tours.filter(
                    models.Q(title__icontains=search) |
                    models.Q(description__icontains=search) |
                    models.Q(location__icontains=search)
                )
            
            # Calculate agent pricing for each tour
            tour_list = []
            for tour in tours:
                # Calculate agent price (15% discount by default)
                from decimal import Decimal
                agent_price = tour.price * Decimal('0.85')
                
                tour_data = {
                    'id': tour.id,
                    'title': tour.title,
                    'description': tour.description,
                    'base_price': float(tour.price),
                    'agent_price': float(agent_price),
                    'duration': f"{tour.duration_hours} hours" if tour.duration_hours else "N/A",
                    'location': f"{tour.city}, {tour.country}",
                    'image': get_safe_image_url(tour.image),
                    'category': tour.category.name if tour.category else 'General',
                    'is_active': tour.is_active,
                    'variants': [
                        {
                            'id': variant.id,
                            'name': variant.name,
                            'description': variant.description,
                            'base_price': float(variant.base_price),
                            'agent_price': float(variant.base_price * Decimal('0.85')),
                            'capacity': variant.capacity,
                            'price_modifier': float(variant.price_modifier) if variant.price_modifier else 0,
                            'is_active': variant.is_active
                        }
                        for variant in tour.variants.filter(is_active=True)
                    ]
                }
                tour_list.append(tour_data)
            
            return Response(tour_list)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentTourDetailView(APIView):
    """جزئیات تور برای ایجنت"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, tour_id):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from tours.models import Tour
            
            tour = get_object_or_404(Tour, id=tour_id, is_active=True)
            
            # Calculate agent price
            from decimal import Decimal
            agent_price = tour.price * Decimal('0.85')
            
            tour_data = {
                'id': tour.id,
                'title': tour.title,
                'description': tour.description,
                'base_price': float(tour.price),
                'agent_price': float(agent_price),
                'duration': f"{tour.duration_hours} hours" if tour.duration_hours else "N/A",
                'location': f"{tour.city}, {tour.country}",
                'image': get_safe_image_url(tour.image),
                'category': tour.category.name if tour.category else 'General',
                'is_active': tour.is_active,
                'variants': [
                    {
                        'id': variant.id,
                        'name': variant.name,
                        'description': variant.description,
                        'base_price': float(variant.base_price),
                        'agent_price': float(variant.base_price * 0.85),
                        'capacity': variant.capacity,
                        'price_modifier': float(variant.price_modifier) if variant.price_modifier else 0,
                        'includes': {
                            'transfer': variant.includes_transfer,
                            'guide': variant.includes_guide,
                            'meal': variant.includes_meal,
                            'photographer': variant.includes_photographer,
                            'extended_hours': variant.extended_hours,
                            'private_transfer': variant.private_transfer,
                            'expert_guide': variant.expert_guide,
                            'special_meal': variant.special_meal
                        },
                        'is_active': variant.is_active
                    }
                    for variant in tour.variants.filter(is_active=True)
                ]
            }
            
            return Response(tour_data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentTourAvailableDatesView(APIView):
    """تاریخ‌های موجود برای تور"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, tour_id):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from tours.models import Tour, TourSchedule, TourVariant
            from datetime import timedelta
            from decimal import Decimal
            
            tour = get_object_or_404(Tour, id=tour_id, is_active=True)
            
            # Get available dates for the next 30 days
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=30)
            
            schedules = TourSchedule.objects.filter(
                tour=tour,
                start_date__gte=start_date,
                start_date__lte=end_date,
                is_active=True,
                is_available=True
            ).select_related('tour').prefetch_related('variant_capacities__variant')
            
            available_dates = []
            for schedule in schedules:
                available_dates.append({
                    'date': schedule.start_date.isoformat(),
                    'schedule_id': str(schedule.id),  # Add schedule_id to the response
                    'available_slots': schedule.available_capacity,
                    'variants': [
                        {
                            'id': variant.id,
                            'name': variant.name,
                            'description': variant.description,
                            'base_price': float(variant.base_price),
                            'agent_price': float(variant.base_price * Decimal('0.85')),
                            'capacity': variant.capacity,
                            'available_capacity': schedule.variant_capacities.filter(variant=variant).first().available_capacity if schedule.variant_capacities.filter(variant=variant).exists() else variant.capacity,
                            'price_modifier': float(variant.price_modifier) if variant.price_modifier else 0,
                            'includes': {
                                'transfer': variant.includes_transfer,
                                'guide': variant.includes_guide,
                                'meal': variant.includes_meal,
                                'photographer': variant.includes_photographer,
                                'extended_hours': variant.extended_hours,
                                'private_transfer': variant.private_transfer,
                                'expert_guide': variant.expert_guide,
                                'special_meal': variant.special_meal
                            },
                            'is_active': variant.is_active
                        }
                        for variant in tour.variants.filter(is_active=True)
                    ]
                })
            
            return Response(available_dates)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentTourOptionsView(APIView):
    """گزینه‌های اضافی تور"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, tour_id):
        if request.user.role != 'agent':
            return Response({'error': 'User is not an agent'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from tours.models import Tour, TourOption
            from decimal import Decimal
            
            tour = get_object_or_404(Tour, id=tour_id, is_active=True)
            
            options = TourOption.objects.filter(
                tour=tour,
                is_active=True
            )
            
            option_list = []
            for option in options:
                option_list.append({
                    'id': option.id,
                    'name': option.name,
                    'description': option.description,
                    'base_price': float(option.price),
                    'agent_price': float(option.price * Decimal('0.85')),
                    'is_required': getattr(option, 'is_required', False),
                    'is_active': option.is_active,
                    'category': option.option_type
                })
            
            return Response(option_list)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 
