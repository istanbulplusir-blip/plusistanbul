"""
Agent utilities for secure operations
"""

import secrets
import string
from typing import Optional
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def generate_secure_password(length: int = 12) -> str:
    """
    Generate a secure random password with mixed characters
    
    Args:
        length: Password length (default: 12)
        
    Returns:
        Secure random password string
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]
    
    # Fill remaining length with random characters from all sets
    all_chars = lowercase + uppercase + digits + special_chars
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def send_customer_welcome_email(customer, password: str, agent) -> bool:
    """
    Send welcome email with login credentials to agent-created customer
    
    Args:
        customer: User object (customer)
        password: Generated password
        agent: User object (agent)
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Get agent profile for company name
        agent_profile = getattr(agent, 'agentprofile', None)
        company_name = agent_profile.company_name if agent_profile else agent.username
        
        # Prepare email context
        context = {
            'customer': customer,
            'agent': agent,
            'agent_company': company_name,
            'password': password,
            'login_url': f"{settings.FRONTEND_URL}/login",
            'verification_url': f"{settings.FRONTEND_URL}/verify-email?token={generate_verification_token(customer)}",
            'site_name': 'Peykan Tourism',
            'support_email': settings.SUPPORT_EMAIL,
        }
        
        # Render email template
        html_content = render_to_string('emails/customer_welcome.html', context)
        text_content = render_to_string('emails/customer_welcome.txt', context)
        
        # Send email
        send_mail(
            subject=_('Welcome to Peykan Tourism - Your Account Details'),
            message=text_content,
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_email_verification(customer) -> bool:
    """
    Send email verification to customer
    
    Args:
        customer: User object
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        from users.models import OTPCode
        
        # Generate verification token
        verification_token = generate_verification_token(customer)
        
        # Create OTP record
        OTPCode.objects.create(
            user=customer,
            email=customer.email,
            code=verification_token,
            otp_type='email_verification',
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        # Prepare email context
        context = {
            'customer': customer,
            'verification_url': f"{settings.FRONTEND_URL}/verify-email?token={verification_token}",
            'site_name': 'Peykan Tourism',
            'support_email': settings.SUPPORT_EMAIL,
        }
        
        # Render email template
        html_content = render_to_string('emails/email_verification.html', context)
        text_content = render_to_string('emails/email_verification.txt', context)
        
        # Send email
        send_mail(
            subject=_('Verify Your Email Address - Peykan Tourism'),
            message=text_content,
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def generate_verification_token(customer) -> str:
    """
    Generate a secure verification token for email verification
    
    Args:
        customer: User object
        
    Returns:
        Secure verification token
    """
    # Create a unique token using customer ID and timestamp
    timestamp = str(int(timezone.now().timestamp()))
    random_part = secrets.token_urlsafe(16)
    return f"{customer.id}_{timestamp}_{random_part}"


def send_customer_credentials(customer, password: str, agent, method: str = 'email') -> bool:
    """
    Send login credentials to customer via specified method
    
    Args:
        customer: User object (customer)
        password: Generated password
        agent: User object (agent)
        method: Delivery method ('email', 'sms', 'both')
        
    Returns:
        True if credentials sent successfully, False otherwise
    """
    try:
        # Get agent profile for company name
        agent_profile = getattr(agent, 'agentprofile', None)
        company_name = agent_profile.company_name if agent_profile else agent.username
        
        # Prepare email context
        context = {
            'customer': customer,
            'agent': agent,
            'agent_company': company_name,
            'password': password,
            'login_url': f"{settings.FRONTEND_URL}/login",
            'site_name': 'Peykan Tourism',
            'support_email': settings.SUPPORT_EMAIL,
        }
        
        # Render email template
        html_content = render_to_string('emails/customer_credentials.html', context)
        text_content = render_to_string('emails/customer_credentials.txt', context)
        
        # Send email
        send_mail(
            subject=_('Your Login Credentials - Peykan Tourism'),
            message=text_content,
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )
        
        # TODO: Implement SMS sending if method includes 'sms'
        if 'sms' in method and customer.phone_number:
            # send_sms_credentials(customer, password, agent)
            pass
        
        return True
        
    except Exception as e:
        print(f"Error sending credentials: {e}")
        return False


def check_existing_customer(email: str) -> Optional[dict]:
    """
    Check if customer with email already exists and return relevant info
    
    Args:
        email: Customer email address
        
    Returns:
        Dict with customer info if exists, None otherwise
    """
    try:
        from users.models import User
        
        customer = User.objects.filter(email=email).first()
        if customer:
            return {
                'id': customer.id,
                'email': customer.email,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'is_email_verified': customer.is_email_verified,
                'is_active': customer.is_active,
                'created_at': customer.created_at,
                'role': customer.role,
            }
        return None
        
    except Exception as e:
        print(f"Error checking existing customer: {e}")
        return None


def link_existing_customer_to_agent(customer, agent, relationship_notes: str = '') -> bool:
    """
    Link an existing customer to an agent
    
    Args:
        customer: User object (existing customer)
        agent: User object (agent)
        relationship_notes: Notes about the relationship
        
    Returns:
        True if linked successfully, False otherwise
    """
    try:
        from .models import AgentCustomer
        
        # Check if relationship already exists
        existing_relationship = AgentCustomer.objects.filter(
            agent=agent,
            customer=customer
        ).first()
        
        if existing_relationship:
            # Update existing relationship
            existing_relationship.relationship_notes = relationship_notes
            existing_relationship.is_active = True
            existing_relationship.save()
        else:
            # Create new relationship
            AgentCustomer.objects.create(
                agent=agent,
                customer=customer,
                customer_name=f"{customer.first_name} {customer.last_name}".strip() or customer.username,
                customer_email=customer.email,
                customer_phone=customer.phone_number or '',
                relationship_notes=relationship_notes,
                created_by_agent=False,  # Customer existed before agent relationship
                requires_verification=not customer.is_email_verified
            )
        
        return True
        
    except Exception as e:
        print(f"Error linking existing customer to agent: {e}")
        return False
