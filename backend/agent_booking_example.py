#!/usr/bin/env python3
"""
مثال کامل از نحوه استفاده از سیستم ثبت سفارش ایجنت
"""

import os
import sys
import django
from datetime import datetime, date, time

# تنظیم Django
sys.path.append('/path/to/your/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from users.models import User
from agents.services import AgentBookingService
from tours.models import Tour, TourVariant, TourSchedule
from transfers.models import TransferRoute, TransferRoutePricing


class AgentBookingExample:
    """مثال کامل از سیستم ثبت سفارش ایجنت"""
    
    def __init__(self):
        self.agent = None
        self.customer = None
    
    def setup_agent_and_customer(self):
        """تنظیم ایجنت و مشتری"""
        print("🔧 تنظیم ایجنت و مشتری...")
        
        # پیدا کردن یا ایجاد ایجنت
        self.agent = User.objects.filter(role='agent').first()
        if not self.agent:
            print("❌ هیچ ایجنت فعالی یافت نشد")
            return False
        
        print(f"✅ ایجنت: {self.agent.username} ({self.agent.agent_code})")
        
        # ایجاد مشتری جدید
        customer_data = {
            'email': 'customer@example.com',
            'first_name': 'احمد',
            'last_name': 'محمدی',
            'phone': '+989123456789',
            'notes': 'مشتری VIP'
        }
        
        try:
            self.customer, agent_customer = AgentBookingService.create_customer_for_agent(
                self.agent, customer_data
            )
            print(f"✅ مشتری ایجاد شد: {self.customer.first_name} {self.customer.last_name}")
            return True
        except Exception as e:
            print(f"❌ خطا در ایجاد مشتری: {e}")
            return False
    
    def example_tour_booking(self):
        """مثال ثبت تور"""
        print("\n🎯 مثال ثبت تور...")
        
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
            
            schedule = tour.schedules.filter(is_active=True).first()
            if not schedule:
                print("❌ هیچ برنامه فعالی یافت نشد")
                return
            
            print(f"📋 تور: {tour.title}")
            print(f"📋 واریانت: {variant.name}")
            print(f"📋 برنامه: {schedule.date}")
            
            # داده‌های ثبت تور
            tour_data = {
                'tour_id': str(tour.id),
                'variant_id': str(variant.id),
                'schedule_id': str(schedule.id),
                'booking_date': schedule.date,
                'booking_time': schedule.start_time,
                'participants': {
                    'adult': 2,
                    'child': 1,
                    'infant': 0
                },
                'selected_options': [
                    {
                        'id': 'option1',
                        'name': 'گاید خصوصی',
                        'price': 50.00,
                        'quantity': 1
                    }
                ]
            }
            
            # ثبت تور
            result = AgentBookingService.book_tour_for_customer(
                self.agent, self.customer, tour_data
            )
            
            if result['success']:
                print(f"✅ تور با موفقیت ثبت شد!")
                print(f"📄 شماره سفارش: {result['order_number']}")
                print(f"💰 مبلغ کل: {result['total_amount']} USD")
                print(f"💵 کمیسیون: {result['commission_amount']} USD")
            else:
                print(f"❌ خطا در ثبت تور: {result['error']}")
                
        except Exception as e:
            print(f"❌ خطا در مثال تور: {e}")
    
    def example_transfer_booking(self):
        """مثال ثبت ترانسفر"""
        print("\n🚗 مثال ثبت ترانسفر...")
        
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
            
            print(f"📋 مسیر: {route.name or f'{route.origin} → {route.destination}'}")
            print(f"📋 نوع وسیله: {pricing.vehicle_name}")
            
            # داده‌های ثبت ترانسفر
            transfer_data = {
                'route_id': str(route.id),
                'vehicle_type': pricing.vehicle_type,
                'booking_date': date.today(),
                'booking_time': time(14, 0),  # ساعت 2 بعدازظهر
                'passenger_count': 4,
                'trip_type': 'round_trip',
                'return_hour': 16,  # ساعت 4 بعدازظهر
                'pickup_address': 'فرودگاه امام خمینی',
                'dropoff_address': 'هتل اسپیناس پالاس',
                'selected_options': [
                    {
                        'id': 'option1',
                        'name': 'کودک صندلی',
                        'price': 15.00,
                        'quantity': 1
                    }
                ]
            }
            
            # ثبت ترانسفر
            result = AgentBookingService.book_transfer_for_customer(
                self.agent, self.customer, transfer_data
            )
            
            if result['success']:
                print(f"✅ ترانسفر با موفقیت ثبت شد!")
                print(f"📄 شماره سفارش: {result['order_number']}")
                print(f"💰 مبلغ کل: {result['total_amount']} USD")
                print(f"💵 کمیسیون: {result['commission_amount']} USD")
            else:
                print(f"❌ خطا در ثبت ترانسفر: {result['error']}")
                
        except Exception as e:
            print(f"❌ خطا در مثال ترانسفر: {e}")
    
    def example_car_rental_booking(self):
        """مثال ثبت اجاره ماشین"""
        print("\n🚙 مثال ثبت اجاره ماشین...")
        
        try:
            # پیدا کردن ماشین فعال
            from car_rentals.models import CarRental
            car = CarRental.objects.filter(is_active=True).first()
            if not car:
                print("❌ هیچ ماشین فعالی یافت نشد")
                return
            
            print(f"📋 ماشین: {car.brand} {car.model} ({car.year})")
            print(f"📋 قیمت روزانه: {car.price_per_day} USD")
            
            # داده‌های ثبت اجاره ماشین
            car_data = {
                'car_id': str(car.id),
                'pickup_date': date.today(),
                'pickup_time': time(10, 0),
                'dropoff_date': date.today().replace(day=date.today().day + 3),
                'dropoff_time': time(10, 0),
                'days': 3,
                'hours': 0,
                'include_insurance': True,
                'driver_name': 'احمد محمدی',
                'driver_phone': '+989123456789',
                'selected_options': [
                    {
                        'id': 'option1',
                        'name': 'GPS',
                        'price': 10.00,
                        'quantity': 1
                    }
                ]
            }
            
            # ثبت اجاره ماشین
            result = AgentBookingService.book_car_rental_for_customer(
                self.agent, self.customer, car_data
            )
            
            if result['success']:
                print(f"✅ اجاره ماشین با موفقیت ثبت شد!")
                print(f"📄 شماره سفارش: {result['order_number']}")
                print(f"💰 مبلغ کل: {result['total_amount']} USD")
                print(f"💵 کمیسیون: {result['commission_amount']} USD")
            else:
                print(f"❌ خطا در ثبت اجاره ماشین: {result['error']}")
                
        except Exception as e:
            print(f"❌ خطا در مثال اجاره ماشین: {e}")
    
    def show_agent_summary(self):
        """نمایش خلاصه ایجنت"""
        print("\n📊 خلاصه ایجنت...")
        
        try:
            # دریافت مشتریان
            customers = AgentBookingService.get_agent_customers(self.agent)
            print(f"👥 تعداد مشتریان: {len(customers)}")
            
            # دریافت سفارشات
            orders = AgentBookingService.get_agent_orders(self.agent)
            print(f"📦 تعداد سفارشات: {len(orders)}")
            
            # محاسبه آمار
            total_sales = sum(order['total_amount'] for order in orders)
            total_commission = sum(order['commission_amount'] for order in orders)
            
            print(f"💰 فروش کل: {total_sales} USD")
            print(f"💵 کمیسیون کل: {total_commission} USD")
            
            # نمایش آخرین سفارشات
            print("\n📋 آخرین سفارشات:")
            for order in orders[:3]:
                print(f"  • {order['order_number']}: {order['customer_name']} - {order['total_amount']} USD")
                
        except Exception as e:
            print(f"❌ خطا در نمایش خلاصه: {e}")
    
    def run_example(self):
        """اجرای مثال کامل"""
        print("🚀 شروع مثال سیستم ثبت سفارش ایجنت...")
        print("=" * 60)
        
        # تنظیم ایجنت و مشتری
        if not self.setup_agent_and_customer():
            return
        
        # مثال‌های مختلف
        self.example_tour_booking()
        self.example_transfer_booking()
        self.example_car_rental_booking()
        
        # نمایش خلاصه
        self.show_agent_summary()
        
        print("=" * 60)
        print("✅ مثال کامل شد!")


if __name__ == "__main__":
    example = AgentBookingExample()
    example.run_example()
