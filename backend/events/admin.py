"""
Django Admin configuration for Events app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from django import forms
from parler.admin import TranslatableAdmin
from .models import (
    EventCategory, Venue, Artist, Event, TicketType, EventPerformance, Seat,
    EventOption, EventReview, EventBooking, EventSection, SectionTicketType,
    EventDiscount, EventFee, EventPricingRule, EventCancellationPolicy
)
from datetime import datetime, timedelta


# Inline classes must be defined before EventAdmin
class EventCancellationPolicyInline(admin.TabularInline):
    """Inline admin for EventCancellationPolicy."""
    
    model = EventCancellationPolicy
    extra = 1
    fields = ['hours_before', 'refund_percentage', 'description', 'is_active']
    ordering = ['-hours_before']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Set default values for new policies
        if not obj:  # Creating new event
            form.base_fields['is_active'].initial = True
        
        return formset


class TicketTypeInline(admin.TabularInline):
    """Inline admin for TicketType."""
    
    model = TicketType
    extra = 1
    fields = ['name', 'description', 'ticket_type', 'capacity', 'price_modifier', 'is_active']


class EventPerformanceInline(admin.TabularInline):
    """Inline admin for EventPerformance."""
    
    model = EventPerformance
    extra = 1
    fields = ['date', 'is_special', 'is_available']


class EventOptionInline(admin.TabularInline):
    """Inline admin for EventOption."""
    
    model = EventOption
    extra = 1
    fields = ['name', 'description', 'price', 'option_type', 'is_active']


class EventDiscountInline(admin.TabularInline):
    """Inline admin for EventDiscount."""
    
    model = EventDiscount
    extra = 1
    fields = ['code', 'name', 'discount_type', 'discount_value', 'is_active']


class EventFeeInline(admin.TabularInline):
    """Inline admin for EventFee."""
    
    model = EventFee
    extra = 1
    fields = ['name', 'fee_type', 'calculation_type', 'fee_value', 'is_active']


# Register the main Event admin
@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    """Admin for Event model."""
    
    list_display = [
        'title', 'category', 'venue', 'style', 'price', 'currency', 'is_featured',
        'is_popular', 'is_special', 'is_seasonal', 'is_active', 'booking_count'
    ]
    list_filter = [
        'category', 'venue', 'style', 'is_featured', 'is_popular',
        'is_special', 'is_seasonal', 'is_active', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'category__name', 'venue__name'
    ]
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    actions = ['create_complete_event_structure', 'create_quick_event_template']
    
    inlines = [
        TicketTypeInline, EventPerformanceInline, EventOptionInline,
        EventDiscountInline, EventFeeInline, EventCancellationPolicyInline
    ]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('id', 'title', 'description', 'short_description', 'slug')
        }),
        (_('Category & Venue'), {
            'fields': ('category', 'venue', 'artists')
        }),
        (_('Event Details'), {
            'fields': ('style', 'age_restriction')
        }),
        (_('Location'), {
            'fields': ('city', 'country', 'image')
        }),
        (_('Pricing'), {
            'fields': ('price', 'currency')
        }),
        (_('Timing'), {
            'fields': ('door_open_time', 'start_time', 'end_time')
        }),
        (_('Content'), {
            'fields': ('highlights', 'rules', 'required_items', 'gallery')
        }),
        (_('Cancellation Policy'), {
            'fields': ('cancellation_hours', 'refund_percentage')
        }),
        (_('Status'), {
            'fields': ('is_featured', 'is_popular', 'is_special', 'is_seasonal', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def create_quick_event_template(self, request, queryset):
        """Create a quick event template with standard structure."""
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # Redirect to a custom form or create template event
        messages.info(request, "Quick event template creation feature coming soon!")
        return redirect(reverse('admin:events_event_add'))
    create_quick_event_template.short_description = "Create Quick Event Template"
    
    def create_complete_event_structure(self, request, queryset):
        """Create complete event structure including performances, sections, and seats."""
        from django.contrib import messages
        from .models import EventPerformance, EventSection, SectionTicketType, Seat, TicketType
        from datetime import datetime, timedelta
        
        created_count = 0
        for event in queryset:
            # Create standard ticket types if they don't exist
            ticket_types_data = [
                {
                    'name': 'Normal',
                    'description': 'Standard ticket',
                    'ticket_type': 'normal',
                    'capacity': 1000,
                    'price_modifier': 1.0,
                    'benefits': ['Standard seating', 'Basic amenities']
                },
                {
                    'name': 'Student',
                    'description': 'Student discount ticket',
                    'ticket_type': 'student',
                    'capacity': 500,
                    'price_modifier': 0.7,
                    'benefits': ['Student discount', 'Valid student ID required']
                },
                {
                    'name': 'Wheelchair Accessible',
                    'description': 'Wheelchair accessible seating',
                    'ticket_type': 'wheelchair',
                    'capacity': 100,
                    'price_modifier': 1.0,
                    'benefits': ['Wheelchair accessible', 'Companion seat included']
                },
                {
                    'name': 'VIP',
                    'description': 'VIP premium ticket',
                    'ticket_type': 'vip',
                    'capacity': 200,
                    'price_modifier': 2.5,
                    'benefits': ['Premium seating', 'Exclusive amenities', 'Meet & greet']
                }
            ]
            
            for tt_data in ticket_types_data:
                ticket_type, created = TicketType.objects.get_or_create(
                    event=event,
                    name=tt_data['name'],
                    defaults={
                        'description': tt_data['description'],
                        'ticket_type': tt_data['ticket_type'],
                        'capacity': tt_data['capacity'],
                        'price_modifier': tt_data['price_modifier'],
                        'benefits': tt_data['benefits'],
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
            
            # Create standard performances if they don't exist
            performances_data = [
                {
                    'date': datetime.now().date() + timedelta(days=30),
                    'start_time': '19:00',
                    'end_time': '22:00',
                    'max_capacity': 1000,
                    'current_capacity': 0,
                    'is_special': False,
                    'is_available': True
                },
                {
                    'date': datetime.now().date() + timedelta(days=31),
                    'start_time': '19:00',
                    'end_time': '22:00',
                    'max_capacity': 1000,
                    'current_capacity': 0,
                    'is_special': False,
                    'is_available': True
                }
            ]
            
            for perf_data in performances_data:
                performance, created = EventPerformance.objects.get_or_create(
                    event=event,
                    date=perf_data['date'],
                    defaults={
                        'start_date': perf_data['date'],
                        'end_date': perf_data['date'],
                        'start_time': perf_data['start_time'],
                        'end_time': perf_data['end_time'],
                        'max_capacity': perf_data['max_capacity'],
                        'current_capacity': perf_data['current_capacity'],
                        'is_special': perf_data['is_special'],
                        'is_available': perf_data['is_available']
                    }
                )
                if created:
                    created_count += 1
                    
                    # Create standard sections for this performance
                    sections_data = [
                        {
                            'name': 'Eco',
                            'description': 'Economy section with basic amenities',
                            'total_capacity': 300,
                            'base_price': event.price * 0.6,
                            'is_premium': False,
                            'is_wheelchair_accessible': False
                        },
                        {
                            'name': 'Normal',
                            'description': 'Standard section with good view',
                            'total_capacity': 400,
                            'base_price': event.price,
                            'is_premium': False,
                            'is_wheelchair_accessible': True
                        },
                        {
                            'name': 'VIP',
                            'description': 'Premium VIP section with exclusive amenities',
                            'total_capacity': 300,
                            'base_price': event.price * 1.8,
                            'is_premium': True,
                            'is_wheelchair_accessible': True
                        }
                    ]
                    
                    for section_data in sections_data:
                        section, created = EventSection.objects.get_or_create(
                            performance=performance,
                            name=section_data['name'],
                            defaults={
                                'description': section_data['description'],
                                'total_capacity': section_data['total_capacity'],
                                'base_price': section_data['base_price'],
                                'currency': event.currency,
                                'is_premium': section_data['is_premium'],
                                'is_wheelchair_accessible': section_data['is_wheelchair_accessible']
                            }
                        )
                        if created:
                            created_count += 1
                            
                            # Create SectionTicketTypes for this section
                            ticket_types = TicketType.objects.filter(event=event)
                            for ticket_type in ticket_types:
                                # Calculate capacity per ticket type
                                capacity_per_type = section.total_capacity // len(ticket_types)
                                
                                SectionTicketType.objects.get_or_create(
                                    section=section,
                                    ticket_type=ticket_type,
                                    defaults={
                                        'allocated_capacity': capacity_per_type,
                                        'available_capacity': capacity_per_type,
                                        'reserved_capacity': 0,
                                        'sold_capacity': 0,
                                        'price_modifier': ticket_type.price_modifier
                                    }
                                )
                            
                            # Create seats for this section
                            section_tickets = section.ticket_types.all()
                            seat_number = 1
                            for stt in section_tickets:
                                for i in range(stt.allocated_capacity):
                                    seat, created = Seat.objects.get_or_create(
                                        performance=performance,
                                        section=section.name,
                                        row_number=1,
                                        seat_number=seat_number,
                                        defaults={
                                            'ticket_type': stt.ticket_type,
                                            'status': 'available',
                                            'price': section.base_price * stt.price_modifier,
                                            'currency': event.currency,
                                            'is_premium': section.is_premium,
                                            'is_wheelchair_accessible': (
                                                section.is_wheelchair_accessible and 
                                                stt.ticket_type.name == 'Wheelchair Accessible'
                                            )
                                        }
                                    )
                                    if created:
                                        created_count += 1
                                    seat_number += 1
        
        messages.success(request, f'Successfully created complete event structure with {created_count} objects.')
    create_complete_event_structure.short_description = "Create Complete Event Structure (Performances, Sections, Seats)"
    
    def booking_count(self, obj):
        """Get number of bookings for this event."""
        try:
            return obj.bookings.count()
        except:
            return 0
    booking_count.short_description = _('Bookings')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('category', 'venue').prefetch_related('artists')


@admin.register(EventCategory)
class EventCategoryAdmin(TranslatableAdmin):
    """Admin for EventCategory model."""
    
    list_display = ['name', 'icon', 'color', 'event_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'slug')
        }),
        (_('Styling'), {
            'fields': ('icon', 'color')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def event_count(self, obj):
        """Get number of events in this category."""
        try:
            return obj.events.count()
        except:
            return 0
    event_count.short_description = _('Event Count')


@admin.register(Venue)
class VenueAdmin(TranslatableAdmin):
    """Admin for Venue model."""
    
    list_display = [
        'name', 'city', 'country', 'total_capacity', 'event_count', 'is_active'
    ]
    list_filter = ['country', 'city', 'is_active']
    search_fields = ['name', 'description', 'address', 'city', 'country']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'slug')
        }),
        (_('Location'), {
            'fields': ('city', 'country', 'address', 'coordinates')
        }),
        (_('Details'), {
            'fields': ('image', 'website', 'total_capacity', 'facilities')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def event_count(self, obj):
        """Get number of events at this venue."""
        try:
            return obj.events.count()
        except:
            return 0
    event_count.short_description = _('Event Count')


@admin.register(Artist)
class ArtistAdmin(TranslatableAdmin):
    """Admin for Artist model."""
    
    list_display = ['name', 'event_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'bio']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'bio', 'slug')
        }),
        (_('Details'), {
            'fields': ('image', 'website', 'social_media')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def event_count(self, obj):
        """Get number of events for this artist."""
        try:
            return obj.events.count()
        except:
            return 0
    event_count.short_description = _('Event Count')


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    """Admin for TicketType model."""
    
    list_display = [
        'name', 'event', 'ticket_type', 'capacity', 'price_modifier', 
        'is_active', 'booking_count'
    ]
    list_filter = [
        'event__category', 'ticket_type', 'is_active'
    ]
    search_fields = [
        'name', 'description', 'event__title'
    ]
    ordering = ['event', 'name']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('event', 'name', 'description', 'ticket_type')
        }),
        (_('Pricing & Capacity'), {
            'fields': ('capacity', 'price_modifier')
        }),
        (_('Benefits'), {
            'fields': ('benefits',)
        }),
        (_('Restrictions'), {
            'fields': ('age_min', 'age_max')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def booking_count(self, obj):
        """Get number of bookings for this ticket type."""
        try:
            return obj.seats.filter(status='sold').count()
        except:
            return 0
    booking_count.short_description = _('Bookings')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('event')


@admin.register(EventPerformance)
class EventPerformanceAdmin(admin.ModelAdmin):
    """Admin for EventPerformance model."""
    
    list_display = [
        'event', 'date', 'start_time', 'end_time', 'is_special', 'is_available', 
        'max_capacity', 'current_capacity', 'available_capacity', 'booking_count'
    ]
    list_filter = [
        'event__category', 'is_special', 'is_available', 'date'
    ]
    search_fields = [
        'event__title', 'event__venue__name'
    ]
    ordering = ['event', 'date']
    actions = ['create_standard_sections', 'create_standard_seats']
    
    fieldsets = (
        (_('Performance Information'), {
            'fields': ('event', 'date', 'is_special')
        }),
        (_('Timing'), {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time')
        }),
        (_('Capacity'), {
            'fields': ('max_capacity', 'current_capacity')
        }),
        (_('Status'), {
            'fields': ('is_available',)
        }),
    )
    
    def create_standard_sections(self, request, queryset):
        """Create standard sections (Eco, Normal, VIP) for selected performances."""
        from django.contrib import messages
        from .models import EventSection, SectionTicketType, TicketType
        
        created_count = 0
        for performance in queryset:
            # Create standard sections
            sections_data = [
                {
                    'name': 'Eco',
                    'description': 'Economy section with basic amenities',
                    'total_capacity': 50,
                    'base_price': 10.00,
                    'is_premium': False,
                    'is_wheelchair_accessible': False
                },
                {
                    'name': 'Normal',
                    'description': 'Standard section with good view',
                    'total_capacity': 100,
                    'base_price': 15.00,
                    'is_premium': False,
                    'is_wheelchair_accessible': True
                },
                {
                    'name': 'VIP',
                    'description': 'Premium VIP section with exclusive amenities',
                    'total_capacity': 30,
                    'base_price': 25.00,
                    'is_premium': True,
                    'is_wheelchair_accessible': True
                }
            ]
            
            for section_data in sections_data:
                section, created = EventSection.objects.get_or_create(
                    performance=performance,
                    name=section_data['name'],
                    defaults={
                        'description': section_data['description'],
                        'total_capacity': section_data['total_capacity'],
                        'base_price': section_data['base_price'],
                        'currency': 'USD',
                        'is_premium': section_data['is_premium'],
                        'is_wheelchair_accessible': section_data['is_wheelchair_accessible']
                    }
                )
                if created:
                    created_count += 1
                    
                    # Create SectionTicketTypes for this section
                    ticket_types = TicketType.objects.filter(event=performance.event)
                    for ticket_type in ticket_types:
                        SectionTicketType.objects.get_or_create(
                            section=section,
                            ticket_type=ticket_type,
                            defaults={
                                'allocated_capacity': section.total_capacity // len(ticket_types),
                                'available_capacity': section.total_capacity // len(ticket_types),
                                'reserved_capacity': 0,
                                'sold_capacity': 0,
                                'price_modifier': 1.0
                            }
                        )
        
        messages.success(request, f'Successfully created {created_count} sections with ticket types.')
    create_standard_sections.short_description = "Create Standard Sections (Eco, Normal, VIP)"
    
    def create_standard_seats(self, request, queryset):
        """Create seats for all sections of selected performances."""
        from django.contrib import messages
        from .models import Seat, SectionTicketType
        
        created_count = 0
        for performance in queryset:
            for section in performance.sections.all():
                section_tickets = section.ticket_types.all()
                
                seat_number = 1
                for stt in section_tickets:
                    # Create seats for this ticket type
                    for i in range(stt.allocated_capacity):
                        seat, created = Seat.objects.get_or_create(
                            performance=performance,
                            section=section.name,
                            row_number=1,
                            seat_number=seat_number,
                            defaults={
                                'ticket_type': stt.ticket_type,
                                'status': 'available',
                                'price': section.base_price * stt.price_modifier,
                                'currency': 'USD',
                                'is_premium': section.is_premium,
                                'is_wheelchair_accessible': (
                                    section.is_wheelchair_accessible and 
                                    stt.ticket_type.name == 'Wheelchair Accessible'
                                )
                            }
                        )
                        if created:
                            created_count += 1
                        seat_number += 1
        
        messages.success(request, f'Successfully created {created_count} seats.')
    create_standard_seats.short_description = "Create Seats for All Sections"
    
    def available_capacity(self, obj):
        """Get available capacity."""
        try:
            return obj.available_capacity
        except:
            return 0
    available_capacity.short_description = _('Available Capacity')
    
    def booking_count(self, obj):
        """Get number of bookings for this performance."""
        try:
            return obj.bookings.count()
        except:
            return 0
    booking_count.short_description = _('Bookings')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('event').prefetch_related('bookings')


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    """Admin for Seat model."""
    
    list_display = [
        'performance', 'section', 'row_number', 'seat_number', 'ticket_type',
        'price', 'currency', 'status', 'is_wheelchair_accessible', 'is_premium'
    ]
    list_filter = [
        'performance__event__category', 'status', 'is_wheelchair_accessible',
        'is_premium', 'section', 'currency'
    ]
    search_fields = [
        'performance__event__title', 'seat_number', 'row_number', 'section'
    ]
    ordering = ['performance', 'section', 'row_number', 'seat_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Seat Information'), {
            'fields': ('performance', 'ticket_type', 'seat_number', 'row_number', 'section')
        }),
        (_('Pricing'), {
            'fields': ('price', 'currency')
        }),
        (_('Status'), {
            'fields': ('status', 'reservation_id', 'reservation_expires_at')
        }),
        (_('Features'), {
            'fields': ('is_wheelchair_accessible', 'is_premium')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('performance__event', 'ticket_type')


@admin.register(EventOption)
class EventOptionAdmin(admin.ModelAdmin):
    """Admin for EventOption model."""
    
    list_display = [
        'name', 'event', 'option_type', 'price', 'currency', 'is_available', 'is_active'
    ]
    list_filter = [
        'event__category', 'option_type', 'is_active', 'is_available'
    ]
    search_fields = [
        'name', 'description', 'event__title'
    ]
    ordering = ['event', 'name']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('event', 'name', 'description', 'option_type')
        }),
        (_('Pricing'), {
            'fields': ('price', 'currency')
        }),
        (_('Availability'), {
            'fields': ('is_available', 'max_quantity')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('event')


@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    """Admin for EventReview model."""
    
    list_display = [
        'event', 'user', 'rating', 'title', 'is_verified', 'is_helpful', 'created_at'
    ]
    list_filter = [
        'event__category', 'rating', 'is_verified', 'created_at'
    ]
    search_fields = [
        'event__title', 'user__username', 'user__email', 'title', 'comment'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Review Information'), {
            'fields': ('event', 'user', 'rating', 'title', 'comment')
        }),
        (_('Metadata'), {
            'fields': ('is_verified', 'is_helpful')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('event', 'user')


@admin.register(EventBooking)
class EventBookingAdmin(admin.ModelAdmin):
    """Admin for EventBooking model."""
    
    list_display = [
        'booking_reference', 'event', 'performance', 'user', 'total_tickets',
        'final_price', 'status', 'created_at'
    ]
    list_filter = [
        'event__category', 'status', 'booking_date', 'created_at'
    ]
    search_fields = [
        'booking_reference', 'event__title', 'user__username', 'user__email'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'booking_reference', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Booking Information'), {
            'fields': ('booking_reference', 'event', 'performance', 'user')
        }),
        (_('Booking Details'), {
            'fields': ('booking_date', 'booking_time', 'participants_count')
        }),
        (_('Seat Selection'), {
            'fields': ('selected_seats',)
        }),
        (_('Ticket Breakdown'), {
            'fields': ('ticket_breakdown',)
        }),
        (_('Options'), {
            'fields': ('selected_options', 'options_total')
        }),
        (_('Pricing'), {
            'fields': ('unit_price', 'total_price', 'currency')
        }),
        (_('Special Requirements'), {
            'fields': ('special_requirements',)
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_tickets(self, obj):
        """Get total number of tickets."""
        try:
            return obj.total_tickets
        except:
            return obj.participants_count
    total_tickets.short_description = _('Total Tickets')
    
    def final_price(self, obj):
        """Get final price."""
        try:
            return f"${obj.total_price:.2f}"
        except:
            return "N/A"
    final_price.short_description = _('Final Price')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('event', 'performance', 'user')


@admin.register(EventSection)
class EventSectionAdmin(admin.ModelAdmin):
    """Admin for EventSection model."""
    
    list_display = [
        'performance', 'name', 'total_capacity', 'available_capacity',
        'reserved_capacity', 'sold_capacity', 'occupancy_rate', 'is_premium'
    ]
    list_filter = [
        'performance__event__category', 'is_wheelchair_accessible', 'is_premium'
    ]
    search_fields = [
        'performance__event__title', 'name', 'description'
    ]
    ordering = ['performance', 'name']
    readonly_fields = ['available_capacity', 'reserved_capacity', 'sold_capacity', 'occupancy_rate']
    actions = ['create_multiple_sections', 'create_seats_for_sections']
    
    fieldsets = (
        (_('Section Information'), {
            'fields': ('performance', 'name', 'description')
        }),
        (_('Capacity Management'), {
            'fields': ('total_capacity',)
        }),
        (_('Computed Capacity'), {
            'fields': ('available_capacity', 'reserved_capacity', 'sold_capacity', 'occupancy_rate'),
            'classes': ('collapse',)
        }),
        (_('Pricing'), {
            'fields': ('base_price', 'currency')
        }),
        (_('Features'), {
            'fields': ('is_wheelchair_accessible', 'is_premium')
        }),
    )
    
    def create_multiple_sections(self, request, queryset):
        """Create multiple sections for selected performances."""
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # Redirect to bulk creation form
        return redirect(reverse('admin:events_eventperformance_bulk_sections'))
    create_multiple_sections.short_description = "Create Multiple Sections for Performance"
    
    def create_seats_for_sections(self, request, queryset):
        """Create seats for selected sections."""
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # Redirect to bulk seat creation form
        return redirect(reverse('admin:events_eventsection_bulk_seats'))
    create_seats_for_sections.short_description = "Create Seats for Sections"
    
    def available_capacity(self, obj):
        """Get available capacity using computed property."""
        try:
            return obj.available_capacity
        except:
            return 0
    available_capacity.short_description = _('Available Capacity')
    
    def reserved_capacity(self, obj):
        """Get reserved capacity using computed property."""
        try:
            return obj.reserved_capacity
        except:
            return 0
    reserved_capacity.short_description = _('Reserved Capacity')
    
    def sold_capacity(self, obj):
        """Get sold capacity using computed property."""
        try:
            return obj.sold_capacity
        except:
            return 0
    sold_capacity.short_description = _('Sold Capacity')
    
    def occupancy_rate(self, obj):
        """Get occupancy rate percentage."""
        try:
            return f"{obj.occupancy_rate:.1f}%"
        except:
            return "0%"
    occupancy_rate.short_description = _('Occupancy Rate')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('performance__event')


@admin.register(SectionTicketType)
class SectionTicketTypeAdmin(admin.ModelAdmin):
    """Admin for SectionTicketType model."""
    
    list_display = [
        'section', 'ticket_type', 'allocated_capacity', 'available_capacity',
        'reserved_capacity', 'sold_capacity', 'final_price', 'is_active'
    ]
    list_filter = [
        'section__performance__event__category', 'is_active'
    ]
    search_fields = [
        'section__performance__event__title', 'section__name', 'ticket_type__name'
    ]
    ordering = ['section', 'ticket_type']
    readonly_fields = ['final_price']
    
    fieldsets = (
        (_('Allocation Information'), {
            'fields': ('section', 'ticket_type')
        }),
        (_('Capacity Management'), {
            'fields': ('allocated_capacity', 'available_capacity', 'reserved_capacity', 'sold_capacity')
        }),
        (_('Pricing'), {
            'fields': ('price_modifier', 'final_price')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def final_price(self, obj):
        """Calculate final price."""
        try:
            base_price = obj.section.base_price
            modifier = obj.price_modifier
            final = base_price * modifier
            return f"${final:.2f}"
        except:
            return "N/A"
    final_price.short_description = _('Final Price')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('section__performance__event', 'ticket_type')


@admin.register(EventDiscount)
class EventDiscountAdmin(admin.ModelAdmin):
    """Admin for EventDiscount model."""
    
    list_display = [
        'event', 'code', 'name', 'discount_type', 'discount_value',
        'is_valid', 'is_active', 'current_uses'
    ]
    list_filter = [
        'event__category', 'discount_type', 'is_active', 'valid_from', 'valid_until'
    ]
    search_fields = [
        'event__title', 'code', 'name', 'description'
    ]
    ordering = ['event', 'code']
    
    fieldsets = (
        (_('Discount Information'), {
            'fields': ('event', 'code', 'name', 'description')
        }),
        (_('Discount Details'), {
            'fields': ('discount_type', 'discount_value')
        }),
        (_('Conditions'), {
            'fields': ('min_amount', 'max_discount')
        }),
        (_('Usage Limits'), {
            'fields': ('max_uses', 'current_uses')
        }),
        (_('Validity'), {
            'fields': ('valid_from', 'valid_until')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def is_valid(self, obj):
        """Check if discount is currently valid."""
        try:
            return obj.is_valid()
        except:
            return False
    is_valid.boolean = True
    is_valid.short_description = _('Valid')
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('event')


@admin.register(EventFee)
class EventFeeAdmin(admin.ModelAdmin):
    """Admin for EventFee model."""
    
    list_display = [
        'event', 'name', 'fee_type', 'calculation_type', 'fee_value',
        'is_mandatory', 'is_active'
    ]
    list_filter = [
        'event__category', 'fee_type', 'calculation_type', 'is_mandatory', 'is_active'
    ]
    search_fields = [
        'event__title', 'name', 'description'
    ]
    ordering = ['event', 'fee_type', 'name']
    
    fieldsets = (
        (_('Fee Information'), {
            'fields': ('event', 'name', 'description')
        }),
        (_('Fee Details'), {
            'fields': ('fee_type', 'calculation_type', 'fee_value')
        }),
        (_('Conditions'), {
            'fields': ('min_amount', 'max_fee')
        }),
        (_('Status'), {
            'fields': ('is_mandatory', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('event')


@admin.register(EventPricingRule)
class EventPricingRuleAdmin(admin.ModelAdmin):
    """Admin for EventPricingRule model."""
    
    list_display = [
        'event', 'name', 'rule_type', 'adjustment_type', 'adjustment_value',
        'priority', 'is_active'
    ]
    list_filter = [
        'event__category', 'rule_type', 'adjustment_type', 'is_active'
    ]
    search_fields = [
        'event__title', 'name', 'description'
    ]
    ordering = ['event', '-priority', 'name']
    
    fieldsets = (
        (_('Rule Information'), {
            'fields': ('event', 'name', 'description')
        }),
        (_('Rule Details'), {
            'fields': ('rule_type', 'adjustment_type', 'adjustment_value')
        }),
        (_('Conditions'), {
            'fields': ('conditions',)
        }),
        (_('Priority'), {
            'fields': ('priority',)
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    def get_queryset(self, request):
        """Add annotations for better performance."""
        return super().get_queryset(request).select_related('event') 