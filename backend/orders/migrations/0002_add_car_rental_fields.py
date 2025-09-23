# Generated manually for car rental fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        # Add car rental specific fields to OrderItem
        migrations.AddField(
            model_name='orderitem',
            name='pickup_date',
            field=models.DateField(null=True, blank=True, verbose_name='Pickup date'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='dropoff_date',
            field=models.DateField(null=True, blank=True, verbose_name='Dropoff date'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='pickup_time',
            field=models.TimeField(null=True, blank=True, verbose_name='Pickup time'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='dropoff_time',
            field=models.TimeField(null=True, blank=True, verbose_name='Dropoff time'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='pickup_location_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('predefined', 'Predefined Location'),
                    ('custom', 'Custom Location'),
                ],
                default='predefined',
                verbose_name='Pickup location type'
            ),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='pickup_location_id',
            field=models.UUIDField(null=True, blank=True, verbose_name='Pickup location ID'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='pickup_location_custom',
            field=models.CharField(max_length=255, blank=True, verbose_name='Custom pickup location'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='pickup_location_coordinates',
            field=models.JSONField(default=dict, blank=True, verbose_name='Pickup location coordinates'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='dropoff_location_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('predefined', 'Predefined Location'),
                    ('custom', 'Custom Location'),
                    ('same_as_pickup', 'Same as Pickup'),
                ],
                default='same_as_pickup',
                verbose_name='Dropoff location type'
            ),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='dropoff_location_id',
            field=models.UUIDField(null=True, blank=True, verbose_name='Dropoff location ID'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='dropoff_location_custom',
            field=models.CharField(max_length=255, blank=True, verbose_name='Custom dropoff location'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='dropoff_location_coordinates',
            field=models.JSONField(default=dict, blank=True, verbose_name='Dropoff location coordinates'),
        ),
    ]
