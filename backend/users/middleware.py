"""
Middleware for user activity logging and security features.
"""

import time
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import JsonResponse

from .services import UserActivityService, SecurityService

User = get_user_model()


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log user activities.
    """
    
    def process_request(self, request):
        """Process request and log activity."""
        # Skip logging for certain paths
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/health/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Skip logging for API endpoints that don't need activity tracking
        skip_api_paths = [
            '/api/users/token/',
            '/api/users/token/refresh/',
            '/api/users/token/verify/',
        ]
        
        if any(request.path.startswith(path) for path in skip_api_paths):
            return None
        
        # Log activity for authenticated users
        if request.user.is_authenticated:
            try:
                UserActivityService.log_activity(
                    user=request.user,
                    activity_type='api_request',
                    description=f'{request.method} {request.path}',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    metadata={
                        'method': request.method,
                        'path': request.path,
                        'query_params': dict(request.GET),
                        'content_type': request.content_type,
                    }
                )
            except Exception as e:
                # Don't fail the request if logging fails
                print(f"Failed to log user activity: {e}")
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware for security features like rate limiting and account lockout.
    """
    
    def process_request(self, request):
        """Process request for security checks."""
        # Skip security checks for certain paths
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/health/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Check account lockout for authenticated users
        if request.user.is_authenticated:
            is_locked, lockout_message = SecurityService.check_account_lockout(request.user)
            if is_locked:
                return JsonResponse(
                    {'error': lockout_message},
                    status=403
                )
        
        # Check rate limiting for authentication endpoints
        if request.path in ['/api/users/login/', '/api/users/register/']:
            identifier = self.get_client_ip(request)
            if request.user.is_authenticated:
                identifier = f"user_{request.user.id}"
            
            is_allowed, error_message = SecurityService.check_login_rate_limit(identifier)
            if not is_allowed:
                return JsonResponse(
                    {'error': error_message},
                    status=429
                )
        
        # Check rate limiting for password reset endpoints
        if request.path in ['/api/users/forgot-password/', '/api/users/reset-password/']:
            identifier = self.get_client_ip(request)
            if request.user.is_authenticated:
                identifier = f"user_{request.user.id}"
            
            is_allowed, error_message = SecurityService.check_password_reset_rate_limit(identifier)
            if not is_allowed:
                return JsonResponse(
                    {'error': error_message},
                    status=429
                )
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware for session security features.
    """
    
    def process_request(self, request):
        """Process request for session security."""
        if request.user.is_authenticated:
            # Check if user's password was changed recently
            # If so, invalidate all sessions
            try:
                from .models import UserActivity
                from django.utils import timezone
                from datetime import timedelta
                
                # Check if password was changed in the last 5 minutes
                recent_password_change = UserActivity.objects.filter(
                    user=request.user,
                    activity_type='password_change',
                    created_at__gte=timezone.now() - timedelta(minutes=5)
                ).exists()
                
                if recent_password_change:
                    # Invalidate current session
                    SecurityService.invalidate_user_sessions(request.user)
                    
                    # Return error response
                    return JsonResponse(
                        {'error': 'Session invalidated due to password change. Please log in again.'},
                        status=401
                    )
                    
            except Exception as e:
                # Don't fail the request if session check fails
                print(f"Failed to check session security: {e}")
        
        return None
