"""
Review protection and rate limiting utilities for Tours app.
"""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .validators import ReviewContentValidator, ReviewRateLimitValidator


class ReviewSpamProtection:
    """
    Protects against review spam and abuse.
    """
    
    def __init__(self, max_reviews_per_day=3, max_reviews_per_product=1):
        self.max_reviews_per_day = max_reviews_per_day
        self.max_reviews_per_product = max_reviews_per_product
    
    def check_spam(self, user, content, product, product_type):
        """
        Comprehensive spam check for review submission.
        
        Args:
            user: User instance
            content: Review content
            product: Product instance
            product_type: Type of product ('tour', 'event', etc.)
            
        Returns:
            dict: Spam check result
        """
        issues = []
        status = 'clean'
        
        # Check content for suspicious keywords
        content_validation = ReviewContentValidator.validate_content(content)
        if not content_validation['is_clean']:
            issues.extend(content_validation['issues'])
            status = content_validation['status']
        
        # Check daily rate limit
        daily_check = ReviewRateLimitValidator.check_daily_limit(
            user, self.max_reviews_per_day
        )
        if not daily_check['can_review']:
            issues.append(f'Daily review limit exceeded ({daily_check["total_today"]}/{self.max_reviews_per_day})')
            status = 'rate_limited'
        
        # Check product-specific limit
        product_check = ReviewRateLimitValidator.check_product_limit(
            user, product, product_type, self.max_reviews_per_product
        )
        if not product_check['can_review']:
            issues.append(f'You have already reviewed this {product_type}')
            status = 'duplicate'
        
        # Check for rapid submissions (within 1 minute)
        rapid_check = self._check_rapid_submission(user)
        if not rapid_check['can_submit']:
            issues.append('Please wait before submitting another review')
            status = 'rapid_submission'
        
        return {
            'status': status,
            'issues': issues,
            'can_submit': len(issues) == 0,
            'daily_remaining': daily_check['remaining'],
            'product_remaining': product_check['remaining']
        }
    
    def _check_rapid_submission(self, user):
        """
        Check if user is submitting reviews too rapidly.
        
        Args:
            user: User instance
            
        Returns:
            dict: Rapid submission check result
        """
        cache_key = f'review_last_submission_{user.id}'
        last_submission = cache.get(cache_key)
        
        if last_submission:
            time_diff = timezone.now() - last_submission
            if time_diff.total_seconds() < 60:  # 1 minute
                return {
                    'can_submit': False,
                    'wait_seconds': 60 - int(time_diff.total_seconds())
                }
        
        return {'can_submit': True}
    
    def record_submission(self, user):
        """
        Record a review submission for rate limiting.
        
        Args:
            user: User instance
        """
        cache_key = f'review_last_submission_{user.id}'
        cache.set(cache_key, timezone.now(), 3600)  # Cache for 1 hour


class ReviewRateLimit:
    """
    Manages review rate limiting using cache.
    """
    
    def __init__(self, user, max_per_day=3, max_per_product=1):
        self.user = user
        self.max_per_day = max_per_day
        self.max_per_product = max_per_product
    
    def check_limit(self):
        """
        Check if user can submit a review.
        
        Returns:
            dict: Limit check result
        """
        daily_check = ReviewRateLimitValidator.check_daily_limit(
            self.user, self.max_per_day
        )
        
        return {
            'can_review': daily_check['can_review'],
            'daily_remaining': daily_check['remaining'],
            'max_per_day': self.max_per_day,
            'total_today': daily_check['total_today']
        }
    
    def increment(self):
        """
        Increment the review count for today.
        
        Returns:
            bool: True if successful, False if limit exceeded
        """
        cache_key = f'review_count_{self.user.id}_{timezone.now().date()}'
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.max_per_day:
            return False
        
        cache.set(cache_key, current_count + 1, 86400)  # 24 hours
        return True
    
    def get_remaining(self):
        """
        Get remaining reviews for today.
        
        Returns:
            int: Number of remaining reviews
        """
        cache_key = f'review_count_{self.user.id}_{timezone.now().date()}'
        current_count = cache.get(cache_key, 0)
        return max(0, self.max_per_day - current_count)


