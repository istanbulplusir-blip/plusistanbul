from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time
from decimal import Decimal

from tours.models import (
    Tour, TourVariant, TourSchedule, TourOption, 
    TourCategory, TourItinerary, TourCancellationPolicy
)


class Command(BaseCommand):
    help = "Create a complete Istanbul Bosphorus tour with 3-language support"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating Istanbul Bosphorus Tour...")
        
        # Create or get category
        category, _ = TourCategory.objects.get_or_create(
            slug="boat-tours",
            defaults={"name": "Boat Tours"}
        )
        
        # Set category translations
        category.set_current_language('en')
        category.name = "Boat Tours"
        category.description = "Explore Istanbul from the water"
        category.save()
        
        category.set_current_language('tr')
        category.name = "Tekne Turları"
        category.description = "İstanbul'u sudan keşfedin"
        category.save()
        
        category.set_current_language('fa')
        category.name = "تورهای قایقی"
        category.description = "استانبول را از روی آب کشف کنید"
        category.save()
        
        # Create tour
        tour, created = Tour.objects.get_or_create(
            slug="istanbul-bosphorus-cruise",
            defaults={
                "price": Decimal('45.00'),
                "currency": "USD",
                "duration_hours": 6,
                "pickup_time": time(9, 0),
                "start_time": time(10, 0),
                "end_time": time(16, 0),
                "min_participants": 10,
                "max_participants": 150,
                "booking_cutoff_hours": 24,
                "cancellation_hours": 48,
                "refund_percentage": 80,
                "includes_transfer": True,
                "includes_guide": True,
                "includes_meal": True,
                "includes_photographer": False,
                "tour_type": "day",
                "transport_type": "boat",
                "is_active": True,
                "is_featured": True,
                "is_popular": True,
                "is_special": True,
                "city": "Istanbul",
                "country": "Turkey",
                "category": category,
            }
        )
        
        # English content
        tour.set_current_language('en')
        tour.title = "Istanbul Bosphorus Cruise & Two Continents Tour"
        tour.description = """
Experience the magic of Istanbul from the water on this unforgettable Bosphorus cruise! 
Sail between Europe and Asia while enjoying breathtaking views of palaces, fortresses, 
and historic mansions lining the shores.

This comprehensive tour combines a scenic boat cruise with visits to iconic landmarks 
on both continents. You'll explore the majestic Dolmabahçe Palace, cross the famous 
Bosphorus Bridge, and enjoy a delicious Turkish lunch with stunning water views.

Perfect for first-time visitors and photography enthusiasts, this tour offers the best 
way to see Istanbul's unique position as the bridge between two continents. Our expert 
guides share fascinating stories about the city's rich history, from Byzantine emperors 
to Ottoman sultans.
"""
        tour.short_description = "A 6-hour cruise along the Bosphorus Strait, exploring Istanbul's iconic waterfront palaces, bridges, and landmarks spanning two continents."
        tour.highlights = """✨ Tour Highlights:

🚢 Scenic Bosphorus cruise between Europe & Asia
🏰 Visit Dolmabahçe Palace - Ottoman grandeur
🌉 Cross the iconic Bosphorus Bridge
📸 Photo stops at best viewpoints
🍽️ Traditional Turkish lunch included
🏛️ See Rumeli Fortress from the water
🕌 View waterfront mosques and palaces
🏡 Ottoman mansions (yalı) along the shore
🌊 Maiden's Tower photo opportunity
👥 Small group experience (max 150)
🎧 Audio guide in multiple languages
⛵ Comfortable modern cruise boat"""
        
        tour.rules = """📋 Tour Rules & Guidelines:

🕘 Arrive 30 minutes before departure
🎫 Bring printed or digital ticket
👟 Wear comfortable walking shoes
🧥 Bring jacket (windy on water)
📱 Keep phone charged for photos
🚭 No smoking inside the boat
📷 Photography allowed everywhere
👥 Stay with the group at stops
⏰ Follow the schedule strictly
🌿 Respect historical sites
🚫 No alcohol on the boat
👶 Children must be supervised"""
        
        tour.required_items = """🎒 What to Bring:

🎫 Tour confirmation/ticket
🆔 Valid ID or passport
👟 Comfortable walking shoes
🧥 Light jacket or sweater
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
        tour.title = "İstanbul Boğaz Turu ve İki Kıta Gezisi"
        tour.description = """
