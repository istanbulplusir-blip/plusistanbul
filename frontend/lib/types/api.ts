/**
 * TypeScript types for API responses and requests.
 */

// Base types
export interface BaseModel {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// User types
export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_phone_verified: boolean;
  is_email_verified: boolean;
  phone_number?: string;
  preferred_language: string;
  preferred_currency: string;
  created_at?: string;
  updated_at?: string;
}

export interface UserProfile extends BaseModel {
  avatar?: string | null;
  bio?: string;
  address?: string;
  city?: string;
  country?: string;
  postal_code?: string;
  website?: string;
  facebook?: string;
  instagram?: string;
  twitter?: string;
  newsletter_subscription: boolean;
  marketing_emails: boolean;
}

// Tour types
export interface Tour extends BaseModel {
  slug: string;
  title: string;
  description: string;
  short_description: string;
  highlights: string;
  included: string;
  excluded: string;
  image: string;
  gallery_images: {
    id: string;
    image: string;
    image_url: string;
    title: string;
    description: string;
    order: number;
    is_active: boolean;
  }[];
  base_price: number;
  currency: string;
  duration_days: number;
  duration_nights: number;
  max_group_size: number;
  min_age: number;
  difficulty_level: string;
  category: TourCategory;
  destinations: TourDestination[];
  schedules: TourSchedule[];
  variants: TourVariant[];
  options: TourOption[];
  reviews: TourReview[];
  average_rating: number;
  review_count: number;
  is_active: boolean;
}

export interface TourCategory extends BaseModel {
  name: string;
  description: string;
  image: string;
  is_active: boolean;
}

export interface TourDestination extends BaseModel {
  name: string;
  description: string;
  image: string;
  country: string;
  city: string;
  coordinates: {
    lat: number;
    lng: number;
  };
}

export interface TourSchedule extends BaseModel {
  date: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
  max_capacity: number;
  current_capacity: number;
  available_capacity: number;
  is_full: boolean;
  cutoff_datetime: string;
  variant_capacities: Record<string, { 
    total: number; 
    booked: number; 
    available: number; 
  }>;
}

export interface TourVariant extends BaseModel {
  name: string;
  description: string;
  price_modifier: number;
  capacity: number;
  is_active: boolean;
  variant_type: string;
  benefits: string[];
}

export interface TourOption extends BaseModel {
  name: string;
  description: string;
  price: number;
  currency: string;
  option_type: string;
  is_available: boolean;
  max_quantity: number;
}

export interface TourReview extends BaseModel {
  rating: number;
  title: string;
  comment: string;
  is_verified: boolean;
  is_helpful: number;
  user_name: string;
}

export type TourListResponse = PaginatedResponse<Tour>;
export type TourDetailResponse = Tour;

export interface TourSearchParams {
  query?: string;
  category?: string;
  destination?: string;
  min_price?: number;
  max_price?: number;
  duration_min?: number;
  duration_max?: number;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
}

export interface TourBookingRequest {
  tour_id: string;
  schedule_id: string;
  variant_id: string;
  passengers: {
    adults: number;
    children: number;
    infants: number;
  };
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requirements?: string;
}

// Event types
export interface Event extends BaseModel {
  slug: string;
  title: string;
  description: string;
  short_description: string;
  highlights: string;
  rules: string;
  required_items: string;
  image: string;
  gallery_images: {
    id: string;
    image: string;
    image_url: string;
    title: string;
    description: string;
    order: number;
    is_active: boolean;
  }[];
  style: string;
  door_open_time: string;
  start_time: string;
  end_time: string;
  age_restriction?: number;
  category: EventCategory;
  venue: Venue;
  artists: Artist[];
  ticket_types: TicketType[];
  options: EventOption[];
  performances?: EventPerformance[];
  reviews: EventReview[];
  average_rating: number;
  review_count: number;
  is_available_today: boolean;
  is_active: boolean;
  is_featured?: boolean;
  is_popular?: boolean;
  min_price?: number;
  max_price?: number;
  
