from django.core.management.base import BaseCommand
from tours.models import Tour
from parler.utils.context import switch_language

class Command(BaseCommand):
    help = 'Update missing data for Tour X'

    def handle(self, *args, **options):
        try:
            # Get Tour X
            tour = Tour.objects.get(slug='tour-x')
            self.stdout.write(f"Found Tour X: {tour.title}")
            
            # Update highlights in Persian
            tour.set_current_language('fa')
            if not tour.highlights:
                tour.highlights = """✨ نکات برجسته تور فرهنگی تهران:

🏛️ بازدید از موزه ملی ایران با راهنمای متخصص
🛒 تجربه خرید در بازار سنتی و صنایع دستی
🍽️ صرف ناهار در رستوران محلی با غذاهای ایرانی
⛩️ بازدید از مجموعه معبد باستانی و آثار تاریخی
🎭 تماشای اجرای فرهنگی سنتی
🏔️ منظره‌ای فوق‌العاده از نقطه دید کوهستانی
🎨 آشنایی با کارگاه صنایع دستی و هنرمندان محلی
🫖 مراسم چای سنتی در چایخانه کهن
📸 عکس‌های حرفه‌ای از لحظات مهم سفر
🚌 سرویس حمل و نقل راحت در سراسر شهر"""
                self.stdout.write("✅ Added Persian highlights")
            
            # Update highlights in English
            tour.set_current_language('en')
            tour.highlights = """✨ Cultural Tehran Tour Highlights:

🏛️ Guided visit to Iran National Museum with expert guide
🛒 Traditional bazaar shopping experience and handicrafts
🍽️ Lunch at local restaurant with authentic Iranian cuisine
⛩️ Ancient temple complex visit with historical artifacts
🎭 Traditional cultural performance viewing
🏔️ Spectacular mountain viewpoint panorama
🎨 Artisan workshop visit and meet local craftsmen
🫖 Traditional tea ceremony in historic tea house
📸 Professional photography of memorable moments
🚌 Comfortable transportation throughout the city"""
            tour.save()
            self.stdout.write("✅ Added English highlights")
            
            # Update rules in Persian
            tour.set_current_language('fa')
            if not tour.rules:
                tour.rules = """📋 قوانین و مقررات تور:

🕘 لطفاً 15 دقیقه قبل از زمان تعیین شده در محل ملاقات حاضر شوید
👔 لباس راحت و کفش مناسب برای پیاده‌روی بپوشید
📱 تلفن همراه خود را شارژ کامل نگه دارید
🚭 استعمال دخانیات در اتوبوس و اماکن مقدس ممنوع است
📷 عکاسی در برخی نقاط ممکن است محدود باشد
🍽️ در صورت حساسیت غذایی حتماً اطلاع دهید
👥 از گروه جدا نشوید و دستورات راهنما را رعایت کنید
🎒 وسایل شخصی خود را همیشه همراه داشته باشید
⏰ برنامه زمانی را رعایت کنید تا از تجربه کامل لذت ببرید
🚫 آوردن مواد غذایی از خارج و نوشیدنی‌های الکلی ممنوع است"""
                self.stdout.write("✅ Added Persian rules")
            
            # Update rules in English
            tour.set_current_language('en')
            tour.rules = """📋 Tour Rules & Regulations:

🕘 Please arrive 15 minutes before scheduled departure time
👔 Wear comfortable clothing and suitable walking shoes
📱 Keep your mobile phone fully charged
🚭 Smoking is prohibited on the bus and in sacred places
📷 Photography may be restricted at certain locations
🍽️ Please inform us of any food allergies or dietary restrictions
👥 Stay with the group and follow guide instructions
🎒 Keep your personal belongings with you at all times
⏰ Respect the schedule to enjoy the complete experience
🚫 Outside food and alcoholic beverages are not permitted"""
            tour.save()
            self.stdout.write("✅ Added English rules")
            
            # Update required items in Persian
            tour.set_current_language('fa')
            if not tour.required_items:
                tour.required_items = """🎒 موارد ضروری برای همراه داشتن:

📄 مدارک شناسایی معتبر (کارت ملی یا پاسپورت)
💧 بطری آب شخصی
🧴 کرم ضد آفتاب و کلاه آفتابی
👟 کفش راحت و مناسب برای پیاده‌روی
📱 تلفن همراه با شارژ کامل
💳 پول نقد یا کارت برای خریدهای شخصی
🧥 لباس گرم (بسته به آب و هوا)
📷 دوربین یا تلفن همراه برای عکاسی
🩹 داروهای شخصی در صورت نیاز
🎒 کیف کوچک برای حمل وسایل شخصی
🕶️ عینک آفتابی
🧻 دستمال کاغذی"""
                self.stdout.write("✅ Added Persian required items")
            
            # Update required items in English
            tour.set_current_language('en')
            tour.required_items = """🎒 Essential Items to Bring:

📄 Valid identification documents (ID card or passport)
💧 Personal water bottle
🧴 Sunscreen and sun hat
👟 Comfortable walking shoes
📱 Mobile phone with full charge
💳 Cash or card for personal purchases
🧥 Warm clothing (weather dependent)
📷 Camera or phone for photography
🩹 Personal medications if needed
🎒 Small bag for personal items
🕶️ Sunglasses
🧻 Tissues"""
            tour.save()
            self.stdout.write("✅ Added English required items")
            
            # Check and update other missing fields
            tour.set_current_language('fa')
            
            # Update pickup time if missing
            if not tour.pickup_time:
                tour.pickup_time = "08:00:00"
                self.stdout.write("✅ Added pickup time: 08:00")
            
            # Update start time if missing
            if not tour.start_time:
                tour.start_time = "08:30:00"
                self.stdout.write("✅ Added start time: 08:30")
            
            # Update end time if missing
            if not tour.end_time:
                tour.end_time = "18:00:00"
                self.stdout.write("✅ Added end time: 18:00")
            
            # Update min participants if missing
            if not tour.min_participants:
                tour.min_participants = 5
                self.stdout.write("✅ Added min participants: 5")
            
            # Update booking cutoff if missing
            if not tour.booking_cutoff_hours:
                tour.booking_cutoff_hours = 24
                self.stdout.write("✅ Added booking cutoff: 24 hours")
            
            tour.save()
            
            # Final verification
            self.stdout.write("\n" + "="*50)
            self.stdout.write("🔍 VERIFICATION RESULTS:")
            self.stdout.write("="*50)
            
            tour.set_current_language('fa')
            self.stdout.write(f"✅ Highlights (Persian): {'✓' if tour.highlights else '❌'}")
            tour.set_current_language('en')
            self.stdout.write(f"✅ Highlights (English): {'✓' if tour.highlights else '❌'}")
            
            tour.set_current_language('fa')
            self.stdout.write(f"✅ Rules (Persian): {'✓' if tour.rules else '❌'}")
            tour.set_current_language('en')
            self.stdout.write(f"✅ Rules (English): {'✓' if tour.rules else '❌'}")
            
            tour.set_current_language('fa')
            self.stdout.write(f"✅ Required Items (Persian): {'✓' if tour.required_items else '❌'}")
            tour.set_current_language('en')
            self.stdout.write(f"✅ Required Items (English): {'✓' if tour.required_items else '❌'}")
            
            self.stdout.write(f"✅ Pickup Time: {'✓' if tour.pickup_time else '❌'}")
            self.stdout.write(f"✅ Start Time: {'✓' if tour.start_time else '❌'}")
            self.stdout.write(f"✅ End Time: {'✓' if tour.end_time else '❌'}")
            self.stdout.write(f"✅ Min Participants: {'✓' if tour.min_participants else '❌'}")
            self.stdout.write(f"✅ Max Participants: {'✓' if tour.max_participants else '❌'}")
            self.stdout.write(f"✅ Booking Cutoff: {'✓' if tour.booking_cutoff_hours else '❌'}")
            self.stdout.write(f"✅ Cancellation Hours: {'✓' if tour.cancellation_hours else '❌'}")
            self.stdout.write(f"✅ Refund Percentage: {'✓' if tour.refund_percentage else '❌'}")
            self.stdout.write(f"✅ Tour Type: {'✓' if tour.tour_type else '❌'}")
            self.stdout.write(f"✅ Transport Type: {'✓' if tour.transport_type else '❌'}")
            
            self.stdout.write("\n🎉 Tour X missing data has been updated successfully!")
            
        except Tour.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Tour X not found!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
