"""
Django signals for order notifications.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order
from .email_service import OrderEmailService
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def capture_old_status(sender, instance, **kwargs):
    """Capture old status before saving."""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """Send email notifications when order is created or status changes."""
    
    # Skip if email is not available
    if not instance.customer_email:
        logger.warning(f"No email available for order {instance.order_number}")
        return
    
    try:
        if created:
            # New order created - send confirmation if status is confirmed
            if instance.status == 'confirmed':
                OrderEmailService.send_order_confirmation(instance)
                logger.info(f"Order confirmation email triggered for new order {instance.order_number}")
        else:
            # Existing order updated - check for status change
            old_status = getattr(instance, '_old_status', None)
            new_status = instance.status
            
            if old_status and old_status != new_status:
                logger.info(f"Order status changed: {old_status} -> {new_status} for order {instance.order_number}")
                
                # Send appropriate email based on new status
                if new_status == 'confirmed':
                    OrderEmailService.send_order_confirmation(instance)
                elif new_status == 'cancelled':
                    OrderEmailService.send_order_cancelled(instance)
                else:
                    OrderEmailService.send_order_status_change(instance, old_status, new_status)
                    
    except Exception as e:
        logger.error(f"Error in order notification signal for order {instance.order_number}: {str(e)}")


@receiver(post_save, sender=Order)
def update_capacity_on_status_change(sender, instance, created, **kwargs):
    """Update capacity when order status changes."""
    try:
        if not created:  # Only for existing orders
            old_status = getattr(instance, '_old_status', None)
            new_status = instance.status
            
            if old_status and old_status != new_status:
                logger.info(f"Updating capacity for order {instance.order_number}: {old_status} -> {new_status}")
                
                # Import here to avoid circular imports
                from .models import OrderService
                OrderService._update_capacity_for_order_status_change(instance, old_status, new_status)
                
    except Exception as e:
        logger.error(f"Error updating capacity for order {instance.order_number}: {str(e)}")


# WhatsApp notification helper (for future use)
class WhatsAppService:
    """Service for WhatsApp notifications."""
    
    @staticmethod
    def generate_order_message(order):
        """Generate WhatsApp message for order."""
        
        items_text = "\n".join([
            f"• {item.product_title} (تعداد: {item.quantity}) - {item.total_price:,} {item.currency}"
            for item in order.items.all()
        ])
        
        message = f"""سلام 👋
سفارش جدید ثبت شد:

📋 شماره سفارش: #{order.order_number}
👤 نام مشتری: {order.customer_name}
📞 تلفن: {order.customer_phone}
📧 ایمیل: {order.customer_email}

🛍️ آیتم‌های سفارش:
{items_text}

💰 مجموع کل: {order.total_amount:,} {order.currency}

⏰ تاریخ سفارش: {order.created_at.strftime('%Y/%m/%d - %H:%M')}

لطفاً پس از دریافت مبلغ، سفارش را تایید کنید.
"""
        return message
    
    @staticmethod
    def generate_whatsapp_link(phone_number, message):
        """Generate WhatsApp deep link."""
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{phone_number}?text={encoded_message}"
