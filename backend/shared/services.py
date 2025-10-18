"""
Shared services for Peykan Tourism Platform.
"""

import requests
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language
from typing import Dict, Optional, Any
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string


class CurrencyConverterService:
    """
    Service for currency conversion.
    Uses external API for real-time rates with caching.
    """
    
    CACHE_TIMEOUT = 3600  # 1 hour
    BASE_CURRENCY = 'USD'
    
    @classmethod
    def get_exchange_rates(cls) -> Dict[str, float]:
        """
        Get exchange rates from cache or API.
        """
        cache_key = 'exchange_rates'
        rates = cache.get(cache_key)
        
        if rates is None:
            rates = cls._fetch_exchange_rates()
            if rates:
                cache.set(cache_key, rates, cls.CACHE_TIMEOUT)
        
        return rates or {}
    
    @classmethod
    def _fetch_exchange_rates(cls) -> Dict[str, float]:
        """
        Fetch exchange rates from external API.
        """
        try:
            # Using a free exchange rate API
            url = f"https://api.exchangerate-api.com/v4/latest/{cls.BASE_CURRENCY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('rates', {})
        except Exception as e:
            # Fallback to mock rates for development
            return cls._get_mock_rates()
    
    @classmethod
    def _get_mock_rates(cls) -> Dict[str, float]:
        """
        Mock exchange rates for development.
        """
        return {
            'USD': 1.0,
            'EUR': 0.85,
            'TRY': 15.5,
            'IRR': 420000,
        }
    
    @classmethod
    def convert_currency(
        cls, 
        amount: Decimal, 
        from_currency: str, 
        to_currency: str
    ) -> Decimal:
        """
        Convert amount from one currency to another.
        """
        if from_currency == to_currency:
            return amount
        
        rates = cls.get_exchange_rates()
        
        if from_currency == cls.BASE_CURRENCY:
            # Converting from base currency
            rate = rates.get(to_currency, 1.0)
            return amount * Decimal(str(rate))
        elif to_currency == cls.BASE_CURRENCY:
            # Converting to base currency
            rate = rates.get(from_currency, 1.0)
            return amount / Decimal(str(rate))
        else:
            # Converting between two non-base currencies
            from_rate = rates.get(from_currency, 1.0)
            to_rate = rates.get(to_currency, 1.0)
            return amount * Decimal(str(to_rate)) / Decimal(str(from_rate))
    
    @classmethod
    def format_price(
        cls, 
        amount: Decimal, 
        currency: str, 
        locale: Optional[str] = None
    ) -> str:
        """
        Format price with currency symbol.
        """
        if locale is None:
            locale = get_language() or 'en'
        
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'TRY': '₺',
            'IRR': 'ریال',
        }
        
        symbol = currency_symbols.get(currency, currency)
        
        if currency == 'IRR':
            # Format Iranian Rial with thousands separator
            formatted_amount = f"{amount:,.0f}"
        else:
            formatted_amount = f"{amount:.2f}"
        
        return f"{symbol}{formatted_amount}"


class LanguageService:
    """
    Service for language-related operations.
    """
    
    SUPPORTED_LANGUAGES = ['fa', 'en', 'tr']
    RTL_LANGUAGES = ['fa']
    
    @classmethod
    def is_rtl(cls, language_code: str) -> bool:
        """
        Check if language is RTL.
        """
        return language_code in cls.RTL_LANGUAGES
    
    @classmethod
    def get_language_direction(cls, language_code: str) -> str:
        """
        Get text direction for language.
        """
        return 'rtl' if cls.is_rtl(language_code) else 'ltr'
    
    @classmethod
    def get_language_name(cls, language_code: str) -> str:
        """
        Get language name.
        """
        language_names = {
            'fa': 'Persian',
            'en': 'English',
            'tr': 'Turkish',
        }
        return language_names.get(language_code, language_code)


