"""
Capacity Manager Service for Events.
Manages capacity across the entire hierarchy: Venue → Performance → Section → TicketType → Seat
"""

from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Q
from .models import Event, EventPerformance, EventSection, SectionTicketType, TicketType, Seat


class CapacityManager:
    """
    Service class for managing capacity across the entire hierarchy.
    """
    
    @staticmethod
    def validate_venue_capacity(venue, performances):
        """Validate that venue can accommodate all performances."""
        total_performance_capacity = sum(p.max_capacity for p in performances)
        if total_performance_capacity > venue.total_capacity:
            raise ValidationError(
                f'Total performance capacity ({total_performance_capacity}) '
                f'exceeds venue capacity ({venue.total_capacity})'
            )
    
    @staticmethod
    def validate_performance_capacity(performance, sections):
        """Validate that performance capacity matches sections."""
        total_section_capacity = sum(s.total_capacity for s in sections)
        if total_section_capacity != performance.max_capacity:
            raise ValidationError(
                f'Total section capacity ({total_section_capacity}) '
                f'does not match performance capacity ({performance.max_capacity})'
            )
    
    @staticmethod
    def validate_section_capacity(section, ticket_allocations):
        """Validate that section capacity matches ticket allocations."""
        total_ticket_capacity = sum(stt.allocated_capacity for stt in ticket_allocations)
        if total_ticket_capacity != section.total_capacity:
            raise ValidationError(
                f'Total ticket capacity ({total_ticket_capacity}) '
                f'does not match section capacity ({section.total_capacity})'
            )
    
    @staticmethod
    def create_performance_capacity(performance, capacity_config):
        """
        Create complete capacity structure for a performance.
        
        capacity_config = {
            'sections': [
                {
                    'name': 'VIP',
                    'total_capacity': 200,
                    'base_price': 150.00,
                    'is_premium': True,
                    'ticket_types': [
                        {'ticket_type_id': 'vip_id', 'allocated_capacity': 200, 'price_modifier': 1.5}
                    ]
                },
                {
                    'name': 'Normal',
                    'total_capacity': 800,
                    'base_price': 100.00,
                    'is_premium': False,
                    'ticket_types': [
                        {'ticket_type_id': 'normal_id', 'allocated_capacity': 800, 'price_modifier': 1.0}
                    ]
                }
            ]
        }
        """
        with transaction.atomic():
            # Validate venue capacity
            total_capacity = sum(s['total_capacity'] for s in capacity_config['sections'])
            if total_capacity > performance.event.venue.total_capacity:
                raise ValidationError('Total capacity exceeds venue capacity')
            
            # Update performance capacity
            performance.max_capacity = total_capacity
            performance.current_capacity = 0
            performance.save()
            
            # Create sections and ticket allocations
            for section_config in capacity_config['sections']:
                section = EventSection.objects.create(
                    performance=performance,
                    name=section_config['name'],
                    total_capacity=section_config['total_capacity'],
                    available_capacity=section_config['total_capacity'],
                    base_price=section_config['base_price'],
                    is_premium=section_config.get('is_premium', False)
                )
                
                for ticket_config in section_config['ticket_types']:
                    SectionTicketType.objects.create(
                        section=section,
                        ticket_type_id=ticket_config['ticket_type_id'],
                        allocated_capacity=ticket_config['allocated_capacity'],
                        available_capacity=ticket_config['allocated_capacity'],
                        price_modifier=ticket_config['price_modifier']
                    )
    
    @staticmethod
    def get_available_seats(performance, ticket_type_id=None, section_name=None):
        """Get available seats for a performance with optional filters."""
        query = Q(section__performance=performance, available_capacity__gt=0)
        
        if ticket_type_id:
            query &= Q(ticket_type_id=ticket_type_id)
        
        if section_name:
            query &= Q(section__name=section_name)
        
        return SectionTicketType.objects.filter(query).select_related(
            'section', 'ticket_type'
        )
    
    @staticmethod
    def reserve_seats(performance, ticket_type_id, section_name, count):
        """Reserve seats for a specific ticket type and section."""
        try:
            section_ticket = SectionTicketType.objects.get(
                section__performance=performance,
                section__name=section_name,
                ticket_type_id=ticket_type_id
            )
            
            section_ticket.reserve_capacity(count)
            return True, section_ticket
            
        except SectionTicketType.DoesNotExist:
            return False, "Section ticket type not found"
        except ValidationError as e:
            return False, str(e)
    
    @staticmethod
    def get_capacity_summary(performance):
        """Get comprehensive capacity summary for a performance."""
        sections = performance.sections.all()
        
        summary = {
            'performance': {
                'max_capacity': performance.max_capacity,
                'current_capacity': performance.current_capacity,
                'available_capacity': performance.available_capacity,
                'occupancy_rate': (performance.current_capacity / performance.max_capacity * 100) if performance.max_capacity > 0 else 0
            },
            'sections': []
        }
        
        for section in sections:
            section_summary = {
                'name': section.name,
                'total_capacity': section.total_capacity,
                'available_capacity': section.available_capacity,
                'reserved_capacity': section.reserved_capacity,
                'sold_capacity': section.sold_capacity,
                'occupancy_rate': section.occupancy_rate,
                'ticket_types': []
            }
            
            for stt in section.ticket_types.all():
                ticket_summary = {
                    'name': stt.ticket_type.name,
                    'allocated_capacity': stt.allocated_capacity,
                    'available_capacity': stt.available_capacity,
                    'reserved_capacity': stt.reserved_capacity,
                    'sold_capacity': stt.sold_capacity,
                    'final_price': stt.final_price
                }
                section_summary['ticket_types'].append(ticket_summary)
            
            summary['sections'].append(section_summary)
        
        return summary
    
    @staticmethod
    def migrate_existing_capacity_data():
        """
        Migrate existing capacity data to new structure.
        """
        print("🔄 Starting capacity migration...")
        
        for event in Event.objects.all():
            print(f"📅 Migrating event: {event.title}")
            
            for performance in event.performances.all():
                print(f"  - Performance: {performance.date}")
                
                # Group seats by section
                sections_data = {}
                for seat in performance.seats.all():
                    section_name = seat.section
                    if section_name not in sections_data:
                        sections_data[section_name] = {
                            'seats': [],
                            'ticket_types': set()
                        }
                    sections_data[section_name]['seats'].append(seat)
                    if seat.ticket_type:
                        sections_data[section_name]['ticket_types'].add(seat.ticket_type)
                
                # Create EventSection for each section
                total_performance_capacity = 0
                for section_name, data in sections_data.items():
                    total_seats = len(data['seats'])
                    total_performance_capacity += total_seats
                    
                    # Create section
                    section = EventSection.objects.create(
                        performance=performance,
                        name=section_name,
                        total_capacity=total_seats,
                        available_capacity=total_seats,
                        base_price=100.00  # Default price
                    )
                    
                    # Create SectionTicketType allocations
                    if data['ticket_types']:
                        # Distribute capacity among ticket types
                        capacity_per_ticket = total_seats // len(data['ticket_types'])
                        remaining_capacity = total_seats % len(data['ticket_types'])
                        
                        for i, ticket_type in enumerate(data['ticket_types']):
                            allocated_capacity = capacity_per_ticket
                            if i < remaining_capacity:
                                allocated_capacity += 1
                            
                            SectionTicketType.objects.create(
                                section=section,
                                ticket_type=ticket_type,
                                allocated_capacity=allocated_capacity,
                                available_capacity=allocated_capacity,
                                price_modifier=ticket_type.price_modifier
                            )
                    else:
                        # If no ticket types, create default allocation
                        default_ticket = event.ticket_types.first()
                        if default_ticket:
                            SectionTicketType.objects.create(
                                section=section,
                                ticket_type=default_ticket,
                                allocated_capacity=total_seats,
                                available_capacity=total_seats,
                                price_modifier=1.00
                            )
                
                # Update performance capacity
                performance.max_capacity = total_performance_capacity
                performance.current_capacity = 0
                performance.save()
                
                print(f"    ✅ Created {len(sections_data)} sections with {total_performance_capacity} total capacity")
        
        print("✅ Capacity migration completed!")
    
    @staticmethod
    def validate_migration():
        """
        Validate that migration was successful.
        """
        print("🔍 Validating migration...")
        
        issues = []
        
        for event in Event.objects.all():
            print(f"📅 Validating event: {event.title}")
            
            for performance in event.performances.all():
                # Check performance capacity
                total_section_capacity = sum(
                    s.total_capacity for s in performance.sections.all()
                )
                
                if total_section_capacity != performance.max_capacity:
                    issue = f"Performance {performance.date}: Capacity mismatch (Expected: {performance.max_capacity}, Actual: {total_section_capacity})"
                    issues.append(issue)
                    print(f"  ❌ {issue}")
                
                # Check section capacity
                for section in performance.sections.all():
                    total_ticket_capacity = sum(
                        stt.allocated_capacity for stt in section.ticket_types.all()
                    )
                    
                    if total_ticket_capacity != section.total_capacity:
                        issue = f"Section {section.name}: Capacity mismatch (Expected: {section.total_capacity}, Actual: {total_ticket_capacity})"
                        issues.append(issue)
                        print(f"  ❌ {issue}")
                    
                    # Check capacity components
                    total_components = (
                        section.available_capacity + 
                        section.reserved_capacity + 
                        section.sold_capacity
                    )
                    
                    if total_components != section.total_capacity:
                        issue = f"Section {section.name}: Component mismatch (Expected: {section.total_capacity}, Actual: {total_components})"
                        issues.append(issue)
                        print(f"  ❌ {issue}")
        
        if issues:
            print(f"\n❌ Found {len(issues)} issues")
            return False
        else:
            print("✅ Migration validation passed!")
            return True
    
    @staticmethod
    def create_sample_capacity_structure(event_id):
        """
        Create a sample capacity structure for testing.
        """
        try:
            event = Event.objects.get(id=event_id)
            performance = event.performances.first()
            
            if not performance:
                print("❌ No performance found for event")
                return False
            
            # Sample capacity configuration
            capacity_config = {
                'sections': [
                    {
                        'name': 'VIP',
                        'total_capacity': 200,
                        'base_price': 150.00,
                        'is_premium': True,
                        'ticket_types': [
                            {'ticket_type_id': event.ticket_types.first().id, 'allocated_capacity': 200, 'price_modifier': 1.5}
                        ]
                    },
                    {
                        'name': 'Normal',
                        'total_capacity': 300,
                        'base_price': 100.00,
                        'is_premium': False,
                        'ticket_types': [
                            {'ticket_type_id': event.ticket_types.first().id, 'allocated_capacity': 300, 'price_modifier': 1.0}
                        ]
                    },
                    {
                        'name': 'Economy',
                        'total_capacity': 500,
                        'base_price': 75.00,
                        'is_premium': False,
                        'ticket_types': [
                            {'ticket_type_id': event.ticket_types.first().id, 'allocated_capacity': 500, 'price_modifier': 0.8}
                        ]
                    }
                ]
            }
            
            CapacityManager.create_performance_capacity(performance, capacity_config)
            print(f"✅ Created sample capacity structure for {event.title}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample capacity: {e}")
            return False 