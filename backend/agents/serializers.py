"""
DRF Serializers for Agents app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import AgentProfile, AgentCustomer, AgentCommission
from users.models import User


class AgentProfileSerializer(serializers.ModelSerializer):
    """Serializer for AgentProfile model"""
    
    class Meta:
        model = AgentProfile
        fields = [
            'id', 'user', 'company_name', 'license_number', 'business_address',
            'business_phone', 'business_email', 'website', 'commission_rate',
            'min_commission', 'max_commission', 'total_orders', 'total_commission_earned',
            'total_commission_paid', 'average_commission', 'payment_method',
            'payment_account', 'payment_frequency', 'is_active', 'is_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_orders',
                           'total_commission_earned', 'total_commission_paid', 'average_commission']


class AgentCustomerSerializer(serializers.ModelSerializer):
    """Serializer for AgentCustomer model"""
    
    customer_id = serializers.UUIDField(source='customer.id', read_only=True)
    customer_name = serializers.CharField(max_length=255)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    class Meta:
        model = AgentCustomer
        fields = [
            'id', 'agent', 'customer', 'customer_id', 'customer_name', 'customer_email',
            'customer_phone', 'customer_address', 'customer_city', 'customer_country',
            'customer_birth_date', 'customer_gender', 'preferred_language',
            'preferred_contact_method', 'customer_status', 'customer_tier',
            'relationship_notes', 'special_requirements', 'marketing_consent',
            'total_orders', 'total_spent', 'last_order_date', 'is_active',
            'created_by_agent', 'requires_verification', 'credentials_sent',
            'credentials_sent_at', 'last_login_at', 'login_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'agent', 'customer', 'customer_id', 'total_orders',
                           'total_spent', 'last_order_date', 'credentials_sent',
                           'credentials_sent_at', 'last_login_at', 'login_count',
                           'created_at', 'updated_at']
    
    def validate_customer_email(self, value):
        """Validate customer email"""
        if not value:
            raise serializers.ValidationError(_("Customer email is required"))
        return value
    
    def validate_customer_name(self, value):
        """Validate customer name"""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Customer name is required"))
        return value.strip()


class AgentCustomerCreateSerializer(serializers.Serializer):
    """Serializer for creating new customers by agents"""
    
    # Basic Information
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Address Information
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=[('male', _('Male')), ('female', _('Female')), ('other', _('Other'))],
        required=False, allow_blank=True
    )
    
    # Preferences
    preferred_language = serializers.ChoiceField(
        choices=[('fa', _('Persian')), ('en', _('English')), ('ar', _('Arabic'))],
        default='fa'
    )
    preferred_contact_method = serializers.ChoiceField(
        choices=[('email', _('Email')), ('phone', _('Phone')), 
                ('whatsapp', _('WhatsApp')), ('sms', _('SMS'))],
        default='email'
    )
    
    # Customer Settings
    customer_status = serializers.ChoiceField(
        choices=[('active', _('Active')), ('inactive', _('Inactive')), 
                ('blocked', _('Blocked')), ('vip', _('VIP'))],
        default='active'
    )
    customer_tier = serializers.ChoiceField(
        choices=[('bronze', _('Bronze')), ('silver', _('Silver')), 
                ('gold', _('Gold')), ('platinum', _('Platinum'))],
        default='bronze'
    )
    
    # Additional Information
    relationship_notes = serializers.CharField(required=False, allow_blank=True)
    special_requirements = serializers.CharField(required=False, allow_blank=True)
    marketing_consent = serializers.BooleanField(default=False)
    
    # Authentication Options
    send_credentials = serializers.BooleanField(default=True)
    verification_method = serializers.ChoiceField(
        choices=[('email', _('Email')), ('sms', _('SMS')), ('both', _('Both'))],
        default='email'
    )
    welcome_message = serializers.CharField(required=False, allow_blank=True)
    custom_instructions = serializers.CharField(required=False, allow_blank=True)
    
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if not value:
            raise serializers.ValidationError(_("Email is required"))
        
        # Check if customer already exists
        if User.objects.filter(email=value).exists():
            # Customer exists, this is fine - we'll link them to agent
            pass
        
        return value
    
    def validate_first_name(self, value):
        """Validate first name"""
        if not value or not value.strip():
            raise serializers.ValidationError(_("First name is required"))
        return value.strip()
    
    def validate_last_name(self, value):
        """Validate last name"""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Last name is required"))
        return value.strip()
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value and not value.strip():
            return ''
        
        if value:
            # Basic phone validation - can be enhanced
            import re
            phone_pattern = r'^[\+]?[0-9\s\-\(\)]+$'
            if not re.match(phone_pattern, value):
                raise serializers.ValidationError(_("Invalid phone number format"))
        
        return value


class AgentCommissionSerializer(serializers.ModelSerializer):
    """Serializer for AgentCommission model"""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='order.user.get_full_name', read_only=True)
    
    class Meta:
        model = AgentCommission
        fields = [
            'id', 'agent', 'order', 'order_number', 'customer_name',
            'commission_rate', 'commission_amount', 'status', 'notes',
            'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for Agent (User with agent role)"""
    
    agent_profile = AgentProfileSerializer(read_only=True)
    commissions = AgentCommissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
            'role', 'is_active', 'is_email_verified', 'agent_code', 'commission_rate',
            'agent_profile', 'commissions', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'commissions']


class AgentSummarySerializer(serializers.Serializer):
    """Serializer for agent dashboard summary"""
    
    total_customers = serializers.IntegerField()
    active_customers = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_orders = serializers.IntegerField()
    monthly_commission = serializers.DecimalField(max_digits=12, decimal_places=2)