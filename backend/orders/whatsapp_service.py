"""
WhatsApp integration service for order notifications.
"""

import urllib.parse
from django.conf import settings
from django.utils import timezone
from shared.whatsapp_service import CentralizedWhatsAppService


class WhatsAppService:
    """Service for WhatsApp deep link integration."""
    
    @classmethod
    def get_support_number(cls):
        """Get WhatsApp number from centralized service."""
        return CentralizedWhatsAppService.get_whatsapp_number()
    
    @classmethod
    def generate_order_message(cls, order):
        """Generate WhatsApp message for new order."""
        
        # Format items list
        items_text = ""
        for item in order.items.all():
            items_text += f"• {item.product_title}"
            if item.variant_name:
                items_text += f" ({item.variant_name})"
            total_price = item.unit_price * item.quantity
            items_text += f" - تعداد: {item.quantity} - {total_price:,} {order.currency}\n"
        
        # Special requests (using billing_address as fallback for notes)
        special_requests = ""
        if hasattr(order, 'billing_address') and order.billing_address:
            special_requests = f"\n📝 آدرس:\n{order.billing_address}\n"
        
        # Generate message
        message = f"""سلام 👋

🆕 سفارش جدید ثبت شد:

📋 شماره سفارش: #{order.order_number}
👤 نام مشتری: {order.customer_name}
📞 تلفن: {order.customer_phone}
📧 ایمیل: {order.customer_email}

🛍️ آیتم‌های سفارش:
{items_text}
💰 مجموع کل: {order.total_amount:,} {order.currency}{special_requests}
⏰ تاریخ سفارش: {order.created_at.strftime('%Y/%m/%d - %H:%M')}

لطفاً پس از هماهنگی و دریافت مبلغ، سفارش را در پنل ادمین تایید کنید.

🔗 لینک مدیریت سفارش: {cls._get_admin_order_url(order.order_number)}"""

        return message
    
    @classmethod
    def generate_customer_message(cls, order):
        """Generate WhatsApp message for customer to send."""
        
        # Format items list (shorter for customer)
        items_text = ""
        for item in order.items.all()[:3]:  # Show only first 3 items
            items_text += f"• {item.product_title}\n"
        
        if order.items.count() > 3:
            items_text += f"• و {order.items.count() - 3} آیتم دیگر...\n"
        
        message = f"""سلام 👋

من سفارش شماره #{order.order_number} را در سایت ثبت کردم.

🛍️ خلاصه سفارش:
{items_text}
💰 مجموع: {order.total_amount:,} {order.currency}

لطفاً راهنمایی کنید که چگونه پرداخت را تکمیل کنم.

ممنون 🙏"""

        return message
    
    @classmethod
    def generate_whatsapp_link(cls, message, phone_number=None):
        """Generate WhatsApp deep link."""
        if not phone_number:
            phone_number = cls.get_support_number()
        
        # Use centralized service for formatting
        return CentralizedWhatsAppService.get_whatsapp_url(message)
    
    @classmethod
    def generate_customer_whatsapp_link(cls, order):
        """Generate WhatsApp link for customer to contact support."""
        message = cls.generate_customer_message(order)
        return cls.generate_whatsapp_link(message)
    
    @classmethod
    def generate_admin_whatsapp_link(cls, order):
        """Generate WhatsApp link to notify admin about new order."""
        message = cls.generate_order_message(order)
        return cls.generate_whatsapp_link(message)
    
    @classmethod
    def _get_admin_order_url(cls, order_number):
        """Get admin URL for order management."""
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{base_url}/admin/orders/{order_number}/"
    
    @classmethod
    def get_support_info(cls):
        """Get support contact information."""
        return CentralizedWhatsAppService.get_support_info()
    
    @classmethod
    def _format_phone_number(cls, phone):
        """Format phone number for display."""
        # Remove country code for display
        if phone.startswith('98'):
            phone = phone[2:]
        elif phone.startswith('989'):
            phone = phone[3:]
        
        # Format as 09XX XXX XXXX
        if len(phone) == 10:
            return f"0{phone[:3]} {phone[3:6]} {phone[6:]}"
        
        return phone


# Utility functions for easy access
def get_customer_whatsapp_link(order):
    """Get WhatsApp link for customer to contact support about order."""
    return WhatsAppService.generate_customer_whatsapp_link(order)


def get_admin_whatsapp_link(order):
    """Get WhatsApp link to notify admin about new order."""
    return WhatsAppService.generate_admin_whatsapp_link(order)


def get_support_info():
    """Get support contact information."""
    return WhatsAppService.get_support_info()
