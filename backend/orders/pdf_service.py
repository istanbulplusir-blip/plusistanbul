"""
PDF receipt generation service.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
import os
from django.conf import settings
from decimal import Decimal

try:
    import arabic_reshaper  # type: ignore
    from bidi.algorithm import get_display  # type: ignore
    HAS_RTL_LIBS = True
except Exception:
    HAS_RTL_LIBS = False
from django.utils import timezone


class PDFReceiptGenerator:
    """Generate PDF receipts for orders."""
    
    def __init__(self):
        self.setup_fonts()
    
    def setup_fonts(self):
        """Setup Persian fonts for PDF."""
        try:
            # Try multiple Persian font sources
            font_loaded = False
            
            # 1. Try local fonts in project
            local_font_candidates = [
                os.path.join('sahel', 'Sahel.ttf'),
                os.path.join('sahel', 'Sahel-Bold.ttf'),
                os.path.join('vazir', 'ttf', 'Vazirmatn-Regular.ttf'),
                os.path.join('vazir', 'ttf', 'Vazirmatn-Bold.ttf'),
                'Vazirmatn-Regular.ttf',
                'Vazirmatn-Bold.ttf',
                'Vazirmatn[wght].ttf',
                'Sahel.ttf',
                'Vazirmatn-Regular.ttf',
                'arabtype.ttf',  # fallback
            ]
            
            for font_file in local_font_candidates:
                local_font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', font_file)
                
                if os.path.exists(local_font_path):
                    try:
                        font_base = os.path.splitext(os.path.basename(local_font_path))[0]
                        # Register as Persian family
                        pdfmetrics.registerFont(TTFont('Persian', local_font_path))
                        self.persian_font = 'Persian'
                        # Try bold pairing if available
                        bold_candidate = local_font_path.replace('Regular', 'Bold').replace('Sahel.ttf', 'Sahel-Bold.ttf')
                        if os.path.exists(bold_candidate):
                            pdfmetrics.registerFont(TTFont('Persian-Bold', bold_candidate))
                            self.persian_font_bold = 'Persian-Bold'
                        else:
                            self.persian_font_bold = self.persian_font
                        print(f"Local Persian font loaded successfully: {font_file}")
                        font_loaded = True
                        break
                    except Exception as font_error:
                        print(f"Failed to load local font {font_file}: {font_error}")
                        continue
            
            # 2. Try system fonts (Windows)
            if not font_loaded:
                system_font_candidates = [
                    'C:/Windows/Fonts/tahoma.ttf',
                    'C:/Windows/Fonts/arial.ttf',
                    'C:/Windows/Fonts/calibri.ttf',
                ]
                
                for font_path in system_font_candidates:
                    if os.path.exists(font_path):
                        try:
                            font_name = os.path.basename(font_path).replace('.ttf', '')
                            pdfmetrics.registerFont(TTFont('SystemPersian', font_path))
                            pdfmetrics.registerFont(TTFont('SystemPersian-Bold', font_path))
                            self.persian_font = 'SystemPersian'
                            self.persian_font_bold = 'SystemPersian-Bold'
                            print(f"System font loaded for Persian support: {font_name}")
                            font_loaded = True
                            break
                        except Exception as font_error:
                            print(f"Failed to load system font {font_path}: {font_error}")
                            continue
            
            # 3. Final fallback
            if not font_loaded:
                print("No suitable font found, using Helvetica")
                self.persian_font = 'Helvetica'
                self.persian_font_bold = 'Helvetica-Bold'
                
        except Exception as e:
            print(f"Font setup error: {e}")
            # Ultimate fallback
            self.persian_font = 'Helvetica'
            self.persian_font_bold = 'Helvetica-Bold'
    

    
    def generate_receipt(self, order, language='en'):
        """
        Generate PDF receipt for an order.
        
        Args:
            order: Order instance
            language: Language code ('en', 'fa', 'ar')
        """
        from .invoice_translations import is_rtl_language, get_translation
        
        buffer = BytesIO()
        is_rtl = is_rtl_language(language)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=f"Receipt-{order.order_number}"
        )
        
        # Build content
        story = []
        
        # Header (simpler than invoice)
        story.extend(self._create_receipt_header(order, language, is_rtl))
        
        # Order details
        story.extend(self._create_order_details(order, language, is_rtl))
        
        # Items table
        story.extend(self._create_items_table_invoice(order, language, is_rtl))
        
        # Totals
        story.extend(self._create_invoice_totals(order, language, is_rtl))
        
        # Footer
        story.extend(self._create_footer(order, language, is_rtl))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _shape(self, text: str, force_rtl: bool = True) -> str:
        """
        Shape text for RTL languages (Persian, Arabic).
        
        Args:
            text: Text to shape
            force_rtl: If True, apply RTL shaping. If False, return as-is.
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Only apply RTL shaping if forced and libraries available
        if force_rtl and HAS_RTL_LIBS and text:
            try:
                reshaped = arabic_reshaper.reshape(text)
                return get_display(reshaped)
            except Exception as e:
                print(f"RTL shaping error: {e}")
                return text
        return text
    
    def _has_rtl_chars(self, text: str) -> bool:
        """
        Check if text contains RTL characters (Persian, Arabic, Hebrew).
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains RTL characters
        """
        if not text:
            return False
        
        # Unicode ranges for RTL scripts
        rtl_ranges = [
            (0x0600, 0x06FF),  # Arabic
            (0x0750, 0x077F),  # Arabic Supplement
            (0x08A0, 0x08FF),  # Arabic Extended-A
            (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
            (0x0590, 0x05FF),  # Hebrew
        ]
        
        for char in text:
            code = ord(char)
            for start, end in rtl_ranges:
                if start <= code <= end:
                    return True
        return False
    
    def _format_text(self, text: str, is_rtl_lang: bool = False) -> str:
        """
        Format text based on language direction and content.
        
        Args:
            text: Text to format
            is_rtl_lang: If True, document language is RTL (but we check content too)
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Only apply RTL shaping if text actually contains RTL characters
        if self._has_rtl_chars(text):
            return self._shape(text, force_rtl=True)
        
        # For LTR text, return as-is
        return text

    def _create_header(self, order):
        """Create PDF header."""
        styles = getSampleStyleSheet()
        
        # Company header style
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Heading1'],
            fontSize=24,
            fontName=self.persian_font_bold,
            textColor=HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Order title style
        order_style = ParagraphStyle(
            'OrderStyle',
            parent=styles['Heading2'],
            fontSize=18,
            fontName=self.persian_font_bold,
            textColor=HexColor('#3498db'),
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        content = []

        # Header with logo
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'assetes', 'Logo-3D-highQ - Copy.png')
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=3.5*cm, height=3.5*cm)
                content.append(img)
            except Exception:
                pass
        
        # Company name (Persian text)
        content.append(Paragraph(self._shape('🏢 پیکان توریسم'), header_style))
        content.append(Spacer(1, 0.5*cm))
        
        # Receipt title (Persian text)
        content.append(Paragraph(self._shape(f'📄 رسید سفارش #{order.order_number}'), order_style))
        content.append(Spacer(1, 0.5*cm))
        
        # Date and status
        date_text = self._shape(f'تاریخ: {order.created_at.strftime("%Y/%m/%d - %H:%M")}')
        status_text = self._shape(f'وضعیت: {self._get_status_persian(order.status)}')
        
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            fontName=self.persian_font,
            alignment=TA_CENTER,
            spaceAfter=5
        )
        
        content.append(Paragraph(date_text, date_style))
        content.append(Paragraph(status_text, date_style))
        content.append(Spacer(1, 1*cm))
        
        return content
    
    def _create_order_details(self, order):
        """Create order details section."""
        styles = getSampleStyleSheet()
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading3'],
            fontSize=14,
            fontName=self.persian_font_bold,
            textColor=HexColor('#2c3e50'),
            alignment=TA_RIGHT,
            spaceAfter=10
        )
        
        content = []
        
        # Customer information section
        content.append(Paragraph(self._shape('👤 اطلاعات مشتری'), section_style))
        
        # Customer details table
        customer_data = [
            [self._shape('نام و نام خانوادگی:'), self._shape(order.customer_name)],
            [self._shape('ایمیل:'), self._shape(order.customer_email)],
            [self._shape('تلفن:'), self._shape(order.customer_phone)],
        ]
        
        customer_table = Table(customer_data, colWidths=[4*cm, 8*cm])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.persian_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f9fa'), colors.white]),
        ]))
        
        content.append(customer_table)
        content.append(Spacer(1, 0.5*cm))
        
        return content
    
    def _create_items_table(self, order):
        """Create items table."""
        styles = getSampleStyleSheet()
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading3'],
            fontSize=14,
            fontName=self.persian_font_bold,
            textColor=HexColor('#2c3e50'),
            alignment=TA_RIGHT,
            spaceAfter=10
        )
        
        content = []
        content.append(Paragraph(self._shape('🛍️ آیتم‌های سفارش'), section_style))
        
        # Common cell styles for RTL
        header_cell_style = ParagraphStyle(
            'HeaderCell', parent=styles['Normal'], fontName=self.persian_font_bold,
            fontSize=12, alignment=TA_RIGHT, textColor=colors.white
        )
        right_cell_style = ParagraphStyle(
            'RightCell', parent=styles['Normal'], fontName=self.persian_font,
            fontSize=10, alignment=TA_RIGHT
        )

        # Table headers (Paragraphs for RTL correctness)
        table_data = [[
            Paragraph(self._shape('محصول'), header_cell_style),
            Paragraph(self._shape('تعداد'), header_cell_style),
            Paragraph(self._shape('قیمت واحد'), header_cell_style),
            Paragraph(self._shape('قیمت کل'), header_cell_style)
        ]]
        
        # Add items
        for item in order.items.all():
            product_name = item.product_title
            if item.variant_name:
                product_name += f" ({item.variant_name})"
            
            table_data.append([
                Paragraph(self._shape(product_name), right_cell_style),
                self._shape(str(item.quantity)),
                self._shape(f'{item.unit_price:,} {item.currency}'),
                self._shape(f'{item.total_price:,} {item.currency}')
            ])
            
            # Add product-specific details
            details = self._get_product_specific_details(item)
            if details:
                for detail in details:
                    table_data.append([
                        Paragraph(self._shape(f"  └─ {detail['name']}"), right_cell_style),
                        '',
                        '',
                        self._shape(detail['value'])
                    ])
        
        # Add total row
        table_data.append([
            Paragraph(self._shape('مجموع کل'), right_cell_style),
            '',
            '',
            self._shape(f'{order.total_amount:,} {order.currency}')
        ])
        
        # Create table
        items_table = Table(table_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
        items_table.setStyle(TableStyle([
            # Header row background/color
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

            # Column aligns
            ('ALIGN', (0, 1), (0, -2), 'RIGHT'),    # Product name
            ('ALIGN', (1, 1), (1, -2), 'CENTER'),   # Quantity
            ('ALIGN', (2, 1), (3, -2), 'RIGHT'),    # Prices

            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f6f3')),
            ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
            ('ALIGN', (3, -1), (3, -1), 'RIGHT'),

            # Grid and valign
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        content.append(items_table)
        content.append(Spacer(1, 1*cm))
        
        return content
    
    def _get_product_specific_details(self, item):
        """Get product-specific details for PDF display."""
        details = []
        
        # Booking date and time
        details.append({
            'name': 'تاریخ رزرو',
            'value': item.booking_date.strftime('%Y/%m/%d')
        })
        
        if item.booking_time:
            details.append({
                'name': 'ساعت رزرو',
                'value': item.booking_time.strftime('%H:%M')
            })
        
        # Product-specific details based on type
        if item.product_type == 'tour':
            details.extend(self._get_tour_details(item))
        elif item.product_type == 'event':
            details.extend(self._get_event_details(item))
        elif item.product_type == 'transfer':
            details.extend(self._get_transfer_details(item))
        
        # Selected options
        if item.selected_options:
            details.extend(self._get_selected_options_details(item))
        
        return details
    
    def _get_tour_details(self, item):
        """Get tour-specific details."""
        details = []
        booking_data = item.booking_data or {}
        
        # Participants
        participants = booking_data.get('participants', {})
        if participants:
            adult_count = participants.get('adult', 0)
            child_count = participants.get('child', 0)
            infant_count = participants.get('infant', 0)
            
            if adult_count > 0:
                details.append({
                    'name': 'بزرگسال',
                    'value': f'{adult_count} نفر'
                })
            if child_count > 0:
                details.append({
                    'name': 'کودک',
                    'value': f'{child_count} نفر'
                })
            if infant_count > 0:
                details.append({
                    'name': 'نوزاد',
                    'value': f'{infant_count} نفر'
                })
        
        # Pickup location
        pickup_location = booking_data.get('pickup_location')
        if pickup_location:
            details.append({
                'name': 'محل سوار شدن',
                'value': pickup_location
            })
        
        # Hotel name
        hotel_name = booking_data.get('hotel_name')
        if hotel_name:
            details.append({
                'name': 'نام هتل',
                'value': hotel_name
            })
        
        return details
    
    def _get_event_details(self, item):
        """Get event-specific details."""
        details = []
        booking_data = item.booking_data or {}
        
        # Performance details
        performance = booking_data.get('performance')
        if performance:
            performance_name = performance.get('name', '')
            if performance_name:
                details.append({
                    'name': 'نمایش',
                    'value': performance_name
                })
            
            performance_date = performance.get('date')
            if performance_date:
                details.append({
                    'name': 'تاریخ نمایش',
                    'value': performance_date
                })
            
            performance_time = performance.get('time')
            if performance_time:
                details.append({
                    'name': 'ساعت نمایش',
                    'value': performance_time
                })
        
        # Seat selection
        seat_info = booking_data.get('seat_info')
        if seat_info:
            seat_type = seat_info.get('type', '')
            seat_number = seat_info.get('number', '')
            if seat_type and seat_number:
                details.append({
                    'name': 'صندلی',
                    'value': f'{seat_type} - {seat_number}'
                })
        
        return details
    
    def _get_transfer_details(self, item):
        """Get transfer-specific details."""
        details = []
        booking_data = item.booking_data or {}
        
        # Route details
        route = booking_data.get('route')
        if route:
            from_location = route.get('from_location', '')
            to_location = route.get('to_location', '')
            if from_location and to_location:
                details.append({
                    'name': 'مسیر',
                    'value': f'{from_location} → {to_location}'
                })
        
        # Vehicle type
        vehicle_type = booking_data.get('vehicle_type')
        if vehicle_type:
            details.append({
                'name': 'نوع وسیله',
                'value': vehicle_type
            })
        
        # Passenger count
        passenger_count = booking_data.get('passenger_count')
        if passenger_count:
            details.append({
                'name': 'تعداد مسافر',
                'value': f'{passenger_count} نفر'
            })
        
        # Pickup address
        pickup_address = booking_data.get('pickup_address')
        if pickup_address:
            details.append({
                'name': 'آدرس سوار شدن',
                'value': pickup_address
            })
        
        # Drop-off address
        dropoff_address = booking_data.get('dropoff_address')
        if dropoff_address:
            details.append({
                'name': 'آدرس پیاده شدن',
                'value': dropoff_address
            })
        
        return details
    
    def _get_selected_options_details(self, item):
        """Get selected options details."""
        details = []
        selected_options = item.selected_options or []
        
        for option in selected_options:
            if isinstance(option, dict):
                option_name = option.get('name', '')
                option_value = option.get('value', '')
                option_price = option.get('price', 0)
                
                if option_name and option_value:
                    value_text = option_value
                    if option_price > 0:
                        value_text += f' (+{option_price:,} {item.currency})'
                    
                    details.append({
                        'name': option_name,
                        'value': value_text
                    })
        
        return details
    
    def _create_footer(self, order, language='en', is_rtl=False):
        """Create PDF footer with multi-language support."""
        from .invoice_translations import get_translation
        
        styles = getSampleStyleSheet()
        font = self.persian_font if is_rtl else 'Helvetica'
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName=font,
            textColor=HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            spaceAfter=5
        )
        
        content = []
        content.append(Spacer(1, 1*cm))
        
        # Thank you message
        thank_you = get_translation(language, 'thank_you', 'Thank you for your business!')
        content.append(Paragraph(self._format_text(f'✨ {thank_you}', is_rtl), footer_style))
        
        content.append(Spacer(1, 0.3*cm))
        
        # Company info
        company_name = get_translation(language, 'company_name', 'Peykan Tourism')
        company_phone = get_translation(language, 'company_phone', '+98 21 1234 5678')
        company_email = get_translation(language, 'company_email', 'info@peykantourism.com')
        
        contact_text = f'{company_phone} | {company_email}'
        
        content.append(Paragraph(self._format_text(f'📞 {contact_text}', is_rtl), footer_style))
        content.append(Paragraph(self._format_text(f'© 2025 {company_name}', is_rtl), footer_style))
        
        return content
    
    def _get_status_persian(self, status):
        """Get Persian status label."""
        status_map = {
            'pending': 'در انتظار',
            'confirmed': 'تایید شده',
            'cancelled': 'لغو شده',
            'completed': 'تکمیل شده'
        }
        return status_map.get(status, status)

    # --- Invoice generation ---
    def generate_invoice(self, order, language='en'):
        """
        Generate PDF invoice for an order.
        
        Args:
            order: Order instance
            language: Language code ('en', 'fa', 'ar')
        """
        from .invoice_translations import is_rtl_language
        
        buffer = BytesIO()
        is_rtl = is_rtl_language(language)
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=f"Invoice-{order.order_number}"
        )

        story = []
        story.extend(self._create_invoice_header(order, language, is_rtl))
        story.extend(self._create_invoice_billing(order, language, is_rtl))
        story.extend(self._create_items_table_invoice(order, language, is_rtl))
        story.extend(self._create_invoice_totals(order, language, is_rtl))
        story.extend(self._create_footer(order, language, is_rtl))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data

    def _create_invoice_header(self, order, language='en', is_rtl=False):
        """Create invoice header with multi-language support."""
        from .invoice_translations import get_translation
        
        styles = getSampleStyleSheet()
        font = self.persian_font if is_rtl else 'Helvetica'
        font_bold = self.persian_font_bold if is_rtl else 'Helvetica-Bold'
        alignment = TA_RIGHT if is_rtl else TA_CENTER
        
        title_style = ParagraphStyle(
            'InvoiceTitle', parent=styles['Heading1'], fontSize=22, fontName=font_bold,
            alignment=TA_CENTER, textColor=HexColor('#2c3e50'), spaceAfter=12
        )
        sub_style = ParagraphStyle(
            'InvoiceSub', parent=styles['Normal'], fontSize=11, fontName=font,
            alignment=TA_CENTER, textColor=HexColor('#7f8c8d'), spaceAfter=6
        )
        
        content = []
        
        # Logo
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'assetes', 'Logo-3D-highQ - Copy.png')
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=3.5*cm, height=3.5*cm)
                content.append(img)
            except Exception:
                pass
        
        # Title
        title = get_translation(language, 'invoice_title', 'Invoice')
        content.append(Paragraph(self._format_text(f'📄 {title}', is_rtl), title_style))
        
        # Order info
        order_label = get_translation(language, 'order_number', 'Order Number')
        date_label = get_translation(language, 'date', 'Date')
        
        order_text = f'{order_label}: {order.order_number}'
        date_text = f'{date_label}: {order.created_at.strftime("%Y/%m/%d - %H:%M")}'
        
        content.append(Paragraph(self._format_text(order_text, is_rtl), sub_style))
        content.append(Paragraph(self._format_text(date_text, is_rtl), sub_style))
        content.append(Spacer(1, 0.5*cm))
        
        return content

    def _create_invoice_billing(self, order, language='en', is_rtl=False):
        """Create billing information section with multi-language support."""
        from .invoice_translations import get_translation
        
        styles = getSampleStyleSheet()
        font = self.persian_font if is_rtl else 'Helvetica'
        font_bold = self.persian_font_bold if is_rtl else 'Helvetica-Bold'
        alignment = TA_RIGHT if is_rtl else TA_LEFT
        
        section_style = ParagraphStyle(
            'Section', parent=styles['Heading3'], fontSize=14,
            fontName=font_bold, alignment=alignment, spaceAfter=8,
            textColor=HexColor('#2c3e50')
        )
        
        content = []
        
        # Section title
        title = get_translation(language, 'billing_information', 'Billing Information')
        content.append(Paragraph(self._format_text(f'👤 {title}', is_rtl), section_style))
        
        # Customer data
        name_label = get_translation(language, 'customer_name', 'Customer Name')
        email_label = get_translation(language, 'email', 'Email')
        phone_label = get_translation(language, 'phone', 'Phone')
        address_label = get_translation(language, 'address', 'Address')
        
        # Get billing address from order notes or empty
        billing_address = getattr(order, 'billing_address', '') or getattr(order, 'notes', '') or ''
        
        data = [
            [self._format_text(name_label, is_rtl), 
             self._format_text(order.customer_name, is_rtl)],
            [self._format_text(email_label, is_rtl), 
             order.customer_email],
            [self._format_text(phone_label, is_rtl), 
             order.customer_phone],
            [self._format_text(address_label, is_rtl), 
             self._format_text(billing_address, is_rtl)],
        ]
        
        # Adjust column widths based on direction
        col_widths = [4*cm, 10*cm] if is_rtl else [4*cm, 10*cm]
        table = Table(data, colWidths=col_widths)
        
        table_style = [
            ('FONTNAME', (0, 0), (-1, -1), font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT' if is_rtl else 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT' if is_rtl else 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]
        
        table.setStyle(TableStyle(table_style))
        content.append(table)
        content.append(Spacer(1, 0.5*cm))
        
        return content

    def _create_receipt_header(self, order, language='en', is_rtl=False):
        """Create receipt header (simpler than invoice)."""
        from .invoice_translations import get_translation
        
        styles = getSampleStyleSheet()
        font = self.persian_font if is_rtl else 'Helvetica'
        font_bold = self.persian_font_bold if is_rtl else 'Helvetica-Bold'
        
        title_style = ParagraphStyle(
            'ReceiptTitle', parent=styles['Heading1'], fontSize=20, fontName=font_bold,
            alignment=TA_CENTER, textColor=HexColor('#27ae60'), spaceAfter=12
        )
        sub_style = ParagraphStyle(
            'ReceiptSub', parent=styles['Normal'], fontSize=10, fontName=font,
            alignment=TA_CENTER, textColor=HexColor('#7f8c8d'), spaceAfter=6
        )
        
        content = []
        
        # Logo
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'assetes', 'Logo-3D-highQ - Copy.png')
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=3*cm, height=3*cm)
                content.append(img)
            except Exception:
                pass
        
        # Title
        title = get_translation(language, 'receipt_title', 'Receipt')
        content.append(Paragraph(self._format_text(f'🧾 {title}', is_rtl), title_style))
        
        # Order info
        order_label = get_translation(language, 'order_number', 'Order Number')
        date_label = get_translation(language, 'date', 'Date')
        
        order_text = f'{order_label}: {order.order_number}'
        date_text = f'{date_label}: {order.created_at.strftime("%Y/%m/%d - %H:%M")}'
        
        content.append(Paragraph(self._format_text(order_text, is_rtl), sub_style))
        content.append(Paragraph(self._format_text(date_text, is_rtl), sub_style))
        content.append(Spacer(1, 0.5*cm))
        
        return content

    def _create_order_details(self, order, language='en', is_rtl=False):
        """Create order details section."""
        from .invoice_translations import get_translation
        
        font = self.persian_font if is_rtl else 'Helvetica'
        font_bold = self.persian_font_bold if is_rtl else 'Helvetica-Bold'
        
        styles = getSampleStyleSheet()
        section_style = ParagraphStyle(
            'Section', parent=styles['Heading3'], fontSize=12,
            fontName=font_bold, alignment=TA_RIGHT if is_rtl else TA_LEFT,
            spaceAfter=8, textColor=HexColor('#2c3e50')
        )
        
        content = []
        
        # Customer info
        name_label = get_translation(language, 'customer_name', 'Customer')
        email_label = get_translation(language, 'email', 'Email')
        status_label = get_translation(language, 'payment_status', 'Status')
        
        # Get status translation
        status_key = order.payment_status.lower()
        status_text = get_translation(language, status_key, order.payment_status)
        
        info_text = f"""
        {name_label}: {order.customer_name}<br/>
        {email_label}: {order.customer_email}<br/>
        {status_label}: {status_text}
        """
        
        info_style = ParagraphStyle(
            'Info', parent=styles['Normal'], fontSize=10, fontName=font,
            alignment=TA_RIGHT if is_rtl else TA_LEFT, spaceAfter=6
        )
        
        content.append(Paragraph(self._format_text(info_text, is_rtl), info_style))
        
        content.append(Spacer(1, 0.3*cm))
        
        return content

    def _create_items_table_invoice(self, order, language='en', is_rtl=False):
        """Create detailed items table for invoice with multi-language support."""
        from .invoice_translations import get_translation
        
        font = self.persian_font if is_rtl else 'Helvetica'
        font_bold = self.persian_font_bold if is_rtl else 'Helvetica-Bold'
        
        styles = getSampleStyleSheet()
        section_style = ParagraphStyle(
            'Section', parent=styles['Heading3'], fontSize=14,
            fontName=font_bold, alignment=TA_RIGHT if is_rtl else TA_LEFT,
            spaceAfter=8, textColor=HexColor('#2c3e50')
        )
        
        detail_style = ParagraphStyle(
            'Detail', parent=styles['Normal'], fontSize=8,
            fontName=font, alignment=TA_RIGHT if is_rtl else TA_LEFT,
            textColor=HexColor('#7f8c8d'), leading=10
        )
        
        content = []
        
        # Section title
        items_title = get_translation(language, 'item', 'Items')
        content.append(Paragraph(self._format_text(f'📦 {items_title}', is_rtl), section_style))
        
        # Process each item with details
        for idx, item in enumerate(order.items.all(), 1):
            # Item header with product name
            # Use appropriate font based on product name content
            product_has_rtl = self._has_rtl_chars(item.product_title)
            header_font = self.persian_font_bold if product_has_rtl else font_bold
            header_align = TA_RIGHT if product_has_rtl else (TA_RIGHT if is_rtl else TA_LEFT)
            
            item_header_style = ParagraphStyle(
                'ItemHeader', parent=styles['Normal'], fontSize=11,
                fontName=header_font, alignment=header_align,
                textColor=HexColor('#2c3e50'), spaceAfter=4
            )
            
            product_name = f"{idx}. {item.product_title}"
            content.append(Paragraph(self._format_text(product_name, is_rtl), item_header_style))
            
            # Build details list
            details = []
            
            # Variant
            if item.variant_name:
                variant_label = get_translation(language, 'variant_type', 'Type')
                details.append(f"• {variant_label}: {item.variant_name}")
            
            # Booking date and time
            if item.booking_date:
                date_label = get_translation(language, 'booking_date', 'Date')
                details.append(f"• {date_label}: {item.booking_date.strftime('%Y-%m-%d')}")
            
            if item.booking_time:
                time_label = get_translation(language, 'booking_time', 'Time')
                details.append(f"• {time_label}: {item.booking_time.strftime('%H:%M')}")
            
            # Participants (for tours)
            if item.booking_data and 'participants' in item.booking_data:
                participants = item.booking_data['participants']
                if participants.get('adult', 0) > 0:
                    details.append(f"• Adult: {participants['adult']} x {item.unit_price:,.2f} {item.currency}")
                if participants.get('child', 0) > 0:
                    child_price = float(item.unit_price) * 0.7
                    details.append(f"• Child: {participants['child']} x {child_price:,.2f} {item.currency}")
                if participants.get('infant', 0) > 0:
                    details.append(f"• Infant: {participants['infant']} (Free)")
            
            # Selected options
            if item.selected_options and isinstance(item.selected_options, list):
                for option in item.selected_options:
                    if isinstance(option, dict):
                        opt_name = option.get('name', 'Option')
                        opt_qty = option.get('quantity', 1)
                        opt_price = option.get('price', 0)
                        if opt_price > 0:
                            details.append(f"• {opt_name}: {opt_qty} x {opt_price:,.2f} {item.currency}")
            
            # Special requests
            if item.booking_data and 'special_requests' in item.booking_data:
                special_req = item.booking_data['special_requests']
                if special_req:
                    req_label = get_translation(language, 'notes', 'Notes')
                    details.append(f"• {req_label}: {special_req[:50]}")
            
            # Create details paragraph
            if details:
                # For RTL, format each line separately to avoid HTML tag issues
                if is_rtl:
                    for detail in details:
                        content.append(Paragraph(self._format_text(detail, is_rtl), detail_style))
                else:
                    details_text = '<br/>'.join(details)
                    content.append(Paragraph(details_text, detail_style))
            
            # Price summary for this item
            price_data = [
                [
                    self._format_text(get_translation(language, 'quantity', 'Quantity'), is_rtl),
                    self._format_text(str(item.quantity), is_rtl)
                ],
                [
                    self._format_text(get_translation(language, 'unit_price', 'Unit Price'), is_rtl),
                    self._format_text(f"{item.unit_price:,.2f} {item.currency}", is_rtl)
                ],
                [
                    self._format_text(get_translation(language, 'total', 'Total'), is_rtl),
                    self._format_text(f"{item.total_price:,.2f} {item.currency}", is_rtl)
                ]
            ]
            
            price_table = Table(price_data, colWidths=[8*cm, 8*cm])
            price_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT' if is_rtl else 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f6f3')),
                ('FONTNAME', (0, -1), (-1, -1), font_bold),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            content.append(price_table)
            content.append(Spacer(1, 0.3*cm))
        
        return content

    def _create_invoice_totals(self, order, language='en', is_rtl=False):
        """Create totals section with multi-language support."""
        from .invoice_translations import get_translation
        
        font = self.persian_font if is_rtl else 'Helvetica'
        font_bold = self.persian_font_bold if is_rtl else 'Helvetica-Bold'
        
        content = []
        
        # Get labels
        subtotal_label = get_translation(language, 'subtotal', 'Subtotal')
        discount_label = get_translation(language, 'discount', 'Discount')
        tax_label = get_translation(language, 'tax', 'Tax')
        service_fee_label = get_translation(language, 'service_fee', 'Service Fee')
        total_label = get_translation(language, 'total_amount', 'Total Amount')
        
        # Prepare data
        labels = [
            (subtotal_label, order.subtotal or 0),
            (service_fee_label, order.service_fee_amount or 0),
            (tax_label, order.tax_amount or 0),
            (discount_label, -(order.discount_amount or 0)),
            (total_label, order.total_amount),
        ]
        
        # Format amounts
        data = []
        for lbl, amount in labels:
            formatted_amount = f"{abs(amount):,.2f} {order.currency}"
            if amount < 0:
                formatted_amount = f"-{formatted_amount}"
            
            data.append([
                self._format_text(lbl, is_rtl),
                self._format_text(formatted_amount, is_rtl)
            ])
        
        # Create table
        table = Table(data, colWidths=[10*cm, 6*cm])
        
        table_style = [
            ('FONTNAME', (0, 0), (-1, -2), font),
            ('FONTNAME', (0, -1), (-1, -1), font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT' if is_rtl else 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f6f3')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]
        
        table.setStyle(TableStyle(table_style))
        content.append(table)
        content.append(Spacer(1, 0.5*cm))
        
        return content


# Service instance
pdf_generator = PDFReceiptGenerator()
