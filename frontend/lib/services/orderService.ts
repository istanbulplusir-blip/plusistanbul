/**
 * Order Service for handling order-related API calls
 */

import { tokenService } from './tokenService';

export interface OrderItem {
  id: string;
  product_type: string;
  product_id: string;
  product_title: string;
  product_slug: string;
  variant_id?: string;
  variant_name?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  currency: string;
  options_total?: number;
  selected_options?: Record<string, unknown>;
  booking_date?: string;
  booking_time?: string;
  booking_data?: {
    // Common fields
    participants?: {
      adult: number;
      child: number;
      infant: number;
    };
    special_requests?: string;
    special_requirements?: string;
    schedule_id?: string;
    pickup_time?: string;

    // Tour related
    selected_options?: unknown[];

    // Event related
    seats?: unknown[];
    section?: string;
    ticket_type_name?: string;
    performance_date?: string;
    performance_time?: string;
    venue_name?: string;
    venue_city?: string;
    venue_country?: string;

    // Transfer related
    trip_type?: 'one_way' | 'round_trip';
    outbound_date?: string;
    outbound_time?: string;
    return_date?: string;
    return_time?: string;
    pickup_address?: string;
    dropoff_address?: string;
    passenger_count?: number;
    luggage_count?: number;
    vehicle_type?: string;
    vehicle_name?: string;
    max_passengers?: number;
    estimated_duration?: number;
    route_name?: string;
    route_origin?: string;
    route_destination?: string;
    outbound_price?: string | number;
    return_price?: string | number;
    surcharges?: Record<string, unknown>;
    discounts?: Record<string, unknown>;
    round_trip_discount?: string;
  };
}

export interface Order {
  id: string;
  order_number: string;
  user: string;
  agent?: string;
  status: string;
  payment_status: string;
  total_amount: number;
  subtotal?: number;
  service_fee_amount?: number;
  tax_amount?: number;
  discount_amount?: number;
  agent_commission_rate?: number;
  agent_commission_amount?: number;
  commission_paid?: boolean;
  currency: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  special_requests?: string;
  notes?: string;
}

export interface OrdersResponse {
  success: boolean;
  orders?: Order[];
  results?: Order[];
  message?: string;
  errors?: Record<string, string[]>;
}

export interface TimelineEvent {
  event: string;
  title: string;
  date: string;
  status: string;
}

class OrderService {
  private baseUrl = '/api/v1/orders/';

