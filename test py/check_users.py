#!/usr/bin/env python
"""
Check existing users in the database.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_users():
    """Check existing users in the database."""
    print("🔍 Checking existing users...")
    
    # Get all users
    users = User.objects.all()
    
    if users.count() == 0:
        print("❌ No users found in database!")
        return False
    
    print(f"✅ Found {users.count()} user(s):")
    
    for user in users:
        print(f"\n👤 User: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   First Name: {user.first_name}")
        print(f"   Last Name: {user.last_name}")
        print(f"   Active: {user.is_active}")
        print(f"   Email Verified: {getattr(user, 'is_email_verified', 'N/A')}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")
        print(f"   Date Joined: {user.date_joined}")
    
    # Check for test user specifically
    test_user = User.objects.filter(username='testuser').first()
    if test_user:
        print(f"\n✅ Test user found: {test_user.username}")
        print(f"   Password: Test@123456")
        print(f"   Ready for testing!")
        return True
    else:
        print(f"\n❌ Test user not found!")
        print(f"   Run: python create_verified_user.py")
        return False

if __name__ == '__main__':
    check_users() 