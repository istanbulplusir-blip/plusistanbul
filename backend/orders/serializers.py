"""
DRF Serializers for Orders app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_type', 'product_id', 'product_title', 'product_slug',
            'variant_id', 'variant_name', 'quantity', 'unit_price', 'total_price',
            'currency', 'options_total', 'selected_options',
            'booking_date', 'booking_time', 'booking_data',
            # Car rental specific fields
            'pickup_date', 'dropoff_date', 'pickup_time', 'dropoff_time',
            'pickup_location_type', 'pickup_location_id', 'pickup_location_custom',
            'dropoff_location_type', 'dropoff_location_id', 'dropoff_location_custom'
        ]
        read_only_fields = ['id']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'agent', 'status', 'payment_status',
            'total_amount', 'subtotal', 'service_fee_amount', 'tax_amount', 'discount_amount',
            'agent_commission_rate', 'agent_commission_amount', 'currency',
            'created_at', 'updated_at', 'items',
            'customer_name', 'customer_email', 'customer_phone',
            'billing_address', 'payment_method',
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at', 'items']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    special_requests = serializers.CharField(required=False, allow_blank=True)
    agent_id = serializers.UUIDField(required=False)
    def validate(self, attrs):
        # Validate cart exists and is not empty
        from cart.models import Cart
        try:
            cart = Cart.objects.get(id=attrs['cart_id'])
        except Cart.DoesNotExist:
            raise serializers.ValidationError(_('Cart not found.'))
        if not cart.items.exists():
            raise serializers.ValidationError(_('Cart is empty.'))
        attrs['cart'] = cart
        return attrs 