#!/usr/bin/env python
"""
Test API pricing after creating TourPricing records.
"""

import requests

def test_api_pricing():
    """Test API pricing for capacity-test-tour."""
    
    print("🧪 Testing API Pricing After Fix")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    tour_slug = "capacity-test-tour"
    
    try:
        response = requests.get(f"{base_url}/tours/{tour_slug}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tour: {data.get('title')}")
            
            pricing_summary = data.get('pricing_summary', {})
            print(f"📊 Pricing Summary: {len(pricing_summary)} variants")
            
            for variant_id, pricing in pricing_summary.items():
                age_groups = pricing.get('age_groups', {})
                print(f"  Variant {variant_id}: {len(age_groups)} age groups")
                
                if age_groups:
                    for age_group, details in age_groups.items():
                        factor = details.get('factor', 'N/A')
                        final_price = details.get('final_price', 'N/A')
                        is_free = details.get('is_free', False)
                        print(f"    - {age_group}: factor={factor}, final_price={final_price}, is_free={is_free}")
                else:
                    print(f"    - No age groups data!")
            
            # Check if pricing should work now
            if any(len(p.get('age_groups', {})) > 0 for p in pricing_summary.values()):
                print("\n🎉 Pricing should now work in frontend!")
            else:
                print("\n❌ Pricing still has issues")
                
        else:
            print(f"❌ API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_pricing() 