"""
Management command for order operations.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from orders.models import Order, OrderService
from django.utils import timezone


class Command(BaseCommand):
    help = 'Manage orders - confirm, cancel, or mark as paid'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['confirm', 'cancel', 'paid', 'list'],
            help='Action to perform on orders'
        )
        parser.add_argument(
            '--order-number',
            type=str,
            help='Specific order number to process'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['pending', 'confirmed', 'paid', 'cancelled'],
            help='Filter orders by status'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        action = options['action']
        order_number = options.get('order_number')
        status_filter = options.get('status')
        dry_run = options.get('dry_run')

        if action == 'list':
            self.list_orders(status_filter)
        elif order_number:
            self.process_single_order(order_number, action, dry_run)
        else:
            self.process_bulk_orders(action, status_filter, dry_run)

    def list_orders(self, status_filter):
        """List orders with optional status filter."""
        queryset = Order.objects.all()
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        orders = queryset.order_by('-created_at')[:20]  # Show last 20
        
        self.stdout.write(f"\n{'Order Number':<15} {'Status':<12} {'User':<15} {'Amount':<10} {'Created'}")
        self.stdout.write("-" * 80)
        
        for order in orders:
            self.stdout.write(
                f"{order.order_number:<15} {order.status:<12} {order.user.username:<15} "
                f"${order.total_amount:<9.2f} {order.created_at.strftime('%Y-%m-%d %H:%M')}"
            )

    def process_single_order(self, order_number, action, dry_run):
        """Process a single order."""
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            raise CommandError(f'Order {order_number} not found')

        self.stdout.write(f"\nProcessing order: {order.order_number}")
        self.stdout.write(f"Current status: {order.status}")
        self.stdout.write(f"Action: {action}")
        self.stdout.write(f"Dry run: {dry_run}")

        if dry_run:
            self.stdout.write("DRY RUN - No changes will be made")
            return

        success = self._perform_action(order, action)
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully {action}ed order {order.order_number}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to {action} order {order.order_number}')
            )

    def process_bulk_orders(self, action, status_filter, dry_run):
        """Process multiple orders."""
        queryset = Order.objects.all()
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by appropriate status for each action
        if action == 'confirm':
            queryset = queryset.filter(status='pending')
        elif action == 'cancel':
            queryset = queryset.filter(status__in=['pending', 'confirmed'])
        elif action == 'paid':
            queryset = queryset.filter(status__in=['pending', 'confirmed'])

        orders = list(queryset)
        
        if not orders:
            self.stdout.write("No orders found matching criteria")
            return

        self.stdout.write(f"\nFound {len(orders)} orders to process")
        if dry_run:
            self.stdout.write("DRY RUN - No changes will be made")
            for order in orders:
                self.stdout.write(f"  Would {action}: {order.order_number}")
            return

        success_count = 0
        failed_count = 0

        for order in orders:
            try:
                success = self._perform_action(order, action)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {order.order_number}: {str(e)}')
                )
                failed_count += 1

        self.stdout.write(f"\nResults:")
        self.stdout.write(f"  Successfully processed: {success_count}")
        self.stdout.write(f"  Failed: {failed_count}")

    def _perform_action(self, order, action):
        """Perform the specified action on an order."""
        try:
            with transaction.atomic():
                if action == 'confirm':
                    if order.status == 'pending':
                        success, message = order.confirm_order()
                        if success:
                            # Log the change
                            from orders.models import OrderHistory
                            OrderHistory.objects.create(
                                order=order,
                                user=None,  # System action
                                field_name='status',
                                old_value='pending',
                                new_value='confirmed',
                                change_reason='Confirmed via management command'
                            )
                        return success
                    else:
                        self.stdout.write(f"Order {order.order_number} is not pending")
                        return False

                elif action == 'cancel':
                    if order.status in ['pending', 'confirmed']:
                        success = order.cancel_order('Cancelled via management command')
                        if success:
                            # Log the change
                            from orders.models import OrderHistory
                            OrderHistory.objects.create(
                                order=order,
                                user=None,  # System action
                                field_name='status',
                                old_value=order.status,
                                new_value='cancelled',
                                change_reason='Cancelled via management command'
                            )
                        return success
                    else:
                        self.stdout.write(f"Order {order.order_number} cannot be cancelled")
                        return False

                elif action == 'paid':
                    if order.status in ['pending', 'confirmed']:
                        old_status = order.status
                        order.status = 'paid'
                        order.payment_status = 'paid'
                        order.save()
                        
                        # Log the change
                        from orders.models import OrderHistory
                        OrderHistory.objects.create(
                            order=order,
                            user=None,  # System action
                            field_name='status',
                            old_value=old_status,
                            new_value='paid',
                            change_reason='Marked as paid via management command'
                        )
                        return True
                    else:
                        self.stdout.write(f"Order {order.order_number} cannot be marked as paid")
                        return False

        except Exception as e:
            self.stdout.write(f"Error performing action: {str(e)}")
            return False
