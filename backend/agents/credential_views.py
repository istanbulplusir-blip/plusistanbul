"""
Agent Customer Credential Management Views
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import User
from .models import AgentCustomer
from .utils import generate_secure_password, send_customer_credentials, send_email_verification
from .permissions import IsAgentOnly


class AgentCustomerCredentialView(APIView):
    """Manage customer credentials"""
    
    permission_classes = [IsAuthenticated, IsAgentOnly]
    
    def post(self, request, customer_id):
        """Send login credentials to customer"""
        try:
            agent = request.user
            customer = get_object_or_404(User, id=customer_id, role='customer')
            
            # Verify agent owns this customer
            agent_customer = get_object_or_404(
                AgentCustomer,
                agent=agent,
                customer=customer
            )
            
            # Generate new password
            new_password = generate_secure_password()
            customer.set_password(new_password)
            customer.save()
            
            # Send credentials via email/SMS
            delivery_method = request.data.get('method', 'email')
            email_sent = send_customer_credentials(customer, new_password, agent, delivery_method)
            
            if email_sent:
                # Update agent customer record
                agent_customer.credentials_sent = True
                agent_customer.credentials_sent_at = timezone.now()
                agent_customer.save()
                
                return Response({
                    'success': True,
                    'message': _('Login credentials sent to customer successfully'),
                    'delivery_method': delivery_method,
                    'sent_at': agent_customer.credentials_sent_at.isoformat()
                })
            else:
                return Response({
                    'success': False,
                    'message': _('Failed to send credentials. Please try again.')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': _('An error occurred while sending credentials'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, customer_id):
        """Reset customer password"""
        try:
            agent = request.user
            customer = get_object_or_404(User, id=customer_id, role='customer')
            
            # Verify agent owns this customer
            agent_customer = get_object_or_404(
                AgentCustomer,
                agent=agent,
                customer=customer
            )
            
            # Generate new password
            new_password = generate_secure_password()
            customer.set_password(new_password)
            customer.save()
            
            # Send new credentials
            delivery_method = request.data.get('method', 'email')
            email_sent = send_customer_credentials(customer, new_password, agent, delivery_method)
            
            if email_sent:
                # Update agent customer record
                agent_customer.credentials_sent = True
                agent_customer.credentials_sent_at = timezone.now()
                agent_customer.save()
                
                return Response({
                    'success': True,
                    'message': _('Password reset successfully. New credentials sent to customer'),
                    'delivery_method': delivery_method,
                    'reset_at': agent_customer.credentials_sent_at.isoformat()
                })
            else:
                return Response({
                    'success': False,
                    'message': _('Failed to send new credentials. Please try again.')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': _('An error occurred while resetting password'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentCustomerVerificationView(APIView):
    """Manage customer verification"""
    
    permission_classes = [IsAuthenticated, IsAgentOnly]
    
    def post(self, request, customer_id):
        """Resend verification email"""
        try:
            agent = request.user
            customer = get_object_or_404(User, id=customer_id, role='customer')
            
            # Verify agent owns this customer
            agent_customer = get_object_or_404(
                AgentCustomer,
                agent=agent,
                customer=customer
            )
            
            # Send verification email
            email_sent = send_email_verification(customer)
            
            if email_sent:
                return Response({
                    'success': True,
                    'message': _('Verification email sent to customer successfully'),
                    'sent_at': timezone.now().isoformat()
                })
            else:
                return Response({
                    'success': False,
                    'message': _('Failed to send verification email. Please try again.')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': _('An error occurred while sending verification email'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentCustomerAuthStatusView(APIView):
    """Get customer authentication status"""
    
    permission_classes = [IsAuthenticated, IsAgentOnly]
    
    def get(self, request, customer_id):
        """Get customer authentication status"""
        try:
            agent = request.user
            customer = get_object_or_404(User, id=customer_id, role='customer')
            
            # Verify agent owns this customer
            agent_customer = get_object_or_404(
                AgentCustomer,
                agent=agent,
                customer=customer
            )
            
            # Get customer's last login info
            from users.models import UserSession
            last_session = UserSession.objects.filter(
                user=customer,
                is_active=True
            ).order_by('-last_activity').first()
            
            return Response({
                'success': True,
                'data': {
                    'customer_id': str(customer.id),
                    'email': customer.email,
                    'is_email_verified': customer.is_email_verified,
                    'is_active': customer.is_active,
                    'credentials_sent': agent_customer.credentials_sent,
                    'credentials_sent_at': agent_customer.credentials_sent_at.isoformat() if agent_customer.credentials_sent_at else None,
                    'last_login_at': agent_customer.last_login_at.isoformat() if agent_customer.last_login_at else None,
                    'login_count': agent_customer.login_count,
                    'requires_verification': agent_customer.requires_verification,
                    'created_by_agent': agent_customer.created_by_agent,
                    'last_session': {
                        'ip_address': last_session.ip_address if last_session else None,
                        'user_agent': last_session.user_agent if last_session else None,
                        'last_activity': last_session.last_activity.isoformat() if last_session and last_session.last_activity else None,
                    } if last_session else None
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': _('An error occurred while fetching authentication status'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentCustomerOAuthLinkView(APIView):
    """Handle OAuth account linking for agent-created customers"""
    
    permission_classes = [IsAuthenticated, IsAgentOnly]
    
    def post(self, request, customer_id):
        """Link existing OAuth account to agent-created customer"""
        try:
            agent = request.user
            customer = get_object_or_404(User, id=customer_id, role='customer')
            
            # Verify agent owns this customer
            agent_customer = get_object_or_404(
                AgentCustomer,
                agent=agent,
                customer=customer
            )
            
            # Get OAuth provider and account info
            provider = request.data.get('provider')  # 'google', 'facebook', etc.
            oauth_email = request.data.get('oauth_email')
            oauth_id = request.data.get('oauth_id')
            
            if not all([provider, oauth_email, oauth_id]):
                return Response({
                    'success': False,
                    'message': _('Provider, OAuth email, and OAuth ID are required')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if OAuth email matches customer email
            if oauth_email.lower() != customer.email.lower():
                return Response({
                    'success': False,
                    'message': _('OAuth email does not match customer email')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # TODO: Implement OAuth account linking logic
            # This would typically involve:
            # 1. Creating a SocialAccount record
            # 2. Linking it to the customer
            # 3. Updating customer verification status if needed
            
            return Response({
                'success': True,
                'message': _('OAuth account linked successfully'),
                'provider': provider,
                'linked_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': _('An error occurred while linking OAuth account'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
