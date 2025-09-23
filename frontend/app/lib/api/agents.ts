import { apiClient } from '../../../lib/api/client';
import type { 
  Agent, 
  AgentSummary, 
  AgentCommission, 
  AgentCustomer, 
  AgentPricingRule,
  AgentBookingData,
  AgentTourData,
  AgentTransferData,
  AgentCarRentalData,
  AgentEventData,
  AgentPricingPreviewData,
  AgentCustomerStatistics,
  AgentCommissionSummary,
  AgentMonthlyCommission,
  PaginatedResponse
} from '../types/api';

const BASE = '/agents/';

// Dashboard APIs
export const getAgentDashboard = () => 
  apiClient.get(`${BASE}dashboard/stats/`);

export const getAgentDashboardStats = () => 
  apiClient.get(`${BASE}dashboard/stats/`);

// Bookings APIs
export const getAgentBookings = () => 
  apiClient.get(`${BASE}bookings/`);

// Customer Management APIs
export const getAgentCustomers = (params?: {
  status?: string;
  tier?: string;
  search?: string;
  created_after?: string;
  created_before?: string;
}) => 
  apiClient.get(`${BASE}customers/`, { params });

export const createAgentCustomer = (customerData: {
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  gender?: 'male' | 'female' | 'other';
  preferred_language?: 'fa' | 'en' | 'ar';
  preferred_contact_method?: 'email' | 'phone' | 'whatsapp' | 'sms';
  customer_status?: 'active' | 'inactive' | 'blocked' | 'vip';
  customer_tier?: 'bronze' | 'silver' | 'gold' | 'platinum';
  relationship_notes?: string;
  special_requirements?: string;
  marketing_consent?: boolean;
  // Authentication options
  send_credentials?: boolean;
  verification_method?: 'email' | 'sms' | 'both';
  welcome_message?: string;
  custom_instructions?: string;
}) => 
  apiClient.post(`${BASE}customers/`, customerData);

// Credential management functions
export const sendCustomerCredentials = (customerId: string, options?: {
  method?: 'email' | 'sms' | 'both';
  message?: string;
}) => 
  apiClient.post(`${BASE}customers/${customerId}/credentials/`, options || { method: 'email' });

export const sendCustomerVerification = (customerId: string) => 
  apiClient.post(`${BASE}customers/${customerId}/verification/`);

export const getCustomerAuthStatus = (customerId: string) => 
  apiClient.get(`${BASE}customers/${customerId}/auth-status/`);

export const getAgentCustomerDetail = (customerId: string) => 
  apiClient.get(`${BASE}customers/${customerId}/`);

export const updateAgentCustomer = (customerId: string, customerData: Partial<{
  first_name: string;
  last_name: string;
  phone: string;
  address: string;
  city: string;
  country: string;
  birth_date: string;
  gender: 'male' | 'female' | 'other';
  preferred_language: 'fa' | 'en' | 'ar';
  preferred_contact_method: 'email' | 'phone' | 'whatsapp' | 'sms';
  relationship_notes: string;
  special_requirements: string;
  marketing_consent: boolean;
}>) => 
  apiClient.put(`${BASE}customers/${customerId}/`, customerData);

export const deleteAgentCustomer = (customerId: string) => 
  apiClient.delete(`${BASE}customers/${customerId}/`);

export const getAgentCustomerOrders = (customerId: string, params?: {
  limit?: number;
  offset?: number;
}) => 
  apiClient.get(`${BASE}customers/${customerId}/orders/`, { params });

export const updateAgentCustomerTier = (customerId: string, tier: 'bronze' | 'silver' | 'gold' | 'platinum') => 
  apiClient.post(`${BASE}customers/${customerId}/tier/`, { tier });

export const updateAgentCustomerStatus = (customerId: string, status: 'active' | 'inactive' | 'blocked' | 'vip') => 
  apiClient.post(`${BASE}customers/${customerId}/status/`, { status });

