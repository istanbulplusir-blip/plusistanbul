/**
 * API functions for Car Rentals
 */

import { apiClient } from './client';
import type { CarRentalLocation } from '../types/car-rentals';

// Types
export interface CarRental {
  id: string;
  slug: string;
  title: string;
  description: string;
  short_description: string;
  brand: string;
  model: string;
  year: number;
  seats: number;
  fuel_type: 'gasoline' | 'diesel' | 'hybrid' | 'electric' | 'lpg';
  transmission: 'manual' | 'automatic' | 'semi_automatic';
  price_per_day: string;
  price_per_hour?: string;
  currency: string;
  allow_hourly_rental?: boolean;
  min_rent_hours?: number;
  max_hourly_rental_hours?: number;
  city: string;
  country: string;
  pickup_location: string;
  dropoff_location: string;
  default_pickup_locations?: Array<{
    id: string;
    name: string;
    description?: string;
    address: string;
    city: string;
    country: string;
    latitude?: number;
    longitude?: number;
    location_type: 'airport' | 'hotel' | 'station' | 'city_center' | 'port' | 'other';
  }>;
  default_dropoff_locations?: Array<{
    id: string;
    name: string;
    description?: string;
    address: string;
    city: string;
    country: string;
    latitude?: number;
    longitude?: number;
    location_type: 'airport' | 'hotel' | 'station' | 'city_center' | 'port' | 'other';
  }>;
  allow_custom_pickup_location?: boolean;
  allow_custom_dropoff_location?: boolean;
  image?: string;
  image_url?: string;
  is_featured: boolean;
  is_popular: boolean;
  is_special: boolean;
  is_seasonal: boolean;
  is_available: boolean;
  comprehensive_insurance_price?: string;
  category: {
    id: string;
    name: string;
    slug: string;
  };
  agent: {
    id: string;
    username: string;
    first_name: string;
    last_name: string;
  };
  pricing_summary: {
    base_price: number;
    weekly_discount: number;
    monthly_discount: number;
    min_price: number;
    max_price: number;
  };
  created_at: string;
  updated_at: string;
}

export interface CarRentalCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  sort_order: number;
  is_active: boolean;
}

export interface CarRentalOption {
  id: string;
  name: string;
  description: string;
  option_type: string;
  price_type: 'fixed' | 'daily' | 'percentage';
  price: string;
  price_percentage?: number;
  max_quantity: number;
  is_active: boolean;
}

export interface CarRentalAvailability {
  id: string;
  car_rental: string;
  start_date: string;
  end_date: string;
  is_available: boolean;
  max_quantity: number;
  booked_quantity: number;
  available_quantity: number;
  price_override?: string;
}

export interface CarRentalSearchParams {
  query?: string;
  category?: string;
  city?: string;
  country?: string;
  brand?: string;
  fuel_type?: string;
  transmission?: string;
  min_seats?: number;
  max_seats?: number;
  min_price?: number;
  max_price?: number;
  pickup_date?: string;
  dropoff_date?: string;
  sort_by?: 'price_asc' | 'price_desc' | 'year_desc' | 'name_asc' | 'name_desc' | 'created_at_desc';
}

export interface CarRentalBookingParams {
  car_rental_id: string;
  pickup_date: string;
  dropoff_date: string;
  pickup_time: string;
  dropoff_time: string;
  driver_name: string;
  driver_license: string;
  driver_phone: string;
  driver_email: string;
  selected_options: Array<{
    id: string;
    quantity: number;
  }>;
  basic_insurance: boolean;
  comprehensive_insurance: boolean;
  special_requirements?: string;
}

export interface CarRentalAvailabilityCheck {
  pickup_date: string;
  dropoff_date: string;
  pickup_time?: string;
  dropoff_time?: string;
}

