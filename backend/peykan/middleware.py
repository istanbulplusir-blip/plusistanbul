"""
Custom middleware for Peykan Tourism Platform.
"""

from django.utils import translation
from django.conf import settings


class LanguageMiddleware:
    """
    Middleware to handle language detection and setting.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get language from Accept-Language header
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        
        # Parse Accept-Language header
        if accept_language:
            # Extract the first language code
            lang_code = accept_language.split(',')[0].split(';')[0].strip()
            
            # Map common language codes to our supported languages
            if lang_code.startswith('fa') or lang_code.startswith('ar'):
                request.LANGUAGE_CODE = 'fa'
            elif lang_code.startswith('tr'):
                request.LANGUAGE_CODE = 'tr'
            elif lang_code.startswith('en'):
                request.LANGUAGE_CODE = 'en'
            else:
                # Default to Persian
                request.LANGUAGE_CODE = 'fa'
        else:
            # Default to Persian if no Accept-Language header
            request.LANGUAGE_CODE = 'fa'
        
        # Set the language for this request
        translation.activate(request.LANGUAGE_CODE)
        
        response = self.get_response(request)
        
        return response
