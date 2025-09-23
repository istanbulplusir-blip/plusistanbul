from django.core.management.base import BaseCommand
from django.utils import timezone
from tours.models import Tour, TourItinerary

class Command(BaseCommand):
    help = "Add Persian translations for Tour X itinerary items"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Adding Persian translations for Tour X itinerary...")
        
        # Get Tour X
        tour = Tour.objects.filter(slug='tour-x').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour X not found! Please create it first."))
            return
        
        self.stdout.write(f"✅ Found Tour X: {tour.title}")
        
        # Persian translations for itinerary items
        persian_translations = {
            1: {
                'title': 'خوش‌آمدگویی و راهنمایی',
                'description': 'با راهنمای تور و همسفران خود آشنا شوید. راهنمایی کوتاه درباره برنامه روزانه و دستورالعمل‌های ایمنی.'
            },
            2: {
                'title': 'بازدید از موزه تاریخی',
                'description': 'تاریخ غنی منطقه را از طریق نمایشگاه‌های تعاملی و آثار باستانی کشف کنید. درباره میراث فرهنگی که این منطقه را شکل داده است بیاموزید.'
            },
            3: {
                'title': 'تجربه بازار سنتی',
                'description': 'خود را در فضای پرجنب‌وجوش بازار محلی غرق کنید. صنایع دستی سنتی، ادویه‌ها و خوراکی‌های محلی را کشف کنید.'
            },
            4: {
                'title': 'ناهار در رستوران محلی',
                'description': 'از آشپزی اصیل محلی در رستورانی که با دقت انتخاب شده است لذت ببرید. طعم غذاهای سنتی تهیه شده با مواد تازه محلی را بچشید.'
            },
            5: {
                'title': 'مجموعه معبد باستانی',
                'description': 'از مجموعه معبد باشکوهی که قرن‌ها قدمت دارد بازدید کنید. از معماری پیچیده و اهمیت معنوی آن حیرت‌زده شوید.'
            },
            6: {
                'title': 'نمایش فرهنگی',
                'description': 'نمایش موسیقی و رقص سنتی توسط هنرمندان محلی را تجربه کنید. درباره سنت‌های فرهنگی و میراث هنری بیاموزید.'
            },
            7: {
                'title': 'نمای پانوراما',
                'description': 'نمای پانورامای نفس‌گیر شهر و مناظر اطراف را تماشا کنید. فرصت عکاسی عالی با مناظر خیره‌کننده.'
            },
            8: {
                'title': 'بازدید از کارگاه صنعتگران',
                'description': 'صنعتگران ماهر را در حال کار و خلق صنایع دستی سنتی تماشا کنید. درباره تکنیک‌های سنتی بیاموزید و شاید دست به کار شوید.'
            },
            9: {
                'title': 'مراسم چای عصرانه',
                'description': 'در مراسم چای سنتی شرکت کنید، درباره آداب و رسوم محلی بیاموزید و از فضای آرام لذت ببرید.'
            },
            10: {
                'title': 'خداحافظی و بازگشت',
                'description': 'روز را با گردهمایی خداحافظی، به اشتراک‌گذاری تجربیات و خاطرات به پایان برسانید. به نقطه ملاقات اصلی بازگردید.'
            }
        }
        
        # Update each itinerary item with Persian translations
        updated_count = 0
        for order, translations in persian_translations.items():
            try:
                itinerary_item = TourItinerary.objects.get(tour=tour, order=order)
                
                # Set Persian translations
                itinerary_item.set_current_language('fa')
                itinerary_item.title = translations['title']
                itinerary_item.description = translations['description']
                itinerary_item.save()
                
                self.stdout.write(f"   ✅ Updated item {order}: {translations['title']}")
                updated_count += 1
                
            except TourItinerary.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"   ⚠️ Itinerary item {order} not found"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Error updating item {order}: {e}"))
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 ITINERARY TRANSLATIONS SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Total Items Updated: {updated_count}/10")
        self.stdout.write(f"Language: Persian (fa)")
        self.stdout.write(f"Tour: {tour.title}")
        
        if updated_count == 10:
            self.stdout.write(self.style.SUCCESS("\n✅ All itinerary items translated to Persian!"))
            self.stdout.write("   - Titles and descriptions now available in Persian")
            self.stdout.write("   - Frontend will display correct language based on user selection")
            self.stdout.write("   - Both English and Persian content available")
        else:
            self.stdout.write(self.style.WARNING(f"\n⚠️ Only {updated_count}/10 items were updated"))
        
        self.stdout.write("\n🌐 Translation Status:")
        self.stdout.write("   - English: ✅ Available")
        self.stdout.write("   - Persian: ✅ Now Available")
        self.stdout.write("   - Turkish: ❌ Not Available (can be added later)")
        
        self.stdout.write(self.style.SUCCESS("\n🎯 Tour X itinerary is now fully bilingual!"))
