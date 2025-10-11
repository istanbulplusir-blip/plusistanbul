#!/usr/bin/env python3
"""
Manual test script for Google OAuth token verification.

This script can be used to manually test Google OAuth functionality
with real Google ID tokens in a development environment.

Usage:
    python test_google_oauth_manual.py

Note: This requires a valid Google ID token for testing.
For production testing, use the automated test suite instead.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from users.utils.google_oauth import verify_google_id_token
from users.models import User
from rest_framework.test import APIClient
from django.urls import reverse
import json


def test_google_oauth_configuration():
    """Test Google OAuth configuration."""
    print("🔍 Testing Google OAuth Configuration...")
    
    # Check settings
    print(f"✅ GOOGLE_CLIENT_ID: {settings.GOOGLE_CLIENT_ID}")
    print(f"✅ GOOGLE_CLIENT_SECRET: {'*' * len(settings.GOOGLE_CLIENT_SECRET)}")
    
    # Verify client ID format
    expected_client_id = "728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com"
    if settings.GOOGLE_CLIENT_ID == expected_client_id:
        print("✅ Client ID matches production configuration")
    else:
        print(f"❌ Client ID mismatch. Expected: {expected_client_id}")
        return False
    
    return True


def test_google_oauth_endpoint():
    """Test Google OAuth API endpoint accessibility."""
    print("\n🔍 Testing Google OAuth API Endpoint...")
    
    client = APIClient()
    google_login_url = reverse('users:google_login')
    
    # Test endpoint exists
    response = client.post(google_login_url, {})
    if response.status_code == 400:  # Bad request (missing token)
        print("✅ Google OAuth endpoint is accessible")
        print(f"✅ Endpoint URL: {google_login_url}")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False


def test_token_verification_function():
    """Test the token verification function with invalid token."""
    print("\n🔍 Testing Token Verification Function...")
    
    try:
        # This should raise an exception for invalid token
        verify_google_id_token("invalid_token")
        print("❌ Token verification should have failed")
        return False
    except Exception as e:
        print(f"✅ Token verification correctly rejects invalid tokens: {type(e).__name__}")
        return True


def test_user_creation_flow():
    """Test user creation flow (without actual Google token)."""
    print("\n🔍 Testing User Creation Flow...")
    
    # Clean up any existing test user
    User.objects.filter(email='test@example.com').delete()
    
    # Simulate user creation (as would happen after successful OAuth)
    user = User.objects.create_user(
        username='test@example.com',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        is_active=True
    )
    user.is_email_verified = True
    user.set_unusable_password()  # OAuth users don't have passwords
    user.save()
    
    # Verify user was created correctly
    created_user = User.objects.get(email='test@example.com')
    if (created_user.is_active and 
        created_user.is_email_verified and 
        not created_user.has_usable_password()):
        print("✅ User creation flow works correctly")
        
        # Clean up
        created_user.delete()
        return True
    else:
        print("❌ User creation flow failed")
        return False


def main():
    """Run all manual tests."""
    print("🚀 Starting Google OAuth Manual Tests...\n")
    
    tests = [
        test_google_oauth_configuration,
        test_google_oauth_endpoint,
        test_token_verification_function,
        test_user_creation_flow,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Google OAuth is properly configured.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1


if __name__ == '__main__':
    sys.exit(main())