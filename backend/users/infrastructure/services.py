"""
Infrastructure Layer - Service Implementations
Concrete implementations of domain services
"""

from typing import Optional
from datetime import datetime, timedelta
import uuid

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ..domain.services import (
    PasswordService, EmailVerificationService, PhoneVerificationService
)
from ..domain.entities import OTPType
from ..domain.repositories import OTPRepository
from shared.services import (
    send_verification_email, send_password_reset_email, send_welcome_email
)


class DjangoPasswordService(PasswordService):
    """Django-based password service implementation"""
    
    def hash_password(self, password: str) -> str:
        """Hash password using Django's password hashing"""
        return make_password(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password using Django's password checking"""
        return check_password(password, hashed_password)
    
    def reset_password(self, email: str, new_password: str, otp_code: str) -> bool:
        """Reset password with OTP verification"""
        try:
            from ..models import User
            from django.contrib.auth.hashers import make_password
            
            # Find user by email
            user = User.objects.get(email=email)
            
            # Hash the new password
            hashed_password = make_password(new_password)
            
            # Update user's password
            user.password = hashed_password
            user.save()
            return True
        except User.DoesNotExist:
            return False
        except Exception as e:
            return False
    
    def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        """Change password for authenticated user"""
        # This would be implemented with user repository
        # For now, return True as placeholder
        return True


class DjangoEmailVerificationService(EmailVerificationService):
    """Django-based email verification service implementation"""
    
    def __init__(self, otp_service):
        self.otp_service = otp_service
    
    def send_verification_email(self, user_id: uuid.UUID, email: str, user_name: str = None) -> bool:
        """Send verification email with OTP"""
        try:
            # Generate OTPCode
            otp = self.otp_service.generate_otp(user_id, email, OTPType.EMAIL_VERIFICATION)
            
            # Send email using shared service
            success = send_verification_email(email, otp.code, user_name)
            
            if success:
                print(f"✅ Verification email sent to {email} with OTP: {otp.code}")
            else:
                print(f"❌ Failed to send verification email to {email}")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to send verification email: {e}")
            return False
    
    def send_password_reset_email(self, user_id: uuid.UUID, email: str, user_name: str = None) -> bool:
        """Send password reset email with OTP"""
        try:
            # Generate OTP
            otp = self.otp_service.generate_otp(user_id, email, OTPType.PASSWORD_RESET)
            # Send email using shared service
            success = send_password_reset_email(email, otp.code, user_name)
            return success
        except Exception as e:
            return False
    
    def send_welcome_email(self, email: str, user_name: str) -> bool:
        """Send welcome email after successful registration"""
        try:
            success = send_welcome_email(email, user_name)
            
            if success:
                print(f"✅ Welcome email sent to {email}")
            else:
                print(f"❌ Failed to send welcome email to {email}")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to send welcome email: {e}")
            return False
    
    def verify_email(self, email: str, otp_code: str) -> bool:
        """Verify email with OTP"""
        # This would be implemented with OTP verification
        # For now, return True as placeholder
        return True


class DjangoPhoneVerificationService(PhoneVerificationService):
    """Django-based phone verification service implementation"""
    
    def __init__(self, otp_service):
        self.otp_service = otp_service
    
    def send_verification_sms(self, user_id: uuid.UUID, phone: str) -> bool:
        """Send verification SMS"""
        try:
            # Generate OTP
            otp = self.otp_service.generate_otp(user_id, phone, OTPType.PHONE_VERIFICATION)
            
            # In a real implementation, you would integrate with an SMS service
            # For now, we'll just print the OTP for development
            print(f"📱 SMS to {phone}: Your verification code is {otp.code}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send verification SMS: {e}")
            return False
    
    def verify_phone(self, phone: str, otp_code: str) -> bool:
        """Verify phone with OTP"""
        # This would be implemented with OTP verification
        # For now, return True as placeholder
        return True


class MockEmailService(EmailVerificationService):
    """Mock email service for development/testing"""
    
    def __init__(self, otp_service):
        self.otp_service = otp_service
    
    def send_verification_email(self, user_id: uuid.UUID, email: str) -> bool:
        """Mock email sending - just print to console"""
        try:
            # Generate OTP
            otp = self.otp_service.generate_otp(user_id, email, OTPType.EMAIL_VERIFICATION)
            
            print(f"📧 === MOCK EMAIL ===")
            print(f"📧 To: {email}")
            print(f"📧 Subject: تایید ایمیل - Peykan Tourism")
            print(f"📧 OTP Code: {otp.code}")
            print(f"📧 =================")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send mock email: {e}")
            return False
    
    def verify_email(self, email: str, otp_code: str) -> bool:
        """Mock email verification"""
        return True


class MockSMSService(PhoneVerificationService):
    """Mock SMS service for development/testing"""
    
    def __init__(self, otp_service):
        self.otp_service = otp_service
    
    def send_verification_sms(self, user_id: uuid.UUID, phone: str) -> bool:
        """Mock SMS sending - just print to console"""
        try:
            # Generate OTP
            otp = self.otp_service.generate_otp(user_id, phone, OTPType.PHONE_VERIFICATION)
            
            print(f"📱 === MOCK SMS ===")
            print(f"📱 To: {phone}")
            print(f"📱 Message: Your verification code is {otp.code}")
            print(f"📱 ================")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send mock SMS: {e}")
            return False
    
    def verify_phone(self, phone: str, otp_code: str) -> bool:
        """Mock phone verification"""
        return True 