İstanbul'un büyüsünü sudan yaşayın! Unutulmaz bir Boğaz turu ile Avrupa ve Asya 
arasında yolculuk yapın, kıyılardaki sarayları, kaleleri ve tarihi yalıları izleyin.

Bu kapsamlı tur, muhteşem bir tekne gezisi ile her iki kıtadaki ikonik yerleri 
ziyaret etmeyi birleştiriyor. Görkemli Dolmabahçe Sarayı'nı keşfedecek, ünlü 
Boğaziçi Köprüsü'nden geçecek ve muhteşem su manzaralı lezzetli bir Türk öğle 
yemeğinin tadını çıkaracaksınız.

İlk kez ziyaret edenler ve fotoğraf tutkunları için mükemmel olan bu tur, 
İstanbul'un iki kıta arasındaki köprü konumunu görmenin en iyi yoludur. Uzman 
rehberlerimiz, Bizans imparatorlarından Osmanlı padişahlarına kadar şehrin zengin 
tarihi hakkında büyüleyici hikayeler paylaşıyor.
"""
        tour.short_description = "Boğaz boyunca 6 saatlik bir gezi, İstanbul'un iki kıtaya yayılan ikonik sahil saraylarını, köprülerini ve simge yapılarını keşfedin."
        tour.highlights = """✨ Tur Öne Çıkanları:

🚢 Avrupa ve Asya arası Boğaz gezisi
🏰 Dolmabahçe Sarayı ziyareti
🌉 İkonik Boğaziçi Köprüsü geçişi
📸 En iyi manzara noktalarında fotoğraf molası
🍽️ Geleneksel Türk öğle yemeği dahil
🏛️ Sudan Rumeli Hisarı manzarası
🕌 Sahildeki camiler ve saraylar
🏡 Boğaz yalıları
🌊 Kız Kulesi fotoğraf fırsatı
👥 Küçük grup deneyimi (maks 150)
🎧 Çoklu dilde sesli rehber
⛵ Konforlu modern gezi teknesi"""
        
        tour.rules = """📋 Tur Kuralları ve Yönergeler:

🕘 Kalkıştan 30 dakika önce gelin
🎫 Basılı veya dijital bilet getirin
👟 Rahat yürüyüş ayakkabısı giyin
🧥 Ceket getirin (suda rüzgarlı)
📱 Fotoğraf için telefonu şarjlı tutun
🚭 Tekne içinde sigara içilmez
📷 Her yerde fotoğraf çekebilirsiniz
👥 Duraklarda grupla kalın
⏰ Programı kesinlikle takip edin
🌿 Tarihi yerlere saygı gösterin
🚫 Teknede alkol yasak
👶 Çocuklar gözetim altında olmalı"""
        
        tour.required_items = """🎒 Getirmeniz Gerekenler:

