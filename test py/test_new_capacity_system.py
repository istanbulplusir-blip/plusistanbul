#!/usr/bin/env python
"""
Test script for the new Event Capacity Management System.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, EventSection, SectionTicketType, TicketType
from events.capacity_manager import CapacityManager


def test_capacity_structure():
    """Test the new capacity structure."""
    print("🧪 Testing New Capacity Structure")
    print("=" * 50)
    
    # Get first event
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    performance = event.performances.first()
    if not performance:
        print("❌ No performances found")
        return False
    
    print(f"📅 Testing Event: {event.title}")
    print(f"🎪 Testing Performance: {performance.date}")
    
    # Test 1: Check if sections exist
    sections = performance.sections.all()
    if not sections.exists():
        print("❌ No sections found")
        return False
    
    print(f"✅ Found {sections.count()} sections")
    
    # Test 2: Check capacity consistency
    total_section_capacity = sum(s.total_capacity for s in sections)
    if total_section_capacity != performance.max_capacity:
        print(f"❌ Capacity mismatch: Performance={performance.max_capacity}, Sections={total_section_capacity}")
        return False
    
    print(f"✅ Capacity consistency: {performance.max_capacity}")
    
    # Test 3: Check each section
    for section in sections:
        print(f"  📍 Section: {section.name}")
        print(f"    Total: {section.total_capacity}")
        print(f"    Available: {section.available_capacity}")
        print(f"    Reserved: {section.reserved_capacity}")
        print(f"    Sold: {section.sold_capacity}")
        print(f"    Occupancy: {section.occupancy_rate:.1f}%")
        
        # Check section capacity components
        total_components = (
            section.available_capacity + 
            section.reserved_capacity + 
            section.sold_capacity
        )
        
        if total_components != section.total_capacity:
            print(f"    ❌ Component mismatch: {total_components} != {section.total_capacity}")
            return False
        
        # Check ticket types
        ticket_types = section.ticket_types.all()
        if not ticket_types.exists():
            print(f"    ⚠️  No ticket types")
        else:
            print(f"    🎫 Ticket types: {ticket_types.count()}")
            
            total_ticket_capacity = sum(stt.allocated_capacity for stt in ticket_types)
            if total_ticket_capacity != section.total_capacity:
                print(f"    ❌ Ticket capacity mismatch: {total_ticket_capacity} != {section.total_capacity}")
                return False
            
            for stt in ticket_types:
                print(f"      - {stt.ticket_type.name}: {stt.allocated_capacity} seats (${stt.final_price})")
    
    return True


def test_capacity_manager():
    """Test CapacityManager functionality."""
    print("\n🔧 Testing CapacityManager")
    print("=" * 50)
    
    # Get first event
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    performance = event.performances.first()
    if not performance:
        print("❌ No performances found")
        return False
    
    print(f"📅 Testing with Event: {event.title}")
    print(f"🎪 Testing with Performance: {performance.date}")
    
    # Test 1: Get capacity summary
    try:
        summary = CapacityManager.get_capacity_summary(performance)
        print("✅ Capacity summary generated")
        print(f"  Performance capacity: {summary['performance']['max_capacity']}")
        print(f"  Sections: {len(summary['sections'])}")
        
        for section in summary['sections']:
            print(f"    {section['name']}: {section['available_capacity']}/{section['total_capacity']} available")
    
    except Exception as e:
        print(f"❌ Error getting capacity summary: {e}")
        return False
    
    # Test 2: Get available seats
    try:
        available_seats = CapacityManager.get_available_seats(performance)
        print(f"✅ Available seats query: {available_seats.count()} results")
    
    except Exception as e:
        print(f"❌ Error getting available seats: {e}")
        return False
    
    # Test 3: Test seat reservation (if seats available)
    if available_seats.exists():
        first_seat = available_seats.first()
        print(f"🎫 Testing reservation for {first_seat.ticket_type.name} in {first_seat.section.name}")
        
        try:
            success, result = CapacityManager.reserve_seats(
                performance,
                first_seat.ticket_type.id,
                first_seat.section.name,
                1
            )
            
            if success:
                print("✅ Seat reservation successful")
                
                # Release the reservation
                first_seat.release_capacity(1)
                print("✅ Seat reservation released")
            else:
                print(f"❌ Seat reservation failed: {result}")
                return False
        
        except Exception as e:
            print(f"❌ Error during seat reservation: {e}")
            return False
    
    return True


def test_api_endpoints():
    """Test API endpoints for capacity management."""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    # This would require a running server and HTTP requests
    # For now, just test the serializers
    from events.serializers import EventSectionSerializer, SectionTicketTypeSerializer
    
    # Get first section
    section = EventSection.objects.first()
    if not section:
        print("❌ No sections found")
        return False
    
    # Test section serializer
    try:
        section_data = EventSectionSerializer(section).data
        print("✅ Section serializer working")
        print(f"  Section: {section_data['name']}")
        print(f"  Capacity: {section_data['total_capacity']}")
        print(f"  Available: {section_data['available_capacity']}")
    
    except Exception as e:
        print(f"❌ Section serializer error: {e}")
        return False
    
    # Test ticket type serializer
    ticket_type = section.ticket_types.first()
    if ticket_type:
        try:
            ticket_data = SectionTicketTypeSerializer(ticket_type).data
            print("✅ Ticket type serializer working")
            print(f"  Ticket: {ticket_data['ticket_type_name']}")
            print(f"  Price: ${ticket_data['final_price']}")
        
        except Exception as e:
            print(f"❌ Ticket type serializer error: {e}")
            return False
    
    return True


def create_sample_capacity():
    """Create a sample capacity structure for demonstration."""
    print("\n🎯 Creating Sample Capacity Structure")
    print("=" * 50)
    
    # Get first event
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    performance = event.performances.first()
    if not performance:
        print("❌ No performances found")
        return False
    
    # Clear existing sections
    performance.sections.all().delete()
    
    # Get ticket types
    ticket_types = event.ticket_types.all()
    if not ticket_types.exists():
        print("❌ No ticket types found")
        return False
    
    vip_ticket = ticket_types.first()
    normal_ticket = ticket_types.first()  # Use same for demo
    
    # Create sample capacity configuration
    capacity_config = {
        'sections': [
            {
                'name': 'VIP',
                'total_capacity': 200,
                'base_price': 150.00,
                'is_premium': True,
                'ticket_types': [
                    {'ticket_type_id': vip_ticket.id, 'allocated_capacity': 200, 'price_modifier': 1.5}
                ]
            },
            {
                'name': 'Normal',
                'total_capacity': 300,
                'base_price': 100.00,
                'is_premium': False,
                'ticket_types': [
                    {'ticket_type_id': normal_ticket.id, 'allocated_capacity': 300, 'price_modifier': 1.0}
                ]
            },
            {
                'name': 'Economy',
                'total_capacity': 500,
                'base_price': 75.00,
                'is_premium': False,
                'ticket_types': [
                    {'ticket_type_id': normal_ticket.id, 'allocated_capacity': 500, 'price_modifier': 0.8}
                ]
            }
        ]
    }
    
    try:
        CapacityManager.create_performance_capacity(performance, capacity_config)
        print("✅ Sample capacity structure created")
        print(f"  Total capacity: {performance.max_capacity}")
        print(f"  Sections: {performance.sections.count()}")
        
        for section in performance.sections.all():
            print(f"    {section.name}: {section.total_capacity} seats (${section.base_price})")
        
        return True
    
    except Exception as e:
        print(f"❌ Error creating sample capacity: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Event Capacity System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Capacity Structure", test_capacity_structure),
        ("Capacity Manager", test_capacity_manager),
        ("API Endpoints", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        
        # Create sample capacity for demonstration
        print("\n🎯 Creating sample capacity structure...")
        create_sample_capacity()
        
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 