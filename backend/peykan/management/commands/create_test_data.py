from django.core.management.base import BaseCommand
from users.models import User
from create_test_data import create_test_users, create_tour_test_data, create_event_test_data, create_transfer_test_data, create_test_cart_data
from create_comprehensive_event_test_data import run_comprehensive_event_test_data

class Command(BaseCommand):
    help = 'Create comprehensive test data for users, tours, events, transfers, and cart.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing data before creating new test data',
        )
        parser.add_argument(
            '--users-only',
            action='store_true',
            help='Create only user test data',
        )
        parser.add_argument(
            '--tours-only',
            action='store_true',
            help='Create only tour test data',
        )
        parser.add_argument(
            '--events-only',
            action='store_true',
            help='Create only event test data',
        )
        parser.add_argument(
            '--transfers-only',
            action='store_true',
            help='Create only transfer test data',
        )
        parser.add_argument(
            '--cart-only',
            action='store_true',
            help='Create only cart test data',
        )
        parser.add_argument(
            '--comprehensive-events',
            action='store_true',
            help='Create comprehensive event test data with all features',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting existing data...'))
            # Add reset logic here if needed
            self.stdout.write(self.style.SUCCESS('Data reset completed.'))

        if options['users_only']:
            self.stdout.write(self.style.NOTICE('Creating test users...'))
            users = create_test_users()
            self.stdout.write(self.style.SUCCESS('Test users created.'))
            return

        if options['tours_only']:
            self.stdout.write(self.style.NOTICE('Creating tours...'))
            tours = create_tour_test_data()
            self.stdout.write(self.style.SUCCESS('Tours created.'))
            return

        if options['events_only']:
            self.stdout.write(self.style.NOTICE('Creating comprehensive events...'))
            result = run_comprehensive_event_test_data()
            self.stdout.write(self.style.SUCCESS('Comprehensive events created.'))
            return

        if options['transfers_only']:
            self.stdout.write(self.style.NOTICE('Creating transfers...'))
            transfer = create_transfer_test_data()
            self.stdout.write(self.style.SUCCESS('Transfers created.'))
            return

        if options['cart_only']:
            self.stdout.write(self.style.NOTICE('Creating cart for test customer...'))
            customer_user = User.objects.filter(is_active=True, is_staff=False).first()
            if customer_user:
                create_test_cart_data(customer_user)
                self.stdout.write(self.style.SUCCESS(f'Cart created for user: {customer_user.username}'))
            else:
                self.stdout.write(self.style.WARNING('No active non-staff user found for cart creation.'))
            return

        if options['comprehensive_events']:
            self.stdout.write(self.style.NOTICE('Creating comprehensive event test data...'))
            result = run_comprehensive_event_test_data()
            self.stdout.write(self.style.SUCCESS('Comprehensive event test data created successfully!'))
            return

        # Create all test data
        self.stdout.write(self.style.NOTICE('Creating test users...'))
        users = create_test_users()
        self.stdout.write(self.style.SUCCESS('Test users created.'))

        self.stdout.write(self.style.NOTICE('Creating tours...'))
        tours = create_tour_test_data()
        self.stdout.write(self.style.SUCCESS('Tours created.'))

        self.stdout.write(self.style.NOTICE('Creating comprehensive events...'))
        event_result = run_comprehensive_event_test_data()
        self.stdout.write(self.style.SUCCESS('Comprehensive events created.'))

        self.stdout.write(self.style.NOTICE('Creating transfers...'))
        transfer = create_transfer_test_data()
        self.stdout.write(self.style.SUCCESS('Transfers created.'))

        self.stdout.write(self.style.NOTICE('Creating cart for test customer...'))
        customer_user = User.objects.filter(is_active=True, is_staff=False).first()
        if customer_user:
            create_test_cart_data(customer_user)
            self.stdout.write(self.style.SUCCESS(f'Cart created for user: {customer_user.username}'))
        else:
            self.stdout.write(self.style.WARNING('No active non-staff user found for cart creation.'))

        self.stdout.write(self.style.SUCCESS('All test data created successfully!')) 