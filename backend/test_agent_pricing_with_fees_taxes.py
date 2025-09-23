#!/usr/bin/env python3
"""
تست کامل قیمت‌گذاری ایجنت با فیس و تکس
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


class AgentPricingWithFeesTaxesTest:
    """تست قیمت‌گذاری ایجنت با فیس و تکس"""
    
    def __init__(self):
        self.tour = None
        self.variant = None
        self.agent = None
        self.selected_options = []
    
    def setup_test_data(self):
        """تنظیم داده‌های تست"""
        print("🔧 تنظیم داده‌های تست...")
        
        # پیدا کردن تور
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
        
        # پیدا کردن اپشن‌ها
        options = TourOption.objects.filter(tour=self.tour, is_active=True)
        print(f"📋 اپشن‌های موجود: {options.count()} مورد")
        
        # انتخاب اپشن‌ها
        for option in options[:3]:
            self.selected_options.append({
                'id': str(option.id),
                'name': option.name,
                'price': float(option.price),
                'quantity': 1
            })
            print(f"  • {option.name}: {option.price} USD")
        
        # تنظیم ایجنت
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
    
    def calculate_pricing_comparison(self):
        """محاسبه مقایسه قیمت‌گذاری"""
        print("\n💰 محاسبه مقایسه قیمت‌گذاری...")
        
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
            regular_pricing = TourPricingService.calculate_price(
                tour=self.tour,
                variant=self.variant,
                participants=participants,
                selected_options=self.selected_options
            )
            
            # محاسبه فیس و تکس برای کاربر عادی
            regular_fees_taxes = AgentPricingService._calculate_fees_and_taxes(regular_pricing['total'])
            
            print(f"\n👤 قیمت کاربر عادی:")
            print(f"  • Subtotal: {regular_pricing['total']:.2f} USD")
            print(f"  • Fees (3%): {regular_fees_taxes['fees_total']:.2f} USD")
            print(f"  • Taxes (9%): {regular_fees_taxes['tax_total']:.2f} USD")
            print(f"  • Total: {regular_fees_taxes['grand_total']:.2f} USD")
            
            # محاسبه قیمت ایجنت
            agent_pricing = AgentPricingService.calculate_tour_price_for_agent(
                tour=self.tour,
                variant=self.variant,
                agent=self.agent,
                participants=participants,
                selected_options=self.selected_options,
                include_fees_taxes=True
            )
            
            print(f"\n🎯 قیمت ایجنت:")
            print(f"  • Subtotal: {agent_pricing['agent_subtotal']:.2f} USD")
            print(f"  • Fees (3%): {agent_pricing['agent_fees']:.2f} USD")
            print(f"  • Taxes (9%): {agent_pricing['agent_taxes']:.2f} USD")
            print(f"  • Total: {agent_pricing['agent_total']:.2f} USD")
            
            # محاسبه صرفه‌جویی
            subtotal_savings = float(regular_pricing['total']) - agent_pricing['agent_subtotal']
            total_savings = regular_fees_taxes['grand_total'] - agent_pricing['agent_total']
            
            print(f"\n💵 صرفه‌جویی:")
            print(f"  • در Subtotal: {subtotal_savings:.2f} USD ({agent_pricing['savings_percentage']:.1f}%)")
            print(f"  • در Total: {total_savings:.2f} USD")
            
            return {
                'regular': {
                    'subtotal': float(regular_pricing['total']),
                    'fees': regular_fees_taxes['fees_total'],
                    'taxes': regular_fees_taxes['tax_total'],
                    'total': regular_fees_taxes['grand_total']
                },
                'agent': {
                    'subtotal': agent_pricing['agent_subtotal'],
                    'fees': agent_pricing['agent_fees'],
                    'taxes': agent_pricing['agent_taxes'],
                    'total': agent_pricing['agent_total']
                },
                'savings': {
                    'subtotal': subtotal_savings,
                    'total': total_savings,
                    'percentage': agent_pricing['savings_percentage']
                }
            }
            
        except Exception as e:
            print(f"❌ خطا در محاسبه: {e}")
            return None
    
    def show_detailed_breakdown(self, pricing_data):
        """نمایش جزئیات قیمت‌گذاری"""
        print("\n📊 جزئیات قیمت‌گذاری:")
        print("=" * 60)
        
        regular = pricing_data['regular']
        agent = pricing_data['agent']
        savings = pricing_data['savings']
        
        print(f"🏷️ محصول: {self.tour.title}")
        print(f"📦 واریانت: {self.variant.name}")
        print(f"💰 قیمت پایه واریانت: {self.variant.base_price} USD")
        
        print(f"\n👥 شرکت‌کنندگان:")
        base_price = float(self.variant.base_price)
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
        
        print(f"\n💰 مقایسه قیمت‌گذاری:")
        print(f"  👤 کاربر عادی:")
        print(f"    • Subtotal: {regular['subtotal']:.2f} USD")
        print(f"    • Fees (3%): {regular['fees']:.2f} USD")
        print(f"    • Taxes (9%): {regular['taxes']:.2f} USD")
        print(f"    • Total: {regular['total']:.2f} USD")
        
        print(f"  🎯 ایجنت:")
        print(f"    • Subtotal: {agent['subtotal']:.2f} USD")
        print(f"    • Fees (3%): {agent['fees']:.2f} USD")
        print(f"    • Taxes (9%): {agent['taxes']:.2f} USD")
        print(f"    • Total: {agent['total']:.2f} USD")
        
        print(f"\n💵 صرفه‌جویی:")
        print(f"  • در Subtotal: {savings['subtotal']:.2f} USD ({savings['percentage']:.1f}%)")
        print(f"  • در Total: {savings['total']:.2f} USD")
        
        print(f"\n🔧 روش قیمت‌گذاری ایجنت:")
        print(f"  • نوع: تخفیف درصدی")
        print(f"  • تخفیف: 15% از subtotal")
        print(f"  • محاسبه: {regular['subtotal']:.2f} × 0.85 = {agent['subtotal']:.2f}")
        print(f"  • فیس: {agent['subtotal']:.2f} × 0.03 = {agent['fees']:.2f}")
        print(f"  • تکس: ({agent['subtotal']:.2f} + {agent['fees']:.2f}) × 0.09 = {agent['taxes']:.2f}")
    
    def simulate_cart_scenario(self, pricing_data):
        """شبیه‌سازی سناریو سبد خرید"""
        print("\n🛒 شبیه‌سازی سناریو سبد خرید:")
        print("=" * 60)
        
        regular = pricing_data['regular']
        agent = pricing_data['agent']
        
        print("📋 خلاصه سفارش:")
        print(f"  • تور: {self.tour.title}")
        print(f"  • واریانت: {self.variant.name}")
        print(f"  • تاریخ: ۳۰ سپتامبر ۲۰۲۵")
        print(f"  • زمان: ۰۹:۰۰ - ۱۷:۰۰")
        print(f"  • تعداد نفرات: ۴ نفر")
        print(f"  • اپشن‌ها: {len(self.selected_options)} مورد")
        
        print(f"\n🛒 سبد خرید کاربر عادی:")
        print(f"  • Subtotal: ${regular['subtotal']:.2f}")
        print(f"  • Fees: ${regular['fees']:.2f}")
        print(f"  • Tax: ${regular['taxes']:.2f}")
        print(f"  • Total: ${regular['total']:.2f}")
        
        print(f"\n🛒 سبد خرید ایجنت:")
        print(f"  • Subtotal: ${agent['subtotal']:.2f}")
        print(f"  • Fees: ${agent['fees']:.2f}")
        print(f"  • Tax: ${agent['taxes']:.2f}")
        print(f"  • Total: ${agent['total']:.2f}")
        
        print(f"\n🎯 مزایای ایجنت:")
        print(f"  • تخفیف 15% روی subtotal")
        print(f"  • فیس و تکس کمتر (بر اساس subtotal کمتر)")
        print(f"  • صرفه‌جویی کل: ${pricing_data['savings']['total']:.2f}")
        print(f"  • امکان رقابت بهتر با مشتریان")
    
    def run_test(self):
        """اجرای تست کامل"""
        print("🚀 شروع تست قیمت‌گذاری ایجنت با فیس و تکس")
        print("=" * 60)
        
        # مرحله 1: تنظیم داده‌ها
        if not self.setup_test_data():
            return
        
        # مرحله 2: محاسبه قیمت‌ها
        pricing_data = self.calculate_pricing_comparison()
        if not pricing_data:
            return
        
        # مرحله 3: نمایش جزئیات
        self.show_detailed_breakdown(pricing_data)
        
        # مرحله 4: شبیه‌سازی سناریو
        self.simulate_cart_scenario(pricing_data)
        
        print("=" * 60)
        print("✅ تست کامل شد!")


if __name__ == "__main__":
    test = AgentPricingWithFeesTaxesTest()
    test.run_test()
