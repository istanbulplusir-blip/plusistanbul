import { apiClient } from '../../../lib/api/client';
import type { Order, CreateOrderPayload } from '../types/api';

export const getOrders = () => apiClient.get('/orders/');

export const getOrderDetail = (order_number: string) => 
  apiClient.get(`/orders/${order_number}/`);

export const createOrder = (data: CreateOrderPayload) => 
  apiClient.post(`/orders/create/`, data);

export const updateOrder = (order_number: string, data: Partial<Order>) => 
  apiClient.patch(`/orders/${order_number}/`, data);

export const cancelOrder = (order_number: string) => 
  apiClient.post(`/orders/${order_number}/cancel/`, {});

// Re-export types for convenience
export type { Order, CreateOrderPayload }; 