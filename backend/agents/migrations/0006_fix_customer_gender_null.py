# Generated manually to fix customer_gender field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0005_add_credential_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentcustomer',
            name='customer_gender',
            field=models.CharField(
                blank=True,
                choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                max_length=10,
                null=True,
                verbose_name='Customer gender'
            ),
        ),
    ]