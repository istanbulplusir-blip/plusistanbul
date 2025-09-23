"""
Custom exceptions for Events app.
"""

class EventException(Exception):
    """Base exception for events."""
    pass

class EventNotFoundError(EventException):
    """Raised when event is not found."""
    pass

class PerformanceNotFoundError(EventException):
    """Raised when performance is not found."""
    pass

class SeatNotAvailableError(EventException):
    """Raised when seat is not available."""
    pass

class SeatAlreadyReservedError(EventException):
    """Raised when seat is already reserved."""
    pass

class InvalidSeatSelectionError(EventException):
    """Raised when seat selection is invalid."""
    pass

class PerformanceFullError(EventException):
    """Raised when performance is full."""
    pass

class TicketTypeNotFoundError(EventException):
    """Raised when ticket type is not found."""
    pass

class InvalidTicketTypeError(EventException):
    """Raised when ticket type is invalid for the event."""
    pass

class CartOperationError(EventException):
    """Raised when cart operation fails."""
    pass

class BookingValidationError(EventException):
    """Raised when booking validation fails."""
    pass

class PaymentRequiredError(EventException):
    """Raised when payment is required but not provided."""
    pass

class EventNotActiveError(EventException):
    """Raised when event is not active."""
    pass

class PerformanceNotAvailableError(EventException):
    """Raised when performance is not available."""
    pass

class SeatReservationExpiredError(EventException):
    """Raised when seat reservation has expired."""
    pass

class DuplicateBookingError(EventException):
    """Raised when trying to book the same seats twice."""
    pass

class InsufficientSeatsError(EventException):
    """Raised when not enough seats are available."""
    pass

class InvalidPerformanceDateError(EventException):
    """Raised when performance date is invalid."""
    pass

class EventCapacityExceededError(EventException):
    """Raised when event capacity is exceeded."""
    pass 