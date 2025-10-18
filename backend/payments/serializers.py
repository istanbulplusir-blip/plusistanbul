"""
DRF Serializers for Payments app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Payment, PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'payment', 'transaction_type', 'amount', 'currency',
            'status', 'gateway_response', 'error_code', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'order', 'user', 'amount', 'currency',
            'status', 'payment_method', 'created_at', 'updated_at', 'transactions'
        ]
        read_only_fields = ['id', 'payment_id', 'created_at', 'updated_at', 'transactions']

class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_method = serializers.CharField()
    def validate(self, attrs):
        from orders.models import Order
        try:
            order = Order.objects.get(id=attrs['order_id'])
        except Order.DoesNotExist:
            raise serializers.ValidationError(_('Order not found.'))
        attrs['order'] = order
        return attrs 