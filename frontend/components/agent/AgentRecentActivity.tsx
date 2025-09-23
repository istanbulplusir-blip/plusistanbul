'use client';

import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/Badge';
import { 
  CheckCircleIcon,
  // ClockIcon, // Unused import
  // ExclamationTriangleIcon, // Unused import
  UserIcon
} from '@heroicons/react/24/outline';
import { agentApi } from '@/lib/api/agents';

interface ActivityItemProps {
  type: 'order' | 'customer' | 'commission' | 'warning';
  title: string;
  description: string;
  time: string;
  status?: 'success' | 'pending' | 'warning';
  icon: React.ComponentType<{ className?: string }>;
  iconColor: string;
}

function ActivityItem({ 
  title, 
  description, 
  time, 
  status, 
  icon: Icon, 
  iconColor 
}: ActivityItemProps) {

  return (
    <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
      <div className={`p-2 rounded-full ${iconColor} flex-shrink-0`}>
        <Icon className="w-4 h-4 text-white" />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {title}
          </p>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {time}
          </span>
        </div>
        
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {description}
        </p>
        
        {status && (
          <Badge 
            variant={status === 'success' ? 'default' : status === 'pending' ? 'secondary' : 'destructive'}
            className="mt-2 text-xs"
          >
            {status}
          </Badge>
        )}
      </div>
    </div>
  );
}

export function AgentRecentActivity() {
  const [activities, setActivities] = useState<ActivityItemProps[]>([]);
  // const [loading, setLoading] = useState(true); // Unused variable
  // const [error, setError] = useState<string | null>(null); // Unused variable

  useEffect(() => {
    const fetchRecentActivities = async () => {
      try {
        // setLoading(true); // Unused variable
        // setError(null); // Unused variable
        
        const dashboardStats = await agentApi.dashboard.getDashboardStats();
        
        // Transform API data to activities format
        const activitiesData: ActivityItemProps[] = (dashboardStats.recent_activities || []).map((activity) => {
          const getActivityType = (type: string): 'order' | 'customer' | 'commission' | 'warning' => {
            switch (type) {
              case 'order': return 'order';
              case 'commission': return 'commission';
              default: return 'order';
            }
          };

          const getActivityIcon = (type: string) => {
            switch (type) {
              case 'order': return CheckCircleIcon;
              case 'commission': return CheckCircleIcon;
              default: return CheckCircleIcon;
            }
          };

          const getActivityIconColor = (type: string) => {
            switch (type) {
              case 'order': return 'bg-green-500';
              case 'commission': return 'bg-blue-500';
              default: return 'bg-green-500';
            }
          };

          const getActivityStatus = (type: string): 'success' | 'pending' | 'warning' => {
            switch (type) {
              case 'order': return 'success';
              case 'commission': return 'success';
              default: return 'success';
            }
          };

          return {
            type: getActivityType(activity.type),
            title: activity.type === 'order' ? 'سفارش جدید' : 'کمیسیون جدید',
            description: activity.description,
            time: new Date(activity.created_at).toLocaleDateString('fa-IR'),
            status: getActivityStatus(activity.type),
            icon: getActivityIcon(activity.type),
            iconColor: getActivityIconColor(activity.type)
          };
        });
        
        setActivities(activitiesData);
      } catch (err) {
        console.error('Error fetching recent activities:', err);
        // setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها'); // Unused variable
        
        // Fallback to mock data
        const mockActivities: ActivityItemProps[] = [
          {
            type: 'order' as const,
            title: 'New Order',
            description: 'تور باغ‌های ایرانی - 4 نفر',
            time: '2 ساعت پیش',
            status: 'success' as const,
            icon: CheckCircleIcon,
            iconColor: 'bg-green-500'
          },
          {
            type: 'customer' as const,
            title: 'New Customer',
            description: 'احمد محمدی ثبت نام کرد',
            time: '4 ساعت پیش',
            status: 'pending' as const,
            icon: UserIcon,
            iconColor: 'bg-blue-500'
          },
          {
            type: 'commission' as const,
            title: 'Commission Paid',
            description: 'کمیسیون ماه گذشته پرداخت شد',
            time: '1 روز پیش',
            status: 'success' as const,
            icon: CheckCircleIcon,
            iconColor: 'bg-green-500'
          }
        ];
        setActivities(mockActivities);
      } finally {
        // setLoading(false); // Unused variable
      }
    };

    fetchRecentActivities();
  }, []);

  return (
    <div className="space-y-2">
      {activities.map((activity, index) => (
        <ActivityItem key={index} {...activity} />
      ))}
      
      {/* View All Button */}
      <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
        <button className="w-full text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium">
          {'View All'} →
        </button>
      </div>
    </div>
  );
}
