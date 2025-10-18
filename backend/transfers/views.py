"""
Views for transfers app.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from decimal import Decimal

from .models import TransferRoute, TransferRoutePricing, TransferOption, TransferBooking, TransferLocation
from .serializers import (
    TransferRouteSerializer, TransferRouteDetailSerializer,
    TransferBookingSerializer, TransferBookingCreateSerializer,
    TransferSearchSerializer, TransferPriceCalculationSerializer,
    TransferPriceResponseSerializer, PopularRouteSerializer,
    TransferOptionSerializer, TransferLocationSerializer,
)
from .services import TransferPricingService
import math
import requests


class TransferLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for transfer locations with map integration.
    """
    
    queryset = TransferLocation.objects.filter(is_active=True)
    serializer_class = TransferLocationSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city', 'country', 'location_type', 'is_popular']
    search_fields = ['translations__name', 'address', 'city', 'country']
    ordering = ['city', 'country', 'id']
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular locations."""
        popular_locations = self.queryset.filter(is_popular=True)
        serializer = self.get_serializer(popular_locations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search_by_coordinates(self, request):
        """Search locations by coordinates radius."""
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        radius_km = request.data.get('radius_km', 10)
        
        if not lat or not lng:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(lat)
            lng = float(lng)
            radius_km = float(radius_km)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinate values'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simple bounding box search (can be improved with PostGIS)
        lat_range = radius_km / 111.0  # Approximate km per degree
        lng_range = radius_km / (111.0 * math.cos(math.radians(lat)))
        
        locations = self.queryset.filter(
            latitude__range=[lat - lat_range, lat + lat_range],
            longitude__range=[lng - lng_range, lng + lng_range]
        )
        
        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reverse_geocode(self, request):
        """تبدیل مختصات به آدرس با استفاده از Nominatim"""
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        
        if not lat or not lng:
            return Response(
                {'error': 'Latitude and longitude are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinate values'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # استفاده از Nominatim برای reverse geocoding
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json',
                'addressdetails': 1,
                'accept-language': 'en,tr',  # اولویت زبان انگلیسی و ترکی
            }
            headers = {
                'User-Agent': 'PeykanTourism/1.0'  # مطابق با قوانین Nominatim
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # استخراج اطلاعات مفید
                address_parts = data.get('address', {})
                display_name = data.get('display_name', '')
                
                # تشخیص نوع مکان
                location_type = 'custom'
                if any(key in address_parts for key in ['hotel', 'motel', 'guest_house']):
                    location_type = 'hotel'
                elif any(key in address_parts for key in ['aerodrome', 'airport']):
                    location_type = 'airport'
                elif any(key in address_parts for key in ['railway', 'station']):
                    location_type = 'station'
                elif any(key in address_parts for key in ['attraction', 'tourism']):
                    location_type = 'landmark'
                
                # ایجاد نام مناسب
                name = (
                    address_parts.get('hotel') or
                    address_parts.get('aerodrome') or
                    address_parts.get('attraction') or
                    address_parts.get('building') or
                    address_parts.get('house_name') or
                    address_parts.get('road', '') + ' ' + address_parts.get('house_number', '')
                ).strip()
                
                if not name:
                    # اگر نام مشخصی نداشت، از بخش‌های آدرس استفاده کن
                    name_parts = [
                        address_parts.get('road'),
                        address_parts.get('neighbourhood'),
                        address_parts.get('suburb')
                    ]
                    name = ', '.join(filter(None, name_parts)) or 'مکان انتخاب شده'
                
                return Response({
                    'name': name,
                    'address': display_name,
                    'city': address_parts.get('city') or address_parts.get('town') or address_parts.get('village', ''),
                    'country': address_parts.get('country', ''),
                    'location_type': location_type,
                    'coordinates': {'lat': lat, 'lng': lng},
                    'raw_data': data  # برای دیباگ
                })
            else:
                return Response(
                    {'error': 'Geocoding service unavailable'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
                
        except requests.RequestException as e:
            return Response(
                {'error': f'Geocoding request failed: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': f'Reverse geocoding failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def check_route_availability(self, request):
        """بررسی وجود مسیر بین دو مکان"""
        origin_id = request.data.get('origin_id')
        destination_id = request.data.get('destination_id')
        origin_name = request.data.get('origin_name')
        destination_name = request.data.get('destination_name')
        
        if not ((origin_id and destination_id) or (origin_name and destination_name)):
            return Response(
                {'error': 'Origin and destination IDs or names are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # جستجو بر اساس ID مکان‌ها
            route = None
            if origin_id and destination_id:
                route = TransferRoute.objects.filter(
                    origin_location_id=origin_id,
                    destination_location_id=destination_id,
                    is_active=True
                ).first()
            
            # جستجو بر اساس نام مکان‌ها (fallback)
            if not route and origin_name and destination_name:
                route = TransferRoute.objects.filter(
                    origin__iexact=origin_name,
                    destination__iexact=destination_name,
                    is_active=True
                ).first()
            
            if route:
                # دریافت قیمت‌گذاری‌های موجود
                pricing = TransferRoutePricing.objects.filter(
                    route=route,
                    is_active=True
                )
                
                serializer = TransferRouteDetailSerializer(route)
                return Response({
                    'route_exists': True,
                    'route': serializer.data,
                    'available_vehicles': len(pricing)
                })
            else:
                return Response({
                    'route_exists': False,
                    'message': 'No route found for this origin-destination combination'
                })
                
        except Exception as e:
            return Response(
                {'error': f'Route check failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def validate_location(self, request):
        """اعتبارسنجی مکان برای ترانسفر"""
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        name = request.data.get('name', '')
        
        if not lat or not lng:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinate values'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # بررسی محدوده جغرافیایی (ترکیه و استانبول)
        if not (40.5 <= lat <= 41.5 and 28.0 <= lng <= 30.0):
            return Response({
                'is_valid': False,
                'reason': 'out_of_service_area',
                'message': 'This location is outside our service area',
                'suggestion': 'Please select locations in Istanbul and surrounding areas'
            })
        
        # بررسی مکان‌های غیرقابل دسترس (دریا، کوه‌های مرتفع)
        try:
            # استفاده از Nominatim برای بررسی نوع مکان
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json',
                'addressdetails': 1,
                'accept-language': 'en,tr',
            }
            headers = {
                'User-Agent': 'PeykanTourism/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                address_parts = data.get('address', {})
                
                # بررسی مکان‌های غیرقابل دسترس
                if any(key in address_parts for key in ['sea', 'ocean', 'water', 'lake']):
                    return Response({
                        'is_valid': False,
                        'reason': 'water_location',
                        'message': 'Water location selection is not possible',
                        'suggestion': 'Please select locations on land'
                    })
                
                # بررسی مکان‌های کوهستانی مرتفع
                if any(key in address_parts for key in ['mountain', 'peak', 'ridge']):
                    return Response({
                        'is_valid': False,
                        'reason': 'mountainous_location',
                        'message': 'This location is in mountainous area and difficult to access',
                        'suggestion': 'Please select locations in urban or accessible areas'
                    })
                
                # بررسی مکان‌های مناسب برای ترانسفر
                suitable_types = ['hotel', 'aerodrome', 'airport', 'railway', 'station', 'attraction', 'tourism', 'building', 'house']
                if any(key in address_parts for key in suitable_types):
                    return Response({
                        'is_valid': True,
                        'message': 'Location is suitable for transfer',
                        'location_type': 'suitable'
                    })
                
                # مکان‌های عمومی (جاده، محله)
                return Response({
                    'is_valid': True,
                    'message': 'Location is accessible',
                    'location_type': 'general',
                    'warning': 'This location may not be suitable for transfer'
                })
                
            else:
                # در صورت عدم دسترسی به Nominatim، بررسی ساده انجام دهیم
                return Response({
                    'is_valid': True,
                    'message': 'مکان در محدوده جغرافیایی مناسب است',
                    'location_type': 'unknown',
                    'warning': 'نوع مکان مشخص نشد'
                })
                
        except requests.RequestException:
            # در صورت خطا در Nominatim، بررسی ساده انجام دهیم
            return Response({
                'is_valid': True,
                'message': 'مکان در محدوده جغرافیایی مناسب است',
                'location_type': 'unknown',
                'warning': 'نوع مکان مشخص نشد'
            })
        except Exception as e:
            return Response(
                {'error': f'Location validation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def search_locations(self, request):
        """جستجوی پیشرفته مکان‌ها"""
        query = request.data.get('query', '').strip()
        location_type = request.data.get('location_type', '')
        city = request.data.get('city', '')
        
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # جستجو در مکان‌های موجود
            locations = self.queryset.filter(
                Q(translations__name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
            
            if location_type:
                locations = locations.filter(location_type=location_type)
            
            if city:
                locations = locations.filter(city__icontains=city)
            
            # محدود کردن نتایج
            locations = locations[:20]
            
            serializer = self.get_serializer(locations, many=True)
            
            # جستجو در Nominatim برای مکان‌های جدید
            try:
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': query,
                    'format': 'json',
                    'addressdetails': 1,
                    'limit': 10,
                    'accept-language': 'en,tr',
                    'countrycodes': 'tr',  # ترکیه
                }
                headers = {
                    'User-Agent': 'PeykanTourism/1.0'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    nominatim_results = response.json()
                    
                    # تبدیل نتایج Nominatim به فرمت مکان
                    external_locations = []
                    for item in nominatim_results:
                        if item.get('lat') and item.get('lon'):
                            address_parts = item.get('address', {})
                            
                            # بررسی محدوده جغرافیایی
                            lat = float(item['lat'])
                            lng = float(item['lon'])
                            
                            if 40.5 <= lat <= 41.5 and 28.0 <= lng <= 30.0:
                                external_locations.append({
                                    'id': f"external-{item['place_id']}",
                                    'name': item.get('display_name', ''),
                                    'address': item.get('display_name', ''),
                                    'city': address_parts.get('city') or address_parts.get('town') or address_parts.get('village', ''),
                                    'country': address_parts.get('country', ''),
                                    'coordinates': {'lat': lat, 'lng': lng},
                                    'location_type': 'external',
                                    'is_active': True,
                                    'is_popular': False,
                                    'source': 'nominatim'
                                })
                    
                    return Response({
                        'database_locations': serializer.data,
                        'external_locations': external_locations,
                        'total_results': len(serializer.data) + len(external_locations)
                    })
                else:
                    return Response({
                        'database_locations': serializer.data,
                        'external_locations': [],
                        'total_results': len(serializer.data)
                    })
                    
            except requests.RequestException:
                return Response({
                    'database_locations': serializer.data,
                    'external_locations': [],
                    'total_results': len(serializer.data)
                })
                
        except Exception as e:
            return Response(
                {'error': f'Search failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def create_test_locations(self, request):
        """ایجاد مکان‌های تستی استانبول"""
        try:
            # مکان‌های تستی استانبول
            test_locations = [
                {
                    'name': 'Istanbul New Airport (IST)',
                    'address': 'Tayakadın, Terminal Caddesi No:1, 34283 Arnavutköy/İstanbul',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'latitude': 41.2753,
                    'longitude': 28.7519,
                    'location_type': 'airport',
                    'is_popular': True,
                    'is_active': True
                },
                {
                    'name': 'Sabiha Gökçen Airport (SAW)',
                    'address': 'Sanayi Mahallesi, Sabiha Gökçen Havalimanı, 34912 Pendik/İstanbul',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'latitude': 40.8986,
                    'longitude': 29.3092,
                    'location_type': 'airport',
                    'is_popular': True,
                    'is_active': True
                },
                {
                    'name': 'Hilton Istanbul Bomonti',
                    'address': 'Silahşör Caddesi No:42, 34381 Şişli/İstanbul',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'latitude': 41.0608,
                    'longitude': 28.9856,
                    'location_type': 'hotel',
                    'is_popular': True,
                    'is_active': True
                },
                {
                    'name': 'Hilton Istanbul Bosphorus',
                    'address': 'Cumhuriyet Caddesi No:50, 34367 Harbiye/İstanbul',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'latitude': 41.0478,
                    'longitude': 28.9856,
                    'location_type': 'hotel',
                    'is_popular': True,
                    'is_active': True
                },
                {
                    'name': 'Taksim Square',
                    'address': 'Taksim Meydanı, 34437 Beyoğlu/İstanbul',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'latitude': 41.0370,
                    'longitude': 28.9850,
                    'location_type': 'landmark',
                    'is_popular': True,
                    'is_active': True
                },
                {
                    'name': 'Beşiktaş',
                    'address': 'Beşiktaş, İstanbul',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'latitude': 41.0425,
                    'longitude': 29.0086,
                    'location_type': 'district',
                    'is_popular': True,
                    'is_active': True
                },
                {
                    'name': 'Kadıköy',
                    'address': 'Kadıköy, İstanbul',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'latitude': 40.9900,
                    'longitude': 29.0244,
                    'location_type': 'district',
                    'is_popular': True,
                    'is_active': True
                },
                {
                    'name': 'Sultanahmet',
                    'address': 'Sultanahmet, Fatih/İstanbul',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'latitude': 41.0082,
                    'longitude': 28.9784,
                    'location_type': 'landmark',
                    'is_popular': True,
                    'is_active': True
                }
            ]
            
            created_locations = []
            for location_data in test_locations:
                # بررسی وجود مکان
                existing_location = TransferLocation.objects.filter(
                    name=location_data['name'],
                    city=location_data['city']
                ).first()
                
                if not existing_location:
                    location = TransferLocation.objects.create(
                        name=location_data['name'],
                        address=location_data['address'],
                        city=location_data['city'],
                        country=location_data['country'],
                        latitude=location_data['latitude'],
                        longitude=location_data['longitude'],
                        location_type=location_data['location_type'],
                        is_popular=location_data['is_popular'],
                        is_active=location_data['is_active']
                    )
                    created_locations.append(location)
                else:
                    created_locations.append(existing_location)
            
            serializer = self.get_serializer(created_locations, many=True)
            return Response({
                'message': f'{len(created_locations)} test locations created/updated',
                'locations': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create test locations: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransferOptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for transfer options.
    """
    queryset = TransferOption.objects.filter(is_active=True)
    serializer_class = TransferOptionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['option_type', 'route', 'vehicle_type']
    search_fields = ['name', 'description']
    ordering = ['option_type', 'name']


class TransferRouteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for transfer routes.
    """
    queryset = TransferRoute.objects.filter(is_active=True).prefetch_related('pricing')
    serializer_class = TransferRouteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['origin', 'destination', 'is_popular']
    search_fields = ['origin', 'destination']
    ordering_fields = ['origin', 'destination', 'created_at']
    ordering = ['origin']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TransferRouteDetailSerializer
        elif self.action == 'popular':
            return PopularRouteSerializer
        return TransferRouteSerializer
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular transfer routes."""
        popular_routes = self.queryset.filter(is_popular=True)[:6]
        serializer = self.get_serializer(popular_routes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_routes(self, request):
        """Get all available transfer routes."""
        routes = self.get_queryset()
        serializer = self.get_serializer(routes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search transfer routes."""
        search_serializer = TransferSearchSerializer(data=request.data)
        if search_serializer.is_valid():
            data = search_serializer.validated_data
            queryset = self.get_queryset()
            
            # Apply filters
            if data.get('query'):
                queryset = queryset.filter(
                    Q(origin__icontains=data['query']) |
                    Q(destination__icontains=data['query'])
                )
            
            if data.get('origin'):
                queryset = queryset.filter(origin__icontains=data['origin'])
            
            if data.get('destination'):
                queryset = queryset.filter(destination__icontains=data['destination'])
            
            if data.get('vehicle_type'):
                queryset = queryset.filter(pricing__vehicle_type=data['vehicle_type'])
            
            if data.get('min_price'):
                queryset = queryset.filter(pricing__base_price__gte=data['min_price'])
            
            if data.get('max_price'):
                queryset = queryset.filter(pricing__base_price__lte=data['max_price'])
            
            # Apply sorting
            sort_by = data.get('sort_by', 'origin')
            if sort_by == 'price_asc':
                queryset = queryset.order_by('pricing__base_price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-pricing__base_price')
            elif sort_by == 'origin':
                queryset = queryset.order_by('origin')
            
            # Paginate results
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_slug(self, request, slug=None):
        """Get transfer route by slug."""
        try:
            route = TransferRoute.objects.get(slug=slug, is_active=True)
            serializer = self.get_serializer(route)
            return Response(serializer.data)
        except TransferRoute.DoesNotExist:
            return Response(
                {'error': 'Transfer route not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def calculate_price(self, request, pk=None):
        """Calculate transfer price."""
        route = self.get_object()
        
        # Add route to request data
        data = request.data.copy()
        data['route_id'] = str(route.id)
        
        calculation_serializer = TransferPriceCalculationSerializer(data=data)
        if calculation_serializer.is_valid():
            validated_data = calculation_serializer.validated_data
            
            # Use the service to calculate price
            try:
                price_data = TransferPricingService.calculate_price(
                    route=validated_data['route'],
                    pricing=validated_data['pricing'],
                    booking_time=validated_data['booking_time'],
                    return_time=validated_data.get('return_time'),
                    selected_options=validated_data.get('selected_options', [])
                )
                
                response_serializer = TransferPriceResponseSerializer(data=price_data)
                if response_serializer.is_valid():
                    return Response(response_serializer.data)
                else:
                    return Response(
                        {'error': 'Price calculation failed'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(calculation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TransferBookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for transfer bookings.
    """
    serializer_class = TransferBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'trip_type']
    ordering_fields = ['created_at', 'outbound_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter bookings by user."""
        return TransferBooking.objects.filter(user=self.request.user).select_related('route', 'pricing')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransferBookingCreateSerializer
        return TransferBookingSerializer
    
    def perform_create(self, serializer):
        """Create booking with user."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        
        if booking.status == 'cancelled':
            return Response(
                {'error': 'Booking is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.status == 'completed':
            return Response(
                {'error': 'Cannot cancel completed booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings."""
        from datetime import date
        today = date.today()
        
        upcoming_bookings = self.get_queryset().filter(
            outbound_date__gte=today,
            status__in=['pending', 'confirmed']
        )
        
        serializer = self.get_serializer(upcoming_bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get booking history."""
        from datetime import date
        today = date.today()
        
        history_bookings = self.get_queryset().filter(
            Q(outbound_date__lt=today) | Q(status__in=['cancelled', 'completed'])
        )
        
        serializer = self.get_serializer(history_bookings, many=True)
        return Response(serializer.data)


class TransferBookingAPIView(APIView):
    """
    Agent-only transfer booking API using unified booking service
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a transfer booking - AGENT ONLY"""
        try:
            # This API is only for agents
            if request.user.role != 'agent':
                return Response(
                    {'error': 'This endpoint is only for agents'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            from .booking_service import TransferBookingService
            
            # For agent bookings, customer_id should be provided
            customer_id = request.data.get('customer_id')
            if not customer_id:
                return Response(
                    {'error': 'Customer not selected. Please select a customer before booking.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find the customer
            from agents.models import AgentCustomer
            agent_customer = request.user.agent_customers.filter(customer__id=customer_id).first()
            if not agent_customer:
                return Response(
                    {'error': 'Customer not found or not associated with this agent'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Use the customer as the booking user
            booking_user = agent_customer.customer
            agent = request.user
            
            # Use the unified booking service
            result = TransferBookingService.book_transfer(
                user=booking_user,
                transfer_data=request.data,
                agent=agent
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