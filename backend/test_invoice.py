"""
Test invoice generation with different languages.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import Order
from orders.pdf_service import pdf_generator

# Get first order
order = Order.objects.first()

if order:
    print(f"Testing invoice generation for order: {order.order_number}")
    print(f"Customer: {order.customer_name}")
    print("-" * 50)
    
    # Test English
    print("\n1. Testing English (en)...")
    try:
        pdf_data = pdf_generator.generate_invoice(order, 'en')
        print(f"✅ English invoice generated: {len(pdf_data)} bytes")
        with open('invoice_en.pdf', 'wb') as f:
            f.write(pdf_data)
        print("   Saved to: invoice_en.pdf")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test Persian
    print("\n2. Testing Persian (fa)...")
    try:
        pdf_data = pdf_generator.generate_invoice(order, 'fa')
        print(f"✅ Persian invoice generated: {len(pdf_data)} bytes")
        with open('invoice_fa.pdf', 'wb') as f:
            f.write(pdf_data)
        print("   Saved to: invoice_fa.pdf")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test Arabic
    print("\n3. Testing Arabic (ar)...")
    try:
        pdf_data = pdf_generator.generate_invoice(order, 'ar')
        print(f"✅ Arabic invoice generated: {len(pdf_data)} bytes")
        with open('invoice_ar.pdf', 'wb') as f:
            f.write(pdf_data)
        print("   Saved to: invoice_ar.pdf")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Font info:")
    print(f"Persian font: {pdf_generator.persian_font}")
    print(f"Persian font bold: {pdf_generator.persian_font_bold}")
    
else:
    print("❌ No orders found in database")
