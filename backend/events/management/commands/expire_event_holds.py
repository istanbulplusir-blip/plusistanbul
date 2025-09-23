from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Expire reserved event seats whose reservation_expires_at is in the past.'

    def handle(self, *args, **options):
        from events.models import Seat
        now = timezone.now()
        qs = Seat.objects.filter(status='reserved', reservation_expires_at__lt=now)
        count = qs.update(status='available', reservation_id=None, reservation_expires_at=None)
        self.stdout.write(self.style.SUCCESS(f'Expired and released {count} reserved seats'))

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from events.models import Seat


class Command(BaseCommand):
    help = "Expire reserved event seats whose reservation_expires_at is past."

    def handle(self, *args, **options):
        now = timezone.now()
        qs = Seat.objects.filter(status='reserved', reservation_expires_at__lt=now)
        count = 0
        with transaction.atomic():
            count = qs.select_for_update(skip_locked=True).update(
                status='available', reservation_id=None, reservation_expires_at=None
            )
        self.stdout.write(self.style.SUCCESS(f"Expired {count} seat holds"))


