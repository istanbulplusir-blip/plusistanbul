"""Add cancellation policy fields to Event model."""

from django.db import migrations, models
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='cancellation_hours',
            field=models.PositiveIntegerField(default=48, verbose_name='Cancellation hours'),
        ),
        migrations.AddField(
            model_name='event',
            name='refund_percentage',
            field=models.PositiveIntegerField(
                default=50,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name='Refund percentage'
            ),
        ),
    ]
