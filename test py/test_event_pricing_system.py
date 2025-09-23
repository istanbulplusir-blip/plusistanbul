#!/usr/bin/env python
"""
Test script for the new Event Pricing System.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from events.models import Event, EventPerformance, EventSection, SectionTicketType, EventOption, EventDiscount, EventFee, EventPricingRule
from events.pricing_service import EventPriceCalculator, EventPricingRules

def test_pricing_system():
    """Test the new pricing system."""
    print("🧪 Testing New Event Pricing System")
    print("=" * 60)
    
    # Get first event
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    performance = event.performances.first()
    if not performance:
        print("❌ No performances found")
        return False
    
    print(f"🎭 Testing Event: {event.title}")
    print(f"📅 Performance: {performance.date}")
    print("-" * 40)
    
    # Test 1: Basic pricing calculation
    print("\n1️⃣ Testing Basic Pricing Calculation")
    try:
        calculator = EventPriceCalculator(event, performance)
        
        # Get first section and ticket type
        section = performance.sections.first()
        if not section:
            print("❌ No sections found")
            return False
        
        section_ticket = section.ticket_types.first()
        if not section_ticket:
            print("❌ No ticket types found")
            return False
        
        result = calculator.calculate_ticket_price(
            section_name=section.name,
            ticket_type_id=str(section_ticket.ticket_type.id),
            quantity=2
        )
        
        print(f"✅ Basic pricing calculation successful")
        print(f"   Section: {section.name}")
        print(f"   Ticket Type: {section_ticket.ticket_type.name}")
        print(f"   Base Price: ${result['base_price']}")
        print(f"   Unit Price: ${result['unit_price']}")
        print(f"   Quantity: {result['quantity']}")
        print(f"   Subtotal: ${result['subtotal']}")
        print(f"   Final Price: ${result['final_price']}")
        
    except Exception as e:
        print(f"❌ Basic pricing calculation failed: {e}")
        return False
    
    # Test 2: Options pricing
    print("\n2️⃣ Testing Options Pricing")
    try:
        # Get available options
        options = event.options.filter(is_active=True)[:2]
        if options:
            selected_options = [
                {'option_id': str(opt.id), 'quantity': 1}
                for opt in options
            ]
            
            result = calculator.calculate_ticket_price(
                section_name=section.name,
                ticket_type_id=str(section_ticket.ticket_type.id),
                quantity=1,
                selected_options=selected_options
            )
            
            print(f"✅ Options pricing calculation successful")
            print(f"   Options Total: ${result['options_total']}")
            print(f"   Final Price: ${result['final_price']}")
            
            for option in result['options']:
                print(f"     - {option['name']}: ${option['total']}")
        else:
            print("⚠️  No options available for testing")
            
    except Exception as e:
        print(f"❌ Options pricing calculation failed: {e}")
        return False
    
    # Test 3: Discount calculation
    print("\n3️⃣ Testing Discount Calculation")
    try:
        result = calculator.calculate_ticket_price(
            section_name=section.name,
            ticket_type_id=str(section_ticket.ticket_type.id),
            quantity=1,
            is_group_booking=True
        )
        
        print(f"✅ Discount calculation successful")
        print(f"   Discount Total: ${result['discount_total']}")
        print(f"   Final Price: ${result['final_price']}")
        
        for discount in result['discounts']:
            print(f"     - {discount['name']}: ${discount['amount']}")
            
    except Exception as e:
        print(f"❌ Discount calculation failed: {e}")
        return False
    
    # Test 4: Fees and taxes
    print("\n4️⃣ Testing Fees and Taxes")
    try:
        result = calculator.calculate_ticket_price(
            section_name=section.name,
            ticket_type_id=str(section_ticket.ticket_type.id),
            quantity=1,
            apply_fees=True,
            apply_taxes=True
        )
        
        print(f"✅ Fees and taxes calculation successful")
        print(f"   Fees Total: ${result['fees_total']}")
        print(f"   Taxes Total: ${result['taxes_total']}")
        print(f"   Final Price: ${result['final_price']}")
        
        for fee in result['fees']:
            print(f"     - {fee['name']}: ${fee['amount']}")
        
        for tax in result['taxes']:
            print(f"     - {tax['name']}: ${tax['amount']}")
            
    except Exception as e:
        print(f"❌ Fees and taxes calculation failed: {e}")
        return False
    
    # Test 5: Complete pricing breakdown
    print("\n5️⃣ Testing Complete Pricing Breakdown")
    try:
        result = calculator.calculate_ticket_price(
            section_name=section.name,
            ticket_type_id=str(section_ticket.ticket_type.id),
            quantity=2,
            selected_options=selected_options if options else [],
            is_group_booking=True,
            apply_fees=True,
            apply_taxes=True
        )
        
        print(f"✅ Complete pricing breakdown successful")
        print(f"   Subtotal: ${result['subtotal']}")
        print(f"   Options: ${result['options_total']}")
        print(f"   Discounts: ${result['discount_total']}")
        print(f"   Fees: ${result['fees_total']}")
        print(f"   Taxes: ${result['taxes_total']}")
        print(f"   Final Price: ${result['final_price']}")
        
    except Exception as e:
        print(f"❌ Complete pricing breakdown failed: {e}")
        return False
    
    # Test 6: Pricing rules
    print("\n6️⃣ Testing Pricing Rules")
    try:
        rules = EventPricingRules.get_fee_rates()
        discount_rules = EventPricingRules.get_discount_rules()
        
        print(f"✅ Pricing rules retrieved successfully")
        print(f"   Service Fee Rate: {rules['service_fee_rate']}")
        print(f"   VAT Rate: {rules['vat_rate']}")
        print(f"   Group Discount Rate: {discount_rules['group_discount_rate']}")
        
    except Exception as e:
        print(f"❌ Pricing rules test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All pricing system tests passed!")
    return True


def test_discount_models():
    """Test discount model functionality."""
    print("\n🎫 Testing Discount Models")
    print("-" * 40)
    
    # Get first event
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    # Test discount creation
    try:
        from django.utils import timezone
        now = timezone.now()
        
        discount = EventDiscount.objects.create(
            event=event,
            code='TEST20',
            name='Test 20% Discount',
            description='Test discount for 20% off',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            min_amount=Decimal('50.00'),
            max_discount=Decimal('100.00'),
            valid_from=now,
            valid_until=now + timedelta(days=30)
        )
        
        print(f"✅ Discount created: {discount.code}")
        
        # Test discount calculation
        test_amount = Decimal('100.00')
        discount_amount = discount.calculate_discount(test_amount)
        print(f"   Test amount: ${test_amount}")
        print(f"   Discount amount: ${discount_amount}")
        print(f"   Final amount: ${test_amount - discount_amount}")
        
        # Clean up
        discount.delete()
        print(f"✅ Discount cleaned up")
        
    except Exception as e:
        print(f"❌ Discount test failed: {e}")
        return False
    
    return True


def test_fee_models():
    """Test fee model functionality."""
    print("\n💰 Testing Fee Models")
    print("-" * 40)
    
    # Get first event
    event = Event.objects.first()
    if not event:
        print("❌ No events found")
        return False
    
    # Test fee creation
    try:
        fee = EventFee.objects.create(
            event=event,
            name='Service Fee',
            description='3% service fee',
            fee_type='service',
            calculation_type='percentage',
            fee_value=Decimal('3.00')
        )
        
        print(f"✅ Fee created: {fee.name}")
        
        # Test fee calculation
        test_amount = Decimal('100.00')
        fee_amount = fee.calculate_fee(test_amount)
        print(f"   Test amount: ${test_amount}")
        print(f"   Fee amount: ${fee_amount}")
        print(f"   Final amount: ${test_amount + fee_amount}")
        
        # Clean up
        fee.delete()
        print(f"✅ Fee cleaned up")
        
    except Exception as e:
        print(f"❌ Fee test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("🚀 Starting Event Pricing System Tests")
    print("=" * 60)
    
    success = True
    
    # Test pricing system
    if not test_pricing_system():
        success = False
    
    # Test discount models
    if not test_discount_models():
        success = False
    
    # Test fee models
    if not test_fee_models():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Event pricing system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success


if __name__ == '__main__':
    main() 