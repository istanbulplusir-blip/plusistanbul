#!/usr/bin/env python
"""
Setup script for Peykan Tourism Admin Panel.
This script helps configure the admin panel and create initial superuser.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from django.db import transaction

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

User = get_user_model()


def create_superuser():
    """Create a superuser account."""
    print("Creating superuser account...")
    
    try:
        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            print("Superuser already exists!")
            return
        
        # Create superuser
        username = input("Enter username for superuser: ")
        email = input("Enter email for superuser: ")
        password = input("Enter password for superuser: ")
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=input("Enter first name: "),
            last_name=input("Enter last name: "),
            phone_number=input("Enter phone number (optional): ") or None,
            role='admin'
        )
        
        print(f"Superuser '{username}' created successfully!")
        print(f"Email: {email}")
        print(f"Role: {user.role}")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")


def check_admin_configuration():
    """Check if admin configuration is properly set up."""
    print("Checking admin configuration...")
    
    # Check if all admin files exist
    admin_files = [
        'users/admin.py',
        'tours/admin.py',
        'events/admin.py',
        'transfers/admin.py',
        'cart/admin.py',
        'orders/admin.py',
        'payments/admin.py',
        'agents/admin.py',
        'peykan/admin.py'
    ]
    
    missing_files = []
    for file_path in admin_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Missing admin files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("Please ensure all admin files are created.")
    else:
        print("All admin files are present.")
    
    # Check if models are registered
    from django.contrib import admin
    registered_models = []
    
    for model, model_admin in admin.site._registry.items():
        registered_models.append(f"{model._meta.app_label}.{model._meta.model_name}")
    
    print(f"Registered models: {len(registered_models)}")
    for model in sorted(registered_models):
        print(f"  - {model}")


def create_sample_data():
    """Create sample data for testing the admin panel."""
    print("Creating sample data...")
    
    try:
        # Create sample categories
        from tours.models import TourCategory
        from events.models import EventCategory
        
        # Tour categories
        tour_categories = [
            {'name': 'Historical Tours', 'description': 'Explore historical sites and monuments'},
            {'name': 'Adventure Tours', 'description': 'Thrilling adventure and outdoor activities'},
            {'name': 'Cultural Tours', 'description': 'Immerse in local culture and traditions'},
        ]
        
        for cat_data in tour_categories:
            TourCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
        
        # Event categories
        event_categories = [
            {'name': 'Music Events', 'description': 'Live music concerts and performances'},
            {'name': 'Sports Events', 'description': 'Sports competitions and games'},
            {'name': 'Theater Events', 'description': 'Theater plays and performances'},
        ]
        
        for cat_data in event_categories:
            EventCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
        
        print("Sample categories created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")


def run_migrations():
    """Run database migrations."""
    print("Running database migrations...")
    
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}")


def main():
    """Main setup function."""
    print("=" * 50)
    print("Peykan Tourism Admin Panel Setup")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Run database migrations")
        print("2. Check admin configuration")
        print("3. Create superuser account")
        print("4. Create sample data")
        print("5. Run all setup steps")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            run_migrations()
        elif choice == '2':
            check_admin_configuration()
        elif choice == '3':
            create_superuser()
        elif choice == '4':
            create_sample_data()
        elif choice == '5':
            print("Running all setup steps...")
            run_migrations()
            check_admin_configuration()
            create_superuser()
            create_sample_data()
            print("\nSetup completed!")
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main() 