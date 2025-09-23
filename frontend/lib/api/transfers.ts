/**
 * Transfer API functions for Peykan Tourism Platform
 */

import { apiClient } from './client';
import { TransferLocation } from '../types/api';

// Transfer Route interface
export interface TransferRoute {
  id: string;
  name: string;
  description: string;
  origin: string;
  destination: string;
  slug: string;
  distance_km: number;
  estimated_duration: number;
  estimated_duration_minutes?: number;
  is_popular: boolean;
  is_active: boolean;
  peak_hour_surcharge?: string;
  midnight_surcharge?: string;
  round_trip_discount_enabled?: boolean;
  round_trip_discount_percentage?: string;
  business_hours_start?: number;
  business_hours_end?: number;
  cancellation_hours?: number;
  refund_percentage?: number;
  cancellation_policies?: Array<{
  id: string;
  name: string;
  description: string;
    cancellation_hours: number;
    hours_before: number;
    refund_percentage: number;
  is_active: boolean;
  }>;
  created_at: string;
  updated_at: string;
  pricing: Array<{
    id: string;
    vehicle_type: string;
    vehicle_name: string;
    vehicle_description?: string;
    base_price: number;
    currency: string;
    max_passengers: number;
    max_luggage: number;
    features: string[];
    amenities: string[];
  }>;
  origin_location?: TransferLocation;
  destination_location?: TransferLocation;
}

// Transfer Locations API
export const getTransferLocations = async (params?: {
  city?: string;
  country?: string;
  location_type?: string;
  is_popular?: boolean;
  search?: string;
}): Promise<{ results: TransferLocation[]; count: number }> => {
  const response = await apiClient.get('/transfers/locations/', { params });
  return (response as { data: { results: TransferLocation[]; count: number } }).data;
};

export const getPopularTransferLocations = async (): Promise<TransferLocation[]> => {
  const response = await apiClient.get('/transfers/locations/popular/');
  return (response as { data: TransferLocation[] }).data;
};

export const searchTransferLocationsByCoordinates = async (params: {
  latitude: number;
  longitude: number;
  radius_km?: number;
}): Promise<TransferLocation[]> => {
  const response = await apiClient.post('/transfers/locations/search_by_coordinates/', params);
  return (response as { data: TransferLocation[] }).data;
};

// Transfer Routes API
export const getTransferRoutes = async (params?: {
  origin?: string;
  destination?: string;
  is_popular?: boolean;
  search?: string;
}): Promise<{ results: TransferRoute[]; count: number }> => {
  const response = await apiClient.get('/transfers/routes/', { params });
  return (response as { data: { results: TransferRoute[]; count: number } }).data;
};

export const getTransferRouteById = async (id: string): Promise<TransferRoute> => {
  const response = await apiClient.get(`/transfers/routes/${id}/`);
  return (response as { data: TransferRoute }).data;
};

export const getTransferRouteBySlug = async (slug: string): Promise<TransferRoute> => {
  const response = await apiClient.get(`/transfers/routes/by-slug/${slug}/`);
  return (response as { data: TransferRoute }).data;
};

export const getPopularTransferRoutes = async (): Promise<TransferRoute[]> => {
  const response = await apiClient.get('/transfers/routes/popular/');
  return (response as { data: TransferRoute[] }).data;
};

export const getAvailableTransferRoutes = async (): Promise<TransferRoute[]> => {
  const response = await apiClient.get('/transfers/routes/available_routes/');
  return (response as { data: TransferRoute[] }).data;
};

// Transfer Pricing API
export interface TransferPriceCalculationRequest {
  route_id?: string;
  origin_location_id?: string;
  destination_location_id?: string;
  vehicle_type: string;
  trip_type?: 'one_way' | 'round_trip';
  booking_time: string;
  return_time?: string;
  selected_options?: Array<{ id: string; quantity?: number }>;
}

export interface TransferPriceCalculationResponse {
  price_breakdown: {
    base_price: number;
    outbound_surcharge: number;
    return_surcharge: number;
    outbound_price: number;
    return_price: number;
    round_trip_discount: number;
    options_total: number;
    subtotal: number;
    final_price: number;
    currency: string;
    options_breakdown: Array<{ id: string; name: string; price: number }>;
    pricing_type: string;
    calculation_method: string;
  };
  final_price: number;
  base_price: number;
  price_breakdown_normalized: {
    base_price: number;
    modifiers: {
      outbound_surcharge: number;
      return_surcharge: number;
    round_trip_discount: number;
    };
    options_total: number;
    fees_total: number;
    taxes_total: number;
    subtotal: number;
    final_price: number;
    currency: string;
  };
  trip_info: {
    vehicle_type: string;
    is_round_trip: boolean;
    booking_time: string;
    return_time?: string;
  };
  route_info: {
    origin: string;
    destination: string;
    name: string;
  };
  time_info: {
    booking_hour: number;
    time_category: string;
    surcharge_percentage: number;
  };
  location_info?: {
    origin: {
      id: string;
      name: string;
      city: string;
      country: string;
      coordinates: {
        lat: number;
        lng: number;
      };
    };
    destination: {
      id: string;
      name: string;
      city: string;
      country: string;
      coordinates: {
        lat: number;
        lng: number;
      };
    };
  };
}

