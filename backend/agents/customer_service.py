"""
سرویس مدیریت مشتریان ایجنت‌ها
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum, Avg
from django.contrib.auth import get_user_model

from .models import AgentCustomer, AgentProfile
from orders.models import Order

User = get_user_model()


class AgentCustomerService:
    """سرویس مدیریت مشتریان ایجنت‌ها"""
    
    @staticmethod
    def create_customer_for_agent(agent, customer_data):
        """ایجاد مشتری جدید برای ایجنت"""
        
        if not agent.is_agent:
            raise ValidationError("User is not an agent")
        
        with transaction.atomic():
            # بررسی اینکه آیا مشتری قبلاً وجود دارد
            existing_customer = User.objects.filter(
                email=customer_data['email']
            ).first()
            
            if existing_customer:
                # بررسی اینکه آیا این مشتری قبلاً با این ایجنت مرتبط است
                agent_customer = AgentCustomer.objects.filter(
                    agent=agent,
                    customer=existing_customer
                ).first()
                
                if agent_customer:
                    raise ValidationError("Customer already exists for this agent")
                
                # ایجاد ارتباط جدید با مشتری موجود
                agent_customer = AgentCustomer.objects.create(
                    agent=agent,
                    customer=existing_customer,
                    customer_name=customer_data.get('name', f"{existing_customer.first_name} {existing_customer.last_name}".strip()),
                    customer_email=existing_customer.email,
                    customer_phone=customer_data.get('phone', existing_customer.phone_number or ''),
                    customer_address=customer_data.get('address', ''),
                    customer_city=customer_data.get('city', ''),
                    customer_country=customer_data.get('country', ''),
                    customer_birth_date=customer_data.get('birth_date'),
                    customer_gender=customer_data.get('gender', ''),
                    preferred_language=customer_data.get('preferred_language', 'fa'),
                    preferred_contact_method=customer_data.get('preferred_contact_method', 'email'),
                    customer_status=customer_data.get('customer_status', 'active'),
                    customer_tier=customer_data.get('customer_tier', 'bronze'),
                    relationship_notes=customer_data.get('relationship_notes', ''),
                    special_requirements=customer_data.get('special_requirements', ''),
                    marketing_consent=customer_data.get('marketing_consent', False),
                    created_by_agent=False  # مشتری قبلاً وجود داشته
                )
                
                return existing_customer, agent_customer
            
            else:
                # ایجاد مشتری جدید
                customer = User.objects.create_user(
                    username=customer_data['email'],
                    email=customer_data['email'],
                    password=customer_data.get('password', User.objects.make_random_password()),
                    first_name=customer_data.get('first_name', ''),
                    last_name=customer_data.get('last_name', ''),
                    phone_number=customer_data.get('phone', ''),
                    role='customer',
                )
                
                # ایجاد ارتباط ایجنت-مشتری
                agent_customer = AgentCustomer.objects.create(
                    agent=agent,
                    customer=customer,
                    customer_name=f"{customer.first_name} {customer.last_name}".strip() or customer.username,
                    customer_email=customer.email,
                    customer_phone=customer_data.get('phone', customer.phone_number or ''),
                    customer_address=customer_data.get('address', ''),
                    customer_city=customer_data.get('city', ''),
                    customer_country=customer_data.get('country', ''),
                    customer_birth_date=customer_data.get('birth_date') if customer_data.get('birth_date') else None,
                    customer_gender=customer_data.get('gender') if customer_data.get('gender') else '',
                    preferred_language=customer_data.get('preferred_language', 'fa'),
                    preferred_contact_method=customer_data.get('preferred_contact_method', 'email'),
                    customer_status=customer_data.get('customer_status', 'active'),
                    customer_tier=customer_data.get('customer_tier', 'bronze'),
                    relationship_notes=customer_data.get('relationship_notes', ''),
                    special_requirements=customer_data.get('special_requirements', ''),
                    marketing_consent=customer_data.get('marketing_consent', False),
                    created_by_agent=True
                )
                
                # ارسال ایمیل خوش‌آمدگویی و تأیید
                from .utils import send_customer_welcome_email, send_email_verification
                
                # ارسال ایمیل خوش‌آمدگویی با credentials
                send_credentials = customer_data.get('send_credentials', True)
                if send_credentials:
                    password = customer_data.get('password', User.objects.make_random_password())
                    email_sent = send_customer_welcome_email(customer, password, agent)
                    if email_sent:
                        agent_customer.credentials_sent = True
                        agent_customer.credentials_sent_at = timezone.now()
                        agent_customer.save()
                
                # ارسال ایمیل تأیید
                verification_sent = send_email_verification(customer)
                
                return customer, agent_customer
    
    @staticmethod
    def update_customer_info(agent, customer_id, customer_data):
        """به‌روزرسانی اطلاعات مشتری"""
        
        try:
            agent_customer = AgentCustomer.objects.get(
                agent=agent,
                customer_id=customer_id
            )
            
            # به‌روزرسانی اطلاعات مشتری
            customer = agent_customer.customer
            customer.first_name = customer_data.get('first_name', customer.first_name)
            customer.last_name = customer_data.get('last_name', customer.last_name)
            customer.phone_number = customer_data.get('phone', customer.phone_number)
            customer.save()
            
            # به‌روزرسانی اطلاعات AgentCustomer
            agent_customer.customer_name = customer_data.get('name', agent_customer.customer_name)
            agent_customer.customer_email = customer_data.get('email', agent_customer.customer_email)
            agent_customer.customer_phone = customer_data.get('phone', agent_customer.customer_phone)
            agent_customer.customer_address = customer_data.get('address', agent_customer.customer_address)
            agent_customer.customer_city = customer_data.get('city', agent_customer.customer_city)
            agent_customer.customer_country = customer_data.get('country', agent_customer.customer_country)
            agent_customer.customer_birth_date = customer_data.get('birth_date') if customer_data.get('birth_date') else agent_customer.customer_birth_date
            agent_customer.customer_gender = customer_data.get('gender') if customer_data.get('gender') else agent_customer.customer_gender
            agent_customer.preferred_language = customer_data.get('preferred_language', agent_customer.preferred_language)
            agent_customer.preferred_contact_method = customer_data.get('preferred_contact_method', agent_customer.preferred_contact_method)
            agent_customer.customer_status = customer_data.get('customer_status', agent_customer.customer_status)
            agent_customer.customer_tier = customer_data.get('customer_tier', agent_customer.customer_tier)
            agent_customer.relationship_notes = customer_data.get('relationship_notes', agent_customer.relationship_notes)
            agent_customer.special_requirements = customer_data.get('special_requirements', agent_customer.special_requirements)
            agent_customer.marketing_consent = customer_data.get('marketing_consent', agent_customer.marketing_consent)
            agent_customer.save()
            
            return agent_customer
            
        except AgentCustomer.DoesNotExist:
            raise ValidationError("Customer not found for this agent")
    
    @staticmethod
    def get_agent_customers(agent, filters=None):
        """دریافت لیست مشتریان ایجنت"""
        
        queryset = AgentCustomer.objects.filter(agent=agent)
        
        if filters:
            # فیلتر بر اساس وضعیت
            if filters.get('status'):
                queryset = queryset.filter(customer_status=filters['status'])
            
            # فیلتر بر اساس تیر
            if filters.get('tier'):
                queryset = queryset.filter(customer_tier=filters['tier'])
            
            # فیلتر بر اساس جستجو
            if filters.get('search'):
                search_term = filters['search']
                queryset = queryset.filter(
                    Q(customer_name__icontains=search_term) |
                    Q(customer_email__icontains=search_term) |
                    Q(customer_phone__icontains=search_term)
                )
            
            # فیلتر بر اساس تاریخ ایجاد
            if filters.get('created_after'):
                queryset = queryset.filter(created_at__gte=filters['created_after'])
            
            if filters.get('created_before'):
                queryset = queryset.filter(created_at__lte=filters['created_before'])
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_customer_detail(agent, customer_id):
        """دریافت جزئیات مشتری"""
        
        try:
            agent_customer = AgentCustomer.objects.get(
                agent=agent,
                customer_id=customer_id
            )
            
            # دریافت آمار سفارشات مشتری
            orders = Order.objects.filter(
                user=agent_customer.customer,
                agent=agent
            ).order_by('-created_at')
            
            # محاسبه آمار
            total_orders = orders.count()
            total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            last_order_date = orders.first().created_at if orders.exists() else None
            
            # به‌روزرسانی آمار در AgentCustomer
            agent_customer.total_orders = total_orders
            agent_customer.total_spent = total_spent
            agent_customer.last_order_date = last_order_date
            agent_customer.save()
            
            return {
                'agent_customer': agent_customer,
                'customer': agent_customer.customer,
                'orders': orders[:10],  # آخرین 10 سفارش
                'total_orders': total_orders,
                'total_spent': total_spent,
                'last_order_date': last_order_date
            }
            
        except AgentCustomer.DoesNotExist:
            raise ValidationError("Customer not found for this agent")
    
    @staticmethod
    def get_customer_statistics(agent):
        """دریافت آمار مشتریان ایجنت"""
        
        customers = AgentCustomer.objects.filter(agent=agent)
        
        # آمار کلی
        total_customers = customers.count()
        active_customers = customers.filter(customer_status='active').count()
        vip_customers = customers.filter(customer_status='vip').count()
        
        # آمار بر اساس تیر
        tier_stats = customers.values('customer_tier').annotate(
            count=Count('id')
        ).order_by('customer_tier')
        
        # آمار بر اساس وضعیت
        status_stats = customers.values('customer_status').annotate(
            count=Count('id')
        ).order_by('customer_status')
        
        # آمار بر اساس زبان ترجیحی
        language_stats = customers.values('preferred_language').annotate(
            count=Count('id')
        ).order_by('preferred_language')
        
        # آمار بر اساس روش تماس ترجیحی
        contact_stats = customers.values('preferred_contact_method').annotate(
            count=Count('id')
        ).order_by('preferred_contact_method')
        
        # آمار مالی
        total_spent = customers.aggregate(total=Sum('total_spent'))['total'] or Decimal('0.00')
        average_spent = customers.aggregate(avg=Avg('total_spent'))['avg'] or Decimal('0.00')
        
        # مشتریان برتر (بر اساس مبلغ خرج شده)
        top_customers = customers.order_by('-total_spent')[:5]
        
        return {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'vip_customers': vip_customers,
            'tier_stats': list(tier_stats),
            'status_stats': list(status_stats),
            'language_stats': list(language_stats),
            'contact_stats': list(contact_stats),
            'total_spent': total_spent,
            'average_spent': average_spent,
            'top_customers': list(top_customers.values(
                'customer_name', 'customer_email', 'total_spent', 'total_orders', 'customer_tier'
            ))
        }
    
    @staticmethod
    def update_customer_tier(agent, customer_id, new_tier):
        """به‌روزرسانی تیر مشتری"""
        
        try:
            agent_customer = AgentCustomer.objects.get(
                agent=agent,
                customer_id=customer_id
            )
            
            old_tier = agent_customer.customer_tier
            agent_customer.customer_tier = new_tier
            agent_customer.save()
            
            return {
                'success': True,
                'old_tier': old_tier,
                'new_tier': new_tier,
                'message': f'Customer tier updated from {old_tier} to {new_tier}'
            }
            
        except AgentCustomer.DoesNotExist:
            raise ValidationError("Customer not found for this agent")
    
    @staticmethod
    def update_customer_status(agent, customer_id, new_status):
        """به‌روزرسانی وضعیت مشتری"""
        
        try:
            agent_customer = AgentCustomer.objects.get(
                agent=agent,
                customer_id=customer_id
            )
            
            old_status = agent_customer.customer_status
            agent_customer.customer_status = new_status
            agent_customer.save()
            
            return {
                'success': True,
                'old_status': old_status,
                'new_status': new_status,
                'message': f'Customer status updated from {old_status} to {new_status}'
            }
            
        except AgentCustomer.DoesNotExist:
            raise ValidationError("Customer not found for this agent")
    
    @staticmethod
    def delete_customer_relationship(agent, customer_id):
        """حذف ارتباط مشتری با ایجنت"""
        
        try:
            agent_customer = AgentCustomer.objects.get(
                agent=agent,
                customer_id=customer_id
            )
            
            # اگر مشتری توسط ایجنت ایجاد شده، کاربر را نیز حذف کن
            if agent_customer.created_by_agent:
                agent_customer.customer.delete()
            
            agent_customer.delete()
            
            return {
                'success': True,
                'message': 'Customer relationship deleted successfully'
            }
            
        except AgentCustomer.DoesNotExist:
            raise ValidationError("Customer not found for this agent")
    
    @staticmethod
    def get_customer_orders(agent, customer_id, limit=20, offset=0):
        """دریافت سفارشات مشتری"""
        
        try:
            agent_customer = AgentCustomer.objects.get(
                agent=agent,
                customer_id=customer_id
            )
            
            orders = Order.objects.filter(
                user=agent_customer.customer,
                agent=agent
            ).order_by('-created_at')
            
            total_count = orders.count()
            orders_page = orders[offset:offset + limit]
            
            return {
                'orders': orders_page,
                'total_count': total_count,
                'has_more': total_count > offset + limit
            }
            
        except AgentCustomer.DoesNotExist:
            raise ValidationError("Customer not found for this agent")
    
    @staticmethod
    def search_customers(agent, search_term, limit=20):
        """جستجوی مشتریان"""
        
        customers = AgentCustomer.objects.filter(
            agent=agent
        ).filter(
            Q(customer_name__icontains=search_term) |
            Q(customer_email__icontains=search_term) |
            Q(customer_phone__icontains=search_term)
        ).order_by('-created_at')[:limit]
        
        return customers
    
    @staticmethod
    def get_recent_customers(agent, limit=10):
        """دریافت مشتریان اخیر"""
        
        customers = AgentCustomer.objects.filter(
            agent=agent
        ).order_by('-created_at')[:limit]
        
        return customers
    
    @staticmethod
    def get_vip_customers(agent):
        """دریافت مشتریان VIP"""
        
        customers = AgentCustomer.objects.filter(
            agent=agent,
            customer_status='vip'
        ).order_by('-total_spent')
        
        return customers
