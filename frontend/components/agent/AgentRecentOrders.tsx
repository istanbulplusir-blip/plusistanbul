'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { 
  CalendarDaysIcon,
  TruckIcon,
  TicketIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { agentApi } from '@/lib/api/agents';
import AgentLoading from './AgentLoading';
import AgentErrorHandler from './AgentErrorHandler';

interface OrderItemProps {
  id: string;
  customer: string;
  product: string;
  type: 'tour' | 'transfer' | 'car' | 'event';
  amount: number;
  commission: number;
  status: 'pending' | 'confirmed' | 'cancelled';
  date: string;
  icon: React.ComponentType<{ className?: string }>;
}

function OrderItem({ 
  customer, 
  product, 
  amount, 
  commission, 
  status, 
  date, 
  icon: Icon 
}: OrderItemProps) {
  const t = useTranslations('agent');

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    confirmed: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    cancelled: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
  };

  return (
    <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
          <Icon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
        </div>
        
        <div>
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {customer}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {product}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {date}
          </p>
        </div>
      </div>
      
      <div className="flex items-center space-x-3">
        <div className="text-right">
          <p className="text-sm font-semibold text-gray-900 dark:text-white">
            ${amount?.toLocaleString() || '0'}
          </p>
          <p className="text-xs text-green-600 dark:text-green-400">
            {t('orders.commission')}: ${commission}
          </p>
        </div>
        
        <Badge className={statusColors[status]}>
          {status === 'pending' ? 'Pending' : status === 'confirmed' ? 'Confirmed' : status === 'cancelled' ? 'Cancelled' : status === 'completed' ? 'Completed' : status}
        </Badge>
        
        <Button variant="ghost" size="sm" className="p-1">
          <EyeIcon className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}

export function AgentRecentOrders() {
  const [orders, setOrders] = useState<OrderItemProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecentOrders = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const agentBookings = await agentApi.booking.getAgentBookings();
        
        // Transform API data to orders format
        const ordersData: OrderItemProps[] = agentBookings.slice(0, 5).map((order, index) => {
          const icons = [CalendarDaysIcon, TruckIcon, TicketIcon];
          // const types: ('tour' | 'transfer' | 'car' | 'event')[] = ['tour', 'transfer', 'car', 'event']; // Unused variable
          
          // Determine product type from order items
          const productType = order.items && order.items.length > 0 ? order.items[0].product_type : 'tour';
          const productTitle = order.items && order.items.length > 0 ? order.items[0].product_title : 'محصول';
          
          return {
            id: order.order_number,
            customer: order.customer_name || 'نامشخص',
            product: productTitle,
            type: productType as 'tour' | 'transfer' | 'car' | 'event',
            amount: order.total_amount,
            commission: order.commission_amount || 0,
            status: order.status === 'confirmed' ? 'confirmed' as const : 
                   order.status === 'cancelled' ? 'cancelled' as const : 'pending' as const,
            date: new Date(order.created_at).toLocaleDateString('fa-IR'),
            icon: icons[index % icons.length]
          };
        });
        
        setOrders(ordersData);
      } catch (err) {
        console.error('Error fetching recent orders:', err);
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها');
        
        // Fallback to mock data
        const mockOrders: OrderItemProps[] = [
          {
            id: 'ORD-001',
            customer: 'احمد محمدی',
            product: 'تور باغ‌های ایرانی',
            type: 'tour' as const,
            amount: 1250,
            commission: 187,
            status: 'confirmed' as const,
            date: 'امروز',
            icon: CalendarDaysIcon
          },
          {
            id: 'ORD-002',
            customer: 'فاطمه احمدی',
            product: 'ترانسفر فرودگاه',
            type: 'transfer' as const,
            amount: 450,
            commission: 67,
            status: 'pending' as const,
            date: 'دیروز',
            icon: TruckIcon
          },
          {
            id: 'ORD-003',
            customer: 'علی رضایی',
            product: 'اجاره ماشین لوکس',
            type: 'car' as const,
            amount: 800,
            commission: 120,
            status: 'confirmed' as const,
            date: '2 روز پیش',
            icon: TruckIcon
          },
          {
            id: 'ORD-004',
            customer: 'مریم حسینی',
            product: 'کنسرت موسیقی سنتی',
            type: 'event' as const,
            amount: 350,
            commission: 52,
            status: 'cancelled' as const,
            date: '3 روز پیش',
            icon: TicketIcon
          }
        ];
        setOrders(mockOrders);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentOrders();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{'Recent Orders'}</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentLoading message="در حال بارگذاری سفارشات اخیر..." />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{'Recent Orders'}</CardTitle>
        </CardHeader>
        <CardContent>
          <AgentErrorHandler 
            error={error}
            onRetry={() => window.location.reload()}
            title="خطا در بارگذاری سفارشات اخیر"
            description="لیست سفارشات اخیر بارگذاری نشد. لطفاً دوباره تلاش کنید."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>{'Recent Orders'}</span>
          <Button variant="ghost" size="sm" className="text-primary-600 hover:text-primary-700">
            {'View All'}
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {orders.map((order, index) => (
            <OrderItem key={order.id || `order-${index}`} {...order} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
