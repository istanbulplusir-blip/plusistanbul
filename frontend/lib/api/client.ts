/**
 * API Client configuration for Peykan Tourism Platform.
 */

import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosRequestConfig } from 'axios';
import { tokenService } from '../services/tokenService';

// Create axios instance with improved configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 5000, // Reduced timeout to 5 seconds for better responsiveness
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable cookies for CORS
});

// Retry configuration
const MAX_RETRIES = 1; // Reduced from 2 to 1
const RETRY_DELAY = 1000; // 1 second

// Request deduplication cache
const pendingRequests = new Map<string, Promise<unknown>>();

// Helper function to create request key
const createRequestKey = (config: InternalAxiosRequestConfig): string => {
  return `${config.method?.toUpperCase() || 'GET'}:${config.url}:${JSON.stringify(config.params || {})}:${JSON.stringify(config.data || {})}`;
};

// Request interceptor to add auth token and handle deduplication
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from token service
    const authHeader = tokenService.getAuthHeader();
    
    if ('Authorization' in authHeader && config.headers) {
      config.headers.Authorization = authHeader.Authorization;
    }
    
    // Add Accept-Language header based on current locale
    if (config.headers) {
      // Get current language from URL or localStorage
      let currentLanguage = 'fa'; // Default to Persian
      
      if (typeof window !== 'undefined') {
        // Try to get from URL first
        const pathname = window.location.pathname;
        const localeMatch = pathname.match(/^\/([a-z]{2})\//);
        if (localeMatch && ['fa', 'en', 'tr'].includes(localeMatch[1])) {
          currentLanguage = localeMatch[1];
        } else {
          // Fallback to localStorage
          const storedLang = localStorage.getItem('language');
          if (storedLang && ['fa', 'en', 'tr'].includes(storedLang)) {
            currentLanguage = storedLang;
          }
        }
      }
      
      config.headers['Accept-Language'] = currentLanguage;
    }
    
    // Add retry count to config using a custom property
    if (!(config as InternalAxiosRequestConfig & { retryCount?: number }).retryCount) {
      (config as InternalAxiosRequestConfig & { retryCount?: number }).retryCount = 0;
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling with retry logic
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    console.error('API Response error:', error);
    
    // Handle authentication errors
    if (error.response?.status === 401) {
      // Try to refresh token
      const refreshSuccess = await tokenService.refreshToken();
      
      if (refreshSuccess) {
        // Retry the original request with new token
        const originalRequest = error.config;
        const authHeader = tokenService.getAuthHeader();
        
        if ('Authorization' in authHeader) {
          originalRequest.headers.Authorization = authHeader.Authorization;
        }
        
        return apiClient(originalRequest);
      } else {
        // Refresh failed, clear auth and redirect to login
        tokenService.clearTokens();
        
        // Redirect to login if in browser
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }
    
    // Handle network errors and timeouts with retry logic
    if (error.code === 'ECONNABORTED' || !error.response) {
      const config = error.config;
      
      // Check if we can retry this request
      if (config) {
        const configWithRetry = config as InternalAxiosRequestConfig & { retryCount?: number };
        const retryCount = configWithRetry.retryCount || 0;
        if (retryCount < MAX_RETRIES) {
          configWithRetry.retryCount = retryCount + 1;
          
          console.log(`Retrying request (${configWithRetry.retryCount}/${MAX_RETRIES})...`);
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (configWithRetry.retryCount || 1)));
          
          // Retry the request
          return apiClient(config);
        }
      }
      
      // No more retries, provide user-friendly error
      if (error.code === 'ECONNABORTED') {
        console.error('Request timeout after retries');
        error.message = 'Request timeout: The server is taking too long to respond. Please try again.';
      } else {
        console.error('Network error - backend may be down');
        error.message = 'Network error: Unable to connect to the server. Please check your connection and try again.';
      }
    }
    
    return Promise.reject(error);
  }
);

// Enhanced request method with deduplication
const enhancedApiClient = {
  ...apiClient,
  
  // Override get method to add deduplication
  async get(url: string, config?: AxiosRequestConfig) {
    const requestKey = createRequestKey({ ...config, method: 'GET', url } as InternalAxiosRequestConfig);
    
    // Check if there's already a pending request
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey);
    }
    
    // Create new request
    const requestPromise = apiClient.get(url, config);
    
    // Store the request promise
    pendingRequests.set(requestKey, requestPromise);
    
    // Clean up after request completes
    requestPromise.finally(() => {
      pendingRequests.delete(requestKey);
    });
    
    return requestPromise;
  },
  
  // Override post method to add deduplication
  async post(url: string, data?: unknown, config?: AxiosRequestConfig) {
    const requestKey = createRequestKey({ ...config, method: 'POST', url, data } as InternalAxiosRequestConfig);
    
    // Check if there's already a pending request
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey);
    }
    
    // Create new request
    const requestPromise = apiClient.post(url, data, config);
    
    // Store the request promise
    pendingRequests.set(requestKey, requestPromise);
    
    // Clean up after request completes
    requestPromise.finally(() => {
      pendingRequests.delete(requestKey);
    });
    
    return requestPromise;
  },
  
  // Override put method to add deduplication
  async put(url: string, data?: unknown, config?: AxiosRequestConfig) {
    const requestKey = createRequestKey({ ...config, method: 'PUT', url, data } as InternalAxiosRequestConfig);
    
    // Check if there's already a pending request
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey);
    }
    
    // Create new request
    const requestPromise = apiClient.put(url, data, config);
    
    // Store the request promise
    pendingRequests.set(requestKey, requestPromise);
    
    // Clean up after request completes
    requestPromise.finally(() => {
      pendingRequests.delete(requestKey);
    });
    
    return requestPromise;
  },
  
  // Override delete method to add deduplication
  async delete(url: string, config?: AxiosRequestConfig) {
    const requestKey = createRequestKey({ ...config, method: 'DELETE', url } as InternalAxiosRequestConfig);
    
    // Check if there's already a pending request
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey);
    }
    
    // Create new request
    const requestPromise = apiClient.delete(url, config);
    
    // Store the request promise
    pendingRequests.set(requestKey, requestPromise);
    
    // Clean up after request completes
    requestPromise.finally(() => {
      pendingRequests.delete(requestKey);
    });
    
    return requestPromise;
  },
  
  // Override patch method to add deduplication
  async patch(url: string, data?: unknown, config?: AxiosRequestConfig) {
    const requestKey = createRequestKey({ ...config, method: 'PATCH', url, data } as InternalAxiosRequestConfig);
    
    // Check if there's already a pending request
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey);
    }
    
    // Create new request
    const requestPromise = apiClient.patch(url, data, config);
    
    // Store the request promise
    pendingRequests.set(requestKey, requestPromise);
    
    // Clean up after request completes
    requestPromise.finally(() => {
      pendingRequests.delete(requestKey);
    });
    
    return requestPromise;
  }
};

export { enhancedApiClient as apiClient }; 