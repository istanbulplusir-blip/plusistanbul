#!/usr/bin/env python3
"""
مثال کامل از سیستم قیمت‌گذاری مخصوص ایجنت‌ها
"""

import os
import sys
import django
from decimal import Decimal

# تنظیم Django
sys.path.append('/path/to/your/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from users.models import User
from agents.models import AgentPricingRule
from agents.pricing_service import AgentPricingService
from tours.models import Tour, TourVariant
from transfers.models import TransferRoute


class AgentPricingExample:
    """مثال کامل از سیستم قیمت‌گذاری ایجنت"""
    
    def __init__(self):
        self.agent = None
    
    def setup_agent(self):
        """تنظیم ایجنت"""
        print("🔧 تنظیم ایجنت...")
        
        # پیدا کردن یا ایجاد ایجنت
        self.agent = User.objects.filter(role='agent').first()
        if not self.agent:
            print("❌ هیچ ایجنت فعالی یافت نشد")
            return False
        
        print(f"✅ ایجنت: {self.agent.username} ({self.agent.agent_code})")
        return True
    
    def setup_pricing_rules(self):
        """تنظیم قوانین قیمت‌گذاری"""
        print("\n💰 تنظیم قوانین قیمت‌گذاری...")
        
        # قانون 1: تخفیف 15% برای تورها
        rule1 = AgentPricingService.create_pricing_rule(
            agent=self.agent,
            product_type='tour',
            pricing_method='discount_percentage',
            discount_percentage=15.00,
            description='تخفیف ویژه تورها برای ایجنت'
        )
        print(f"✅ قانون تور: {rule1.get_pricing_method_display()} - {rule1.discount_percentage}%")
        
        # قانون 2: قیمت ثابت برای ترانسفرها
        rule2 = AgentPricingService.create_pricing_rule(
            agent=self.agent,
            product_type='transfer',
            pricing_method='fixed_price',
            fixed_price=80.00,
            description='قیمت ثابت ترانسفر برای ایجنت'
        )
        print(f"✅ قانون ترانسفر: {rule2.get_pricing_method_display()} - {rule2.fixed_price} USD")
        
        # قانون 3: ضریب سفارشی برای اجاره ماشین
        rule3 = AgentPricingService.create_pricing_rule(
            agent=self.agent,
            product_type='car_rental',
            pricing_method='custom_factor',
            custom_factor=0.85,  # 15% تخفیف
            min_price=50.00,
            description='ضریب سفارشی اجاره ماشین'
        )
        print(f"✅ قانون اجاره ماشین: {rule3.get_pricing_method_display()} - ضریب {rule3.custom_factor}")
        
        return True
    
    def example_tour_pricing(self):
        """مثال قیمت‌گذاری تور"""
        print("\n🎯 مثال قیمت‌گذاری تور...")
        
        try:
            # پیدا کردن تور فعال
            tour = Tour.objects.filter(is_active=True).first()
            if not tour:
                print("❌ هیچ تور فعالی یافت نشد")
                return
            
            variant = tour.variants.filter(is_active=True).first()
            if not variant:
                print("❌ هیچ واریانت فعالی یافت نشد")
                return
            
            print(f"📋 تور: {tour.title}")
            print(f"📋 واریانت: {variant.name}")
            print(f"📋 قیمت پایه: {variant.base_price} USD")
            
            # محاسبه قیمت برای سناریوهای مختلف
            scenarios = [
                {'adult': 2, 'child': 0, 'infant': 0, 'name': '2 بزرگسال'},
                {'adult': 1, 'child': 1, 'infant': 0, 'name': '1 بزرگسال + 1 کودک'},
                {'adult': 2, 'child': 1, 'infant': 1, 'name': 'خانواده کامل'},
            ]
            
            for scenario in scenarios:
                participants = {k: v for k, v in scenario.items() if k != 'name'}
                
                pricing_result = AgentPricingService.calculate_tour_price_for_agent(
                    tour=tour,
                    variant=variant,
                    agent=self.agent,
                    participants=participants
                )
                
                print(f"\n  📊 {scenario['name']}:")
                print(f"    💰 قیمت اصلی: {pricing_result['base_price']} USD")
                print(f"    🎯 قیمت ایجنت: {pricing_result['agent_price']} USD")
                print(f"    💵 صرفه‌جویی: {pricing_result['savings']} USD ({pricing_result['savings_percentage']:.1f}%)")
                print(f"    🔧 روش: {pricing_result['pricing_method']}")
                
        except Exception as e:
            print(f"❌ خطا در مثال تور: {e}")
    
    def example_transfer_pricing(self):
        """مثال قیمت‌گذاری ترانسفر"""
        print("\n🚗 مثال قیمت‌گذاری ترانسفر...")
        
        try:
            # پیدا کردن مسیر فعال
            route = TransferRoute.objects.filter(is_active=True).first()
            if not route:
                print("❌ هیچ مسیر فعالی یافت نشد")
                return
            
            print(f"📋 مسیر: {route.name or f'{route.origin} → {route.destination}'}")
            
            # محاسبه قیمت برای سناریوهای مختلف
            scenarios = [
                {'vehicle_type': 'sedan', 'passengers': 2, 'trip_type': 'one_way', 'name': 'سدان - 2 نفر - یک طرفه'},
                {'vehicle_type': 'suv', 'passengers': 4, 'trip_type': 'round_trip', 'name': 'SUV - 4 نفر - رفت و برگشت'},
                {'vehicle_type': 'van', 'passengers': 8, 'trip_type': 'one_way', 'name': 'ون - 8 نفر - یک طرفه'},
            ]
            
            for scenario in scenarios:
                pricing_result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=route,
                    vehicle_type=scenario['vehicle_type'],
                    agent=self.agent,
                    passenger_count=scenario['passengers'],
                    trip_type=scenario['trip_type'],
                    hour=14  # ساعت 2 بعدازظهر
                )
                
                print(f"\n  📊 {scenario['name']}:")
                print(f"    💰 قیمت اصلی: {pricing_result['base_price']} USD")
                print(f"    🎯 قیمت ایجنت: {pricing_result['agent_price']} USD")
                print(f"    💵 صرفه‌جویی: {pricing_result['savings']} USD ({pricing_result['savings_percentage']:.1f}%)")
                print(f"    🔧 روش: {pricing_result['pricing_method']}")
                
        except Exception as e:
            print(f"❌ خطا در مثال ترانسفر: {e}")
    
    def example_car_rental_pricing(self):
        """مثال قیمت‌گذاری اجاره ماشین"""
        print("\n🚙 مثال قیمت‌گذاری اجاره ماشین...")
        
        try:
            # پیدا کردن ماشین فعال
            from car_rentals.models import CarRental
            car = CarRental.objects.filter(is_active=True).first()
            if not car:
                print("❌ هیچ ماشین فعالی یافت نشد")
                return
            
            print(f"📋 ماشین: {car.brand} {car.model} ({car.year})")
            print(f"📋 قیمت روزانه: {car.price_per_day} USD")
            
            # محاسبه قیمت برای سناریوهای مختلف
            scenarios = [
                {'days': 1, 'hours': 0, 'include_insurance': False, 'name': '1 روز بدون بیمه'},
                {'days': 3, 'hours': 0, 'include_insurance': True, 'name': '3 روز با بیمه'},
                {'days': 7, 'hours': 0, 'include_insurance': False, 'name': '1 هفته بدون بیمه'},
                {'days': 0, 'hours': 8, 'include_insurance': False, 'name': '8 ساعت'},
            ]
            
            for scenario in scenarios:
                pricing_result = AgentPricingService.calculate_car_rental_price_for_agent(
                    car=car,
                    agent=self.agent,
                    days=scenario['days'],
                    hours=scenario['hours'],
                    include_insurance=scenario['include_insurance']
                )
                
                print(f"\n  📊 {scenario['name']}:")
                print(f"    💰 قیمت اصلی: {pricing_result['base_price']} USD")
                print(f"    🎯 قیمت ایجنت: {pricing_result['agent_price']} USD")
                print(f"    💵 صرفه‌جویی: {pricing_result['savings']} USD ({pricing_result['savings_percentage']:.1f}%)")
                print(f"    🔧 روش: {pricing_result['pricing_method']}")
                
        except Exception as e:
            print(f"❌ خطا در مثال اجاره ماشین: {e}")
    
    def show_pricing_summary(self):
        """نمایش خلاصه قوانین قیمت‌گذاری"""
        print("\n📊 خلاصه قوانین قیمت‌گذاری...")
        
        try:
            summary = AgentPricingService.get_agent_pricing_summary(self.agent)
            
            print(f"📋 تعداد قوانین: {summary['total_rules']}")
            print(f"📋 قوانین بر اساس نوع محصول:")
            
            for product_type, rule_info in summary['by_product_type'].items():
                print(f"  • {rule_info['method']}: {rule_info['value']}")
                if rule_info['description']:
                    print(f"    توضیحات: {rule_info['description']}")
            
        except Exception as e:
            print(f"❌ خطا در نمایش خلاصه: {e}")
    
    def run_example(self):
        """اجرای مثال کامل"""
        print("🚀 شروع مثال سیستم قیمت‌گذاری مخصوص ایجنت...")
        print("=" * 60)
        
        # تنظیم ایجنت
        if not self.setup_agent():
            return
        
        # تنظیم قوانین قیمت‌گذاری
        if not self.setup_pricing_rules():
            return
        
        # مثال‌های مختلف
        self.example_tour_pricing()
        self.example_transfer_pricing()
        self.example_car_rental_pricing()
        
        # نمایش خلاصه
        self.show_pricing_summary()
        
        print("=" * 60)
        print("✅ مثال کامل شد!")


if __name__ == "__main__":
    example = AgentPricingExample()
    example.run_example()
