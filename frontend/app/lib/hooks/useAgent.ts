/**
 * Agent Hook
 * Custom hook for managing agent-related state and operations
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  Agent, 
  AgentSummary, 
  AgentCustomer, 
  AgentCommission,
  AgentTour,
  AgentTourData,
  AgentTransferData,
  AgentCarRentalData,
  AgentEventData,
  AgentPricingPreviewData,
  AgentCustomerStatistics,
  AgentCommissionSummary,
  AgentMonthlyCommission
} from '../types/api';
import {
  getAgentDashboard,
  getAgentDashboardStats,
  getAgentCustomers,
  createAgentCustomer,
  getAgentCustomerDetail,
  updateAgentCustomer,
  deleteAgentCustomer,
  getAgentCustomerOrders,
  updateAgentCustomerTier,
  updateAgentCustomerStatus,
  searchAgentCustomers,
  getAgentCustomerStatistics,
  getAgentOrders,
  getAgentCommissions,
  getAgentCommissionSummary,
  getAgentCommissionDetail,
  getAgentMonthlyCommission,
  getAgentTours,
  getAgentTourDetail,
  getAgentTourAvailableDates,
  getAgentTourOptions,
  bookAgentTour,
  bookAgentTransfer,
  bookAgentCarRental,
  bookAgentEvent,
  getAgentPricingRules,
  createAgentPricingRule,
  getAgentPricingPreview
} from '../api/agents';
import { parseApiError } from '../api/agent-utils';

interface UseAgentState {
  // Agent info
  agent: Agent | null;
  agentSummary: AgentSummary | null;
  dashboardStats: Record<string, unknown> | null;
  
  // Customers
  customers: AgentCustomer[];
  customersLoading: boolean;
  customersError: string | null;
  customerStatistics: AgentCustomerStatistics | null;
  
  // Commissions
  commissions: AgentCommission[];
  commissionsLoading: boolean;
  commissionsError: string | null;
  commissionSummary: AgentCommissionSummary | null;
  monthlyCommission: AgentMonthlyCommission | null;
  
  // Tours
  tours: AgentTour[];
  toursLoading: boolean;
  toursError: string | null;
  
  // Orders
  orders: Record<string, unknown>[];
  ordersLoading: boolean;
  ordersError: string | null;
  
  // General loading and error states
  loading: boolean;
  error: string | null;
}

interface UseAgentActions {
  // Dashboard
  loadDashboard: () => Promise<void>;
  loadDashboardStats: () => Promise<void>;
  
  // Customers
  loadCustomers: (params?: Record<string, unknown>) => Promise<void>;
  createCustomer: (customerData: Record<string, unknown>) => Promise<AgentCustomer>;
  updateCustomer: (customerId: string, customerData: Record<string, unknown>) => Promise<AgentCustomer>;
  deleteCustomer: (customerId: string) => Promise<void>;
  loadCustomerDetail: (customerId: string) => Promise<AgentCustomer>;
  loadCustomerOrders: (customerId: string, params?: Record<string, unknown>) => Promise<Record<string, unknown>[]>;
  updateCustomerTier: (customerId: string, tier: string) => Promise<void>;
  updateCustomerStatus: (customerId: string, status: string) => Promise<void>;
  searchCustomers: (query: string, limit?: number) => Promise<AgentCustomer[]>;
  loadCustomerStatistics: () => Promise<void>;
  
  // Commissions
  loadCommissions: (params?: Record<string, unknown>) => Promise<void>;
  loadCommissionSummary: (params?: Record<string, unknown>) => Promise<void>;
  loadCommissionDetail: (commissionId: string) => Promise<AgentCommission>;
  loadMonthlyCommission: (year?: number, month?: number) => Promise<void>;
  
  // Tours
  loadTours: (params?: Record<string, unknown>) => Promise<void>;
  loadTourDetail: (tourId: string) => Promise<AgentTour>;
  loadTourAvailableDates: (tourId: string) => Promise<Record<string, unknown>[]>;
  loadTourOptions: (tourId: string) => Promise<Record<string, unknown>[]>;
  
  // Orders
  loadOrders: (status?: string) => Promise<void>;
  
  // Booking
  bookTour: (bookingData: Record<string, unknown>) => Promise<Record<string, unknown>>;
  bookTransfer: (bookingData: Record<string, unknown>) => Promise<Record<string, unknown>>;
  bookCarRental: (bookingData: Record<string, unknown>) => Promise<Record<string, unknown>>;
  bookEvent: (bookingData: Record<string, unknown>) => Promise<Record<string, unknown>>;
  
  // Pricing
  loadPricingRules: () => Promise<Record<string, unknown>[]>;
  createPricingRule: (ruleData: Record<string, unknown>) => Promise<Record<string, unknown>>;
  getPricingPreview: (previewData: Record<string, unknown>) => Promise<Record<string, unknown>>;
  
  // Profile
  updateAgentProfile: (profileData?: Record<string, unknown>) => Promise<void>;
  
  // Utility
  clearError: () => void;
  refresh: () => Promise<void>;
}

export const useAgent = (): UseAgentState & UseAgentActions => {
  const [state, setState] = useState<UseAgentState>({
    agent: null,
    agentSummary: null,
    dashboardStats: null,
    customers: [],
    customersLoading: false,
    customersError: null,
    customerStatistics: null,
    commissions: [],
    commissionsLoading: false,
    commissionsError: null,
    commissionSummary: null,
    monthlyCommission: null,
    tours: [],
    toursLoading: false,
    toursError: null,
    orders: [],
    ordersLoading: false,
    ordersError: null,
    loading: false,
    error: null,
  });

  const clearError = useCallback(() => {
    setState(prev => ({
      ...prev,
      error: null,
      customersError: null,
      commissionsError: null,
      toursError: null,
      ordersError: null,
    }));
  }, []);

  const handleError = useCallback((error: unknown, type?: string) => {
    const apiError = parseApiError(error);
    const errorMessage = apiError.message;
    
    setState(prev => ({
      ...prev,
      loading: false,
      customersLoading: false,
      commissionsLoading: false,
      toursLoading: false,
      ordersLoading: false,
      error: errorMessage,
      ...(type && { [`${type}Error`]: errorMessage }),
    }));
  }, []);

  // Dashboard actions
  const loadDashboard = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const response = await getAgentDashboard();
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { agent: Agent; summary: AgentSummary } }).data;
        setState(prev => ({
          ...prev,
          loading: false,
          agent: responseData.agent,
          agentSummary: responseData.summary,
        }));
      }
    } catch (error) {
      handleError(error);
    }
  }, [handleError]);

  const loadDashboardStats = useCallback(async () => {
    try {
      const response = await getAgentDashboardStats();
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: Record<string, unknown> }).data;
        setState(prev => ({
          ...prev,
          dashboardStats: responseData,
        }));
      }
    } catch (error) {
      handleError(error);
    }
  }, [handleError]);

  // Customer actions
  const loadCustomers = useCallback(async (params?: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, customersLoading: true, customersError: null }));
      const response = await getAgentCustomers(params);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { customers: AgentCustomer[] } }).data;
        setState(prev => ({
          ...prev,
          customersLoading: false,
          customers: responseData.customers,
        }));
      }
    } catch (error) {
      handleError(error, 'customers');
    }
  }, [handleError]);

  const createCustomer = useCallback(async (customerData: Record<string, unknown>): Promise<AgentCustomer> => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const response = await createAgentCustomer(customerData as {
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
      });
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { customer: AgentCustomer } }).data;
        setState(prev => ({
          ...prev,
          loading: false,
          customers: [responseData.customer, ...prev.customers],
        }));
        return responseData.customer;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const updateCustomer = useCallback(async (customerId: string, customerData: Record<string, unknown>): Promise<AgentCustomer> => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const response = await updateAgentCustomer(customerId, customerData);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { customer: AgentCustomer } }).data;
        setState(prev => ({
          ...prev,
          loading: false,
          customers: prev.customers.map(customer => 
            customer.id === customerId ? responseData.customer : customer
          ),
        }));
        return responseData.customer;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const deleteCustomer = useCallback(async (customerId: string) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      await deleteAgentCustomer(customerId);
      setState(prev => ({
        ...prev,
        loading: false,
        customers: prev.customers.filter(customer => customer.id !== customerId),
      }));
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const loadCustomerDetail = useCallback(async (customerId: string): Promise<AgentCustomer> => {
    try {
      const response = await getAgentCustomerDetail(customerId);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { customer: AgentCustomer } }).data;
        return responseData.customer;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const loadCustomerOrders = useCallback(async (customerId: string, params?: Record<string, unknown>): Promise<Record<string, unknown>[]> => {
    try {
      const response = await getAgentCustomerOrders(customerId, params);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { orders: Record<string, unknown>[] } }).data;
        return responseData.orders;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const updateCustomerTier = useCallback(async (customerId: string, tier: string) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      await updateAgentCustomerTier(customerId, tier as 'bronze' | 'silver' | 'gold' | 'platinum');
      setState(prev => ({
        ...prev,
        loading: false,
        customers: prev.customers.map(customer => 
          customer.id === customerId ? { ...customer, tier: tier as 'bronze' | 'silver' | 'gold' | 'platinum' } : customer
        ),
      }));
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const updateCustomerStatus = useCallback(async (customerId: string, status: string) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      await updateAgentCustomerStatus(customerId, status as 'active' | 'inactive' | 'blocked' | 'vip');
      setState(prev => ({
        ...prev,
        loading: false,
        customers: prev.customers.map(customer => 
          customer.id === customerId ? { ...customer, status: status as 'active' | 'inactive' | 'blocked' | 'vip' } : customer
        ),
      }));
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const searchCustomers = useCallback(async (query: string, limit?: number): Promise<AgentCustomer[]> => {
    try {
      const response = await searchAgentCustomers(query, limit);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { customers: AgentCustomer[] } }).data;
        return responseData.customers;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const loadCustomerStatistics = useCallback(async () => {
    try {
      const response = await getAgentCustomerStatistics();
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: AgentCustomerStatistics }).data;
        setState(prev => ({
          ...prev,
          customerStatistics: responseData,
        }));
      }
    } catch (error) {
      handleError(error);
    }
  }, [handleError]);

  // Commission actions
  const loadCommissions = useCallback(async (params?: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, commissionsLoading: true, commissionsError: null }));
      const response = await getAgentCommissions(params);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { commissions: AgentCommission[] } }).data;
        setState(prev => ({
          ...prev,
          commissionsLoading: false,
          commissions: responseData.commissions,
        }));
      } else if (response && typeof response === 'object' && 'commissions' in response) {
        // Handle direct response format
        const responseData = (response as { commissions: AgentCommission[] });
        setState(prev => ({
          ...prev,
          commissionsLoading: false,
          commissions: responseData.commissions,
        }));
      }
    } catch (error) {
      handleError(error, 'commissions');
    }
  }, [handleError]);

  const loadCommissionSummary = useCallback(async (params?: Record<string, unknown>) => {
    try {
      const response = await getAgentCommissionSummary(params);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: AgentCommissionSummary }).data;
        setState(prev => ({
          ...prev,
          commissionSummary: responseData,
        }));
      }
    } catch (error) {
      handleError(error);
    }
  }, [handleError]);

  const loadCommissionDetail = useCallback(async (commissionId: string): Promise<AgentCommission> => {
    try {
      const response = await getAgentCommissionDetail(commissionId);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: AgentCommission }).data;
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const loadMonthlyCommission = useCallback(async (year?: number, month?: number) => {
    try {
      const response = await getAgentMonthlyCommission(year, month);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: AgentMonthlyCommission }).data;
        setState(prev => ({
          ...prev,
          monthlyCommission: responseData,
        }));
      }
    } catch (error) {
      handleError(error);
    }
  }, [handleError]);

  // Tour actions
  const loadTours = useCallback(async (params?: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, toursLoading: true, toursError: null }));
      const response = await getAgentTours(params);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: AgentTour[] }).data;
        setState(prev => ({
          ...prev,
          toursLoading: false,
          tours: responseData,
        }));
      }
    } catch (error) {
      handleError(error, 'tours');
    }
  }, [handleError]);

  const loadTourDetail = useCallback(async (tourId: string): Promise<AgentTour> => {
    try {
      const response = await getAgentTourDetail(tourId);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: AgentTour }).data;
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const loadTourAvailableDates = useCallback(async (tourId: string): Promise<Record<string, unknown>[]> => {
    try {
      const response = await getAgentTourAvailableDates(tourId);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: Record<string, unknown>[] }).data;
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const loadTourOptions = useCallback(async (tourId: string): Promise<Record<string, unknown>[]> => {
    try {
      const response = await getAgentTourOptions(tourId);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: Record<string, unknown>[] }).data;
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  // Order actions
  const loadOrders = useCallback(async (status?: string) => {
    try {
      setState(prev => ({ ...prev, ordersLoading: true, ordersError: null }));
      const response = await getAgentOrders(status);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { orders: Record<string, unknown>[] } }).data;
        setState(prev => ({
          ...prev,
          ordersLoading: false,
          orders: responseData.orders,
        }));
      } else if (response && typeof response === 'object' && 'orders' in response) {
        // Handle direct response format
        const responseData = (response as { orders: Record<string, unknown>[] });
        setState(prev => ({
          ...prev,
          ordersLoading: false,
          orders: responseData.orders,
        }));
      }
    } catch (error) {
      handleError(error, 'orders');
    }
  }, [handleError]);

  // Booking actions
  const bookTour = useCallback(async (bookingData: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const response = await bookAgentTour(bookingData as unknown as AgentTourData);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: Record<string, unknown> }).data;
        setState(prev => ({ ...prev, loading: false }));
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const bookTransfer = useCallback(async (bookingData: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const response = await bookAgentTransfer(bookingData as unknown as AgentTransferData);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: Record<string, unknown> }).data;
        setState(prev => ({ ...prev, loading: false }));
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const bookCarRental = useCallback(async (bookingData: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const response = await bookAgentCarRental(bookingData as unknown as AgentCarRentalData);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: Record<string, unknown> }).data;
        setState(prev => ({ ...prev, loading: false }));
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const bookEvent = useCallback(async (bookingData: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const response = await bookAgentEvent(bookingData as unknown as AgentEventData);
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: Record<string, unknown> }).data;
        setState(prev => ({ ...prev, loading: false }));
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  // Pricing actions
  const loadPricingRules = useCallback(async (): Promise<Record<string, unknown>[]> => {
    try {
      const response = await getAgentPricingRules();
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: { rules: Record<string, unknown>[] } }).data;
        return responseData.rules;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const createPricingRule = useCallback(async (ruleData: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const response = await createAgentPricingRule(ruleData as {
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
      });
      if (response && typeof response === 'object' && 'data' in response) {
        const responseData = (response as { data: Record<string, unknown> }).data;
        setState(prev => ({ ...prev, loading: false }));
        return responseData;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  const getPricingPreview = useCallback(async (previewData: Record<string, unknown>): Promise<Record<string, unknown>> => {
    try {
      const response = await getAgentPricingPreview(previewData as unknown as AgentPricingPreviewData);
      if (response && typeof response === 'object') {
        // Backend returns { success: true, pricing: {...} }
        if ('pricing' in response) {
          return response.pricing as Record<string, unknown>;
        }
        // Fallback: return the entire response
        return response as Record<string, unknown>;
      }
      throw new Error('Invalid response format');
    } catch (error) {
      handleError(error);
      throw error;
    }
  }, [handleError]);

  // Profile actions
  const updateAgentProfile = useCallback(async (profileData?: Record<string, unknown>) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      console.log('Updating agent profile with data:', profileData);
      
      // Make API call to update agent profile
      const response = await fetch('/api/v1/agents/profile/update/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });
      
      console.log('Profile update response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Profile update response data:', data);
        
        if (data.success && data.agent) {
          setState(prev => ({ 
            ...prev, 
            agent: data.agent, 
            loading: false 
          }));
          
          console.log('Agent profile updated successfully:', data.agent);
          
          // Reload dashboard to ensure all data is fresh
          await loadDashboard();
        } else {
          throw new Error(data.message || 'Failed to update profile');
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Profile update failed:', errorData);
        throw new Error(errorData.error || `HTTP ${response.status}: Failed to update profile`);
      }
    } catch (error) {
      console.error('Error updating agent profile:', error);
      handleError(error);
      throw error;
    }
  }, [handleError, loadDashboard]);

  // Utility actions
  const refresh = useCallback(async () => {
    await Promise.all([
      loadDashboard(),
      loadDashboardStats(),
      loadCustomers(),
      loadCommissions(),
      loadTours(),
      loadOrders(),
    ]);
  }, [loadDashboard, loadDashboardStats, loadCustomers, loadCommissions, loadTours, loadOrders]);

  // Load initial data
  useEffect(() => {
    loadDashboard();
    loadDashboardStats();
  }, [loadDashboard, loadDashboardStats]);

  return {
    ...state,
    loadDashboard,
    loadDashboardStats,
    loadCustomers,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    loadCustomerDetail,
    loadCustomerOrders,
    updateCustomerTier,
    updateCustomerStatus,
    searchCustomers,
    loadCustomerStatistics,
    loadCommissions,
    loadCommissionSummary,
    loadCommissionDetail,
    loadMonthlyCommission,
    loadTours,
    loadTourDetail,
    loadTourAvailableDates,
    loadTourOptions,
    loadOrders,
    bookTour,
    bookTransfer,
    bookCarRental,
    bookEvent,
    loadPricingRules,
    createPricingRule,
    getPricingPreview,
    updateAgentProfile,
    clearError,
    refresh,
  };
};
