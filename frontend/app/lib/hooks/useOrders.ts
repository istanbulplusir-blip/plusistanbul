import useSWR from 'swr';
import { getOrders, getOrderDetail, createOrder } from '../api/orders';
import type { CreateOrderPayload } from '../api/orders';



// Fetcher functions
const ordersFetcher = async () => {
  const response = await getOrders();
  return (response as { data: unknown }).data;
};

const orderDetailFetcher = async (orderNumber: string) => {
  const response = await getOrderDetail(orderNumber);
  return (response as { data: unknown }).data;
};

// Hook for orders list
export const useOrders = () => {
  const { data, error, isLoading, mutate } = useSWR(
    ['/api/orders'],
    () => ordersFetcher(),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    }
  );

  const createNewOrder = async (orderData: CreateOrderPayload) => {
    try {
      const response = await createOrder(orderData);
      await mutate();
      return { success: true, order: (response as { data: { order: unknown } }).data.order };
    } catch (error: unknown) {
      return { 
        success: false, 
        error: error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'data' in error.response && error.response.data && typeof error.response.data === 'object' && 'error' in error.response.data && typeof error.response.data.error === 'string'
          ? error.response.data.error 
          : 'Failed to create order' 
      };
    }
  };

  return {
    orders: data || [],
    isLoading,
    error,
    createOrder: createNewOrder,
    mutate,
  };
};

// Hook for order detail
export const useOrderDetail = (orderNumber: string) => {
  const { data, error, isLoading, mutate } = useSWR(
    orderNumber ? [`/api/orders/${orderNumber}`] : null,
    () => orderDetailFetcher(orderNumber),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    }
  );

  return {
    order: data,
    isLoading,
    error,
    mutate,
  };
}; 