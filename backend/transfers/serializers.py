"""
DRF Serializers for Transfers app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import (
    TransferRoute, TransferRoutePricing, TransferOption, TransferBooking, 
    TransferCancellationPolicy, TransferLocation
)
from decimal import Decimal


class TransferLocationSerializer(serializers.ModelSerializer):
    """Serializer for TransferLocation model."""
    
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = TransferLocation
        fields = [
            'id', 'name', 'description', 'address', 'city', 'country',
            'latitude', 'longitude', 'coordinates', 'location_type', 
            'location_type_display', 'is_popular', 'is_active'
        ]
        read_only_fields = ['id']
    
    def get_coordinates(self, obj):
        """Return coordinates as a nested object."""
        return {
            'lat': float(obj.latitude),
            'lng': float(obj.longitude)
        }
    
    def to_representation(self, instance):
        """Handle null values in translatable fields."""
        data = super().to_representation(instance)
        
        # Provide fallback empty strings for translatable fields
        if data.get('name') is None:
            data['name'] = f"{instance.city}, {instance.country}"
        if data.get('description') is None:
            data['description'] = ''
        
        return data


class TransferCancellationPolicySerializer(serializers.ModelSerializer):
    """Serializer for TransferCancellationPolicy model."""
    
    class Meta:
        model = TransferCancellationPolicy
        fields = [
            'id', 'hours_before', 'refund_percentage', 'description', 'is_active'
        ]
        read_only_fields = ['id']


class TransferRoutePricingSerializer(serializers.ModelSerializer):
    """Serializer for TransferRoutePricing model."""
    
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    # Add agent currency conversion
    agent_price = serializers.SerializerMethodField()
    agent_currency = serializers.SerializerMethodField()
    
    class Meta:
        model = TransferRoutePricing
        fields = [
            'id', 'vehicle_type', 'vehicle_type_display', 'vehicle_name', 'vehicle_description',
            'base_price', 'currency', 'agent_price', 'agent_currency',
            'max_passengers', 'max_luggage', 'features', 'amenities', 'is_active'
        ]
        read_only_fields = ['id']
    
    def get_agent_price(self, obj):
        """Get price in agent's preferred currency"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'preferred_currency'):
            agent_currency = request.user.preferred_currency
            if agent_currency != obj.currency:
                # Convert currency (simplified - in real app use CurrencyConverterService)
                from shared.services import CurrencyConverterService
                try:
                    converted_price = CurrencyConverterService.convert_currency(
                        obj.base_price, obj.currency, agent_currency
                    )
                    return float(converted_price)
                except:
                    return float(obj.base_price)
        return float(obj.base_price)
    
    def get_agent_currency(self, obj):
        """Get agent's preferred currency"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'preferred_currency'):
            return request.user.preferred_currency
        return obj.currency


class TransferRouteSerializer(serializers.ModelSerializer):
    """Serializer for TransferRoute model."""
    
    pricing = TransferRoutePricingSerializer(many=True, read_only=True)
    cancellation_policies = TransferCancellationPolicySerializer(many=True, read_only=True)
    
    class Meta:
        model = TransferRoute
        fields = [
            'id', 'name', 'description', 'origin', 'destination',
            'estimated_duration_minutes',
            'peak_hour_surcharge', 'midnight_surcharge',
            'round_trip_discount_enabled', 'round_trip_discount_percentage',
            'cancellation_hours', 'refund_percentage',  # Keep for backward compatibility
            'cancellation_policies',  # New field for multiple policies
            'is_active', 'pricing', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def to_representation(self, instance):
        """Handle null values in translatable fields to prevent frontend errors."""
        data = super().to_representation(instance)
        
        # Provide fallback empty strings for translatable fields that might be null
        if data.get('name') is None:
            data['name'] = ''
        if data.get('description') is None:
            data['description'] = ''
        
        # Ensure array fields always return empty arrays instead of null
        data['pricing'] = data.get('pricing') or []
            
        return data


class TransferRouteWithPricingSerializer(serializers.ModelSerializer):
    """Serializer for TransferRoute with pricing information."""
    
    pricing = TransferRoutePricingSerializer(many=True, read_only=True)
    
    class Meta:
        model = TransferRoute
        fields = [
            'id', 'origin', 'destination', 'is_popular', 'pricing'
        ]


class TransferOptionSerializer(serializers.ModelSerializer):
    """Serializer for TransferOption model."""
    
    option_type_display = serializers.CharField(source='get_option_type_display', read_only=True)
    price_type_display = serializers.CharField(source='get_price_type_display', read_only=True)
    
    class Meta:
        model = TransferOption
        fields = [
            'id', 'name', 'description', 'option_type', 'option_type_display',
            'price_type', 'price_type_display', 'price', 'price_percentage',
            'max_quantity', 'is_active', 'created_at', 'route', 'vehicle_type'
        ]
        read_only_fields = ['id', 'created_at']
    
    def to_representation(self, instance):
        """Handle null values in translatable fields to prevent frontend errors."""
        data = super().to_representation(instance)
        
        # Provide fallback empty strings for translatable fields that might be null
        if data.get('name') is None:
            data['name'] = ''
        if data.get('description') is None:
            data['description'] = ''
            
        return data


class TransferBookingSerializer(serializers.ModelSerializer):
    """Serializer for TransferBooking model."""
    
    route = TransferRouteSerializer(read_only=True)
    pricing = TransferRoutePricingSerializer(read_only=True)
    trip_type_display = serializers.CharField(source='get_trip_type_display', read_only=True)
    
    class Meta:
        model = TransferBooking
        fields = [
            'id', 'booking_reference', 'route', 'pricing', 'trip_type',
            'trip_type_display', 'outbound_date', 'outbound_time',
            'return_date', 'return_time', 'passenger_count', 'luggage_count',
            'pickup_address', 'pickup_instructions', 'dropoff_address',
            'dropoff_instructions', 'contact_name', 'contact_phone',
            'outbound_price', 'return_price', 'round_trip_discount',
            'options_total', 'final_price', 'selected_options',
            'special_requirements', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'booking_reference', 'created_at']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Fallback for text fields that might be null
        for field in ['pickup_address', 'pickup_instructions', 'dropoff_address', 'dropoff_instructions', 'contact_name', 'contact_phone', 'special_requirements']:
            if data.get(field) is None:
                data[field] = ''
        
        # Ensure array fields always return empty arrays instead of null
        data['selected_options'] = data.get('selected_options') or []
            
        return data


class TransferSearchSerializer(serializers.Serializer):
    """Serializer for transfer search parameters."""
    
    query = serializers.CharField(required=False, allow_blank=True)
    origin = serializers.CharField(required=False, allow_blank=True)
    destination = serializers.CharField(required=False, allow_blank=True)
    vehicle_type = serializers.CharField(required=False, allow_blank=True)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    sort_by = serializers.CharField(required=False, default='date_asc')


class TransferPriceCalculationSerializer(serializers.Serializer):
    """Serializer for transfer price calculation."""
    
    route_id = serializers.UUIDField()
    vehicle_type = serializers.CharField()
    booking_time = serializers.TimeField()
    return_time = serializers.TimeField(required=False, allow_null=True)
    selected_options = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    def validate(self, attrs):
        route_id = attrs['route_id']
        vehicle_type = attrs['vehicle_type']
        
        # Validate route exists
        try:
            route = TransferRoute.objects.get(id=route_id, is_active=True)
        except TransferRoute.DoesNotExist:
            raise serializers.ValidationError(_('Route not found.'))
        
        # Validate pricing exists
        try:
            pricing = TransferRoutePricing.objects.get(
                route=route,
                vehicle_type=vehicle_type,
                is_active=True
            )
        except TransferRoutePricing.DoesNotExist:
            raise serializers.ValidationError(_('Pricing not found for this route and vehicle type.'))
        
        attrs['route'] = route
        attrs['pricing'] = pricing
        return attrs


class TransferPriceResponseSerializer(serializers.Serializer):
    """Serializer for transfer price calculation response."""
    
    price_breakdown = serializers.DictField()
    trip_info = serializers.DictField()
    route_info = serializers.DictField()
    time_info = serializers.DictField()


class TransferBookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating transfer bookings."""
    
    route_id = serializers.UUIDField(write_only=True)
    vehicle_type = serializers.CharField(write_only=True)
    
    class Meta:
        model = TransferBooking
        fields = [
            'route_id', 'vehicle_type', 'trip_type', 'outbound_date', 'outbound_time',
            'return_date', 'return_time', 'passenger_count', 'luggage_count',
            'pickup_address', 'pickup_instructions', 'dropoff_address',
            'dropoff_instructions', 'contact_name', 'contact_phone',
            'selected_options', 'special_requirements'
        ]
    
    def validate(self, attrs):
        route_id = attrs.pop('route_id')
        vehicle_type = attrs.pop('vehicle_type')
        
        # Validate route exists
        try:
            route = TransferRoute.objects.get(id=route_id, is_active=True)
        except TransferRoute.DoesNotExist:
            raise serializers.ValidationError(_('Route not found.'))
        
        # Validate pricing exists
        try:
            pricing = TransferRoutePricing.objects.get(
                route=route,
                vehicle_type=vehicle_type,
                is_active=True
            )
        except TransferRoutePricing.DoesNotExist:
            raise serializers.ValidationError(_('Pricing not found for this route and vehicle type.'))
        
        # Validate passenger count
        if attrs.get('passenger_count', 0) > pricing.max_passengers:
            raise serializers.ValidationError(
                _('Passenger count exceeds maximum capacity for this vehicle type.')
            )
        
        # Validate trip type and dates
        trip_type = attrs.get('trip_type')
        if trip_type == 'round_trip':
            if not attrs.get('return_date') or not attrs.get('return_time'):
                raise serializers.ValidationError(
                    _('Return date and time are required for round trip.')
                )
        
        attrs['route'] = route
        attrs['pricing'] = pricing

        # --- Temporal validations ---
        # Outbound must be at least now + 2 hours
        try:
            now = timezone.localtime() if timezone.is_aware(timezone.now()) else timezone.now()
        except Exception:
            now = timezone.now()
        min_outbound = now + timezone.timedelta(hours=2)
        outbound_date = attrs.get('outbound_date')
        outbound_time = attrs.get('outbound_time')
        if outbound_date and outbound_time:
            from datetime import datetime
            outbound_dt = datetime.combine(outbound_date, outbound_time)
            if outbound_dt < min_outbound.replace(tzinfo=None):
                raise serializers.ValidationError(_('Outbound date/time must be at least 2 hours from now.'))
        
        # If round trip, ensure return exists and is >= outbound + 2h and <= outbound + 12 days
        if attrs.get('trip_type') == 'round_trip':
            return_date = attrs.get('return_date')
            return_time = attrs.get('return_time')
            if not return_date or not return_time:
                raise serializers.ValidationError(_('Return date and time are required for round trip.'))
            from datetime import datetime, timedelta
            if outbound_date and outbound_time:
                outbound_dt = datetime.combine(outbound_date, outbound_time)
                return_dt = datetime.combine(return_date, return_time)
                if return_dt < outbound_dt + timedelta(hours=2):
                    raise serializers.ValidationError(_('Return must be at least 2 hours after outbound time.'))
                if return_dt > outbound_dt + timedelta(days=12):
                    raise serializers.ValidationError(_('Return date cannot be more than 12 days after outbound date.'))
        return attrs
    
    def create(self, validated_data):
        # Calculate pricing
        route = validated_data.pop('route')
        pricing = validated_data.pop('pricing')
        
        # Create booking
        booking = TransferBooking.objects.create(
            route=route,
            pricing=pricing,
            **validated_data
        )
        
        return booking


