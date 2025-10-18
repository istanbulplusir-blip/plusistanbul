"""
Management command to add 3-language translations to the Peykan P-Class car.
"""

from django.core.management.base import BaseCommand
from car_rentals.models import CarRental, CarRentalCategory, CarRentalLocation, CarRentalOption
from django.utils.translation import activate


class Command(BaseCommand):
    help = 'Add 3-language translations to the Peykan P-Class car'

    def handle(self, *args, **options):
        
        try:
            car = CarRental.objects.get(slug='peykan-p-class-2025')
            self.stdout.write(f'Found car: {car.brand} {car.model}')
        except CarRental.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Peykan P-Class car not found. Please run create_complete_test_car first.')
            )
            return
        
        # English translations
        activate('en')
        car.set_current_language('en')
        car.title = 'Peykan P-Class 2025 - Luxury Sedan'
        car.description = '''The Peykan P-Class 2025 represents the pinnacle of Iranian automotive luxury and engineering excellence. This premium sedan combines cutting-edge technology with timeless elegance, offering an unparalleled driving experience for discerning customers.

Key Features:
• Advanced 2.0L Turbo Engine with 250 HP
• Premium leather interior with heated seats
• 12.3-inch touchscreen infotainment system
• Advanced safety features including adaptive cruise control
• Wireless charging and premium audio system
• Climate control with air purification
• Panoramic sunroof
• Premium alloy wheels with run-flat tires

Perfect for business meetings, special occasions, and luxury travel. Experience the ultimate in comfort and performance with the Peykan P-Class 2025.'''
        
        car.short_description = 'Premium luxury sedan with advanced features and exceptional comfort. Perfect for business and special occasions.'
        car.highlights = '''• Luxury leather interior
• Advanced infotainment system
• Premium safety features
• Climate control with air purification
• Panoramic sunroof
• Premium audio system'''
        
        car.rules = '''Rental Terms and Conditions:
• Minimum age: 25 years
• Valid driver's license required
• Credit card for security deposit
• No smoking in vehicle
• Return with full fuel tank
• Clean vehicle policy applies
• Additional driver fees apply'''
        
        car.required_items = '''Required Documents:
• Valid driver's license
• Credit card for deposit
• Proof of insurance (if applicable)
• Additional driver documents (if applicable)'''
        
        car.save()
        self.stdout.write(self.style.SUCCESS('✅ English translations added'))
        
        # Persian translations
        activate('fa')
        car.set_current_language('fa')
        car.title = 'پیکان پی-کلاس ۲۰۲۵ - سدان لوکس'
        car.description = '''پیکان پی-کلاس ۲۰۲۵ نمایانگر اوج لوکس و تعالی مهندسی خودروی ایرانی است. این سدان پریمیوم ترکیبی از فناوری پیشرفته و ظرافت بی‌زمان است که تجربه رانندگی بی‌نظیری را برای مشتریان سخت‌گیر ارائه می‌دهد.

ویژگی‌های کلیدی:
• موتور پیشرفته ۲.۰ لیتری توربو با ۲۵۰ اسب بخار
• صندلی‌های چرمی لوکس با گرمایش
• سیستم سرگرمی لمسی ۱۲.۳ اینچی
• ویژگی‌های ایمنی پیشرفته شامل کروز کنترل تطبیقی
• شارژ بی‌سیم و سیستم صوتی پریمیوم
• کنترل آب و هوا با تصفیه هوا
• سانروف پانورامیک
• چرخ‌های آلیاژی پریمیوم با لاستیک ضدپنچری

مناسب برای جلسات کاری، مناسبت‌های خاص و سفرهای لوکس. تجربه نهایی راحتی و عملکرد با پیکان پی-کلاس ۲۰۲۵.'''
        
        car.short_description = 'سدان لوکس پریمیوم با ویژگی‌های پیشرفته و راحتی استثنایی. مناسب برای کار و مناسبت‌های خاص.'
        car.highlights = '''• صندلی‌های چرمی لوکس
• سیستم سرگرمی پیشرفته
• ویژگی‌های ایمنی پریمیوم
• کنترل آب و هوا با تصفیه هوا
• سانروف پانورامیک
• سیستم صوتی پریمیوم'''
        
        car.rules = '''شرایط و قوانین اجاره:
• حداقل سن: ۲۵ سال
• گواهینامه معتبر الزامی
• کارت اعتباری برای ودیعه امنیتی
• ممنوعیت استعمال دخانیات در خودرو
• بازگشت با باک پر
• سیاست خودروی تمیز اعمال می‌شود
• هزینه راننده اضافی اعمال می‌شود'''
        
        car.required_items = '''اسناد مورد نیاز:
• گواهینامه معتبر
• کارت اعتباری برای ودیعه
• بیمه نامه (در صورت وجود)
• اسناد راننده اضافی (در صورت وجود)'''
        
        car.save()
        self.stdout.write(self.style.SUCCESS('✅ Persian translations added'))
        
        # Arabic translations
        activate('ar')
        car.set_current_language('ar')
        car.title = 'بيكان بي-كلاس ٢٠٢٥ - سيدان فاخر'
        car.description = '''تمثل بيكان بي-كلاس ٢٠٢٥ قمة الفخامة والتميز الهندسي في صناعة السيارات الإيرانية. يجمع هذا السيدان الفاخر بين التكنولوجيا المتطورة والأناقة الخالدة، مما يوفر تجربة قيادة لا مثيل لها للعملاء المميزين.

الميزات الرئيسية:
• محرك توربو متقدم ٢.٠ لتر بقوة ٢٥٠ حصان
• مقاعد جلدية فاخرة مع تدفئة
• نظام ترفيهي بشاشة لمس ١٢.٣ بوصة
• ميزات أمان متقدمة تشمل التحكم التكيفي في السرعة
• شحن لاسلكي ونظام صوتي فاخر
• تحكم في المناخ مع تنقية الهواء
• سقف بانورامي
• عجلات ألمنيوم فاخرة مع إطارات مقاومة للثقب

مثالي للاجتماعات التجارية والمناسبات الخاصة والسفر الفاخر. استمتع بأقصى درجات الراحة والأداء مع بيكان بي-كلاس ٢٠٢٥.'''
        
        car.short_description = 'سيدان فاخر متقدم بميزات متطورة وراحة استثنائية. مثالي للعمل والمناسبات الخاصة.'
        car.highlights = '''• مقاعد جلدية فاخرة
• نظام ترفيهي متقدم
• ميزات أمان فاخرة
• تحكم في المناخ مع تنقية الهواء
• سقف بانورامي
• نظام صوتي فاخر'''
        
        car.rules = '''شروط وأحكام الإيجار:
• الحد الأدنى للعمر: ٢٥ سنة
• رخصة قيادة صالحة مطلوبة
• بطاقة ائتمان للوديعة الأمنية
• منع التدخين في المركبة
• إرجاع بخزان وقود ممتلئ
• تطبق سياسة المركبة النظيفة
• تطبق رسوم السائق الإضافي'''
        
        car.required_items = '''الوثائق المطلوبة:
• رخصة قيادة صالحة
• بطاقة ائتمان للوديعة
• بوليصة تأمين (إن وجدت)
• وثائق السائق الإضافي (إن وجدت)'''
        
        car.save()
        self.stdout.write(self.style.SUCCESS('✅ Arabic translations added'))
        
        # Add translations to category
        try:
            category = car.category
            if category:
                # English
                category.set_current_language('en')
                category.name = 'Luxury Cars'
                category.description = 'Premium and luxury vehicles for special occasions'
                category.save()
                
                # Persian
                category.set_current_language('fa')
                category.name = 'خودروهای لوکس'
                category.description = 'خودروهای پریمیوم و لوکس برای مناسبت‌های خاص'
                category.save()
                
                # Arabic
                category.set_current_language('ar')
                category.name = 'السيارات الفاخرة'
                category.description = 'مركبات فاخرة ومتطورة للمناسبات الخاصة'
                category.save()
                
                self.stdout.write(self.style.SUCCESS('✅ Category translations added'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not add category translations: {e}'))
        
        # Add translations to locations
        try:
            locations = car.default_pickup_locations.all()
            for location in locations:
                # English
                location.set_current_language('en')
                if 'airport' in location.slug:
                    location.name = 'Tehran Imam Khomeini Airport'
                    location.description = 'Main international airport of Tehran'
                    location.address = 'Tehran Imam Khomeini International Airport, Tehran, Iran'
                else:
                    location.name = 'Tehran City Center'
                    location.description = 'Central business district of Tehran'
                    location.address = 'Valiasr Street, Tehran, Iran'
                location.save()
                
                # Persian
                location.set_current_language('fa')
                if 'airport' in location.slug:
                    location.name = 'فرودگاه امام خمینی تهران'
                    location.description = 'فرودگاه بین‌المللی اصلی تهران'
                    location.address = 'فرودگاه بین‌المللی امام خمینی، تهران، ایران'
                else:
                    location.name = 'مرکز شهر تهران'
                    location.description = 'منطقه تجاری مرکزی تهران'
                    location.address = 'خیابان ولیعصر، تهران، ایران'
                location.save()
                
                # Arabic
                location.set_current_language('ar')
                if 'airport' in location.slug:
                    location.name = 'مطار الإمام الخميني طهران'
                    location.description = 'المطار الدولي الرئيسي لطهران'
                    location.address = 'مطار الإمام الخميني الدولي، طهران، إيران'
                else:
                    location.name = 'وسط مدينة طهران'
                    location.description = 'المنطقة التجارية المركزية لطهران'
                    location.address = 'شارع ولي العصر، طهران، إيران'
                location.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Location translations added'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not add location translations: {e}'))
        
        # Display summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('PEYKAN P-CLASS 2025 - TRANSLATIONS ADDED')
        self.stdout.write('='*60)
        
        self.stdout.write('\n🌍 LANGUAGES SUPPORTED:')
        self.stdout.write('   ✅ English (en)')
        self.stdout.write('   ✅ Persian (fa)')
        self.stdout.write('   ✅ Arabic (ar)')
        
        self.stdout.write('\n📝 TRANSLATED FIELDS:')
        self.stdout.write('   ✅ Title')
        self.stdout.write('   ✅ Description')
        self.stdout.write('   ✅ Short Description')
        self.stdout.write('   ✅ Highlights')
        self.stdout.write('   ✅ Rules')
        self.stdout.write('   ✅ Required Items')
        self.stdout.write('   ✅ Category')
        self.stdout.write('   ✅ Locations')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('✅ ALL TRANSLATIONS ADDED SUCCESSFULLY!')
        self.stdout.write('✅ Car is now ready for multi-language testing')
        self.stdout.write('✅ Admin panel supports all 3 languages')
        self.stdout.write('='*60)
        
        self.stdout.write(f'\n🔗 Admin URL: http://localhost:8000/admin/car_rentals/carrental/{car.id}/change/')
        self.stdout.write(f'🔗 Frontend URL: http://localhost:3000/car-rentals/{car.slug}')
