'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { useUnifiedCurrency } from './UnifiedCurrencyContext';
import { apiClient } from '../api/client';
import { LimitValidationService } from '../services/limitValidation';

// Unified cart item interface that matches backend structure
export interface CartItem {
  id: string;
  product_type: 'tour' | 'event' | 'transfer' | 'car_rental';
  product_id: string;
  product_title?: string;
  product_slug?: string;
  product_image?: string;
  variant_id?: string;
  variant_name?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  options_total: number;
  currency: string;
  booking_date: string;
  booking_time: string;
  selected_options: Array<{
    option_id: string;
    quantity: number;
    price?: number;
  }>;
  booking_data: {
    participants?: {
      adult: number;
      child: number;
      infant: number;
    };
    special_requests?: string;
    schedule_id?: string;
    // Car rental specific fields
    car_rental_id?: string;
    pickup_date?: string;
    dropoff_date?: string;
    pickup_time?: string;
    dropoff_time?: string;
    rental_days?: number;
    driver_name?: string;
    driver_license?: string;
    driver_phone?: string;
    driver_email?: string;
    additional_drivers?: Array<{
      name: string;
      license: string;
      phone: string;
    }>;
    basic_insurance?: boolean;
    comprehensive_insurance?: boolean;
  };
  // Display fields
  title?: string;
  image?: string;
  duration?: string;
  location?: string;
}

export interface CartLimits {
  maxItems: number;
  maxTotal: number;
  userType: 'guest' | 'authenticated';
}

interface CartState {
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
  subtotal: number;
  feesTotal: number;
  taxTotal: number;
  grandTotal: number;
  currency: string;
  isLoading: boolean;
  isClient: boolean;
  error: string | null;
  limits: CartLimits;
}

interface CartActions {
  addItem: (item: Omit<CartItem, 'id' | 'total_price'>) => Promise<{ success: boolean; error?: string }>;
  updateItem: (id: string, updates: Partial<CartItem>) => Promise<{ success: boolean; error?: string }>;
  removeItem: (id: string) => Promise<{ success: boolean; error?: string }>;
  clearCart: () => Promise<{ success: boolean; error?: string }>;
  getItemById: (id: string) => CartItem | undefined;
  isInCart: (productId: string, variantId?: string) => boolean;
  refreshCart: () => Promise<void>;
  validateLimits: (newItemTotal?: number) => { isValid: boolean; errorMessage?: string };
}

type CartContextType = CartState & CartActions;

const CartContext = createContext<CartContextType | undefined>(undefined);

