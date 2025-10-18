'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Calendar,
  Clock,
  User,
  Mail,
  Phone,
  MapPin,
  CreditCard,
  Download,
  X,
  Edit3,
  CheckCircle,
  AlertCircle,
  Package,
  Music,
  Truck,
  MessageSquare,
  RefreshCw,
  MessageCircle,
  Route,
  Users
} from 'lucide-react';
import { orderService, type Order } from '../../../../lib/services/orderService';
import { Button } from '../../../../components/ui/Button';
import ProtectedRoute from '../../../../components/ProtectedRoute';
// import OptimizedImage from '../../../../components/common/OptimizedImage';

// interface OrderDetailPageProps {
//   params: {
//     locale: string;
//     orderNumber: string;
//   };
// }

export default function OrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const t = useTranslations('orders');
  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [whatsappLink, setWhatsappLink] = useState<string | null>(null);

  const orderNumber = params.orderNumber as string;

  const loadWhatsAppLink = useCallback(async (orderNum: string) => {
    try {
      const result = await orderService.getWhatsAppLinks(orderNum);
      if (result.success && result.customerLink) {
        setWhatsappLink(result.customerLink);
      }
    } catch (err) {
      console.warn('Failed to load WhatsApp link:', err);
    }
  }, []);

  const loadOrderDetails = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/orders/${orderNumber}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || 'Failed to get order details');
      }

      const orderData = await response.json();
      setOrder(orderData);
      // Load WhatsApp link
      loadWhatsAppLink(orderData.order_number);
    } catch (error) {
      console.error('Error loading order details:', error);
      setError(error instanceof Error ? error.message : t('errorLoadingOrderDetails'));
    } finally {
      setIsLoading(false);
    }
  }, [orderNumber, t, loadWhatsAppLink]);

  useEffect(() => {
    loadOrderDetails();
  }, [loadOrderDetails]);

  const getProductTypeIcon = (type: string) => {
    switch (type) {
      case 'tour':
        return <MapPin className="w-5 h-5 text-blue-500" />;
      case 'event':
        return <Music className="w-5 h-5 text-purple-500" />;
      case 'transfer':
        return <Truck className="w-5 h-5 text-green-500" />;
      default:
        return <Package className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'cancelled':
        return <X className="w-5 h-5 text-red-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300';
      case 'cancelled':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300';
      case 'completed':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300';
    }
  };

  const canCancelOrder = (order: Order) => {
    return order.status === 'pending' || order.status === 'confirmed';
  };

  const canModifyOrder = (order: Order) => {
    return order.status === 'pending';
  };

  const handleCancelOrder = async () => {
    if (!order || !canCancelOrder(order)) return;

    const confirmCancel = window.confirm(t('cancelConfirmation'));
    if (!confirmCancel) return;

    setActionLoading('cancel');
    try {
      const result = await orderService.cancelOrder(order.order_number);
      
      if (result.success) {
        alert(t('orderCancelledSuccess'));
        // Refresh order details
        await loadOrderDetails();
      } else {
        alert(result.message || t('errorCancellingOrder'));
      }
    } catch {
      alert(t('errorCancellingOrder'));
    } finally {
      setActionLoading(null);
    }
  };

  const handleModifyOrder = () => {
    if (!order || !canModifyOrder(order)) return;
    // TODO: Navigate to modify order page
    alert(t('modifyOrderComingSoon'));
  };

  const handleDownloadReceipt = async () => {
    if (!order) return;

    setActionLoading('download');
    try {
      const result = await orderService.downloadReceipt(order.order_number);
      
      if (result.success) {
        alert(result.message || t('receiptReady'));
      } else {
        alert(result.message || t('errorDownloadingReceipt'));
      }
    } catch {
      alert(t('errorDownloadingReceipt'));
    } finally {
      setActionLoading(null);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <motion.div 
          className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <div className="container mx-auto px-4 py-8">
            <motion.div 
              className="flex flex-col items-center justify-center py-16"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <motion.div 
                className="relative inline-block mb-6"
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <div className="w-16 h-16 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 p-1">
                  <div className="w-full h-full rounded-full bg-white dark:bg-gray-900 flex items-center justify-center">
                    <Package className="w-6 h-6 text-primary-500" />
                  </div>
                </div>
              </motion.div>
              <motion.span 
                className="text-lg font-medium bg-gradient-to-r from-gray-700 to-gray-500 dark:from-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {t('loadingOrderDetails')}
              </motion.span>
            </motion.div>
          </div>
        </motion.div>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <div className="container mx-auto px-4 py-8">
            <div className="text-center py-12">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">{t('loadingError')}</h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
              <div className="flex justify-center gap-4">
                <Button onClick={loadOrderDetails} variant="outline">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {t('retryButton')}
                </Button>
                <Button onClick={() => router.push('/profile')} variant="default">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  {t('backToProfile')}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (!order) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <div className="container mx-auto px-4 py-8">
            <div className="text-center py-12">
              <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">{t('orderNotFound')}</h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">{t('orderNotFoundMessage', { orderNumber })}</p>
              <Button onClick={() => router.push('/profile')} variant="default">
                <ArrowLeft className="w-4 h-4 mr-2" />
                {t('backToProfile')}
              </Button>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <motion.div 
        className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <motion.div 
            className="mb-8"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <motion.button
              onClick={() => router.push('/profile')}
              className="flex items-center text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 mb-6 transition-colors"
              whileHover={{ scale: 1.05, x: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              {t('backToProfile')}
            </motion.button>

            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <div className="flex items-center gap-4 mb-4">
                  <motion.div 
                    className="w-14 h-14 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center shadow-lg"
                    whileHover={{ scale: 1.05, rotate: 5 }}
                    animate={{ y: [0, -2, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Package className="w-7 h-7 text-white" />
                  </motion.div>
                  <div>
                    <motion.h1 
                      className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                      whileHover={{ scale: 1.02 }}
                    >
                      {t('orderNumber', { orderNumber: order.order_number })}
                    </motion.h1>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                      {orderService.formatDate(order.created_at)}
                    </span>
                  </div>
                  <motion.div 
                    className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-full border shadow-sm ${getStatusColor(order.status)} ${
                      order.status === 'confirmed' ? 'border-green-200/50 dark:border-green-700/50' :
                      order.status === 'pending' ? 'border-yellow-200/50 dark:border-yellow-700/50' :
                      order.status === 'cancelled' ? 'border-red-200/50 dark:border-red-700/50' :
                      'border-gray-200/50 dark:border-gray-700/50'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.3, delay: 0.4 }}
                  >
                    <motion.div
                      animate={{ 
                        rotate: order.status === 'pending' ? [0, 360] : 0,
                        scale: order.status === 'confirmed' ? [1, 1.2, 1] : 1
                      }}
                      transition={{ 
                        duration: order.status === 'pending' ? 2 : 0.5,
                        repeat: order.status === 'pending' ? Infinity : 0
                      }}
                    >
                      {getStatusIcon(order.status)}
                    </motion.div>
                    {t(orderService.getOrderStatusKey(order.status))}
                  </motion.div>
                </div>
              </motion.div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                {canModifyOrder(order) && (
                  <Button
                    onClick={handleModifyOrder}
                    variant="outline"
                    size="sm"
                    disabled={actionLoading !== null}
                    className="flex-shrink-0"
                  >
                    <Edit3 className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">{t('modifyOrder')}</span>
                  </Button>
                )}
                
                {order.status !== 'cancelled' && (
                  <>
                    <Button
                      onClick={handleDownloadReceipt}
                      variant="outline"
                      size="sm"
                      disabled={actionLoading !== null}
                      loading={actionLoading === 'download'}
                      className="flex-shrink-0"
                    >
                      <Download className="w-4 h-4 sm:mr-2" />
                      <span className="hidden sm:inline">{t('downloadReceipt')}</span>
                    </Button>

                    {whatsappLink && (
                      <Button
                        onClick={() => window.open(whatsappLink, '_blank')}
                        variant="outline"
                        size="sm"
                        className="bg-green-50 hover:bg-green-100 text-green-700 border-green-200 hover:border-green-300 dark:bg-green-900/20 dark:text-green-400 dark:border-green-700 dark:hover:bg-green-900/30 flex-shrink-0"
                      >
                        <MessageCircle className="w-4 h-4 sm:mr-2" />
                        <span className="hidden sm:inline">{t('completeOnWhatsApp')}</span>
                      </Button>
                    )}
                  </>
                )}

                {canCancelOrder(order) && (
                  <Button
                    onClick={handleCancelOrder}
                    variant="destructive"
                    size="sm"
                    disabled={actionLoading !== null}
                    loading={actionLoading === 'cancel'}
                    className="flex-shrink-0"
                  >
                    <X className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">{t('cancelOrder')}</span>
                  </Button>
                )}
              </div>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Order Items */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  {t('orderItemsCount', { count: order.items.length })}
                </h2>

                <div className="space-y-4">
                  {order.items.map((item) => (
                    <div key={item.id} className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 mt-1">
                          {getProductTypeIcon(item.product_type)}
                        </div>

                        <div className="flex-1">
                          <div className="mb-2">
                            <h3 className="font-medium text-gray-900 dark:text-gray-100">
                              {item.product_title}
                            </h3>
                          </div>

                          {item.variant_name && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                              Type: {item.variant_name}
                            </p>
                          )}

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
                            <div className="flex items-center gap-2">
                              <Package className="w-4 h-4" />
                              {item.product_type === 'event' && item.booking_data?.seats ? (
                                <span>Seats: {item.booking_data.seats.length}</span>
                              ) : (
                                <span>Quantity: {item.quantity} people</span>
                              )}
                            </div>

                            {item.booking_date && (
                              <div className="flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                <span>Date: {orderService.formatDate(item.booking_date)}</span>
                              </div>
                            )}

                            {item.booking_time && (
                              <div className="flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                <span>Time: {item.booking_time}</span>
                              </div>
                            )}

                            {item.booking_data?.pickup_time && (
                              <div className="flex items-center gap-2">
                                <MapPin className="w-4 h-4" />
                                <span>Pickup: {item.booking_data.pickup_time}</span>
                              </div>
                            )}

                            {item.booking_data?.schedule_id && (
                              <div className="flex items-center gap-2">
                                <Route className="w-4 h-4" />
                                <span>Schedule: {item.booking_data.schedule_id.slice(0, 8)}...</span>
                              </div>
                            )}
                          </div>

                          {/* Show participants breakdown for tours */}
                          {item.product_type === 'tour' && item.booking_data?.participants && (
                            <div className="bg-white dark:bg-gray-600 rounded-lg p-3 mb-3">
                              <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Participants:</div>
                              <div className="space-y-1 text-sm">
                                {item.booking_data.participants.adult > 0 && (
                                  <div className="flex justify-between">
                                    <span>Adult ({item.booking_data.participants.adult}x)</span>
                                    <span>{orderService.formatCurrency(item.unit_price * item.booking_data.participants.adult, order.currency)}</span>
                                  </div>
                                )}
                                {item.booking_data.participants.child > 0 && (
                                  <div className="flex justify-between">
                                    <span>Child ({item.booking_data.participants.child}x)</span>
                                    <span>{orderService.formatCurrency(item.unit_price * item.booking_data.participants.child * 0.7, order.currency)}</span>
                                  </div>
                                )}
                                {item.booking_data.participants.infant > 0 && (
                                  <div className="flex justify-between">
                                    <span>Infant ({item.booking_data.participants.infant}x)</span>
                                    <span className="text-green-600 font-medium">{t('free')}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}

                          {item.selected_options && (
                            <div className="mb-3">
                              <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">{t('selectedOptions')}:</p>
                              <div className="space-y-2">
                                {Array.isArray(item.selected_options) && item.selected_options.map((option: {name?: string, option_id?: string, quantity?: number, price?: number}, optIndex: number) => (
                                  <motion.div
                                    key={optIndex}
                                    className="flex justify-between items-center px-3 py-2 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200/50 dark:border-blue-700/50"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.3, delay: optIndex * 0.1 }}
                                  >
                                    <div className="flex flex-col">
                                      <span className="text-xs font-medium text-blue-700 dark:text-blue-300">
                                        {option.name || `Option ${option.option_id?.slice(0, 8) || 'Unknown'}`}
                                      </span>
                                      <span className="text-xs text-blue-600 dark:text-blue-400">
                                        {option.quantity}x
                                      </span>
                                    </div>
                                    <span className="text-xs font-semibold text-blue-700 dark:text-blue-300">
                                      {option.price ? orderService.formatCurrency(option.price * (option.quantity || 1), order.currency) : 'Price not available'}
                                    </span>
                                  </motion.div>
                                ))}
                                {!Array.isArray(item.selected_options) && (
                                  <div className="text-xs text-gray-500 dark:text-gray-400">
                                    {JSON.stringify(item.selected_options)}
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Comprehensive Booking Summary */}
                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <Package className="w-5 h-5 mr-2" />
                    Booking Summary
                  </h3>

                  {order.items.map((item) => (
                    <div key={item.id} className="mb-6 last:mb-0">
                      {/* Tour Header */}
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4 mb-4">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
                                {item.product_title}
                              </h4>
                              {item.variant_name && (
                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                  {item.variant_name}
                                </p>
                              )}
                              {/* Event-specific information */}
                              {item.product_type === 'event' && item.booking_data && (
                                <div className="mt-2 space-y-1">
                                  {item.booking_data.section && (
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                      Section: {item.booking_data.section}
                                    </p>
                                  )}
                                  {item.booking_data.ticket_type_name && (
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                      Ticket Type: {item.booking_data.ticket_type_name}
                                    </p>
                                  )}
                                </div>
                              )}
                            </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              Order #{order.order_number}
                            </div>
                            <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                              {orderService.formatDate(order.created_at)}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Schedule Information */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                        <div className="bg-white dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                          <div className="flex items-center mb-2">
                            <Calendar className="w-4 h-4 text-blue-500 mr-2" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Date</span>
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {item.product_type === 'transfer' && item.booking_data?.outbound_date
                              ? orderService.formatDate(item.booking_data.outbound_date)
                              : (item.booking_date ? orderService.formatDate(item.booking_date) : 'Not specified')
                            }
                            {item.product_type === 'transfer' && item.booking_data?.trip_type === 'round_trip' && item.booking_data?.return_date && (
                              <div className="mt-1 text-xs text-gray-500">
                                Return: {orderService.formatDate(item.booking_data.return_date)}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="bg-white dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                          <div className="flex items-center mb-2">
                            <Clock className="w-4 h-4 text-green-500 mr-2" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Time</span>
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {item.product_type === 'transfer' && item.booking_data?.outbound_time
                              ? item.booking_data.outbound_time
                              : (item.booking_time || 'Not specified')
                            }
                            {item.product_type === 'transfer' && item.booking_data?.trip_type === 'round_trip' && item.booking_data?.return_time && (
                              <div className="mt-1 text-xs text-gray-500">
                                Return: {item.booking_data.return_time}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="bg-white dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                          <div className="flex items-center mb-2">
                            <MapPin className="w-4 h-4 text-red-500 mr-2" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Pickup</span>
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {item.product_type === 'transfer' && item.booking_data?.pickup_address
                              ? item.booking_data.pickup_address
                              : (item.booking_data?.pickup_time || '08:30 AM')
                            }
                          </div>
                        </div>

                        <div className="bg-white dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                          <div className="flex items-center mb-2">
                            <Users className="w-4 h-4 text-purple-500 mr-2" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                              {item.product_type === 'transfer' ? 'Passengers' : item.product_type === 'event' ? 'Seats' : 'People'}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {item.product_type === 'transfer'
                              ? `${item.booking_data?.passenger_count || item.quantity || 1} passenger${(item.booking_data?.passenger_count || item.quantity || 1) > 1 ? 's' : ''}`
                              : item.product_type === 'event' && item.booking_data?.seats
                              ? `${item.booking_data.seats.length} seat${item.booking_data.seats.length > 1 ? 's' : ''}`
                              : `${item.quantity} total`
                            }
                          </div>
                        </div>

                        {/* Vehicle Information - For Transfers */}
                        {item.product_type === 'transfer' && item.booking_data?.vehicle_type && (
                          <div className="bg-white dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                            <div className="flex items-center mb-2">
                              <Truck className="w-4 h-4 text-orange-500 mr-2" />
                              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Vehicle</span>
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              {item.booking_data.vehicle_name || item.booking_data.vehicle_type || 'N/A'}
                              {item.booking_data.max_passengers && (
                                <span className="ml-1 text-xs">
                                  (max {item.booking_data.max_passengers} passengers)
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Participants Breakdown - For Tours */}
                      {item.product_type === 'tour' && item.booking_data?.participants && (
                        <div className="bg-white dark:bg-gray-700 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-600">
                          <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Participants</h5>
                          <div className="space-y-2">
                            {item.booking_data.participants.adult > 0 && (
                              <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-600 last:border-b-0">
                                <span className="text-sm text-gray-700 dark:text-gray-300">
                                  Adult ({item.booking_data.participants.adult}x)
                                </span>
                                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {orderService.formatCurrency(item.unit_price * item.booking_data.participants.adult, order.currency)}
                                </span>
                              </div>
                            )}
                            {item.booking_data.participants.child > 0 && (
                              <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-600 last:border-b-0">
                                <span className="text-sm text-gray-700 dark:text-gray-300">
                                  Child ({item.booking_data.participants.child}x)
                                </span>
                                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {orderService.formatCurrency(item.unit_price * item.booking_data.participants.child * 0.7, order.currency)}
                                </span>
                              </div>
                            )}
                            {item.booking_data.participants.infant > 0 && (
                              <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-600 last:border-b-0">
                                <span className="text-sm text-gray-700 dark:text-gray-300">
                                  Infant ({item.booking_data.participants.infant}x)
                                </span>
                                <span className="text-sm font-medium text-green-600 dark:text-green-400">
                                  Free
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Event Details - For Events */}
                      {item.product_type === 'event' && item.booking_data && (
                        <div className="bg-white dark:bg-gray-700 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-600">
                          <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Event Details</h5>
                          <div className="space-y-4">
                            {/* Performance Information */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Performance Date</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.performance_date ? orderService.formatDate(item.booking_data.performance_date) : 'N/A'}
                                </p>
                              </div>
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Performance Time</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.performance_time ? item.booking_data.performance_time : 'N/A'}
                                </p>
                              </div>
                            </div>

                            {/* Venue Information */}
                            {item.booking_data.venue_name && (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <span className="text-sm text-gray-600 dark:text-gray-400">Venue</span>
                                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    {item.booking_data.venue_name}
                                  </p>
                                </div>
                                <div>
                                  <span className="text-sm text-gray-600 dark:text-gray-400">Location</span>
                                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    {[item.booking_data.venue_city, item.booking_data.venue_country].filter(Boolean).join(', ') || 'N/A'}
                                  </p>
                                </div>
                              </div>
                            )}

                            {/* Section Information */}
                            {item.booking_data.section && (
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Section</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.section}
                                </p>
                              </div>
                            )}

                            {/* Ticket Type Information */}
                            {(item.booking_data.ticket_type_name || item.variant_name) && (
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Ticket Type</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.ticket_type_name || item.variant_name}
                                </p>
                              </div>
                            )}

                            {/* Seats Information */}
                            {item.booking_data.seats && Array.isArray(item.booking_data.seats) && item.booking_data.seats.length > 0 && (
                              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-700">
                                <h6 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">Seats</h6>
                                <div className="space-y-2">
                                   {item.booking_data.seats.map((seat: unknown, seatIndex: number) => {
                                    const seatObj = seat as {
                                      row_number?: string | number;
                                      seat_number?: string | number;
                                      seat_id?: string;
                                      section?: string;
                                      type?: string;
                                      price?: number;
                                    };

                                    // Create a proper seat display name
                                    let seatDisplayName = `Seat ${seatIndex + 1}`;
                                    if (seatObj.row_number && seatObj.seat_number) {
                                      seatDisplayName = `Row ${seatObj.row_number}, Seat ${seatObj.seat_number}`;
                                    } else if (seatObj.seat_number) {
                                      seatDisplayName = `Seat ${seatObj.seat_number}`;
                                    } else if (seatObj.seat_id) {
                                      // Fallback to showing a portion of the UUID
                                      seatDisplayName = `Seat ${seatObj.seat_id.slice(0, 8)}`;
                                    }

                                    // Add wheelchair or type information if available
                                    const seatDetails = [];
                                    if (seatObj.section) seatDetails.push(seatObj.section);
                                    if (seatObj.type && seatObj.type.toLowerCase().includes('wheelchair')) {
                                      seatDetails.push('(Wheelchair)');
                                    } else if (seatObj.type && seatObj.type !== seatObj.section) {
                                      seatDetails.push(seatObj.type);
                                    }

                                    return (
                                      <div key={seatIndex} className="flex justify-between items-center">
                                        <div className="flex flex-col">
                                          <span className="text-sm text-blue-700 dark:text-blue-300 font-medium">
                                            {seatDisplayName}
                                          </span>
                                          {seatDetails.length > 0 && (
                                            <span className="text-xs text-blue-600 dark:text-blue-400">
                                              {seatDetails.join(', ')}
                                            </span>
                                          )}
                                        </div>
                                        <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                                          {seatObj.price ? orderService.formatCurrency(seatObj.price, order.currency) : 'N/A'}
                                        </span>
                                      </div>
                                    );
                                  })}
                                </div>
                                <div className="flex justify-between items-center pt-2 border-t border-blue-200 dark:border-blue-700 mt-2">
                                  <span className="text-sm font-medium text-blue-800 dark:text-blue-200">Seats Total</span>
                                  <span className="text-sm font-bold text-blue-700 dark:text-blue-300">
                                    {orderService.formatCurrency(
                                      item.booking_data.seats.reduce((total: number, seat: unknown) => {
                                        const seatObj = seat as { price?: number };
                                        return total + (seatObj.price || 0);
                                      }, 0),
                                      order.currency
                                    )}
                                  </span>
                                </div>
                              </div>
                            )}

                            {/* Special Requests */}
                            {item.booking_data.special_requests && (
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Special Requests</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.special_requests}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Transfer Details - For Transfers */}
                      {item.product_type === 'transfer' && item.booking_data && (
                        <div className="bg-white dark:bg-gray-700 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-600">
                          <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Transfer Details</h5>
                          <div className="space-y-4">
                            {/* Route Information */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Route</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.route_name ||
                                   (item.booking_data.route_origin && item.booking_data.route_destination
                                     ? `${item.booking_data.route_origin} → ${item.booking_data.route_destination}`
                                     : 'N/A → N/A')}
                                </p>
                              </div>
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Vehicle</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.vehicle_name || item.booking_data.vehicle_type || 'N/A'}
                                  {item.booking_data.max_passengers && (
                                    <span className="text-xs text-gray-500 ml-1">
                                      (max {item.booking_data.max_passengers} passengers)
                                    </span>
                                  )}
                                </p>
                              </div>
                            </div>

                            {/* Trip Type */}
                            {item.booking_data.trip_type && (
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Trip Type</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.trip_type === 'round_trip' ? 'Round Trip' : 'One Way'}
                                </p>
                              </div>
                            )}

                            {/* Time Details - For Round Trip */}
                            {item.booking_data.trip_type === 'round_trip' && (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Outbound */}
                                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-700">
                                  <h6 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">Outbound Trip</h6>
                                  <div className="space-y-1">
                                    {item.booking_data.outbound_date && (
                                      <div className="flex justify-between">
                                        <span className="text-xs text-blue-600 dark:text-blue-400">Date:</span>
                                        <span className="text-xs font-medium">{orderService.formatDate(item.booking_data.outbound_date)}</span>
                                      </div>
                                    )}
                                    {item.booking_data.outbound_time && (
                                      <div className="flex justify-between">
                                        <span className="text-xs text-blue-600 dark:text-blue-400">Time:</span>
                                        <span className="text-xs font-medium">{item.booking_data.outbound_time}</span>
                                      </div>
                                    )}
                                    {item.booking_data.outbound_price && (
                                      <div className="flex justify-between">
                                        <span className="text-xs text-blue-600 dark:text-blue-400">Price:</span>
                                        <span className="text-xs font-medium">${item.booking_data.outbound_price}</span>
                                      </div>
                                    )}
                                  </div>
                                </div>

                                {/* Return */}
                                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-700">
                                  <h6 className="text-sm font-medium text-green-800 dark:text-green-200 mb-2">Return Trip</h6>
                                  <div className="space-y-1">
                                    {item.booking_data.return_date && (
                                      <div className="flex justify-between">
                                        <span className="text-xs text-green-600 dark:text-green-400">Date:</span>
                                        <span className="text-xs font-medium">{orderService.formatDate(item.booking_data.return_date)}</span>
                                      </div>
                                    )}
                                    {item.booking_data.return_time && (
                                      <div className="flex justify-between">
                                        <span className="text-xs text-green-600 dark:text-green-400">Time:</span>
                                        <span className="text-xs font-medium">{item.booking_data.return_time}</span>
                                      </div>
                                    )}
                                    {item.booking_data.return_price && parseFloat(String(item.booking_data.return_price)) !== 0 && (
                                      <div className="flex justify-between">
                                        <span className="text-xs text-green-600 dark:text-green-400">Price:</span>
                                        <span className="text-xs font-medium">${item.booking_data.return_price}</span>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Time Details - For One Way */}
                            {(!item.booking_data.trip_type || item.booking_data.trip_type === 'one_way') && (
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Departure Time</span>
                                <div className="mt-1">
                                  {item.booking_data.outbound_date && (
                                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                      Date: {orderService.formatDate(item.booking_data.outbound_date)}
                                    </p>
                                  )}
                                  {item.booking_data.outbound_time && (
                                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                      Time: {item.booking_data.outbound_time}
                                    </p>
                                  )}
                                </div>
                              </div>
                            )}

                            {/* Passenger & Luggage */}
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Passengers</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.passenger_count || item.quantity || 1} passenger{(item.booking_data.passenger_count || item.quantity || 1) > 1 ? 's' : ''}
                                </p>
                              </div>
                              {(item.booking_data.luggage_count || 0) > 0 && (
                                <div>
                                  <span className="text-sm text-gray-600 dark:text-gray-400">Luggage</span>
                                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    {item.booking_data.luggage_count || 0} piece{(item.booking_data.luggage_count || 0) > 1 ? 's' : ''}
                                  </p>
                                </div>
                              )}
                            </div>

                            {/* Pickup & Dropoff Addresses */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {item.booking_data.pickup_address && (
                                <div>
                                  <span className="text-sm text-gray-600 dark:text-gray-400">Pickup Address</span>
                                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    {item.booking_data.pickup_address}
                                  </p>
                                </div>
                              )}
                              {item.booking_data.dropoff_address && (
                                <div>
                                  <span className="text-sm text-gray-600 dark:text-gray-400">Drop-off Address</span>
                                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    {item.booking_data.dropoff_address}
                                  </p>
                                </div>
                              )}
                            </div>

                            {/* Duration */}
                            {item.booking_data.estimated_duration && (
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Estimated Duration</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.estimated_duration} minutes
                                </p>
                              </div>
                            )}

                            {/* Special Requirements */}
                            {item.booking_data.special_requirements && (
                              <div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">Special Requirements</span>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {item.booking_data.special_requirements}
                                </p>
                              </div>
                            )}

                            {/* Pricing Breakdown */}
                            {(item.booking_data.surcharges || item.booking_data.discounts) && (
                              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                                <h6 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Pricing Details</h6>

                                {/* Surcharges */}
                                {item.booking_data.surcharges && Object.keys(item.booking_data.surcharges).length > 0 && (
                                  <div className="mb-3">
                                    <h6 className="text-xs font-medium text-orange-600 dark:text-orange-400 mb-1">Surcharges</h6>
                                    <div className="space-y-1">
                                      {Object.entries(item.booking_data.surcharges).map(([key, value]: [string, unknown]) => (
                                        <div key={key} className="flex justify-between text-xs">
                                          <span className="text-gray-600 dark:text-gray-400">
                                            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                          </span>
                                          <span className="font-medium text-orange-600 dark:text-orange-400">
                                            +${typeof value === 'string' ? value : String(value)}
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Discounts */}
                                {item.booking_data.discounts && Object.keys(item.booking_data.discounts).length > 0 && (
                                  <div className="mb-3">
                                    <h6 className="text-xs font-medium text-green-600 dark:text-green-400 mb-1">Discounts</h6>
                                    <div className="space-y-1">
                                      {Object.entries(item.booking_data.discounts).map(([key, value]: [string, unknown]) => (
                                        <div key={key} className="flex justify-between text-xs">
                                          <span className="text-gray-600 dark:text-gray-400">
                                            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                          </span>
                                          <span className="font-medium text-green-600 dark:text-green-400">
                                            -${typeof value === 'string' ? value : String(value)}
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Round Trip Discount */}
                                {item.booking_data.round_trip_discount && item.booking_data.round_trip_discount !== '0.00' && (
                                  <div className="flex justify-between text-xs py-1 border-t border-gray-100 dark:border-gray-600">
                                    <span className="text-gray-600 dark:text-gray-400">Round Trip Discount</span>
                                    <span className="font-medium text-green-600 dark:text-green-400">
                                      -${item.booking_data.round_trip_discount}
                                    </span>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Selected Options */}
                      {item.selected_options && Array.isArray(item.selected_options) && item.selected_options.length > 0 && (
                        <div className="bg-white dark:bg-gray-700 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-600">
                          <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Additional Options</h5>
                          <div className="space-y-2">
                            {item.selected_options.map((option: {name?: string, option_id?: string, quantity?: number, price?: number}, optIndex: number) => (
                              <div key={optIndex} className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-600 last:border-b-0">
                                <div>
                                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    {option.name || `Option ${option.option_id?.slice(0, 8) || 'Unknown'}`}
                                  </span>
                                  <span className="text-sm text-gray-600 dark:text-gray-400 ml-2">
                                    ({option.quantity}x)
                                  </span>
                                </div>
                                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {option.price ? orderService.formatCurrency(option.price * (option.quantity || 1), order.currency) : 'Price not available'}
                                </span>
                              </div>
                            ))}
                            <div className="flex justify-between items-center pt-2 border-t border-gray-200 dark:border-gray-600">
                              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Options Total</span>
                              <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                                {orderService.formatCurrency(item.options_total || 0, order.currency)}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Item Total */}
                      <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-4 border border-green-200 dark:border-green-700">
                        <div className="flex justify-between items-center">
                          <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                            Item Total
                          </span>
                          <span className="text-lg font-bold text-green-600 dark:text-green-400">
                            {orderService.formatCurrency(Number(item.total_price || 0), order.currency)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Order Summary */}
                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Order Summary</h3>
                  <div className="space-y-2">
                    {(order.subtotal || 0) > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{t('subtotal')}:</span>
                        <span className="font-medium">{orderService.formatCurrency(order.subtotal || 0, order.currency || 'USD')}</span>
                      </div>
                    )}

                    {(order.service_fee_amount || 0) > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{t('fees')}:</span>
                        <span className="font-medium">{orderService.formatCurrency(order.service_fee_amount || 0, order.currency || 'USD')}</span>
                      </div>
                    )}

                    {(order.tax_amount || 0) > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{t('tax')}:</span>
                        <span className="font-medium">{orderService.formatCurrency(order.tax_amount || 0, order.currency || 'USD')}</span>
                      </div>
                    )}

                    {(order.discount_amount || 0) > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Discount:</span>
                        <span className="font-medium text-green-600">-{orderService.formatCurrency(order.discount_amount || 0, order.currency || 'USD')}</span>
                      </div>
                    )}

                    {(order.agent_commission_amount || 0) > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Commission:</span>
                        <span className="font-medium">{orderService.formatCurrency(order.agent_commission_amount || 0, order.currency || 'USD')}</span>
                      </div>
                    )}

                    <div className="border-t border-gray-200 dark:border-gray-600 pt-2 mt-4">
                      <div className="flex justify-between items-center">
                        <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                          {t('total')}:
                        </span>
                        <span className="text-xl font-bold text-gray-900 dark:text-gray-100">
                          {orderService.formatCurrency(order.total_amount, order.currency || 'USD')}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Debug Information */}
                  <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Debug Information</h4>
                    <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                      <div>Order ID: {order.id}</div>
                      <div>Order Number: {order.order_number}</div>
                      <div>User: {order.user}</div>
                      <div>Status: {order.status}</div>
                      <div>Payment Status: {order.payment_status}</div>
                      <div>Currency: {order.currency}</div>
                      <div className="mt-2">
                        <strong>Pricing Breakdown:</strong>
                        <div className="ml-4">
                          <div>Subtotal: {order.subtotal || 0}</div>
                          <div>Service Fee: {order.service_fee_amount || 0}</div>
                          <div>Tax: {order.tax_amount || 0}</div>
                          <div>Discount: {order.discount_amount || 0}</div>
                          <div>Commission: {order.agent_commission_amount || 0}</div>
                          <div><strong>Total: {order.total_amount}</strong></div>
                        </div>
                      </div>
                      <div className="mt-2">
                        <strong>Calculation Check:</strong>
                        <div className="ml-4">
                          {(() => {
                            const subtotal = Number(order.subtotal || 0);
                            const serviceFee = Number(order.service_fee_amount || 0);
                            const tax = Number(order.tax_amount || 0);
                            const discount = Number(order.discount_amount || 0);
                            const expectedTotal = subtotal + serviceFee + tax - discount;
                            const actualTotal = Number(order.total_amount || 0);
                            const match = Math.abs(expectedTotal - actualTotal) < 0.01; // Allow for floating point precision

                            return (
                              <>
                                <div>Expected Total: {expectedTotal.toFixed(2)}</div>
                                <div>Actual Total: {actualTotal.toFixed(2)}</div>
                                <div>Match: {match ? '✅' : '❌'}</div>
                                {!match && (
                                  <div className="text-red-500 text-xs mt-1">
                                    Difference: {Math.abs(expectedTotal - actualTotal).toFixed(2)}
                                  </div>
                                )}
                              </>
                            );
                          })()}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Special Requests */}
              {order.special_requests && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <MessageSquare className="w-5 h-5 mr-2" />
                    {t('specialRequestsTitle')}
                  </h2>
                  <p className="text-gray-700 dark:text-gray-300">
                    {order.special_requests}
                  </p>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Customer Information */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                  <User className="w-5 h-5 mr-2" />
                  {t('customerInformation')}
                </h2>

                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <User className="w-4 h-4 text-gray-500 flex-shrink-0" />
                    <span className="text-gray-700 dark:text-gray-300 truncate">{order.customer_name}</span>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Mail className="w-4 h-4 text-gray-500 flex-shrink-0" />
                    <span className="text-gray-700 dark:text-gray-300 truncate text-sm">{order.customer_email}</span>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Phone className="w-4 h-4 text-gray-500 flex-shrink-0" />
                    <span className="text-gray-700 dark:text-gray-300 truncate">{order.customer_phone}</span>
                  </div>
                </div>
              </div>

              {/* Payment Information */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                  <CreditCard className="w-5 h-5 mr-2" />
                  {t('paymentInfo')}
                </h2>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{t('paymentStatusLabel')}:</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${orderService.getPaymentStatusColor(order.payment_status)}`}>
                      {t(orderService.getPaymentStatusKey(order.payment_status))}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{t('paymentAmount')}:</span>
                    <span className="font-semibold text-gray-900 dark:text-gray-100">
                      {orderService.formatCurrency(order.total_amount, order.currency)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{t('orderDateLabel')}:</span>
                    <span className="text-gray-700 dark:text-gray-300">
                      {orderService.formatDate(order.created_at)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Order Timeline */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  {t('orderStatus')}
                </h2>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{t('orderCreated')}</p>
                        <p className="text-xs text-gray-500">{orderService.formatDate(order.created_at)}</p>
                      </div>
                    </div>
                    
                    {/* WhatsApp Button for Order Created Status */}
                    {whatsappLink && order.status === 'pending' && (
                      <motion.button
                        onClick={() => window.open(whatsappLink, '_blank')}
                        className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 sm:py-2 text-xs sm:text-sm bg-green-50 hover:bg-green-100 text-green-700 border border-green-200 hover:border-green-300 dark:bg-green-900/20 dark:text-green-400 dark:border-green-700 dark:hover:bg-green-900/30 rounded-lg transition-all duration-300 flex-shrink-0"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <MessageCircle className="w-3 h-3 sm:w-4 sm:h-4" />
                        <span className="hidden sm:inline">{t('completeAndPay')}</span>
                      </motion.button>
                    )}
                  </div>

                  {order.status !== 'pending' && (
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${
                        order.status === 'cancelled' ? 'bg-red-500' : 'bg-green-500'
                      }`}></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {order.status === 'cancelled' ? t('orderCancelled') : 
                           order.status === 'confirmed' ? t('orderConfirmed') :
                           order.status === 'completed' ? t('orderCompleted') : 
                           t('statusChanged')}
                        </p>
                        <p className="text-xs text-gray-500">{orderService.formatDate(order.updated_at)}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </ProtectedRoute>
  );
}