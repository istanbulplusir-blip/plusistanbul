# Generated migration to fix SystemSettings consistency

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_systemsettings_cart_max_items_user_and_more'),
    ]

    operations = [
        # Update existing SystemSettings to consistent values
        migrations.RunSQL(
            """
            UPDATE core_systemsettings 
            SET 
                cart_max_items_guest = 3,
                cart_max_total_guest = 500.00,
                cart_max_items_user = 10,
                cart_max_total_user = 5000.00,
                cart_max_carts_guest = 20,
                cart_rate_limit_guest = 30,
                cart_rate_limit_user = 20,
                order_max_pending_per_user = 3,
                order_max_pending_per_product = 1
            WHERE id = 1;
            """,
            reverse_sql="SELECT 1;"  # No reverse operation needed
        ),
    ]
