'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { AgentCommission } from '@/app/lib/types/api';
import { formatCommissionStatus } from '@/lib/api/agent-utils';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
import {
  CurrencyDollarIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ArrowPathIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';

export default function AgentCommissionsPage() {
  const t = useTranslations('agent');
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
    commissions,
    commissionsLoading,
    commissionsError,
    commissionSummary,
    monthlyCommission,
    loadCommissions,
    loadCommissionSummary,
    loadMonthlyCommission,
    clearError,
  } = useAgent();

  // State for UI
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    start_date: '',
    end_date: ''
  });
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);

  // Load initial data
  useEffect(() => {
    loadCommissions();
    loadCommissionSummary();
    loadMonthlyCommission(selectedYear, selectedMonth);
  }, [loadCommissions, loadCommissionSummary, loadMonthlyCommission, selectedYear, selectedMonth]);

  // Handle search
  const handleSearch = () => {
    loadCommissions(filters);
  };

  // Handle period change

  // Get status color
  const getStatusColorClass = (status: string) => {
    const colorMap: Record<string, string> = {
      pending: 'yellow',
      approved: 'blue',
      paid: 'green',
      rejected: 'red',
      cancelled: 'gray',
    };
    return colorMap[status] || 'gray';
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
      pending: ClockIcon,
      approved: CheckCircleIcon,
      paid: BanknotesIcon,
      rejected: XCircleIcon,
      cancelled: ExclamationTriangleIcon,
    };
    return iconMap[status] || ClockIcon;
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

  // Get month name
  const getMonthName = (month: number) => {
    const months = [
      t('commissions.january'), t('commissions.february'), t('commissions.march'),
      t('commissions.april'), t('commissions.may'), t('commissions.june'),
      t('commissions.july'), t('commissions.august'), t('commissions.september'),
      t('commissions.october'), t('commissions.november'), t('commissions.december')
    ];
    return months[month - 1];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t('commissions.title')}
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {t('commissions.subtitle')}
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <button
            onClick={() => {
              loadCommissions();
              loadCommissionSummary();
              loadMonthlyCommission(selectedYear, selectedMonth);
            }}
            className={cn(
              "inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
              isRTL ? "space-x-reverse space-x-2" : "space-x-2"
            )}
          >
            <ArrowPathIcon className="w-4 h-4" />
            <span>{t('commissions.refresh')}</span>
          </button>
        </div>
      </div>

      {/* Commission Summary Cards */}
      {commissionSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('commissions.totalCommission')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {formatCurrency(commissionSummary.total_commission)}
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
                  <ChartBarIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('commissions.totalOrders')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {commissionSummary.total_orders}
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
                      {t('commissions.pendingCommission')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {formatCurrency(commissionSummary.status_stats?.pending?.amount || 0)}
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
                  <BanknotesIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('commissions.paidCommission')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {formatCurrency(commissionSummary.status_stats?.paid?.amount || 0)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Monthly Commission Card */}
      {monthlyCommission && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              {t('commissions.monthlyCommission')} - {getMonthName(monthlyCommission.month)} {monthlyCommission.year}
            </h3>
            <div className="flex items-center space-x-2">
              <select
                value={selectedYear}
                onChange={(e) => {
                  const year = parseInt(e.target.value);
                  setSelectedYear(year);
                  loadMonthlyCommission(year, selectedMonth);
                }}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
              <select
                value={selectedMonth}
                onChange={(e) => {
                  const month = parseInt(e.target.value);
                  setSelectedMonth(month);
                  loadMonthlyCommission(selectedYear, month);
                }}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                  <option key={month} value={month}>{getMonthName(month)}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(monthlyCommission.total_commission)}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {t('commissions.totalCommission')}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {formatCurrency(monthlyCommission.pending_commission)}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {t('commissions.pendingCommission')}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(monthlyCommission.paid_commission)}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {t('commissions.paidCommission')}
              </div>
            </div>
          </div>
        </div>
      )}

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
                placeholder={t('commissions.searchPlaceholder')}
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
            <span>Filters</span>
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
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="">{t('commissions.filters.allStatuses')}</option>
                  <option value="pending">{t('commissions.statusOptions.pending')}</option>
                  <option value="approved">{t('commissions.statusOptions.approved')}</option>
                  <option value="paid">{t('commissions.statusOptions.paid')}</option>
                  <option value="rejected">{t('commissions.statusOptions.rejected')}</option>
                  <option value="cancelled">{t('commissions.statusOptions.cancelled')}</option>
                </select>
              </div>

              {/* Date From */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('commissions.dateFrom')}
                </label>
                <input
                  type="date"
                  value={filters.start_date}
                  onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Date To */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('commissions.dateTo')}
                </label>
                <input
                  type="date"
                  value={filters.end_date}
                  onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
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
                    start_date: '',
                    end_date: ''
                  });
                  loadCommissions();
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {t('commissions.clearFilters')}
              </button>
              <button
                onClick={() => loadCommissions(filters)}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {t('commissions.applyFilters')}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Commissions Table */}
      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        {commissionsLoading ? (
          <div className="p-8 text-center">
            <div className="inline-flex items-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className={cn("ml-3 text-gray-600 dark:text-gray-400", isRTL && "ml-0 mr-3")}>
                {t('commissions.loading')}
              </span>
            </div>
          </div>
        ) : commissionsError ? (
          <div className="p-8 text-center">
            <div className="text-red-600 dark:text-red-400">
              {commissionsError}
            </div>
            <button
              onClick={() => {
                clearError();
                loadCommissions(filters);
              }}
              className="mt-2 text-sm text-blue-600 hover:text-blue-500"
            >
              {t('commissions.retry')}
            </button>
          </div>
        ) : commissions.length === 0 ? (
          <div className="p-8 text-center">
            <CurrencyDollarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {t('commissions.noCommissions')}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {t('commissions.noCommissionsDescription')}
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
                    {t('commissions.orderNumber')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('commissions.orderAmount')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('commissions.commissionRate')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('commissions.commissionAmount')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    Status
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('commissions.date')}
                  </th>
                  <th className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                    isRTL && "text-right"
                  )}>
                    {t('commissions.actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {commissions.map((commission: AgentCommission) => {
                  const StatusIcon = getStatusIcon(commission.status);
                  
                  return (
                    <tr key={commission.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {commission.order_number}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(commission.order_amount, commission.currency)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 dark:text-white">
                          {commission.commission_rate}%
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(commission.commission_amount, commission.currency)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={cn(
                          "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                          `bg-${getStatusColorClass(commission.status)}-100 text-${getStatusColorClass(commission.status)}-800 dark:bg-${getStatusColorClass(commission.status)}-900 dark:text-${getStatusColorClass(commission.status)}-200`
                        )}>
                          <StatusIcon className="w-3 h-3 mr-1" />
                          {formatCommissionStatus(commission.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {formatDate(commission.created_at)}
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

      {/* Commission Trends */}
      {commissions.length > 0 && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            {t('commissions.commissionTrends')}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(
                  commissions.reduce((sum: number, commission: AgentCommission) => 
                    commission.status === 'paid' ? sum + commission.commission_amount : sum, 0
                  )
                )}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {t('commissions.totalPaid')}
              </div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <ClockIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(
                  commissions.reduce((sum: number, commission: AgentCommission) => 
                    commission.status === 'pending' ? sum + commission.commission_amount : sum, 0
                  )
                )}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {t('commissions.totalPending')}
              </div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {commissions.length}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {t('commissions.totalCommissions')}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
