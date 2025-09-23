'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';

interface UnifiedCurrencyContextType {
  currency: string;
  setCurrency: (currency: string) => void;
  isAgent: boolean;
  agentCurrency?: string;
  isLoading: boolean;
}

const UnifiedCurrencyContext = createContext<UnifiedCurrencyContextType | undefined>(undefined);

export const useUnifiedCurrency = () => {
  const context = useContext(UnifiedCurrencyContext);
  if (context === undefined) {
    throw new Error('useUnifiedCurrency must be used within a UnifiedCurrencyProvider');
  }
  return context;
};

interface UnifiedCurrencyProviderProps {
  children: React.ReactNode;
}

export const UnifiedCurrencyProvider: React.FC<UnifiedCurrencyProviderProps> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [currency, setCurrencyState] = useState<string>('USD');
  const [isLoading, setIsLoading] = useState(true);

  // Determine if user is an agent
  const isAgent = isAuthenticated && user?.role === 'agent';
  const agentCurrency = isAgent ? user?.preferred_currency : undefined;

  // Load initial currency
  useEffect(() => {
    const loadInitialCurrency = () => {
      try {
        if (isAgent && agentCurrency) {
          // For agents, use their preferred currency from database
          setCurrencyState(agentCurrency);
          console.log('Using agent preferred currency:', agentCurrency);
        } else {
          // For regular users, use localStorage or default
          const storedCurrency = localStorage.getItem('currency');
          if (storedCurrency && ['USD', 'EUR', 'TRY', 'IRR'].includes(storedCurrency)) {
            setCurrencyState(storedCurrency);
            console.log('Using stored currency:', storedCurrency);
          } else {
            setCurrencyState('USD');
            console.log('Using default currency: USD');
          }
        }
      } catch (error) {
        console.error('Error loading initial currency:', error);
        setCurrencyState('USD');
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialCurrency();
  }, [isAgent, agentCurrency]);

  // Set currency function
  const setCurrency = useCallback((newCurrency: string) => {
    if (!['USD', 'EUR', 'TRY', 'IRR'].includes(newCurrency)) {
      console.warn('Invalid currency:', newCurrency);
      return;
    }

    setCurrencyState(newCurrency);
    
    // Store in localStorage for non-agents
    if (!isAgent) {
      localStorage.setItem('currency', newCurrency);
      console.log('Stored currency in localStorage:', newCurrency);
    }
    
    console.log('Currency changed to:', newCurrency);
  }, [isAgent]);

  // Update currency when agent's preferred currency changes
  useEffect(() => {
    if (isAgent && agentCurrency && agentCurrency !== currency) {
      setCurrencyState(agentCurrency);
      console.log('Updated currency from agent settings:', agentCurrency);
    }
  }, [isAgent, agentCurrency, currency]);

  const value: UnifiedCurrencyContextType = {
    currency,
    setCurrency,
    isAgent,
    agentCurrency,
    isLoading,
  };

  return (
    <UnifiedCurrencyContext.Provider value={value}>
      {children}
    </UnifiedCurrencyContext.Provider>
  );
};
