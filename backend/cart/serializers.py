"""
DRF Serializers for Cart app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    
    product_title = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()
    variant_name = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    pricing_breakdown = serializers.SerializerMethodField()
    pricing_breakdown_normalized = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product_type', 'product_id', 'product_title', 'product_slug',
            'variant_name', 'quantity', 'unit_price', 'total_price',
            'currency', 'selected_options', 'booking_data', 'origin', 'destination',
            'pricing_breakdown', 'pricing_breakdown_normalized', 'created_at',
            # Car rental specific fields
            'pickup_date', 'dropoff_date', 'pickup_time', 'dropoff_time',
            'pickup_location_type', 'pickup_location_id', 'pickup_location_custom',
            'dropoff_location_type', 'dropoff_location_id', 'dropoff_location_custom'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_product_title(self, obj):
        """Get product title based on product type."""
        if obj.product_type == 'tour':
            from tours.models import Tour
            try:
                tour = Tour.objects.get(id=obj.product_id)
                return tour.title
            except Tour.DoesNotExist:
                return 'Tour not found'
        elif obj.product_type == 'event':
            from events.models import Event
            try:
                event = Event.objects.get(id=obj.product_id)
                return event.title
            except Event.DoesNotExist:
                return 'Event not found'
        elif obj.product_type == 'transfer':
            from transfers.models import TransferRoute
            try:
                transfer = TransferRoute.objects.get(id=obj.product_id)
                return transfer.name
            except TransferRoute.DoesNotExist:
                return 'Transfer route not found'
        elif obj.product_type == 'car_rental':
            from car_rentals.models import CarRental
            try:
                car_rental = CarRental.objects.get(id=obj.product_id)
                return car_rental.title
            except CarRental.DoesNotExist:
                return 'Car rental not found'
        return 'Unknown product'
    
    def get_product_slug(self, obj):
        """Get product slug based on product type."""
        if obj.product_type == 'tour':
            from tours.models import Tour
            try:
                tour = Tour.objects.get(id=obj.product_id)
                return tour.slug
            except Tour.DoesNotExist:
                return ''
        elif obj.product_type == 'event':
            from events.models import Event
            try:
                event = Event.objects.get(id=obj.product_id)
                return event.slug
            except Event.DoesNotExist:
                return ''
        elif obj.product_type == 'transfer':
            from transfers.models import TransferRoute
            try:
                transfer = TransferRoute.objects.get(id=obj.product_id)
                return transfer.id  # TransferRoute doesn't have slug, use ID
            except TransferRoute.DoesNotExist:
                return ''
        elif obj.product_type == 'car_rental':
            from car_rentals.models import CarRental
            try:
                car_rental = CarRental.objects.get(id=obj.product_id)
                return car_rental.slug
            except CarRental.DoesNotExist:
                return ''
        return ''
    
    def get_variant_name(self, obj):
        """Get variant name if exists."""
        if not obj.variant_id:
            return None
        
        if obj.product_type == 'tour':
            from tours.models import TourVariant
            try:
                variant = TourVariant.objects.get(id=obj.variant_id)
                return variant.name
            except TourVariant.DoesNotExist:
                return None
        elif obj.product_type == 'event':
            from events.models import TicketType, Event
            try:
                event = Event.objects.get(id=obj.product_id)
                variant = TicketType.objects.get(id=obj.variant_id, event=event)
                return variant.name
            except (TicketType.DoesNotExist, Event.DoesNotExist):
                return None
        elif obj.product_type == 'transfer':
            from transfers.models import TransferRoutePricing
            try:
                # For transfers, variant_id is the vehicle_type string
                pricing = TransferRoutePricing.objects.get(
                    route_id=obj.product_id,
                    vehicle_type=obj.variant_id
                )
                return pricing.vehicle_name
            except TransferRoutePricing.DoesNotExist:
                return obj.variant_id  # Fallback to vehicle type
        return None
    
    def get_total_price(self, obj):
        """Always return the stored total_price from the database for all product types."""
        return obj.total_price

    def get_origin(self, obj):
        """Get origin for transfer routes."""
        if obj.product_type == 'transfer':
            from transfers.models import TransferRoute
            try:
                transfer = TransferRoute.objects.get(id=obj.product_id)
                return transfer.origin
            except TransferRoute.DoesNotExist:
                return ''
        return ''
    
    def get_destination(self, obj):
        """Get destination for transfer routes."""
        if obj.product_type == 'transfer':
            from transfers.models import TransferRoute
            try:
                transfer = TransferRoute.objects.get(id=obj.product_id)
                return transfer.destination
            except TransferRoute.DoesNotExist:
                return ''
        return ''

    def get_pricing_breakdown(self, obj):
        """Get pricing breakdown for transfer items."""
        if obj.product_type == 'transfer':
            try:
                from transfers.models import TransferRoute, TransferRoutePricing
                from transfers.services import TransferPricingService
                from datetime import datetime
                
                route = TransferRoute.objects.get(id=obj.product_id)
                booking_data = obj.booking_data or {}
                vehicle_type = booking_data.get('vehicle_type', 'sedan')
                trip_type = booking_data.get('trip_type', 'one_way')
                
                # Get pricing
                pricing = TransferRoutePricing.objects.filter(
                    route=route,
                    vehicle_type=vehicle_type,
                    is_active=True
                ).first()
                
                if not pricing:
                    return None
                
                # Extract time from outbound_datetime
                outbound_time = None
                return_time = None
                
                if booking_data.get('outbound_datetime'):
                    try:
                        datetime_str = booking_data.get('outbound_datetime')
                        if ' ' in datetime_str:
                            outbound_time = datetime.strptime(datetime_str.split(' ')[1], '%H:%M').time()
                    except:
                        pass
                
                if booking_data.get('return_datetime'):
                    try:
                        datetime_str = booking_data.get('return_datetime')
                        if ' ' in datetime_str:
                            return_time = datetime.strptime(datetime_str.split(' ')[1], '%H:%M').time()
                    except:
                        pass
                
                # Calculate price using pricing_metadata
                price_result = pricing.calculate_price(
                    hour=outbound_time.hour if outbound_time else 12,
                    return_hour=(return_time.hour if return_time else None),
                    is_round_trip=trip_type == 'round_trip',
                    selected_options=obj.selected_options
                )
                
                return {
                    'base_price': price_result.get('base_price', 0),
                    'outbound_surcharge': price_result.get('outbound_surcharge', 0),
                    'return_surcharge': price_result.get('return_surcharge', 0),
                    'round_trip_discount': price_result.get('round_trip_discount', 0),
                    'options_total': price_result.get('options_total', 0),
                    'final_price': price_result.get('final_price', 0)
                }
                
            except Exception as e:
                print(f"Error calculating pricing breakdown: {e}")
                return None
        
        return None

    def get_pricing_breakdown_normalized(self, obj):
        """Provide a unified normalized pricing breakdown for all product types."""
        try:
            currency = obj.currency or 'USD'
            # Transfers: map detailed surcharges/discounts
            if obj.product_type == 'transfer':
                base = 0.0
                out_s = 0.0
                ret_s = 0.0
                rtd = 0.0
                options_total = float(getattr(obj, 'options_total', 0) or 0)
                final_price = float(getattr(obj, 'total_price', 0) or 0)
                pb = self.get_pricing_breakdown(obj)
                if isinstance(pb, dict):
                    base = float(pb.get('base_price') or 0)
                    out_s = float(pb.get('outbound_surcharge') or 0)
                    ret_s = float(pb.get('return_surcharge') or 0)
                    rtd = float(pb.get('round_trip_discount') or 0)
                    options_total = float(pb.get('options_total') or options_total)
                    final_price = float(pb.get('final_price') or final_price)
                subtotal = base + out_s + ret_s + options_total - rtd
                return {
                    'base_price': base,
                    'modifiers': {
                        'outbound_surcharge': out_s,
                        'return_surcharge': ret_s,
                        'round_trip_discount': rtd,
                    },
                    'options_total': options_total,
                    'fees_total': 0.0,
                    'taxes_total': 0.0,
                    'subtotal': subtotal,
                    'final_price': final_price,
                    'currency': currency,
                }
            
            # Events and Tours: best-effort normalized breakout from stored fields
            unit_price = float(getattr(obj, 'unit_price', 0) or 0)
            options_total = float(getattr(obj, 'options_total', 0) or 0)
            total_price = float(getattr(obj, 'total_price', 0) or 0)
            return {
                'base_price': unit_price,
                'modifiers': {},
                'options_total': options_total,
                'fees_total': 0.0,
                'taxes_total': 0.0,
                'subtotal': total_price,  # stored total already reflects participants/options for tours
                'final_price': total_price,
                'currency': currency,
            }
        except Exception:
            return None


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    distinct_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    fees_total = serializers.SerializerMethodField()
    tax_total = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_id', 'items', 'total_items', 'distinct_items',
            'subtotal', 'fees_total', 'tax_total', 'grand_total', 'total_price', 'currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        """Get total number of items in cart."""
        return sum(item.quantity for item in obj.items.all())
    
    def get_distinct_items(self, obj):
        """Get number of distinct cart items (each product added counts as 1)."""
        return obj.items.count()
    
    def get_subtotal(self, obj):
        """Calculate subtotal using stored total_price for each item (handles tour complex pricing)."""
        total = 0
        for item in obj.items.all():
            # Use the stored total_price from database which handles all pricing correctly
            total += item.total_price
        return total
    
    def get_total_price(self, obj):
        """Calculate total price using stored total_price for each item (handles tour complex pricing)."""
        total = 0
        for item in obj.items.all():
            # Use the stored total_price from database which handles tour age-group pricing correctly
            total += item.total_price
        return total

    def _calculate_cart_totals(self, obj):
        from .models import CartService
        return CartService.calculate_totals(obj, apply_fees=True, apply_taxes=True)

    def get_fees_total(self, obj):
        return self._calculate_cart_totals(obj)['fees_total']

    def get_tax_total(self, obj):
        return self._calculate_cart_totals(obj)['tax_total']

    def get_grand_total(self, obj):
        return self._calculate_cart_totals(obj)['grand_total']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""
    
    product_type = serializers.ChoiceField(choices=[
        ('tour', _('Tour')),
        ('event', _('Event')),
        ('transfer', _('Transfer')),
        ('car_rental', _('Car Rental')),
    ])
    product_id = serializers.UUIDField()
    variant_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    quantity = serializers.IntegerField(min_value=1, max_value=50)
    booking_date = serializers.DateField(required=False, allow_null=True)
    booking_time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    selected_options = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    booking_data = serializers.DictField(required=False)
    
    # Pricing fields for pre-calculated pricing
    pricing_breakdown = serializers.DictField(required=False, allow_null=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    
    # Car rental specific fields
    pickup_date = serializers.DateField(required=False, allow_null=True)
    dropoff_date = serializers.DateField(required=False, allow_null=True)
    pickup_time = serializers.TimeField(required=False, allow_null=True)
    dropoff_time = serializers.TimeField(required=False, allow_null=True)
    pickup_location_type = serializers.CharField(required=False, allow_blank=True)
    pickup_location_id = serializers.UUIDField(required=False, allow_null=True)
    pickup_location_custom = serializers.CharField(required=False, allow_blank=True)
    pickup_location_coordinates = serializers.DictField(required=False)
    dropoff_location_type = serializers.CharField(required=False, allow_blank=True)
    dropoff_location_id = serializers.UUIDField(required=False, allow_null=True)
    dropoff_location_custom = serializers.CharField(required=False, allow_blank=True)
    dropoff_location_coordinates = serializers.DictField(required=False)
    special_requests = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        product_type = attrs['product_type']
        product_id = attrs['product_id']
        quantity = attrs['quantity']
        variant_id = attrs.get('variant_id')
        
        # Validate variant_id for transfers
        if product_type == 'transfer' and variant_id:
            from transfers.models import TransferRoutePricing
            valid_vehicle_types = [choice[0] for choice in TransferRoutePricing.VEHICLE_CATEGORY_CHOICES]
            if variant_id not in valid_vehicle_types:
                raise serializers.ValidationError({
                    'variant_id': f'Invalid vehicle type. Must be one of: {", ".join(valid_vehicle_types)}'
                })
        
        # Validate selected_options for transfers
        if product_type == 'transfer' and attrs.get('selected_options'):
            from transfers.models import TransferOption, TransferRoute
            
            try:
                route = TransferRoute.objects.get(id=product_id)
                validated_options = []
                
                for option_data in attrs['selected_options']:
                    # Support both 'id' (from frontend) and 'option_id' (legacy)
                    option_id = option_data.get('id') or option_data.get('option_id')
                    option_name = option_data.get('option_name')
                    quantity = option_data.get('quantity', 1)
                    price = option_data.get('price', 0)
                    
                    # Try to find option by UUID first, then by option_type
                    option = None
                    if option_id:
                        try:
                            # Check if option_id is a valid UUID
                            import uuid
                            uuid.UUID(option_id)
                            option = TransferOption.objects.get(id=option_id, is_active=True)
                        except (ValueError, TransferOption.DoesNotExist):
                            # If not a valid UUID, try to find by option_type
                            if option_name:
                                option = TransferOption.objects.filter(
                                    option_type=option_name,
                                    is_active=True
                                ).first()
                    
                    if option:
                        # Get option name in English to avoid translation issues
                        try:
                            option_name = option.name
                        except:
                            # Fallback to option_type if name translation fails
                            option_name = option.option_type or 'Unknown Option'
                        
                        validated_options.append({
                            'option_id': str(option.id),
                            'option_name': option_name,
                            'option_type': option.option_type,
                            'quantity': quantity,
                            'price': float(option.calculate_price(0))  # Use option's calculated price
                        })
                    else:
                        # If option not found, keep the original data but validate it
                        validated_options.append({
                            'option_id': option_id,
                            'option_name': option_name,
                            'quantity': quantity,
                            'price': price
                        })
                
                attrs['selected_options'] = validated_options
                
            except TransferRoute.DoesNotExist:
                raise serializers.ValidationError("Transfer route not found")
        
        # Business rule for tours: infants per booking line cannot exceed 2 and do not count towards capacity
        if product_type == 'tour':
            booking_data = attrs.get('booking_data') or {}
            participants = booking_data.get('participants') or {}
            try:
                infant_count = int(participants.get('infant', 0))
            except (TypeError, ValueError):
                infant_count = 0
            if infant_count > 2:
                raise serializers.ValidationError(_('You can add at most 2 infants per tour booking.'))
        return attrs
        
        # Validate product exists
        if product_type == 'tour':
            from tours.models import Tour
            try:
                product = Tour.objects.get(id=product_id, is_active=True)
            except Tour.DoesNotExist:
                raise serializers.ValidationError(_('Tour not found.'))
        elif product_type == 'event':
            from events.models import Event
            try:
                product = Event.objects.get(id=product_id, is_active=True)
            except Event.DoesNotExist:
                raise serializers.ValidationError(_('Event not found.'))
        elif product_type == 'transfer':
            from transfers.models import TransferRoute
            try:
                product = TransferRoute.objects.get(id=product_id, is_active=True)
            except TransferRoute.DoesNotExist:
                raise serializers.ValidationError(_('Transfer route not found.'))
        
        # Validate variant if provided
        if attrs.get('variant_id'):
            variant_id = attrs['variant_id']
            if product_type == 'tour':
                from tours.models import TourVariant
                try:
                    variant = TourVariant.objects.get(id=variant_id, tour=product)
                except TourVariant.DoesNotExist:
                    raise serializers.ValidationError(_('Invalid tour variant.'))
            elif product_type == 'event':
                from events.models import TicketType
                try:
                    variant = TicketType.objects.get(id=variant_id, event=product)
                except TicketType.DoesNotExist:
                    raise serializers.ValidationError(_('Invalid ticket type.'))
            elif product_type == 'transfer':
                from transfers.models import TransferRoute
                try:
                    variant = TransferRoute.objects.get(id=variant_id)
                except TransferRoute.DoesNotExist:
                    raise serializers.ValidationError(_('Invalid vehicle type.'))
        
        # Validate options if provided
        if attrs.get('selected_options'):
            selected_options = attrs['selected_options']
            if product_type == 'tour':
                from tours.models import TourOption
                for option_data in selected_options:
                    option_id = option_data.get('option_id')
                    if option_id:
                        try:
                            option = TourOption.objects.get(id=option_id, tour=product)
                        except TourOption.DoesNotExist:
                            raise serializers.ValidationError(_('Invalid tour option.'))
            elif product_type == 'event':
                from events.models import EventOption
                for option_data in selected_options:
                    option_id = option_data.get('option_id')
                    if option_id:
                        try:
                            option = EventOption.objects.get(id=option_id, event=product)
                        except EventOption.DoesNotExist:
                            raise serializers.ValidationError(_('Invalid event option.'))
            elif product_type == 'transfer':
                from transfers.models import TransferOption
                for option_data in selected_options:
                    option_id = option_data.get('option_id')
                    if option_id:
                        try:
                            option = TransferOption.objects.get(id=option_id)
                        except TransferOption.DoesNotExist:
                            raise serializers.ValidationError(_('Invalid transfer option.'))
        
        attrs['product'] = product
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart items."""
    
    # Note: quantity is not allowed for tours - it's calculated from participants
    # For events and transfers, quantity can still be updated directly
    selected_options = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    booking_data = serializers.DictField(required=False)

    def validate_booking_data(self, value):
        # Normalize participants to ints if present
        participants = value.get('participants')
        if isinstance(participants, dict):
            normalized = {}
            for k, v in participants.items():
                try:
                    normalized[k] = int(v)
                except (TypeError, ValueError):
                    normalized[k] = 0
            value['participants'] = normalized
            # Business rule: infants per tour cart line cannot exceed 2
            infant_count = int(normalized.get('infant', 0))
            if infant_count > 2:
                raise serializers.ValidationError(_('You can add at most 2 infants per tour booking.'))
        return value


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cart items."""
    
    class Meta:
        model = CartItem
        fields = [
            'product_type', 'product_id', 'booking_date', 'booking_time',
            'variant_id', 'variant_name', 'quantity', 'unit_price', 
            'currency', 'selected_options', 'booking_data'
        ]
    
    def create(self, validated_data):
        cart = self.context['cart']
        return CartItem.objects.create(cart=cart, **validated_data) 