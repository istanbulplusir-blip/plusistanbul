/**
 * API utility functions and type guards for better error handling
 */

// Error handling types and utilities
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  status: number;
  message?: string;
}

// Type guards for better error handling
export const isApiError = (error: unknown): error is ApiError => {
  return Boolean(error && 
         typeof error === 'object' && 
         'message' in error && 
         typeof (error as Record<string, unknown>).message === 'string');
};

export const isAxiosError = (error: unknown): error is { 
  response?: { 
    status: number; 
    data?: unknown; 
    statusText?: string; 
  }; 
  message: string; 
  code?: string; 
} => {
  return Boolean(error && 
         typeof error === 'object' && 
         'response' in error && 
         'message' in error);
};

// Helper function to extract error message
export const extractErrorMessage = (error: unknown, defaultMessage: string = 'An error occurred'): string => {
  if (isApiError(error)) {
    return error.message;
  }
  
  if (isAxiosError(error)) {
    return error.message || defaultMessage;
  }
  
  if (error && typeof error === 'object' && 'message' in error && typeof (error as Record<string, unknown>).message === 'string') {
    return (error as Record<string, unknown>).message as string;
  }
  
  return defaultMessage;
};

// Helper function to check if error is a specific HTTP status
export const isHttpError = (error: unknown, status: number): boolean => {
  if (isAxiosError(error)) {
    return error.response?.status === status;
  }
  return false;
};

// Helper function to check if error is a network error
export const isNetworkError = (error: unknown): boolean => {
  if (isAxiosError(error)) {
    return error.code === 'ECONNABORTED' || error.code === 'NETWORK_ERROR';
  }
  return false;
};
