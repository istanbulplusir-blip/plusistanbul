"""
Test Runner for Transfer Product Testing
Runs all transfer-related tests with proper configuration
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

def run_transfer_tests():
    """Run all transfer-related tests"""
    test_modules = [
        'test_transfer_pricing_unit',
        'test_transfer_agent_integration', 
        'test_transfer_performance'
    ]
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    print("🚀 Starting Transfer Product Test Suite")
    print("=" * 50)
    
    for module in test_modules:
        print(f"\n📋 Running {module}...")
        failures = test_runner.run_tests([module])
        
        if failures:
            print(f"❌ {module} failed with {failures} failures")
        else:
            print(f"✅ {module} passed")
    
    print("\n" + "=" * 50)
    print("🎉 Transfer Product Test Suite Complete")

if __name__ == '__main__':
    run_transfer_tests()
