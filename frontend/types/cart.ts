// Base cart item interface
export interface BaseCartItem {
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
  selected_options: CartItemOption[];
  booking_data: Record<string, unknown>;
  created_at: string;
}

// Cart item option interface
export interface CartItemOption {
  option_id: string;
  name: string;
  price: number;
  quantity: number;
  description?: string;
}

// Tour-specific cart item
export interface TourCartItem extends BaseCartItem {
  product_type: 'tour';
  booking_data: {
    participants: {
      adult: number;
      child: number;
      infant: number;
    };
    schedule_id: string;
    variant_id: string;
    special_requests?: string;
  };
}

// Event-specific cart item
export interface EventCartItem extends BaseCartItem {
  product_type: 'event';
  booking_data: {
    performance_id: string;
    ticket_type_id: string;
    seat_numbers: string[];
    section: string;
    performance_date: string;
    performance_time: string;
  };
}

// Transfer-specific cart item
export interface TransferCartItem extends BaseCartItem {
  product_type: 'transfer';
  booking_data: {
    route_id: string;
    vehicle_type: string;
    trip_type: 'one_way' | 'round_trip';
    outbound_datetime: string;
    return_datetime?: string;
    passenger_count: number;
    luggage_count: number;
    contact_name?: string;
    contact_phone?: string;
  };
}

// Discriminated union type for cart items
export type CartItem = TourCartItem | EventCartItem | TransferCartItem;

// Cart interface
export interface Cart {
  id: string;
  user: string;
  session_id: string;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  total_price: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

// Cart update payload
export interface CartUpdatePayload {
  quantity?: number;
  selected_options?: CartItemOption[];
  booking_data?: Record<string, unknown>;
}

// Cart API response
export interface CartApiResponse {
  success: boolean;
  message?: string;
  error?: string;
  cart?: Cart;
  cart_item?: CartItem;
} 