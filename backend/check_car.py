import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan_tourism.settings')
django.setup()

from car_rentals.models import CarRental

car = CarRental.objects.filter(slug='peykan-p-class-2025').first()
if car:
    print(f"Title: {car.title}")
    print(f"Max rent days: {car.max_rent_days}")
    print(f"Min rent days: {car.min_rent_days}")
    print(f"Allow hourly rental: {car.allow_hourly_rental}")
    print(f"Max hourly rental hours: {car.max_hourly_rental_hours}")
else:
    print("Car not found")
