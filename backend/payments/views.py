"""
DRF Views for Payments app.
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Payment, PaymentTransaction
from .serializers import PaymentSerializer, CreatePaymentSerializer

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(user=user).order_by('-created_at')

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'payment_id'
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(user=user)

class CreatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data['order']
        user = request.user
        # Create payment
        payment = Payment.objects.create(
            order=order,
            user=user,
            amount=order.total_amount,
            currency=order.currency,
            status='pending',
            payment_method=serializer.validated_data['payment_method'],
        )
        return Response({'message': 'Payment initiated.', 'payment': PaymentSerializer(payment).data}, status=status.HTTP_201_CREATED) 