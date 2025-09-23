#!/usr/bin/env python
"""
Test frontend functionality for Tour system.
"""

import requests
import time

def test_frontend_functionality():
    """Test that frontend pages load correctly."""
    
    print("🧪 Testing Frontend Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:3000"
    
    # Test 1: Home Page
    print("\n1️⃣ Testing Home Page...")
    try:
        response = requests.get(f"{base_url}/fa")
        if response.status_code == 200:
            print("✅ Home Page (Persian) loads correctly")
            if "تور" in response.text or "Tour" in response.text:
                print("   ✅ Tour content found")
            else:
                print("   ⚠️ Tour content not found")
        else:
            print(f"❌ Home Page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Home Page: {e}")
        return False
    
    # Test 2: Tours List Page
    print("\n2️⃣ Testing Tours List Page...")
    try:
        response = requests.get(f"{base_url}/fa/tours")
        if response.status_code == 200:
            print("✅ Tours List Page loads correctly")
            if "تور" in response.text or "Tour" in response.text:
                print("   ✅ Tour content found")
            else:
                print("   ⚠️ Tour content not found")
        else:
            print(f"❌ Tours List Page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Tours List Page: {e}")
        return False
    
    # Test 3: Tour Detail Page
    print("\n3️⃣ Testing Tour Detail Page...")
    try:
        response = requests.get(f"{base_url}/fa/tours/capacity-test-tour")
        if response.status_code == 200:
            print("✅ Tour Detail Page loads correctly")
            if "Capacity Test Tour" in response.text or "تور" in response.text:
                print("   ✅ Tour detail content found")
            else:
                print("   ⚠️ Tour detail content not found")
        else:
            print(f"❌ Tour Detail Page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Tour Detail Page: {e}")
        return False
    
    # Test 4: English Locale
    print("\n4️⃣ Testing English Locale...")
    try:
        response = requests.get(f"{base_url}/en/tours")
        if response.status_code == 200:
            print("✅ English Tours Page loads correctly")
            if "Tour" in response.text:
                print("   ✅ English content found")
            else:
                print("   ⚠️ English content not found")
        else:
            print(f"❌ English Tours Page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing English Tours Page: {e}")
        return False
    
    # Test 5: Turkish Locale
    print("\n5️⃣ Testing Turkish Locale...")
    try:
        response = requests.get(f"{base_url}/tr/tours")
        if response.status_code == 200:
            print("✅ Turkish Tours Page loads correctly")
            if "Tur" in response.text:
                print("   ✅ Turkish content found")
            else:
                print("   ⚠️ Turkish content not found")
        else:
            print(f"❌ Turkish Tours Page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Turkish Tours Page: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All frontend functionality tests passed!")
    return True

if __name__ == "__main__":
    test_frontend_functionality()
