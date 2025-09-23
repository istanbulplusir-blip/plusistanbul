import { apiClient } from './client';
import type { 
  AddToCartPayload, 
  UpdateCartItemPayload 
} from '../types/api';

// Base URL comes from apiClient; withCredentials is enabled there for session-based guest carts

// Cart API endpoints
export const getCart = () => 
  apiClient.get('/cart/');

export const getCartSummary = () => 
  apiClient.get('/cart/summary/');

export const addToCart = (data: AddToCartPayload) => 
  apiClient.post('/cart/add/', data);

export const updateCartItem = (itemId: string, data: UpdateCartItemPayload) => 
  apiClient.patch(`/cart/items/${itemId}/`, data);

export const removeFromCart = (itemId: string) => 
  apiClient.delete(`/cart/items/${itemId}/remove/`);

export const clearCart = () => 
  apiClient.delete('/cart/clear/');

// Event-specific cart operations
export const addEventSeatsToCart = (data: {
  event_id: string;
  performance_id: string;
  ticket_type_id: string;
  seats: Array<{
    seat_id: string;
    seat_number: string;
    row_number: string;
    section: string;
    price: number;
  }>;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
}) => 
  apiClient.post('/cart/events/seats/', data);

// Tour-specific cart operations
export const addTourToCart = (data: {
  tour_id: string;
  variant_id?: string;
  quantity: number;
  passengers?: {
    adults: number;
    children: number;
    infants: number;
  };
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
}) => 
  apiClient.post('/cart/tours/', data);

// Transfer-specific cart operations (deprecated - use transfers.ts instead)
export const addTransferToCart = (data: {
  transfer_id: string;
  vehicle_type_id?: string;
  quantity: number;
  passengers?: {
    adults: number;
    children: number;
    infants: number;
  };
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
}) => 
  apiClient.post('/cart/add/', {
    product_type: 'transfer',
    product_id: data.transfer_id,
    variant_id: data.vehicle_type_id,
    quantity: data.quantity,
    selected_options: data.selected_options || [],
    booking_data: {
      passengers: data.passengers,
    },
    special_requests: data.special_requests || '',
  });