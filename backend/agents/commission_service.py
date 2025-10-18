"""
سرویس مدیریت کمیسیون ایجنت‌ها
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.db import models
from .models import AgentCommission, AgentProfile, AgentPricingRule
from orders.models import Order


class AgentCommissionService:
    """سرویس مدیریت کمیسیون ایجنت‌ها"""
    
    @staticmethod
    def calculate_commission_for_order(order, agent):
        """محاسبه کمیسیون برای یک سفارش"""
        
        if not agent.is_agent:
            return {
                'success': False,
                'error': 'User is not an agent',
                'commission_amount': Decimal('0.00')
            }
        
        try:
            # دریافت پروفایل ایجنت
            agent_profile = agent.agent_profile
        except AgentProfile.DoesNotExist:
            return {
                'success': False,
                'error': 'Agent profile not found',
                'commission_amount': Decimal('0.00')
            }
        
        # محاسبه کمیسیون بر اساس نوع محصول
        commission_calculations = []
        total_commission = Decimal('0.00')
        
        for cart_item in order.items.all():
            product_type = cart_item.product_type
            item_amount = cart_item.total_price
            
            # محاسبه کمیسیون برای این آیتم
            item_commission = AgentCommissionService._calculate_item_commission(
                agent=agent,
                agent_profile=agent_profile,
                product_type=product_type,
                item_amount=item_amount,
                cart_item=cart_item
            )
            
            commission_calculations.append({
                'product_type': product_type,
                'item_amount': item_amount,
                'commission_rate': item_commission['rate'],
                'commission_amount': item_commission['amount'],
                'method': item_commission['method']
            })
            
            total_commission += item_commission['amount']
        
        return {
            'success': True,
            'total_commission': total_commission,
            'commission_calculations': commission_calculations,
            'agent_profile': {
                'commission_rate': agent_profile.commission_rate,
                'min_commission': agent_profile.min_commission,
                'max_commission': agent_profile.max_commission
            }
        }
    
    @staticmethod
    def _calculate_item_commission(agent, agent_profile, product_type, item_amount, cart_item):
        """محاسبه کمیسیون برای یک آیتم خاص"""
        
        # دریافت قانون قیمت‌گذاری ایجنت
        pricing_rule = AgentPricingRule.objects.filter(
            agent=agent,
            product_type=product_type,
            is_active=True
        ).order_by('-priority').first()
        
        # محاسبه کمیسیون بر اساس قانون قیمت‌گذاری
        if pricing_rule:
            commission_rate = AgentCommissionService._get_commission_rate_from_pricing_rule(
                pricing_rule, agent_profile
            )
            method = f"pricing_rule_{pricing_rule.pricing_method}"
        else:
            # استفاده از نرخ کمیسیون پیش‌فرض
            commission_rate = agent_profile.commission_rate
            method = "default_rate"
        
        # محاسبه مبلغ کمیسیون
        commission_amount = item_amount * (commission_rate / 100)
        
        # اعمال محدودیت‌ها
        if agent_profile.min_commission and commission_amount < agent_profile.min_commission:
            commission_amount = agent_profile.min_commission
        
        if agent_profile.max_commission and commission_amount > agent_profile.max_commission:
            commission_amount = agent_profile.max_commission
        
        return {
            'rate': commission_rate,
            'amount': commission_amount,
            'method': method
        }
    
    @staticmethod
    def _get_commission_rate_from_pricing_rule(pricing_rule, agent_profile):
        """دریافت نرخ کمیسیون از قانون قیمت‌گذاری"""
        
        if pricing_rule.pricing_method == 'discount_percentage':
            # برای تخفیف درصدی، کمیسیون بر اساس مبلغ پس از تخفیف محاسبه می‌شود
            return agent_profile.commission_rate
        
        elif pricing_rule.pricing_method == 'fixed_price':
            # برای قیمت ثابت، کمیسیون بر اساس تفاوت قیمت محاسبه می‌شود
            return agent_profile.commission_rate
        
        elif pricing_rule.pricing_method == 'markup_percentage':
            # برای مارک‌آپ، کمیسیون بیشتر محاسبه می‌شود
            return agent_profile.commission_rate * Decimal('1.2')  # 20% بیشتر
        
        elif pricing_rule.pricing_method == 'custom_factor':
            # برای ضریب سفارشی، کمیسیون بر اساس ضریب محاسبه می‌شود
            return agent_profile.commission_rate * pricing_rule.custom_factor
        
        else:
            return agent_profile.commission_rate
    
    @staticmethod
    @transaction.atomic
    def create_commission_record(order, agent):
        """ایجاد رکورد کمیسیون برای سفارش"""
        
        # محاسبه کمیسیون
        commission_data = AgentCommissionService.calculate_commission_for_order(order, agent)
        
        if not commission_data['success']:
            raise ValidationError(commission_data['error'])
        
        # ایجاد رکورد کمیسیون
        commission = AgentCommission.objects.create(
            agent=agent,
            order=order,
            commission_rate=commission_data['agent_profile']['commission_rate'],
            order_amount=order.total_amount,
            commission_amount=commission_data['total_commission'],
            currency=order.currency,
            status='pending',
            notes=f"Commission calculated for {len(commission_data['commission_calculations'])} items"
        )
        
        # به‌روزرسانی آمار ایجنت
        AgentCommissionService._update_agent_stats(agent, commission_data['total_commission'])
        
        return commission
    
    @staticmethod
    def _update_agent_stats(agent, commission_amount):
        """به‌روزرسانی آمار ایجنت"""
        
        try:
            agent_profile = agent.agent_profile
            
            # به‌روزرسانی مجموع کمیسیون
            agent_profile.total_commission_earned += commission_amount
            
            # به‌روزرسانی تعداد سفارشات
            agent_profile.total_orders += 1
            
            # محاسبه میانگین کمیسیون
            if agent_profile.total_orders > 0:
                agent_profile.average_commission = agent_profile.total_commission_earned / agent_profile.total_orders
            
            agent_profile.save()
            
        except AgentProfile.DoesNotExist:
            pass
    
    @staticmethod
    def approve_commission(commission_id, approved_by=None):
        """تأیید کمیسیون"""
        
        try:
            commission = AgentCommission.objects.get(id=commission_id)
            
            if commission.status != 'pending':
                raise ValidationError("Commission is not in pending status")
            
            commission.status = 'approved'
            commission.approved_at = timezone.now()
            commission.approved_by = approved_by
            commission.save()
            
            return commission
            
        except AgentCommission.DoesNotExist:
            raise ValidationError("Commission not found")
    
    @staticmethod
    def reject_commission(commission_id, reason, rejected_by=None):
        """رد کمیسیون"""
        
        try:
            commission = AgentCommission.objects.get(id=commission_id)
            
            if commission.status != 'pending':
                raise ValidationError("Commission is not in pending status")
            
            commission.status = 'rejected'
            commission.rejected_at = timezone.now()
            commission.rejected_by = rejected_by
            commission.rejection_reason = reason
            commission.save()
            
            return commission
            
        except AgentCommission.DoesNotExist:
            raise ValidationError("Commission not found")
    
    @staticmethod
    def pay_commission(commission_id, payment_method, payment_reference=None, paid_by=None):
        """پرداخت کمیسیون"""
        
        try:
            commission = AgentCommission.objects.get(id=commission_id)
            
            if commission.status != 'approved':
                raise ValidationError("Commission must be approved before payment")
            
            commission.status = 'paid'
            commission.paid_at = timezone.now()
            commission.paid_by = paid_by
            commission.payment_method = payment_method
            commission.payment_reference = payment_reference
            commission.save()
            
            # به‌روزرسانی آمار ایجنت
            try:
                agent_profile = commission.agent.agent_profile
                agent_profile.total_commission_paid += commission.commission_amount
                agent_profile.save()
            except AgentProfile.DoesNotExist:
                pass
            
            return commission
            
        except AgentCommission.DoesNotExist:
            raise ValidationError("Commission not found")
    
    @staticmethod
    def get_agent_commission_summary(agent, start_date=None, end_date=None):
        """دریافت خلاصه کمیسیون ایجنت"""
        
        queryset = AgentCommission.objects.filter(agent=agent)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # آمار کلی
        total_commission = queryset.aggregate(
            total=models.Sum('commission_amount')
        )['total'] or Decimal('0.00')
        
        total_orders = queryset.count()
        
        # آمار بر اساس وضعیت
        status_stats = {}
        for status in ['pending', 'approved', 'paid', 'rejected']:
            status_stats[status] = queryset.filter(status=status).aggregate(
                count=models.Count('id'),
                amount=models.Sum('commission_amount')
            )
        
        # آمار بر اساس نوع محصول
        product_stats = {}
        for product_type in ['tour', 'transfer', 'car_rental', 'event']:
            # استفاده از distinct برای جلوگیری از تکرار
            product_queryset = queryset.filter(
                order__items__product_type=product_type
            ).distinct()
            
            product_stats[product_type] = product_queryset.aggregate(
                count=models.Count('id'),
                amount=models.Sum('commission_amount')
            )
        
        return {
            'total_commission': total_commission,
            'total_orders': total_orders,
            'status_stats': status_stats,
            'product_stats': product_stats,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    @staticmethod
    def get_commission_history(agent, limit=50, offset=0):
        """دریافت تاریخچه کمیسیون ایجنت"""
        
        commissions = AgentCommission.objects.filter(agent=agent).order_by('-created_at')
        
        return {
            'commissions': commissions[offset:offset + limit],
            'total_count': commissions.count(),
            'has_more': commissions.count() > offset + limit
        }
    
    @staticmethod
    def calculate_monthly_commission(agent, year, month):
        """محاسبه کمیسیون ماهانه"""
        
        from django.db.models import Sum, Count
        
        monthly_commissions = AgentCommission.objects.filter(
            agent=agent,
            created_at__year=year,
            created_at__month=month
        )
        
        return {
            'year': year,
            'month': month,
            'total_commission': monthly_commissions.aggregate(
                total=Sum('commission_amount')
            )['total'] or Decimal('0.00'),
            'total_orders': monthly_commissions.count(),
            'pending_commission': monthly_commissions.filter(status='pending').aggregate(
                total=Sum('commission_amount')
            )['total'] or Decimal('0.00'),
            'paid_commission': monthly_commissions.filter(status='paid').aggregate(
                total=Sum('commission_amount')
            )['total'] or Decimal('0.00')
        }
