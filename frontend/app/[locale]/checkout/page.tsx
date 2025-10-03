'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useCart } from '../../../lib/hooks/useCart';
import { useAuth } from '../../../lib/contexts/AuthContext';
import { useCustomerData } from '../../../lib/hooks/useCustomerData';
import { CheckoutCustomerInfo } from '../../../components/forms/CheckoutCustomerInfo';
import { 
  ShoppingCart, 
  ArrowLeft,
  AlertCircle,
  CreditCard,
  CheckCircle,
  Package,
  Truck
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { CartItem } from '../../../lib/contexts/UnifiedCartContext';
import OptimizedImage from '@/components/common/OptimizedImage';
import { getImageUrl } from '@/lib/utils';

// interface CustomerInfo {
//   full_name: string;
//   email: string;
//   phone: string;
//   address: string;
//   city: string;
//   country: string;
//   postal_code: string;
//   special_requests: string;
// }

export default function CheckoutPage() {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations('checkout');
  
  const { 
    items, 
    totalItems, 
    currency, 
    subtotal, 
    feesTotal, 
    taxTotal, 
    grandTotal, 
    clearCart 
  } = useCart();
  const { isAuthenticated } = useAuth();
  const { 
    customerData
  } = useCustomerData();
  
  const [specialRequests, setSpecialRequests] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect if cart is empty
  useEffect(() => {
    if (totalItems === 0) {
      router.push(`/${locale}/cart`);
    }
  }, [totalItems, router, locale]);

  const handleBackToCart = () => {
    router.push(`/${locale}/cart`);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setError(null);

    try {
      // Validate customer data
      if (!customerData) {
        throw new Error('اطلاعات مشتری یافت نشد');
      }

      // Create order data in the format expected by backend
      const orderData = {
        // Customer information (mapped to Order fields)
        customer_name: customerData.full_name || '',
        customer_email: customerData.email || '',
        customer_phone: customerData.phone || '',

        // Billing information (required by Order model)
        billing_city: customerData.city || '',
        billing_country: customerData.country || '',
        billing_address: '', // Not needed for services

        // Notes
        customer_notes: specialRequests,

        // Payment information
        payment_method: 'whatsapp', // Default payment method
        payment_reference: '', // Will be set when payment is processed
        payment_date: null, // Will be set when payment is confirmed

        // Pricing information
        currency: currency,
        subtotal: subtotal,
        service_fee_amount: feesTotal,
        total_amount: grandTotal,
        tax_amount: taxTotal,
        discount_amount: 0,
        // Order items
        items: items.map((item: CartItem) => ({
          product_type: item.product_type,
          product_id: item.product_id,
          product_title: item.product_title,
          product_slug: item.product_slug || '',
          variant_id: item.variant_id,
          variant_name: item.variant_name,
          quantity: item.quantity,
          unit_price: item.unit_price,
          total_price: item.total_price,
          selected_options: item.selected_options,
          options_total: item.options_total,
          booking_data: item.booking_data,
          booking_date: item.booking_date,
          booking_time: item.booking_time
        }))
      };

      // Debug logging
      console.log('=== CHECKOUT DEBUG ===');
      console.log('Order data being sent to backend:', orderData);
      console.log('Pricing breakdown:');
      console.log('  Subtotal:', subtotal);
      console.log('  Fees Total:', feesTotal);
      console.log('  Tax Total:', taxTotal);
      console.log('  Grand Total:', grandTotal);
      console.log('Items:', items);

      // Send order to backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/orders/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(orderData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'خطا در ایجاد سفارش');
      }

      const orderResult = await response.json();
      console.log('Order creation response:', orderResult);
      console.log('Order number:', orderResult.order_number);
      console.log('Order ID:', orderResult.id);
      
      // Clear cart after successful order (non-blocking)
      try {
        await clearCart();
        console.log('Cart cleared successfully');
      } catch (cartError) {
        console.warn('Failed to clear cart:', cartError);
        // Don't block the redirect if cart clear fails
      }
      
      // Redirect to order confirmation
      if (orderResult.order_number) {
        console.log('Redirecting to order detail:', `/${locale}/orders/${orderResult.order_number}`);
        // Use window.location.href for more reliable redirect
        window.location.href = `/${locale}/orders/${orderResult.order_number}`;
      } else if (orderResult.id) {
        // If order_number is not available, try to get it from the order detail
        try {
          const orderDetailResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/orders/${orderResult.id}/`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          
          if (orderDetailResponse.ok) {
            const orderDetail = await orderDetailResponse.json();
            if (orderDetail.order_number) {
              console.log('Redirecting to order detail via ID:', `/${locale}/orders/${orderDetail.order_number}`);
              window.location.href = `/${locale}/orders/${orderDetail.order_number}`;
            } else {
              // Fallback: redirect to orders list
              console.log('Redirecting to orders list (no order_number)');
              window.location.href = `/${locale}/orders`;
            }
          } else {
            // Fallback: redirect to orders list
            console.log('Redirecting to orders list (API error)');
            window.location.href = `/${locale}/orders`;
          }
        } catch (detailError) {
          console.error('Error fetching order detail:', detailError);
          // Fallback: redirect to orders list
          console.log('Redirecting to orders list (fetch error)');
          window.location.href = `/${locale}/orders`;
        }
      } else {
        console.error('Order number not found in response:', orderResult);
        // Try to redirect to orders list instead of showing error
        console.log('Redirecting to orders list (no order data)');
        window.location.href = `/${locale}/orders`;
      }
      
    } catch (err) {
      console.error('Checkout error:', err);
      setError(err instanceof Error ? err.message : 'خطای نامشخص');
    } finally {
      setIsProcessing(false);
    }
  };

  if (totalItems === 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <ShoppingCart className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            سبد خرید خالی است
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            برای ادامه خرید، ابتدا محصولی به سبد خرید اضافه کنید
          </p>
          <Button onClick={() => router.push(`/${locale}/tours`)}>
            مشاهده تورها
          </Button>
        </div>
      </div>
    );
  }

  // Check authentication manually
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            برای تکمیل سفارش باید وارد شوید
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            لطفاً ابتدا وارد حساب کاربری خود شوید
          </p>
          <Button onClick={() => router.push(`/${locale}/login`)}>
            ورود به حساب کاربری
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <Button
              onClick={handleBackToCart}
              variant="ghost"
              className="mb-4 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              {t('backToCart')}
            </Button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{t('checkoutTitle')}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">{t('checkoutSubtitle')}</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
                <span className="text-red-700 dark:text-red-200">{error}</span>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Customer Information */}
              <div className="lg:col-span-2 space-y-6">
                <CheckoutCustomerInfo 
                  onSpecialRequestsChange={setSpecialRequests}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6"
                />
              </div>

              {/* Order Summary */}
              <div className="space-y-6">
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                    <Package className="h-5 w-5 text-blue-600" />
                    خلاصه سفارش
                  </h2>

                  {/* Order Items */}
                  <div className="space-y-4 mb-6">
                    {items.map((item: CartItem, index) => (
                      <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="w-12 h-12 rounded-lg overflow-hidden bg-gray-200 dark:bg-gray-600">
                          <OptimizedImage
                            src={getImageUrl(item.image) || '/images/placeholder-car.jpg'}
                            alt={item.title || item.product_title || 'Product'}
                            width={48}
                            height={48}
                            className="w-full h-full object-cover"
                            fallbackSrc="/images/tour-image.jpg"
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {item.product_title}
                          </h3>
                          {item.variant_name && (
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {item.variant_name}
                            </p>
                          )}
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            تعداد: {item.quantity}
                          </p>
                        </div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {currency} {item.total_price}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Pricing Breakdown */}
                  <div className="space-y-2 border-t border-gray-200 dark:border-gray-600 pt-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">جمع کل:</span>
                      <span className="text-gray-900 dark:text-white">{currency} {subtotal}</span>
                    </div>
                    {feesTotal > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">کارمزد:</span>
                        <span className="text-gray-900 dark:text-white">{currency} {feesTotal}</span>
                      </div>
                    )}
                    {taxTotal > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">مالیات:</span>
                        <span className="text-gray-900 dark:text-white">{currency} {taxTotal}</span>
                      </div>
                    )}
                    <div className="flex justify-between text-lg font-semibold border-t border-gray-200 dark:border-gray-600 pt-2">
                      <span className="text-gray-900 dark:text-white">مجموع:</span>
                      <span className="text-gray-900 dark:text-white">{currency} {grandTotal}</span>
                    </div>
                  </div>
                </div>

                {/* Payment Method */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <CreditCard className="h-5 w-5 text-blue-600" />
                    روش پرداخت
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                      <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                        <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">پرداخت از طریق واتساپ</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          پس از تایید سفارش، لینک پرداخت برای شما ارسال می‌شود
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  disabled={isProcessing}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      در حال پردازش...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-2">
                      <Truck className="h-4 w-4" />
                      تایید و ارسال سفارش
                    </div>
                  )}
                </Button>

                {/* Security Note */}
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
                    <div className="text-sm text-green-700 dark:text-green-200">
                      <p className="font-medium mb-1">اطلاعات شما امن است</p>
                      <p>
                        تمام اطلاعات شما با استفاده از رمزنگاری پیشرفته محافظت می‌شود
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
  );
}