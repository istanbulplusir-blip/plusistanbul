"""
Serializers for Car Rentals.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import (
    CarRentalCategory,
    CarRentalLocation,
    CarRental,
    CarRentalImage,
    CarRentalOption,
    CarRentalAvailability,
    CarRentalBooking
)
from shared.serializers import ImageFieldSerializerMixin


class CarRentalCategorySerializer(serializers.ModelSerializer):
    """Serializer for CarRentalCategory."""
    
    class Meta:
        model = CarRentalCategory
        fields = ['id', 'name', 'description', 'sort_order', 'is_active', 'slug']
    
    def get_name(self, obj):
        """Get translated name."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.name
    
    def get_description(self, obj):
        """Get translated description."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.description


class CarRentalLocationSerializer(serializers.ModelSerializer):
    """Serializer for CarRentalLocation."""
    
    class Meta:
        model = CarRentalLocation
        fields = [
            'id', 'name', 'description', 'address', 'city', 'country',
            'latitude', 'longitude', 'location_type', 'is_active', 'sort_order',
            'operating_hours_start', 'operating_hours_end', 'slug'
        ]


class CarRentalImageSerializer(serializers.ModelSerializer):
    """Serializer for CarRentalImage."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarRentalImage
        fields = ['id', 'image', 'image_url', 'caption', 'sort_order', 'is_primary']
    
    def get_image_url(self, obj):
        """Get full image URL."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CarRentalOptionSerializer(serializers.ModelSerializer):
    """Serializer for CarRentalOption."""
    
    class Meta:
        model = CarRentalOption
        fields = [
            'id', 'name', 'description', 'option_type', 'price_type', 
            'price', 'price_percentage', 'currency', 'is_active', 'max_quantity', 'slug'
        ]
    
    def get_name(self, obj):
        """Get translated name."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.name
    
    def get_description(self, obj):
        """Get translated description."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.description


class CarRentalAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for CarRentalAvailability."""
    
    available_quantity = serializers.ReadOnlyField()
    
    class Meta:
        model = CarRentalAvailability
        fields = [
            'id', 'start_date', 'end_date', 'is_available', 
            'max_quantity', 'booked_quantity', 'available_quantity',
            'price_override', 'notes'
        ]


class CarRentalListSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Serializer for CarRental list view."""
    
    category = CarRentalCategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    pricing_summary = serializers.SerializerMethodField()
    default_pickup_locations = CarRentalLocationSerializer(many=True, read_only=True)
    default_dropoff_locations = CarRentalLocationSerializer(many=True, read_only=True)
    
    class Meta:
        model = CarRental
        fields = [
            'id', 'slug', 'title', 'short_description', 'image', 'primary_image',
            'brand', 'model', 'year', 'seats', 'fuel_type', 'transmission',
            'price_per_day', 'price_per_hour', 'currency', 'city', 'country', 
            'min_rent_days', 'max_rent_days', 'allow_hourly_rental', 'min_rent_hours',
            'max_hourly_rental_hours', 'mileage_limit_per_day', 
            'advance_booking_days', 'deposit_amount', 'weekly_discount_percentage',
            'monthly_discount_percentage', 'is_featured', 'is_popular', 'is_special', 
            'is_seasonal', 'is_available', 'category', 'pricing_summary', 
            'default_pickup_locations', 'default_dropoff_locations', 
            'allow_custom_pickup_location', 'allow_custom_dropoff_location', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary image or first image."""
        primary_img = obj.images.filter(is_primary=True).first()
        if primary_img:
            return CarRentalImageSerializer(primary_img, context=self.context).data
        
        first_img = obj.images.first()
        if first_img:
            return CarRentalImageSerializer(first_img, context=self.context).data
        
        return None
    
    def get_pricing_summary(self, obj):
        """Get pricing summary with discounts."""
        return {
            'daily_rate': str(obj.price_per_day),
            'hourly_rate': str(obj.price_per_hour) if obj.price_per_hour else None,
            'weekly_discount': str(obj.weekly_discount_percentage),
            'monthly_discount': str(obj.monthly_discount_percentage),
            'currency': obj.currency
        }


class CarRentalDetailSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Serializer for CarRental detail view."""
    
    images = CarRentalImageSerializer(many=True, read_only=True)
    category = CarRentalCategorySerializer(read_only=True)
    availability = CarRentalAvailabilitySerializer(many=True, read_only=True)
    options = CarRentalOptionSerializer(many=True, read_only=True)
    default_pickup_locations = CarRentalLocationSerializer(many=True, read_only=True)
    default_dropoff_locations = CarRentalLocationSerializer(many=True, read_only=True)
    pricing_summary = serializers.SerializerMethodField()
    is_available_today = serializers.SerializerMethodField()
    
    class Meta:
        model = CarRental
        fields = [
            'id', 'slug', 'title', 'description', 'short_description', 'highlights',
            'rules', 'required_items', 'image', 'images', 'category',
            'brand', 'model', 'year', 'seats', 'fuel_type', 'transmission',
            'min_rent_days', 'max_rent_days', 'allow_hourly_rental', 'min_rent_hours',
            'max_hourly_rental_hours', 'mileage_limit_per_day', 'deposit_amount',
            'price_per_day', 'price_per_hour', 'weekly_discount_percentage',
            'monthly_discount_percentage', 'currency', 'pickup_location', 'dropoff_location',
            'pickup_instructions', 'dropoff_instructions', 'basic_insurance_included',
            'comprehensive_insurance_price', 'is_available', 'advance_booking_days',
            'agent', 'city', 'country', 'is_featured', 'is_popular', 'is_special',
            'is_seasonal', 'availability', 'options', 'default_pickup_locations',
            'default_dropoff_locations', 'allow_custom_pickup_location',
            'allow_custom_dropoff_location', 'pricing_summary', 'is_available_today',
            'created_at', 'updated_at'
        ]
    
    def get_title(self, obj):
        """Get translated title."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.title
    
    def get_description(self, obj):
        """Get translated description."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.description
    
    def get_short_description(self, obj):
        """Get translated short description."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.short_description
    
    def get_highlights(self, obj):
        """Get translated highlights."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.highlights
    
    def get_rules(self, obj):
        """Get translated rules."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.rules
    
    def get_required_items(self, obj):
        """Get translated required items."""
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        obj.set_current_language(current_language)
        return obj.required_items
    
    def get_pricing_summary(self, obj):
        """Get comprehensive pricing summary."""
        return {
            'daily_rate': str(obj.price_per_day),
            'hourly_rate': str(obj.price_per_hour) if obj.price_per_hour else None,
            'weekly_discount': str(obj.weekly_discount_percentage),
            'monthly_discount': str(obj.monthly_discount_percentage),
            'deposit_amount': str(obj.deposit_amount),
            'currency': obj.currency,
            'insurance': {
                'basic_included': obj.basic_insurance_included,
                'comprehensive_price': str(obj.comprehensive_insurance_price)
            }
        }
    
    def get_is_available_today(self, obj):
        """Check if car is available today."""
        from django.utils import timezone
        today = timezone.now().date()
        return obj.availability.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_available=True
        ).exists()


class CarRentalBookingSerializer(serializers.ModelSerializer):
    """Serializer for CarRentalBooking."""
    
    car_rental = CarRentalListSerializer(read_only=True)
    total_rental_days = serializers.ReadOnlyField()
    
    class Meta:
        model = CarRentalBooking
        fields = [
            'id', 'booking_reference', 'car_rental', 'user', 'pickup_date',
            'dropoff_date', 'pickup_time', 'dropoff_time', 'total_days',
            'total_hours', 'total_rental_days', 'daily_rate', 'hourly_rate',
            'base_price', 'options_total', 'insurance_total', 'deposit_amount',
            'total_price', 'currency', 'driver_name', 'driver_license',
            'driver_phone', 'driver_email', 'additional_drivers', 'selected_options',
            'basic_insurance', 'comprehensive_insurance', 'special_requirements',
            'status', 'created_at', 'updated_at'
        ]


