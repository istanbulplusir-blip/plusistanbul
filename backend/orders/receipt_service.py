"""
Receipt Service for generating order receipts.
"""

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.conf import settings
from decimal import Decimal


class ReceiptService:
    """Service for generating order receipts."""

    @staticmethod
    def generate_receipt_pdf(order):
        """Generate PDF receipt for an order."""
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Order Receipt", title_style))
        story.append(Spacer(1, 12))

        # Company info
        company_info = f"""
        <b>Peykan Tourism</b><br/>
        Order Number: {order.order_number}<br/>
        Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}<br/>
        Status: {order.get_status_display()}
        """
        story.append(Paragraph(company_info, styles['Normal']))
        story.append(Spacer(1, 12))

        # Customer info
        customer_info = f"""
        <b>Customer Information:</b><br/>
        Name: {order.customer_name}<br/>
        Email: {order.customer_email}<br/>
        Phone: {order.customer_phone or 'N/A'}
        """
        story.append(Paragraph(customer_info, styles['Normal']))
        story.append(Spacer(1, 12))

        # Order items
        items_data = [['Product', 'Quantity', 'Unit Price', 'Total']]
        for item in order.items.all():
            items_data.append([
                item.product_title[:30] + '...' if len(item.product_title) > 30 else item.product_title,
                str(item.quantity),
                f"${item.unit_price:.2f}",
                f"${item.total_price:.2f}"
            ])

        # Create table
        table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Order totals
        totals_info = f"""
        <b>Order Summary:</b><br/>
        Subtotal: ${order.subtotal:.2f}<br/>
        Service Fee: ${order.service_fee_amount:.2f}<br/>
        Tax: ${order.tax_amount:.2f}<br/>
        <b>Total: ${order.total_amount:.2f}</b>
        """
        story.append(Paragraph(totals_info, styles['Normal']))

        # Build PDF
        doc.build(story)

        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_receipt_html(order):
        """Generate HTML receipt for web display."""
        items_html = ""
        for item in order.items.all():
            items_html += f"""
            <tr>
                <td>{item.product_title}</td>
                <td class="text-center">{item.quantity}</td>
                <td class="text-right">${item.unit_price:.2f}</td>
                <td class="text-right">${item.total_price:.2f}</td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Order Receipt - {order.order_number}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
                .info {{ margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .text-center {{ text-align: center; }}
                .text-right {{ text-align: right; }}
                .total {{ font-weight: bold; font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Peykan Tourism</h1>
                <h2>Order Receipt</h2>
                <p>Order #: {order.order_number}</p>
                <p>Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                <p>Status: {order.get_status_display()}</p>
            </div>

            <div class="info">
                <h3>Customer Information</h3>
                <p><strong>Name:</strong> {order.customer_name}</p>
                <p><strong>Email:</strong> {order.customer_email}</p>
                <p><strong>Phone:</strong> {order.customer_phone or 'N/A'}</p>
            </div>

            <h3>Order Items</h3>
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th class="text-center">Quantity</th>
                        <th class="text-right">Unit Price</th>
                        <th class="text-right">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <div class="info">
                <h3>Order Summary</h3>
                <p><strong>Subtotal:</strong> ${order.subtotal:.2f}</p>
                <p><strong>Service Fee:</strong> ${order.service_fee_amount:.2f}</p>
                <p><strong>Tax:</strong> ${order.tax_amount:.2f}</p>
                <p class="total"><strong>Total:</strong> ${order.total_amount:.2f}</p>
            </div>
        </body>
        </html>
        """

        return html
