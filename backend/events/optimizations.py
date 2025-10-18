"""
Query optimizations for Events app.
"""

from django.db.models import Prefetch, Q, Count, Avg
from django.core.cache import cache
from .models import Event, EventPerformance, TicketType, Seat

class EventQueryOptimizer:
    """Optimized queries for events."""
    
    @staticmethod
    def get_event_with_optimized_data(event_id):
        """
        Get event with all related data in optimized queries.
        """
        cache_key = f"event_optimized_{event_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Optimized query with prefetch_related
        event = Event.objects.select_related(
            'category', 'venue'
        ).prefetch_related(
            Prefetch(
                'performances',
                queryset=EventPerformance.objects.filter(is_available=True)
            ),
            Prefetch(
                'ticket_types',
                queryset=TicketType.objects.filter(is_active=True)
            ),
            'artists',
            'options',
            Prefetch(
                'reviews',
                queryset=EventReview.objects.filter(is_verified=True)[:10]
            )
        ).get(id=event_id)
        
        # Cache for 15 minutes
        cache.set(cache_key, event, 900)
        
        return event
    
    @staticmethod
    def get_performance_with_seats(performance_id, section=None, ticket_type_id=None):
        """
        Get performance with optimized seat queries.
        """
        cache_key = f"performance_seats_{performance_id}_{section}_{ticket_type_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Build seat filter
        seat_filter = Q(status='available')
        if section:
            seat_filter &= Q(section=section)
        if ticket_type_id:
            seat_filter &= Q(ticket_type_id=ticket_type_id)
        
        # Optimized query
        performance = EventPerformance.objects.select_related(
            'event'
        ).prefetch_related(
            Prefetch(
                'seats',
                queryset=Seat.objects.filter(seat_filter).select_related('ticket_type')
            )
        ).get(id=performance_id)
        
        # Cache for 5 minutes (seats change frequently)
        cache.set(cache_key, performance, 300)
        
        return performance
    
    @staticmethod
    def get_events_list_with_stats():
        """
        Get events list with optimized statistics.
        """
        cache_key = "events_list_stats"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Optimized query with annotations
        events = Event.objects.filter(
            is_active=True
        ).select_related(
            'category', 'venue'
        ).prefetch_related(
            'artists'
        ).annotate(
            performance_count=Count('performances', filter=Q(performances__is_available=True)),
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-created_at')
        
        # Cache for 10 minutes
        cache.set(cache_key, list(events), 600)
        
        return events
    
    @staticmethod
    def get_available_seats_count(performance_id):
        """
        Get available seats count for a performance.
        """
        cache_key = f"seats_count_{performance_id}"
        cached_count = cache.get(cache_key)
        
        if cached_count is not None:
            return cached_count
        
        # Optimized count query
        count = Seat.objects.filter(
            performance_id=performance_id,
            status='available'
        ).count()
        
        # Cache for 2 minutes (very frequent changes)
        cache.set(cache_key, count, 120)
        
        return count
    
    @staticmethod
    def invalidate_event_cache(event_id):
        """
        Invalidate cache for a specific event.
        """
        cache_keys = [
            f"event_optimized_{event_id}",
            f"events_list_stats"
        ]
        
        for key in cache_keys:
            cache.delete(key)
    
    @staticmethod
    def invalidate_performance_cache(performance_id):
        """
        Invalidate cache for a specific performance.
        """
        # Delete all performance-related cache keys
        cache.delete_pattern(f"performance_seats_{performance_id}_*")
        cache.delete(f"seats_count_{performance_id}")

class SeatSelectionOptimizer:
    """Optimizations for seat selection."""
    
    @staticmethod
    def get_section_availability(performance_id, section):
        """
        Get seat availability for a specific section.
        """
        cache_key = f"section_availability_{performance_id}_{section}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Optimized query for section availability
        seats = Seat.objects.filter(
            performance_id=performance_id,
            section=section,
            status='available'
        ).select_related('ticket_type').values(
            'id', 'seat_number', 'row_number', 'section', 
            'price', 'currency', 'ticket_type__name'
        )
        
        # Group by ticket type
        availability = {}
        for seat in seats:
            ticket_type = seat['ticket_type__name']
            if ticket_type not in availability:
                availability[ticket_type] = []
            availability[ticket_type].append(seat)
        
        # Cache for 3 minutes
        cache.set(cache_key, availability, 180)
        
        return availability
    
    @staticmethod
    def reserve_seats(seat_ids, duration_minutes=30):
        """
        Reserve seats temporarily.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Update seat status to reserved
        seats = Seat.objects.filter(
            id__in=seat_ids,
            status='available'
        )
        
        # Use select_for_update to prevent race conditions
        with transaction.atomic():
            seats = seats.select_for_update()
            
            # Check if all seats are still available
            if seats.count() != len(seat_ids):
                return False, "Some seats are no longer available"
            
            # Update seats to reserved
            seats.update(
                status='reserved',
                reservation_expires_at=timezone.now() + timedelta(minutes=duration_minutes)
            )
            
            # Invalidate related caches
            performance_ids = set(seats.values_list('performance_id', flat=True))
            for perf_id in performance_ids:
                SeatSelectionOptimizer.invalidate_performance_cache(perf_id)
            
            return True, f"Reserved {len(seat_ids)} seats"
    
    @staticmethod
    def release_seats(seat_ids):
        """
        Release reserved seats.
        """
        # Update seat status back to available
        seats = Seat.objects.filter(
            id__in=seat_ids,
            status='reserved'
        )
        
        updated_count = seats.update(
            status='available',
            reservation_expires_at=None
        )
        
        # Invalidate related caches
        if updated_count > 0:
            performance_ids = set(seats.values_list('performance_id', flat=True))
            for perf_id in performance_ids:
                SeatSelectionOptimizer.invalidate_performance_cache(perf_id)
        
        return updated_count

# Import missing models
try:
    from .models import EventReview
except ImportError:
    # Fallback if EventReview doesn't exist
    EventReview = None

try:
    from django.db import transaction
except ImportError:
    transaction = None 