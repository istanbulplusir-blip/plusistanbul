#!/usr/bin/env python
"""
Script to check FAQ categories for duplicates
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from shared.models import FAQ
from collections import Counter

def check_faq_categories():
    """Check for duplicate FAQ categories"""
    print("Checking FAQ categories...")
    
    # Get all FAQ categories
    faqs = FAQ.objects.filter(is_active=True)
    categories = [faq.category for faq in faqs if faq.category]
    
    print(f"Total FAQs: {faqs.count()}")
    print(f"Total categories: {len(set(categories))}")
    
    # Count category occurrences
    category_counts = Counter(categories)
    
    print("\nCategory breakdown:")
    for category, count in category_counts.items():
        print(f"  {category}: {count} FAQs")
    
    # Check for duplicates
    duplicates = [cat for cat, count in category_counts.items() if count > 1]
    
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate categories:")
        for dup in duplicates:
            print(f"  - {dup}")
    else:
        print("\n✅ No duplicate categories found")
    
    # Show sample FAQs for each category
    print("\nSample FAQs by category:")
    for category in sorted(set(categories)):
        sample_faqs = FAQ.objects.filter(category=category, is_active=True)[:3]
        print(f"\n{category}:")
        for faq in sample_faqs:
            print(f"  - {faq.question[:50]}...")

if __name__ == '__main__':
    check_faq_categories()
