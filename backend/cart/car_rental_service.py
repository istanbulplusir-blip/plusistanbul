"""
Car Rental Cart Service for Peykan Tourism Platform.
"""

from typing import Dict, Any, Optional
from decimal import Decimal
from django.db import transaction
from .models import Cart, CartItem
from car_rentals.models import CarRental, CarRentalLocation
import logging

logger = logging.getLogger(__name__)


class CarRentalCartService:
    """Service for handling car rental cart operations."""
    
    @staticmethod
    def add_car_rental_to_cart(
        cart: Cart,
        car_rental_id: str,
        pickup_date: str,
        dropoff_date: str,
        pickup_time: str,
        dropoff_time: str,
        pickup_location_type: str,
        pickup_location_id: Optional[str] = None,
        pickup_location_custom: Optional[str] = None,
        pickup_location_coordinates: Optional[Dict[str, float]] = None,
        dropoff_location_type: str = 'same_as_pickup',
        dropoff_location_id: Optional[str] = None,
        dropoff_location_custom: Optional[str] = None,
        dropoff_location_coordinates: Optional[Dict[str, float]] = None,
        selected_options: Optional[list] = None,
        special_requests: str = "",
        booking_data: Optional[Dict[str, Any]] = None
    ) -> tuple[CartItem, bool]:
        """
        Add car rental to cart with proper validation and pricing.
        
        Returns:
            tuple: (cart_item, is_new_item)
        """
        logger.info(f"Adding car rental {car_rental_id} to cart")
        
        if selected_options is None:
            selected_options = []
        
        try:
            # Get car rental
            car_rental = CarRental.objects.get(id=car_rental_id)
        except CarRental.DoesNotExist:
            raise ValueError(f"Car rental {car_rental_id} not found")
        
        # Check for None values and provide defaults
        if not pickup_time:
            pickup_time = "10:00"
        if not dropoff_time:
            dropoff_time = "10:00"
        
        # Calculate rental duration using model method
        days, hours, total_hours = car_rental.calculate_rental_duration(
            pickup_date, dropoff_date, pickup_time, dropoff_time
        )
        
        # Calculate base price (without insurance)
        try:
            base_price = car_rental.calculate_total_price(days, hours, include_insurance=False)
        except ValidationError as e:
            raise ValueError(str(e))
        
        # Calculate options total and update selected_options with final prices
        options_total = Decimal('0.00')
        updated_selected_options = []

        for option in selected_options:
            try:
                from car_rentals.models import CarRentalOption
                # Handle both 'id' and 'option_id' field names
                option_id = option.get('id') or option.get('option_id')
                if not option_id:
                    logger.warning(f"Option missing ID: {option}")
                    continue

                option_obj = CarRentalOption.objects.get(id=option_id)
                # For hourly rentals, options are calculated as fixed price or daily price
                if days == 0:
                    # For hourly rentals, use fixed price or daily price (minimum 1 day)
                    if option_obj.price_type == 'fixed':
                        option_duration = 1  # Fixed price doesn't depend on duration
                    else:
                        option_duration = 1  # Daily price for minimum 1 day
                else:
                    # For daily rentals, use the actual rental days
                    option_duration = days
                option_price = option_obj.calculate_price(base_price, option_duration, option.get('quantity', 1))
                options_total += option_price

                # Update option with final price for CartItem.save()
                updated_option = option.copy()
                updated_option['final_price'] = float(option_price)
                updated_option['original_price'] = option.get('price', 0)
                updated_selected_options.append(updated_option)

            except CarRentalOption.DoesNotExist:
                logger.warning(f"Option {option_id} not found")
                continue

        # Replace selected_options with updated version
        selected_options = updated_selected_options
        
        # Calculate insurance total (if comprehensive insurance is selected)
        insurance_total = Decimal('0.00')
        # Check for comprehensive insurance in booking_data first, then selected_options
        comprehensive_insurance = False
        if booking_data:
            comprehensive_insurance = booking_data.get('comprehensive_insurance', False)
            logger.info(f"DEBUG: booking_data comprehensive_insurance = {comprehensive_insurance}")
        if not comprehensive_insurance:
            comprehensive_insurance = any(opt.get('name', '').lower().find('comprehensive') != -1 for opt in selected_options)
            logger.info(f"DEBUG: selected_options comprehensive_insurance = {comprehensive_insurance}")
        
        logger.info(f"DEBUG: Final comprehensive_insurance = {comprehensive_insurance}, car_rental.comprehensive_insurance_price = {car_rental.comprehensive_insurance_price}")
        
        if comprehensive_insurance and car_rental.comprehensive_insurance_price:
            # For hourly rentals, insurance is calculated for minimum 1 day
            insurance_duration = days if days > 0 else 1
            insurance_total = Decimal(str(car_rental.comprehensive_insurance_price)) * insurance_duration
            logger.info(f"DEBUG: Insurance calculated: {insurance_total} (price: {car_rental.comprehensive_insurance_price} * duration: {insurance_duration})")
        
        # Calculate total price
        total_price = base_price + options_total + insurance_total
        
        logger.info(f"Car rental pricing: base={base_price}, options={options_total}, insurance={insurance_total}, total={total_price}")
        
        # Get pickup location name
        pickup_location_name = CarRentalCartService._get_location_name(
            pickup_location_type, pickup_location_id, pickup_location_custom
        )
        
        # Get dropoff location name
        if dropoff_location_type == 'same_as_pickup':
            dropoff_location_name = pickup_location_name
        else:
            dropoff_location_name = CarRentalCartService._get_location_name(
                dropoff_location_type, dropoff_location_id, dropoff_location_custom
            )
        
        # Check for existing cart item with same car rental and dates
        existing_item = cart.items.filter(
            product_type='car_rental',
            product_id=car_rental_id,
            pickup_date=pickup_date,
            dropoff_date=dropoff_date,
            pickup_time=pickup_time,
            dropoff_time=dropoff_time
        ).first()
        
        if existing_item:
            logger.info(f"Updating existing cart item {existing_item.id}")
            # Update existing item
            existing_item.quantity = 1
            existing_item.unit_price = base_price  # Set unit_price to base price (without insurance)
            existing_item.total_price = total_price  # Set total_price to include insurance
            existing_item.options_total = options_total
            existing_item.selected_options = selected_options
            existing_item.pickup_location_type = pickup_location_type
            existing_item.pickup_location_id = pickup_location_id
            existing_item.pickup_location_custom = pickup_location_custom
            existing_item.pickup_location_coordinates = pickup_location_coordinates or {}
            existing_item.dropoff_location_type = dropoff_location_type
            existing_item.dropoff_location_id = dropoff_location_id
            existing_item.dropoff_location_custom = dropoff_location_custom
            existing_item.dropoff_location_coordinates = dropoff_location_coordinates or {}
            existing_item.booking_data = {
                'pickup_location_name': pickup_location_name,
                'dropoff_location_name': dropoff_location_name,
                'rental_days': days,
                'rental_hours': hours,
                'total_hours': total_hours,
                'rental_type': 'hourly' if days == 0 else 'daily',
                'special_requests': special_requests,
                'comprehensive_insurance': comprehensive_insurance,
                'insurance_total': float(insurance_total),
                **(booking_data or {})
            }
            existing_item.save()
            return existing_item, False
        
        # Create new cart item
        logger.info(f"Creating new cart item for car rental {car_rental_id}")
        cart_item = CartItem.objects.create(
            cart=cart,
            product_type='car_rental',
            product_id=car_rental_id,
            booking_date=pickup_date,
            booking_time=pickup_time,
            pickup_date=pickup_date,
            dropoff_date=dropoff_date,
            pickup_time=pickup_time,
            dropoff_time=dropoff_time,
            pickup_location_type=pickup_location_type,
            pickup_location_id=pickup_location_id,
            pickup_location_custom=pickup_location_custom or '',
            pickup_location_coordinates=pickup_location_coordinates or {},
            dropoff_location_type=dropoff_location_type,
            dropoff_location_id=dropoff_location_id,
            dropoff_location_custom=dropoff_location_custom or '',
            dropoff_location_coordinates=dropoff_location_coordinates or {},
            quantity=1,
            unit_price=base_price,  # Set unit_price to base price (without insurance)
            total_price=total_price,  # Set total_price to include insurance
            currency=car_rental.currency,
            selected_options=selected_options,
            options_total=options_total,
            booking_data={
                'pickup_location_name': pickup_location_name,
                'dropoff_location_name': dropoff_location_name,
                'rental_days': days,
                'rental_hours': hours,
                'total_hours': total_hours,
                'rental_type': 'hourly' if days == 0 else 'daily',
                'special_requests': special_requests,
                'car_brand': car_rental.brand,
                'car_model': car_rental.model,
                'car_year': car_rental.year,
                'comprehensive_insurance': comprehensive_insurance,
                'insurance_total': float(insurance_total),
                **(booking_data or {})
            }
        )
        
        return cart_item, True
    
    @staticmethod
    def _get_location_name(
        location_type: str,
        location_id: Optional[str],
        location_custom: Optional[str]
    ) -> str:
        """Get location display name."""
        if location_type == 'predefined' and location_id:
            try:
                location = CarRentalLocation.objects.get(id=location_id)
                return location.name
            except CarRentalLocation.DoesNotExist:
                return 'Unknown Location'
        elif location_type == 'custom' and location_custom:
            return location_custom
        return 'Not specified'
    
    @staticmethod
    def validate_car_rental_booking(
        car_rental_id: str,
        pickup_date: str,
        dropoff_date: str,
        pickup_time: str,
        dropoff_time: str
    ) -> tuple[bool, str]:
        """
        Validate car rental booking data.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            car_rental = CarRental.objects.get(id=car_rental_id)
        except CarRental.DoesNotExist:
            return False, "Car rental not found"
        
        # Validate dates
        from datetime import datetime, date, time
        from django.utils import timezone
        try:
            # Check for None values
            if not pickup_time or not dropoff_time:
                return False, "Pickup time and dropoff time are required"
            
            # Handle both HH:MM and HH:MM:SS formats
            pickup_time_formatted = pickup_time if len(pickup_time.split(':')) == 3 else f"{pickup_time}:00"
            dropoff_time_formatted = dropoff_time if len(dropoff_time.split(':')) == 3 else f"{dropoff_time}:00"
            
            pickup_dt = datetime.strptime(f"{pickup_date} {pickup_time_formatted}", "%Y-%m-%d %H:%M:%S")
            dropoff_dt = datetime.strptime(f"{dropoff_date} {dropoff_time_formatted}", "%Y-%m-%d %H:%M:%S")
            
            # Make timezone aware
            pickup_dt = timezone.make_aware(pickup_dt)
            dropoff_dt = timezone.make_aware(dropoff_dt)
        except ValueError as e:
            logger.error(f"Date/time parsing error: {e}")
            return False, "Invalid date/time format"
        
        # Calculate rental duration
        days, hours, total_hours = car_rental.calculate_rental_duration(
            pickup_date, dropoff_date, pickup_time, dropoff_time
        )
        
        # Validate based on rental type
        if pickup_date == dropoff_date:
            # Same day rental (hourly)
            if not car_rental.allow_hourly_rental:
                return False, "Same-day rental not allowed for this car"
            
            if total_hours < car_rental.min_rent_hours:
                return False, f"Minimum rental period is {car_rental.min_rent_hours} hours for same-day rental"
            
            if total_hours > car_rental.max_hourly_rental_hours:
                return False, f"Maximum same-day rental is {car_rental.max_hourly_rental_hours} hours"
            
            if not car_rental.price_per_hour:
                return False, "Hourly pricing not available for this car"
        
        else:
            # Multi-day rental
            if days < car_rental.min_rent_days:
                return False, f"Minimum rental period is {car_rental.min_rent_days} days"
            
            if days > car_rental.max_rent_days:
                return False, f"Maximum rental period is {car_rental.max_rent_days} days"
        
        # Check advance booking (skip for testing)
        # now = timezone.now()
        # min_pickup_time = now + timezone.timedelta(hours=6)
        # 
        # if pickup_dt < min_pickup_time:
        #     return False, "Pickup time must be at least 6 hours from now"
        
        return True, ""
