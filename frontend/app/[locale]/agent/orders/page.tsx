'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
import {
  ShoppingBagIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  CalendarDaysIcon,
  CurrencyDollarIcon,
  UserIcon,
  TruckIcon,
  TicketIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

export default function AgentOrdersPage() {
  const t = useTranslations('agent');
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
    orders,
    ordersLoading,
    ordersError,
    loadOrders,
    clearError
  } = useAgent();

  // State for UI
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    date_from: '',
    date_to: '',
    customer: ''
  });

  // Load initial data
  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  // Handle search
  const handleSearch = () => {
    loadOrders(filters.status);
  };

  // Get status color
  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      pending: 'yellow',
      confirmed: 'blue',
      cancelled: 'red',
      completed: 'green',
    };
    return colorMap[status] || 'gray';
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
      pending: ClockIcon,
      confirmed: CheckCircleIcon,
      cancelled: XCircleIcon,
      completed: CheckCircleIcon,
    };
    return iconMap[status] || ExclamationTriangleIcon;
  };

  // Get product type icon
  const getProductTypeIcon = (productType: string) => {
    const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
      tour: CalendarDaysIcon,
      transfer: TruckIcon,
      event: TicketIcon,
      car_rental: TruckIcon,
    };
    return iconMap[productType] || ShoppingBagIcon;
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(locale, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format currency
  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t('orders.title')}
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {t('orders.subtitle')}
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <button
            onClick={() => loadOrders()}
            className={cn(
              "inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
              isRTL ? "space-x-reverse space-x-2" : "space-x-2"
            )}
          >
            <ArrowPathIcon className="w-4 h-4" />
            <span>{t('orders.refresh')}</span>
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          {/* Search */}
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder={t('orders.searchPlaceholder')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className={cn(
                  "block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                  isRTL && "text-right"
                )}
              />
            </div>
          </div>

          {/* Filters Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              "inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
              isRTL ? "space-x-reverse space-x-2" : "space-x-2"
            )}
          >
            <FunnelIcon className="w-4 h-4" />
            <span>{t('orders.filters')}</span>
            {showFilters ? (
              <ChevronUpIcon className="w-4 h-4" />
            ) : (
              <ChevronDownIcon className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('orders.status')}
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="">{t('orders.allStatuses')}</option>
                  <option value="pending">{t('orders.pending')}</option>
                  <option value="confirmed">{t('orders.confirmed')}</option>
                  <option value="cancelled">{t('orders.cancelled')}</option>
                  <option value="completed">{t('orders.completed')}</option>
                </select>
              </div>

              {/* Date From */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('orders.dateFrom')}
                </label>
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Date To */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('orders.dateTo')}
                </label>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Customer Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('orders.customer')}
                </label>
                <input
                  type="text"
                  placeholder={t('orders.customerPlaceholder')}
                  value={filters.customer}
                  onChange={(e) => setFilters({ ...filters, customer: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            {/* Filter Actions */}
            <div className="mt-4 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setFilters({
                    status: '',
                    date_from: '',
                    date_to: '',
                    customer: ''
                  });
                  loadOrders();
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {t('orders.clearFilters')}
              </button>
              <button
                onClick={() => loadOrders(filters.status)}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {t('orders.applyFilters')}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Orders Table */}
      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        {ordersLoading ? (
          <div className="p-8 text-center">
            <div className="inline-flex items-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className={cn("ml-3 text-gray-600 dark:text-gray-400", isRTL && "ml-0 mr-3")}>
                {t('orders.loading')}
              </span>
            </div>
          </div>
        ) : ordersError ? (
          <div className="p-8 text-center">
            <div className="text-red-600 dark:text-red-400">
              {ordersError}
            </div>
            <button
              onClick={() => {
                clearError();
                loadOrders(filters.status);
              }}
              className="mt-2 text-sm text-blue-600 hover:text-blue-500"
            >
              {t('orders.retry')}
            </button>
          </div>
        ) : orders.length === 0 ? (
          <div className="p-8 text-center">
            <ShoppingBagIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {t('orders.noOrders')}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {t('orders.noOrdersDescription')}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('orders.orderNumber')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('orders.customer')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('orders.product')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('orders.amount')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('orders.status')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('orders.date')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('orders.actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {orders.map((order: Record<string, unknown>, index: number) => {
                  const StatusIcon = getStatusIcon(order.status as string);
                  const ProductIcon = getProductTypeIcon((order.items as Array<{product_type?: string}>)?.[0]?.product_type || 'tour');
                  
                  return (
                    <tr key={order.id as string || order.order_number as string || `order-${index}`} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {order.order_number as string}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-8 w-8">
                            <div className="h-8 w-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                              <UserIcon className="h-4 w-4 text-gray-600 dark:text-gray-300" />
                            </div>
                          </div>
                          <div className={cn("ml-3", isRTL && "ml-0 mr-3")}>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {order.customer_name as string}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {order.customer_email as string}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <ProductIcon className="h-5 w-5 text-gray-400 mr-2" />
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {(order.items as Array<{product_title?: string}>)?.[0]?.product_title || t('orders.unknownProduct')}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {(order.items as Array<{product_type?: string}>)?.[0]?.product_type || 'tour'}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(order.total_amount as number, order.currency as string)}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {(order.items as Array<unknown>)?.length || 0} {t('orders.items')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={cn(
                          "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                          `bg-${getStatusColor(order.status as string)}-100 text-${getStatusColor(order.status as string)}-800 dark:bg-${getStatusColor(order.status as string)}-900 dark:text-${getStatusColor(order.status as string)}-200`
                        )}>
                          <StatusIcon className="w-3 h-3 mr-1" />
                          {t(`orders.${order.status as string}`) || (order.status as string)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {formatDate(order.created_at as string)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">
                          <EyeIcon className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Order Statistics */}
      {orders.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ShoppingBagIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('orders.totalOrders')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {orders.length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('orders.totalRevenue')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {formatCurrency(
                        orders.reduce((sum: number, order: Record<string, unknown>) => sum + (order.total_amount as number || 0), 0),
                        (orders[0] as Record<string, unknown>)?.currency as string || 'USD'
                      )}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('orders.completedOrders')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {orders.filter((order: Record<string, unknown>) => order.status === 'completed').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClockIcon className="h-6 w-6 text-yellow-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('orders.pendingOrders')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {orders.filter((order: Record<string, unknown>) => order.status === 'pending').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
