"""
Views for Car Rentals.
"""

from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.db import transaction
from .models import (
    CarRental, CarRentalCategory, CarRentalLocation, CarRentalOption, 
    CarRentalAvailability, CarRentalBooking, CarRentalImage
)
from .serializers import (
    CarRentalListSerializer, CarRentalDetailSerializer, CarRentalCategorySerializer,
    CarRentalLocationSerializer, CarRentalOptionSerializer, CarRentalAvailabilitySerializer, 
    CarRentalBookingSerializer, CarRentalSearchSerializer, CarRentalBookingCreateSerializer, 
    CarRentalAvailabilityCheckSerializer
)


class CarRentalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CarRentalCategory model."""
    
    queryset = CarRentalCategory.objects.filter(is_active=True)
    serializer_class = CarRentalCategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['translations__name', 'translations__description']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order', 'name']


class CarRentalLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CarRentalLocation model."""
    
    queryset = CarRentalLocation.objects.filter(is_active=True)
    serializer_class = CarRentalLocationSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'address', 'city', 'country']
    filterset_fields = ['location_type', 'city', 'country']
    ordering_fields = ['sort_order', 'id']
    ordering = ['sort_order', 'id']
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get locations grouped by type."""
        locations = self.get_queryset()
        grouped = {}
        
        for location in locations:
            location_type = location.location_type
            if location_type not in grouped:
                grouped[location_type] = []
            
            serializer = self.get_serializer(location)
            grouped[location_type].append(serializer.data)
        
        return Response(grouped)


class CarRentalOptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CarRentalOption model."""
    
    queryset = CarRentalOption.objects.filter(is_active=True)
    serializer_class = CarRentalOptionSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['translations__name', 'translations__description']
    filterset_fields = ['option_type', 'price_type', 'is_active']
    ordering_fields = ['option_type', 'name', 'price']
    ordering = ['option_type', 'name']


class CarRentalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CarRental model."""
    
    queryset = CarRental.objects.filter(is_active=True, is_available=True).select_related(
        'category', 'agent'
    ).prefetch_related(
        'images', 'availability'
    )
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'translations__title', 'translations__description', 'brand', 'model',
        'city', 'country', 'pickup_location', 'dropoff_location'
    ]
    filterset_fields = [
        'category', 'brand', 'fuel_type', 'transmission', 'is_featured',
        'is_popular', 'is_special', 'is_seasonal', 'city', 'country', 'agent'
    ]
    ordering_fields = [
        'price_per_day', 'seats', 'year', 'created_at', 'is_featured'
    ]
    ordering = ['-is_featured', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CarRentalListSerializer
        elif self.action == 'quick_info':
            return CarRentalListSerializer  # Use list serializer for quick info
        return CarRentalDetailSerializer
    
    def get_queryset(self):
        """Get queryset with proper filtering and optimization."""
        queryset = super().get_queryset()
        
        # Additional filters
        min_seats = self.request.query_params.get('min_seats')
        if min_seats:
            queryset = queryset.filter(seats__gte=min_seats)
        
        max_seats = self.request.query_params.get('max_seats')
        if max_seats:
            queryset = queryset.filter(seats__lte=max_seats)
        
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price_per_day__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price_per_day__lte=max_price)
        
        # Date availability filter
        pickup_date = self.request.query_params.get('pickup_date')
        dropoff_date = self.request.query_params.get('dropoff_date')
        
        if pickup_date and dropoff_date:
            queryset = queryset.filter(
                availability__start_date__lte=pickup_date,
                availability__end_date__gte=dropoff_date,
                availability__is_available=True
            ).distinct()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for car rentals."""
        serializer = CarRentalSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        queryset = self.get_queryset()
        
        # Apply search filters
        if data.get('query'):
            query = data['query']
            queryset = queryset.filter(
                Q(translations__title__icontains=query) |
                Q(translations__description__icontains=query) |
                Q(brand__icontains=query) |
                Q(model__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            ).distinct()
        
        if data.get('category'):
            queryset = queryset.filter(category_id=data['category'])
        
        if data.get('city'):
            queryset = queryset.filter(city__icontains=data['city'])
        
        if data.get('country'):
            queryset = queryset.filter(country__icontains=data['country'])
        
        if data.get('brand'):
            queryset = queryset.filter(brand__icontains=data['brand'])
        
        if data.get('fuel_type'):
            queryset = queryset.filter(fuel_type=data['fuel_type'])
        
        if data.get('transmission'):
            queryset = queryset.filter(transmission=data['transmission'])
        
        if data.get('min_seats'):
            queryset = queryset.filter(seats__gte=data['min_seats'])
        
        if data.get('max_seats'):
            queryset = queryset.filter(seats__lte=data['max_seats'])
        
        if data.get('min_price'):
            queryset = queryset.filter(price_per_day__gte=data['min_price'])
        
        if data.get('max_price'):
            queryset = queryset.filter(price_per_day__lte=data['max_price'])
        
        # Date availability filter
        if data.get('pickup_date') and data.get('dropoff_date'):
            queryset = queryset.filter(
                availability__start_date__lte=data['pickup_date'],
                availability__end_date__gte=data['dropoff_date'],
                availability__is_available=True
            ).distinct()
        
        # Apply sorting
        sort_by = data.get('sort_by', 'created_desc')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price_per_day')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price_per_day')
        elif sort_by == 'seats_asc':
            queryset = queryset.order_by('seats')
        elif sort_by == 'seats_desc':
            queryset = queryset.order_by('-seats')
        elif sort_by == 'year_desc':
            queryset = queryset.order_by('-year')
        elif sort_by == 'year_asc':
            queryset = queryset.order_by('year')
        elif sort_by == 'created_desc':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'created_asc':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'created_at_desc':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'created_at_asc':
            queryset = queryset.order_by('created_at')
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def check_availability(self, request, slug=None):
        """Check availability for specific dates using slug."""
        car_rental = self.get_object()
        serializer = CarRentalAvailabilityCheckSerializer(
            data=request.data, 
            context={'car_rental': car_rental, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        return Response({
            'available': True,
            'car_rental': CarRentalDetailSerializer(car_rental, context={'request': request}).data,
            'pickup_date': data['pickup_date'],
            'dropoff_date': data['dropoff_date'],
            'rental_days': data['rental_days'],
            'rental_hours': data['rental_hours'],
            'total_hours': data['total_hours'],
            'total_price': str(data['total_price']),
            'currency': car_rental.currency,
            'availability_id': data['availability'].id,
            'pricing_breakdown': {
                'base_price': str(data['total_price']),
                'daily_rate': str(car_rental.price_per_day),
                'hourly_rate': str(car_rental.price_per_hour or 0),
                'weekly_discount': str(car_rental.weekly_discount_percentage),
                'monthly_discount': str(car_rental.monthly_discount_percentage),
                'rental_type': 'hourly' if data['rental_days'] == 0 else 'daily'
            }
        })
    
    
    @action(detail=True, methods=['get'])
    def availability_calendar(self, request, slug=None):
        """Get availability calendar for a car rental."""
        car_rental = self.get_object()
        availability = car_rental.availability.filter(is_available=True).order_by('start_date')
        
        serializer = CarRentalAvailabilitySerializer(availability, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def options(self, request, slug=None):
        """Get available options for a car rental."""
        car_rental = self.get_object()
        options = CarRentalOption.objects.filter(is_active=True).order_by('option_type', 'translations__name')
        
        serializer = CarRentalOptionSerializer(options, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured car rentals."""
        queryset = self.get_queryset().filter(is_featured=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular car rentals."""
        queryset = self.get_queryset().filter(is_popular=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def quick_info(self, request, slug=None):
        """Get quick info for a car rental."""
        try:
            car_rental = self.get_object()
            serializer = self.get_serializer(car_rental)
            return Response(serializer.data)
        except CarRental.DoesNotExist:
            return Response(
                {'error': 'Car rental not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class CarRentalBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for CarRentalBooking model."""
    
    serializer_class = CarRentalBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['booking_reference', 'driver_name', 'driver_email']
    filterset_fields = ['status', 'car_rental', 'pickup_date', 'dropoff_date']
    ordering_fields = ['created_at', 'pickup_date', 'total_price']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get bookings for the current user."""
        return CarRentalBooking.objects.filter(user=self.request.user).select_related(
            'car_rental', 'car_rental__category'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CarRentalBookingCreateSerializer
        return CarRentalBookingSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new car rental booking."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        car_rental = data['car_rental']
        availability = data['availability']
        rental_days = data['rental_days']
        
        # Calculate pricing
        base_price = car_rental.calculate_total_price(rental_days)
        options_total = Decimal('0.00')
        insurance_total = Decimal('0.00')
        
        # Calculate options total
        selected_options = data.get('selected_options', [])
        for option_data in selected_options:
            option_id = option_data.get('id')
            quantity = option_data.get('quantity', 1)
            
            try:
                option = CarRentalOption.objects.get(id=option_id, is_active=True)
                option_price = option.calculate_price(base_price, rental_days, quantity)
                options_total += option_price
            except CarRentalOption.DoesNotExist:
                pass
        
        # Calculate insurance total
        if data.get('comprehensive_insurance', False):
            insurance_total = car_rental.comprehensive_insurance_price * rental_days
        
        total_price = base_price + options_total + insurance_total
        
        # Reserve availability
        if not availability.reserve_quantity(1):
            return Response({
                'error': 'No availability for the selected dates'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Create booking
                booking = CarRentalBooking.objects.create(
                    car_rental=car_rental,
                    user=request.user,
                    pickup_date=data['pickup_date'],
                    dropoff_date=data['dropoff_date'],
                    pickup_time=data['pickup_time'],
                    dropoff_time=data['dropoff_time'],
                    total_days=rental_days,
                    daily_rate=car_rental.price_per_day,
                    hourly_rate=car_rental.price_per_hour,
                    base_price=base_price,
                    options_total=options_total,
                    insurance_total=insurance_total,
                    deposit_amount=car_rental.deposit_amount,
                    total_price=total_price,
                    currency=car_rental.currency,
                    driver_name=data['driver_name'],
                    driver_license=data['driver_license'],
                    driver_phone=data['driver_phone'],
                    driver_email=data['driver_email'],
                    additional_drivers=data.get('additional_drivers', []),
                    selected_options=selected_options,
                    basic_insurance=data.get('basic_insurance', True),
                    comprehensive_insurance=data.get('comprehensive_insurance', False),
                    special_requirements=data.get('special_requirements', ''),
                    availability=availability,
                    status='pending'
                )
                
                # Add to cart/order system
                from cart.services import CartService
                from cart.models import CartItem
                
                cart = CartService.get_or_create_cart(
                    session_id=CartService.get_session_id(request),
                    user=request.user
                )
                
                # Create cart item
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product_type='car_rental',
                    product_id=str(car_rental.id),
                    booking_date=data['pickup_date'],
                    booking_time=data['pickup_time'],
                    quantity=1,
                    unit_price=total_price,
                    total_price=total_price,
                    currency=car_rental.currency,
                    selected_options=selected_options,
                    options_total=options_total,
                    booking_data={
                        'car_rental_id': str(car_rental.id),
                        'pickup_date': data['pickup_date'].isoformat(),
                        'dropoff_date': data['dropoff_date'].isoformat(),
                        'pickup_time': data['pickup_time'].isoformat(),
                        'dropoff_time': data['dropoff_time'].isoformat(),
                        'rental_days': rental_days,
                        'driver_name': data['driver_name'],
                        'driver_license': data['driver_license'],
                        'driver_phone': data['driver_phone'],
                        'driver_email': data['driver_email'],
                        'additional_drivers': data.get('additional_drivers', []),
                        'basic_insurance': data.get('basic_insurance', True),
                        'comprehensive_insurance': data.get('comprehensive_insurance', False),
                        'special_requirements': data.get('special_requirements', ''),
                        'availability_id': str(availability.id)
                    }
                )
                
                response_serializer = CarRentalBookingSerializer(booking, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            # Release availability if booking fails
            availability.release_quantity(1)
            return Response({
                'error': f'Booking creation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_car_rental_availability(request, slug):
    """Check car rental availability by slug."""
    try:
        car_rental = CarRental.objects.get(slug=slug, is_active=True, is_available=True)
    except CarRental.DoesNotExist:
        return Response({
            'error': 'Car rental not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CarRentalAvailabilityCheckSerializer(
        data=request.data, 
        context={'car_rental': car_rental, 'request': request}
    )
    serializer.is_valid(raise_exception=True)
    
    data = serializer.validated_data
    
    return Response({
        'available': True,
        'car_rental': CarRentalDetailSerializer(car_rental, context={'request': request}).data,
        'pickup_date': data['pickup_date'],
        'dropoff_date': data['dropoff_date'],
        'rental_days': data['rental_days'],
        'rental_hours': data['rental_hours'],
        'total_hours': data['total_hours'],
        'total_price': str(data['total_price']),
        'currency': car_rental.currency,
        'availability_id': data['availability'].id,
        'pricing_breakdown': {
            'base_price': str(data['base_price']),
            'insurance_price': str(data['insurance_price']),
            'options_price': '0.00',  # Options calculated by frontend based on selected options
            'total_price': str(data['total_price'])
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def car_rental_filters(request):
    """Get available filters for car rentals."""
    from django.db.models import Count, Min, Max
    
    # Get filter options
    categories = CarRentalCategory.objects.filter(is_active=True).values_list('id', 'translations__name')
    brands = CarRental.objects.filter(is_active=True).values_list('brand', flat=True).distinct()
    cities = CarRental.objects.filter(is_active=True).values_list('city', flat=True).distinct()
    countries = CarRental.objects.filter(is_active=True).values_list('country', flat=True).distinct()
    
    # Get price range
    price_range = CarRental.objects.filter(is_active=True).aggregate(
        min_price=Min('price_per_day'),
        max_price=Max('price_per_day')
    )
    
    # Get seat range
    seat_range = CarRental.objects.filter(is_active=True).aggregate(
        min_seats=Min('seats'),
        max_seats=Max('seats')
    )
    
    return Response({
        'categories': [{'id': cat[0], 'name': cat[1]} for cat in categories if cat[1]],
        'brands': list(brands),
        'cities': list(cities),
        'countries': list(countries),
        'fuel_types': [choice[0] for choice in CarRental.FUEL_TYPE_CHOICES],
        'transmissions': [choice[0] for choice in CarRental.TRANSMISSION_CHOICES],
        'price_range': price_range,
        'seat_range': seat_range
    })