🎫 Tur onayı/bilet
🆔 Geçerli kimlik veya pasaport
👟 Rahat yürüyüş ayakkabısı
🧥 Hafif ceket veya kazak
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
        tour.title = "کروز بسفر استانبول و تور دو قاره"
        tour.description = """
جادوی استانبول را از روی آب تجربه کنید! در این کروز فراموش‌نشدنی بسفر، 
بین اروپا و آسیا حرکت کنید و از مناظر خیره‌کننده کاخ‌ها، قلعه‌ها و 
عمارت‌های تاریخی در کنار ساحل لذت ببرید.

این تور جامع، یک کروز دیدنی را با بازدید از نقاط دیدنی نمادین در هر دو 
قاره ترکیب می‌کند. شما کاخ باشکوه دلمه‌باغچه را کشف خواهید کرد، از پل 
معروف بسفر عبور می‌کنید و از یک ناهار خوشمزه ترکی با مناظر آب خیره‌کننده 
لذت خواهید برد.

این تور که برای بازدیدکنندگان اولین بار و علاقه‌مندان به عکاسی عالی است، 
بهترین راه برای دیدن موقعیت منحصر به فرد استانبول به عنوان پل بین دو قاره 
را ارائه می‌دهد. راهنمایان متخصص ما داستان‌های جذابی درباره تاریخ غنی شهر، 
از امپراتوران بیزانس تا سلاطین عثمانی، به اشتراک می‌گذارند.
"""
        tour.short_description = "یک کروز ۶ ساعته در امتداد تنگه بسفر، کاوش در کاخ‌های ساحلی، پل‌ها و نقاط دیدنی نمادین استانبول که دو قاره را در بر می‌گیرد."
        tour.highlights = """✨ نکات برجسته تور:

🚢 کروز دیدنی بسفر بین اروپا و آسیا
🏰 بازدید از کاخ دلمه‌باغچه - شکوه عثمانی
🌉 عبور از پل نمادین بسفر
📸 توقف برای عکس در بهترین نقاط دید
🍽️ ناهار سنتی ترکی شامل می‌شود
🏛️ دیدن قلعه روملی از روی آب
🕌 مشاهده مساجد و کاخ‌های ساحلی
🏡 عمارت‌های عثمانی (یالی) در کنار ساحل
🌊 فرصت عکس از برج دختر
👥 تجربه گروه کوچک (حداکثر ۱۵۰ نفر)
🎧 راهنمای صوتی به زبان‌های مختلف
⛵ قایق کروز مدرن و راحت"""
        
        tour.rules = """📋 قوانین و دستورالعمل‌های تور:

🕘 ۳۰ دقیقه قبل از حرکت حاضر شوید
🎫 بلیط چاپی یا دیجیتال همراه داشته باشید
👟 کفش راحت برای پیاده‌روی بپوشید
🧥 ژاکت بیاورید (روی آب باد می‌آید)
📱 تلفن را برای عکس شارژ نگه دارید
🚭 داخل قایق سیگار نکشید
📷 عکاسی در همه جا مجاز است
👥 در ایستگاه‌ها با گروه بمانید
⏰ برنامه را به دقت دنبال کنید
🌿 به مکان‌های تاریخی احترام بگذارید
🚫 الکل در قایق ممنوع است
👶 کودکان باید تحت نظارت باشند"""
        
        tour.required_items = """🎒 چیزهایی که باید بیاورید:

🎫 تأییدیه/بلیط تور
🆔 شناسنامه یا پاسپورت معتبر
👟 کفش راحت برای پیاده‌روی
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
        variants_data = [
            ("ECONOMY", Decimal('45.00'), 60, "Economy package - Standard boat seating"),
            ("STANDARD", Decimal('65.00'), 50, "Standard package - Upper deck seating"),
            ("PREMIUM", Decimal('95.00'), 30, "Premium package - VIP lounge access"),
            ("VIP", Decimal('150.00'), 10, "VIP package - Private cabin & exclusive services"),
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
                    "includes_meal": name != "ECONOMY",
                    "includes_photographer": name in ["PREMIUM", "VIP"],
                    "extended_hours": 0 if name in ["ECONOMY", "STANDARD"] else 1,
                    "private_transfer": name == "VIP",
                    "expert_guide": name in ["PREMIUM", "VIP"],
                    "special_meal": name == "VIP",
                }
            )
            self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} variant: {name}")
        
        # Create schedules for next 14 days
        base_date = timezone.now().date()
        for i in range(14):
            schedule_date = base_date + timezone.timedelta(days=i)
            schedule, created = TourSchedule.objects.get_or_create(
                tour=tour,
                start_date=schedule_date,
                defaults={
                    "end_date": schedule_date,
                    "start_time": time(10, 0),
                    "end_time": time(16, 0),
                    "is_available": True,
                    "day_of_week": schedule_date.weekday(),
                }
            )
            schedule.initialize_variant_capacities()
            if created:
                self.stdout.write(f"✅ Created schedule: {schedule_date}")
        
        # Create options
        options_data = [
            ("Professional Photography Package", "Professional photographer for the entire cruise", 
             Decimal('35.00'), "equipment"),
            ("Premium Lunch Upgrade", "Gourmet Turkish cuisine with sea view", 
             Decimal('25.00'), "food"),
            ("Private Guide", "Exclusive private guide for your group", 
             Decimal('80.00'), "service"),
            ("Sunset Cruise Upgrade", "Extended tour to include sunset viewing", 
             Decimal('20.00'), "service"),
            ("Turkish Tea & Snacks", "Traditional Turkish tea service with snacks", 
             Decimal('10.00'), "food"),
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
                    "max_quantity": 10,
                }
            )
            self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} option: {name}")
        
        # Create itinerary
        self._create_itinerary(tour)
        
        # Create cancellation policies
        self._create_cancellation_policies(tour)
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 ISTANBUL BOSPHORUS TOUR SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Tour: {tour.slug}")
        self.stdout.write(f"Languages: English, Turkish, Persian")
        self.stdout.write(f"Variants: {tour.variants.count()}")
        self.stdout.write(f"Schedules: {tour.schedules.count()}")
        self.stdout.write(f"Options: {tour.options.count()}")
        self.stdout.write(f"Itinerary Items: {tour.itinerary.count()}")
        self.stdout.write(f"Cancellation Policies: {tour.cancellation_policies.count()}")
        self.stdout.write(self.style.SUCCESS("\n✅ Istanbul Bosphorus Tour created successfully!"))
    
    def _create_itinerary(self, tour):
        """Create itinerary items with 3-language support"""
        itinerary_data = [
            {
                "order": 1,
                "duration": 30,
                "location": "Hotel Pickup",
                "en": {"title": "Hotel Pickup & Welcome", 
                       "desc": "Comfortable pickup from your hotel in Istanbul. Meet your guide and fellow travelers."},
                "tr": {"title": "Otel Alımı ve Karşılama", 
                       "desc": "İstanbul'daki otelinizden konforlu alım. Rehberiniz ve diğer gezginlerle tanışın."},
                "fa": {"title": "پیکاپ از هتل و خوش‌آمدگویی", 
                       "desc": "پیکاپ راحت از هتل شما در استانبول. با راهنما و همسفران خود آشنا شوید."}
            },
            {
                "order": 2,
                "duration": 60,
                "location": "Dolmabahçe Palace",
                "en": {"title": "Dolmabahçe Palace Visit", 
                       "desc": "Explore the magnificent Ottoman palace with its stunning architecture and crystal chandeliers."},
                "tr": {"title": "Dolmabahçe Sarayı Ziyareti", 
                       "desc": "Muhteşem mimarisi ve kristal avizeleriyle görkemli Osmanlı sarayını keşfedin."},
                "fa": {"title": "بازدید از کاخ دلمه‌باغچه", 
                       "desc": "کاخ باشکوه عثمانی را با معماری خیره‌کننده و لوسترهای کریستالی کشف کنید."}
            },
            {
                "order": 3,
                "duration": 120,
                "location": "Bosphorus Strait",
                "en": {"title": "Bosphorus Cruise", 
                       "desc": "Sail along the Bosphorus between Europe and Asia. See palaces, fortresses, and Ottoman mansions."},
                "tr": {"title": "Boğaz Gezisi", 
                       "desc": "Avrupa ve Asya arasında Boğaz'da yolculuk yapın. Sarayları, kaleleri ve Osmanlı yalılarını görün."},
                "fa": {"title": "کروز بسفر", 
                       "desc": "در امتداد بسفر بین اروپا و آسیا حرکت کنید. کاخ‌ها، قلعه‌ها و عمارت‌های عثمانی را ببینید."}
            },
            {
                "order": 4,
                "duration": 15,
                "location": "Bosphorus Bridge",
                "en": {"title": "Bosphorus Bridge Crossing", 
                       "desc": "Cross the iconic bridge connecting two continents. Perfect photo opportunity!"},
                "tr": {"title": "Boğaziçi Köprüsü Geçişi", 
                       "desc": "İki kıtayı birleştiren ikonik köprüden geçin. Mükemmel fotoğraf fırsatı!"},
                "fa": {"title": "عبور از پل بسفر", 
                       "desc": "از پل نمادین که دو قاره را به هم متصل می‌کند عبور کنید. فرصت عالی برای عکس!"}
            },
            {
                "order": 5,
                "duration": 75,
                "location": "Waterfront Restaurant",
                "en": {"title": "Turkish Lunch with Sea View", 
                       "desc": "Enjoy authentic Turkish cuisine at a waterfront restaurant with stunning Bosphorus views."},
                "tr": {"title": "Deniz Manzaralı Türk Öğle Yemeği", 
                       "desc": "Muhteşem Boğaz manzaralı sahil restoranında otantik Türk mutfağının tadını çıkarın."},
                "fa": {"title": "ناهار ترکی با منظره دریا", 
                       "desc": "از غذای اصیل ترکی در رستوران ساحلی با مناظر خیره‌کننده بسفر لذت ببرید."}
            },
            {
                "order": 6,
                "duration": 30,
                "location": "Rumeli Fortress",
                "en": {"title": "Rumeli Fortress Photo Stop", 
                       "desc": "Photo stop at the historic fortress built by Mehmed the Conqueror in 1452."},
                "tr": {"title": "Rumeli Hisarı Fotoğraf Molası", 
                       "desc": "1452'de Fatih Sultan Mehmet tarafından inşa edilen tarihi kalede fotoğraf molası."},
                "fa": {"title": "توقف عکس در قلعه روملی", 
                       "desc": "توقف برای عکس در قلعه تاریخی که توسط محمد فاتح در ۱۴۵۲ ساخته شد."}
            },
            {
                "order": 7,
                "duration": 20,
                "location": "Maiden's Tower",
                "en": {"title": "Maiden's Tower View", 
                       "desc": "See the iconic Maiden's Tower standing in the middle of the Bosphorus."},
                "tr": {"title": "Kız Kulesi Manzarası", 
                       "desc": "Boğaz'ın ortasında duran ikonik Kız Kulesi'ni görün."},
                "fa": {"title": "منظره برج دختر", 
                       "desc": "برج نمادین دختر را که در وسط بسفر ایستاده است ببینید."}
            },
            {
                "order": 8,
                "duration": 30,
                "location": "Ortaköy",
                "en": {"title": "Ortaköy Square Visit", 
                       "desc": "Visit the charming Ortaköy neighborhood with its famous mosque and street food."},
                "tr": {"title": "Ortaköy Meydanı Ziyareti", 
                       "desc": "Ünlü camisi ve sokak lezzetleriyle büyüleyici Ortaköy semtini ziyaret edin."},
                "fa": {"title": "بازدید از میدان اورتاکوی", 
                       "desc": "از محله جذاب اورتاکوی با مسجد معروف و غذاهای خیابانی آن بازدید کنید."}
            },
            {
                "order": 9,
                "duration": 30,
                "location": "Hotel Drop-off",
                "en": {"title": "Return to Hotel", 
                       "desc": "Comfortable return to your hotel with wonderful memories of Istanbul."},
                "tr": {"title": "Otele Dönüş", 
                       "desc": "İstanbul'un harika anılarıyla otelinize konforlu dönüş."},
                "fa": {"title": "بازگشت به هتل", 
                       "desc": "بازگشت راحت به هتل با خاطرات فوق‌العاده از استانبول."}
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
            
            # Set Turkish
            item.set_current_language('tr')
            item.title = item_data["tr"]["title"]
            item.description = item_data["tr"]["desc"]
            item.save()
            
            # Set Persian
            item.set_current_language('fa')
            item.title = item_data["fa"]["title"]
            item.description = item_data["fa"]["desc"]
            item.save()
            
            if created:
                self.stdout.write(f"✅ Created itinerary item {item_data['order']}")
    
    def _create_cancellation_policies(self, tour):
        """Create cancellation policies"""
        policies_data = [
            (72, 100, "Full refund up to 72 hours before tour start"),
            (48, 80, "80% refund up to 48 hours before tour start"),
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
