#!/usr/bin/env python3
"""
تست کامل قیمت‌گذاری تور فرهنگی ۳۰ سپتامبر برای ایجنت
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date, time

# تنظیم Django
sys.path.append('/path/to/your/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from users.models import User
from tours.models import Tour, TourVariant, TourSchedule, TourOption
from agents.pricing_service import AgentPricingService
from agents.models import AgentPricingRule


class SpecificTourPricingTest:
    """تست قیمت‌گذاری تور فرهنگی ۳۰ سپتامبر"""
    
    def __init__(self):
        self.tour = None
        self.variant = None
        self.agent = None
        self.selected_options = []
    
    def find_tour(self):
        """پیدا کردن تور فرهنگی ۳۰ سپتامبر"""
        print("🔍 جستجوی تور فرهنگی ۳۰ سپتامبر...")
        
        # جستجو بر اساس عنوان (با استفاده از Parler)
        tours = Tour.objects.filter(
            translations__title__icontains='فرهنگی',
            is_active=True
        )
        
        if not tours.exists():
            print("❌ تور فرهنگی یافت نشد")
            return False
        
        self.tour = tours.first()
        # تنظیم زبان فارسی برای نمایش عنوان
        self.tour.set_current_language('fa')
        print(f"✅ تور یافت شد: {self.tour.title}")
        print(f"📋 توضیحات: {self.tour.description[:100] if self.tour.description else 'بدون توضیحات'}...")
        
        # پیدا کردن واریانت استاندارد
        variants = self.tour.variants.filter(
            name__icontains='استاندارد',
            is_active=True
        )
        
        if not variants.exists():
            # اگر واریانت استاندارد نباشد، اولین واریانت فعال را انتخاب کن
            variants = self.tour.variants.filter(is_active=True)
        
        if not variants.exists():
            print("❌ هیچ واریانت فعالی یافت نشد")
            return False
        
        self.variant = variants.first()
        print(f"✅ واریانت: {self.variant.name}")
        print(f"💰 قیمت پایه: {self.variant.base_price} USD")
        
        return True
    
    def find_options(self):
        """پیدا کردن اپشن‌های مورد نظر"""
        print("\n🔍 جستجوی اپشن‌ها...")
        
        # اپشن‌های مورد نظر
        target_options = [
            'صبحانه اضافی',
            'راهنمای خصوصی', 
            'پکیج عکس حرفه‌ای'
        ]
        
        self.selected_options = []
        
        for option_name in target_options:
            options = TourOption.objects.filter(
                tour=self.tour,
                name__icontains=option_name,
                is_active=True
            )
            
            if options.exists():
                option = options.first()
                self.selected_options.append({
                    'id': str(option.id),
                    'name': option.name,
                    'price': float(option.price),
                    'quantity': 1
                })
                print(f"✅ اپشن: {option.name} - {option.price} USD")
            else:
                print(f"⚠️ اپشن '{option_name}' یافت نشد")
        
        print(f"📋 تعداد اپشن‌های انتخاب شده: {len(self.selected_options)}")
        return True
    
    def setup_agent(self):
        """تنظیم ایجنت"""
        print("\n🔧 تنظیم ایجنت...")
        
        # پیدا کردن ایجنت فعال
        self.agent = User.objects.filter(role='agent', is_active=True).first()
        if not self.agent:
            print("❌ هیچ ایجنت فعالی یافت نشد")
            return False
        
        print(f"✅ ایجنت: {self.agent.username} ({self.agent.agent_code})")
        
        # تنظیم قانون قیمت‌گذاری برای تورها
        rule = AgentPricingService.create_pricing_rule(
            agent=self.agent,
            product_type='tour',
            pricing_method='discount_percentage',
            discount_percentage=15.00,  # 15% تخفیف
            description='تخفیف ویژه تورهای فرهنگی'
        )
        
        print(f"✅ قانون قیمت‌گذاری: {rule.get_pricing_method_display()} - {rule.discount_percentage}%")
        return True
    
    def calculate_regular_user_price(self):
        """محاسبه قیمت برای کاربر عادی"""
        print("\n💰 محاسبه قیمت کاربر عادی...")
        
        # اطلاعات سفارش
        participants = {
            'adult': 2,    # 2 بزرگسال
            'child': 1,    # 1 کودک  
            'infant': 1    # 1 نوزاد
        }
        
        print("📋 جزئیات سفارش:")
        print(f"  • بزرگسال: {participants['adult']} نفر")
        print(f"  • کودک: {participants['child']} نفر") 
        print(f"  • نوزاد: {participants['infant']} نفر")
        
        # محاسبه قیمت پایه با سرویس موجود
        from tours.services import TourPricingService
        
        try:
            pricing_result = TourPricingService.calculate_price(
                tour=self.tour,
                variant=self.variant,
                participants=participants,
                selected_options=self.selected_options
            )
            
            print("\n📊 قیمت‌گذاری کاربر عادی:")
            print(f"  💰 قیمت کل: {pricing_result['total']} USD")
            print(f"  📋 جزئیات:")
            
            # نمایش جزئیات قیمت
            if 'breakdown' in pricing_result:
                breakdown = pricing_result['breakdown']
                for key, value in breakdown.items():
                    print(f"    • {key}: {value} USD")
            
            # نمایش اپشن‌ها
            if self.selected_options:
                print(f"  🎯 اپشن‌های انتخاب شده:")
                total_options_price = 0
                for option in self.selected_options:
                    option_total = option['price'] * option['quantity']
                    total_options_price += option_total
                    print(f"    • {option['name']} ({option['quantity']}x): ${option_total:.2f}")
                print(f"  📊 مجموع اپشن‌ها: ${total_options_price:.2f}")
            
            return pricing_result
            
        except Exception as e:
            print(f"❌ خطا در محاسبه قیمت: {e}")
            return None
    
    def calculate_agent_price(self):
        """محاسبه قیمت برای ایجنت"""
        print("\n🎯 محاسبه قیمت ایجنت...")
        
        # اطلاعات سفارش (همان اطلاعات کاربر عادی)
        participants = {
            'adult': 2,    # 2 بزرگسال
            'child': 1,    # 1 کودک  
            'infant': 1    # 1 نوزاد
        }
        
        try:
            # محاسبه قیمت با قیمت‌گذاری مخصوص ایجنت
            pricing_result = AgentPricingService.calculate_tour_price_for_agent(
                tour=self.tour,
                variant=self.variant,
                agent=self.agent,
                participants=participants,
                selected_options=self.selected_options
            )
            
            print("\n📊 قیمت‌گذاری ایجنت:")
            print(f"  💰 قیمت اصلی: {pricing_result['base_price']} USD")
            print(f"  🎯 قیمت ایجنت: {pricing_result['agent_price']} USD")
            print(f"  💵 صرفه‌جویی: {pricing_result['savings']} USD")
            print(f"  📈 درصد صرفه‌جویی: {pricing_result['savings_percentage']:.1f}%")
            print(f"  🔧 روش قیمت‌گذاری: {pricing_result['pricing_method']}")
            
            # نمایش جزئیات
            if 'breakdown' in pricing_result:
                print(f"  📋 جزئیات قیمت:")
                breakdown = pricing_result['breakdown']
                for key, value in breakdown.items():
                    print(f"    • {key}: {value} USD")
            
            return pricing_result
            
        except Exception as e:
            print(f"❌ خطا در محاسبه قیمت ایجنت: {e}")
            return None
    
    def compare_prices(self, regular_price, agent_price):
        """مقایسه قیمت‌ها"""
        print("\n📊 مقایسه قیمت‌ها:")
        print("=" * 50)
        
        if not regular_price or not agent_price:
            print("❌ امکان مقایسه وجود ندارد")
            return
        
        regular_total = float(regular_price['total'])
        agent_total = float(agent_price['agent_price'])
        
        print(f"👤 کاربر عادی:     ${regular_total:.2f} USD")
        print(f"🎯 ایجنت:          ${agent_total:.2f} USD")
        print(f"💵 تفاوت قیمت:     ${regular_total - agent_total:.2f} USD")
        
        savings_percentage = ((regular_total - agent_total) / regular_total) * 100
        print(f"📈 درصد صرفه‌جویی: {savings_percentage:.1f}%")
        
        print("\n🎯 خلاصه سفارش:")
        print(f"  • تور: {self.tour.title}")
        print(f"  • واریانت: {self.variant.name}")
        print(f"  • تاریخ: ۳۰ سپتامبر ۲۰۲۵")
        print(f"  • زمان: ۰۹:۰۰ - ۱۷:۰۰")
        print(f"  • تعداد نفرات: ۴ نفر (۲ بزرگسال، ۱ کودک، ۱ نوزاد)")
        print(f"  • اپشن‌ها: {len(self.selected_options)} مورد")
        
        print("\n💰 قیمت‌گذاری:")
        print(f"  • قیمت اصلی: ${regular_total:.2f} USD")
        print(f"  • قیمت ایجنت: ${agent_total:.2f} USD")
        print(f"  • صرفه‌جویی: ${regular_total - agent_total:.2f} USD")
    
    def run_test(self):
        """اجرای تست کامل"""
        print("🚀 شروع تست قیمت‌گذاری تور فرهنگی ۳۰ سپتامبر")
        print("=" * 60)
        
        # مرحله 1: پیدا کردن تور
        if not self.find_tour():
            return
        
        # مرحله 2: پیدا کردن اپشن‌ها
        if not self.find_options():
            return
        
        # مرحله 3: تنظیم ایجنت
        if not self.setup_agent():
            return
        
        # مرحله 4: محاسبه قیمت کاربر عادی
        regular_price = self.calculate_regular_user_price()
        
        # مرحله 5: محاسبه قیمت ایجنت
        agent_price = self.calculate_agent_price()
        
        # مرحله 6: مقایسه قیمت‌ها
        self.compare_prices(regular_price, agent_price)
        
        print("=" * 60)
        print("✅ تست کامل شد!")


if __name__ == "__main__":
    test = SpecificTourPricingTest()
    test.run_test()
