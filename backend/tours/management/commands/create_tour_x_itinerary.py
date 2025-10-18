from django.core.management.base import BaseCommand
from tours.models import Tour, TourItinerary


class Command(BaseCommand):
    help = "Create tour itinerary for Tour X with images and detailed descriptions"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating Tour X Itinerary...")
        
        # Get Tour X
        tour = Tour.objects.filter(slug='tour-x').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour X not found! Please create it first."))
            return
        
        self.stdout.write(f"✅ Found Tour X: {tour.title}")
        
        # Clear existing itinerary
        tour.itinerary.all().delete()
        self.stdout.write("🗑️ Cleared existing itinerary")
        
        # Create itinerary items
        itinerary_data = [
            {
                "order": 1,
                "title": "Welcome & Orientation",
                "description": "Meet your guide and fellow travelers. Brief orientation about the day's schedule and safety guidelines.",
                "duration_minutes": 30,
                "location": "Meeting Point - Central Plaza",
                "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 2,
                "title": "Historical Museum Visit",
                "description": "Explore the rich history of the region through interactive exhibits and ancient artifacts. Learn about the cultural heritage that shaped this area.",
                "duration_minutes": 90,
                "location": "National History Museum",
                "image": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 3,
                "title": "Traditional Market Experience",
                "description": "Immerse yourself in the vibrant local market atmosphere. Discover traditional crafts, spices, and local delicacies.",
                "duration_minutes": 60,
                "location": "Old Bazaar District",
                "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 4,
                "title": "Lunch at Local Restaurant",
                "description": "Enjoy authentic local cuisine at a carefully selected restaurant. Taste traditional dishes prepared with fresh, local ingredients.",
                "duration_minutes": 75,
                "location": "Traditional Restaurant",
                "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 5,
                "title": "Ancient Temple Complex",
                "description": "Visit the magnificent temple complex dating back centuries. Marvel at the intricate architecture and spiritual significance.",
                "duration_minutes": 120,
                "location": "Sacred Temple Complex",
                "image": "https://images.unsplash.com/photo-1542810634-71277d95dcbb?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 6,
                "title": "Cultural Performance",
                "description": "Experience traditional music and dance performances by local artists. Learn about the cultural traditions and artistic heritage.",
                "duration_minutes": 45,
                "location": "Cultural Center",
                "image": "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 7,
                "title": "Scenic Viewpoint",
                "description": "Take in breathtaking panoramic views of the city and surrounding landscape. Perfect photo opportunity with stunning vistas.",
                "duration_minutes": 30,
                "location": "Mountain Viewpoint",
                "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 8,
                "title": "Artisan Workshop Visit",
                "description": "Watch skilled artisans at work creating traditional crafts. Learn about traditional techniques and maybe try your hand at crafting.",
                "duration_minutes": 60,
                "location": "Artisan Quarter",
                "image": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 9,
                "title": "Evening Tea Ceremony",
                "description": "Participate in a traditional tea ceremony, learning about local customs and enjoying the peaceful atmosphere.",
                "duration_minutes": 45,
                "location": "Traditional Tea House",
                "image": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&h=600&fit=crop&crop=center",
            },
            {
                "order": 10,
                "title": "Farewell & Return",
                "description": "Wrap up the day with a farewell gathering, sharing experiences and memories. Return to the original meeting point.",
                "duration_minutes": 30,
                "location": "Meeting Point - Central Plaza",
                "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop&crop=center",
            },
        ]
        
        created_items = []
        for item_data in itinerary_data:
            # Create itinerary item with translatable fields
            itinerary_item, created = TourItinerary.objects.get_or_create(
                tour=tour,
                order=item_data["order"],
                defaults={
                    "duration_minutes": item_data["duration_minutes"],
                    "location": item_data["location"],
                    "image": item_data["image"],
                },
            )
            
            # Set translatable fields
            itinerary_item.set_current_language('en')
            itinerary_item.title = item_data["title"]
            itinerary_item.description = item_data["description"]
            itinerary_item.save()
            
            created_items.append(itinerary_item)
            if created:
                self.stdout.write(f"✅ Created itinerary item {item_data['order']}: {item_data['title']}")
            else:
                self.stdout.write(f"📋 Updated itinerary item {item_data['order']}: {item_data['title']}")
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📋 TOUR X ITINERARY SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Tour: {tour.title}")
        self.stdout.write(f"Total Itinerary Items: {len(created_items)}")
        self.stdout.write(f"Total Duration: {sum(item.duration_minutes for item in created_items)} minutes")
        
        self.stdout.write("\n🗺️ Itinerary Overview:")
        for item in created_items:
            self.stdout.write(f"  {item.order:2d}. {item.title} ({item.duration_minutes} min) - {item.location}")
        
        self.stdout.write("\n🎯 Itinerary Features:")
        self.stdout.write("  ✅ 10 detailed stops with images")
        self.stdout.write("  ✅ Cultural and historical focus")
        self.stdout.write("  ✅ Local experiences and interactions")
        self.stdout.write("  ✅ Balanced timing and locations")
        self.stdout.write("  ✅ High-quality Unsplash images")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Tour X itinerary created successfully!"))
