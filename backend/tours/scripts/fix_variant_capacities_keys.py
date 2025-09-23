from tours.models import TourSchedule
from django.db import transaction

@transaction.atomic
def fix_variant_capacities_keys():
    count = 0
    for sched in TourSchedule.objects.all():
        vc = sched.variant_capacities
        if isinstance(vc, dict):
            new_vc = {str(k): v for k, v in vc.items()}
            if new_vc != vc:
                sched.variant_capacities = new_vc
                sched.save(update_fields=['variant_capacities'])
                count += 1
    print(f"Updated {count} TourSchedule objects.")

if __name__ == "__main__":
    fix_variant_capacities_keys() 