export function UnifiedCartProvider({ children }: { children: ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const { currency: unifiedCurrency } = useUnifiedCurrency();
  const [state, setState] = useState<CartState>({
    items: [],
    totalItems: 0,
    totalPrice: 0,
    subtotal: 0,
    feesTotal: 0,
    taxTotal: 0,
    grandTotal: 0,
    currency: 'USD',
    isLoading: true,
    isClient: false,
    error: null,
    limits: {
      maxItems: isAuthenticated ? 10 : 3,
      maxTotal: isAuthenticated ? 5000 : 500,
      userType: isAuthenticated ? 'authenticated' : 'guest'
    },
  });

  // LocalStorage is not used for cart persistence anymore; backend session handles guest carts

  const updateState = useCallback((updates: Partial<CartState>) => {
    setState(prev => {
      const newState = { ...prev, ...updates };
      
      // Calculate totals (business rule: each cart line counts as 1)
      if (updates.items) {
        newState.totalItems = updates.items.length;
        newState.totalPrice = updates.items.reduce((sum, item) => sum + item.total_price, 0);
        newState.currency = unifiedCurrency || 'USD';
      }
      
      return newState;
    });
  }, []);

  // Update limits when authentication status changes
  useEffect(() => {
    setState(prev => ({
      ...prev,
      limits: {
        maxItems: isAuthenticated ? 10 : 3,
        maxTotal: isAuthenticated ? 5000 : 500,
        userType: isAuthenticated ? 'authenticated' : 'guest'
      }
    }));
  }, [isAuthenticated]);

  const loadCartFromBackend = useCallback(async () => {
    try {
      // First get cart items
      const cartResponse = await apiClient.get('/cart/');
      if ((cartResponse as { status: number }).status === 200) {
        const cartData = (cartResponse as { data: { items?: unknown[]; session_id?: string } }).data || {};
        const backendItems = (cartData.items || []) as Array<{
          id: string;
          product_type: 'tour' | 'event' | 'transfer' | 'car_rental';
          product_id: string;
          product_title: string;
          variant_id?: string;
          variant_name?: string;
          quantity: number;
          unit_price: string;
          total_price: string;
          options_total?: string;
          currency: string;
          booking_date?: string;
          booking_time?: string;
          selected_options?: Array<{ option_id: string; quantity: number }>;
          booking_data?: Record<string, unknown>;
          image?: string;
          duration?: string;
          location?: string;
        }>;
        
        // Convert backend items to frontend format
        const convertedItems: CartItem[] = backendItems.map((item: {
          id: string;
          product_type: 'tour' | 'event' | 'transfer' | 'car_rental';
          product_id: string;
          product_title: string;
          variant_id?: string;
          variant_name?: string;
          quantity: number;
          unit_price: string;
          total_price: string;
          options_total?: string;
          currency: string;
          booking_date?: string;
          booking_time?: string;
          selected_options?: Array<{ option_id: string; quantity: number }>;
          booking_data?: Record<string, unknown>;
          image?: string;
          duration?: string;
          location?: string;
        }) => ({
          id: item.id,
          product_type: item.product_type,
          product_id: item.product_id,
          product_title: item.product_title || '',
          variant_id: item.variant_id,
          variant_name: item.variant_name,
          quantity: item.quantity,
          unit_price: parseFloat(item.unit_price),
          total_price: parseFloat(item.total_price),
          options_total: parseFloat(item.options_total || '0'),
          currency: item.currency,
          booking_date: item.booking_date || new Date().toISOString().split('T')[0],
          booking_time: item.booking_time || new Date().toISOString().split('T')[1].split('.')[0],
          selected_options: item.selected_options || [],
          booking_data: item.booking_data || {},
          // Display fields
          title: item.product_title || item.variant_name || '',
          image: item.image,
          duration: item.duration,
          location: item.location,
        }));

        // Then get cart summary for totals
        const summaryResponse = await apiClient.get('/cart/summary/');
        let summaryData = {
          subtotal: 0,
          fees_total: 0,
          tax_total: 0,
          grand_total: 0,
          currency: 'USD'
        };
        
        if ((summaryResponse as { status: number }).status === 200) {
          const responseData = (summaryResponse as { data: { subtotal?: number; fees_total?: number; tax_total?: number; grand_total?: number; currency?: string } }).data;
          summaryData = {
            subtotal: responseData?.subtotal ?? summaryData.subtotal,
            fees_total: responseData?.fees_total ?? summaryData.fees_total,
            tax_total: responseData?.tax_total ?? summaryData.tax_total,
            grand_total: responseData?.grand_total ?? summaryData.grand_total,
            currency: responseData?.currency || summaryData.currency
          };
        }

        // Persist guest session id for later merge after login
        try {
          if (typeof window !== 'undefined' && cartData.session_id) {
            localStorage.setItem('guest_session_id', cartData.session_id);
            console.log('💾 Saved guest session ID:', cartData.session_id);
          }
        } catch (error) {
          console.error('Error saving guest session ID:', error);
        }
        
        updateState({ 
          items: convertedItems, 
          subtotal: summaryData.subtotal ?? 0,
          feesTotal: summaryData.fees_total ?? 0,
          taxTotal: summaryData.tax_total ?? 0,
          grandTotal: summaryData.grand_total ?? 0,
          currency: summaryData.currency || 'USD',
          isLoading: false 
        });
        
      } else {
        updateState({ 
          items: [], 
          subtotal: 0,
          feesTotal: 0,
          taxTotal: 0,
          grandTotal: 0,
          isLoading: false 
        });
      }
    } catch (error) {
      console.error('Error loading cart from backend:', error);
      updateState({ 
        items: [], 
        subtotal: 0,
        feesTotal: 0,
        taxTotal: 0,
        grandTotal: 0,
        isLoading: false 
      });
    }
  }, [updateState]);

  // Initialize client-side state
  useEffect(() => {
    setState(prev => ({ ...prev, isClient: true }));
  }, []);

  // Load cart when authentication state changes
  useEffect(() => {
    if (state.isClient) {
      loadCartFromBackend();
    }
  }, [state.isClient, isAuthenticated, user, loadCartFromBackend]);

  const addItem = useCallback(async (newItem: Omit<CartItem, 'id' | 'total_price'>): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await apiClient.post('/cart/add/', newItem);
      if ((response as { status: number }).status === 201 || (response as { status: number }).status === 200) {
        const responseData = (response as { data: { cart_item: unknown; session_id?: string } }).data;
        const backendItem = responseData.cart_item as {
          id: string;
          product_type: 'tour' | 'event' | 'transfer' | 'car_rental';
          product_id: string;
          product_title: string;
          variant_id?: string;
          variant_name?: string;
          quantity: number;
          unit_price: string;
          total_price: string;
          options_total?: string;
          currency: string;
          booking_date?: string;
          booking_time?: string;
          selected_options?: Array<{ option_id: string; quantity: number }>;
          booking_data?: Record<string, unknown>;
        };
        
        // Convert backend item to frontend format
        const convertedItem: CartItem = {
          id: backendItem.id,
          product_type: backendItem.product_type,
          product_id: backendItem.product_id,
          product_title: backendItem.product_title || '',
          variant_id: backendItem.variant_id,
          variant_name: backendItem.variant_name,
          quantity: backendItem.quantity,
          unit_price: parseFloat(backendItem.unit_price),
          total_price: parseFloat(backendItem.total_price),
          options_total: parseFloat(backendItem.options_total || '0'),
          currency: backendItem.currency,
          booking_date: backendItem.booking_date || new Date().toISOString().split('T')[0],
          booking_time: backendItem.booking_time || new Date().toISOString().split('T')[1].split('.')[0],
          selected_options: backendItem.selected_options || [],
          booking_data: backendItem.booking_data || {},
          title: backendItem.product_title || backendItem.variant_name || '',
        };

        // Update local state
        const existingIndex = state.items.findIndex(item => item.id === convertedItem.id);
        let updatedItems;
        
        if (existingIndex >= 0) {
          updatedItems = [...state.items];
          updatedItems[existingIndex] = convertedItem;
        } else {
          updatedItems = [...state.items, convertedItem];
        }
        
        updateState({ items: updatedItems });
        
        // Refresh cart summary to get updated totals
        await loadCartFromBackend();

        // Update guest session ID if provided
        if (responseData.session_id && !isAuthenticated) {
          try {
            localStorage.setItem('guest_session_id', responseData.session_id);
            console.log('💾 Updated guest session ID after add:', responseData.session_id);
          } catch (error) {
            console.error('Error updating guest session ID:', error);
          }
        }

        return { success: true };
      } else {
        return { success: false, error: 'Failed to add item' };
      }
    } catch (error) {
      console.error('Error adding item to cart:', error);
      return { success: false, error: 'Failed to add item to cart' };
    }
  }, [state.items, updateState, isAuthenticated, loadCartFromBackend]);

  // Call this right after successful login/register to merge guest cart
  const mergeGuestCartIntoUser = useCallback(async (): Promise<void> => {
    try {
      let sessionKey: string | null = null;
      try { sessionKey = typeof window !== 'undefined' ? localStorage.getItem('guest_session_id') : null; } catch {}
      
      if (sessionKey) {
        console.log('🔄 Attempting to merge guest cart with session:', sessionKey);
        const response = await apiClient.post('/cart/merge/', { session_key: sessionKey });
        
        console.log('📦 Merge response:', (response as { data: unknown; status: number }).data);
        
        // Only remove session key if merge was successful
        if ((response as { data: unknown; status: number }).status === 200) {
          try { 
            if (sessionKey) localStorage.removeItem('guest_session_id'); 
          } catch {}
          console.log('✅ Guest cart merged successfully');
        }
        
        // Refresh cart after merge attempt
        await loadCartFromBackend();
      } else {
        console.log('ℹ️ No guest session key found to merge');
      }
    } catch (e) {
      console.error('❌ Error merging carts:', e);
      // Still refresh cart in case of error
      try {
        await loadCartFromBackend();
      } catch (refreshError) {
        console.error('❌ Error refreshing cart after merge failure:', refreshError);
      }
    }
  }, [loadCartFromBackend]);

  const updateItem = useCallback(async (id: string, updates: Partial<CartItem>): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await apiClient.patch(`/cart/items/${id}/`, updates);
      if ((response as { status: number }).status === 200) {
        const backendItem = (response as { data: { cart_item: unknown } }).data.cart_item as Partial<CartItem>;
        
        // Update local state
        const updatedItems = state.items.map(item =>
          item.id === id ? { ...item, ...backendItem } : item
        );

        updateState({ items: updatedItems });
        return { success: true };
      } else {
        return { success: false, error: 'Failed to update item' };
      }
    } catch (error) {
      console.error('Error updating cart item:', error);
      return { success: false, error: 'Failed to update item' };
    }
  }, [state.items, updateState]);

  const removeItem = useCallback(async (id: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await apiClient.delete(`/cart/items/${id}/remove/`);
      if ((response as { status: number }).status === 200 || (response as { status: number }).status === 204) {
        const updatedItems = state.items.filter(item => item.id !== id);
        updateState({ items: updatedItems });
        return { success: true };
      } else {
        return { success: false, error: 'Failed to remove item' };
      }
    } catch (error) {
      console.error('Error removing cart item:', error);
      return { success: false, error: 'Failed to remove item' };
    }
  }, [state.items, updateState]);

  const clearCart = useCallback(async (): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await apiClient.delete('/cart/clear/');
      if ((response as { status: number }).status === 200) {
        updateState({ items: [] });
        return { success: true };
      } else {
        return { success: false, error: 'Failed to clear cart' };
      }
    } catch (error) {
      console.error('Error clearing cart:', error);
      return { success: false, error: 'Failed to clear cart' };
    }
  }, [updateState]);

  const getItemById = useCallback((id: string): CartItem | undefined => {
    return state.items.find(item => item.id === id);
  }, [state.items]);

  const isInCart = useCallback((productId: string, variantId?: string): boolean => {
    return state.items.some(item => 
      item.product_id === productId && 
      (variantId ? item.variant_id === variantId : true)
    );
  }, [state.items]);

  const refreshCart = useCallback(async (): Promise<void> => {
    await loadCartFromBackend();
  }, [loadCartFromBackend]);

  const validateLimits = useCallback((newItemTotal: number = 0): { isValid: boolean; errorMessage?: string } => {
    return LimitValidationService.validateCartLimits(
      isAuthenticated,
      state.totalItems,
      state.totalPrice,
      newItemTotal
    );
  }, [isAuthenticated, state.totalItems, state.totalPrice]);

  // Listen for auth merge event - placed after all functions are defined
  useEffect(() => {
    const handleAuthMerge = () => {
      console.log('Auth merge event received, calling mergeGuestCartIntoUser');
      mergeGuestCartIntoUser();
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('auth:mergeGuestCart', handleAuthMerge);
      return () => window.removeEventListener('auth:mergeGuestCart', handleAuthMerge);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const value: CartContextType = {
    ...state,
    addItem,
    updateItem,
    removeItem,
    clearCart,
    getItemById,
    isInCart,
    refreshCart,
    validateLimits,
    // @ts-expect-error expose merge for auth flow components
    mergeGuestCartIntoUser,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

export function useUnifiedCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useUnifiedCart must be used within a UnifiedCartProvider');
  }
  return context;
} 