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
        import logging
        logger = logging.getLogger(__name__)
        
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
            logger.warning(f"Invalid or expired OTP code for {target}")
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
                
                # Upgrade guest users to customer role
                if user.role == 'guest':
                    user.role = 'customer'
                    user.save()
                    logger.info(f"Upgraded user {user.email} from 'guest' to 'customer' role via OTP login")
                
                # Merge guest cart if exists
                cart_message = self._merge_guest_cart(request, user, logger)
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'OTP verified successfully.' + cart_message,
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
            except User.DoesNotExist:
                logger.error(f"User not found with phone number: {target}")
                return Response({
                    'error': 'User not found with this phone number.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif otp_type == 'phone':
            # Mark user as verified
            if otp.user:
                otp.user.is_verified = True
                otp.user.save()
                logger.info(f"Phone verified for user: {otp.user.email}")
                return Response({
                    'message': 'Phone verified successfully.'
                })
        
        elif otp_type == 'email':
            # Mark user as verified and active
            if otp.user:
                # Set role to customer if not already set
                if otp.user.role == 'guest':
                    otp.user.role = 'customer'
                    logger.info(f"Set role='customer' for user {otp.user.email} via email verification")
                
                otp.user.is_email_verified = True
                otp.user.is_active = True  # Activate user after email verification
                otp.user.save()
                
                # Merge guest cart if exists
                cart_message = self._merge_guest_cart(request, otp.user, logger)
                
                # Generate tokens for auto-login after verification
                refresh = RefreshToken.for_user(otp.user)
                return Response({
                    'message': 'Email verified successfully.' + cart_message,
                    'user': UserSerializer(otp.user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
        
        return Response({
            'message': 'OTP verified successfully.'
        })
    
    def _merge_guest_cart(self, request, user, logger):
        """
        Merge guest cart to user cart after OTP authentication.
        Enhanced with better error handling, logging, and transaction support.
        
        Returns user-friendly message about merge result.
        """
        from django.db import transaction
        from cart.models import CartService, Cart
        from orders.models import Order
        
        try:
            session_key = request.session.session_key
            
            if not session_key:
                logger.info(f"No session key found for user {user.email}, skipping cart merge")
                return ''
            
            logger.info(f"Starting cart merge for user {user.email}, session_id={session_key}")
            
            # Check if there's a guest cart to merge
            guest_cart = Cart.objects.filter(
                session_id=session_key,
                user__isnull=True,
                is_active=True
            ).first()
            
            if not guest_cart or not guest_cart.items.exists():
                logger.info(f"No guest cart found for user {user.email}, session_id={session_key}")
                return ''
            
            guest_items_count = guest_cart.items.count()
            logger.info(f"Found guest cart with {guest_items_count} items for user {user.email}")
            
            # Use transaction to ensure atomicity
            with transaction.atomic():
                # Get or create user cart
                user_cart = CartService.get_or_create_cart(
                    session_id=session_key,
                    user=user
                )
                logger.info(f"User cart retrieved/created: cart_id={user_cart.id}")
                
                # Check for overbooking conflicts before merging
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
                                    'product_id': str(guest_item.product_id),
                                    'schedule_id': schedule_id,
                                })
                                logger.warning(f"Overbooking conflict detected for tour {guest_item.product_id}, schedule {schedule_id}")
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
                                'product_id': str(guest_item.product_id),
                                'booking_date': str(guest_item.booking_date),
                            })
                            logger.warning(f"Overbooking conflict detected for {guest_item.product_type} {guest_item.product_id}")
                
                # If there are overbooking conflicts, skip those items but merge others
                if overbooking_conflicts:
                    logger.warning(f"Found {len(overbooking_conflicts)} overbooking conflicts for user {user.email}")
                
                # Merge items (skip conflicting ones)
                merged_items = 0
                skipped_items = 0
                
                for guest_item in guest_cart.items.all():
                    # Check if this item has a conflict
                    has_conflict = False
                    if guest_item.product_type == 'tour':
                        schedule_id = guest_item.booking_data.get('schedule_id')
                        has_conflict = any(
                            c.get('product_id') == str(guest_item.product_id) and 
                            c.get('schedule_id') == schedule_id 
                            for c in overbooking_conflicts
                        )
                    else:
                        has_conflict = any(
                            c.get('product_id') == str(guest_item.product_id) and 
                            c.get('booking_date') == str(guest_item.booking_date)
                            for c in overbooking_conflicts
                        )
                    
                    if has_conflict:
                        skipped_items += 1
                        logger.info(f"Skipping conflicting item: {guest_item.product_type} {guest_item.product_id}")
                        continue
                    
                    # Check if item already exists in user cart (duplicate detection)
                    existing_item = self._find_duplicate_item(user_cart, guest_item)
                    
                    if existing_item:
                        # Merge quantities for duplicate items
                        old_quantity = existing_item.quantity
                        existing_item.quantity += guest_item.quantity
                        existing_item.save()
                        merged_items += 1
                        logger.info(f"Merged duplicate item: {guest_item.product_type} {guest_item.product_id}, quantity {old_quantity} -> {existing_item.quantity}")
                    else:
                        # Move item to user cart
                        guest_item.cart = user_cart
                        guest_item.save()
                        merged_items += 1
                        logger.info(f"Moved item to user cart: {guest_item.product_type} {guest_item.product_id}")
                
                # Only delete guest cart after successful merge
                guest_cart.delete()
                logger.info(f"Successfully merged cart for user {user.email}: {merged_items} items merged, {skipped_items} items skipped")
                
                # Build user-friendly message
                if merged_items > 0:
                    if skipped_items > 0:
                        return f' Cart merged with {merged_items} items. {skipped_items} items skipped due to conflicts.'
                    else:
                        return f' Cart merged with {merged_items} items.'
                elif skipped_items > 0:
                    return ' Cart merge skipped due to overbooking conflicts.'
                else:
                    return ''
            
        except Exception as e:
            # Don't fail the authentication if cart merge fails
            logger.error(f"Error merging guest cart for user {user.email}: {str(e)}", exc_info=True)
            return ''
    
    def _find_duplicate_item(self, cart, item):
        """
        Find duplicate item in cart based on product type and relevant identifiers.
        
        For tours: compare schedule_id from booking_data
        For other products: compare booking_date
        """
        if item.product_type == 'tour':
            # For tours, use schedule_id for accurate duplicate detection
            schedule_id = item.booking_data.get('schedule_id')
            if schedule_id:
                return cart.items.filter(
                    product_type=item.product_type,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    booking_data__schedule_id=schedule_id
                ).first()
            else:
                # Fallback to basic matching if no schedule_id
                return cart.items.filter(
                    product_type=item.product_type,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    booking_date=item.booking_date
                ).first()
        else:
            # For other products, compare booking_date and variant
            return cart.items.filter(
                product_type=item.product_type,
                product_id=item.product_id,
                variant_id=item.variant_id,
                booking_date=item.booking_date
            ).first()


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
    
    def _merge_guest_cart_google(self, request, user, logger):
        """
        Merge guest cart to user cart after Google OAuth authentication.
        
        Returns dict with:
        - message: User-friendly message about merge result
        - stats: Dictionary with merge statistics (items_merged, conflicts, etc.)
        """
        from django.db import transaction
        from cart.models import CartService, Cart
        from orders.models import Order
        
        merge_result = {
            'message': '',
            'stats': {
                'items_merged': 0,
                'conflicts': 0,
                'items_skipped': 0
            }
        }
        
        try:
            session_key = request.session.session_key
            
            if not session_key:
                logger.info(f"No session key found for user {user.email}, skipping cart merge")
                return merge_result
            
            logger.info(f"Starting cart merge for user {user.email}, session_id={session_key}")
            
            # Check if there's a guest cart to merge
            guest_cart = Cart.objects.filter(
                session_id=session_key,
                user__isnull=True,
                is_active=True
            ).first()
            
            if not guest_cart or not guest_cart.items.exists():
                logger.info(f"No guest cart found for user {user.email}, session_id={session_key}")
                return merge_result
            
            guest_items_count = guest_cart.items.count()
            logger.info(f"Found guest cart with {guest_items_count} items for user {user.email}")
            
            # Use transaction to ensure atomicity
            with transaction.atomic():
                # Get or create user cart
                user_cart = CartService.get_or_create_cart(
                    session_id=session_key,
                    user=user
                )
                logger.info(f"User cart retrieved/created: cart_id={user_cart.id}")
                
                # Check for overbooking conflicts before merging
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
                                    'product_id': str(guest_item.product_id),
                                    'schedule_id': schedule_id,
                                })
                                logger.warning(f"Overbooking conflict detected for tour {guest_item.product_id}, schedule {schedule_id}")
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
                                'product_id': str(guest_item.product_id),
                                'booking_date': str(guest_item.booking_date),
                            })
                            logger.warning(f"Overbooking conflict detected for {guest_item.product_type} {guest_item.product_id}")
                
                # If there are overbooking conflicts, skip those items but merge others
                if overbooking_conflicts:
                    merge_result['stats']['conflicts'] = len(overbooking_conflicts)
                    logger.warning(f"Found {len(overbooking_conflicts)} overbooking conflicts for user {user.email}")
                
                # Merge items (skip conflicting ones)
                merged_items = 0
                skipped_items = 0
                
                for guest_item in guest_cart.items.all():
                    # Check if this item has a conflict
                    has_conflict = False
                    if guest_item.product_type == 'tour':
                        schedule_id = guest_item.booking_data.get('schedule_id')
                        has_conflict = any(
                            c.get('product_id') == str(guest_item.product_id) and 
                            c.get('schedule_id') == schedule_id 
                            for c in overbooking_conflicts
                        )
                    else:
                        has_conflict = any(
                            c.get('product_id') == str(guest_item.product_id) and 
                            c.get('booking_date') == str(guest_item.booking_date)
                            for c in overbooking_conflicts
                        )
                    
                    if has_conflict:
                        skipped_items += 1
                        logger.info(f"Skipping conflicting item: {guest_item.product_type} {guest_item.product_id}")
                        continue
                    
                    # Check if item already exists in user cart (duplicate detection)
                    existing_item = self._find_duplicate_item(user_cart, guest_item)
                    
                    if existing_item:
                        # Merge quantities for duplicate items
                        old_quantity = existing_item.quantity
                        existing_item.quantity += guest_item.quantity
                        existing_item.save()
                        merged_items += 1
                        logger.info(f"Merged duplicate item: {guest_item.product_type} {guest_item.product_id}, quantity {old_quantity} -> {existing_item.quantity}")
                    else:
                        # Move item to user cart
                        guest_item.cart = user_cart
                        guest_item.save()
                        merged_items += 1
                        logger.info(f"Moved item to user cart: {guest_item.product_type} {guest_item.product_id}")
                
                merge_result['stats']['items_merged'] = merged_items
                merge_result['stats']['items_skipped'] = skipped_items
                
                # Only delete guest cart after successful merge
                guest_cart.delete()
                logger.info(f"Successfully merged cart for user {user.email}: {merged_items} items merged, {skipped_items} items skipped")
                
                # Build user-friendly message
                if merged_items > 0:
                    if skipped_items > 0:
                        merge_result['message'] = f' Cart merged with {merged_items} items. {skipped_items} items skipped due to conflicts.'
                    else:
                        merge_result['message'] = f' Cart merged with {merged_items} items.'
                elif skipped_items > 0:
                    merge_result['message'] = ' Cart merge skipped due to overbooking conflicts.'
                
        except Exception as e:
            # Don't fail the login if cart merge fails, but log the error
            logger.error(f"Error merging guest cart for user {user.email}: {str(e)}", exc_info=True)
            merge_result['message'] = ''
            merge_result['stats']['error'] = str(e)
        
        return merge_result
    
    def _find_duplicate_item(self, cart, item):
        """
        Find duplicate item in cart based on product type and relevant identifiers.
        
        For tours: compare schedule_id from booking_data
        For other products: compare booking_date
        """
        if item.product_type == 'tour':
            # For tours, use schedule_id for accurate duplicate detection
            schedule_id = item.booking_data.get('schedule_id')
            if schedule_id:
                return cart.items.filter(
                    product_type=item.product_type,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    booking_data__schedule_id=schedule_id
                ).first()
            else:
                # Fallback to basic matching if no schedule_id
                return cart.items.filter(
                    product_type=item.product_type,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    booking_date=item.booking_date
                ).first()
        else:
            # For other products, compare booking_date and variant
            return cart.items.filter(
                product_type=item.product_type,
                product_id=item.product_id,
                variant_id=item.variant_id,
                booking_date=item.booking_date
            ).first()

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data['id_token']

        try:
            payload = verify_google_id_token(token_str)
        except Exception as e:
            logger.error(f"Google token verification failed: {str(e)}")
            return Response({'error': 'Invalid Google token', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        email = payload.get('email')
        email_verified = payload.get('email_verified', False)
        name = payload.get('name') or ''
        first_name, *rest = name.split(' ', 1)
        last_name = rest[0] if rest else ''

        if not email or not email_verified:
            logger.warning(f"Email not verified by Google: {email}")
            return Response({'error': 'Email not verified by Google'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        created = False
        if not user:
            # Create new user with role='customer'
            user = User(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='customer',  # Set role to customer for OAuth users
                is_active=True,
            )
            user.set_unusable_password()
            if hasattr(user, 'is_email_verified'):
                user.is_email_verified = True
            user.save()
            created = True
            logger.info(f"Created new user via Google OAuth: {email} with role='customer'")
        else:
            updated = False
            # Upgrade guest users to customer role
            if user.role == 'guest':
                user.role = 'customer'
                updated = True
                logger.info(f"Upgraded user {email} from 'guest' to 'customer' role")
            if hasattr(user, 'is_email_verified') and not user.is_email_verified:
                user.is_email_verified = True
                updated = True
            if not user.is_active:
                user.is_active = True
                updated = True
            if updated:
                user.save()
                logger.info(f"Updated existing user via Google OAuth: {email}")

        refresh = RefreshToken.for_user(user)
        
        # Automatically merge cart after OAuth login with enhanced error handling
        cart_merge_result = self._merge_guest_cart_google(request, user, logger)
        cart_message = cart_merge_result.get('message', '')
        merge_stats = cart_merge_result.get('stats', {})
        
        response_data = {
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
        }
        
        # Add merge statistics if available
        if merge_stats and merge_stats.get('items_merged', 0) > 0:
            response_data['cart_merge'] = merge_stats
        
        return Response(response_data)