  // Enhanced fields for new frontend
  available_performances?: EventPerformance[];
  pricing_summary: Record<string, {
    ticket_type_name: string;
    ticket_type_code: string;
    base_price: number;
    modified_price: number;
    price_modifier: number;
    capacity: number;
    benefits: string[];
    age_min?: number;
    age_max?: number;
  }>;
  booking_info: {
    age_restriction?: number;
    door_open_time?: string;
    start_time?: string;
    end_time?: string;
    style: string;
    venue_capacity: number;
    venue_facilities: string[];
  };
  
  // New enhanced fields
  performance_calendar: EventPerformanceCalendar[];
  seat_map_info: {
    venue_name: string;
    total_capacity: number;
    available_sections: string[];
    has_seat_map: boolean;
    facilities: string[];
  };
  available_options: Record<string, EventOption[]>;
  capacity_overview: {
    total_performances: number;
    available_performances: number;
    total_capacity: number;
    available_capacity: number;
    overall_occupancy_rate: number;
  };
}

export interface EventPerformanceCalendar {
  id: string;
  date: string;
  start_time: string;
  end_time: string;
  is_special: boolean;
  capacity_summary: {
    total_capacity: number;
    available_capacity: number;
    occupancy_rate: number;
  };
  booking_cutoff: string;
}

export interface EventPerformance extends BaseModel {
  date: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
  max_capacity: number;
  current_capacity: number;
  available_capacity: number;
  is_full: boolean;
  is_special: boolean;
  ticket_capacities: Record<string, number>;
  sections: EventSection[];
  cutoff_datetime: string;
  
  // Enhanced fields
  pricing_matrix: Record<string, Record<string, {
    ticket_type_name: string;
    base_price: number;
    price_modifier: number;
    final_price: number;
    available_capacity: number;
    benefits: string[];
  }>>;
  
  seat_availability: Record<string, {
    total_capacity: number;
    available_capacity: number;
    reserved_capacity: number;
    sold_capacity: number;
    is_wheelchair_accessible: boolean;
    is_premium: boolean;
  }>;
  
  // Legacy fields for compatibility
  available_seats?: Record<string, Array<{
    id: string;
    seat_number: string;
    row_number: string;
    section: string;
    price: number;
    currency: string;
    is_wheelchair_accessible: boolean;
    is_premium: boolean;
  }>>;
  
  sections_summary?: Record<string, Record<string, {
    section_name: string;
    total_seats: number;
    min_price: number;
    max_price: number;
    has_premium: boolean;
  }>>;
  
  ticket_availability?: Record<string, {
    ticket_type_name: string;
    available_count: number;
    total_capacity: number;
    price_modifier: number;
  }>;

  // Add min_price for frontend
  min_price: number;
}

export interface EventSection extends BaseModel {
  name: string;
  description: string;
  total_capacity: number;
  available_capacity: number;
  reserved_capacity: number;
  sold_capacity: number;
  base_price: number;
  currency: string;
  is_wheelchair_accessible: boolean;
  is_premium: boolean;
  occupancy_rate: number;
  is_full: boolean;
  ticket_types: SectionTicketType[];
}

export interface SectionTicketType extends BaseModel {
  section: EventSection;
  ticket_type: TicketType;
  allocated_capacity: number;
  available_capacity: number;
  reserved_capacity: number;
  sold_capacity: number;
  price_modifier: number;
  final_price: number;
}

export interface TicketType extends BaseModel {
  name: string;
  description: string;
  price_modifier: number;
  capacity: number;
  is_active: boolean;
  ticket_type: string;
  benefits: string[];
  age_min?: number;
  age_max?: number;
}

export interface EventOption extends BaseModel {
  name: string;
  description: string;
  price: number;
  currency: string;
  option_type: string;
  is_available: boolean;
  max_quantity: number;
}

// Enhanced booking and pricing types
export interface EventBookingRequest {
  event_id: string;
  performance_id: string;
  section_name: string;
  ticket_type_id: string;
  quantity: number;
  selected_seats?: string[];
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  discount_code?: string;
  special_requirements?: string;
}

export interface EventPricingRequest {
  performance_id: string;
  section_name: string;
  ticket_type_id: string;
  quantity: number;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  discount_code?: string;
}

