"""
DRF Views for Users app.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random
import string

from .models import User, UserProfile, OTPCode
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    LoginSerializer, OTPRequestSerializer, OTPVerifySerializer,
    PasswordResetSerializer, ChangePasswordSerializer, GoogleAuthSerializer
)
from .utils.google_oauth import verify_google_id_token


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        # Extract data from request
        if hasattr(request, 'data'):
            data = request.data
        else:
            import json
            try:
                data = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = request.POST
        print(f"Registration data received: {data}")
        
        # Extract registration data
        email = data.get('email')
        username = data.get('username') or email.split('@')[0] if email else None
        
        registration_data = {
            'username': username,
            'email': email,
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'password': data.get('password'),
            'password_confirm': data.get('password_confirm'),
            'phone_number': data.get('phone_number'),
            'role': data.get('role', 'customer')
        }
        
        print(f"Extracted data: {registration_data}")
        
        # Execute registration use case
        from .application.use_cases import RegisterUserUseCase
        from .infrastructure.repositories import DjangoUserRepository, DjangoUserProfileRepository, DjangoOTPCodeRepository
        from .infrastructure.services import DjangoPasswordService, DjangoEmailVerificationService
        from .domain.services import DjangoUserRegistrationService, DjangoOTPService
        
        # Initialize dependencies
        user_repository = DjangoUserRepository()
        profile_repository = DjangoUserProfileRepository()
        otp_repository = DjangoOTPCodeRepository()
        password_service = DjangoPasswordService()
        registration_service = DjangoUserRegistrationService(user_repository, password_service)
        otp_service = DjangoOTPService(otp_repository)
        email_service = DjangoEmailVerificationService(otp_service)
        
        # Create use case
        use_case = RegisterUserUseCase(
            registration_service=registration_service,
            user_repository=user_repository,
            profile_repository=profile_repository,
            otp_service=otp_service,
            email_service=email_service
        )
        
        # Execute use case
        result = use_case.execute(**registration_data)
        print(f"Use case result: {result}")
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        # Log request data
        logger.info(f"🔍 Login request data: {request.data}")
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        logger.info(f"🔍 Extracted username: {username}")
        logger.info(f"🔍 Extracted password length: {len(password)}")
        
        # Authenticate manually first
        logger.info("🔍 Using Django authenticate...")
        user = authenticate(username=username, password=password)
        logger.info(f"🔍 Django authenticate result: {user}")
        
        # Continue with serializer validation
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"❌ Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=400)
            
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"✅ User {user.username} logged in successfully")
        return Response({
            'message': 'Login successful.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """Update user profile."""
    
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileUpdateView(APIView):
    """Update user profile with extended information."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Update user profile information."""
        user = request.user
        
        try:
            # Get or create user profile
            from users.services import UserDataService
            profile = UserDataService.get_or_create_user_profile(user)
            
            # Update profile fields
            if 'phone_number' in request.data:
                profile.phone_number = request.data['phone_number']
            if 'address' in request.data:
                profile.address = request.data['address']
            if 'city' in request.data:
                profile.city = request.data['city']
            if 'country' in request.data:
                profile.country = request.data['country']
            if 'postal_code' in request.data:
                profile.postal_code = request.data['postal_code']
            
            profile.save()
            
            # Update user fields if provided
            if 'full_name' in request.data:
                name_parts = request.data['full_name'].split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
                user.save()
            
            return Response({
                'message': 'Profile updated successfully',
                'profile': {
                    'phone_number': profile.phone_number,
                    'address': profile.address,
                    'city': profile.city,
                    'country': profile.country,
                    'postal_code': profile.postal_code,
                },
                'user': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to update profile: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OTPRequestView(APIView):
    """Request OTP for verification."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        otp_type = data['otp_type']
        target = data.get('phone') or data.get('email')
        
        # Generate OTP code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Set expiry (10 minutes)
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Create OTP record
        otp_data = {
            'user': None,  # Will be set after verification
            'code': code,
            'otp_type': otp_type,
            'expires_at': expires_at
        }
        
        # Set email or phone based on otp_type
        if otp_type in ['phone', 'login']:
            otp_data['phone'] = target
        else:
            otp_data['email'] = target
            
        otp = OTPCode.objects.create(**otp_data)
        
        # Send OTP (mock for now)
        if otp_type in ['phone', 'login']:
            # Send SMS
            print(f"SMS OTP to {target}: {code}")
        else:
            # Send Email
            print(f"Email OTP to {target}: {code}")
        
        return Response({
            'message': f'OTP sent to {target}',
            'otp_type': otp_type,
            'target': target
        })


class OTPVerifyView(APIView):
    """Verify OTP code."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        code = data['code']
        otp_type = data['otp_type']
        target = data.get('phone') or data.get('email')
        
        # Find valid OTP
        try:
            otp_filter = {
                'code': code,
                'otp_type': otp_type,
                'is_used': False,
                'expires_at__gt': timezone.now()
            }
            
            # Add email or phone filter based on otp_type
            if otp_type in ['phone', 'login']:
                otp_filter['phone'] = target
            else:
                otp_filter['email'] = target
                
            otp = OTPCode.objects.get(**otp_filter)
        except OTPCode.DoesNotExist:
            return Response({
                'error': 'Invalid or expired OTP code.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark OTP as used
        otp.is_used = True
        otp.save()
        
        # Handle different OTP types
        if otp_type == 'login':
            # Find user by phone
            try:
                user = User.objects.get(profile__phone=target)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'OTP verified successfully.',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found with this phone number.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif otp_type == 'phone':
            # Mark user as verified
            if otp.user:
                otp.user.is_verified = True
                otp.user.save()
                return Response({
                    'message': 'Phone verified successfully.'
                })
        
        elif otp_type == 'email':
            # Mark user as verified and active
            if otp.user:
                otp.user.is_email_verified = True
                otp.user.is_active = True  # Activate user after email verification
                otp.user.save()
                
                # Generate tokens for auto-login after verification
                refresh = RefreshToken.for_user(otp.user)
                return Response({
                    'message': 'Email verified successfully.',
                    'user': UserSerializer(otp.user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
        
        return Response({
            'message': 'OTP verified successfully.'
        })


class PasswordResetRequestView(APIView):
    """Request password reset OTP."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found with this email.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate OTP code
        code = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Create OTP record
        OTPCode.objects.create(
            user=user,
            code=code,
            otp_type='password_reset',
            email=email,
            expires_at=expires_at
        )
        
        # Send OTP email (mock for now)
        print(f"Password reset OTP to {email}: {code}")
        
        return Response({
            'message': f'Password reset code sent to {email}',
            'email': email
        })


class PasswordResetView(APIView):
    """Reset password using OTP."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        email = data['email']
        code = data['code']
        new_password = data['new_password']
        
        # Verify OTP
        try:
            otp = OTPCode.objects.get(
                code=code,
                otp_type='password_reset',
                email=email,
                is_used=False,
                expires_at__gt=timezone.now()
            )
        except OTPCode.DoesNotExist:
            return Response({
                'error': 'Invalid or expired OTP code.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user and update password
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp.is_used = True
            otp.save()
            
            return Response({
                'message': 'Password reset successfully.'
            })
        except User.DoesNotExist:
            return Response({
                'error': 'User not found with this email.'
            }, status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    """Change password for authenticated user."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        
        # Verify current password
        if not user.check_password(current_password):
            return Response({
                'error': 'Current password is incorrect.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password changed successfully.'
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user by blacklisting refresh token and clearing cart."""
    
    try:
        # Blacklist refresh token
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Clear user cart
        from cart.models import CartService
        user_cart = CartService.get_or_create_cart(
            session_id=request.session.session_key,
            user=request.user
        )
        CartService.clear_cart(user_cart)
        
        # Clear session data
        request.session.flush()
        
        return Response({
            'message': 'Logged out successfully.'
        })
    except Exception:
        return Response({
            'message': 'Logged out successfully.'
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    """Get current user information."""
    
    return Response({
        'user': UserSerializer(request.user).data
    })


# Alias views for compatibility with Clean Architecture URLs
LogoutView = logout_view
VerifyEmailView = OTPVerifyView
VerifyPhoneView = OTPVerifyView

# Create alias for ResetPasswordView if it doesn't exist
if 'ResetPasswordView' not in globals():
    ResetPasswordView = PasswordResetView 


class GoogleLoginView(APIView):
    """Login/Register via Google ID token, then issue JWT."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data['id_token']

        try:
            payload = verify_google_id_token(token_str)
        except Exception as e:
            return Response({'error': 'Invalid Google token', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        email = payload.get('email')
        email_verified = payload.get('email_verified', False)
        name = payload.get('name') or ''
        first_name, *rest = name.split(' ', 1)
        last_name = rest[0] if rest else ''

        if not email or not email_verified:
            return Response({'error': 'Email not verified by Google'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        created = False
        if not user:
            user = User(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
            user.set_unusable_password()
            if hasattr(user, 'is_email_verified'):
                user.is_email_verified = True
            user.save()
            created = True
        else:
            updated = False
            if hasattr(user, 'is_email_verified') and not user.is_email_verified:
                user.is_email_verified = True
                updated = True
            if not user.is_active:
                user.is_active = True
                updated = True
            if updated:
                user.save()

        refresh = RefreshToken.for_user(user)
        
        # Automatically merge cart after OAuth login
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
                    
                    # Check for overbooking conflicts before merging
                    from orders.models import Order
                    overbooking_conflicts = []
                    
                    for guest_item in guest_cart.items.all():
                        # Check if user already has pending orders for this product/date/variant
                        if guest_item.product_type == 'tour':
                            schedule_id = guest_item.booking_data.get('schedule_id')
                            if schedule_id:
                                existing_pending_orders = Order.objects.filter(
                                    user=user,
                                    items__product_type='tour',
                                    items__product_id=guest_item.product_id,
                                    items__variant_id=guest_item.variant_id,
                                    items__booking_data__schedule_id=schedule_id,
                                    status='pending'
                                ).exists()
                                
                                if existing_pending_orders:
                                    overbooking_conflicts.append({
                                        'product_type': guest_item.product_type,
                                        'product_id': guest_item.product_id,
                                        'product_title': guest_item.product_title,
                                        'message': 'شما قبلاً این تور را رزرو کرده‌اید. ابتدا سفارش قبلی را تکمیل کنید.'
                                    })
                        else:
                            # For events and other products
                            existing_pending_orders = Order.objects.filter(
                                user=user,
                                items__product_type=guest_item.product_type,
                                items__product_id=guest_item.product_id,
                                items__variant_id=guest_item.variant_id,
                                items__booking_date=guest_item.booking_date,
                                status='pending'
                            ).exists()
                            
                            if existing_pending_orders:
                                overbooking_conflicts.append({
                                    'product_type': guest_item.product_type,
                                    'product_id': guest_item.product_id,
                                    'product_title': guest_item.product_title,
                                    'message': 'شما قبلاً این محصول را رزرو کرده‌اید. ابتدا سفارش قبلی را تکمیل کنید.'
                                })
                    
                    # If there are overbooking conflicts, don't merge cart
                    if overbooking_conflicts:
                        cart_message = ' Cart merge skipped due to overbooking conflicts. Please check your orders.'
                    else:
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
                        
                        cart_message = f' Cart merged with {merged_items} items.' if merged_items > 0 else ''
                    
                    # Delete guest cart
                    guest_cart.delete()
                else:
                    cart_message = ''
            else:
                cart_message = ''
        except Exception as e:
            # Don't fail the login if cart merge fails
            cart_message = ''
        
        return Response({
            'message': ('Google sign-up successful' if created else 'Google sign-in successful') + cart_message,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })