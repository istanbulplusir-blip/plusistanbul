from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from decimal import Decimal

from tours.models import (
    Tour, TourVariant, TourSchedule, TourOption, 
    TourCategory, TourItinerary, TourCancellationPolicy
)


class Command(BaseCommand):
    help = "Create Venezia Shopping Tour with 3-language support"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating Venezia Shopping Tour...")
        
        # Create or get category
        category, _ = TourCategory.objects.get_or_create(
            slug="shopping-tours",
            defaults={"name": "Shopping Tours"}
        )
        
        # Set category translations
        category.set_current_language('en')
        category.name = "Shopping Tours"
        category.description = "Explore the best shopping destinations"
        category.save()
        
        category.set_current_language('tr')
        category.name = "Alışveriş Turları"
        category.description = "En iyi alışveriş destinasyonlarını keşfedin"
        category.save()
        
        category.set_current_language('fa')
        category.name = "تورهای خرید"
        category.description = "بهترین مقاصد خرید را کشف کنید"
        category.save()
        
        # Create tour
        tour, created = Tour.objects.get_or_create(
            slug="venezia-shopping-tour",
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
                "includes_meal": False,
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
        tour.title = "Venezia Shopping Tour - Leather & Mega Outlet"
        tour.description = """
Experience the ultimate shopping adventure in Istanbul! Visit the largest and highest quality 
leather industry center with an exclusive fashion show, followed by shopping at the magnificent 
Mega Outlet center.

This tour takes you to Istanbul's most popular and beautiful shopping destinations. Explore 
premium leather goods with a private fashion show, then enjoy unlimited shopping at one of 
the city's largest outlet centers featuring international brands at unbeatable prices.

Perfect for shopping enthusiasts looking for quality leather products, designer brands, and 
unique souvenirs. Our expert guides ensure you get the best deals and authentic products.
"""
        tour.short_description = "Visit Istanbul's premier leather center with exclusive fashion show and shop at the magnificent Mega Outlet - no lunch included."
        tour.highlights = """✨ Tour Highlights:

🛍️ Largest leather industry center in Istanbul
👗 Exclusive private fashion show
🏬 Mega Outlet shopping center
👜 Premium leather goods and accessories
🎁 Souvenir shop with unique items
💎 International designer brands
🏷️ Unbeatable outlet prices
🚌 Comfortable transportation
👥 Small group experience (max 30)
🗣️ Expert shopping guide
📸 Photo opportunities
⭐ Authentic Turkish products"""
        
        tour.rules = """📋 Tour Rules:

🕘 Arrive 30 minutes before departure
🎫 Bring printed or digital ticket
👟 Wear comfortable walking shoes
💳 Bring credit/debit cards
💰 Carry some cash for small purchases
🎒 Bring shopping bags or backpack
📱 Keep phone charged
🚭 No smoking in shopping centers
👥 Stay with the group
⏰ Follow the schedule
🛍️ Check return policies before buying
💵 Keep receipts for customs"""
        
        tour.required_items = """🎒 What to Bring:

🎫 Tour confirmation/ticket
🆔 Valid ID or passport
👟 Comfortable walking shoes
💳 Credit/debit cards
💰 Cash (Turkish Lira/USD/EUR)
🎒 Shopping bags or backpack
📱 Mobile phone + charger
📷 Camera for photos
🧥 Light jacket (for AC)
💧 Water bottle
🩹 Personal medications
📝 Shopping list
🌂 Umbrella (seasonal)"""
        tour.save()
        
        # Turkish content
        tour.set_current_language('tr')
        tour.title = "Venezia Alışveriş Turu - Deri ve Mega Outlet"
        tour.description = """
İstanbul'da nihai alışveriş macerasını yaşayın! Özel defile ile en büyük ve en kaliteli 
deri sanayi merkezini ziyaret edin, ardından muhteşem Mega Outlet merkezinde alışveriş yapın.

Bu tur sizi İstanbul'un en popüler ve güzel alışveriş destinasyonlarına götürüyor. Özel 
defile ile premium deri ürünlerini keşfedin, ardından uluslararası markaların yer aldığı 
şehrin en büyük outlet merkezlerinden birinde sınırsız alışverişin tadını çıkarın.

Kaliteli deri ürünleri, tasarımcı markaları ve benzersiz hediyelik eşyalar arayan alışveriş 
tutkunları için mükemmel. Uzman rehberlerimiz en iyi fırsatları ve orijinal ürünleri 
bulmanızı sağlar.
"""
        tour.short_description = "Özel defile ile İstanbul'un önde gelen deri merkezini ziyaret edin ve muhteşem Mega Outlet'te alışveriş yapın - öğle yemeği dahil değil."
        tour.highlights = """✨ Tur Öne Çıkanları:

🛍️ İstanbul'un en büyük deri sanayi merkezi
👗 Özel defile gösterisi
🏬 Mega Outlet alışveriş merkezi
👜 Premium deri ürünler ve aksesuarlar
🎁 Benzersiz hediyelik eşya mağazası
💎 Uluslararası tasarımcı markalar
🏷️ Rakipsiz outlet fiyatları
🚌 Konforlu ulaşım
👥 Küçük grup deneyimi (maks 30)
🗣️ Uzman alışveriş rehberi
📸 Fotoğraf fırsatları
⭐ Orijinal Türk ürünleri"""
        
        tour.rules = """📋 Tur Kuralları:

🕘 Kalkıştan 30 dakika önce gelin
🎫 Basılı veya dijital bilet getirin
👟 Rahat yürüyüş ayakkabısı giyin
💳 Kredi/banka kartı getirin
💰 Küçük alışverişler için nakit taşıyın
🎒 Alışveriş çantası veya sırt çantası getirin
📱 Telefonu şarjlı tutun
🚭 Alışveriş merkezlerinde sigara içmeyin
👥 Grupla kalın
⏰ Programı takip edin
🛍️ Satın almadan önce iade politikalarını kontrol edin
💵 Gümrük için fişleri saklayın"""
        
        tour.required_items = """🎒 Getirmeniz Gerekenler:

🎫 Tur onayı/bilet
🆔 Geçerli kimlik veya pasaport
👟 Rahat yürüyüş ayakkabısı
💳 Kredi/banka kartları
💰 Nakit (Türk Lirası/USD/EUR)
🎒 Alışveriş çantası veya sırt çantası
📱 Cep telefonu + şarj aleti
📷 Fotoğraf için kamera
🧥 Hafif ceket (klima için)
💧 Su şişesi
🩹 Kişisel ilaçlar
📝 Alışveriş listesi
🌂 Şemsiye (mevsimsel)"""
        tour.save()
        
        # Persian content
        tour.set_current_language('fa')
        tour.title = "تور خرید ونیزیا - چرم و مگا اوتلت"
        tour.description = """
ماجراجویی نهایی خرید را در استانبول تجربه کنید! از بزرگترین و با کیفیت‌ترین مرکز 
صنعت چرم با فشن شو اختصاصی بازدید کنید، سپس در مرکز مگا اوتلت شگفت‌انگیز خرید کنید.

این تور شما را به محبوب‌ترین و زیباترین مقاصد خرید استانبول می‌برد. محصولات چرمی 
پریمیوم را با فشن شو خصوصی کشف کنید، سپس از خرید نامحدود در یکی از بزرگترین 
مراکز اوتلت شهر با برندهای بین‌المللی با قیمت‌های بی‌نظیر لذت ببرید.

برای علاقه‌مندان به خرید که به دنبال محصولات چرمی با کیفیت، برندهای طراح و 
سوغاتی‌های منحصر به فرد هستند، عالی است. راهنمایان متخصص ما اطمینان می‌دهند 
که بهترین معاملات و محصولات اصیل را دریافت می‌کنید.
"""
        tour.short_description = "از مرکز چرم برتر استانبول با فشن شو اختصاصی بازدید کنید و در مگا اوتلت شگفت‌انگیز خرید کنید - بدون ناهار."
        tour.highlights = """✨ نکات برجسته تور:

🛍️ بزرگترین مرکز صنعت چرم در استانبول
👗 فشن شو خصوصی اختصاصی
🏬 مرکز خرید مگا اوتلت
👜 محصولات و لوازم جانبی چرمی پریمیوم
🎁 فروشگاه سوغات با اقلام منحصر به فرد
💎 برندهای طراح بین‌المللی
🏷️ قیمت‌های بی‌نظیر اوتلت
🚌 حمل و نقل راحت
👥 تجربه گروه کوچک (حداکثر ۳۰ نفر)
🗣️ راهنمای خرید متخصص
📸 فرصت‌های عکاسی
⭐ محصولات اصیل ترکی"""
        
        tour.rules = """📋 قوانین تور:

🕘 ۳۰ دقیقه قبل از حرکت حاضر شوید
🎫 بلیط چاپی یا دیجیتال همراه داشته باشید
👟 کفش راحت برای پیاده‌روی بپوشید
💳 کارت اعتباری/بانکی بیاورید
💰 برای خریدهای کوچک پول نقد حمل کنید
🎒 کیسه خرید یا کوله‌پشتی بیاورید
📱 تلفن را شارژ نگه دارید
🚭 در مراکز خرید سیگار نکشید
👥 با گروه بمانید
⏰ برنامه را دنبال کنید
🛍️ قبل از خرید سیاست‌های بازگشت را بررسی کنید
💵 رسیدها را برای گمرک نگه دارید"""
        
        tour.required_items = """🎒 چیزهایی که باید بیاورید:

🎫 تأییدیه/بلیط تور
🆔 شناسنامه یا پاسپورت معتبر
👟 کفش راحت برای پیاده‌روی
💳 کارت‌های اعتباری/بانکی
💰 پول نقد (لیر ترکیه/دلار/یورو)
🎒 کیسه خرید یا کوله‌پشتی
📱 تلفن همراه + شارژر
📷 دوربین برای عکس
🧥 ژاکت سبک (برای تهویه مطبوع)
💧 بطری آب
🩹 داروهای شخصی
📝 لیست خرید
🌂 چتر (فصلی)"""
        tour.save()
        
        self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} tour: {tour.slug}")
        
        # Create variants
        variants_data = [
            ("ECONOMY", Decimal('30.00'), 15, "Economy package - Standard shopping experience"),
            ("STANDARD", Decimal('30.00'), 10, "Standard package - Enhanced shopping experience"),
            ("VIP", Decimal('30.00'), 5, "VIP package - Premium shopping experience with personal assistant"),
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
                    "includes_meal": False,
                    "includes_photographer": False,
                    "extended_hours": 0,
                    "private_transfer": name == "VIP",
                    "expert_guide": name == "VIP",
                    "special_meal": False,
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
                    "start_time": time(9, 30),
                    "end_time": time(17, 30),
                    "is_available": True,
                    "day_of_week": schedule_date.weekday(),
                }
            )
            schedule.initialize_variant_capacities()
            if created:
                self.stdout.write(f"✅ Created schedule: {schedule_date}")
        
        # Create itinerary
        self._create_itinerary(tour)
        
        # Create cancellation policies
        self._create_cancellation_policies(tour)
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 VENEZIA SHOPPING TOUR SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Tour: {tour.slug}")
        self.stdout.write(f"Languages: English, Turkish, Persian")
        self.stdout.write(f"Variants: {tour.variants.count()}")
        self.stdout.write(f"Schedules: {tour.schedules.count()}")
        self.stdout.write(f"Itinerary Items: {tour.itinerary.count()}")
        self.stdout.write(f"Cancellation Policies: {tour.cancellation_policies.count()}")
        self.stdout.write(self.style.SUCCESS("\n✅ Venezia Shopping Tour created successfully!"))
    
    def _create_itinerary(self, tour):
        """Create itinerary items with 3-language support"""
        itinerary_data = [
            {
                "order": 1,
                "duration": 30,
                "location": "Hotel Pickup",
                "en": {"title": "Hotel Pickup", 
                       "desc": "Comfortable pickup from your hotel in Istanbul."},
                "tr": {"title": "Otel Alımı", 
                       "desc": "İstanbul'daki otelinizden konforlu alım."},
                "fa": {"title": "پیکاپ از هتل", 
                       "desc": "پیکاپ راحت از هتل شما در استانبول."}
            },
            {
                "order": 2,
                "duration": 180,
                "location": "Leather Center",
                "en": {"title": "Leather Industry Center Visit", 
                       "desc": "Visit the largest leather center with exclusive fashion show and shopping."},
                "tr": {"title": "Deri Sanayi Merkezi Ziyareti", 
                       "desc": "Özel defile ve alışveriş ile en büyük deri merkezini ziyaret edin."},
                "fa": {"title": "بازدید از مرکز صنعت چرم", 
                       "desc": "بازدید از بزرگترین مرکز چرم با فشن شو اختصاصی و خرید."}
            },
            {
                "order": 3,
                "duration": 60,
                "location": "Fashion Show",
                "en": {"title": "Exclusive Fashion Show", 
                       "desc": "Enjoy a private fashion show featuring premium leather products."},
                "tr": {"title": "Özel Defile Gösterisi", 
                       "desc": "Premium deri ürünlerin yer aldığı özel bir defilenin tadını çıkarın."},
                "fa": {"title": "فشن شو اختصاصی", 
                       "desc": "از فشن شو خصوصی با محصولات چرمی پریمیوم لذت ببرید."}
            },
            {
                "order": 4,
                "duration": 180,
                "location": "Mega Outlet",
                "en": {"title": "Mega Outlet Shopping", 
                       "desc": "Shop at Istanbul's magnificent Mega Outlet with international brands."},
                "tr": {"title": "Mega Outlet Alışverişi", 
                       "desc": "Uluslararası markalarla İstanbul'un muhteşem Mega Outlet'inde alışveriş yapın."},
                "fa": {"title": "خرید در مگا اوتلت", 
                       "desc": "در مگا اوتلت شگفت‌انگیز استانبول با برندهای بین‌المللی خرید کنید."}
            },
            {
                "order": 5,
                "duration": 60,
                "location": "Souvenir Shop",
                "en": {"title": "Souvenir Shopping", 
                       "desc": "Browse unique Turkish souvenirs and gifts."},
                "tr": {"title": "Hediyelik Eşya Alışverişi", 
                       "desc": "Benzersiz Türk hediyelik eşyalarına ve hediyelerine göz atın."},
                "fa": {"title": "خرید سوغات", 
                       "desc": "سوغاتی‌ها و هدایای منحصر به فرد ترکی را مرور کنید."}
            },
            {
                "order": 6,
                "duration": 30,
                "location": "Hotel Drop-off",
                "en": {"title": "Return to Hotel", 
                       "desc": "Comfortable return to your hotel with your shopping bags."},
                "tr": {"title": "Otele Dönüş", 
                       "desc": "Alışveriş çantalarınızla otelinize konforlu dönüş."},
                "fa": {"title": "بازگشت به هتل", 
                       "desc": "بازگشت راحت به هتل با کیسه‌های خرید شما."}
            }
        ]
        
        for item_data in itinerary_data:
            # Delete existing item if it exists to avoid slug conflicts
            TourItinerary.objects.filter(tour=tour, order=item_data["order"]).delete()
            
            # Generate unique slug
            slug = f"{tour.slug}-stop-{item_data['order']}"
            
            # Create new item
            item = TourItinerary.objects.create(
                tour=tour,
                slug=slug,
                order=item_data["order"],
                duration_minutes=item_data["duration"],
                location=item_data["location"],
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
