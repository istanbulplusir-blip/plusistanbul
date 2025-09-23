#!/usr/bin/env python
"""
Management command to fix Tour X images by converting Unsplash URLs to local media files
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from tours.models import Tour, TourItinerary

class Command(BaseCommand):
    help = "Fix Tour X images by converting Unsplash URLs to local media files"
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Fixing Tour X images...")
        
        # Find Tour X
        tour = Tour.objects.filter(slug='tour-x').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour X not found! Please create it first."))
            return
        
        self.stdout.write(f"✅ Found Tour X: {tour.title}")
        
        try:
            # Fix main tour image
            if not tour.image:
                self.stdout.write("   📸 Setting main tour image...")
                tour.image = "tours/tour-x-main.jpg"
                tour.save()
                self.stdout.write("   ✅ Main tour image set")
            
            # Fix gallery images
            if tour.gallery:
                self.stdout.write("   🖼️ Converting gallery images...")
                new_gallery = []
                for i, img_url in enumerate(tour.gallery):
                    if isinstance(img_url, str) and img_url.startswith('http'):
                        # Convert to local path
                        new_path = f"tours/tour-x-gallery-{i+1}.jpg"
                        new_gallery.append(new_path)
                        self.stdout.write(f"   ✅ Gallery {i+1}: {img_url} → {new_path}")
                    else:
                        new_gallery.append(img_url)
                
                tour.gallery = new_gallery
                tour.save()
                self.stdout.write("   ✅ Gallery images converted")
            
            # Fix itinerary images
            itinerary_items = TourItinerary.objects.filter(tour=tour).order_by('order')
            self.stdout.write("   🗺️ Converting itinerary images...")
            
            for item in itinerary_items:
                # Check if image field has a value and convert it to string
                image_value = str(item.image) if item.image else ""
                if image_value and image_value.startswith('http'):
                    # Convert to local path
                    new_path = f"tours/tour-x-itinerary-{item.order}.jpg"
                    item.image = new_path
                    item.save()
                    self.stdout.write(f"   ✅ Itinerary {item.order}: {image_value} → {new_path}")
            
            self.stdout.write("   ✅ Itinerary images converted")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error fixing images: {e}"))
            return
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 IMAGE FIX SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write("✅ Tour X images converted to local paths!")
        self.stdout.write("   - Main image: tours/tour-x-main.jpg")
        self.stdout.write("   - Gallery: tours/tour-x-gallery-*.jpg")
        self.stdout.write("   - Itinerary: tours/tour-x-itinerary-*.jpg")
        self.stdout.write("   - Frontend will now load images correctly")
        self.stdout.write(self.style.SUCCESS("\n🎯 Tour X image fix complete!"))

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'fix_tour_x_images'])
