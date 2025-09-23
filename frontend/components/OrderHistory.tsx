'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Package, Calendar, DollarSign, Eye, XCircle, Filter, Search, Clock, CheckCircle, AlertCircle, Truck, Music, MapPin, RefreshCw } from 'lucide-react';
import { orderService, Order } from '../lib/services/orderService';
import { useTranslations } from 'next-intl';

interface OrderHistoryProps {
  onShowToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export default function OrderHistory({ onShowToast }: OrderHistoryProps) {
  const t = useTranslations('orders');
  const [orders, setOrders] = useState<Order[]>([]);
  const [filteredOrders, setFilteredOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [productTypeFilter, setProductTypeFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);

  const loadOrders = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await orderService.getUserOrders();
      
      if (result.success && result.orders) {
        setOrders(result.orders);
        setFilteredOrders(result.orders);
      } else {
        setError(result.message || t('errorLoadingOrders'));
        onShowToast(result.message || t('errorLoadingOrders'), 'error');
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : t('errorLoadingOrders');
      setError(errorMessage);
      onShowToast(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  }, [onShowToast, t]);

  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  // Filter and search functionality
  useEffect(() => {
    let filtered = orders;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(order =>
        order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.items.some(item => 
          item.product_title.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => order.status === statusFilter);
    }

    // Product type filter
    if (productTypeFilter !== 'all') {
      filtered = filtered.filter(order =>
        order.items.some(item => item.product_type === productTypeFilter)
      );
    }

    setFilteredOrders(filtered);
  }, [orders, searchTerm, statusFilter, productTypeFilter]);

  const handleViewOrder = (orderNumber: string) => {
    // Navigate to order detail page
    window.location.href = `/orders/${orderNumber}`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'cancelled':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getProductTypeIcon = (type: string) => {
    switch (type) {
      case 'tour':
        return <MapPin className="w-4 h-4 text-blue-500" />;
      case 'event':
        return <Music className="w-4 h-4 text-purple-500" />;
      case 'transfer':
        return <Truck className="w-4 h-4 text-green-500" />;
      default:
        return <Package className="w-4 h-4 text-gray-500" />;
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
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300';
    }
  };

  if (isLoading) {
    return (
      <motion.div 
        className="flex flex-col items-center justify-center py-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div 
          className="relative inline-block mb-6"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 p-1">
            <div className="w-full h-full rounded-full bg-white dark:bg-gray-900 flex items-center justify-center">
              <Package className="w-5 h-5 text-primary-500" />
            </div>
          </div>
        </motion.div>
        <motion.span 
          className="text-lg font-medium bg-gradient-to-r from-gray-700 to-gray-500 dark:from-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {t('loadingOrders')}
        </motion.span>
      </motion.div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
        <motion.button
          onClick={loadOrders}
          className="px-4 py-2 bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white rounded-xl transition-all duration-300 shadow-md hover:shadow-lg"
          whileHover={{ scale: 1.02, y: -1 }}
          whileTap={{ scale: 0.98 }}
        >
          <RefreshCw className="w-4 h-4 mr-2 inline" />
          {t('retryButton')}
        </motion.button>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="text-center py-12">
        <Package className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{t('noOrdersFound')}</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          {t('noOrdersYetMessage')}
        </p>
        <motion.button
          onClick={() => window.location.href = '/'}
          className="px-4 py-2 bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white rounded-xl transition-all duration-300 shadow-md hover:shadow-lg"
          whileHover={{ scale: 1.02, y: -1 }}
          whileTap={{ scale: 0.98 }}
        >
          {t('viewProducts')}
        </motion.button>
      </div>
    );
  }

  return (
    <motion.div 
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Search and Filter Header */}
      <motion.div 
        className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark p-6 border border-gray-200/50 dark:border-gray-700/50"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <motion.div 
              className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center shadow-lg"
              whileHover={{ scale: 1.05, rotate: 5 }}
              animate={{ y: [0, -2, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Package className="w-5 h-5 text-white" />
            </motion.div>
            <motion.h2 
              className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              {t('ordersHistory')}
            </motion.h2>
          </div>
          <motion.button
            onClick={loadOrders}
            className="flex items-center gap-2 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 bg-primary-50 dark:bg-primary-900/20 px-4 py-2 rounded-xl transition-colors border border-primary-200/50 dark:border-primary-700/50"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <RefreshCw className="w-4 h-4" />
            {t('refresh')}
          </motion.button>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder={t('searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-3 py-2 text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 border border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-300 dark:hover:border-blue-500 transition-colors"
            >
              <Filter className="w-4 h-4" />
              {t('filter')}
            </button>
            
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {t('ordersCount', { filtered: filteredOrders.length, total: orders.length })}
            </div>
          </div>
        </div>

        {/* Filter Options */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('orderStatusFilter')}
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">{t('allStatuses')}</option>
                  <option value="confirmed">{t('confirmed')}</option>
                  <option value="pending">{t('pending')}</option>
                  <option value="cancelled">{t('cancelled')}</option>
                  <option value="completed">{t('completed')}</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('productTypeFilter')}
                </label>
                <select
                  value={productTypeFilter}
                  onChange={(e) => setProductTypeFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">{t('allProducts')}</option>
                  <option value="tour">{t('tours')}</option>
                  <option value="event">{t('events')}</option>
                  <option value="transfer">{t('transfers')}</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </motion.div>

      {/* Orders List */}
      {filteredOrders.length === 0 ? (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {searchTerm || statusFilter !== 'all' || productTypeFilter !== 'all' 
              ? t('noFilteredOrders')
              : t('noOrdersFound')
            }
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            {searchTerm || statusFilter !== 'all' || productTypeFilter !== 'all'
              ? t('changeFilters')
              : t('noOrdersYetMessage')
            }
          </p>
        </div>
      ) : (
        <motion.div 
          className="space-y-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {filteredOrders.map((order, index) => (
          <motion.div
            key={order.id}
            className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/50 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 shadow-glass dark:shadow-glass-dark"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 + (index * 0.1) }}
            whileHover={{ scale: 1.01, y: -2 }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-1">
                  {getProductTypeIcon(order.items[0]?.product_type || 'package')}
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {t('orderNumber', { orderNumber: order.order_number })}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {orderService.formatDate(order.created_at)}
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(order.status)}`}>
                  {getStatusIcon(order.status)}
                  {order.status === 'confirmed' ? t('confirmed') :
                   order.status === 'pending' ? t('pending') : 
                   order.status === 'cancelled' ? t('cancelled') : 
                   order.status === 'completed' ? t('completed') : order.status}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {t('totalPrice')}: {orderService.formatCurrency(order.total_amount, order.currency)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Package className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {t('itemCount')}: {order.items.length}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {t('orderDateLabel')}: {orderService.formatDate(order.created_at)}
                </span>
              </div>
            </div>

            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">{t('orderItems')}:</h4>
              <div className="space-y-2">
                {order.items.slice(0, 3).map((item) => (
                  <div key={item.id} className="text-sm">
                    <div className="text-gray-700 dark:text-gray-300 mb-1">{item.product_title}</div>
                    {item.variant_name && (
                      <div className="text-xs text-gray-600 dark:text-gray-400">{t('variantType')}: {item.variant_name}</div>
                    )}
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {item.quantity} {t('itemsUnit')}
                      {item.booking_date && ` • ${orderService.formatDate(item.booking_date)}`}
                    </div>
                  </div>
                ))}
                {order.items.length > 3 && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {t('moreItems', { count: order.items.length - 3 })}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center justify-end mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <motion.button
                onClick={() => handleViewOrder(order.order_number)}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white rounded-xl transition-all duration-300 shadow-md hover:shadow-lg"
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
              >
                <Eye className="w-4 h-4" />
                {t('viewDetails')}
              </motion.button>
            </div>
          </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
} 