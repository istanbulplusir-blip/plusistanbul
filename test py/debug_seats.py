#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, Seat
from django.db import connection

def debug_seats():
    print("=== بررسی دقیق صندلی‌ها ===\n")
    
    # Find the specific event and performance
    event = Event.objects.filter(slug__icontains="ebi").first()
    performance = EventPerformance.objects.filter(
        event=event,
        date__year=2025,
        date__month=5,
        date__day=13
    ).first()
    
    print(f"Event: {event.translations.first().title if event.translations.exists() else 'No title'}")
    print(f"Performance: {performance.date} at {performance.start_time}")
    print(f"Performance ID: {performance.id}")
    
    # Get all seats for this performance
    seats = Seat.objects.filter(performance=performance)
    print(f"\nTotal seats: {seats.count()}")
    
    # Group seats by section and status
    sections = {}
    for seat in seats:
        section = seat.section
        if section not in sections:
            sections[section] = {'total': 0, 'available': 0, 'reserved': 0, 'sold': 0, 'blocked': 0}
        
        sections[section]['total'] += 1
        sections[section][seat.status] += 1
    
    print("\n=== Seat Status by Section ===")
    for section_name, counts in sections.items():
        print(f"\n📍 {section_name}:")
        print(f"  Total: {counts['total']}")
        print(f"  Available: {counts['available']}")
        print(f"  Reserved: {counts['reserved']}")
        print(f"  Sold: {counts['sold']}")
        print(f"  Blocked: {counts['blocked']}")
    
    # Check specific seats
    print("\n=== Sample Seats ===")
    for seat in seats[:10]:
        print(f"  {seat.section} - Row {seat.row_number}, Seat {seat.seat_number} - Status: {seat.status} - Price: {seat.price}")
    
    # Check if seats are being filtered by status
    print("\n=== Available Seats Only ===")
    available_seats = seats.filter(status='available')
    print(f"Available seats: {available_seats.count()}")
    
    for seat in available_seats[:5]:
        print(f"  {seat.section} - Row {seat.row_number}, Seat {seat.seat_number} - Price: {seat.price}")
    
    # Check reservation status
    print("\n=== Reserved Seats ===")
    reserved_seats = seats.filter(status='reserved')
    print(f"Reserved seats: {reserved_seats.count()}")
    
    for seat in reserved_seats[:5]:
        print(f"  {seat.section} - Row {seat.row_number}, Seat {seat.seat_number} - Reservation ID: {seat.reservation_id}")

if __name__ == "__main__":
    debug_seats()
