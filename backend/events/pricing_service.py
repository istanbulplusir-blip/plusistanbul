"""
Event Pricing Service for comprehensive price calculation.
Handles base price, options, discounts, fees, and taxes.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.utils import timezone
from .models import Event, EventPerformance, EventSection, SectionTicketType, EventOption, EventBooking


class EventPriceCalculator:
    """
    Comprehensive price calculator for events with caching.
    """
    
    def __init__(self, event: Event, performance: EventPerformance):
        self.event = event
        self.performance = performance
        self.currency = 'USD'  # Default currency
        self.cache_timeout = 300  # 5 minutes cache
    
    def _get_cache_key(self, section_name: str, ticket_type_id: str, quantity: int, 
                       selected_options: Optional[List[Dict]] = None, discount_code: Optional[str] = None,
                       is_group_booking: bool = False, apply_fees: bool = False, apply_taxes: bool = False) -> str:
        """Generate cache key for pricing calculation."""
        # Sort options by option_id to ensure consistent cache keys
        if selected_options:
            sorted_options = sorted(selected_options, key=lambda x: x.get('option_id', ''))
            options_hash = hash(str(sorted_options))
        else:
            options_hash = hash('[]')
        cache_key = f"pricing_{self.event.id}_{self.performance.id}_{section_name}_{ticket_type_id}_{quantity}_{options_hash}_{discount_code}_{is_group_booking}_{apply_fees}_{apply_taxes}"
        return cache_key
    
    def calculate_ticket_price(
        self,
        section_name: str,
        ticket_type_id: str,
        quantity: int = 1,
        selected_options: Optional[List[Dict]] = None,
        discount_code: Optional[str] = None,
        is_group_booking: bool = False,
        apply_fees: bool = False,
        apply_taxes: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive ticket price with all components and caching.
        
        Args:
            section_name: Name of the section (e.g., 'VIP', 'Normal')
            ticket_type_id: ID of the ticket type
            quantity: Number of tickets
            selected_options: List of selected options with quantities
            discount_code: Optional discount/promo code
            is_group_booking: Whether this is a group booking
            apply_fees: Whether to apply service fees
            apply_taxes: Whether to apply taxes
            use_cache: Whether to use caching (default: True)
        
        Returns:
            Dict with complete price breakdown
        """
        # Try to get from cache first
        if use_cache:
            cache_key = self._get_cache_key(
                section_name, ticket_type_id, quantity, selected_options,
                discount_code, is_group_booking, apply_fees, apply_taxes
            )
            cached_result = cache.get(cache_key)
            if cached_result:
                # Update timestamp for cache freshness
                cached_result['calculation_timestamp'] = timezone.now().isoformat()
                cached_result['from_cache'] = True
                return cached_result
        
        try:
            # Validate inputs
            if quantity <= 0:
                raise ValidationError(_('Quantity must be positive'))
            
            if not section_name or not ticket_type_id:
                raise ValidationError(_('Section name and ticket type ID are required'))
            
            # Get section and ticket type with validation
            try:
                section = self.performance.sections.get(name=section_name)
            except EventSection.DoesNotExist:
                raise ValidationError(_(f'Section "{section_name}" not found for this performance'))
            
            try:
                section_ticket = section.ticket_types.get(ticket_type__id=ticket_type_id)
            except SectionTicketType.DoesNotExist:
                raise ValidationError(_(f'Ticket type "{ticket_type_id}" not available in section "{section_name}"'))
            
            # Validate capacity
            if section_ticket.available_capacity < quantity:
                raise ValidationError(
                    _(f'Only {section_ticket.available_capacity} seats available, {quantity} requested')
                )
            
            # Base calculation with validation
            base_price = section.base_price
            if base_price <= 0:
                raise ValidationError(_('Base price must be positive'))
            
            price_modifier = section_ticket.price_modifier
            if price_modifier <= 0:
                raise ValidationError(_('Price modifier must be positive'))
            
            unit_price = base_price * price_modifier
            
            # Calculate subtotal
            subtotal = unit_price * quantity
            
            # Initialize breakdown with better structure
            breakdown = {
                'base_price': base_price,
                'price_modifier': price_modifier,
                'unit_price': unit_price,
                'quantity': quantity,
                'subtotal': subtotal,
                'options': [],
                'options_total': Decimal('0.00'),
                'discounts': [],
                'discount_total': Decimal('0.00'),
                'fees': [],
                'fees_total': Decimal('0.00'),
                'taxes': [],
                'taxes_total': Decimal('0.00'),
                'final_price': Decimal('0.00'),
                'currency': self.currency,
                'calculation_timestamp': timezone.now().isoformat(),
                'from_cache': False
            }
            
            # Calculate options with validation
            if selected_options:
                try:
                    options_result = self._calculate_options(selected_options, subtotal)
                    breakdown['options'] = options_result['options']
                    breakdown['options_total'] = options_result['total']
                except Exception as e:
                    raise ValidationError(_(f'Error calculating options: {str(e)}'))
            
            # Calculate discounts with validation
            if discount_code or is_group_booking:
                try:
                    discounts_result = self._calculate_discounts(
                        subtotal + breakdown['options_total'],
                        discount_code,
                        is_group_booking
                    )
                    breakdown['discounts'] = discounts_result['discounts']
                    breakdown['discount_total'] = discounts_result['total']
                except Exception as e:
                    raise ValidationError(_(f'Error calculating discounts: {str(e)}'))
            
            # Calculate fees with validation
            if apply_fees:
                try:
                    fees_result = self._calculate_fees(
                        subtotal + breakdown['options_total'] - breakdown['discount_total']
                    )
                    breakdown['fees'] = fees_result['fees']
                    breakdown['fees_total'] = fees_result['total']
                except Exception as e:
                    raise ValidationError(_(f'Error calculating fees: {str(e)}'))
            
            # Calculate taxes with validation
            if apply_taxes:
                try:
                    taxes_result = self._calculate_taxes(
                        subtotal + breakdown['options_total'] - breakdown['discount_total'] + breakdown['fees_total']
                    )
                    breakdown['taxes'] = taxes_result['taxes']
                    breakdown['taxes_total'] = taxes_result['total']
                except Exception as e:
                    raise ValidationError(_(f'Error calculating taxes: {str(e)}'))
            
            # Calculate final price
            final_price = (
                subtotal + 
                breakdown['options_total'] - 
                breakdown['discount_total'] + 
                breakdown['fees_total'] + 
                breakdown['taxes_total']
            )
            
            # Ensure final price is not negative
            if final_price < 0:
                final_price = Decimal('0.00')
            
            breakdown['final_price'] = final_price
            
            # Add summary information
            breakdown['summary'] = {
                'total_before_discount': subtotal + breakdown['options_total'],
                'total_after_discount': subtotal + breakdown['options_total'] - breakdown['discount_total'],
                'total_with_fees': subtotal + breakdown['options_total'] - breakdown['discount_total'] + breakdown['fees_total'],
                'final_total': final_price
            }
            
            # Cache the result if caching is enabled
            if use_cache:
                cache_key = self._get_cache_key(
                    section_name, ticket_type_id, quantity, selected_options,
                    discount_code, is_group_booking, apply_fees, apply_taxes
                )
                cache.set(cache_key, breakdown, self.cache_timeout)
            
            return breakdown
            
        except ValidationError:
            raise
        except Exception as e:
            # Log unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in calculate_ticket_price: {e}")
            raise ValidationError(_('Price calculation failed due to unexpected error'))
    
    def _calculate_options(self, selected_options: List[Dict], subtotal: Decimal) -> Dict[str, Any]:
        """Calculate options pricing."""
        options_breakdown = []
        options_total = Decimal('0.00')
        
        for option_data in selected_options:
            option_id = option_data.get('option_id')
            quantity = int(option_data.get('quantity', 1))
            
            try:
                option = EventOption.objects.get(
                    id=option_id,
                    event=self.event,
                    is_active=True
                )
                
                # Calculate option price
                if hasattr(option, 'price_percentage') and option.price_percentage > 0:
                    # Percentage-based pricing
                    option_price = subtotal * (option.price_percentage / Decimal('100'))
                else:
                    # Fixed pricing
                    option_price = option.price
                
                option_total = option_price * quantity
                options_total += option_total
                
                options_breakdown.append({
                    'option_id': str(option.id),
                    'name': option.name,
                    'type': option.option_type,
                    'price': option_price,
                    'quantity': quantity,
                    'total': option_total
                })
                
            except EventOption.DoesNotExist:
                continue
        
        return {
            'options': options_breakdown,
            'total': options_total
        }
    
    def _calculate_discounts(
        self,
        amount: Decimal,
        discount_code: Optional[str] = None,
        is_group_booking: bool = False
    ) -> Dict[str, Any]:
        """Calculate discounts."""
        discounts = []
        discount_total = Decimal('0.00')
        
        # Group booking discount
        if is_group_booking and amount >= Decimal('500.00'):
            group_discount = amount * Decimal('0.10')  # 10% for groups over $500
            discount_total += group_discount
            discounts.append({
                'type': 'group_booking',
                'name': 'Group Booking Discount',
                'percentage': 10.0,
                'amount': group_discount
            })
        
        # Promo code discount (placeholder for future implementation)
        if discount_code:
            # TODO: Implement promo code validation and calculation
            # For now, apply a mock 5% discount
            promo_discount = amount * Decimal('0.05')
            discount_total += promo_discount
            discounts.append({
                'type': 'promo_code',
                'name': f'Promo Code: {discount_code}',
                'percentage': 5.0,
                'amount': promo_discount
            })
        
        return {
            'discounts': discounts,
            'total': discount_total
        }
    
    def _calculate_fees(self, amount: Decimal) -> Dict[str, Any]:
        """Calculate service fees."""
        fees = []
        fees_total = Decimal('0.00')
        
        # Service fee (3% of amount)
        service_fee = amount * Decimal('0.03')
        fees_total += service_fee
        fees.append({
            'type': 'service_fee',
            'name': 'Service Fee',
            'percentage': 3.0,
            'amount': service_fee
        })
        
        # Booking fee (fixed $2.50 per booking)
        booking_fee = Decimal('2.50')
        fees_total += booking_fee
        fees.append({
            'type': 'booking_fee',
            'name': 'Booking Fee',
            'percentage': 0.0,
            'amount': booking_fee
        })
        
        return {
            'fees': fees,
            'total': fees_total
        }
    
    def _calculate_taxes(self, amount: Decimal) -> Dict[str, Any]:
        """Calculate taxes."""
        taxes = []
        taxes_total = Decimal('0.00')
        
        # VAT (9% for events in Iran)
        vat_rate = Decimal('0.09')
        vat_amount = amount * vat_rate
        taxes_total += vat_amount
        taxes.append({
            'type': 'vat',
            'name': 'Value Added Tax (VAT)',
            'percentage': 9.0,
            'amount': vat_amount
        })
        
        return {
            'taxes': taxes,
            'total': taxes_total
        }
    
    def get_available_sections(self) -> List[Dict]:
        """Get available sections with pricing information."""
        sections = []
        
        for section in self.performance.sections.all():
            section_data = {
                'name': section.name,
                'description': section.description,
                'base_price': float(section.base_price),
                'total_capacity': section.total_capacity,
                'available_capacity': section.available_capacity,
                'is_premium': section.is_premium,
                'is_wheelchair_accessible': section.is_wheelchair_accessible,
                'ticket_types': []
            }
            
            for stt in section.ticket_types.all():
                ticket_data = {
                    'id': str(stt.ticket_type.id),
                    'name': stt.ticket_type.name,
                    'price_modifier': float(stt.price_modifier),
                    'final_price': float(stt.final_price),
                    'allocated_capacity': stt.allocated_capacity,
                    'available_capacity': stt.available_capacity
                }
                section_data['ticket_types'].append(ticket_data)
            
            sections.append(section_data)
        
        return sections
    
    def get_available_options(self) -> List[Dict]:
        """Get available options for this event."""
        options = []
        
        for option in self.event.options.filter(is_active=True):
            option_data = {
                'id': str(option.id),
                'name': option.name,
                'description': option.description,
                'type': option.option_type,
                'price': float(option.price),
                'price_percentage': float(getattr(option, 'price_percentage', 0)),
                'max_quantity': option.max_quantity,
                'is_available': option.is_available
            }
            options.append(option_data)
        
        return options
    
    @staticmethod
    def validate_booking(
        performance: EventPerformance,
        section_name: str,
        ticket_type_id: str,
        quantity: int
    ) -> bool:
        """Validate if booking is possible."""
        try:
            section = performance.sections.get(name=section_name)
            section_ticket = section.ticket_types.get(ticket_type_id=ticket_type_id)
            
            # Check capacity
            if section_ticket.available_capacity < quantity:
                return False
            
            # Check if performance is available
            if not performance.is_available:
                return False
            
            return True
            
        except (EventSection.DoesNotExist, SectionTicketType.DoesNotExist):
            return False
    
    @staticmethod
    def reserve_tickets(
        performance: EventPerformance,
        section_name: str,
        ticket_type_id: str,
        quantity: int
    ) -> bool:
        """Reserve tickets for a booking."""
        try:
            section = performance.sections.get(name=section_name)
            section_ticket = section.ticket_types.get(ticket_type_id=ticket_type_id)
            
            if section_ticket.can_reserve(quantity):
                section_ticket.reserve_capacity(quantity)
                return True
            
            return False
            
        except (EventSection.DoesNotExist, SectionTicketType.DoesNotExist):
            return False
    
    @staticmethod
    def release_tickets(
        performance: EventPerformance,
        section_name: str,
        ticket_type_id: str,
        quantity: int
    ) -> bool:
        """Release reserved tickets."""
        try:
            section = performance.sections.get(name=section_name)
            section_ticket = section.ticket_types.get(ticket_type_id=ticket_type_id)
            
            section_ticket.release_capacity(quantity)
            return True
            
        except (EventSection.DoesNotExist, SectionTicketType.DoesNotExist):
            return False

    def clear_pricing_cache(self, section_name: str = None, ticket_type_id: str = None):
        """Clear pricing cache for specific section or ticket type."""
        if section_name and ticket_type_id:
            # Clear specific cache
            cache_key_pattern = f"pricing_{self.event.id}_{self.performance.id}_{section_name}_{ticket_type_id}_*"
            # Note: Django cache doesn't support pattern deletion, so we'll clear all related caches
            cache.delete_pattern(cache_key_pattern)
        else:
            # Clear all pricing caches for this event/performance
            cache_key_pattern = f"pricing_{self.event.id}_{self.performance.id}_*"
            cache.delete_pattern(cache_key_pattern)
    
    def calculate_bulk_pricing(
        self,
        ticket_requests: List[Dict],
        discount_code: Optional[str] = None,
        is_group_booking: bool = False,
        apply_fees: bool = False,
        apply_taxes: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate pricing for multiple ticket requests efficiently.
        
        Args:
            ticket_requests: List of ticket requests with section_name, ticket_type_id, quantity
            discount_code: Optional discount/promo code
            is_group_booking: Whether this is a group booking
            apply_fees: Whether to apply service fees
            apply_taxes: Whether to apply taxes
            use_cache: Whether to use caching
        
        Returns:
            Dict with bulk pricing breakdown
        """
        if not ticket_requests:
            raise ValidationError(_('At least one ticket request is required'))
        
        bulk_result = {
            'tickets': [],
            'subtotal': Decimal('0.00'),
            'options_total': Decimal('0.00'),
            'discount_total': Decimal('0.00'),
            'fees_total': Decimal('0.00'),
            'taxes_total': Decimal('0.00'),
            'final_total': Decimal('0.00'),
            'currency': self.currency,
            'calculation_timestamp': timezone.now().isoformat(),
            'summary': {
                'total_tickets': 0,
                'total_sections': 0,
                'total_ticket_types': 0
            }
        }
        
        # Track unique sections and ticket types for summary
        unique_sections = set()
        unique_ticket_types = set()
        total_tickets = 0
        
        # Calculate individual ticket prices
        for request in ticket_requests:
            try:
                section_name = request.get('section_name')
                ticket_type_id = request.get('ticket_type_id')
                quantity = request.get('quantity', 1)
                selected_options = request.get('selected_options', [])
                
                if not section_name or not ticket_type_id:
                    raise ValidationError(_('Section name and ticket type ID are required for each request'))
                
                # Calculate individual ticket price
                ticket_price = self.calculate_ticket_price(
                    section_name=section_name,
                    ticket_type_id=ticket_type_id,
                    quantity=quantity,
                    selected_options=selected_options,
                    discount_code=None,  # Apply discount at bulk level
                    is_group_booking=False,  # Apply group discount at bulk level
                    apply_fees=apply_fees,
                    apply_taxes=apply_taxes,
                    use_cache=use_cache
                )
                
                # Add to bulk result
                bulk_result['tickets'].append({
                    'section_name': section_name,
                    'ticket_type_id': ticket_type_id,
                    'quantity': quantity,
                    'selected_options': selected_options,
                    'pricing': ticket_price
                })
                
                # Update totals
                bulk_result['subtotal'] += ticket_price['subtotal']
                bulk_result['options_total'] += ticket_price['options_total']
                bulk_result['fees_total'] += ticket_price['fees_total']
                bulk_result['taxes_total'] += ticket_price['taxes_total']
                
                # Update summary
                unique_sections.add(section_name)
                unique_ticket_types.add(ticket_type_id)
                total_tickets += quantity
                
            except Exception as e:
                # Log error but continue with other tickets
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error calculating price for ticket request {request}: {e}")
                continue
        
        # Apply bulk-level discounts
        if discount_code or is_group_booking:
            try:
                discounts_result = self._calculate_discounts(
                    bulk_result['subtotal'] + bulk_result['options_total'],
                    discount_code,
                    is_group_booking
                )
                bulk_result['discount_total'] = discounts_result['total']
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error calculating bulk discounts: {e}")
                bulk_result['discount_total'] = Decimal('0.00')
        
        # Calculate final total
        bulk_result['final_total'] = (
            bulk_result['subtotal'] + 
            bulk_result['options_total'] - 
            bulk_result['discount_total'] + 
            bulk_result['fees_total'] + 
            bulk_result['taxes_total']
        )
        
        # Ensure final total is not negative
        if bulk_result['final_total'] < 0:
            bulk_result['final_total'] = Decimal('0.00')
        
        # Update summary
        bulk_result['summary'].update({
            'total_tickets': total_tickets,
            'total_sections': len(unique_sections),
            'total_ticket_types': len(unique_ticket_types)
        })
        
        return bulk_result
    
    def get_pricing_summary(self, section_name: str = None) -> Dict[str, Any]:
        """
        Get pricing summary for a section or all sections.
        
        Args:
            section_name: Optional section name to filter
        
        Returns:
            Dict with pricing summary
        """
        sections = self.performance.sections.all()
        if section_name:
            sections = sections.filter(name=section_name)
        
        summary = {
            'event_id': self.event.id,
            'performance_id': self.performance.id,
            'sections': [],
            'total_capacity': 0,
            'available_capacity': 0,
            'price_range': {
                'min': Decimal('999999.99'),
                'max': Decimal('0.00')
            }
        }
        
        for section in sections:
            section_summary = {
                'name': section.name,
                'base_price': section.base_price,
                'total_capacity': section.total_capacity,
                'available_capacity': section.available_capacity,
                'ticket_types': []
            }
            
            # Get ticket types for this section
            for stt in section.ticket_types.all():
                ticket_summary = {
                    'id': stt.ticket_type.id,
                    'name': stt.ticket_type.name,
                    'price_modifier': stt.price_modifier,
                    'final_price': stt.final_price,
                    'allocated_capacity': stt.allocated_capacity,
                    'available_capacity': stt.available_capacity
                }
                section_summary['ticket_types'].append(ticket_summary)
                
                # Update price range
                if stt.final_price < summary['price_range']['min']:
                    summary['price_range']['min'] = stt.final_price
                if stt.final_price > summary['price_range']['max']:
                    summary['price_range']['max'] = stt.final_price
            
            summary['sections'].append(section_summary)
            summary['total_capacity'] += section.total_capacity
            summary['available_capacity'] += section.available_capacity
        
        # Reset price range if no tickets found
        if summary['price_range']['min'] == Decimal('999999.99'):
            summary['price_range']['min'] = Decimal('0.00')
        
        return summary


class EventPricingRules:
    """
    Rules and configurations for event pricing.
    """
    
    # Default fee rates
    SERVICE_FEE_RATE = Decimal('0.03')  # 3%
    BOOKING_FEE_AMOUNT = Decimal('2.50')  # $2.50
    VAT_RATE = Decimal('0.09')  # 9%
    
    # Discount rules
    GROUP_DISCOUNT_THRESHOLD = Decimal('500.00')  # $500
    GROUP_DISCOUNT_RATE = Decimal('0.10')  # 10%
    EARLY_BIRD_DISCOUNT_RATE = Decimal('0.15')  # 15%
    EARLY_BIRD_DAYS = 30  # 30 days before event
    
    # Capacity rules
    MIN_GROUP_SIZE = 10
    MAX_GROUP_SIZE = 100
    
    @classmethod
    def get_fee_rates(cls) -> Dict[str, Decimal]:
        """Get current fee rates."""
        return {
            'service_fee_rate': cls.SERVICE_FEE_RATE,
            'booking_fee_amount': cls.BOOKING_FEE_AMOUNT,
            'vat_rate': cls.VAT_RATE
        }
    
    @classmethod
    def get_discount_rules(cls) -> Dict[str, Any]:
        """Get current discount rules."""
        return {
            'group_discount_threshold': cls.GROUP_DISCOUNT_THRESHOLD,
            'group_discount_rate': cls.GROUP_DISCOUNT_RATE,
            'early_bird_discount_rate': cls.EARLY_BIRD_DISCOUNT_RATE,
            'early_bird_days': cls.EARLY_BIRD_DAYS,
            'min_group_size': cls.MIN_GROUP_SIZE,
            'max_group_size': cls.MAX_GROUP_SIZE
        } 