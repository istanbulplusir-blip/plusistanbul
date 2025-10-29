#!/usr/bin/env python3
"""
Create catalog in Docker database
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings_production')
django.setup()

from shared.models import CatalogFile
from django.core.files import File

# Check if catalog already exists
if CatalogFile.objects.filter(is_featured=True).exists():
    print("✅ Featured catalog already exists")
    catalog = CatalogFile.objects.filter(is_featured=True).first()
    print(f"   Title: {catalog.title}")
    print(f"   File: {catalog.file.name if catalog.file else 'No file'}")
    sys.exit(0)

# Create catalog
print("📝 Creating catalog...")

catalog = CatalogFile()

# Set translations
catalog.set_current_language('fa')
catalog.title = "راهنمای تورهای پیکان ترول ۲۰۲۵"
catalog.description = "کاتالوگ کامل تورها و خدمات پیکان توریسم برای سال ۲۰۲۵"

catalog.set_current_language('en')
catalog.title = "Peykan Travel Tour Guide 2025"
catalog.description = "Complete catalog of Peykan Tourism tours and services for 2025"

catalog.set_current_language('tr')
catalog.title = "Peykan Seyahat Tur Rehberi 2025"
catalog.description = "2025 için Peykan Turizm turları ve hizmetlerinin tam kataloğu"

# Set other fields
catalog.catalog_type = 'tour'
catalog.version = '2025-1'
catalog.is_featured = True
catalog.is_active = True
catalog.display_order = 0

# Check if file exists
file_path = '/app/media/catalogs/Peykan Travel Tour-Guide-2025-1.pdf'
if os.path.exists(file_path):
    print(f"✅ PDF file found: {file_path}")
    with open(file_path, 'rb') as f:
        catalog.file.save('Peykan Travel Tour-Guide-2025-1.pdf', File(f), save=False)
else:
    print(f"⚠️  PDF file not found: {file_path}")
    print("   Catalog will be created without file")

catalog.save()

print("✅ Catalog created successfully!")
print(f"   ID: {catalog.id}")
print(f"   Title (fa): {catalog.safe_translation_getter('title', language_code='fa')}")
print(f"   Featured: {catalog.is_featured}")
print(f"   Active: {catalog.is_active}")
if catalog.file:
    print(f"   File: {catalog.file.name}")
    print(f"   File size: {catalog.file_size_mb} MB")
