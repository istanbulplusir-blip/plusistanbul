#!/usr/bin/env python
"""
Clean up expired reservations and fix capacity inconsistencies.
Run with: python cleanup_expired_reservations.py
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
from events.models import Event, EventPerformance, EventSection, SectionTicketType, Seat, TicketType, EventCategory, Venue

def cleanup_expired_reservations():
    """Clean up expired reservations and fix capacity."""
    print("=== CLEANING UP EXPIRED RESERVATIONS ===\n")
    
    now = timezone.now()
    
    # Find expired reserved seats
    expired_seats = Seat.objects.filter(
        status='reserved',
        reservation_expires_at__lt=now
    )
    
    print(f"Found {expired_seats.count()} expired reserved seats")
    
    if expired_seats.exists():
        # Group by performance for batch processing
        performance_ids = expired_seats.values_list('performance_id', flat=True).distinct()
        
        for perf_id in performance_ids:
            print(f"\nProcessing performance {perf_id}")
            
            with transaction.atomic():
                # Get expired seats for this performance
                perf_expired_seats = expired_seats.filter(performance_id=perf_id)
                
                # Update seats back to available
                updated_count = perf_expired_seats.update(
                    status='available',
                    reservation_id=None,
                    reservation_expires_at=None
                )
                
                print(f"  Released {updated_count} seats back to available")
                
                # Update capacity counts for affected sections
                for section in EventSection.objects.filter(performance_id=perf_id):
                    section.clear_capacity_cache()
                    print(f"  Cleared cache for section {section.name}")
        
        print(f"\nTotal seats released: {expired_seats.count()}")
    
    # Check for capacity inconsistencies
    print("\n=== CHECKING CAPACITY CONSISTENCIES ===")
    
    inconsistencies = []
    for stt in SectionTicketType.objects.all():
        total = stt.allocated_capacity
        available = stt.available_capacity
        reserved = stt.reserved_capacity
        sold = stt.sold_capacity
        calculated_total = available + reserved + sold
        
        if total != calculated_total:
            inconsistencies.append({
                'stt': stt,
                'total': total,
                'calculated': calculated_total,
                'available': available,
                'reserved': reserved,
                'sold': sold
            })
    
    if inconsistencies:
        print(f"Found {len(inconsistencies)} capacity inconsistencies:")
        for inc in inconsistencies:
            stt = inc['stt']
            print(f"  {stt.section.name} - {stt.ticket_type.name}:")
            print(f"    Allocated: {inc['total']}, Calculated: {inc['calculated']}")
            print(f"    Available: {inc['available']}, Reserved: {inc['reserved']}, Sold: {inc['sold']}")
        
        # Fix inconsistencies by recalculating from actual seat counts
        print("\nFixing capacity inconsistencies...")
        
        for inc in inconsistencies:
            stt = inc['stt']
            section = stt.section
            ticket_type = stt.ticket_type
            
            # Count actual seats by status
            actual_available = Seat.objects.filter(
                performance=section.performance,
                section=section.name,
                status='available'
            ).count()
            
            actual_reserved = Seat.objects.filter(
                performance=section.performance,
                section=section.name,
                status='reserved'
            ).count()
            
            actual_sold = Seat.objects.filter(
                performance=section.performance,
                section=section.name,
                status='sold'
            ).count()
            
            # Update SectionTicketType with correct counts
            stt.available_capacity = actual_available
            stt.reserved_capacity = actual_reserved
            stt.sold_capacity = actual_sold
            stt.allocated_capacity = actual_available + actual_reserved + actual_sold
            stt.save()
            
            print(f"  Fixed {section.name} - {ticket_type.name}:")
            print(f"    Available: {actual_available}, Reserved: {actual_reserved}, Sold: {actual_sold}")
    else:
        print("No capacity inconsistencies found.")

def create_test_event():
    """Create a test event with proper structure for testing."""
    print("\n=== CREATING TEST EVENT ===\n")
    
    try:
        with transaction.atomic():
            # Get or create event category
            category, _ = EventCategory.objects.get_or_create(
                slug='test-category-debug',
                defaults={}
            )
            
            # Get or create venue
            venue, _ = Venue.objects.get_or_create(
                slug='test-venue-debug',
                defaults={
                    'total_capacity': 30
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
            performance_date = timezone.now().date() + timedelta(days=7)
            performance, created = EventPerformance.objects.get_or_create(
                event=event,
                date=performance_date,
                defaults={
                    'start_date': performance_date,
                    'end_date': performance_date,
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
    print("Starting cleanup and test event creation...\n")
    
    # Clean up expired reservations
    cleanup_expired_reservations()
    
    # Create test event
    print("\n" + "="*50)
    create_test_event()
    
    print("\n" + "="*50)
    print("Cleanup and test event creation complete!")
