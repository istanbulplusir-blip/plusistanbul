#!/usr/bin/env python
"""
Debug script to check description translation for Tour X
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour

def debug_description_translation():
    """Debug description translation"""
    print("🔍 Debugging Description Translation")
    print("=" * 60)
    
    # Find Tour X
    tour = Tour.objects.filter(slug='tour-x').first()
    if not tour:
        print("❌ Tour X not found!")
        return
    
    print(f"✅ Found Tour X")
    
    # Check description in different languages
    print("\n📝 Description in different languages:")
    
    # English
    tour.set_current_language('en')
    english_desc = tour.description
    print(f"   English: {english_desc[:100]}...")
    
    # Persian
    tour.set_current_language('fa')
    persian_desc = tour.description
    print(f"   Persian: {persian_desc[:100]}...")
    
    # Check if they are different
    if english_desc != persian_desc:
        print("   ✅ Descriptions are different - translation working!")
    else:
        print("   ⚠️ Descriptions are the same - translation not working!")
    
    # Check the actual translation records
    print("\n🔍 Checking translation records:")
    try:
        translations = tour.translations.all()
        print(f"   Total translations: {translations.count()}")
        
        for trans in translations:
            print(f"   Language: {trans.language_code}")
            print(f"   Title: {trans.title}")
            print(f"   Description: {trans.description[:100]}...")
            print("   ---")
            
    except Exception as e:
        print(f"   ❌ Error checking translations: {e}")
    
    # Check if English description is empty or same as Persian
    english_trans = tour.translations.filter(language_code='en').first()
    if english_trans:
        if not english_trans.description or english_trans.description.strip() == '':
            print("   ❌ English description is empty!")
        elif english_trans.description == tour.translations.filter(language_code='fa').first().description:
            print("   ❌ English description is same as Persian!")
        else:
            print("   ✅ English description exists and is different from Persian")

if __name__ == "__main__":
    debug_description_translation()
