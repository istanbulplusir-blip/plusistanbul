#!/usr/bin/env python
"""
Debug authentication issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from users.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

# Import Clean Architecture components
from users.infrastructure.repositories import DjangoUserRepository
from users.infrastructure.services import DjangoPasswordService
from users.domain.services import DjangoAuthenticationService

def test_authentication():
    print("=== Testing Authentication ===")
    
    try:
        # Get user
        user = User.objects.get(username='testuser')
        print(f"✅ User found: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔐 Is active: {user.is_active}")
        print(f"🔑 Has usable password: {user.has_usable_password()}")
        print(f"🔑 Password field length: {len(user.password)}")
        print(f"🔑 Password field preview: {user.password[:50]}...")
        
        # Test Django's built-in password check
        print(f"\n=== Testing Django Password Check ===")
        django_check = user.check_password("123789")
        print(f"🔑 Django check_password('123789'): {django_check}")
        
        # Test manual password check
        print(f"\n=== Testing Manual Password Check ===")
        manual_check = check_password("123789", user.password)
        print(f"🔑 Manual check_password('123789', user.password): {manual_check}")
        
        # Test Django authenticate
        print(f"\n=== Testing Django Authenticate ===")
        auth_user = authenticate(username='testuser', password='123789')
        print(f"🔑 Django authenticate('testuser', '123789'): {auth_user}")
        
        # Test with email
        print(f"\n=== Testing with Email ===")
        auth_user_email = authenticate(username='test@example.com', password='123789')
        print(f"🔑 Django authenticate('test@example.com', '123789'): {auth_user_email}")
        
        # Test wrong password
        print(f"\n=== Testing Wrong Password ===")
        wrong_auth = authenticate(username='testuser', password='wrong')
        print(f"🔑 Django authenticate('testuser', 'wrong'): {wrong_auth}")
        
        # Test wrong username
        print(f"\n=== Testing Wrong Username ===")
        wrong_user = authenticate(username='wronguser', password='123789')
        print(f"🔑 Django authenticate('wronguser', '123789'): {wrong_user}")
        
    except User.DoesNotExist:
        print("❌ User 'testuser' not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_clean_architecture_auth():
    print("\n" + "="*50)
    print("=== Testing Clean Architecture Authentication ===")
    
    try:
        # Initialize Clean Architecture components
        user_repo = DjangoUserRepository()
        password_service = DjangoPasswordService()
        auth_service = DjangoAuthenticationService(user_repo, password_service)
        
        # Test getting user by username
        print("\n--- Testing User Repository ---")
        user = user_repo.get_by_username('testuser')
        if user:
            print(f"✅ User found via repository: {user.username}")
            print(f"📧 Email: {user.email}")
            print(f"🔐 Is active: {user.is_active}")
            print(f"🔑 Password hash length: {len(user.password_hash) if user.password_hash else 0}")
            print(f"🔑 Password hash preview: {user.password_hash[:50] if user.password_hash else 'None'}...")
        else:
            print("❌ User not found via repository")
            return
        
        # Test password verification
        print("\n--- Testing Password Service ---")
        password_check = password_service.verify_password("123789", user.password_hash)
        print(f"🔑 Password service verify('123789', password_hash): {password_check}")
        
        # Test authentication service
        print("\n--- Testing Authentication Service ---")
        auth_user = auth_service.authenticate_user('testuser', '123789')
        print(f"🔑 Auth service authenticate('testuser', '123789'): {auth_user}")
        
        # Test with wrong password
        print("\n--- Testing Wrong Password ---")
        wrong_auth = auth_service.authenticate_user('testuser', 'wrong')
        print(f"🔑 Auth service authenticate('testuser', 'wrong'): {wrong_auth}")
        
        # Test with email
        print("\n--- Testing with Email ---")
        email_auth = auth_service.authenticate_user('test@example.com', '123789')
        print(f"🔑 Auth service authenticate('test@example.com', '123789'): {email_auth}")
        
    except Exception as e:
        print(f"❌ Clean Architecture Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_authentication()
    test_clean_architecture_auth() 