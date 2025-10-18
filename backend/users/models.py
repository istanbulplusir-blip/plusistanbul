"""
User models for Peykan Tourism Platform.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from core.models import BaseModel
from datetime import timedelta
from django.utils import timezone


class User(AbstractUser, BaseModel):
    """
    Custom User model with UUID primary key and role-based authentication.
    """
    
    # Override id field to use UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Role choices
    ROLE_CHOICES = [
        ('guest', _('Guest')),
        ('customer', _('Customer')),
        ('agent', _('Agent')),
        ('admin', _('Admin')),
    ]
    
    # User fields
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='guest',
        verbose_name=_('Role')
    )
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name=_('Phone number')
    )
    
    # Preferences
    preferred_language = models.CharField(
        max_length=2, 
        default='fa',
        choices=[
            ('fa', 'Persian'),
            ('en', 'English'),
            ('tr', 'Turkish'),
        ],
        verbose_name=_('Preferred language')
    )
    preferred_currency = models.CharField(
        max_length=3, 
        default='USD',
        choices=[
            ('USD', 'US Dollar'),
            ('EUR', 'Euro'),
            ('TRY', 'Turkish Lira'),
            ('IRR', 'Iranian Rial'),
        ],
        verbose_name=_('Preferred currency')
    )
    
    # Agent-specific fields
    agent_code = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name=_('Agent code')
    )
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        verbose_name=_('Commission rate (%)')
    )
    
    # Customer-specific fields
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('Date of birth')
    )
    nationality = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Nationality')
    )
    
    # Verification fields
    is_phone_verified = models.BooleanField(default=False, verbose_name=_('Phone verified'))
    is_email_verified = models.BooleanField(default=False, verbose_name=_('Email verified'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username or self.email or str(self.id)
    
    @property
    def is_agent(self):
        return self.role == 'agent'
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_guest(self):
        return self.role == 'guest'
    
    def save(self, *args, **kwargs):
        # Generate agent code for agents
        if self.role == 'agent' and not self.agent_code:
            self.agent_code = f"AG{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)
    
    def verify_email(self):
        """Mark email as verified and activate user"""
        self.is_email_verified = True
        self.is_active = True
        self.save(update_fields=['is_email_verified', 'is_active'])
    
    def verify_phone(self):
        """Mark phone as verified"""
        self.is_phone_verified = True
        self.save(update_fields=['is_phone_verified'])




class OTPCode(models.Model):
    """
    One-Time Password Model
    Handles email and phone verification codes
    """
    
    OTP_TYPE_CHOICES = [
        ('email_verification', _('Email Verification')),
        ('phone_verification', _('Phone Verification')),
        ('password_reset', _('Password Reset')),
        ('login', _('Login')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes', verbose_name=_('User'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('Phone'))
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES, verbose_name=_('OTP Type'))
    code = models.CharField(max_length=6, verbose_name=_('OTP Code'))
    is_used = models.BooleanField(default=False, verbose_name=_('Is Used'))
    expires_at = models.DateTimeField(verbose_name=_('Expires At'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    used_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Used At'))
    
    class Meta:
        verbose_name = _('OTP Code')
        verbose_name_plural = _('OTP Codes')
        db_table = 'user_otps'
        indexes = [
            models.Index(fields=['user', 'otp_type']),
            models.Index(fields=['email', 'otp_type']),
            models.Index(fields=['phone', 'otp_type']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_type} - {self.code}"
    
    @property
    def is_expired(self):
        """Check if OTP is expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    
    def save(self, *args, **kwargs):
        """Override save to set default expiration time"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)


class UserProfile(BaseModel):
    """
    Extended user profile information.
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name=_('User')
    )
    
    # Personal information
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        verbose_name=_('Avatar')
    )
    bio = models.TextField(blank=True, verbose_name=_('Bio'))
    
    # Address information
    address = models.TextField(blank=True, verbose_name=_('Address'))
    city = models.CharField(max_length=100, blank=True, verbose_name=_('City'))
    country = models.CharField(max_length=100, blank=True, verbose_name=_('Country'))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_('Postal code'))
    
    # Social media
    website = models.URLField(blank=True, verbose_name=_('Website'))
    facebook = models.URLField(blank=True, verbose_name=_('Facebook'))
    instagram = models.URLField(blank=True, verbose_name=_('Instagram'))
    twitter = models.URLField(blank=True, verbose_name=_('Twitter'))
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='fa', verbose_name=_('Preferred Language'))
    timezone = models.CharField(max_length=50, default='Asia/Tehran', verbose_name=_('Timezone'))
    newsletter_subscription = models.BooleanField(default=True, verbose_name=_('Newsletter subscription'))
    marketing_emails = models.BooleanField(default=True, verbose_name=_('Marketing emails'))
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"{self.user.username} Profile"


class UserSession(BaseModel):
    """
    User session tracking for analytics and security.
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        verbose_name=_('User')
    )
    
    # Session details
    session_key = models.CharField(max_length=40, verbose_name=_('Session key'))
    ip_address = models.GenericIPAddressField(verbose_name=_('IP address'))
    user_agent = models.TextField(verbose_name=_('User agent'))
    
    # Location
    country = models.CharField(max_length=100, blank=True, verbose_name=_('Country'))
    city = models.CharField(max_length=100, blank=True, verbose_name=_('City'))
    
    # Activity
    last_activity = models.DateTimeField(auto_now=True, verbose_name=_('Last activity'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    
    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} - {self.last_activity}"


class UserActivity(models.Model):
    """
    User Activity Model
    Track user activities for security and analytics
    """
    
    ACTIVITY_TYPE_CHOICES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('password_change', _('Password Change')),
        ('email_verification', _('Email Verification')),
        ('phone_verification', _('Phone Verification')),
        ('profile_update', _('Profile Update')),
        ('password_reset_request', _('Password Reset Request')),
        ('password_reset_complete', _('Password Reset Complete')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', verbose_name=_('User'))
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES, verbose_name=_('Activity Type'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('IP Address'))
    user_agent = models.TextField(blank=True, verbose_name=_('User Agent'))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_('Metadata'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        db_table = 'user_activities'
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}" 