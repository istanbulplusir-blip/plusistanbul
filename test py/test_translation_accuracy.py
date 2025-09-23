#!/usr/bin/env python
"""
Detailed test script to verify translation accuracy
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

def test_translation_accuracy():
    """Test if translations are working correctly"""
    print("🔍 Testing Translation Accuracy")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test both Persian and English
    test_languages = ['fa', 'en']
    
    results = {}
    
    for lang in test_languages:
        print(f"\n🌐 Testing Language: {lang}")
        print("-" * 40)
        
        headers = {'Accept-Language': lang}
        
        try:
            response = requests.get(
                f"{base_url}/tours/tour-x/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results[lang] = data  # No data wrapper
                
                # Check tour title
                title = data['title']
                print(f"   📝 Tour Title: {title}")
                
                # Check if title contains Persian characters
                has_persian = any('\u0600' <= char <= '\u06FF' for char in title)
                print(f"   🔤 Contains Persian: {has_persian}")
                
                # Check itinerary items
                itinerary = data['itinerary']
                print(f"   📋 Itinerary Items: {len(itinerary)}")
                
                if itinerary:
                    # Check first 3 items
                    for i, item in enumerate(itinerary[:3]):
                        item_title = item.get('title', '')
                        item_desc = item.get('description', '')[:50] + "..."
                        has_persian_item = any('\u0600' <= char <= '\u06FF' for char in item_title)
                        
                        print(f"      Item {i+1}: {item_title}")
                        print(f"         Persian: {has_persian_item}")
                        print(f"         Desc: {item_desc}")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Compare results
    print("\n" + "=" * 60)
    print("📊 TRANSLATION COMPARISON")
    print("=" * 60)
    
    if 'fa' in results and 'en' in results:
        fa_data = results['fa']
        en_data = results['en']
        
        # Compare tour titles
        fa_title = fa_data['title']
        en_title = en_data['title']
        
        fa_has_persian = any('\u0600' <= char <= '\u06FF' for char in fa_title)
        en_has_persian = any('\u0600' <= char <= '\u06FF' for char in en_title)
        
        print(f"\n🏷️ Tour Title Comparison:")
        print(f"   Persian: {fa_title}")
        print(f"   English: {en_title}")
        print(f"   Persian contains Persian chars: {fa_has_persian}")
        print(f"   English contains Persian chars: {en_has_persian}")
        
        if fa_has_persian and not en_has_persian:
            print("   ✅ Translation working correctly!")
        elif not fa_has_persian and en_has_persian:
            print("   ⚠️ Translation reversed!")
        elif fa_has_persian and en_has_persian:
            print("   ⚠️ Both showing Persian!")
        elif not fa_has_persian and not en_has_persian:
            print("   ⚠️ Both showing English!")
        
        # Compare itinerary items
        fa_itinerary = fa_data['itinerary']
        en_itinerary = en_data['itinerary']
        
        print(f"\n🗺️ Itinerary Comparison (first 3 items):")
        
        for i in range(min(3, len(fa_itinerary), len(en_itinerary))):
            fa_item = fa_itinerary[i]
            en_item = en_itinerary[i]
            
            fa_item_title = fa_item['title']
            en_item_title = en_item['title']
            
            fa_has_persian = any('\u0600' <= char <= '\u06FF' for char in fa_item_title)
            en_has_persian = any('\u0600' <= char <= '\u06FF' for char in en_item_title)
            
            print(f"   Item {i+1}:")
            print(f"     Persian: {fa_item_title}")
            print(f"     English: {en_item_title}")
            print(f"     Persian has Persian: {fa_has_persian}")
            print(f"     English has Persian: {en_has_persian}")
            
            if fa_has_persian and not en_has_persian:
                print("     ✅ Correct!")
            else:
                print("     ⚠️ Issue detected!")
    
    print("\n" + "=" * 60)
    print("🎯 Translation Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_translation_accuracy()
