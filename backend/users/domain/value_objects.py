"""
Value Objects for Authentication Domain
Following Domain-Driven Design principles
"""

from dataclasses import dataclass
from typing import Optional
import re
from datetime import datetime


@dataclass(frozen=True)
class Email:
    """Email value object with validation"""
    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError("Invalid email format")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PhoneNumber:
    """Phone number value object with validation"""
    value: str

    def __post_init__(self):
        if not self._is_valid_phone(self.value):
            raise ValueError("Invalid phone number format")

    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Password value object with validation"""
    value: str

    def __post_init__(self):
        if not self._is_valid_password(self.value):
            raise ValueError("Password must be at least 8 characters long")

    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """Validate password strength"""
        return len(password) >= 8

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Username:
    """Username value object with validation"""
    value: str

    def __post_init__(self):
        if not self._is_valid_username(self.value):
            raise ValueError("Invalid username format")

    @staticmethod
    def _is_valid_username(username: str) -> bool:
        """Validate username format"""
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return bool(re.match(pattern, username))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class OTPCode:
    """OTP Code value object"""
    value: str

    def __post_init__(self):
        if not self._is_valid_otp(self.value):
            raise ValueError("OTP must be 6 digits")

    @staticmethod
    def _is_valid_otp(code: str) -> bool:
        """Validate OTP format"""
        return len(code) == 6 and code.isdigit()

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Language:
    """Language value object"""
    code: str

    SUPPORTED_LANGUAGES = ['fa', 'en', 'tr']

    def __post_init__(self):
        if self.code not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {self.code}")

    def __str__(self) -> str:
        return self.code


@dataclass(frozen=True)
class Currency:
    """Currency value object"""
    code: str

    SUPPORTED_CURRENCIES = ['USD', 'EUR', 'TRY', 'IRR']

    def __post_init__(self):
        if self.code not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {self.code}")

    def __str__(self) -> str:
        return self.code


@dataclass(frozen=True)
class IPAddress:
    """IP Address value object"""
    value: str

    def __post_init__(self):
        if not self._is_valid_ip(self.value):
            raise ValueError("Invalid IP address format")

    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """Validate IP address format"""
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SessionKey:
    """Session key value object"""
    value: str

    def __post_init__(self):
        if not self._is_valid_session_key(self.value):
            raise ValueError("Invalid session key format")

    @staticmethod
    def _is_valid_session_key(key: str) -> bool:
        """Validate session key format"""
        return len(key) == 40 and key.isalnum()

    def __str__(self) -> str:
        return self.value 