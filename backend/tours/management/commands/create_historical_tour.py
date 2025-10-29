from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from decimal import Decimal

from tours.models import (
    Tour, TourVariant, TourSchedule, TourOption, 
    TourCategory, TourItinerary, TourCancellationPolicy
)


class Command(BaseCommand):
    help = "Create Istanbul Historical Tour with complete details"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating Istanbul Historical Tour...")
        
        # Create or get category
        category, _ = TourCategory.objects.get_or_create(
            slug="historical-tours",
            defaults={"name": "Historical Tours"}
        )
        
        # Set category translations
        for lang_code, name, desc in [
            ('en', 'Historical Tours', 'Explore Istanbul\'s rich history'),
            ('tr', 'Tarihi Turlar', 'İstanbul\'un zengin tarihini keşfedin'),
            ('fa', 'تورهای تاریخی', 'تاریخ غنی استانبول را کشف کنید')
        ]:
            category.set_current_language(lang_code)
            category.name = name
            category.description = desc
            category.save()
        
        # Create tour
        tour, created = Tour.objects.get_or_create(
            slug="istanbul-historical-tour",
            defaults={
                "price": Decimal('30.00'),
                "currency": "USD",
                "duration_hours": 8,
                "pickup_time": time(9, 0),
                "start_time": time(9, 30),
                "end_time": time(17, 30),
                "min_participants": 1,
                "max_participants": 30,
                "booking_cutoff_hours": 24,
                "cancellation_hours": 48,
                "refund_percentage": 80,
                "includes_transfer": True,
                "includes_guide": True,
                "includes_meal": True,
                "includes_photographer": False,
                "tour_type": "day",
                "transport_type": "land",
                "is_active": True,
                "is_featured": True,
                "is_popular": True,
                "city": "Istanbul",
                "country": "Turkey",
                "category": category,
            }
        )
        
        # English content
        tour.set_current_language('en')
        tour.title = "Istanbul Historical Tour - Mosques & Balat"
        tour.description = """
Discover Istanbul's magnificent Islamic heritage and colorful neighborhoods on this comprehensive historical tour. 
Visit the iconic Blue Mosque (Sultan Ahmed Mosque), explore the grand Suleymaniye Mosque complex with its 
courtyards, tombs, and stunning terrace overlooking the Bosphorus.

Wander through the vibrant Balat neighborhood, famous for its colorful houses and as a filming location for 
the popular Turkish series Çukur. Experience authentic Istanbul culture, architecture, and history while 
enjoying a delicious lunch at a modern shopping center.

Perfect for history enthusiasts, architecture lovers, and those seeking to understand Istanbul's rich Ottoman 
and Byzantine heritage. Our expert guides bring centuries of history to life with fascinating stories and insights.
"""
        tour.short_description = "Visit Sultan Ahmed & Suleymaniye Mosques, explore colorful Balat neighborhood with Çukur locations, lunch at shopping center."
        
        tour.highlights = """✨ Tour Highlights:

🕌 Sultan Ahmed Mosque (Blue Mosque)
🏛️ Suleymaniye Mosque complex
🎨 Colorful Balat neighborhood
📺 Çukur TV series filming locations
🏰 Ottoman architecture
🌅 Bosphorus terrace views
🍽️ Lunch at shopping center
📸 Instagram-worthy photo spots
🎭 Local culture experience
👥 Small group (max 30)
🗣️ Expert historical guide
🚌 Comfortable transportation"""
        
        tour.rules = """📋 Tour Rules:

🕘 Arrive 30 minutes before departure
🎫 Bring printed or digital ticket
👗 Dress modestly for mosques
🧕 Women: headscarf for mosque visits
👞 Remove shoes at mosque entrances
📱 Keep phone on silent in mosques
📷 Photography allowed (no flash in mosques)
👥 Stay with the group
⏰ Follow the schedule
🙏 Respect religious sites
🚫 No eating/drinking in mosques
🤫 Keep quiet during prayers"""
        
        tour.required_items = """🎒 What to Bring:

🎫 Tour confirmation/ticket
🆔 Valid ID or passport
👟 Comfortable walking shoes
🧕 Headscarf (women - for mosques)
🧥 Light jacket or cardigan
🧢 Hat and sunglasses
🧴 Sunscreen (SPF 30+)
💧 Water bottle
📱 Mobile phone + charger
📷 Camera for photos
💰 Cash for souvenirs
🩹 Personal medications
🎒 Small backpack
🌂 Umbrella (seasonal)"""
        tour.save()
        
        # Turkish content
        tour.set_current_language('tr')
        tour.title = "İstanbul Tarihi Turu - Camiler ve Balat"
        tour.description = """
Bu kapsamlı tarihi turda İstanbul'un muhteşem İslami mirasını ve renkli mahallelerini keşfedin. 
İkonik Mavi Cami'yi (Sultan Ahmet Camii) ziyaret edin, avluları, türbeleri ve Boğaz'a bakan 
muhteşem terasıyla büyük Süleymaniye Camii kompleksini keşfedin.

Renkli evleriyle ve popüler Türk dizisi Çukur'un çekim lokasyonu olmasıyla ünlü canlı Balat 
semtinde gezinin. Modern bir alışveriş merkezinde lezzetli bir öğle yemeğinin tadını çıkarırken 
otantik İstanbul kültürünü, mimarisini ve tarihini deneyimleyin.

Tarih meraklıları, mimari severler ve İstanbul'un zengin Osmanlı ve Bizans mirasını anlamak 
isteyenler için mükemmel. Uzman rehberlerimiz büyüleyici hikayeler ve içgörülerle yüzyıllık 
tarihi canlandırıyor.
"""
        tour.short_description = "Sultan Ahmet ve Süleymaniye Camilerini ziyaret edin, Çukur lokasyonları ile renkli Balat semtini keşfedin, alışveriş merkezinde öğle yemeği."
        
        tour.highlights = """✨ Tur Öne Çıkanları:

🕌 Sultan Ahmet Camii (Mavi Cami)
🏛️ Süleymaniye Camii kompleksi
🎨 Renkli Balat semti
📺 Çukur dizisi çekim lokasyonları
🏰 Osmanlı mimarisi
🌅 Boğaz terası manzaraları
🍽️ Alışveriş merkezinde öğle yemeği
📸 Instagram için fotoğraf noktaları
🎭 Yerel kültür deneyimi
👥 Küçük grup (maks 30)
🗣️ Uzman tarihi rehber
🚌 Konforlu ulaşım"""
        
        tour.rules = """📋 Tur Kuralları:

🕘 Kalkıştan 30 dakika önce gelin
🎫 Basılı veya dijital bilet getirin
👗 Camiler için uygun giyinin
🧕 Kadınlar: cami ziyareti için başörtüsü
👞 Cami girişlerinde ayakkabı çıkarın
📱 Camilerde telefonu sessizde tutun
📷 Fotoğraf çekebilirsiniz (camilerde flaş yok)
👥 Grupla kalın
⏰ Programı takip edin
🙏 Dini yerlere saygı gösterin
🚫 Camilerde yeme/içme yasak
🤫 Namaz sırasında sessiz olun"""
        
        tour.required_items = """🎒 Getirmeniz Gerekenler:

🎫 Tur onayı/bilet
🆔 Geçerli kimlik veya pasaport
👟 Rahat yürüyüş ayakkabısı
🧕 Başörtüsü (kadınlar - camiler için)
🧥 Hafif ceket veya hırka
🧢 Şapka ve güneş gözlüğü
🧴 Güneş kremi (SPF 30+)
💧 Su şişesi
📱 Cep telefonu + şarj aleti
📷 Fotoğraf için kamera
💰 Hediyelik eşya için nakit
🩹 Kişisel ilaçlar
🎒 Küçük sırt çantası
🌂 Şemsiye (mevsimsel)"""
        tour.save()
        
        # Persian content
        tour.set_current_language('fa')
        tour.title = "تور تاریخی استانبول - مساجد و بالات"
        tour.description = """
میراث اسلامی باشکوه و محله‌های رنگارنگ استانبول را در این تور تاریخی جامع کشف کنید. 
از مسجد آبی نمادین (مسجد سلطان احمد) بازدید کنید، مجموعه مسجد بزرگ سلیمانیه را با 
حیاط‌ها، مقبره‌ها و تراس خیره‌کننده‌اش رو به بسفر کشف کنید.

در محله پر جنب و جوش بالات، معروف به خانه‌های رنگارنگ و به عنوان لوکیشن فیلمبرداری 
سریال محبوب ترکی چوکور، قدم بزنید. فرهنگ، معماری و تاریخ اصیل استانبول را تجربه کنید 
در حالی که از ناهار خوشمزه در یک مرکز خرید مدرن لذت می‌برید.

برای علاقه‌مندان به تاریخ، عاشقان معماری و کسانی که می‌خواهند میراث غنی عثمانی و 
بیزانس استانبول را درک کنند، عالی است. راهنمایان متخصص ما قرن‌ها تاریخ را با 
داستان‌ها و بینش‌های جذاب زنده می‌کنند.
"""
        tour.short_description = "بازدید از مساجد سلطان احمد و سلیمانیه، کاوش محله رنگارنگ بالات با لوکیشن‌های چوکور، ناهار در مرکز خرید."
        
        tour.highlights = """✨ نکات برجسته تور:

🕌 مسجد سلطان احمد (مسجد آبی)
🏛️ مجموعه مسجد سلیمانیه
🎨 محله رنگارنگ بالات
📺 لوکیشن‌های فیلمبرداری سریال چوکور
🏰 معماری عثمانی
🌅 مناظر تراس بسفر
🍽️ ناهار در مرکز خرید
📸 نقاط عکاسی برای اینستاگرام
🎭 تجربه فرهنگ محلی
👥 گروه کوچک (حداکثر ۳۰ نفر)
🗣️ راهنمای متخصص تاریخی
🚌 حمل و نقل راحت"""
        
        tour.rules = """📋 قوانین تور:

🕘 ۳۰ دقیقه قبل از حرکت حاضر شوید
🎫 بلیط چاپی یا دیجیتال همراه داشته باشید
👗 برای مساجد لباس محتشمانه بپوشید
🧕 خانم‌ها: روسری برای بازدید از مسجد
👞 در ورودی مسجد کفش‌ها را در بیاورید
📱 تلفن را در مساجد بی‌صدا نگه دارید
📷 عکاسی مجاز است (در مساجد بدون فلاش)
👥 با گروه بمانید
⏰ برنامه را دنبال کنید
🙏 به مکان‌های مذهبی احترام بگذارید
🚫 در مساجد خوردن/نوشیدن ممنوع است
🤫 در هنگام نماز ساکت باشید"""
        
        tour.required_items = """🎒 چیزهایی که باید بیاورید:

🎫 تأییدیه/بلیط تور
🆔 شناسنامه یا پاسپورت معتبر
👟 کفش راحت برای پیاده‌روی
🧕 روسری (خانم‌ها - برای مساجد)
🧥 ژاکت یا ژاکت سبک
🧢 کلاه و عینک آفتابی
🧴 کرم ضد آفتاب (SPF 30+)
💧 بطری آب
📱 تلفن همراه + شارژر
📷 دوربین برای عکس
💰 پول نقد برای سوغات
🩹 داروهای شخصی
🎒 کوله‌پشتی کوچک
🌂 چتر (فصلی)"""
        tour.save()
        
        self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} tour: {tour.slug}")
        
        # Create variants
        for name, price, capacity in [
            ("ECONOMY", Decimal('30.00'), 15),
            ("STANDARD", Decimal('30.00'), 10),
            ("VIP", Decimal('30.00'), 5),
        ]:
            TourVariant.objects.get_or_create(
                tour=tour,
                name=name,
                defaults={
                    "description": f"{name} package",
                    "base_price": price,
                    "capacity": capacity,
                    "is_active": True,
                    "includes_transfer": True,
                    "includes_guide": True,
                    "includes_meal": True,
                    "includes_photographer": False,
                    "private_transfer": name == "VIP",
                    "expert_guide": name == "VIP",
                }
            )
        
        # Create schedules
        base_date = timezone.now().date()
        for i in range(14):
            schedule_date = base_date + timezone.timedelta(days=i)
            schedule, _ = TourSchedule.objects.get_or_create(
                tour=tour,
                start_date=schedule_date,
                defaults={
                    "end_date": schedule_date,
                    "start_time": time(9, 30),
                    "end_time": time(17, 30),
                    "is_available": True,
                    "day_of_week": schedule_date.weekday(),
                }
            )
            schedule.initialize_variant_capacities()
        
        # Create itinerary
        self._create_itinerary(tour)
        
        # Create cancellation policies
        for hours, refund in [(72, 100), (48, 80), (24, 50), (0, 0)]:
            TourCancellationPolicy.objects.get_or_create(
                tour=tour,
                hours_before=hours,
                defaults={
                    "refund_percentage": refund,
                    "description": f"{refund}% refund",
                    "is_active": True,
                }
            )
        
        self.stdout.write(self.style.SUCCESS("\n✅ Istanbul Historical Tour created successfully!"))
    
    def _create_itinerary(self, tour):
        """Create itinerary items"""
        itinerary_data = [
            {
                "order": 1,
                "duration": 30,
                "location": "Hotel Pickup",
                "en": {"title": "Hotel Pickup", "desc": "Comfortable pickup from your hotel in Istanbul."},
                "tr": {"title": "Otel Alımı", "desc": "İstanbul'daki otelinizden konforlu alım."},
                "fa": {"title": "پیکاپ از هتل", "desc": "پیکاپ راحت از هتل شما در استانبول."}
            },
            {
                "order": 2,
                "duration": 90,
                "location": "Sultan Ahmed Mosque",
                "en": {"title": "Blue Mosque Visit", "desc": "Explore the magnificent Sultan Ahmed Mosque with its stunning blue tiles and six minarets."},
                "tr": {"title": "Mavi Cami Ziyareti", "desc": "Muhteşem mavi çinileri ve altı minaresiyle Sultan Ahmet Camii'ni keşfedin."},
                "fa": {"title": "بازدید از مسجد آبی", "desc": "مسجد باشکوه سلطان احمد را با کاشی‌های آبی خیره‌کننده و شش مناره کشف کنید."}
            },
            {
                "order": 3,
                "duration": 120,
                "location": "Suleymaniye Mosque",
                "en": {"title": "Suleymaniye Complex", "desc": "Visit the grand Suleymaniye Mosque complex including courtyards, tombs, and terrace with Bosphorus views."},
                "tr": {"title": "Süleymaniye Kompleksi", "desc": "Avlular, türbeler ve Boğaz manzaralı teras dahil büyük Süleymaniye Camii kompleksini ziyaret edin."},
                "fa": {"title": "مجموعه سلیمانیه", "desc": "از مجموعه مسجد بزرگ سلیمانیه شامل حیاط‌ها، مقبره‌ها و تراس با مناظر بسفر بازدید کنید."}
            },
            {
                "order": 4,
                "duration": 60,
                "location": "Shopping Center",
                "en": {"title": "Lunch Break", "desc": "Enjoy lunch at a modern shopping center with various dining options."},
                "tr": {"title": "Öğle Yemeği Molası", "desc": "Çeşitli yemek seçenekleri sunan modern bir alışveriş merkezinde öğle yemeğinin tadını çıkarın."},
                "fa": {"title": "استراحت ناهار", "desc": "از ناهار در یک مرکز خرید مدرن با گزینه‌های غذایی مختلف لذت ببرید."}
            },
            {
                "order": 5,
                "duration": 90,
                "location": "Balat",
                "en": {"title": "Balat Neighborhood", "desc": "Explore the colorful Balat district and visit Çukur TV series filming locations."},
                "tr": {"title": "Balat Semti", "desc": "Renkli Balat semtini keşfedin ve Çukur dizisi çekim lokasyonlarını ziyaret edin."},
                "fa": {"title": "محله بالات", "desc": "منطقه رنگارنگ بالات را کشف کنید و از لوکیشن‌های فیلمبرداری سریال چوکور بازدید کنید."}
            },
            {
                "order": 6,
                "duration": 30,
                "location": "Hotel Drop-off",
                "en": {"title": "Return to Hotel", "desc": "Comfortable return to your hotel with wonderful memories."},
                "tr": {"title": "Otele Dönüş", "desc": "Harika anılarla otelinize konforlu dönüş."},
                "fa": {"title": "بازگشت به هتل", "desc": "بازگشت راحت به هتل با خاطرات فوق‌العاده."}
            }
        ]
        
        for item_data in itinerary_data:
            TourItinerary.objects.filter(tour=tour, order=item_data["order"]).delete()
            slug = f"{tour.slug}-stop-{item_data['order']}"
            item = TourItinerary.objects.create(
                tour=tour,
                slug=slug,
                order=item_data["order"],
                duration_minutes=item_data["duration"],
                location=item_data["location"],
            )
            for lang in ['en', 'tr', 'fa']:
                item.set_current_language(lang)
                item.title = item_data[lang]["title"]
                item.description = item_data[lang]["desc"]
                item.save()
