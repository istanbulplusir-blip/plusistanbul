"""
Domain Services for Authentication
Following Domain-Driven Design principles
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
from datetime import datetime, timedelta
import uuid
import random
import string

from .entities import User, OTPCode, UserRole, OTPType
from .value_objects import Email, PhoneNumber, Username, Password, OTPCode as OTPCodeVO
from .repositories import UserRepository, OTPRepository


class AuthenticationService(ABC):
    """Authentication domain service interface"""
    
    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        pass
    
    @abstractmethod
    def authenticate_with_otp(self, target: str, otp_code: str, otp_type: OTPType) -> Optional[User]:
        """Authenticate user with OTP"""
        pass


class UserRegistrationService(ABC):
    """User registration domain service interface"""
    
    @abstractmethod
    def register_user(self, 
                     username: str, 
                     email: str, 
                     password: str, 
                     first_name: str, 
                     last_name: str,
                     phone_number: Optional[str] = None,
                     role: UserRole = UserRole.CUSTOMER) -> User:
        """Register a new user"""
        pass
    
    @abstractmethod
    def validate_registration_data(self, 
                                 username: str, 
                                 email: str, 
                                 password: str,
                                 password_confirm: str) -> Tuple[bool, list]:
        """Validate registration data"""
        pass


class OTPService(ABC):
    """OTP domain service interface"""
    
    @abstractmethod
    def generate_otp(self, user_id: uuid.UUID, target: str, otp_type: OTPType) -> OTPCode:
        """Generate OTP for user"""
        pass
    
    @abstractmethod
    def verify_otp(self, target: str, code: str, otp_type: OTPType) -> Optional[OTPCode]:
        """Verify OTP code"""
        pass
    
    @abstractmethod
    def resend_otp(self, user_id: uuid.UUID, target: str, otp_type: OTPType) -> OTPCode:
        """Resend OTP"""
        pass


class PasswordService(ABC):
    """Password domain service interface"""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash password"""
        pass
    
    @abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password"""
        pass
    
    @abstractmethod
    def reset_password(self, email: str, new_password: str, otp_code: str) -> bool:
        """Reset password with OTP"""
        pass
    
    @abstractmethod
    def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        """Change password"""
        pass


class EmailVerificationService(ABC):
    """Email verification domain service interface"""
    
    @abstractmethod
    def send_verification_email(self, user_id: uuid.UUID, email: str) -> bool:
        """Send verification email"""
        pass
    
    @abstractmethod
    def verify_email(self, email: str, otp_code: str) -> bool:
        """Verify email with OTP"""
        pass


class PhoneVerificationService(ABC):
    """Phone verification domain service interface"""
    
    @abstractmethod
    def send_verification_sms(self, user_id: uuid.UUID, phone: str) -> bool:
        """Send verification SMS"""
        pass
    
    @abstractmethod
    def verify_phone(self, phone: str, otp_code: str) -> bool:
        """Verify phone with OTP"""
        pass


# Concrete implementations
class DjangoAuthenticationService(AuthenticationService):
    """Django-based authentication service implementation"""
    
    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        self.user_repository = user_repository
        self.password_service = password_service
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            # Try to get user by username first
            user = self.user_repository.get_by_username(username)
            
            # If not found, try email
            if not user:
                user = self.user_repository.get_by_email(username)
            
            if not user:
                return None
            
            # Check password regardless of user status
            # Use password_hash field from domain entity
            if not user.password_hash or not self.password_service.verify_password(password, user.password_hash):
                return None
            
            # Return user even if inactive - let use case handle activation status
            return user
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None
    
    def authenticate_with_otp(self, target: str, otp_code: str, otp_type: OTPType) -> Optional[User]:
        """Authenticate user with OTP"""
        # This would be implemented with OTP repository
        pass


class DjangoUserRegistrationService(UserRegistrationService):
    """Django-based user registration service implementation"""
    
    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        self.user_repository = user_repository
        self.password_service = password_service
    
    def register_user(self, 
                     username: str, 
                     email: str, 
                     password: str, 
                     first_name: str, 
                     last_name: str,
                     phone_number: Optional[str] = None,
                     role: UserRole = UserRole.CUSTOMER) -> User:
        """Register a new user"""
        # Validate input
        is_valid, errors = self.validate_registration_data(username, email, password, password)
        if not is_valid:
            raise ValueError(f"Invalid registration data: {errors}")
        
        # Check if user already exists
        if self.user_repository.exists_by_username(username):
            raise ValueError("Username already exists")
        
        if self.user_repository.exists_by_email(email):
            raise ValueError("Email already exists")
        
        if phone_number and self.user_repository.exists_by_phone(phone_number):
            raise ValueError("Phone number already exists")
        
        # Create user
        user_id = uuid.uuid4()
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role,
            is_active=True,
            is_phone_verified=False,
            is_email_verified=False
        )
        
        # Save user
        return self.user_repository.create(user)
    
    def validate_registration_data(self, 
                                 username: str, 
                                 email: str, 
                                 password: str,
                                 password_confirm: str) -> Tuple[bool, list]:
        """Validate registration data"""
        errors = []
        
        # Validate username
        try:
            Username(username)
        except ValueError:
            errors.append("Invalid username format")
        
        # Validate email
        try:
            Email(email)
        except ValueError:
            errors.append("Invalid email format")
        
        # Validate password
        try:
            Password(password)
        except ValueError:
            errors.append("Password must be at least 8 characters long")
        
        # Validate password confirmation
        if password != password_confirm:
            errors.append("Passwords do not match")
        
        return len(errors) == 0, errors


class DjangoOTPService(OTPService):
    """Django-based OTP service implementation"""
    
    def __init__(self, otp_repository: OTPRepository):
        self.otp_repository = otp_repository
    
    def generate_otp(self, user_id: uuid.UUID, target: str, otp_type: OTPType) -> OTPCode:
        """Generate OTP for user"""
        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Set expiry (10 minutes) - use timezone.now() for consistency
        from django.utils import timezone
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Prepare OTP data
        otp_data = {
            "id": uuid.uuid4(),
            "user_id": user_id,
            "code": code,
            "otp_type": otp_type,
            "is_used": False,
            "expires_at": expires_at
        }
        
        # Set email or phone based on OTP type
        if otp_type in [OTPType.EMAIL_VERIFICATION, OTPType.PASSWORD_RESET]:
            otp_data["email"] = target
        elif otp_type == OTPType.PHONE_VERIFICATION:
            otp_data["phone"] = target

        otp = OTPCode(**otp_data)
        
        return self.otp_repository.create(otp)
    
    def verify_otp(self, target: str, code: str, otp_type: OTPType) -> Optional[OTPCode]:
        """Verify OTP code"""
        try:
            otp_code_vo = OTPCodeVO(code)
            otp = self.otp_repository.get_valid_otp(target, otp_type.value, str(otp_code_vo))
            if otp and otp.is_valid:
                # Mark as used
                otp.mark_as_used()
                self.otp_repository.update(otp)
                return otp
            return None
        except ValueError:
            return None
    
    def resend_otp(self, user_id: uuid.UUID, target: str, otp_type: OTPType) -> OTPCode:
        """Resend OTP"""
        # Delete existing OTPs for this user and type
        existing_otps = self.otp_repository.get_user_otps(user_id, otp_type.value)
        for otp in existing_otps:
            self.otp_repository.delete(otp.id)
        
        # Generate new OTP
        return self.generate_otp(user_id, target, otp_type) 