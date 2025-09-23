'use client';

import { useState, useEffect } from 'react';
import { useAgentTranslations } from '@/lib/hooks/useAgentTranslations';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  CalendarDaysIcon,
  ArrowTrendingUpIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';

interface AnalyticsData {
  // Overview Stats
  total_bookings: number;
  total_revenue: number;
  total_commission: number;
  total_customers: number;
  
  // Growth Stats
  bookings_growth: number;
  revenue_growth: number;
  commission_growth: number;
  customers_growth: number;
  
  // Period Comparison
  current_period: {
    bookings: number;
    revenue: number;
    commission: number;
    customers: number;
  };
  previous_period: {
    bookings: number;
    revenue: number;
    commission: number;
    customers: number;
  };
  
  // Charts Data
  bookings_chart: Array<{ date: string; bookings: number }>;
  revenue_chart: Array<{ date: string; revenue: number }>;
  commission_chart: Array<{ date: string; commission: number }>;
  
  // Top Products
  top_tours: Array<{ name: string; bookings: number; revenue: number }>;
  top_transfers: Array<{ name: string; bookings: number; revenue: number }>;
  top_car_rentals: Array<{ name: string; bookings: number; revenue: number }>;
  top_events: Array<{ name: string; bookings: number; revenue: number }>;
  
  // Customer Analytics
  customer_segments: Array<{ segment: string; count: number; percentage: number }>;
  repeat_customers: number;
  new_customers: number;
  
  // Performance Metrics
  conversion_rate: number;
  average_booking_value: number;
  customer_satisfaction: number;
}

interface DateRange {
  start: string;
  end: string;
  label: string;
}

interface ChartType {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
}

