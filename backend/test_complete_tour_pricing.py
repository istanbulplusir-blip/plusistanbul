#!/usr/bin/env python3
"""
تست کامل قیمت‌گذاری تور با اپشن‌های واقعی
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


class CompleteTourPricingTest:
    """تست کامل قیمت‌گذاری تور با اپشن‌ها"""
    
    def __init__(self):
        self.tour = None
        self.variant = None
        self.agent = None
        self.selected_options = []
    
    def find_tour_and_options(self):
        """پیدا کردن تور و اپشن‌های موجود"""
        print("🔍 جستجوی تور و اپشن‌ها...")
        
        # پیدا کردن تور فعال
        tours = Tour.objects.filter(is_active=True)
        if not tours.exists():
            print("❌ هیچ تور فعالی یافت نشد")
            return False
        
        self.tour = tours.first()
        self.tour.set_current_language('fa')
        print(f"✅ تور: {self.tour.title}")
        
        # پیدا کردن واریانت
        variants = self.tour.variants.filter(is_active=True)
        if not variants.exists():
            print("❌ هیچ واریانت فعالی یافت نشد")
            return False
        
        self.variant = variants.first()
        print(f"✅ واریانت: {self.variant.name} - {self.variant.base_price} USD")
        
        # پیدا کردن اپشن‌های موجود
        options = TourOption.objects.filter(tour=self.tour, is_active=True)
        print(f"📋 اپشن‌های موجود: {options.count()} مورد")
        
        # انتخاب 3 اپشن اول
        selected_count = 0
        for option in options[:3]:
            self.selected_options.append({
                'id': str(option.id),
                'name': option.name,
                'price': float(option.price),
                'quantity': 1
            })
            selected_count += 1
            print(f"  • {option.name}: {option.price} USD")
        
        print(f"✅ {selected_count} اپشن انتخاب شد")
        return True
    
    def setup_agent(self):
        """تنظیم ایجنت"""
        print("\n🔧 تنظیم ایجنت...")
        
        self.agent = User.objects.filter(role='agent', is_active=True).first()
        if not self.agent:
            print("❌ هیچ ایجنت فعالی یافت نشد")
            return False
        
        print(f"✅ ایجنت: {self.agent.username} ({self.agent.agent_code})")
        
        # تنظیم قانون قیمت‌گذاری
        rule = AgentPricingService.create_pricing_rule(
            agent=self.agent,
            product_type='tour',
            pricing_method='discount_percentage',
            discount_percentage=15.00,
            description='تخفیف ویژه تورها'
        )
        
        print(f"✅ قانون: {rule.get_pricing_method_display()} - {rule.discount_percentage}%")
        return True
    
    def calculate_prices(self):
        """محاسبه قیمت‌ها"""
        print("\n💰 محاسبه قیمت‌ها...")
        
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
        print(f"  • اپشن‌ها: {len(self.selected_options)} مورد")
        
        # محاسبه قیمت کاربر عادی
        from tours.services import TourPricingService
        
        try:
            regular_price = TourPricingService.calculate_price(
                tour=self.tour,
                variant=self.variant,
                participants=participants,
                selected_options=self.selected_options
            )
            
            print(f"\n👤 قیمت کاربر عادی: {regular_price['total']} USD")
            
            # محاسبه قیمت ایجنت
            agent_price = AgentPricingService.calculate_tour_price_for_agent(
                tour=self.tour,
                variant=self.variant,
                agent=self.agent,
                participants=participants,
                selected_options=self.selected_options
            )
            
            print(f"🎯 قیمت ایجنت: {agent_price['agent_price']} USD")
            
            # محاسبه صرفه‌جویی
            savings = float(regular_price['total']) - float(agent_price['agent_price'])
            savings_percentage = (savings / float(regular_price['total'])) * 100
            
            print(f"💵 صرفه‌جویی: {savings:.2f} USD ({savings_percentage:.1f}%)")
            
            return {
                'regular': regular_price,
                'agent': agent_price,
                'savings': savings,
                'savings_percentage': savings_percentage
            }
            
        except Exception as e:
            print(f"❌ خطا در محاسبه: {e}")
            return None
    
    def show_detailed_breakdown(self, pricing_data):
        """نمایش جزئیات قیمت‌گذاری"""
        print("\n📊 جزئیات قیمت‌گذاری:")
        print("=" * 50)
        
        regular = pricing_data['regular']
        agent = pricing_data['agent']
        
        print(f"🏷️ محصول: {self.tour.title}")
        print(f"📦 واریانت: {self.variant.name}")
        print(f"💰 قیمت پایه واریانت: {self.variant.base_price} USD")
        
        base_price = float(self.variant.base_price)
        print(f"\n👥 شرکت‌کنندگان:")
        print(f"  • بزرگسال (2x): {base_price} × 2 = {base_price * 2:.2f} USD")
        print(f"  • کودک (1x): {base_price * 0.67:.2f} × 1 = {base_price * 0.67:.2f} USD")
        print(f"  • نوزاد (1x): رایگان")
        
        if self.selected_options:
            print(f"\n🎯 اپشن‌های انتخاب شده:")
            total_options_price = 0
            for option in self.selected_options:
                option_total = option['price'] * option['quantity']
                total_options_price += option_total
                print(f"  • {option['name']} ({option['quantity']}x): {option['price']} USD")
            print(f"  📊 مجموع اپشن‌ها: {total_options_price:.2f} USD")
        
        print(f"\n💰 قیمت‌گذاری:")
        print(f"  👤 کاربر عادی: {float(regular['total']):.2f} USD")
        print(f"  🎯 ایجنت: {float(agent['agent_price']):.2f} USD")
        print(f"  💵 صرفه‌جویی: {pricing_data['savings']:.2f} USD")
        print(f"  📈 درصد صرفه‌جویی: {pricing_data['savings_percentage']:.1f}%")
        
        print(f"\n🔧 روش قیمت‌گذاری ایجنت:")
        print(f"  • نوع: {agent['pricing_method']}")
        print(f"  • تخفیف: 15% از قیمت کل")
        print(f"  • محاسبه: {float(regular['total']):.2f} × 0.85 = {float(agent['agent_price']):.2f}")
    
    def simulate_booking_scenario(self, pricing_data):
        """شبیه‌سازی سناریو سفارش"""
        print("\n🎯 شبیه‌سازی سناریو سفارش:")
        print("=" * 50)
        
        print("📋 خلاصه سفارش:")
        print(f"  • تور: {self.tour.title}")
        print(f"  • واریانت: {self.variant.name}")
        print(f"  • تاریخ: ۳۰ سپتامبر ۲۰۲۵")
        print(f"  • زمان: ۰۹:۰۰ - ۱۷:۰۰")
        print(f"  • تعداد نفرات: ۴ نفر")
        print(f"  • اپشن‌ها: {len(self.selected_options)} مورد")
        
        print(f"\n💰 قیمت‌گذاری:")
        print(f"  • قیمت اصلی: ${float(pricing_data['regular']['total']):.2f} USD")
        print(f"  • قیمت ایجنت: ${float(pricing_data['agent']['agent_price']):.2f} USD")
        print(f"  • صرفه‌جویی: ${pricing_data['savings']:.2f} USD")
        
        print(f"\n🎯 مزایای ایجنت:")
        print(f"  • تخفیف 15% روی کل سفارش")
        print(f"  • قیمت شفاف و قابل پیش‌بینی")
        print(f"  • امکان رقابت بهتر با مشتریان")
        print(f"  • افزایش حاشیه سود")
    
    def run_test(self):
        """اجرای تست کامل"""
        print("🚀 شروع تست کامل قیمت‌گذاری تور")
        print("=" * 60)
        
        # مرحله 1: پیدا کردن تور و اپشن‌ها
        if not self.find_tour_and_options():
            return
        
        # مرحله 2: تنظیم ایجنت
        if not self.setup_agent():
            return
        
        # مرحله 3: محاسبه قیمت‌ها
        pricing_data = self.calculate_prices()
        if not pricing_data:
            return
        
        # مرحله 4: نمایش جزئیات
        self.show_detailed_breakdown(pricing_data)
        
        # مرحله 5: شبیه‌سازی سناریو
        self.simulate_booking_scenario(pricing_data)
        
        print("=" * 60)
        print("✅ تست کامل شد!")


if __name__ == "__main__":
    test = CompleteTourPricingTest()
    test.run_test()
