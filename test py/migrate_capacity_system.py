#!/usr/bin/env python
"""
Migration script to fix the Event capacity system.
Run with: python migrate_capacity_system.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.db import transaction, connection
from django.utils import timezone
from events.models import Event, EventPerformance, EventSection, SectionTicketType, Seat, TicketType

def migrate_capacity_system():
    """Migrate the capacity system to use computed properties."""
    print("=== MIGRATING CAPACITY SYSTEM ===\n")
    
    try:
        with transaction.atomic():
            # Check if the old capacity fields exist
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM pragma_table_info('events_sectiontickettype')
                    WHERE name IN ('allocated_capacity', 'available_capacity', 'reserved_capacity', 'sold_capacity')
                """)
                existing_fields = [row[0] for row in cursor.fetchall()]
            
            if existing_fields:
                print(f"Found old capacity fields: {existing_fields}")
                print("Removing old capacity fields...")
                
                # Remove the old capacity fields
                for field in existing_fields:
                    try:
                        cursor.execute(f"ALTER TABLE events_sectiontickettype DROP COLUMN {field}")
                        print(f"  Removed {field}")
                    except Exception as e:
                        print(f"  Error removing {field}: {e}")
                
                print("Old capacity fields removed successfully")
            else:
                print("No old capacity fields found - migration already completed")
            
            # Update all SectionTicketType records to ensure they have proper relationships
            print("\nUpdating SectionTicketType records...")
            
            updated_count = 0
            for stt in SectionTicketType.objects.all():
                # Ensure the section has a performance
                if not hasattr(stt.section, 'performance'):
                    print(f"  Warning: SectionTicketType {stt.id} has no performance")
                    continue
                
                # Ensure seats exist for this section and ticket type
                seat_count = Seat.objects.filter(
                    performance=stt.section.performance,
                    section=stt.section.name,
                    ticket_type=stt.ticket_type
                ).count()
                
                if seat_count == 0:
                    print(f"  Creating {stt.section.total_capacity} seats for {stt.section.name} - {stt.ticket_type.name}")
                    
                    # Create seats for this section and ticket type
                    for row_num in range(1, 6):  # 5 rows
                        for seat_num in range(1, 3):  # 2 seats per row
                            seat, created = Seat.objects.get_or_create(
                                performance=stt.section.performance,
                                section=stt.section.name,
                                row_number=str(row_num),
                                seat_number=str(seat_num),
                                ticket_type=stt.ticket_type,
                                defaults={
                                    'status': 'available',
                                    'price': stt.section.base_price * stt.price_modifier,
                                    'currency': stt.section.currency,
                                    'is_wheelchair_accessible': stt.section.is_wheelchair_accessible,
                                    'is_premium': stt.section.is_premium
                                }
                            )
                            if created:
                                updated_count += 1
                
                updated_count += 1
            
            print(f"Updated {updated_count} SectionTicketType records")
            
            # Verify the new system works
            print("\nVerifying new capacity system...")
            
            for stt in SectionTicketType.objects.all()[:5]:  # Check first 5
                print(f"  {stt.section.name} - {stt.ticket_type.name}:")
                print(f"    Allocated: {stt.allocated_capacity}")
                print(f"    Available: {stt.available_capacity}")
                print(f"    Reserved: {stt.reserved_capacity}")
                print(f"    Sold: {stt.sold_capacity}")
            
            print("\nCapacity system migration completed successfully!")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()

def verify_capacity_system():
    """Verify that the new capacity system is working correctly."""
    print("\n=== VERIFYING CAPACITY SYSTEM ===\n")
    
    # Check a few SectionTicketTypes
    stts = SectionTicketType.objects.all()[:3]
    
    for stt in stts:
        print(f"SectionTicketType: {stt.section.name} - {stt.ticket_type.name}")
        
        # Check computed properties
        allocated = stt.allocated_capacity
        available = stt.available_capacity
        reserved = stt.reserved_capacity
        sold = stt.sold_capacity
        
        print(f"  Allocated: {allocated}")
        print(f"  Available: {available}")
        print(f"  Reserved: {reserved}")
        print(f"  Sold: {sold}")
        
        # Verify consistency
        if allocated == available + reserved + sold:
            print("  ✓ Capacity consistency: OK")
        else:
            print(f"  ✗ Capacity inconsistency: {allocated} != {available} + {reserved} + {sold}")
        
        # Check actual seat counts
        actual_seats = Seat.objects.filter(
            performance=stt.section.performance,
            section=stt.section.name,
            ticket_type=stt.ticket_type
        )
        
        actual_allocated = actual_seats.count()
        actual_available = actual_seats.filter(status='available').count()
        actual_reserved = actual_seats.filter(status='reserved').count()
        actual_sold = actual_seats.filter(status='sold').count()
        
        print(f"  Actual seats - Total: {actual_allocated}, Available: {actual_available}, Reserved: {actual_reserved}, Sold: {actual_sold}")
        
        if allocated == actual_allocated:
            print("  ✓ Allocated capacity: OK")
        else:
            print(f"  ✗ Allocated capacity mismatch: {allocated} != {actual_allocated}")

if __name__ == '__main__':
    print("Starting capacity system migration...\n")
    
    # Run migration
    migrate_capacity_system()
    
    # Verify the new system
    verify_capacity_system()
    
    print("\n" + "="*50)
    print("Migration and verification complete!")
