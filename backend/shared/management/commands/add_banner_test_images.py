from django.core.management.base import BaseCommand
from shared.models import Banner


class Command(BaseCommand):
    help = "Add test images to banners that don't have images"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Adding test images to banners...")
        
        # Get banners without images
        banners = Banner.objects.filter(image='')
        
        if not banners.exists():
            self.stdout.write(self.style.SUCCESS("✅ All banners already have images!"))
            return
        
        self.stdout.write(f"Found {banners.count()} banners without images")
        
        # Sample image paths (you can replace these with actual images)
        sample_images = {
            'homepage_bottom': {
                'desktop': 'banners/homepage-bottom-banner.jpg',
                'mobile': 'banners/mobile/homepage-bottom-banner.jpg',
            },
            'sidebar': {
                'desktop': 'banners/sidebar-banner.jpg',
                'mobile': 'banners/mobile/sidebar-banner.jpg',
            },
        }
        
        for banner in banners:
            if banner.banner_type in sample_images:
                # Note: These are placeholder paths
                # In production, you should upload actual images through admin
                banner.image = sample_images[banner.banner_type]['desktop']
                banner.mobile_image = sample_images[banner.banner_type]['mobile']
                banner.save()
                
                self.stdout.write(f"✅ Added placeholder images to {banner.banner_type} banner")
                self.stdout.write(f"   Desktop: {banner.image}")
                self.stdout.write(f"   Mobile: {banner.mobile_image}")
            else:
                self.stdout.write(f"⚠️ No sample image defined for {banner.banner_type}")
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write("Note: Placeholder image paths have been added.")
        self.stdout.write("Please upload actual images through Django admin:")
        self.stdout.write("  1. Go to: http://localhost:8000/admin/shared/banner/")
        self.stdout.write("  2. Click on each banner")
        self.stdout.write("  3. Upload desktop and mobile images")
        self.stdout.write("  4. Save")
        self.stdout.write(self.style.SUCCESS("\n✅ Command completed!"))
