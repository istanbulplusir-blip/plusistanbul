'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardContent } from '@/components/ui/Card';
import { 
  CurrencyDollarIcon,
  ShoppingBagIcon,
  UserGroupIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { agentApi } from '@/lib/api/agents';
import AgentErrorHandler from './AgentErrorHandler';

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

function StatCard({ title, value, change, changeType, icon: Icon, color }: StatCardProps) {
  const changeColor = {
    positive: 'text-green-600 dark:text-green-400',
    negative: 'text-red-600 dark:text-red-400',
    neutral: 'text-gray-600 dark:text-gray-400'
  }[changeType];

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              {title}
            </p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {value}
            </p>
            <p className={`text-sm ${changeColor} mt-1`}>
              {change}
            </p>
          </div>
          <div className={`p-3 rounded-lg ${color}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function AgentStatsCards() {
  const t = useTranslations('agent.stats');
  const [stats, setStats] = useState<StatCardProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const dashboardStats = await agentApi.dashboard.getDashboardStats();
        
        // Transform API data to stats format
        const statsData: StatCardProps[] = [
          {
            title: t('totalCommission'),
            value: `$${(dashboardStats.total_commission || 0).toLocaleString()}`,
            change: '+12.5% from last month', // This would come from API comparison
            changeType: 'positive' as const,
            icon: CurrencyDollarIcon,
            color: 'bg-green-500'
          },
          {
            title: t('totalOrders'),
            value: (dashboardStats.total_orders || 0).toString(),
            change: '+8.2% from last month', // This would come from API comparison
            changeType: 'positive' as const,
            icon: ShoppingBagIcon,
            color: 'bg-blue-500'
          },
          {
            title: t('totalCustomers'),
            value: (dashboardStats.total_customers || 0).toString(),
            change: '+3 new this week', // This would come from API comparison
            changeType: 'positive' as const,
            icon: UserGroupIcon,
            color: 'bg-purple-500'
          },
          {
            title: t('conversionRate'),
            value: `${(dashboardStats.conversion_rate || 0).toFixed(1)}%`,
            change: '-2.1% from last month', // This would come from API comparison
            changeType: 'negative' as const,
            icon: ChartBarIcon,
            color: 'bg-orange-500'
          }
        ];
        
        setStats(statsData);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها');
        
        // Fallback to mock data
        const mockStats: StatCardProps[] = [
          {
            title: 'Total Commission',
            value: '$2,450.00',
            change: '+12.5% from last month',
            changeType: 'positive' as const,
            icon: CurrencyDollarIcon,
            color: 'bg-green-500'
          },
          {
            title: 'Total Orders',
            value: '47',
            change: '+8.2% from last month',
            changeType: 'positive' as const,
            icon: ShoppingBagIcon,
            color: 'bg-blue-500'
          },
          {
            title: 'Total Customers',
            value: '23',
            change: '+3 new this week',
            changeType: 'positive' as const,
            icon: UserGroupIcon,
            color: 'bg-purple-500'
          },
          {
            title: 'Conversion Rate',
            value: '68.5%',
            change: '-2.1% from last month',
            changeType: 'negative' as const,
            icon: ChartBarIcon,
            color: 'bg-orange-500'
          }
        ];
        setStats(mockStats);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [t]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="mb-8">
        <AgentErrorHandler 
          error={error}
          onRetry={() => window.location.reload()}
          title="خطا در بارگذاری آمار"
          description="آمار داشبورد بارگذاری نشد. لطفاً دوباره تلاش کنید."
        />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  );
}
