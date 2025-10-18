/**
 * Hook for managing customer data across the application.
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { CustomerDataService, CustomerInfo } from '../services/CustomerDataService';

export const useCustomerData = () => {
  const { user, isAuthenticated } = useAuth();
  const [customerData, setCustomerData] = useState<CustomerInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load customer data from user profile or create default values.
   */
  const loadCustomerData = useCallback(async () => {
    if (!isAuthenticated || !user) {
      setCustomerData(CustomerDataService.getDefaultCustomerData());
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await CustomerDataService.getCustomerData(user);
      setCustomerData(data);
    } catch (err) {
      console.error('Error loading customer data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load customer data');
      // Fallback to default data
      setCustomerData(CustomerDataService.getDefaultCustomerData(user));
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, user]);

  /**
   * Save customer data to user profile.
   */
  const saveCustomerData = useCallback(async (data: CustomerInfo) => {
    if (!isAuthenticated) {
      throw new Error('User must be authenticated to save customer data');
    }

    setIsLoading(true);
    setError(null);

    try {
      // Validate data
      const validation = CustomerDataService.validateCustomerData(data);
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '));
      }

      await CustomerDataService.saveCustomerData(data);
      setCustomerData(data);
    } catch (err) {
      console.error('Error saving customer data:', err);
      setError(err instanceof Error ? err.message : 'Failed to save customer data');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  /**
   * Update customer data locally without saving.
   */
  const updateCustomerData = useCallback((data: Partial<CustomerInfo>) => {
    setCustomerData(prev => prev ? { ...prev, ...data } : null);
  }, []);

  /**
   * Reset customer data to default values.
   */
  const resetCustomerData = useCallback(() => {
    setCustomerData(CustomerDataService.getDefaultCustomerData(user || undefined));
    setError(null);
  }, [user]);

  /**
   * Get guest session information.
   */
  const getGuestSessionInfo = useCallback(() => {
    return CustomerDataService.getGuestSessionInfo();
  }, []);

  /**
   * Log cart merge attempt.
   */
  const logCartMergeAttempt = useCallback((sessionInfo: { sessionKey: string; isGuest: boolean }, success: boolean, errorMessage?: string) => {
    CustomerDataService.logCartMergeAttempt(sessionInfo, user, success, errorMessage);
  }, [user]);

  // Load customer data when user changes
  useEffect(() => {
    loadCustomerData();
  }, [loadCustomerData]);

  return {
    customerData,
    isLoading,
    error,
    loadCustomerData,
    saveCustomerData,
    updateCustomerData,
    resetCustomerData,
    getGuestSessionInfo,
    logCartMergeAttempt,
    isAuthenticated,
    user
  };
};
