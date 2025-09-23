'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { agentApi } from '@/lib/api/agents';
import AgentLoading from './AgentLoading';
import AgentErrorHandler from './AgentErrorHandler';

interface BookingStats {
  totalBookings: number;
  thisMonth: number;
  lastMonth: number;
  growth: number;
}

export function AgentTotalBookings() {
  const t = useTranslations('agent.dashboard');
  const [stats, setStats] = useState<BookingStats>({
    totalBookings: 0,
    thisMonth: 0,
    lastMonth: 0,
    growth: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBookingStats = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const dashboardStats = await agentApi.dashboard.getDashboardStats();
        
        // Calculate booking stats from monthly sales data
        const monthlySales = dashboardStats.monthly_sales || [];
        const totalBookings = dashboardStats.total_orders || 0;
        
        // Calculate this month and last month bookings
        const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM format
        const lastMonth = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 7);
        
        const thisMonthData = monthlySales.find(item => item.month === currentMonth);
        const lastMonthData = monthlySales.find(item => item.month === lastMonth);
        
        const thisMonthBookings = thisMonthData ? Math.max(1, Math.floor(thisMonthData.amount / 100)) : 0;
        const lastMonthBookings = lastMonthData ? Math.max(1, Math.floor(lastMonthData.amount / 100)) : 0;
        
        const growth = lastMonthBookings > 0 ? ((thisMonthBookings - lastMonthBookings) / lastMonthBookings) * 100 : 0;
        
        setStats({
          totalBookings,
          thisMonth: thisMonthBookings,
          lastMonth: lastMonthBookings,
          growth
        });
      } catch (err) {
        console.error('Error fetching booking stats:', err);
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها');
        
        // Fallback to mock data
        setStats({
          totalBookings: 1,
          thisMonth: 1,
          lastMonth: 0,
          growth: 100
        });
      } finally {
        setLoading(false);
      }
    };

    fetchBookingStats();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base sm:text-lg">{t('totalBookings')}</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentLoading message="در حال بارگذاری آمار سفارشات..." />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base sm:text-lg">{t('totalBookings')}</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentErrorHandler 
            error={error}
            onRetry={() => window.location.reload()}
            title="خطا در بارگذاری آمار سفارشات"
            description="آمار سفارشات بارگذاری نشد. لطفاً دوباره تلاش کنید."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base sm:text-lg">{t('totalBookings')}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Total Bookings */}
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats.totalBookings}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Total Bookings
            </div>
          </div>

          {/* This Month */}
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">This Month</span>
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              {stats.thisMonth}
            </span>
          </div>

          {/* Growth */}
          {stats.growth !== 0 && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Growth</span>
              <span className={`text-sm font-medium ${
                stats.growth > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {stats.growth > 0 ? '+' : ''}{stats.growth.toFixed(1)}%
              </span>
            </div>
          )}

          {/* Last Month */}
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Last Month</span>
            <span className="text-sm text-gray-900 dark:text-white">
              {stats.lastMonth}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
