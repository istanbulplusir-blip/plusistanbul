#!/usr/bin/env python
"""
Fix TransferOption with empty slug
"""
import os
import sys
import django

# Add backend directory to path
sys.path.insert(0, 'peykan-tourism1/backend')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferOption
from django.utils.text import slugify

def fix_empty_slugs():
    print("=== Fixing TransferOption empty slugs ===")

    # Find options with empty slugs
    empty_slug_options = TransferOption.objects.filter(slug='')

    print(f"Found {empty_slug_options.count()} options with empty slugs")

    for option in empty_slug_options:
        print(f"Fixing option: {option} (ID: {option.id})")

        try:
            # Try to get name from translations
            name = None
            try:
                name = option.name
            except:
                # Try to get translation in any available language
                for translation in option.translations.all():
                    if translation.name:
                        name = translation.name
                        break

            if name:
                base_slug = slugify(name, allow_unicode=True)
                print(f"  Generated slug from name: {base_slug}")
            else:
                # Use option_type as fallback
                base_slug = slugify(option.option_type, allow_unicode=True)
                print(f"  Generated slug from option_type: {base_slug}")

            # Ensure uniqueness
            counter = 1
            original_slug = base_slug
            while TransferOption.objects.filter(slug=base_slug).exclude(pk=option.pk).exists():
                base_slug = f"{original_slug}-{counter}"
                counter += 1

            option.slug = base_slug
            option.save(update_fields=['slug'])
            print(f"  Saved with slug: {option.slug}")

        except Exception as e:
            print(f"  Error fixing option {option.id}: {e}")

    print("=== Done fixing empty slugs ===")

if __name__ == '__main__':
    fix_empty_slugs()
