from django.core.management.base import BaseCommand
from tours.models import TourSchedule


class Command(BaseCommand):
    help = 'Sync variant capacities for all tour schedules to prevent inconsistencies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tour-slug',
            type=str,
            help='Sync only for a specific tour slug',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        tour_slug = options.get('tour_slug')
        dry_run = options.get('dry_run', False)
        
        if tour_slug:
            schedules = TourSchedule.objects.filter(tour__slug=tour_slug, is_available=True)
            self.stdout.write(f'Syncing variant capacities for tour: {tour_slug}')
        else:
            schedules = TourSchedule.objects.filter(is_available=True)
            self.stdout.write('Syncing variant capacities for all tours')
        
        total_schedules = schedules.count()
        self.stdout.write(f'Found {total_schedules} schedules to process')
        
        fixed_count = 0
        
        for schedule in schedules:
            # Check for inconsistencies
            available_variant_ids = set(str(v.id) for v in schedule.get_available_variants())
            capacity_variant_ids = set(schedule.variant_capacities_raw.keys())
            
            if available_variant_ids != capacity_variant_ids:
                self.stdout.write(f'  Schedule {schedule.id} ({schedule.start_date}): INCONSISTENCY DETECTED')
                self.stdout.write(f'    available_variants: {available_variant_ids}')
                self.stdout.write(f'    variant_capacities: {capacity_variant_ids}')
                
                if not dry_run:
                    schedule.sync_variant_capacities()
                    self.stdout.write(f'    ✅ Fixed! New capacity: {schedule.compute_total_capacity()}')
                    fixed_count += 1
                else:
                    self.stdout.write(f'    🔍 Would fix (dry run)')
                    fixed_count += 1
        
        if dry_run:
            self.stdout.write(f'\nDry run complete. Would fix {fixed_count} schedules.')
        else:
            self.stdout.write(f'\nSync complete. Fixed {fixed_count} schedules.')
