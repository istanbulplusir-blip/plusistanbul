"""
Repository Interfaces for Authentication Domain
Following Repository Pattern and SOLID principles
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
import uuid

from .entities import User, OTPCode, UserProfile, UserSession
from .value_objects import Email, PhoneNumber, Username


class UserRepository(ABC):
    """User repository interface"""
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number"""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Update user"""
        pass
    
    @abstractmethod
    def delete(self, user_id: uuid.UUID) -> bool:
        """Delete user"""
        pass
    
    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        pass
    
    @abstractmethod
    def exists_by_phone(self, phone: str) -> bool:
        """Check if phone exists"""
        pass


class OTPRepository(ABC):
    """OTP repository interface"""
    
    @abstractmethod
    def create(self, otp: OTPCode) -> OTPCode:
        """Create a new OTP"""
        pass
    
    @abstractmethod
    def get_by_id(self, otp_id: uuid.UUID) -> Optional[OTPCode]:
        """Get OTP by ID"""
        pass
    
    @abstractmethod
    def get_valid_otp(self, target: str, otp_type: str, code: str) -> Optional[OTPCode]:
        """Get valid OTP by target, type and code"""
        pass
    
    @abstractmethod
    def get_user_otps(self, user_id: uuid.UUID, otp_type: str = None) -> List[OTPCode]:
        """Get all OTPs for a user"""
        pass
    
    @abstractmethod
    def update(self, otp: OTPCode) -> OTPCode:
        """Update OTP"""
        pass
    
    @abstractmethod
    def delete(self, otp_id: uuid.UUID) -> bool:
        """Delete OTP"""
        pass
    
    @abstractmethod
    def delete_expired_otps(self) -> int:
        """Delete expired OTPs and return count"""
        pass
    
    @abstractmethod
    def mark_as_used(self, otp_id: uuid.UUID) -> bool:
        """Mark OTP as used"""
        pass
    
    @abstractmethod
    def mark_as_expired(self, otp_id: uuid.UUID) -> bool:
        """Mark OTP as expired"""
        pass


class UserProfileRepository(ABC):
    """User Profile repository interface"""
    
    @abstractmethod
    def create(self, profile: UserProfile) -> UserProfile:
        """Create a new user profile"""
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Get profile by user ID"""
        pass
    
    @abstractmethod
    def update(self, profile: UserProfile) -> UserProfile:
        """Update user profile"""
        pass
    
    @abstractmethod
    def delete(self, user_id: uuid.UUID) -> bool:
        """Delete user profile"""
        pass


class UserSessionRepository(ABC):
    """User Session repository interface"""
    
    @abstractmethod
    def create(self, session: UserSession) -> UserSession:
        """Create a new user session"""
        pass
    
    @abstractmethod
    def get_by_id(self, session_id: uuid.UUID) -> Optional[UserSession]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    def get_by_session_key(self, session_key: str) -> Optional[UserSession]:
        """Get session by session key"""
        pass
    
    @abstractmethod
    def get_user_sessions(self, user_id: uuid.UUID, active_only: bool = True) -> List[UserSession]:
        """Get all sessions for a user"""
        pass
    
    @abstractmethod
    def update(self, session: UserSession) -> UserSession:
        """Update user session"""
        pass
    
    @abstractmethod
    def delete(self, session_id: uuid.UUID) -> bool:
        """Delete user session"""
        pass
    
    @abstractmethod
    def deactivate_session(self, session_id: uuid.UUID) -> bool:
        """Deactivate session"""
        pass
    
    @abstractmethod
    def deactivate_user_sessions(self, user_id: uuid.UUID) -> int:
        """Deactivate all sessions for a user"""
        pass
    
    @abstractmethod
    def delete_expired_sessions(self) -> int:
        """Delete expired sessions and return count"""
        pass 