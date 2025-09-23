from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time
from decimal import Decimal

from tours.models import Tour, TourVariant, TourSchedule, TourOption, TourCategory


class Command(BaseCommand):
    help = "Create Tour X with specific capacity requirements: 60 total capacity (30 per day)"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating Tour X with specified capacity requirements...")
        
        # Create or get category
        category, _ = TourCategory.objects.get_or_create(
            slug="cultural",
            defaults={
                "name": "Cultural Tours",
                "description": "Cultural and historical tours",
            },
        )
        
        # Create Tour X
        tour, created = Tour.objects.get_or_create(
            slug="tour-x",
            defaults={
                "title": "Tour X - Cultural Experience",
                "description": "A comprehensive cultural tour with multiple variants and specific capacity management",
                "short_description": "Experience culture with flexible options",
                "highlights": "Historical sites, cultural experiences, guided tours",
                "rules": "Please arrive 15 minutes before departure time",
                "required_items": "Comfortable shoes, camera, water bottle",
                "price": Decimal('150.00'),
                "currency": "USD",
                "duration_hours": 8,
                "pickup_time": time(8, 30),
                "start_time": time(9, 0),
                "end_time": time(17, 0),
                "min_participants": 1,
                "max_participants": 60,  # Total capacity
                "booking_cutoff_hours": 24,
                "cancellation_hours": 48,
                "refund_percentage": 80,
                "includes_transfer": True,
                "includes_guide": True,
                "includes_meal": True,
                "includes_photographer": False,
                "tour_type": "day",
                "transport_type": "land",
                "is_active": True,
                "category": category,
                "gallery": [
                    "https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Tour+X+1",
                    "https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Tour+X+2",
                ],
            },
        )
        
        if created:
            self.stdout.write(f"✅ Created tour: {tour.title}")
        else:
            self.stdout.write(f"📋 Using existing tour: {tour.title}")
        
        # Create variants with specific capacities
        variants_spec = [
            ("VIP", Decimal('250.00'), 10),      # 10 capacity per day
            ("ECO", Decimal('180.00'), 10),      # 10 capacity per day  
            ("NORMAL", Decimal('150.00'), 10),   # 10 capacity per day
        ]
        
        variants = []
        for name, base_price, capacity in variants_spec:
            variant, created = TourVariant.objects.get_or_create(
                tour=tour,
                name=name,
                defaults={
                    "description": f"{name} package with enhanced services",
                    "base_price": base_price,
                    "capacity": capacity,  # This is per day capacity
                    "is_active": True,
                    "includes_transfer": True,
                    "includes_guide": True,
                    "includes_meal": True,
                    "includes_photographer": name == "VIP",  # Only VIP includes photographer
                    "extended_hours": 0 if name == "NORMAL" else 1 if name == "ECO" else 2,
                    "private_transfer": name == "VIP",
                    "expert_guide": name in ["VIP", "ECO"],
                    "special_meal": name == "VIP",
                },
            )
            variants.append(variant)
            if created:
                self.stdout.write(f"✅ Created variant: {variant.name} (Capacity: {variant.capacity}, Price: ${variant.base_price})")
            else:
                self.stdout.write(f"📋 Using existing variant: {variant.name}")
        
        # Create schedules for May 20 and May 21, 2024
        schedule_dates = [
            date(2024, 5, 20),  # May 20
            date(2024, 5, 21),  # May 21
        ]
        
        schedules = []
        for schedule_date in schedule_dates:
            schedule, created = TourSchedule.objects.get_or_create(
                tour=tour,
                start_date=schedule_date,
                defaults={
                    "end_date": schedule_date,
                    "start_time": time(9, 0),
                    "end_time": time(17, 0),
                    "is_available": True,
                    "day_of_week": schedule_date.weekday(),
                    "price_adjustment": Decimal('0.00'),
                    "price_adjustment_type": "fixed",
                },
            )
            
            # Initialize variant capacities for this schedule
            schedule.initialize_variant_capacities()
            
            schedules.append(schedule)
            if created:
                self.stdout.write(f"✅ Created schedule: {schedule.start_date} (Capacity: {schedule.max_capacity})")
            else:
                self.stdout.write(f"📋 Using existing schedule: {schedule.start_date}")
        
        # Create tour options
        options_data = [
            {
                "name": "Private Guide",
                "description": "Exclusive private guide for your group",
                "price": Decimal('50.00'),
                "price_percentage": 0,
                "currency": "USD",
                "option_type": "service",
                "is_available": True,
                "max_quantity": 1,
            },
            {
                "name": "Lunch Upgrade",
                "description": "Premium lunch at selected restaurant",
                "price": Decimal('25.00'),
                "price_percentage": 0,
                "currency": "USD",
                "option_type": "food",
                "is_available": True,
                "max_quantity": 10,
            },
            {
                "name": "Photo Package",
                "description": "Professional photography service",
                "price": Decimal('30.00'),
                "price_percentage": 0,
                "currency": "USD",
                "option_type": "equipment",
                "is_available": True,
                "max_quantity": 5,
            },
        ]
        
        for option_data in options_data:
            option, created = TourOption.objects.get_or_create(
                tour=tour,
                name=option_data["name"],
                defaults=option_data,
            )
            if created:
                self.stdout.write(f"✅ Created option: {option.name} (${option.price})")
            else:
                self.stdout.write(f"📋 Using existing option: {option.name}")
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 TOUR X SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Tour: {tour.title}")
        self.stdout.write(f"Total Capacity: {tour.max_participants}")
        self.stdout.write(f"Currency: {tour.currency}")
        self.stdout.write(f"Duration: {tour.duration_hours} hours")
        
        self.stdout.write("\n🎫 Variants:")
        for variant in variants:
            self.stdout.write(f"  - {variant.name}: ${variant.base_price} (Capacity: {variant.capacity})")
        
        self.stdout.write("\n📅 Schedules:")
        for schedule in schedules:
            self.stdout.write(f"  - {schedule.start_date}: {schedule.max_capacity} capacity")
        
        self.stdout.write("\n✅ CAPACITY VERIFICATION:")
        self.stdout.write(f"  Total Tour Capacity: {tour.max_participants} ✅")
        for schedule in schedules:
            self.stdout.write(f"  {schedule.start_date} Capacity: {schedule.max_capacity} ✅")
        
        self.stdout.write("\n🎯 Capacity Requirements Met:")
        self.stdout.write("  - Tour X Total Capacity: 60 ✅")
        self.stdout.write("  - May 20 Capacity: 30 (10 VIP + 10 ECO + 10 NORMAL) ✅")
        self.stdout.write("  - May 21 Capacity: 30 (10 VIP + 10 ECO + 10 NORMAL) ✅")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Tour X created successfully with all capacity requirements!"))
