"""
Centralized WhatsApp service for getting phone numbers from multiple sources.
"""

from django.conf import settings
from .models import ContactInfo, Footer, SiteSettings


class CentralizedWhatsAppService:
    """Centralized service for WhatsApp phone number management."""
    
    @classmethod
    def get_whatsapp_number(cls):
        """
        Get WhatsApp number from multiple sources with priority order:
        1. ContactInfo (primary)
        2. Footer (secondary) 
        3. SiteSettings (if added)
        4. Settings WHATSAPP_SUPPORT_NUMBER (fallback)
        """
        # Priority 1: ContactInfo
        try:
            contact_info = ContactInfo.objects.filter(is_active=True).first()
            if contact_info and contact_info.whatsapp_number:
                return contact_info.whatsapp_number.strip()
        except Exception:
            pass
        
        # Priority 2: Footer
        try:
            footer = Footer.objects.filter(is_active=True).first()
            if footer and footer.whatsapp_number:
                return footer.whatsapp_number.strip()
        except Exception:
            pass
        
        # Priority 3: SiteSettings (if we add whatsapp_number field)
        try:
            site_settings = SiteSettings.get_settings()
            if hasattr(site_settings, 'whatsapp_number') and site_settings.whatsapp_number:
                return site_settings.whatsapp_number.strip()
        except Exception:
            pass
        
        # Priority 4: Settings fallback
        return getattr(settings, 'WHATSAPP_SUPPORT_NUMBER', '989123456789')
    
    @classmethod
    def get_formatted_whatsapp_number(cls):
        """Get formatted WhatsApp number for display."""
        phone = cls.get_whatsapp_number()
        return cls._format_phone_number(phone)
    
    @classmethod
    def get_whatsapp_url(cls, message=""):
        """Get WhatsApp URL with optional message."""
        phone = cls.get_whatsapp_number()
        formatted_phone = cls._format_phone_number(phone)
        
        if message:
            import urllib.parse
            encoded_message = urllib.parse.quote(message)
            return f"https://wa.me/{formatted_phone}?text={encoded_message}"
        
        return f"https://wa.me/{formatted_phone}"
    
    @classmethod
    def _format_phone_number(cls, phone):
        """Format phone number for WhatsApp URL."""
        # Remove all non-digit characters
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing
        if clean_phone.startswith('9') and len(clean_phone) == 10:
            # Iranian number without country code
            clean_phone = '98' + clean_phone
        elif clean_phone.startswith('0') and len(clean_phone) == 11:
            # Iranian number with 0 prefix
            clean_phone = '98' + clean_phone[1:]
        elif not clean_phone.startswith('98') and len(clean_phone) >= 10:
            # Assume it needs country code
            clean_phone = '98' + clean_phone
        
        return clean_phone
    
    @classmethod
    def get_support_info(cls):
        """Get complete support information."""
        phone = cls.get_whatsapp_number()
        formatted_phone = cls._format_phone_number(phone)
        
        return {
            'phone': phone,
            'formatted_phone': formatted_phone,
            'whatsapp_url': f"https://wa.me/{formatted_phone}",
            'display_phone': cls._get_display_phone(phone)
        }
    
    @classmethod
    def _get_display_phone(cls, phone):
        """Get phone number formatted for display."""
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Format for display (09XX XXX XXXX)
        if clean_phone.startswith('98') and len(clean_phone) == 12:
            return f"0{clean_phone[2:5]} {clean_phone[5:8]} {clean_phone[8:]}"
        elif clean_phone.startswith('989') and len(clean_phone) == 13:
            return f"0{clean_phone[3:6]} {clean_phone[6:9]} {clean_phone[9:]}"
        elif len(clean_phone) == 10:
            return f"0{clean_phone[:3]} {clean_phone[3:6]} {clean_phone[6:]}"
        
        return phone
