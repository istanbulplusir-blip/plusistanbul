import { apiClient } from './client';
import type { 
  LoginRequest, 
  RegisterRequest, 
  User 
} from '../types/api';

// Authentication API endpoints
export const login = (data: LoginRequest) => 
  apiClient.post('/auth/login/', data);

export const register = (data: RegisterRequest) => 
  apiClient.post('/auth/register/', data);

export const logout = () => {
  const refreshToken = typeof window !== 'undefined' 
    ? localStorage.getItem('refresh_token') 
    : null;
    
  return apiClient.post('/auth/logout/', {
    refresh_token: refreshToken
  });
};

export const refreshToken = (refreshToken: string) => 
  apiClient.post('/auth/token/refresh/', {
    refresh: refreshToken
  });

export const getProfile = () => 
  apiClient.get('/auth/profile/');

export const updateProfile = (data: Partial<User>) => 
  apiClient.patch('/auth/profile/', data);

export const changePassword = (data: {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}) => 
  apiClient.post('/auth/change-password/', data);

export const requestPasswordReset = (email: string) => 
  apiClient.post('/auth/forgot-password/', { email });

export const resetPassword = (data: {
  email: string;
  new_password: string;
  new_password_confirm: string;
  otp_code: string;
}) => 
  apiClient.post('/auth/reset-password/confirm/', data);

export const requestOTP = (data: {
  phone?: string;
  email?: string;
  otp_type: 'phone' | 'email' | 'password_reset' | 'login';
}) => 
  apiClient.post('/auth/otp/request/', data);

export const verifyOTP = (data: {
  email?: string;
  phone?: string;
  code: string;
  otp_type: 'email' | 'phone' | 'password_reset' | 'login';
}) => 
  apiClient.post('/auth/otp/verify/', data);

export const verifyEmail = (data: {
  email: string;
  code: string;
}) => 
  apiClient.post('/auth/verify-email/', {
    email: data.email,
    otp_code: data.code
  }); 

// Google Sign-In (ID token)
export const googleSignIn = (id_token: string) =>
  apiClient.post('/auth/social/google/', { id_token });