export default function AgentAnalyticsPage() {
  const t = useAgentTranslations();
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
  } = useAgent();

  // State for analytics data
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loadingData, setLoadingData] = useState(false);
  
  // State for filters
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange>({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
    label: 'آخرین 30 روز'
  });
  
  const [selectedChartType, setSelectedChartType] = useState('bookings');

  // Date range options
  const dateRanges: DateRange[] = [
    {
      start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'آخرین 7 روز'
    },
    {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'آخرین 30 روز'
    },
    {
      start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'آخرین 90 روز'
    },
    {
      start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'آخرین سال'
    }
  ];

  // Chart types
  const chartTypes: ChartType[] = [
    { id: 'bookings', name: t.analytics.bookings, icon: CalendarDaysIcon },
    { id: 'revenue', name: t.analytics.revenue, icon: CurrencyDollarIcon },
    { id: 'commission', name: t.analytics.commission, icon: ArrowTrendingUpIcon },
    { id: 'customers', name: t.analytics.customers, icon: UserGroupIcon }
  ];

  // Load analytics data
  const loadAnalyticsData = async () => {
    setLoadingData(true);
    try {
      // Mock analytics data
      const mockData: AnalyticsData = {
        total_bookings: 156,
        total_revenue: 12500000,
        total_commission: 1875000,
        total_customers: 89,
        bookings_growth: 12.5,
        revenue_growth: 8.3,
        commission_growth: 8.3,
        customers_growth: 15.2,
        current_period: {
          bookings: 156,
          revenue: 12500000,
          commission: 1875000,
          customers: 89
        },
        previous_period: {
          bookings: 138,
          revenue: 11500000,
          commission: 1725000,
          customers: 77
        },
        bookings_chart: [
          { date: '2024-01-01', bookings: 5 },
          { date: '2024-01-02', bookings: 8 },
          { date: '2024-01-03', bookings: 12 },
          { date: '2024-01-04', bookings: 7 },
          { date: '2024-01-05', bookings: 15 },
          { date: '2024-01-06', bookings: 9 },
          { date: '2024-01-07', bookings: 11 }
        ],
        revenue_chart: [
          { date: '2024-01-01', revenue: 450000 },
          { date: '2024-01-02', revenue: 720000 },
          { date: '2024-01-03', revenue: 1080000 },
          { date: '2024-01-04', revenue: 630000 },
          { date: '2024-01-05', revenue: 1350000 },
          { date: '2024-01-06', revenue: 810000 },
          { date: '2024-01-07', revenue: 990000 }
        ],
        commission_chart: [
          { date: '2024-01-01', commission: 67500 },
          { date: '2024-01-02', commission: 108000 },
          { date: '2024-01-03', commission: 162000 },
          { date: '2024-01-04', commission: 94500 },
          { date: '2024-01-05', commission: 202500 },
          { date: '2024-01-06', commission: 121500 },
          { date: '2024-01-07', commission: 148500 }
        ],
        top_tours: [
          { name: 'تور اصفهان', bookings: 45, revenue: 3600000 },
          { name: 'تور شیراز', bookings: 38, revenue: 3040000 },
          { name: 'تور کیش', bookings: 32, revenue: 2560000 }
        ],
        top_transfers: [
          { name: 'فرودگاه امام - تهران', bookings: 28, revenue: 420000 },
          { name: 'تهران - اصفهان', bookings: 22, revenue: 1760000 },
          { name: 'تهران - شیراز', bookings: 18, revenue: 2160000 }
        ],
        top_car_rentals: [
          { name: 'پراید', bookings: 15, revenue: 750000 },
          { name: 'سمند', bookings: 12, revenue: 840000 },
          { name: 'پژو 206', bookings: 8, revenue: 640000 }
        ],
        top_events: [
          { name: 'کنسرت موسیقی سنتی', bookings: 25, revenue: 1250000 },
          { name: 'نمایش تئاتر', bookings: 18, revenue: 900000 },
          { name: 'جشنواره فیلم', bookings: 12, revenue: 600000 }
        ],
        customer_segments: [
          { segment: 'VIP', count: 15, percentage: 16.9 },
          { segment: 'Regular', count: 45, percentage: 50.6 },
          { segment: 'New', count: 29, percentage: 32.6 }
        ],
        repeat_customers: 45,
        new_customers: 44,
        conversion_rate: 68.5,
        average_booking_value: 80128,
        customer_satisfaction: 4.7
      };
      
      setAnalyticsData(mockData);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setLoadingData(false);
    }
  };

  // Load data on component mount and when filters change
  useEffect(() => {
    loadAnalyticsData();
  }, [selectedDateRange]);

  // Format currency
  const formatCurrency = (amount: number, currency: string = 'IRR') => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  // Format percentage
  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  // Get growth icon and color
  const getGrowthIcon = (growth: number) => {
    if (growth > 0) {
      return <ArrowUpIcon className="w-4 h-4 text-green-500" />;
    } else if (growth < 0) {
      return <ArrowDownIcon className="w-4 h-4 text-red-500" />;
    }
    return null;
  };

  // Get growth color
  const getGrowthColor = (growth: number) => {
    if (growth > 0) return 'text-green-600';
    if (growth < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  // Export data
  const exportData = (format: 'csv' | 'pdf') => {
    // Mock export functionality
    alert(`Exporting data as ${format.toUpperCase()}...`);
  };

  if (loadingData) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            {t.analytics.loading}
          </p>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            {t.analytics.noData}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {t.analytics.title}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {t.analytics.subtitle}
              </p>
            </div>
            
            <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-3">
              <select
                value={selectedDateRange.label}
                onChange={(e) => {
                  const range = dateRanges.find(r => r.label === e.target.value);
                  if (range) setSelectedDateRange(range);
                }}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {dateRanges.map((range) => (
                  <option key={range.label} value={range.label}>
                    {range.label}
                  </option>
                ))}
              </select>
              
              <div className="flex gap-2">
                <button
                  onClick={() => exportData('csv')}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                  CSV
                </button>
                <button
                  onClick={() => exportData('pdf')}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                  PDF
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CalendarDaysIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {t.analytics.totalBookings}
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {analyticsData.total_bookings}
                </p>
                <div className="flex items-center mt-1">
                  {getGrowthIcon(analyticsData.bookings_growth)}
                  <span className={cn("text-sm font-medium", getGrowthColor(analyticsData.bookings_growth))}>
                    {formatPercentage(analyticsData.bookings_growth)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {t.analytics.totalRevenue}
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {formatCurrency(analyticsData.total_revenue)}
                </p>
                <div className="flex items-center mt-1">
                  {getGrowthIcon(analyticsData.revenue_growth)}
                  <span className={cn("text-sm font-medium", getGrowthColor(analyticsData.revenue_growth))}>
                    {formatPercentage(analyticsData.revenue_growth)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowTrendingUpIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {t.analytics.totalCommission}
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {formatCurrency(analyticsData.total_commission)}
                </p>
                <div className="flex items-center mt-1">
                  {getGrowthIcon(analyticsData.commission_growth)}
                  <span className={cn("text-sm font-medium", getGrowthColor(analyticsData.commission_growth))}>
                    {formatPercentage(analyticsData.commission_growth)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {t.analytics.totalCustomers}
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {analyticsData.total_customers}
                </p>
                <div className="flex items-center mt-1">
                  {getGrowthIcon(analyticsData.customers_growth)}
                  <span className={cn("text-sm font-medium", getGrowthColor(analyticsData.customers_growth))}>
                    {formatPercentage(analyticsData.customers_growth)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Chart Type Selector */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                {t.analytics.charts}
              </h3>
              
              <div className="flex flex-wrap gap-2 mb-6">
                {chartTypes.map((chart) => (
                  <button
                    key={chart.id}
                    onClick={() => setSelectedChartType(chart.id)}
                    className={cn(
                      "inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md transition-colors",
                      isRTL ? "space-x-reverse space-x-2" : "space-x-2",
                      selectedChartType === chart.id
                        ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
                        : "border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                    )}
                  >
                    <chart.icon className="w-4 h-4" />
                    <span>{chart.name}</span>
                  </button>
                ))}
              </div>

              {/* Mock Chart */}
              <div className="h-64 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-gray-600 dark:text-gray-400">
                    {t.analytics.chartPlaceholder}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Top Products */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {t.analytics.topTours}
            </h3>
            <div className="space-y-4">
              {analyticsData.top_tours.map((tour, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {tour.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      {tour.bookings} {t.analytics.bookings}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(tour.revenue)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {t.analytics.topTransfers}
            </h3>
            <div className="space-y-4">
              {analyticsData.top_transfers.map((transfer, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {transfer.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      {transfer.bookings} {t.analytics.bookings}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(transfer.revenue)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Customer Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {t.analytics.customerSegments}
            </h3>
            <div className="space-y-4">
              {analyticsData.customer_segments.map((segment, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-gray-900 dark:text-white">
                    {segment.segment}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500 dark:text-gray-500">
                      {segment.count}
                    </span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {segment.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {t.analytics.customerTypes}
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-900 dark:text-white">
                  {t.analytics.repeatCustomers}
                </span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {analyticsData.repeat_customers}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-900 dark:text-white">
                  {t.analytics.newCustomers}
                </span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {analyticsData.new_customers}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {t.analytics.performanceMetrics}
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-900 dark:text-white">
                  {t.analytics.conversionRate}
                </span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {analyticsData.conversion_rate}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-900 dark:text-white">
                  {t.analytics.averageBookingValue}
                </span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {formatCurrency(analyticsData.average_booking_value)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-900 dark:text-white">
                  {t.analytics.customerSatisfaction}
                </span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {analyticsData.customer_satisfaction}/5
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
