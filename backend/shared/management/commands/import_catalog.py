"""
Management command to import existing catalog PDF file into database.
"""

from django.core.management.base import BaseCommand
from django.core.files import File
from shared.models import CatalogFile
import os


class Command(BaseCommand):
    help = 'Import existing catalog PDF file into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='Peykan Travel Tour-Guide-2025-1.pdf',
            help='Filename of the PDF in media/catalogs/ directory'
        )
        parser.add_argument(
            '--featured',
            action='store_true',
            help='Set this catalog as featured'
        )

    def handle(self, *args, **options):
        filename = options['file']
        set_featured = options['featured']
        
        self.stdout.write(f'Importing catalog: {filename}')
        
        # Check if file exists in media/catalogs/
        file_path = os.path.join('media', 'catalogs', filename)
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        # Check if catalog already exists
        existing_catalog = CatalogFile.objects.filter(
            file__icontains=filename
        ).first()
        
        if existing_catalog:
            self.stdout.write(self.style.WARNING(f'Catalog already exists: {existing_catalog}'))
            
            # Update featured status if requested
            if set_featured and not existing_catalog.is_featured:
                # Unset other featured catalogs
                CatalogFile.objects.filter(is_featured=True).update(is_featured=False)
                existing_catalog.is_featured = True
                existing_catalog.save()
                self.stdout.write(self.style.SUCCESS(f'Updated catalog as featured'))
            
            self.stdout.write(self.style.SUCCESS(f'Catalog ID: {existing_catalog.id}'))
            self.stdout.write(self.style.SUCCESS(f'File URL: {existing_catalog.get_file_url()}'))
            return
        
        # Create new catalog entry
        catalog = CatalogFile(
            catalog_type='tour',
            version='2025-1',
            is_featured=set_featured,
            display_order=0,
            is_active=True
        )
        
        # Set file path (relative to MEDIA_ROOT)
        catalog.file.name = f'catalogs/{filename}'
        
        # Calculate file size
        catalog.file_size = os.path.getsize(file_path)
        
        # Save without file upload (file already exists)
        catalog.save()
        
        # Set translations
        catalog.set_current_language('en')
        catalog.title = 'Peykan Travel Tour Guide 2025'
        catalog.description = 'Complete tour guide catalog for 2025 season featuring all our tours, packages, and services.'
        catalog.meta_description = 'Download Peykan Travel Tour Guide 2025 - Complete catalog of Istanbul tours, packages, and travel services.'
        catalog.save()
        
        catalog.set_current_language('fa')
        catalog.title = 'راهنمای تورهای پیکان ترول ۲۰۲۵'
        catalog.description = 'کاتالوگ کامل راهنمای تور برای فصل ۲۰۲۵ شامل تمام تورها، پکیج‌ها و خدمات ما.'
        catalog.meta_description = 'دانلود راهنمای تورهای پیکان ترول ۲۰۲۵ - کاتالوگ کامل تورهای استانبول، پکیج‌ها و خدمات سفر.'
        catalog.save()
        
        catalog.set_current_language('tr')
        catalog.title = 'Peykan Travel Tur Rehberi 2025'
        catalog.description = '2025 sezonu için tüm turlarımızı, paketlerimizi ve hizmetlerimizi içeren eksiksiz tur rehberi kataloğu.'
        catalog.meta_description = 'Peykan Travel Tur Rehberi 2025\'i İndirin - İstanbul turları, paketler ve seyahat hizmetlerinin eksiksiz kataloğu.'
        catalog.save()
        
        # If this is featured, unset other featured catalogs
        if set_featured:
            CatalogFile.objects.exclude(id=catalog.id).filter(is_featured=True).update(is_featured=False)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported catalog: {catalog}'))
        self.stdout.write(self.style.SUCCESS(f'Catalog ID: {catalog.id}'))
        self.stdout.write(self.style.SUCCESS(f'File size: {catalog.file_size_mb} MB'))
        self.stdout.write(self.style.SUCCESS(f'File URL: {catalog.get_file_url()}'))
        self.stdout.write(self.style.SUCCESS(f'Is featured: {catalog.is_featured}'))
        
        # Verify file is accessible
        if os.path.exists(file_path):
            self.stdout.write(self.style.SUCCESS('✓ File is accessible on filesystem'))
        else:
            self.stdout.write(self.style.ERROR('✗ File not accessible on filesystem'))
