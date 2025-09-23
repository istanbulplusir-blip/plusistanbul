"""Add cancellation policy fields to Transfer model."""

from django.db import migrations, models
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('transfers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferroute',
            name='cancellation_hours',
            field=models.PositiveIntegerField(default=48, verbose_name='Cancellation hours'),
        ),
        migrations.AddField(
            model_name='transferroute',
            name='refund_percentage',
            field=models.PositiveIntegerField(
                default=50,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name='Refund percentage'
            ),
        ),
    ]
