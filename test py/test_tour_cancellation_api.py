#!/usr/bin/env python
"""
Test script to verify Tour X cancellation policy API response
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

def test_tour_cancellation_api():
    """Test if Tour X cancellation policy is returned correctly by API"""
    print("🧪 Testing Tour X Cancellation Policy API")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        response = requests.get(
            f"{base_url}/tours/tour-x/",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response received")
            print(f"📋 Tour Title: {data.get('title', 'N/A')}")
            print(f"📋 Cancellation Hours: {data.get('cancellation_hours', 'N/A')}")
            print(f"📋 Refund Percentage: {data.get('refund_percentage', 'N/A')}")
            
            # Check if cancellation policy fields exist
            if 'cancellation_hours' in data and 'refund_percentage' in data:
                print("✅ Cancellation policy fields found in API response")
                
                cancellation_hours = data['cancellation_hours']
                refund_percentage = data['refund_percentage']
                
                if cancellation_hours > 0 and refund_percentage >= 0:
                    print(f"✅ Valid cancellation policy: {refund_percentage}% refund up to {cancellation_hours} hours")
                else:
                    print("⚠️ Cancellation policy values are not valid")
            else:
                print("❌ Cancellation policy fields missing from API response")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_tour_cancellation_api()
