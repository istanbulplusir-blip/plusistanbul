'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { apiClient } from '@/lib/api/client';
import { useToast } from '@/components/Toast';
import { Clock, AlertCircle, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface PendingOrdersDisplayProps {
  tourId?: string;
  scheduleId?: string;
  variantId?: string;
  onOrderUpdate?: () => void;
}

interface PendingOrder {
  order_number: string;
  status: string;
  created_at: string;
  total_amount: number;
  currency: string;
  items: Array<{
    product_title: string;
    product_id: string; // Add product_id field
    booking_date: string;
    quantity: number;
    booking_data: {
      participants?: {
        adult: number;
        child: number;
        infant: number;
      };
      schedule_id?: string;
      variant_id?: string;
    };
  }>;
}

export default function PendingOrdersDisplay({ 
  tourId, 
  scheduleId, 
  variantId, 
  onOrderUpdate 
}: PendingOrdersDisplayProps) {
  const t = useTranslations('TourDetail');
  const { addToast } = useToast();
  const [pendingOrders, setPendingOrders] = useState<PendingOrder[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchPendingOrders = useCallback(async () => {
    if (!tourId) return;
    
    try {
      setLoading(true);
      const response = await apiClient.get('/orders/pending/');
      const orders = (response as { data: { pending_orders: PendingOrder[] } }).data.pending_orders || [];
      
      // Filter orders for this specific tour/schedule/variant
      const filteredOrders = orders.filter((order: PendingOrder) => {
        return order.items.some(item => {
          // Use product_id for exact matching instead of product_title
          const matchesTour = item.product_id === tourId;
          const matchesSchedule = !scheduleId || item.booking_data?.schedule_id === scheduleId;
          const matchesVariant = !variantId || item.booking_data?.variant_id === variantId;
          return matchesTour && matchesSchedule && matchesVariant;
        });
      });
      
      setPendingOrders(filteredOrders);
    } catch (error) {
      console.error('Error fetching pending orders:', error);
    } finally {
      setLoading(false);
    }
  }, [tourId, scheduleId, variantId]);

  const confirmOrder = async (orderNumber: string) => {
    try {
      setRefreshing(true);
      await apiClient.post(`/orders/${orderNumber}/confirm/`);
      
      addToast({
        type: 'success',
        title: t('orderConfirmed'),
        message: t('orderConfirmedMessage'),
        duration: 4000
      });
      
      // Refresh pending orders
      await fetchPendingOrders();
      onOrderUpdate?.();
      
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { error?: string } } }).response?.data?.error || t('confirmationFailed');
      addToast({
        type: 'error',
        title: t('confirmationError'),
        message: errorMessage,
        duration: 4000
      });
    } finally {
      setRefreshing(false);
    }
  };

  const cancelOrder = async (orderNumber: string) => {
    try {
      setRefreshing(true);
      await apiClient.post(`/orders/${orderNumber}/cancel/`, {
        reason: 'User cancelled from tour page'
      });
      
      addToast({
        type: 'success',
        title: t('orderCancelled'),
        message: t('orderCancelledMessage'),
        duration: 4000
      });
      
      // Refresh pending orders
      await fetchPendingOrders();
      onOrderUpdate?.();
      
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { error?: string } } }).response?.data?.error || t('cancellationFailed');
      addToast({
        type: 'error',
        title: t('cancellationError'),
        message: errorMessage,
        duration: 4000
      });
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchPendingOrders();
  }, [fetchPendingOrders]);

  if (loading) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
            {t('loadingPendingOrders')}
          </span>
        </div>
      </div>
    );
  }

  if (pendingOrders.length === 0) {
    return null; // Don't show anything if no pending orders
  }

  return (
    <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4">
      <div className="flex items-center mb-3">
        <Clock className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mr-2" />
        <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
          {t('pendingOrdersTitle')} ({pendingOrders.length})
        </h4>
      </div>
      
      <div className="space-y-3">
        {pendingOrders.map((order) => (
          <div key={order.order_number} className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-yellow-200 dark:border-yellow-600">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mr-2" />
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {t('order')} {order.order_number}
                </span>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {new Date(order.created_at).toLocaleDateString()}
              </span>
            </div>
            
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {order.items.map((item, index) => (
                <div key={index} className="mb-1">
                  <span className="font-medium">{item.product_title}</span>
                  {item.booking_data?.participants && (
                    <span className="ml-2">
                      ({item.booking_data.participants.adult} {t('adults')}, 
                       {item.booking_data.participants.child} {t('children')}, 
                       {item.booking_data.participants.infant} {t('infants')})
                    </span>
                  )}
                </div>
              ))}
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {t('total')}: {order.total_amount} {order.currency}
              </div>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => confirmOrder(order.order_number)}
                disabled={refreshing}
                className="flex-1 bg-green-600 text-white text-xs py-2 px-3 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {refreshing ? (
                  <Loader2 className="h-3 w-3 animate-spin mx-auto" />
                ) : (
                  <div className="flex items-center justify-center">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    {t('confirm')}
                  </div>
                )}
              </button>
              
              <button
                onClick={() => cancelOrder(order.order_number)}
                disabled={refreshing}
                className="flex-1 bg-red-600 text-white text-xs py-2 px-3 rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {refreshing ? (
                  <Loader2 className="h-3 w-3 animate-spin mx-auto" />
                ) : (
                  <div className="flex items-center justify-center">
                    <XCircle className="h-3 w-3 mr-1" />
                    {t('cancel')}
                  </div>
                )}
              </button>
            </div>
            
            <div className="mt-2 text-xs text-yellow-700 dark:text-yellow-300">
              {t('pendingOrderNote')}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-3 text-xs text-yellow-700 dark:text-yellow-300">
        <AlertCircle className="h-3 w-3 inline mr-1" />
        {t('capacityNote')}
      </div>
    </div>
  );
}