class CarRentalSearchSerializer(serializers.Serializer):
    """Serializer for car rental search parameters."""
    
    query = serializers.CharField(required=False, help_text=_('Search query'))
    category = serializers.UUIDField(required=False, help_text=_('Category ID'))
    city = serializers.CharField(required=False, help_text=_('City'))
    country = serializers.CharField(required=False, help_text=_('Country'))
    brand = serializers.CharField(required=False, help_text=_('Brand'))
    fuel_type = serializers.ChoiceField(choices=CarRental.FUEL_TYPE_CHOICES, required=False)
    transmission = serializers.ChoiceField(choices=CarRental.TRANSMISSION_CHOICES, required=False)
    min_seats = serializers.IntegerField(required=False, min_value=1, help_text=_('Minimum seats'))
    max_seats = serializers.IntegerField(required=False, min_value=1, help_text=_('Maximum seats'))
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text=_('Minimum price per day'))
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text=_('Maximum price per day'))
    pickup_date = serializers.DateField(required=False, help_text=_('Pickup date'))
    dropoff_date = serializers.DateField(required=False, help_text=_('Dropoff date'))
    sort_by = serializers.ChoiceField(
        choices=[
            ('price_asc', _('Price: Low to High')),
            ('price_desc', _('Price: High to Low')),
            ('seats_asc', _('Seats: Low to High')),
            ('seats_desc', _('Seats: High to Low')),
            ('year_desc', _('Year: Newest First')),
            ('year_asc', _('Year: Oldest First')),
            ('created_desc', _('Newest First')),
            ('created_asc', _('Oldest First')),
            ('created_at_desc', _('Newest First')),
            ('created_at_asc', _('Oldest First')),
        ],
        required=False,
        default='created_desc'
    )


