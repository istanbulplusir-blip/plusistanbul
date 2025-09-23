#!/usr/bin/env python3
"""
ایجاد کمیسیون برای سفارش موجود ایجنت تست
"""

import os
import sys
import django

# تنظیم Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from users.models import User
from agents.models import AgentCommission
from orders.models import Order
from decimal import Decimal


def create_commission_for_existing_order():
    """ایجاد کمیسیون برای سفارش موجود"""
    
    print("💰 ایجاد کمیسیون برای سفارش موجود")
    print("=" * 50)
    
    try:
        agent = User.objects.get(username='agenttest')
        print(f"✅ ایجنت پیدا شد: {agent.username}")
    except User.DoesNotExist:
        print("❌ ایجنت agenttest پیدا نشد!")
        return False
    
    # پیدا کردن سفارش موجود
    orders = Order.objects.filter(agent=agent)
    if not orders.exists():
        print("❌ هیچ سفارشی برای ایجنت پیدا نشد!")
        return False
    
    order = orders.first()
    print(f"✅ سفارش پیدا شد: {order.order_number}")
    print(f"   مبلغ سفارش: ${order.total_amount}")
    print(f"   نرخ کمیسیون: {order.agent_commission_rate}%")
    print(f"   مبلغ کمیسیون: ${order.agent_commission_amount}")
    
    # بررسی وجود کمیسیون
    existing_commission = AgentCommission.objects.filter(agent=agent, order=order).first()
    if existing_commission:
        print(f"⚠️ کمیسیون از قبل وجود دارد: {existing_commission.id}")
        print(f"   مبلغ کمیسیون: ${existing_commission.commission_amount}")
        print(f"   وضعیت: {existing_commission.status}")
        return True
    
    # ایجاد کمیسیون
    commission = AgentCommission.objects.create(
        agent=agent,
        order=order,
        commission_rate=order.agent_commission_rate,
        order_amount=order.total_amount,
        commission_amount=order.agent_commission_amount,
        currency=order.currency,
        status='pending',
        notes='Commission created for existing order'
    )
    
    print(f"✅ کمیسیون ایجاد شد!")
    print(f"   ID: {commission.id}")
    print(f"   مبلغ کمیسیون: ${commission.commission_amount}")
    print(f"   نرخ کمیسیون: {commission.commission_rate}%")
    print(f"   وضعیت: {commission.status}")
    
    # به‌روزرسانی آمار ایجنت
    agent_profile = agent.agent_profile
    agent_profile.total_orders += 1
    agent_profile.total_commission_earned += commission.commission_amount
    agent_profile.save()
    
    print(f"✅ آمار ایجنت به‌روزرسانی شد")
    print(f"   کل سفارشات: {agent_profile.total_orders}")
    print(f"   کل کمیسیون: ${agent_profile.total_commission_earned}")
    
    return True


def main():
    """اجرای اصلی"""
    
    success = create_commission_for_existing_order()
    
    if success:
        print(f"\n🎉 کمیسیون با موفقیت ایجاد شد!")
        print(f"حالا می‌توانید دوباره اسکریپت check_agent_data.py را اجرا کنید.")
    else:
        print(f"\n❌ خطا در ایجاد کمیسیون!")


if __name__ == '__main__':
    main()
