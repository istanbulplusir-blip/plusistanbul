/**
 * SWR hooks for Car Rental data management.
 */

import useSWR, { SWRConfiguration, mutate } from 'swr';
import { useCallback } from 'react';
import * as carRentalsApi from '../api/car-rentals';
import type { CarRentalLocation } from '../types/car-rentals';

// Car Rentals List
export const useCarRentals = (
  params?: {
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
  },
  config?: SWRConfiguration
) => {
  const key = params ? ['car-rentals', params] : 'car-rentals';
  
  return useSWR<{ count: number; next: string | null; previous: string | null; results: carRentalsApi.CarRental[] }>(
    key,
    () => carRentalsApi.getCarRentals(params),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Car Rental by ID
export const useCarRental = (
  id: string,
  config?: SWRConfiguration
) => {
  return useSWR<carRentalsApi.CarRental>(
    id ? ['car-rental', id] : null,
    () => carRentalsApi.getCarRental(id),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Car Rental by Slug
export const useCarRentalBySlug = (
  slug: string,
  config?: SWRConfiguration
) => {
  return useSWR<carRentalsApi.CarRental>(
    slug ? ['car-rental-slug', slug] : null,
    () => carRentalsApi.getCarRentalBySlug(slug),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Categories
export const useCarRentalCategories = (config?: SWRConfiguration) => {
  return useSWR<carRentalsApi.CarRentalCategory[]>(
    'car-rental-categories',
    carRentalsApi.getCarRentalCategories,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Options
export const useCarRentalOptions = (config?: SWRConfiguration) => {
  return useSWR<carRentalsApi.CarRentalOption[]>(
    'car-rental-options',
    carRentalsApi.getCarRentalOptions,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Locations
export const useCarRentalLocations = (config?: SWRConfiguration) => {
  return useSWR<CarRentalLocation[]>(
    'car-rental-locations',
    carRentalsApi.getCarRentalLocations,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Featured Car Rentals
export const useFeaturedCarRentals = (config?: SWRConfiguration) => {
  return useSWR<{ results: carRentalsApi.CarRental[] }>(
    'featured-car-rentals',
    carRentalsApi.getFeaturedCarRentals,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Popular Car Rentals
export const usePopularCarRentals = (config?: SWRConfiguration) => {
  return useSWR<{ results: carRentalsApi.CarRental[] }>(
    'popular-car-rentals',
    carRentalsApi.getPopularCarRentals,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Search Car Rentals
export const useCarRentalSearch = (
  params: carRentalsApi.CarRentalSearchParams,
  config?: SWRConfiguration
) => {
  const key = ['car-rental-search', params];
  
  return useSWR<{ count: number; results: carRentalsApi.CarRental[] }>(
    key,
    () => carRentalsApi.searchCarRentals(params),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Availability Check
export const useCarRentalAvailability = (
  id: string,
  params: carRentalsApi.CarRentalAvailabilityCheck,
  config?: SWRConfiguration
) => {
  const key = id && params.pickup_date && params.dropoff_date 
    ? ['car-rental-availability', id, params] 
    : null;
  
  return useSWR<carRentalsApi.CarRentalAvailabilityResponse>(
    key,
    () => carRentalsApi.checkCarRentalAvailability(id, params),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Availability Calendar
export const useCarRentalAvailabilityCalendar = (
  id: string,
  params?: { month?: number; year?: number },
  config?: SWRConfiguration
) => {
  const key = id ? ['car-rental-availability-calendar', id, params] : null;
  
  return useSWR<{ [date: string]: { available: boolean; price?: number } }>(
    key,
    () => carRentalsApi.getCarRentalAvailabilityCalendar(id, params),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Car Rental Options for specific car
export const useCarRentalOptionsForCar = (
  slug: string,
  config?: SWRConfiguration
) => {
  return useSWR<carRentalsApi.CarRentalOption[]>(
    slug ? ['car-rental-options', slug] : null,
    () => carRentalsApi.getCarRentalOptionsForCar(slug),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Filters
export const useCarRentalFilters = (config?: SWRConfiguration) => {
  return useSWR<{
    categories: carRentalsApi.CarRentalCategory[];
    brands: string[];
    cities: string[];
    countries: string[];
    fuel_types: string[];
    transmissions: string[];
    price_range: { min: number; max: number };
    seat_range: { min: number; max: number };
  }>(
    'car-rental-filters',
    carRentalsApi.getCarRentalFilters,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      ...config
    }
  );
};

// Mutations
export const useCarRentalMutations = () => {
  const mutateCarRentals = useCallback(() => {
    mutate('car-rentals');
  }, []);

  const mutateCarRental = useCallback((id: string) => {
    mutate(['car-rental', id]);
  }, []);

  const mutateCarRentalBySlug = useCallback((slug: string) => {
    mutate(['car-rental-slug', slug]);
  }, []);

  const mutateFeaturedCarRentals = useCallback(() => {
    mutate('featured-car-rentals');
  }, []);

  const mutatePopularCarRentals = useCallback(() => {
    mutate('popular-car-rentals');
  }, []);

  return {
    mutateCarRentals,
    mutateCarRental,
    mutateCarRentalBySlug,
    mutateFeaturedCarRentals,
    mutatePopularCarRentals,
  };
};
