#!/usr/bin/env python
"""
Management command to fix Tour X gallery image paths
"""
from django.core.management.base import BaseCommand
from tours.models import Tour

class Command(BaseCommand):
    help = "Fix Tour X gallery image paths to include /media/ prefix"
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Fixing Tour X gallery image paths...")
        
        # Find Tour X
        tour = Tour.objects.filter(slug='tour-x').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour X not found! Please create it first."))
            return
        
        self.stdout.write(f"✅ Found Tour X: {tour.title}")
        
        try:
            # Fix gallery image paths
            if tour.gallery:
                self.stdout.write("   🖼️ Fixing gallery image paths...")
                new_gallery = []
                for img in tour.gallery:
                    if img and not img.startswith('/media/'):
                        new_path = f"/media/{img}"
                        new_gallery.append(new_path)
                        self.stdout.write(f"   ✅ Fixed: {img} → {new_path}")
                    else:
                        new_gallery.append(img)
                        self.stdout.write(f"   ✅ Already correct: {img}")
                
                tour.gallery = new_gallery
                tour.save()
                self.stdout.write("   ✅ Gallery image paths fixed")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error fixing gallery paths: {e}"))
            return
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 GALLERY PATH FIX SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write("✅ Tour X gallery image paths fixed!")
        self.stdout.write("   - All gallery images now have /media/ prefix")
        self.stdout.write("   - Frontend will now load gallery images correctly")
        self.stdout.write(self.style.SUCCESS("\n🎯 Tour X gallery path fix complete!"))

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'fix_tour_x_gallery_paths'])