class CarRentalBookingCreateSerializer(serializers.Serializer):
    """Serializer for creating car rental bookings."""
    
    car_rental_id = serializers.UUIDField()
    pickup_date = serializers.DateField()
    dropoff_date = serializers.DateField()
    pickup_time = serializers.TimeField()
    dropoff_time = serializers.TimeField()
    
    # Driver information
    driver_name = serializers.CharField(max_length=255)
    driver_license = serializers.CharField(max_length=50)
    driver_phone = serializers.CharField(max_length=20)
    driver_email = serializers.EmailField()
    
    # Additional drivers
    additional_drivers = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    # Selected options
    selected_options = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    # Insurance
    basic_insurance = serializers.BooleanField(default=True)
    comprehensive_insurance = serializers.BooleanField(default=False)
    
    # Special requirements
    special_requirements = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate booking data."""
        from .models import CarRental, CarRentalAvailability
        from datetime import datetime, date
        
        # Validate car rental exists
        try:
            car_rental = CarRental.objects.get(id=attrs['car_rental_id'], is_active=True, is_available=True)
        except CarRental.DoesNotExist:
            raise serializers.ValidationError(_('Car rental not found or not available.'))
        
        # Validate dates
        pickup_date = attrs['pickup_date']
        dropoff_date = attrs['dropoff_date']
        
        if pickup_date >= dropoff_date:
            raise serializers.ValidationError(_('Pickup date must be before dropoff date.'))
        
        # Calculate rental days
        rental_days = (dropoff_date - pickup_date).days
        
        # Validate minimum rental days
        if rental_days < car_rental.min_rent_days:
            raise serializers.ValidationError(
                _('Minimum rental period is {min_days} days.').format(min_days=car_rental.min_rent_days)
            )
        
        # Validate maximum rental days
        if rental_days > car_rental.max_rent_days:
            raise serializers.ValidationError(
                _('Maximum rental period is {max_days} days.').format(max_days=car_rental.max_rent_days)
            )
        
        # Check availability - need all days in range to be available
        from datetime import timedelta

        # Check each day in the rental period
        current_date = pickup_date
        availability_records = []

        while current_date <= dropoff_date:
            day_availability = CarRentalAvailability.objects.filter(
                car_rental=car_rental,
                start_date__lte=current_date,
                end_date__gte=current_date,
                is_available=True
            ).first()

            if not day_availability or not day_availability.is_available_for_booking():
                raise serializers.ValidationError(
                    _('No availability for date {date}.').format(date=current_date)
                )

            availability_records.append(day_availability)
            current_date += timedelta(days=1)

        # Use the first availability record as representative
        availability = availability_records[0] if availability_records else None
        
        # Validate selected options
        selected_options = attrs.get('selected_options', [])
        for option_data in selected_options:
            option_id = option_data.get('id')
            quantity = option_data.get('quantity', 1)
            
            try:
                option = CarRentalOption.objects.get(id=option_id, is_active=True)
                if quantity > option.max_quantity:
                    raise serializers.ValidationError(
                        _('Maximum quantity for {option_name} is {max_qty}.').format(
                            option_name=option.name, max_qty=option.max_quantity
                        )
                    )
            except CarRentalOption.DoesNotExist:
                raise serializers.ValidationError(_('Invalid option selected.'))
        
        # Store validated data
        attrs['car_rental'] = car_rental
        attrs['availability'] = availability
        attrs['rental_days'] = rental_days
        
        return attrs


class CarRentalAvailabilityCheckSerializer(serializers.Serializer):
    """Serializer for checking car rental availability."""
    
    pickup_date = serializers.DateField()
    dropoff_date = serializers.DateField()
    pickup_time = serializers.TimeField(required=False, default='10:00')
    dropoff_time = serializers.TimeField(required=False, default='10:00')
    
    def validate(self, attrs):
        """Validate availability check data."""
        from .models import CarRental, CarRentalAvailability
        from datetime import date
        
        # Validate dates
        pickup_date = attrs['pickup_date']
        dropoff_date = attrs['dropoff_date']
        
        if pickup_date > dropoff_date:
            raise serializers.ValidationError(_('Pickup date must be before or equal to dropoff date.'))
        
        # Get car rental from context (passed from view)
        car_rental = self.context.get('car_rental')
        if not car_rental:
            raise serializers.ValidationError(_('Car rental not found.'))

        # Check availability - need all days in range to be available
        from datetime import timedelta

        # Check each day in the rental period
        current_date = pickup_date
        availability_records = []

        while current_date <= dropoff_date:
            day_availability = CarRentalAvailability.objects.filter(
                car_rental=car_rental,
                start_date__lte=current_date,
                end_date__gte=current_date,
                is_available=True
            ).first()

            if not day_availability or not day_availability.is_available_for_booking():
                raise serializers.ValidationError(
                    _('No availability for date {date}.').format(date=current_date)
                )

            availability_records.append(day_availability)
            current_date += timedelta(days=1)

        # Use the first availability record as representative
        availability = availability_records[0] if availability_records else None
        
        # Validate rental duration limits
        rental_days = (dropoff_date - pickup_date).days

        # Validate minimum rental days
        if rental_days < car_rental.min_rent_days:
            raise serializers.ValidationError(
                _('Minimum rental period is {min_days} days.').format(min_days=car_rental.min_rent_days)
            )

        # Validate maximum rental days
        if rental_days > car_rental.max_rent_days:
            raise serializers.ValidationError(
                _('Maximum rental period is {max_days} days.').format(max_days=car_rental.max_rent_days)
            )

        # Calculate rental duration
        pickup_time = attrs.get('pickup_time', '10:00')
        dropoff_time = attrs.get('dropoff_time', '10:00')

        days, hours, total_hours = car_rental.calculate_rental_duration(
            pickup_date, dropoff_date,
            pickup_time,
            dropoff_time
        )

        # Calculate pricing based on duration
        try:
            # Calculate base price (without insurance)
            base_price = car_rental.calculate_total_price(days, hours, include_insurance=False)
            # Calculate insurance price separately
            insurance_price = 0
            if car_rental.comprehensive_insurance_price > 0:
                # For hourly rentals, insurance is calculated for minimum 1 day
                insurance_days = days if days > 0 else 1
                insurance_price = car_rental.comprehensive_insurance_price * insurance_days
            
            # Total price includes base + insurance
            total_price = base_price + insurance_price
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        attrs['car_rental'] = car_rental
        attrs['availability'] = availability
        attrs['rental_days'] = days
        attrs['rental_hours'] = hours
        attrs['total_hours'] = total_hours
        attrs['total_price'] = total_price
        attrs['base_price'] = base_price
        attrs['insurance_price'] = insurance_price
        
        return attrs
