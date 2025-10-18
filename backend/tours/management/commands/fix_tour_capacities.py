"""
Management command to fix tour capacity calculations.
"""

from django.core.management.base import BaseCommand
from tours.models import Tour, TourSchedule
from orders.models import OrderItem


class Command(BaseCommand):
    help = 'Fix tour capacity calculations by syncing variant_capacities_raw with confirmed orders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tour-slug',
            type=str,
            help='Fix capacities for a specific tour slug',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Fix capacities for all tours',
        )

    def handle(self, *args, **options):
        if options['tour_slug']:
            tours = Tour.objects.filter(slug=options['tour_slug'])
        elif options['all']:
            tours = Tour.objects.all()
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --tour-slug or --all')
            )
            return

        for tour in tours:
            self.stdout.write(f'Fixing capacities for tour: {tour.title}')
            
            schedules = tour.schedules.all()
            for schedule in schedules:
                self.stdout.write(f'  Processing schedule: {schedule.start_date}')
                
                # Get confirmed orders for this schedule
                confirmed_items = OrderItem.objects.filter(
                    product_type='tour',
                    product_id=tour.id,
                    booking_data__schedule_id=str(schedule.id),
                    order__status__in=['confirmed', 'paid', 'completed']
                )
                
                # Calculate participants per variant
                variant_participants = {}
                for item in confirmed_items:
                    variant_id = str(item.variant_id)
                    participants = item.booking_data.get('participants', {}) or {}
                    adult_count = int(participants.get('adult', 0))
                    child_count = int(participants.get('child', 0))
                    total_participants = adult_count + child_count
                    
                    if variant_id not in variant_participants:
                        variant_participants[variant_id] = 0
                    variant_participants[variant_id] += total_participants
                
                # Update variant_capacities_raw
                capacities = schedule.variant_capacities_raw or {}
                updated = False
                
                for variant_id, booked_count in variant_participants.items():
                    if variant_id in capacities:
                        old_booked = capacities[variant_id].get('booked', 0)
                        capacities[variant_id]['booked'] = booked_count
                        capacities[variant_id]['available'] = capacities[variant_id]['total'] - booked_count
                        
                        if old_booked != booked_count:
                            self.stdout.write(
                                f'    Updated variant {variant_id}: booked={booked_count}, available={capacities[variant_id]["available"]}'
                            )
                            updated = True
                
                if updated:
                    schedule.variant_capacities_raw = capacities
                    schedule.save()
                    self.stdout.write(f'    Schedule {schedule.start_date} updated')
                else:
                    self.stdout.write(f'    Schedule {schedule.start_date} - no changes needed')

        self.stdout.write(
            self.style.SUCCESS('Capacity fixing completed successfully!')
        )
