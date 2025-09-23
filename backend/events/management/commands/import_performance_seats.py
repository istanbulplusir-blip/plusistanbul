from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from events.models import EventPerformance, Seat
import csv


class Command(BaseCommand):
    help = 'Import or generate seats for a given performance.'

    def add_arguments(self, parser):
        parser.add_argument('--performance', required=True, help='Performance UUID')
        parser.add_argument('--csv', help='Path to CSV file with seats')
        parser.add_argument('--generate-grid', action='store_true', help='Generate a simple grid of seats')
        parser.add_argument('--sections', help='Comma-separated section names (for generate-grid) e.g. A,B,C')
        parser.add_argument('--rows', help='Row range (for generate-grid) e.g. 1-10')
        parser.add_argument('--seats-per-row', type=int, default=10, help='Number of seats per row (for generate-grid)')
        parser.add_argument('--base-price', type=float, default=100.0, help='Base price for generated seats')
        parser.add_argument('--currency', default='USD', help='Currency code (default USD)')

    def handle(self, *args, **options):
        performance_id = options['performance']
        csv_path = options.get('csv')
        generate_grid = options.get('generate_grid')

        try:
            performance = EventPerformance.objects.get(id=performance_id)
        except EventPerformance.DoesNotExist:
            raise CommandError('Performance not found')

        created = 0

        with transaction.atomic():
            if csv_path:
                created = self._import_from_csv(performance, csv_path, options)
            elif generate_grid:
                created = self._generate_grid(performance, options)
            else:
                raise CommandError('Provide either --csv or --generate-grid')

        self.stdout.write(self.style.SUCCESS(f"Created {created} seats for performance {performance.id}"))

    def _import_from_csv(self, performance, csv_path, options) -> int:
        created = 0
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                section = row.get('section') or 'General'
                row_number = row.get('row_number') or row.get('row') or '1'
                seat_number = row.get('seat_number') or row.get('seat')
                if not seat_number:
                    continue
                price = float(row.get('price') or options.get('base_price') or 100.0)
                currency = row.get('currency') or options.get('currency') or 'USD'
                is_premium = str(row.get('is_premium', '')).lower() in ['1', 'true', 'yes']
                is_wheelchair = str(row.get('is_wheelchair_accessible', '')).lower() in ['1', 'true', 'yes']

                obj, was_created = Seat.objects.get_or_create(
                    performance=performance,
                    seat_number=str(seat_number),
                    row_number=str(row_number),
                    section=str(section),
                    defaults={
                        'price': price,
                        'currency': currency,
                        'is_premium': is_premium,
                        'is_wheelchair_accessible': is_wheelchair,
                        'status': 'available',
                    }
                )
                if was_created:
                    created += 1
        return created

    def _generate_grid(self, performance, options) -> int:
        created = 0
        sections = (options.get('sections') or 'A').split(',')
        rows_spec = options.get('rows') or '1-10'
        seats_per_row = int(options.get('seats_per_row') or 10)
        base_price = float(options.get('base_price') or 100.0)
        currency = options.get('currency') or 'USD'

        # parse rows_spec like 1-10
        if '-' in rows_spec:
            start, end = rows_spec.split('-', 1)
            start = int(start)
            end = int(end)
            row_numbers = [str(i) for i in range(start, end + 1)]
        else:
            row_numbers = [r.strip() for r in rows_spec.split(',') if r.strip()]

        for section in sections:
            for row_number in row_numbers:
                for seat_idx in range(1, seats_per_row + 1):
                    seat_number = str(seat_idx)
                    obj, was_created = Seat.objects.get_or_create(
                        performance=performance,
                        seat_number=seat_number,
                        row_number=str(row_number),
                        section=str(section),
                        defaults={
                            'price': base_price,
                            'currency': currency,
                            'is_premium': False,
                            'is_wheelchair_accessible': False,
                            'status': 'available',
                        }
                    )
                    if was_created:
                        created += 1
        return created


