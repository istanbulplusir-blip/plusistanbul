"""
Django management command to create sample support FAQs.
"""

from django.core.management.base import BaseCommand
from shared.models import SupportFAQ


class Command(BaseCommand):
    help = 'Create sample support FAQs for Peykan Tourism'

    def handle(self, *args, **options):
        try:
            # Check if support FAQs already exist
            if SupportFAQ.objects.filter(is_active=True).exists():
                self.stdout.write(
                    self.style.WARNING('Support FAQs already exist. Skipping creation.')
                )
                return

            # Create sample support FAQs
            support_faqs = [
                {
                    'category': 'booking',
                    'question': 'How do I book a tour?',
                    'whatsapp_message': 'Hello! I would like to know how to book a tour. Can you please guide me through the booking process?',
                    'order': 1
                },
                {
                    'category': 'booking',
                    'question': 'What payment methods do you accept?',
                    'whatsapp_message': 'Hi! I want to book a tour and would like to know what payment methods you accept. Do you accept credit cards, PayPal, or bank transfers?',
                    'order': 2
                },
                {
                    'category': 'cancellation',
                    'question': 'What is your cancellation policy?',
                    'whatsapp_message': 'Hello! I need to know about your cancellation policy. What are the terms and conditions for canceling a booked tour?',
                    'order': 1
                },
                {
                    'category': 'cancellation',
                    'question': 'Can I get a refund if I cancel?',
                    'whatsapp_message': 'Hi! I booked a tour but might need to cancel. Can you tell me about your refund policy and how much I can get back?',
                    'order': 2
                },
                {
                    'category': 'transfer',
                    'question': 'How do I arrange airport transfer?',
                    'whatsapp_message': 'Hello! I need to arrange airport transfer from Istanbul Airport to my hotel. Can you help me with this service?',
                    'order': 1
                },
                {
                    'category': 'transfer',
                    'question': 'What types of vehicles do you have for transfers?',
                    'whatsapp_message': 'Hi! I want to book a transfer service and would like to know what types of vehicles you have available. Do you have options for different group sizes?',
                    'order': 2
                },
                {
                    'category': 'general',
                    'question': 'What languages do your guides speak?',
                    'whatsapp_message': 'Hello! I\'m interested in your tours and would like to know what languages your tour guides speak. Do you have guides who speak English, Turkish, or other languages?',
                    'order': 1
                },
                {
                    'category': 'general',
                    'question': 'Do you provide hotel pickup for tours?',
                    'whatsapp_message': 'Hi! I\'m staying at a hotel in Istanbul and want to know if you provide hotel pickup service for your tours. What areas do you cover?',
                    'order': 2
                },
                {
                    'category': 'general',
                    'question': 'What should I bring on a tour?',
                    'whatsapp_message': 'Hello! I\'m going on a tour soon and would like to know what I should bring with me. Any specific clothing, equipment, or documents needed?',
                    'order': 3
                }
            ]

            created_faqs = []
            for faq_data in support_faqs:
                faq = SupportFAQ.objects.create(
                    category=faq_data['category'],
                    question=faq_data['question'],
                    whatsapp_message=faq_data['whatsapp_message'],
                    order=faq_data['order'],
                    is_active=True
                )
                created_faqs.append(faq)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {len(created_faqs)} support FAQs'
                )
            )
            
            # Display the created FAQs by category
            for category in ['booking', 'cancellation', 'transfer', 'general']:
                category_faqs = [f for f in created_faqs if f.category == category]
                if category_faqs:
                    self.stdout.write(f'\n{category.title()} FAQs:')
                    for faq in category_faqs:
                        self.stdout.write(f'  - {faq.question}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating support FAQs: {str(e)}')
            )
