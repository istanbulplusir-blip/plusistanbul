from django.core.management.base import BaseCommand
from tours.models import Tour, TourSchedule
from cart.models import CartItem
from orders.models import OrderItem
from django.db.models import Sum
from datetime import date


class Command(BaseCommand):
    help = 'Check capacity consistency between stored data and real-time calculations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tour-slug',
            type=str,
            help='Check only for a specific tour slug',
        )

    def handle(self, *args, **options):
        tour_slug = options.get('tour_slug')
        
        if tour_slug:
            tours = Tour.objects.filter(slug=tour_slug)
            self.stdout.write(f'Checking capacity consistency for tour: {tour_slug}')
        else:
            tours = Tour.objects.all()
            self.stdout.write('Checking capacity consistency for all tours')
        
        for tour in tours:
            self.stdout.write(f'\n=== Tour: {tour.title} ({tour.slug}) ===')
            
            for schedule in tour.schedules.filter(is_available=True).order_by('start_date'):
                self.stdout.write(f'\nSchedule: {schedule.start_date}')
                self.stdout.write(f'  Schedule ID: {schedule.id}')
                
                # Stored capacity data
                stored_total = schedule.compute_total_capacity()
                stored_available = schedule.available_capacity
                stored_booked = stored_total - stored_available
                
                self.stdout.write(f'  Stored data:')
                self.stdout.write(f'    Total: {stored_total}')
                self.stdout.write(f'    Available: {stored_available}')
                self.stdout.write(f'    Booked: {stored_booked}')
                
                # Real-time calculation
                cart_bookings = CartItem.objects.filter(
                    product_type='tour',
                    product_id=tour.id,
                    booking_data__schedule_id=str(schedule.id)
                ).aggregate(total=Sum('quantity'))['total'] or 0
                
                order_bookings = OrderItem.objects.filter(
                    product_type='tour',
                    product_id=tour.id,
                    booking_data__schedule_id=str(schedule.id),
                    order__status__in=['confirmed', 'paid', 'completed']
                ).aggregate(total=Sum('quantity'))['total'] or 0
                
                real_time_booked = cart_bookings + order_bookings
                real_time_available = max(0, stored_total - real_time_booked)
                
                self.stdout.write(f'  Real-time data:')
                self.stdout.write(f'    Cart bookings: {cart_bookings}')
                self.stdout.write(f'    Order bookings: {order_bookings}')
                self.stdout.write(f'    Total booked: {real_time_booked}')
                self.stdout.write(f'    Available: {real_time_available}')
                
                # Check consistency
                if stored_available != real_time_available:
                    self.stdout.write(f'  ⚠️  INCONSISTENCY DETECTED!')
                    self.stdout.write(f'    Stored available: {stored_available}')
                    self.stdout.write(f'    Real-time available: {real_time_available}')
                else:
                    self.stdout.write(f'  ✅ Consistent')
                
                # Check variant capacities
                self.stdout.write(f'  Variant capacities:')
                for variant_id, capacity_data in schedule.variant_capacities.items():
                    variant_total = capacity_data.get('total', 0)
                    variant_booked = capacity_data.get('booked', 0)
                    variant_available = capacity_data.get('available', 0)
                    
                    self.stdout.write(f'    Variant {variant_id}:')
                    self.stdout.write(f'      Total: {variant_total}, Booked: {variant_booked}, Available: {variant_available}')
