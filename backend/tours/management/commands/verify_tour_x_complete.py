from django.core.management.base import BaseCommand
from tours.models import Tour
from parler.utils.context import switch_language

class Command(BaseCommand):
    help = 'Verify Tour X data completeness'

    def handle(self, *args, **options):
        try:
            # Get Tour X
            tour = Tour.objects.get(slug='tour-x')
            
            print("=" * 80)
            print("🔍 TOUR X COMPLETE DATA VERIFICATION")
            print("=" * 80)
            
            # Check all translatable fields
            missing_fields = []
            incomplete_translations = []
            
            # Check Persian content
            tour.set_current_language('fa')
            print("\n📋 PERSIAN CONTENT:")
            print(f"Title: {tour.title}")
            print(f"Description: {'✓' if tour.description else '❌ MISSING'}")
            print(f"Short Description: {'✓' if tour.short_description else '❌ MISSING'}")
            print(f"Highlights: {'✓' if tour.highlights else '❌ MISSING'}")
            print(f"Rules: {'✓' if tour.rules else '❌ MISSING'}")
            print(f"Required Items: {'✓' if tour.required_items else '❌ MISSING'}")
            
            if not tour.description:
                missing_fields.append("Description (Persian)")
            if not tour.short_description:
                missing_fields.append("Short Description (Persian)")
            if not tour.highlights:
                missing_fields.append("Highlights (Persian)")
            if not tour.rules:
                missing_fields.append("Rules (Persian)")
            if not tour.required_items:
                missing_fields.append("Required Items (Persian)")
            
            # Check English content
            tour.set_current_language('en')
            print("\n📋 ENGLISH CONTENT:")
            print(f"Title: {tour.title}")
            print(f"Description: {'✓' if tour.description else '❌ MISSING'}")
            print(f"Short Description: {'✓' if tour.short_description else '❌ MISSING'}")
            print(f"Highlights: {'✓' if tour.highlights else '❌ MISSING'}")
            print(f"Rules: {'✓' if tour.rules else '❌ MISSING'}")
            print(f"Required Items: {'✓' if tour.required_items else '❌ MISSING'}")
            
            if not tour.description:
                missing_fields.append("Description (English)")
            if not tour.short_description:
                missing_fields.append("Short Description (English)")
            if not tour.highlights:
                missing_fields.append("Highlights (English)")
            if not tour.rules:
                missing_fields.append("Rules (English)")
            if not tour.required_items:
                missing_fields.append("Required Items (English)")
            
            # Check non-translatable fields
            print("\n⏰ TIME & BOOKING:")
            print(f"Pickup Time: {tour.pickup_time if tour.pickup_time else '❌ MISSING'}")
            print(f"Start Time: {tour.start_time if tour.start_time else '❌ MISSING'}")
            print(f"End Time: {tour.end_time if tour.end_time else '❌ MISSING'}")
            print(f"Duration Hours: {tour.duration_hours if tour.duration_hours else '❌ MISSING'}")
            print(f"Min Participants: {tour.min_participants if tour.min_participants else '❌ MISSING'}")
            print(f"Max Participants: {tour.max_participants if tour.max_participants else '❌ MISSING'}")
            print(f"Booking Cutoff: {tour.booking_cutoff_hours if tour.booking_cutoff_hours else '❌ MISSING'} hours")
            print(f"Cancellation Hours: {tour.cancellation_hours if tour.cancellation_hours else '❌ MISSING'}")
            print(f"Refund Percentage: {tour.refund_percentage if tour.refund_percentage else '❌ MISSING'}%")
            
            if not tour.pickup_time:
                missing_fields.append("Pickup Time")
            if not tour.start_time:
                missing_fields.append("Start Time")
            if not tour.end_time:
                missing_fields.append("End Time")
            if not tour.duration_hours:
                missing_fields.append("Duration Hours")
            if not tour.min_participants:
                missing_fields.append("Min Participants")
            if not tour.max_participants:
                missing_fields.append("Max Participants")
            if not tour.booking_cutoff_hours:
                missing_fields.append("Booking Cutoff Hours")
            if not tour.cancellation_hours:
                missing_fields.append("Cancellation Hours")
            if not tour.refund_percentage:
                missing_fields.append("Refund Percentage")
            
            print("\n🚌 TRANSPORT & TYPE:")
            print(f"Tour Type: {tour.tour_type if tour.tour_type else '❌ MISSING'}")
            print(f"Transport Type: {tour.transport_type if tour.transport_type else '❌ MISSING'}")
            
            if not tour.tour_type:
                missing_fields.append("Tour Type")
            if not tour.transport_type:
                missing_fields.append("Transport Type")
            
            print("\n💰 PRICING:")
            print(f"Price: ${tour.price if tour.price else '❌ MISSING'}")
            print(f"Currency: {tour.currency if tour.currency else '❌ MISSING'}")
            
            if not tour.price:
                missing_fields.append("Price")
            if not tour.currency:
                missing_fields.append("Currency")
            
            print("\n📍 LOCATION & CATEGORY:")
            print(f"Category: {tour.category.name if tour.category else '❌ MISSING'}")
            
            if not tour.category:
                missing_fields.append("Category")
            
            print("\n🖼️ MEDIA:")
            print(f"Main Image: {tour.image if tour.image else '❌ MISSING'}")
            print(f"Gallery Images: {len(tour.gallery) if tour.gallery else '❌ MISSING/EMPTY'}")
            
            if not tour.image:
                missing_fields.append("Main Image")
            if not tour.gallery or len(tour.gallery) == 0:
                missing_fields.append("Gallery Images")
            
            print("\n🏷️ FLAGS:")
            print(f"Is Featured: {'✓' if tour.is_featured else '❌'}")
            print(f"Is Popular: {'✓' if tour.is_popular else '❌'}")
            print(f"Is Active: {'✓' if tour.is_active else '❌'}")
            
            # Check related objects
            print("\n🎫 RELATED DATA:")
            variants = tour.variants.all()
            schedules = tour.schedules.all()
            itinerary = tour.itinerary.all()
            options = tour.options.all()
            reviews = tour.reviews.all()
            
            print(f"Variants: {variants.count()} {'✓' if variants.exists() else '❌'}")
            print(f"Schedules: {schedules.count()} {'✓' if schedules.exists() else '❌'}")
            print(f"Itinerary: {itinerary.count()} {'✓' if itinerary.exists() else '❌'}")
            print(f"Options: {options.count()} {'✓' if options.exists() else '❌'}")
            print(f"Reviews: {reviews.count()} {'✓' if reviews.exists() else '❌'}")
            
            if not variants.exists():
                missing_fields.append("Tour Variants")
            if not schedules.exists():
                missing_fields.append("Tour Schedules")
            if not itinerary.exists():
                missing_fields.append("Tour Itinerary")
            if not options.exists():
                missing_fields.append("Tour Options")
            if not reviews.exists():
                missing_fields.append("Tour Reviews")
            
            # Summary
            print("\n" + "=" * 80)
            print("📊 COMPLETENESS SUMMARY")
            print("=" * 80)
            
            if missing_fields:
                print(f"❌ MISSING FIELDS ({len(missing_fields)}):")
                for i, field in enumerate(missing_fields, 1):
                    print(f"  {i}. {field}")
                    
                print(f"\n📈 COMPLETENESS: {((20 - len(missing_fields)) / 20 * 100):.1f}%")
                print("\n🔧 ACTION REQUIRED:")
                print("Some fields are missing and need to be updated for complete functionality.")
            else:
                print("🎉 ALL FIELDS ARE COMPLETE!")
                print("📈 COMPLETENESS: 100%")
                print("✅ Tour X is ready for production!")
            
        except Tour.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Tour X not found!"))
            self.stdout.write("Please run: python manage.py create_tour_x")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
