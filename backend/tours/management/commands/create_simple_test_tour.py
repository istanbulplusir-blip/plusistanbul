from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, timedelta

from tours.models import Tour, TourVariant, TourSchedule, TourOption, TourCategory


class Command(BaseCommand):
    help = "Create a simple test tour for testing"

    def handle(self, *args, **options):
        # Create or get category
        category, _ = TourCategory.objects.get_or_create(
            slug="test-tours",
            defaults={
                "name": "Test Tours",
                "name_en": "Test Tours",
                "name_fa": "تورهای تستی",
                "name_tr": "Test Turları",
                "description": "Test category for development",
            },
        )
        
        # Create tour
        tour, created = Tour.objects.get_or_create(
            slug="test-tour-sample",
            defaults={
                "title": "Test Tour - Sample",
                "description": "This is a test tour for development and testing purposes",
                "short_description": "Test tour for development",
                "price": 100,
                "currency": "USD",
                "duration_hours": 8,
                "pickup_time": time(8, 30),
                "start_time": time(9, 0),
                "end_time": time(17, 0),
                "min_participants": 1,
                "max_participants": 50,
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
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created new tour: {tour.title}"))
        else:
            self.stdout.write(self.style.WARNING(f"Tour already exists: {tour.title}"))

        # Create variants
        variants_data = [
            ("Standard", "Standard package", 100, 20),
            ("Premium", "Premium package with extras", 150, 15),
            ("VIP", "VIP package with all amenities", 200, 10),
        ]
        
        for name, desc, price, capacity in variants_data:
            variant, created = TourVariant.objects.get_or_create(
                tour=tour,
                name=name,
                defaults={
                    "description": desc,
                    "base_price": price,
                    "capacity": capacity,
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created variant: {name}"))

        # Create schedules for next 7 days
        today = timezone.now().date()
        for i in range(7):
            schedule_date = today + timedelta(days=i)
            schedule, created = TourSchedule.objects.get_or_create(
                tour=tour,
                start_date=schedule_date,
                defaults={
                    "end_date": schedule_date,
                    "start_time": time(9, 0),
                    "end_time": time(17, 0),
                    "is_available": True,
                    "day_of_week": schedule_date.weekday(),
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created schedule for: {schedule_date}"))
                # Initialize variant capacities
                schedule.initialize_variant_capacities()

        # Create options
        options_data = [
            ("Lunch", "Delicious lunch included", 15, "food"),
            ("Photo Package", "Professional photography", 25, "equipment"),
        ]
        
        for name, desc, price, opt_type in options_data:
            option, created = TourOption.objects.get_or_create(
                tour=tour,
                name=name,
                defaults={
                    "description": desc,
                    "price": price,
                    "price_percentage": 0,
                    "currency": "USD",
                    "option_type": opt_type,
                    "is_available": True,
                    "max_quantity": 10,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created option: {name}"))

        self.stdout.write(self.style.SUCCESS("\n✅ Test tour created successfully!"))
        self.stdout.write(self.style.SUCCESS(f"Tour slug: {tour.slug}"))
        self.stdout.write(self.style.SUCCESS(f"Tour ID: {tour.id}"))
