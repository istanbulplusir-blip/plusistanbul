#!/usr/bin/env python
"""
Check transfer options for Isfahan Airport -> Isfahan City Center route
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption

def check_transfer_options():
    """Check transfer options for the specific route"""
    
    print("🔍 Checking Transfer Options for Isfahan Airport -> Isfahan City Center...")
    
    try:
        # Find the specific route
        route = TransferRoute.objects.filter(
            origin__icontains='Isfahan Airport',
            destination__icontains='Isfahan City Center',
            is_active=True
        ).first()
        
        if not route:
            print("❌ Route not found")
            return False
            
        print(f"📍 Found route: {route.origin} → {route.destination}")
        print(f"🆔 Route ID: {route.id}")
        
        # Check pricing options for this route
        pricing_options = TransferRoutePricing.objects.filter(route=route, is_active=True)
        print(f"\n🚗 Vehicle Types Available: {pricing_options.count()}")
        
        for pricing in pricing_options:
            print(f"   - {pricing.vehicle_name} ({pricing.vehicle_type}) - ${pricing.base_price}")
        
        # Check transfer options for this route
        transfer_options = TransferOption.objects.filter(route=route, is_active=True)
        print(f"\n🎯 Transfer Options Available: {transfer_options.count()}")
        
        if transfer_options.count() > 0:
            for option in transfer_options:
                try:
                    name = option.name or f"Option {option.id}"
                    description = option.description or "No description"
                    print(f"   - {name}: ${option.price} ({description})")
                    print(f"     ID: {option.id}, Type: {option.option_type}, Active: {option.is_active}")
                except Exception as e:
                    print(f"   - Option {option.id}: ${option.price} (Translation error: {str(e)})")
                    print(f"     ID: {option.id}, Type: {option.option_type}, Active: {option.is_active}")
        else:
            print("   No transfer options found for this route")
        
        # Check if there are any global transfer options
        global_options = TransferOption.objects.filter(route__isnull=True, is_active=True)
        print(f"\n🌍 Global Transfer Options: {global_options.count()}")
        
        if global_options.count() > 0:
            for option in global_options:
                try:
                    name = option.name or f"Option {option.id}"
                    description = option.description or "No description"
                    print(f"   - {name}: ${option.price} ({description})")
                    print(f"     ID: {option.id}, Type: {option.option_type}, Active: {option.is_active}")
                except Exception as e:
                    print(f"   - Option {option.id}: ${option.price} (Translation error: {str(e)})")
                    print(f"     ID: {option.id}, Type: {option.option_type}, Active: {option.is_active}")
        
        # Check all routes to see which ones have options
        print(f"\n📊 Summary of all routes with options:")
        all_routes = TransferRoute.objects.filter(is_active=True)
        routes_with_options = 0
        
        for route_item in all_routes:
            route_options = TransferOption.objects.filter(route=route_item, is_active=True)
            if route_options.count() > 0:
                routes_with_options += 1
                print(f"   - {route_item.origin} → {route_item.destination}: {route_options.count()} options")
        
        print(f"\n📈 Total routes with options: {routes_with_options}/{all_routes.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    success = check_transfer_options()
    sys.exit(0 if success else 1)