  /**
   * Get user orders
   */
  async getUserOrders(): Promise<OrdersResponse> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        // Return empty orders instead of error for better UX
        return {
          success: true,
          orders: [],
        };
      }

      const response = await fetch(`${this.baseUrl}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        // If endpoint doesn't exist (404) or server error (500), return empty array
        if (response.status === 404 || response.status === 500) {
          return {
            success: true,
            orders: [],
          };
        }
        
        const data = await response.json();
        throw new Error(data.message || 'Failed to get orders');
      }

      const data = await response.json();
      return {
        success: true,
        orders: Array.isArray(data) ? data : (data.results || []),
      };
    } catch (error: unknown) {
      console.warn('Orders API not available:', error);
      // Return empty array instead of error for better UX
      return {
        success: true,
        orders: [],
      };
    }
  }

  /**
   * Get order details by order number
   */
  async getOrderDetails(orderNumber: string): Promise<{ success: boolean; order?: Order; message?: string }> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${this.baseUrl}${orderNumber}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || 'Failed to get order details');
      }

      const data = await response.json();
      return {
        success: true,
        order: data,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get order details';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }

  /**
   * Get order status key for translation
   */
  getOrderStatusKey(status: string): string {
    const statusKeys: Record<string, string> = {
      'pending': 'pending',
      'confirmed': 'confirmed',
      'cancelled': 'cancelled',
      'completed': 'completed',
      'refunded': 'refunded',
    };
    return statusKeys[status] || status;
  }

  /**
   * Get payment status key for translation
   */
  getPaymentStatusKey(status: string): string {
    const statusKeys: Record<string, string> = {
      'pending': 'pendingPayment',
      'paid': 'paidStatus',
      'failed': 'failed',
      'refunded': 'refunded',
    };
    return statusKeys[status] || status;
  }

  /**
   * Get status color class
   */
  getStatusColor(status: string): string {
    const statusColors: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'confirmed': 'bg-blue-100 text-blue-800',
      'cancelled': 'bg-red-100 text-red-800',
      'completed': 'bg-green-100 text-green-800',
      'refunded': 'bg-gray-100 text-gray-800',
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  }

  /**
   * Get payment status color class
   */
  getPaymentStatusColor(status: string): string {
    const statusColors: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'paid': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800',
      'refunded': 'bg-gray-100 text-gray-800',
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  }

  /**
   * Format date to locale format
   */
  formatDate(dateString: string): string {
    if (!dateString) return '';
    // Use current locale, defaulting to English if not Persian
    const locale = typeof window !== 'undefined' && window.navigator.language === 'fa' ? 'fa-IR' : 'en-US';
    return new Date(dateString).toLocaleDateString(locale);
  }

  /**
   * Format currency
   */
  formatCurrency(amount: number, currency: string = 'USD'): string {
    // Use current locale, defaulting to English if not Persian
    const locale = typeof window !== 'undefined' && window.navigator.language === 'fa' ? 'fa-IR' : 'en-US';
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
    }).format(amount);
  }

  /**
   * Format selected options for display
   */
  formatSelectedOptions(selectedOptions: unknown): Array<{name: string, value: string, type?: string}> {
    if (!selectedOptions) return [];
    
    try {
      let options = selectedOptions;
      
      // If it's a string, try to parse it
      if (typeof selectedOptions === 'string') {
        options = JSON.parse(selectedOptions);
      }
      
      // Handle array format (like events and tours)
      if (Array.isArray(options)) {
        return options.map(option => {
          // Event option with name and quantity
          if (option.name && option.quantity) {
            return {
              name: option.name,
              value: `${option.quantity}x`,
              type: 'event_option'
            };
          }
          
          // Tour option with option_id and quantity
          if (option.option_id && option.quantity) {
            return {
              name: `Option ${option.option_id.slice(0, 8)}...`,
              value: `${option.quantity}x`,
              type: 'tour_option'
            };
          }
          
          // Event performance with seats and options
          if (option.performance_id) {
            const details = [];
            
            if (option.section) {
              details.push(`${option.section}`);
            }
            
            if (option.seats && option.seats.length > 0) {
              const seatInfo = option.seats.map((s: {row_number: string, seat_number: string}) => `${s.row_number}-${s.seat_number}`).join(', ');
              details.push(`Seats: ${seatInfo}`);
            }
            
            if (option.options && option.options.length > 0) {
              const optionNames = option.options.map((o: {name: string, quantity: number}) => `${o.name} (${o.quantity}x)`).join(', ');
              details.push(`${optionNames}`);
            }
            
            return {
              name: 'Performance Details',
              value: details.join(' | '),
              type: 'event_performance'
            };
          }
          
          return {
            name: 'Option',
            value: JSON.stringify(option),
            type: 'unknown'
          };
        });
      }
      
      // Handle object format
      if (typeof options === 'object') {
        return Object.entries(options).map(([key, value]) => ({
          name: key,
          value: String(value),
          type: 'object_property'
        }));
      }
      
      return [];
    } catch (error) {
      console.error('Error formatting selected options:', error);
      return [{
        name: 'Selected Options',
        value: String(selectedOptions),
        type: 'error'
      }];
    }
  }

  /**
   * Cancel an order
   */
  async cancelOrder(orderNumber: string): Promise<{ success: boolean; message?: string; order?: Order }> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${this.baseUrl}${orderNumber}/actions/cancel/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to cancel order');
      }

      return {
        success: true,
        message: data.message,
        order: data.order,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to cancel order';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }



  /**
   * Get order timeline
   */
  async getOrderTimeline(orderNumber: string): Promise<{ success: boolean; timeline?: TimelineEvent[]; message?: string }> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${this.baseUrl}${orderNumber}/timeline/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to get order timeline');
      }

      return {
        success: true,
        timeline: data.timeline,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get order timeline';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }

  /**
   * Get WhatsApp links for order
   */
  async getWhatsAppLinks(orderNumber: string): Promise<{ 
    success: boolean; 
    customerLink?: string; 
    adminLink?: string; 
    supportInfo?: { phone: string; formatted_phone: string; whatsapp_url: string };
    message?: string 
  }> {
    try {
      const token = tokenService.getAccessToken();
      if (!token) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${this.baseUrl}${orderNumber}/whatsapp/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to get WhatsApp links');
      }

      return {
        success: true,
        customerLink: data.customer_whatsapp_link,
        adminLink: data.admin_whatsapp_link,
        supportInfo: data.support_info,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get WhatsApp links';
      return {
        success: false,
        message: errorMessage,
      };
    }
  }

  private getAuthHeaders(): Record<string, string> {
    const token = tokenService.getAccessToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  async downloadReceipt(orderNumber: string) {
    try {
      const response = await fetch(`${this.baseUrl}${orderNumber}/receipt/`, {
        method: 'GET',
        headers: {
          ...this.getAuthHeaders(),
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Error downloading receipt');
      }

      // Check if response is PDF
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/pdf')) {
        // Handle PDF download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `receipt-${orderNumber}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        return {
          success: true,
          message: 'Receipt downloaded successfully'
        };
      } else {
        // Handle JSON response (error case)
        const data = await response.json();
        return {
          success: false,
          message: data.message || 'Error downloading receipt'
        };
      }
    } catch (error: unknown) {
      console.error('Error downloading receipt:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Error downloading receipt'
      };
    }
  }
}

export const orderService = new OrderService(); 