'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { motion, AnimatePresence } from 'framer-motion';
import { orderService, Order } from '../../../lib/services/orderService';

import ProtectedRoute from '../../../components/ProtectedRoute';
import { 
  Package, 
  Calendar, 
  Clock, 
  CreditCard, 
  Eye, 
  Download,
  CheckCircle,
  XCircle,
  AlertCircle,
  Sparkles
} from 'lucide-react';





export default function OrdersPage() {
  const router = useRouter();
  const t = useTranslations('orders');
  
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showOrderDetails, setShowOrderDetails] = useState(false);

  const fetchOrders = useCallback(async () => {
    try {
      const data = await orderService.getUserOrders();
      setOrders(data.results || data.orders || []);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : t('errorLoadingOrders');
      console.error('Fetch orders error:', err);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [t]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'text-green-600 bg-green-100';
      case 'completed':
        return 'text-blue-600 bg-blue-100';
      case 'cancelled':
        return 'text-red-600 bg-red-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed':
        return t('confirmed');
      case 'completed':
        return t('completed');
      case 'cancelled':
        return t('cancelled');
      case 'pending':
        return t('pending');
      default:
        return status;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'cancelled':
        return <XCircle className="w-4 h-4" />;
      case 'pending':
        return <Clock className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const formatPrice = (price: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('fa-IR', {
      style: 'currency',
      currency: currency
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR');
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('fa-IR');
  };

  const handleViewOrder = (order: Order) => {
    setSelectedOrder(order);
    setShowOrderDetails(true);
  };

  const handleDownloadInvoice = async (orderId: string) => {
    try {
      const response = await fetch(`/api/v1/orders/${orderId}/invoice/`, { credentials: 'include' });

      if (!response.ok) {
        throw new Error(t('errorGettingInvoice'));
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice-${orderId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : t('errorDownloadInvoice');
      console.error('Download invoice error:', err);
      alert(errorMessage);
    }
  };

  if (isLoading) {
    return (
      <motion.div 
        className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-4xl mx-auto px-4">
          <motion.div 
            className="text-center"
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
            <motion.p 
              className="text-lg font-medium bg-gradient-to-r from-gray-700 to-gray-500 dark:from-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {t('loadingOrders')}
            </motion.p>
          </motion.div>
        </div>
      </motion.div>
    );
  }

  return (
    <ProtectedRoute>
      <motion.div 
        className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <motion.div 
            className="mb-8"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="flex items-center gap-3 mb-4">
              <motion.div 
                className="w-12 h-12 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center shadow-lg"
                whileHover={{ scale: 1.05, rotate: 5 }}
                animate={{ y: [0, -2, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Package className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <motion.h1 
                  className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent mb-2"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                >
                  {t('title')}
                </motion.h1>
                <motion.p 
                  className="text-gray-600 dark:text-gray-400"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                >
                  {t('ordersHistoryDescription')}
                </motion.p>
              </div>
            </div>
          </motion.div>

          <AnimatePresence>
            {error && (
              <motion.div 
                className="mb-6 p-6 bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 backdrop-blur-xl border border-red-200/50 dark:border-red-700/50 rounded-2xl shadow-glass dark:shadow-glass-dark"
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.5 }}
              >
                <div className="flex items-start gap-3">
                  <motion.div
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                  >
                    <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                  </motion.div>
                  <p className="text-red-800 dark:text-red-300 font-medium">{error}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {orders.length === 0 ? (
            <motion.div 
              className="text-center py-16"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <motion.div 
                className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-2xl mb-8 shadow-lg"
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ duration: 0.8, delay: 0.5, type: "spring", bounce: 0.4 }}
                whileHover={{ scale: 1.05, rotate: 5 }}
              >
                <Package className="w-12 h-12 text-gray-400 dark:text-gray-300" />
              </motion.div>
              
              <motion.h2 
                className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent mb-6"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.7 }}
              >
                {t('noOrdersYet')}
              </motion.h2>
              
              <motion.p 
                className="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto text-lg leading-relaxed"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8 }}
              >
                {t('noOrdersDescription')}
              </motion.p>
              
              <motion.button
                onClick={() => router.push('/tours')}
                className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-8 py-4 rounded-2xl font-semibold transition-all duration-300 shadow-lg hover:shadow-glow flex items-center gap-3 mx-auto"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.9 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <Sparkles className="w-5 h-5" />
                {t('browseProducts')}
              </motion.button>
            </motion.div>
          ) : (
            <motion.div 
              className="space-y-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              {orders.map((order, index) => (
                <motion.div 
                  key={order.id} 
                  className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-4 sm:p-6 lg:p-8 hover:shadow-xl transition-all duration-300"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 + (index * 0.1) }}
                  whileHover={{ scale: 1.01, y: -2 }}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 sm:mb-6 gap-4">
                    <div className="flex items-center gap-3 sm:gap-4">
                      <motion.div 
                        className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-r from-primary-100 to-secondary-100 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-xl sm:rounded-2xl flex items-center justify-center border border-primary-200/50 dark:border-primary-700/50 flex-shrink-0"
                        whileHover={{ scale: 1.05, rotate: 5 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Package className="w-6 h-6 sm:w-7 sm:h-7 text-primary-600 dark:text-primary-400" />
                      </motion.div>
                      <div className="min-w-0 flex-1">
                        <motion.h3 
                          className="text-lg sm:text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent truncate"
                          whileHover={{ scale: 1.02 }}
                        >
                          {t('orderNumber', { orderNumber: order.order_number })}
                        </motion.h3>
                        <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                          <Clock className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
                          <span className="truncate">{formatDateTime(order.created_at)}</span>
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full sm:w-auto">
                      <motion.span 
                        className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-semibold flex items-center gap-1.5 sm:gap-2 border shadow-sm flex-shrink-0 ${getStatusColor(order.status)} ${
                          order.status === 'confirmed' ? 'border-green-200/50 dark:border-green-700/50' :
                          order.status === 'pending' ? 'border-yellow-200/50 dark:border-yellow-700/50' :
                          order.status === 'cancelled' ? 'border-red-200/50 dark:border-red-700/50' :
                          'border-gray-200/50 dark:border-gray-700/50'
                        }`}
                        whileHover={{ scale: 1.05 }}
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.3, delay: 0.5 + (index * 0.1) }}
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
                        <span className="hidden sm:inline">{getStatusText(order.status)}</span>
                      </motion.span>
                      
                      <div className="flex items-center gap-2 ml-auto sm:ml-0">
                        <motion.button
                          onClick={() => handleViewOrder(order)}
                          className="p-2 sm:p-3 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 bg-gray-50 dark:bg-gray-700/50 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg sm:rounded-xl transition-all duration-200 border border-gray-200/50 dark:border-gray-600/50"
                          title={t('viewDetailsTooltip')}
                          whileHover={{ scale: 1.1, rotate: 5 }}
                          whileTap={{ scale: 0.9 }}
                        >
                          <Eye className="w-4 h-4 sm:w-5 sm:h-5" />
                        </motion.button>
                        <motion.button
                          onClick={() => handleDownloadInvoice(order.id)}
                          className="p-2 sm:p-3 text-gray-600 dark:text-gray-400 hover:text-green-600 dark:hover:text-green-400 bg-gray-50 dark:bg-gray-700/50 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg sm:rounded-xl transition-all duration-200 border border-gray-200/50 dark:border-gray-600/50"
                          title={t('downloadInvoiceTooltip')}
                          whileHover={{ scale: 1.1, rotate: -5 }}
                          whileTap={{ scale: 0.9 }}
                        >
                          <Download className="w-4 h-4 sm:w-5 sm:h-5" />
                        </motion.button>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-3 sm:mb-4">
                    <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                      <Calendar className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
                      <span className="truncate">{t('orderDateLabel')}: {formatDate(order.created_at)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                      <CreditCard className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
                      <span className="truncate">{t('paymentStatusLabel')}: {order.payment_status}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-600 dark:text-gray-400 sm:col-span-2 lg:col-span-1">
                      <span className="font-medium text-gray-900 dark:text-gray-100 truncate">
                        {t('totalAmount')}: {formatPrice(order.total_amount, order.currency)}
                      </span>
                    </div>
                  </div>

                  <div className="border-t border-gray-200 dark:border-gray-700 pt-3 sm:pt-4">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 sm:mb-3 text-sm sm:text-base">{t('orderItems')} ({order.items.length}):</h4>
                    <div className="space-y-2">
                      {order.items.slice(0, 3).map((item, index) => (
                        <div key={index} className="text-xs sm:text-sm">
                          <div className="flex flex-col gap-1">
                            <div>
                              <span className="text-gray-700 dark:text-gray-300 font-medium">
                                {item.product_title}
                              </span>
                            </div>

                            {item.variant_name && (
                              <div className="text-xs text-gray-600 dark:text-gray-400">
                                {t('variantType')}: {item.variant_name}
                              </div>
                            )}

                            {/* Show participants breakdown for tours */}
                            {item.product_type === 'tour' && item.booking_data?.participants && (
                              <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700/50 rounded text-xs">
                                <div className="text-gray-600 dark:text-gray-400 mb-1 font-medium">{t('participants')}:</div>
                                <div className="space-y-0.5">
                                  {item.booking_data.participants.adult > 0 && (
                                    <div className="flex justify-between">
                                      <span>Adult ({item.booking_data.participants.adult}x)</span>
                                      <span>{formatPrice(item.unit_price * item.booking_data.participants.adult / item.quantity * item.quantity, order.currency)}</span>
                                    </div>
                                  )}
                                  {item.booking_data.participants.child > 0 && (
                                    <div className="flex justify-between">
                                      <span>Child ({item.booking_data.participants.child}x)</span>
                                      <span>{formatPrice(item.unit_price * item.booking_data.participants.child * 0.7 / item.quantity * item.quantity, order.currency)}</span>
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

                            {item.booking_date && (
                              <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                {t('bookingDate')}: {formatDate(item.booking_date)}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                      {order.items.length > 3 && (
                        <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 pt-1">
                          {t('moreItems', { count: order.items.length - 3 })}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* Order Details Modal */}
          {showOrderDetails && selectedOrder && (
            <motion.div 
              className="fixed inset-0 bg-black/60 dark:bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-2 sm:p-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowOrderDetails(false)}
            >
              <motion.div 
                className="bg-white dark:bg-gray-800 rounded-2xl max-w-4xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-200/50 dark:border-gray-700/50"
                initial={{ scale: 0.9, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.9, opacity: 0, y: 20 }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-gray-800 dark:to-gray-800 rounded-t-2xl">
                  <div className="flex items-center justify-between">
                    <motion.h2 
                      className="text-lg sm:text-xl font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.2 }}
                    >
                      {t('orderDetailsTitle', { orderNumber: selectedOrder.order_number })}
                    </motion.h2>
                    <motion.button
                      onClick={() => setShowOrderDetails(false)}
                      className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      whileHover={{ scale: 1.1, rotate: 90 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <XCircle className="w-5 h-5 sm:w-6 sm:h-6" />
                    </motion.button>
                  </div>
                </div>

                <motion.div 
                  className="p-4 sm:p-6 space-y-4 sm:space-y-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  {/* Order Status */}
                  <div className="flex flex-wrap items-center gap-2 sm:gap-4">
                    <motion.span 
                      className={`px-3 sm:px-4 py-2 rounded-full text-xs sm:text-sm font-medium flex items-center gap-2 ${getStatusColor(selectedOrder.status)}`}
                      whileHover={{ scale: 1.05 }}
                    >
                      {getStatusIcon(selectedOrder.status)}
                      <span className="hidden sm:inline">{getStatusText(selectedOrder.status)}</span>
                    </motion.span>
                    <motion.span 
                      className={`px-3 sm:px-4 py-2 rounded-full text-xs sm:text-sm font-medium ${
                        selectedOrder.payment_status === 'paid' 
                          ? 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20' 
                          : 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20'
                      }`}
                      whileHover={{ scale: 1.05 }}
                    >
                      {selectedOrder.payment_status === 'paid' ? t('paidStatus') : t('pendingPayment')}
                    </motion.span>
                  </div>

                  {/* Customer Information */}
                  <motion.div 
                    className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 sm:p-6"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                  >
                    <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3 sm:mb-4">{t('customerInformation')}</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 text-sm">
                      <div>
                        <p className="text-gray-600 dark:text-gray-400">{t('fullName')}:</p>
                        <p className="font-medium text-gray-900 dark:text-gray-100 truncate">{selectedOrder.customer_name}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 dark:text-gray-400">{t('email')}:</p>
                        <p className="font-medium text-gray-900 dark:text-gray-100 truncate text-xs sm:text-sm">{selectedOrder.customer_email}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 dark:text-gray-400">{t('phone')}:</p>
                        <p className="font-medium text-gray-900 dark:text-gray-100">{selectedOrder.customer_phone}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 dark:text-gray-400">{t('address')}:</p>
                        <p className="font-medium text-gray-900 dark:text-gray-100">{selectedOrder.notes || t('noAddress')}</p>
                      </div>
                    </div>
                  </motion.div>

                  {/* Order Items */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                  >
                    <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3 sm:mb-4">{t('orderItemsTitle')}</h3>
                    <div className="space-y-3 sm:space-y-4">
                      {selectedOrder.items.map((item, index) => (
                        <motion.div 
                          key={index} 
                          className="border border-gray-200 dark:border-gray-600 rounded-xl p-3 sm:p-4 bg-gray-50/50 dark:bg-gray-700/30"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.6 + (index * 0.1) }}
                          whileHover={{ scale: 1.01 }}
                        >
                          <div className="mb-2">
                            <h4 className="font-medium text-gray-900 dark:text-gray-100 text-sm sm:text-base">{item.product_title}</h4>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                            <div>
                              <span className="font-medium">{t('productType')}:</span> {item.product_type}
                            </div>
                            <div>
                              <span className="font-medium">{t('quantity')}:</span> {item.quantity}
                            </div>
                            {item.booking_date && (
                              <div>
                                <span className="font-medium">{t('bookingDate')}:</span> {formatDate(item.booking_date)}
                              </div>
                            )}
                            {item.booking_time && (
                              <div>
                                <span className="font-medium">{t('bookingTime')}:</span> {item.booking_time}
                              </div>
                            )}
                          </div>
                          {item.variant_name && (
                            <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-2">
                              <span className="font-medium">{t('variantType')}:</span> {item.variant_name}
                            </p>
                          )}
                          {item.selected_options && (
                            <div className="mt-2">
                              <p className="text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('selectedOptions')}:</p>
                              <div className="flex flex-wrap gap-1">
                                {orderService.formatSelectedOptions(item.selected_options).map((option, optIndex) => (
                                  <span 
                                    key={optIndex}
                                    className="inline-block px-2 py-1 text-xs bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300 rounded border border-blue-200 dark:border-blue-700"
                                  >
                                    <span className="font-medium">{option.name}:</span> {option.value}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>

                  {/* Special Requests */}
                  {selectedOrder.special_requests && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.7 }}
                    >
                      <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">{t('specialRequestsTitle')}</h3>
                      <p className="text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700/50 rounded-xl p-3 sm:p-4 text-sm sm:text-base">
                        {selectedOrder.special_requests}
                      </p>
                    </motion.div>
                  )}

                  {/* Order Summary */}
                  <motion.div 
                    className="border-t border-gray-200 dark:border-gray-700 pt-4"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                  >
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                      <span className="text-base sm:text-lg font-semibold text-gray-900 dark:text-gray-100">{t('grandTotal')}:</span>
                      <motion.span 
                        className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
                        whileHover={{ scale: 1.05 }}
                      >
                        {formatPrice(selectedOrder.total_amount)}
                      </motion.span>
                    </div>
                  </motion.div>
                </motion.div>
              </motion.div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </ProtectedRoute>
  );
} 