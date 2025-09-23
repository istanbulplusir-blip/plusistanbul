'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useAuth } from './AuthContext';
import { apiClient } from '../api/client';
import { CartItem, TourCartItem, EventCartItem, TransferCartItem } from '../hooks/useCart';

interface CartContextType {
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
  currency: string;
  isLoading: boolean;
  isClient: boolean;
  addItem: (item: CartItem) => Promise<{ success: boolean; error?: string }>;
  updateItem: (id: string, updates: Partial<CartItem>) => Promise<{ success: boolean; error?: string }>;
  removeItem: (id: string) => Promise<{ success: boolean; error?: string }>;
  clearCart: () => Promise<{ success: boolean; error?: string }>;
  getItemById: (id: string) => CartItem | undefined;
  isInCart: (id: string) => boolean;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const [items, setItems] = useState<CartItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isClient, setIsClient] = useState(false);

  // Calculate derived values
  const totalItems = items.reduce((total, item) => {
    if (item.type === 'tour') {
      return total + (item as TourCartItem).total_participants;
    } else {
      return total + (item as EventCartItem | TransferCartItem).quantity;
    }
  }, 0);

  const totalPrice = items.reduce((total, item) => {
    if (item.type === 'tour') {
      return total + (item as TourCartItem).subtotal;
    } else if (item.type === 'transfer' && (item as TransferCartItem).pricing_breakdown) {
      return total + (item as TransferCartItem).pricing_breakdown!.final_price;
    } else {
      return total + (item.price * (item as EventCartItem | TransferCartItem).quantity);
    }
  }, 0);

  const currency = items.length > 0 ? items[0].currency : 'USD';

  const loadCartFromLocalStorage = useCallback(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        const parsedCart = JSON.parse(savedCart);
        setItems(parsedCart.items || []);
      } catch (error) {
        console.error('Error parsing cart data:', error);
        setItems([]);
      }
    } else {
      setItems([]);
    }
    setIsLoading(false);
  }, []);

  const loadCartFromBackend = useCallback(async () => {
    try {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      if (!token) {
        console.warn('No access token found, loading from localStorage');
        loadCartFromLocalStorage();
        return;
      }

      const response = await apiClient.get('/cart/');

      if ((response as { status: number }).status === 200) {
        const cartData = (response as { data: { items?: unknown[] } }).data;
        const backendItems = (cartData.items || []) as Array<{
          id: string;
          product_type: 'tour' | 'event' | 'transfer';
          product_id: string;
          product_title: string;
          product_image?: string;
          product_slug?: string;
          unit_price: string;
          currency: string;
          quantity: number;
          total_price: string;
          options_total?: string;
          variant_id?: string;
          variant_name?: string;
          route_data?: {
            peak_hour_surcharge?: string;
            midnight_surcharge?: string;
            round_trip_discount_enabled?: boolean;
            round_trip_discount_percentage?: string;
          };
          origin?: string;
          destination?: string;
          booking_data?: Record<string, unknown>;
          selected_options?: Array<{ option_id: string; quantity: number }>;
          pricing_breakdown?: unknown;
        }>;
        
        // Convert backend items to frontend format
        const convertedItems = backendItems.map((item: {
          id: string;
          product_type: 'tour' | 'event' | 'transfer';
          product_id: string;
          product_title: string;
          product_image?: string;
          product_slug?: string;
          unit_price: string;
          currency: string;
          quantity: number;
          total_price: string;
          options_total?: string;
          variant_id?: string;
          variant_name?: string;
          route_data?: {
            peak_hour_surcharge?: string;
            midnight_surcharge?: string;
            round_trip_discount_enabled?: boolean;
            round_trip_discount_percentage?: string;
          };
          origin?: string;
          destination?: string;
          booking_data?: Record<string, unknown>;
          selected_options?: Array<{ option_id: string; quantity: number }>;
          pricing_breakdown?: unknown;
        }) => {
          if (item.product_type === 'transfer') {
            // Debug: Log the actual backend data
            console.log('Backend transfer item:', item);
            console.log('Backend origin:', item.origin);
            console.log('Backend destination:', item.destination);
            console.log('Backend pricing_breakdown:', item.pricing_breakdown);
            
            return {
              id: item.id,
              type: 'transfer' as const,
              title: item.product_title,
              price: parseFloat(item.unit_price),
              currency: item.currency,
              quantity: item.quantity,
              slug: item.product_slug || '',
              
              // Transfer-specific fields - use backend serializer data
              route_id: (item.booking_data?.route_id || item.product_id || '') as string,
              route_data: {
                id: (item.product_id || '') as string,
                name: (item.product_title || '') as string,
                name_display: (item.product_title || '') as string,
                origin: (item.origin || '') as string,
                destination: (item.destination || '') as string,
                distance_km: 0, // Default value since not available in backend data
                estimated_duration_minutes: 0, // Default value since not available in backend data
                vehicle_type: (item.booking_data?.vehicle_type || '') as string,
                peak_hour_surcharge: (item.route_data?.peak_hour_surcharge || '0') as string,
                midnight_surcharge: (item.route_data?.midnight_surcharge || '0') as string,
                round_trip_discount_enabled: (item.route_data?.round_trip_discount_enabled || false) as boolean,
                round_trip_discount_percentage: (item.route_data?.round_trip_discount_percentage || '0') as string
              },
              origin: (item.origin || '') as string,
              destination: (item.destination || '') as string,
              trip_type: (item.booking_data?.trip_type || 'one_way') as 'one_way' | 'round_trip',
              passenger_count: (item.booking_data?.passenger_count || 0) as number,
              luggage_count: (item.booking_data?.luggage_count || 0) as number,
              vehicle_type: (item.booking_data?.vehicle_type || '') as string,
              outbound_date: item.booking_data?.outbound_date || '',
              outbound_time: item.booking_data?.outbound_time || '',
              outbound_datetime: item.booking_data?.outbound_date && item.booking_data?.outbound_time 
                ? `${item.booking_data.outbound_date}T${item.booking_data.outbound_time}` 
                : new Date().toISOString(),
              return_date: item.booking_data?.return_date || '',
              return_time: item.booking_data?.return_time || '',
              return_datetime: item.booking_data?.return_date && item.booking_data?.return_time 
                ? `${item.booking_data.return_date}T${item.booking_data.return_time}` 
                : undefined,
              contact_name: (item.booking_data?.contact_name || '') as string,
              contact_phone: (item.booking_data?.contact_phone || '') as string,
              special_requirements: (item.booking_data?.special_requirements || '') as string,
              selected_options: (item.selected_options || []) as Array<{ option_id: string; quantity: number }>,
              pricing_breakdown: item.pricing_breakdown && typeof item.pricing_breakdown === 'object' && Object.keys(item.pricing_breakdown).length > 0 
                ? (item.pricing_breakdown as {
                    base_price: number;
                    outbound_surcharge: number;
                    return_surcharge: number;
                    round_trip_discount: number;
                    options_total: number;
                    final_price: number;
                    currency: string;
                  })
                : null
            };
          } else if (item.product_type === 'tour') {
            return {
              id: item.id,
              type: 'tour' as const,
              title: item.product_title,
              price: parseFloat(item.unit_price),
              currency: item.currency,
              image: item.product_image || '',
              duration: item.booking_data?.duration || '',
              location: item.booking_data?.location || '',
              
              // Tour-specific fields
              tour_id: item.product_id,
              schedule_id: item.booking_data?.schedule_id || '',
              variant_id: item.variant_id || '',
              participants: item.booking_data?.participants || { adult: 1, child: 0, infant: 0 },
              selected_options: item.selected_options || [],
              special_requests: item.booking_data?.special_requests || '',
              
              // Calculated fields
              total_participants: (item.booking_data?.participants && typeof item.booking_data.participants === 'object' && 'adult' in item.booking_data.participants ? (item.booking_data.participants as { adult: number; child: number; infant: number }).adult : 0) + 
                                (item.booking_data?.participants && typeof item.booking_data.participants === 'object' && 'child' in item.booking_data.participants ? (item.booking_data.participants as { adult: number; child: number; infant: number }).child : 0) + 
                                (item.booking_data?.participants && typeof item.booking_data.participants === 'object' && 'infant' in item.booking_data.participants ? (item.booking_data.participants as { adult: number; child: number; infant: number }).infant : 0),
              unit_price: parseFloat(item.unit_price),
              options_total: parseFloat(item.options_total || '0'),
              subtotal: parseFloat(item.total_price)
            } as TourCartItem;
          } else {
            return {
              id: item.id,
              type: 'event' as const,
              title: item.product_title,
              price: parseFloat(item.unit_price),
              quantity: item.quantity,
              currency: item.currency,
              date: item.booking_data?.performance_date || item.booking_data?.date || '',
              time: item.booking_data?.performance_time || item.booking_data?.time || '',
              variant: item.variant_name || '',
              variant_name: item.variant_name || '',
              options: item.selected_options || {},
              special_requests: item.booking_data?.special_requests || '',
              image: item.product_image || '',
              duration: item.booking_data?.duration || '',
              location: item.booking_data?.venue_name || item.booking_data?.location || '',
              
              // Preserve the complete booking_data for detailed event information
              booking_data: item.booking_data || {},
              selected_options: item.selected_options || []
            } as EventCartItem;
          }
        });
        
        setItems(convertedItems);
      } else {
        console.error('Failed to load cart from backend:', (response as { status: number }).status);
        loadCartFromLocalStorage();
      }
    } catch (error) {
      console.error('Error loading cart from backend:', error);
      loadCartFromLocalStorage();
    } finally {
      setIsLoading(false);
    }
  }, [loadCartFromLocalStorage]);

  // Load cart from backend and localStorage on mount
  useEffect(() => {
    setIsClient(true);
    
    // Only load cart when we have complete authentication state
    if (isAuthenticated && user) {
      loadCartFromBackend();
    } else if (!isAuthenticated) {
      loadCartFromLocalStorage();
    }
  }, [isAuthenticated, user, loadCartFromBackend, loadCartFromLocalStorage]);

  const addItem = async (newItem: CartItem): Promise<{ success: boolean; error?: string; redirectTo?: string }> => {
    try {
      // Check authentication first
      if (!isAuthenticated || !user) {
        // For guests, check for overbooking conflicts in localStorage
        if (newItem.type === 'tour') {
          const tourItem = newItem as TourCartItem;
          const existingTourItem = items.find(item => 
            item.type === 'tour' && 
            (item as TourCartItem).tour_id === tourItem.tour_id &&
            (item as TourCartItem).schedule_id === tourItem.schedule_id &&
            (item as TourCartItem).variant_id === tourItem.variant_id
          );
          
          if (existingTourItem) {
            return { 
              success: false, 
              error: 'این تور در سبد خرید شما موجود است. ابتدا سفارش قبلی را تکمیل کنید.',
              redirectTo: 'checkout'
            };
          }
        } else if (newItem.type === 'event') {
          const eventItem = newItem as EventCartItem;
          const existingEventItem = items.find(item => 
            item.type === 'event' && 
            (item as EventCartItem).id === eventItem.id &&
            (item as EventCartItem).date === eventItem.date
          );
          
          if (existingEventItem) {
            return { 
              success: false, 
              error: 'این رویداد در سبد خرید شما موجود است. ابتدا سفارش قبلی را تکمیل کنید.',
              redirectTo: 'checkout'
            };
          }
        }
        
        // For guests, add to localStorage
        if (newItem.type === 'transfer') {
          // For transfers, always create a new item (no quantity merging)
          setItems(prevItems => {
            // Remove any existing transfer item (only one transfer allowed)
            const filteredItems = prevItems.filter(item => item.type !== 'transfer');
            return [...filteredItems, newItem];
          });
        } else if (newItem.type === 'tour') {
          // For tours, always create a new item (no quantity merging)
          setItems(prevItems => {
            const filteredItems = prevItems.filter(item => item.id !== newItem.id);
            return [...filteredItems, newItem];
          });
        } else {
          // For events, check if same item exists
          setItems(prevItems => {
            const existingItemIndex = prevItems.findIndex(item => 
              item.id === newItem.id && item.type === newItem.type
            );
            
            if (existingItemIndex >= 0) {
              // Update existing item quantity
              const updatedItems = [...prevItems];
              const existingItem = updatedItems[existingItemIndex] as EventCartItem;
              const newItemTyped = newItem as EventCartItem;
              updatedItems[existingItemIndex] = {
                ...existingItem,
                quantity: existingItem.quantity + newItemTyped.quantity
              };
              return updatedItems;
            } else {
              // Add new item
              return [...prevItems, newItem];
            }
          });
        }
        
        // Update localStorage
        const updatedItems = [...items, newItem];
        localStorage.setItem('cart', JSON.stringify({ items: updatedItems }));
        return { success: true };
      }
      
      // For authenticated users, the backend API call should be handled by the specific components
      // But we refresh the cart from backend after adding to get latest data
      await loadCartFromBackend();
      return { success: true };
    } catch (error) {
      console.error('Error adding item to cart:', error);
      return { success: false, error: 'Failed to add item to cart' };
    }
  };

  const updateItem = async (id: string, updates: Partial<CartItem>): Promise<{ success: boolean; error?: string }> => {
    try {
      // First update the backend if authenticated
      if (isAuthenticated) {
        const response = await apiClient.patch(`/cart/items/${id}/update/`, updates);
        if ((response as { status: number }).status === 200) {
          await loadCartFromBackend();
          return { success: true };
        } else {
          console.error('Failed to update cart item on backend:', (response as { status: number }).status);
        }
      }

      // Local update (for unauthenticated users or as fallback)
      setItems(prevItems =>
        prevItems.map(item => {
          if (item.id === id) {
            return { ...item, ...updates } as CartItem;
          }
          return item;
        })
      );
      return { success: true };
    } catch (error) {
      console.error('Error updating cart item:', error);
      return { success: false, error: 'Failed to update cart item' };
    }
  };

  const removeItem = async (id: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // First remove from backend if authenticated
      if (isAuthenticated) {
        const response = await apiClient.delete(`/cart/items/${id}/remove/`);
        if ((response as { status: number }).status === 200 || (response as { status: number }).status === 204) {
          await loadCartFromBackend();
          return { success: true };
        } else {
          console.error('Failed to remove cart item from backend:', (response as { status: number }).status);
        }
      }

      // Local removal (for unauthenticated users or as fallback)
      setItems(prevItems => prevItems.filter(item => item.id !== id));
      return { success: true };
    } catch (error) {
      console.error('Error removing cart item:', error);
      return { success: false, error: 'Failed to remove cart item' };
    }
  };

  const clearCart = async (): Promise<{ success: boolean; error?: string }> => {
    try {
      // First clear from backend if authenticated
      if (isAuthenticated) {
        const response = await apiClient.delete('/cart/clear/');
        if ((response as { status: number }).status === 200) {
          await loadCartFromBackend();
          return { success: true };
        } else {
          console.error('Failed to clear cart on backend:', (response as { status: number }).status);
        }
      }

      // Local clear (for unauthenticated users or as fallback)
      setItems([]);
      return { success: true };
    } catch (error) {
      console.error('Error clearing cart:', error);
      return { success: false, error: 'Failed to clear cart' };
    }
  };

  const getItemById = (id: string): CartItem | undefined => {
    return items.find(item => item.id === id);
  };

  const isInCart = (id: string): boolean => {
    return items.some(item => item.id === id);
  };

  const refreshCart = async (): Promise<void> => {
    if (isAuthenticated && user) {
      await loadCartFromBackend();
    } else {
      loadCartFromLocalStorage();
    }
  };

  const value = {
    items,
    totalItems,
    totalPrice,
    currency,
    isLoading,
    isClient,
    addItem,
    updateItem,
    removeItem,
    clearCart,
    getItemById,
    isInCart,
    refreshCart,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
} 