'use client';

import { useTranslations } from 'next-intl';
import { AgentDashboard } from '@/components/agent/AgentDashboard';
import { AgentStatsCards } from '@/components/agent/AgentStatsCards';
import { AgentRecentOrders } from '@/components/agent/AgentRecentOrders';
import { AgentCommissionChart } from '@/components/agent/AgentCommissionChart';

export default function AgentPage() {
  const t = useTranslations('agent');

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          {t('dashboard.title')}
        </h1>
        <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1 sm:mt-2">
          {t('dashboard.subtitle')}
        </p>
      </div>

      {/* Stats Cards */}
      <AgentStatsCards />

      {/* Dashboard Content */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-6">
        {/* Main Dashboard */}
        <div className="xl:col-span-2">
          <AgentDashboard />
        </div>

        {/* Sidebar */}
        <div className="space-y-4 sm:space-y-6">
          {/* Commission Chart */}
          <AgentCommissionChart />
          
          {/* Recent Orders */}
          <AgentRecentOrders />
        </div>
      </div>
    </div>
  );
}
