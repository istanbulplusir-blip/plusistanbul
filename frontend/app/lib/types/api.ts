// API Response Types
export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  status: number;
}

// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'guest' | 'customer' | 'agent' | 'admin';
  is_active: boolean;
  is_phone_verified: boolean;
  is_email_verified: boolean;
  date_joined: string;
  last_login: string | null;
  profile: UserProfile;
}

export interface UserProfile {
  id: string;
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

// Auth Types
export interface AuthResponse {
  message: string;
  user: User;
  tokens?: {
    refresh: string;
    access: string;
  };
  email_verification_required?: boolean;
  email?: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  role?: string;
}

export interface OTPPayload {
  phone?: string;
  email?: string;
  otp_type: 'phone' | 'email' | 'password_reset' | 'login';
}

export interface OTPVerifyPayload extends OTPPayload {
  code: string;
}

export interface PasswordResetPayload {
  email: string;
  code: string;
  new_password: string;
  new_password_confirm: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

// Tour Types
export interface Tour {
  id: string;
  slug: string;
  title: string;
  description: string;
  short_description: string;
  highlights: string;
  itinerary: string;
  included_services: string;
  excluded_services: string;
  important_notes: string;
  image: string;
  gallery: string[];
  base_price: number;
  currency: string;
  duration_hours: number;
  max_participants: number;
  booking_cutoff_hours: number;
  cancellation_hours: number;
  refund_percentage: number;
  cancellation_policies: Array<{
    id: string;
    hours_before: number;
    refund_percentage: number;
    description: string;
    is_active: boolean;
  }>;
  includes_transfer: boolean;
  includes_guide: boolean;
  includes_meal: boolean;
  includes_photographer: boolean;
  category: TourCategory;
  variants: TourVariant[];
  options: TourOption[];
  schedules: TourSchedule[];
  reviews: TourReview[];
  average_rating: number;
  review_count: number;
  is_available_today: boolean;
  is_active: boolean;
  created_at: string;
}

export interface TourCategory {
  id: string;
  name: string;
  description: string;
  image: string;
  is_active: boolean;
}

export interface TourVariant {
  id: string;
  name: string;
  description: string;
  price_modifier: number;
  capacity: number;
  is_active: boolean;
}

export interface TourOption {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  option_type: string;
  is_available: boolean;
  max_quantity?: number;
}

export interface TourSchedule {
  id: string;
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
  max_capacity: number;
  current_capacity: number;
  available_capacity: number;
  is_full: boolean;
  day_of_week: number;
  variant_capacities: Record<string, number>;
}

export interface TourReview {
  id: string;
  rating: number;
  title: string;
  comment: string;
  is_verified: boolean;
  is_helpful: number;
  created_at: string;
  user_name: string;
  // New fields for enhanced functionality
  category?: string;
  status?: 'pending' | 'approved' | 'rejected' | 'flagged';
  moderation_notes?: string;
  moderated_by?: string;
  moderated_at?: string;
  sentiment_score?: number;
  can_edit?: boolean;
  can_delete?: boolean;
  can_report?: boolean;
  can_respond?: boolean;
  responses?: ReviewResponse[];
}

// New interfaces for review management
export interface ReviewStats {
  total_reviews: number;
  average_rating: number;
  rating_distribution: Record<number, number>;
  category_distribution: Record<string, number>;
  recent_reviews: number;
  pending_reviews?: number;
  flagged_reviews?: number;
}

export interface CreateReviewData {
  rating: number;
  title?: string;
  comment: string;
  category?: string;
}

export interface UpdateReviewData {
  rating?: number;
  title?: string;
  comment?: string;
  category?: string;
}

export interface ReviewReportData {
  reason: string;
  description?: string;
}

export interface ReviewResponseData {
  content: string;
  is_public?: boolean;
  is_official?: boolean;
}

export interface ReviewResponse {
  id: string;
  content: string;
  is_public: boolean;
  is_official: boolean;
  created_at: string;
  responder_name: string;
  can_edit?: boolean;
  can_delete?: boolean;
}

export interface TourSearchParams {
  query?: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  min_duration?: number;
  max_duration?: number;
  date_from?: string;
  date_to?: string;
  includes_transfer?: boolean;
  includes_guide?: boolean;
  includes_meal?: boolean;
  sort_by?: string;
}

export interface TourBookingPayload {
  tour_id: string;
  schedule_id: string;
  variant_id?: string;
  quantity: number;
  booking_date: string;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
    price: number;
  }>;
  special_requests?: string;
}

// Cart Types
export interface CartItem {
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

export interface Cart {
  id: string;
  user?: string;
  session_key?: string;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  total_price: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

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
  quantity: number;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
}

// Order Types
export interface OrderItem {
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
  booking_date?: string;
  booking_time?: string;
}

export interface Order {
  id: string;
  order_number: string;
  user: string;
  agent?: string;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
  total_amount: number;
  currency: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  special_requests?: string;
  notes?: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface CreateOrderPayload {
  cart_id: string;
  special_requests?: string;
  agent_id?: string;
}

// Payment Types
export interface PaymentTransaction {
  id: string;
  payment: string;
  transaction_type: 'authorization' | 'capture' | 'refund' | 'void' | 'chargeback';
  amount: number;
  currency: string;
  status: 'pending' | 'success' | 'failed';
  gateway_response: Record<string, unknown>;
  error_code?: string;
  error_message?: string;
  created_at: string;
}

export interface Payment {
  id: string;
  payment_id: string;
  order: string;
  user: string;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'failed' | 'refunded';
  payment_method: string;
  transactions: PaymentTransaction[];
  created_at: string;
  updated_at: string;
}

export interface CreatePaymentPayload {
  order_id: string;
  payment_method: string;
}

// Agent Types
export interface AgentCommission {
  id: string;
  order: string;
  order_number: string;
  order_amount: number;
  commission_rate: number;
  commission_amount: number;
  currency: string;
  status: 'pending' | 'approved' | 'paid' | 'rejected' | 'cancelled';
  status_display: string;
  created_at: string;
  approved_at?: string;
  approved_by?: string;
  rejected_at?: string;
  rejected_by?: string;
  rejection_reason?: string;
  paid_at?: string;
  paid_by?: string;
  payment_method?: string;
  payment_reference?: string;
  notes?: string;
}

export interface Agent {
  id: string;
  user: string;
  username: string;
  email: string;
  agent_code: string;
  commission_rate: number;
  agency_name: string;
  agency_code: string;
  status: 'active' | 'inactive' | 'suspended';
  commissions: AgentCommission[];
  created_at: string;
  updated_at: string;
}

export interface AgentSummary {
  agent_id: string;
  agent_name: string;
  company_name: string;
  commission_rate: number;
  total_customers: number;
  total_orders: number;
  total_commission: number;
  currency: string;
  is_active: boolean;
  is_verified: boolean;
  recent_orders: Array<{
    order_number: string;
    customer_name: string;
    total_amount: number;
    status: string;
    created_at: string;
  }>;
  recent_commissions: Array<{
    id: string;
    order_number: string;
    commission_amount: number;
    status: string;
    created_at: string;
  }>;
}

export interface AgentCustomer {
  id: string;
  agent_customer_id: string;
  name: string;
  email: string;
  phone: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  gender?: 'male' | 'female' | 'other';
  preferred_language: 'fa' | 'en' | 'ar';
  preferred_contact_method: 'email' | 'phone' | 'whatsapp' | 'sms';
  status: 'active' | 'inactive' | 'blocked' | 'vip';
  status_display: string;
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  tier_display: string;
  total_orders: number;
  total_spent: number;
  last_order_date?: string;
  created_at: string;
  is_active: boolean;
  created_by_agent: boolean;
  // New authentication fields
  is_email_verified?: boolean;
  has_logged_in?: boolean;
  last_login_at?: string;
  requires_verification?: boolean;
  credentials_sent?: boolean;
  credentials_sent_at?: string;
  login_count?: number;
}

export interface AgentPricingRule {
  id: string;
  product_type: 'tour' | 'event' | 'transfer' | 'car_rental';
  product_type_display: string;
  pricing_method: 'discount_percentage' | 'fixed_price' | 'markup_percentage' | 'custom_factor';
  pricing_method_display: string;
  discount_percentage?: number;
  fixed_price?: number;
  markup_percentage?: number;
  custom_factor?: number;
  min_price?: number;
  max_price?: number;
  description?: string;
  priority: number;
  created_at: string;
}

export interface AgentBookingData {
  customer_id: string;
  special_requests?: string;
  notes?: string;
}

export interface AgentTourData extends AgentBookingData {
  tour_id: string;
  variant_id: string;
  schedule_id: string;
  booking_date: string;
  booking_time: string;
  participants: {
    adults: number;
    children: number;
    infants: number;
  };
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
}

export interface AgentTransferData extends AgentBookingData {
  route_id: string;
  vehicle_type: string;
  booking_date: string;
  booking_time: string;
  passenger_count: number;
  trip_type?: 'one_way' | 'round_trip';
  return_date?: string;
  return_time?: string;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
}

export interface AgentCarRentalData extends AgentBookingData {
  car_id: string;
  pickup_date: string;
  pickup_time: string;
  dropoff_date: string;
  dropoff_time: string;
  days: number;
  hours?: number;
  include_insurance?: boolean;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
}

export interface AgentEventData extends AgentBookingData {
  event_id: string;
  performance_id: string;
  section: string;
  ticket_type_id: string;
  quantity: number;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
}

export interface AgentPricingPreviewData {
  product_type: 'tour' | 'transfer' | 'car_rental' | 'event';
  tour_id?: string;
  variant_id?: string;
  participants?: {
    adults: number;
    children: number;
    infants: number;
  };
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  route_id?: string;
  vehicle_type?: string;
  passenger_count?: number;
  trip_type?: 'one_way' | 'round_trip';
  hour?: string;
  return_hour?: string;
  car_id?: string;
  days?: number;
  hours?: number;
  include_insurance?: boolean;
}

export interface AgentCustomerStatistics {
  total_customers: number;
  active_customers: number;
  vip_customers: number;
  tier_stats: Record<string, number>;
  status_stats: Record<string, number>;
  language_stats: Record<string, number>;
  contact_stats: Record<string, number>;
  total_spent: number;
  average_spent: number;
  top_customers: Array<{
    id: string;
    name: string;
    total_spent: number;
    total_orders: number;
  }>;
}

export interface AgentCommissionSummary {
  total_commission: number;
  total_orders: number;
  status_stats: Record<string, {
    count: number;
    amount: number;
  }>;
  product_stats: Record<string, {
    count: number;
    amount: number;
  }>;
  period: string;
}

export interface AgentMonthlyCommission {
  year: number;
  month: number;
  total_commission: number;
  total_orders: number;
  pending_commission: number;
  paid_commission: number;
}

export interface AgentTour {
  id: string;
  title: string;
  description: string;
  base_price: number;
  agent_price: number;
  duration: string;
  location: string;
  image: string;
  category: string;
  is_active: boolean;
  variants: Array<{
    id: string;
    name: string;
    description: string;
    base_price: number;
    agent_price: number;
    capacity: number;
    price_modifier: number;
    is_active: boolean;
  }>;
}

export interface AgentTourDetail extends AgentTour {
  variants: Array<{
    id: string;
    name: string;
    description: string;
    base_price: number;
    agent_price: number;
    capacity: number;
    price_modifier: number;
    includes: {
      transfer: boolean;
      guide: boolean;
      meal: boolean;
      photographer: boolean;
      extended_hours: boolean;
      private_transfer: boolean;
      expert_guide: boolean;
      special_meal: boolean;
    };
    is_active: boolean;
  }>;
}

export interface AgentTourAvailableDate {
  date: string;
  available_slots: number;
  variants: Array<{
    id: string;
    name: string;
    description: string;
    base_price: number;
    agent_price: number;
    capacity: number;
    price_modifier: number;
    includes: {
      transfer: boolean;
      guide: boolean;
      meal: boolean;
      photographer: boolean;
      extended_hours: boolean;
      private_transfer: boolean;
      expert_guide: boolean;
      special_meal: boolean;
    };
    is_active: boolean;
  }>;
}

export interface AgentTourOption {
  id: string;
  name: string;
  description: string;
  base_price: number;
  agent_price: number;
  is_required: boolean;
  is_active: boolean;
  category: string;
}

// Pagination Types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Error Types
export interface ApiError {
  error: string;
  detail?: string;
  code?: string;
} 