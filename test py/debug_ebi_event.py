#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, EventSection, SectionTicketType, Seat
from cart.models import Cart, CartItem
from django.utils import timezone

def debug_ebi_event():
    print("=== بررسی مشکل ظرفیت Event Ebi ===\n")
    
    # Find the Ebi event
    try:
        event = Event.objects.filter(slug__icontains="ebi").first()
        if not event:
            event = Event.objects.filter(translations__title__icontains="ebi").first()
        
        if event:
            translation = event.translations.first()
            title = translation.title if translation else 'No title'
            print(f"✅ Event found: {title}")
            print(f"Event ID: {event.id}")
            print(f"Slug: {event.slug}")
        else:
            print("❌ Event 'Ebi' not found")
            return
    except Exception as e:
        print(f"❌ Error finding event: {e}")
        return
    
    # Check performances
    print("\n=== Performances ===")
    performances = EventPerformance.objects.filter(event=event)
    for perf in performances:
        print(f"Performance: {perf.date} at {perf.start_time}")
        print(f"  ID: {perf.id}")
        print(f"  Max Capacity: {perf.max_capacity}")
        print(f"  Current Capacity: {perf.current_capacity}")
        print(f"  Available Capacity: {perf.available_capacity}")
        print(f"  Is Available: {perf.is_available}")
        print()
    
    # Check sections and capacity
    print("=== Sections and Capacity ===")
    for perf in performances:
        print(f"\nPerformance: {perf.date}")
        
        # Check if sections exist
        sections = EventSection.objects.filter(performance=perf)
        if sections.exists():
            for section in sections:
                print(f"  Section: {section.name}")
                print(f"    Total Capacity: {section.total_capacity}")
                print(f"    Available Capacity: {section.available_capacity}")
                print(f"    Reserved Capacity: {section.reserved_capacity}")
                print(f"    Sold Capacity: {section.sold_capacity}")
                
                # Check ticket types
                ticket_types = SectionTicketType.objects.filter(section=section)
                for tt in ticket_types:
                    print(f"      Ticket Type: {tt.ticket_type.name}")
                    print(f"        Allocated: {tt.allocated_capacity}")
                    print(f"        Available: {tt.available_capacity}")
                    print(f"        Reserved: {tt.reserved_capacity}")
                    print(f"        Sold: {tt.sold_capacity}")
        else:
            print(f"  ❌ No sections found for this performance")
    
    # Check individual seats
    print("\n=== Individual Seats ===")
    for perf in performances:
        print(f"\nPerformance: {perf.date}")
        seats = Seat.objects.filter(performance=perf)
        
        if seats.exists():
            print(f"  Total Seats: {seats.count()}")
            
            # Count by status
            status_counts = seats.values('status').annotate(count=django.db.models.Count('id'))
            for status_count in status_counts:
                status = status_count['status']
                count = status_count['count']
                print(f"    {status.capitalize()}: {count}")
            
            # Check reserved seats with expiration
            reserved_seats = seats.filter(status='reserved')
            if reserved_seats.exists():
                print(f"  Reserved Seats Details:")
                for seat in reserved_seats[:10]:  # Show first 10
                    expires_at = seat.reservation_expires_at
                    if expires_at:
                        is_expired = expires_at < timezone.now()
                        print(f"    Seat {seat.seat_number} (Row {seat.row_number}) - Section {seat.section}")
                        print(f"      Expires: {expires_at}")
                        print(f"      Is Expired: {is_expired}")
                        if is_expired:
                            print(f"      ⚠️  OVERDUE BY: {timezone.now() - expires_at}")
                if reserved_seats.count() > 10:
                    print(f"    ... and {reserved_seats.count() - 10} more reserved seats")
        else:
            print(f"  ❌ No seats found for this performance")
    
    # Check cart items
    print("\n=== Cart Items ===")
    cart_items = CartItem.objects.filter(
        product_type='event',
        product_id=str(event.id)
    )
    
    if cart_items.exists():
        print(f"Total cart items for this event: {cart_items.count()}")
        for item in cart_items:
            print(f"  Cart Item ID: {item.id}")
            print(f"    Quantity: {item.quantity}")
            print(f"    Is Reserved: {item.is_reserved}")
            if item.reservation_expires_at:
                print(f"    Reservation Expires: {item.reservation_expires_at}")
                is_expired = item.reservation_expires_at < timezone.now()
                print(f"    Is Expired: {is_expired}")
                if is_expired:
                    print(f"    ⚠️  OVERDUE BY: {timezone.now() - item.reservation_expires_at}")
            print(f"    Cart Session: {item.cart.session_id}")
            print(f"    Cart User: {item.cart.user}")
    else:
        print("  ✅ No cart items found for this event")
    
    # Check for expired reservations
    print("\n=== Expired Reservations ===")
    now = timezone.now()
    
    # Check expired seats
    expired_seats = Seat.objects.filter(
        performance__event=event,
        status='reserved',
        reservation_expires_at__lt=now
    )
    
    if expired_seats.exists():
        print(f"❌ Found {expired_seats.count()} expired reserved seats!")
        print("These should be automatically released but aren't!")
        
        # Show some examples
        for seat in expired_seats[:5]:
            overdue = now - seat.reservation_expires_at
            print(f"  Seat {seat.seat_number} (Row {seat.row_number}) - Section {seat.section}")
            print(f"    Expired: {seat.reservation_expires_at}")
            print(f"    Overdue by: {overdue}")
    else:
        print("✅ No expired reserved seats found")
    
    # Check expired cart items
    expired_cart_items = CartItem.objects.filter(
        product_type='event',
        product_id=str(event.id),
        is_reserved=True,
        reservation_expires_at__lt=now
    )
    
    if expired_cart_items.exists():
        print(f"❌ Found {expired_cart_items.count()} expired cart items!")
        for item in expired_cart_items[:5]:
            overdue = now - item.reservation_expires_at
            print(f"  Cart Item {item.id}")
            print(f"    Expired: {item.reservation_expires_at}")
            print(f"    Overdue by: {overdue}")
    else:
        print("✅ No expired cart items found")
    
    print("\n=== Recommendations ===")
    print("1. Check if the cleanup task is running")
    print("2. Manually release expired reservations")
    print("3. Check cart cleanup logic")
    print("4. Verify capacity calculation methods")

if __name__ == "__main__":
    debug_ebi_event()
