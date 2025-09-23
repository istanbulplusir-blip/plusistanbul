#!/usr/bin/env python
"""
Check route settings for round trip discount
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute

def check_route_settings():
    """Check route settings"""
    
    print("🔍 Checking Route Settings...")
    
    try:
        # Get Isfahan route
        route = TransferRoute.objects.filter(
            origin__icontains='Isfahan Airport',
            destination__icontains='Isfahan City Center'
        ).first()
        
        if not route:
            print("❌ Route not found")
            return False
            
        print(f"📍 Route: {route.origin} → {route.destination}")
        print(f"🕐 Round Trip Discount Enabled: {route.round_trip_discount_enabled}")
        print(f"💰 Round Trip Discount: {route.round_trip_discount_percentage}%")
        print(f"⏰ Peak Hour Surcharge: {route.peak_hour_surcharge}%")
        print(f"🌙 Midnight Surcharge: {route.midnight_surcharge}%")
        
        # Enable round trip discount for testing
        if not route.round_trip_discount_enabled:
            print("\n🔧 Enabling round trip discount for testing...")
            route.round_trip_discount_enabled = True
            route.save()
            print("✅ Round trip discount enabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_route_settings()
    sys.exit(0 if success else 1)
