"""
User services for activity logging and security features.
"""

import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any, List
from django.db import models

from .models import UserActivity, User, OTPCode

User = get_user_model()


class UserActivityService:
    """
    Service for logging user activities and security events.
    """
    
    @staticmethod
    def log_activity(
        user: User,
        activity_type: str,
        description: str = '',
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserActivity:
        """
        Log a user activity.
        
        Args:
            user: User instance
            activity_type: Type of activity
            description: Description of the activity
            ip_address: IP address of the request
            user_agent: User agent string
            metadata: Additional metadata
            
        Returns:
            UserActivity instance
        """
        try:
            activity = UserActivity.objects.create(
                user=user,
                activity_type=activity_type,
                description=description,
                ip_address=ip_address or '',
                user_agent=user_agent or '',
                metadata=metadata or {}
            )
            return activity
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Failed to log user activity: {e}")
            return None
    
    @staticmethod
    def log_login_attempt(
        user: Optional[User],
        username: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> Optional[UserActivity]:
        """
        Log a login attempt.
        
        Args:
            user: User instance (None for failed attempts)
            username: Username attempted
            success: Whether login was successful
            ip_address: IP address
            user_agent: User agent string
            failure_reason: Reason for failure
            
        Returns:
            UserActivity instance
        """
        if success and user:
            return UserActivityService.log_activity(
                user=user,
                activity_type='login',
                description=f'Successful login for {username}',
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={'username': username, 'success': True}
            )
        else:
            # For failed attempts, we need to find the user or create a temporary record
            try:
                if user:
                    target_user = user
                else:
                    # Try to find user by username/email
                    target_user = User.objects.filter(
                        Q(username=username) | Q(email=username)
                    ).first()
                
                if target_user:
                    return UserActivityService.log_activity(
                        user=target_user,
                        activity_type='login_failed',
                        description=f'Failed login attempt for {username}: {failure_reason or "Invalid credentials"}',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        metadata={
                            'username': username,
                            'success': False,
                            'failure_reason': failure_reason or 'Invalid credentials'
                        }
                    )
            except Exception as e:
                print(f"Failed to log failed login attempt: {e}")
        
        return None
    
    @staticmethod
    def log_password_change(
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[UserActivity]:
        """
        Log a password change.
        
        Args:
            user: User instance
            ip_address: IP address
            user_agent: User agent string
            
        Returns:
            UserActivity instance
        """
        return UserActivityService.log_activity(
            user=user,
            activity_type='password_change',
            description=f'Password changed for {user.email}',
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={'user_id': str(user.id), 'user_email': user.email}
        )
    
    @staticmethod
    def log_profile_update(
        user: User,
        updated_fields: List[str],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[UserActivity]:
        """
        Log a profile update.
        
        Args:
            user: User instance
            updated_fields: List of updated field names
            ip_address: IP address
            user_agent: User agent string
            
        Returns:
            UserActivity instance
        """
        return UserActivityService.log_activity(
            user=user,
            activity_type='profile_update',
            description=f'Profile updated for {user.email}',
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                'user_id': str(user.id),
                'user_email': user.email,
                'updated_fields': updated_fields
            }
        )
    
    @staticmethod
    def get_user_activities(
        user: User,
        activity_type: Optional[str] = None,
        limit: int = 50
    ) -> List[UserActivity]:
        """
        Get user activities.
        
        Args:
            user: User instance
            activity_type: Filter by activity type
            limit: Maximum number of activities to return
            
        Returns:
            List of UserActivity instances
        """
        queryset = UserActivity.objects.filter(user=user)
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        return list(queryset.order_by('-created_at')[:limit])


class SecurityService:
    """
    Service for security features like rate limiting and account lockout.
    """
    
    @staticmethod
    def check_rate_limit(
        identifier: str,
        action: str,
        limit: int,
        window_seconds: int = 60
    ) -> tuple[bool, Optional[str]]:
        """
        Check if an action is within rate limits.
        
        Args:
            identifier: Unique identifier (user ID, IP address, etc.)
            action: Action being performed
            limit: Maximum number of actions allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        cache_key = f"rate_limit_{action}_{identifier}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return False, f"Rate limit exceeded. Please wait {window_seconds} seconds before trying again."
        
        # Increment counter
        cache.set(cache_key, current_count + 1, window_seconds)
        return True, None
    
    @staticmethod
    def check_login_rate_limit(
        identifier: str,
        limit: int = 5,
        window_seconds: int = 300  # 5 minutes
    ) -> tuple[bool, Optional[str]]:
        """
        Check login rate limit.
        
        Args:
            identifier: User ID or IP address
            limit: Maximum login attempts
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        return SecurityService.check_rate_limit(
            identifier=identifier,
            action='login',
            limit=limit,
            window_seconds=window_seconds
        )
    
    @staticmethod
    def check_password_reset_rate_limit(
        identifier: str,
        limit: int = 3,
        window_seconds: int = 3600  # 1 hour
    ) -> tuple[bool, Optional[str]]:
        """
        Check password reset rate limit.
        
        Args:
            identifier: User ID or IP address
            limit: Maximum password reset attempts
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        return SecurityService.check_rate_limit(
            identifier=identifier,
            action='password_reset',
            limit=limit,
            window_seconds=window_seconds
        )
    
    @staticmethod
    def check_account_lockout(user: User) -> tuple[bool, Optional[str]]:
        """
        Check if user account is locked due to failed login attempts.
        
        Args:
            user: User instance
            
        Returns:
            Tuple of (is_locked, lockout_message)
        """
        # Check for recent failed login attempts
        recent_failed_attempts = UserActivity.objects.filter(
            user=user,
            activity_type='login_failed',
            created_at__gte=timezone.now() - timedelta(minutes=15)
        ).count()
        
        if recent_failed_attempts >= 5:  # 5 failed attempts in 15 minutes
            return True, "Account temporarily locked due to multiple failed login attempts. Please try again in 15 minutes."
        
        return False, None
    
    @staticmethod
    def lock_account_temporarily(user: User, minutes: int = 15) -> None:
        """
        Temporarily lock user account.
        
        Args:
            user: User instance
            minutes: Number of minutes to lock account
        """
        cache_key = f"account_locked_{user.id}"
        cache.set(cache_key, True, minutes * 60)
    
    @staticmethod
    def is_account_locked(user: User) -> bool:
        """
        Check if user account is currently locked.
        
        Args:
            user: User instance
            
        Returns:
            True if account is locked
        """
        cache_key = f"account_locked_{user.id}"
        return cache.get(cache_key, False)
    
    @staticmethod
    def invalidate_user_sessions(user: User) -> int:
        """
        Invalidate all user sessions (for password change, etc.).
        
        Args:
            user: User instance
            
        Returns:
            Number of sessions invalidated
        """
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            
            # Blacklist all refresh tokens for the user
            for token in RefreshToken.objects.filter(user=user):
                token.blacklist()
            
            # Update user sessions to inactive
            from .models import UserSession
            sessions_updated = UserSession.objects.filter(
                user=user,
                is_active=True
            ).update(is_active=False)
            
            # Log the session invalidation
            UserActivityService.log_activity(
                user=user,
                activity_type='session_invalidation',
                description=f'All sessions invalidated for {user.email}',
                metadata={'sessions_invalidated': sessions_updated}
            )
            
            return sessions_updated
            
        except Exception as e:
            print(f"Failed to invalidate user sessions: {e}")
            return 0


class UserDataService:
    """
    Service for user data operations and analytics.
    """
    
    @staticmethod
    def get_or_create_user_profile(user: User):
        """
        Get or create user profile.
        
        Args:
            user: User instance
            
        Returns:
            UserProfile instance
        """
        from .models import UserProfile
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'city': '',
                'country': ''
            }
        )
        return profile
    
    @staticmethod
    def get_user_statistics(user: User) -> Dict[str, Any]:
        """
        Get user statistics and activity summary.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary with user statistics
        """
        try:
            # Basic user info
            stats = {
                'user_id': str(user.id),
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'is_email_verified': user.is_email_verified,
                'is_phone_verified': user.is_phone_verified,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
            
            # Activity counts
            activity_counts = UserActivity.objects.filter(user=user).values('activity_type').annotate(
                count=models.Count('id')
            )
            
            stats['activity_counts'] = {item['activity_type']: item['count'] for item in activity_counts}
            
            # Recent activities
            recent_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:10]
            stats['recent_activities'] = [
                {
                    'activity_type': activity.activity_type,
                    'description': activity.description,
                    'created_at': activity.created_at.isoformat(),
                    'ip_address': activity.ip_address
                }
                for activity in recent_activities
            ]
            
            # Security status
            stats['security_status'] = {
                'is_locked': SecurityService.is_account_locked(user),
                'failed_login_attempts_24h': UserActivity.objects.filter(
                    user=user,
                    activity_type='login_failed',
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).count(),
                'last_password_change': UserActivity.objects.filter(
                    user=user,
                    activity_type='password_change'
                ).order_by('-created_at').first().created_at.isoformat() if UserActivity.objects.filter(
                    user=user,
                    activity_type='password_change'
                ).exists() else None
            }
            
            return stats
            
        except Exception as e:
            print(f"Failed to get user statistics: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def cleanup_old_activities(days: int = 90) -> int:
        """
        Clean up old user activities.
        
        Args:
            days: Number of days to keep activities
            
        Returns:
            Number of activities deleted
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days)
            deleted_count, _ = UserActivity.objects.filter(
                created_at__lt=cutoff_date
            ).delete()
            
            return deleted_count
            
        except Exception as e:
            print(f"Failed to cleanup old activities: {e}")
            return 0