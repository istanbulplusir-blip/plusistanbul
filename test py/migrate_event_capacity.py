#!/usr/bin/env python
"""
Migration script to convert existing event capacity data to new structure.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, EventSection, SectionTicketType, TicketType, Seat
from events.capacity_manager import CapacityManager


def migrate_existing_data():
    """Migrate existing capacity data to new structure."""
    print("🔄 Starting Event Capacity Migration...")
    print("=" * 50)
    
    # Get all events
    events = Event.objects.all()
    print(f"📅 Found {events.count()} events to migrate")
    
    for event in events:
        print(f"\n🎭 Processing Event: {event.title}")
        print("-" * 30)
        
        performances = event.performances.all()
        print(f"  📅 Found {performances.count()} performances")
        
        for performance in performances:
            print(f"    🎪 Performance: {performance.date}")
            
            # Check if already migrated
            if performance.sections.exists():
                print(f"      ⚠️  Already has sections, skipping...")
                continue
            
            # Get all seats for this performance
            seats = performance.seats.all()
            print(f"      💺 Found {seats.count()} seats")
            
            if not seats.exists():
                print(f"      ⚠️  No seats found, skipping...")
                continue
            
            # Group seats by section
            sections_data = {}
            for seat in seats:
                section_name = seat.section or 'General'
                if section_name not in sections_data:
                    sections_data[section_name] = {
                        'seats': [],
                        'ticket_types': set(),
                        'total_seats': 0
                    }
                sections_data[section_name]['seats'].append(seat)
                sections_data[section_name]['total_seats'] += 1
                if seat.ticket_type:
                    sections_data[section_name]['ticket_types'].add(seat.ticket_type)
            
            print(f"      📍 Found {len(sections_data)} sections")
            
            # Create EventSection for each section
            total_performance_capacity = 0
            for section_name, data in sections_data.items():
                print(f"        📍 Creating section: {section_name}")
                
                # Calculate base price from existing seats
                base_price = Decimal('100.00')  # Default
                if data['seats']:
                    prices = [seat.price for seat in data['seats'] if seat.price]
                    if prices:
                        base_price = min(prices)
                
                # Create section
                section = EventSection.objects.create(
                    performance=performance,
                    name=section_name,
                    total_capacity=data['total_seats'],
                    available_capacity=data['total_seats'],
                    base_price=base_price,
                    description=f"Section {section_name} for {event.title}"
                )
                
                print(f"          ✅ Created section with {data['total_seats']} capacity")
                
                # Create SectionTicketType allocations
                if data['ticket_types']:
                    print(f"          🎫 Creating {len(data['ticket_types'])} ticket type allocations")
                    
                    # Distribute capacity among ticket types
                    capacity_per_ticket = data['total_seats'] // len(data['ticket_types'])
                    remaining_capacity = data['total_seats'] % len(data['ticket_types'])
                    
                    for i, ticket_type in enumerate(data['ticket_types']):
                        allocated_capacity = capacity_per_ticket
                        if i < remaining_capacity:
                            allocated_capacity += 1
                        
                        # Calculate price modifier
                        price_modifier = Decimal('1.00')
                        if ticket_type.price_modifier:
                            price_modifier = ticket_type.price_modifier
                        
                        SectionTicketType.objects.create(
                            section=section,
                            ticket_type=ticket_type,
                            allocated_capacity=allocated_capacity,
                            available_capacity=allocated_capacity,
                            price_modifier=price_modifier
                        )
                        
                        print(f"            ✅ {ticket_type.name}: {allocated_capacity} seats")
                else:
                    # If no ticket types, create default allocation
                    default_ticket = event.ticket_types.first()
                    if default_ticket:
                        SectionTicketType.objects.create(
                            section=section,
                            ticket_type=default_ticket,
                            allocated_capacity=data['total_seats'],
                            available_capacity=data['total_seats'],
                            price_modifier=Decimal('1.00')
                        )
                        print(f"          ✅ Default ticket type: {data['total_seats']} seats")
                    else:
                        print(f"          ⚠️  No ticket types available")
                
                total_performance_capacity += data['total_seats']
            
            # Update performance capacity
            performance.max_capacity = total_performance_capacity
            performance.current_capacity = 0
            performance.save()
            
            print(f"      ✅ Updated performance capacity: {total_performance_capacity}")
    
    print("\n" + "=" * 50)
    print("✅ Migration completed!")
    print("=" * 50)


def validate_migration():
    """Validate the migration results."""
    print("\n🔍 Validating Migration Results...")
    print("=" * 50)
    
    issues = []
    total_events = 0
    total_performances = 0
    total_sections = 0
    
    for event in Event.objects.all():
        total_events += 1
        print(f"📅 Validating Event: {event.title}")
        
        for performance in event.performances.all():
            total_performances += 1
            
            # Check if performance has sections
            if not performance.sections.exists():
                issue = f"Performance {performance.date}: No sections created"
                issues.append(issue)
                print(f"  ❌ {issue}")
                continue
            
            # Check performance capacity
            total_section_capacity = sum(
                s.total_capacity for s in performance.sections.all()
            )
            
            if total_section_capacity != performance.max_capacity:
                issue = f"Performance {performance.date}: Capacity mismatch (Expected: {performance.max_capacity}, Actual: {total_section_capacity})"
                issues.append(issue)
                print(f"  ❌ {issue}")
            else:
                print(f"  ✅ Performance capacity: {performance.max_capacity}")
            
            # Check sections
            for section in performance.sections.all():
                total_sections += 1
                
                # Check section capacity
                total_ticket_capacity = sum(
                    stt.allocated_capacity for stt in section.ticket_types.all()
                )
                
                if total_ticket_capacity != section.total_capacity:
                    issue = f"Section {section.name}: Capacity mismatch (Expected: {section.total_capacity}, Actual: {total_ticket_capacity})"
                    issues.append(issue)
                    print(f"    ❌ {issue}")
                else:
                    print(f"    ✅ Section {section.name}: {section.total_capacity} capacity")
                
                # Check capacity components
                total_components = (
                    section.available_capacity + 
                    section.reserved_capacity + 
                    section.sold_capacity
                )
                
                if total_components != section.total_capacity:
                    issue = f"Section {section.name}: Component mismatch (Expected: {section.total_capacity}, Actual: {total_components})"
                    issues.append(issue)
                    print(f"    ❌ {issue}")
    
    print(f"\n📊 Migration Summary:")
    print(f"  Events processed: {total_events}")
    print(f"  Performances processed: {total_performances}")
    print(f"  Sections created: {total_sections}")
    
    if issues:
        print(f"\n❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"\n✅ Migration validation passed!")
        return True


def create_sample_structure():
    """Create a sample capacity structure for testing."""
    print("\n🎯 Creating Sample Capacity Structure...")
    
    # Get first event
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    performance = event.performances.first()
    if not performance:
        print("❌ No performances found")
        return False
    
    # Clear existing sections if any
    performance.sections.all().delete()
    
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
    
    try:
        CapacityManager.create_performance_capacity(performance, capacity_config)
        print(f"✅ Created sample capacity structure for {event.title}")
        return True
    except Exception as e:
        print(f"❌ Error creating sample capacity: {e}")
        return False


if __name__ == '__main__':
    print("🚀 Event Capacity Migration Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'migrate':
            migrate_existing_data()
        elif command == 'validate':
            validate_migration()
        elif command == 'sample':
            create_sample_structure()
        else:
            print("❌ Unknown command. Use: migrate, validate, or sample")
    else:
        # Run full migration
        migrate_existing_data()
        validate_migration() 