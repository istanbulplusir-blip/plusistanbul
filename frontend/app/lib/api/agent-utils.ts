/**
 * Agent API Utilities
 * Helper functions for agent-related operations
 */

export class AgentApiError extends Error {
  public status: number;
  public code?: string;
  public details?: Record<string, unknown>;

  constructor(message: string, status: number, code?: string, details?: Record<string, unknown>) {
    super(message);
    this.name = 'AgentApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

/**
 * Validate agent customer data
 */
export const validateAgentCustomerData = (data: Record<string, unknown>): string[] => {
  const errors: string[] = [];

  if (!data.email || typeof data.email !== 'string' || !data.email.trim()) {
    errors.push('Email is required');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push('Invalid email format');
  }

  if (!data.first_name || typeof data.first_name !== 'string' || !data.first_name.trim()) {
    errors.push('First name is required');
  }

  if (!data.last_name || typeof data.last_name !== 'string' || !data.last_name.trim()) {
    errors.push('Last name is required');
  }

  if (data.phone && typeof data.phone === 'string' && !/^[\+]?[0-9\s\-\(\)]+$/.test(data.phone)) {
    errors.push('Invalid phone number format');
  }

  if (data.birth_date && typeof data.birth_date === 'string' && isNaN(Date.parse(data.birth_date))) {
    errors.push('Invalid birth date format');
  }

  if (data.gender && typeof data.gender === 'string' && !['male', 'female', 'other'].includes(data.gender)) {
    errors.push('Invalid gender value');
  }

  if (data.preferred_language && typeof data.preferred_language === 'string' && !['fa', 'en', 'ar'].includes(data.preferred_language)) {
    errors.push('Invalid preferred language');
  }

  if (data.preferred_contact_method && typeof data.preferred_contact_method === 'string' && !['email', 'phone', 'whatsapp', 'sms'].includes(data.preferred_contact_method)) {
    errors.push('Invalid preferred contact method');
  }

  if (data.customer_status && typeof data.customer_status === 'string' && !['active', 'inactive', 'blocked', 'vip'].includes(data.customer_status)) {
    errors.push('Invalid customer status');
  }

  if (data.customer_tier && typeof data.customer_tier === 'string' && !['bronze', 'silver', 'gold', 'platinum'].includes(data.customer_tier)) {
    errors.push('Invalid customer tier');
  }

  return errors;
};

/**
 * Validate agent tour booking data
 */
export const validateAgentTourBookingData = (data: Record<string, unknown>): string[] => {
  const errors: string[] = [];

  if (!data.customer_id || typeof data.customer_id !== 'string' || !data.customer_id.trim()) {
    errors.push('Customer ID is required');
  }

  if (!data.tour_id || typeof data.tour_id !== 'string' || !data.tour_id.trim()) {
    errors.push('Tour ID is required');
  }

  if (!data.variant_id || typeof data.variant_id !== 'string' || !data.variant_id.trim()) {
    errors.push('Variant ID is required');
  }

  if (!data.schedule_id || typeof data.schedule_id !== 'string' || !data.schedule_id.trim()) {
    errors.push('Schedule ID is required');
  }

  if (!data.booking_date || typeof data.booking_date !== 'string' || !data.booking_date.trim()) {
    errors.push('Booking date is required');
  } else if (typeof data.booking_date === 'string' && isNaN(Date.parse(data.booking_date))) {
    errors.push('Invalid booking date format');
  }

  if (!data.booking_time || typeof data.booking_time !== 'string' || !data.booking_time.trim()) {
    errors.push('Booking time is required');
  }

  if (!data.participants || typeof data.participants !== 'object' || data.participants === null) {
    errors.push('Participants data is required');
  } else {
    const participants = data.participants as Record<string, unknown>;
    const { adults, children, infants } = participants;
    
    if (typeof adults !== 'number' || adults < 0) {
      errors.push('Invalid adults count');
    }
    
    if (typeof children !== 'number' || children < 0) {
      errors.push('Invalid children count');
    }
    
    if (typeof infants !== 'number' || infants < 0) {
      errors.push('Invalid infants count');
    }
    
    if (typeof adults === 'number' && typeof children === 'number' && typeof infants === 'number' && adults + children + infants === 0) {
      errors.push('At least one participant is required');
    }
  }

  return errors;
};

/**
 * Validate agent transfer booking data
 */
export const validateAgentTransferBookingData = (data: Record<string, unknown>): string[] => {
  const errors: string[] = [];

  if (!data.customer_id || typeof data.customer_id !== 'string' || !data.customer_id.trim()) {
    errors.push('Customer ID is required');
  }

  if (!data.route_id || typeof data.route_id !== 'string' || !data.route_id.trim()) {
    errors.push('Route ID is required');
  }

  if (!data.vehicle_type || typeof data.vehicle_type !== 'string' || !data.vehicle_type.trim()) {
    errors.push('Vehicle type is required');
  }

  if (!data.booking_date || typeof data.booking_date !== 'string' || !data.booking_date.trim()) {
    errors.push('Booking date is required');
  } else if (typeof data.booking_date === 'string' && isNaN(Date.parse(data.booking_date))) {
    errors.push('Invalid booking date format');
  }

  if (!data.booking_time || typeof data.booking_time !== 'string' || !data.booking_time.trim()) {
    errors.push('Booking time is required');
  }

  if (typeof data.passenger_count !== 'number' || data.passenger_count < 1) {
    errors.push('Invalid passenger count');
  }

  if (data.trip_type === 'round_trip') {
    if (!data.return_date || typeof data.return_date !== 'string' || !data.return_date.trim()) {
      errors.push('Return date is required for round trip');
    } else if (typeof data.return_date === 'string' && isNaN(Date.parse(data.return_date))) {
      errors.push('Invalid return date format');
    }

    if (!data.return_time || typeof data.return_time !== 'string' || !data.return_time.trim()) {
      errors.push('Return time is required for round trip');
    }
  }

  return errors;
};

/**
 * Validate agent car rental booking data
 */
export const validateAgentCarRentalBookingData = (data: Record<string, unknown>): string[] => {
  const errors: string[] = [];

  if (!data.customer_id || typeof data.customer_id !== 'string' || !data.customer_id.trim()) {
    errors.push('Customer ID is required');
  }

  if (!data.car_id || typeof data.car_id !== 'string' || !data.car_id.trim()) {
    errors.push('Car ID is required');
  }

  if (!data.pickup_date || typeof data.pickup_date !== 'string' || !data.pickup_date.trim()) {
    errors.push('Pickup date is required');
  } else if (typeof data.pickup_date === 'string' && isNaN(Date.parse(data.pickup_date))) {
    errors.push('Invalid pickup date format');
  }

  if (!data.pickup_time || typeof data.pickup_time !== 'string' || !data.pickup_time.trim()) {
    errors.push('Pickup time is required');
  }

  if (!data.dropoff_date || typeof data.dropoff_date !== 'string' || !data.dropoff_date.trim()) {
    errors.push('Dropoff date is required');
  } else if (typeof data.dropoff_date === 'string' && isNaN(Date.parse(data.dropoff_date))) {
    errors.push('Invalid dropoff date format');
  }

  if (!data.dropoff_time || typeof data.dropoff_time !== 'string' || !data.dropoff_time.trim()) {
    errors.push('Dropoff time is required');
  }

  if (typeof data.days !== 'number' || data.days < 1) {
    errors.push('Invalid rental days');
  }

  // Check if pickup date is before dropoff date
  if (data.pickup_date && data.dropoff_date && typeof data.pickup_date === 'string' && typeof data.dropoff_date === 'string') {
    const pickupDate = new Date(data.pickup_date);
    const dropoffDate = new Date(data.dropoff_date);
    
    if (pickupDate >= dropoffDate) {
      errors.push('Dropoff date must be after pickup date');
    }
  }

  return errors;
};

/**
 * Validate agent event booking data
 */
export const validateAgentEventBookingData = (data: Record<string, unknown>): string[] => {
  const errors: string[] = [];

  if (!data.customer_id || typeof data.customer_id !== 'string' || !data.customer_id.trim()) {
    errors.push('Customer ID is required');
  }

  if (!data.event_id || typeof data.event_id !== 'string' || !data.event_id.trim()) {
    errors.push('Event ID is required');
  }

  if (!data.performance_id || typeof data.performance_id !== 'string' || !data.performance_id.trim()) {
    errors.push('Performance ID is required');
  }

  if (!data.section || typeof data.section !== 'string' || !data.section.trim()) {
    errors.push('Section is required');
  }

  if (!data.ticket_type_id || typeof data.ticket_type_id !== 'string' || !data.ticket_type_id.trim()) {
    errors.push('Ticket type ID is required');
  }

  if (typeof data.quantity !== 'number' || data.quantity < 1) {
    errors.push('Invalid ticket quantity');
  }

  return errors;
};

/**
 * Validate agent pricing rule data
 */
export const validateAgentPricingRuleData = (data: Record<string, unknown>): string[] => {
  const errors: string[] = [];

  if (!data.product_type || typeof data.product_type !== 'string' || !['tour', 'event', 'transfer', 'car_rental'].includes(data.product_type)) {
    errors.push('Invalid product type');
  }

  if (!data.pricing_method || typeof data.pricing_method !== 'string' || !['discount_percentage', 'fixed_price', 'markup_percentage', 'custom_factor'].includes(data.pricing_method)) {
    errors.push('Invalid pricing method');
  }

  // Validate pricing values based on method
  switch (data.pricing_method) {
    case 'discount_percentage':
      if (typeof data.discount_percentage !== 'number' || data.discount_percentage < 0 || data.discount_percentage > 100) {
        errors.push('Discount percentage must be between 0 and 100');
      }
      break;
    
    case 'fixed_price':
      if (typeof data.fixed_price !== 'number' || data.fixed_price < 0) {
        errors.push('Fixed price must be a positive number');
      }
      break;
    
    case 'markup_percentage':
      if (typeof data.markup_percentage !== 'number' || data.markup_percentage < 0) {
        errors.push('Markup percentage must be a positive number');
      }
      break;
    
    case 'custom_factor':
      if (typeof data.custom_factor !== 'number' || data.custom_factor <= 0) {
        errors.push('Custom factor must be a positive number');
      }
      break;
  }

  // Validate min/max price constraints
  if (data.min_price && (typeof data.min_price !== 'number' || data.min_price < 0)) {
    errors.push('Minimum price must be a positive number');
  }

  if (data.max_price && (typeof data.max_price !== 'number' || data.max_price < 0)) {
    errors.push('Maximum price must be a positive number');
  }

  if (data.min_price && data.max_price && typeof data.min_price === 'number' && typeof data.max_price === 'number' && data.min_price > data.max_price) {
    errors.push('Minimum price cannot be greater than maximum price');
  }

  return errors;
};

/**
 * Format commission amount for display
 */
export const formatCommissionAmount = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format customer tier for display
 */
export const formatCustomerTier = (tier: string): string => {
  const tierMap: Record<string, string> = {
    bronze: 'برنزی',
    silver: 'نقره‌ای',
    gold: 'طلایی',
    platinum: 'پلاتینی',
  };
  return tierMap[tier] || tier;
};

/**
 * Format customer status for display
 */
export const formatCustomerStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    active: 'فعال',
    inactive: 'غیرفعال',
    blocked: 'مسدود',
    vip: 'ویژه',
  };
  return statusMap[status] || status;
};