class PopularRouteSerializer(serializers.ModelSerializer):
    """Serializer for popular routes in the list page."""
    
    popular_vehicle_type = serializers.SerializerMethodField()
    base_price = serializers.SerializerMethodField()
    card_image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    route_image = serializers.SerializerMethodField()
    
    class Meta:
        model = TransferRoute
        fields = [
            'id', 'name', 'origin', 'destination', 'popular_vehicle_type',
            'base_price', 'card_image', 'route_image'
        ]
    
    def get_popular_vehicle_type(self, obj):
        """Get the most popular vehicle type for this route."""
        return obj.pricing.filter(is_active=True).first().vehicle_type if obj.pricing.exists() else None
    
    def get_base_price(self, obj):
        """Get the base price for the most popular vehicle type."""
        pricing = obj.pricing.filter(is_active=True).first()
        return pricing.base_price if pricing else None
    
    def get_card_image(self, obj):
        """Get card image for the route."""
        # For now, return None or a default image
        return None
    
    def get_name(self, obj):
        """Get route name."""
        return obj.name or f"{obj.origin} → {obj.destination}"
    
    def get_route_image(self, obj):
        """Get route image."""
        # For now, return None or a default image
        return None
    
    def to_representation(self, instance):
        """Handle null values in translatable fields to prevent frontend errors."""
        data = super().to_representation(instance)
        
        # Provide fallback empty strings for translatable fields that might be null
        if data.get('name') is None:
            data['name'] = f"{instance.origin} → {instance.destination}"
        
        # Handle nullable fields
        if data.get('card_image') is None:
            data['card_image'] = ''
        if data.get('route_image') is None:
            data['route_image'] = ''
            
        return data


class TransferRouteDetailSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for transfer route detail view with all related data."""
    
    pricing = TransferRoutePricingSerializer(many=True, read_only=True)
    options = TransferOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = TransferRoute
        fields = [
            'id', 'name', 'description', 'origin', 'destination',
            'peak_hour_surcharge', 'midnight_surcharge',
            'round_trip_discount_enabled', 'round_trip_discount_percentage',
            'cancellation_hours', 'refund_percentage',
            'is_active', 'pricing', 'options', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def to_representation(self, instance):
        """Handle null values in translatable fields to prevent frontend errors."""
        data = super().to_representation(instance)
        
        # Provide fallback empty strings for translatable fields that might be null
        if data.get('name') is None:
            data['name'] = f"{instance.origin} → {instance.destination}"
        if data.get('description') is None:
            data['description'] = ''
        
        # Ensure array fields always return empty arrays instead of null
        data['pricing'] = data.get('pricing') or []
        data['options'] = data.get('options') or []
            
        return data

