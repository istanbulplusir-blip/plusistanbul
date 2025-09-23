# Generated manually for data migration from JSONField to relational model

from django.db import migrations


def migrate_variant_capacities(apps, schema_editor):
    """
    Migrate variant capacities from JSONField to relational model.
    """
    TourSchedule = apps.get_model('tours', 'TourSchedule')
    TourScheduleVariantCapacity = apps.get_model('tours', 'TourScheduleVariantCapacity')
    TourVariant = apps.get_model('tours', 'TourVariant')
    
    migrated_count = 0
    error_count = 0
    
    for schedule in TourSchedule.objects.all():
        if schedule.variant_capacities_raw:
            try:
                # Get the JSON data
                capacities_data = schedule.variant_capacities_raw
                
                if isinstance(capacities_data, dict):
                    for variant_id_str, capacity_data in capacities_data.items():
                        try:
                            # Get the variant
                            variant = TourVariant.objects.get(id=variant_id_str)
                            
                            # Extract capacity data
                            total_capacity = capacity_data.get('total', variant.capacity)
                            booked_capacity = capacity_data.get('booked', 0)
                            available_capacity = capacity_data.get('available', total_capacity - booked_capacity)
                            
                            # Create the relational record
                            TourScheduleVariantCapacity.objects.get_or_create(
                                schedule=schedule,
                                variant=variant,
                                defaults={
                                    'total_capacity': total_capacity,
                                    'reserved_capacity': 0,  # Start with 0 reserved
                                    'confirmed_capacity': booked_capacity,  # Move booked to confirmed
                                    'is_available': True,
                                }
                            )
                            migrated_count += 1
                            
                        except TourVariant.DoesNotExist:
                            print(f"Variant {variant_id_str} not found for schedule {schedule.id}")
                            error_count += 1
                        except Exception as e:
                            print(f"Error migrating variant {variant_id_str} for schedule {schedule.id}: {e}")
                            error_count += 1
                            
            except Exception as e:
                print(f"Error processing schedule {schedule.id}: {e}")
                error_count += 1
    
    print(f"Migration completed: {migrated_count} records migrated, {error_count} errors")


def reverse_migrate_variant_capacities(apps, schema_editor):
    """
    Reverse migration: convert relational data back to JSONField.
    """
    TourSchedule = apps.get_model('tours', 'TourSchedule')
    TourScheduleVariantCapacity = apps.get_model('tours', 'TourScheduleVariantCapacity')
    
    for schedule in TourSchedule.objects.all():
        capacities_data = {}
        
        for capacity in schedule.variant_capacities.all():
            variant_id = str(capacity.variant.id)
            capacities_data[variant_id] = {
                'total': capacity.total_capacity,
                'booked': capacity.confirmed_capacity + capacity.reserved_capacity,
                'available': capacity.available_capacity,
            }
        
        schedule.variant_capacities_raw = capacities_data
        schedule.save(update_fields=['variant_capacities_raw'])


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0019_add_tour_schedule_variant_capacity'),
    ]

    operations = [
        migrations.RunPython(
            migrate_variant_capacities,
            reverse_migrate_variant_capacities,
        ),
    ]