class ValidationService:
    """
    Service for common validation operations.
    """
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number format.
        """
        import re
        # Basic phone validation - can be enhanced based on requirements
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_date_range(start_date, end_date) -> bool:
        """
        Validate date range.
        """
        from datetime import date
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        
        return start_date <= end_date


class NotificationService:
    """
    Service for sending notifications (SMS, Email).
    """
    
    @classmethod
    def send_sms(cls, phone: str, message: str) -> bool:
        """
        Send SMS using Kavenegar or mock service.
        """
        if settings.KAVENEGAR_API_KEY:
            return cls._send_sms_kavenegar(phone, message)
        else:
            return cls._send_sms_mock(phone, message)
    
    @classmethod
    def _send_sms_kavenegar(cls, phone: str, message: str) -> bool:
        """
        Send SMS using Kavenegar API.
        """
        try:
            url = "https://api.kavenegar.com/v1/{}/sms/send.json".format(
                settings.KAVENEGAR_API_KEY
            )
            data = {
                'receptor': phone,
                'message': message,
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    @classmethod
    def _send_sms_mock(cls, phone: str, message: str) -> bool:
        """
        Mock SMS service for development.
        """
        print(f"Mock SMS to {phone}: {message}")
        return True
    
    @classmethod
    def send_email(cls, email: str, subject: str, message: str) -> bool:
        """
        Send email.
        """
        try:
            from django.core.mail import send_mail
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return True
        except Exception:
            return False


class CacheService:
    """
    Service for cache operations.
    """
    
    @staticmethod
    def get_user_preferences(user_id: str) -> Dict[str, Any]:
        """
        Get user preferences from cache.
        """
        cache_key = f'user_preferences_{user_id}'
        return cache.get(cache_key, {})
    
    @staticmethod
    def set_user_preferences(user_id: str, preferences: Dict[str, Any]) -> None:
        """
        Set user preferences in cache.
        """
        cache_key = f'user_preferences_{user_id}'
        cache.set(cache_key, preferences, 3600)  # 1 hour
    
    @staticmethod
    def clear_user_preferences(user_id: str) -> None:
        """
        Clear user preferences from cache.
        """
        cache_key = f'user_preferences_{user_id}'
        cache.delete(cache_key)
    
    @staticmethod
    def get_cart_data(session_id: str) -> Dict[str, Any]:
        """
        Get cart data from cache.
        """
        cache_key = f'cart_{session_id}'
        return cache.get(cache_key, {})
    
    @staticmethod
    def set_cart_data(session_id: str, cart_data: Dict[str, Any]) -> None:
        """
        Set cart data in cache.
        """
        cache_key = f'cart_{session_id}'
        cache.set(cache_key, cart_data, 1800)  # 30 minutes
    
    @staticmethod
    def clear_cart_data(session_id: str) -> None:
        """
        Clear cart data from cache.
        """
        cache_key = f'cart_{session_id}'
        cache.delete(cache_key)


def generate_otp_code(length=6):
    """Generate a random OTP code."""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(user_email, otp_code, user_name=None):
    """Send email verification OTP."""
    subject = 'تأیید ایمیل - پلتفرم پیکان توریسم'
    
    # HTML template for email
    html_message = f"""
    <div dir="rtl" style="font-family: Tahoma, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0; font-size: 24px;">پیکان توریسم</h1>
            <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">تأیید آدرس ایمیل</p>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-bottom: 20px;">سلام {user_name or 'کاربر گرامی'}!</h2>
            
            <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                برای تکمیل فرآیند ثبت‌نام، لطفاً کد تأیید زیر را در صفحه مربوطه وارد کنید:
            </p>
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <h3 style="color: white; margin: 0; font-size: 32px; letter-spacing: 5px; font-weight: bold;">{otp_code}</h3>
            </div>
            
            <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                این کد تا 10 دقیقه معتبر است. اگر شما این درخواست را نکرده‌اید، لطفاً این ایمیل را نادیده بگیرید.
            </p>
            
            <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 20px;">
                <p style="color: #999; font-size: 14px; margin: 0;">
                    با تشکر،<br>
                    تیم پیکان توریسم
                </p>
            </div>
        </div>
    </div>
    """
    
    # Plain text version
    message = f"""
    سلام {user_name or 'کاربر گرامی'}!
    
    برای تکمیل فرآیند ثبت‌نام، لطفاً کد تأیید زیر را در صفحه مربوطه وارد کنید:
    
    کد تأیید: {otp_code}
    
    این کد تا 10 دقیقه معتبر است.
    
    با تشکر،
    تیم پیکان توریسم
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email to {user_email}: {e}")
        return False


