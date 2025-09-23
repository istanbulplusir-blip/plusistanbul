#!/usr/bin/env python
"""
Management command to add English description translation for Tour X
"""
from django.core.management.base import BaseCommand
from tours.models import Tour

class Command(BaseCommand):
    help = "Add English description translation for Tour X"
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Adding English description translation for Tour X...")
        
        # Find Tour X
        tour = Tour.objects.filter(slug='tour-x').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour X not found! Please create it first."))
            return
        
        self.stdout.write(f"✅ Found Tour X: {tour.title}")
        
        try:
            # Set English language and update description
            tour.set_current_language('en')
            tour.description = """
        A comprehensive cultural tour with special capacity management and diverse experiences. This tour includes visits to museums, ancient temples, traditional markets, and unique cultural experiences.
        
        Tour Features:
        • Visit to National History Museum
        • Traditional Market Experience
        • Ancient Temple Complex Visit
        • Traditional Music and Dance Performance
        • Traditional Tea Ceremony
        • Artisan Workshop
        """
            tour.save()
            
            self.stdout.write("   ✅ Updated English description")
            
            # Verify the translation
            tour.set_current_language('en')
            english_desc = tour.description
            tour.set_current_language('fa')
            persian_desc = tour.description
            
            self.stdout.write(f"   📝 English description: {english_desc[:100]}...")
            self.stdout.write(f"   📝 Persian description: {persian_desc[:100]}...")
            
            # Check if they are different
            if english_desc != persian_desc:
                self.stdout.write(self.style.SUCCESS("   ✅ Translation successful!"))
            else:
                self.stdout.write(self.style.WARNING("   ⚠️ Descriptions are the same - translation may not have worked"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error updating description: {e}"))
            return
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 DESCRIPTION TRANSLATION SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write("✅ Tour X description is now bilingual!")
        self.stdout.write("   - English: Comprehensive cultural tour description")
        self.stdout.write("   - Persian: توضیحات تور فرهنگی جامع")
        self.stdout.write("   - Frontend will display correct language based on user selection")
        self.stdout.write(self.style.SUCCESS("\n🎯 Tour X description translation complete!"))

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'update_tour_x_description_translation'])
