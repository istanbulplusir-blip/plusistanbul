"""
سرویس محاسبه قیمت مخصوص ایجنت‌ها
"""

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import AgentPricingRule


class AgentPricingService:
    """سرویس محاسبه قیمت برای ایجنت‌ها"""
    
    @staticmethod
    def calculate_tour_price_for_agent(tour, variant, agent, participants, selected_options=None, include_fees_taxes=True):
        """محاسبه قیمت تور برای ایجنت"""
        
        # Convert option IDs to proper format for TourPricingService
        formatted_options = []
        if selected_options:
            from tours.models import TourOption
            for option_id in selected_options:
                try:
                    option = TourOption.objects.get(id=option_id, tour=tour, is_active=True)
                    formatted_options.append({
                        'option_id': option_id,
                        'price': float(option.price),
                        'quantity': 1
                    })
                except TourOption.DoesNotExist:
                    continue
        
        # محاسبه قیمت پایه با استفاده از سرویس موجود
        from tours.services import TourPricingService
        base_pricing = TourPricingService.calculate_price(
            tour=tour,
            variant=variant,
            participants=participants,
            selected_options=formatted_options
        )
        base_total = base_pricing['total']
        
        # اعمال قوانین قیمت‌گذاری ایجنت
        agent_subtotal = AgentPricingService._apply_agent_pricing_rules(
            agent=agent,
            product_type='tour',
            base_price=base_total,
            product_id=tour.id,
            variant_id=variant.id,
            participants=participants
        )
        
        # محاسبه فیس و تکس برای قیمت ایجنت
        fees_taxes_info = {}
        if include_fees_taxes:
            fees_taxes_info = AgentPricingService._calculate_fees_and_taxes(agent_subtotal)
        
        agent_fees = fees_taxes_info.get('fees_total', 0)
        agent_taxes = fees_taxes_info.get('tax_total', 0)
        agent_total = float(agent_subtotal) + agent_fees + agent_taxes
        
        return {
            'base_price': float(base_total),
            'agent_subtotal': float(agent_subtotal),
            'agent_fees': agent_fees,
            'agent_taxes': agent_taxes,
            'agent_total': agent_total,
            'savings': float(base_total - agent_subtotal),
            'savings_percentage': float(((base_total - agent_subtotal) / base_total) * 100) if base_total > 0 else 0,
            'pricing_method': AgentPricingService._get_pricing_method(agent, 'tour'),
            'participants': participants,
            'options': selected_options or [],
            'breakdown': {k: float(v) for k, v in base_pricing['breakdown'].items()},
            'currency': base_pricing['currency'],
            'fees_taxes_breakdown': fees_taxes_info
        }
    
    @staticmethod
    def calculate_transfer_price_for_agent(route, vehicle_type, agent, passenger_count, trip_type='one_way', **kwargs):
        """محاسبه قیمت ترانسفر برای ایجنت - نسخه کامل"""
        
        try:
            from transfers.models import TransferRoutePricing, TransferOption
            pricing = TransferRoutePricing.objects.get(
                route=route,
                vehicle_type=vehicle_type,
                is_active=True
            )
            
            # بررسی محدودیت ظرفیت
            passenger_count_int = int(passenger_count) if isinstance(passenger_count, str) else passenger_count
            if passenger_count_int > pricing.max_passengers:
                raise ValidationError(f'تعداد مسافر ({passenger_count_int}) از ظرفیت خودرو ({pricing.max_passengers}) بیشتر است')
            
            # محاسبه قیمت پایه (بدون کمیسیون ایجنت)
            price_data = pricing.calculate_price(
                hour=kwargs.get('hour'),
                return_hour=kwargs.get('return_hour'),
                is_round_trip=(trip_type == 'round_trip'),
                selected_options=kwargs.get('selected_options', [])
            )
            
            # محاسبه قیمت اپشن‌ها
            options_total = Decimal('0.00')
            if kwargs.get('selected_options'):
                for option_data in kwargs['selected_options']:
                    try:
                        option = TransferOption.objects.get(id=option_data['id'])
                        quantity = int(option_data.get('quantity', 1))
                        options_total += option.price * quantity
                    except TransferOption.DoesNotExist:
                        continue
            
            # قیمت نهایی شامل اپشن‌ها (قیمت عادی بدون کمیسیون)
            if isinstance(price_data, dict):
                # Use the final_price from the calculation (includes all discounts)
                final_price = Decimal(str(price_data.get('final_price', 0)))
                base_transfer_price = price_data.get('base_price', 0)
                outbound_surcharge = price_data.get('outbound_surcharge', 0)
                return_surcharge = price_data.get('return_surcharge', 0)
                round_trip_discount = price_data.get('round_trip_discount', 0)
            else:
                base_transfer_price = price_data
                final_price = Decimal(str(base_transfer_price)) + options_total
            
            # محاسبه subtotal (قبل از fees و taxes)
            subtotal = final_price
            
            # اعمال تخفیف ایجنت روی subtotal (قبل از fees و taxes)
            agent_subtotal = AgentPricingService._apply_agent_pricing_rules(
                agent=agent,
                product_type='transfer',
                base_price=subtotal,
                product_id=route.id,
                variant_id=vehicle_type
            )
            
            # محاسبه fees و taxes روی agent_subtotal
            fees_taxes_info = AgentPricingService._calculate_fees_and_taxes(agent_subtotal)
            
            # قیمت نهایی ایجنت (شامل fees و taxes)
            agent_final_price = agent_subtotal + Decimal(str(fees_taxes_info['fees_total'])) + Decimal(str(fees_taxes_info['tax_total']))
            
            # محاسبه صرفه‌جویی (بر اساس subtotal)
            savings = subtotal - agent_subtotal
            savings_percentage = (savings / subtotal * 100) if subtotal > 0 else 0
            
            # محاسبه کمیسیون ایجنت (بر اساس agent_subtotal)
            commission_rate = AgentPricingService._get_agent_commission_rate(agent)
            commission_amount = agent_subtotal * (Decimal(str(commission_rate)) / Decimal('100'))
            
            # Safely convert price_breakdown values to float
            price_breakdown = {}
            if isinstance(price_data, dict):
                for k, v in price_data.items():
                    try:
                        price_breakdown[k] = float(v) if v is not None else 0.0
                    except (ValueError, TypeError):
                        price_breakdown[k] = 0.0
            
            # Add options total to breakdown
            price_breakdown['options_total'] = float(options_total)
            
            return {
                'base_price': float(base_transfer_price),  # Use actual base price, not final price
                'final_price': float(final_price),  # قیمت نهایی بدون تخفیف ایجنت (برای مشتری)
                'agent_total': float(agent_final_price),  # قیمت نهایی ایجنت (شامل fees و taxes)
                'agent_subtotal': float(agent_subtotal),  # subtotal ایجنت (قبل از fees و taxes)
                'subtotal': float(subtotal),  # subtotal اصلی (قبل از fees و taxes)
                'options_total': float(options_total),
                'savings': float(savings),
                'savings_percentage': float(savings_percentage),
                'pricing_method': 'agent_discount',
                'price_breakdown': price_breakdown,
                'currency': getattr(pricing, 'currency', 'USD'),
                'capacity_info': {
                    'max_passengers': pricing.max_passengers,
                    'requested_passengers': passenger_count_int,
                    'capacity_available': True
                },
                'trip_info': {
                    'trip_type': trip_type,
                    'vehicle_type': vehicle_type,
                    'route_name': f"{route.origin} → {route.destination}"
                },
                # Add actual discount percentages for display
                'round_trip_discount_percentage': float(route.round_trip_discount_percentage) if route.round_trip_discount_enabled else 0.0,
                'peak_hour_surcharge_percentage': float(route.peak_hour_surcharge),
                'midnight_surcharge_percentage': float(route.midnight_surcharge),
                # Add fees and taxes information
                'fees_taxes_breakdown': fees_taxes_info,
                # Add commission information
                'commission_info': {
                    'commission_rate': float(commission_rate),
                    'commission_amount': float(commission_amount),
                    'commission_base': float(agent_subtotal)  # Base for commission calculation (subtotal)
                }
            }
            
        except TransferRoutePricing.DoesNotExist:
            raise ValidationError("Transfer pricing not found")
        except Exception as e:
            raise ValidationError(f'خطا در محاسبه قیمت ترانسفر: {str(e)}')
    
    @staticmethod
    def calculate_car_rental_price_for_agent(car, agent, days, hours=0, include_insurance=False, **kwargs):
        """محاسبه قیمت اجاره ماشین برای ایجنت"""
        
        # محاسبه قیمت پایه
        base_total = car.calculate_total_price(
            days=days,
            hours=hours,
            include_insurance=include_insurance
        )
        
        # اعمال قوانین قیمت‌گذاری ایجنت
        agent_price = AgentPricingService._apply_agent_pricing_rules(
            agent=agent,
            product_type='car_rental',
            base_price=base_total,
            product_id=car.id,
            variant_id=None
        )
        
        return {
            'base_price': float(base_total),
            'agent_price': float(agent_price),
            'savings': float(base_total - agent_price),
            'savings_percentage': float(((base_total - agent_price) / base_total) * 100) if base_total > 0 else 0,
            'pricing_method': AgentPricingService._get_pricing_method(agent, 'car_rental'),
            'car_name': f"{car.brand} {car.model} ({car.year})",
            'rental_type': 'hourly' if days == 0 else 'daily',
            'days': days,
            'hours': hours,
            'include_insurance': include_insurance,
            'daily_rate': float(car.price_per_day),
            'hourly_rate': float(car.price_per_hour) if car.price_per_hour else None,
            'currency': 'USD'
        }
    
    @staticmethod
    def calculate_event_price_for_agent(event, performance, agent, section, ticket_type_id, quantity, **kwargs):
        """محاسبه قیمت رویداد برای ایجنت"""
        
        # محاسبه قیمت پایه (فرضی - باید با سرویس واقعی جایگزین شود)
        base_price_per_ticket = Decimal('50.00')  # قیمت فرضی
        base_total = base_price_per_ticket * quantity
        
        # اعمال قوانین قیمت‌گذاری ایجنت
        agent_price = AgentPricingService._apply_agent_pricing_rules(
            agent=agent,
            product_type='event',
            base_price=base_total,
            product_id=event.id,
            variant_id=ticket_type_id
        )
        
        return {
            'base_price': float(base_total),
            'agent_price': float(agent_price),
            'savings': float(base_total - agent_price),
            'savings_percentage': float(((base_total - agent_price) / base_total) * 100) if base_total > 0 else 0,
            'pricing_method': AgentPricingService._get_pricing_method(agent, 'event'),
            'event_name': event.title,
            'performance_date': performance.date.isoformat(),
            'section': section,
            'quantity': quantity,
            'price_per_ticket': float(base_price_per_ticket),
            'currency': 'USD'
        }
    
    @staticmethod
    def _apply_agent_pricing_rules(agent, product_type, base_price, product_id=None, variant_id=None, participants=None):
        """اعمال قوانین قیمت‌گذاری ایجنت"""
        
        try:
            # جستجوی قانون قیمت‌گذاری فعال
            # Note: AgentPricingRule is linked to User, not Agent directly
            # For now, we'll use default pricing rules
            pricing_rule = None
            
            if not pricing_rule:
                # استفاده از تخفیف پیش‌فرض ایجنت (12% برای ترانسفر)
                if product_type == 'transfer':
                    discount_pct = Decimal('12.0')  # 12% discount for transfers
                    discount = base_price * (discount_pct / Decimal('100'))
                    return base_price - discount
                return base_price
            
            # اعمال قانون قیمت‌گذاری
            if pricing_rule.pricing_method == 'percentage_discount':
                discount = base_price * (pricing_rule.discount_percentage / 100)
                final_price = base_price - discount
                
            elif pricing_rule.pricing_method == 'fixed_price':
                final_price = pricing_rule.fixed_price
                
            elif pricing_rule.pricing_method == 'markup_percentage':
                markup = base_price * (pricing_rule.markup_percentage / 100)
                final_price = base_price + markup
                
            elif pricing_rule.pricing_method == 'custom_factor':
                # برای تورها، اعمال ضریب سفارشی روی قیمت پایه
                final_price = base_price * pricing_rule.custom_factor
                
            else:
                final_price = base_price
            
            # اعمال محدودیت‌ها
            if pricing_rule.min_price and final_price < pricing_rule.min_price:
                final_price = pricing_rule.min_price
            if pricing_rule.max_price and final_price > pricing_rule.max_price:
                final_price = pricing_rule.max_price
            
            return final_price
            
        except Exception as e:
            # در صورت خطا، قیمت پایه را برگردان
            return base_price
    
    @staticmethod
    def _get_pricing_method(agent, product_type):
        """دریافت روش قیمت‌گذاری ایجنت"""
        try:
            pricing_rule = AgentPricingRule.objects.filter(
                agent=agent,
                product_type=product_type,
                is_active=True
            ).order_by('-priority').first()
            
            if pricing_rule:
                return pricing_rule.pricing_method
            else:
                return 'default_discount'
        except:
            return 'default_discount'
    
    @staticmethod
    def _calculate_fees_and_taxes(subtotal):
        """محاسبه فیس و تکس بر اساس سیاست پلتفرم"""
        from decimal import Decimal as _D
        
        subtotal_decimal = _D(str(subtotal))
        discounts = _D('0.00')  # placeholder for future discounts
        service_fee_rate = _D('0.03')  # 3% service fee
        vat_rate = _D('0.09')  # 9% VAT
        
        # محاسبه فیس
        fees_total = (subtotal_decimal * service_fee_rate).quantize(_D('0.01'))
        
        # محاسبه تکس (بر اساس subtotal + fees)
        tax_base = subtotal_decimal - discounts + fees_total
        tax_total = (tax_base * vat_rate).quantize(_D('0.01'))
        
        # محاسبه مجموع کل
        grand_total = (subtotal_decimal - discounts + fees_total + tax_total).quantize(_D('0.01'))
        
        return {
            'subtotal': float(subtotal_decimal),
            'discounts_total': float(discounts),
            'fees_total': float(fees_total),
            'tax_total': float(tax_total),
            'grand_total': float(grand_total),
            'service_fee_rate': float(service_fee_rate),
            'vat_rate': float(vat_rate)
        }
    
    @staticmethod
    def _get_pricing_method(agent, product_type):
        """دریافت روش قیمت‌گذاری استفاده شده"""
        try:
            rule = AgentPricingRule.objects.filter(
                agent=agent, 
                product_type=product_type, 
                is_active=True
            ).order_by('-priority').first()
            
            if rule:
                return rule.pricing_method
            return 'default_discount'
        except:
            return 'default_discount'
    
    @staticmethod
    def _get_agent_commission_rate(agent):
        """دریافت نرخ کمیسیون ایجنت"""
        try:
            from .models import AgentProfile
            profile = agent.agent_profile
            return float(profile.commission_rate)
        except:
            # Default commission rate for transfers
            return 5.0  # 5% default commission
    
    @staticmethod
    def get_agent_pricing_summary(agent):
        """دریافت خلاصه قوانین قیمت‌گذاری ایجنت"""
        
        rules = AgentPricingRule.objects.filter(agent=agent, is_active=True)
        
        summary = {
            'total_rules': rules.count(),
            'by_product_type': {},
            'total_savings_potential': 0
        }
        
        for rule in rules:
            product_type = rule.product_type
            if product_type not in summary['by_product_type']:
                summary['by_product_type'][product_type] = {
                    'method': rule.pricing_method,
                    'value': None,
                    'description': rule.description
                }
                
                # تعیین مقدار بر اساس روش قیمت‌گذاری
                if rule.pricing_method == 'discount_percentage':
                    summary['by_product_type'][product_type]['value'] = f"{rule.discount_percentage}% تخفیف"
                elif rule.pricing_method == 'fixed_price':
                    summary['by_product_type'][product_type]['value'] = f"{rule.fixed_price} USD ثابت"
                elif rule.pricing_method == 'markup_percentage':
                    summary['by_product_type'][product_type]['value'] = f"{rule.markup_percentage}% مارک‌آپ"
                elif rule.pricing_method == 'custom_factor':
                    summary['by_product_type'][product_type]['value'] = f"ضریب {rule.custom_factor}"
        
        return summary
    
    @staticmethod
    def create_pricing_rule(agent, product_type, pricing_method, **kwargs):
        """ایجاد قانون قیمت‌گذاری جدید"""
        
        # بررسی اینکه آیا قانون موجود است
        existing_rule = AgentPricingRule.objects.filter(
            agent=agent,
            product_type=product_type
        ).first()
        
        if existing_rule:
            # به‌روزرسانی قانون موجود
            existing_rule.pricing_method = pricing_method
            existing_rule.discount_percentage = kwargs.get('discount_percentage')
            existing_rule.fixed_price = kwargs.get('fixed_price')
            existing_rule.markup_percentage = kwargs.get('markup_percentage')
            existing_rule.custom_factor = kwargs.get('custom_factor')
            existing_rule.min_price = kwargs.get('min_price')
            existing_rule.max_price = kwargs.get('max_price')
            existing_rule.description = kwargs.get('description', '')
            existing_rule.is_active = kwargs.get('is_active', True)
            existing_rule.save()
            return existing_rule
        else:
            # ایجاد قانون جدید
            return AgentPricingRule.objects.create(
                agent=agent,
                product_type=product_type,
                pricing_method=pricing_method,
                discount_percentage=kwargs.get('discount_percentage'),
                fixed_price=kwargs.get('fixed_price'),
                markup_percentage=kwargs.get('markup_percentage'),
                custom_factor=kwargs.get('custom_factor'),
                min_price=kwargs.get('min_price'),
                max_price=kwargs.get('max_price'),
                description=kwargs.get('description', ''),
                is_active=kwargs.get('is_active', True)
            )
