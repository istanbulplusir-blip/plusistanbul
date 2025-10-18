"""
Admin user management views for creating and managing users.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
import uuid

from .models import User, UserProfile, UserActivity
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer
)
from .admin_serializers import (
    UserAdminSerializer, UserListSerializer
)
from .serializers import UserProfileSerializer
from .permissions import IsAdminOnly, CanManageUsers
from .services import UserActivityService

User = get_user_model()


class AdminUserViewSet(ModelViewSet):
    """
    Admin ViewSet for user management.
    Only accessible by admin users.
    """
    
    queryset = User.objects.all()
    permission_classes = [IsAdminOnly]
    filterset_fields = ['role', 'is_active', 'is_email_verified', 'is_phone_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'last_login', 'email']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserAdminSerializer
    
    def get_queryset(self):
        """Filter queryset based on admin permissions."""
        queryset = super().get_queryset()
        
        # Admins can see all users
        if self.request.user.is_admin:
            return queryset
        
        # Agents can only see their customers
        if self.request.user.is_agent:
            return queryset.filter(
                Q(created_by_agent__agent=self.request.user) | 
                Q(id=self.request.user.id)
            )
        
        return queryset.none()
    
    def create(self, request, *args, **kwargs):
        """Create a new user."""
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                
                # Create user
                user = serializer.save()
                
                # Create user profile
                UserProfile.objects.create(user=user)
                
                # Log activity
                UserActivityService.log_activity(
                    user=request.user,
                    activity_type='user_creation',
                    description=f'Admin created user: {user.email}',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    metadata={'created_user_id': str(user.id), 'created_user_email': user.email}
                )
                
                return Response(
                    UserAdminSerializer(user).data,
                    status=status.HTTP_201_CREATED
                )
                
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create user: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Update user information."""
        try:
            user = self.get_object()
            old_data = {
                'role': user.role,
                'is_active': user.is_active,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_user = serializer.save()
            
            # Log activity
            changes = []
            for field, old_value in old_data.items():
                new_value = getattr(updated_user, field)
                if old_value != new_value:
                    changes.append(f'{field}: {old_value} -> {new_value}')
            
            if changes:
                UserActivityService.log_activity(
                    user=request.user,
                    activity_type='user_update',
                    description=f'Admin updated user: {updated_user.email}',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    metadata={
                        'updated_user_id': str(updated_user.id),
                        'updated_user_email': updated_user.email,
                        'changes': changes
                    }
                )
            
            return Response(UserAdminSerializer(updated_user).data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to update user: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Deactivate user instead of deleting."""
        try:
            user = self.get_object()
            
            # Don't allow admins to deactivate themselves
            if user == request.user:
                return Response(
                    {'error': 'You cannot deactivate your own account'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Deactivate instead of delete
            user.is_active = False
            user.save()
            
            # Log activity
            UserActivityService.log_activity(
                user=request.user,
                activity_type='user_deactivation',
                description=f'Admin deactivated user: {user.email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'deactivated_user_id': str(user.id), 'deactivated_user_email': user.email}
            )
            
            return Response(
                {'message': f'User {user.email} has been deactivated'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to deactivate user: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a deactivated user."""
        try:
            user = self.get_object()
            user.is_active = True
            user.save()
            
            # Log activity
            UserActivityService.log_activity(
                user=request.user,
                activity_type='user_activation',
                description=f'Admin activated user: {user.email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'activated_user_id': str(user.id), 'activated_user_email': user.email}
            )
            
            return Response(
                {'message': f'User {user.email} has been activated'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to activate user: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset user password (admin only)."""
        try:
            user = self.get_object()
            new_password = request.data.get('new_password')
            
            if not new_password:
                return Response(
                    {'error': 'New password is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(new_password)
            user.save()
            
            # Log activity
            UserActivityService.log_activity(
                user=request.user,
                activity_type='password_reset_admin',
                description=f'Admin reset password for user: {user.email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'reset_user_id': str(user.id), 'reset_user_email': user.email}
            )
            
            return Response(
                {'message': f'Password reset successfully for {user.email}'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to reset password: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def verify_email(self, request, pk=None):
        """Manually verify user email (admin only)."""
        try:
            user = self.get_object()
            user.is_email_verified = True
            user.is_active = True  # Activate user if email is verified
            user.save()
            
            # Log activity
            UserActivityService.log_activity(
                user=request.user,
                activity_type='email_verification_admin',
                description=f'Admin manually verified email for user: {user.email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'verified_user_id': str(user.id), 'verified_user_email': user.email}
            )
            
            return Response(
                {'message': f'Email verified successfully for {user.email}'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to verify email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def verify_phone(self, request, pk=None):
        """Manually verify user phone (admin only)."""
        try:
            user = self.get_object()
            user.is_phone_verified = True
            user.save()
            
            # Log activity
            UserActivityService.log_activity(
                user=request.user,
                activity_type='phone_verification_admin',
                description=f'Admin manually verified phone for user: {user.email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'verified_user_id': str(user.id), 'verified_user_email': user.email}
            )
            
            return Response(
                {'message': f'Phone verified successfully for {user.email}'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to verify phone: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminUserStatsView(APIView):
    """
    Admin view for user statistics.
    """
    
    permission_classes = [IsAdminOnly]
    
    def get(self, request):
        """Get user statistics."""
        try:
            from datetime import timedelta
            
            # Basic counts
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            verified_users = User.objects.filter(is_email_verified=True).count()
            
            # Role distribution
            role_counts = User.objects.values('role').annotate(count=Count('id'))
            
            # Recent registrations (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_registrations = User.objects.filter(created_at__gte=thirty_days_ago).count()
            
            # Recent logins (last 7 days)
            seven_days_ago = timezone.now() - timedelta(days=7)
            recent_logins = User.objects.filter(last_login__gte=seven_days_ago).count()
            
            stats = {
                'total_users': total_users,
                'active_users': active_users,
                'verified_users': verified_users,
                'role_distribution': list(role_counts),
                'recent_registrations_30d': recent_registrations,
                'recent_logins_7d': recent_logins,
                'verification_rate': round((verified_users / total_users * 100), 2) if total_users > 0 else 0,
                'activation_rate': round((active_users / total_users * 100), 2) if total_users > 0 else 0,
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get user statistics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminUserActivityView(APIView):
    """
    Admin view for user activity logs.
    """
    
    permission_classes = [IsAdminOnly]
    
    def get(self, request):
        """Get user activity logs."""
        try:
            from django.core.paginator import Paginator
            
            # Get query parameters
            user_id = request.query_params.get('user_id')
            activity_type = request.query_params.get('activity_type')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            # Build queryset
            queryset = UserActivity.objects.all()
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            if activity_type:
                queryset = queryset.filter(activity_type=activity_type)
            
            # Paginate results
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            activities = []
            for activity in page_obj:
                activities.append({
                    'id': str(activity.id),
                    'user_id': str(activity.user.id),
                    'user_email': activity.user.email,
                    'activity_type': activity.activity_type,
                    'description': activity.description,
                    'ip_address': activity.ip_address,
                    'user_agent': activity.user_agent,
                    'metadata': activity.metadata,
                    'created_at': activity.created_at.isoformat(),
                })
            
            return Response({
                'activities': activities,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get user activities: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
