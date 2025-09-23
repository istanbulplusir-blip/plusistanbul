"""
Domain Layer - Core business logic and entities
Following Domain-Driven Design principles
"""

from .entities import User, OTPCode, UserProfile, UserSession, UserRole, OTPType, VerificationStatus
from .value_objects import Email, PhoneNumber, Password, Username, OTPCode as OTPCodeVO, Language, Currency, IPAddress, SessionKey
from .repositories import UserRepository, OTPRepository, UserProfileRepository, UserSessionRepository
from .services import (
    AuthenticationService, UserRegistrationService, OTPService,
    PasswordService, EmailVerificationService, PhoneVerificationService,
    DjangoAuthenticationService, DjangoUserRegistrationService, DjangoOTPService
)

__all__ = [
    # Entities
    'User', 'OTPCode', 'UserProfile', 'UserSession',
    'UserRole', 'OTPType', 'VerificationStatus',
    
    # Value Objects
    'Email', 'PhoneNumber', 'Password', 'Username', 'OTPCodeVO',
    'Language', 'Currency', 'IPAddress', 'SessionKey',
    
    # Repository Interfaces
    'UserRepository', 'OTPRepository', 'UserProfileRepository', 'UserSessionRepository',
    
    # Service Interfaces
    'AuthenticationService', 'UserRegistrationService', 'OTPService',
    'PasswordService', 'EmailVerificationService', 'PhoneVerificationService',
    
    # Service Implementations
    'DjangoAuthenticationService', 'DjangoUserRegistrationService', 'DjangoOTPService',
] 