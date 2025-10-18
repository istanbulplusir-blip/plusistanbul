from django.core.management.base import BaseCommand
from tours.models import Tour


class Command(BaseCommand):
    help = 'Verify complete adventure tour data'

    def handle(self, *args, **options):
        try:
            tour = Tour.objects.get(slug='complete-adventure-tour')
            
            print("=" * 80)
            print("🔍 COMPLETE ADVENTURE TOUR VERIFICATION")
            print("=" * 80)
            
            # Check all 3 languages
            languages = [
                ('en', 'English', '🇬🇧'),
                ('fa', 'Persian', '🇮🇷'),
                ('tr', 'Turkish', '🇹🇷')
            ]
            
            all_complete = True
            
            for lang_code, lang_name, flag in languages:
                tour.set_current_language(lang_code)
                print(f"\n{flag} {lang_name.upper()} CONTENT:")
                print("-" * 60)
                
                fields_status = {
                    'Title': bool(tour.title),
                    'Description': bool(tour.description),
                    'Short Description': bool(tour.short_description),
                    'Highlights': bool(tour.highlights),
                    'Rules': bool(tour.rules),
                    'Required Items': bool(tour.required_items),
                }
                
                for field, status in fields_status.items():
                    icon = '✅' if status else '❌'
                    print(f"  {icon} {field}")
                    if not status:
                        all_complete = False
            
            # Check non-translatable fields
            print(f"\n⚙️ GENERAL SETTINGS:")
            print("-" * 60)
            
            general_fields = {
                'Price': tour.price,
                'Currency': tour.currency,
                'Duration': tour.duration_hours,
                'Pickup Time': tour.pickup_time,
                'Start Time': tour.start_time,
                'End Time': tour.end_time,
                'Min Participants': tour.min_participants,
                'Max Participants': tour.max_participants,
                'Booking Cutoff': tour.booking_cutoff_hours,
                'Cancellation Hours': tour.cancellation_hours,
                'Refund Percentage': tour.refund_percentage,
                'Tour Type': tour.tour_type,
                'Transport Type': tour.transport_type,
                'Category': tour.category,
                'City': tour.city,
                'Country': tour.country,
            }
            
            for field, value in general_fields.items():
                icon = '✅' if value else '❌'
                print(f"  {icon} {field}: {value if value else 'MISSING'}")
                if not value:
                    all_complete = False
            
            # Check flags
            print(f"\n🏷️ STATUS FLAGS:")
            print("-" * 60)
            print(f"  {'✅' if tour.is_active else '❌'} Active")
            print(f"  {'✅' if tour.is_featured else '❌'} Featured")
            print(f"  {'✅' if tour.is_popular else '❌'} Popular")
            
            # Check related data
            print(f"\n📦 RELATED DATA:")
            print("-" * 60)
            
            variants = tour.variants.all()
            schedules = tour.schedules.all()
            itinerary = tour.itinerary.all()
            options = tour.options.all()
            reviews = tour.reviews.all()
            policies = tour.cancellation_policies.all()
            
            related_data = {
                'Variants': variants.count(),
                'Schedules': schedules.count(),
                'Itinerary Items': itinerary.count(),
                'Options': options.count(),
                'Reviews': reviews.count(),
                'Cancellation Policies': policies.count(),
            }
            
            for name, count in related_data.items():
                icon = '✅' if count > 0 else '❌'
                print(f"  {icon} {name}: {count}")
                if count == 0:
                    all_complete = False
            
            # Check itinerary translations
            print(f"\n🗺️ ITINERARY TRANSLATIONS:")
            print("-" * 60)
            
            for lang_code, lang_name, flag in languages:
                complete_items = 0
                for item in itinerary:
                    item.set_current_language(lang_code)
                    if item.title and item.description:
                        complete_items += 1
                
                icon = '✅' if complete_items == itinerary.count() else '❌'
                print(f"  {icon} {flag} {lang_name}: {complete_items}/{itinerary.count()} items")
                if complete_items != itinerary.count():
                    all_complete = False
            
            # Calculate completeness percentage
            print("\n" + "=" * 80)
            print("📊 SUMMARY")
            print("=" * 80)
            
            if all_complete:
                print("🎉 TOUR IS 100% COMPLETE!")
                print("✅ All fields filled in all 3 languages")
                print("✅ All related data present")
                print("✅ Ready for production!")
            else:
                print("⚠️ TOUR HAS MISSING DATA")
                print("Please review the items marked with ❌ above")
            
            # Stats
            print(f"\n📈 STATISTICS:")
            print(f"  Languages: 3 (English, Persian, Turkish)")
            print(f"  Variants: {variants.count()}")
            print(f"  Schedules: {schedules.count()}")
            print(f"  Itinerary Items: {itinerary.count()}")
            print(f"  Options: {options.count()}")
            print(f"  Reviews: {reviews.count()}")
            print(f"  Average Rating: {tour.average_rating:.1f}⭐" if reviews.exists() else "  No ratings yet")
            print(f"  Cancellation Policies: {policies.count()}")
            
        except Tour.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Complete adventure tour not found!"))
            self.stdout.write("Please run: python manage.py create_complete_tour")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
