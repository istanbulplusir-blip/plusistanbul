"""
اصلاح Agent Views برای پشتیبانی از تنظیمات ارز کاربر ایجنت
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone

from .models import AgentProfile, AgentCustomer
from .services import AgentBookingService
from .pricing_service import AgentPricingService
from .serializers import AgentCustomerSerializer, AgentCustomerCreateSerializer


class AgentTransferBookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for agent transfer bookings with currency support
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculate_pricing(self, request):
        """
        Calculate transfer pricing for agent with currency conversion
        """
        try:
            agent = request.user
            data = request.data
            
            # Validate required fields
            required_fields = ['route_id', 'vehicle_type', 'passenger_count']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get route and pricing
            from transfers.models import TransferRoute, TransferRoutePricing
            try:
                route = TransferRoute.objects.get(id=data['route_id'], is_active=True)
                pricing = TransferRoutePricing.objects.get(
                    route=route,
                    vehicle_type=data['vehicle_type'],
                    is_active=True
                )
            except (TransferRoute.DoesNotExist, TransferRoutePricing.DoesNotExist):
                return Response(
                    {'error': 'Transfer route or pricing not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate pricing with agent's preferred currency
            pricing_result = AgentPricingService.calculate_transfer_price_for_agent(
                route=route,
                vehicle_type=data['vehicle_type'],
                agent=agent,
                passenger_count=data['passenger_count'],
                trip_type=data.get('trip_type', 'one_way'),
                hour=data.get('hour'),
                return_hour=data.get('return_hour'),
                selected_options=data.get('selected_options', [])
            )
            
            return Response(pricing_result)
            
        except Exception as e:
            return Response(
                {'error': f'Pricing calculation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def book_transfer(self, request):
        """
        Book transfer for customer with currency support
        """
        try:
            agent = request.user
            data = request.data
            
            # Validate required fields
            required_fields = ['customer_id', 'route_id', 'vehicle_type', 'passenger_count']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get customer
            try:
                customer = AgentCustomer.objects.get(
                    id=data['customer_id'],
                    agent=agent
                ).customer
            except AgentCustomer.DoesNotExist:
                return Response(
                    {'error': 'Customer not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Prepare booking data
            booking_data = {
                'route_id': data['route_id'],
                'vehicle_type': data['vehicle_type'],
                'passenger_count': data['passenger_count'],
                'trip_type': data.get('trip_type', 'one_way'),
                'booking_date': data.get('booking_date'),
                'booking_time': data.get('booking_time'),
                'return_date': data.get('return_date'),
                'return_time': data.get('return_time'),
                'selected_options': data.get('selected_options', []),
                'special_requests': data.get('special_requests', ''),
                'notes': data.get('notes', ''),
                'agent_currency': agent.preferred_currency  # اضافه کردن ارز ایجنت
            }
            
            # Book transfer
            with transaction.atomic():
                result = AgentBookingService.book_transfer_for_customer(
                    agent=agent,
                    customer=customer,
                    transfer_data=booking_data
                )
            
            if result['success']:
                return Response({
                    'success': True,
                    'booking_id': result['booking_id'],
                    'message': 'Transfer booked successfully',
                    'currency': agent.preferred_currency
                })
            else:
                return Response(
                    {'error': result['message']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Booking failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AgentTourBookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for agent tour bookings with currency support
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculate_pricing(self, request):
        """
        Calculate tour pricing for agent with currency conversion
        """
        try:
            agent = request.user
            data = request.data
            
            # Validate required fields
            required_fields = ['tour_id', 'variant_id', 'participants']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get tour and variant
            from tours.models import Tour, TourVariant
            try:
                tour = Tour.objects.get(id=data['tour_id'], is_active=True)
                variant = TourVariant.objects.get(id=data['variant_id'], tour=tour)
            except (Tour.DoesNotExist, TourVariant.DoesNotExist):
                return Response(
                    {'error': 'Tour or variant not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate pricing with agent's preferred currency
            pricing_result = AgentPricingService.calculate_tour_price_for_agent(
                tour=tour,
                variant=variant,
                agent=agent,
                participants=data['participants'],
                selected_options=data.get('selected_options', []),
                include_fees_taxes=data.get('include_fees_taxes', True)
            )
            
            return Response(pricing_result)
            
        except Exception as e:
            return Response(
                {'error': f'Pricing calculation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
