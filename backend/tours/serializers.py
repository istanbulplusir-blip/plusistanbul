"""
DRF Serializers for Tours app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    Tour, TourCategory, TourVariant, TourSchedule, 
    TourOption, TourReview, TourPricing, TourItinerary, ReviewReport, ReviewResponse, TourCancellationPolicy, TourGallery
)
from django.db.models import Avg, Sum
import copy
from django.utils import timezone
from datetime import timedelta
from .mixins import ReviewManagementMixin
from .protection import ReviewProtectionManager
from shared.serializers import ProductImageSerializer, ImageFieldSerializerMixin


class TourCategorySerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Serializer for TourCategory model."""
    
    class Meta:
        model = TourCategory
        fields = ['id', 'slug', 'name', 'description', 'icon', 'color', 'is_active']


class TourPricingSerializer(serializers.ModelSerializer):
    """Serializer for TourPricing model."""
    
    age_group_display = serializers.CharField(source='get_age_group_display', read_only=True)
    
    class Meta:
        model = TourPricing
        fields = [
            'id', 'age_group', 'age_group_display', 'factor', 'is_free', 'requires_services'
        ]


class TourGallerySerializer(serializers.ModelSerializer):
    """Serializer for tour gallery images."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TourGallery
        fields = ['id', 'image', 'image_url', 'title', 'description', 'order', 'is_active']
        read_only_fields = ['id']
    
    def get_image_url(self, obj):
        """Get the full image URL."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class TourCancellationPolicySerializer(serializers.ModelSerializer):
    """Serializer for TourCancellationPolicy model."""
    
    class Meta:
        model = TourCancellationPolicy
        fields = [
            'id', 'hours_before', 'refund_percentage', 'description', 'is_active'
        ]
        read_only_fields = ['id']


class TourVariantSerializer(serializers.ModelSerializer):
    """Serializer for TourVariant model with pricing."""
    
    pricing = serializers.SerializerMethodField()
    
    class Meta:
        model = TourVariant
        fields = [
            'id', 'name', 'description', 'base_price',
            'capacity', 'is_active', 'includes_transfer', 'includes_guide',
            'includes_meal', 'includes_photographer', 'extended_hours',
            'private_transfer', 'expert_guide', 'special_meal', 'pricing'
        ]

    def get_pricing(self, obj):
        """Get pricing for all age groups with defaults."""
        pricing_data = {}
        age_groups = ['infant', 'child', 'adult']
        
        # Get existing pricing
        for pricing in obj.pricing.filter():
            pricing_data[pricing.age_group] = {
                'factor': float(pricing.factor),
                'final_price': float(obj.base_price) * float(pricing.factor) if not pricing.is_free else 0,
                'is_free': pricing.is_free,
                'requires_services': pricing.requires_services
            }
        
        # Set defaults for missing age groups
        for age_group in age_groups:
            if age_group not in pricing_data:
                if age_group == 'infant':
                    pricing_data[age_group] = {
                        'factor': 0.0,
                        'final_price': 0.0,
                        'is_free': True,
                        'requires_services': False
                    }
                elif age_group == 'child':
                    pricing_data[age_group] = {
                        'factor': 0.5,
                        'final_price': float(obj.base_price) * 0.5,
                        'is_free': False,
                        'requires_services': True
                    }
                else:  # adult
                    pricing_data[age_group] = {
                        'factor': 1.0,
                        'final_price': float(obj.base_price),
                        'is_free': False,
                        'requires_services': True
                    }
        
        return pricing_data


