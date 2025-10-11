"""
DRF Serializers for Users app.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, OTPCode
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'avatar', 'bio', 'address', 'city', 'country', 'postal_code',
            'website', 'facebook', 'instagram', 'twitter',
            'newsletter_subscription', 'marketing_emails'
        ]
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """Main User serializer for read operations."""
    
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'is_active', 'is_phone_verified', 'is_email_verified',
            'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_phone_verified', 'is_email_verified']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role', 'profile'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(_("Passwords don't match."))
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        validated_data.pop('password_confirm', None)
        
        user = User.objects.create_user(**validated_data)
        
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        else:
            UserProfile.objects.create(user=user)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates."""
    
    profile = UserProfileSerializer(partial=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        import logging
        logger = logging.getLogger(__name__)
        
        username = attrs.get('username')
        password = attrs.get('password')
        
        logger.debug(f"Validating login credentials for username: {username}")
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                logger.warning(f"Failed login attempt for username: {username}")
                raise serializers.ValidationError(_('Invalid credentials.'))
            if not user.is_active:
                logger.warning(f"Disabled account login attempt for username: {username}")
                raise serializers.ValidationError(_('User account is disabled.'))
            logger.debug(f"Successfully validated credentials for username: {username}")
            attrs['user'] = user
        else:
            logger.warning("Login attempt with missing credentials")
            raise serializers.ValidationError(_('Must include username and password.'))
        
        return attrs


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for OTP request."""
    
    phone = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    otp_type = serializers.ChoiceField(choices=[
        ('email_verification', 'Email verification'),
        ('phone_verification', 'Phone verification'),
        ('password_reset', 'Password reset'),
        ('login', 'Login'),
    ])
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        email = attrs.get('email')
        
        if not phone and not email:
            raise serializers.ValidationError(_('Phone or email is required.'))
        
        if attrs['otp_type'] in ['phone_verification', 'login'] and not phone:
            raise serializers.ValidationError(_('Phone is required for this OTP type.'))
        
        if attrs['otp_type'] in ['email_verification', 'password_reset'] and not email:
            raise serializers.ValidationError(_('Email is required for this OTP type.'))
        
        return attrs


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification."""
    
    phone = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    code = serializers.CharField(max_length=6, min_length=6)
    otp_type = serializers.ChoiceField(choices=[
        ('email_verification', 'Email verification'),
        ('phone_verification', 'Phone verification'),
        ('password_reset', 'Password reset'),
        ('login', 'Login'),
    ])
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        email = attrs.get('email')
        
        if not phone and not email:
            raise serializers.ValidationError(_('Phone or email is required.'))
        
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset."""
    
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("Passwords don't match."))
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("Passwords don't match."))
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return attrs 


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google Sign-In (ID token)."""
    id_token = serializers.CharField()