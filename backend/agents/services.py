"""
سرویس‌های ایجنت برای مدیریت مشتریان و سفارشات
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models import User
from cart.models import CartService, CartItem
from orders.models import OrderService, Order
from tours.models import Tour, TourVariant, TourSchedule
from transfers.models import TransferRoute, TransferRoutePricing
from car_rentals.models import CarRental
from events.models import Event, EventPerformance


class AgentBookingService:
    """سرویس ثبت سفارش ایجنت برای مشتریان"""
    
    @staticmethod
    def create_customer_for_agent(agent, customer_data):
        """Enhanced customer creation with proper authentication setup"""
        if not agent.is_agent:
            raise ValidationError("User is not an agent")
        
        # Check if customer already exists
        from .utils import check_existing_customer, link_existing_customer_to_agent
        existing_customer = check_existing_customer(customer_data['email'])
        
        if existing_customer:
            # Link existing customer to agent
            customer = User.objects.get(id=existing_customer['id'])
            success = link_existing_customer_to_agent(
                customer, 
                agent, 
                customer_data.get('notes', '')
            )
            
            if success:
                return customer, customer.agentcustomers.filter(agent=agent).first()
            else:
                raise ValidationError("Failed to link existing customer to agent")
        
        # Generate secure password or use provided one
        from .utils import generate_secure_password, send_customer_welcome_email, send_email_verification
        password = customer_data.get('password')
        if not password:
            password = generate_secure_password()
        
        # Create customer with proper authentication setup
        customer = User.objects.create_user(
            username=customer_data['email'],
            email=customer_data['email'],
            password=password,
            first_name=customer_data.get('first_name', ''),
            last_name=customer_data.get('last_name', ''),
            phone_number=customer_data.get('phone', ''),
            role='customer',
            is_email_verified=False,  # Will be verified via email
            is_active=True
        )
        
        # Create agent-customer relationship
        from .models import AgentCustomer
        agent_customer = AgentCustomer.objects.create(
            agent=agent,
            customer=customer,
            customer_name=f"{customer.first_name} {customer.last_name}".strip() or customer.username,
            customer_email=customer.email,
            customer_phone=customer.phone_number or '',
            relationship_notes=customer_data.get('notes', ''),
            created_by_agent=True,
            requires_verification=True,  # New field
            credentials_sent=False,
            credentials_sent_at=None
        )
        
        # Send welcome email with login credentials if requested
        send_credentials = customer_data.get('send_credentials', True)
        if send_credentials:
            email_sent = send_customer_welcome_email(customer, password, agent)
            if email_sent:
                agent_customer.credentials_sent = True
                agent_customer.credentials_sent_at = timezone.now()
                agent_customer.save()
        
        # Send email verification
        verification_sent = send_email_verification(customer)
        
        return customer, agent_customer
    
    @staticmethod
    def book_tour_for_customer(agent, customer, tour_data):
        """ثبت تور برای مشتری"""
        try:
            with transaction.atomic():
                # بررسی صحت داده‌ها
                tour = Tour.objects.get(id=tour_data['tour_id'], is_active=True)
                variant = TourVariant.objects.get(id=tour_data['variant_id'], tour=tour, is_active=True)
                schedule = TourSchedule.objects.get(id=tour_data['schedule_id'], tour=tour, is_active=True)
                
                # بررسی ظرفیت
                participants = tour_data['participants']
                total_participants = sum(participants.values())
                if total_participants <= 0:
                    raise ValidationError("حداقل یک نفر باید انتخاب شود")
                
                # محاسبه قیمت با قیمت‌گذاری مخصوص ایجنت
                from .pricing_service import AgentPricingService
                pricing_result = AgentPricingService.calculate_tour_price_for_agent(
                    tour=tour,
                    variant=variant,
                    agent=agent,
                    participants=participants,
                    selected_options=tour_data.get('selected_options', [])
                )
                
                # ایجاد سبد خرید برای مشتری
                cart = CartService.get_or_create_cart(
                    session_id=f"agent_{agent.id}_{customer.id}_{timezone.now().timestamp()}",
                    user=customer
                )
                
                # اضافه کردن تور به سبد
                cart_item_data = {
                    'product_type': 'tour',
                    'product_id': str(tour.id),
                    'variant_id': str(variant.id),
                    'variant_name': variant.name,
                    'booking_date': tour_data['booking_date'],
                    'booking_time': tour_data['booking_time'],
                    'quantity': total_participants,
                    'unit_price': pricing_result['agent_total'] / total_participants,  # قیمت ایجنت تقسیم بر تعداد نفرات
                    'total_price': pricing_result['agent_total'],  # قیمت کل ایجنت
                    'selected_options': tour_data.get('selected_options', []) if isinstance(tour_data.get('selected_options', []), list) else [],
                    'booking_data': {
                        'schedule_id': str(schedule.id),
                        'participants': participants,
                        'agent_booking': True,
                        'agent_id': str(agent.id),
                        'pricing_info': {
                            'base_price': pricing_result['base_price'],
                            'agent_price': pricing_result['agent_total'],
                            'savings': pricing_result['savings'],
                            'pricing_method': pricing_result['pricing_method']
                        }
                    }
                }
                
                cart_item = CartService.add_to_cart(cart, cart_item_data)
                
                # ایجاد سفارش
                order = OrderService.create_order_from_cart(
                    cart=cart,
                    user=customer,
                    agent=agent
                )
                
                # Handle payment method
                payment_method = tour_data.get('payment_method', 'whatsapp')
                if payment_method == 'direct_payment':
                    # For direct payment, mark as paid immediately (placeholder implementation)
                    order.status = 'paid'
                    order.payment_status = 'paid'
                    order.payment_method = 'bank_gateway'
                    order.save()
                else:
                    # For WhatsApp payment, keep as pending
                    order.payment_method = 'whatsapp'
                    order.save()
                
                # ایجاد کمیسیون با سرویس جدید
                from .commission_service import AgentCommissionService
                commission = AgentCommissionService.create_commission_record(order, agent)
                
                return {
                    'success': True,
                    'order_number': order.order_number,
                    'total_amount': float(order.total_amount),
                    'commission_amount': float(commission.commission_amount),
                    'cart_item_id': str(cart_item.id),
                    'pricing_info': {
                        'base_price': pricing_result['base_price'],
                        'agent_price': pricing_result['agent_total'],
                        'savings': pricing_result['savings'],
                        'savings_percentage': pricing_result['savings_percentage'],
                        'pricing_method': pricing_result['pricing_method']
                    },
                    'message': 'تور با موفقیت ثبت شد'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'خطا در ثبت تور'
            }
    
    @staticmethod
    def book_transfer_for_customer(agent, customer, transfer_data):
        """Book transfer for customer using unified transfer booking service"""
        try:
            from transfers.booking_service import TransferBookingService
            
            # Use the unified transfer booking service
            result = TransferBookingService.book_transfer(
                user=customer,
                transfer_data=transfer_data,
                agent=agent
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error booking transfer'
            }
    
    @staticmethod
    def book_car_rental_for_customer(agent, customer, car_rental_data):
        """ثبت اجاره ماشین برای مشتری"""
        try:
            with transaction.atomic():
                # بررسی صحت داده‌ها
                car = CarRental.objects.get(id=car_rental_data['car_id'], is_active=True)
                
                # محاسبه قیمت
                total_price = car.calculate_total_price(
                    days=car_rental_data['days'],
                    hours=car_rental_data.get('hours', 0),
                    include_insurance=car_rental_data.get('include_insurance', False)
                )
                
                # ایجاد سبد خرید
                cart = CartService.get_or_create_cart(
                    session_id=f"agent_{agent.id}_{customer.id}_{timezone.now().timestamp()}",
                    user=customer
                )
                
                # اضافه کردن اجاره ماشین به سبد
                cart_item_data = {
                    'product_type': 'car_rental',
                    'product_id': str(car.id),
                    'variant_id': None,
                    'variant_name': f"{car.brand} {car.model}",
                    'booking_date': car_rental_data['pickup_date'],
                    'booking_time': car_rental_data['pickup_time'],
                    'pickup_date': car_rental_data['pickup_date'],
                    'dropoff_date': car_rental_data['dropoff_date'],
                    'pickup_time': car_rental_data['pickup_time'],
                    'dropoff_time': car_rental_data['dropoff_time'],
                    'quantity': 1,
                    'unit_price': car.price_per_day,
                    'selected_options': car_rental_data.get('selected_options', []),
                    'booking_data': {
                        'days': car_rental_data['days'],
                        'hours': car_rental_data.get('hours', 0),
                        'include_insurance': car_rental_data.get('include_insurance', False),
                        'driver_name': car_rental_data.get('driver_name', ''),
                        'driver_phone': car_rental_data.get('driver_phone', ''),
                        'agent_booking': True,
                        'agent_id': str(agent.id),
                        'insurance_total': car_rental_data.get('insurance_total', 0)
                    }
                }
                
                cart_item = CartService.add_to_cart(cart, cart_item_data)
                
                # ایجاد سفارش
                order = OrderService.create_order_from_cart(
                    cart=cart,
                    user=customer,
                    agent=agent
                )
                
                # ایجاد کمیسیون
                from .commission_service import AgentCommissionService
                commission = AgentCommissionService.create_commission_record(order, agent)
                
                return {
                    'success': True,
                    'order_number': order.order_number,
                    'total_amount': float(order.total_amount),
                    'commission_amount': float(commission.commission_amount),
                    'cart_item_id': str(cart_item.id),
                    'message': 'اجاره ماشین با موفقیت ثبت شد'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'خطا در ثبت اجاره ماشین'
            }
    
    @staticmethod
    def book_event_for_customer(agent, customer, event_data):
        """ثبت رویداد برای مشتری"""
        try:
            with transaction.atomic():
                # بررسی صحت داده‌ها
                event = Event.objects.get(id=event_data['event_id'], is_active=True)
                performance = EventPerformance.objects.get(
                    id=event_data['performance_id'],
                    event=event,
                    is_active=True
                )
                
                # محاسبه قیمت
                from events.pricing_service import EventPriceCalculator
                calculator = EventPriceCalculator()
                
                pricing_result = calculator.calculate_ticket_price(
                    section_name=event_data['section'],
                    ticket_type_id=event_data['ticket_type_id'],
                    quantity=event_data['quantity'],
                    selected_options=event_data.get('selected_options', []),
                    apply_fees=False,
                    apply_taxes=False
                )
                
                # ایجاد سبد خرید
                cart = CartService.get_or_create_cart(
                    session_id=f"agent_{agent.id}_{customer.id}_{timezone.now().timestamp()}",
                    user=customer
                )
                
                # اضافه کردن رویداد به سبد
                cart_item_data = {
                    'product_type': 'event',
                    'product_id': str(event.id),
                    'variant_id': event_data['ticket_type_id'],
                    'variant_name': event_data['section'],
                    'booking_date': performance.date,
                    'booking_time': performance.start_time,
                    'quantity': event_data['quantity'],
                    'unit_price': pricing_result['base_price'],
                    'selected_options': event_data.get('selected_options', []),
                    'booking_data': {
                        'performance_id': str(performance.id),
                        'section': event_data['section'],
                        'ticket_type_id': event_data['ticket_type_id'],
                        'agent_booking': True,
                        'agent_id': str(agent.id)
                    }
                }
                
                cart_item = CartService.add_to_cart(cart, cart_item_data)
                
                # ایجاد سفارش
                order = OrderService.create_order_from_cart(
                    cart=cart,
                    user=customer,
                    agent=agent
                )
                
                # ایجاد کمیسیون
                from .commission_service import AgentCommissionService
                commission = AgentCommissionService.create_commission_record(order, agent)
                
                return {
                    'success': True,
                    'order_number': order.order_number,
                    'total_amount': float(order.total_amount),
                    'commission_amount': float(commission.commission_amount),
                    'cart_item_id': str(cart_item.id),
                    'message': 'رویداد با موفقیت ثبت شد'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'خطا در ثبت رویداد'
            }
    
    @staticmethod
    def get_agent_customers(agent):
        """دریافت لیست مشتریان ایجنت"""
        from .models import AgentCustomer
        customers = AgentCustomer.objects.filter(agent=agent, is_active=True)
        
        return [{
            'id': str(customer.customer.id),
            'name': customer.customer_name,
            'email': customer.customer_email,
            'phone': customer.customer_phone,
            'created_at': customer.created_at.isoformat(),
            'notes': customer.relationship_notes
        } for customer in customers]
    
    @staticmethod
    def get_agent_orders(agent, status=None):
        """دریافت سفارشات ایجنت"""
        orders = Order.objects.filter(agent=agent)
        if status:
            orders = orders.filter(status=status)
        
        return [{
            'order_number': order.order_number,
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'total_amount': float(order.total_amount),
            'commission_amount': float(order.agent_commission_amount),
            'status': order.status,
            'payment_status': order.payment_status,
            'created_at': order.created_at.isoformat(),
            'items': [{
                'product_type': item.product_type,
                'product_title': item.product_title,
                'quantity': item.quantity,
                'total_price': float(item.total_price)
            } for item in order.items.all()]
        } for order in orders.order_by('-created_at')]