export interface EventPricingBreakdown {
  base_price: number;
  price_modifier: number;
  unit_price: number;
  quantity: number;
  subtotal: number;
  pricing_type?: 'event' | 'tour' | 'transfer'; // Add this to support different product types
  trip_type?: 'one_way' | 'round_trip'; // Add this for transfer-specific logic
  options: Array<{
    option_id: string;
    name: string;
    type: string;
    price: number;
    quantity: number;
    total: number;
  }>;
  options_total: number;
  discounts: Array<{
    type: string;
    name: string;
    amount: number;
    percentage?: number;
  }>;
  discount_total: number;
  fees: Array<{
    name: string;
    type: string;
    amount: number;
  }>;
  fees_total: number;
  taxes: Array<{
    name: string;
    type: string;
    amount: number;
  }>;
  taxes_total: number;
  final_price: number;
  
  // Transfer-specific fields
  outbound_surcharge?: number;
  outbound_surcharge_percentage?: number;
  return_surcharge?: number;
  return_surcharge_percentage?: number;
  round_trip_discount?: number;
  round_trip_discount_percentage?: number;
}

export interface EventSeatReservation {
  performance_id: string;
  section_name: string;
  ticket_type_id: string;
  quantity: number;
}

export interface EventSeatMap {
  event_id: string;
  performance_id: string;
  seat_map: Record<string, Array<{
    id: string;
    seat_number: string;
    row_number: string;
    price: number;
    currency: string;
    status: 'available' | 'reserved' | 'sold' | 'blocked';
    is_wheelchair_accessible: boolean;
    is_premium: boolean;
  }>>;
  venue_info: {
    name: string;
    total_capacity: number;
    facilities: string[];
  };
}

export interface EventAvailabilityCalendar {
  event_id: string;
  calendar: Array<{
    date: string;
    performance_id: string;
    start_time: string;
    end_time: string;
    is_special: boolean;
    availability: {
      total_capacity: number;
      available_capacity: number;
      occupancy_rate: number;
    };
    booking_cutoff: string;
  }>;
}

// Enhanced cart item for events
export interface EventCartItem {
  id: string;
  event_id: string;
  performance_id: string;
  section_name: string;
  ticket_type_id: string;
  title: string;
  image: string;
  date: string;
  time: string;
  location: string;
  variant: string;
  quantity: number;
  price: number;
  currency: string;
  selected_seats?: string[];
  selected_options?: Record<string, unknown>;
  pricing_breakdown?: EventPricingBreakdown;
  reservation_expires_at?: string;
}

export interface EventCategory extends BaseModel {
  name: string;
  description: string;
  image: string;
  icon: string;
  color: string;
  is_active: boolean;
}

export interface Venue extends BaseModel {
  name: string;
  description: string;
  address: string;
  image: string;
  website?: string;
  city: string;
  country: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  total_capacity: number;
  facilities: string[];
}

export interface Artist extends BaseModel {
  name: string;
  bio: string;
  image: string;
  website?: string;
  social_media: Record<string, string>;
}

// Legacy TicketType and EventOption - merged with enhanced versions above

export interface EventReview extends BaseModel {
  rating: number;
  title: string;
  comment: string;
  is_verified: boolean;
  is_helpful: number;
  user_name: string;
}

export type EventListResponse = PaginatedResponse<Event>;
export type EventDetailResponse = Event;

export interface EventSearchParams {
  query?: string;
  category?: string;
  venue?: string;
  style?: string;
  min_price?: number;
  max_price?: number;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
}

// Legacy EventBookingRequest - merged with enhanced version above

// Cart types
export interface CartItem extends BaseModel {
  product_type: 'tour' | 'event' | 'transfer';
  product_id: string;
  product_name: string;
  product_image: string;
  variant_id?: string;
  variant_name?: string;
  schedule_id?: string;
  schedule_date?: string;
  schedule_time?: string;
  quantity: number;
  unit_price: number;
  currency: string;
  total_price: number;
  selected_options: Array<{
    option_id: string;
    option_name: string;
    quantity: number;
    unit_price: number;
    total_price: number;
  }>;
  passengers?: {
    adults: number;
    children: number;
    infants: number;
  };
  selected_seats?: string[];
  special_requirements?: string;
}

