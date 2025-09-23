#!/usr/bin/env python
"""
Test TransferOption creation to verify slug generation fix
"""
import os
import sys
import django

# Add backend directory to path
sys.path.insert(0, 'peykan-tourism1/backend')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferOption, TransferRoute
from parler.models import TranslationDoesNotExist

def test_transfer_option_creation():
    print("=== Testing TransferOption creation ===")

    # Get the first available route
    route = TransferRoute.objects.first()
    if not route:
        print("No routes found, skipping test")
        return

    print(f"Using route: {route}")

    # Create a new TransferOption
    option = TransferOption(
        route=route,
        option_type='wheelchair',
        price_type='fixed',
        price=25.00,
        is_active=True
    )

    # Set translations
    option.set_current_language('en')
    option.name = "Wheelchair Access"
    option.description = "Wheelchair accessible vehicle"

    option.set_current_language('fa')
    option.name = "دسترسی صندلی چرخدار"
    option.description = "وسیله نقلیه قابل دسترسی با صندلی چرخدار"

    try:
        option.save()
        print(f"✅ Successfully created TransferOption: {option}")
        print(f"   Slug: {option.slug}")
        print(f"   ID: {option.id}")

        # Verify slug is unique
        existing_count = TransferOption.objects.filter(slug=option.slug).count()
        print(f"   Slug uniqueness check: {existing_count} options with this slug")

        # Clean up test option
        option.delete()
        print("   Test option deleted")

    except Exception as e:
        print(f"❌ Error creating TransferOption: {e}")

    print("=== Test completed ===")

if __name__ == '__main__':
    test_transfer_option_creation()
