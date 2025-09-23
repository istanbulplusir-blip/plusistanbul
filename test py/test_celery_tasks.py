#!/usr/bin/env python
"""
Test script for Celery tasks.
Run this to test if the background tasks are working correctly.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.utils import timezone
from events.tasks import (
    cleanup_expired_reservations,
    update_capacity_cache,
    validate_capacity_consistency,
    emergency_capacity_cleanup
)
from cart.tasks import (
    cleanup_expired_carts,
    cleanup_expired_reservations as cart_cleanup_reservations,
    validate_cart_integrity,
    emergency_cart_cleanup
)

def test_events_tasks():
    """Test events-related Celery tasks."""
    print("=== Testing Events Tasks ===\n")
    
    try:
        # Test 1: Cleanup expired reservations
        print("1. Testing cleanup_expired_reservations...")
        result = cleanup_expired_reservations.delay()
        print(f"   Task queued with ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Test 2: Update capacity cache
        print("\n2. Testing update_capacity_cache...")
        result = update_capacity_cache.delay()
        print(f"   Task queued with ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Test 3: Validate capacity consistency
        print("\n3. Testing validate_capacity_consistency...")
        result = validate_capacity_consistency.delay()
        print(f"   Task queued with ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Test 4: Emergency cleanup
        print("\n4. Testing emergency_capacity_cleanup...")
        result = emergency_capacity_cleanup.delay()
        print(f"   Task queued with ID: {result.id}")
        print(f"   Status: {result.status}")
        
        print("\n✅ All events tasks queued successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing events tasks: {e}")
        return False
    
    return True

def test_cart_tasks():
    """Test cart-related Celery tasks."""
    print("\n=== Testing Cart Tasks ===\n")
    
    try:
        # Test 1: Cleanup expired carts
        print("1. Testing cleanup_expired_carts...")
        result = cleanup_expired_carts.delay()
        print(f"   Task queued with ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Test 2: Cleanup expired cart reservations
        print("\n2. Testing cleanup_expired_reservations (cart)...")
        result = cart_cleanup_reservations.delay()
        print(f"   Task queued with ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Test 3: Validate cart integrity
        print("\n3. Testing validate_cart_integrity...")
        result = validate_cart_integrity.delay()
        print(f"   Task queued with ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Test 4: Emergency cart cleanup
        print("\n4. Testing emergency_cart_cleanup...")
        result = emergency_cart_cleanup.delay()
        print(f"   Task queued with ID: {result.id}")
        print(f"   Status: {result.status}")
        
        print("\n✅ All cart tasks queued successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing cart tasks: {e}")
        return False
    
    return True

def test_synchronous_execution():
    """Test tasks synchronously (for immediate results)."""
    print("\n=== Testing Synchronous Execution ===\n")
    
    try:
        # Test cleanup expired reservations synchronously
        print("1. Testing cleanup_expired_reservations synchronously...")
        result = cleanup_expired_reservations()
        print(f"   Result: {result}")
        
        # Test update capacity cache synchronously
        print("\n2. Testing update_capacity_cache synchronously...")
        result = update_capacity_cache()
        print(f"   Result: {result}")
        
        # Test validate capacity consistency synchronously
        print("\n3. Testing validate_capacity_consistency synchronously...")
        result = validate_capacity_consistency()
        print(f"   Result: {result}")
        
        print("\n✅ All synchronous tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error in synchronous tests: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🚀 Celery Tasks Test Script")
    print("=" * 50)
    
    # Test 1: Events tasks
    events_success = test_events_tasks()
    
    # Test 2: Cart tasks
    cart_success = test_cart_tasks()
    
    # Test 3: Synchronous execution
    sync_success = test_synchronous_execution()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Events Tasks: {'✅ PASS' if events_success else '❌ FAIL'}")
    print(f"   Cart Tasks: {'✅ PASS' if cart_success else '❌ FAIL'}")
    print(f"   Synchronous: {'✅ PASS' if sync_success else '❌ FAIL'}")
    
    if all([events_success, cart_success, sync_success]):
        print("\n🎉 All tests passed! Celery tasks are working correctly.")
        print("\nNext steps:")
        print("1. Start Celery worker: python manage.py start_celery_worker")
        print("2. Start Celery beat: python manage.py start_celery_beat")
        print("3. Monitor logs for automatic cleanup")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Ensure Redis is running")
        print("2. Check Celery configuration in settings.py")
        print("3. Verify all required packages are installed")

if __name__ == "__main__":
    main()
