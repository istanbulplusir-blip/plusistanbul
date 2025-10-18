"""
Presentation Layer - API Controllers
Following Clean Architecture principles
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..permissions import IsVerifiedUser, IsActiveUser
from ..services import UserActivityService, SecurityService
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View

from ..application.use_cases import (
    RegisterUserUseCase, LoginUserUseCase, LogoutUserUseCase,
    VerifyEmailUseCase, VerifyPhoneUseCase, ResetPasswordUseCase,
    ChangePasswordUseCase, GetUserProfileUseCase, UpdateUserProfileUseCase, ForgotPasswordUseCase,
    RequestSensitiveFieldUpdateUseCase, VerifySensitiveFieldUpdateUseCase
)
from ..infrastructure.repositories import (
    DjangoUserRepository, DjangoOTPCodeRepository, 
    DjangoUserProfileRepository, DjangoUserSessionRepository
)
from ..domain.services import (
    DjangoAuthenticationService, DjangoUserRegistrationService,
    DjangoOTPService
)


class AuthenticationController:
    """Authentication controller with dependency injection"""
    
    def __init__(self):
        # Initialize repositories
        self.user_repository = DjangoUserRepository()
        self.otp_repository = DjangoOTPCodeRepository()
        self.profile_repository = DjangoUserProfileRepository()
        self.session_repository = DjangoUserSessionRepository()
        
        # Initialize services
        self.auth_service = DjangoAuthenticationService(
            self.user_repository, 
            self._get_password_service()
        )
        self.registration_service = DjangoUserRegistrationService(
            self.user_repository,
            self._get_password_service()
        )
        self.otp_service = DjangoOTPService(self.otp_repository)
        
        # Initialize use cases
        self.register_use_case = RegisterUserUseCase(
            self.registration_service,
            self.user_repository,
            self.profile_repository,
            self.otp_service,
            self._get_email_service()
        )
        
        self.login_use_case = LoginUserUseCase(
            self.auth_service,
            self.session_repository
        )
        
        self.logout_use_case = LogoutUserUseCase(
            self.session_repository
        )
        
        self.verify_email_use_case = VerifyEmailUseCase(
            self.otp_service,
            self.user_repository,
            self._get_email_service()
        )
        
        self.verify_phone_use_case = VerifyPhoneUseCase(
            self.otp_service,
            self.user_repository,
            self._get_phone_service()
        )
        
        self.forgot_password_use_case = ForgotPasswordUseCase(
            self.otp_service,
            self.user_repository,
            self._get_email_service()
        )
        
        self.reset_password_use_case = ResetPasswordUseCase(
            self.otp_service,
            self.user_repository,
            self._get_password_service(),
            self._get_email_service()
        )
        
        self.change_password_use_case = ChangePasswordUseCase(
            self.user_repository,
            self._get_password_service()
        )
        
        self.get_profile_use_case = GetUserProfileUseCase(
            self.user_repository,
            self.profile_repository
        )
        
        self.update_profile_use_case = UpdateUserProfileUseCase(
            self.user_repository,
            self.profile_repository
        )
        
        self.request_sensitive_update_use_case = RequestSensitiveFieldUpdateUseCase(
            self.user_repository,
            self.otp_service,
            self._get_email_service(),
            self._get_phone_service()
        )
        
        self.verify_sensitive_update_use_case = VerifySensitiveFieldUpdateUseCase(
            self.user_repository,
            self.otp_service
        )
    
    def _get_password_service(self):
        """Get password service implementation"""
        from ..infrastructure.services import DjangoPasswordService
        return DjangoPasswordService()
    
    def _get_email_service(self):
        """Get email service implementation"""
        from ..infrastructure.services import DjangoEmailVerificationService
        return DjangoEmailVerificationService(self.otp_service)

    def _get_phone_service(self):
        """Get phone service implementation"""
        from ..infrastructure.services import DjangoPhoneVerificationService
        return DjangoPhoneVerificationService(self.otp_service)


class RegisterView(APIView):
    """User registration endpoint"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Handle user registration"""
        try:
            data = request.data
            print("Registration data received:", data)  # Debug log
            
            # Extract data
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            password_confirm = data.get('password_confirm')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phone_number = data.get('phone_number')
            role = data.get('role', 'customer')
            
            print("Extracted data:", {  # Debug log
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password_length': len(password) if password else 0,
                'password_confirm_length': len(password_confirm) if password_confirm else 0,
                'phone_number': phone_number,
                'role': role
            })
            
            # Execute use case
            result = self.controller.register_use_case.execute(
                username=username,
                email=email,
                password=password,
                password_confirm=password_confirm,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role=role
            )
            
            print("Use case result:", result)  # Debug log
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'user': result['user'],
                    'profile': result['profile'],
                    'email_verification_required': result.get('email_verification_required', False),
                    'email': result.get('email', '')
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': result['message'],
                    'errors': result.get('errors', [])
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print("Registration exception:", str(e))  # Debug log
            import traceback
            print("Traceback:", traceback.format_exc())  # Debug log
            return Response({
                'message': 'Registration failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    """User login endpoint"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Handle user login"""
        try:
            data = request.data
            print(f"🔍 Login request data: {data}")  # Debug log
            
            # Extract data
            username = data.get('username')
            password = data.get('password')
            
            print(f"🔍 Extracted username: {username}")  # Debug log
            print(f"🔍 Extracted password length: {len(password) if password else 0}")  # Debug log
            
            if not username or not password:
                return Response({
                    'message': 'Username and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # TEMPORARY: Use Django's built-in authentication
            from django.contrib.auth import authenticate
            from rest_framework_simplejwt.tokens import RefreshToken
            
            print(f"🔍 Using Django authenticate...")  # Debug log
            user = authenticate(username=username, password=password)
            
            if not user:
                # Try with email
                user = authenticate(username=username, password=password)
            
            print(f"🔍 Django authenticate result: {user}")  # Debug log
            
            if not user:
                # Log failed login attempt
                UserActivityService.log_login_attempt(
                    user=None,
                    username=username,
                    success=False,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    failure_reason='Invalid credentials'
                )
                return Response({
                    'non_field_errors': ['Invalid credentials.']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not user.is_active:
                # Log failed login attempt
                UserActivityService.log_login_attempt(
                    user=user,
                    username=username,
                    success=False,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    failure_reason='Account disabled'
                )
                return Response({
                    'non_field_errors': ['Account is disabled.']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            tokens = {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
            
            # Log successful login
            UserActivityService.log_login_attempt(
                user=user,
                username=username,
                success=True,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Convert user to dict
            user_data = {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'role': user.role,
                'is_active': user.is_active,
                'is_phone_verified': user.is_phone_verified,
                'is_email_verified': user.is_email_verified,
                'phone_number': user.phone_number,
                'preferred_language': user.preferred_language,
                'preferred_currency': user.preferred_currency,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
            
            print(f"🔍 Login successful for user: {user.username}")  # Debug log
            
            # Automatically merge cart after regular login
            cart_message = ''
            try:
                from cart.models import CartService, Cart
                session_key = request.session.session_key
                
                if session_key:
                    # Check if there's a guest cart to merge
                    guest_cart = Cart.objects.filter(
                        session_id=session_key,
                        user__isnull=True,
                        is_active=True
                    ).first()
                    
                    if guest_cart and guest_cart.items.exists():
                        # Get user cart
                        user_cart = CartService.get_or_create_cart(
                            session_id=session_key,
                            user=user
                        )
                        
                        # Merge items
                        merged_items = 0
                        for guest_item in guest_cart.items.all():
                            # Check if item already exists in user cart
                            if guest_item.product_type == 'tour':
                                existing_item = user_cart.items.filter(
                                    product_type=guest_item.product_type,
                                    product_id=guest_item.product_id,
                                    variant_id=guest_item.variant_id,
                                    booking_data__schedule_id=guest_item.booking_data.get('schedule_id')
                                ).first()
                            else:
                                existing_item = user_cart.items.filter(
                                    product_type=guest_item.product_type,
                                    product_id=guest_item.product_id,
                                    variant_id=guest_item.variant_id
                                ).first()
                            
                            if existing_item:
                                # Update quantity
                                existing_item.quantity += guest_item.quantity
                                existing_item.save()
                            else:
                                # Move item to user cart
                                guest_item.cart = user_cart
                                guest_item.save()
                            
                            merged_items += 1
                        
                        # Delete guest cart
                        guest_cart.delete()
                        
                        cart_message = f' Cart merged with {merged_items} items.' if merged_items > 0 else ''
            except Exception as e:
                # Don't fail the login if cart merge fails
                print(f"Cart merge error: {e}")
                cart_message = ''
            
            return Response({
                'success': True,
                'message': 'Login successful' + cart_message,
                'user': user_data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            import traceback
            print('Login error:', str(e))
            print('Traceback:', traceback.format_exc())
            return Response({
                'success': False,
                'message': 'Login failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    """User logout endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Handle user logout"""
        try:
            # Execute use case
            result = self.controller.logout_use_case.execute(
                user_id=request.user.id
            )
            
            return Response({
                'message': result['message'],
                'deactivated_sessions': result['deactivated_sessions']
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'message': 'Logout failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(APIView):
    """Email verification endpoint"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Handle email verification"""
        try:
            data = request.data
            
            # Extract data
            email = data.get('email')
            otp_code = data.get('otp_code')
            
            # Execute use case
            result = self.controller.verify_email_use_case.execute(
                email=email,
                otp_code=otp_code
            )
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'user': result['user'],
                    'tokens': result.get('tokens')
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Email verification failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Resend verification email"""
        try:
            # Get email from request data or use authenticated user's email
            email = request.data.get('email')
            
            # If no email provided and user is authenticated, use their email
            if not email and hasattr(request, 'user') and request.user.is_authenticated:
                email = request.user.email
            
            if not email:
                return Response({
                    'message': 'Email is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Execute use case
            result = self.controller.verify_email_use_case.resend_verification(email)
            
            return Response({
                'message': result['message']
            }, status=status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Failed to resend verification email',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPhoneView(APIView):
    """Phone verification endpoint"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Handle phone verification"""
        try:
            data = request.data
            
            # Extract data
            phone = data.get('phone')
            otp_code = data.get('otp_code')
            
            # Execute use case
            result = self.controller.verify_phone_use_case.execute(
                phone=phone,
                otp_code=otp_code
            )
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'user': result['user']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Phone verification failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Resend verification SMS"""
        try:
            # Get phone from request data or use authenticated user's phone
            phone = request.data.get('phone')
            
            # If no phone provided and user is authenticated, use their phone
            if not phone and hasattr(request, 'user') and request.user.is_authenticated:
                phone = getattr(request.user, 'phone_number', None)
            
            if not phone:
                return Response({
                    'message': 'Phone number is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Execute use case
            result = self.controller.verify_phone_use_case.resend_verification(phone)
            
            return Response({
                'message': result['message']
            }, status=status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Failed to resend verification SMS',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForgotPasswordView(APIView):
    """Forgot password endpoint - Request password reset OTP"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Handle forgot password request"""
        try:
            data = request.data
            
            # Extract data
            email = data.get('email')
            
            if not email:
                return Response({
                    'message': 'Email is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Execute use case
            result = self.controller.forgot_password_use_case.execute(email=email)
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'email': result['email']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Forgot password request failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    """Password reset endpoint"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Handle password reset"""
        try:
            data = request.data
            
            # Extract data
            email = data.get('email')
            new_password = data.get('new_password')
            otp_code = data.get('otp_code')
            
            # Execute use case
            result = self.controller.reset_password_use_case.execute(
                email=email,
                new_password=new_password,
                otp_code=otp_code
            )
            
            if result['success']:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Password reset failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Request password reset"""
        try:
            data = request.data
            email = data.get('email')
            
            # Execute use case
            result = self.controller.reset_password_use_case.request_reset(email)
            
            return Response({
                'message': result['message']
            }, status=status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Failed to request password reset',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    """Password change endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Handle password change"""
        try:
            data = request.data
            
            # Extract data
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            # Execute use case
            result = self.controller.change_password_use_case.execute(
                user_id=request.user.id,
                current_password=current_password,
                new_password=new_password
            )
            
            if result['success']:
                # Log password change
                UserActivityService.log_password_change(
                    user=request.user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Invalidate all user sessions
                sessions_invalidated = SecurityService.invalidate_user_sessions(request.user)
                
                return Response({
                    'message': result['message'],
                    'sessions_invalidated': sessions_invalidated
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Password change failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    """User profile endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def get(self, request):
        """Get user profile"""
        try:
            # Execute use case
            result = self.controller.get_profile_use_case.execute(
                user_id=request.user.id
            )
            
            if result['success']:
                return Response({
                    'user': result['user'],
                    'profile': result['profile']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'message': 'Failed to get user profile',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update user profile"""
        try:
            data = request.data
            
            # Separate user and profile data
            user_data = {}
            profile_data = {}
            
            # Handle nested structure from frontend
            if 'user_data' in data:
                user_data = data['user_data']
            if 'profile' in data:
                profile_data = data['profile']
            
            # Also handle flat structure for backward compatibility
            # User fields
            user_fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'nationality', 'preferred_language', 'preferred_currency']
            for field in user_fields:
                if field in data:
                    user_data[field] = data[field]
            
            # Profile fields
            profile_fields = ['bio', 'address', 'city', 'country', 'postal_code', 
                            'website', 'facebook', 'instagram', 'twitter',
                            'newsletter_subscription', 'marketing_emails']
            for field in profile_fields:
                if field in data:
                    profile_data[field] = data[field]
            
            # Execute use case
            result = self.controller.update_profile_use_case.execute(
                user_id=request.user.id,
                user_data=user_data,
                profile_data=profile_data
            )
            
            if result['success']:
                return Response({
                    'user': result['user'],
                    'profile': result['profile'],
                    'message': result['message']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Failed to update user profile',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SensitiveFieldUpdateView(APIView):
    """Sensitive field update endpoint - Request OTP for sensitive field changes"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Request sensitive field update with OTP"""
        try:
            data = request.data
            
            # Extract data
            field = data.get('field')
            new_value = data.get('new_value')
            
            if not field or not new_value:
                return Response({
                    'message': 'Field and new_value are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Execute use case
            result = self.controller.request_sensitive_update_use_case.execute(
                user_id=request.user.id,
                field=field,
                new_value=new_value
            )
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'field': result['field'],
                    'new_value': result['new_value'],
                    'otp_id': result['otp_id']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Failed to request sensitive field update',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SensitiveFieldVerifyView(APIView):
    """Sensitive field verification endpoint - Verify OTP and update field"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AuthenticationController()
    
    def post(self, request):
        """Verify sensitive field update with OTP"""
        try:
            data = request.data
            
            # Extract data
            field = data.get('field')
            new_value = data.get('new_value')
            otp_code = data.get('otp_code')
            
            if not field or not new_value or not otp_code:
                return Response({
                    'message': 'Field, new_value, and otp_code are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Execute use case
            result = self.controller.verify_sensitive_update_use_case.execute(
                user_id=request.user.id,
                field=field,
                new_value=new_value,
                otp_code=otp_code
            )
            
            if result['success']:
                return Response({
                    'user': result['user'],
                    'message': result['message']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'message': 'Failed to verify sensitive field update',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)