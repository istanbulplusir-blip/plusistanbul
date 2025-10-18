"""
DRF Views for Events app.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Min, Max
from django.utils.translation import gettext_lazy as _
from .models import (
    Event, EventCategory, Venue, Artist, TicketType, 
    EventPerformance, Seat, EventOption, EventReview,
    EventSection, SectionTicketType, EventDiscount, EventFee, EventPricingRule
)
from .serializers import (
    EventListSerializer, EventDetailSerializer, EventSearchSerializer,
    EventCategorySerializer, VenueSerializer, ArtistSerializer,
    EventReviewSerializer, EventReviewCreateSerializer, EventBookingSerializer,
    EventSectionSerializer, SectionTicketTypeSerializer,
    EventPricingCalculatorSerializer, EventDiscountSerializer, EventFeeSerializer,
    EventPricingRuleSerializer
)
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.http import Http404
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
import json
from rest_framework.decorators import api_view
from .tasks import (
    cleanup_expired_reservations, 
    update_capacity_cache, 
    validate_capacity_consistency,
    emergency_capacity_cleanup
)


class EventCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for EventCategory model."""
    
    queryset = EventCategory.objects.filter(is_active=True)
    serializer_class = EventCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['translations__name', 'translations__description']
    ordering_fields = ['translations__name', 'created_at']
    ordering = ['translations__name']


class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Venue model."""
    
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['translations__name', 'translations__description', 'translations__address', 'city', 'country']
    ordering_fields = ['translations__name', 'city', 'total_capacity']
    filterset_fields = ['city', 'country']
    ordering = ['translations__name']


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Artist model."""
    
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['translations__name', 'translations__bio']
    ordering_fields = ['translations__name', 'created_at']
    ordering = ['translations__name']