/**
 * Format commission status for display
 */
export const formatCommissionStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: 'در انتظار',
    approved: 'تأیید شده',
    paid: 'پرداخت شده',
    rejected: 'رد شده',
    cancelled: 'لغو شده',
  };
  return statusMap[status] || status;
};

/**
 * Get status color for UI components
 */
export const getStatusColor = (status: string, type: 'customer' | 'commission' | 'order' = 'customer'): string => {
  const colorMap: Record<string, Record<string, string>> = {
    customer: {
      active: 'green',
      inactive: 'gray',
      blocked: 'red',
      vip: 'purple',
    },
    commission: {
      pending: 'yellow',
      approved: 'blue',
      paid: 'green',
      rejected: 'red',
      cancelled: 'gray',
    },
    order: {
      pending: 'yellow',
      confirmed: 'blue',
      cancelled: 'red',
      completed: 'green',
    },
  };

  return colorMap[type]?.[status] || 'gray';
};

/**
 * Calculate agent price with discount
 */
export const calculateAgentPrice = (
  basePrice: number,
  discountPercentage: number = 15
): number => {
  return basePrice * (1 - discountPercentage / 100);
};

/**
 * Generate customer search suggestions
 */
export const generateCustomerSearchSuggestions = (customers: Array<{name: string; email: string; phone: string}>, query: string): Array<{name: string; email: string; phone: string}> => {
  if (!query.trim()) return customers.slice(0, 10);

  const lowercaseQuery = query.toLowerCase();
  
  return customers
    .filter(customer => 
      customer.name.toLowerCase().includes(lowercaseQuery) ||
      customer.email.toLowerCase().includes(lowercaseQuery) ||
      customer.phone.includes(query)
    )
    .slice(0, 10);
};

/**
 * Parse API error response
 */
export const parseApiError = (error: unknown): AgentApiError => {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as { response: { status: number; data: Record<string, unknown> } }).response;
    const { status, data } = response;
    const message = (data.error as string) || (data.message as string) || 'An error occurred';
    const code = data.code as string;
    const details = data.details as Record<string, unknown>;
    
    return new AgentApiError(message, status, code, details);
  } else if (error && typeof error === 'object' && 'request' in error) {
    return new AgentApiError('Network error - please check your connection', 0);
  } else if (error && typeof error === 'object' && 'message' in error) {
    return new AgentApiError((error as { message: string }).message || 'An unexpected error occurred', 0);
  } else {
    return new AgentApiError('An unexpected error occurred', 0);
  }
};
