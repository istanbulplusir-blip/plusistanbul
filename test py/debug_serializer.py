#!/usr/bin/env python
"""
Debug script to test the serializer directly
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour
from tours.serializers import TourDetailSerializer
from django.test import RequestFactory

def debug_serializer():
    """Debug the serializer directly"""
    print("🔍 Debugging Serializer")
    print("=" * 60)
    
    # Find Tour X
    tour = Tour.objects.filter(slug='tour-x').first()
    if not tour:
        print("❌ Tour X not found!")
        return
    
    print(f"✅ Found Tour X")
    
    # Create a mock request with different languages
    factory = RequestFactory()
    
    test_languages = ['fa', 'en']
    
    for lang in test_languages:
        print(f"\n🌐 Testing Language: {lang}")
        print("-" * 40)
        
        # Create request with Accept-Language header
        request = factory.get('/api/v1/tours/tour-x/')
        request.LANGUAGE_CODE = lang
        
        # Create serializer context
        context = {'request': request}
        
        # Serialize the tour
        serializer = TourDetailSerializer(tour, context=context)
        data = serializer.data
        
        # Check title
        title = data.get('title', 'No title found')
        print(f"   📝 Serialized Title: {title}")
        
        # Check if title contains Persian characters
        has_persian = any('\u0600' <= char <= '\u06FF' for char in title)
        print(f"   🔤 Contains Persian: {has_persian}")
        
        # Check itinerary items
        itinerary = data.get('itinerary', [])
        if itinerary:
            first_item = itinerary[0]
            item_title = first_item.get('title', '')
            has_persian_item = any('\u0600' <= char <= '\u06FF' for char in item_title)
            print(f"   📋 First itinerary item: {item_title}")
            print(f"   🔤 Item contains Persian: {has_persian_item}")
    
    print("\n" + "=" * 60)
    print("🎯 Serializer Debug Complete!")
    print("=" * 60)

if __name__ == "__main__":
    debug_serializer()
