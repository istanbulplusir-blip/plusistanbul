"""
اصلاح AgentPricingService برای استفاده از تنظیمات ارز کاربر ایجنت
"""

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from shared.services import CurrencyConverterService

from .models import AgentPricingRule


class AgentPricingService:
    """سرویس محاسبه قیمت برای ایجنت‌ها - نسخه اصلاح شده"""
    
    @staticmethod
    def calculate_transfer_price_for_agent(route, vehicle_type, agent, passenger_count, trip_type='one_way', **kwargs):
        """محاسبه قیمت ترانسفر برای ایجنت با پشتیبانی از ارز کاربر"""
        
        try:
            from transfers.models import TransferRoutePricing
            pricing = TransferRoutePricing.objects.get(
                route=route,
                vehicle_type=vehicle_type
            )
            
            # محاسبه قیمت با سرویس موجود
            price_data = pricing._calculate_transfer_price(
                hour=kwargs.get('hour'),
                return_hour=kwargs.get('return_hour'),
                is_round_trip=(trip_type == 'round_trip'),
                selected_options=kwargs.get('selected_options', [])
            )
            
            base_total = Decimal(str(price_data['final_price'])) * passenger_count
            
            # اعمال قوانین قیمت‌گذاری ایجنت
            agent_price = AgentPricingService._apply_agent_pricing_rules(
                agent=agent,
                product_type='transfer',
                base_price=base_total,
                product_id=route.id,
                variant_id=vehicle_type
            )
            
            # تبدیل ارز به ارز مورد نظر ایجنت
            agent_preferred_currency = getattr(agent, 'preferred_currency', 'USD')
            pricing_currency = getattr(pricing, 'currency', 'USD')
            
            # تبدیل قیمت‌ها به ارز مورد نظر ایجنت
            if agent_preferred_currency != pricing_currency:
                base_total_converted = CurrencyConverterService.convert_currency(
                    base_total, pricing_currency, agent_preferred_currency
                )
                agent_price_converted = CurrencyConverterService.convert_currency(
                    agent_price, pricing_currency, agent_preferred_currency
                )
            else:
                base_total_converted = base_total
                agent_price_converted = agent_price
            
            # Safely convert price_breakdown values to float
            price_breakdown = {}
            for k, v in price_data.items():
                if isinstance(v, (int, float, str)):
                    try:
                        # تبدیل مقادیر breakdown به ارز مورد نظر
                        if k in ['base_price', 'outbound_price', 'return_price', 'final_price', 'options_total']:
                            if agent_preferred_currency != pricing_currency:
                                v_converted = CurrencyConverterService.convert_currency(
                                    Decimal(str(v)), pricing_currency, agent_preferred_currency
                                )
                                price_breakdown[k] = float(v_converted)
                            else:
                                price_breakdown[k] = float(v)
                        else:
                            price_breakdown[k] = float(v)
                    except (ValueError, TypeError):
                        price_breakdown[k] = v
                else:
                    price_breakdown[k] = v
            
            return {
                'base_price': float(base_total_converted),
                'agent_price': float(agent_price_converted),
                'total': float(agent_price_converted),
                'savings': float(base_total_converted - agent_price_converted),
                'savings_percentage': float(((base_total_converted - agent_price_converted) / base_total_converted) * 100) if base_total_converted > 0 else 0,
                'pricing_method': AgentPricingService._get_pricing_method(agent, 'transfer'),
                'passenger_count': passenger_count,
                'trip_type': trip_type,
                'vehicle_type': vehicle_type,
                'route_name': f"{route.origin} → {route.destination}",
                'price_breakdown': price_breakdown,
                'currency': agent_preferred_currency,  # استفاده از ارز مورد نظر ایجنت
                'original_currency': pricing_currency,  # ارز اصلی برای مرجع
                'conversion_applied': agent_preferred_currency != pricing_currency
            }
            
        except TransferRoutePricing.DoesNotExist:
            raise ValueError("Transfer pricing not found")
    
    @staticmethod
    def calculate_tour_price_for_agent(tour, variant, agent, participants, selected_options=None, include_fees_taxes=True):
        """محاسبه قیمت تور برای ایجنت با پشتیبانی از ارز کاربر"""
        
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
        
        # تبدیل ارز به ارز مورد نظر ایجنت
        agent_preferred_currency = getattr(agent, 'preferred_currency', 'USD')
        tour_currency = getattr(tour, 'currency', 'USD')
        
        # تبدیل قیمت‌ها به ارز مورد نظر ایجنت
        if agent_preferred_currency != tour_currency:
            base_total_converted = CurrencyConverterService.convert_currency(
                base_total, tour_currency, agent_preferred_currency
            )
            agent_subtotal_converted = CurrencyConverterService.convert_currency(
                agent_subtotal, tour_currency, agent_preferred_currency
            )
        else:
            base_total_converted = base_total
            agent_subtotal_converted = agent_subtotal
        
        # محاسبه فیس و تکس برای قیمت ایجنت
        fees_taxes_info = {}
        if include_fees_taxes:
            fees_taxes_info = AgentPricingService._calculate_fees_and_taxes(agent_subtotal_converted)
        
        agent_fees = fees_taxes_info.get('fees_total', 0)
        agent_taxes = fees_taxes_info.get('tax_total', 0)
        agent_total = float(agent_subtotal_converted) + agent_fees + agent_taxes
        
        return {
            'base_price': float(base_total_converted),
            'agent_subtotal': float(agent_subtotal_converted),
            'agent_fees': agent_fees,
            'agent_taxes': agent_taxes,
            'agent_total': agent_total,
            'savings': float(base_total_converted - agent_subtotal_converted),
            'savings_percentage': float(((base_total_converted - agent_subtotal_converted) / base_total_converted) * 100) if base_total_converted > 0 else 0,
            'pricing_method': AgentPricingService._get_pricing_method(agent, 'tour'),
            'participants': participants,
            'options': selected_options or [],
            'breakdown': {k: float(v) for k, v in base_pricing['breakdown'].items()},
            'currency': agent_preferred_currency,  # استفاده از ارز مورد نظر ایجنت
            'original_currency': tour_currency,  # ارز اصلی برای مرجع
            'conversion_applied': agent_preferred_currency != tour_currency,
            'fees_taxes_breakdown': fees_taxes_info
        }
