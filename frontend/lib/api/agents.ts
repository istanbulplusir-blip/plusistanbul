/**
 * Agent API endpoints for Peykan Tourism Platform
 */

import { apiClient } from './client';

// Types
export interface Tour {
  id: number;
  title: string;
  description: string;
  base_price: number;
  agent_price?: number;
  duration: string;
  location: string;
  image: string;
  category: string;
  is_active: boolean;
}

export interface TourVariant {
  id: number;
  name: string;
  description: string;
  base_price: number;
  agent_price: number;
  duration: string;
  max_participants: number;
  capacity?: number;
  available_capacity?: number;
  includes: string[] | {
    transfer?: boolean;
    guide?: boolean;
    meal?: boolean;
    photographer?: boolean;
    extended_hours?: boolean;
    private_transfer?: boolean;
    expert_guide?: boolean;
    special_meal?: boolean;
  };
  is_active: boolean;
}

export interface TourOption {
  id: number;
  name: string;
  description: string;
  base_price: number;
  agent_price: number;
  is_required: boolean;
  is_active: boolean;
  category: string;
}

export interface Customer {
  id: number; // Keep as number for consistency with backend
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  national_id: string;
  birth_date: string;
  created_at: string;
  total_bookings: number;
  total_spent: number;
}

export interface PricingData {
  base_price: number;
  agent_subtotal: number;
  agent_fees: number;
  agent_taxes: number;
  agent_total: number;
  savings: number;
  savings_percentage: number;
  pricing_method: string;
  breakdown: Record<string, number>;
  fees_taxes_breakdown: Record<string, number>;
}

export interface BookingRequest {
  customer_id: number;
  tour_id: number;
  variant_id: number;
  schedule_id: string;
  booking_date: string;
  booking_time: string;
  participants: {
    adults: number;
    children: number;
    infants: number;
  };
  selected_options: any[];
  payment_method?: string;
  product_type?: string;
}

export interface BookingResponse {
  booking_id: string;
  order_number: string;
  status: string;
  confirmation_code: string;
  created_at: string;
  total_amount: number;
  commission: number;
  commission_amount?: number;
  customer_name?: string;
  items?: Array<{
    product_type: string;
    product_title: string;
  }>;
}

export interface AvailableDate {
  date: string;
  schedule_id: string;  // Add schedule_id to the interface
  available_slots: number;
  variants: TourVariant[];
}

export interface TransferRoute {
  id: number;
  name: string;
  origin: string;
  destination: string;
  from_location: string;
  to_location: string;
  distance: number;
  duration: string;
  estimated_duration: number;
  base_price: number;
  vehicle_types: Array<{
    type: string;
    name: string;
    base_price: number;
    capacity: number;
    features: string[];
  }>;
  options?: Array<{
    id: string;
    name: string;
    description: string;
    price: number;
    option_type: string;
    price_type: string;
    max_quantity: number;
    is_active: boolean;
  }>;
  is_active: boolean;
  round_trip_discount_enabled?: boolean;
  round_trip_discount_percentage?: number;
}

export interface TransferVehicle {
  id: number;
  name: string;
  capacity: number;
  description: string;
  base_price: number;
  image: string;
}

export interface TransferPricing {
  base_price: number;
  night_surcharge: number;
  options_total: number;
  return_price: number;
  return_discount: number;
  final_price: number;
  agent_commission: number;
  customer_price: number;
  fees_total?: number;
  tax_total?: number;
  grand_total?: number;
  subtotal?: number;
  price_breakdown?: {
    outbound_surcharge: number;
    return_surcharge: number;
    round_trip_discount: number;
    options_total: number;
  };
  savings?: number;
  agent_price?: number;
  total?: number;
  commission_amount?: number;
  // Additional fields from agent pricing response
  agent_total?: number;
  savings_percentage?: number;
  currency?: string;
  capacity_info?: {
    max_passengers: number;
    requested_passengers: number;
    capacity_available: boolean;
  };
  trip_info?: {
    trip_type: string;
    vehicle_type: string;
    route_name: string;
  };
}

