#!/usr/bin/env python
"""
Analyze the current capacity structure in the Event system.
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, TicketType, Seat, Venue

def analyze_capacity_structure():
    """Analyze the current capacity structure."""
    
    print("🔍 ANALYZING EVENT CAPACITY STRUCTURE")
    print("=" * 60)
    
    # Get test event
    try:
        event = Event.objects.get(id="e535c9e4-a079-4e6f-bbd4-10ab31d2fbb7")
        print(f"📅 Event: {event.title}")
        print(f"🏟️  Venue: {event.venue.name} (Capacity: {event.venue.total_capacity})")
        print()
    except Event.DoesNotExist:
        print("❌ Test event not found")
        return
    
    # Analyze TicketTypes
    print("🎫 TICKET TYPES ANALYSIS")
    print("-" * 30)
    ticket_types = event.ticket_types.all()
    
    for tt in ticket_types:
        print(f"  • {tt.name} ({tt.ticket_type})")
        print(f"    - Capacity: {tt.capacity}")
        print(f"    - Price Modifier: {tt.price_modifier}")
        print(f"    - Active: {tt.is_active}")
        print()
    
    # Analyze Performances
    print("🎭 PERFORMANCES ANALYSIS")
    print("-" * 30)
    performances = event.performances.all()
    
    for perf in performances:
        print(f"  📅 Performance: {perf.date}")
        print(f"    - Available: {perf.is_available}")
        print(f"    - Max Capacity: {perf.max_capacity}")
        print(f"    - Current Capacity: {perf.current_capacity}")
        print(f"    - Available Capacity: {perf.available_capacity}")
        print(f"    - Ticket Capacities: {perf.ticket_capacities}")
        print()
        
        # Analyze Seats for this performance
        seats = perf.seats.all()
        print(f"    🪑 SEATS ANALYSIS ({seats.count()} total)")
        
        # Group by ticket type
        seats_by_ticket_type = {}
        for seat in seats:
            ticket_type_name = seat.ticket_type.name if seat.ticket_type else "No Ticket Type"
            if ticket_type_name not in seats_by_ticket_type:
                seats_by_ticket_type[ticket_type_name] = []
            seats_by_ticket_type[ticket_type_name].append(seat)
        
        for ticket_type_name, ticket_seats in seats_by_ticket_type.items():
            print(f"      • {ticket_type_name}: {len(ticket_seats)} seats")
            
            # Count by status
            status_counts = {}
            for seat in ticket_seats:
                status = seat.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"        - {status}: {count}")
        
        print()
    
    # Analyze Capacity Consistency
    print("🔍 CAPACITY CONSISTENCY ANALYSIS")
    print("-" * 40)
    
    for perf in performances:
        print(f"  📅 Performance: {perf.date}")
        
        # Check venue capacity vs performance capacity
        venue_capacity = event.venue.total_capacity
        perf_max_capacity = perf.max_capacity
        
        print(f"    - Venue Capacity: {venue_capacity}")
        print(f"    - Performance Max Capacity: {perf_max_capacity}")
        
        if perf_max_capacity > venue_capacity:
            print(f"    ⚠️  WARNING: Performance capacity exceeds venue capacity!")
        elif perf_max_capacity < venue_capacity:
            print(f"    ℹ️  Performance capacity is less than venue capacity")
        else:
            print(f"    ✅ Performance capacity matches venue capacity")
        
        # Check ticket type capacities sum
        total_ticket_capacity = sum(tt.capacity for tt in ticket_types if tt.is_active)
        print(f"    - Total Ticket Type Capacity: {total_ticket_capacity}")
        
        if total_ticket_capacity > perf_max_capacity:
            print(f"    ⚠️  WARNING: Total ticket capacity exceeds performance capacity!")
        elif total_ticket_capacity < perf_max_capacity:
            print(f"    ℹ️  Total ticket capacity is less than performance capacity")
        else:
            print(f"    ✅ Total ticket capacity matches performance capacity")
        
        # Check actual seats vs ticket capacities
        for tt in ticket_types:
            if not tt.is_active:
                continue
                
            tt_seats = perf.seats.filter(ticket_type=tt)
            actual_seats = tt_seats.count()
            expected_seats = tt.capacity
            
            print(f"    - {tt.name}: Expected {expected_seats}, Actual {actual_seats}")
            
            if actual_seats != expected_seats:
                print(f"      ⚠️  MISMATCH: Expected vs Actual seats!")
        
        print()
    
    # Analyze Section Structure
    print("🏗️  SECTION STRUCTURE ANALYSIS")
    print("-" * 35)
    
    for perf in performances:
        print(f"  📅 Performance: {perf.date}")
        
        # Get unique sections
        sections = perf.seats.values_list('section', flat=True).distinct()
        print(f"    - Sections: {list(sections)}")
        
        for section in sections:
            section_seats = perf.seats.filter(section=section)
            print(f"    - Section '{section}': {section_seats.count()} seats")
            
            # Group by ticket type within section
            section_by_ticket = {}
            for seat in section_seats:
                ticket_name = seat.ticket_type.name if seat.ticket_type else "No Ticket Type"
                if ticket_name not in section_by_ticket:
                    section_by_ticket[ticket_name] = []
                section_by_ticket[ticket_name].append(seat)
            
            for ticket_name, seats in section_by_ticket.items():
                print(f"      • {ticket_name}: {len(seats)} seats")
        
        print()
    
    # Summary and Issues
    print("📋 SUMMARY AND ISSUES")
    print("-" * 25)
    
    issues = []
    
    # Check for missing ticket types in seats
    for perf in performances:
        seats_without_ticket_type = perf.seats.filter(ticket_type__isnull=True)
        if seats_without_ticket_type.exists():
            issues.append(f"Performance {perf.date}: {seats_without_ticket_type.count()} seats without ticket type")
    
    # Check for capacity mismatches
    for perf in performances:
        for tt in ticket_types:
            if not tt.is_active:
                continue
            tt_seats = perf.seats.filter(ticket_type=tt)
            if tt_seats.count() != tt.capacity:
                issues.append(f"Performance {perf.date}, {tt.name}: Capacity mismatch ({tt.capacity} vs {tt_seats.count()} seats)")
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ No major issues found")
    
    print()
    print("🎯 RECOMMENDATIONS")
    print("-" * 20)
    print("1. Ensure all seats have proper ticket type assignment")
    print("2. Validate that ticket type capacities match actual seat counts")
    print("3. Implement capacity validation at the model level")
    print("4. Add database constraints for capacity consistency")
    print("5. Create a unified capacity management service")

if __name__ == "__main__":
    analyze_capacity_structure() 