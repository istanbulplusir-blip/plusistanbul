'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { agentApi } from '@/lib/api/agents';
import AgentLoading from './AgentLoading';
import AgentErrorHandler from './AgentErrorHandler';

interface CommissionData {
  name: string;
  value: number;
  color: string;
}

export function AgentCommissionChart() {
  const t = useTranslations('agent.commissions');
  const [commissionData, setCommissionData] = useState<CommissionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCommissionData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const dashboardStats = await agentApi.dashboard.getDashboardStats();
        
        // Transform API data to chart format
        let chartData: CommissionData[] = [];
        
        if (dashboardStats.top_products && dashboardStats.top_products.length > 0) {
          chartData = dashboardStats.top_products.map((product, index) => {
            const colors = ['#3b82f6', '#14b8a6', '#8b5cf6', '#f59e0b', '#ef4444'];
            return {
              name: product.name || `Product ${index + 1}`,
              value: (product.revenue || 0) * 0.15, // Assuming 15% commission rate
              color: colors[index % colors.length]
            };
          });
        } else {
          // If no products, show total commission as a single item
          const totalCommission = dashboardStats.total_commission || 0;
          if (totalCommission > 0) {
            chartData = [{
              name: 'Total Commission',
              value: totalCommission,
              color: '#3b82f6'
            }];
          }
        }
        
        setCommissionData(chartData);
      } catch (err) {
        console.error('Error fetching commission data:', err);
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها');
        
        // Fallback to mock data
        const mockData: CommissionData[] = [
          { name: 'تورها', value: 1875, color: '#3b82f6' },
          { name: 'ترانسفرها', value: 1335, color: '#14b8a6' },
          { name: 'اجاره ماشین', value: 1005, color: '#8b5cf6' },
          { name: 'رویدادها', value: 630, color: '#f59e0b' },
        ];
        setCommissionData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchCommissionData();
  }, []);

  const totalCommission = commissionData.reduce((sum, item) => sum + item.value, 0);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t('title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentLoading message="در حال بارگذاری نمودار کمیسیون..." />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t('title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentErrorHandler 
            error={error}
            onRetry={() => window.location.reload()}
            title="خطا در بارگذاری نمودار کمیسیون"
            description="نمودار کمیسیون بارگذاری نشد. لطفاً دوباره تلاش کنید."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{t('title')}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={commissionData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {commissionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => [`$${value.toLocaleString()}`, t('commission_amount')]}
                contentStyle={{
                  backgroundColor: 'var(--tw-bg-white)',
                  border: '1px solid var(--tw-border-gray-200)',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
              />
              <Legend 
                verticalAlign="bottom" 
                height={36}
                formatter={(value: string) => (
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {value}
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {t('total_commission')}:
            </span>
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              ${totalCommission.toLocaleString()}
            </span>
          </div>
          
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            {t('filters.this_month')}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
