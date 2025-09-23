import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import OTPCode
from users.domain.services import DjangoUserRegistrationService, DjangoOTPService
from users.domain.entities import OTPType
from users.infrastructure.services import DjangoPasswordService, DjangoEmailVerificationService
from users.infrastructure.repositories import DjangoUserRepository, DjangoOTPCodeRepository

User = get_user_model()

# Delete all regular users (non-superusers)
User.objects.filter(is_superuser=False).delete()
print("All regular users have been deleted.")

# Create new user
user_data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'Test@123456',
    'first_name': 'Test',
    'last_name': 'User'
}

user_repo = DjangoUserRepository()
password_service = DjangoPasswordService()
registration_service = DjangoUserRegistrationService(user_repo, password_service)

# Create user
user_entity = registration_service.register_user(
    username=user_data['username'],
    email=user_data['email'],
    password=user_data['password'],
    first_name=user_data['first_name'],
    last_name=user_data['last_name']
)

# Get the Django model instance
user = User.objects.get(username=user_data['username'])
print(f"Created user: {user.username} ({user.email})")

# Create OTP directly using Django model
otp = OTPCode.objects.create(
    user=user,
    email=user.email,
    otp_type='email_verification',
    code='123456',
    expires_at=timezone.now() + timezone.timedelta(minutes=10)
)
print(f"OTP code: {otp.code}")

# Verify email directly using Django model
user.verify_email()
print("Email verified successfully!")

# Final user status
user.refresh_from_db()
print(f"\nUser Status:")
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Email Verified: {user.is_email_verified}")
print(f"Active: {user.is_active}")

# Print login credentials
print("\nLogin Credentials:")
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Password: {user_data['password']}") 