export interface Cart extends BaseModel {
  user: User;
  items: CartItem[];
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  currency: string;
  expires_at: string;
}

// Order types
export interface Order extends BaseModel {
  order_number: string;
  user: User;
  items: CartItem[];
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  currency: string;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
  customer_info: {
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    address: string;
    city: string;
    country: string;
    postal_code: string;
  };
  special_requirements?: string;
  notes?: string;
}

// Payment types
export interface Payment extends BaseModel {
  order: Order;
  amount: number;
  currency: string;
  payment_method: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  transaction_id?: string;
  gateway_response?: Record<string, unknown>;
}

// Agent types
export interface Agent extends BaseModel {
  user: User;
  company_name: string;
  license_number: string;
  commission_rate: number;
  is_verified: boolean;
  is_active: boolean;
}

export interface AgentCommission {
  id: string;
  created_at: string;
  updated_at?: string;
  agent?: Agent;
  order?: Order;
  commission_amount: number;
  commission_rate: number;
  status: 'pending' | 'approved' | 'paid' | 'rejected' | 'cancelled';
  payment_date?: string;
  notes?: string;
  order_number: string;
  order_amount: number;
  currency: string;
}

export interface AgentCustomer {
  id: string;
  created_at: string;
  updated_at?: string;
  agent?: Agent;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  status: 'active' | 'inactive' | 'suspended';
  total_orders: number;
  total_spent: number;
  currency: string;
  notes?: string;
  name?: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  gender?: 'male' | 'female' | 'other';
  preferred_language?: string;
  preferred_contact_method?: string;
}

// Transfer types
export interface Transfer extends BaseModel {
  slug: string;
  title: string;
  description: string;
  short_description: string;
  image: string;
  gallery_images: {
    id: string;
    image: string;
    image_url: string;
    title: string;
    description: string;
    order: number;
    is_active: boolean;
  }[];
  base_price: number;
  currency: string;
  transfer_type: string;
  vehicle_type: string;
  max_passengers: number;
  duration_minutes: number;
  pickup_locations: TransferLocation[];
  dropoff_locations: TransferLocation[];
  schedules: TransferSchedule[];
  variants: TransferVariant[];
  options: TransferOption[];
  is_active: boolean;
  available_schedules: TransferSchedule[];
}

export interface TransferLocation extends BaseModel {
  name: string;
  description: string;
  address: string;
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  coordinates: {
    lat: number;
    lng: number;
  };
  location_type: 'airport' | 'hotel' | 'station' | 'landmark' | 'custom';
  location_type_display: string;
  is_popular: boolean;
  is_active: boolean;
}

export interface TransferSchedule extends BaseModel {
  date: string;
  time: string;
  is_available: boolean;
  max_capacity: number;
  current_capacity: number;
  available_capacity: number;
  is_full: boolean;
}

export interface TransferVariant extends BaseModel {
  name: string;
  description: string;
  price_modifier: number;
  capacity: number;
  is_active: boolean;
  vehicle_type: string;
  benefits: string[];
}

export interface TransferOption extends BaseModel {
  name: string;
  description: string;
  price: number;
  currency: string;
  option_type: string;
  is_available: boolean;
  max_quantity: number;
}

// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  role?: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user?: User;
  tokens?: {
    access: string;
    refresh: string;
  };
  requires_email_verification?: boolean;
  email?: string;
  email_verification_required?: boolean;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

// Common response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface ErrorResponse {
  detail: string;
  code?: string;
}

export type TransferListResponse = PaginatedResponse<Transfer>;
export interface TransferDetailResponse extends Transfer {
  pricing_summary: Record<string, {
    variant_name: string;
    vehicle_type: string;
    base_price: number;
    modified_price: number;
    price_modifier: number;
    capacity: number;
    max_passengers: number;
    max_luggage: number;
    benefits: string[];
  }>;
  available_schedules: TransferSchedule[];
}

