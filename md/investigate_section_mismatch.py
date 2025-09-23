#!/usr/bin/env python3
"""
Comprehensive investigation script to identify section data mismatch issues.
This script will help debug why frontend shows sections that backend can't find.
"""

import requests
import json
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
EVENT_SLUG = "18316769-d8ae-4e2e-9837-b53aa121cb49"  # From error logs

def test_backend_health():
    """Test if backend is running and responsive."""
    print("🏥 Testing Backend Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and responsive")
            return True
        else:
            print(f"⚠️ Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Backend is slow to respond")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False

def investigate_event_structure():
    """Investigate the complete event structure to understand the data mismatch."""
    print("\n🔍 Investigating Event Structure...")
    
    try:
        # Get event details
        response = requests.get(f"{BASE_URL}/events/events/{EVENT_SLUG}/", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Event found: {data.get('title', 'Unknown')}")
            print(f"Event ID: {data.get('id')}")
            
            # Check performances
            performances = data.get('performances', [])
            print(f"📅 Found {len(performances)} performances")
            
            for i, perf in enumerate(performances):
                print(f"\n🎭 Performance {i+1}:")
                print(f"   ID: {perf.get('id')}")
                print(f"   Date: {perf.get('date')}")
                print(f"   Time: {perf.get('start_time')}")
                
                # Check sections in performance
                sections = perf.get('sections', [])
                print(f"   Sections in performance: {len(sections)}")
                
                if sections:
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
                    print("     ⚠️ No sections found in performance")
                
                # Check if this is the problematic performance
                if perf.get('id') == "f8d0c7ea-cba3-4fa9-b615-4270b843d9e2":
                    print("     🎯 This is the problematic performance from the logs!")
                    
        else:
            print(f"❌ Failed to get event: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timeout - backend may be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - backend may be down")
    except Exception as e:
        print(f"💥 Error: {e}")

def test_performance_sections_endpoint():
    """Test the specific performance sections endpoint that's failing."""
    print("\n🎯 Testing Performance Sections Endpoint...")
    
    performance_id = "f8d0c7ea-cba3-4fa9-b615-4270b843d9e2"
    
    try:
        response = requests.get(
            f"{BASE_URL}/events/events/{EVENT_SLUG}/performances/{performance_id}/seats/",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Performance sections endpoint working")
            print(f"Performance ID: {data.get('performance_id')}")
            print(f"Total sections: {data.get('total_sections')}")
            
            sections = data.get('sections', [])
            if sections:
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
                print("⚠️ No sections returned from endpoint")
                
        else:
            print(f"❌ Performance sections endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timeout - backend may be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - backend may be down")
    except Exception as e:
        print(f"💥 Error: {e}")

def test_pricing_calculation_directly():
    """Test pricing calculation directly to see the exact error."""
    print("\n💰 Testing Pricing Calculation Directly...")
    
    pricing_request = {
        "performance_id": "f8d0c7ea-cba3-4fa9-b615-4270b843d9e2",
        "section_name": "B",
        "ticket_type_id": "ce78eb8a-94cc-4d30-83b6-98b5252c71d4",
        "quantity": 1,
        "selected_options": [],
        "discount_code": ""
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/events/events/{EVENT_SLUG}/calculate_pricing/",
            json=pricing_request,
            timeout=20
        )
        
        if response.status_code == 200:
            print("✅ Pricing calculation successful")
            data = response.json()
            print(f"Price breakdown: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Pricing calculation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"Error message: {error_data['error']}")
                if 'detail' in error_data:
                    print(f"Error detail: {error_data['detail']}")
            except:
                pass
                
    except requests.exceptions.Timeout:
        print("⏰ Request timeout - backend may be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - backend may be down")
    except Exception as e:
        print(f"💥 Error: {e}")

def check_database_consistency():
    """Check if there are database consistency issues."""
    print("\n🗄️ Checking Database Consistency...")
    
    try:
        # Test a simple endpoint to see if database is accessible
        response = requests.get(f"{BASE_URL}/events/", timeout=10)
        
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Database accessible - found {len(events)} events")
            
            # Check if our event exists in the list
            event_exists = any(event.get('id') == EVENT_SLUG for event in events)
            if event_exists:
                print("✅ Event exists in events list")
            else:
                print("⚠️ Event not found in events list - possible ID mismatch")
        else:
            print(f"⚠️ Database endpoint responded with: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Database check failed: {e}")

def main():
    """Run comprehensive investigation."""
    print("🚀 Starting Comprehensive Section Mismatch Investigation")
    print("=" * 70)
    print(f"Testing API at: {BASE_URL}")
    print(f"Event ID: {EVENT_SLUG}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 70)
    
    # Check backend health first
    if not test_backend_health():
        print("\n❌ Backend is not accessible. Please start the backend first.")
        sys.exit(1)
    
    # Run all investigations
    investigate_event_structure()
    test_performance_sections_endpoint()
    test_pricing_calculation_directly()
    check_database_consistency()
    
    print("\n" + "=" * 70)
    print("🏁 Investigation completed")
    print("\n💡 Analysis:")
    print("1. If sections exist in event data but not in performance endpoint → API issue")
    print("2. If no sections exist anywhere → Database migration issue")
    print("3. If pricing fails with 400 → Section validation logic issue")
    print("4. If backend is slow → Performance optimization needed")
    print("\n🔧 Next steps:")
    print("1. Check backend logs for errors")
    print("2. Verify database has section data")
    print("3. Check if recent migrations affected sections")
    print("4. Test with a different event to see if issue is global")

if __name__ == "__main__":
    main()
