"""
DRF Views for Tours app.
"""

from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Sum
from datetime import date, timedelta
from django.utils import timezone
from django.core.cache import cache

from .models import Tour, TourCategory, TourVariant, TourSchedule, TourOption, TourReview, TourPricing, ReviewReport, ReviewResponse, TourBooking
from .serializers import (
    TourListSerializer, TourDetailSerializer, TourCategorySerializer,
    TourVariantSerializer, TourOptionSerializer, TourScheduleSerializer,
    TourReviewSerializer, TourReviewCreateSerializer, TourReviewDetailSerializer, TourSearchSerializer,
    TourBookingSerializer, CheckTourAvailabilitySerializer,
    ReviewReportSerializer, ReviewReportCreateSerializer, ReviewReportUpdateSerializer,
    ReviewResponseSerializer, ReviewResponseCreateSerializer, ReviewResponseUpdateSerializer
)
from .mixins import ReviewManagementMixin
from .protection import ReviewProtectionManager


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_tours_view(request):
    """Test view to check if tours exist."""
    tours = Tour.objects.all()
    return Response({
        'count': tours.count(),
        'tours': list(tours.values('id', 'slug', 'price', 'currency', 'is_active'))
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def home_tours_view(request):
    """Get categorized tours for home page display."""
    tours = Tour.objects.filter(is_active=True).select_related('category')

    # Separate tours by category
    featured_tours = tours.filter(is_featured=True)[:6]
    special_tours = tours.filter(is_special=True)[:6]
    seasonal_tours = tours.filter(is_seasonal=True)[:6]
    popular_tours = tours.filter(is_popular=True)[:6]

    return Response({
        'featured_tours': TourListSerializer(featured_tours, many=True, context={'request': request}).data,
        'special_tours': TourListSerializer(special_tours, many=True, context={'request': request}).data,
        'seasonal_tours': TourListSerializer(seasonal_tours, many=True, context={'request': request}).data,
        'popular_tours': TourListSerializer(popular_tours, many=True, context={'request': request}).data,
    })


class TourCategoryListView(generics.ListAPIView):
    """List all tour categories."""
    
    queryset = TourCategory.objects.filter(is_active=True).order_by('slug')
    serializer_class = TourCategorySerializer
    permission_classes = [permissions.AllowAny]


class TourListView(generics.ListAPIView):
    """List all tours (no search/filter)."""
    serializer_class = TourListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Tour.objects.filter(is_active=True)  # Add back is_active filter
    pagination_class = None
    filter_backends = []
    search_fields = []
    ordering_fields = []


class TourDetailView(generics.RetrieveAPIView):
    """Get tour details by slug."""

    queryset = Tour.objects.filter(is_active=True).select_related('category')
    serializer_class = TourDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs.get('slug')
        tour = get_object_or_404(Tour, slug=slug, is_active=True)

        # Set the current language for the tour object
        current_language = self.request.LANGUAGE_CODE if hasattr(self.request, 'LANGUAGE_CODE') else 'fa'
        tour.set_current_language(current_language)

        return tour


class UserPendingOrdersView(APIView):
    """Get user's pending orders for duplicate booking prevention."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, tour_slug=None):
        """Get user's pending orders."""
        from orders.models import Order
        pending_orders = Order.objects.filter(
            user=request.user,
            status='pending'
        ).prefetch_related('items').order_by('-created_at')

        orders_data = []
        for order in pending_orders:
            order_data = {
                'id': str(order.id),
                'order_number': order.order_number,
                'created_at': order.created_at.isoformat(),
                'items': []
            }

            for item in order.items.all():
                item_data = {
                    'id': str(item.id),
                    'product_type': item.product_type,
                    'product_id': str(item.product_id),
                    'booking_date': item.booking_date.isoformat() if item.booking_date else None,
                    'booking_data': item.booking_data or {}
                }
                order_data['items'].append(item_data)

            orders_data.append(order_data)

        return Response(orders_data)


class TourSearchView(APIView):
    """Advanced tour search."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = TourSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        queryset = Tour.objects.filter(is_active=True).select_related('category')
        
        # Apply search filters
        if data.get('query'):
            query = data['query']
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(highlights__icontains=query)
            )
        
        if data.get('category'):
            queryset = queryset.filter(category_id=data['category'])
        
        if data.get('min_price'):
            queryset = queryset.filter(base_price__gte=data['min_price'])
        
        if data.get('max_price'):
            queryset = queryset.filter(base_price__lte=data['max_price'])
        
        if data.get('min_duration'):
            queryset = queryset.filter(duration_hours__gte=data['min_duration'])
        
        if data.get('max_duration'):
            queryset = queryset.filter(duration_hours__lte=data['max_duration'])
        
        if data.get('date_from') or data.get('date_to'):
            schedules_filter = Q()
            if data.get('date_from'):
                schedules_filter &= Q(schedules__start_date__gte=data['date_from'])
            if data.get('date_to'):
                schedules_filter &= Q(schedules__end_date__lte=data['date_to'])
            schedules_filter &= Q(schedules__is_available=True)
            queryset = queryset.filter(schedules_filter).distinct()
        
        if data.get('includes_transfer') is not None:
            queryset = queryset.filter(includes_transfer=data['includes_transfer'])
        
        if data.get('includes_guide') is not None:
            queryset = queryset.filter(includes_guide=data['includes_guide'])
        
        if data.get('includes_meal') is not None:
            queryset = queryset.filter(includes_meal=data['includes_meal'])
        
        # Apply sorting
        sort_by = data.get('sort_by', 'created_desc')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('base_price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-base_price')
        elif sort_by == 'duration_asc':
            queryset = queryset.order_by('duration_hours')
        elif sort_by == 'duration_desc':
            queryset = queryset.order_by('-duration_hours')
        elif sort_by == 'rating_desc':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')
        elif sort_by == 'created_asc':
            queryset = queryset.order_by('created_at')
        else:  # created_desc
            queryset = queryset.order_by('-created_at')
        
        # Paginate results
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = TourListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TourScheduleListView(generics.ListAPIView):
    """List schedules for a specific tour."""
    
    serializer_class = TourScheduleSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        tour_slug = self.kwargs.get('tour_slug')
        tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return tour.schedules.filter(is_available=True)


class TourReviewListView(generics.ListAPIView):
    """List reviews for a specific tour."""
    
    serializer_class = TourReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        tour_slug = self.kwargs.get('tour_slug')
        tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return tour.reviews.filter(is_verified=True).order_by('-created_at')


class TourReviewCreateView(generics.CreateAPIView):
    """Create a review for a tour (authenticated users only)."""
    
    serializer_class = TourReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        tour_slug = self.kwargs.get('tour_slug')
        context['tour'] = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return context


class GuestReviewCreateView(generics.CreateAPIView):
    """Handle review creation for guest users (redirects to auth)."""
    
    serializer_class = TourReviewCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'error': 'Authentication required',
                'message': 'Please register or login to leave a review',
                'auth_required': True,
                'redirect_url': '/auth/register',
                'tour_slug': self.kwargs.get('tour_slug')
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # If user is authenticated, proceed with normal flow
        return super().post(request, *args, **kwargs)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        tour_slug = self.kwargs.get('tour_slug')
        context['tour'] = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return context


class TourBookingView(APIView):
    """Book a tour."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = TourBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        tour = data['tour']
        schedule = data['schedule']
        quantity = data['quantity']
        
        # Calculate total price
        base_price = tour.base_price
        variant_price_modifier = 0
        
        if data.get('variant_id'):
            try:
                variant = tour.variants.get(id=data['variant_id'])
                variant_price_modifier = variant.price_modifier
            except TourVariant.DoesNotExist:
                return Response({
                    'error': 'Invalid variant selected.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        unit_price = base_price + variant_price_modifier
        total_price = unit_price * quantity
        
        # Add options price
        options_total = 0
        selected_options = data.get('selected_options', [])
        for option_data in selected_options:
            try:
                option = tour.options.get(id=option_data['option_id'])
                option_quantity = option_data.get('quantity', 1)
                options_total += option.price * option_quantity
            except TourOption.DoesNotExist:
                return Response({
                    'error': f'Invalid option: {option_data.get("option_id")}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        total_price += options_total
        
        # Create booking response (this would typically create a cart item or order)
        booking_data = {
            'tour': {
                'id': str(tour.id),
                'title': tour.title,
                'slug': tour.slug,
            },
            'schedule': {
                'id': str(schedule.id),
                'start_date': schedule.start_date,
                'start_time': schedule.start_time,
            },
            'variant_id': data.get('variant_id'),
            'quantity': quantity,
            'unit_price': float(unit_price),
            'options_total': float(options_total),
            'total_price': float(total_price),
            'currency': tour.currency,
            'selected_options': selected_options,
            'special_requests': data.get('special_requests', ''),
        }
        
        return Response({
            'message': 'Tour booking request created successfully.',
            'booking': booking_data
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def tour_availability_view(request, tour_slug):
    """Check tour availability for specific dates."""
    
    tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    if not date_from or not date_to:
        return Response({
            'error': 'Both date_from and date_to parameters are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from datetime import datetime
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        return Response({
            'error': 'Invalid date format. Use YYYY-MM-DD.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    schedules = tour.schedules.filter(
        start_date__gte=date_from,
        end_date__lte=date_to,
        is_available=True
    )
    
    availability_data = []
    for schedule in schedules:
        availability_data.append({
            'date': schedule.start_date,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time,
            'available_capacity': schedule.available_capacity,
            'is_full': schedule.is_full,
        })
    
    return Response({
        'tour': {
            'id': str(tour.id),
            'title': tour.title,
            'slug': tour.slug,
        },
        'availability': availability_data
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def tour_stats_view(request, tour_slug):
    """Get tour statistics."""
    
    tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
    
    # Calculate statistics
    reviews = tour.reviews.all()
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()
    
    # Recent bookings (mock data for now)
    recent_bookings = 0  # This would come from actual booking data
    
    stats = {
        'total_reviews': total_reviews,
        'average_rating': round(average_rating, 1),
        'rating_distribution': rating_distribution,
        'recent_bookings': recent_bookings,
        'is_popular': total_reviews > 10 and average_rating >= 4.0,
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def tour_schedules_view(request, tour_id):
    """Get available schedules for a tour with variant capacity information."""
    try:
        tour = Tour.objects.get(id=tour_id, is_active=True)
    except Tour.DoesNotExist:
        return Response(
            {'error': 'Tour not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    schedules = tour.schedules.filter(is_available=True).order_by('start_date')
    schedule_data = []
    
    for schedule in schedules:
        try:
            schedule.initialize_variant_capacities()
        except Exception:
            pass

        # Get variants available for this schedule
        available_variants = schedule.get_available_variants()
        
        for variant in available_variants:
            variant_capacity = schedule.variant_capacities.get(str(variant.id), {}).get('total', variant.capacity)
            
            # Calculate booked capacity for this variant on this schedule
            # ONLY include confirmed orders, not pending ones
            from cart.models import CartItem
            from orders.models import OrderItem
            
            # Count ONLY confirmed orders (exclude pending and cart items)
            # Pending orders should NOT reduce available capacity until they become confirmed/paid
            confirmed_items = OrderItem.objects.filter(
                product_type='tour',
                product_id=tour.id,
                variant_id=str(variant.id),
                booking_data__schedule_id=str(schedule.id),
                order__status__in=['confirmed', 'paid', 'completed']
            )
            
            # Calculate total participants from confirmed orders (adults + children only)
            confirmed_participants = 0
            for item in confirmed_items:
                booking_data = item.booking_data or {}
                participants = booking_data.get('participants', {}) or {}
                adult_count = int(participants.get('adult', 0))
                child_count = int(participants.get('child', 0))
                confirmed_participants += adult_count + child_count

            # Get booked capacity from variant_capacities_raw
            variant_booked = schedule.variant_capacities.get(str(variant.id), {}).get('booked', 0)

            # Use the maximum of calculated and stored booked capacity
            booked_capacity = max(confirmed_participants, variant_booked)
            available_capacity = max(0, variant_capacity - booked_capacity)
            
            schedule_data.append({
                'id': schedule.id,
                'start_date': schedule.start_date.isoformat(),
                'end_date': schedule.end_date.isoformat(),
                'start_time': schedule.start_time.isoformat(),
                'end_time': schedule.end_time.isoformat(),
                'is_available': schedule.is_available,
                'day_of_week': schedule.day_of_week,
                'variant_id': variant.id,
                'variant_name': variant.name,
                'total_capacity': variant_capacity,
                'booked_capacity': booked_capacity,
                'available_capacity': available_capacity,
                'is_full': available_capacity <= 0
            })
    
    return Response({
        'tour': {
            'id': tour.id,
            'title': tour.title,
            'slug': tour.slug,
            'currency': tour.currency,
        },
        'schedules': schedule_data
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_tour_availability_view(request):
    """
    Check tour availability for specific date and variant.
    Only considers confirmed orders, not pending ones.
    """
    tour_id = request.data.get('tour_id')
    variant_id = request.data.get('variant_id')
    schedule_id = request.data.get('schedule_id')
    participants = request.data.get('participants', {})
    
    if not all([tour_id, variant_id, schedule_id, participants]):
        return Response({
            'available': False,
            'error': 'Missing required fields: tour_id, variant_id, schedule_id, participants'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        tour = Tour.objects.get(id=tour_id, is_active=True)
        variant = TourVariant.objects.get(id=variant_id, tour=tour, is_active=True)
        schedule = TourSchedule.objects.get(id=schedule_id, tour=tour, is_available=True)
    except (Tour.DoesNotExist, TourVariant.DoesNotExist, TourSchedule.DoesNotExist):
        return Response({
            'available': False,
            'error': 'Tour, variant, or schedule not found.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate total participants requested
    # Infants do not count towards capacity; cap infants to 2 per booking
    infant_count = max(0, int(participants.get('infant', 0)))
    if infant_count > 2:
        return Response({
            'available': False,
            'error': 'You can add at most 2 infants per tour booking.'
        }, status=status.HTTP_400_BAD_REQUEST)
    total_participants = int(participants.get('adult', 0)) + int(participants.get('child', 0))
    
    # Check variant capacity
    variant_capacity = schedule.variant_capacities.get(str(variant.id), variant.capacity)
    
    # Calculate current bookings
    # ONLY include confirmed orders, not pending ones
    from cart.models import CartItem
    from orders.models import OrderItem
    
    # Count ONLY confirmed orders (exclude pending and cart items)
    # Pending orders should NOT reduce available capacity until they become confirmed/paid
    confirmed_items = OrderItem.objects.filter(
        product_type='tour',
        product_id=tour.id,
        variant_id=str(variant.id),
        booking_data__schedule_id=str(schedule.id),
        order__status__in=['confirmed', 'paid', 'completed']
    )
    
    # Calculate total participants from confirmed orders (adults + children only)
    confirmed_participants = 0
    for item in confirmed_items:
        booking_data = item.booking_data or {}
        participants = booking_data.get('participants', {}) or {}
        adult_count = int(participants.get('adult', 0))
        child_count = int(participants.get('child', 0))
        confirmed_participants += adult_count + child_count

    # Get booked capacity from variant_capacities_raw
    variant_booked = schedule.variant_capacities.get(str(variant.id), {}).get('booked', 0)

    # Use the maximum of calculated and stored booked capacity
    booked_capacity = max(confirmed_participants, variant_booked)
    available_capacity = max(0, variant_capacity - booked_capacity)
    
    # Check if requested participants (excluding infants) fit
    if total_participants > available_capacity:
        return Response({
            'available': False,
            'error': f'Not enough capacity. Requested: {total_participants}, Available: {available_capacity}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'available': True,
        'available_capacity': available_capacity,
        'requested_participants': total_participants,
        'infant_count': infant_count,
        'note': 'Capacity check passed. Pending orders do not affect availability.'
    })


class TourVariantListView(generics.ListAPIView):
    """List all variants for a specific tour."""
    
    serializer_class = TourVariantSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        tour_slug = self.kwargs.get('tour_slug')
        tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return tour.variants.filter(is_active=True)


class TourVariantDetailView(generics.RetrieveAPIView):
    """Get details of a specific tour variant."""
    
    serializer_class = TourVariantSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'variant_id'
    
    def get_queryset(self):
        tour_slug = self.kwargs.get('tour_slug')
        tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return tour.variants.filter(is_active=True)


class TourOptionListView(generics.ListAPIView):
    """List all options for a specific tour."""
    
    serializer_class = TourOptionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        tour_slug = self.kwargs.get('tour_slug')
        tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return tour.options.filter(is_available=True)


class TourOptionDetailView(generics.RetrieveAPIView):
    """Get details of a specific tour option."""
    
    serializer_class = TourOptionSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'option_id'
    
    def get_queryset(self):
        tour_slug = self.kwargs.get('tour_slug')
        tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return tour.options.filter(is_available=True)


class TourItineraryListView(generics.ListAPIView):
    """List itinerary items for a specific tour."""
    
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        tour_slug = self.kwargs.get('tour_slug')
        tour = get_object_or_404(Tour, slug=tour_slug, is_active=True)
        return tour.itinerary.all().order_by('order')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        itinerary_data = []
        
        # Get current language from request
        current_language = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else 'fa'
        
        for item in queryset:
            # Set the current language for this item to get proper translations
            item.set_current_language(current_language)
            
            itinerary_data.append({
                'id': str(item.id),
                'title': item.title,
                'description': item.description,
                'order': item.order,
                'duration_minutes': item.duration_minutes,
                'location': item.location,
                'image': item.image.url if item.image else None
            })
        
        return Response(itinerary_data)


class TourBookingStepsView(APIView):
    """Get booking steps for tours."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, tour_slug):
        """Get booking steps for a specific tour."""
        try:
            tour = Tour.objects.get(slug=tour_slug, is_active=True)
        except Tour.DoesNotExist:
            return Response(
                {'error': 'Tour not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Default booking steps for tours
        booking_steps = [
            {
                'id': 1,
                'title': 'انتخاب تاریخ',
                'description': 'انتخاب تاریخ و زمان',
                'isComplete': False,
                'isActive': True
            },
            {
                'id': 2,
                'title': 'انتخاب پکیج',
                'description': 'انتخاب نوع تور',
                'isComplete': False,
                'isActive': False
            },
            {
                'id': 3,
                'title': 'شرکت‌کنندگان',
                'description': 'انتخاب تعداد شرکت‌کنندگان',
                'isComplete': False,
                'isActive': False
            },
            {
                'id': 4,
                'title': 'بررسی',
                'description': 'بررسی و تأیید',
                'isComplete': False,
                'isActive': False
            }
        ]
        
        return Response({
            'tour': {
                'id': str(tour.id),
                'title': tour.title,
                'slug': tour.slug
            },
            'booking_steps': booking_steps
        }) 


class TourReviewEditView(generics.UpdateAPIView):
    """Edit a tour review."""
    
    serializer_class = TourReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get reviews that the user can edit."""
        return TourReview.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get the review to edit."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(TourReview, id=review_id, user=self.request.user)
        
        # Check if user can edit this review
        mixin = ReviewManagementMixin()
        can_edit = mixin.can_edit_review(self.request.user, review)
        
        if not can_edit['can_edit']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(can_edit['reason'])
        
        return review
    
    def update(self, request, *args, **kwargs):
        """Update review with validation."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Validate content using protection system
        content = request.data.get('comment', '')
        protection_manager = ReviewProtectionManager()
        validation_result = protection_manager.validate_review_submission(
            request.user, content, instance.tour, 'tour'
        )
        
        if not validation_result['valid']:
            return Response({
                'error': 'Content validation failed',
                'issues': validation_result['issues']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)


class TourReviewDeleteView(generics.DestroyAPIView):
    """Delete a tour review."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get reviews that the user can delete."""
        return TourReview.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get the review to delete."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(TourReview, id=review_id, user=self.request.user)
        
        # Check if user can delete this review
        mixin = ReviewManagementMixin()
        can_delete = mixin.can_delete_review(self.request.user, review)
        
        if not can_delete['can_delete']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(can_delete['reason'])
        
        return review


class ReviewReportCreateView(generics.CreateAPIView):
    """Create a review report."""
    
    serializer_class = ReviewReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create report with validation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if user has already reported this review
        review = serializer.validated_data['review']
        existing_report = ReviewReport.objects.filter(
            reporter=request.user,
            review=review,
            status__in=['pending', 'investigating']
        ).first()
        
        if existing_report:
            return Response({
                'error': 'You have already reported this review',
                'report_id': existing_report.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ReviewReportListView(generics.ListAPIView):
    """List review reports (admin/staff only)."""
    
    serializer_class = ReviewReportSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get reports based on status filter."""
        queryset = ReviewReport.objects.all()
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class ReviewReportDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update review report (admin/staff only)."""
    
    serializer_class = ReviewReportUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ReviewReport.objects.all()


class ReviewResponseCreateView(generics.CreateAPIView):
    """Create a response to a review."""
    
    serializer_class = ReviewResponseCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create response with validation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if user has already responded to this review
        review = serializer.validated_data['review']
        existing_response = ReviewResponse.objects.filter(
            responder=request.user,
            review=review
        ).first()
        
        if existing_response:
            return Response({
                'error': 'You have already responded to this review',
                'response_id': existing_response.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ReviewResponseUpdateView(generics.UpdateAPIView):
    """Update a review response."""
    
    serializer_class = ReviewResponseUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get responses that the user can edit."""
        return ReviewResponse.objects.filter(responder=self.request.user)
    
    def get_object(self):
        """Get the response to edit."""
        response_id = self.kwargs.get('response_id')
        response = get_object_or_404(ReviewResponse, id=response_id, responder=self.request.user)
        
        # Check if user can edit this response
        if not response.can_be_edited_by(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You cannot edit this response or the editing time has expired.')
        
        return response


class ReviewResponseDeleteView(generics.DestroyAPIView):
    """Delete a review response."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get responses that the user can delete."""
        return ReviewResponse.objects.filter(responder=self.request.user)
    
    def get_object(self):
        """Get the response to delete."""
        response_id = self.kwargs.get('response_id')
        response = get_object_or_404(ReviewResponse, id=response_id, responder=self.request.user)
        
        # Check if user can delete this response
        if not response.can_be_deleted_by(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have permission to delete this response.')
        
        return response


class TourReviewDetailView(generics.RetrieveAPIView):
    """Get detailed review information with responses and permissions."""
    
    serializer_class = TourReviewDetailSerializer
    permission_classes = [permissions.AllowAny]
    queryset = TourReview.objects.filter(status='approved')
    
    def get_object(self):
        """Get the review with related data."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            TourReview.objects.select_related('user', 'tour').prefetch_related('responses'),
            id=review_id
        )
        
        # Only show approved reviews to public
        if not review.is_approved and not self.request.user.is_staff:
            from rest_framework.exceptions import NotFound
            raise NotFound('Review not found or not approved.')
        
        return review


class ReviewManagementDashboardView(APIView):
    """Dashboard for review management (admin/staff only)."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Get review management statistics."""
        # Get review statistics
        total_reviews = TourReview.objects.count()
        pending_reviews = TourReview.objects.filter(status='pending').count()
        flagged_reviews = TourReview.objects.filter(status='flagged').count()
        approved_reviews = TourReview.objects.filter(status='approved').count()
        
        # Get report statistics
        total_reports = ReviewReport.objects.count()
        pending_reports = ReviewReport.objects.filter(status='pending').count()
        investigating_reports = ReviewReport.objects.filter(status='investigating').count()
        
        # Get response statistics
        total_responses = ReviewResponse.objects.count()
        public_responses = ReviewResponse.objects.filter(is_public=True).count()
        official_responses = ReviewResponse.objects.filter(is_official=True).count()
        
        # Get recent activity
        recent_reviews = TourReview.objects.order_by('-created_at')[:5]
        recent_reports = ReviewReport.objects.order_by('-created_at')[:5]
        
        return Response({
            'statistics': {
                'reviews': {
                    'total': total_reviews,
                    'pending': pending_reviews,
                    'flagged': flagged_reviews,
                    'approved': approved_reviews
                },
                'reports': {
                    'total': total_reports,
                    'pending': pending_reports,
                    'investigating': investigating_reports
                },
                'responses': {
                    'total': total_responses,
                    'public': public_responses,
                    'official': official_responses
                }
            },
            'recent_activity': {
                'reviews': TourReviewSerializer(recent_reviews, many=True).data,
                'reports': ReviewReportSerializer(recent_reports, many=True).data
            }
        }) 


class TourPurchaseCheckView(APIView):
    """Check if authenticated user has purchased this tour."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, tour_slug):
        try:
            tour = Tour.objects.get(slug=tour_slug, is_active=True)
            
            # Check if user has any completed bookings for this tour
            # This should check actual purchase history, not just cart items
            from tours.models import TourBooking
            has_purchased = TourBooking.objects.filter(
                user=request.user,
                tour=tour,
                status__in=['completed', 'confirmed', 'active']
            ).exists()
            
            return Response({
                'has_purchased': has_purchased,
                'tour_id': tour.id,
                'tour_slug': tour.slug
            })
            
        except Tour.DoesNotExist:
            return Response(
                {'error': 'Tour not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'Error checking purchase history'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 