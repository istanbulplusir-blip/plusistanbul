"""
Email templates for order notifications.
"""

def get_order_confirmation_template(order):
    """Generate order confirmation email template."""
    
    items_html = ""
    for item in order.items.all():
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">
                <strong>{item.product_title}</strong>
                {f'<br><small>نوع: {item.variant_name}</small>' if item.variant_name else ''}
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                {item.quantity}
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: left;">
                {item.total_price:,} {item.currency}
            </td>
        </tr>
        """
    
    template = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تایید سفارش - پیکان توریسم</title>
        <style>
            body {{ font-family: 'Tahoma', 'Arial', sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }}
            .content {{ padding: 30px 20px; }}
            .order-details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .items-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .items-table th {{ background: #e9ecef; padding: 12px; text-align: right; }}
            .total-row {{ background: #e3f2fd; font-weight: bold; }}
            .footer {{ background: #343a40; color: white; padding: 20px; text-align: center; font-size: 14px; }}
            .status-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: bold; }}
            .status-confirmed {{ background: #d4edda; color: #155724; }}
            .status-pending {{ background: #fff3cd; color: #856404; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 سفارش شما تایید شد!</h1>
                <p>سفارش شماره: #{order.order_number}</p>
            </div>
            
            <div class="content">
                <p>سلام <strong>{order.customer_name}</strong> عزیز،</p>
                <p>سفارش شما با موفقیت تایید شد و در حال پردازش است.</p>
                
                <div class="order-details">
                    <h3>جزئیات سفارش</h3>
                    <p><strong>شماره سفارش:</strong> #{order.order_number}</p>
                    <p><strong>تاریخ سفارش:</strong> {order.created_at.strftime('%Y/%m/%d - %H:%M')}</p>
                    <p><strong>وضعیت:</strong> 
                        <span class="status-badge status-confirmed">تایید شده</span>
                    </p>
                </div>
                
                <h3>آیتم‌های سفارش</h3>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>محصول</th>
                            <th style="text-align: center;">تعداد</th>
                            <th style="text-align: left;">قیمت</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                        <tr class="total-row">
                            <td colspan="2" style="padding: 15px; text-align: center;">
                                <strong>مجموع کل</strong>
                            </td>
                            <td style="padding: 15px; text-align: left;">
                                <strong>{order.total_amount:,} {order.currency}</strong>
                            </td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>📞 اطلاعات تماس</h4>
                    <p><strong>تلفن پشتیبانی:</strong> 021-12345678</p>
                    <p><strong>واتساپ:</strong> 09123456789</p>
                    <p><strong>ایمیل:</strong> support@peykan-tourism.com</p>
                </div>
                
                <p>در صورت داشتن هرگونه سوال، با ما تماس بگیرید.</p>
                <p>از اعتماد شما متشکریم! 🙏</p>
            </div>
            
            <div class="footer">
                <p>© 2025 پیکان توریسم - تمامی حقوق محفوظ است</p>
                <p>این ایمیل به صورت خودکار ارسال شده است.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return template


def get_order_status_change_template(order, old_status, new_status):
    """Generate order status change email template."""
    
    status_messages = {
        'pending': 'در انتظار بررسی',
        'confirmed': 'تایید شد',
        'cancelled': 'لغو شد',
        'completed': 'تکمیل شد'
    }
    
    status_colors = {
        'pending': '#fff3cd',
        'confirmed': '#d4edda',
        'cancelled': '#f8d7da',
        'completed': '#d1ecf1'
    }
    
    status_text_colors = {
        'pending': '#856404',
        'confirmed': '#155724',
        'cancelled': '#721c24',
        'completed': '#0c5460'
    }
    
    template = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تغییر وضعیت سفارش - پیکان توریسم</title>
        <style>
            body {{ font-family: 'Tahoma', 'Arial', sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }}
            .content {{ padding: 30px 20px; }}
            .status-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: bold; }}
            .footer {{ background: #343a40; color: white; padding: 20px; text-align: center; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 وضعیت سفارش تغییر کرد</h1>
                <p>سفارش شماره: #{order.order_number}</p>
            </div>
            
            <div class="content">
                <p>سلام <strong>{order.customer_name}</strong> عزیز،</p>
                <p>وضعیت سفارش شما تغییر کرده است:</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                    <h3>وضعیت جدید:</h3>
                    <span class="status-badge" style="background: {status_colors.get(new_status, '#e9ecef')}; color: {status_text_colors.get(new_status, '#495057')};">
                        {status_messages.get(new_status, new_status)}
                    </span>
                </div>
                
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>📞 نیاز به راهنمایی دارید؟</h4>
                    <p><strong>تلفن پشتیبانی:</strong> 021-12345678</p>
                    <p><strong>واتساپ:</strong> 09123456789</p>
                    <p><strong>ایمیل:</strong> support@peykan-tourism.com</p>
                </div>
                
                <p>از اعتماد شما متشکریم! 🙏</p>
            </div>
            
            <div class="footer">
                <p>© 2025 پیکان توریسم - تمامی حقوق محفوظ است</p>
                <p>این ایمیل به صورت خودکار ارسال شده است.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return template
