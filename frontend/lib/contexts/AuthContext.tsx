'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User } from '../types/api';
import { tokenService } from '../services/tokenService';
import { apiClient } from '../api/client';
import { PreferenceService } from '../services/preferenceService';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (userData: User, tokens: { access: string; refresh: string }) => void;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  mergeGuestCart: () => Promise<{ success: boolean; message?: string; conflicts?: unknown[]; redirectTo?: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication status on mount
    checkAuthStatus();
    
    // Cleanup function
    return () => {
      // Cleanup any pending operations if needed
    };
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Use token service to check authentication
      const isAuth = tokenService.isAuthenticated();
      const userData = tokenService.getUser();
      
      
      if (isAuth && userData) {
        // Verify token with backend
        const isValid = await tokenService.validateToken();
        
        if (isValid) {
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          // Token is invalid, try to refresh
          const refreshSuccess = await tokenService.refreshToken();
          if (refreshSuccess) {
            const refreshedUser = tokenService.getUser();
            setUser(refreshedUser);
            setIsAuthenticated(true);
          } else {
            // Refresh failed, clear everything
            tokenService.clearTokens();
            setUser(null);
            setIsAuthenticated(false);
          }
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const mergeGuestCart = async (): Promise<{ success: boolean; message?: string; conflicts?: unknown[]; redirectTo?: string }> => {
    try {
      // Get guest session ID from localStorage
      let sessionKey: string | null = null;
      try {
        sessionKey = typeof window !== 'undefined' ? localStorage.getItem('guest_session_id') : null;
      } catch {}

      console.log('🔍 Merge guest cart - session key:', sessionKey);

      if (sessionKey) {
        // Call backend to merge guest cart into user cart
        const response = await apiClient.post('/cart/merge/', { session_key: sessionKey });

        console.log('✅ Guest cart merge response:', response);

        console.log('Guest cart merged successfully');
        return { success: true, message: (response as { data: { message?: string } }).data.message };
      }

      console.log('⚠️ No session key found for guest cart merge');
      return { success: true };
    } catch (error: unknown) {
      console.error('Error merging guest cart:', error);
      
      // Handle overbooking conflicts
      if ((error as { response?: { data?: { code?: string; message?: string; conflicts?: unknown[]; redirectTo?: string } } }).response?.data?.code === 'OVERBOOKING_CONFLICTS') {
        return {
          success: false,
          message: (error as { response?: { data?: { message?: string } } }).response?.data?.message,
          conflicts: (error as { response?: { data?: { conflicts?: unknown[] } } }).response?.data?.conflicts,
          redirectTo: (error as { response?: { data?: { redirect_to?: string } } }).response?.data?.redirect_to
        };
      }
      
      // Handle other merge errors
      if ((error as { response?: { data?: { code?: string; message?: string } } }).response?.data?.code === 'MERGE_LIMIT_EXCEEDED' || (error as { response?: { data?: { code?: string; message?: string } } }).response?.data?.code === 'MERGE_TOTAL_EXCEEDED') {
        return {
          success: false,
          message: (error as { response?: { data?: { message?: string } } }).response?.data?.message,
          redirectTo: 'cart'
        };
      }
      
      // Don't throw error, just log it
      return { success: false, message: 'خطا در ادغام سبد خرید' };
    }
  };

  const login = async (userData: User, tokens: { access: string; refresh: string }) => {
    // Use token service to store tokens
    tokenService.storeTokens({
      access: tokens.access,
      refresh: tokens.refresh,
      user: userData
    });
    
    setUser(userData);
    setIsAuthenticated(true);
    
    // Sync guest preferences to user profile
    try {
      const syncResult = await PreferenceService.syncGuestPreferencesToUser(userData as unknown as { id: string; [key: string]: unknown });
      if (syncResult.success) {
        console.log('✅ Guest preferences synced successfully');
        // Update user data with synced preferences
        const updatedUser = { ...userData };
        const guestPrefs = PreferenceService.getGuestPreferences();
        if (guestPrefs.currency && guestPrefs.currency !== userData.preferred_currency) {
          updatedUser.preferred_currency = guestPrefs.currency;
        }
        if (guestPrefs.language && guestPrefs.language !== userData.preferred_language) {
          updatedUser.preferred_language = guestPrefs.language;
        }
        setUser(updatedUser);
        tokenService.storeTokens({
          access: tokens.access,
          refresh: tokens.refresh,
          user: updatedUser
        });
      } else {
        console.warn('⚠️ Guest preference sync failed:', syncResult.message);
      }
    } catch (error) {
      console.error('❌ Error syncing guest preferences:', error);
      // Continue with login even if preference sync fails
    }
    
    // Trigger UnifiedCartContext merge (let it handle the actual merging)
    if (typeof window !== 'undefined') {
      try {
        const event = new CustomEvent('auth:mergeGuestCart');
        window.dispatchEvent(event);
        console.log('Auth merge event dispatched');
      } catch (error) {
        console.error('Failed to dispatch auth merge event:', error);
      }
    }
  };

  const logout = async () => {
    try {
      // Don't clear guest session ID on logout - let user continue as guest
      // The guest session ID will be managed by UnifiedCartContext

      // Use token service to clear tokens
      tokenService.clearTokens();
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Error during logout:', error);
      // Continue with logout even if there are errors
      tokenService.clearTokens();
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      // Update user in token service
      const currentTokens = {
        access: tokenService.getAccessToken() || '',
        refresh: tokenService.getRefreshToken() || '',
        user: updatedUser
      };
      tokenService.storeTokens(currentTokens);
      setUser(updatedUser);
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    updateUser,
    mergeGuestCart,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 