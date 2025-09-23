"""
Infrastructure Layer - Data access and external services
Following Clean Architecture principles
"""

from .repositories import (
    DjangoUserRepository, DjangoOTPCodeRepository,
    DjangoUserProfileRepository, DjangoUserSessionRepository
)
from .services import (
    DjangoPasswordService, DjangoEmailVerificationService,
    DjangoPhoneVerificationService, MockEmailService, MockSMSService
)

__all__ = [
    # Repository Implementations
    'DjangoUserRepository', 'DjangoOTPCodeRepository',
    'DjangoUserProfileRepository', 'DjangoUserSessionRepository',
    
    # Service Implementations
    'DjangoPasswordService', 'DjangoEmailVerificationService',
    'DjangoPhoneVerificationService', 'MockEmailService', 'MockSMSService',
] 