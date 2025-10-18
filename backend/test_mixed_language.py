"""
Test invoice with mixed language content (Persian product name in English invoice).
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import Order, OrderItem
from orders.pdf_service import pdf_generator

# Get first order
order = Order.objects.first()

if order:
    # Get first item and temporarily change its name to Persian
    item = order.items.first()
    if item:
        original_title = item.product_title
        
        # Test 1: Persian name in English invoice
        print("=" * 60)
        print("Test 1: Persian product name in English invoice")
        print("=" * 60)
        item.product_title = "تور ماجراجویی کامل - کوه و طبیعت"
        item.save()
        
        try:
            pdf_data = pdf_generator.generate_invoice(order, 'en')
            print(f"✅ English invoice with Persian name: {len(pdf_data)} bytes")
            with open('invoice_en_persian_name.pdf', 'wb') as f:
                f.write(pdf_data)
            print("   Saved to: invoice_en_persian_name.pdf")
            print("   Product name: تور ماجراجویی کامل - کوه و طبیعت")
            print("   Expected: Should display correctly with Persian font")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 2: English name in Persian invoice
        print("\n" + "=" * 60)
        print("Test 2: English product name in Persian invoice")
        print("=" * 60)
        item.product_title = "Complete Adventure Tour - Mountain & Nature"
        item.save()
        
        try:
            pdf_data = pdf_generator.generate_invoice(order, 'fa')
            print(f"✅ Persian invoice with English name: {len(pdf_data)} bytes")
            with open('invoice_fa_english_name.pdf', 'wb') as f:
                f.write(pdf_data)
            print("   Saved to: invoice_fa_english_name.pdf")
            print("   Product name: Complete Adventure Tour - Mountain & Nature")
            print("   Expected: Should display correctly without RTL shaping")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 3: Mixed content
        print("\n" + "=" * 60)
        print("Test 3: Mixed Persian/English in English invoice")
        print("=" * 60)
        item.product_title = "Istanbul City Tour - تور شهر استانبول"
        item.save()
        
        try:
            pdf_data = pdf_generator.generate_invoice(order, 'en')
            print(f"✅ English invoice with mixed name: {len(pdf_data)} bytes")
            with open('invoice_en_mixed_name.pdf', 'wb') as f:
                f.write(pdf_data)
            print("   Saved to: invoice_en_mixed_name.pdf")
            print("   Product name: Istanbul City Tour - تور شهر استانبول")
            print("   Expected: Both parts should display correctly")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Restore original name
        item.product_title = original_title
        item.save()
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    else:
        print("❌ No order items found")
else:
    print("❌ No orders found in database")