// Agent Tours API
export const agentToursApi = {
  // Get all tours available for agents
  async getTours(): Promise<Tour[]> {
    try {
      const response = await apiClient.get('/agents/tours/');
      return (response as any).data;
    } catch (error) {
      console.error('Error fetching agent tours:', error);
      throw error;
    }
  },

  // Get tour details
  async getTourDetails(tourId: number): Promise<Tour> {
    try {
      const response = await apiClient.get(`/agents/tours/${tourId}/`);
      return (response as any).data;
    } catch (error) {
      console.error('Error fetching tour details:', error);
      throw error;
    }
  },

  // Get available dates and variants for a tour
  async getAvailableDates(tourId: number): Promise<AvailableDate[]> {
    try {
      const response = await apiClient.get(`/agents/tours/${tourId}/available-dates/`);
      return (response as any).data;
    } catch (error) {
      console.error('Error fetching available dates:', error);
      throw error;
    }
  },

  // Get tour options
  async getTourOptions(tourId: number): Promise<TourOption[]> {
    try {
      const response = await apiClient.get(`/agents/tours/${tourId}/options/`);
      return (response as any).data;
    } catch (error) {
      console.error('Error fetching tour options:', error);
      throw error;
    }
  }
};

// Agent Customers API
export const agentCustomersApi = {
  // Get all customers for the agent
  async getCustomers(): Promise<Customer[]> {
    try {
      const response = await apiClient.get('/agents/customers/');
      const data = (response as any).data;
      // Handle both array and object response formats
      return Array.isArray(data) ? data : (data.customers || []);
    } catch (error) {
      console.error('Error fetching customers:', error);
      throw error;
    }
  },

  // Create new customer
  async createCustomer(customerData: Omit<Customer, 'id' | 'created_at' | 'total_bookings' | 'total_spent'>): Promise<Customer> {
    try {
      const response = await apiClient.post('/agents/customers/', customerData);
      return (response as any).data;
    } catch (error) {
      console.error('Error creating customer:', error);
      throw error;
    }
  },

  // Send login credentials to customer
  async sendCredentials(
    customerId: string,
    options?: {
      method?: 'email' | 'sms' | 'both';
      message?: string;
    }
  ): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.post(
        `/agents/customers/${customerId}/credentials/`,
        options || { method: 'email' }
      );
      return (response as any).data;
    } catch (error) {
      console.error('Error sending credentials:', error);
      throw error;
    }
  },

  // Send verification email
  async sendVerification(customerId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.post(
        `/agents/customers/${customerId}/verification/`
      );
      return (response as any).data;
    } catch (error) {
      console.error('Error sending verification:', error);
      throw error;
    }
  },

  // Reset customer password
  async resetPassword(customerId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.post(
        `/agents/customers/${customerId}/credentials/`,
        { method: 'email' }
      );
      return (response as any).data;
    } catch (error) {
      console.error('Error resetting password:', error);
      throw error;
    }
  },

  // Get customer authentication status
  async getAuthStatus(customerId: string): Promise<{
    is_email_verified: boolean;
    has_logged_in: boolean;
    last_login_at: string | null;
    login_count: number;
    credentials_sent: boolean;
    credentials_sent_at: string | null;
  }> {
    try {
      const response = await apiClient.get(
        `/agents/customers/${customerId}/auth-status/`
      );
      return (response as any).data.data;
    } catch (error) {
      console.error('Error fetching auth status:', error);
      throw error;
    }
  },

  // Update customer
  async updateCustomer(customerId: number, customerData: Partial<Customer>): Promise<Customer> {
    try {
      const response = await apiClient.put(`/agents/customers/${customerId}/`, customerData);
      return (response as any).data;
    } catch (error) {
      console.error('Error updating customer:', error);
      throw error;
    }
  },

  // Get customer details
  async getCustomerDetails(customerId: number): Promise<Customer> {
    try {
      const response = await apiClient.get(`/agents/customers/${customerId}/`);
      return (response as any).data;
    } catch (error) {
      console.error('Error fetching customer details:', error);
      throw error;
    }
  }
};

