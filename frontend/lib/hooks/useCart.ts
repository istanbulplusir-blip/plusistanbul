'use client';

// Re-export from UnifiedCartContext for backward compatibility
export { useUnifiedCart as useCart } from '../contexts/UnifiedCartContext';

// Interface for tour-specific cart item
export interface TourCartItem {
  id: string;
  type: 'tour';
  title: string;
  price: number;
  currency: string;
  image?: string;
  duration?: string;
  location?: string;
  
  // Tour-specific fields
  tour_id: string;
  schedule_id: string;
  variant_id: string;
  participants: {
    adult: number;
    child: number;
    infant: number;
  };
  selected_options: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
  
  // Calculated fields
  total_participants: number;
  unit_price: number;
  options_total: number;
  subtotal: number;
}

// Interface for event cart items
export interface EventCartItem {
  id: string;
  type: 'event';
  title: string;
  price: number;
  quantity: number;
  currency: string;
  date?: string;
  time?: string;
  variant?: string;
  variant_name?: string;
  options?: Record<string, unknown>;
  special_requests?: string;
  image?: string;
  duration?: string;
  location?: string;
  
  // Backend-aligned fields for detailed event data
  booking_data?: {
    performance_id?: string;
    ticket_type_id?: string;
    performance_date?: string;
    performance_time?: string;
    venue_name?: string;
    venue_address?: string;
    venue_city?: string;
    venue_country?: string;
    seats?: Array<{
      seat_id: string;
      seat_number: string;
      row_number: string;
      section: string;
      price: number;
      ticket_type?: string;
    }>;
    section?: string;
    selected_options?: Array<{
      option_id: string;
      quantity: number;
      name?: string;
      price?: number;
    }>;
    special_requests?: string;
  };
  selected_options?: Array<{
    option_id: string;
    quantity: number;
    name?: string;
    price?: number;
  }>;
}

// Interface for transfer cart items
export interface TransferCartItem {
  id: string;
  type: 'transfer';
  title: string;
  price: number;
  quantity: number;
  currency: string;
  slug: string;
  
  // Backend-aligned fields
  route_id: string;
  route_data: {
    id: string;
    name: string;
    name_display: string;
    origin: string;
    destination: string;
    distance_km: number;
    estimated_duration_minutes: number;
  };
  vehicle_type: string;
  trip_type: 'one_way' | 'round_trip';
  outbound_datetime: string;
  return_datetime?: string;
  passenger_count: number;
  luggage_count: number;
  contact_name: string;
  contact_phone: string;
  selected_options: Array<{
    option_id: string;
    quantity: number;
    name?: string;
    description?: string;
    price?: number;
  }>;
  special_requirements?: string;
  
  // Pricing breakdown from backend
  pricing_breakdown: {
    base_price: number;
    outbound_surcharge: number;
    return_surcharge: number;
    round_trip_discount: number;
    options_total: number;
    final_price: number;
    currency: string;
  } | null;
  
  // UI display fields
  image?: string;
  duration?: string;
  location?: string;
}

export type CartItem = TourCartItem | EventCartItem | TransferCartItem; 