export interface CarRentalAvailabilityResponse {
  available: boolean;
  rental_days: number;
  total_price: number;
  daily_rate: number;
  pricing_breakdown: {
    base_price: number;
    weekly_discount: number;
    monthly_discount: number;
    options_total: number;
    insurance_total: number;
    final_price: number;
  };
}

// API Functions
export const getCarRentals = async (params?: {
  page?: number;
  page_size?: number;
  search?: string;
  category?: string;
  city?: string;
  brand?: string;
  fuel_type?: string;
  transmission?: string;
  min_seats?: number;
  max_seats?: number;
  min_price?: number;
  max_price?: number;
  is_featured?: boolean;
  is_popular?: boolean;
  ordering?: string;
}) => {
  const response = await apiClient.get('/car-rentals/car-rentals/', { params });
  return (response as { data: { count: number; next: string | null; previous: string | null; results: CarRental[] } }).data;
};

export const getCarRental = async (id: string) => {
  const response = await apiClient.get(`/car-rentals/car-rentals/${id}/`);
  return (response as { data: CarRental }).data;
};

export const getCarRentalBySlug = async (slug: string) => {
  const response = await apiClient.get(`/car-rentals/car-rentals/${slug}/`);
  return (response as { data: CarRental }).data;
};

export const getCarRentalCategories = async () => {
  const response = await apiClient.get('/car-rentals/categories/');
  return (response as { data: CarRentalCategory[] }).data;
};

export const getCarRentalOptions = async () => {
  const response = await apiClient.get('/car-rentals/options/');
  return (response as { data: CarRentalOption[] }).data;
};

export const getCarRentalLocations = async () => {
  const response = await apiClient.get('/car-rentals/locations/');
  return (response as { data: CarRentalLocation[] }).data;
};

export const searchCarRentals = async (params: CarRentalSearchParams) => {
  const response = await apiClient.get('/car-rentals/car-rentals/search/', { params });
  return (response as { data: { count: number; results: CarRental[] } }).data;
};

export const getFeaturedCarRentals = async () => {
  const response = await apiClient.get('/car-rentals/car-rentals/featured/');
  return (response as { data: { results: CarRental[] } }).data;
};

export const getPopularCarRentals = async () => {
  const response = await apiClient.get('/car-rentals/car-rentals/popular/');
  return (response as { data: { results: CarRental[] } }).data;
};

export const checkCarRentalAvailability = async (id: string, params: CarRentalAvailabilityCheck) => {
  const response = await apiClient.post(`/car-rentals/car-rentals/${id}/check-availability/`, params);
  return (response as { data: CarRentalAvailabilityResponse }).data;
};

export const checkCarRentalAvailabilityBySlug = async (slug: string, params: CarRentalAvailabilityCheck) => {
  const response = await apiClient.post(`/car-rentals/car-rentals/${slug}/check-availability/`, params);
  return (response as { data: CarRentalAvailabilityResponse }).data;
};

export const getCarRentalAvailabilityCalendar = async (id: string, params?: {
  month?: number;
  year?: number;
}) => {
  const response = await apiClient.get(`/car-rentals/car-rentals/${id}/availability-calendar/`, { params });
  return (response as { data: { [date: string]: { available: boolean; price?: number } } }).data;
};

export const getCarRentalOptionsForCar = async (slug: string) => {
  const response = await apiClient.get(`/car-rentals/car-rentals/${slug}/options/`);
  return (response as { data: CarRentalOption[] }).data;
};

export const createCarRentalBooking = async (params: CarRentalBookingParams) => {
  const response = await apiClient.post('/car-rentals/bookings/', params);
  return (response as { data: { id: string } }).data;
};

export const getCarRentalFilters = async () => {
  const response = await apiClient.get('/car-rentals/filters/');
  return (response as { data: {
    categories: CarRentalCategory[];
    brands: string[];
    cities: string[];
    countries: string[];
    fuel_types: string[];
    transmissions: string[];
    price_range: { min: number; max: number };
    seat_range: { min: number; max: number };
  } }).data;
};