def send_password_reset_email(user_email, otp_code, user_name=None):
    """Send password reset OTP."""
    subject = 'بازنشانی رمز عبور - پلتفرم پیکان توریسم'
    
    # HTML template for email
    html_message = f"""
    <div dir="rtl" style="font-family: Tahoma, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
        <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0; font-size: 24px;">پیکان توریسم</h1>
            <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">بازنشانی رمز عبور</p>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-bottom: 20px;">سلام {user_name or 'کاربر گرامی'}!</h2>
            
            <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                درخواست بازنشانی رمز عبور برای حساب کاربری شما دریافت شده است. برای ادامه، لطفاً کد تأیید زیر را وارد کنید:
            </p>
            
            <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <h3 style="color: white; margin: 0; font-size: 32px; letter-spacing: 5px; font-weight: bold;">{otp_code}</h3>
            </div>
            
            <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                این کد تا 10 دقیقه معتبر است. اگر شما این درخواست را نکرده‌اید، لطفاً این ایمیل را نادیده بگیرید.
            </p>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="color: #666; margin: 0; font-size: 14px;">
                    <strong>نکته امنیتی:</strong> هرگز کد تأیید خود را با دیگران به اشتراک نگذارید.
                </p>
            </div>
            
            <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 20px;">
                <p style="color: #999; font-size: 14px; margin: 0;">
                    با تشکر،<br>
                    تیم پیکان توریسم
                </p>
            </div>
        </div>
    </div>
    """
    
    # Plain text version
    message = f"""
    سلام {user_name or 'کاربر گرامی'}!
    
    درخواست بازنشانی رمز عبور برای حساب کاربری شما دریافت شده است. برای ادامه، لطفاً کد تأیید زیر را وارد کنید:
    
    کد تأیید: {otp_code}
    
    این کد تا 10 دقیقه معتبر است.
    
    نکته امنیتی: هرگز کد تأیید خود را با دیگران به اشتراک نگذارید.
    
    با تشکر،
    تیم پیکان توریسم
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email to {user_email}: {e}")
        return False


def send_welcome_email(user_email, user_name):
    """Send welcome email after successful registration."""
    subject = 'خوش آمدید به پیکان توریسم!'
    
    # HTML template for email
    html_message = f"""
    <div dir="rtl" style="font-family: Tahoma, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0; font-size: 24px;">پیکان توریسم</h1>
            <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">خوش آمدید!</p>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-bottom: 20px;">سلام {user_name}!</h2>
            
            <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                به خانواده بزرگ پیکان توریسم خوش آمدید! 🎉
            </p>
            
            <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                حالا می‌توانید از تمام امکانات پلتفرم ما استفاده کنید:
            </p>
            
            <ul style="color: #666; line-height: 1.8; margin-bottom: 20px;">
                <li>🛫 رزرو تورهای داخلی و خارجی</li>
                <li>🎭 خرید بلیط رویدادها و کنسرت‌ها</li>
                <li>🚗 رزرو سرویس‌های ترنسفر</li>
                <li>💳 پرداخت امن و آسان</li>
                <li>📱 دسترسی از هر کجا</li>
            </ul>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <a href="http://localhost:3000" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">
                    شروع کنید
                </a>
            </div>
            
            <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 20px;">
                <p style="color: #999; font-size: 14px; margin: 0;">
                    با تشکر،<br>
                    تیم پیکان توریسم
                </p>
            </div>
        </div>
    </div>
    """
    
    # Plain text version
    message = f"""
    سلام {user_name}!
    
    به خانواده بزرگ پیکان توریسم خوش آمدید! 🎉
    
    حالا می‌توانید از تمام امکانات پلتفرم ما استفاده کنید:
    - رزرو تورهای داخلی و خارجی
    - خرید بلیط رویدادها و کنسرت‌ها
    - رزرو سرویس‌های ترنسفر
    - پرداخت امن و آسان
    - دسترسی از هر کجا
    
    برای شروع: http://localhost:3000
    
    با تشکر،
    تیم پیکان توریسم
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email to {user_email}: {e}")
        return False 