import { apiClient } from '../../../lib/api/client';
import type { Cart, CartItem, AddToCartPayload, UpdateCartItemPayload } from '../types/api';

// Base URL handled by apiClient

export const getCart = () => apiClient.get('/cart/');

export const getCartSummary = () => 
  apiClient.get('/cart/summary/');

export const getCartCount = () => apiClient.get('/cart/count/');

export const addToCart = (data: AddToCartPayload) => 
  apiClient.post('/cart/add/', data);

export const updateCartItem = (item_id: string, data: UpdateCartItemPayload) => 
  apiClient.put(`/cart/items/${item_id}/update/`, data);

export const removeFromCart = (item_id: string) => 
  apiClient.delete(`/cart/items/${item_id}/remove/`);

export const clearCart = () => 
  apiClient.delete('/cart/clear/');

export const mergeCart = (session_key: string) => 
  apiClient.post('/cart/merge/', { session_key });

// Re-export types for convenience
export type { Cart, CartItem, AddToCartPayload, UpdateCartItemPayload }; 