/**
 * Custom hook for Agent API operations
 */

import { useState, useCallback } from 'react';
import { agentApi } from '@/lib/api/agents';

export const useAgentApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleApiCall = useCallback(async <T>(
    apiCall: () => Promise<T>,
    fallbackData?: T
  ): Promise<T | undefined> => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      console.error('API Error:', err);
      
      if (fallbackData) {
        return fallbackData;
      }
      
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    handleApiCall,
    clearError,
    // Tours
    getTours: useCallback(() => 
      handleApiCall(() => agentApi.tours.getTours()), [handleApiCall]
    ),
    getTourDetails: useCallback((tourId: number) => 
      handleApiCall(() => agentApi.tours.getTourDetails(tourId)), [handleApiCall]
    ),
    getAvailableDates: useCallback((tourId: number) => 
      handleApiCall(() => agentApi.tours.getAvailableDates(tourId)), [handleApiCall]
    ),
    getTourOptions: useCallback((tourId: number) => 
      handleApiCall(() => agentApi.tours.getTourOptions(tourId)), [handleApiCall]
    ),
    
    // Customers
    getCustomers: useCallback(() => 
      handleApiCall(() => agentApi.customers.getCustomers()), [handleApiCall]
    ),
    createCustomer: useCallback((customerData: Omit<import('@/lib/api/agents').Customer, 'id' | 'created_at' | 'total_bookings' | 'total_spent'>) => 
      handleApiCall(() => agentApi.customers.createCustomer(customerData)), [handleApiCall]
    ),
    updateCustomer: useCallback((customerId: number, customerData: Partial<import('@/lib/api/agents').Customer>) => 
      handleApiCall(() => agentApi.customers.updateCustomer(customerId, customerData)), [handleApiCall]
    ),
    getCustomerDetails: useCallback((customerId: number) => 
      handleApiCall(() => agentApi.customers.getCustomerDetails(customerId)), [handleApiCall]
    ),
    
    // Pricing
    calculatePricing: useCallback((bookingData: { tour_id: number; variant_id: number; participants: { adults: number; children: number; infants: number }; options: number[] }) => 
      handleApiCall(() => agentApi.pricing.calculatePricing(bookingData)), [handleApiCall]
    ),
    previewPricing: useCallback((bookingData: { tour_id: number; variant_id: number; participants: { adults: number; children: number; infants: number }; options: number[] }) => 
      handleApiCall(() => agentApi.pricing.previewPricing(bookingData)), [handleApiCall]
    ),
    
    // Booking
    createBooking: useCallback((bookingData: import('@/lib/api/agents').BookingRequest) => 
      handleApiCall(() => agentApi.booking.createBooking(bookingData)), [handleApiCall]
    ),
    getBookingDetails: useCallback((bookingId: string) => 
      handleApiCall(() => agentApi.booking.getBookingDetails(bookingId)), [handleApiCall]
    ),
    getAgentBookings: useCallback(() => 
      handleApiCall(() => agentApi.booking.getAgentBookings()), [handleApiCall]
    ),
    
    // Dashboard
    getDashboardStats: useCallback(() => 
      handleApiCall(() => agentApi.dashboard.getDashboardStats()), [handleApiCall]
    ),
    getCommissionHistory: useCallback(() => 
      handleApiCall(() => agentApi.dashboard.getCommissionHistory()), [handleApiCall]
    )
  };
};
