from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from decimal import Decimal

from tours.models import (
    Tour, TourVariant, TourSchedule, TourOption, 
    TourCategory, TourItinerary, TourCancellationPolicy
)


class Command(BaseCommand):
    help = "Create Princes Islands Tour with 3-language support"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating Princes Islands Tour...")
        
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
            slug="princes-islands-cruise",
            defaults={
                "price": Decimal('30.00'),
                "currency": "USD",
                "duration_hours": 9,
                "pickup_time": time(8, 30),
                "start_time": time(9, 0),
                "end_time": time(18, 0),
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
                "transport_type": "boat",
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
        tour.title = "Princes Islands Cruise - Marmara Sea Adventure"
        tour.description = """
Escape to the beautiful Princes Islands on a full-day cruise in the Marmara Sea! 
Enjoy a private boat with DJ entertainment, explore the pristine islands with their 
pleasant climate, and savor a delicious lunch on the historic ship.

This tour offers a perfect blend of relaxation, entertainment, and exploration. Dance 
to the DJ's music on the boat, discover the car-free islands with their Victorian-era 
mansions, and enjoy free time to explore at your own pace.

Perfect for families, couples, and groups looking for a unique island experience away 
from the city bustle. The islands offer stunning nature, historic architecture, and 
peaceful beaches.
"""
        tour.short_description = "Full-day cruise to Princes Islands with private boat, DJ entertainment, island exploration, and lunch on historic ship."
        tour.highlights = """✨ Tour Highlights:

🚢 Private boat cruise in Marmara Sea
🎵 DJ entertainment on board
🏝️ Visit Princes Islands archipelago
🌳 Pristine nature and pleasant climate
🍽️ Lunch on historic ship
🏛️ Victorian-era mansions
🚫 Car-free islands
🚲 Bicycle and horse carriage options
🏖️ Beautiful beaches
📸 Stunning photo opportunities
👥 Small group experience (max 30)
⛵ Comfortable cruise boat"""
        
        tour.rules = """📋 Tour Rules:

🕘 Arrive 30 minutes before departure
🎫 Bring printed or digital ticket
👟 Wear comfortable walking shoes
🧥 Bring jacket (windy on water)
📱 Keep phone charged
🚭 No smoking inside the boat
📷 Photography allowed everywhere
👥 Stay with the group at stops
⏰ Follow the schedule
🌿 Respect island nature
🚫 No littering on islands
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
💰 Cash for island activities
🩹 Personal medications
🎒 Small backpack
🌂 Umbrella (seasonal)
🩱 Swimsuit (optional)"""
        tour.save()
        
        # Turkish content
        tour.set_current_language('tr')
        tour.title = "Adalar Turu - Marmara Denizi Macerası"
        tour.description = """
Marmara Denizi'nde tam gün süren bir gezi ile güzel Prens Adaları'na kaçın! 
DJ eğlenceli özel teknenin tadını çıkarın, hoş iklimleriyle bozulmamış adaları 
keşfedin ve tarihi gemide lezzetli bir öğle yemeğinin tadını çıkarın.

Bu tur, rahatlama, eğlence ve keşfin mükemmel bir karışımını sunuyor. Teknede 
DJ'in müziğiyle dans edin, Viktorya dönemi konakları ile arabasız adaları keşfedin 
ve kendi hızınızda keşfetmek için serbest zamanın tadını çıkarın.

Şehir koşuşturmacasından uzakta benzersiz bir ada deneyimi arayan aileler, çiftler 
ve gruplar için mükemmel. Adalar muhteşem doğa, tarihi mimari ve huzurlu plajlar sunuyor.
"""
        tour.short_description = "Özel tekne, DJ eğlencesi, ada keşfi ve tarihi gemide öğle yemeği ile Prens Adaları'na tam gün gezi."
        tour.highlights = """✨ Tur Öne Çıkanları:

🚢 Marmara Denizi'nde özel tekne gezisi
🎵 Gemide DJ eğlencesi
🏝️ Prens Adaları takımadalarını ziyaret
🌳 Bozulmamış doğa ve hoş iklim
🍽️ Tarihi gemide öğle yemeği
🏛️ Viktorya dönemi konakları
🚫 Arabasız adalar
🚲 Bisiklet ve fayton seçenekleri
🏖️ Güzel plajlar
📸 Muhteşem fotoğraf fırsatları
👥 Küçük grup deneyimi (maks 30)
⛵ Konforlu gezi teknesi"""
        
        tour.rules = """📋 Tur Kuralları:

🕘 Kalkıştan 30 dakika önce gelin
🎫 Basılı veya dijital bilet getirin
👟 Rahat yürüyüş ayakkabısı giyin
🧥 Ceket getirin (suda rüzgarlı)
📱 Telefonu şarjlı tutun
🚭 Tekne içinde sigara içmeyin
📷 Her yerde fotoğraf çekebilirsiniz
👥 Duraklarda grupla kalın
⏰ Programı takip edin
🌿 Ada doğasına saygı gösterin
🚫 Adalarda çöp atmayın
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
💰 Ada aktiviteleri için nakit
🩹 Kişisel ilaçlar
🎒 Küçük sırt çantası
🌂 Şemsiye (mevsimsel)
🩱 Mayo (isteğe bağlı)"""
        tour.save()
        
        # Persian content
        tour.set_current_language('fa')
        tour.title = "کروز جزایر پرنسس - ماجراجویی دریای مرمره"
        tour.description = """
به جزایر زیبای پرنسس در یک کروز تمام روز در دریای مرمره فرار کنید! 
از قایق خصوصی با سرگرمی DJ لذت ببرید، جزایر بکر با آب و هوای دلپذیر را 
کشف کنید و از ناهار خوشمزه در کشتی تاریخی لذت ببرید.

این تور ترکیبی عالی از آرامش، سرگرمی و کاوش را ارائه می‌دهد. با موسیقی 
DJ در قایق برقصید، جزایر بدون ماشین را با عمارت‌های دوران ویکتوریا کشف 
کنید و از زمان آزاد برای کاوش با سرعت خود لذت ببرید.

برای خانواده‌ها، زوج‌ها و گروه‌هایی که به دنبال تجربه منحصر به فرد جزیره 
دور از شلوغی شهر هستند، عالی است. جزایر طبیعت خیره‌کننده، معماری تاریخی 
و سواحل آرام را ارائه می‌دهند.
"""
        tour.short_description = "کروز تمام روز به جزایر پرنسس با قایق خصوصی، سرگرمی DJ، کاوش جزیره و ناهار در کشتی تاریخی."
        tour.highlights = """✨ نکات برجسته تور:

🚢 کروز قایق خصوصی در دریای مرمره
🎵 سرگرمی DJ در کشتی
🏝️ بازدید از مجموعه جزایر پرنسس
🌳 طبیعت بکر و آب و هوای دلپذیر
🍽️ ناهار در کشتی تاریخی
🏛️ عمارت‌های دوران ویکتوریا
🚫 جزایر بدون ماشین
🚲 گزینه‌های دوچرخه و کالسکه اسبی
🏖️ سواحل زیبا
📸 فرصت‌های عکاسی خیره‌کننده
👥 تجربه گروه کوچک (حداکثر ۳۰ نفر)
⛵ قایق کروز راحت"""
        
        tour.rules = """📋 قوانین تور:

🕘 ۳۰ دقیقه قبل از حرکت حاضر شوید
🎫 بلیط چاپی یا دیجیتال همراه داشته باشید
👟 کفش راحت برای پیاده‌روی بپوشید
🧥 ژاکت بیاورید (روی آب باد می‌آید)
📱 تلفن را شارژ نگه دارید
🚭 داخل قایق سیگار نکشید
📷 عکاسی در همه جا مجاز است
👥 در ایستگاه‌ها با گروه بمانید
⏰ برنامه را دنبال کنید
🌿 به طبیعت جزیره احترام بگذارید
🚫 در جزایر زباله نریزید
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
💰 پول نقد برای فعالیت‌های جزیره
🩹 داروهای شخصی
🎒 کوله‌پشتی کوچک
🌂 چتر (فصلی)
🩱 لباس شنا (اختیاری)"""
        tour.save()
        
        self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} tour: {tour.slug}")
        
        # Create variants
        variants_data = [
            ("ECONOMY", Decimal('30.00'), 15, "Economy package - Standard boat seating"),
            ("STANDARD", Decimal('30.00'), 10, "Standard package - Upper deck seating"),
            ("VIP", Decimal('30.00'), 5, "VIP package - Private cabin & exclusive services"),
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
                    "includes_photographer": name == "VIP",
                    "extended_hours": 0,
                    "private_transfer": name == "VIP",
                    "expert_guide": name == "VIP",
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
                    "start_time": time(9, 0),
                    "end_time": time(18, 0),
                    "is_available": True,
                    "day_of_week": schedule_date.weekday(),
                }
            )
            schedule.initialize_variant_capacities()
            if created:
                self.stdout.write(f"✅ Created schedule: {schedule_date}")
        
        # Create cancellation policies
        policies_data = [
            (72, 100, "Full refund up to 72 hours before tour start"),
            (48, 80, "80% refund up to 48 hours before tour start"),
            (24, 50, "50% refund up to 24 hours before tour start"),
            (0, 0, "No refund less than 24 hours before tour start"),
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
        
        self.stdout.write(self.style.SUCCESS("\n✅ Princes Islands Tour created successfully!"))
