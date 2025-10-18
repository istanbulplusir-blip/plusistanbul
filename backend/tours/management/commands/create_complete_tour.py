from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time
from decimal import Decimal

from tours.models import (
    Tour, TourVariant, TourSchedule, TourOption, 
    TourCategory, TourItinerary, TourCancellationPolicy
)


class Command(BaseCommand):
    help = "Create a complete 3-language tour with all features"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating complete 3-language tour...")
        
        # Create or get category
        category, _ = TourCategory.objects.get_or_create(
            slug="adventure",
            defaults={"name": "Adventure Tours"}
        )
        
        # Set category translations
        category.set_current_language('en')
        category.name = "Adventure Tours"
        category.description = "Exciting adventure tours for thrill seekers"
        category.save()
        
        category.set_current_language('fa')
        category.name = "تورهای ماجراجویی"
        category.description = "تورهای ماجراجویانه هیجان‌انگیز برای علاقه‌مندان"
        category.save()
        
        category.set_current_language('tr')
        category.name = "Macera Turları"
        category.description = "Heyecan arayanlar için heyecan verici macera turları"
        category.save()
        
        # Create tour
        tour, created = Tour.objects.get_or_create(
            slug="complete-adventure-tour",
            defaults={
                "price": Decimal('200.00'),
                "currency": "USD",
                "duration_hours": 10,
                "pickup_time": time(7, 30),
                "start_time": time(8, 0),
                "end_time": time(18, 0),
                "min_participants": 4,
                "max_participants": 40,
                "booking_cutoff_hours": 48,
                "cancellation_hours": 72,
                "refund_percentage": 90,
                "includes_transfer": True,
                "includes_guide": True,
                "includes_meal": True,
                "includes_photographer": True,
                "tour_type": "day",
                "transport_type": "land",
                "is_active": True,
                "is_featured": True,
                "is_popular": True,
                "city": "Tehran",
                "country": "Iran",
                "category": category,
            }
        )
        
        # English content
        tour.set_current_language('en')
        tour.title = "Complete Adventure Tour - Mountain & Nature"
        tour.description = """
Experience an unforgettable adventure in the stunning mountains and pristine nature. 
This comprehensive tour includes hiking, nature photography, traditional meals, and 
cultural experiences with local communities.

Perfect for adventure enthusiasts and nature lovers seeking an authentic experience 
in Iran's beautiful landscapes. Our expert guides ensure your safety while providing 
deep insights into the region's ecology and culture.
"""
        tour.short_description = "An exciting 10-hour adventure tour combining mountain hiking, nature exploration, and cultural experiences with local communities."
        tour.highlights = """✨ Tour Highlights:

🏔️ Mountain hiking with breathtaking views
🌲 Pristine nature exploration
📸 Professional photography opportunities
🍽️ Traditional local cuisine
👥 Meet local communities
🚌 Comfortable transportation
🎒 Small group experience (max 40)
🧗 Adventure activities
🌄 Sunrise/sunset viewing
🏕️ Nature camping experience"""
        
        tour.rules = """📋 Tour Rules:

🕘 Arrive 30 minutes before departure
👟 Wear proper hiking shoes
🎒 Bring personal backpack
💧 Carry sufficient water
📱 Keep phone charged
🚭 No smoking in natural areas
📷 Respect photography restrictions
👥 Stay with the group
⏰ Follow the schedule
🌿 Protect the environment"""
        
        tour.required_items = """🎒 Required Items:

👟 Hiking boots
🧥 Weather-appropriate clothing
🧢 Hat and sunglasses
🧴 Sunscreen (SPF 30+)
💧 Water bottle (2L minimum)
🎒 Day backpack
📱 Mobile phone + power bank
📷 Camera (optional)
🩹 Personal medications
🍫 Energy snacks
🧤 Gloves (seasonal)
🌂 Rain jacket"""
        tour.save()
        
        # Persian content
        tour.set_current_language('fa')
        tour.title = "تور ماجراجویی کامل - کوه و طبیعت"
        tour.description = """
یک ماجراجویی فراموش‌نشدنی در کوه‌های خیره‌کننده و طبیعت بکر تجربه کنید.
این تور جامع شامل کوهنوردی، عکاسی از طبیعت، غذاهای سنتی و تجربیات 
فرهنگی با جوامع محلی است.

مناسب برای علاقه‌مندان به ماجراجویی و عاشقان طبیعت که به دنبال تجربه‌ای 
اصیل در مناظر زیبای ایران هستند. راهنمایان متخصص ما ایمنی شما را تضمین 
می‌کنند و در عین حال بینش عمیقی از اکولوژی و فرهنگ منطقه ارائه می‌دهند.
"""
        tour.short_description = "یک تور ماجراجویانه ۱۰ ساعته هیجان‌انگیز که کوهنوردی، کاوش طبیعت و تجربیات فرهنگی با جوامع محلی را ترکیب می‌کند."
        tour.highlights = """✨ نکات برجسته تور:

🏔️ کوهنوردی با مناظر خیره‌کننده
🌲 کاوش طبیعت بکر
📸 فرصت‌های عکاسی حرفه‌ای
🍽️ غذاهای سنتی محلی
👥 ملاقات با جوامع محلی
🚌 حمل و نقل راحت
🎒 تجربه گروه کوچک (حداکثر ۴۰ نفر)
🧗 فعالیت‌های ماجراجویانه
🌄 تماشای طلوع/غروب خورشید
🏕️ تجربه کمپینگ در طبیعت"""
        
        tour.rules = """📋 قوانین تور:

🕘 ۳۰ دقیقه قبل از حرکت حاضر شوید
👟 کفش کوهنوردی مناسب بپوشید
🎒 کوله‌پشتی شخصی همراه داشته باشید
💧 آب کافی حمل کنید
📱 تلفن خود را شارژ نگه دارید
🚭 در مناطق طبیعی سیگار نکشید
📷 محدودیت‌های عکاسی را رعایت کنید
👥 با گروه بمانید
⏰ برنامه زمانی را دنبال کنید
🌿 از محیط زیست محافظت کنید"""
        
        tour.required_items = """🎒 وسایل ضروری:

👟 کفش کوهنوردی
🧥 لباس مناسب آب و هوا
🧢 کلاه و عینک آفتابی
🧴 کرم ضد آفتاب (SPF 30+)
💧 بطری آب (حداقل ۲ لیتر)
🎒 کوله‌پشتی روزانه
📱 تلفن همراه + پاوربانک
📷 دوربین (اختیاری)
🩹 داروهای شخصی
🍫 تنقلات انرژی‌زا
🧤 دستکش (فصلی)
🌂 بارانی"""
        tour.save()
        
        # Turkish content
        tour.set_current_language('tr')
        tour.title = "Komple Macera Turu - Dağ ve Doğa"
        tour.description = """
Muhteşem dağlarda ve el değmemiş doğada unutulmaz bir macera yaşayın.
Bu kapsamlı tur, yürüyüş, doğa fotoğrafçılığı, geleneksel yemekler ve 
yerel topluluklarla kültürel deneyimleri içerir.

İran'ın güzel manzaralarında özgün bir deneyim arayan macera tutkunları 
ve doğa severler için mükemmel. Uzman rehberlerimiz güvenliğinizi sağlarken 
bölgenin ekolojisi ve kültürü hakkında derin bilgiler sunar.
"""
        tour.short_description = "Dağ yürüyüşü, doğa keşfi ve yerel topluluklarla kültürel deneyimleri birleştiren heyecan verici 10 saatlik macera turu."
        tour.highlights = """✨ Tur Öne Çıkanları:

🏔️ Nefes kesen manzaralı dağ yürüyüşü
🌲 El değmemiş doğa keşfi
📸 Profesyonel fotoğraf fırsatları
🍽️ Geleneksel yerel mutfak
👥 Yerel topluluklarla tanışma
🚌 Konforlu ulaşım
🎒 Küçük grup deneyimi (maks 40)
🧗 Macera aktiviteleri
🌄 Gün doğumu/batımı izleme
🏕️ Doğada kamp deneyimi"""
        
        tour.rules = """📋 Tur Kuralları:

🕘 Kalkıştan 30 dakika önce gelin
👟 Uygun yürüyüş ayakkabısı giyin
🎒 Kişisel sırt çantası getirin
💧 Yeterli su taşıyın
📱 Telefonunuzu şarjlı tutun
🚭 Doğal alanlarda sigara içmeyin
📷 Fotoğraf kısıtlamalarına uyun
👥 Grupla kalın
⏰ Programı takip edin
🌿 Çevreyi koruyun"""
        
        tour.required_items = """🎒 Gerekli Eşyalar:

👟 Yürüyüş botları
🧥 Hava koşullarına uygun giysi
🧢 Şapka ve güneş gözlüğü
🧴 Güneş kremi (SPF 30+)
💧 Su şişesi (min 2L)
🎒 Günlük sırt çantası
📱 Cep telefonu + powerbank
📷 Kamera (isteğe bağlı)
🩹 Kişisel ilaçlar
🍫 Enerji atıştırmalıkları
🧤 Eldiven (mevsimsel)
🌂 Yağmurluk"""
        tour.save()
        
        self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} tour: {tour.slug}")
        
        # Create variants
        variants_data = [
            ("STANDARD", Decimal('200.00'), 15, "Standard package with basic services"),
            ("PREMIUM", Decimal('280.00'), 15, "Premium package with enhanced services"),
            ("VIP", Decimal('350.00'), 10, "VIP package with exclusive services"),
        ]
        
        for name, price, capacity, desc in variants_data:
            variant, created = TourVariant.objects.get_or_create(
                tour=tour,
                name=name,
                defaults={
                    "description": desc,
                    "base_price": price,
                    "capacity": capacity,
                    "is_active": True,
                    "includes_transfer": True,
                    "includes_guide": True,
                    "includes_meal": True,
                    "includes_photographer": name in ["PREMIUM", "VIP"],
                    "extended_hours": 0 if name == "STANDARD" else 2,
                    "private_transfer": name == "VIP",
                    "expert_guide": name in ["PREMIUM", "VIP"],
                    "special_meal": name == "VIP",
                }
            )
            self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} variant: {name}")
        
        # Create schedules for next 7 days
        base_date = timezone.now().date()
        for i in range(7):
            schedule_date = base_date + timezone.timedelta(days=i)
            schedule, created = TourSchedule.objects.get_or_create(
                tour=tour,
                start_date=schedule_date,
                defaults={
                    "end_date": schedule_date,
                    "start_time": time(8, 0),
                    "end_time": time(18, 0),
                    "is_available": True,
                    "day_of_week": schedule_date.weekday(),
                }
            )
            schedule.initialize_variant_capacities()
            if created:
                self.stdout.write(f"✅ Created schedule: {schedule_date}")
        
        # Create options
        options_data = [
            ("Professional Photography", "Professional photographer for the entire tour", 
             Decimal('40.00'), "equipment"),
            ("Lunch Upgrade", "Premium lunch with special menu", 
             Decimal('20.00'), "food"),
            ("Private Guide", "Exclusive private guide for your group", 
             Decimal('60.00'), "service"),
            ("Equipment Rental", "Complete hiking equipment rental", 
             Decimal('30.00'), "equipment"),
        ]
        
        for name, desc, price, opt_type in options_data:
            option, created = TourOption.objects.get_or_create(
                tour=tour,
                name=name,
                defaults={
                    "description": desc,
                    "price": price,
                    "currency": "USD",
                    "option_type": opt_type,
                    "is_available": True,
                    "max_quantity": 5,
                }
            )
            self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} option: {name}")
        
        # Create itinerary (will add translations next)
        self._create_itinerary(tour)
        
        # Create cancellation policies
        self._create_cancellation_policies(tour)
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 COMPLETE TOUR SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Tour: {tour.slug}")
        self.stdout.write(f"Languages: English, Persian, Turkish")
        self.stdout.write(f"Variants: {tour.variants.count()}")
        self.stdout.write(f"Schedules: {tour.schedules.count()}")
        self.stdout.write(f"Options: {tour.options.count()}")
        self.stdout.write(f"Itinerary Items: {tour.itinerary.count()}")
        self.stdout.write(f"Cancellation Policies: {tour.cancellation_policies.count()}")
        self.stdout.write(self.style.SUCCESS("\n✅ Complete 3-language tour created successfully!"))
    
    def _create_itinerary(self, tour):
        """Create itinerary items with 3-language support"""
        itinerary_data = [
            {
                "order": 1,
                "duration": 30,
                "location": "Meeting Point",
                "en": {"title": "Welcome & Briefing", 
                       "desc": "Meet your guide and group. Safety briefing and equipment check."},
                "fa": {"title": "خوش‌آمدگویی و توجیه", 
                       "desc": "ملاقات با راهنما و گروه. توجیه ایمنی و بررسی تجهیزات."},
                "tr": {"title": "Karşılama ve Brifing", 
                       "desc": "Rehberiniz ve grubunuzla tanışın. Güvenlik brifingi ve ekipman kontrolü."}
            },
            {
                "order": 2,
                "duration": 90,
                "location": "Mountain Trail",
                "en": {"title": "Mountain Hiking", 
                       "desc": "Begin the exciting mountain hike with stunning views."},
                "fa": {"title": "کوهنوردی", 
                       "desc": "شروع کوهنوردی هیجان‌انگیز با مناظر خیره‌کننده."},
                "tr": {"title": "Dağ Yürüyüşü", 
                       "desc": "Muhteşem manzaralarla heyecan verici dağ yürüyüşüne başlayın."}
            },
            {
                "order": 3,
                "duration": 60,
                "location": "Summit",
                "en": {"title": "Summit & Photography", 
                       "desc": "Reach the summit and enjoy panoramic views. Professional photography session."},
                "fa": {"title": "قله و عکاسی", 
                       "desc": "رسیدن به قله و لذت بردن از مناظر پانوراما. جلسه عکاسی حرفه‌ای."},
                "tr": {"title": "Zirve ve Fotoğrafçılık", 
                       "desc": "Zirveye ulaşın ve panoramik manzaraların tadını çıkarın. Profesyonel fotoğraf çekimi."}
            },
            {
                "order": 4,
                "duration": 75,
                "location": "Local Village",
                "en": {"title": "Traditional Lunch", 
                       "desc": "Enjoy authentic local cuisine in a traditional village setting."},
                "fa": {"title": "ناهار سنتی", 
                       "desc": "لذت بردن از غذای محلی اصیل در محیط روستای سنتی."},
                "tr": {"title": "Geleneksel Öğle Yemeği", 
                       "desc": "Geleneksel köy ortamında otantik yerel mutfağın tadını çıkarın."}
            },
            {
                "order": 5,
                "duration": 60,
                "location": "Nature Reserve",
                "en": {"title": "Nature Exploration", 
                       "desc": "Explore pristine nature and learn about local ecology."},
                "fa": {"title": "کاوش طبیعت", 
                       "desc": "کاوش طبیعت بکر و یادگیری درباره اکولوژی محلی."},
                "tr": {"title": "Doğa Keşfi", 
                       "desc": "El değmemiş doğayı keşfedin ve yerel ekoloji hakkında bilgi edinin."}
            },
            {
                "order": 6,
                "duration": 45,
                "location": "Cultural Center",
                "en": {"title": "Cultural Experience", 
                       "desc": "Meet local community and experience traditional culture."},
                "fa": {"title": "تجربه فرهنگی", 
                       "desc": "ملاقات با جامعه محلی و تجربه فرهنگ سنتی."},
                "tr": {"title": "Kültürel Deneyim", 
                       "desc": "Yerel toplulukla tanışın ve geleneksel kültürü deneyimleyin."}
            },
            {
                "order": 7,
                "duration": 30,
                "location": "Viewpoint",
                "en": {"title": "Sunset Viewing", 
                       "desc": "Watch the spectacular sunset from the best viewpoint."},
                "fa": {"title": "تماشای غروب", 
                       "desc": "تماشای غروب خورشید دیدنی از بهترین نقطه دید."},
                "tr": {"title": "Gün Batımı İzleme", 
                       "desc": "En iyi noktadan muhteşem gün batımını izleyin."}
            },
            {
                "order": 8,
                "duration": 30,
                "location": "Meeting Point",
                "en": {"title": "Return & Farewell", 
                       "desc": "Return to meeting point and share experiences."},
                "fa": {"title": "بازگشت و خداحافظی", 
                       "desc": "بازگشت به نقطه ملاقات و به اشتراک‌گذاری تجربیات."},
                "tr": {"title": "Dönüş ve Veda", 
                       "desc": "Buluşma noktasına dönün ve deneyimlerinizi paylaşın."}
            }
        ]
        
        for item_data in itinerary_data:
            item, created = TourItinerary.objects.get_or_create(
                tour=tour,
                order=item_data["order"],
                defaults={
                    "duration_minutes": item_data["duration"],
                    "location": item_data["location"],
                }
            )
            
            # Set English
            item.set_current_language('en')
            item.title = item_data["en"]["title"]
            item.description = item_data["en"]["desc"]
            item.save()
            
            # Set Persian
            item.set_current_language('fa')
            item.title = item_data["fa"]["title"]
            item.description = item_data["fa"]["desc"]
            item.save()
            
            # Set Turkish
            item.set_current_language('tr')
            item.title = item_data["tr"]["title"]
            item.description = item_data["tr"]["desc"]
            item.save()
            
            if created:
                self.stdout.write(f"✅ Created itinerary item {item_data['order']}")
    
    def _create_cancellation_policies(self, tour):
        """Create cancellation policies"""
        policies_data = [
            (72, 90, "90% refund up to 72 hours before tour start"),
            (48, 70, "70% refund up to 48 hours before tour start"),
            (24, 50, "50% refund up to 24 hours before tour start"),
            (12, 25, "25% refund up to 12 hours before tour start"),
            (0, 0, "No refund less than 12 hours before tour start"),
        ]
        
        for hours, refund, desc in policies_data:
            policy, created = TourCancellationPolicy.objects.get_or_create(
                tour=tour,
                hours_before=hours,
                defaults={
                    "refund_percentage": refund,
                    "description": desc,
                    "is_active": True,
                }
            )
            if created:
                self.stdout.write(f"✅ Created policy: {hours}h - {refund}%")