class EventSectionViewSet(viewsets.ModelViewSet):
    """ViewSet for EventSection management."""
    
    queryset = EventSection.objects.all()
    serializer_class = EventSectionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filter sections by performance."""
        queryset = super().get_queryset()
        performance_id = self.request.query_params.get('performance_id')
        if performance_id:
            queryset = queryset.filter(performance_id=performance_id)
        return queryset.select_related('performance')


class SectionTicketTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for SectionTicketType management."""
    
    queryset = SectionTicketType.objects.all()
    serializer_class = SectionTicketTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filter by section."""
        queryset = super().get_queryset()
        section_id = self.request.query_params.get('section_id')
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        return queryset.select_related('section', 'ticket_type')


class EventCapacityViewSet(viewsets.ViewSet):
    """ViewSet for capacity management operations."""
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get capacity summary for an event."""
        try:
            event = Event.objects.get(pk=pk)
            performances = event.performances.all()
            
            summary = {
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'total_performances': performances.count()
                },
                'performances': []
            }
            
            for performance in performances:
                from events.capacity_manager import CapacityManager
                performance_summary = CapacityManager.get_capacity_summary(performance)
                summary['performances'].append(performance_summary)
            
            return Response(summary)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def reserve_seats(self, request, pk=None):
        """Reserve seats for a performance."""
        try:
            performance = EventPerformance.objects.get(pk=pk)
            
            # Validate request data
            ticket_type_id = request.data.get('ticket_type_id')
            section_name = request.data.get('section_name')
            count = request.data.get('count', 1)
            
            if not all([ticket_type_id, section_name, count]):
                return Response(
                    {'error': 'Missing required fields: ticket_type_id, section_name, count'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reserve seats
            from events.capacity_manager import CapacityManager
            success, result = CapacityManager.reserve_seats(
                performance, ticket_type_id, section_name, count
            )
            
            if success:
                return Response({
                    'message': f'Successfully reserved {count} seats',
                    'section_ticket': SectionTicketTypeSerializer(result).data
                })
            else:
                return Response(
                    {'error': result}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except EventPerformance.DoesNotExist:
            return Response(
                {'error': 'Performance not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """Get available seats for a performance."""
        try:
            performance = EventPerformance.objects.get(pk=pk)
            
            # Get filters
            ticket_type_id = request.query_params.get('ticket_type_id')
            section_name = request.query_params.get('section_name')
            
            # Get available seats
            from events.capacity_manager import CapacityManager
            available_seats = CapacityManager.get_available_seats(
                performance, ticket_type_id, section_name
            )
            
            return Response({
                'performance_id': performance.id,
                'available_seats': SectionTicketTypeSerializer(available_seats, many=True).data
            })
            
        except EventPerformance.DoesNotExist:
            return Response(
                {'error': 'Performance not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for Event model."""
    
    serializer_class = EventDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['category', 'venue', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'date', 'price']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventDetailSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['hold_seats', 'release_seats', 'performance_seats', 'calculate_pricing']:
            # Allow anonymous users to hold/release seats, view performance seats, and calculate pricing
            permission_classes = [AllowAny]
        else:
            # Use default permissions for other actions
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Get queryset with proper filtering and optimization."""
        queryset = Event.objects.filter(is_active=True).select_related(
            'category', 'venue'
        ).prefetch_related(
            'artists',
            'ticket_types',
            'options',
            'reviews',
            # Optimized performance and section prefetching
            'performances',
            'performances__sections',
            'performances__sections__ticket_types',
            'performances__sections__ticket_types__ticket_type'
        )
        
        # Apply filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        venue = self.request.query_params.get('venue')
        if venue:
            queryset = queryset.filter(venue__slug=venue)
        
        # Add date filtering for performances
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(performances__date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(performances__date__lte=date_to)
        
        # Add style filtering
        style = self.request.query_params.get('style')
        if style:
            queryset = queryset.filter(style=style)
        
        # New event type filters for home page categorization
        event_type = self.request.query_params.get('type')
        if event_type:
            today = timezone.now().date()
            if event_type == 'upcoming':
                queryset = queryset.filter(performances__date__gte=today)
            elif event_type == 'past':
                queryset = queryset.filter(performances__date__lt=today)
            elif event_type == 'special':
                queryset = queryset.filter(performances__is_special=True)
            elif event_type == 'featured':
                queryset = queryset.filter(is_featured=True)
            elif event_type == 'popular':
                queryset = queryset.filter(is_popular=True)
        
        # Ensure distinct results when filtering by performances
        if date_from or date_to or event_type in ['upcoming', 'past', 'special']:
            queryset = queryset.distinct()
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def capacity_info(self, request, pk=None):
        """Get detailed capacity information for an event with optimized queries."""
        try:
            event = self.get_object()
            
            # Use optimized queries with proper select_related and prefetch_related
            performances = event.performances.select_related(
                'event'
            ).prefetch_related(
                'sections__ticket_types__ticket_type'
            ).all()
            
            capacity_info = {
                'event_id': event.id,
                'event_title': event.title,
                'total_performances': performances.count(),
                'performances': []
            }
            
            for performance in performances:
                try:
                    # Use cached properties to avoid additional queries
                    performance_info = {
                        'id': performance.id,
                        'date': performance.date,
                        'start_time': performance.start_time,
                        'end_time': performance.end_time,
                        'is_available': performance.is_available,
                        'total_sections': performance.sections.count(),
                        'sections': []
                    }
                    
                    # Process sections with their ticket types
                    for section in performance.sections.all():
                        try:
                            section_info = {
                                'name': section.name,
                                'description': section.description,
                                'total_capacity': section.total_capacity,
                                'available_capacity': section.available_capacity,
                                'reserved_capacity': section.reserved_capacity,
                                'sold_capacity': section.sold_capacity,
                                'occupancy_rate': section.occupancy_rate,
                                'is_premium': section.is_premium,
                                'is_wheelchair_accessible': section.is_wheelchair_accessible,
                                'ticket_types': []
                            }
                            
                            # Process ticket types for this section
                            for stt in section.ticket_types.all():
                                try:
                                    ticket_info = {
                                        'id': stt.ticket_type.id,
                                        'name': stt.ticket_type.name,
                                        'description': stt.ticket_type.description,
                                        'allocated_capacity': stt.allocated_capacity,
                                        'available_capacity': stt.available_capacity,
                                        'reserved_capacity': stt.reserved_capacity,
                                        'sold_capacity': stt.sold_capacity,
                                        'price_modifier': stt.price_modifier,
                                        'final_price': stt.final_price
                                    }
                                    section_info['ticket_types'].append(ticket_info)
                                except Exception as e:
                                    # Log error but continue processing other ticket types
                                    import logging
                                    logger = logging.getLogger(__name__)
                                    logger.error(f"Error processing ticket type {stt.id}: {e}")
                                    continue
                            
                            performance_info['sections'].append(section_info)
                        except Exception as e:
                            # Log error but continue processing other sections
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Error processing section {section.name}: {e}")
                            continue
                    
                    capacity_info['performances'].append(performance_info)
                except Exception as e:
                    # Log error but continue processing other performances
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing performance {performance.id}: {e}")
                    continue
            
            return Response(capacity_info)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Log unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in capacity_info: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search events with advanced filters."""
        queryset = self.get_queryset()
        
        # Search query
        query = request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(venue__name__icontains=query) |
                Q(artists__name__icontains=query)
            ).distinct()
        
        # Date filters
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(performances__date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(performances__date__lte=date_to)
        
        # Price filters
        min_price = request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(performances__sections__base_price__gte=min_price)
        
        max_price = request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(performances__sections__base_price__lte=max_price)
        
        # Style filter
        style = request.query_params.get('style')
        if style:
            queryset = queryset.filter(style=style)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def performances(self, request, pk=None):
        """Get all performances for an event."""
        try:
            event = self.get_object()
            performances = event.performances.all().order_by('date', 'start_time')
            
            serializer = EventDetailSerializer(performances, many=True)
            return Response(serializer.data)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], url_path='performances/(?P<performance_pk>[^/.]+)/seats')
    def performance_seats(self, request, pk=None, performance_pk=None):
        """Get available seats for a specific performance with optimized queries."""
        try:
            # Use select_related for better performance
            performance = EventPerformance.objects.select_related('event').get(id=performance_pk)
            
            # Get filters
            section_name = request.query_params.get('section')
            ticket_type_id = request.query_params.get('ticket_type_id')
            include_seats = request.query_params.get('include_seats') in ['1', 'true', 'True']
            
            # Get sections and their ticket types with optimized prefetch_related
            sections_data = []
            
            # Build optimized query
            sections_qs = performance.sections.prefetch_related(
                'ticket_types__ticket_type'
            )
            
            if section_name:
                sections_qs = sections_qs.filter(name=section_name)
            
            for section in sections_qs.all():
                try:
                    section_data = {
                        'name': section.name,
                        'description': section.description,
                        'base_price': section.base_price,
                        'total_capacity': section.total_capacity,
                        'available_capacity': section.available_capacity,
                        'reserved_capacity': section.reserved_capacity,
                        'sold_capacity': section.sold_capacity,
                        'occupancy_rate': section.occupancy_rate,
                        'is_premium': section.is_premium,
                        'is_wheelchair_accessible': section.is_wheelchair_accessible,
                        'ticket_types': []
                    }
                    
                    # Process ticket types with filtering
                    for stt in section.ticket_types.all():
                        try:
                            if ticket_type_id and str(stt.ticket_type.id) != ticket_type_id:
                                continue
                            
                            ticket_data = {
                                'id': stt.id,  # SectionTicketType ID
                                'ticket_type': {
                                    'id': stt.ticket_type.id,
                                    'name': stt.ticket_type.name,
                                    'description': stt.ticket_type.description,
                                    'benefits': stt.ticket_type.benefits
                                },
                                'allocated_capacity': stt.allocated_capacity,
                                'available_capacity': stt.available_capacity,
                                'reserved_capacity': stt.reserved_capacity,
                                'sold_capacity': stt.sold_capacity,
                                'price_modifier': stt.price_modifier,
                                'final_price': stt.final_price
                            }
                            section_data['ticket_types'].append(ticket_data)
                        except Exception as e:
                            # Log error but continue processing other ticket types
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Error processing ticket type {stt.id}: {e}")
                            continue
                    
                    # Include individual seats if requested
                    if include_seats:
                        try:
                            from .models import Seat
                            seat_qs = Seat.objects.filter(
                                performance=performance, 
                                section=section.name
                            ).select_related('ticket_type')
                            
                            # Only available seats by default
                            seat_qs = seat_qs.filter(status='available')
                            
                            section_data['seats'] = list(seat_qs.values(
                                'id', 'row_number', 'seat_number', 'status', 'price', 'currency',
                                'is_premium', 'is_wheelchair_accessible', 'ticket_type_id'
                            ))
                        except Exception as e:
                            # Log error but continue without seats
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Error fetching seats for section {section.name}: {e}")
                            section_data['seats'] = []
                    
                    if section_data['ticket_types']:
                        sections_data.append(section_data)
                except Exception as e:
                    # Log error but continue processing other sections
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing section {section.name}: {e}")
                    continue

            # Fallback: derive sections from seats if no explicit sections are linked
            if not sections_data:
                try:
                    from django.db.models import Count, Min
                    seat_aggregates = performance.seats.filter(status='available').values('section').annotate(
                        total_seats=Count('id'),
                        min_price=Min('price'),
                    )
                    for aggregate in seat_aggregates:
                        try:
                            sec_name = aggregate['section'] or 'General'
                            if section_name and sec_name != section_name:
                                continue
                            base_price = float(aggregate['min_price'] or 0)
                            section_data = {
                                'name': sec_name,
                                'description': '',
                                'base_price': base_price,
                                'total_capacity': int(aggregate['total_seats'] or 0),
                                'available_capacity': int(aggregate['total_seats'] or 0),
                                'reserved_capacity': 0,
                                'sold_capacity': 0,
                                'occupancy_rate': 0,
                                'is_premium': False,
                                'is_wheelchair_accessible': False,
                                'ticket_types': []
                            }
                            for tt in performance.event.ticket_types.filter(is_active=True):
                                try:
                                    if ticket_type_id and str(tt.id) != ticket_type_id:
                                        continue
                                    section_data['ticket_types'].append({
                                        'id': tt.id,
                                        'name': tt.name,
                                        'description': tt.description,
                                        'allocated_capacity': section_data['total_capacity'],
                                        'available_capacity': section_data['available_capacity'],
                                        'reserved_capacity': 0,
                                        'sold_capacity': 0,
                                        'price_modifier': float(tt.price_modifier or 1),
                                        'final_price': base_price * float(tt.price_modifier or 1),
                                        'benefits': tt.benefits,
                                    })
                                except Exception as e:
                                    # Log error but continue processing other ticket types
                                    import logging
                                    logger = logging.getLogger(__name__)
                                    logger.error(f"Error processing fallback ticket type {tt.id}: {e}")
                                    continue
                            if section_data['ticket_types']:
                                sections_data.append(section_data)
                        except Exception as e:
                            # Log error but continue processing other aggregates
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Error processing fallback section {sec_name}: {e}")
                            continue
                except Exception as e:
                    # Log error but continue with empty sections
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing fallback sections: {e}")
            
            return Response({
                'performance_id': performance.id,
                'performance_date': performance.date,
                'performance_time': performance.start_time,
                'total_sections': len(sections_data),
                'sections': sections_data
            })
            
        except EventPerformance.DoesNotExist:
            return Response(
                {'error': 'Performance not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Log unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in performance_seats: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='performances/(?P<performance_id>[^/.]+)/seat-map', permission_classes=[AllowAny])
    def performance_seat_map(self, request, performance_id=None):
        """Return a simplified seat-map for a specific performance (no SVG geometry yet)."""
        try:
            performance = EventPerformance.objects.get(id=performance_id)
            seats = performance.seats.all().values(
                'id', 'section', 'row_number', 'seat_number', 'status', 'price', 'currency',
                'is_wheelchair_accessible', 'is_premium', 'reservation_id', 'reservation_expires_at'
            )
            return Response({
                'performance_id': performance.id,
                'performance_date': performance.date,
                'performance_time': performance.start_time,
                'seats': list(seats)
            })
        except EventPerformance.DoesNotExist:
            return Response({'error': 'Performance not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='performances/(?P<performance_id>[^/.]+)/hold')
    def hold_seats(self, request, performance_id=None):
        """Temporarily reserve (hold) seats for a performance."""
        try:
            performance = EventPerformance.objects.get(id=performance_id)
        except EventPerformance.DoesNotExist:
            return Response({'error': 'Performance not found'}, status=status.HTTP_404_NOT_FOUND)

        seat_ids = request.data.get('seat_ids') or []
        ticket_type_id = request.data.get('ticket_type_id')
        ttl_seconds = int(request.data.get('ttl_seconds') or 600)  # default 10 minutes
        if not isinstance(seat_ids, list) or len(seat_ids) == 0:
            return Response({'error': 'seat_ids must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

        from .models import Seat
        seats = list(Seat.objects.filter(performance=performance, id__in=seat_ids))
        if len(seats) != len(seat_ids):
            return Response({'error': 'Some seats not found for this performance'}, status=status.HTTP_400_BAD_REQUEST)

        # Check availability
        not_available = [str(s.id) for s in seats if s.status != 'available']
        if not_available:
            return Response({'error': 'Some seats are not available', 'seats': not_available}, status=status.HTTP_409_CONFLICT)

        # Hold atomically with select_for_update and recheck
        reservation_id = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(seconds=ttl_seconds)
        from django.db import transaction
        from .models import Seat as SeatModel
        with transaction.atomic():
            lock_qs = SeatModel.objects.select_for_update().filter(id__in=[s.id for s in seats])
            # Recheck availability under lock
            not_available = [str(s.id) for s in lock_qs if s.status != 'available']
            if not_available:
                return Response({'error': 'Some seats are no longer available', 'seats': not_available}, status=status.HTTP_409_CONFLICT)
            # Update
            lock_qs.update(status='reserved', reservation_id=reservation_id, reservation_expires_at=expires_at)

        return Response({
            'message': 'Seats held successfully',
            'reservation_id': reservation_id,
            'expires_at': expires_at.isoformat(),
            'seat_ids': [str(s.id) for s in seats],
            'ticket_type_id': ticket_type_id
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='performances/(?P<performance_id>[^/.]+)/release')
    def release_seats(self, request, performance_id=None):
        """Release previously held seats by reservation_id or seat_ids."""
        try:
            performance = EventPerformance.objects.get(id=performance_id)
        except EventPerformance.DoesNotExist:
            return Response({'error': 'Performance not found'}, status=status.HTTP_404_NOT_FOUND)

        reservation_id = request.data.get('reservation_id')
        seat_ids = request.data.get('seat_ids') or []
        if not reservation_id and not seat_ids:
            return Response({'error': 'Provide reservation_id or seat_ids[] to release'}, status=status.HTTP_400_BAD_REQUEST)

        from .models import Seat
        qs = Seat.objects.filter(performance=performance, status='reserved')
        if reservation_id:
            qs = qs.filter(reservation_id=reservation_id)
        elif isinstance(seat_ids, list) and seat_ids:
            qs = qs.filter(id__in=seat_ids)
        else:
            return Response({'error': 'Invalid seat_ids'}, status=status.HTTP_400_BAD_REQUEST)

        from django.db import transaction
        released = 0
        with transaction.atomic():
            locked = qs.select_for_update()
            released = locked.update(status='available', reservation_id=None, reservation_expires_at=None)

        return Response({'message': 'Seats released', 'released_count': released}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for an event."""
        try:
            event = self.get_object()
            reviews = event.reviews.all().order_by('-created_at')
            
            # Pagination
            page = self.paginate_queryset(reviews)
            if page is not None:
                serializer = EventReviewSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = EventReviewSerializer(reviews, many=True)
            return Response(serializer.data)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_review(self, request, pk=None):
        """Add a review to an event."""
        try:
            event = self.get_object()
            serializer = EventReviewCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(event=event, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def book(self, request, pk=None):
        """Book an event."""
        try:
            event = self.get_object()
            serializer = EventBookingSerializer(data=request.data)
            
            if serializer.is_valid():
                booking = serializer.save(event=event, user=request.user)
                return Response({
                    'message': 'Booking created successfully',
                    'booking_id': booking.id,
                    'booking_reference': booking.booking_reference
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def calculate_pricing(self, request, pk=None):
        """Calculate pricing for event booking."""
        try:
            event = self.get_object()
            
            # Validate request data
            serializer = EventPricingCalculatorSerializer(data=request.data, context={'event': event})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Get validated data
            data = serializer.validated_data
            performance_id = data.get('performance_id')
            ticket_type_id = data.get('ticket_type_id')
            section_name = data.get('section_name')
            quantity = data.get('quantity', 1)
            selected_options = data.get('selected_options', [])
            discount_code = data.get('discount_code', '')
            
            # Get performance
            try:
                performance = event.performances.get(id=performance_id)
            except EventPerformance.DoesNotExist:
                return Response(
                    {'error': 'Performance not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate pricing using the pricing service
            from events.pricing_service import EventPriceCalculator
            
            calculator = EventPriceCalculator(event, performance)
            try:
                pricing_result = calculator.calculate_ticket_price(
                    section_name=section_name,
                    ticket_type_id=ticket_type_id,
                    quantity=quantity,
                    selected_options=selected_options,
                    discount_code=discount_code
                )
            except (EventSection.DoesNotExist, SectionTicketType.DoesNotExist) as e:
                return Response(
                    {'error': 'Invalid section or ticket_type for this performance', 'detail': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except ValidationError as e:
                # Extract the first error message from ValidationError
                error_message = str(e)
                # If the error is a list representation, extract the first item
                if error_message.startswith('[') and error_message.endswith(']'):
                    try:
                        import ast
                        error_list = ast.literal_eval(error_message)
                        if isinstance(error_list, list) and len(error_list) > 0:
                            error_message = str(error_list[0])
                    except:
                        pass  # If parsing fails, use the original string
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure JSON-serializable output (convert Decimal to float)
            def _to_json_serializable(obj):
                from decimal import Decimal as _D
                if isinstance(obj, dict):
                    return {k: _to_json_serializable(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [_to_json_serializable(v) for v in obj]
                if isinstance(obj, _D):
                    try:
                        return float(obj)
                    except Exception:
                        return str(obj)
                return obj

            # Add currency normalization and normalized breakdown
            if isinstance(pricing_result, dict):
                currency_code = event.currency if hasattr(event, 'currency') else 'USD'
                pricing_result.setdefault('currency', currency_code)
                if 'price_breakdown' in pricing_result and isinstance(pricing_result['price_breakdown'], dict):
                    pricing_result['price_breakdown'].setdefault('currency', currency_code)
                    pb = pricing_result['price_breakdown']
                    # Build normalized price breakdown for frontend reuse
                    try:
                        base = float(pb.get('base_price') or 0)
                        pm = float(pb.get('price_modifier') or 0)
                        options_total = float(pb.get('options_total') or 0)
                        fees_total = float(pb.get('fees_total') or 0)
                        taxes_total = float(pb.get('taxes_total') or 0)
                        subtotal = float(pb.get('subtotal') or (base + pm + options_total + fees_total + taxes_total))
                        final_price = float(pb.get('final_price') or subtotal)
                        pricing_result['price_breakdown_normalized'] = {
                            'base_price': base,
                            'modifiers': {
                                'price_modifier': pm,
                            },
                            'options_total': options_total,
                            'fees_total': fees_total,
                            'taxes_total': taxes_total,
                            'subtotal': subtotal,
                            'final_price': final_price,
                            'currency': str(currency_code),
                        }
                    except Exception:
                        pass
            return Response(_to_json_serializable(pricing_result))

        except Exception as e:
            return Response(
                {'error': 'Pricing calculation failed', 'detail': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def calculate_bulk_pricing(self, request, pk=None):
        """Calculate pricing for multiple ticket requests."""
        try:
            event = self.get_object()
            
            # Validate request data
            ticket_requests = request.data.get('ticket_requests', [])
            discount_code = request.data.get('discount_code')
            is_group_booking = request.data.get('is_group_booking', False)
            apply_fees = request.data.get('apply_fees', False)
            apply_taxes = request.data.get('apply_taxes', False)
            
            if not ticket_requests:
                return Response(
                    {'error': 'ticket_requests is required and must be a non-empty list'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate each ticket request
            for i, req in enumerate(ticket_requests):
                if not isinstance(req, dict):
                    return Response(
                        {'error': f'ticket_requests[{i}] must be a dictionary'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                required_fields = ['performance_id', 'section_name', 'ticket_type_id', 'quantity']
                for field in required_fields:
                    if field not in req:
                        return Response(
                            {'error': f'ticket_requests[{i}] missing required field: {field}'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            # Group requests by performance
            performance_requests = {}
            for req in ticket_requests:
                performance_id = req['performance_id']
                if performance_id not in performance_requests:
                    performance_requests[performance_id] = []
                performance_requests[performance_id].append(req)
            
            # Calculate pricing for each performance
            results = []
            total_summary = {
                'total_tickets': 0,
                'total_sections': 0,
                'total_ticket_types': 0,
                'subtotal': Decimal('0.00'),
                'options_total': Decimal('0.00'),
                'discount_total': Decimal('0.00'),
                'fees_total': Decimal('0.00'),
                'taxes_total': Decimal('0.00'),
                'final_total': Decimal('0.00'),
                'currency': 'USD'
            }
            
            for performance_id, requests in performance_requests.items():
                try:
                    # Get performance
                    performance = event.performances.get(id=performance_id)
                    
                    # Create pricing calculator
                    from events.pricing_service import EventPriceCalculator
                    calculator = EventPriceCalculator(event, performance)
                    
                    # Calculate bulk pricing for this performance
                    bulk_result = calculator.calculate_bulk_pricing(
                        ticket_requests=requests,
                        discount_code=discount_code,
                        is_group_booking=is_group_booking,
                        apply_fees=apply_fees,
                        apply_taxes=apply_taxes
                    )
                    
                    # Add performance info
                    bulk_result['performance_id'] = performance_id
                    bulk_result['performance_date'] = performance.date
                    bulk_result['performance_time'] = performance.start_time
                    
                    results.append(bulk_result)
                    
                    # Update total summary
                    total_summary['total_tickets'] += bulk_result['summary']['total_tickets']
                    total_summary['total_sections'] += bulk_result['summary']['total_sections']
                    total_summary['total_ticket_types'] += bulk_result['summary']['total_ticket_types']
                    total_summary['subtotal'] += bulk_result['subtotal']
                    total_summary['options_total'] += bulk_result['options_total']
                    total_summary['discount_total'] += bulk_result['discount_total']
                    total_summary['fees_total'] += bulk_result['fees_total']
                    total_summary['taxes_total'] += bulk_result['taxes_total']
                    total_summary['final_total'] += bulk_result['final_total']
                    
                except EventPerformance.DoesNotExist:
                    return Response(
                        {'error': f'Performance {performance_id} not found for this event'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                except ValidationError as e:
                    return Response(
                        {'error': f'Validation error for performance {performance_id}: {str(e)}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error calculating bulk pricing for performance {performance_id}: {e}")
                    return Response(
                        {'error': f'Error calculating pricing for performance {performance_id}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            # Return comprehensive result
            response_data = {
                'event_id': event.id,
                'event_title': event.title,
                'performance_results': results,
                'total_summary': total_summary,
                'calculation_timestamp': timezone.now().isoformat(),
                'discount_code': discount_code,
                'is_group_booking': is_group_booking,
                'apply_fees': apply_fees,
                'apply_taxes': apply_taxes
            }
            
            return Response(response_data)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in calculate_bulk_pricing: {e}")
            return Response(
                {'error': 'Bulk pricing calculation failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def pricing_summary(self, request, pk=None):
        """Get comprehensive pricing summary for an event."""
        try:
            event = self.get_object()
            
            # Get query parameters
            section_name = request.query_params.get('section')
            performance_id = request.query_params.get('performance_id')
            
            # Get performances
            if performance_id:
                performances = event.performances.filter(id=performance_id)
            else:
                performances = event.performances.filter(is_available=True)
            
            if not performances.exists():
                return Response(
                    {'error': 'No available performances found for this event'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate pricing summary for each performance
            performance_summaries = []
            event_summary = {
                'total_capacity': 0,
                'available_capacity': 0,
                'price_range': {
                    'min': Decimal('999999.99'),
                    'max': Decimal('0.00')
                },
                'sections_count': 0,
                'ticket_types_count': 0
            }
            
            for performance in performances:
                try:
                    # Create pricing calculator
                    from events.pricing_service import EventPriceCalculator
                    calculator = EventPriceCalculator(event, performance)
                    
                    # Get pricing summary
                    performance_summary = calculator.get_pricing_summary(section_name)
                    
                    # Add performance info
                    performance_summary['performance_date'] = performance.date
                    performance_summary['performance_time'] = performance.start_time
                    performance_summary['is_available'] = performance.is_available
                    
                    performance_summaries.append(performance_summary)
                    
                    # Update event summary
                    event_summary['total_capacity'] += performance_summary['total_capacity']
                    event_summary['available_capacity'] += performance_summary['available_capacity']
                    event_summary['sections_count'] += len(performance_summary['sections'])
                    
                    # Update price range
                    if performance_summary['price_range']['min'] < event_summary['price_range']['min']:
                        event_summary['price_range']['min'] = performance_summary['price_range']['min']
                    if performance_summary['price_range']['max'] > event_summary['price_range']['max']:
                        event_summary['price_range']['max'] = performance_summary['price_range']['max']
                    
                    # Count unique ticket types
                    for section in performance_summary['sections']:
                        event_summary['ticket_types_count'] += len(section['ticket_types'])
                        
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error calculating pricing summary for performance {performance.id}: {e}")
                    continue
            
            # Reset price range if no tickets found
            if event_summary['price_range']['min'] == Decimal('999999.99'):
                event_summary['price_range']['min'] = Decimal('0.00')
            
            # Return comprehensive summary
            response_data = {
                'event_id': event.id,
                'event_title': event.title,
                'event_summary': event_summary,
                'performance_summaries': performance_summaries,
                'calculation_timestamp': timezone.now().isoformat(),
                'currency': 'USD'
            }
            
            return Response(response_data)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in pricing_summary: {e}")
            return Response(
                {'error': 'Pricing summary calculation failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='home-events')
    def home_events(self, request):
        """Get events categorized for home page display."""
        try:
            today = timezone.now().date()
            
            # Upcoming Events - next 6 events
            upcoming = Event.objects.filter(
                is_active=True,
                performances__date__gte=today
            ).distinct().order_by('performances__date')[:6]
            
            # Past Events - last 3 events
            past = Event.objects.filter(
                is_active=True,
                performances__date__lt=today
            ).distinct().order_by('-performances__date')[:3]
            
            # Special Events - events marked as special or with special performances
            special = Event.objects.filter(
                Q(is_active=True, is_special=True) |
                Q(is_active=True, performances__is_special=True)
            ).distinct()[:3]
            
            # Featured Events
            featured = Event.objects.filter(
                is_active=True,
                is_featured=True
            ).order_by('-created_at')[:4]
            
            # Popular Events
            popular = Event.objects.filter(
                is_active=True,
                is_popular=True
            ).order_by('-created_at')[:4]

            # Seasonal Events
            seasonal = Event.objects.filter(
                is_active=True,
                is_seasonal=True
            ).order_by('-created_at')[:4]
            
            return Response({
                'upcoming_events': EventListSerializer(upcoming, many=True).data,
                'past_events': EventListSerializer(past, many=True).data,
                'special_events': EventListSerializer(special, many=True).data,
                'featured_events': EventListSerializer(featured, many=True).data,
                'popular_events': EventListSerializer(popular, many=True).data,
                'seasonal_events': EventListSerializer(seasonal, many=True).data,
                'total_counts': {
                    'upcoming': upcoming.count(),
                    'past': past.count(),
                    'special': special.count(),
                    'featured': featured.count(),
                    'popular': popular.count(),
                    'seasonal': seasonal.count()
                }
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in home_events: {e}")
            return Response(
                {'error': 'Failed to fetch home events'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_object(self):
        """Get event by slug or ID."""
        lookup_value = self.kwargs.get('pk')
        
        # Try to get by slug first
        try:
            return Event.objects.get(slug=lookup_value, is_active=True)
        except Event.DoesNotExist:
            pass
        
        # If not found by slug, try by ID
        try:
            return Event.objects.get(id=lookup_value, is_active=True)
        except Event.DoesNotExist:
            pass
        
        # If still not found, raise 404
        raise Http404("Event not found")




class EventReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for EventReview model."""
    
    serializer_class = EventReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        event_id = self.kwargs.get('event_pk')
        return EventReview.objects.filter(event_id=event_id)
    
    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_pk')
        serializer.save(event_id=event_id, user=self.request.user)


class EventPricingViewSet(viewsets.ViewSet):
    """ViewSet for event pricing calculations."""
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['post'])
    def calculate_price(self, request, pk=None):
        """Calculate price for event tickets with options and discounts."""
        try:
            event = Event.objects.get(pk=pk)
            
            # Validate request data
            serializer = EventPricingCalculatorSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            performance_id = data.get('performance_id')
            section_name = data.get('section_name')
            ticket_type_id = data.get('ticket_type_id')
            quantity = data.get('quantity', 1)
            selected_options = data.get('selected_options', [])
            discount_code = data.get('discount_code')
            is_group_booking = data.get('is_group_booking', False)
            apply_fees = data.get('apply_fees', True)
            apply_taxes = data.get('apply_taxes', True)
            
            # Get performance
            try:
                performance = event.performances.get(id=performance_id)
            except EventPerformance.DoesNotExist:
                return Response(
                    {'error': 'Performance not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate price using pricing service
            from events.pricing_service import EventPriceCalculator
            calculator = EventPriceCalculator(event, performance)
            
            try:
                pricing_result = calculator.calculate_ticket_price(
                    section_name=section_name,
                    ticket_type_id=str(ticket_type_id),
                    quantity=quantity,
                    selected_options=selected_options,
                    discount_code=discount_code,
                    is_group_booking=is_group_booking,
                    apply_fees=apply_fees,
                    apply_taxes=apply_taxes
                )
                
                return Response(pricing_result)
                
            except ValidationError as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def pricing_info(self, request, pk=None):
        """Get pricing information for an event."""
        try:
            event = Event.objects.get(pk=pk)
            
            pricing_info = {
                'event_id': event.id,
                'event_title': event.title,
                'performances': []
            }
            
            for performance in event.performances.all():
                performance_info = {
                    'id': performance.id,
                    'date': performance.date,
                    'start_time': performance.start_time,
                    'end_time': performance.end_time,
                    'is_available': performance.is_available,
                    'sections': []
                }
                
                for section in performance.sections.all():
                    section_info = {
                        'name': section.name,
                        'description': section.description,
                        'base_price': section.base_price,
                        'total_capacity': section.total_capacity,
                        'available_capacity': section.available_capacity,
                        'is_premium': section.is_premium,
                        'is_wheelchair_accessible': section.is_wheelchair_accessible,
                        'ticket_types': []
                    }
                    
                    for stt in section.ticket_types.all():
                        ticket_info = {
                            'id': stt.ticket_type.id,
                            'name': stt.ticket_type.name,
                            'description': stt.ticket_type.description,
                            'price_modifier': stt.price_modifier,
                            'final_price': stt.final_price,
                            'allocated_capacity': stt.allocated_capacity,
                            'available_capacity': stt.available_capacity,
                            'benefits': stt.ticket_type.benefits
                        }
                        section_info['ticket_types'].append(ticket_info)
                    
                    performance_info['sections'].append(section_info)
                
                pricing_info['performances'].append(performance_info)
            
            return Response(pricing_info)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class EventDiscountViewSet(viewsets.ModelViewSet):
    """ViewSet for EventDiscount management."""
    
    queryset = EventDiscount.objects.all()
    serializer_class = EventDiscountSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['created_at', 'valid_from', 'valid_until']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter active discounts."""
        queryset = super().get_queryset()
        event_id = self.request.query_params.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id, is_active=True)
        return queryset.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def validate_code(self, request, pk=None):
        """Validate a discount code."""
        try:
            discount = self.get_object()
            
            if not discount.is_valid():
                return Response(
                    {'error': 'Discount code is not valid'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            amount = Decimal(request.data.get('amount', '0'))
            discount_amount = discount.calculate_discount(amount)
            
            return Response({
                'discount_id': discount.id,
                'discount_name': discount.name,
                'discount_type': discount.discount_type,
                'discount_value': discount.discount_value,
                'calculated_discount': discount_amount,
                'is_valid': True
            })
            
        except EventDiscount.DoesNotExist:
            return Response(
                {'error': 'Discount code not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class EventFeeViewSet(viewsets.ModelViewSet):
    """ViewSet for EventFee management."""
    
    queryset = EventFee.objects.all()
    serializer_class = EventFeeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['fee_type', 'created_at']
    ordering = ['fee_type', 'name']
    
    def get_queryset(self):
        """Filter active fees."""
        queryset = super().get_queryset()
        event_id = self.request.query_params.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id, is_active=True)
        return queryset.filter(is_active=True)


class EventPricingRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for EventPricingRule management."""
    
    queryset = EventPricingRule.objects.all()
    serializer_class = EventPricingRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['priority', 'created_at']
    ordering = ['-priority', 'name']
    
    def get_queryset(self):
        """Filter active rules."""
        queryset = super().get_queryset()
        event_id = self.request.query_params.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id, is_active=True)
        return queryset.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def test_rule(self, request, pk=None):
        """Test a pricing rule."""
        try:
            rule = self.get_object()
            base_price = Decimal(request.data.get('base_price', '0'))
            
            adjustment = rule.calculate_adjustment(base_price)
            
            return Response({
                'rule_id': rule.id,
                'rule_name': rule.name,
                'base_price': base_price,
                'adjustment': adjustment,
                'final_price': base_price + adjustment
            })
            
        except EventPricingRule.DoesNotExist:
            return Response(
                {'error': 'Pricing rule not found'}, 
                status=status.HTTP_404_NOT_FOUND
            ) 


@api_view(['GET'])
def event_filters(request):
    from .models import EventCategory, Venue
    
    # Get categories with translated fields
    categories = []
    for category in EventCategory.objects.filter(is_active=True):
        categories.append({
            'id': category.id,
            'name': getattr(category, 'name', ''),
            'description': getattr(category, 'description', ''),
            'icon': category.icon,
            'color': category.color,
        })
    
    # Get venues with translated fields
    venues = []
    for venue in Venue.objects.all():
        venues.append({
            'id': venue.id,
            'name': getattr(venue, 'name', ''),
            'city': venue.city,
            'country': venue.country,
            'image': venue.image.url if venue.image else None,
        })
    
    styles = [
        {'value': 'music', 'label': 'Music'},
        {'value': 'sports', 'label': 'Sports'},
        {'value': 'theater', 'label': 'Theater'},
        {'value': 'festival', 'label': 'Festival'},
        {'value': 'conference', 'label': 'Conference'},
        {'value': 'exhibition', 'label': 'Exhibition'},
    ]
    
    return Response({
        'categories': categories,
        'venues': venues,
        'styles': styles,
    }) 