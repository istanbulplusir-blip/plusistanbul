"""
Cart services for Peykan Tourism Platform.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.db import transaction
from .models import Cart, CartItem
from events.models import Event, EventPerformance, TicketType
from events.logging_config import get_cart_logger

logger = get_cart_logger()


class EventCartService:
    """Service for handling event cart operations."""
    
    @staticmethod
    def add_event_seats_to_cart(
        cart: Cart,
        event_id: str,
        performance_id: str,
        ticket_type_id: str,
        seats: List[Dict[str, Any]],
        selected_options: Optional[List[Dict[str, Any]]] = None,
        special_requests: str = ""
    ) -> tuple[CartItem, bool]:
        """
        Add event seats to cart with proper merging logic.
        
        Returns:
            tuple: (cart_item, is_new_item)
        """
        logger.info(f"Adding {len(seats)} seats to cart for event {event_id}, performance {performance_id}")
        
        if selected_options is None:
            selected_options = []

        # Check for existing cart item with same event, performance, and ticket type
        existing_item = cart.items.filter(
            product_type='event',
            product_id=event_id,
            booking_data__performance_id=performance_id,
            booking_data__ticket_type_id=ticket_type_id
        ).first()
        
        # If existing item found, merge seats
        if existing_item:
            logger.info(f"Merging seats with existing cart item {existing_item.id}")
            return EventCartService._merge_seats_to_existing_item(
                existing_item, performance_id, ticket_type_id, seats, selected_options, special_requests
            ), False
        
        # Create new cart item
        logger.info(f"Creating new cart item for event {event_id}")
        return EventCartService._create_new_cart_item(
            cart, event_id, performance_id, ticket_type_id, seats, selected_options, special_requests
        ), True
    
    @staticmethod
    def _merge_seats_to_existing_item(
        existing_item: CartItem,
        performance_id: str,
        ticket_type_id: str,
        new_seats: List[Dict[str, Any]],
        selected_options: Optional[List[Dict[str, Any]]] = None,
        special_requests: str = ""
    ) -> CartItem:
        """Merge new seats with existing cart item."""
        existing_booking_data = existing_item.booking_data or {}
        existing_seats = existing_booking_data.get('seats', [])
        
        # Get existing seat IDs
        existing_seat_ids = set()
        for seat in existing_seats:
            seat_id = seat.get('seat_id')
            if seat_id:
                existing_seat_ids.add(seat_id)
        
        # Filter out seats that already exist
        seats_to_add = []
        for seat in new_seats:
            seat_id = seat.get('seat_id')
            if seat_id and seat_id not in existing_seat_ids:
                seats_to_add.append(seat)
        
        if not seats_to_add:
            # All seats already exist
            return existing_item
        
        # Merge seats
        all_seats = existing_seats + seats_to_add

        # Update booking data
        updated_booking_data = existing_booking_data.copy()
        updated_booking_data['seats'] = all_seats
        updated_booking_data['special_requests'] = special_requests

        # Merge selected options with enriched data
        existing_options = existing_item.selected_options or []
        if existing_options and isinstance(existing_options[0], dict) and 'options' in existing_options[0]:
            # Existing format has nested structure, merge options
            updated_options = existing_options[0]['options'] + (selected_options or [])
        else:
            # Use the enriched options directly
            updated_options = existing_options + (selected_options or [])

        # Recalculate subtotal (seats + options)
        seats_total = sum(Decimal(str(seat.get('price', 0))) for seat in all_seats)
        options_total = Decimal('0.00')
        
        # Calculate options total if selected_options provided
        if updated_options:
            from events.models import EventOption
            for option_data in updated_options:
                option_id = option_data.get('option_id')
                quantity = int(option_data.get('quantity', 1))
                try:
                    option = EventOption.objects.get(
                        id=option_id,
                        event_id=existing_item.product_id,
                        is_active=True
                    )
                    options_total += option.price * quantity
                except EventOption.DoesNotExist:
                    continue
        
        subtotal = seats_total + options_total
        
        # Store seats_total as unit_price and options_total separately
        # This way CartItem.save() will calculate: (unit_price * quantity) + options_total = subtotal
        unit_price = seats_total

        # Update item
        existing_item.booking_data = updated_booking_data
        existing_item.selected_options = updated_options  # Store enriched options
        existing_item.unit_price = unit_price
        existing_item.total_price = subtotal
        existing_item.save()
        
        return existing_item
    
    @staticmethod
    def _create_new_cart_item(
        cart: Cart,
        event_id: str,
        performance_id: str,
        ticket_type_id: str,
        seats: List[Dict[str, Any]],
        selected_options: Optional[List[Dict[str, Any]]] = None,
        special_requests: str = ""
    ) -> CartItem:
        """Create a new cart item for event seats."""
        if selected_options is None:
            selected_options = []
        try:
            # Get event, performance, and ticket type
            event = Event.objects.get(id=event_id, is_active=True)
            performance = EventPerformance.objects.get(id=performance_id, event=event)
            ticket_type = TicketType.objects.get(id=ticket_type_id, event=event)
            
            # Calculate total price including options
            seats_total = sum(Decimal(str(seat.get('price', 0))) for seat in seats)
            options_total = Decimal('0.00')
            
            # Calculate options total if selected_options provided
            if selected_options:
                from events.models import EventOption
                for option_data in selected_options:
                    option_id = option_data.get('option_id')
                    quantity = int(option_data.get('quantity', 1))
                    try:
                        option = EventOption.objects.get(
                            id=option_id,
                            event=event,
                            is_active=True
                        )
                        options_total += option.price * quantity
                        # Add name and price to option_data
                        option_data['name'] = option.name
                        option_data['price'] = float(option.price)
                    except EventOption.DoesNotExist:
                        logger.warning(f"Option {option_id} not found for event {event_id}")
                        continue
            
            # Calculate subtotal (seats + options) - this should be stored as subtotal
            subtotal = seats_total + options_total
            
            # Store seats_total as unit_price and options_total separately
            # This way CartItem.save() will calculate: (unit_price * quantity) + options_total = subtotal
            unit_price = seats_total
            
            # Get currency from event or default to USD
            currency = getattr(event, 'currency', 'USD') or 'USD'
            
            # Create cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product_type='event',
                product_id=event_id,
                booking_date=performance.date,
                booking_time=performance.start_time,
                variant_id=ticket_type_id,
                variant_name=ticket_type.name,
                quantity=1,
                unit_price=unit_price,
                total_price=subtotal,
                currency=currency,
                selected_options=selected_options if selected_options else [],  # Store enriched options with names/prices here
                booking_data={
                    'performance_id': performance_id,
                    'ticket_type_id': ticket_type_id,
                    'performance_date': performance.date.isoformat() if performance.date else None,
                    'performance_time': performance.start_time.isoformat() if performance.start_time else None,
                    'venue_name': getattr(event.venue, 'name', '') if event.venue else '',
                    'venue_address': getattr(event.venue, 'address', '') if event.venue else '',
                    'venue_city': event.venue.city if event.venue else '',
                    'venue_country': event.venue.country if event.venue else '',
                    'seats': seats,
                    'section': seats[0].get('section', '') if seats else '',
                    'ticket_type_name': ticket_type.name,
                    'special_requests': special_requests
                }
            )
            
            return cart_item
            
        except Exception as e:
            logger.error(f"Error creating cart item: {str(e)}")
            raise 