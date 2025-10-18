"""
Order validation services for customer information validation.
"""

from users.models import User


class OrderValidationService:
    """
    Service to validate order data based on user authentication method.
    """

    @staticmethod
    def validate_customer_info(customer_info: dict, user: User) -> dict:
        """
        Validate customer information based on authentication method.
        
        Returns:
            dict: {
                'is_valid': bool,
                'errors': list,
                'warnings': list
            }
        """
        errors = []
        warnings = []

        # Check required fields
        if not customer_info.get('full_name', '').strip():
            errors.append('نام و نام خانوادگی ضروری است')

        if not customer_info.get('email', '').strip():
            errors.append('ایمیل ضروری است')

        # Phone validation based on authentication method
        phone_required = OrderValidationService._is_phone_required(user)
        if phone_required and not customer_info.get('phone', '').strip():
            errors.append('شماره تلفن ضروری است')

        # Check for incomplete profile data
        if not customer_info.get('full_name', '').strip() and user:
            warnings.append('نام و نام خانوادگی در پروفایل ناقص است')

        if phone_required and not customer_info.get('phone', '').strip() and user:
            warnings.append('شماره تلفن در پروفایل ناقص است')

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    @staticmethod
    def _is_phone_required(user: User) -> bool:
        """
        Determine if phone number is required based on authentication method.
        """
        if not user:
            return True

        # OAuth users (Google) don't need phone if email is verified
        if user.is_email_verified and not user.phone_number:
            return False

        # Email OTP users don't need phone if email is verified
        if user.is_email_verified and not user.is_phone_verified:
            return False

        # All other cases require phone
        return True

    @staticmethod
    def get_authentication_status(user: User) -> dict:
        """
        Get user authentication status for display purposes.
        """
        if not user:
            return {
                'type': 'none',
                'message': 'احراز هویت نشده',
                'icon_class': 'text-yellow-600'
            }

        if user.is_email_verified and not user.phone_number:
            return {
                'type': 'oauth',
                'message': 'احراز هویت شده با Google',
                'icon_class': 'text-green-600'
            }

        if user.is_email_verified and user.is_phone_verified:
            return {
                'type': 'full',
                'message': 'ایمیل و تلفن تایید شده',
                'icon_class': 'text-green-600'
            }

        if user.is_email_verified:
            return {
                'type': 'email',
                'message': 'ایمیل تایید شده',
                'icon_class': 'text-blue-600'
            }

        return {
            'type': 'none',
            'message': 'احراز هویت نشده',
            'icon_class': 'text-yellow-600'
        }
