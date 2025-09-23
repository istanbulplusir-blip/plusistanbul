#!/usr/bin/env python
import os
import django
import sys
from datetime import date, timedelta, time
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')

# Setup Django
django.setup()

from events.models import (
    EventCategory,
    Venue,
    Event,
    TicketType,
    EventPerformance,
    EventSection,
    SectionTicketType,
    EventOption,
    Seat,
)
from django.db import transaction

def check_existing_events():
    """Check existing events in database"""
    print("=== CHECKING EXISTING EVENTS ===")
    total_events = Event.objects.count()
    print(f"Total events in database: {total_events}")

    if total_events > 0:
        events = Event.objects.all()[:5]
        for event in events:
            print(f"Event {event.id}: {event.title} - Active: {event.is_active}")
            performance_count = EventPerformance.objects.filter(event=event).count()
            print(f"  - Performances: {performance_count}")
    else:
        print("No events found in database")

    return total_events

def create_test_venue():
    """Create or get test venue"""
    venue, created = Venue.objects.get_or_create(
        name="Test Concert Hall",
        defaults={
            'description': 'A modern concert hall for testing',
            'address': '123 Test Street',
            'city': 'Tehran',
            'country': 'Iran',
            'total_capacity': 1000,
            'coordinates': {},
            'facilities': ['parking', 'wifi'],
        }
    )
    print(f"{'Created' if created else 'Found existing'} venue: {venue.name}")
    return venue

def create_test_category():
    """Create or get test category"""
    category, created = EventCategory.objects.get_or_create(
        name="Music Concert",
        defaults={
            'description': 'Live music concerts',
        }
    )
    print(f"{'Created' if created else 'Found existing'} category: {category.name}")
    return category

def create_test_events():
    """Create comprehensive test events"""
    print("\n=== CREATING TEST EVENTS ===")

    venue = create_test_venue()
    category = create_test_category()

    # Create multiple events with different characteristics
    test_events_data = [
        {
            'slug': 'upcoming-concert',
            'title': 'Upcoming Music Festival',
            'style': 'music',
            'is_featured': True,
            'is_popular': False,
            'days_ahead': 7,  # 7 days from now
        },
        {
            'slug': 'popular-rock-show',
            'title': 'Popular Rock Concert',
            'style': 'music',
            'is_featured': False,
            'is_popular': True,
            'days_ahead': 3,  # 3 days from now
        },
        {
            'slug': 'special-jazz-night',
            'title': 'Special Jazz Night',
            'style': 'music',
            'is_featured': True,
            'is_popular': True,
            'days_ahead': 14,  # 2 weeks from now
        },
        {
            'slug': 'past-classical',
            'title': 'Past Classical Concert',
            'style': 'music',
            'is_featured': False,
            'is_popular': False,
            'days_ahead': -5,  # 5 days ago
        },
        {
            'slug': 'featured-sports-event',
            'title': 'Featured Basketball Game',
            'style': 'sports',
            'is_featured': True,
            'is_popular': False,
            'days_ahead': 10,  # 10 days from now
        },
    ]

    created_events = []

    for event_data in test_events_data:
        with transaction.atomic():
            # Create event
            event, created = Event.objects.get_or_create(
                slug=event_data['slug'],
                defaults={
                    'style': event_data['style'],
                    'category': category,
                    'venue': venue,
                    'is_active': True,
                    'is_featured': event_data['is_featured'],
                    'is_popular': event_data['is_popular'],
                    'door_open_time': time(18, 0),
                    'start_time': time(19, 0),
                    'end_time': time(22, 0),
                }
            )

            # Update fields
            event.title = event_data['title']
            event.description = f'A wonderful {event_data["style"]} event for testing purposes.'
            event.short_description = f'Test {event_data["style"]} event'
            event.highlights = 'High-quality entertainment'
            event.rules = 'No outside food or drinks'
            event.required_items = 'Valid ID required'
            event.save()

            # Create performance
            perf_date = date.today() + timedelta(days=event_data['days_ahead'])
            performance, perf_created = EventPerformance.objects.get_or_create(
                event=event,
                date=perf_date,
                defaults={
                    'is_special': event_data.get('is_featured', False),
                    'start_time': time(19, 0),
                    'end_time': time(22, 0),
                    'is_available': True,
                    'max_capacity': 500,
                    'current_capacity': 0,
                    'ticket_capacities': {},
                }
            )

            print(f"{'Created' if created else 'Updated'} event: {event.title}")
            print(f"  - Date: {perf_date}")
            print(f"  - Featured: {event.is_featured}, Popular: {event.is_popular}")
            created_events.append(event)

    return created_events

def main():
    print("Starting database check and population...")

    # Check existing events
    existing_count = check_existing_events()

    if existing_count == 0:
        print("\nNo events found. Creating test events...")
        create_test_events()
        print("\n=== TEST EVENTS CREATED SUCCESSFULLY ===")
    else:
        print(f"\nFound {existing_count} existing events. Skipping creation.")

    # Final check
    print("\n=== FINAL DATABASE STATUS ===")
    check_existing_events()

    print("\n=== API ENDPOINT TEST ===")
    print("The home-events endpoint should now be accessible at:")
    print("http://localhost:8000/api/v1/events/home-events/")

if __name__ == '__main__':
    main()
