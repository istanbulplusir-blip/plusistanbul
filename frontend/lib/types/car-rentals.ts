/**
 * Type definitions for Car Rentals
 */

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
  city: string;
  country: string;
  pickup_location: string;
  dropoff_location: string;
  image?: string;
  image_url?: string;
  is_featured: boolean;
  is_popular: boolean;
  is_special: boolean;
  is_seasonal: boolean;
  is_available: boolean;
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
  // Rental settings
  weekly_discount_percentage?: number;
  monthly_discount_percentage?: number;
  min_rent_days?: number;
  max_rent_days?: number;
  mileage_limit_per_day?: number;
  advance_booking_days?: number;
  deposit_amount?: number;
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

export interface CarRentalLocation {
  id: string;
  name: string;
  address: string;
  city: string;
  country: string;
  latitude?: number;
  longitude?: number;
  location_type: 'airport' | 'hotel' | 'station' | 'city_center' | 'port' | 'other';
  is_default: boolean;
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

export interface CarRentalFilters {
  categories: CarRentalCategory[];
  brands: string[];
  cities: string[];
  countries: string[];
  fuel_types: string[];
  transmissions: string[];
  price_range: { min: number; max: number };
  seat_range: { min: number; max: number };
}

// Cart integration types
export interface CarRentalCartItem {
  id: string;
  product_type: 'car_rental';
  product_id: string;
  product_title: string;
  product_slug: string;
  booking_date: string;
  booking_time: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  currency: string;
  selected_options: Array<{
    id: string;
    quantity: number;
    price: number;
  }>;
  options_total: number;
  booking_data: {
    car_rental_id: string;
    pickup_date: string;
    dropoff_date: string;
    pickup_time: string;
    dropoff_time: string;
    rental_days: number;
    driver_name: string;
    driver_license: string;
    driver_phone: string;
    driver_email: string;
    additional_drivers: Array<{
      name: string;
      license: string;
      phone: string;
    }>;
    basic_insurance: boolean;
    comprehensive_insurance: boolean;
    special_requirements: string;
  };
}

// Booking step types
export type CarRentalBookingStep = 'car' | 'dates' | 'driver' | 'options' | 'summary';

// Error types
export interface CarRentalBookingError {
  field: string;
  message: string;
  details?: unknown;
  retryable?: boolean;
}
