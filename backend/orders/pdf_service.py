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
    

    
    def generate_receipt(self, order):
        """Generate PDF receipt for an order."""
        buffer = BytesIO()
        
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
        
        # Header
        story.extend(self._create_header(order))
        
        # Order details
        story.extend(self._create_order_details(order))
        
        # Items table
        story.extend(self._create_items_table(order))
        
        # Footer
        story.extend(self._create_footer(order))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _shape(self, text: str) -> str:
        if not isinstance(text, str):
            text = str(text)
        if HAS_RTL_LIBS and text:
            try:
                reshaped = arabic_reshaper.reshape(text)
                return get_display(reshaped)
            except Exception:
                return text
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
    
    def _create_footer(self, order):
        """Create PDF footer."""
        styles = getSampleStyleSheet()
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName=self.persian_font,
            textColor=HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            spaceAfter=5
        )
        
        content = []
        
        # Contact information
        content.append(Spacer(1, 1*cm))
        content.append(Paragraph(self._shape('📞 اطلاعات تماس'), footer_style))
        content.append(Paragraph(self._shape('تلفن: 021-12345678 | واتساپ: 09123456789'), footer_style))
        content.append(Paragraph(self._shape('ایمیل: support@peykan-tourism.com'), footer_style))
        content.append(Spacer(1, 0.5*cm))
        
        # Legal notice
        content.append(Paragraph(self._shape('© 2025 پیکان توریسم - تمامی حقوق محفوظ است'), footer_style))
        content.append(Paragraph(self._shape(f'تاریخ صدور رسید: {timezone.now().strftime("%Y/%m/%d - %H:%M")}'), footer_style))
        
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
    def generate_invoice(self, order):
        """Generate PDF invoice for an order (فاکتور)."""
        buffer = BytesIO()
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
        story.extend(self._create_invoice_header(order))
        story.extend(self._create_invoice_billing(order))
        story.extend(self._create_items_table(order))
        story.extend(self._create_invoice_totals(order))
        story.extend(self._create_footer(order))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data

    def _create_invoice_header(self, order):
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'InvoiceTitle', parent=styles['Heading1'], fontSize=22, fontName=self.persian_font_bold,
            alignment=TA_CENTER, textColor=HexColor('#2c3e50'), spaceAfter=12
        )
        sub_style = ParagraphStyle(
            'InvoiceSub', parent=styles['Normal'], fontSize=12, fontName=self.persian_font,
            alignment=TA_CENTER, textColor=HexColor('#7f8c8d'), spaceAfter=6
        )
        content = []
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'assetes', 'Logo-3D-highQ - Copy.png')
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=3.5*cm, height=3.5*cm)
                content.append(img)
            except Exception:
                pass
        content.append(Paragraph(self._shape('🧾 فاکتور فروش'), title_style))
        content.append(Paragraph(self._shape(f'شماره سفارش: {order.order_number}'), sub_style))
        content.append(Paragraph(self._shape(f'تاریخ: {order.created_at.strftime("%Y/%m/%d - %H:%M")}'), sub_style))
        content.append(Spacer(1, 0.5*cm))
        return content

    def _create_invoice_billing(self, order):
        styles = getSampleStyleSheet()
        section_style = ParagraphStyle('Section', parent=styles['Heading3'], fontSize=14,
                                       fontName=self.persian_font_bold, alignment=TA_RIGHT, spaceAfter=8)
        content = []
        content.append(Paragraph(self._shape('👤 اطلاعات صورتحساب'), section_style))
        data = [
            [self._shape('نام مشتری'), self._shape(order.customer_name)],
            [self._shape('ایمیل'), self._shape(order.customer_email)],
            [self._shape('تلفن'), self._shape(order.customer_phone)],
            [self._shape('آدرس'), self._shape(order.billing_address or '')],
        ]
        table = Table(data, colWidths=[4*cm, 10*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.persian_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
        ]))
        content.append(table)
        content.append(Spacer(1, 0.5*cm))
        return content

    def _create_invoice_totals(self, order):
        styles = getSampleStyleSheet()
        content = []
        labels = [
            (self._shape('جمع جزء'), order.subtotal),
            (self._shape('تخفیف'), -order.discount_amount),
            (self._shape('مالیات'), order.tax_amount),
            (self._shape('مبلغ قابل پرداخت'), order.total_amount),
        ]
        data = [[lbl, self._shape(f"{amount:,.2f} {order.currency}")] for lbl, amount in labels]
        table = Table(data, colWidths=[8*cm, 6*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.persian_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f6f3')),
            ('FONTNAME', (0, -1), (-1, -1), self.persian_font_bold),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        content.append(table)
        content.append(Spacer(1, 0.5*cm))
        return content


# Service instance
pdf_generator = PDFReceiptGenerator()
