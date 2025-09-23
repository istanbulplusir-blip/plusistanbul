from django.core.management.base import BaseCommand
from django.utils import timezone
from uuid import uuid4

from tours.models import Tour, TourVariant, TourSchedule, TourOption, TourCategory


class Command(BaseCommand):
    help = "Create a test tour with variants, schedule capacities, and options"

    def handle(self, *args, **options):
        # Create tour
        from datetime import time
        # Ensure a category exists
        category, _ = TourCategory.objects.get_or_create(
            slug="testing",
            defaults={
                "name": "Testing",
                "description": "Test category",
            },
        )
        tour, _ = Tour.objects.get_or_create(
            slug="capacity-test-tour",
            defaults={
                "title": "Capacity Test Tour",
                "description": "A tour for testing capacities and options",
                "short_description": "Capacity + Options test",
                "price": 100,
                "currency": "USD",
                "duration_hours": 8,
                "pickup_time": time(8, 30),
                "start_time": time(9, 0),
                "end_time": time(17, 0),
                "min_participants": 1,
                "max_participants": 100,
                "booking_cutoff_hours": 4,
                "cancellation_hours": 24,
                "refund_percentage": 50,
                "includes_transfer": True,
                "includes_guide": True,
                "includes_meal": False,
                "is_active": True,
                "category": category,
            },
        )

        # Create variants with capacities
        variants_spec = [
            ("Eco", 120, 20),
            ("Normal", 150, 20),
            ("VIP", 220, 20),
            ("VVIP", 300, 20),
        ]
        variants = []
        for name, base_price, capacity in variants_spec:
            v, _ = TourVariant.objects.get_or_create(
                tour=tour,
                name=name,
                defaults={
                    "description": f"{name} package",
                    "base_price": base_price,
                    "capacity": capacity,
                    "is_active": True,
                },
            )
            variants.append(v)

        # Create schedules for the next 3 days to ensure visible dates in UI
        base_date = timezone.now().date()
        for plus in range(0, 3):
            start_date = base_date + timezone.timedelta(days=plus)
            schedule, _ = TourSchedule.objects.get_or_create(
                tour=tour,
                start_date=start_date,
                defaults={
                    "end_date": start_date,
                    "start_time": timezone.now().time().replace(hour=9, minute=0, second=0, microsecond=0),
                    "end_time": timezone.now().time().replace(hour=17, minute=0, second=0, microsecond=0),
                    "is_available": True,
                    "max_capacity": 0,
                    "current_capacity": 0,
                    "day_of_week": start_date.weekday(),
                },
            )
            schedule.initialize_variant_capacities()

        # Create a couple of options to test options flow
        TourOption.objects.get_or_create(
            tour=tour,
            name="Lunch",
            defaults={
                "description": "Lunch included",
                "price": 10,
                "price_percentage": 0,
                "currency": "USD",
                "option_type": "food",
                "is_available": True,
                "max_quantity": 10,
            },
        )
        TourOption.objects.get_or_create(
            tour=tour,
            name="Photo Package",
            defaults={
                "description": "Professional photos",
                "price": 25,
                "price_percentage": 0,
                "currency": "USD",
                "option_type": "equipment",
                "is_available": True,
                "max_quantity": 5,
            },
        )

        self.stdout.write(self.style.SUCCESS("Created/updated capacity test tour with variants, schedule, and options."))


