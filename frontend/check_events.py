#!/usr/bin/env python3
import requests
import json

def check_api_duplicates():
    """Check for duplicate events in API response"""
    url = "http://localhost:8000/api/v1/events/home-events/"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()

            # Collect all event IDs by category
            categories = {
                'upcoming': data.get('upcoming_events', []),
                'past': data.get('past_events', []),
                'special': data.get('special_events', []),
                'featured': data.get('featured_events', []),
                'popular': data.get('popular_events', [])
            }

            # Check for duplicates
            all_events = {}
            duplicates_found = False

            for category_name, events in categories.items():
                print(f"\n{category_name.upper()} EVENTS ({len(events)}):")
                for event in events:
                    event_id = event.get('id')
                    event_title = event.get('title', 'Unknown')

                    if event_id in all_events:
                        print(f"  ❌ DUPLICATE: {event_id} - {event_title} (also in {all_events[event_id]})")
                        duplicates_found = True
                    else:
                        all_events[event_id] = category_name
                        print(f"  ✅ {event_id} - {event_title}")

            if duplicates_found:
                print("\n❌ DUPLICATE EVENTS FOUND! This could cause React key conflicts.")
            else:
                print("\n✅ NO DUPLICATE EVENTS FOUND.")

            return not duplicates_found
        else:
            print(f"API Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == '__main__':
    print("=== CHECKING FOR DUPLICATE EVENTS IN API RESPONSE ===")
    check_api_duplicates()
