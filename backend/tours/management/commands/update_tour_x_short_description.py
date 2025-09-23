from django.core.management.base import BaseCommand
from tours.models import Tour

class Command(BaseCommand):
    help = 'Update Tour X English short description'

    def handle(self, *args, **options):
        try:
            # Get Tour X
            tour = Tour.objects.get(slug='tour-x')
            self.stdout.write(f"Found Tour X: {tour.title}")
            
            # Update English short description
            tour.set_current_language('en')
            if not tour.short_description:
                tour.short_description = """Experience the rich cultural heritage of Tehran in this comprehensive 8-hour tour. Visit the National Museum, explore traditional bazaars, enjoy authentic Persian cuisine, and witness cultural performances. Perfect for culture enthusiasts and history lovers seeking an immersive Iranian experience."""
                tour.save()
                self.stdout.write("✅ Added English short description")
            else:
                self.stdout.write("✓ English short description already exists")
            
            # Verify both languages
            tour.set_current_language('fa')
            self.stdout.write(f"Persian Short Description: {'✓' if tour.short_description else '❌'}")
            
            tour.set_current_language('en')
            self.stdout.write(f"English Short Description: {'✓' if tour.short_description else '❌'}")
            
            self.stdout.write("🎉 Tour X short description updated successfully!")
            
        except Tour.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Tour X not found!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
