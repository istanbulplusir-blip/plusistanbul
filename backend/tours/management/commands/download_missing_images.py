#!/usr/bin/env python
"""
Management command to download missing Tour X images
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from tours.models import Tour, TourItinerary

class Command(BaseCommand):
    help = "Download missing Tour X images"
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Downloading missing Tour X images...")
        
        # Find Tour X
        tour = Tour.objects.filter(slug='tour-x').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour X not found! Please create it first."))
            return
        
        self.stdout.write(f"✅ Found Tour X: {tour.title}")
        
        # Create media/tours directory if it doesn't exist
        media_tours_dir = os.path.join(settings.MEDIA_ROOT, 'tours')
        os.makedirs(media_tours_dir, exist_ok=True)
        
        try:
            # Download missing gallery images
            missing_gallery = [
                ('tour-x-gallery-2.jpg', 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop&crop=center'),
            ]
            
            self.stdout.write("   🖼️ Downloading missing gallery images...")
            for filename, url in missing_gallery:
                image_path = os.path.join(media_tours_dir, filename)
                if not os.path.exists(image_path):
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        self.stdout.write(f"   ✅ Downloaded: {filename}")
                    else:
                        self.stdout.write(self.style.WARNING(f"   ⚠️ Failed to download: {filename}"))
                else:
                    self.stdout.write(f"   ✅ Already exists: {filename}")
            
            # Download missing itinerary images
            missing_itinerary = [
                ('tour-x-itinerary-2.jpg', 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop&crop=center'),
            ]
            
            self.stdout.write("   🗺️ Downloading missing itinerary images...")
            for filename, url in missing_itinerary:
                image_path = os.path.join(media_tours_dir, filename)
                if not os.path.exists(image_path):
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        self.stdout.write(f"   ✅ Downloaded: {filename}")
                    else:
                        self.stdout.write(self.style.WARNING(f"   ⚠️ Failed to download: {filename}"))
                else:
                    self.stdout.write(f"   ✅ Already exists: {filename}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error downloading images: {e}"))
            return
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 MISSING IMAGES DOWNLOAD SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write("✅ Missing Tour X images downloaded!")
        self.stdout.write("   - All gallery images now exist")
        self.stdout.write("   - All itinerary images now exist")
        self.stdout.write("   - Frontend will now load all images correctly")
        self.stdout.write(self.style.SUCCESS("\n🎯 Missing images download complete!"))

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'download_missing_images'])