export interface TransferSearchParams {
  query?: string;
  pickup_location?: string;
  dropoff_location?: string;
  transfer_type?: string;
  vehicle_type?: string;
  min_price?: number;
  max_price?: number;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
}

export interface TransferBookingRequest {
  transfer_id: string;
  schedule_id: string;
  variant_id: string;
  pickup_location_id: string;
  dropoff_location_id: string;
  passengers: {
    adults: number;
    children: number;
    infants: number;
  };
  trip_type: 'one_way' | 'round_trip';
  return_date?: string;
  return_time?: string;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requirements?: string;
}

export interface TransferRoute extends BaseModel {
  name: string;
  description: string;
  pickup_location: TransferLocation;
  dropoff_location: TransferLocation;
  transfer_type: string;
  base_price: number;
  currency: string;
  estimated_duration: number;
  distance_km: number;
  is_active: boolean;
}

// Cart API Types
export interface AddToCartPayload {
  product_type: 'tour' | 'event' | 'transfer';
  product_id: string;
  variant_id?: string;
  quantity: number;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
}

export interface UpdateCartItemPayload {
  quantity?: number;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
}

export interface CartItemResponse {
  id: string;
  product_type: 'tour' | 'event' | 'transfer';
  product_id: string;
  product_title: string;
  product_slug: string;
  variant_id?: string;
  variant_name?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  currency: string;
  selected_options: Array<{
    option_id: string;
    quantity: number;
    price: number;
  }>;
  special_requests?: string;
  created_at: string;
}

export interface CartResponse {
  id: string;
  user?: string;
  session_key?: string;
  items: CartItemResponse[];
  total_items: number;
  subtotal: number;
  total_price: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

export interface CartSummaryResponse {
  total_items: number;
  subtotal: number;
  total_price: number;
  currency: string;
  items: CartItemResponse[];
} 

export interface PerformanceSeatsResponse {
  performance_id: string;
  sections: ApiSection[];
  total_count: number;
}

// API Response Types for Event Detail Page
export interface ApiSectionTicketType {
  id: string; // This is SectionTicketType.id
  ticket_type: {  // Nested TicketType object
    id: string;
    name: string;
    description: string;
    benefits: string[];
  };
  allocated_capacity: number;
  available_capacity: number;
  reserved_capacity: number;
  sold_capacity: number;
  price_modifier: number;
  final_price: number;
}

export interface ApiSection {
  id?: string;
  name: string;
  description?: string;
  total_capacity?: number;
  available_capacity?: number;
  reserved_capacity?: number;
  sold_capacity?: number;
  base_price?: number;
  currency?: string;
  is_wheelchair_accessible?: boolean;
  is_premium?: boolean;
  occupancy_rate?: number;
  ticket_types?: ApiSectionTicketType[];
  seats?: ApiSeat[];
  created_at?: string;
  updated_at?: string;
}

export interface ApiSeat {
  id: string;
  seat_number: string;
  row_number: string;
  section?: string;
  price?: number;
  currency?: string;
  is_wheelchair_accessible?: boolean;
  is_premium?: boolean;
  status?: string;
  ticket_type_id?: string;
}

// Simplified interfaces for mapped sections
export interface MappedSectionTicketType {
  id: string;
  section: { id: string; name: string };
  ticket_type: { 
    id: string; 
    name: string; 
    description: string; 
    price_modifier: number;
    capacity: number;
    is_active: boolean;
    ticket_type: string; 
    benefits: string[];
    created_at: string;
    updated_at: string;
  };
  allocated_capacity: number;
  available_capacity: number;
  reserved_capacity: number;
  sold_capacity: number;
  price_modifier: number;
  final_price: number;
  created_at: string;
  updated_at: string;
}

export interface MappedEventSection {
  id: string;
  name: string;
  description: string;
  total_capacity: number;
  available_capacity: number;
  reserved_capacity: number;
  sold_capacity: number;
  base_price: number;
  currency: string;
  is_wheelchair_accessible: boolean;
  is_premium: boolean;
  occupancy_rate: number;
  is_full: boolean;
  ticket_types: MappedSectionTicketType[];
  created_at: string;
  updated_at: string;
} 

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