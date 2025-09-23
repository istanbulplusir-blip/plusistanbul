from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date, timedelta, time
from decimal import Decimal
from events.models import (
    EventCategory,
    Venue,
    Event,
    TicketType,
    EventPerformance,
    EventSection,
    SectionTicketType,
    EventOption,
    Seat,
)
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a full test Event with 3 performances, 3 sections per performance, 3 ticket types per section, 10 seats per section, and 3 options.'

    def add_arguments(self, parser):
        parser.add_argument('--slug', default='seatmap-test-event', help='Event slug')
        parser.add_argument('--title', default='SeatMap Test Event', help='Event title')
        parser.add_argument('--style', default='music', help='Event style (music/sports/theater/...)')
        parser.add_argument('--base-price', type=float, default=100.0, help='Base price per section')
        parser.add_argument('--currency', default='USD', help='Currency')

    @transaction.atomic
    def handle(self, *args, **options):
        slug = options['slug']
        title = options['title']
        style = options['style']
        base_price = Decimal(str(options['base_price']))
        currency = options['currency']

        # Category (use or create a generic one)
        category = EventCategory.objects.first()
        if not category:
            category = EventCategory.objects.create()
            category.set_current_language('en')
            category.name = 'Concert'
            category.description = 'Concerts'
            category.save()

        # Venue (reuse existing if available)
        venue = Venue.objects.first()
        if not venue:
            venue = Venue()
            venue.set_current_language('en')
            venue.name = 'Test Hall'
            venue.description = 'Hall for testing'
            venue.address = 'Test Address'
            venue.city = 'Tehran'
            venue.country = 'Iran'
            venue.total_capacity = 1000
            venue.coordinates = {}
            venue.facilities = []
            # Image may be required by model; attempt to set a dummy path if necessary
            try:
                venue.image = None  # type: ignore
            except Exception:
                pass
            venue.save()

        # Event
        # Build defaults, ensuring required fields like price/currency are provided
        defaults = {
            'style': style,
            'category': category,
            'venue': venue,
            'door_open_time': time(16, 0),
            'start_time': time(17, 0),
            'end_time': time(20, 0),
        }
        # If Event has price/currency (from BaseProductModel), include them in defaults to satisfy NOT NULL
        model_fields = {f.name for f in Event._meta.get_fields()}
        if 'price' in model_fields:
            defaults['price'] = base_price
        if 'currency' in model_fields:
            defaults['currency'] = currency

        event, created = Event.objects.get_or_create(
            slug=slug,
            defaults=defaults,
        )
        # Translated fields
        event.set_current_language('en')
        event.title = title
        event.description = 'A fully generated test event with sections, ticket types, seats, and options.'
        event.short_description = 'Test event for seat-map'
        event.highlights = 'Auto-generated'
        event.rules = 'No smoking'
        event.required_items = 'ID'
        # BaseProductModel fields (price/currency) if available
        if hasattr(event, 'price'):
            setattr(event, 'price', base_price)
        if hasattr(event, 'currency'):
            setattr(event, 'currency', currency)
        event.save()

        # Ticket types
        tt_specs = [
            ('VIP', 'vip', Decimal('1.20')),
            ('Normal', 'normal', Decimal('1.00')),
            ('Economy', 'eco', Decimal('0.85')),
        ]
        ticket_types = []
        for name, code, mult in tt_specs:
            tt, _ = TicketType.objects.get_or_create(
                event=event,
                name=name,
                defaults={
                    'ticket_type': code,
                    'benefits': [],
                    'description': f'{name} ticket',
                    'price_modifier': mult,
                    'capacity': 1000,
                    'is_active': True,
                }
            )
            ticket_types.append((tt, code))

        # Options
        option_specs = [
            ('Parking', 'Parking pass', Decimal('10.00'), 'parking'),
            ('Snack', 'Snack box', Decimal('8.00'), 'food'),
            ('Merch', 'Merch bundle', Decimal('15.00'), 'service'),
        ]
        for name, desc, price, opt_type in option_specs:
            EventOption.objects.get_or_create(
                event=event,
                name=name,
                defaults={
                    'description': desc,
                    'price': price,
                    'currency': currency,
                    'option_type': opt_type,
                    'is_available': True,
                    'max_quantity': 5,
                },
            )

        # Performances (next 3 days)
        performances = []
        # Create performances with dynamic defaults only for existing fields
        perf_fields = {f.name for f in EventPerformance._meta.get_fields()}
        for i in range(1, 4):
            perf_date = date.today() + timedelta(days=i)
            perf_defaults = {
                'is_special': False,
                'ticket_capacities': {},
            }
            if 'start_date' in perf_fields:
                perf_defaults['start_date'] = perf_date
            if 'end_date' in perf_fields:
                perf_defaults['end_date'] = perf_date
            if 'start_time' in perf_fields:
                perf_defaults['start_time'] = event.start_time or time(17, 0)
            if 'end_time' in perf_fields:
                perf_defaults['end_time'] = event.end_time or time(20, 0)
            if 'is_available' in perf_fields:
                perf_defaults['is_available'] = True
            if 'max_capacity' in perf_fields:
                perf_defaults['max_capacity'] = 1000
            if 'current_capacity' in perf_fields:
                perf_defaults['current_capacity'] = 0

            perf, _ = EventPerformance.objects.get_or_create(
                event=event,
                date=perf_date,
                defaults=perf_defaults,
            )
            performances.append(perf)

        # Sections per performance
        section_names = ['A', 'B', 'C']
        seats_per_section = 10  # total seats per section
        for perf in performances:
            for sec_name in section_names:
                total_capacity = seats_per_section * len(ticket_types)
                section, _ = EventSection.objects.get_or_create(
                    performance=perf,
                    name=sec_name,
                    defaults={
                        'description': f'Section {sec_name}',
                        'total_capacity': total_capacity,
                        'available_capacity': total_capacity,
                        'reserved_capacity': 0,
                        'sold_capacity': 0,
                        'base_price': base_price,
                        'currency': currency,
                        'is_wheelchair_accessible': False,
                        'is_premium': False,
                    },
                )

                # Ticket allocations per section
                for (tt, _code) in ticket_types:
                    SectionTicketType.objects.get_or_create(
                        section=section,
                        ticket_type=tt,
                        defaults={
                            'allocated_capacity': seats_per_section,
                            'available_capacity': seats_per_section,
                            'reserved_capacity': 0,
                            'sold_capacity': 0,
                            'price_modifier': Decimal('1.00'),
                        },
                    )

                # Generate seats for this section
                for n in range(1, seats_per_section + 1):
                    Seat.objects.get_or_create(
                        performance=perf,
                        seat_number=str(n),
                        row_number='1',
                        section=sec_name,
                        defaults={
                            'price': base_price,
                            'currency': currency,
                            'is_premium': False,
                            'is_wheelchair_accessible': False,
                            'status': 'available',
                        },
                    )

        self.stdout.write(self.style.SUCCESS(f"Created/updated test event '{event.title}' with slug '{slug}'."))
        self.stdout.write(self.style.SUCCESS("Performances, sections, ticket types, seats, and options are ready."))


