"""
تست سیستم کمیسیون ایجنت‌ها
"""

import os
import sys
import django

# تنظیم Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from decimal import Decimal
from django.utils import timezone
from users.models import User
from agents.models import AgentProfile, AgentCommission, AgentPricingRule
from agents.commission_service import AgentCommissionService
from agents.pricing_service import AgentPricingService
from tours.models import Tour, TourVariant
from orders.models import Order, OrderItem


def test_commission_calculation():
    """تست محاسبه کمیسیون"""
    
    print("🧪 تست سیستم کمیسیون ایجنت‌ها")
    print("=" * 50)
    
    # ایجاد ایجنت تست
    try:
        agent = User.objects.get(username='test_agent')
    except User.DoesNotExist:
        agent = User.objects.create_user(
            username='test_agent',
            email='agent@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Agent',
            role='agent'
        )
    
    # ایجاد پروفایل ایجنت
    try:
        agent_profile = agent.agent_profile
    except AgentProfile.DoesNotExist:
        agent_profile = AgentProfile.objects.create(
            user=agent,
            company_name='Test Travel Agency',
            commission_rate=Decimal('15.00'),  # 15% کمیسیون
            min_commission=Decimal('10.00'),
            max_commission=Decimal('1000.00'),
            payment_method='bank_transfer',
            payment_frequency='monthly'
        )
    
    print(f"✅ ایجنت ایجاد شد: {agent.username}")
    print(f"   نرخ کمیسیون: {agent_profile.commission_rate}%")
    print(f"   حداقل کمیسیون: ${agent_profile.min_commission}")
    print(f"   حداکثر کمیسیون: ${agent_profile.max_commission}")
    
    # ایجاد قانون قیمت‌گذاری برای تور
    pricing_rule, created = AgentPricingRule.objects.get_or_create(
        agent=agent,
        product_type='tour',
        defaults={
            'pricing_method': 'discount_percentage',
            'discount_percentage': Decimal('20.00'),  # 20% تخفیف
            'is_active': True,
            'priority': 1,
            'description': 'تخفیف ویژه برای تورها'
        }
    )
    
    if created:
        print(f"✅ قانون قیمت‌گذاری ایجاد شد: {pricing_rule.get_pricing_method_display()}")
    else:
        print(f"✅ قانون قیمت‌گذاری موجود: {pricing_rule.get_pricing_method_display()}")
    
    # تست محاسبه قیمت تور
    try:
        tour = Tour.objects.first()
        if not tour:
            print("❌ هیچ توری یافت نشد")
            return
        
        variant = TourVariant.objects.filter(tour=tour).first()
        if not variant:
            print("❌ هیچ واریانت توری یافت نشد")
            return
        
        participants = {'adult': 2, 'child': 1}
        
        # محاسبه قیمت با سرویس ایجنت
        pricing_result = AgentPricingService.calculate_tour_price_for_agent(
            tour=tour,
            variant=variant,
            agent=agent,
            participants=participants,
            selected_options=[]
        )
        
        print(f"\n📊 محاسبه قیمت تور:")
        print(f"   تور: {tour.title}")
        print(f"   واریانت: {variant.name}")
        print(f"   قیمت پایه: ${pricing_result['base_price']:.2f}")
        print(f"   قیمت ایجنت: ${pricing_result['agent_subtotal']:.2f}")
        print(f"   فیس سرویس: ${pricing_result['agent_fees']:.2f}")
        print(f"   مالیات: ${pricing_result['agent_taxes']:.2f}")
        print(f"   قیمت نهایی: ${pricing_result['agent_total']:.2f}")
        print(f"   صرفه‌جویی: ${pricing_result['savings']:.2f} ({pricing_result['savings_percentage']:.1f}%)")
        
        # تست محاسبه کمیسیون
        commission_data = AgentCommissionService.calculate_commission_for_order(
            order=None,  # برای تست، order را None می‌گذاریم
            agent=agent
        )
        
        print(f"\n💰 محاسبه کمیسیون:")
        print(f"   موفقیت: {commission_data['success']}")
        if commission_data['success']:
            print(f"   کل کمیسیون: ${commission_data['total_commission']:.2f}")
            print(f"   نرخ کمیسیون: {commission_data['agent_profile']['commission_rate']}%")
        else:
            print(f"   خطا: {commission_data['error']}")
        
        # تست خلاصه کمیسیون
        summary = AgentCommissionService.get_agent_commission_summary(agent)
        print(f"\n📈 خلاصه کمیسیون:")
        print(f"   کل کمیسیون: ${summary['total_commission']:.2f}")
        print(f"   کل سفارشات: {summary['total_orders']}")
        
        # تست کمیسیون ماهانه
        current_date = timezone.now()
        monthly_data = AgentCommissionService.calculate_monthly_commission(
            agent=agent,
            year=current_date.year,
            month=current_date.month
        )
        print(f"\n📅 کمیسیون ماهانه ({monthly_data['year']}/{monthly_data['month']}):")
        print(f"   کل کمیسیون: ${monthly_data['total_commission']:.2f}")
        print(f"   کل سفارشات: {monthly_data['total_orders']}")
        print(f"   کمیسیون در انتظار: ${monthly_data['pending_commission']:.2f}")
        print(f"   کمیسیون پرداخت شده: ${monthly_data['paid_commission']:.2f}")
        
        print(f"\n✅ تست سیستم کمیسیون با موفقیت انجام شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست: {str(e)}")
        import traceback
        traceback.print_exc()


def test_pricing_rules():
    """تست قوانین قیمت‌گذاری"""
    
    print(f"\n🧪 تست قوانین قیمت‌گذاری")
    print("=" * 50)
    
    try:
        agent = User.objects.get(username='test_agent')
        
        # دریافت خلاصه قوانین قیمت‌گذاری
        summary = AgentPricingService.get_agent_pricing_summary(agent)
        
        print(f"📋 خلاصه قوانین قیمت‌گذاری:")
        print(f"   تعداد قوانین: {summary['total_rules']}")
        
        for product_type, rule_info in summary['by_product_type'].items():
            print(f"   {product_type}: {rule_info['method']} - {rule_info['value']}")
        
        print(f"✅ تست قوانین قیمت‌گذاری با موفقیت انجام شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست قوانین قیمت‌گذاری: {str(e)}")


if __name__ == '__main__':
    test_commission_calculation()
    test_pricing_rules()
