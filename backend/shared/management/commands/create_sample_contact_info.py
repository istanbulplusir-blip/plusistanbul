"""
Django management command to create sample contact information.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from shared.models import ContactInfo


class Command(BaseCommand):
    help = 'Create sample contact information for Peykan Tourism'

    def handle(self, *args, **options):
        try:
            # Check if contact info already exists
            if ContactInfo.objects.filter(is_active=True).exists():
                self.stdout.write(
                    self.style.WARNING('Contact information already exists. Skipping creation.')
                )
                return

            # Create sample contact info
            contact_info = ContactInfo.objects.create(
                company_name='Peykan Tourism Istanbul',
                address='Istanbul, Turkey - Tourism and Travel Services',
                phone_primary='+90 212 555 0123',
                phone_secondary='+90 212 555 0124',
                email_general='info@peykantravelistanbul.com',
                email_support='support@peykantravelistanbul.com',
                email_sales='sales@peykantravelistanbul.com',
                working_hours='9:00 AM - 6:00 PM',
                working_days='Monday - Friday',
                latitude=41.0082,
                longitude=28.9784,
                instagram_url='https://instagram.com/peykantravel',
                telegram_url='https://t.me/peykansupport',
                whatsapp_number='+90 555 123 4567',
                facebook_url='https://facebook.com/peykantravel',
                twitter_url='https://twitter.com/peykantravel',
                linkedin_url='https://linkedin.com/company/peykantravel',
                is_active=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created contact information for {contact_info.company_name}'
                )
            )
            
            # Display the created data
            self.stdout.write(f'WhatsApp: {contact_info.whatsapp_number}')
            self.stdout.write(f'Phone: {contact_info.phone_primary}')
            self.stdout.write(f'Email: {contact_info.email_support}')
            self.stdout.write(f'Working Hours: {contact_info.working_hours}')
            self.stdout.write(f'Working Days: {contact_info.working_days}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating contact information: {str(e)}')
            )
