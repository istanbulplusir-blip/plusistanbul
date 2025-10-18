"""
Domain Entities for Authentication System
Following Domain-Driven Design principles
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class UserRole(Enum):
    """User role enumeration"""
    GUEST = "guest"
    CUSTOMER = "customer"
    AGENT = "agent"
    ADMIN = "admin"


class OTPType(Enum):
    """OTP type enumeration"""
    PHONE_VERIFICATION = "phone_verification"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    LOGIN = "login"


class VerificationStatus(Enum):
    """Verification status enumeration"""
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class User:
    """User domain entity"""
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    password: Optional[str] = None
    password_hash: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    is_phone_verified: bool = False
    is_email_verified: bool = False
    phone_number: Optional[str] = None
    preferred_language: str = "fa"
    preferred_currency: str = "USD"
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    agent_code: Optional[str] = None
    commission_rate: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_agent(self) -> bool:
        """Check if user is an agent"""
        return self.role == UserRole.AGENT

    @property
    def is_customer(self) -> bool:
        """Check if user is a customer"""
        return self.role == UserRole.CUSTOMER

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == UserRole.ADMIN

    @property
    def is_guest(self) -> bool:
        """Check if user is a guest"""
        return self.role == UserRole.GUEST

    def can_access_admin_panel(self) -> bool:
        """Check if user can access admin panel"""
        return self.is_admin or self.is_agent

    def can_book_products(self) -> bool:
        """Check if user can book products"""
        return self.is_customer or self.is_agent

    def generate_agent_code(self) -> str:
        """Generate agent code for agent users"""
        if self.is_agent and not self.agent_code:
            self.agent_code = f"AG{str(self.id)[:8].upper()}"
        return self.agent_code


@dataclass
class OTPCode:
    """OTP Code domain entity"""
    id: uuid.UUID
    user_id: uuid.UUID
    code: str
    otp_type: OTPType
    is_used: bool
    expires_at: datetime
    created_at: datetime = None
    used_at: Optional[datetime] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def is_valid(self) -> bool:
        """Check if OTP is valid"""
        from django.utils import timezone
        now = timezone.now()
        return (
            not self.is_used and 
            now < self.expires_at
        )

    @property
    def is_expired(self) -> bool:
        """Check if OTP is expired"""
        from django.utils import timezone
        now = timezone.now()
        return now >= self.expires_at

    def mark_as_used(self):
        """Mark OTP as used"""
        from django.utils import timezone
        self.is_used = True
        self.used_at = timezone.now()

    def mark_as_expired(self):
        """Mark OTP as expired - this is now handled by is_expired property"""
        pass


@dataclass
class UserProfile:
    """User Profile domain entity"""
    id: uuid.UUID
    user_id: uuid.UUID
    avatar: Optional[str] = None
    bio: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    newsletter_subscription: bool = True
    marketing_emails: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class UserSession:
    """User Session domain entity"""
    id: uuid.UUID
    user_id: uuid.UUID
    session_key: str
    ip_address: str
    user_agent: str
    country: Optional[str] = None
    city: Optional[str] = None
    last_activity: datetime = None
    is_active: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()

    def update_activity(self):
        """Update last activity timestamp"""
        from django.utils import timezone
        self.last_activity = timezone.now()

    def deactivate(self):
        """Deactivate session"""
        self.is_active = False 