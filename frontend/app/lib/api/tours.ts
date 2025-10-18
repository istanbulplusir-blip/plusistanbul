import { apiClient } from '../../../lib/api/client';
import type { 
  Tour, TourCategory, TourSearchParams, TourBookingPayload, 
  TourSchedule, TourReview
} from '../types/api';

const BASE = '/tours/';

export const getTours = (params?: Record<string, unknown>) => 
  apiClient.get(`${BASE}`, { params });

export const getTourDetail = (slug: string) => 
  apiClient.get(`${BASE}${slug}/`);

export const searchTours = (data: TourSearchParams) => 
  apiClient.post(`${BASE}search/`, data);

export const bookTour = (data: TourBookingPayload) => 
  apiClient.post(`${BASE}tours/booking/`, data);

export const getTourCategories = () => 
  apiClient.get(`${BASE}categories/`);

export const getTourSchedules = (slug: string) => 
  apiClient.get(`${BASE}${slug}/schedules/`);

export const getTourStats = (slug: string) => 
  apiClient.get(`${BASE}${slug}/stats/`);

export const getTourAvailability = (slug: string, params?: { date_from: string; date_to: string }) => 
  apiClient.get(`${BASE}${slug}/availability/`, { params });

export const getTourReviews = (slug: string) => 
  apiClient.get(`${BASE}${slug}/reviews/`);

export const createTourReview = (slug: string, data: { rating: number; title: string; comment: string; category?: string }) => 
  apiClient.post(`${BASE}${slug}/reviews/create/`, data);

// New API endpoints for review management
export const updateTourReview = (reviewId: string, data: { rating?: number; title?: string; comment?: string; category?: string }) => 
  apiClient.put(`/reviews/${reviewId}/edit/`, data);

export const deleteTourReview = (reviewId: string) => 
  apiClient.delete(`/reviews/${reviewId}/delete/`);

export const getTourReviewStats = (slug: string) => 
  apiClient.get(`${BASE}${slug}/reviews/stats/`);

export const reportTourReview = (reviewId: string, data: { reason: string; description?: string }) => 
  apiClient.post(`/reviews/${reviewId}/report/`, data);

export const respondToReview = (reviewId: string, data: { content: string; is_public?: boolean; is_official?: boolean }) => 
  apiClient.post(`/reviews/${reviewId}/respond/`, data);

// Re-export types for convenience
export type { 
  Tour, TourCategory, TourSearchParams, TourBookingPayload, 
  TourSchedule, TourReview 
}; 