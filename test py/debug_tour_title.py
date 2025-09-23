#!/usr/bin/env python
"""
Debug script to check tour title translation directly in Django
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour

def debug_tour_title():
    """Debug tour title translation"""
    print("🔍 Debugging Tour Title Translation")
    print("=" * 60)
    
    # Find Tour X
    tour = Tour.objects.filter(slug='tour-x').first()
    if not tour:
        print("❌ Tour X not found!")
        return
    
    print(f"✅ Found Tour X")
    
    # Check title in different languages
    print("\n📝 Title in different languages:")
    
    # English
    tour.set_current_language('en')
    english_title = tour.title
    print(f"   English: {english_title}")
    
    # Persian
    tour.set_current_language('fa')
    persian_title = tour.title
    print(f"   Persian: {persian_title}")
    
    # Check if they are different
    if english_title != persian_title:
        print("   ✅ Titles are different - translation working!")
    else:
        print("   ⚠️ Titles are the same - translation not working!")
    
    # Check the actual translation records
    print("\n🔍 Checking translation records:")
    try:
        translations = tour.translations.all()
        print(f"   Total translations: {translations.count()}")
        
        for trans in translations:
            print(f"   Language: {trans.language_code}")
            print(f"   Title: {trans.title}")
            print(f"   Description: {trans.description[:50]}...")
            print("   ---")
            
    except Exception as e:
        print(f"   ❌ Error checking translations: {e}")
    
    # Try to get title directly from model
    print("\n🔍 Direct model access:")
    try:
        # Get English translation
        english_trans = tour.translations.filter(language_code='en').first()
        if english_trans:
            print(f"   English translation found: {english_trans.title}")
        else:
            print("   ❌ English translation not found")
        
        # Get Persian translation
        persian_trans = tour.translations.filter(language_code='fa').first()
        if persian_trans:
            print(f"   Persian translation found: {persian_trans.title}")
        else:
            print("   ❌ Persian translation not found")
            
    except Exception as e:
        print(f"   ❌ Error accessing translations: {e}")

if __name__ == "__main__":
    debug_tour_title()
