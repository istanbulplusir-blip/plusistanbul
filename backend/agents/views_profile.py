"""
Agent Profile Views for updating agent settings
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_agent_profile(request):
    """
    Update agent profile settings including preferred currency
    """
    try:
        user = request.user
        
        # Check if user is an agent
        if not hasattr(user, 'role') or user.role != 'agent':
            return Response(
                {'error': 'Only agents can update their profile'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get data from request
        data = request.data
        
        # Update allowed fields (only fields that exist in User model)
        allowed_fields = [
            'preferred_currency',
            'preferred_language', 
            'first_name',
            'last_name',
            'phone_number'
        ]
        
        updated_fields = []
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
                updated_fields.append(field)
        
        # Validate currency if provided
        if 'preferred_currency' in data:
            currency = data['preferred_currency']
            valid_currencies = ['USD', 'EUR', 'IRR', 'TRY']
            if currency not in valid_currencies:
                return Response(
                    {'error': f'Invalid currency. Must be one of: {", ".join(valid_currencies)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Save user
        user.save(update_fields=updated_fields)
        
        # Return updated agent data
        agent_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'preferred_currency': user.preferred_currency,
            'preferred_language': user.preferred_language,
            'role': user.role,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat(),
            'agent_code': user.agent_code,
            'commission_rate': float(user.commission_rate) if user.commission_rate else 0.0,
        }
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'agent': agent_data,
            'updated_fields': updated_fields
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to update profile: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_profile(request):
    """
    Get current agent profile
    """
    try:
        user = request.user
        
        # Check if user is an agent
        if not hasattr(user, 'role') or user.role != 'agent':
            return Response(
                {'error': 'Only agents can access their profile'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Return agent data
        agent_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'preferred_currency': user.preferred_currency,
            'preferred_language': user.preferred_language,
            'role': user.role,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat(),
        }
        
        return Response({
            'success': True,
            'agent': agent_data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get profile: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
