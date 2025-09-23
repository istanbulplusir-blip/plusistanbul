#!/usr/bin/env python3
"""
Test script to debug section validation issues in the events API.
This script will help identify why section "C" is not found for the performance.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
EVENT_SLUG = "test-event"  # Replace with actual event slug

def test_event_details():
    """Test getting event details to see available sections."""
    print("🔍 Testing Event Details...")
    
    try:
        response = requests.get(f"{BASE_URL}/events/events/{EVENT_SLUG}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Event found: {data.get('title', 'Unknown')}")
            
            # Check performances
            performances = data.get('performances', [])
            print(f"📅 Found {len(performances)} performances")
            
            for perf in performances:
                print(f"\n🎭 Performance ID: {perf.get('id')}")
                print(f"   Date: {perf.get('date')}")
                print(f"   Time: {perf.get('start_time')}")
                
                # Check sections
                sections = perf.get('sections', [])
                print(f"   Sections: {len(sections)}")
                
                for section in sections:
                    print(f"     - {section.get('name')} (ID: {section.get('id')})")
                    print(f"       Capacity: {section.get('total_capacity')}")
                    print(f"       Available: {section.get('available_capacity')}")
                    
                    # Check ticket types
                    ticket_types = section.get('ticket_types', [])
                    print(f"       Ticket Types: {len(ticket_types)}")
                    
                    for tt in ticket_types:
                        print(f"         • {tt.get('ticket_type', {}).get('name', 'Unknown')} (ID: {tt.get('id')})")
                        print(f"           Available: {tt.get('available_capacity')}")
        else:
            print(f"❌ Failed to get event: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timeout - backend may be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - backend may be down")
    except Exception as e:
        print(f"💥 Error: {e}")

def test_pricing_calculation():
    """Test pricing calculation with section C to see the exact error."""
    print("\n💰 Testing Pricing Calculation...")
    
    # You'll need to replace these with actual IDs from the event details
    pricing_request = {
        "performance_id": "3625cf6b-d630-4d96-a36f-909f60b1ecb1",  # From error logs
        "section_name": "C",
        "ticket_type_id": "ce78eb8a-94cc-4d30-83b6-98b5252c71d4",  # From error logs
        "quantity": 1,
        "selected_options": [],
        "discount_code": ""
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/events/events/{EVENT_SLUG}/calculate_pricing/",
            json=pricing_request,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ Pricing calculation successful")
            data = response.json()
            print(f"Price breakdown: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Pricing calculation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timeout - backend may be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - backend may be down")
    except Exception as e:
        print(f"💥 Error: {e}")

def test_performance_sections():
    """Test getting performance sections directly."""
    print("\n🎯 Testing Performance Sections...")
    
    # You'll need to replace with actual performance ID
    performance_id = "3625cf6b-d630-4d96-a36f-909f60b1ecb1"
    
    try:
        response = requests.get(
            f"{BASE_URL}/events/events/{EVENT_SLUG}/performances/{performance_id}/seats/",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Performance sections retrieved")
            print(f"Performance ID: {data.get('performance_id')}")
            print(f"Total sections: {data.get('total_sections')}")
            
            sections = data.get('sections', [])
            for section in sections:
                print(f"\n📍 Section: {section.get('name')}")
                print(f"   Description: {section.get('description', 'N/A')}")
                print(f"   Total capacity: {section.get('total_capacity')}")
                print(f"   Available capacity: {section.get('available_capacity')}")
                print(f"   Base price: {section.get('base_price')} {section.get('currency', 'USD')}")
                
                # Check ticket types
                ticket_types = section.get('ticket_types', [])
                print(f"   Ticket types: {len(ticket_types)}")
                
                for tt in ticket_types:
                    print(f"     • {tt.get('ticket_type', {}).get('name', 'Unknown')}")
                    print(f"       Price modifier: {tt.get('price_modifier')}")
                    print(f"       Available capacity: {tt.get('available_capacity')}")
        else:
            print(f"❌ Failed to get performance sections: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timeout - backend may be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - backend may be down")
    except Exception as e:
        print(f"💥 Error: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting Section Validation Tests")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print(f"Event slug: {EVENT_SLUG}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 50)
    
    test_event_details()
    test_performance_sections()
    test_pricing_calculation()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed")
    print("\n💡 Next steps:")
    print("1. Check if the backend is running")
    print("2. Verify the event slug exists")
    print("3. Check if section 'C' actually exists in the database")
    print("4. Look for any data migration issues")

if __name__ == "__main__":
    main()
