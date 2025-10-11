"""
Management command to identify and fix TourCategory objects with missing translations.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from tours.models import TourCategory
from parler.models import TranslationDoesNotExist


class Command(BaseCommand):
    help = 'Identify and fix TourCategory objects with missing translations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--language',
            type=str,
            help='Check specific language (fa, en, tr)',
            default=None,
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix missing translations using slug as fallback',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        target_language = options['language']
        auto_fix = options['fix']
        
        # Get supported languages from settings
        supported_languages = [lang['code'] for lang in settings.PARLER_LANGUAGES[settings.SITE_ID]]
        
        if target_language and target_language not in supported_languages:
            raise CommandError(f'Language "{target_language}" not supported. Available: {supported_languages}')
        
        languages_to_check = [target_language] if target_language else supported_languages
        
        self.stdout.write(
            self.style.SUCCESS(f'Checking TourCategory translations for languages: {languages_to_check}')
        )
        
        # Get all TourCategory objects
        categories = TourCategory.objects.all()
        total_categories = categories.count()
        
        if total_categories == 0:
            self.stdout.write(self.style.WARNING('No TourCategory objects found.'))
            return
        
        self.stdout.write(f'Found {total_categories} categories to check.')
        
        issues_found = []
        
        # Check each category for missing translations
        for category in categories:
            category_issues = {
                'category': category,
                'slug': category.slug,
                'missing_translations': {}
            }
            
            for lang_code in languages_to_check:
                try:
                    # Try to access the translation for this language
                    category.set_current_language(lang_code)
                    name = category.name
                    description = category.description
                    
                    # Check if fields are empty
                    missing_fields = []
                    if not name or name.strip() == '':
                        missing_fields.append('name')
                    if not description or description.strip() == '':
                        missing_fields.append('description')
                    
                    if missing_fields:
                        category_issues['missing_translations'][lang_code] = {
                            'status': 'empty_fields',
                            'missing_fields': missing_fields,
                            'current_name': name,
                            'current_description': description
                        }
                        
                except TranslationDoesNotExist:
                    # Translation doesn't exist for this language
                    category_issues['missing_translations'][lang_code] = {
                        'status': 'no_translation',
                        'missing_fields': ['name', 'description']
                    }
            
            # Only add to issues if there are actual problems
            if category_issues['missing_translations']:
                issues_found.append(category_issues)
        
        # Report findings
        if not issues_found:
            self.stdout.write(
                self.style.SUCCESS('✅ All categories have complete translations!')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {len(issues_found)} categories with translation issues:')
        )
        
        for issue in issues_found:
            self.stdout.write(f'\n📂 Category: {issue["slug"]} (ID: {issue["category"].id})')
            
            for lang_code, problem in issue['missing_translations'].items():
                if problem['status'] == 'no_translation':
                    self.stdout.write(
                        f'  ❌ {lang_code.upper()}: No translation exists'
                    )
                elif problem['status'] == 'empty_fields':
                    self.stdout.write(
                        f'  ⚠️  {lang_code.upper()}: Empty fields: {", ".join(problem["missing_fields"])}'
                    )
                    if problem.get('current_name'):
                        self.stdout.write(f'     Current name: "{problem["current_name"]}"')
                    if problem.get('current_description'):
                        self.stdout.write(f'     Current description: "{problem["current_description"][:100]}..."')
        
        # Auto-fix if requested
        if auto_fix and not dry_run:
            self.stdout.write(f'\n🔧 Attempting to fix {len(issues_found)} categories...')
            
            fixed_count = 0
            with transaction.atomic():
                for issue in issues_found:
                    category = issue['category']
                    
                    for lang_code, problem in issue['missing_translations'].items():
                        try:
                            # Create or update translation
                            category.set_current_language(lang_code)
                            
                            # Generate fallback content based on slug
                            fallback_name = self._generate_fallback_name(category.slug, lang_code)
                            fallback_description = self._generate_fallback_description(category.slug, lang_code)
                            
                            if problem['status'] == 'no_translation':
                                # Create new translation
                                category.create_translation(
                                    lang_code,
                                    name=fallback_name,
                                    description=fallback_description
                                )
                                self.stdout.write(
                                    f'  ✅ Created {lang_code.upper()} translation for {category.slug}'
                                )
                            elif problem['status'] == 'empty_fields':
                                # Update empty fields
                                if 'name' in problem['missing_fields']:
                                    category.name = fallback_name
                                if 'description' in problem['missing_fields']:
                                    category.description = fallback_description
                                category.save()
                                self.stdout.write(
                                    f'  ✅ Updated empty fields in {lang_code.upper()} for {category.slug}'
                                )
                            
                            fixed_count += 1
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'  ❌ Failed to fix {lang_code.upper()} translation for {category.slug}: {str(e)}'
                                )
                            )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully fixed {fixed_count} translation issues!')
            )
        
        elif auto_fix and dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 DRY RUN: Would fix the above issues. Use --fix without --dry-run to apply changes.')
            )
        
        elif not auto_fix:
            self.stdout.write(
                self.style.WARNING('\n💡 Use --fix to automatically create missing translations with fallback content.')
            )
    
    def _generate_fallback_name(self, slug, lang_code):
        """Generate a fallback name based on slug and language."""
        # Convert slug to title case
        name = slug.replace('-', ' ').replace('_', ' ').title()
        
        # Add language-specific prefixes if needed
        if lang_code == 'fa':
            return f'دسته‌بندی {name}'
        elif lang_code == 'tr':
            return f'{name} Kategorisi'
        else:  # English
            return f'{name} Category'
    
    def _generate_fallback_description(self, slug, lang_code):
        """Generate a fallback description based on slug and language."""
        name = slug.replace('-', ' ').replace('_', ' ')
        
        if lang_code == 'fa':
            return f'این دسته‌بندی شامل تورهای مرتبط با {name} می‌باشد.'
        elif lang_code == 'tr':
            return f'Bu kategori {name} ile ilgili turları içermektedir.'
        else:  # English
            return f'This category contains tours related to {name}.'