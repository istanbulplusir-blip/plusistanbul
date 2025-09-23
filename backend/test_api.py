#!/usr/bin/env python
import requests
import json

def test_home_events_api():
    """Test the home-events API endpoint"""
    url = "http://localhost:8000/api/v1/events/home-events/"

    print(f"Testing API endpoint: {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n✅ API Response Successful!")
            print("\nResponse structure:")
            print(f"- upcoming_events: {len(data.get('upcoming_events', []))} events")
            print(f"- past_events: {len(data.get('past_events', []))} events")
            print(f"- special_events: {len(data.get('special_events', []))} events")
            print(f"- featured_events: {len(data.get('featured_events', []))} events")
            print(f"- popular_events: {len(data.get('popular_events', []))} events")

            print("\nTotal counts:")
            counts = data.get('total_counts', {})
            print(f"- upcoming: {counts.get('upcoming', 0)}")
            print(f"- past: {counts.get('past', 0)}")
            print(f"- special: {counts.get('special', 0)}")
            print(f"- featured: {counts.get('featured', 0)}")
            print(f"- popular: {counts.get('popular', 0)}")

            # Show sample event if available
            if data.get('upcoming_events'):
                sample = data['upcoming_events'][0]
                print(f"\nSample upcoming event: {sample.get('title', 'N/A')}")

            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return False

def test_regular_events_api():
    """Test the regular events API as fallback"""
    url = "http://localhost:8000/api/v1/events/events/"

    print(f"\n\nTesting fallback API: {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Fallback API working!")
            print(f"Total events: {data.get('count', 0)}")
            return True
        else:
            print(f"❌ Fallback API Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Fallback API failed: {e}")
        return False

if __name__ == '__main__':
    print("=== TESTING EVENT APIs ===\n")

    # Test main API
    main_success = test_home_events_api()

    # Test fallback API
    fallback_success = test_regular_events_api()

    print("\n=== SUMMARY ===")
    print(f"Home Events API: {'✅ Working' if main_success else '❌ Failed'}")
    print(f"Fallback API: {'✅ Working' if fallback_success else '❌ Failed'}")

    if main_success:
        print("\n🎉 APIs are working! Frontend should now display events.")
    else:
        print("\n⚠️  Main API failed, but fallback might work.")
