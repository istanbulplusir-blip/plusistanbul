/**
 * Agent Commission Trend Chart - نمایش روند کمیسیون در طول زمان
 */

'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { agentApi } from '@/lib/api/agents';
import AgentLoading from './AgentLoading';
import AgentErrorHandler from './AgentErrorHandler';

interface CommissionTrendData {
  month: string;
  commission: number;
  cumulative: number;
}

export function AgentCommissionTrendChart() {
  const t = useTranslations('agent.commissions');
  const [trendData, setTrendData] = useState<CommissionTrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCommissionTrend = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const commissionHistory = await agentApi.commissions.getCommissionHistory();
        
        // Ensure commissionHistory is an array
        const historyArray = Array.isArray(commissionHistory) ? commissionHistory : [];
        
        // Group commissions by month and calculate cumulative
        const monthlyCommissions = historyArray.reduce((acc, item) => {
          const month = new Date(item.created_at).toLocaleDateString('fa-IR', { month: 'short' });
          if (!acc[month]) {
            acc[month] = 0;
          }
          acc[month] += Number(item.amount) || 0;
          return acc;
        }, {} as Record<string, number>);
        
        // Transform to chart data with cumulative calculation
        let cumulative = 0;
        const chartData: CommissionTrendData[] = Object.entries(monthlyCommissions).map(([month, commission]) => {
          cumulative += commission;
          return {
            month,
            commission,
            cumulative
          };
        });
        
        setTrendData(chartData);
      } catch (err) {
        console.error('Error fetching commission trend:', err);
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها');
        
        // Fallback to mock data
        const mockData: CommissionTrendData[] = [
          { month: 'Jan', commission: 180, cumulative: 180 },
          { month: 'Feb', commission: 285, cumulative: 465 },
          { month: 'Mar', commission: 450, cumulative: 915 },
          { month: 'Apr', commission: 420, cumulative: 1335 },
          { month: 'May', commission: 283, cumulative: 1618 },
          { month: 'Jun', commission: 358, cumulative: 1976 },
          { month: 'Jul', commission: 523, cumulative: 2499 }
        ];
        setTrendData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchCommissionTrend();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t('commissionTrends')}</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentLoading message="در حال بارگذاری روند کمیسیون..." />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t('commissionTrends')}</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentErrorHandler 
            error={error}
            onRetry={() => window.location.reload()}
            title="خطا در بارگذاری روند کمیسیون"
            description="نمودار روند کمیسیون بارگذاری نشد. لطفاً دوباره تلاش کنید."
          />
        </CardContent>
      </Card>
    );
  }

  const totalCommission = trendData.length > 0 ? trendData[trendData.length - 1].cumulative : 0;
  const monthlyAverage = trendData.length > 0 ? totalCommission / trendData.length : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{t('commissionTrends')}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="commissionGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="cumulativeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="month" 
                className="text-sm text-gray-600 dark:text-gray-400"
                tick={{ fill: 'currentColor' }}
              />
              <YAxis 
                className="text-sm text-gray-600 dark:text-gray-400"
                tick={{ fill: 'currentColor' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--tw-bg-white)',
                  border: '1px solid var(--tw-border-gray-200)',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
                labelStyle={{ color: 'var(--tw-text-gray-900)' }}
                formatter={(value: number, name: string) => [
                  `$${value.toLocaleString()}`,
                  name === 'commission' ? t('monthly_commission') : t('total_commission')
                ]}
              />
              <Area
                type="monotone"
                dataKey="commission"
                stroke="#14b8a6"
                fillOpacity={1}
                fill="url(#commissionGradient)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="cumulative"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#cumulativeGradient)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary Stats */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg">
            <div className="text-2xl font-bold text-teal-600 dark:text-teal-400">
              ${totalCommission.toLocaleString()}
            </div>
            <div className="text-sm text-teal-600 dark:text-teal-400">
              {t('total_commission')}
            </div>
          </div>
          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              ${monthlyAverage.toFixed(0)}
            </div>
            <div className="text-sm text-blue-600 dark:text-blue-400">
              {t('monthly_commission')}
            </div>
          </div>
          <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {trendData.length}
            </div>
            <div className="text-sm text-green-600 dark:text-green-400">
              {'Months'}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
