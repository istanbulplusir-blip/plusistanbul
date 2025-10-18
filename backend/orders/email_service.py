"""
Email service for order notifications.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
from .email_templates import get_order_confirmation_template, get_order_status_change_template

logger = logging.getLogger(__name__)


class OrderEmailService:
    """Service for sending order-related emails."""
    
    @staticmethod
    def send_order_confirmation(order):
        """Send order confirmation email."""
        try:
            subject = f"تایید سفارش #{order.order_number} - پیکان توریسم"
            html_message = get_order_confirmation_template(order)
            plain_message = strip_tags(html_message)
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [order.customer_email]
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Order confirmation email sent for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order confirmation email for order {order.order_number}: {str(e)}")
            return False
    
    @staticmethod
    def send_order_status_change(order, old_status, new_status):
        """Send order status change email."""
        try:
            subject = f"تغییر وضعیت سفارش #{order.order_number} - پیکان توریسم"
            html_message = get_order_status_change_template(order, old_status, new_status)
            plain_message = strip_tags(html_message)
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [order.customer_email]
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Order status change email sent for order {order.order_number}: {old_status} -> {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order status change email for order {order.order_number}: {str(e)}")
            return False
    
    @staticmethod
    def send_order_cancelled(order):
        """Send order cancellation email."""
        try:
            subject = f"لغو سفارش #{order.order_number} - پیکان توریسم"
            
            html_message = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="fa">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Tahoma', 'Arial', sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; }}
                    .header {{ text-align: center; color: #dc3545; margin-bottom: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>❌ سفارش لغو شد</h1>
                    </div>
                    
                    <p>سلام <strong>{order.customer_name}</strong> عزیز،</p>
                    <p>سفارش شماره <strong>#{order.order_number}</strong> با موفقیت لغو شد.</p>
                    
                    <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>توجه:</strong> در صورت پرداخت مبلغ، طی 3-5 روز کاری به حساب شما بازگردانده خواهد شد.</p>
                    </div>
                    
                    <p>در صورت داشتن سوال، با پشتیبانی تماس بگیرید:</p>
                    <p><strong>تلفن:</strong> 021-12345678</p>
                    <p><strong>واتساپ:</strong> 09123456789</p>
                    
                    <p>از اعتماد شما متشکریم! 🙏</p>
                </div>
            </body>
            </html>
            """
            
            plain_message = strip_tags(html_message)
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [order.customer_email]
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Order cancellation email sent for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order cancellation email for order {order.order_number}: {str(e)}")
            return False