export const searchAgentCustomers = (query: string, limit?: number) => 
  apiClient.get(`${BASE}customers/search/`, { 
    params: { q: query, limit: limit || 20 } 
  });

export const getAgentCustomerStatistics = () => 
  apiClient.get(`${BASE}customers/statistics/`);

// Order Management APIs
export const getAgentOrders = (status?: string) => 
  apiClient.get(`${BASE}orders/`, { params: { status } });

// Booking Services APIs
export const bookAgentTour = (bookingData: AgentTourData) => 
  apiClient.post(`${BASE}book/tour/`, bookingData);

export const bookAgentTransfer = (bookingData: AgentTransferData) => 
  apiClient.post(`${BASE}book/transfer/`, bookingData);

export const bookAgentCarRental = (bookingData: AgentCarRentalData) => 
  apiClient.post(`${BASE}book/car-rental/`, bookingData);

export const bookAgentEvent = (bookingData: AgentEventData) => 
  apiClient.post(`${BASE}book/event/`, bookingData);

// Pricing Management APIs
export const getAgentPricingRules = () => 
  apiClient.get(`${BASE}pricing/rules/`);

export const createAgentPricingRule = (ruleData: {
  product_type: 'tour' | 'event' | 'transfer' | 'car_rental';
  pricing_method: 'discount_percentage' | 'fixed_price' | 'markup_percentage' | 'custom_factor';
  discount_percentage?: number;
  fixed_price?: number;
  markup_percentage?: number;
  custom_factor?: number;
  min_price?: number;
  max_price?: number;
  description?: string;
  is_active?: boolean;
}) => 
  apiClient.post(`${BASE}pricing/rules/`, ruleData);

export const getAgentPricingPreview = async (previewData: AgentPricingPreviewData) => {
  const response = await apiClient.post(`${BASE}pricing/preview/`, previewData);
  return (response as { data: unknown }).data;
};

// Commission Management APIs
export const getAgentCommissions = (params?: {
  limit?: number;
  offset?: number;
  status?: 'pending' | 'approved' | 'paid' | 'rejected' | 'cancelled';
  start_date?: string;
  end_date?: string;
}) => 
  apiClient.get(`${BASE}commissions/`, { params });

export const getAgentCommissionSummary = (params?: {
  start_date?: string;
  end_date?: string;
}) => 
  apiClient.get(`${BASE}commissions/summary/`, { params });

export const getAgentCommissionDetail = (commissionId: string) => 
  apiClient.get(`${BASE}commissions/${commissionId}/`);

export const getAgentMonthlyCommission = (year?: number, month?: number) => 
  apiClient.get(`${BASE}commissions/monthly/`, { 
    params: { 
      year: year || new Date().getFullYear(), 
      month: month || new Date().getMonth() + 1 
    } 
  });

// Tours Management APIs
export const getAgentTours = (params?: {
  category?: string;
  location?: string;
  search?: string;
}) => 
  apiClient.get(`${BASE}tours/`, { params });

export const getAgentTourDetail = (tourId: string) => 
  apiClient.get(`${BASE}tours/${tourId}/`);

export const getAgentTourAvailableDates = (tourId: string) => 
  apiClient.get(`${BASE}tours/${tourId}/available-dates/`);

export const getAgentTourOptions = (tourId: string) => 
  apiClient.get(`${BASE}tours/${tourId}/options/`);

// Re-export types for convenience
export type { 
  Agent, 
  AgentSummary, 
  AgentCommission, 
  AgentCustomer, 
  AgentPricingRule,
  AgentBookingData,
  AgentTourData,
  AgentTransferData,
  AgentCarRentalData,
  AgentEventData,
  AgentPricingPreviewData,
  AgentCustomerStatistics,
  AgentCommissionSummary,
  AgentMonthlyCommission,
  PaginatedResponse
}; 