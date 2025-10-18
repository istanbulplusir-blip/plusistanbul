/**
 * Unified customer data management service for frontend.
 */

import { apiClient } from '../api/client';
import { User as UserType } from '../types/api';

export interface CustomerInfo {
  full_name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  country: string;
  postal_code: string;
  special_requests: string;
  driver_license?: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  profile?: {
    phone_number?: string;
    address?: string;
    city?: string;
    country?: string;
    postal_code?: string;
  };
}

export class CustomerDataService {
  /**
   * Get customer data from user profile or create default values.
   */
  static async getCustomerData(user?: UserType): Promise<CustomerInfo> {
    if (!user) {
      return this.getDefaultCustomerData();
    }

    try {
      // For now, get data directly from user (profile will be fetched separately)
      return {
        full_name: `${user.first_name} ${user.last_name}`.trim() || user.email,
        email: user.email,
        phone: user.phone_number || '',
        address: '', // Removed - not needed for services
        city: '', // Will be fetched from profile separately
        country: '', // Will be fetched from profile separately
        postal_code: '', // Removed - not needed for services
        special_requests: ''
      };
    } catch (error) {
      console.error('Error getting customer data from profile:', error);
      return this.getDefaultCustomerData(user);
    }
  }

  /**
   * Get default customer data.
   */
  static getDefaultCustomerData(user?: UserType): CustomerInfo {
    return {
      full_name: user ? `${user.first_name} ${user.last_name}`.trim() || user.email : '',
      email: user?.email || '',
      phone: user?.phone_number || '',
      address: '', // Removed - not needed for services
      city: '',
      country: '',
      postal_code: '', // Removed - not needed for services
      special_requests: ''
    };
  }

  /**
   * Save customer data to user profile.
   */
  static async saveCustomerData(data: CustomerInfo): Promise<void> {
    try {
      await apiClient.post('/users/profile/update/', {
        phone_number: data.phone,
        address: data.address,
        city: data.city,
        country: data.country,
        postal_code: data.postal_code,
        full_name: data.full_name
      });
    } catch (error) {
      console.error('Error saving customer data:', error);
      throw error;
    }
  }

  /**
   * Validate customer data based on authentication method.
   */
  static validateCustomerData(data: CustomerInfo, user?: UserType): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!data.full_name.trim()) {
      errors.push('نام و نام خانوادگی ضروری است');
    }

    if (!data.email.trim()) {
      errors.push('ایمیل ضروری است');
    } else if (!this.isValidEmail(data.email)) {
      errors.push('فرمت ایمیل نامعتبر است');
    }

    // Phone validation based on authentication method
    if (user) {
      const isOAuthUser = user.is_email_verified && !user.phone_number;
      const isEmailOTPUser = user.is_email_verified && !user.is_phone_verified;

      if (!isOAuthUser && !isEmailOTPUser && !data.phone.trim()) {
        errors.push('شماره تلفن ضروری است');
      }
    } else if (!data.phone.trim()) {
      errors.push('شماره تلفن ضروری است');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Get user limits based on authentication status.
   */
  static getUserLimits(user?: UserType): { maxItems: number; maxTotal: number; userType: string } {
    if (user) {
      return {
        maxItems: 10,
        maxTotal: 5000,
        userType: 'authenticated'
      };
    } else {
      return {
        maxItems: 3,
        maxTotal: 500,
        userType: 'guest'
      };
    }
  }

  /**
   * Check if cart merge would exceed limits.
   */
  static checkMergeLimits(currentItems: number, currentTotal: number, guestItems: number, guestTotal: number, user?: UserType): { canMerge: boolean; reason?: string } {
    const limits = this.getUserLimits(user);
    
    if (currentItems + guestItems > limits.maxItems) {
      return {
        canMerge: false,
        reason: `Cannot merge: would exceed maximum ${limits.maxItems} items limit. Please remove some items first.`
      };
    }
    
    if (currentTotal + guestTotal > limits.maxTotal) {
      return {
        canMerge: false,
        reason: `Cannot merge: would exceed maximum $${limits.maxTotal} total limit. Please remove some items first.`
      };
    }
    
    return { canMerge: true };
  }

  /**
   * Check if email is valid.
   */
  private static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Get guest session information.
   */
  static getGuestSessionInfo(): { sessionKey: string; isGuest: boolean } {
    // This would be implemented based on your session management
    const sessionKey = 'guest_session_' + Date.now();
    return {
      sessionKey,
      isGuest: true
    };
  }

  /**
   * Log cart merge attempt for debugging.
   */
  static logCartMergeAttempt(sessionInfo: { sessionKey: string; isGuest: boolean }, user: UserType | null, success: boolean, errorMessage?: string): void {
    console.log('🔍 Cart Merge Attempt:', {
      sessionKey: sessionInfo.sessionKey,
      isGuest: sessionInfo.isGuest,
      userId: user?.id || 'None',
      userEmail: user?.email || 'None',
      success,
      error: errorMessage
    });
  }
}