class TourOptionSerializer(serializers.ModelSerializer):
    """Serializer for TourOption model."""
    
    class Meta:
        model = TourOption
        fields = [
            'id', 'name', 'description', 'price', 'price_percentage', 'currency',
            'option_type', 'is_available', 'max_quantity'
        ]
    
    def to_representation(self, instance):
        """Custom representation with calculated fields."""
        data = super().to_representation(instance)
        
        # Ensure price is always a number
        if data.get('price') is not None:
            data['price'] = float(data['price'])
        
        # Ensure price_percentage is always a number
        if data.get('price_percentage') is not None:
            data['price_percentage'] = float(data['price_percentage'])
        
        # Ensure max_quantity is always a number
        if data.get('max_quantity') is not None:
            data['max_quantity'] = int(data['max_quantity'])
        
        return data


class TourScheduleSerializer(serializers.ModelSerializer):
    """Serializer for TourSchedule model."""
    
    # Compute capacities from variant_capacities_raw to keep consistent with per-variant logic
    max_capacity = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    cutoff_datetime = serializers.SerializerMethodField()
    variant_capacities = serializers.SerializerMethodField()
    
    class Meta:
        model = TourSchedule
        fields = [
            'id', 'start_date', 'end_date', 'start_time', 'end_time',
            'is_available', 'max_capacity', 'current_capacity',
            'available_capacity', 'is_full', 'day_of_week',
            'variant_capacities', 'cutoff_datetime'
        ]
    
    def get_cutoff_datetime(self, obj):
        """Calculate booking cutoff datetime."""
        from datetime import datetime, timedelta
        tour = obj.tour
        cutoff_hours = tour.booking_cutoff_hours
        
        # Calculate cutoff time based on start date and time
        start_datetime = datetime.combine(obj.start_date, obj.start_time)
        cutoff_datetime = start_datetime - timedelta(hours=cutoff_hours)
        
        return cutoff_datetime.isoformat()
    
    def get_variant_capacities(self, obj):
        """Get variant_capacities with real-time availability using new relational model."""
        try:
            result = {}
            # Only include variants that are available for this schedule
            available_variants = obj.get_available_variants()
            
            for variant in available_variants:
                variant_id = str(variant.id)
                
                # Try to get capacity from new relational model
                try:
                    from .models import TourScheduleVariantCapacity
                    capacity_obj = TourScheduleVariantCapacity.objects.get(
                        schedule=obj, 
                        variant=variant
                    )
                    total_capacity = capacity_obj.total_capacity or variant.capacity
                    booked = (capacity_obj.reserved_capacity or 0) + (capacity_obj.confirmed_capacity or 0)
                    available = capacity_obj.available_capacity
                    
                except TourScheduleVariantCapacity.DoesNotExist:
                    # Fallback to variant default capacity
                    total_capacity = variant.capacity
                    booked = 0
                    available = total_capacity

                result[variant_id] = {
                    'total': total_capacity,
                    'booked': booked,
                    'available': available
                }

            return result
        except Exception as e:
            # Fallback to empty dict
            print(f"Serializer error: {e}")
            return {}

    def get_max_capacity(self, obj):
        try:
            return obj.compute_total_capacity()
        except Exception:
            return getattr(obj, 'max_capacity', 0)

    def get_available_capacity(self, obj):
        try:
            # Use the new property
            return obj.available_capacity
        except Exception:
            # Fallback to old method
            caps = obj.variant_capacities
            total = sum(int(v.get('total', 0) or 0) for v in caps.values())
            booked = sum(int(v.get('booked', 0) or 0) for v in caps.values())
            return max(0, total - booked)

    def get_is_full(self, obj):
        try:
            # Use the new property
            return obj.is_full
        except Exception:
            # Fallback to old method
            return self.get_available_capacity(obj) <= 0


class TourReviewSerializer(serializers.ModelSerializer):
    """Serializer for TourReview model."""
    
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TourReview
        fields = [
            'id', 'rating', 'title', 'comment', 'is_verified',
            'is_helpful', 'created_at', 'user_name', 'category', 'status'
        ]
        read_only_fields = ['id', 'is_verified', 'is_helpful', 'created_at', 'user_name', 'category', 'status']
    
    def get_user_name(self, obj):
        try:
            if obj.user.first_name and obj.user.last_name:
                return f"{obj.user.first_name} {obj.user.last_name}".strip()
            elif obj.user.first_name:
                return obj.user.first_name
            elif obj.user.last_name:
                return obj.user.last_name
            else:
                return obj.user.username
        except Exception:
            return "کاربر ناشناس"


class TourReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tour reviews."""
    
    class Meta:
        model = TourReview
        fields = ['rating', 'title', 'comment', 'category']
    
    def validate(self, attrs):
        user = self.context['request'].user
        tour = self.context['tour']
        
        # Check if user has already reviewed this tour
        if TourReview.objects.filter(user=user, tour=tour).exists():
            raise serializers.ValidationError(_('You have already reviewed this tour.'))
        
        # Validate purchase requirement
        from .validators import ReviewPurchaseValidator
        has_purchase = ReviewPurchaseValidator.validate_tour_purchase(user, tour)
        
        if not has_purchase:
            raise serializers.ValidationError(
                _('You must purchase this tour before leaving a review.')
            )
        
        # Validate content using protection system
        from .protection import ReviewProtectionManager
        protection_manager = ReviewProtectionManager()
        validation_result = protection_manager.validate_review_submission(
            user, attrs.get('comment', ''), tour, 'tour'
        )
        
        if not validation_result['valid']:
            raise serializers.ValidationError({
                'content': validation_result['issues']
            })
        
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        tour = self.context['tour']
        
        # Process submission through protection system
        from .protection import ReviewProtectionManager
        protection_manager = ReviewProtectionManager()
        process_result = protection_manager.process_review_submission(
            user, validated_data.get('comment', ''), tour, 'tour'
        )
        
        # Create the review
        review = TourReview.objects.create(
            user=user, 
            tour=tour, 
            **validated_data
        )
        
        return review


class TourListSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Serializer for tour list view."""
    
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    starting_price = serializers.SerializerMethodField()
    next_schedule_date = serializers.SerializerMethodField()
    next_schedule_capacity_total = serializers.SerializerMethodField()
    next_schedule_capacity_available = serializers.SerializerMethodField()
    has_upcoming = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    schedules = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id', 'slug', 'title', 'description', 'short_description', 'image', 'image_url', 'price', 'currency', 'duration_hours',
            'min_participants', 'max_participants', 'starting_price',
            'is_active', 'is_featured', 'is_popular', 'is_special', 'is_seasonal', 'created_at',
            'next_schedule_date', 'next_schedule_capacity_total', 'next_schedule_capacity_available', 'has_upcoming',
            'category_slug', 'category_name', 'variants', 'schedules'
        ]

    def get_title(self, obj):
        """Get translated title."""
        return obj.title if hasattr(obj, 'title') else obj.slug

    def get_description(self, obj):
        """Get translated description."""
        return obj.description if hasattr(obj, 'description') else ''

    def get_short_description(self, obj):
        """Get translated short description."""
        return obj.short_description if hasattr(obj, 'short_description') else ''

    def get_starting_price(self, obj):
        try:
            active_variants = obj.variants.filter(is_active=True)
            if active_variants.exists():
                min_price = min([v.base_price for v in active_variants if v.base_price is not None])
                return float(min_price)
        except Exception:
            pass
        # Fallback to tour.price
        try:
            return float(obj.price)
        except Exception:
            return None

    def _get_next_schedule(self, obj):
        try:
            from django.utils import timezone
            from cart.models import CartItem
            from orders.models import OrderItem
            from django.db.models import Sum
            
            today = timezone.now().date()
            qs = obj.schedules.filter(start_date__gte=today, is_available=True).order_by('start_date')
            for sched in qs:
                try:
                    # Calculate real-time capacity
                    total_capacity = sched.compute_total_capacity()
                    
                    # Count ONLY confirmed order bookings (exclude cart items and pending orders)
                    # Cart items should NOT reduce available capacity until they become confirmed orders
                    confirmed_items = OrderItem.objects.filter(
                        product_type='tour',
                        product_id=obj.id,
                        booking_date=sched.start_date,
                        order__status__in=['confirmed', 'paid', 'completed']
                    )
                    
                    total_participants = 0
                    for item in confirmed_items:
                        booking_data = item.booking_data or {}
                        participants = booking_data.get('participants', {}) or {}
                        adult_count = int(participants.get('adult', 0))
                        child_count = int(participants.get('child', 0))
                        total_participants += adult_count + child_count
                    
                    available = max(0, total_capacity - total_participants)
                    
                    # Return the first upcoming schedule, even if available == 0 (UI will show Sold out correctly)
                    return sched, total_capacity, available
                except Exception:
                    continue
        except Exception:
            pass
        return None, 0, 0

    def get_next_schedule_date(self, obj):
        sched, _, _ = self._get_next_schedule(obj)
        try:
            return sched.start_date.isoformat() if sched else None
        except Exception:
            return None

    def get_next_schedule_capacity_total(self, obj):
        sched, total, available = self._get_next_schedule(obj)
        # Return total if there is any upcoming schedule (even if available==0), else 0
        return int(total) if sched else 0

    def get_next_schedule_capacity_available(self, obj):
        sched, total, available = self._get_next_schedule(obj)
        return int(available) if sched else 0

    def get_has_upcoming(self, obj):
        sched, _, available = self._get_next_schedule(obj)
        # Has upcoming means there exists a schedule in future; 'available' guides Sold out label
        return bool(sched is not None)

    def get_category_slug(self, obj):
        try:
            return obj.category.slug if obj.category else None
        except Exception:
            return None

    def get_category_name(self, obj):
        try:
            return getattr(obj.category, 'name', '') if obj.category else ''
        except Exception:
            return ''

    def get_image_url(self, obj):
        """Get image URL with tour-specific fallback."""
        return super().get_image_url(obj, 'image', 'tour')
    
    def get_variants(self, obj):
        """Get active variants."""
        try:
            active_variants = obj.variants.filter(is_active=True)
            return [
                {
                    'id': str(variant.id),
                    'name': variant.name,
                    'description': variant.description,
                    'base_price': float(variant.base_price),
                    'capacity': variant.capacity,
                    'is_active': variant.is_active
                }
                for variant in active_variants
            ]
        except Exception:
            return []
    
    def get_schedules(self, obj):
        """Get upcoming schedules."""
        try:
            from datetime import date
            today = date.today()
            upcoming_schedules = obj.schedules.filter(
                start_date__gte=today,
                is_available=True
            ).order_by('start_date')[:5]  # Limit to 5 upcoming schedules
            
            return [
                {
                    'id': str(schedule.id),
                    'start_date': schedule.start_date.isoformat(),
                    'end_date': schedule.end_date.isoformat() if schedule.end_date else None,
                    'start_time': schedule.start_time.isoformat() if schedule.start_time else None,
                    'end_time': schedule.end_time.isoformat() if schedule.end_time else None,
                    'is_available': schedule.is_available,
                    'day_of_week': schedule.day_of_week
                }
                for schedule in upcoming_schedules
            ]
        except Exception:
            return []


class TourDetailSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Comprehensive serializer for tour detail view."""
    
    # Translatable fields as SerializerMethodField
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    highlights = serializers.SerializerMethodField()
    rules = serializers.SerializerMethodField()
    required_items = serializers.SerializerMethodField()
    
    # Related data
    variants = serializers.SerializerMethodField()
    schedules = serializers.SerializerMethodField()
    itinerary = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    category = TourCategorySerializer(read_only=True)
    cancellation_policies = serializers.SerializerMethodField()
    
    # Calculated fields
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    is_available_today = serializers.SerializerMethodField()
    pricing_summary = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    gallery_images = TourGallerySerializer(many=True, read_only=True)
    
    class Meta:
        model = Tour
        fields = [
            'id', 'slug', 'title', 'description', 'short_description',
            'highlights', 'rules', 'required_items', 'image', 'image_url', 'gallery_images',
            'price', 'currency', 'duration_hours', 'pickup_time',
            'start_time', 'end_time', 'min_participants', 'max_participants',
            'booking_cutoff_hours', 'cancellation_hours', 'refund_percentage',
            'includes_transfer', 'includes_guide', 'includes_meal',
            'includes_photographer', 'tour_type', 'transport_type',
            'is_active', 'is_featured', 'is_popular', 'is_special', 'is_seasonal', 'created_at', 'category', 'variants', 'schedules',
            'itinerary', 'options', 'reviews', 'average_rating',
            'review_count', 'is_available_today', 'pricing_summary', 'cancellation_policies'
        ]
    
    def get_title(self, obj):
        """Get translated title."""
        # Set the current language for the tour object
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
    
    def get_itinerary(self, obj):
        """Get tour itinerary items."""
        itinerary_items = TourItinerary.objects.filter(tour=obj).order_by('order')
        
        # Get current language from context
        current_language = self.context.get('request').LANGUAGE_CODE if self.context.get('request') else 'fa'
        
        result = []
        for item in itinerary_items:
            # Set the current language for this item to get proper translations
            item.set_current_language(current_language)
            
            result.append({
                'id': str(item.id),
                'title': item.title,
                'description': item.description,
                'order': item.order,
                'duration_minutes': item.duration_minutes,
                'location': item.location,
                'image': item.image.url if item.image else None
            })
        
        return result
    
    def get_average_rating(self, obj):
        """Calculate average rating from reviews."""
        avg_rating = obj.reviews.filter(is_verified=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        return float(avg_rating) if avg_rating else None
    
    def get_review_count(self, obj):
        """Get count of verified reviews."""
        return obj.reviews.filter(is_verified=True).count()
    
    def get_is_available_today(self, obj):
        """Check if tour is available today."""
        return obj.is_available_today

    def get_variants(self, obj):
        """Get only active variants."""
        active_variants = obj.variants.filter(is_active=True)
        return TourVariantSerializer(active_variants, many=True).data

    def get_options(self, obj):
        """Get only available options."""
        available_options = obj.options.filter(is_available=True)
        return TourOptionSerializer(available_options, many=True).data

    def get_reviews(self, obj):
        """Get only approved reviews."""
        approved_reviews = obj.reviews.filter(status='approved')
        return TourReviewSerializer(approved_reviews, many=True).data
    
    def get_pricing_summary(self, obj):
        summary = {}
        for variant in obj.variants.filter(is_active=True):
            variant_data = {
                'base_price': float(variant.base_price),
                'age_groups': {},
                'options': []
            }
            
            # Get pricing for each age group
            for pricing in variant.pricing.filter():
                final_price = 0
                if not pricing.is_free:
                    final_price = float(variant.base_price) * float(pricing.factor)
                
                variant_data['age_groups'][pricing.age_group] = {
                    'factor': float(pricing.factor),
                    'final_price': final_price,
                    'is_free': pricing.is_free
                }
            
            # Ensure all age groups are present with defaults
            age_groups = ['infant', 'child', 'adult']
            for age_group in age_groups:
                if age_group not in variant_data['age_groups']:
                    # Set default pricing: infant free, child 50%, adult 100%
                    if age_group == 'infant':
                        variant_data['age_groups'][age_group] = {
                            'factor': 0.0,
                            'final_price': 0.0,
                            'is_free': True
                        }
                    elif age_group == 'child':
                        variant_data['age_groups'][age_group] = {
                            'factor': 0.5,
                            'final_price': float(variant.base_price) * 0.5,
                            'is_free': False
                        }
                    else:  # adult
                        variant_data['age_groups'][age_group] = {
                            'factor': 1.0,
                            'final_price': float(variant.base_price),
                            'is_free': False
                        }
            
            # Get available options
            for option in obj.options.filter(is_available=True):
                option_data = {
                    'id': str(option.id),
                    'name': option.name,
                    'price': float(option.price),
                    'price_percentage': float(option.price_percentage),
                    'option_type': option.option_type,
                    'max_quantity': option.max_quantity
                }
                variant_data['options'].append(option_data)
            
            summary[str(variant.id)] = variant_data
        return summary
    
    def get_schedules(self, obj):
        # Use TourScheduleSerializer to serialize each schedule safely
        schedules = obj.schedules.filter(is_available=True).order_by('start_date')
        return [TourScheduleSerializer(s).data for s in schedules]

    def get_cancellation_policies(self, obj):
        """Get cancellation policies for the tour."""
        policies = TourCancellationPolicy.objects.filter(tour=obj).order_by('hours_before')
        return TourCancellationPolicySerializer(policies, many=True).data
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Patch schedules if present
        schedules = data.get('schedules')
        if isinstance(schedules, list):
            for sched in schedules:
                vc = sched.get('variant_capacities')
                if not isinstance(vc, dict):
                    sched['variant_capacities'] = {}
                else:
                    sched['variant_capacities'] = {str(k): v for k, v in vc.items()}
        return data


class TourSearchSerializer(serializers.Serializer):
    """Serializer for tour search parameters."""
    
    query = serializers.CharField(required=False, help_text=_('Search query'))
    category = serializers.UUIDField(required=False, help_text=_('Category ID'))
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        help_text=_('Minimum price')
    )
    max_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        help_text=_('Maximum price')
    )
    min_duration = serializers.IntegerField(required=False, help_text=_('Minimum duration in hours'))
    max_duration = serializers.IntegerField(required=False, help_text=_('Maximum duration in hours'))
    date_from = serializers.DateField(required=False, help_text=_('Available from date'))
    date_to = serializers.DateField(required=False, help_text=_('Available to date'))
    includes_transfer = serializers.BooleanField(required=False, help_text=_('Includes transfer'))
    includes_guide = serializers.BooleanField(required=False, help_text=_('Includes guide'))
    includes_meal = serializers.BooleanField(required=False, help_text=_('Includes meal'))
    sort_by = serializers.ChoiceField(
        choices=[
            ('price_asc', _('Price: Low to High')),
            ('price_desc', _('Price: High to Low')),
            ('duration_asc', _('Duration: Short to Long')),
            ('duration_desc', _('Duration: Long to Short')),
            ('rating_desc', _('Rating: High to Low')),
            ('created_desc', _('Newest First')),
            ('created_asc', _('Oldest First')),
        ],
        required=False,
        default='created_desc'
    )


class TourBookingSerializer(serializers.Serializer):
    """Serializer for tour booking."""
    
    tour_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False)
    schedule_id = serializers.UUIDField()
    
    # Passenger counts
    adult_count = serializers.IntegerField(min_value=0, max_value=50)
    child_count = serializers.IntegerField(min_value=0, max_value=50)
    infant_count = serializers.IntegerField(min_value=0, max_value=50)
    
    # Options and requests
    selected_options = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    special_requests = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate booking data."""
        from .models import Tour, TourVariant, TourSchedule
        
        # Validate tour exists
        try:
            tour = Tour.objects.get(id=attrs['tour_id'], is_active=True)
        except Tour.DoesNotExist:
            raise serializers.ValidationError(_('Tour not found or inactive.'))
        
        # Validate variant if provided
        if attrs.get('variant_id'):
            try:
                variant = TourVariant.objects.get(
                    id=attrs['variant_id'], 
                    tour=tour, 
                    is_active=True
                )
            except TourVariant.DoesNotExist:
                raise serializers.ValidationError(_('Tour variant not found or inactive.'))
        
        # Validate schedule
        try:
            schedule = TourSchedule.objects.get(
                id=attrs['schedule_id'],
                tour=tour,
                is_available=True
            )
        except TourSchedule.DoesNotExist:
            raise serializers.ValidationError(_('Schedule not found or unavailable.'))
        
        # Validate passenger counts
        total_passengers = (
            attrs['adult_count'] + 
            attrs['child_count'] + 
            attrs['infant_count']
        )
        
        if total_passengers == 0:
            raise serializers.ValidationError(_('At least one passenger is required.'))
        
        if total_passengers > tour.max_participants:
            raise serializers.ValidationError(
                _('Total passengers cannot exceed maximum participants.')
            )
        
        if total_passengers < tour.min_participants:
            raise serializers.ValidationError(
                _('Total passengers must meet minimum participants requirement.')
            )
        
        # Check capacity
        available_capacity = schedule.available_capacity
        if total_passengers > available_capacity:
            raise serializers.ValidationError(
                _('Not enough capacity available for selected schedule.')
            )
        
        return attrs 


class CheckTourAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking tour availability before booking."""
    
    tour_id = serializers.UUIDField()
    variant_id = serializers.UUIDField()
    schedule_id = serializers.UUIDField()
    
    participants = serializers.DictField(
        child=serializers.IntegerField(min_value=0, max_value=20)
    )
    
    def validate_participants(self, value):
        """Validate participants dictionary."""
        required_keys = {'adult', 'child', 'infant'}
        if not all(key in value for key in required_keys):
            raise serializers.ValidationError(
                f"Participants must include: {', '.join(required_keys)}"
            )
        
        total_participants = sum(value.values())
        if total_participants <= 0:
            raise serializers.ValidationError(
                "At least one participant is required"
            )
        
        if total_participants > 20:
            raise serializers.ValidationError(
                "Maximum 20 participants allowed per booking"
            )
        
        return value 


class ReviewReportSerializer(serializers.ModelSerializer):
    """Serializer for ReviewReport model."""
    
    reporter_name = serializers.CharField(source='reporter.get_full_name', read_only=True)
    review_title = serializers.CharField(source='review.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    
    class Meta:
        model = ReviewReport
        fields = [
            'id', 'review', 'reporter', 'reason', 'description', 'status',
            'reporter_name', 'review_title', 'status_display', 'reason_display',
            'created_at', 'moderated_by', 'moderated_at', 'moderation_notes',
            'action_taken'
        ]
        read_only_fields = [
            'id', 'reporter', 'status', 'created_at', 'moderated_by',
            'moderated_at', 'moderation_notes', 'action_taken'
        ]
    
    def validate(self, attrs):
        """Validate report data."""
        user = self.context['request'].user
        review = attrs.get('review')
        
        # Check if user can report this review
        mixin = ReviewManagementMixin()
        can_report = mixin.can_report_review(user, review)
        
        if not can_report['can_report']:
            raise serializers.ValidationError({
                'review': can_report['reason']
            })
        
        return attrs


class ReviewReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ReviewReport."""
    
    class Meta:
        model = ReviewReport
        fields = ['review', 'reason', 'description']
    
    def validate(self, attrs):
        """Validate report creation."""
        user = self.context['request'].user
        review = attrs.get('review')
        
        # Check if user can report this review
        mixin = ReviewManagementMixin()
        can_report = mixin.can_report_review(user, review)
        
        if not can_report['can_report']:
            raise serializers.ValidationError({
                'review': can_report['reason']
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create report with current user as reporter."""
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class ReviewReportUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ReviewReport (moderation)."""
    
    class Meta:
        model = ReviewReport
        fields = ['status', 'moderation_notes', 'action_taken']
    
    def validate(self, attrs):
        """Validate moderation update."""
        user = self.context['request'].user
        report = self.instance
        
        # Check if user can moderate this report
        mixin = ReviewManagementMixin()
        if not mixin.can_moderate_review(user, report.review):
            raise serializers.ValidationError({
                'status': 'You do not have permission to moderate this report.'
            })
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update report with moderation info."""
        if 'status' in validated_data:
            validated_data['moderated_by'] = self.context['request'].user
            validated_data['moderated_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Serializer for ReviewResponse model."""
    
    responder_name = serializers.CharField(source='responder.get_full_name', read_only=True)
    review_title = serializers.CharField(source='review.title', read_only=True)
    
    class Meta:
        model = ReviewResponse
        fields = [
            'id', 'review', 'responder', 'content', 'is_public', 'is_official',
            'responder_name', 'review_title', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'responder', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate response data."""
        user = self.context['request'].user
        review = attrs.get('review')
        
        # Check if user can respond to this review
        mixin = ReviewManagementMixin()
        can_respond = mixin.can_respond_to_review(user, review)
        
        if not can_respond['can_respond']:
            raise serializers.ValidationError({
                'review': can_respond['reason']
            })
        
        return attrs


class ReviewResponseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ReviewResponse."""
    
    class Meta:
        model = ReviewResponse
        fields = ['review', 'content', 'is_public', 'is_official']
    
    def validate(self, attrs):
        """Validate response creation."""
        user = self.context['request'].user
        review = attrs.get('review')
        
        # Check if user can respond to this review
        mixin = ReviewManagementMixin()
        can_respond = mixin.can_respond_to_review(user, review)
        
        if not can_respond['can_respond']:
            raise serializers.ValidationError({
                'review': can_respond['reason']
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create response with current user as responder."""
        validated_data['responder'] = self.context['request'].user
        return super().create(validated_data)


class ReviewResponseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ReviewResponse."""
    
    class Meta:
        model = ReviewResponse
        fields = ['content', 'is_public', 'is_official']
    
    def validate(self, attrs):
        """Validate response update."""
        user = self.context['request'].user
        response = self.instance
        
        # Check if user can edit this response
        if not response.can_be_edited_by(user):
            raise serializers.ValidationError({
                'content': 'You cannot edit this response or the editing time has expired.'
            })
        
        return attrs


class TourReviewDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for TourReview with responses and permissions."""
    
    responses = ReviewResponseSerializer(many=True, read_only=True)
    user_permissions = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    can_report = serializers.SerializerMethodField()
    can_respond = serializers.SerializerMethodField()
    
    class Meta:
        model = TourReview
        fields = [
            'id', 'user', 'tour', 'rating', 'title', 'comment', 'category',
            'status', 'is_verified', 'is_helpful', 'created_at', 'updated_at',
            'responses', 'user_permissions', 'can_edit', 'can_delete',
            'can_report', 'can_respond'
        ]
    
    def get_user_permissions(self, obj):
        """Get user permissions for this review."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return {}
        
        mixin = ReviewManagementMixin()
        return mixin.get_review_permissions(request.user, obj)
    
    def get_can_edit(self, obj):
        """Check if current user can edit this review."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        mixin = ReviewManagementMixin()
        can_edit = mixin.can_edit_review(request.user, obj)
        return can_edit['can_edit']
    
    def get_can_delete(self, obj):
        """Check if current user can delete this review."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        mixin = ReviewManagementMixin()
        can_delete = mixin.can_delete_review(request.user, obj)
        return can_delete['can_delete']
    
    def get_can_report(self, obj):
        """Check if current user can report this review."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        mixin = ReviewManagementMixin()
        can_report = mixin.can_report_review(request.user, obj)
        return can_report['can_report']
    
    def get_can_respond(self, obj):
        """Check if current user can respond to this review."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        mixin = ReviewManagementMixin()
        can_respond = mixin.can_respond_to_review(request.user, obj)
        return can_respond['can_respond'] 