export const calculateTransferPrice = async (
  routeId: string,
  request: TransferPriceCalculationRequest
): Promise<TransferPriceCalculationResponse> => {
  const response = await apiClient.post(`/transfers/routes/${routeId}/calculate_price/`, request);
  return (response as { data: TransferPriceCalculationResponse }).data;
};


// Reverse geocoding API
export const reverseGeocode = async (lat: number, lng: number) => {
  const response = await apiClient.post('/transfers/locations/reverse_geocode/', { lat, lng });
  return (response as { data: { name: string; address: string; city: string; country: string; location_type: string; location_type_display?: string; description?: string } }).data;
};

// Route availability check API
export const checkRouteAvailability = async (params: {
  origin_id?: string;
  destination_id?: string;
  origin_name?: string;
  destination_name?: string;
}) => {
  const response = await apiClient.post('/transfers/locations/check_route_availability/', params);
  return (response as { data: { route_exists: boolean; route?: TransferRoute } }).data;
};

// Transfer Options API
export interface TransferOption {
  id: string;
  name: string;
  description: string;
  option_type: string;
  option_type_display: string;
  price_type: 'fixed' | 'percentage';
  price_type_display: string;
  price: number;
  price_percentage: number;
  max_quantity?: number;
  is_active: boolean;
  created_at: string;
  route?: string;
  vehicle_type?: string;
}

export const getTransferOptions = async (params?: {
  option_type?: string;
  route?: string;
  vehicle_type?: string;
  search?: string;
}): Promise<TransferOption[]> => {
  const response = await apiClient.get('/transfers/options/', { params });
  const responseData = (response as { data: { results: TransferOption[] } }).data;
  return responseData.results || [];
};

// Transfer Bookings API
export interface TransferBookingRequest {
  route_id: string;
  vehicle_type: string;
  trip_type: 'one_way' | 'round_trip';
  outbound_date: string;
  outbound_time: string;
  return_date?: string;
  return_time?: string;
  passenger_count: number;
  luggage_count: number;
  pickup_address: string;
  pickup_instructions?: string;
  dropoff_address: string;
  dropoff_instructions?: string;
  contact_name: string;
  contact_phone: string;
  selected_options?: Array<{ id: string; quantity?: number }>;
  special_requirements?: string;
  pricing_breakdown?: TransferPriceCalculationResponse;
  final_price?: number;
}

export interface TransferBooking {
  id: string;
  booking_reference: string;
  route: TransferRoute;
  pricing: {
    vehicle_type: string;
    vehicle_name: string;
    base_price: number;
    currency: string;
  };
  trip_type: 'one_way' | 'round_trip';
  trip_type_display: string;
  outbound_date: string;
  outbound_time: string;
  return_date?: string;
  return_time?: string;
  passenger_count: number;
  luggage_count: number;
  pickup_address: string;
  pickup_instructions: string;
  dropoff_address: string;
  dropoff_instructions: string;
  contact_name: string;
  contact_phone: string;
  outbound_price: number;
  return_price: number;
  round_trip_discount: number;
  options_total: number;
  final_price: number;
  selected_options: Array<{ id: string }>;
  special_requirements: string;
  status: string;
  created_at: string;
}

export const createTransferBooking = async (request: TransferBookingRequest): Promise<TransferBooking> => {
  const response = await apiClient.post('/transfers/bookings/', request);
  return (response as { data: TransferBooking }).data;
};

export const getTransferBookings = async (): Promise<{ results: TransferBooking[]; count: number }> => {
  const response = await apiClient.get('/transfers/bookings/');
  return (response as { data: { results: TransferBooking[]; count: number } }).data;
};

export const getTransferBookingById = async (id: string): Promise<TransferBooking> => {
  const response = await apiClient.get(`/transfers/bookings/${id}/`);
  return (response as { data: TransferBooking }).data;
};

export const cancelTransferBooking = async (id: string): Promise<TransferBooking> => {
  const response = await apiClient.post(`/transfers/bookings/${id}/cancel/`);
  return (response as { data: TransferBooking }).data;
};

export const getUpcomingTransferBookings = async (): Promise<TransferBooking[]> => {
  const response = await apiClient.get('/transfers/bookings/upcoming/');
  return (response as { data: TransferBooking[] }).data;
};

export const getTransferBookingHistory = async (): Promise<TransferBooking[]> => {
  const response = await apiClient.get('/transfers/bookings/history/');
  return (response as { data: TransferBooking[] }).data;
};

// Legacy API functions for backward compatibility
export const getTransferRoute = async (slug: string): Promise<TransferRoute> => {
  return getTransferRouteBySlug(slug);
};

export const getTransfers = async (params?: {
  origin?: string;
  destination?: string;
  is_popular?: boolean;
  search?: string;
}): Promise<{ results: TransferRoute[]; count: number }> => {
  return getTransferRoutes(params);
};

