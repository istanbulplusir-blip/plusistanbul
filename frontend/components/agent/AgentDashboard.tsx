'use client';

import { useTranslations } from 'next-intl';
import { useLocale } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { AgentSalesChart } from './AgentSalesChart';
import { AgentCommissionChart } from './AgentCommissionChart';
import { AgentPerformanceChart } from './AgentPerformanceChart';
import { AgentCommissionTrendChart } from './AgentCommissionTrendChart';
import { AgentTopProducts } from './AgentTopProducts';
import { AgentRecentActivity } from './AgentRecentActivity';
import { AgentTotalBookings } from './AgentTotalBookings';
import { PlusIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';

export function AgentDashboard() {
  const t = useTranslations('agent');
  const locale = useLocale();
  const isRTL = locale === 'fa';

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className={cn(
            "flex items-center justify-between",
            isRTL ? "flex-row-reverse" : "flex-row"
          )}>
            <span className="text-base sm:text-lg">{t('dashboard.quickActions')}</span>
            <ArrowTrendingUpIcon className="w-5 h-5 text-primary-600" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <Button 
              variant="outline" 
              className="h-16 sm:h-20 flex flex-col items-center justify-center hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
            >
              <PlusIcon className="w-5 h-5 sm:w-6 sm:h-6 text-primary-600 mb-1 sm:mb-2" />
              <span className="text-xs sm:text-sm font-medium text-center">{t('dashboard.bookTour')}</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-16 sm:h-20 flex flex-col items-center justify-center hover:bg-secondary-50 dark:hover:bg-secondary-900/20 transition-colors"
            >
              <PlusIcon className="w-5 h-5 sm:w-6 sm:h-6 text-secondary-600 mb-1 sm:mb-2" />
              <span className="text-xs sm:text-sm font-medium text-center">{t('dashboard.bookTransfer')}</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-16 sm:h-20 flex flex-col items-center justify-center hover:bg-accent-50 dark:hover:bg-accent-900/20 transition-colors"
            >
              <PlusIcon className="w-5 h-5 sm:w-6 sm:h-6 text-accent-600 mb-1 sm:mb-2" />
              <span className="text-xs sm:text-sm font-medium text-center">{t('dashboard.bookCarRental')}</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-16 sm:h-20 flex flex-col items-center justify-center hover:bg-warning-50 dark:hover:bg-warning-900/20 transition-colors"
            >
              <PlusIcon className="w-5 h-5 sm:w-6 sm:h-6 text-warning-600 mb-1 sm:mb-2" />
              <span className="text-xs sm:text-sm font-medium text-center">{t('dashboard.bookEvent')}</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6">
        {/* Sales Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base sm:text-lg">{t('dashboard.totalRevenue')}</CardTitle>
          </CardHeader>
          <CardContent>
            <AgentSalesChart />
          </CardContent>
        </Card>

        {/* Commission Chart */}
        <AgentCommissionChart />
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6">
        {/* Performance Chart */}
        <AgentPerformanceChart />

        {/* Commission Trend Chart */}
        <AgentCommissionTrendChart />
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-6">
        {/* Total Bookings */}
        <AgentTotalBookings />

        {/* Top Products */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base sm:text-lg">{t('dashboard.topProducts')}</CardTitle>
          </CardHeader>
          <CardContent>
            <AgentTopProducts />
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base sm:text-lg">{t('dashboard.recentBookings')}</CardTitle>
          </CardHeader>
          <CardContent>
            <AgentRecentActivity />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
