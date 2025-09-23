"""
Custom permission classes for role-based access control.
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAgentOrReadOnly(BasePermission):
    """
    Custom permission to only allow agents to edit, but allow read-only access to others.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to agents
        return request.user.is_authenticated and request.user.is_agent


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit, but allow read-only access to others.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admins
        return request.user.is_authenticated and request.user.is_admin


class IsAgentOrAdmin(BasePermission):
    """
    Custom permission to only allow agents and admins.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_agent or request.user.is_admin)
        )


class IsAdminOnly(BasePermission):
    """
    Custom permission to only allow admins.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsCustomerOrAgent(BasePermission):
    """
    Custom permission to allow customers and agents.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_customer or request.user.is_agent)
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin
        return obj.user == request.user or request.user.is_admin


class IsAgentCustomerOwner(BasePermission):
    """
    Custom permission to only allow agents to access their own customers.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.is_agent:
            return False
        
        # For detail views, check if the customer belongs to the agent
        if hasattr(view, 'get_object'):
            try:
                obj = view.get_object()
                if hasattr(obj, 'agent') and obj.agent == request.user:
                    return True
                elif hasattr(obj, 'created_by_agent') and request.user in obj.created_by_agent.all():
                    return True
            except:
                pass
        
        return True


class IsVerifiedUser(BasePermission):
    """
    Custom permission to only allow verified users (email or phone verified).
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_email_verified or request.user.is_phone_verified


class IsActiveUser(BasePermission):
    """
    Custom permission to only allow active users.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active


class IsNotGuest(BasePermission):
    """
    Custom permission to deny access to guest users.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_guest


class CanManageUsers(BasePermission):
    """
    Custom permission to allow user management (admin only).
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class CanCreateAgentCustomers(BasePermission):
    """
    Custom permission to allow agents to create customers.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_agent


class CanAccessAdminPanel(BasePermission):
    """
    Custom permission to allow access to admin panel (admin or agent).
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_agent)
        )
