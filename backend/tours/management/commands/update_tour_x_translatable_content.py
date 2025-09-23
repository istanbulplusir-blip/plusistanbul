from django.core.management.base import BaseCommand
from django.utils.translation import activate
from tours.models import Tour

class Command(BaseCommand):
    help = 'Update Tour X translatable content (highlights, rules, required_items) in both Persian and English'

    def handle(self, *args, **options):
        try:
            tour = Tour.objects.get(slug='tour-x')
            self.stdout.write(f"Found Tour X: {tour.title}")

            # Persian content
            self.stdout.write("Setting Persian content...")
            activate('fa')
            
            # Highlights
            tour.highlights = """🌟 برجسته‌های تور X:

• بازدید از جاذبه‌های تاریخی و فرهنگی
• تجربه‌ی منحصر به فرد در طبیعت بکر
• عکاسی حرفه‌ای از مناظر زیبا
• صرف وعده‌های غذایی محلی و سنتی
• راهنمای متخصص و دوستانه
• حمل و نقل راحت و ایمن
• گروه‌های کوچک برای تجربه‌ی بهتر
• برنامه‌ریزی دقیق و منظم"""

            # Rules and Regulations
            tour.rules = """📋 قوانین و مقررات تور X:

• رعایت زمان‌بندی دقیق برنامه‌ها الزامی است
• همراه داشتن مدارک شناسایی ضروری است
• رعایت قوانین محلی و احترام به فرهنگ منطقه
• ممنوعیت مصرف دخانیات در فضاهای بسته
• همراه داشتن لباس مناسب برای شرایط آب و هوایی
• رعایت نظم و انضباط در گروه
• ممنوعیت آسیب رساندن به محیط زیست
• رعایت قوانین عکاسی در مکان‌های خاص
• همراه داشتن داروهای شخصی در صورت نیاز
• رعایت قوانین ایمنی در تمام مراحل سفر"""

            # Required Items
            tour.required_items = """🎒 وسایل مورد نیاز تور X:

• کفش راحت و مناسب پیاده‌روی
• کلاه و عینک آفتابی
• کرم ضد آفتاب با SPF مناسب
• بطری آب شخصی
• دوربین عکاسی (اختیاری)
• پاوربانک برای شارژ موبایل
• لباس اضافی مناسب آب و هوا
• کیف کوچک برای وسایل شخصی
• داروهای شخصی در صورت نیاز
• کارت شناسایی و مدارک مهم"""

            tour.save()
            self.stdout.write("✅ Persian content updated successfully")

            # English content
            self.stdout.write("Setting English content...")
            activate('en')
            
            # Highlights
            tour.highlights = """🌟 Tour X Highlights:

• Visit historical and cultural attractions
• Unique experience in pristine nature
• Professional photography of beautiful landscapes
• Local and traditional meals
• Expert and friendly guide
• Comfortable and safe transportation
• Small groups for better experience
• Precise and organized planning"""

            # Rules and Regulations
            tour.rules = """📋 Tour X Rules & Regulations:

• Strict adherence to program timing is mandatory
• Carrying identification documents is essential
• Respect local laws and regional culture
• Smoking prohibited in enclosed spaces
• Bring appropriate clothing for weather conditions
• Maintain order and discipline in the group
• Environmental damage is prohibited
• Follow photography rules in special locations
• Bring personal medications if needed
• Follow safety regulations throughout the trip"""

            # Required Items
            tour.required_items = """🎒 Tour X Required Items:

• Comfortable and suitable walking shoes
• Hat and sunglasses
• Sunscreen with appropriate SPF
• Personal water bottle
• Camera (optional)
• Power bank for mobile charging
• Extra clothing suitable for weather
• Small bag for personal items
• Personal medications if needed
• ID card and important documents"""

            tour.save()
            self.stdout.write("✅ English content updated successfully")

            # Verify the content
            self.stdout.write("\n📊 Content Verification:")
            
            # Check Persian
            activate('fa')
            self.stdout.write(f"   Persian Highlights: {len(tour.highlights)} characters")
            self.stdout.write(f"   Persian Rules: {len(tour.rules)} characters")
            self.stdout.write(f"   Persian Required Items: {len(tour.required_items)} characters")
            
            # Check English
            activate('en')
            self.stdout.write(f"   English Highlights: {len(tour.highlights)} characters")
            self.stdout.write(f"   English Rules: {len(tour.rules)} characters")
            self.stdout.write(f"   English Required Items: {len(tour.required_items)} characters")

            self.stdout.write("\n🎉 Tour X translatable content updated successfully!")

        except Tour.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Tour X not found!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
