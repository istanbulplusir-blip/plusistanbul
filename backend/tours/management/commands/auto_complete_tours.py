from django.core.management.base import BaseCommand
from tours.models import Tour, TourItinerary


class Command(BaseCommand):
    help = "Auto-complete all tours by checking and adding missing content"

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking all tours for missing content...")
        self.stdout.write("="*80)
        
        tours = Tour.objects.all().order_by('slug')
        
        for tour in tours:
            self.stdout.write(f"\n{'='*80}")
            self.stdout.write(f"🎯 Checking: {tour.slug}")
            self.stdout.write(f"{'='*80}")
            
            # Check what's missing
            tour.set_current_language('en')
            needs_highlights = not tour.highlights
            needs_rules = not tour.rules
            needs_items = not tour.required_items
            needs_itinerary = tour.itinerary.count() < 4
            
            if not (needs_highlights or needs_rules or needs_items or needs_itinerary):
                self.stdout.write(self.style.SUCCESS(f"✅ {tour.slug} is complete!"))
                continue
            
            self.stdout.write(f"⚠️ Missing content:")
            if needs_highlights: self.stdout.write("   - Highlights")
            if needs_rules: self.stdout.write("   - Rules")
            if needs_items: self.stdout.write("   - Required Items")
            if needs_itinerary: self.stdout.write(f"   - Itinerary (has {tour.itinerary.count()}, needs 4+)")
            
            # Get completion method
            method_name = f"_complete_{tour.slug.replace('-', '_')}"
            if hasattr(self, method_name):
                self.stdout.write(f"🔧 Completing {tour.slug}...")
                method = getattr(self, method_name)
                method(tour)
                self.stdout.write(self.style.SUCCESS(f"✅ Completed: {tour.slug}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ No auto-completion available for: {tour.slug}"))
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("✅ Tour check complete!"))


    def _add_content(self, tour, highlights_en, highlights_tr, highlights_fa,
                     rules_en, rules_tr, rules_fa, items_en, items_tr, items_fa):
        """Add highlights, rules, and required items to tour"""
        tour.set_current_language('en')
        if not tour.highlights: tour.highlights = highlights_en
        if not tour.rules: tour.rules = rules_en
        if not tour.required_items: tour.required_items = items_en
        tour.save()
        
        tour.set_current_language('tr')
        if not tour.highlights: tour.highlights = highlights_tr
        if not tour.rules: tour.rules = rules_tr
        if not tour.required_items: tour.required_items = items_tr
        tour.save()
        
        tour.set_current_language('fa')
        if not tour.highlights: tour.highlights = highlights_fa
        if not tour.rules: tour.rules = rules_fa
        if not tour.required_items: tour.required_items = items_fa
        tour.save()

    def _add_itinerary(self, tour, items):
        """Add itinerary to tour"""
        if tour.itinerary.count() >= 4:
            return
        TourItinerary.objects.filter(tour=tour).delete()
        for order, duration, location, en_t, tr_t, fa_t, en_d, tr_d, fa_d in items:
            slug = f'{tour.slug}-stop-{order}'
            item = TourItinerary.objects.create(
                tour=tour, slug=slug, order=order,
                duration_minutes=duration, location=location
            )
            for lang, title, desc in [('en', en_t, en_d), ('tr', tr_t, tr_d), ('fa', fa_t, fa_d)]:
                item.set_current_language(lang)
                item.title = title
                item.description = desc
                item.save()
        self.stdout.write(f"  ✅ Added {len(items)} itinerary items")


    def _complete_bosphorus_night_cruise_iranian(self, tour):
        """Complete Bosphorus Night Cruise - Iranian"""
        self._add_content(tour,
            # English
            """✨ Highlights: 🚢 Bosphorus cruise 🎵 Live music 💃 Oriental dance 🍽️ Dinner 🍹 Drinks 🌃 Night views 🎭 Iranian atmosphere 👥 Small group 🌉 Illuminated bridge ⭐ Memorable evening""",
            # Turkish  
            """✨ Öne Çıkanlar: 🚢 Boğaz gezisi 🎵 Canlı müzik 💃 Oryantal dans 🍽️ Akşam yemeği 🍹 İçecekler 🌃 Gece manzaraları 🎭 İran atmosferi 👥 Küçük grup 🌉 Aydınlatılmış köprü ⭐ Unutulmaz akşam""",
            # Persian
            """✨ نکات برجسته: 🚢 کروز بسفر 🎵 موسیقی زنده 💃 رقص شرقی 🍽️ شام 🍹 نوشیدنی 🌃 مناظر شبانه 🎭 فضای ایرانی 👥 گروه کوچک 🌉 پل روشن ⭐ شب به یادماندنی""",
            # Rules EN
            """📋 Rules: 🕘 Arrive 30min early 🎫 Bring ticket 👗 Smart casual 📱 Phone charged 🚭 Smoking areas only 📷 Photos allowed 👥 Stay with group ⏰ Follow schedule 🎵 Respect performers 🍽️ No outside food 🚫 Appropriate behavior 🎉 Enjoy responsibly""",
            # Rules TR
            """📋 Kurallar: 🕘 30dk önce gelin 🎫 Bilet getirin 👗 Şık günlük 📱 Telefon şarjlı 🚭 Sadece sigara alanları 📷 Fotoğraf serbest 👥 Grupla kalın ⏰ Programı takip edin 🎵 Sanatçılara saygı 🍽️ Dışarıdan yiyecek yok 🚫 Uygun davranış 🎉 Sorumlu eğlenin""",
            # Rules FA
            """📋 قوانین: 🕘 ۳۰ دقیقه زودتر 🎫 بلیط بیاورید 👗 لباس رسمی 📱 تلفن شارژ 🚭 فقط مناطق سیگار 📷 عکس مجاز 👥 با گروه بمانید ⏰ برنامه را دنبال کنید 🎵 احترام به هنرمندان 🍽️ غذای بیرون ممنوع 🚫 رفتار مناسب 🎉 مسئولانه لذت ببرید""",
            # Items EN
            """🎒 Bring: 🎫 Ticket 🆔 ID 👗 Smart attire 🧥 Jacket 📱 Phone+charger 📷 Camera 💰 Cash 💳 Card 🩹 Medications 🎒 Small bag""",
            # Items TR
            """🎒 Getirin: 🎫 Bilet 🆔 Kimlik 👗 Şık kıyafet 🧥 Ceket 📱 Telefon+şarj 📷 Kamera 💰 Nakit 💳 Kart 🩹 İlaçlar 🎒 Küçük çanta""",
            # Items FA
            """🎒 بیاورید: 🎫 بلیط 🆔 شناسنامه 👗 لباس رسمی 🧥 ژاکت 📱 تلفن+شارژر 📷 دوربین 💰 نقدی 💳 کارت 🩹 دارو 🎒 کیف کوچک"""
        )
        self._add_itinerary(tour, [
            (1, 30, 'Hotel', 'Hotel Pickup', 'Otel Alımı', 'پیکاپ هتل', 'Pickup from hotel', 'Otelden alım', 'پیکاپ از هتل'),
            (2, 60, 'Boat', 'Board & Welcome', 'Biniş ve Karşılama', 'سوار شدن و خوش‌آمد', 'Board boat, welcome drinks', 'Tekneye biniş, karşılama', 'سوار قایق، خوش‌آمد'),
            (3, 90, 'Dining', 'Dinner Service', 'Akşam Yemeği', 'سرویس شام', 'Turkish dinner with appetizers', 'Mezelerle Türk yemeği', 'شام ترکی با پیش غذا'),
            (4, 60, 'Entertainment', 'Live Show', 'Canlı Gösteri', 'نمایش زنده', 'Live music and dance', 'Canlı müzik ve dans', 'موسیقی و رقص زنده'),
            (5, 30, 'Return', 'Hotel Return', 'Otele Dönüş', 'بازگشت هتل', 'Return to hotel', 'Otele dönüş', 'بازگشت به هتل')
        ])

    def _complete_bosphorus_nights_luxury(self, tour):
        """Complete Bosphorus Nights Luxury"""
        self._add_content(tour,
            """✨ Highlights: 🌃 Luxury evening 🏛️ Galata Port 🕌 Ortaköy Mosque 🌉 Bosphorus Bridge 📸 Photo spots 🏖️ Beşiktaş coast 🍽️ Koka Restaurant 👥 Small group 🚌 Transfer 🌟 Peaceful tour""",
            """✨ Öne Çıkanlar: 🌃 Lüks akşam 🏛️ Galata Port 🕌 Ortaköy Camii 🌉 Boğaz Köprüsü 📸 Fotoğraf noktaları 🏖️ Beşiktaş sahili 🍽️ Koka Restoran 👥 Küçük grup 🚌 Transfer 🌟 Huzurlu tur""",
            """✨ نکات برجسته: 🌃 شب لوکس 🏛️ گالاتا پورت 🕌 مسجد اورتاکوی 🌉 پل بسفر 📸 نقاط عکس 🏖️ ساحل بشیکتاش 🍽️ رستوران کوکا 👥 گروه کوچک 🚌 ترانسفر 🌟 تور آرام""",
            """📋 Rules: 🕘 Arrive 30min early 🎫 Ticket 👟 Comfortable shoes 📱 Phone charged 🚭 Respect areas 📷 Photos allowed 👥 Stay together ⏰ Follow schedule 🌿 Respect sites""",
            """📋 Kurallar: 🕘 30dk önce 🎫 Bilet 👟 Rahat ayakkabı 📱 Telefon şarjlı 🚭 Alanlara saygı 📷 Fotoğraf serbest 👥 Birlikte kalın ⏰ Program takibi 🌿 Yerlere saygı""",
            """📋 قوانین: 🕘 ۳۰ دقیقه زودتر 🎫 بلیط 👟 کفش راحت 📱 تلفن شارژ 🚭 احترام به مناطق 📷 عکس مجاز 👥 با هم بمانید ⏰ برنامه را دنبال کنید 🌿 احترام به مکان‌ها""",
            """🎒 Bring: 🎫 Ticket 🆔 ID 👟 Shoes 🧥 Jacket 📱 Phone 📷 Camera 💰 Cash 🩹 Meds""",
            """🎒 Getirin: 🎫 Bilet 🆔 Kimlik 👟 Ayakkabı 🧥 Ceket 📱 Telefon 📷 Kamera 💰 Nakit 🩹 İlaç""",
            """🎒 بیاورید: 🎫 بلیط 🆔 شناسنامه 👟 کفش 🧥 ژاکت 📱 تلفن 📷 دوربین 💰 نقدی 🩹 دارو"""
        )
        self._add_itinerary(tour, [
            (1, 30, 'Hotel', 'Pickup', 'Alım', 'پیکاپ', 'Hotel pickup', 'Otel alımı', 'پیکاپ هتل'),
            (2, 45, 'Galata Port', 'Galata Port', 'Galata Port', 'گالاتا پورت', 'Waterfront promenade', 'Sahil yürüyüşü', 'پیاده‌روی ساحل'),
            (3, 30, 'Ortaköy', 'Ortaköy Mosque', 'Ortaköy Camii', 'مسجد اورتاکوی', 'Famous mosque by bridge', 'Köprü yanı ünlü cami', 'مسجد معروف کنار پل'),
            (4, 45, 'Bosphorus', 'Bridge Photos', 'Köprü Fotoğrafları', 'عکس‌های پل', 'Photo with bridge background', 'Köprü arka planlı fotoğraf', 'عکس با پس‌زمینه پل'),
            (5, 30, 'Beşiktaş', 'Beşiktaş Coast', 'Beşiktaş Sahili', 'ساحل بشیکتاش', 'Coastal walk', 'Sahil yürüyüşü', 'پیاده‌روی ساحلی'),
            (6, 30, 'Return', 'Hotel Return', 'Dönüş', 'بازگشت', 'Return to hotel', 'Otele dönüş', 'بازگشت هتل')
        ])

    def _complete_istanbul_aquarium_tour(self, tour):
        """Complete Istanbul Aquarium Tour"""
        self._add_content(tour,
            """✨ Highlights: 🎨 Balat neighborhood 🕌 Suleymaniye Mosque 🐠 Aquarium center 🌳 Amazon forests 🏬 Star City shopping 🍽️ Lunch included 👨‍👩‍👧 Family friendly 📸 Photo spots 🎭 Cultural experience 👥 Small group""",
            """✨ Öne Çıkanlar: 🎨 Balat semti 🕌 Süleymaniye Camii 🐠 Akvaryum merkezi 🌳 Amazon ormanları 🏬 Star City alışveriş 🍽️ Öğle yemeği dahil 👨‍👩‍👧 Aile dostu 📸 Fotoğraf noktaları 🎭 Kültürel deneyim 👥 Küçük grup""",
            """✨ نکات برجسته: 🎨 محله بالات 🕌 مسجد سلیمانیه 🐠 مرکز آکواریوم 🌳 جنگل‌های آمازون 🏬 خرید استار سیتی 🍽️ ناهار شامل 👨‍👩‍👧 خانوادگی 📸 نقاط عکس 🎭 تجربه فرهنگی 👥 گروه کوچک""",
            """📋 Rules: 🕘 30min early 🎫 Ticket 👟 Comfortable shoes 👶 Supervise children 📱 Phone charged 🚭 No smoking inside 📷 Photos allowed 👥 Stay together ⏰ Follow schedule 🐠 Respect animals""",
            """📋 Kurallar: 🕘 30dk önce 🎫 Bilet 👟 Rahat ayakkabı 👶 Çocukları gözetin 📱 Telefon şarjlı 🚭 İçerde sigara yok 📷 Fotoğraf serbest 👥 Birlikte ⏰ Program 🐠 Hayvanlara saygı""",
            """📋 قوانین: 🕘 ۳۰ دقیقه زودتر 🎫 بلیط 👟 کفش راحت 👶 کودکان را نظارت کنید 📱 تلفن شارژ 🚭 داخل سیگار ممنوع 📷 عکس مجاز 👥 با هم ⏰ برنامه 🐠 احترام به حیوانات""",
            """🎒 Bring: 🎫 Ticket 🆔 ID 👟 Shoes 💧 Water 📱 Phone 📷 Camera 💰 Cash 👶 Kids items 🩹 Meds""",
            """🎒 Getirin: 🎫 Bilet 🆔 Kimlik 👟 Ayakkabı 💧 Su 📱 Telefon 📷 Kamera 💰 Nakit 👶 Çocuk eşyaları 🩹 İlaç""",
            """🎒 بیاورید: 🎫 بلیط 🆔 شناسنامه 👟 کفش 💧 آب 📱 تلفن 📷 دوربین 💰 نقدی 👶 وسایل بچه 🩹 دارو"""
        )
        self._add_itinerary(tour, [
            (1, 30, 'Hotel', 'Pickup', 'Alım', 'پیکاپ', 'Hotel pickup', 'Otel alımı', 'پیکاپ هتل'),
            (2, 60, 'Balat', 'Balat Visit', 'Balat Ziyareti', 'بازدید بالات', 'Colorful neighborhood', 'Renkli semt', 'محله رنگارنگ'),
            (3, 45, 'Mosque', 'Suleymaniye', 'Süleymaniye', 'سلیمانیه', 'Historic mosque', 'Tarihi cami', 'مسجد تاریخی'),
            (4, 120, 'Aquarium', 'Aquarium Tour', 'Akvaryum Turu', 'تور آکواریوم', 'Aquarium and Amazon forests', 'Akvaryum ve Amazon ormanları', 'آکواریوم و جنگل آمازون'),
            (5, 60, 'Lunch', 'Lunch Break', 'Öğle Yemeği', 'ناهار', 'Lunch at restaurant', 'Restoranda öğle yemeği', 'ناهار در رستوران'),
            (6, 60, 'Shopping', 'Star City', 'Star City', 'استار سیتی', 'Shopping time', 'Alışveriş zamanı', 'زمان خرید'),
            (7, 30, 'Return', 'Hotel Return', 'Dönüş', 'بازگشت', 'Return to hotel', 'Otele dönüş', 'بازگشت هتل')
        ])


    def _complete_istanbul_city_tour(self, tour):
        """Complete Istanbul City Tour"""
        self._add_content(tour,
            """✨ Highlights: 🕌 Ortaköy Mosque 🌉 Bosphorus Bridge 🏰 Maiden's Tower 🏬 Optimum Center 🏔️ Çamlıca Hill 🛍️ Polat Center 📸 Photo opportunities 🏖️ Beşiktaş 👥 Small group 🚌 Transfer""",
            """✨ Öne Çıkanlar: 🕌 Ortaköy Camii 🌉 Boğaz Köprüsü 🏰 Kız Kulesi 🏬 Optimum Merkez 🏔️ Çamlıca Tepesi 🛍️ Polat Merkez 📸 Fotoğraf fırsatları 🏖️ Beşiktaş 👥 Küçük grup 🚌 Transfer""",
            """✨ نکات برجسته: 🕌 مسجد اورتاکوی 🌉 پل بسفر 🏰 برج دختر 🏬 مرکز اوپتیموم 🏔️ تپه چاملیجا 🛍️ مرکز پولات 📸 فرصت‌های عکس 🏖️ بشیکتاش 👥 گروه کوچک 🚌 ترانسفر""",
            """📋 Rules: 🕘 30min early 🎫 Ticket 👟 Walking shoes 💳 Cards for shopping 📱 Phone charged 🚭 Respect areas 📷 Photos allowed 👥 Stay together ⏰ Follow schedule 🛍️ Check return policies""",
            """📋 Kurallar: 🕘 30dk önce 🎫 Bilet 👟 Yürüyüş ayakkabısı 💳 Alışveriş kartları 📱 Telefon şarjlı 🚭 Alanlara saygı 📷 Fotoğraf serbest 👥 Birlikte ⏰ Program 🛍️ İade politikalarını kontrol edin""",
            """📋 قوانین: 🕘 ۳۰ دقیقه زودتر 🎫 بلیط 👟 کفش پیاده‌روی 💳 کارت برای خرید 📱 تلفن شارژ 🚭 احترام به مناطق 📷 عکس مجاز 👥 با هم ⏰ برنامه 🛍️ سیاست بازگشت را بررسی کنید""",
            """🎒 Bring: 🎫 Ticket 🆔 ID 👟 Shoes 💳 Cards 💰 Cash 📱 Phone 📷 Camera 🎒 Shopping bags 🩹 Meds""",
            """🎒 Getirin: 🎫 Bilet 🆔 Kimlik 👟 Ayakkabı 💳 Kartlar 💰 Nakit 📱 Telefon 📷 Kamera 🎒 Alışveriş çantaları 🩹 İlaç""",
            """🎒 بیاورید: 🎫 بلیط 🆔 شناسنامه 👟 کفش 💳 کارت 💰 نقدی 📱 تلفن 📷 دوربین 🎒 کیسه خرید 🩹 دارو"""
        )
        self._add_itinerary(tour, [
            (1, 30, 'Hotel', 'Pickup', 'Alım', 'پیکاپ', 'Hotel pickup', 'Otel alımı', 'پیکاپ هتل'),
            (2, 45, 'Ortaköy', 'Ortaköy & Mosque', 'Ortaköy ve Cami', 'اورتاکوی و مسجد', 'Ortaköy coast and mosque', 'Ortaköy sahili ve camii', 'ساحل و مسجد اورتاکوی'),
            (3, 30, 'Bridge', 'Bosphorus Bridge', 'Boğaz Köprüsü', 'پل بسفر', 'Cross the bridge', 'Köprüden geçiş', 'عبور از پل'),
            (4, 30, 'Beylerbeyi', 'Maiden\'s Tower', 'Kız Kulesi', 'برج دختر', 'Photo stop', 'Fotoğraf molası', 'توقف عکس'),
            (5, 90, 'Shopping', 'Optimum Center', 'Optimum Merkez', 'مرکز اوپتیموم', 'Shopping time', 'Alışveriş zamanı', 'زمان خرید'),
            (6, 45, 'Çamlıca', 'Çamlıca Hill', 'Çamlıca Tepesi', 'تپه چاملیجا', 'Panoramic views', 'Panoramik manzaralar', 'مناظر پانوراما'),
            (7, 60, 'Polat', 'Polat Center', 'Polat Merkez', 'مرکز پولات', 'More shopping', 'Daha fazla alışveriş', 'خرید بیشتر'),
            (8, 30, 'Return', 'Hotel Return', 'Dönüş', 'بازگشت', 'Return to hotel', 'Otele dönüş', 'بازگشت هتل')
        ])

    def _complete_sapanca_nature_tour(self, tour):
        """Complete Sapanca Nature Tour"""
        self._add_content(tour,
            """✨ Highlights: 🌲 Maşukiye forest 🏔️ Jump Terrace 🪂 Zipline & Safari 🏞️ Sapanca Lake 🍽️ Forest restaurant lunch 🌳 Pristine nature 📸 Photo spots 🧗 Adventure activities 👥 Small group 🚌 Transfer""",
            """✨ Öne Çıkanlar: 🌲 Maşukiye ormanı 🏔️ Jump Terrace 🪂 Zipline ve Safari 🏞️ Sapanca Gölü 🍽️ Orman restoranında öğle yemeği 🌳 Bozulmamış doğa 📸 Fotoğraf noktaları 🧗 Macera aktiviteleri 👥 Küçük grup 🚌 Transfer""",
            """✨ نکات برجسته: 🌲 جنگل معشوقیه 🏔️ جامپ تراس 🪂 زیپ لاین و سافاری 🏞️ دریاچه ساپانجا 🍽️ ناهار رستوران جنگلی 🌳 طبیعت بکر 📸 نقاط عکس 🧗 فعالیت‌های ماجراجویانه 👥 گروه کوچک 🚌 ترانسفر""",
            """📋 Rules: 🕘 30min early 🎫 Ticket 👟 Hiking shoes 🎒 Backpack 💧 Water 📱 Phone charged 🚭 No smoking in forest 📷 Photos allowed 👥 Stay together ⏰ Follow schedule 🌿 Protect nature 🧗 Follow safety rules""",
            """📋 Kurallar: 🕘 30dk önce 🎫 Bilet 👟 Yürüyüş ayakkabısı 🎒 Sırt çantası 💧 Su 📱 Telefon şarjlı 🚭 Ormanda sigara yok 📷 Fotoğraf serbest 👥 Birlikte ⏰ Program 🌿 Doğayı koruyun 🧗 Güvenlik kurallarını izleyin""",
            """📋 قوانین: 🕘 ۳۰ دقیقه زودتر 🎫 بلیط 👟 کفش کوهنوردی 🎒 کوله‌پشتی 💧 آب 📱 تلفن شارژ 🚭 در جنگل سیگار ممنوع 📷 عکس مجاز 👥 با هم ⏰ برنامه 🌿 از طبیعت محافظت کنید 🧗 قوانین ایمنی را دنبال کنید""",
            """🎒 Bring: 🎫 Ticket 🆔 ID 👟 Hiking boots 🧥 Jacket 💧 Water 2L 📱 Phone 📷 Camera 💰 Cash for activities 🍫 Snacks 🩹 Meds 🧤 Gloves""",
            """🎒 Getirin: 🎫 Bilet 🆔 Kimlik 👟 Yürüyüş botları 🧥 Ceket 💧 2L su 📱 Telefon 📷 Kamera 💰 Aktiviteler için nakit 🍫 Atıştırmalık 🩹 İlaç 🧤 Eldiven""",
            """🎒 بیاورید: 🎫 بلیط 🆔 شناسنامه 👟 کفش کوهنوردی 🧥 ژاکت 💧 آب ۲ لیتر 📱 تلفن 📷 دوربین 💰 نقدی برای فعالیت‌ها 🍫 تنقلات 🩹 دارو 🧤 دستکش"""
        )
        self._add_itinerary(tour, [
            (1, 30, 'Hotel', 'Pickup', 'Alım', 'پیکاپ', 'Hotel pickup', 'Otel alımı', 'پیکاپ هتل'),
            (2, 90, 'Maşukiye', 'Forest Exploration', 'Orman Keşfi', 'کاوش جنگل', 'Explore pristine forest', 'Bozulmamış ormanı keşfedin', 'کشف جنگل بکر'),
            (3, 60, 'Kartepe', 'Jump Terrace', 'Jump Terrace', 'جامپ تراس', 'Glass terrace at peak', 'Zirvede cam teras', 'تراس شیشه‌ای در قله'),
            (4, 90, 'Activities', 'Safari & Zipline', 'Safari ve Zipline', 'سافاری و زیپ لاین', 'Adventure activities', 'Macera aktiviteleri', 'فعالیت‌های ماجراجویانه'),
            (5, 75, 'Lunch', 'Forest Restaurant', 'Orman Restoranı', 'رستوران جنگلی', 'Lunch in nature', 'Doğada öğle yemeği', 'ناهار در طبیعت'),
            (6, 60, 'Lake', 'Sapanca Lake', 'Sapanca Gölü', 'دریاچه ساپانجا', 'Beautiful freshwater lake', 'Güzel tatlı su gölü', 'دریاچه آب شیرین زیبا'),
            (7, 30, 'Return', 'Hotel Return', 'Dönüş', 'بازگشت', 'Return to hotel', 'Otele dönüş', 'بازگشت هتل')
        ])

    def _complete_turkish_nights_tavern(self, tour):
        """Complete Turkish Nights Tavern"""
        self._add_content(tour,
            """✨ Highlights: 🎵 Iranian & Turkish DJ 🍽️ Dinner 💃 Oriental dance 🍷 Alcoholic drinks 🍹 Turkish appetizers 🎭 Entertainment 🌃 Night atmosphere 👥 Family friendly 🚌 Round-trip transfer ⭐ Fun evening""",
            """✨ Öne Çıkanlar: 🎵 İranlı ve Türk DJ 🍽️ Akşam yemeği 💃 Oryantal dans 🍷 Alkollü içecekler 🍹 Türk mezeleri 🎭 Eğlence 🌃 Gece atmosferi 👥 Aile dostu 🚌 Gidiş-dönüş transfer ⭐ Eğlenceli akşam""",
            """✨ نکات برجسته: 🎵 DJ ایرانی و ترک 🍽️ شام 💃 رقص شرقی 🍷 نوشیدنی‌های الکلی 🍹 مزه‌های ترکی 🎭 سرگرمی 🌃 فضای شبانه 👥 خانوادگی 🚌 ترانسفر رفت و برگشت ⭐ شب سرگرم‌کننده""",
            """📋 Rules: 🕘 30min early 🎫 Ticket 👗 Casual dress 📱 Phone charged 🚭 Smoking areas only 📷 Photos allowed 👥 Stay together 🎵 Respect performers 🍽️ No outside food 🚫 Appropriate behavior 🎉 Enjoy responsibly""",
            """📋 Kurallar: 🕘 30dk önce 🎫 Bilet 👗 Günlük kıyafet 📱 Telefon şarjlı 🚭 Sadece sigara alanları 📷 Fotoğraf serbest 👥 Birlikte 🎵 Sanatçılara saygı 🍽️ Dışarıdan yiyecek yok 🚫 Uygun davranış 🎉 Sorumlu eğlenin""",
            """📋 قوانین: 🕘 ۳۰ دقیقه زودتر 🎫 بلیط 👗 لباس معمولی 📱 تلفن شارژ 🚭 فقط مناطق سیگار 📷 عکس مجاز 👥 با هم 🎵 احترام به هنرمندان 🍽️ غذای بیرون ممنوع 🚫 رفتار مناسب 🎉 مسئولانه لذت ببرید""",
            """🎒 Bring: 🎫 Ticket 🆔 ID 👗 Casual attire 📱 Phone 📷 Camera 💰 Cash 💳 Card 🩹 Meds""",
            """🎒 Getirin: 🎫 Bilet 🆔 Kimlik 👗 Günlük kıyafet 📱 Telefon 📷 Kamera 💰 Nakit 💳 Kart 🩹 İlaç""",
            """🎒 بیاورید: 🎫 بلیط 🆔 شناسنامه 👗 لباس معمولی 📱 تلفن 📷 دوربین 💰 نقدی 💳 کارت 🩹 دارو"""
        )
        self._add_itinerary(tour, [
            (1, 30, 'Hotel', 'Pickup', 'Alım', 'پیکاپ', 'Hotel pickup', 'Otel alımı', 'پیکاپ هتل'),
            (2, 30, 'Tavern', 'Welcome & Seating', 'Karşılama', 'خوش‌آمد', 'Welcome to tavern', 'Meyhaneye hoş geldiniz', 'خوش‌آمد به میخانه'),
            (3, 90, 'Dinner', 'Dinner Service', 'Akşam Yemeği', 'سرویس شام', 'Turkish dinner with appetizers', 'Mezelerle Türk yemeği', 'شام ترکی با پیش غذا'),
            (4, 90, 'Entertainment', 'DJ & Dance Show', 'DJ ve Dans Gösterisi', 'DJ و نمایش رقص', 'Iranian & Turkish DJ, oriental dance', 'İranlı ve Türk DJ, oryantal dans', 'DJ ایرانی و ترک، رقص شرقی'),
            (5, 30, 'Return', 'Hotel Return', 'Dönüş', 'بازگشت', 'Return to hotel', 'Otele dönüş', 'بازگشت هتل')
        ])
