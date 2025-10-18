'use client';

import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/Badge';
import { 
  CalendarDaysIcon,
  TruckIcon,
  TicketIcon
} from '@heroicons/react/24/outline';
import { agentApi } from '@/lib/api/agents';
import AgentLoading from './AgentLoading';
import AgentErrorHandler from './AgentErrorHandler';

interface ProductItemProps {
  name: string;
  type: 'tour' | 'transfer' | 'car' | 'event';
  sales: number;
  commission: number;
  orders: number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

function ProductItem({ name, type, sales, commission, orders, icon: Icon, color }: ProductItemProps) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="w-4 h-4 text-white" />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {name}
          </p>
          <Badge variant="secondary" className="text-xs">
            {type === 'tour' ? 'Tour' : type === 'transfer' ? 'Transfer' : type === 'car' ? 'Car Rental' : 'Event'}
          </Badge>
        </div>
      </div>
      
      <div className="text-right">
        <p className="text-sm font-semibold text-gray-900 dark:text-white">
          ${sales.toLocaleString()}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Commission: ${commission}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {orders} orders
        </p>
      </div>
    </div>
  );
}

export function AgentTopProducts() {
  const [products, setProducts] = useState<ProductItemProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTopProducts = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const dashboardStats = await agentApi.dashboard.getDashboardStats();
        
        // Transform API data to products format
        const productsData: ProductItemProps[] = (dashboardStats.top_products || []).map((product, index) => {
          const icons = [CalendarDaysIcon, TruckIcon, TicketIcon];
          const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500'];
          const types: ('tour' | 'transfer' | 'car' | 'event')[] = ['tour', 'transfer', 'car', 'event'];
          
          return {
            name: product.name || `Product ${index + 1}`,
            type: types[index % types.length],
            sales: product.revenue || 0,
            commission: (product.revenue || 0) * 0.15, // Assuming 15% commission rate
            orders: product.bookings || 0,
            icon: icons[index % icons.length],
            color: colors[index % colors.length]
          };
        });
        
        setProducts(productsData);
      } catch (err) {
        console.error('Error fetching top products:', err);
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها');
        
        // Fallback to mock data
        const mockProducts: ProductItemProps[] = [
          {
            name: 'تور باغ‌های ایرانی',
            type: 'tour' as const,
            sales: 12500,
            commission: 1875,
            orders: 15,
            icon: CalendarDaysIcon,
            color: 'bg-blue-500'
          },
          {
            name: 'ترانسفر فرودگاه',
            type: 'transfer' as const,
            sales: 8900,
            commission: 1335,
            orders: 22,
            icon: TruckIcon,
            color: 'bg-green-500'
          },
          {
            name: 'اجاره ماشین لوکس',
            type: 'car' as const,
            sales: 6700,
            commission: 1005,
            orders: 8,
            icon: TruckIcon,
            color: 'bg-purple-500'
          },
          {
            name: 'کنسرت موسیقی سنتی',
            type: 'event' as const,
            sales: 4200,
            commission: 630,
            orders: 12,
            icon: TicketIcon,
            color: 'bg-orange-500'
          }
        ];
        setProducts(mockProducts);
      } finally {
        setLoading(false);
      }
    };

    fetchTopProducts();
  }, []);

  if (loading) {
    return <AgentLoading message="در حال بارگذاری محصولات برتر..." />;
  }

  if (error) {
    return (
      <AgentErrorHandler 
        error={error}
        onRetry={() => window.location.reload()}
        title="خطا در بارگذاری محصولات برتر"
        description="لیست محصولات برتر بارگذاری نشد. لطفاً دوباره تلاش کنید."
      />
    );
  }

  return (
    <div className="space-y-2">
      {products.map((product, index) => (
        <ProductItem key={index} {...product} />
      ))}
      
      {/* View All Button */}
      <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
        <button className="w-full text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium">
          View All →
        </button>
      </div>
    </div>
  );
}
