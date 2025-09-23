"""
Agent-specific permissions
"""

from rest_framework.permissions import BasePermission


class IsAgentOnly(BasePermission):
    """
    Permission class that allows access only to authenticated agents.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'agent'
        )
