import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import TourSchedule

def print_variant_capacities_keys():
    for sched in TourSchedule.objects.all():
        vc = sched.variant_capacities
        if isinstance(vc, dict):
            key_types = set(type(k) for k in vc.keys())
            print(f"Schedule {sched.id}: key types = {key_types}, keys = {list(vc.keys())}")
        else:
            print(f"Schedule {sched.id}: variant_capacities is not a dict, type = {type(vc)}")

if __name__ == "__main__":
    print_variant_capacities_keys() 