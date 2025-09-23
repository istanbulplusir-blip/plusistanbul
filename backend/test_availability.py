import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan_tourism.settings')
django.setup()

from car_rentals.serializers import CarRentalAvailabilityCheckSerializer
from car_rentals.models import CarRental

# Test the availability check
car = CarRental.objects.filter(slug='peykan-p-class-2025').first()
if car:
    data = {
        'pickup_date': '2025-09-12',
        'dropoff_date': '2025-09-15',
        'pickup_time': '01:00',
        'dropoff_time': '01:00'
    }

    serializer = CarRentalAvailabilityCheckSerializer(
        data=data,
        context={'car_rental': car}
    )

    try:
        is_valid = serializer.is_valid()
        print(f'Validation successful: {is_valid}')
        if not is_valid:
            print(f'Errors: {serializer.errors}')
        else:
            validated_data = serializer.validated_data
            print(f'Rental days: {validated_data.get("rental_days")}')
            print(f'Total price: {validated_data.get("total_price")}')
    except Exception as e:
        print(f'Exception: {e}')
        import traceback
        traceback.print_exc()
else:
    print('Car not found')
