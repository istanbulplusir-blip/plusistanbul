#!/usr/bin/env python
"""
Management command to download and save Tour X images
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from tours.models import Tour, TourItinerary

class Command(BaseCommand):
    help = "Download and save Tour X images"
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Downloading Tour X images...")
        
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
            # Download and save main tour image
            if not tour.image or not os.path.exists(os.path.join(settings.MEDIA_ROOT, str(tour.image))):
                self.stdout.write("   📸 Downloading main tour image...")
                main_image_url = "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop&crop=center"
                response = requests.get(main_image_url, timeout=30)
                if response.status_code == 200:
                    image_path = os.path.join(media_tours_dir, 'tour-x-main.jpg')
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    tour.image = 'tours/tour-x-main.jpg'
                    tour.save()
                    self.stdout.write("   ✅ Main tour image downloaded")
                else:
                    self.stdout.write(self.style.WARNING("   ⚠️ Failed to download main image"))
            
            # Download and save gallery images
            if tour.gallery:
                self.stdout.write("   🖼️ Downloading gallery images...")
                gallery_urls = [
                    "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop&crop=center",
                    "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=800&h=600&fit=crop&crop=center",
                    "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop&crop=center",
                    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=600&fit=crop&crop=center",
                    "https://images.unsplash.com/photo-1542810634-71277d95dcbb?w=800&h=600&fit=crop&crop=center"
                ]
                
                new_gallery = []
                for i, url in enumerate(gallery_urls):
                    image_filename = f'tour-x-gallery-{i+1}.jpg'
                    image_path = os.path.join(media_tours_dir, image_filename)
                    
                    if not os.path.exists(image_path):
                        response = requests.get(url, timeout=30)
                        if response.status_code == 200:
                            with open(image_path, 'wb') as f:
                                f.write(response.content)
                            self.stdout.write(f"   ✅ Gallery {i+1} downloaded")
                        else:
                            self.stdout.write(self.style.WARNING(f"   ⚠️ Failed to download gallery {i+1}"))
                    
                    new_gallery.append(f'tours/{image_filename}')
                
                tour.gallery = new_gallery
                tour.save()
                self.stdout.write("   ✅ Gallery images downloaded")
            
            # Download and save itinerary images
            itinerary_items = TourItinerary.objects.filter(tour=tour).order_by('order')
            self.stdout.write("   🗺️ Downloading itinerary images...")
            
            itinerary_urls = [
                "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop&crop=center",  # 1
                "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=800&h=600&fit=crop&crop=center",  # 2
                "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop&crop=center",  # 3
                "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=600&fit=crop&crop=center",  # 4
                "https://images.unsplash.com/photo-1542810634-71277d95dcbb?w=800&h=600&fit=crop&crop=center",  # 5
                "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800&h=600&fit=crop&crop=center",  # 6
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop&crop=center",  # 7
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop&crop=center",  # 8
                "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&h=600&fit=crop&crop=center",  # 9
                "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop&crop=center"   # 10
            ]
            
            for i, item in enumerate(itinerary_items):
                if i < len(itinerary_urls):
                    image_filename = f'tour-x-itinerary-{item.order}.jpg'
                    image_path = os.path.join(media_tours_dir, image_filename)
                    
                    if not os.path.exists(image_path):
                        response = requests.get(itinerary_urls[i], timeout=30)
                        if response.status_code == 200:
                            with open(image_path, 'wb') as f:
                                f.write(response.content)
                            self.stdout.write(f"   ✅ Itinerary {item.order} downloaded")
                        else:
                            self.stdout.write(self.style.WARNING(f"   ⚠️ Failed to download itinerary {item.order}"))
                    
                    item.image = f'tours/{image_filename}'
                    item.save()
            
            self.stdout.write("   ✅ Itinerary images downloaded")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error downloading images: {e}"))
            return
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 IMAGE DOWNLOAD SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write("✅ Tour X images downloaded successfully!")
        self.stdout.write("   - Main image: tours/tour-x-main.jpg")
        self.stdout.write("   - Gallery: tours/tour-x-gallery-*.jpg")
        self.stdout.write("   - Itinerary: tours/tour-x-itinerary-*.jpg")
        self.stdout.write("   - All files saved to backend/media/tours/")
        self.stdout.write("   - Frontend will now load images correctly")
        self.stdout.write(self.style.SUCCESS("\n🎯 Tour X image download complete!"))

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'download_tour_x_images'])
