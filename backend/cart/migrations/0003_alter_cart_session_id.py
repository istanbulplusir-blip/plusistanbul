# Generated migration to increase session_id max_length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='session_id',
            field=models.CharField(max_length=255, unique=True, verbose_name='Session ID'),
        ),
    ]
