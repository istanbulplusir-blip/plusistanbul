#!/usr/bin/env python
"""
Script to fix transfer test data by adding proper names and descriptions in both Persian and English translations.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute
from django.utils.translation import activate
from parler.utils.context import switch_language

def fix_transfer_data():
    """Fix transfer test data by adding proper names and descriptions in fa and en."""
    
    for lang, lang_label in [('fa', 'فارسی'), ('en', 'English')]:
        activate(lang)
        routes = TransferRoute.objects.all()
        print(f"Fixing {routes.count()} transfer routes for language: {lang_label}")
        for route in routes:
            with switch_language(route, lang):
                changed = False
                # Try to access name/description, if not exist, create translation
                try:
                    name = route.name
                except Exception:
                    name = None
                try:
                    description = route.description
                except Exception:
                    description = None
                if not name:
                    if lang == 'fa':
                        route.name = f"ترنسفر از {route.origin} به {route.destination}"
                    else:
                        route.name = f"Transfer from {route.origin} to {route.destination}"
                    changed = True
                if not description:
                    if lang == 'fa':
                        route.description = f"سرویس ترنسفر راحت و مطمئن از {route.origin} به {route.destination}. مدت زمان تقریبی: {getattr(route, 'estimated_duration_minutes', getattr(route, 'estimated_duration', ''))} دقیقه، فاصله: {route.distance_km} کیلومتر."
                    else:
                        route.description = f"Comfortable and reliable transfer service from {route.origin} to {route.destination}. Estimated duration: {getattr(route, 'estimated_duration_minutes', getattr(route, 'estimated_duration', ''))} minutes, distance: {route.distance_km} km."
                    changed = True
                if changed:
                    route.save()
                    print(f"Updated {lang_label} for route {route.origin} → {route.destination}")
    print("Transfer data translations fixed successfully!")

if __name__ == '__main__':
    fix_transfer_data() 