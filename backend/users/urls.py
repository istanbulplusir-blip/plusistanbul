"""
URL configuration for users app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import from Clean Architecture views
from .presentation.controllers import (
    RegisterView, LoginView, LogoutView,
    VerifyEmailView, VerifyPhoneView, 
    ForgotPasswordView, ResetPasswordView,
    ChangePasswordView, UserProfileView,
    SensitiveFieldUpdateView, SensitiveFieldVerifyView
)

# Import admin views
from .admin_views import AdminUserViewSet, AdminUserStatsView, AdminUserActivityView

# Import from DRF views (working implementation) - Keep for compatibility
from .views import (
    OTPVerifyView, PasswordResetView, PasswordResetRequestView,
    OTPRequestView, GoogleLoginView, UserProfileUpdateView
)

# API Router
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

# Authentication URLs
auth_urlpatterns = [
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Clean Architecture endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    
    # Profile management endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('profile/sensitive/request/', SensitiveFieldUpdateView.as_view(), name='sensitive_field_request'),
    path('profile/sensitive/verify/', SensitiveFieldVerifyView.as_view(), name='sensitive_field_verify'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify_phone'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/confirm/', ResetPasswordView.as_view(), name='reset_password_confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Legacy DRF endpoints (for compatibility)
    path('reset-password/', PasswordResetRequestView.as_view(), name='reset_password_request'),
    path('otp/request/', OTPRequestView.as_view(), name='otp_request'),
    
    # Social login
    path('social/google/', GoogleLoginView.as_view(), name='google_login'),
    
    # Admin endpoints
    path('admin/stats/', AdminUserStatsView.as_view(), name='admin_user_stats'),
    path('admin/activities/', AdminUserActivityView.as_view(), name='admin_user_activities'),
]

# Main URL patterns
urlpatterns = [
    # Admin API endpoints
    path('', include(router.urls)),
    
    # Authentication endpoints - Direct access without nested auth/
    path('', include(auth_urlpatterns)),
]

app_name = 'users' 