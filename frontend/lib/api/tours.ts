import { apiClient } from './client';
import { TourListResponse, TourDetailResponse, TourSearchParams } from '../types/api';

// Interface for home tours response
export interface HomeToursResponse {
  featured_tours: TourDetailResponse[];
  special_tours: TourDetailResponse[];
  seasonal_tours: TourDetailResponse[];
  popular_tours: TourDetailResponse[];
}

// Get all tours
export const getTours = async (params?: TourSearchParams): Promise<TourListResponse> => {
  try {
    const response = await apiClient.get('/tours/', { params });
    return (response as { data: TourListResponse }).data;
  } catch (error) {
    console.error('Error fetching tours:', error);
    return {
      count: 0,
      next: null,
      previous: null,
      results: []
    };
  }
};

// Get tour by slug
export const getTourBySlug = async (slug: string): Promise<TourDetailResponse | null> => {
  try {
    const response = await apiClient.get(`/tours/${slug}/`);
    return (response as { data: TourDetailResponse }).data;
  } catch (error) {
    console.error('Error fetching tour by slug:', error);
    return null;
  }
};

// Get tour by ID
export const getTourById = async (id: string): Promise<TourDetailResponse | null> => {
  try {
    const response = await apiClient.get(`/tours/${id}/`);
    return (response as { data: TourDetailResponse }).data;
  } catch (error) {
    console.error('Error fetching tour by ID:', error);
    return null;
  }
};

// Search tours
export const searchTours = async (searchParams: TourSearchParams): Promise<TourListResponse> => {
  try {
    const response = await apiClient.get('/tours/search/', {
      params: searchParams
    });
    return (response as { data: TourListResponse }).data;
  } catch (error) {
    console.error('Error searching tours:', error);
    return {
      count: 0,
      next: null,
      previous: null,
      results: []
    };
  }
};

// Get home tours (categorized)
export const getHomeTours = async (): Promise<HomeToursResponse> => {
  try {
    const response = await apiClient.get('/tours/home-tours/');
    return (response as { data: HomeToursResponse }).data;
  } catch (error) {
    console.error('Error fetching home tours:', error);
    return {
      featured_tours: [],
      special_tours: [],
      seasonal_tours: [],
      popular_tours: []
    };
  }
};

// Get tour categories
export const getTourCategories = async () => {
  try {
    const response = await apiClient.get('/tours/categories/');
    return (response as { data: unknown[] }).data;
  } catch (error) {
    console.error('Error fetching tour categories:', error);
    return [];
  }
}; 