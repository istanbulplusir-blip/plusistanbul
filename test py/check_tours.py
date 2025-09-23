#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourCategory
from django.db import connection

def check_database():
    print("=== Database Connection ===")
    print(f"Database: {connection.settings_dict['NAME']}")
    
    print("\n=== Tour Categories ===")
    categories = TourCategory.objects.all()
    print(f"Total categories: {categories.count()}")
    for cat in categories:
        try:
            print(f"- {cat.name} (ID: {cat.id}, Slug: {cat.slug})")
        except:
            print(f"- Category ID: {cat.id}, Slug: {cat.slug} (Translation missing)")
    
    print("\n=== All Tours ===")
    tours = Tour.objects.all()
    print(f"Total tours: {tours.count()}")
    
    if tours.count() > 0:
        for tour in tours:
            try:
                print(f"- {tour.title} (ID: {tour.id}, Slug: {tour.slug}, Active: {tour.is_active})")
                print(f"  Category: {tour.category.name if tour.category else 'None'}")
                print(f"  Price: {tour.price}")
                print(f"  Status: {getattr(tour, 'status', 'N/A')}")
            except Exception as e:
                print(f"- Tour ID: {tour.id}, Slug: {tour.slug}, Active: {tour.is_active} (Error: {e})")
    else:
        print("No tours found in database!")
    
    print("\n=== Active Tours ===")
    active_tours = Tour.objects.filter(is_active=True)
    print(f"Active tours: {active_tours.count()}")
    
    if active_tours.count() > 0:
        for tour in active_tours:
            try:
                print(f"- {tour.title} (ID: {tour.id}, Slug: {tour.slug})")
            except:
                print(f"- Tour ID: {tour.id}, Slug: {tour.slug} (Translation missing)")
    
    print("\n=== Inactive Tours ===")
    inactive_tours = Tour.objects.filter(is_active=False)
    print(f"Inactive tours: {inactive_tours.count()}")
    
    print("\n=== Published Tours ===")
    try:
        published_tours = Tour.objects.filter(status='published')
        print(f"Published tours: {published_tours.count()}")
    except:
        print("Status field not available")

if __name__ == "__main__":
    check_database()
