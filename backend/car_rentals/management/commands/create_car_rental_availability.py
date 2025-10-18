"""
Management command to create car rental availability records.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from car_rentals.models import CarRental, CarRentalAvailability


class Command(BaseCommand):
    help = 'Create car rental availability records for the next 365 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--car-slug',
            type=str,
            help='Specific car rental slug to create availability for',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days to create availability for (default: 365)',
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date in YYYY-MM-DD format (default: today)',
        )

    def handle(self, *args, **options):
        car_slug = options.get('car_slug')
        days = options.get('days', 365)
        start_date_str = options.get('start_date')
        
        # Parse start date
        if start_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid start date format. Use YYYY-MM-DD')
                )
                return
        else:
            start_date = date.today()
        
        # Get car rentals
        if car_slug:
            try:
                car_rentals = [CarRental.objects.get(slug=car_slug)]
            except CarRental.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Car rental with slug "{car_slug}" not found')
                )
                return
        else:
            car_rentals = CarRental.objects.filter(is_active=True)
        
        if not car_rentals:
            self.stdout.write(
                self.style.WARNING('No active car rentals found')
            )
            return
        
        # Create availability records
        total_created = 0
        for car_rental in car_rentals:
            self.stdout.write(f'Creating availability for: {car_rental.title}')
            
            # Create availability for each day
            for i in range(days):
                current_date = start_date + timedelta(days=i)
                
                # Check if availability already exists
                existing = CarRentalAvailability.objects.filter(
                    car_rental=car_rental,
                    start_date=current_date,
                    end_date=current_date
                ).first()
                
                if not existing:
                    CarRentalAvailability.objects.create(
                        car_rental=car_rental,
                        start_date=current_date,
                        end_date=current_date,
                        is_available=True,
                        max_quantity=1,
                        booked_quantity=0
                    )
                    total_created += 1
                    
                    if total_created % 50 == 0:
                        self.stdout.write(f'Created {total_created} availability records...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {total_created} availability records for {len(car_rentals)} car rentals'
            )
        )
