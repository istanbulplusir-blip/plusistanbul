from django.core.management.base import BaseCommand
from django.utils import timezone
from cart.models import Cart, CartItem
from datetime import timedelta


class Command(BaseCommand):
    help = 'Clean up old cart items that should have been cleared after order creation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Clean up cart items older than this many days (default: 1)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually deleting',
        )

    def handle(self, *args, **options):
        days = options.get('days', 1)
        dry_run = options.get('dry_run', False)
        
        cutoff_time = timezone.now() - timedelta(days=days)
        
        # Find old cart items
        old_cart_items = CartItem.objects.filter(
            cart__created_at__lt=cutoff_time
        )
        
        total_items = old_cart_items.count()
        self.stdout.write(f'Found {total_items} cart items older than {days} days')
        
        if total_items == 0:
            self.stdout.write('No old cart items to clean up')
            return
        
        # Group by cart
        carts_to_clean = {}
        for item in old_cart_items:
            cart_id = item.cart.id
            if cart_id not in carts_to_clean:
                carts_to_clean[cart_id] = []
            carts_to_clean[cart_id].append(item)
        
        self.stdout.write(f'Found {len(carts_to_clean)} carts with old items')
        
        cleaned_count = 0
        for cart_id, items in carts_to_clean.items():
            cart = items[0].cart
            self.stdout.write(f'Cart {cart_id} ({cart.session_id}): {len(items)} items')
            
            if not dry_run:
                # Clean up this cart
                from cart.models import CartService
                CartService.clear_cart(cart)
                cleaned_count += len(items)
        
        if dry_run:
            self.stdout.write(f'Dry run complete. Would clean {total_items} items from {len(carts_to_clean)} carts.')
        else:
            self.stdout.write(f'Cleanup complete. Cleaned {cleaned_count} items from {len(carts_to_clean)} carts.')
