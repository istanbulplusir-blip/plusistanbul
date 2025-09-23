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
from django.db import transaction

def fix_expired_reservations():
    print("=== آزادسازی صندلی‌های منقضی شده ===\n")
    
    now = timezone.now()
    
    # Find expired reserved seats
    expired_seats = Seat.objects.filter(
        status='reserved',
        reservation_expires_at__lt=now
    )
    
    if not expired_seats.exists():
        print("✅ هیچ صندلی منقضی شده‌ای یافت نشد")
        return
    
    print(f"❌ یافت شد: {expired_seats.count()} صندلی منقضی شده")
    
    # Group by performance for better reporting
    performance_groups = {}
    for seat in expired_seats:
        perf_key = f"{seat.performance.event.slug} - {seat.performance.date}"
        if perf_key not in performance_groups:
            performance_groups[perf_key] = []
        performance_groups[perf_key].append(seat)
    
    print("\n=== جزئیات صندلی‌های منقضی شده ===")
    for perf_key, seats in performance_groups.items():
        print(f"\n{perf_key}:")
        for seat in seats[:5]:  # Show first 5
            overdue = now - seat.reservation_expires_at
            print(f"  Seat {seat.seat_number} (Row {seat.row_number}) - Section {seat.section}")
            print(f"    Expired: {seat.reservation_expires_at}")
            print(f"    Overdue by: {overdue}")
        if len(seats) > 5:
            print(f"  ... and {len(seats) - 5} more seats")
    
    # Ask for confirmation
    response = input("\nآیا می‌خواهید این صندلی‌ها آزاد شوند؟ (y/n): ")
    if response.lower() != 'y':
        print("عملیات لغو شد")
        return
    
    # Release expired seats
    print("\n=== آزادسازی صندلی‌ها ===")
    
    with transaction.atomic():
        try:
            # Update all expired seats to available
            updated_count = expired_seats.update(
                status='available',
                reservation_expires_at=None,
                reservation_id=None
            )
            
            print(f"✅ {updated_count} صندلی با موفقیت آزاد شد")
            
            # Clear capacity cache for affected sections
            affected_performances = set(expired_seats.values_list('performance_id', flat=True))
            affected_sections = set(expired_seats.values_list('section', flat=True))
            
            print(f"تأثیر بر {len(affected_performances)} performance و {len(affected_sections)} section")
            
        except Exception as e:
            print(f"❌ خطا در آزادسازی صندلی‌ها: {e}")
            return
    
    # Verify the fix
    print("\n=== تأیید آزادسازی ===")
    
    # Check remaining reserved seats
    remaining_reserved = Seat.objects.filter(status='reserved')
    print(f"صندلی‌های رزرو شده باقی‌مانده: {remaining_reserved.count()}")
    
    # Check if any are still expired
    still_expired = Seat.objects.filter(
        status='reserved',
        reservation_expires_at__lt=now
    )
    
    if still_expired.exists():
        print(f"❌ هنوز {still_expired.count()} صندلی منقضی شده وجود دارد")
    else:
        print("✅ همه صندلی‌های منقضی شده آزاد شدند")
    
    # Show updated capacity
    print("\n=== ظرفیت به‌روز شده ===")
    
    for perf_key, seats in performance_groups.items():
        # Get the first seat to find performance
        first_seat = seats[0]
        performance = first_seat.performance
        
        print(f"\n{perf_key}:")
        
        # Check sections
        sections = EventSection.objects.filter(performance=performance)
        for section in sections:
            print(f"  Section {section.name}:")
            print(f"    Total: {section.total_capacity}")
            print(f"    Available: {section.available_capacity}")
            print(f"    Reserved: {section.reserved_capacity}")
            print(f"    Sold: {section.sold_capacity}")
    
    print("\n=== عملیات کامل شد ===")
    print("حالا می‌توانید frontend را تست کنید")

if __name__ == "__main__":
    fix_expired_reservations()
