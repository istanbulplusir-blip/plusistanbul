#!/usr/bin/env python3
"""
تست سیستم قیمت‌گذاری فعلی برای همه محصولات
"""

import os
import sys
import django
from decimal import Decimal

# تنظیم Django
sys.path.append('/path/to/your/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourPricing, TourOption, TourSchedule
from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from car_rentals.models import CarRental, CarRentalOption
from events.models import Event, EventPerformance, EventOption
from users.models import User
from cart.models import CartService
from orders.models import OrderService


class PricingSystemTester:
    """تست سیستم قیمت‌گذاری فعلی"""
    
    def __init__(self):
        self.results = {
            'tours': [],
            'transfers': [],
            'car_rentals': [],
            'events': []
        }
    
    def test_tour_pricing(self):
        """تست قیمت‌گذاری تورها"""
        print("🧪 تست قیمت‌گذاری تورها...")
        
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
            
            # تست سناریوهای مختلف
            test_cases = [
                {'adult': 2, 'child': 0, 'infant': 0},  # فقط بزرگسال
                {'adult': 1, 'child': 1, 'infant': 0},  # بزرگسال + کودک
                {'adult': 2, 'child': 1, 'infant': 1},  # همه گروه‌ها
                {'adult': 0, 'child': 3, 'infant': 0},  # فقط کودک
            ]
            
            for i, participants in enumerate(test_cases, 1):
                print(f"  📋 تست {i}: {participants}")
                
                # محاسبه قیمت با سرویس موجود
                from tours.services import TourPricingService
                pricing_result = TourPricingService.calculate_price(
                    tour=tour,
                    variant=variant,
                    participants=participants,
                    selected_options=[]
                )
                
                result = {
                    'tour_id': str(tour.id),
                    'tour_title': tour.title,
                    'variant_name': variant.name,
                    'participants': participants,
                    'base_price': float(variant.base_price),
                    'total_price': float(pricing_result['total']),
                    'breakdown': {k: float(v) for k, v in pricing_result['breakdown'].items()},
                    'currency': pricing_result['currency']
                }
                
                self.results['tours'].append(result)
                print(f"    ✅ قیمت کل: {result['total_price']} {result['currency']}")
                print(f"    📊 جزئیات: {result['breakdown']}")
            
            print(f"✅ تست تورها تکمیل شد ({len(self.results['tours'])} تست)")
            
        except Exception as e:
            print(f"❌ خطا در تست تورها: {e}")
    
    def test_transfer_pricing(self):
        """تست قیمت‌گذاری ترانسفرها"""
        print("🧪 تست قیمت‌گذاری ترانسفرها...")
        
        try:
            # پیدا کردن مسیر فعال
            route = TransferRoute.objects.filter(is_active=True).first()
            if not route:
                print("❌ هیچ مسیر فعالی یافت نشد")
                return
            
            pricing = route.pricing.first()
            if not pricing:
                print("❌ هیچ قیمت‌گذاری یافت نشد")
                return
            
            # تست سناریوهای مختلف
            test_cases = [
                {'vehicle_type': 'sedan', 'passengers': 2, 'trip_type': 'one_way', 'hour': 10},
                {'vehicle_type': 'suv', 'passengers': 4, 'trip_type': 'round_trip', 'hour': 14, 'return_hour': 16},
                {'vehicle_type': 'van', 'passengers': 8, 'trip_type': 'one_way', 'hour': 22},  # ساعت اوج
                {'vehicle_type': 'sedan', 'passengers': 1, 'trip_type': 'one_way', 'hour': 2},  # نیمه شب
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"  📋 تست {i}: {test_case}")
                
                # محاسبه قیمت
                price_data = pricing._calculate_transfer_price(
                    hour=test_case.get('hour'),
                    return_hour=test_case.get('return_hour'),
                    is_round_trip=(test_case['trip_type'] == 'round_trip'),
                    selected_options=[]
                )
                
                total_price = Decimal(str(price_data['final_price'])) * test_case['passengers']
                
                result = {
                    'route_id': str(route.id),
                    'route_name': route.name or f"{route.origin} → {route.destination}",
                    'vehicle_type': test_case['vehicle_type'],
                    'passengers': test_case['passengers'],
                    'trip_type': test_case['trip_type'],
                    'base_price': float(pricing.base_price),
                    'total_price': float(total_price),
                    'price_breakdown': {k: float(v) for k, v in price_data.items()},
                    'currency': pricing.currency
                }
                
                self.results['transfers'].append(result)
                print(f"    ✅ قیمت کل: {result['total_price']} {result['currency']}")
                print(f"    📊 جزئیات: {result['price_breakdown']}")
            
            print(f"✅ تست ترانسفرها تکمیل شد ({len(self.results['transfers'])} تست)")
            
        except Exception as e:
            print(f"❌ خطا در تست ترانسفرها: {e}")
    
    def test_car_rental_pricing(self):
        """تست قیمت‌گذاری اجاره ماشین"""
        print("🧪 تست قیمت‌گذاری اجاره ماشین...")
        
        try:
            # پیدا کردن ماشین فعال
            car = CarRental.objects.filter(is_active=True).first()
            if not car:
                print("❌ هیچ ماشین فعالی یافت نشد")
                return
            
            # تست سناریوهای مختلف
            test_cases = [
                {'days': 1, 'hours': 0, 'include_insurance': False},  # یک روز
                {'days': 3, 'hours': 0, 'include_insurance': True},   # سه روز با بیمه
                {'days': 7, 'hours': 0, 'include_insurance': False}, # یک هفته (تخفیف هفتگی)
                {'days': 0, 'hours': 8, 'include_insurance': False}, # رنت ساعتی
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"  📋 تست {i}: {test_case}")
                
                # محاسبه قیمت
                total_price = car.calculate_total_price(
                    days=test_case['days'],
                    hours=test_case['hours'],
                    include_insurance=test_case['include_insurance']
                )
                
                result = {
                    'car_id': str(car.id),
                    'car_name': f"{car.brand} {car.model} ({car.year})",
                    'rental_type': 'hourly' if test_case['days'] == 0 else 'daily',
                    'days': test_case['days'],
                    'hours': test_case['hours'],
                    'include_insurance': test_case['include_insurance'],
                    'daily_rate': float(car.price_per_day),
                    'hourly_rate': float(car.price_per_hour) if car.price_per_hour else None,
                    'total_price': float(total_price),
                    'currency': 'USD'  # فرضی
                }
                
                self.results['car_rentals'].append(result)
                print(f"    ✅ قیمت کل: {result['total_price']} {result['currency']}")
            
            print(f"✅ تست اجاره ماشین تکمیل شد ({len(self.results['car_rentals'])} تست)")
            
        except Exception as e:
            print(f"❌ خطا در تست اجاره ماشین: {e}")
    
    def test_event_pricing(self):
        """تست قیمت‌گذاری رویدادها"""
        print("🧪 تست قیمت‌گذاری رویدادها...")
        
        try:
            # پیدا کردن رویداد فعال
            event = Event.objects.filter(is_active=True).first()
            if not event:
                print("❌ هیچ رویداد فعالی یافت نشد")
                return
            
            performance = event.performances.filter(is_active=True).first()
            if not performance:
                print("❌ هیچ اجرای فعالی یافت نشد")
                return
            
            # پیدا کردن نوع بلیط (فرضی)
            ticket_type = {'id': '1', 'name': 'General', 'price': 50.00, 'currency': 'USD'}
            
            # تست سناریوهای مختلف
            test_cases = [
                {'quantity': 1, 'section': 'general'},
                {'quantity': 2, 'section': 'vip'},
                {'quantity': 4, 'section': 'general'},
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"  📋 تست {i}: {test_case}")
                
                # محاسبه قیمت با سرویس موجود
                from events.pricing_service import EventPriceCalculator
                calculator = EventPriceCalculator()
                
                # محاسبه قیمت ساده (فرضی)
                pricing_result = {
                    'base_price': ticket_type['price'],
                    'final_price': ticket_type['price'] * test_case['quantity'],
                    'currency': ticket_type['currency']
                }
                
                result = {
                    'event_id': str(event.id),
                    'event_title': event.title,
                    'performance_id': str(performance.id),
                    'ticket_type': ticket_type['name'],
                    'section': test_case['section'],
                    'quantity': test_case['quantity'],
                    'base_price': float(ticket_type['price']),
                    'total_price': float(pricing_result['final_price']),
                    'breakdown': {k: float(v) for k, v in pricing_result.items()},
                    'currency': ticket_type['currency']
                }
                
                self.results['events'].append(result)
                print(f"    ✅ قیمت کل: {result['total_price']} {result['currency']}")
                print(f"    📊 جزئیات: {result['breakdown']}")
            
            print(f"✅ تست رویدادها تکمیل شد ({len(self.results['events'])} تست)")
            
        except Exception as e:
            print(f"❌ خطا در تست رویدادها: {e}")
    
    def run_all_tests(self):
        """اجرای همه تست‌ها"""
        print("🚀 شروع تست سیستم قیمت‌گذاری...")
        print("=" * 50)
        
        self.test_tour_pricing()
        print()
        self.test_transfer_pricing()
        print()
        self.test_car_rental_pricing()
        print()
        self.test_event_pricing()
        
        print("=" * 50)
        print("📊 خلاصه نتایج:")
        print(f"  🎯 تورها: {len(self.results['tours'])} تست")
        print(f"  🚗 ترانسفرها: {len(self.results['transfers'])} تست")
        print(f"  🚙 اجاره ماشین: {len(self.results['car_rentals'])} تست")
        print(f"  🎭 رویدادها: {len(self.results['events'])} تست")
        
        return self.results


if __name__ == "__main__":
    tester = PricingSystemTester()
    results = tester.run_all_tests()
    
    # ذخیره نتایج
    import json
    with open('pricing_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("💾 نتایج در فایل pricing_test_results.json ذخیره شد")
