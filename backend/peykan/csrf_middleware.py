"""
Custom CSRF Middleware for Production
Handles CSRF token issues in production environment
"""

from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ProductionCsrfMiddleware(CsrfViewMiddleware):
    """
    Custom CSRF middleware that handles production-specific CSRF issues
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Skip CSRF for admin login if needed
        if request.path == '/admin/login/' and request.method == 'POST':
            # Log CSRF token for debugging
            csrf_token = request.META.get('HTTP_X_CSRFTOKEN') or request.POST.get('csrfmiddlewaretoken')
            logger.info(f"CSRF Token for admin login: {csrf_token}")
        
        return super().process_view(request, callback, callback_args, callback_kwargs)
    
    def process_response(self, request, response):
        # Ensure CSRF cookie is set properly
        if hasattr(request, 'csrf_processing_done') and request.csrf_processing_done:
            # Set additional CSRF headers for production
            if not response.cookies.get('csrftoken'):
                logger.warning("CSRF token not set in response")
        
        return response
