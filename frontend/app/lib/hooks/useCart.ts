export { useUnifiedCart as useCart } from '../../../lib/contexts/UnifiedCartContext';
import useSWR from 'swr';
import { apiClient } from '../../../lib/api/client';

export const useCartSummary = () => {
  const { data, error, isLoading, mutate } = useSWR(
    ['/cart/summary/'],
    async () => {
      const resp = await apiClient.get('/cart/summary/');
      return (resp as { data: unknown }).data;
    },
    { revalidateOnFocus: false, dedupingInterval: 30000 }
  );
  const summaryData = (data as { total_items: number; subtotal: number; total_price: number; currency: string; items: unknown[] }) || { total_items: 0, subtotal: 0, total_price: 0, currency: 'USD', items: [] };
  return {
    summary: summaryData,
    totalItems: summaryData?.total_items || 0,
    subtotal: summaryData?.subtotal || 0,
    totalPrice: summaryData?.total_price || 0,
    currency: summaryData?.currency || 'USD',
    items: summaryData?.items || [],
    isLoading,
    error,
    mutate,
  };
};

import { useUnifiedCart } from '../../../lib/contexts/UnifiedCartContext';
export const useCartCount = () => {
  const { totalItems } = useUnifiedCart();
  return totalItems;
};