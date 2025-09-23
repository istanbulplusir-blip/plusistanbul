"""
DRF Views for Orders app.
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, OrderService
from .serializers import OrderSerializer, CreateOrderSerializer
from django.http import HttpResponse

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)

class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create order from current user's cart."""
        from cart.models import CartService
        from core.models import SystemSettings
        
        # Get system settings
        settings = SystemSettings.get_settings()
        
        # Check pending order limits
        pending_count = Order.objects.filter(
            user=request.user, 
            status='pending'
        ).count()
        
        if pending_count >= settings.order_max_pending_per_user:
            return Response({
                'error': f'You can have maximum {settings.order_max_pending_per_user} pending orders. Please complete or cancel existing orders.',
                'code': 'PENDING_ORDER_LIMIT_EXCEEDED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's cart with consistent session ID
        session_id = CartService.get_session_id(request)
        cart = CartService.get_or_create_cart(session_id=session_id, user=request.user)
        
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use OrderService to create order with transaction safety
            order = OrderService.create_order_from_cart(
                cart=cart,
                user=request.user,
                payment_data=request.data.get('payment_data'),
                agent=request.data.get('agent_id')
            )
            
            return Response({
                'message': 'Order created successfully.',
                'order_number': order.order_number,
                'order': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to create order.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 


class OrdersRootView(APIView):
    """Root view to support GET list and POST create at /api/v1/orders/."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create order from request data (new format)."""
        try:
            # Extract data from request
            customer_info = request.data.get('customer_info', {})
            items = request.data.get('items', [])
            payment_method = request.data.get('payment_method', 'credit_card')
            total_amount = request.data.get('total_amount', 0)
            currency = request.data.get('currency', 'USD')

            # Debug logging
            print("=== ORDER CREATION DEBUG ===")
            print(f"Request data keys: {list(request.data.keys())}")
            print(f"Customer info: {customer_info}")
            print(f"Items count: {len(items)}")
            print(f"Payment method: {payment_method}")
            print(f"Total amount: {total_amount}")
            print(f"Currency: {currency}")
            print(f"Subtotal from request: {request.data.get('subtotal')}")
            print(f"Tax amount from request: {request.data.get('tax_amount')}")
            print(f"Service fee amount from request: {request.data.get('service_fee_amount')}")
            print(f"Discount amount from request: {request.data.get('discount_amount')}")

            if not items:
                return Response(
                    {'error': 'No items provided.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Map order fields properly using the service
            from .services import OrderFieldMapper, OrderItemFieldMapper

            order_data = OrderFieldMapper.map_order_fields_from_request(request.data, request.user)
            print(f"Order data from OrderFieldMapper: {order_data}")

            # Check pricing fields specifically
            print(f"Pricing fields in order_data:")
            print(f"  subtotal: {order_data.get('subtotal')}")
            print(f"  service_fee_amount: {order_data.get('service_fee_amount')}")
            print(f"  tax_amount: {order_data.get('tax_amount')}")
            print(f"  total_amount: {order_data.get('total_amount')}")
            print(f"  discount_amount: {order_data.get('discount_amount')}")
            
            # Override specific fields from request
            from decimal import Decimal
            order_data.update({
                'user': request.user,  # Add user field
                'currency': currency,
                'payment_method': payment_method,
            })

            # Only set total_amount if it's not already set by OrderFieldMapper
            if 'total_amount' not in order_data or order_data['total_amount'] == 0:
                order_data['total_amount'] = Decimal(str(total_amount))
            
            # Combine address fields into billing_address
            address_parts = [
                customer_info.get('address', ''),
                customer_info.get('city', ''),
                customer_info.get('country', ''),
                customer_info.get('postal_code', '')
            ]
            order_data['billing_address'] = ', '.join(filter(None, address_parts))
            
            order = Order.objects.create(**order_data)

            # Debug logging for created order
            print(f"Order created successfully:")
            print(f"  Order number: {order.order_number}")
            print(f"  Order ID: {order.id}")
            print(f"  Final subtotal: {order.subtotal}")
            print(f"  Final service_fee_amount: {order.service_fee_amount}")
            print(f"  Final tax_amount: {order.tax_amount}")
            print(f"  Final total_amount: {order.total_amount}")
            print(f"  Final discount_amount: {order.discount_amount}")

            # Create order items using the service
            for item_data in items:
                # Map order item fields properly
                item_fields = OrderItemFieldMapper.map_order_item_fields_from_request(item_data, order)

                OrderItem.objects.create(**item_fields)
            
            return Response({
                'message': 'Order created successfully.',
                'order_number': order.order_number,
                'order': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print(f"Order creation error: {e}")
            print(traceback.format_exc())
            return Response(
                {'error': f'Failed to create order: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderActionView(APIView):
    """Handle order actions like cancel, modify, etc."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_number, action):
        """Get order information or documents."""
        try:
            order = get_object_or_404(
                Order,
                order_number=order_number,
                user=request.user
            )

            if action == 'receipt':
                return self._get_receipt(order, request)
            else:
                return Response(
                    {'error': 'Invalid action'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {'error': f'Action failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, order_number, action):
        """Perform action on order."""
        try:
            order = get_object_or_404(
                Order,
                order_number=order_number,
                user=request.user
            )

            if action == 'cancel':
                return self._cancel_order(order, request)
            elif action == 'modify':
                return self._modify_order(order, request)
            elif action == 'confirm':
                return self._confirm_order(order, request)
            else:
                return Response(
                    {'error': 'Invalid action'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {'error': f'Action failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _cancel_order(self, order, request):
        """Cancel an order."""
        reason = request.data.get('reason', 'User cancelled')
        if order.cancel_order(reason):
            return Response({
                'message': 'Order cancelled successfully.',
                'order': OrderSerializer(order).data
            })
        else:
            return Response(
                {'error': 'Order cannot be cancelled.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _modify_order(self, order, request):
        """Modify an order."""
        # Implementation for order modification
        return Response(
            {'error': 'Order modification not implemented yet.'}, 
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    def _confirm_order(self, order, request):
        """Confirm an order and reserve capacity."""
        success, message = order.confirm_order()
        if success:
            return Response({
                'message': message,
                'order': OrderSerializer(order).data
            })
        else:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _get_receipt(self, order, request):
        """Generate and return order receipt PDF."""
        try:
            from .receipt_service import ReceiptService

            # Generate PDF receipt
            pdf_data = ReceiptService.generate_receipt_pdf(order)

            # Return PDF as response
            from django.http import HttpResponse
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt_{order.order_number}.pdf"'
            return response

        except ImportError:
            # If ReceiptService doesn't exist, return JSON response
            return Response({
                'message': 'Receipt service not available',
                'order': OrderSerializer(order).data
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to generate receipt: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# New API Views for Pending Order System

class AddToOrderView(APIView):
    """Add item directly to order (pending) without cart."""
    permission_classes = [permissions.IsAuthenticated]
    
    def check_rate_limit(self, request):
        """Check rate limiting for order operations."""
        client_id = f"order_{request.user.id}"
        cache_key = f"order_rate_limit_{client_id}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= 5:  # 5 requests per 10 seconds
            return False
        
        cache.set(cache_key, current_requests + 1, 10)  # 10 seconds
        return True
    
    def check_duplicate_pending(self, user, product_type, product_id, booking_date):
        """Check for duplicate pending orders."""
        return Order.has_duplicate_pending(user, product_type, product_id, booking_date)
    
    def check_pending_limit(self, user):
        """Check if user has reached pending order limit."""
        pending_count = Order.get_pending_count_for_user(user)
        return pending_count < 3  # Maximum 3 pending orders per user
    
    def post(self, request):
        """Add item to pending order."""
        # Check rate limiting
        if not self.check_rate_limit(request):
            return Response({
                'error': 'Too many requests. Please wait before trying again.',
                'code': 'RATE_LIMIT_EXCEEDED'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Extract data from request
        product_type = request.data.get('product_type')
        product_id = request.data.get('product_id')
        booking_date = request.data.get('booking_date')
        quantity = request.data.get('quantity', 1)
        unit_price = request.data.get('unit_price', 0)
        total_price = request.data.get('total_price', 0)
        booking_data = request.data.get('booking_data', {})
        
        if not all([product_type, product_id, booking_date]):
            return Response({
                'error': 'Missing required fields: product_type, product_id, booking_date'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check duplicate pending order
        if self.check_duplicate_pending(request.user, product_type, product_id, booking_date):
            return Response({
                'error': 'You already have a pending order for this product on the selected date.',
                'code': 'DUPLICATE_PENDING'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check pending order limit
        if not self.check_pending_limit(request.user):
            return Response({
                'error': 'You have reached the maximum number of pending orders (3). Please confirm or cancel existing orders.',
                'code': 'PENDING_LIMIT_EXCEEDED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Map order fields properly using the service
                from .services import OrderFieldMapper, OrderItemFieldMapper
                
                order_data = OrderFieldMapper.map_order_fields_from_request(request.data, request.user)
                
                # Override specific fields for direct order creation
                order_data.update({
                    'currency': request.data.get('currency', 'USD'),
                    'subtotal': total_price,
                    'total_amount': total_price,
                    'payment_method': 'whatsapp',
                    'is_capacity_reserved': False,  # No capacity reserved yet
                })
                
                order = Order.objects.create(**order_data)
                
                # Create order item using the service
                item_data = {
                    'product_type': product_type,
                    'product_id': product_id,
                    'product_title': request.data.get('product_title', 'Unknown Product'),
                    'product_slug': request.data.get('product_slug', 'unknown'),
                    'booking_date': booking_date,
                    'booking_time': request.data.get('booking_time'),
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price,
                    'selected_options': request.data.get('selected_options', []),
                    'options_total': request.data.get('options_total', 0),
                    'booking_data': booking_data
                }
                
                item_fields = OrderItemFieldMapper.map_order_item_fields_from_request(item_data, order)
                OrderItem.objects.create(**item_fields)
                
                return Response({
                    'message': 'Order added successfully (pending).',
                    'order_number': order.order_number,
                    'order': OrderSerializer(order).data,
                    'note': 'Capacity will be reserved when order is confirmed.'
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': f'Failed to create pending order: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmOrderView(APIView):
    """Confirm pending order and reserve capacity."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_number):
        """Confirm a pending order."""
        try:
            order = get_object_or_404(
                Order, 
                order_number=order_number, 
                user=request.user,
                status='pending'
            )
            
            # Confirm order and reserve capacity
            success, message = order.confirm_order()
            
            if success:
                return Response({
                    'message': message,
                    'order': OrderSerializer(order).data
                })
            else:
                return Response({
                    'error': message
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Order.DoesNotExist:
            return Response({
                'error': 'Order not found or not pending.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Confirmation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelOrderView(APIView):
    """Cancel pending or confirmed order."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_number):
        """Cancel an order."""
        try:
            order = get_object_or_404(
                Order, 
                order_number=order_number, 
                user=request.user
            )
            
            reason = request.data.get('reason', 'User cancelled')
            
            if order.cancel_order(reason):
                return Response({
                    'message': 'Order cancelled successfully.',
                    'order': OrderSerializer(order).data
                })
            else:
                return Response({
                    'error': 'Order cannot be cancelled.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Order.DoesNotExist:
            return Response({
                'error': 'Order not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Cancellation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pending_orders(request):
    """Get user's pending orders."""
    try:
        pending_orders = Order.objects.filter(
            user=request.user,
            status='pending'
        ).order_by('-created_at')
        
        serializer = OrderSerializer(pending_orders, many=True)
        
        return Response({
            'pending_orders': serializer.data,
            'count': pending_orders.count(),
            'limit': 3
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to get pending orders: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_order_status_summary(request):
    """Get summary of user's orders by status."""
    try:
        user_orders = Order.objects.filter(user=request.user)
        
        summary = {
            'pending': user_orders.filter(status='pending').count(),
            'confirmed': user_orders.filter(status='confirmed').count(),
            'paid': user_orders.filter(status='paid').count(),
            'completed': user_orders.filter(status='completed').count(),
            'cancelled': user_orders.filter(status='cancelled').count(),
            'total': user_orders.count()
        }
        
        return Response(summary)
        
    except Exception as e:
        return Response({
            'error': f'Failed to get order summary: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderReceiptView(APIView):
    """Generate and download order receipt."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_number):
        """Download order receipt as PDF."""
        try:
            order = get_object_or_404(
                Order, 
                order_number=order_number, 
                user=request.user
            )
            
            # Generate PDF receipt
            from .pdf_service import pdf_generator
            
            # Add detailed error logging
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                pdf_data = pdf_generator.generate_receipt(order)
                logger.info(f"PDF generated successfully for order {order_number}")
            except Exception as pdf_error:
                logger.error(f"PDF generation failed for order {order_number}: {str(pdf_error)}")
                raise pdf_error
            
            # Create HTTP response with PDF
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt-{order.order_number}.pdf"'
            response['Content-Length'] = len(pdf_data)
            
            return response
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Receipt generation error for order {order_number}: {str(e)}")
            
            return Response(
                {'error': f'Failed to generate receipt: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderTimelineView(APIView):
    """Get order timeline/history."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_number):
        """Get order timeline."""
        try:
            order = get_object_or_404(
                Order, 
                order_number=order_number, 
                user=request.user
            )
            
            # Create basic timeline from order data
            timeline = [
                {
                    'event': 'order_created',
                    'title': 'سفارش ثبت شد',
                    'date': order.created_at,
                    'status': 'completed'
                }
            ]
            
            if order.status != 'pending':
                timeline.append({
                    'event': f'order_{order.status}',
                    'title': f'سفارش {order.status} شد',
                    'date': order.updated_at,
                    'status': 'completed'
                })
            
            return Response({
                'timeline': timeline,
                'order': OrderSerializer(order).data
            })
            
        except Exception as e:
            return Response(
                {'error': 'Failed to get order timeline'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderWhatsAppView(APIView):
    """Generate WhatsApp links for order communication."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_number):
        """Get WhatsApp links for order."""
        try:
            order = get_object_or_404(
                Order, 
                order_number=order_number, 
                user=request.user
            )
            
            from .whatsapp_service import WhatsAppService
            
            # Generate both customer and admin links
            customer_link = WhatsAppService.generate_customer_whatsapp_link(order)
            admin_link = WhatsAppService.generate_admin_whatsapp_link(order)
            support_info = WhatsAppService.get_support_info()
            
            return Response({
                'customer_whatsapp_link': customer_link,
                'admin_whatsapp_link': admin_link,
                'support_info': support_info,
                'messages': {
                    'customer': WhatsAppService.generate_customer_message(order),
                    'admin': WhatsAppService.generate_order_message(order)
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate WhatsApp links: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderInvoiceView(APIView):
    """Generate and download order invoice (فاکتور)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_number):
        try:
            order = get_object_or_404(
                Order,
                order_number=order_number,
                user=request.user
            )

            from .pdf_service import pdf_generator

            pdf_data = pdf_generator.generate_invoice(order)
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice-{order.order_number}.pdf"'
            response['Content-Length'] = len(pdf_data)
            return response
        except Exception as e:
            return Response(
                {'error': f'Failed to generate invoice: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )