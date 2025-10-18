'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { agentApi } from '@/lib/api/agents';
import AgentLoading from './AgentLoading';
import AgentErrorHandler from './AgentErrorHandler';

interface SalesData {
  month: string;
  sales: number;
  commission: number;
}

export function AgentSalesChart() {
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSalesData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const dashboardStats = await agentApi.dashboard.getDashboardStats();
        
        // Transform API data to chart format
        const chartData: SalesData[] = (dashboardStats.monthly_sales || []).map((item) => ({
          month: item.month || 'Unknown',
          sales: item.amount || 0,
          commission: (item.amount || 0) * 0.15 // Assuming 15% commission rate
        }));
        
        setSalesData(chartData);
      } catch (err) {
        console.error('Error fetching sales data:', err);
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها');
        
        // Fallback to mock data
        const mockData: SalesData[] = [
          { month: 'Jan', sales: 1200, commission: 180 },
          { month: 'Feb', sales: 1900, commission: 285 },
          { month: 'Mar', sales: 3000, commission: 450 },
          { month: 'Apr', sales: 2800, commission: 420 },
          { month: 'May', sales: 1890, commission: 283 },
          { month: 'Jun', sales: 2390, commission: 358 },
          { month: 'Jul', sales: 3490, commission: 523 },
        ];
        setSalesData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchSalesData();
  }, []);

  if (loading) {
    return <AgentLoading message="در حال بارگذاری نمودار فروش..." />;
  }

  if (error) {
    return (
      <AgentErrorHandler 
        error={error}
        onRetry={() => window.location.reload()}
        title="خطا در بارگذاری نمودار فروش"
        description="نمودار فروش ماهانه بارگذاری نشد. لطفاً دوباره تلاش کنید."
      />
    );
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={salesData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
              name === 'sales' ? 'Sales' : 'Commission'
            ]}
          />
          <Line 
            type="monotone" 
            dataKey="sales" 
            stroke="#3b82f6" 
            strokeWidth={3}
            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
          />
          <Line 
            type="monotone" 
            dataKey="commission" 
            stroke="#14b8a6" 
            strokeWidth={3}
            dot={{ fill: '#14b8a6', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#14b8a6', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="flex items-center justify-center space-x-6 mt-4">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {'Sales'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-secondary-500 rounded-full"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {'Commission'}
          </span>
        </div>
      </div>
    </div>
  );
}
