import { apiClient } from '../../../lib/api/client';
import type { Payment, CreatePaymentPayload } from '../types/api';

const BASE = '/payments/';

export const getPayments = () => 
  apiClient.get(BASE);

export const getPaymentDetail = (payment_id: string) => 
  apiClient.get(`${BASE}${payment_id}/`);

export const createPayment = (data: CreatePaymentPayload) => 
  apiClient.post(`${BASE}create/`, data);

// Re-export types for convenience
export type { Payment, CreatePaymentPayload }; 