class ReviewModeration:
    """
    Handles review moderation and approval.
    """
    
    AUTO_APPROVE_THRESHOLD = 3.0  # Rating >= 3 auto-approves
    
    def __init__(self, auto_approve_threshold=None):
        if auto_approve_threshold is not None:
            self.auto_approve_threshold = auto_approve_threshold
        else:
            self.auto_approve_threshold = self.AUTO_APPROVE_THRESHOLD
    
    def moderate_review(self, review):
        """
        Moderate a review based on content and rating.
        
        Args:
            review: Review instance
            
        Returns:
            dict: Moderation result
        """
        # Check content for issues
        content_validation = ReviewContentValidator.validate_content(
            review.comment
        )
        
        # Determine moderation status
        if content_validation['status'] == 'clean' and review.rating >= self.auto_approve_threshold:
            status = 'approved'
            is_verified = True
            moderation_notes = 'Auto-approved'
        elif content_validation['status'] == 'clean':
            status = 'pending_moderation'
            is_verified = False
            moderation_notes = 'Pending manual review (low rating)'
        else:
            status = 'flagged'
            is_verified = False
            moderation_notes = f'Content issues: {", ".join(content_validation["issues"])}'
        
        return {
            'status': status,
            'is_verified': is_verified,
            'moderation_notes': moderation_notes,
            'content_status': content_validation['status'],
            'auto_approved': status == 'approved'
        }
    
    def apply_moderation(self, review, moderation_result):
        """
        Apply moderation result to review.
        
        Args:
            review: Review instance
            moderation_result: Result from moderate_review method
            
        Returns:
            Review: Updated review instance
        """
        # Update review fields if they exist
        if hasattr(review, 'status'):
            review.status = moderation_result['status']
        
        if hasattr(review, 'is_verified'):
            review.is_verified = moderation_result['is_verified']
        
        if hasattr(review, 'moderation_notes'):
            review.moderation_notes = moderation_result['moderation_notes']
        
        return review


class ReviewProtectionManager:
    """
    Main manager for review protection and moderation.
    """
    
    def __init__(self, max_reviews_per_day=3, max_reviews_per_product=1):
        self.spam_protection = ReviewSpamProtection(
            max_reviews_per_day, max_reviews_per_product
        )
        self.moderation = ReviewModeration()
    
    def validate_review_submission(self, user, content, product, product_type):
        """
        Comprehensive validation for review submission.
        
        Args:
            user: User instance
            content: Review content
            product: Product instance
            product_type: Type of product
            
        Returns:
            dict: Validation result
        """
        # Check spam and rate limits
        spam_check = self.spam_protection.check_spam(user, content, product, product_type)
        
        if not spam_check['can_submit']:
            return {
                'valid': False,
                'issues': spam_check['issues'],
                'status': spam_check['status'],
                'daily_remaining': spam_check['daily_remaining'],
                'product_remaining': spam_check['product_remaining']
            }
        
        # Check purchase requirement
        from .validators import ReviewPurchaseValidator
        has_purchase = ReviewPurchaseValidator.validate_product_purchase(
            user, product, product_type
        )
        
        if not has_purchase:
            return {
                'valid': False,
                'issues': [f'You must purchase this {product_type} before leaving a review'],
                'status': 'purchase_required',
                'daily_remaining': spam_check['daily_remaining'],
                'product_remaining': spam_check['product_remaining']
            }
        
        return {
            'valid': True,
            'issues': [],
            'status': 'valid',
            'daily_remaining': spam_check['daily_remaining'],
            'product_remaining': spam_check['product_remaining']
        }
    
    def process_review_submission(self, user, content, product, product_type):
        """
        Process a review submission with all protections.
        
        Args:
            user: User instance
            content: Review content
            product: Product instance
            product_type: Type of product
            
        Returns:
            dict: Processing result
        """
        # Validate submission
        validation = self.validate_review_submission(user, content, product, product_type)
        
        if not validation['valid']:
            return validation
        
        # Record submission for rate limiting
        self.spam_protection.record_submission(user)
        
        return {
            'valid': True,
            'status': 'submission_recorded',
            'daily_remaining': validation['daily_remaining'] - 1,
            'product_remaining': validation['product_remaining']
        }
