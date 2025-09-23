#!/usr/bin/env python
"""
Debug script to analyze Event reservation system issues.
Run with: python debug_event_system.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from events.models import Event, EventPerformance, EventSection, SectionTicketType, Seat, TicketType
from cart.models import Cart, CartItem
from users.models import User

def analyze_event_system():
    """Analyze the current state of the Event reservation system."""
    print("=== EVENT RESERVATION SYSTEM ANALYSIS ===\n")
    
    # 1. Check Event products
    print("1. EVENT PRODUCTS:")
    events = Event.objects.all()
    print(f"   Total events: {events.count()}")
    
    for event in events[:3]:  # Show first 3 events
        print(f"   - {event.id}: {event.translations.first().title if event.translations.exists() else 'No title'}")
        print(f"     Performances: {event.performances.count()}")
        print(f"     Ticket types: {event.ticket_types.count()}")
        print(f"     Sections: {event.performances.first().sections.count() if event.performances.exists() else 0}")
    
    # 2. Check EventPerformances
    print("\n2. EVENT PERFORMANCES:")
    performances = EventPerformance.objects.all()
    print(f"   Total performances: {performances.count()}")
    
    for perf in performances[:3]:  # Show first 3 performances
        print(f"   - {perf.id}: {perf.event.translations.first().title if perf.event.translations.exists() else 'No title'} - {perf.date}")
        print(f"     Max capacity: {perf.max_capacity}")
        print(f"     Current capacity: {perf.current_capacity}")
        print(f"     Available capacity: {perf.available_capacity}")
        print(f"     Seats: {perf.seats.count()}")
    
    # 3. Check EventSections
    print("\n3. EVENT SECTIONS:")
    sections = EventSection.objects.all()
    print(f"   Total sections: {sections.count()}")
    
    for section in sections[:5]:  # Show first 5 sections
        print(f"   - {section.id}: {section.name}")
        print(f"     Total capacity: {section.total_capacity}")
        print(f"     Available capacity: {section.available_capacity}")
        print(f"     Reserved capacity: {section.reserved_capacity}")
        print(f"     Sold capacity: {section.sold_capacity}")
        print(f"     SectionTicketTypes: {section.ticket_types.count()}")
    
    # 4. Check SectionTicketTypes
    print("\n4. SECTION TICKET TYPES:")
    stts = SectionTicketType.objects.all()
    print(f"   Total SectionTicketTypes: {stts.count()}")
    
    for stt in stts[:5]:  # Show first 5
        print(f"   - {stt.id}: {stt.section.name} - {stt.ticket_type.name}")
        print(f"     Allocated capacity: {stt.allocated_capacity}")
        print(f"     Available capacity: {stt.available_capacity}")
        print(f"     Reserved capacity: {stt.reserved_capacity}")
        print(f"     Sold capacity: {stt.sold_capacity}")
        print(f"     Price modifier: {stt.price_modifier}")
    
    # 5. Check Seats
    print("\n5. INDIVIDUAL SEATS:")
    seats = Seat.objects.all()
    print(f"   Total seats: {seats.count()}")
    
    # Group by status
    status_counts = {}
    for seat in seats:
        status = seat.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   - {status}: {count}")
    
    # Show some sample seats
    print("\n   Sample seats:")
    for seat in seats[:5]:
        print(f"     - {seat.id}: {seat.section} Row {seat.row_number} Seat {seat.seat_number}")
        print(f"       Status: {seat.status}")
        print(f"       Performance: {seat.performance.id}")
        print(f"       Reservation ID: {seat.reservation_id}")
        print(f"       Expires at: {seat.reservation_expires_at}")
    
    # 6. Check Cart items
    print("\n6. CART ITEMS:")
    cart_items = CartItem.objects.filter(product_type='event')
    print(f"   Total event cart items: {cart_items.count()}")
    
    for item in cart_items[:3]:
        print(f"   - {item.id}: {item.product_type} - {item.product_id}")
        print(f"     Quantity: {item.quantity}")
        print(f"     Total price: {item.total_price}")
        print(f"     Booking data: {item.booking_data}")
    
    # 7. Check for capacity inconsistencies
    print("\n7. CAPACITY CONSISTENCY CHECK:")
    for stt in SectionTicketType.objects.all():
        total = stt.allocated_capacity
        available = stt.available_capacity
        reserved = stt.reserved_capacity
        sold = stt.sold_capacity
        calculated_total = available + reserved + sold
        
        if total != calculated_total:
            print(f"   INCONSISTENCY in {stt.section.name} - {stt.ticket_type.name}:")
            print(f"     Allocated: {total}, Calculated: {calculated_total}")
            print(f"     Available: {available}, Reserved: {reserved}, Sold: {sold}")
    
    # 8. Check for expired reservations
    print("\n8. EXPIRED RESERVATIONS:")
    now = timezone.now()
    expired_seats = Seat.objects.filter(
        status='reserved',
        reservation_expires_at__lt=now
    )
    print(f"   Expired reserved seats: {expired_seats.count()}")
    
    if expired_seats.exists():
        print("   Sample expired seats:")
        for seat in expired_seats[:3]:
            print(f"     - {seat.id}: {seat.section} Row {seat.row_number} Seat {seat.seat_number}")
            print(f"       Expired at: {seat.reservation_expires_at}")
            print(f"       Reservation ID: {seat.reservation_id}")

def test_seat_holding():
    """Test the seat holding functionality."""
    print("\n=== TESTING SEAT HOLDING ===\n")
    
    # Find a performance with available seats
    performance = EventPerformance.objects.filter(
        seats__status='available'
    ).first()
    
    if not performance:
        print("No performance with available seats found.")
        return
    
    print(f"Testing with performance: {performance.id}")
    print(f"Event: {performance.event.translations.first().title if performance.event.translations.exists() else 'No title'}")
    
    # Get available seats
    available_seats = performance.seats.filter(status='available')[:3]
    if not available_seats:
        print("No available seats found.")
        return
    
    seat_ids = [str(seat.id) for seat in available_seats]
    print(f"Available seats: {seat_ids}")
    
    # Test holding seats
    try:
        from events.views import EventViewSet
        from rest_framework.test import APIRequestFactory
        from django.contrib.auth.models import AnonymousUser
        
        factory = APIRequestFactory()
        request = factory.post('/test/', {
            'seat_ids': seat_ids,
            'ttl_seconds': 300
        })
        request.user = AnonymousUser()
        
        # This would require more setup to test properly
        print("Seat holding test requires proper API setup.")
        
    except Exception as e:
        print(f"Error testing seat holding: {e}")

def create_test_event():
    """Create a test event with proper structure for testing."""
    print("\n=== CREATING TEST EVENT ===\n")
    
    try:
        with transaction.atomic():
            # Get or create event category
            from events.models import EventCategory
            category, _ = EventCategory.objects.get_or_create(
                name='Test Category',
                defaults={'description': 'Test category for debugging'}
            )
            
            # Get or create venue
            from events.models import Venue
            venue, _ = Venue.objects.get_or_create(
                name='Test Venue',
                defaults={
                    'address': 'Test Address',
                    'city': 'Test City',
                    'country': 'Test Country',
                    'capacity': 30
                }
            )
            
            # Create test event
            event, created = Event.objects.get_or_create(
                slug='test-event-debug',
                defaults={
                    'price': 25.00,
                    'currency': 'USD',
                    'city': 'Test City',
                    'country': 'Test Country',
                    'style': 'music',
                    'door_open_time': '19:00',
                    'start_time': '20:00',
                    'end_time': '22:00',
                    'category': category,
                    'venue': venue
                }
            )
            
            if created:
                print(f"Created test event: {event.id}")
            else:
                print(f"Using existing test event: {event.id}")
            
            # Create ticket types
            ticket_types_data = [
                {'name': 'Normal', 'price_modifier': 1.0, 'capacity': 10},
                {'name': 'VIP', 'price_modifier': 2.0, 'capacity': 10},
                {'name': 'Student', 'price_modifier': 0.7, 'capacity': 10}
            ]
            
            for tt_data in ticket_types_data:
                tt, created = TicketType.objects.get_or_create(
                    event=event,
                    name=tt_data['name'],
                    defaults={
                        'description': f'{tt_data["name"]} ticket',
                        'ticket_type': tt_data['name'].lower(),
                        'capacity': tt_data['capacity'],
                        'price_modifier': tt_data['price_modifier'],
                        'benefits': [f'{tt_data["name"]} benefits'],
                        'is_active': True
                    }
                )
                if created:
                    print(f"Created ticket type: {tt.name}")
            
            # Create performance
            performance, created = EventPerformance.objects.get_or_create(
                event=event,
                date=timezone.now().date() + timedelta(days=7),
                defaults={
                    'start_time': '20:00',
                    'end_time': '22:00',
                    'max_capacity': 30,
                    'current_capacity': 0,
                    'is_special': False,
                    'is_available': True
                }
            )
            
            if created:
                print(f"Created performance: {performance.id}")
            
            # Create sections
            sections_data = [
                {'name': 'Eco', 'base_price': 10.00, 'capacity': 10},
                {'name': 'Normal', 'base_price': 15.00, 'capacity': 10},
                {'name': 'VIP', 'base_price': 25.00, 'capacity': 10}
            ]
            
            for sec_data in sections_data:
                section, created = EventSection.objects.get_or_create(
                    performance=performance,
                    name=sec_data['name'],
                    defaults={
                        'description': f'{sec_data["name"]} section',
                        'total_capacity': sec_data['capacity'],
                        'available_capacity': sec_data['capacity'],
                        'base_price': sec_data['base_price'],
                        'is_premium': sec_data['name'] == 'VIP',
                        'is_wheelchair_accessible': False
                    }
                )
                
                if created:
                    print(f"Created section: {section.name}")
                
                # Create SectionTicketTypes
                for tt in event.ticket_types.all():
                    stt, created = SectionTicketType.objects.get_or_create(
                        section=section,
                        ticket_type=tt,
                        defaults={
                            'allocated_capacity': sec_data['capacity'],
                            'available_capacity': sec_data['capacity'],
                            'price_modifier': tt.price_modifier
                        }
                    )
                    
                    if created:
                        print(f"Created SectionTicketType: {section.name} - {tt.name}")
            
            # Create individual seats
            seat_count = 0
            for section in performance.sections.all():
                for row_num in range(1, 6):  # 5 rows
                    for seat_num in range(1, 3):  # 2 seats per row
                        seat, created = Seat.objects.get_or_create(
                            performance=performance,
                            section=section.name,
                            row_number=str(row_num),
                            seat_number=str(seat_num),
                            defaults={
                                'status': 'available',
                                'price': section.base_price,
                                'is_wheelchair_accessible': False,
                                'is_premium': section.is_premium
                            }
                        )
                        
                        if created:
                            seat_count += 1
            
            print(f"Created {seat_count} individual seats")
            
            # Set some seats as sold/reserved for testing
            test_seats = performance.seats.all()[:5]
            for i, seat in enumerate(test_seats):
                if i < 2:
                    seat.status = 'sold'
                    seat.save()
                    print(f"Set seat {seat.id} as sold")
                elif i < 4:
                    seat.status = 'reserved'
                    seat.reservation_id = f'test_reservation_{i}'
                    seat.reservation_expires_at = timezone.now() + timedelta(minutes=30)
                    seat.save()
                    print(f"Set seat {seat.id} as reserved")
            
            print(f"\nTest event created successfully!")
            print(f"Event ID: {event.id}")
            print(f"Performance ID: {performance.id}")
            print(f"Total seats: {performance.seats.count()}")
            print(f"Available: {performance.seats.filter(status='available').count()}")
            print(f"Reserved: {performance.seats.filter(status='reserved').count()}")
            print(f"Sold: {performance.seats.filter(status='sold').count()}")
            
    except Exception as e:
        print(f"Error creating test event: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Starting Event reservation system analysis...\n")
    
    # Analyze current system
    analyze_event_system()
    
    # Create test event if needed
    print("\n" + "="*50)
    create_test_event()
    
    print("\n" + "="*50)
    print("Analysis complete!")
