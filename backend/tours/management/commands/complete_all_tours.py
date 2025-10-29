from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from decimal import Decimal
from tours.models import Tour, TourVariant, TourSchedule, TourItinerary, TourCancellationPolicy


class Command(BaseCommand):
    help = "Complete all incomplete tours with highlights, rules, required items, and itinerary"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Completing all incomplete tours...")
        
        # List of tours to complete
        tours_to_complete = [
            'bosphorus-night-cruise-iranian',
            'bosphorus-nights-luxury',
            'istanbul-aquarium-tour',
            'istanbul-city-tour',
            'sapanca-nature-tour',
            'turkish-nights-tavern',
            'princes-islands-cruise',
            'istanbul-bosphorus-cruise',
        ]
        
        for slug in tours_to_complete:
            try:
                tour = Tour.objects.get(slug=slug)
                self.stdout.write(f"\n{'='*80}")
                self.stdout.write(f"🔧 Updating: {slug}")
                self.stdout.write(f"{'='*80}")
                
                # Get the completion method for this tour
                method_name = f"_complete_{slug.replace('-', '_')}"
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method(tour)
                    self.stdout.write(self.style.SUCCESS(f"✅ Completed: {slug}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ No completion method for: {slug}"))
            except Tour.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Tour not found: {slug}"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ All tours completed!"))

    def _complete_bosphorus_night_cruise_iranian(self, tour):
        """Complete Bosphorus Night Cruise - Iranian Special"""
        # English
        tour.set_current_language('en')
        tour.highlights = """✨ Tour Highlights:

🚢 Private Bosphorus cruise
🎵 Live music by talented singers
💃 Oriental dance performances
🍽️ Dinner with Turkish cuisine
🍰 Desserts included
🍹 Unlimited non-alcoholic beverages
🍷 Alcoholic drinks available
🌃 Stunning night views
🎭 Iranian special atmosphere
👥 Small group (max 30)
🌉 Bosphorus Bridge illuminated
⭐ Memorable evening experience"""
        
        tour.rules = """📋 Tour Rules:

🕘 Arrive 30 minutes before departure
🎫 Bring printed or digital ticket
👗 Smart casual dress code
📱 Keep phone charged
🚭 Designated smoking areas only
📷 Photography allowed
👥 Stay with the group
⏰ Follow the schedule
🎵 Respect performers
🍽️ No outside food/drinks
🚫 No inappropriate behavior
🎉 Enjoy responsibly"""
        
        tour.required_items = """🎒 What to Bring:

🎫 Tour confirmation/ticket
🆔 Valid ID or passport
👗 Smart casual attire
🧥 Light jacket (for deck)
📱 Mobile phone + charger
📷 Camera for photos
💰 Cash for extras
💳 Credit/debit card
🩹 Personal medications
🎒 Small bag
🌂 Light shawl (optional)"""
        tour.save()
        
        # Turkish
        tour.set_current_language('tr')
        tour.highlights = """✨ Tur Öne Çıkanları:

🚢 Özel Boğaz gezisi
🎵 Yetenekli şarkıcılar tarafından canlı müzik
💃 Oryantal dans gösterileri
🍽️ Türk mutfağı ile akşam yemeği
🍰 Tatlılar dahil
🍹 Sınırsız alkolsüz içecekler
🍷 Alkollü içecekler mevcut
🌃 Muhteşem gece manzaraları
🎭 İran özel atmosferi
👥 Küçük grup (maks 30)
🌉 Aydınlatılmış Boğaziçi Köprüsü
⭐ Unutulmaz akşam deneyimi"""
        
        tour.rules = """📋 Tur Kuralları:

🕘 Kalkıştan 30 dakika önce gelin
🎫 Basılı veya dijital bilet getirin
👗 Şık günlük kıyafet
📱 Telefonu şarjlı tutun
🚭 Sadece sigara içme alanları
📷 Fotoğraf çekebilirsiniz
👥 Grupla kalın
⏰ Programı takip edin
🎵 Sanatçılara saygı gösterin
🍽️ Dışarıdan yiyecek/içecek yok
🚫 Uygunsuz davranış yok
🎉 Sorumlu bir şekilde eğlenin"""
        
        tour.required_items = """🎒 Getirmeniz Gerekenler:

🎫 Tur onayı/bilet
🆔 Geçerli kimlik veya pasaport
👗 Şık günlük kıyafet
🧥 Hafif ceket (güverte için)
📱 Cep telefonu + şarj aleti
📷 Fotoğraf için kamera
💰 Ekstralar için nakit
💳 Kredi/banka kartı
🩹 Kişisel ilaçlar
🎒 Küçük çanta
🌂 Hafif şal (isteğe bağlı)"""
        tour.save()
        
        # Persian
        tour.set_current_language('fa')
        tour.highlights = """✨ نکات برجسته تور:

🚢 کروز خصوصی بسفر
🎵 موسیقی زنده توسط خوانندگان با استعداد
💃 اجرای رقص شرقی
🍽️ شام با غذای ترکی
🍰 دسرها شامل است
🍹 نوشیدنی‌های غیرالکلی نامحدود
🍷 نوشیدنی‌های الکلی موجود است
🌃 مناظر شبانه خیره‌کننده
🎭 فضای ویژه ایرانی
👥 گروه کوچک (حداکثر ۳۰ نفر)
🌉 پل بسفر روشن شده
⭐ تجربه شبانه به یادماندنی"""
        
        tour.rules = """📋 قوانین تور:

🕘 ۳۰ دقیقه قبل از حرکت حاضر شوید
🎫 بلیط چاپی یا دیجیتال همراه داشته باشید
👗 لباس رسمی غیررسمی
📱 تلفن را شارژ نگه دارید
🚭 فقط مناطق سیگار مشخص شده
📷 عکاسی مجاز است
👥 با گروه بمانید
⏰ برنامه را دنبال کنید
🎵 به هنرمندان احترام بگذارید
🍽️ غذا/نوشیدنی از بیرون ممنوع
🚫 رفتار نامناسب ممنوع
🎉 مسئولانه لذت ببرید"""
        
        tour.required_items = """🎒 چیزهایی که باید بیاورید:

🎫 تأییدیه/بلیط تور
🆔 شناسنامه یا پاسپورت معتبر
👗 لباس رسمی غیررسمی
🧥 ژاکت سبک (برای عرشه)
📱 تلفن همراه + شارژر
📷 دوربین برای عکس
💰 پول نقد برای موارد اضافی
💳 کارت اعتباری/بانکی
🩹 داروهای شخصی
🎒 کیف کوچک
🌂 شال سبک (اختیاری)"""
        tour.save()
        
        # Create itinerary
        self._create_itinerary(tour, [
            {
                "order": 1, "duration": 30, "location": "Hotel Pickup",
                "en": {"title": "Hotel Pickup", "desc": "Pickup from your hotel and transfer to the boat."},
                "tr": {"title": "Otel Alımı", "desc": "Otelinizden alım ve tekneye transfer."},
                "fa": {"title": "پیکاپ از هتل", "desc": "پیکاپ از هتل و انتقال به قایق."}
            },
            {
                "order": 2, "duration": 60, "location": "Bosphorus",
                "en": {"title": "Welcome & Cruise Start", "desc": "Board the boat, welcome drinks, and cruise begins along the Bosphorus."},
                "tr": {"title": "Karşılama ve Gezi Başlangıcı", "desc": "Tekneye binin, karşılama içecekleri ve Boğaz boyunca gezi başlar."},
                "fa": {"title": "خوش‌آمدگویی و شروع کروز", "desc": "سوار قایق شوید، نوشیدنی‌های خوش‌آمدگویی و کروز در امتداد بسفر شروع می‌شود."}
            },
            {
                "order": 3, "duration": 90, "location": "Dinner",
                "en": {"title": "Dinner Service", "desc": "Enjoy delicious Turkish dinner with appetizers, main course, and desserts."},
                "tr": {"title": "Akşam Yemeği Servisi", "desc": "Mezeler, ana yemek ve tatlılarla lezzetli Türk akşam yemeğinin tadını çıkarın."},
                "fa": {"title": "سرویس شام", "desc": "از شام خوشمزه ترکی با پیش غذا، غذای اصلی و دسرها لذت ببرید."}
            },
            {
                "order": 4, "duration": 60, "location": "Entertainment",
                "en": {"title": "Live Music & Dance", "desc": "Live music performances and oriental dance show."},
                "tr": {"title": "Canlı Müzik ve Dans", "desc": "Canlı müzik performansları ve oryantal dans gösterisi."},
                "fa": {"title": "موسیقی زنده و رقص", "desc": "اجراهای موسیقی زنده و نمایش رقص شرقی."}
            },
            {
                "order": 5, "duration": 30, "location": "Return",
                "en": {"title": "Return to Hotel", "desc": "Disembark and transfer back to your hotel."},
                "tr": {"title": "Otele Dönüş", "desc": "Karaya çıkın ve otelinize geri dönün."},
                "fa": {"title": "بازگشت به هتل", "desc": "پیاده شوید و به هتل خود برگردید."}
            }
        ])

    def _create_itinerary(self, tour, itinerary_data):
        """Create itinerary items for a tour"""
        TourItinerary.objects.filter(tour=tour).delete()
        for item_data in itinerary_data:
            slug = f"{tour.slug}-stop-{item_data['order']}"
            item = TourItinerary.objects.create(
                tour=tour, slug=slug, order=item_data["order"],
                duration_minutes=item_data["duration"], location=item_data["location"]
            )
            for lang in ['en', 'tr', 'fa']:
                item.set_current_language(lang)
                item.title = item_data[lang]["title"]
                item.description = item_data[lang]["desc"]
                item.save()
            self.stdout.write(f"  ✅ Created itinerary item {item_data['order']}")
