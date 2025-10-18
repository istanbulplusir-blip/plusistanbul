"""
Multi-language translations for invoice/receipt generation.
"""

INVOICE_TRANSLATIONS = {
    'en': {
        # Header
        'invoice_title': 'Sales Invoice',
        'receipt_title': 'Payment Receipt',
        'order_number': 'Order Number',
        'date': 'Date',
        'invoice_number': 'Invoice #',
        
        # Company Info
        'company_name': 'Peykan Tourism',
        'company_address': 'Tehran, Iran',
        'company_phone': '+98 21 1234 5678',
        'company_email': 'info@peykantourism.com',
        'company_website': 'www.peykantourism.com',
        
        # Customer Info
        'billing_information': 'Billing Information',
        'customer_name': 'Customer Name',
        'email': 'Email',
        'phone': 'Phone',
        'address': 'Address',
        
        # Items Table
        'item': 'Item',
        'description': 'Description',
        'quantity': 'Qty',
        'unit_price': 'Unit Price',
        'total': 'Total',
        'product': 'Product',
        'booking_date': 'Booking Date',
        'booking_time': 'Booking Time',
        'variant_type': 'Type',
        'participants': 'Participants',
        'adult': 'Adult',
        'child': 'Child',
        'infant': 'Infant',
        'free': 'Free',
        'options': 'Options',
        
        # Totals
        'subtotal': 'Subtotal',
        'discount': 'Discount',
        'tax': 'Tax',
        'service_fee': 'Service Fee',
        'total_amount': 'Total Amount',
        'amount_paid': 'Amount Paid',
        'balance_due': 'Balance Due',
        
        # Payment
        'payment_status': 'Payment Status',
        'payment_method': 'Payment Method',
        'paid': 'Paid',
        'pending': 'Pending',
        'cancelled': 'Cancelled',
        
        # Footer
        'thank_you': 'Thank you for your business!',
        'terms': 'Terms & Conditions',
        'notes': 'Notes',
        'signature': 'Authorized Signature',
        
        # Status
        'confirmed': 'Confirmed',
        'completed': 'Completed',
    },
    
    'fa': {
        # Header
        'invoice_title': 'فاکتور فروش',
        'receipt_title': 'رسید پرداخت',
        'order_number': 'شماره سفارش',
        'date': 'تاریخ',
        'invoice_number': 'شماره فاکتور',
        
        # Company Info
        'company_name': 'گردشگری پیکان',
        'company_address': 'تهران، ایران',
        'company_phone': '۰۲۱-۱۲۳۴۵۶۷۸',
        'company_email': 'info@peykantourism.com',
        'company_website': 'www.peykantourism.com',
        
        # Customer Info
        'billing_information': 'اطلاعات صورتحساب',
        'customer_name': 'نام مشتری',
        'email': 'ایمیل',
        'phone': 'تلفن',
        'address': 'آدرس',
        
        # Items Table
        'item': 'آیتم',
        'description': 'توضیحات',
        'quantity': 'تعداد',
        'unit_price': 'قیمت واحد',
        'total': 'جمع',
        'product': 'محصول',
        'booking_date': 'تاریخ رزرو',
        'booking_time': 'زمان رزرو',
        'variant_type': 'نوع',
        'participants': 'شرکت‌کنندگان',
        'adult': 'بزرگسال',
        'child': 'کودک',
        'infant': 'نوزاد',
        'free': 'رایگان',
        'options': 'گزینه‌ها',
        
        # Totals
        'subtotal': 'جمع جزء',
        'discount': 'تخفیف',
        'tax': 'مالیات',
        'service_fee': 'کارمزد خدمات',
        'total_amount': 'مبلغ قابل پرداخت',
        'amount_paid': 'مبلغ پرداخت شده',
        'balance_due': 'مانده حساب',
        
        # Payment
        'payment_status': 'وضعیت پرداخت',
        'payment_method': 'روش پرداخت',
        'paid': 'پرداخت شده',
        'pending': 'در انتظار',
        'cancelled': 'لغو شده',
        
        # Footer
        'thank_you': 'از خرید شما متشکریم!',
        'terms': 'شرایط و ضوابط',
        'notes': 'یادداشت‌ها',
        'signature': 'امضای مجاز',
        
        # Status
        'confirmed': 'تایید شده',
        'completed': 'تکمیل شده',
    },
    
    'ar': {
        # Header
        'invoice_title': 'فاتورة المبيعات',
        'receipt_title': 'إيصال الدفع',
        'order_number': 'رقم الطلب',
        'date': 'التاريخ',
        'invoice_number': 'رقم الفاتورة',
        
        # Company Info
        'company_name': 'بيكان للسياحة',
        'company_address': 'طهران، إيران',
        'company_phone': '۰۲۱-۱۲۳۴۵۶۷۸+',
        'company_email': 'info@peykantourism.com',
        'company_website': 'www.peykantourism.com',
        
        # Customer Info
        'billing_information': 'معلومات الفواتير',
        'customer_name': 'اسم العميل',
        'email': 'البريد الإلكتروني',
        'phone': 'الهاتف',
        'address': 'العنوان',
        
        # Items Table
        'item': 'البند',
        'description': 'الوصف',
        'quantity': 'الكمية',
        'unit_price': 'سعر الوحدة',
        'total': 'المجموع',
        'product': 'المنتج',
        'booking_date': 'تاريخ الحجز',
        'booking_time': 'وقت الحجز',
        'variant_type': 'النوع',
        'participants': 'المشاركون',
        'adult': 'بالغ',
        'child': 'طفل',
        'infant': 'رضيع',
        'free': 'مجاني',
        'options': 'الخيارات',
        
        # Totals
        'subtotal': 'المجموع الفرعي',
        'discount': 'الخصم',
        'tax': 'الضريبة',
        'service_fee': 'رسوم الخدمة',
        'total_amount': 'المبلغ الإجمالي',
        'amount_paid': 'المبلغ المدفوع',
        'balance_due': 'الرصيد المستحق',
        
        # Payment
        'payment_status': 'حالة الدفع',
        'payment_method': 'طريقة الدفع',
        'paid': 'مدفوع',
        'pending': 'قيد الانتظار',
        'cancelled': 'ملغى',
        
        # Footer
        'thank_you': 'شكراً لتعاملكم معنا!',
        'terms': 'الشروط والأحكام',
        'notes': 'ملاحظات',
        'signature': 'التوقيع المعتمد',
        
        # Status
        'confirmed': 'مؤكد',
        'completed': 'مكتمل',
    }
}


def get_translation(lang: str, key: str, default: str = '') -> str:
    """
    Get translation for a specific key in the given language.
    
    Args:
        lang: Language code ('en', 'fa', 'ar')
        key: Translation key
        default: Default value if translation not found
        
    Returns:
        Translated string or default value
    """
    lang = lang.lower() if lang else 'en'
    
    # Fallback to English if language not supported
    if lang not in INVOICE_TRANSLATIONS:
        lang = 'en'
    
    return INVOICE_TRANSLATIONS[lang].get(key, default or key)


def is_rtl_language(lang: str) -> bool:
    """Check if language is RTL (Right-to-Left)."""
    return lang.lower() in ['fa', 'ar', 'he', 'ur']
