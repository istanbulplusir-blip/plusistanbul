"""
Review validation utilities for Tours app.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ReviewPurchaseValidator:
    """
    Validates that users have purchased products before allowing reviews.
    """
    
    @staticmethod
    def validate_tour_purchase(user, tour):
        """
        Check if user has purchased this tour.
        
        Args:
            user: User instance
            tour: Tour instance
            
        Returns:
            bool: True if user has purchased, False otherwise
        """
        from .models import TourBooking
        
        return TourBooking.objects.filter(
            user=user, 
            tour=tour, 
            status__in=['confirmed', 'completed']
        ).exists()
    
    @staticmethod
    def validate_event_purchase(user, event):
        """
        Check if user has purchased this event.
        
        Args:
            user: User instance
            event: Event instance
            
        Returns:
            bool: True if user has purchased, False otherwise
        """
        from events.models import EventBooking
        
        return EventBooking.objects.filter(
            user=user, 
            event=event, 
            status__in=['confirmed', 'completed']
        ).exists()
    
    @staticmethod
    def validate_product_purchase(user, product, product_type):
        """
        Generic method to validate product purchase.
        
        Args:
            user: User instance
            product: Product instance (Tour, Event, etc.)
            product_type: Type of product ('tour', 'event', etc.)
            
        Returns:
            bool: True if user has purchased, False otherwise
        """
        if product_type == 'tour':
            return ReviewPurchaseValidator.validate_tour_purchase(user, product)
        elif product_type == 'event':
            return ReviewPurchaseValidator.validate_event_purchase(user, product)
        else:
            # For future product types, return False by default
            return False


class ReviewContentValidator:
    """
    Validates review content for spam and inappropriate content.
    """
    
    # Suspicious keywords that might indicate spam
    SPAM_KEYWORDS = [
        'spam', 'advertisement', 'fake', 'scam', 'buy now',
        'click here', 'free money', 'make money fast'
    ]
    
    # Inappropriate content keywords
    INAPPROPRIATE_KEYWORDS = [
        'inappropriate', 'offensive', 'hate', 'discrimination'
    ]
    
    @staticmethod
    def validate_content(content, check_spam=True, check_inappropriate=True):
        """
        Validate review content.
        
        Args:
            content: Review content text
            check_spam: Whether to check for spam keywords
            check_inappropriate: Whether to check for inappropriate content
            
        Returns:
            dict: Validation result with status and messages
        """
        content_lower = content.lower()
        issues = []
        status = 'clean'
        
        if check_spam:
            spam_keywords = [kw for kw in ReviewContentValidator.SPAM_KEYWORDS 
                           if kw in content_lower]
            if spam_keywords:
                issues.append(f'Content contains suspicious keywords: {", ".join(spam_keywords)}')
                status = 'suspicious'
        
        if check_inappropriate:
            inappropriate_keywords = [kw for kw in ReviewContentValidator.INAPPROPRIATE_KEYWORDS 
                                   if kw in content_lower]
            if inappropriate_keywords:
                issues.append(f'Content contains inappropriate keywords: {", ".join(inappropriate_keywords)}')
                status = 'inappropriate'
        
        return {
            'status': status,
            'issues': issues,
            'is_clean': len(issues) == 0
        }
    
    @staticmethod
    def validate_rating(rating):
        """
        Validate review rating.
        
        Args:
            rating: Rating value (1-5)
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            rating_int = int(rating)
            return 1 <= rating_int <= 5
        except (ValueError, TypeError):
            return False


class ReviewRateLimitValidator:
    """
    Validates review rate limits to prevent abuse.
    """
    
    DEFAULT_MAX_PER_DAY = 3
    DEFAULT_MAX_PER_PRODUCT = 1
    
    @staticmethod
    def check_daily_limit(user, max_per_day=None):
        """
        Check if user has exceeded daily review limit.
        
        Args:
            user: User instance
            max_per_day: Maximum reviews per day (default: 3)
            
        Returns:
            dict: Check result with remaining count
        """
        from django.utils import timezone
        from .models import TourReview
        from events.models import EventReview
        
        if max_per_day is None:
            max_per_day = ReviewRateLimitValidator.DEFAULT_MAX_PER_DAY
        
        today = timezone.now().date()
        
        # Count today's reviews across all product types
        tour_reviews = TourReview.objects.filter(
            user=user, 
            created_at__date=today
        ).count()
        
        event_reviews = EventReview.objects.filter(
            user=user, 
            created_at__date=today
        ).count()
        
        total_today = tour_reviews + event_reviews
        remaining = max(0, max_per_day - total_today)
        
        return {
            'can_review': total_today < max_per_day,
            'total_today': total_today,
            'max_per_day': max_per_day,
            'remaining': remaining
        }
    
    @staticmethod
    def check_product_limit(user, product, product_type, max_per_product=None):
        """
        Check if user has exceeded product-specific review limit.
        
        Args:
            user: User instance
            product: Product instance
            product_type: Type of product
            max_per_product: Maximum reviews per product (default: 1)
            
        Returns:
            dict: Check result
        """
        if max_per_product is None:
            max_per_product = ReviewRateLimitValidator.DEFAULT_MAX_PER_PRODUCT
        
        if product_type == 'tour':
            from .models import TourReview
            existing_reviews = TourReview.objects.filter(user=user, tour=product).count()
        elif product_type == 'event':
            from events.models import EventReview
            existing_reviews = EventReview.objects.filter(user=user, event=product).count()
        else:
            existing_reviews = 0
        
        return {
            'can_review': existing_reviews < max_per_product,
            'existing_reviews': existing_reviews,
            'max_per_product': max_per_product,
            'remaining': max(0, max_per_product - existing_reviews)
        }
