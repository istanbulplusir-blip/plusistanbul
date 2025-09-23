"""
Validators for Events app.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .exceptions import *
from .models import Event, EventPerformance, Seat, TicketType

class EventValidator:
    """Validators for event operations."""
    
    @staticmethod
    def validate_event_exists(event_id):
        """Validate that event exists and is active."""
        try:
            event = Event.objects.get(id=event_id)
            if not event.is_active:
                raise EventNotActiveError(f"Event {event_id} is not active")
            return event
        except Event.DoesNotExist:
            raise EventNotFoundError(f"Event {event_id} not found")
    
    @staticmethod
    def validate_performance_exists(performance_id):
        """Validate that performance exists and is available."""
        try:
            performance = EventPerformance.objects.get(id=performance_id)
            if not performance.is_available:
                raise PerformanceNotAvailableError(f"Performance {performance_id} is not available")
            return performance
        except EventPerformance.DoesNotExist:
            raise PerformanceNotFoundError(f"Performance {performance_id} not found")
    
    @staticmethod
    def validate_ticket_type_exists(ticket_type_id):
        """Validate that ticket type exists and is active."""
        try:
            ticket_type = TicketType.objects.get(id=ticket_type_id)
            if not ticket_type.is_active:
                raise InvalidTicketTypeError(f"Ticket type {ticket_type_id} is not active")
            return ticket_type
        except TicketType.DoesNotExist:
            raise TicketTypeNotFoundError(f"Ticket type {ticket_type_id} not found")
    
    @staticmethod
    def validate_performance_date(performance):
        """Validate that performance date is in the future."""
        if performance.date < timezone.now().date():
            raise InvalidPerformanceDateError(f"Performance date {performance.date} is in the past")
    
    @staticmethod
    def validate_seat_availability(seat_ids):
        """Validate that all seats are available."""
        seats = Seat.objects.filter(id__in=seat_ids)
        
        if seats.count() != len(seat_ids):
            raise SeatNotAvailableError("Some seats are not found")
        
        unavailable_seats = seats.exclude(status='available')
        if unavailable_seats.exists():
            unavailable_ids = list(unavailable_seats.values_list('id', flat=True))
            raise SeatNotAvailableError(f"Seats {unavailable_ids} are not available")
        
        return seats
    
    @staticmethod
    def validate_seat_performance_consistency(seat_ids, performance_id):
        """Validate that all seats belong to the same performance."""
        seats = Seat.objects.filter(id__in=seat_ids)
        
        inconsistent_seats = seats.exclude(performance_id=performance_id)
        if inconsistent_seats.exists():
            raise InvalidSeatSelectionError("All seats must belong to the same performance")
    
    @staticmethod
    def validate_seat_ticket_type_consistency(seat_ids, ticket_type_id):
        """Validate that all seats have the same ticket type."""
        seats = Seat.objects.filter(id__in=seat_ids)
        
        inconsistent_seats = seats.exclude(ticket_type_id=ticket_type_id)
        if inconsistent_seats.exists():
            raise InvalidSeatSelectionError("All seats must have the same ticket type")
    
    @staticmethod
    def validate_performance_capacity(performance_id, requested_seats):
        """Validate that performance has enough available seats."""
        available_count = Seat.objects.filter(
            performance_id=performance_id,
            status='available'
        ).count()
        
        if available_count < requested_seats:
            raise InsufficientSeatsError(
                f"Only {available_count} seats available, {requested_seats} requested"
            )
    
    @staticmethod
    def validate_booking_limits(user_id, event_id, max_bookings=5):
        """Validate user booking limits for an event."""
        from orders.models import Order
        
        # Count active bookings for this user and event
        active_bookings = Order.objects.filter(
            user_id=user_id,
            items__product_type='event',
            items__product_id=event_id,
            status__in=['pending', 'confirmed']
        ).count()
        
        if active_bookings >= max_bookings:
            raise BookingValidationError(f"Maximum {max_bookings} bookings allowed per event")

class SeatSelectionValidator:
    """Validators for seat selection operations."""
    
    @staticmethod
    def validate_single_performance_selection(existing_seats, new_performance_id):
        """Validate that user can only select seats from one performance at a time."""
        if existing_seats:
            existing_performance = existing_seats[0].get('performance_id')
            if existing_performance != new_performance_id:
                raise InvalidSeatSelectionError(
                    "You can only select seats from one performance at a time"
                )
    
    @staticmethod
    def validate_seat_adjacency(seat_ids, require_adjacent=False):
        """Validate seat adjacency if required."""
        if not require_adjacent:
            return True
        
        seats = Seat.objects.filter(id__in=seat_ids).order_by('row_number', 'seat_number')
        
        if len(seats) <= 1:
            return True
        
        # Check if seats are adjacent
        for i in range(len(seats) - 1):
            current = seats[i]
            next_seat = seats[i + 1]
            
            # Same row, consecutive seats
            if (current.row_number == next_seat.row_number and 
                int(next_seat.seat_number) - int(current.seat_number) == 1):
                continue
            
            # Adjacent rows, same seat number
            if (int(next_seat.row_number) - int(current.row_number) == 1 and 
                current.seat_number == next_seat.seat_number):
                continue
            
            raise InvalidSeatSelectionError("Selected seats must be adjacent")
        
        return True
    
    @staticmethod
    def validate_wheelchair_accessibility(seat_ids, require_wheelchair=False):
        """Validate wheelchair accessibility if required."""
        if not require_wheelchair:
            return True
        
        seats = Seat.objects.filter(id__in=seat_ids)
        non_accessible = seats.filter(is_wheelchair_accessible=False)
        
        if non_accessible.exists():
            raise InvalidSeatSelectionError("All selected seats must be wheelchair accessible")
        
        return True

class CartValidator:
    """Validators for cart operations."""
    
    @staticmethod
    def validate_cart_item_limits(cart, max_items=10):
        """Validate cart item limits."""
        if cart.items.count() >= max_items:
            raise CartOperationError(f"Maximum {max_items} items allowed in cart")
    
    @staticmethod
    def validate_cart_total_limit(cart, max_total=10000):
        """Validate cart total limit."""
        if cart.total > max_total:
            raise CartOperationError(f"Cart total cannot exceed ${max_total}")
    
    @staticmethod
    def validate_duplicate_seats(cart, new_seat_ids):
        """Validate that seats are not already in cart."""
        existing_seat_ids = set()
        
        for item in cart.items.filter(product_type='event'):
            seats = item.booking_data.get('seats', [])
            for seat in seats:
                existing_seat_ids.add(seat.get('seat_id'))
        
        duplicate_seats = existing_seat_ids.intersection(set(new_seat_ids))
        if duplicate_seats:
            raise DuplicateBookingError(f"Seats {list(duplicate_seats)} are already in cart")

class BookingValidator:
    """Validators for booking operations."""
    
    @staticmethod
    def validate_booking_data(booking_data):
        """Validate booking data structure."""
        required_fields = ['event_id', 'performance_id', 'ticket_type_id', 'seats']
        
        for field in required_fields:
            if field not in booking_data:
                raise BookingValidationError(f"Missing required field: {field}")
        
        if not booking_data['seats']:
            raise BookingValidationError("At least one seat must be selected")
    
    @staticmethod
    def validate_payment_data(payment_data):
        """Validate payment data."""
        if not payment_data:
            raise PaymentRequiredError("Payment data is required")
        
        required_fields = ['payment_method', 'transaction_id']
        for field in required_fields:
            if field not in payment_data:
                raise PaymentRequiredError(f"Missing payment field: {field}")
    
    @staticmethod
    def validate_booking_timeout(booking_time, timeout_minutes=30):
        """Validate that booking hasn't timed out."""
        if booking_time:
            timeout_threshold = timezone.now() - timedelta(minutes=timeout_minutes)
            if booking_time < timeout_threshold:
                raise SeatReservationExpiredError("Seat reservation has expired") 