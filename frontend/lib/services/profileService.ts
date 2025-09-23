/**
 * Profile Service for handling profile-related API calls
 */

import { tokenService } from './tokenService';

export interface ProfileUpdateData {
  // Non-sensitive fields (can be updated directly)
  date_of_birth?: string;
  nationality?: string;
  preferred_language?: string;
  preferred_currency?: string;
  profile?: {
    bio?: string;
    address?: string;
    city?: string;
    country?: string;
    postal_code?: string;
    website?: string;
    facebook?: string;
    instagram?: string;
    twitter?: string;
    newsletter_subscription?: boolean;
    marketing_emails?: boolean;
  };
}

export interface SensitiveFieldRequest {
  field: 'email' | 'phone_number' | 'first_name' | 'last_name';
  new_value: string;
  method?: 'email' | 'phone_number';
}

export interface SensitiveFieldVerify {
  field: 'email' | 'phone_number' | 'first_name' | 'last_name';
  new_value: string;
  otp_code: string;
}

export interface ProfileResponse {
  success: boolean;
  user?: Record<string, unknown>;
  profile?: Record<string, unknown>;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface SensitiveFieldResponse {
  success: boolean;
  message: string;
  field?: string;
  new_value?: string;
  otp_id?: string;
  requires_otp?: boolean;
  sensitive_fields?: string[];
}

class ProfileService {
  private baseUrl = '/api/v1/auth';

  /**
   * Get user profile
   */
  async getProfile(): Promise<ProfileResponse> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${this.baseUrl}/profile/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to get profile');
      }

      return {
        success: true,
        user: data.user,
        profile: data.profile,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get profile';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }

  /**
   * Update basic profile (non-sensitive fields)
   */
  async updateBasicProfile(data: ProfileUpdateData): Promise<ProfileResponse> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${this.baseUrl}/profile/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        // Check if it's a sensitive field error
        if (result.requires_otp) {
          throw new Error(`Sensitive fields ${result.sensitive_fields?.join(', ')} require OTP verification`);
        }
        throw new Error(result.message || 'Failed to update profile');
      }

      return {
        success: true,
        user: result.user,
        profile: result.profile,
        message: result.message,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update profile';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }

  /**
   * Request sensitive field update (send OTP)
   */
  async requestSensitiveFieldUpdate(data: SensitiveFieldRequest): Promise<SensitiveFieldResponse> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${this.baseUrl}/profile/sensitive/request/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Failed to request sensitive field update');
      }

      return {
        success: true,
        message: result.message,
        field: result.field,
        new_value: result.new_value,
        otp_id: result.otp_id,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to request sensitive field update';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }

  /**
   * Verify sensitive field update (verify OTP and update)
   */
  async verifySensitiveFieldUpdate(data: SensitiveFieldVerify): Promise<ProfileResponse> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${this.baseUrl}/profile/sensitive/verify/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Failed to verify sensitive field update');
      }

      return {
        success: true,
        user: result.user,
        message: result.message,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to verify sensitive field update';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }

  /**
   * Upload avatar
   */
  async uploadAvatar(file: File): Promise<ProfileResponse> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const formData = new FormData();
      formData.append('avatar', file);

      const response = await fetch(`${this.baseUrl}/profile/avatar/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Failed to upload avatar');
      }

      return {
        success: true,
        user: result.user,
        message: result.message,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload avatar';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }

  /**
   * Resend email verification OTP
   */
  async resendEmailOTP(): Promise<{ success: boolean; message: string }> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) throw new Error('No access token available');
      
      // Get user email from token service
      const user = tokenService.getUser();
      const email = user?.email;
      
      if (!email) {
        throw new Error('User email not found');
      }
      
      const response = await fetch(`${this.baseUrl}/verify-email/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Failed to resend email OTP');
      return { success: true, message: result.message };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to resend email OTP';
      return { success: false, message: errorMessage };
    }
  }

  /**
   * Resend phone verification OTP
   */
  async resendPhoneOTP(): Promise<{ success: boolean; message: string }> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) throw new Error('No access token available');
      
      // Get user phone from token service
      const user = tokenService.getUser();
      const phone = user?.phone_number;
      
      if (!phone) {
        throw new Error('User phone number not found');
      }
      
      const response = await fetch(`${this.baseUrl}/verify-phone/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Failed to resend phone OTP');
      return { success: true, message: result.message };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to resend phone OTP';
      return { success: false, message: errorMessage };
    }
  }
}

export const profileService = new ProfileService(); 