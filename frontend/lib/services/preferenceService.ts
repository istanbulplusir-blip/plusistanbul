/**
 * Preference Service for managing user preferences across guest and authenticated states
 */

import { apiClient } from '../api/client';

export interface GuestPreferences {
  currency?: string;
  language?: string;
}

export interface UserPreferences {
  preferred_currency?: string;
  preferred_language?: string;
}

export class PreferenceService {
  /**
   * Get guest preferences from localStorage
   */
  static getGuestPreferences(): GuestPreferences {
    if (typeof window === 'undefined') return {};
    
    try {
      return {
        currency: localStorage.getItem('currency') || undefined,
        language: localStorage.getItem('language') || undefined,
      };
    } catch (error) {
      console.error('Error getting guest preferences:', error);
      return {};
    }
  }

  /**
   * Store guest preferences in localStorage
   */
  static setGuestPreferences(preferences: GuestPreferences): void {
    if (typeof window === 'undefined') return;
    
    try {
      if (preferences.currency) {
        localStorage.setItem('currency', preferences.currency);
      }
      if (preferences.language) {
        localStorage.setItem('language', preferences.language);
      }
    } catch (error) {
      console.error('Error setting guest preferences:', error);
    }
  }

  /**
   * Clear guest preferences from localStorage
   */
  static clearGuestPreferences(): void {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.removeItem('currency');
      localStorage.removeItem('language');
    } catch (error) {
      console.error('Error clearing guest preferences:', error);
    }
  }

  /**
   * Sync guest preferences to user profile
   * This is called after successful login to merge guest preferences
   */
  static async syncGuestPreferencesToUser(user: { id: string; [key: string]: unknown }): Promise<{ success: boolean; message?: string }> {
    try {
      const guestPrefs = this.getGuestPreferences();
      
      // Check if guest preferences differ from user preferences
      const updates: UserPreferences = {};
      
      if (guestPrefs.currency && guestPrefs.currency !== user.preferred_currency) {
        updates.preferred_currency = guestPrefs.currency;
        console.log(`Syncing currency: ${user.preferred_currency} → ${guestPrefs.currency}`);
      }
      
      if (guestPrefs.language && guestPrefs.language !== user.preferred_language) {
        updates.preferred_language = guestPrefs.language;
        console.log(`Syncing language: ${user.preferred_language} → ${guestPrefs.language}`);
      }
      
      // If there are updates to make, call the API
      if (Object.keys(updates).length > 0) {
        console.log('Syncing guest preferences to user profile:', updates);
        
        // Determine the correct API endpoint based on user role
        let endpoint = '/api/v1/users/profile/';
        if (user.role === 'agent') {
          endpoint = '/api/v1/agents/profile/update/';
        }
        
        const response = await apiClient.patch(endpoint, updates);
        
        if ((response as { status: number }).status === 200) {
          console.log('✅ Guest preferences synced successfully');
          
          // Clear guest preferences after successful sync
          this.clearGuestPreferences();
          
          return { success: true, message: 'Preferences synced successfully' };
        } else {
          console.warn('⚠️ Failed to sync preferences, but login continues');
          return { success: false, message: 'Failed to sync preferences' };
        }
      } else {
        console.log('ℹ️ No guest preferences to sync');
        return { success: true, message: 'No preferences to sync' };
      }
    } catch (error) {
      console.error('❌ Error syncing guest preferences:', error);
      // Don't throw error - login should continue even if preference sync fails
      return { success: false, message: 'Error syncing preferences' };
    }
  }

  /**
   * Update user preferences and sync to localStorage for consistency
   */
  static async updateUserPreferences(preferences: UserPreferences, userRole: string = 'customer'): Promise<{ success: boolean; message?: string }> {
    try {
      // Determine the correct API endpoint based on user role
      let endpoint = '/api/v1/users/profile/';
      if (userRole === 'agent') {
        endpoint = '/api/v1/agents/profile/update/';
      }
      
      const response = await apiClient.patch(endpoint, preferences);
      
      if ((response as { status: number }).status === 200) {
        // Update localStorage to keep it in sync
        if (preferences.preferred_currency) {
          localStorage.setItem('currency', preferences.preferred_currency);
        }
        if (preferences.preferred_language) {
          localStorage.setItem('language', preferences.preferred_language);
        }
        
        return { success: true, message: 'Preferences updated successfully' };
      } else {
        return { success: false, message: 'Failed to update preferences' };
      }
    } catch (error) {
      console.error('Error updating user preferences:', error);
      return { success: false, message: 'Error updating preferences' };
    }
  }

  /**
   * Get current effective preferences (user preferences if authenticated, guest preferences otherwise)
   */
  static getCurrentPreferences(user: { preferred_currency?: string; preferred_language?: string } | null): { currency: string; language: string } {
    if (user && user.preferred_currency && user.preferred_language) {
      return {
        currency: user.preferred_currency,
        language: user.preferred_language,
      };
    }
    
    const guestPrefs = this.getGuestPreferences();
    return {
      currency: guestPrefs.currency || 'USD',
      language: guestPrefs.language || 'fa',
    };
  }
}
