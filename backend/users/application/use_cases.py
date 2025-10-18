"""
Application Layer - Use Cases
Following Clean Architecture principles
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import uuid

from ..domain.entities import User, UserRole, OTPType
from ..domain.services import (
    AuthenticationService, UserRegistrationService, OTPService, 
    PasswordService, EmailVerificationService, PhoneVerificationService
)
from ..domain.repositories import UserRepository, OTPRepository, UserProfileRepository, UserSessionRepository


class RegisterUserUseCase:
    """Use case for user registration"""
    
    def __init__(self, 
                 registration_service: UserRegistrationService,
                 user_repository: UserRepository,
                 profile_repository: UserProfileRepository,
                 otp_service: OTPService,
                 email_service: EmailVerificationService):
        self.registration_service = registration_service
        self.user_repository = user_repository
        self.profile_repository = profile_repository
        self.otp_service = otp_service
        self.email_service = email_service
    
    def execute(self, 
                username: str, 
                email: str, 
                password: str, 
                password_confirm: str,
                first_name: str, 
                last_name: str,
                phone_number: Optional[str] = None,
                role: str = "customer") -> Dict[str, Any]:
        """Execute user registration"""
        
        # Validate input
        is_valid, errors = self.registration_service.validate_registration_data(
            username, email, password, password_confirm
        )
        if not is_valid:
            return {
                "success": False,
                "errors": errors,
                "message": "Invalid registration data"
            }
        
        try:
            # Register user
            user_role = UserRole(role)
            user = self.registration_service.register_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role=user_role
            )
            
            # Set user as inactive until email verification
            user.is_active = False
            self.user_repository.update(user)
            
            # Create user profile
            profile = self._create_user_profile(user.id)
            
            # Send verification email with user name
            if email:
                user_name = f"{first_name} {last_name}".strip()
                self.email_service.send_verification_email(user.id, email, user_name)
            
            return {
                "success": True,
                "user": self._user_to_dict(user),
                "profile": self._profile_to_dict(profile),
                "email_verification_required": True,
                "email": email,
                "message": "User registered successfully. Please check your email for verification."
            }
            
        except ValueError as e:
            return {
                "success": False,
                "errors": [str(e)],
                "message": "Registration failed"
            }
    
    def _create_user_profile(self, user_id: uuid.UUID):
        """Create default user profile if it doesn't exist"""
        from ..domain.entities import UserProfile
        
        # Check if profile already exists
        existing_profile = self.profile_repository.get_by_user_id(user_id)
        if existing_profile:
            return existing_profile
        
        # Create new profile
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=user_id
        )
        
        return self.profile_repository.create(profile)
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user entity to dictionary"""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_phone_verified": user.is_phone_verified,
            "is_email_verified": user.is_email_verified,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "preferred_currency": user.preferred_currency,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _profile_to_dict(self, profile) -> Dict[str, Any]:
        """Convert profile entity to dictionary"""
        return {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "avatar": profile.avatar.url if profile.avatar else None,
            "bio": profile.bio,
            "address": profile.address,
            "city": profile.city,
            "country": profile.country,
            "postal_code": profile.postal_code,
            "website": profile.website,
            "facebook": profile.facebook,
            "instagram": profile.instagram,
            "twitter": profile.twitter,
            "newsletter_subscription": profile.newsletter_subscription,
            "marketing_emails": profile.marketing_emails
        }

    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate JWT tokens"""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(user)
        
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }


class LoginUserUseCase:
    """Use case for user login"""
    
    def __init__(self, 
                 auth_service: AuthenticationService,
                 session_repository: UserSessionRepository):
        self.auth_service = auth_service
        self.session_repository = session_repository
    
    def execute(self, username: str, password: str, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Execute user login"""
        
        # Authenticate user
        user = self.auth_service.authenticate_user(username, password)
        
        if not user:
            return {
                "success": False,
                "message": "نام کاربری یا رمز عبور اشتباه است"
            }
        
        if not user.is_active:
            if not user.is_email_verified:
                return {
                    "success": False,
                    "message": "لطفاً ایمیل خود را تایید کنید",
                    "requires_email_verification": True,
                    "email": user.email
                }
            return {
                "success": False,
                "message": "حساب کاربری شما غیرفعال است"
            }
        
        # Create session
        session = self._create_user_session(user.id, ip_address, user_agent)
        
        # Generate tokens (JWT)
        tokens = self._generate_tokens(user)
        
        return {
            "success": True,
            "user": self._user_to_dict(user),
            "tokens": tokens,
            "message": "ورود موفقیت‌آمیز"
        }
    
    def _create_user_session(self, user_id: uuid.UUID, ip_address: str, user_agent: str):
        """Create user session"""
        from ..domain.entities import UserSession
        
        session = UserSession(
            id=uuid.uuid4(),
            user_id=user_id,
            session_key=f"session_{uuid.uuid4().hex}",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return self.session_repository.create(session)
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate JWT tokens"""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(user)
        
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user entity to dictionary"""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_phone_verified": user.is_phone_verified,
            "is_email_verified": user.is_email_verified,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "preferred_currency": user.preferred_currency,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }


class LogoutUserUseCase:
    """Use case for user logout"""
    
    def __init__(self, session_repository: UserSessionRepository):
        self.session_repository = session_repository
    
    def execute(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Execute user logout"""
        
        # Deactivate all user sessions
        deactivated_count = self.session_repository.deactivate_user_sessions(user_id)
        
        return {
            "success": True,
            "deactivated_sessions": deactivated_count,
            "message": "Logout successful"
        }


class VerifyEmailUseCase:
    """Use case for email verification"""
    
    def __init__(self, 
                 otp_service: OTPService,
                 user_repository: UserRepository,
                 email_service: EmailVerificationService):
        self.otp_service = otp_service
        self.user_repository = user_repository
        self.email_service = email_service
    
    def execute(self, email: str, otp_code: str) -> Dict[str, Any]:
        """Execute email verification"""
        
        try:
            # Verify OTP
            otp = self.otp_service.verify_otp(
                target=email,
                code=otp_code,
                otp_type=OTPType.EMAIL_VERIFICATION
            )
            
            if not otp:
                return {
                    "success": False,
                    "message": "Invalid or expired verification code"
                }
            
            # Get user by email
            user = self.user_repository.get_by_email(email)
            
            if not user:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            # Mark email as verified and activate user
            user.is_email_verified = True
            user.is_active = True
            self.user_repository.update(user)
            
            # Generate tokens for auto-login
            tokens = self._generate_tokens(user)
            
            return {
                "success": True,
                "user": self._user_to_dict(user),
                "tokens": tokens,
                "message": "Email verified successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def resend_verification(self, email: str) -> Dict[str, Any]:
        """Resend verification email"""
        
        try:
            # Get user by email
            user = self.user_repository.get_by_email(email)
            
            if not user:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            if user.is_email_verified:
                return {
                    "success": False,
                    "message": "Email already verified"
                }
            
            # Send verification email
            user_name = f"{user.first_name} {user.last_name}".strip()
            self.email_service.send_verification_email(user.id, email, user_name)
            
            return {
                "success": True,
                "message": "Verification email sent successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user entity to dictionary"""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_phone_verified": user.is_phone_verified,
            "is_email_verified": user.is_email_verified,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "preferred_currency": user.preferred_currency,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate JWT tokens"""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(user)
        
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }


class VerifyPhoneUseCase:
    """Use case for phone verification"""
    
    def __init__(self, 
                 otp_service: OTPService,
                 user_repository: UserRepository,
                 phone_service: PhoneVerificationService):
        self.otp_service = otp_service
        self.user_repository = user_repository
        self.phone_service = phone_service
    
    def execute(self, phone: str, otp_code: str) -> Dict[str, Any]:
        """Execute phone verification"""
        
        # Verify OTP
        otp = self.otp_service.verify_otp(phone, otp_code, OTPType.PHONE_VERIFICATION)
        
        if not otp:
            return {
                "success": False,
                "message": "Invalid or expired OTP code"
            }
        
        # Update user phone verification status
        user = self.user_repository.get_by_id(otp.user_id)
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        user.is_phone_verified = True
        updated_user = self.user_repository.update(user)
        
        return {
            "success": True,
            "user": self._user_to_dict(updated_user),
            "message": "Phone verified successfully"
        }
    
    def resend_verification(self, phone: str) -> Dict[str, Any]:
        """Resend verification SMS"""
        
        # Find user by phone
        from ..domain.value_objects import PhoneNumber as PhoneNumberVO
        phone_vo = PhoneNumberVO(phone)
        user = self.user_repository.get_by_phone(phone_vo)
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Send verification SMS
        success = self.phone_service.send_verification_sms(user.id, phone)
        
        return {
            "success": success,
            "message": "Verification SMS sent" if success else "Failed to send verification SMS"
        }
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user entity to dictionary"""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_phone_verified": user.is_phone_verified,
            "is_email_verified": user.is_email_verified,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "preferred_currency": user.preferred_currency
        }


class ForgotPasswordUseCase:
    """Use case for requesting password reset (forgot password)"""
    
    def __init__(self, 
                 otp_service: OTPService,
                 user_repository: UserRepository,
                 email_service: EmailVerificationService):
        self.otp_service = otp_service
        self.user_repository = user_repository
        self.email_service = email_service
    
    def execute(self, email: str) -> Dict[str, Any]:
        """Execute forgot password request"""
        
        # Find user by email
        try:
            from ..domain.value_objects import Email as EmailVO
            email_vo = EmailVO(email)
            user = self.user_repository.get_by_email(email_vo)
        except ValueError:
            return {
                "success": False,
                "message": "Invalid email format"
            }
        
        if not user:
            return {
                "success": False,
                "message": "User not found with this email address"
            }
        
        # Send password reset email with user name
        user_name = f"{user.first_name} {user.last_name}".strip()
        success = self.email_service.send_password_reset_email(user.id, email, user_name)
        
        return {
            "success": success,
            "message": "Password reset email sent successfully" if success else "Failed to send password reset email",
            "email": email
        }


class ResetPasswordUseCase:
    """Use case for password reset"""
    
    def __init__(self, 
                 otp_service: OTPService,
                 user_repository: UserRepository,
                 password_service: PasswordService,
                 email_service: EmailVerificationService):
        self.otp_service = otp_service
        self.user_repository = user_repository
        self.password_service = password_service
        self.email_service = email_service
    
    def execute(self, email: str, new_password: str, otp_code: str) -> Dict[str, Any]:
        """Execute password reset"""
        
        # Verify OTP
        otp = self.otp_service.verify_otp(email, otp_code, OTPType.PASSWORD_RESET)
        
        if not otp:
            return {
                "success": False,
                "message": "Invalid or expired OTP code"
            }
        
        # Find user
        try:
            from ..domain.value_objects import Email as EmailVO
            email_vo = EmailVO(email)
            user = self.user_repository.get_by_email(email_vo)
        except ValueError:
            return {
                "success": False,
                "message": "Invalid email format"
            }
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Reset password
        success = self.password_service.reset_password(email, new_password, otp_code)
        
        if success:
            return {
                "success": True,
                "message": "Password reset successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to reset password"
            }
    
    def request_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset"""
        
        # Find user by email
        from ..domain.value_objects import Email as EmailVO
        email_vo = EmailVO(email)
        user = self.user_repository.get_by_email(email_vo)
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Send password reset email with user name
        user_name = f"{user.first_name} {user.last_name}".strip()
        success = self.email_service.send_password_reset_email(user.id, email, user_name)
        
        return {
            "success": success,
            "message": "Password reset email sent" if success else "Failed to send password reset email"
        }


class ChangePasswordUseCase:
    """Use case for password change"""
    
    def __init__(self, 
                 user_repository: UserRepository,
                 password_service: PasswordService):
        self.user_repository = user_repository
        self.password_service = password_service
    
    def execute(self, user_id: uuid.UUID, current_password: str, new_password: str) -> Dict[str, Any]:
        """Execute password change"""
        
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Change password
        success = self.password_service.change_password(user_id, current_password, new_password)
        
        if success:
            return {
                "success": True,
                "message": "Password changed successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to change password"
            }


class GetUserProfileUseCase:
    """Use case for getting user profile"""
    
    def __init__(self, user_repository: UserRepository, profile_repository: UserProfileRepository):
        self.user_repository = user_repository
        self.profile_repository = profile_repository
    
    def execute(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Execute get user profile"""
        
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Get profile
        profile = self.profile_repository.get_by_user_id(user_id)
        
        return {
            "success": True,
            "user": self._user_to_dict(user),
            "profile": self._profile_to_dict(profile) if profile else None
        }
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user entity to dictionary"""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_phone_verified": user.is_phone_verified,
            "is_email_verified": user.is_email_verified,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "preferred_currency": user.preferred_currency,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "nationality": user.nationality,
            "agent_code": user.agent_code,
            "commission_rate": float(user.commission_rate),
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _profile_to_dict(self, profile) -> Dict[str, Any]:
        """Convert profile entity to dictionary"""
        return {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "avatar": profile.avatar.url if profile.avatar else None,
            "bio": profile.bio,
            "address": profile.address,
            "city": profile.city,
            "country": profile.country,
            "postal_code": profile.postal_code,
            "website": profile.website,
            "facebook": profile.facebook,
            "instagram": profile.instagram,
            "twitter": profile.twitter,
            "newsletter_subscription": profile.newsletter_subscription,
            "marketing_emails": profile.marketing_emails,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        } 


class UpdateUserProfileUseCase:
    """Use case for updating user profile"""
    
    def __init__(self, user_repository: UserRepository, profile_repository: UserProfileRepository):
        self.user_repository = user_repository
        self.profile_repository = profile_repository
    
    def execute(self, user_id: uuid.UUID, user_data: Dict[str, Any], profile_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute update user profile - Only for non-sensitive fields"""
        
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Define sensitive fields that require OTP verification
        sensitive_fields = ['email', 'phone_number', 'first_name', 'last_name']
        
        # Check if user is trying to update sensitive fields
        sensitive_updates = [field for field in sensitive_fields if field in user_data]
        if sensitive_updates:
            return {
                "success": False,
                "message": f"Sensitive fields {sensitive_updates} require OTP verification. Use sensitive field update endpoints.",
                "requires_otp": True,
                "sensitive_fields": sensitive_updates
            }
        
        try:
            # Update user fields (only non-sensitive)
            if user_data:
                for field, value in user_data.items():
                    if hasattr(user, field) and value is not None and field not in sensitive_fields:
                        # Handle date fields
                        if field == 'date_of_birth' and value:
                            from datetime import date
                            try:
                                # Convert string to date object
                                if isinstance(value, str):
                                    value = date.fromisoformat(value)
                                setattr(user, field, value)
                            except ValueError:
                                return {
                                    "success": False,
                                    "message": f"Invalid date format for {field}. Use YYYY-MM-DD format."
                                }
                        else:
                            setattr(user, field, value)
                user.updated_at = datetime.now()
                user = self.user_repository.update(user)
            
            # Update profile fields
            profile = None
            if profile_data:
                profile = self.profile_repository.get_by_user_id(user_id)
                if profile:
                    for field, value in profile_data.items():
                        if hasattr(profile, field) and value is not None:
                            setattr(profile, field, value)
                    profile.updated_at = datetime.now()
                    profile = self.profile_repository.update(profile)
                else:
                    # Create profile if it doesn't exist
                    from ..domain.entities import UserProfile
                    profile = UserProfile(
                        id=uuid.uuid4(),
                        user_id=user_id,
                        **profile_data
                    )
                    profile = self.profile_repository.create(profile)
            else:
                # Get existing profile for response
                profile = self.profile_repository.get_by_user_id(user_id)
            
            return {
                "success": True,
                "user": self._user_to_dict(user),
                "profile": self._profile_to_dict(profile) if profile else None,
                "message": "Profile updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update profile: {str(e)}"
            }
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user entity to dictionary"""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_phone_verified": user.is_phone_verified,
            "is_email_verified": user.is_email_verified,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "preferred_currency": user.preferred_currency,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "nationality": user.nationality,
            "agent_code": user.agent_code,
            "commission_rate": float(user.commission_rate),
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _profile_to_dict(self, profile) -> Dict[str, Any]:
        """Convert profile entity to dictionary"""
        return {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "avatar": profile.avatar.url if profile.avatar else None,
            "bio": profile.bio,
            "address": profile.address,
            "city": profile.city,
            "country": profile.country,
            "postal_code": profile.postal_code,
            "website": profile.website,
            "facebook": profile.facebook,
            "instagram": profile.instagram,
            "twitter": profile.twitter,
            "newsletter_subscription": profile.newsletter_subscription,
            "marketing_emails": profile.marketing_emails,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        }


class RequestSensitiveFieldUpdateUseCase:
    """Use case for requesting sensitive field updates with OTP"""
    
    def __init__(self, 
                 user_repository: UserRepository,
                 otp_service: OTPService,
                 email_service: EmailVerificationService,
                 phone_service: PhoneVerificationService):
        self.user_repository = user_repository
        self.otp_service = otp_service
        self.email_service = email_service
        self.phone_service = phone_service
    
    def execute(self, user_id: uuid.UUID, field: str, new_value: str) -> Dict[str, Any]:
        """Execute request for sensitive field update"""
        
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Validate field
        allowed_fields = ['email', 'phone_number', 'first_name', 'last_name']
        if field not in allowed_fields:
            return {
                "success": False,
                "message": f"Field '{field}' is not allowed for sensitive updates"
            }
        
        # Check if value is actually changing
        current_value = getattr(user, field, None)
        if current_value == new_value:
            return {
                "success": False,
                "message": f"New value is the same as current value for {field}"
            }
        
        try:
            # Generate OTP based on field type
            if field == 'email':
                # Validate email format
                if not self._is_valid_email(new_value):
                    return {
                        "success": False,
                        "message": "Invalid email format"
                    }
                
                # Check if email is already taken
                existing_user = self.user_repository.get_by_email(new_value)
                if existing_user and existing_user.id != user_id:
                    return {
                        "success": False,
                        "message": "Email is already taken by another user"
                    }
                
                # Send OTP to new email
                otp = self.otp_service.generate_otp(
                    user_id=user_id,
                    target=new_value,
                    otp_type=OTPType.EMAIL_VERIFICATION
                )
                otp_result = {'success': True, 'otp': otp}
                
                if otp_result['success']:
                    # Send verification email
                    self.email_service.send_verification_email(
                        user_id, new_value, user.full_name
                    )
                    
                    return {
                        "success": True,
                        "message": f"OTP sent to {new_value}",
                        "field": field,
                        "new_value": new_value,
                        "otp_id": str(otp_result['otp'].id)
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to create OTP"
                    }
            
            elif field == 'phone_number':
                # Validate phone format
                if not self._is_valid_phone(new_value):
                    return {
                        "success": False,
                        "message": "Invalid phone number format"
                    }
                
                # Check if phone is already taken
                existing_user = self.user_repository.get_by_phone(new_value)
                if existing_user and existing_user.id != user_id:
                    return {
                        "success": False,
                        "message": "Phone number is already taken by another user"
                    }
                
                # Send OTP to new phone
                otp = self.otp_service.generate_otp(
                    user_id=user_id,
                    target=new_value,
                    otp_type=OTPType.PHONE_VERIFICATION
                )
                otp_result = {'success': True, 'otp': otp}
                
                if otp_result['success']:
                    # Send verification SMS
                    self.phone_service.send_verification_sms(
                        user_id, new_value
                    )
                    
                    return {
                        "success": True,
                        "message": f"OTP sent to {new_value}",
                        "field": field,
                        "new_value": new_value,
                        "otp_id": str(otp_result['otp'].id)
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to create OTP"
                    }
            
            else:  # first_name or last_name
                # For name fields, we'll use email OTP for verification
                otp = self.otp_service.generate_otp(
                    user_id=user_id,
                    target=user.email,
                    otp_type=OTPType.EMAIL_VERIFICATION
                )
                otp_result = {'success': True, 'otp': otp}
                
                if otp_result['success']:
                    # Send verification email to current email
                    self.email_service.send_verification_email(
                        user_id, user.email, user.full_name
                    )
                    
                    return {
                        "success": True,
                        "message": f"OTP sent to {user.email}",
                        "field": field,
                        "new_value": new_value,
                        "otp_id": str(otp_result['otp'].id)
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to create OTP"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to request update: {str(e)}"
            }
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None


class VerifySensitiveFieldUpdateUseCase:
    """Use case for verifying sensitive field updates with OTP"""
    
    def __init__(self, user_repository: UserRepository, otp_service: OTPService):
        self.user_repository = user_repository
        self.otp_service = otp_service
    
    def execute(self, user_id: uuid.UUID, field: str, new_value: str, otp_code: str) -> Dict[str, Any]:
        """Execute verification of sensitive field update"""
        
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Validate field
        allowed_fields = ['email', 'phone_number', 'first_name', 'last_name']
        if field not in allowed_fields:
            return {
                "success": False,
                "message": f"Field '{field}' is not allowed for sensitive updates"
            }
        
        try:
            # Verify OTP
            if field == 'email':
                otp_result = self.otp_service.verify_otp(
                    user_id=user_id,
                    email=new_value,
                    otp_code=otp_code,
                    otp_type=OTPType.EMAIL_VERIFICATION
                )
            elif field == 'phone_number':
                otp_result = self.otp_service.verify_otp(
                    user_id=user_id,
                    phone=new_value,
                    otp_code=otp_code,
                    otp_type=OTPType.PHONE_VERIFICATION
                )
            else:  # first_name or last_name
                otp_result = self.otp_service.verify_otp(
                    user_id=user_id,
                    email=user.email,
                    otp_code=otp_code,
                    otp_type=OTPType.EMAIL_VERIFICATION
                )
            
            if not otp_result['success']:
                return {
                    "success": False,
                    "message": "Invalid OTP code"
                }
            
            # Update the field
            setattr(user, field, new_value)
            
            # Update verification status for email/phone
            if field == 'email':
                user.is_email_verified = True
            elif field == 'phone_number':
                user.is_phone_verified = True
            
            user.updated_at = datetime.now()
            user = self.user_repository.update(user)
            
            return {
                "success": True,
                "user": self._user_to_dict(user),
                "message": f"{field} updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to verify update: {str(e)}"
            }
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user entity to dictionary"""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_phone_verified": user.is_phone_verified,
            "is_email_verified": user.is_email_verified,
            "phone_number": user.phone_number,
            "preferred_language": user.preferred_language,
            "preferred_currency": user.preferred_currency,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "nationality": user.nationality,
            "agent_code": user.agent_code,
            "commission_rate": float(user.commission_rate),
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        } 