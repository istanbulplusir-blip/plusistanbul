"""
Admin serializers for user management.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import UserProfile, UserActivity

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list view (admin)."""
    
    full_name = serializers.SerializerMethodField()
    last_login_display = serializers.SerializerMethodField()
    created_at_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'is_active', 'is_email_verified', 'is_phone_verified',
            'last_login', 'last_login_display', 'created_at', 'created_at_display',
            'phone_number', 'preferred_language', 'preferred_currency'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M:%S')
        return 'Never'
    
    def get_created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin user management."""
    
    profile = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    activities_count = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'is_active', 'is_email_verified', 'is_phone_verified',
            'phone_number', 'preferred_language', 'preferred_currency',
            'date_of_birth', 'nationality', 'agent_code', 'commission_rate',
            'created_at', 'updated_at', 'last_login', 'date_joined',
            'profile', 'activities_count', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'date_joined']
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'id': str(profile.id),
                'avatar': profile.avatar.url if profile.avatar else None,
                'bio': profile.bio,
                'address': profile.address,
                'city': profile.city,
                'country': profile.country,
                'postal_code': profile.postal_code,
                'website': profile.website,
                'facebook': profile.facebook,
                'instagram': profile.instagram,
                'twitter': profile.twitter,
                'newsletter_subscription': profile.newsletter_subscription,
                'marketing_emails': profile.marketing_emails,
            }
        except UserProfile.DoesNotExist:
            return None
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_activities_count(self, obj):
        return UserActivity.objects.filter(user=obj).count()
    
    def get_last_activity(self, obj):
        last_activity = UserActivity.objects.filter(user=obj).order_by('-created_at').first()
        if last_activity:
            return {
                'activity_type': last_activity.activity_type,
                'description': last_activity.description,
                'created_at': last_activity.created_at.isoformat(),
                'ip_address': last_activity.ip_address
            }
        return None


class UserCreateAdminSerializer(serializers.ModelSerializer):
    """Serializer for creating users (admin)."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role', 'phone_number',
            'preferred_language', 'preferred_currency', 'date_of_birth',
            'nationality', 'is_active', 'is_email_verified', 'is_phone_verified'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserUpdateAdminSerializer(serializers.ModelSerializer):
    """Serializer for updating users (admin)."""
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role',
            'phone_number', 'preferred_language', 'preferred_currency',
            'date_of_birth', 'nationality', 'is_active',
            'is_email_verified', 'is_phone_verified', 'commission_rate'
        ]
    
    def update(self, instance, validated_data):
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class UserPasswordResetAdminSerializer(serializers.Serializer):
    """Serializer for admin password reset."""
    
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        return attrs


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity logs."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'activity_type',
            'description', 'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics."""
    
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    role_distribution = serializers.ListField()
    recent_registrations_30d = serializers.IntegerField()
    recent_logins_7d = serializers.IntegerField()
    verification_rate = serializers.FloatField()
    activation_rate = serializers.FloatField()


class UserBulkActionSerializer(serializers.Serializer):
    """Serializer for bulk user actions."""
    
    ACTION_CHOICES = [
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
        ('verify_email', 'Verify Email'),
        ('verify_phone', 'Verify Phone'),
        ('send_welcome_email', 'Send Welcome Email'),
    ]
    
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    
    def validate_user_ids(self, value):
        """Validate that all user IDs exist."""
        existing_users = User.objects.filter(id__in=value).count()
        if existing_users != len(value):
            raise serializers.ValidationError("Some user IDs do not exist.")
        return value


class UserSearchSerializer(serializers.Serializer):
    """Serializer for user search."""
    
    query = serializers.CharField(max_length=255, required=False)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    is_active = serializers.BooleanField(required=False)
    is_email_verified = serializers.BooleanField(required=False)
    is_phone_verified = serializers.BooleanField(required=False)
    created_after = serializers.DateTimeField(required=False)
    created_before = serializers.DateTimeField(required=False)
    last_login_after = serializers.DateTimeField(required=False)
    last_login_before = serializers.DateTimeField(required=False)
