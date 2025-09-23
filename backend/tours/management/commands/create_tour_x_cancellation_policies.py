from django.core.management.base import BaseCommand
from tours.models import Tour, TourCancellationPolicy


class Command(BaseCommand):
    help = 'Create cancellation policies for Tour X'

    def handle(self, *args, **options):
        try:
            tour = Tour.objects.get(slug='tour-x')
            self.stdout.write(f"Found Tour X: {tour.title}")

            # Create cancellation policies based on hardcoded translation rules
            policies_data = [
                {
                    'hours_before': 48,
                    'refund_percentage': 50,
                    'description': '50% بازگشت وجه تا 48 ساعت قبل از شروع تور',
                    'is_active': True
                },
                {
                    'hours_before': 24,
                    'refund_percentage': 25,
                    'description': '25% بازگشت وجه تا 24 ساعت قبل از شروع تور',
                    'is_active': True
                },
                {
                    'hours_before': 12,
                    'refund_percentage': 0,
                    'description': 'بدون بازگشت وجه کمتر از 12 ساعت قبل از شروع تور',
                    'is_active': True
                }
            ]

            created_count = 0
            for policy_data in policies_data:
                policy, created = TourCancellationPolicy.objects.get_or_create(
                    tour=tour,
                    hours_before=policy_data['hours_before'],
                    defaults=policy_data
                )
                
                if created:
                    self.stdout.write(f"✅ Created policy: {policy_data['hours_before']}h - {policy_data['refund_percentage']}%")
                    created_count += 1
                else:
                    self.stdout.write(f"✓ Policy already exists: {policy_data['hours_before']}h - {policy_data['refund_percentage']}%")

            self.stdout.write(f"\n📊 Summary:")
            self.stdout.write(f"   Total policies created: {created_count}")
            self.stdout.write(f"   Total policies for Tour X: {tour.cancellation_policies.count()}")

        except Tour.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Tour X not found!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