export const searchTransfers = async (params: {
  origin?: string;
  destination?: string;
  search?: string;
}): Promise<TransferRoute[]> => {
  const response = await getTransferRoutes(params);
  return response.results;
};

// Cart operations
export interface CartTransferItem {
  id: string;
  route_id: string;
  vehicle_type: string;
  trip_type: 'one_way' | 'round_trip';
  outbound_date: string;
  outbound_time: string;
  return_date?: string;
  return_time?: string;
  passenger_count: number;
  luggage_count: number;
  pickup_address: string;
  dropoff_address: string;
  selected_options?: Array<{ id: string }>;
  price: number;
  currency: string;
}

export const addTransferToCart = async (data: {
  route_id: string;
  vehicle_type: string;
  trip_type: 'one_way' | 'round_trip';
  outbound_date: string;
  outbound_time: string;
  return_date?: string;
  return_time?: string;
  passenger_count: number;
  luggage_count: number;
  pickup_address: string;
  dropoff_address: string;
  contact_name?: string;
  contact_phone?: string;
  special_requirements?: string;
  selected_options?: Array<{ id: string }>;
}): Promise<CartTransferItem> => {
  // Transform data to match backend cart format
  const cartData = {
    product_type: 'transfer',
    product_id: data.route_id,
    variant_id: data.vehicle_type,
    quantity: 1, // Transfers are per vehicle, not per passenger
    booking_date: data.outbound_date,
    booking_time: data.outbound_time,
    selected_options: data.selected_options || [],
    pricing_breakdown: data.pricing_breakdown,
    final_price: data.final_price,
    booking_data: {
      trip_type: data.trip_type,
      return_date: data.return_date,
      return_time: data.return_time,
      passenger_count: data.passenger_count,
      luggage_count: data.luggage_count,
      pickup_address: data.pickup_address,
      dropoff_address: data.dropoff_address,
      contact_name: data.contact_name,
      contact_phone: data.contact_phone,
      special_requirements: data.special_requirements,
    },
    special_requests: data.special_requirements || '',
  };

  // Use the general cart/add/ endpoint like tours do
  const response = await apiClient.post('/cart/add/', cartData);
  return (response as { data: CartTransferItem }).data;
};

export const removeTransferFromCart = async (itemId: string): Promise<{ success: boolean }> => {
  const response = await apiClient.delete(`/cart/items/${itemId}/remove/`);
  return (response as { data: { success: boolean } }).data;
};

export const updateTransferInCart = async (itemId: string, data: Partial<CartTransferItem>): Promise<CartTransferItem> => {
  const response = await apiClient.patch(`/cart/items/${itemId}/`, data);
  return (response as { data: CartTransferItem }).data;
};

export const getTransferCartItems = async (): Promise<CartTransferItem[]> => {
  const response = await apiClient.get('/cart/');
  return (response as { data: { items: CartTransferItem[] } }).data.items.filter(item => item.product_type === 'transfer');
};

// Additional API functions for backward compatibility
export const getTransferBySlug = async (slug: string): Promise<TransferRoute> => {
  return getTransferRouteBySlug(slug);
};

export const getTransferById = async (id: string): Promise<TransferRoute> => {
  return getTransferRouteById(id);
};

export interface TransferSchedule {
  id: string;
  time: string;
  vehicle_type: string;
  available: boolean;
  price: number;
}

export const getTransferSchedules = async (routeId: string): Promise<TransferSchedule[]> => {
  const response = await apiClient.get(`/transfers/routes/${routeId}/schedules/`);
  return (response as { data: TransferSchedule[] }).data;
};

export interface TransferAvailability {
  date: string;
  vehicle_types: {
    [key: string]: {
      available: boolean;
      price: number;
      schedules: TransferSchedule[];
    };
  };
}

export const getTransferAvailability = async (params: {
  route_id: string;
  date: string;
  vehicle_type?: string;
}): Promise<TransferAvailability> => {
  const response = await apiClient.get('/transfers/availability/', { params });
  return (response as { data: TransferAvailability }).data;
};

export interface TransferFilters {
  origins: string[];
  destinations: string[];
  vehicle_types: string[];
  price_ranges: { min: number; max: number }[];
}

export const getTransferFilters = async (): Promise<TransferFilters> => {
  const response = await apiClient.get('/transfers/filters/');
  return (response as { data: TransferFilters }).data;
};

export interface TransferStats {
  total_routes: number;
  total_bookings: number;
  popular_routes: Array<{
    route: string;
    booking_count: number;
  }>;
}

export const getTransferStats = async (): Promise<TransferStats> => {
  const response = await apiClient.get('/transfers/stats/');
  return (response as { data: TransferStats }).data;
};

export const getRouteByLocations = async (params: {
  origin: string;
  destination: string;
}): Promise<TransferRoute | null> => {
  const response = await getTransferRoutes(params);
  return response.results.length > 0 ? response.results[0] : null;
};

export const bookTransfer = async (data: TransferBookingRequest): Promise<TransferBooking> => {
  return createTransferBooking(data);
}; 