// Agent Pricing API
export const agentPricingApi = {
  // Calculate pricing for agent booking
  async calculatePricing(bookingData: {
    tour_id: number;
    variant_id: number;
    participants: {
      adults: number;
      children: number;
      infants: number;
    };
    options: number[];
  }): Promise<PricingData> {
    try {
      const response = await apiClient.post('/agents/pricing/preview/', {
        product_type: 'tour',
        tour_id: bookingData.tour_id,
        variant_id: bookingData.variant_id,
        participants: bookingData.participants,
        selected_options: bookingData.options
      });
      const responseData = (response as any).data;
      // Backend returns { success: true, pricing: {...} }
      if (responseData && responseData.pricing) {
        return responseData.pricing;
      }
      return responseData;
    } catch (error) {
      console.error('Error calculating pricing:', error);
      throw error;
    }
  },

  // Preview pricing without booking
  async previewPricing(bookingData: {
    tour_id: number;
    variant_id: number;
    participants: {
      adults: number;
      children: number;
      infants: number;
    };
    options: number[];
  }): Promise<PricingData> {
    try {
      const response = await apiClient.post('/agents/pricing/preview/', {
        product_type: 'tour',
        tour_id: bookingData.tour_id,
        variant_id: bookingData.variant_id,
        participants: bookingData.participants,
        selected_options: bookingData.options
      });
      const responseData = (response as any).data;
      // Backend returns { success: true, pricing: {...} }
      if (responseData && responseData.pricing) {
        return responseData.pricing;
      }
      return responseData;
    } catch (error) {
      console.error('Error previewing pricing:', error);
      throw error;
    }
  }
};

// Agent Booking API
export const agentBookingApi = {
  // Create booking for customer
  async createBooking(bookingData: BookingRequest): Promise<BookingResponse> {
    try {
      // Determine the correct endpoint based on product type
      let endpoint = '/agents/book/tour/';
      if (bookingData.product_type === 'transfer') {
        endpoint = '/agents/book/transfer/';
      } else if (bookingData.product_type === 'car_rental') {
        endpoint = '/agents/book/car-rental/';
      } else if (bookingData.product_type === 'event') {
        endpoint = '/agents/book/event/';
      }
      
      const response = await apiClient.post(endpoint, bookingData);
      return (response as any).data;
    } catch (error) {
      console.error('Error creating booking:', error);
      throw error;
    }
  },

  // Get booking details
  async getBookingDetails(bookingId: string): Promise<BookingResponse> {
    try {
      const response = await apiClient.get(`/agents/bookings/${bookingId}/`);
      return (response as any).data;
    } catch (error) {
      console.error('Error fetching booking details:', error);
      throw error;
    }
  },

  // Get agent's bookings (orders)
  async getAgentBookings(): Promise<BookingResponse[]> {
    try {
      const response = await apiClient.get('/agents/orders/');
      return (response as any).data.orders;
    } catch (error) {
      console.error('Error fetching agent bookings:', error);
      throw error;
    }
  }
};

// Agent Dashboard API
export const agentDashboardApi = {
  // Get agent dashboard statistics
  async getDashboardStats(): Promise<{
    total_commission: number;
    total_orders: number;
    total_customers: number;
    conversion_rate: number;
    monthly_sales: Array<{ month: string; amount: number }>;
    top_products: Array<{ name: string; bookings: number; revenue: number }>;
    recent_activities: Array<{ type: string; description: string; created_at: string }>;
  }> {
    try {
      const response = await apiClient.get('/agents/dashboard/stats/');
      return (response as any).data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  },

  // Get agent commission history
  async getCommissionHistory(): Promise<Array<{
    id: number;
    amount: number;
    booking_id: string;
    created_at: string;
    status: string;
  }>> {
    try {
      const response = await apiClient.get('/agents/commissions/');
      return (response as any).data;
    } catch (error) {
      console.error('Error fetching commission history:', error);
      throw error;
    }
  }
};

// Agent Commissions API
export const agentCommissionsApi = {
  // Get commission history
  async getCommissionHistory(): Promise<Array<{
    id: string;
    amount: number;
    booking_id: string;
    created_at: string;
    status: string;
  }>> {
    try {
      const response = await apiClient.get('/agents/commissions/');
      const commissions = (response as any).data.commissions || [];
      
      // Transform the data to match expected format
      return commissions.map((commission: any) => ({
        id: commission.id,
        amount: commission.commission_amount,
        booking_id: commission.order_number,
        created_at: commission.created_at,
        status: commission.status
      }));
    } catch (error) {
      console.error('Error fetching commission history:', error);
      throw error;
    }
  }
};

// Export all APIs
export const agentApi = {
  tours: agentToursApi,
  customers: agentCustomersApi,
  pricing: agentPricingApi,
  booking: agentBookingApi,
  dashboard: agentDashboardApi,
  commissions: agentCommissionsApi
};
