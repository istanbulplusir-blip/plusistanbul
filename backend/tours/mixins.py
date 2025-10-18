"""
Review management mixins for Tours app.
"""

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _


class ReviewManagementMixin:
    """
    Mixin providing review management functionality.
    """
    
    # Time limits for editing/deleting reviews
    EDIT_TIME_LIMIT_HOURS = 24
    DELETE_TIME_LIMIT_HOURS = 48
    
    def can_edit_review(self, user, review):
        """
        Check if user can edit this review.
        
        Args:
            user: User instance
            review: Review instance
            
        Returns:
            dict: Result with permissions and remaining time
        """
        if not user.is_authenticated:
            return {
                'can_edit': False,
                'reason': 'User not authenticated',
                'remaining_time': None
            }
        
        if user != review.user:
            return {
                'can_edit': False,
                'reason': 'You can only edit your own reviews',
                'remaining_time': None
            }
        
        # Check if review is still editable
        time_since_creation = timezone.now() - review.created_at
        time_limit = timedelta(hours=self.EDIT_TIME_LIMIT_HOURS)
        
        if time_since_creation > time_limit:
            return {
                'can_edit': False,
                'reason': f'Reviews can only be edited within {self.EDIT_TIME_LIMIT_HOURS} hours',
                'remaining_time': None
            }
        
        remaining_time = time_limit - time_since_creation
        return {
            'can_edit': True,
            'reason': None,
            'remaining_time': remaining_time
        }
    
    def can_delete_review(self, user, review):
        """
        Check if user can delete this review.
        
        Args:
            user: User instance
            review: Review instance
            
        Returns:
            dict: Result with permissions and remaining time
        """
        if not user.is_authenticated:
            return {
                'can_delete': False,
                'reason': 'User not authenticated',
                'remaining_time': None
            }
        
        if user != review.user:
            return {
                'can_delete': False,
                'reason': 'You can only delete your own reviews',
                'remaining_time': None
            }
        
        # Check if review is still deletable
        time_since_creation = timezone.now() - review.created_at
        time_limit = timedelta(hours=self.DELETE_TIME_LIMIT_HOURS)
        
        if time_since_creation > time_limit:
            return {
                'can_delete': False,
                'reason': f'Reviews can only be deleted within {self.DELETE_TIME_LIMIT_HOURS} hours',
                'remaining_time': None
            }
        
        remaining_time = time_limit - time_since_creation
        return {
            'can_delete': True,
            'reason': None,
            'remaining_time': remaining_time
        }
    
    def can_moderate_review(self, user, review):
        """
        Check if user can moderate this review.
        
        Args:
            user: User instance
            review: Review instance
            
        Returns:
            bool: True if user can moderate
        """
        # Staff users can moderate any review
        if user.is_staff:
            return True
        
        # Superusers can moderate any review
        if user.is_superuser:
            return True
        
        # Check if user has specific moderation permissions
        if user.has_perm('tours.can_moderate_reviews'):
            return True
        
        return False
    
    def can_report_review(self, user, review):
        """
        Check if user can report this review.
        
        Args:
            user: User instance
            review: Review instance
            
        Returns:
            dict: Result with permissions
        """
        if not user.is_authenticated:
            return {
                'can_report': False,
                'reason': 'You must be logged in to report reviews'
            }
        
        if user == review.user:
            return {
                'can_report': False,
                'reason': 'You cannot report your own review'
            }
        
        # Check if user has already reported this review
        from .models import ReviewReport
        existing_report = ReviewReport.objects.filter(
            reporter=user,
            review=review,
            status__in=['pending', 'investigating']
        ).first()
        
        if existing_report:
            return {
                'can_report': False,
                'reason': 'You have already reported this review'
            }
        
        return {
            'can_report': True,
            'reason': None
        }
    
    def can_respond_to_review(self, user, review):
        """
        Check if user can respond to this review.
        
        Args:
            user: User instance
            review: Review instance
            
        Returns:
            dict: Result with permissions
        """
        if not user.is_authenticated:
            return {
                'can_respond': False,
                'reason': 'You must be logged in to respond to reviews'
            }
        
        # Product owners can respond to reviews (if owner field exists)
        if hasattr(review, 'tour') and hasattr(review.tour, 'owner') and review.tour.owner == user:
            return {
                'can_respond': True,
                'reason': None
            }
        
        # Staff users can respond to any review
        if user.is_staff:
            return {
                'can_respond': True,
                'reason': None
            }
        
        return {
            'can_respond': False,
            'reason': 'Only product owners and staff can respond to reviews'
        }
    
    def get_review_permissions(self, user, review):
        """
        Get comprehensive permissions for a review.
        
        Args:
            user: User instance
            review: Review instance
            
        Returns:
            dict: All permissions for the review
        """
        return {
            'edit': self.can_edit_review(user, review),
            'delete': self.can_delete_review(user, review),
            'moderate': self.can_moderate_review(user, review),
            'report': self.can_report_review(user, review),
            'respond': self.can_respond_to_review(user, review),
            'is_owner': user == review.user if user.is_authenticated else False,
            'is_staff': user.is_staff if user.is_authenticated else False
        }
