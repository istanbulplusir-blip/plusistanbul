"""
Test Google OAuth token verification functionality.
"""

import os
import json
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from users.models import User
from users.utils.google_oauth import verify_google_id_token


class GoogleOAuthTestCase(TestCase):
    """Test Google OAuth functionality."""
    
    def setUp(self):
        self.client = APIClient()
        self.google_login_url = reverse('users:google_login')
        
    def test_google_client_id_configured(self):
        """Test that Google Client ID is properly configured."""
        from django.conf import settings
        
        # Check that GOOGLE_CLIENT_ID is set
        self.assertTrue(hasattr(settings, 'GOOGLE_CLIENT_ID'))
        self.assertIsNotNone(settings.GOOGLE_CLIENT_ID)
        self.assertNotEqual(settings.GOOGLE_CLIENT_ID, '')
        
        # Check that it matches the production environment value
        expected_client_id = "728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com"
        self.assertEqual(settings.GOOGLE_CLIENT_ID, expected_client_id)
        
    def test_google_client_secret_configured(self):
        """Test that Google Client Secret is properly configured."""
        from django.conf import settings
        
        # Check that GOOGLE_CLIENT_SECRET is set
        self.assertTrue(hasattr(settings, 'GOOGLE_CLIENT_SECRET'))
        self.assertIsNotNone(settings.GOOGLE_CLIENT_SECRET)
        self.assertNotEqual(settings.GOOGLE_CLIENT_SECRET, '')
        
    @patch('users.utils.google_oauth.id_token.verify_oauth2_token')
    def test_google_token_verification_success(self, mock_verify):
        """Test successful Google ID token verification."""
        # Mock Google token payload
        mock_payload = {
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
            'sub': '123456789',
            'aud': '728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com'
        }
        mock_verify.return_value = mock_payload
        
        # Test token verification function
        test_token = "fake_google_id_token"
        result = verify_google_id_token(test_token)
        
        # Verify the function was called with correct parameters
        mock_verify.assert_called_once()
        self.assertEqual(result, mock_payload)
        
    @patch('users.utils.google_oauth.id_token.verify_oauth2_token')
    def test_google_login_new_user(self, mock_verify):
        """Test Google login with new user creation."""
        # Mock Google token payload
        mock_payload = {
            'email': 'newuser@example.com',
            'email_verified': True,
            'name': 'New User',
            'given_name': 'New',
            'family_name': 'User',
            'sub': '987654321',
            'aud': '728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com'
        }
        mock_verify.return_value = mock_payload
        
        # Make request to Google login endpoint
        response = self.client.post(self.google_login_url, {
            'id_token': 'fake_google_id_token'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify response structure
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertIn('tokens', data)
        self.assertIn('Google sign-up successful', data['message'])
        
        # Verify user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_email_verified)
        
    @patch('users.utils.google_oauth.id_token.verify_oauth2_token')
    def test_google_login_existing_user(self, mock_verify):
        """Test Google login with existing user."""
        # Create existing user
        existing_user = User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            is_active=True
        )
        
        # Mock Google token payload
        mock_payload = {
            'email': 'existing@example.com',
            'email_verified': True,
            'name': 'Existing User',
            'given_name': 'Existing',
            'family_name': 'User',
            'sub': '555666777',
            'aud': '728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com'
        }
        mock_verify.return_value = mock_payload
        
        # Make request to Google login endpoint
        response = self.client.post(self.google_login_url, {
            'id_token': 'fake_google_id_token'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify response structure
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertIn('tokens', data)
        self.assertIn('Google sign-in successful', data['message'])
        
        # Verify user data
        self.assertEqual(data['user']['email'], 'existing@example.com')
        
    @patch('users.utils.google_oauth.id_token.verify_oauth2_token')
    def test_google_login_invalid_token(self, mock_verify):
        """Test Google login with invalid token."""
        # Mock token verification failure
        mock_verify.side_effect = Exception("Invalid token")
        
        # Make request to Google login endpoint
        response = self.client.post(self.google_login_url, {
            'id_token': 'invalid_google_id_token'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        # Verify error response
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid Google token')
        
    @patch('users.utils.google_oauth.id_token.verify_oauth2_token')
    def test_google_login_unverified_email(self, mock_verify):
        """Test Google login with unverified email."""
        # Mock Google token payload with unverified email
        mock_payload = {
            'email': 'unverified@example.com',
            'email_verified': False,
            'name': 'Unverified User',
            'given_name': 'Unverified',
            'family_name': 'User',
            'sub': '111222333',
            'aud': '728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com'
        }
        mock_verify.return_value = mock_payload
        
        # Make request to Google login endpoint
        response = self.client.post(self.google_login_url, {
            'id_token': 'fake_google_id_token'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        # Verify error response
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Email not verified by Google')
        
    def test_google_login_missing_token(self):
        """Test Google login with missing ID token."""
        # Make request without ID token
        response = self.client.post(self.google_login_url, {})
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_google_oauth_endpoint_accessible(self):
        """Test that Google OAuth API endpoint is accessible."""
        # Make OPTIONS request to check endpoint accessibility
        response = self.client.options(self.google_login_url)
        
        # Should return 200 OK for OPTIONS request
        self.assertIn(response.status_code, [200, 405])  # 405 is also acceptable for OPTIONS
        
        # Make POST request with empty data to check endpoint exists
        response = self.client.post(self.google_login_url, {})
        
        # Should return 400 (bad request) not 404 (not found)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    @patch('users.utils.google_oauth.id_token.verify_oauth2_token')
    def test_google_oauth_complete_flow_with_configured_client_id(self, mock_verify):
        """Test complete Google OAuth flow with the actual configured client ID."""
        from django.conf import settings
        
        # Verify we're using the correct production client ID
        expected_client_id = "728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com"
        self.assertEqual(settings.GOOGLE_CLIENT_ID, expected_client_id)
        
        # Mock Google token payload with the actual client ID
        mock_payload = {
            'email': 'testuser@gmail.com',
            'email_verified': True,
            'name': 'Test User Complete',
            'given_name': 'Test',
            'family_name': 'User Complete',
            'sub': '123456789012345',
            'aud': expected_client_id,  # Use the actual configured client ID
            'iss': 'https://accounts.google.com',
            'exp': 1234567890,
            'iat': 1234567800
        }
        mock_verify.return_value = mock_payload
        
        # Test the complete flow: token verification -> user creation -> JWT generation
        response = self.client.post(self.google_login_url, {
            'id_token': 'valid_google_id_token_for_production'
        })
        
        # Verify successful response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify response structure matches requirements
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertIn('tokens', data)
        self.assertIn('Google sign-up successful', data['message'])
        
        # Verify user was created with correct data
        user = User.objects.get(email='testuser@gmail.com')
        self.assertEqual(user.username, 'testuser@gmail.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User Complete')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_email_verified)
        self.assertFalse(user.has_usable_password())  # OAuth users don't have passwords
        
        # Verify JWT tokens are provided
        self.assertIn('access', data['tokens'])
        self.assertIn('refresh', data['tokens'])
        self.assertIsNotNone(data['tokens']['access'])
        self.assertIsNotNone(data['tokens']['refresh'])
        
        # Verify user data in response
        self.assertEqual(data['user']['email'], 'testuser@gmail.com')
        self.assertEqual(data['user']['first_name'], 'Test')
        self.assertEqual(data['user']['last_name'], 'User Complete')
        
        # Verify the token verification was called with correct parameters
        mock_verify.assert_called_once()
        call_args = mock_verify.call_args
        self.assertEqual(call_args[0][0], 'valid_google_id_token_for_production')  # Token
        # Verify the audience (client ID) parameter
        from django.conf import settings
        self.assertEqual(call_args[0][2], settings.GOOGLE_CLIENT_ID)  # Client ID
        
    @patch('users.utils.google_oauth.id_token.verify_oauth2_token')
    def test_google_oauth_user_authentication_flow(self, mock_verify):
        """Test Google OAuth authentication flow for existing users."""
        # Create an existing user first
        existing_user = User.objects.create_user(
            username='existing@gmail.com',
            email='existing@gmail.com',
            first_name='Existing',
            last_name='User',
            is_active=True,
            is_email_verified=False  # Test that OAuth updates verification status
        )
        
        # Mock Google token payload
        mock_payload = {
            'email': 'existing@gmail.com',
            'email_verified': True,
            'name': 'Existing User Updated',
            'given_name': 'Existing',
            'family_name': 'User Updated',
            'sub': '987654321098765',
            'aud': '728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com'
        }
        mock_verify.return_value = mock_payload
        
        # Test authentication flow
        response = self.client.post(self.google_login_url, {
            'id_token': 'valid_google_id_token_existing_user'
        })
        
        # Verify successful authentication
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify it's a sign-in, not sign-up
        self.assertIn('Google sign-in successful', data['message'])
        
        # Verify user was updated (email verification status)
        updated_user = User.objects.get(email='existing@gmail.com')
        self.assertTrue(updated_user.is_email_verified)  # Should be updated to True
        self.assertTrue(updated_user.is_active)
        
        # Verify JWT tokens are provided for authentication
        self.assertIn('access', data['tokens'])
        self.assertIn('refresh', data['tokens'])
        
        # Verify no duplicate user was created
        user_count = User.objects.filter(email='existing@gmail.com').count()
        self.assertEqual(user_count, 1)
        
    def test_google_oauth_configuration_validation(self):
        """Test that Google OAuth configuration is properly validated."""
        from django.conf import settings
        from users.utils.google_oauth import verify_google_id_token
        
        # Test that settings are properly configured
        self.assertTrue(hasattr(settings, 'GOOGLE_CLIENT_ID'))
        self.assertTrue(hasattr(settings, 'GOOGLE_CLIENT_SECRET'))
        
        # Test that the client ID is the expected production value
        expected_client_id = "728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com"
        self.assertEqual(settings.GOOGLE_CLIENT_ID, expected_client_id)
        
        # Test that the verify function exists and is callable
        self.assertTrue(callable(verify_google_id_token))
        
        # Test that the function raises an exception for invalid tokens
        with self.assertRaises(Exception):
            verify_google_id_token("invalid_token")


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
        django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.test_google_oauth"])