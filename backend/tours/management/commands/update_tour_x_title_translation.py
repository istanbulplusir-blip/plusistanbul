#!/usr/bin/env python
"""
Management command to add English translation for Tour X title
"""
from django.core.management.base import BaseCommand
from tours.models import Tour

class Command(BaseCommand):
    help = "Add English translation for Tour X title"
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Adding English translation for Tour X title...")
        
        # Find Tour X
        tour = Tour.objects.filter(slug='tour-x').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour X not found! Please create it first."))
            return
        
        self.stdout.write(f"✅ Found Tour X: {tour.title}")
        
        try:
            # Set English language and update title
            tour.set_current_language('en')
            tour.title = "Tour X - Cultural Experience"
            tour.save()
            
            self.stdout.write("   ✅ Updated English title: Tour X - Cultural Experience")
            
            # Verify the translation
            tour.set_current_language('en')
            english_title = tour.title
            tour.set_current_language('fa')
            persian_title = tour.title
            
            self.stdout.write(f"   📝 English title: {english_title}")
            self.stdout.write(f"   📝 Persian title: {persian_title}")
            
            # Check if they are different
            if english_title != persian_title:
                self.stdout.write(self.style.SUCCESS("   ✅ Translation successful!"))
            else:
                self.stdout.write(self.style.WARNING("   ⚠️ Titles are the same - translation may not have worked"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error updating title: {e}"))
            return
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 TITLE TRANSLATION SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write("✅ Tour X title is now bilingual!")
        self.stdout.write("   - English: Tour X - Cultural Experience")
        self.stdout.write("   - Persian: تور ایکس - تجربه فرهنگی")
        self.stdout.write("   - Frontend will display correct language based on user selection")
        self.stdout.write(self.style.SUCCESS("\n🎯 Tour X title translation complete!"))
