from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from decimal import Decimal
from django.core.management import call_command

from tours.models import (
    Tour, TourVariant, TourSchedule, TourOption, 
    TourCategory, TourItinerary, TourCancellationPolicy
)


class Command(BaseCommand):
    help = "Create all 10 Istanbul tours with 3-language support"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating all Istanbul tours...")
        
        tours_data = [
            # Tour 1: Already created - Venezia Shopping
            # Tour 2: Already created - Princes Islands
            
            # Tour 3: Historical Tour
            {
                "slug": "istanbul-historical-tour",
                "category_slug": "historical-tours",
                "category_names": {
                    "en": "Historical Tours",
                    "tr": "Tarihi Turlar",
                    "fa": "تورهای تاریخی"
                },
                "titles": {
                    "en": "Istanbul Historical Tour - Mosques & Balat",
                    "tr": "İstanbul Tarihi Turu - Camiler ve Balat",
                    "fa": "تور تاریخی استانبول - مساجد و بالات"
                },
                "descriptions": {
                    "en": "Explore Istanbul's rich history with visits to Sultan Ahmed Mosque (Blue Mosque), Suleymaniye Mosque complex including courtyards, tombs, and terrace overlooking the Bosphorus, and the colorful Balat neighborhood with Çukur filming locations. Lunch included at a shopping center.",
                    "tr": "Sultan Ahmet Camii (Mavi Cami), avlu, türbeler ve Boğaz'a bakan teras dahil Süleymaniye Camii kompleksi ve Çukur çekim lokasyonları ile renkli Balat semtini ziyaret ederek İstanbul'un zengin tarihini keşfedin. Alışveriş merkezinde öğle yemeği dahil.",
                    "fa": "تاریخ غنی استانبول را با بازدید از مسجد سلطان احمد (مسجد آبی)، مجموعه مسجد سلیمانیه شامل حیاط‌ها، مقبره‌ها و تراس رو به بسفر، و محله رنگارنگ بالات با لوکیشن‌های فیلمبرداری چوکور کشف کنید. ناهار در مرکز خرید شامل است."
                },
                "short_descriptions": {
                    "en": "Visit Sultan Ahmed & Suleymaniye Mosques, explore colorful Balat neighborhood with Çukur locations, lunch at shopping center.",
                    "tr": "Sultan Ahmet ve Süleymaniye Camilerini ziyaret edin, Çukur lokasyonları ile renkli Balat semtini keşfedin, alışveriş merkezinde öğle yemeği.",
                    "fa": "بازدید از مساجد سلطان احمد و سلیمانیه، کاوش محله رنگارنگ بالات با لوکیشن‌های چوکور، ناهار در مرکز خرید."
                },
                "tour_type": "day",
                "transport_type": "land",
                "duration_hours": 8,
                "includes_meal": True,
            },
            
            # Tour 4: Bosphorus Night Cruise
            {
                "slug": "bosphorus-night-cruise-iranian",
                "category_slug": "night-tours",
                "category_names": {
                    "en": "Night Tours",
                    "tr": "Gece Turları",
                    "fa": "تورهای شبانه"
                },
                "titles": {
                    "en": "Bosphorus Night Cruise - Iranian Special",
                    "tr": "Boğaz Gece Gezisi - İran Özel",
                    "fa": "کروز شبانه بسفر - ویژه ایرانی"
                },
                "descriptions": {
                    "en": "An unforgettable and memorable Iranian night! Cruise along the Bosphorus with live music by talented singers, oriental dance performances, unlimited non-alcoholic beverages, dinner, dessert, and alcoholic drinks. A perfect evening experience.",
                    "tr": "Unutulmaz ve akılda kalıcı bir İran gecesi! Yetenekli şarkıcılar tarafından canlı müzik, oryantal dans gösterileri, sınırsız alkolsüz içecekler, akşam yemeği, tatlı ve alkollü içeceklerle Boğaz'da gezi yapın. Mükemmel bir akşam deneyimi.",
                    "fa": "یک شب خاطره‌انگیز و به یادماندنی ایرانی! کروز در امتداد بسفر با موسیقی زنده توسط خوانندگان با استعداد، اجرای رقص شرقی، نوشیدنی‌های غیرالکلی نامحدود، شام، دسر و نوشیدنی‌های الکلی. یک تجربه عالی شبانه."
                },
                "short_descriptions": {
                    "en": "Bosphorus cruise with live music, oriental dance, dinner, dessert, and unlimited drinks - Iranian special night.",
                    "tr": "Canlı müzik, oryantal dans, akşam yemeği, tatlı ve sınırsız içeceklerle Boğaz gezisi - İran özel gecesi.",
                    "fa": "کروز بسفر با موسیقی زنده، رقص شرقی، شام، دسر و نوشیدنی‌های نامحدود - شب ویژه ایرانی."
                },
                "tour_type": "night",
                "transport_type": "boat",
                "duration_hours": 4,
                "pickup_time": time(19, 30),
                "start_time": time(20, 0),
                "end_time": time(23, 59),
                "includes_meal": True,
            },
            
            # Tour 5: Sapanca Nature Tour
            {
                "slug": "sapanca-nature-tour",
                "category_slug": "nature-tours",
                "category_names": {
                    "en": "Nature Tours",
                    "tr": "Doğa Turları",
                    "fa": "تورهای طبیعت"
                },
                "titles": {
                    "en": "Sapanca Nature Tour - Forest & Lake",
                    "tr": "Sapanca Doğa Turu - Orman ve Göl",
                    "fa": "تور طبیعت ساپانجا - جنگل و دریاچه"
                },
                "descriptions": {
                    "en": "Visit Istanbul's largest and most pristine forest known as Maşukiye. Experience the glass terrace (Jump Terrace) at Kartepe mountain peak, extra time for safari and zipline activities, and the freshwater Sapanca Lake. Lunch included at a forest restaurant.",
                    "tr": "Maşukiye olarak bilinen İstanbul'un en büyük ve en bozulmamış ormanını ziyaret edin. Kartepe dağı zirvesindeki cam terası (Jump Terrace) deneyimleyin, safari ve zipline aktiviteleri için ekstra zaman, ve tatlı su Sapanca Gölü. Orman restoranında öğle yemeği dahil.",
                    "fa": "از بزرگترین و بکرترین جنگل استانبول معروف به معشوقیه بازدید کنید. تراس شیشه‌ای (جامپ تراس) در قله کوه کارتپه را تجربه کنید، زمان اضافی برای فعالیت‌های سافاری و زیپ لاین، و دریاچه آب شیرین ساپانجا. ناهار در رستوران جنگلی شامل است."
                },
                "short_descriptions": {
                    "en": "Visit Maşukiye forest, Jump Terrace at Kartepe peak, safari & zipline time, Sapanca Lake, lunch at forest restaurant.",
                    "tr": "Maşukiye ormanını ziyaret edin, Kartepe zirvesinde Jump Terrace, safari ve zipline zamanı, Sapanca Gölü, orman restoranında öğle yemeği.",
                    "fa": "بازدید از جنگل معشوقیه، جامپ تراس در قله کارتپه، زمان سافاری و زیپ لاین، دریاچه ساپانجا، ناهار در رستوران جنگلی."
                },
                "tour_type": "day",
                "transport_type": "land",
                "duration_hours": 9,
                "includes_meal": True,
            },
            
            # Tour 6: Istanbul City Tour
            {
                "slug": "istanbul-city-tour",
                "category_slug": "city-tours",
                "category_names": {
                    "en": "City Tours",
                    "tr": "Şehir Turları",
                    "fa": "تورهای شهری"
                },
                "titles": {
                    "en": "Istanbul City Tour - Highlights & Shopping",
                    "tr": "İstanbul Şehir Turu - Öne Çıkanlar ve Alışveriş",
                    "fa": "تور شهر استانبول - نقاط برجسته و خرید"
                },
                "descriptions": {
                    "en": "Explore Istanbul's highlights: Ortaköy coast and Mecidiye Mosque, Beşiktaş neighborhood and Bosphorus Bridge crossing (Bridge of Wishes), Beylerbeyi coast and Maiden's Tower, Optimum shopping center (no lunch), Çamlıca Hill, and Polat shopping center.",
                    "tr": "İstanbul'un öne çıkanlarını keşfedin: Ortaköy sahili ve Mecidiye Camii, Beşiktaş semti ve Boğaziçi Köprüsü geçişi (Dilekler Köprüsü), Beylerbeyi sahili ve Kız Kulesi, Optimum alışveriş merkezi (öğle yemeği yok), Çamlıca Tepesi ve Polat alışveriş merkezi.",
                    "fa": "نقاط برجسته استانبول را کشف کنید: ساحل اورتاکوی و مسجد مجیدیه، محله بشیکتاش و عبور از پل بسفر (پل آرزوها), ساحل بیلربی و برج دختر، مرکز خرید اوپتیموم (بدون ناهار)، تپه چاملیجا و مرکز خرید پولات."
                },
                "short_descriptions": {
                    "en": "Visit Ortaköy, Beşiktaş, Bosphorus Bridge, Maiden's Tower, Optimum center, Çamlıca Hill, Polat center - no lunch.",
                    "tr": "Ortaköy, Beşiktaş, Boğaziçi Köprüsü, Kız Kulesi, Optimum merkez, Çamlıca Tepesi, Polat merkez ziyareti - öğle yemeği yok.",
                    "fa": "بازدید از اورتاکوی، بشیکتاش، پل بسفر، برج دختر، مرکز اوپتیموم، تپه چاملیجا، مرکز پولات - بدون ناهار."
                },
                "tour_type": "day",
                "transport_type": "land",
                "duration_hours": 8,
                "includes_meal": False,
            },
            
            # Tour 7: Turkish Nights Tavern
            {
                "slug": "turkish-nights-tavern",
                "category_slug": "night-entertainment",
                "category_names": {
                    "en": "Night Entertainment",
                    "tr": "Gece Eğlencesi",
                    "fa": "سرگرمی شبانه"
                },
                "titles": {
                    "en": "Turkish Nights Tavern - Dinner & Dance",
                    "tr": "Türk Geceleri Meyhanesi - Yemek ve Dans",
                    "fa": "میخانه شب‌های ترک - شام و رقص"
                },
                "descriptions": {
                    "en": "Enjoy Turkish nights alone or with family! Iranian and Turkish DJ, dinner with oriental dance, alcoholic beverages, and variety of Turkish appetizers and starters. Round-trip transfer included. Perfect for a fun evening experience.",
                    "tr": "Türk gecelerinin tadını yalnız veya ailenizle çıkarın! İranlı ve Türk DJ, oryantal dansla akşam yemeği, alkollü içecekler ve çeşitli Türk meze ve başlangıçları. Gidiş-dönüş transfer dahil. Eğlenceli bir akşam deneyimi için mükemmel.",
                    "fa": "از شب‌های ترک به تنهایی یا با خانواده لذت ببرید! DJ ایرانی و ترک، شام با رقص شرقی، نوشیدنی‌های الکلی و انواع مزه و پیش غذاهای ترکی. ترانسفر رفت و برگشت شامل است. برای یک تجربه شبانه سرگرم‌کننده عالی است."
                },
                "short_descriptions": {
                    "en": "Iranian & Turkish DJ, dinner with oriental dance, alcoholic drinks, Turkish appetizers, round-trip transfer.",
                    "tr": "İranlı ve Türk DJ, oryantal dansla akşam yemeği, alkollü içecekler, Türk mezeleri, gidiş-dönüş transfer.",
                    "fa": "DJ ایرانی و ترک، شام با رقص شرقی، نوشیدنی‌های الکلی، مزه‌های ترکی، ترانسفر رفت و برگشت."
                },
                "tour_type": "night",
                "transport_type": "land",
                "duration_hours": 4,
                "pickup_time": time(19, 30),
                "start_time": time(20, 0),
                "end_time": time(23, 59),
                "includes_meal": True,
            },
            
            # Tour 8: Aquarium Tour
            {
                "slug": "istanbul-aquarium-tour",
                "category_slug": "family-tours",
                "category_names": {
                    "en": "Family Tours",
                    "tr": "Aile Turları",
                    "fa": "تورهای خانوادگی"
                },
                "titles": {
                    "en": "Istanbul Aquarium Tour - Balat & Amazon",
                    "tr": "İstanbul Akvaryum Turu - Balat ve Amazon",
                    "fa": "تور آکواریوم استانبول - بالات و آمازون"
                },
                "descriptions": {
                    "en": "Visit the colorful Balat neighborhood and Suleymaniye Mosque, explore the Aquarium center with simulated Amazon forests, and shop at Star City center. Lunch included. Perfect for families with children.",
                    "tr": "Renkli Balat semtini ve Süleymaniye Camii'ni ziyaret edin, simüle edilmiş Amazon ormanları ile Akvaryum merkezini keşfedin ve Star City merkezinde alışveriş yapın. Öğle yemeği dahil. Çocuklu aileler için mükemmel.",
                    "fa": "از محله رنگارنگ بالات و مسجد سلیمانیه بازدید کنید، مرکز آکواریوم را با جنگل‌های شبیه‌سازی شده آمازون کشف کنید و در مرکز استار سیتی خرید کنید. ناهار شامل است. برای خانواده‌ها با کودکان عالی است."
                },
                "short_descriptions": {
                    "en": "Visit Balat & Suleymaniye Mosque, Aquarium with Amazon forests, Star City shopping, lunch included.",
                    "tr": "Balat ve Süleymaniye Camii ziyareti, Amazon ormanları ile Akvaryum, Star City alışverişi, öğle yemeği dahil.",
                    "fa": "بازدید از بالات و مسجد سلیمانیه، آکواریوم با جنگل‌های آمازون، خرید استار سیتی، ناهار شامل است."
                },
                "tour_type": "day",
                "transport_type": "land",
                "duration_hours": 8,
                "includes_meal": True,
            },
            
            # Tour 9: Bosphorus Nights Luxury
            {
                "slug": "bosphorus-nights-luxury",
                "category_slug": "night-tours",
                "category_names": {
                    "en": "Night Tours",
                    "tr": "Gece Turları",
                    "fa": "تورهای شبانه"
                },
                "titles": {
                    "en": "Bosphorus Nights - Luxury Evening Tour",
                    "tr": "Boğaz Geceleri - Lüks Akşam Turu",
                    "fa": "شب‌های بسفر - تور شبانه لوکس"
                },
                "descriptions": {
                    "en": "A luxurious and peaceful evening tour with stunning views. Visit Galata Port with waterfront promenade, open-air cafes and brand stores, Ortaköy coast and famous mosque by the bridge, photo opportunities with Bosphorus Bridge background, Duatepe, Beşiktaş coast, and Koka restaurant.",
                    "tr": "Muhteşem manzaralı lüks ve huzurlu bir akşam turu. İskele kenarında yürüyüş, açık hava kafeleri ve marka mağazaları ile Galata Port'u, köprü yanındaki ünlü cami ile Ortaköy sahilini, Boğaziçi Köprüsü arka planıyla fotoğraf fırsatlarını, Duatepe'yi, Beşiktaş sahilini ve Koka restoranını ziyaret edin.",
                    "fa": "یک تور شبانه لوکس و آرام با مناظر خیره‌کننده. بازدید از گالاتا پورت با پیاده‌روی کنار اسکله، کافه‌های فضای باز و فروشگاه‌های برند، ساحل اورتاکوی و مسجد معروف کنار پل، فرصت‌های عکاسی با پس‌زمینه پل بسفر، دوعاتپه، ساحل بشیکتاش و رستوران کوکا."
                },
                "short_descriptions": {
                    "en": "Luxury evening: Galata Port, Ortaköy mosque, Bosphorus Bridge photos, Duatepe, Beşiktaş coast, Koka restaurant.",
                    "tr": "Lüks akşam: Galata Port, Ortaköy camii, Boğaziçi Köprüsü fotoğrafları, Duatepe, Beşiktaş sahili, Koka restoranı.",
                    "fa": "شب لوکس: گالاتا پورت، مسجد اورتاکوی، عکس‌های پل بسفر، دوعاتپه، ساحل بشیکتاش، رستوران کوکا."
                },
                "tour_type": "night",
                "transport_type": "land",
                "duration_hours": 4,
                "pickup_time": time(19, 0),
                "start_time": time(19, 30),
                "end_time": time(23, 30),
                "includes_meal": False,
            },
        ]
        
        for tour_data in tours_data:
            self._create_tour(tour_data)
        
        self.stdout.write(self.style.SUCCESS("\n✅ All Istanbul tours created successfully!"))
    
    def _create_tour(self, data):
        """Create a single tour with all details"""
        self.stdout.write(f"\n🚀 Creating {data['slug']}...")
        
        # Create or get category
        category, _ = TourCategory.objects.get_or_create(
            slug=data['category_slug'],
            defaults={"name": data['category_names']['en']}
        )
        
        # Set category translations
        for lang in ['en', 'tr', 'fa']:
            category.set_current_language(lang)
            category.name = data['category_names'][lang]
            category.description = data['category_names'][lang]
            category.save()
        
        # Create tour
        tour, created = Tour.objects.get_or_create(
            slug=data['slug'],
            defaults={
                "price": Decimal('30.00'),
                "currency": "USD",
                "duration_hours": data.get('duration_hours', 8),
                "pickup_time": data.get('pickup_time', time(9, 0)),
                "start_time": data.get('start_time', time(9, 30)),
                "end_time": data.get('end_time', time(17, 30)),
                "min_participants": 1,
                "max_participants": 30,
                "booking_cutoff_hours": 24,
                "cancellation_hours": 48,
                "refund_percentage": 80,
                "includes_transfer": True,
                "includes_guide": True,
                "includes_meal": data.get('includes_meal', True),
                "includes_photographer": False,
                "tour_type": data.get('tour_type', 'day'),
                "transport_type": data.get('transport_type', 'land'),
                "is_active": True,
                "is_featured": True,
                "is_popular": True,
                "city": "Istanbul",
                "country": "Turkey",
                "category": category,
            }
        )
        
        # Set tour translations with highlights, rules, and required items
        for lang in ['en', 'tr', 'fa']:
            tour.set_current_language(lang)
            tour.title = data['titles'][lang]
            tour.description = data['descriptions'][lang]
            tour.short_description = data['short_descriptions'][lang]
            
            # Set highlights, rules, and required items if provided
            if 'highlights' in data and lang in data['highlights']:
                tour.highlights = data['highlights'][lang]
            if 'rules' in data and lang in data['rules']:
                tour.rules = data['rules'][lang]
            if 'required_items' in data and lang in data['required_items']:
                tour.required_items = data['required_items'][lang]
            
            tour.save()
        
        self.stdout.write(f"{'✅ Created' if created else '📋 Updated'} tour: {tour.slug}")
        
        # Create itinerary if provided
        if 'itinerary' in data:
            self._create_tour_itinerary(tour, data['itinerary'])
        
        # Create variants
        variants_data = [
            ("ECONOMY", Decimal('30.00'), 15, "Economy package"),
            ("STANDARD", Decimal('30.00'), 10, "Standard package"),
            ("VIP", Decimal('30.00'), 5, "VIP package"),
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
                    "includes_meal": data.get('includes_meal', True),
                    "includes_photographer": False,
                    "extended_hours": 0,
                    "private_transfer": name == "VIP",
                    "expert_guide": name == "VIP",
                    "special_meal": name == "VIP",
                }
            )
        
        # Create schedules for next 14 days
        base_date = timezone.now().date()
        for i in range(14):
            schedule_date = base_date + timezone.timedelta(days=i)
            schedule, created = TourSchedule.objects.get_or_create(
                tour=tour,
                start_date=schedule_date,
                defaults={
                    "end_date": schedule_date,
                    "start_time": data.get('start_time', time(9, 30)),
                    "end_time": data.get('end_time', time(17, 30)),
                    "is_available": True,
                    "day_of_week": schedule_date.weekday(),
                }
            )
            schedule.initialize_variant_capacities()
        
        # Create cancellation policies
        policies_data = [
            (72, 100, "Full refund up to 72 hours before tour start"),
            (48, 80, "80% refund up to 48 hours before tour start"),
            (24, 50, "50% refund up to 24 hours before tour start"),
            (0, 0, "No refund less than 24 hours before tour start"),
        ]
        
        for hours, refund, desc in policies_data:
            TourCancellationPolicy.objects.get_or_create(
                tour=tour,
                hours_before=hours,
                defaults={
                    "refund_percentage": refund,
                    "description": desc,
                    "is_active": True,
                }
            )
    
    def _create_tour_itinerary(self, tour, itinerary_data):
        """Create itinerary items for a tour"""
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
            
            # Set translations
            for lang in ['en', 'tr', 'fa']:
                item.set_current_language(lang)
                item.title = item_data[lang]["title"]
                item.description = item_data[lang]["desc"]
                item.save()
            
            self.stdout.write(f"  ✅ Created itinerary item {item_data['order']}")
