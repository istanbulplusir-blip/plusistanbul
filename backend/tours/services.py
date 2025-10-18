"""
Tour capacity management service for atomic operations and business logic.
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Optional, Tuple
from decimal import Decimal
from .models import TourSchedule, TourVariant, TourPricing, TourScheduleVariantCapacity


class TourCapacityService:
    """Service for managing tour capacity with atomic operations."""

    @staticmethod
    def get_variant_capacity(schedule_id: str, variant_id: str) -> Optional[TourScheduleVariantCapacity]:
        """
        Get variant capacity record for a schedule and variant.
        
        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID
            
        Returns:
            TourScheduleVariantCapacity instance or None
        """
        try:
            return TourScheduleVariantCapacity.objects.get(
                schedule_id=schedule_id,
                variant_id=variant_id
            )
        except TourScheduleVariantCapacity.DoesNotExist:
            return None

    @staticmethod
    def create_variant_capacity(schedule_id: str, variant_id: str, total_capacity: int = None) -> TourScheduleVariantCapacity:
        """
        Create or get variant capacity record.
        
        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID
            total_capacity: Total capacity (defaults to variant capacity)
            
        Returns:
            TourScheduleVariantCapacity instance
        """
        try:
            schedule = TourSchedule.objects.get(id=schedule_id)
            variant = TourVariant.objects.get(id=variant_id, tour=schedule.tour)
            
            if total_capacity is None:
                total_capacity = variant.capacity
            
            capacity, created = TourScheduleVariantCapacity.objects.get_or_create(
                schedule=schedule,
                variant=variant,
                defaults={
                    'total_capacity': total_capacity,
                    'reserved_capacity': 0,
                    'confirmed_capacity': 0,
                    'is_available': True,
                }
            )
            return capacity
        except (TourSchedule.DoesNotExist, TourVariant.DoesNotExist) as e:
            raise ValidationError(f"Schedule or variant not found: {e}")

    @staticmethod
    def check_capacity_availability_relational(schedule_id: str, variant_id: str, quantity: int = 1) -> Tuple[bool, str]:
        """
        Check if capacity is available using relational model.
        
        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID
            quantity: Number of participants
            
        Returns:
            Tuple[bool, str]: (is_available, error_message)
        """
        try:
            capacity = TourScheduleVariantCapacity.objects.get(
                schedule_id=schedule_id,
                variant_id=variant_id
            )
            
            if not capacity.is_available:
                return False, "Variant is not available for this schedule"
            
            if capacity.available_capacity < quantity:
                return False, f"Insufficient capacity. Available: {capacity.available_capacity}, Required: {quantity}"
            
            return True, ""
            
        except TourScheduleVariantCapacity.DoesNotExist:
            # Try to create from variant defaults
            try:
                capacity = TourCapacityService.create_variant_capacity(schedule_id, variant_id)
                if capacity.available_capacity < quantity:
                    return False, f"Insufficient capacity. Available: {capacity.available_capacity}, Required: {quantity}"
                return True, ""
            except ValidationError as e:
                return False, str(e)

    @staticmethod
    def reserve_capacity_relational(schedule_id: str, variant_id: str, quantity: int = 1) -> Tuple[bool, str]:
        """
        Reserve capacity using relational model with atomic operations.
        
        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID
            quantity: Number of participants to reserve
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if quantity <= 0:
            return True, ""
        
        with transaction.atomic():
            try:
                capacity = TourScheduleVariantCapacity.objects.select_for_update().get(
                    schedule_id=schedule_id,
                    variant_id=variant_id
                )
                
                if not capacity.is_available:
                    return False, "Variant is not available for this schedule"
                
                if capacity.available_capacity < quantity:
                    return False, f"Insufficient capacity. Available: {capacity.available_capacity}, Required: {quantity}"
                
                # Reserve capacity
                capacity.reserved_capacity += quantity
                capacity.save(update_fields=['reserved_capacity'])
                
                return True, ""
                
            except TourScheduleVariantCapacity.DoesNotExist:
                # Create capacity record and reserve
                try:
                    capacity = TourCapacityService.create_variant_capacity(schedule_id, variant_id)
                    if capacity.available_capacity < quantity:
                        return False, f"Insufficient capacity. Available: {capacity.available_capacity}, Required: {quantity}"
                    
                    capacity.reserved_capacity = quantity
                    capacity.save(update_fields=['reserved_capacity'])
                    return True, ""
                    
                except ValidationError as e:
                    return False, str(e)

    @staticmethod
    def release_capacity_relational(schedule_id: str, variant_id: str, quantity: int = 1) -> Tuple[bool, str]:
        """
        Release reserved capacity using relational model.
        
        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID
            quantity: Number of participants to release
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if quantity <= 0:
            return True, ""
        
        with transaction.atomic():
            try:
                capacity = TourScheduleVariantCapacity.objects.select_for_update().get(
                    schedule_id=schedule_id,
                    variant_id=variant_id
                )
                
                if capacity.reserved_capacity < quantity:
                    return False, f"Cannot release {quantity} capacity. Only {capacity.reserved_capacity} is reserved"
                
                capacity.reserved_capacity -= quantity
                capacity.save(update_fields=['reserved_capacity'])
                
                return True, ""
                
            except TourScheduleVariantCapacity.DoesNotExist:
                return False, "Capacity record not found"

    @staticmethod
    def confirm_capacity_relational(schedule_id: str, variant_id: str, quantity: int = 1) -> Tuple[bool, str]:
        """
        Confirm reserved capacity using relational model.
        
        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID
            quantity: Number of participants to confirm
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if quantity <= 0:
            return True, ""
        
        with transaction.atomic():
            try:
                capacity = TourScheduleVariantCapacity.objects.select_for_update().get(
                    schedule_id=schedule_id,
                    variant_id=variant_id
                )
                
                if capacity.reserved_capacity < quantity:
                    return False, f"Cannot confirm {quantity} capacity. Only {capacity.reserved_capacity} is reserved"
                
                # Move from reserved to confirmed
                capacity.reserved_capacity -= quantity
                capacity.confirmed_capacity += quantity
                capacity.save(update_fields=['reserved_capacity', 'confirmed_capacity'])
                
                return True, ""
                
            except TourScheduleVariantCapacity.DoesNotExist:
                return False, "Capacity record not found"

    @staticmethod
    def cancel_capacity_relational(schedule_id: str, variant_id: str, quantity: int = 1) -> Tuple[bool, str]:
        """
        Cancel confirmed capacity using relational model.
        
        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID
            quantity: Number of participants to cancel
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if quantity <= 0:
            return True, ""
        
        with transaction.atomic():
            try:
                capacity = TourScheduleVariantCapacity.objects.select_for_update().get(
                    schedule_id=schedule_id,
                    variant_id=variant_id
                )
                
                if capacity.confirmed_capacity < quantity:
                    return False, f"Cannot cancel {quantity} capacity. Only {capacity.confirmed_capacity} is confirmed"
                
                capacity.confirmed_capacity -= quantity
                capacity.save(update_fields=['confirmed_capacity'])
                
                return True, ""
                
            except TourScheduleVariantCapacity.DoesNotExist:
                return False, "Capacity record not found"

    @staticmethod
    def get_available_capacity_relational(schedule_id: str, variant_id: str = None) -> int:
        """
        Get available capacity using relational model.
        
        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID (optional, if None returns total for all variants)
            
        Returns:
            Available capacity
        """
        if variant_id:
            try:
                capacity = TourScheduleVariantCapacity.objects.get(
                    schedule_id=schedule_id,
                    variant_id=variant_id
                )
                return capacity.available_capacity
            except TourScheduleVariantCapacity.DoesNotExist:
                return 0
        else:
            # Return total available capacity for all variants
            total_available = 0
            for capacity in TourScheduleVariantCapacity.objects.filter(schedule_id=schedule_id):
                total_available += capacity.available_capacity
            return total_available

    # Legacy methods for backward compatibility
    @staticmethod
    def check_capacity_availability(schedule_id: str, variant_id: str = None, quantity: int = 0) -> Tuple[bool, str]:
        """
        Check if capacity is available for a tour schedule and variant.
        This does NOT reserve capacity, just checks availability.

        Args:
            schedule_id: The schedule ID
            variant_id: The variant ID (optional)
            quantity: Number of participants

        Returns:
            Tuple[bool, str]: (is_available, error_message)
        """
        from tours.models import TourSchedule

        try:
            schedule = TourSchedule.objects.get(id=schedule_id)
            variant_id_str = str(variant_id) if variant_id else None

            if variant_id_str:
                # Check variant-specific capacity
                capacities = schedule.variant_capacities_raw or {}
                if variant_id_str not in capacities:
                    # Initialize if missing
                    from tours.models import TourVariant
                    try:
                        variant = TourVariant.objects.get(id=variant_id, tour=schedule.tour)
                        capacities[variant_id_str] = {
                            'total': variant.capacity,
                            'booked': 0,
                            'available': variant.capacity
                        }
                    except TourVariant.DoesNotExist:
                        return False, "Variant not found"

                available = capacities[variant_id_str].get('available', 0)
                if available < quantity:
                    return False, f"Insufficient capacity for variant. Available: {available}, Requested: {quantity}"
            else:
                # Check total capacity
                total_available = schedule.max_capacity - schedule.total_reserved_capacity - schedule.total_confirmed_capacity
                if total_available < quantity:
                    return False, f"Insufficient total capacity. Available: {total_available}, Requested: {quantity}"

            return True, ""

        except TourSchedule.DoesNotExist:
            return False, "Schedule not found"
        except Exception as e:
            return False, f"Capacity check failed: {str(e)}"

    @staticmethod
    def reserve_capacity(schedule_id: str, variant_id: str = None, quantity: int = 0) -> Tuple[bool, str]:
        """
        Reserve capacity for a tour schedule and variant.
        This is now just an orchestration layer - actual logic is in model methods.

        Args:
            schedule_id: UUID of the tour schedule
            variant_id: UUID of the tour variant (optional)
            quantity: Number of spots to reserve

        Returns:
            Tuple of (success, error_message)
        """
        if quantity <= 0:
            return True, ""

        try:
            # Use model's atomic reserve method
            schedule = TourSchedule.objects.get(id=schedule_id)

            if variant_id:
                # Reserve variant-specific capacity using model method
                success = schedule.reserve_capacity_atomic(variant_id, quantity)
                if not success:
                    return False, f"Insufficient capacity for variant {variant_id}"
            else:
                # Update total counters only (no variant specified)
                with transaction.atomic():
                    schedule = TourSchedule.objects.select_for_update().get(id=schedule_id)
                    schedule.total_reserved_capacity += quantity
                    schedule.save()

            return True, ""

        except TourSchedule.DoesNotExist:
            return False, f"Invalid schedule: {schedule_id}"
        except Exception as e:
            return False, f"Capacity reservation failed: {str(e)}"

    @staticmethod
    def release_capacity(schedule_id: str, variant_id: str, quantity: int) -> Tuple[bool, str]:
        """Release reserved capacity for a tour schedule and variant."""
        if quantity <= 0:
            return True, ""

        try:
            with transaction.atomic():
                schedule = TourSchedule.objects.select_for_update().get(id=schedule_id)
                capacities = schedule.variant_capacities_raw or {}
                variant_key = str(variant_id)

                if variant_key not in capacities:
                    return False, "Variant capacity not found"

                booked = capacities[variant_key].get('booked', 0)
                if booked < quantity:
                    return False, f"Cannot release more than booked. Booked: {booked}, Requested: {quantity}"

                # Release capacity
                capacities[variant_key]['booked'] = booked - quantity
                capacities[variant_key]['available'] = capacities[variant_key]['total'] - capacities[variant_key]['booked']

                schedule.variant_capacities_raw = capacities
                schedule.total_reserved_capacity = max(0, schedule.total_reserved_capacity - quantity)
                schedule.save()

                return True, ""

        except TourSchedule.DoesNotExist:
            return False, "Schedule not found"
        except Exception as e:
            return False, f"Capacity release failed: {str(e)}"

    @staticmethod
    def confirm_capacity(schedule_id: str, variant_id: str = None, quantity: int = 0) -> Tuple[bool, str]:
        """
        Convert reserved capacity to confirmed capacity.
        This method is called when an order changes from pending to paid/confirmed.
        This is now just an orchestration layer - actual logic is in model methods.
        """
        if quantity <= 0:
            return True, ""

        try:
            # Use model's atomic confirm method
            schedule = TourSchedule.objects.get(id=schedule_id)

            if variant_id:
                # Confirm variant-specific capacity using model method
                success = schedule.confirm_capacity_atomic(variant_id, quantity)
                if not success:
                    return False, f"Failed to confirm capacity for variant {variant_id}"
            else:
                # Update total counters only (no variant specified)
                with transaction.atomic():
                    schedule = TourSchedule.objects.select_for_update().get(id=schedule_id)
                    schedule.total_reserved_capacity = max(0, schedule.total_reserved_capacity - quantity)
                    schedule.total_confirmed_capacity += quantity
                    schedule.save()

            return True, ""

        except TourSchedule.DoesNotExist:
            return False, "Schedule not found"
        except Exception as e:
            return False, f"Capacity confirmation failed: {str(e)}"

    @staticmethod
    def cancel_capacity(schedule_id: str, quantity: int) -> Tuple[bool, str]:
        """
        Release confirmed capacity (e.g., when order is cancelled).
        """
        if quantity <= 0:
            return True, ""

        try:
            with transaction.atomic():
                schedule = TourSchedule.objects.select_for_update().get(id=schedule_id)

                if schedule.total_confirmed_capacity < quantity:
                    return False, f"Insufficient confirmed capacity. Confirmed: {schedule.total_confirmed_capacity}, Requested: {quantity}"

                # Release confirmed capacity
                schedule.total_confirmed_capacity -= quantity
                schedule.save()

                return True, ""

        except TourSchedule.DoesNotExist:
            return False, "Schedule not found"
        except Exception as e:
            return False, f"Capacity cancellation failed: {str(e)}"

    @staticmethod
    def get_available_capacity(schedule_id: str, variant_id: str = None) -> int:
        """
        Get available capacity for a specific variant in a schedule.
        Now uses new relational model for consistency.
        """
        try:
            schedule = TourSchedule.objects.get(id=schedule_id)

            if variant_id:
                # Try to get from new relational model first
                try:
                    from .models import TourScheduleVariantCapacity
                    capacity_obj = TourScheduleVariantCapacity.objects.get(
                        schedule=schedule, 
                        variant__id=variant_id
                    )
                    return capacity_obj.available_capacity
                except TourScheduleVariantCapacity.DoesNotExist:
                    # Fallback to variant's base capacity
                    try:
                        variant = TourVariant.objects.get(id=variant_id, tour=schedule.tour)
                        return variant.capacity
                    except TourVariant.DoesNotExist:
                        return 0
            else:
                # Return total available capacity for the schedule
                return schedule.available_capacity

        except TourSchedule.DoesNotExist:
            return 0
        except Exception:
            return 0

    @staticmethod
    def _calculate_variant_available_capacity(schedule: 'TourSchedule', variant_key: str) -> int:
        """Calculate available capacity for a variant using unified method."""
        try:
            capacities = schedule.variant_capacities_raw or {}
            variant_data = capacities.get(variant_key, {})
            
            total_capacity = variant_data.get('total', 0)
            booked_capacity = variant_data.get('booked', 0)
            
            # Calculate real-time availability from cart and orders
            from cart.models import CartItem
            from orders.models import OrderItem
            from django.db.models import Sum
            
            # Calculate participants from confirmed orders (adults + children only)
            confirmed_items = OrderItem.objects.filter(
                product_type='tour',
                product_id=schedule.tour.id,
                variant_id=variant_key,
                booking_data__schedule_id=str(schedule.id),
                order__status__in=['confirmed', 'paid', 'completed']
            )
            
            total_participants = 0
            for item in confirmed_items:
                booking_data = item.booking_data or {}
                participants = booking_data.get('participants', {}) or {}
                adult_count = int(participants.get('adult', 0))
                child_count = int(participants.get('child', 0))
                total_participants += adult_count + child_count
            
            available = max(0, total_capacity - total_participants)
            
            return available
            
        except Exception:
            # Fallback to stored capacity data
            return variant_data.get('available', 0)


class TourPricingService:
    """Service for calculating tour pricing with proper business logic."""

    @staticmethod
    def calculate_price(tour, variant, participants, selected_options=None):
        """
        Calculate total price for tour booking.

        Args:
            tour: Tour instance
            variant: TourVariant instance
            participants: Dict with adult, child, infant counts
            selected_options: List of selected option dicts

        Returns:
            Dict with pricing breakdown
        """
        from decimal import Decimal

        total = Decimal('0.00')
        breakdown = {
            'adult': Decimal('0.00'),
            'child': Decimal('0.00'),
            'infant': Decimal('0.00'),
            'options': Decimal('0.00')
        }

        # Calculate participant pricing
        # Map frontend keys to backend keys
        age_group_mapping = {
            'adults': 'adult',
            'children': 'child', 
            'infants': 'infant'
        }
        
        for frontend_key, count in participants.items():
            if count > 0:
                age_group = age_group_mapping.get(frontend_key, frontend_key)
                
                try:
                    pricing = TourPricing.objects.get(
                        tour=tour,
                        variant=variant,
                        age_group=age_group
                    )
                    # Infants are always free
                    if age_group == 'infant' or pricing.is_free:
                        price = Decimal('0.00')
                    else:
                        price = pricing.final_price
                except TourPricing.DoesNotExist:
                    # Fallback to variant base price, infants free
                    if age_group == 'infant':
                        price = Decimal('0.00')
                    else:
                        price = variant.base_price

                cost = price * count
                breakdown[age_group] = cost  # Use age_group instead of frontend_key
                total += cost

        # Calculate options pricing
        if selected_options:
            for option in selected_options:
                option_price = Decimal(str(option.get('price', 0)))
                option_quantity = int(option.get('quantity', 1))
                option_cost = option_price * option_quantity
                breakdown['options'] += option_cost
                total += option_cost

        return {
            'total': total,
            'breakdown': breakdown,
            'currency': tour.currency
        }
