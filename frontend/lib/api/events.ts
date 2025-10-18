/**
 * Event API utilities for Peykan Tourism Platform.
 */

import { apiClient } from './client';
import { 
  EventListResponse, EventDetailResponse, 
  EventSearchParams, EventBookingRequest, EventReview,
  EventCategory, Venue, Artist, EventPerformance,
  EventPricingRequest, EventPricingBreakdown,
  EventSeatMap, EventAvailabilityCalendar,
  EventSeatReservation, PerformanceSeatsResponse
} from '../types/api';
import { normalizeEventPricing, NormalizedPriceBreakdown } from '../utils/pricing';

// Event Categories
export const getEventCategories = async (): Promise<EventCategory[]> => {
  const response = await apiClient.get('/events/categories/');
  return (response as { data: EventCategory[] }).data;
};

// Venues
export const getVenues = async (params?: {
  search?: string;
  city?: string;
  country?: string;
}): Promise<Venue[]> => {
  const response = await apiClient.get('/events/venues/', { params });
  return (response as { data: Venue[] }).data;
};

// Artists
export const getArtists = async (params?: {
  search?: string;
}): Promise<Artist[]> => {
  const response = await apiClient.get('/events/artists/', { params });
  return (response as { data: Artist[] }).data;
};

// Enhanced Events API
export const getEvents = async (params?: {
  search?: string;
  category?: string;
  venue?: string;
  style?: string;
  min_price?: number;
  max_price?: number;
  date_from?: string;
  date_to?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
  type?: 'upcoming' | 'past' | 'special' | 'featured' | 'popular';
}): Promise<EventListResponse> => {
  const response = await apiClient.get('/events/events/', { params });
  return (response as { data: EventListResponse }).data;
};

// New API for home page categorized events
export const getHomeEvents = async (): Promise<{
  upcoming_events: Event[];
  past_events: Event[];
  special_events: Event[];
  featured_events: Event[];
  popular_events: Event[];
  total_counts: {
    upcoming: number;
    past: number;
    special: number;
    featured: number;
    popular: number;
  };
}> => {
  const response = await apiClient.get('/events/home-events/');
  const data = (response as { data: unknown }).data as {
    upcoming_events?: unknown[];
    past_events?: unknown[];
    special_events?: unknown[];
    featured_events?: unknown[];
    popular_events?: unknown[];
    total_counts?: {
      upcoming: number;
      past: number;
      special: number;
      featured: number;
      popular: number;
    };
  };
  
  // Transform the response to match our Event interface
  return {
    upcoming_events: (data.upcoming_events || []) as Event[],
    past_events: (data.past_events || []) as Event[],
    special_events: (data.special_events || []) as Event[],
    featured_events: (data.featured_events || []) as Event[],
    popular_events: (data.popular_events || []) as Event[],
    total_counts: data.total_counts || {
      upcoming: 0,
      past: 0,
      special: 0,
      featured: 0,
      popular: 0
    }
  };
};

export const searchEvents = async (searchParams: EventSearchParams): Promise<EventListResponse> => {
  const response = await apiClient.get('/events/events/search/', { 
    params: searchParams 
  });
  return (response as { data: EventListResponse }).data;
};

export const getEventBySlug = async (slug: string): Promise<EventDetailResponse> => {
  try {
    const response = await apiClient.get(`/events/events/${slug}/`);
    return (response as { data: EventDetailResponse }).data;
  } catch (error: unknown) {
    console.error('Error fetching event by slug:', error);
    
    // Handle specific error types
    if (error instanceof Error && 'code' in error && error.code === 'ECONNABORTED' || 
        error instanceof Error && 'message' in error && error.message?.includes('timeout')) {
      throw new Error('Request timeout: The server is taking too long to respond. Please try again.');
    }
    
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status === 404) {
      throw new Error('Event not found');
    }
    
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status >= 500) {
      throw new Error('Server error: Please try again later');
    }
    
    // Re-throw the original error if it's not handled
    throw error;
  }
};

export const getEventById = async (id: string): Promise<EventDetailResponse> => {
  try {
    const response = await apiClient.get(`/events/events/${id}/`);
    return (response as { data: EventDetailResponse }).data;
  } catch (error: unknown) {
    console.error('Error fetching event by ID:', error);
    
    // Handle specific error types
    if (error instanceof Error && 'code' in error && error.code === 'ECONNABORTED' || 
        error instanceof Error && 'message' in error && error.message?.includes('timeout')) {
      throw new Error('Request timeout: The server is taking too long to respond. Please try again.');
    }
    
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status === 404) {
      throw new Error('Event not found');
    }
    
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status >= 500) {
      throw new Error('Server error: Please try again later');
    }
    
    // Re-throw the original error if it's not handled
    throw error;
  }
};

// Enhanced Performance APIs
export const getEventPerformancesDetailed = async (eventId: string): Promise<{
  event_id: string;
  performances: Array<{
    id: string;
    date: string;
    start_time: string;
    end_time: string;
    is_available: boolean;
    capacity_summary: Record<string, unknown>;
    available_sections: Record<string, unknown>[];
    booking_cutoff: string;
  }>;
}> => {
  const response = await apiClient.get(`/events/events/${eventId}/performances-detailed/`);
  return (response as { data: { event_id: string; performances: { id: string; date: string; start_time: string; end_time: string; is_available: boolean; capacity_summary: Record<string, unknown>; available_sections: Record<string, unknown>[]; booking_cutoff: string; }[]; } }).data;
};

export const getEventAvailabilityCalendar = async (eventId: string): Promise<EventAvailabilityCalendar> => {
  const response = await apiClient.get(`/events/events/${eventId}/availability-calendar/`);
  return (response as { data: EventAvailabilityCalendar }).data;
};

// Enhanced Pricing APIs
export const calculateEventPricing = async (
  eventId: string,
  pricingRequest: EventPricingRequest
): Promise<{
  event_id: string;
  performance_id: string;
  pricing_breakdown: EventPricingBreakdown; // keep raw for existing UI
  normalized: NormalizedPriceBreakdown; // new normalized shape for future use
}> => {
  try {
    // Backend endpoint uses underscore: calculate_pricing
    const response = await apiClient.post(`/events/events/${eventId}/calculate_pricing/`, pricingRequest);
    const data = (response as { data: unknown }).data;
    
    // Backend returns the pricing breakdown directly; normalize to expected shape
    return {
      event_id: eventId,
      performance_id: pricingRequest.performance_id,
      pricing_breakdown: data as EventPricingBreakdown,
      normalized: normalizeEventPricing(data as EventPricingBreakdown),
    };
  } catch (error: unknown) {
    console.error('Error calculating event pricing:', error);
    
    // Handle specific error types with better error messages
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number') {
      const status = error.response.status as number;
      
      if (status === 400) {
        // Extract the specific error message from the backend
        const errorResponse = error.response as { data?: { error?: string } };
        const errorData = errorResponse.data;
        if (errorData && typeof errorData === 'object' && 'error' in errorData) {
          const errorMessage = errorData.error as string;
          
          // Handle specific section validation errors
          if (errorMessage.includes('not found for this performance')) {
            throw new Error(`Section "${pricingRequest.section_name}" is not available for this performance. Please select a different section.`);
          }
          
          if (errorMessage.includes('not available in section')) {
            throw new Error(`Ticket type is not available in section "${pricingRequest.section_name}". Please select a different combination.`);
          }
          
          if (errorMessage.includes('Only') && errorMessage.includes('seats available')) {
            throw new Error(errorMessage);
          }
          
          // Generic validation error
          throw new Error(errorMessage);
        }
        
        throw new Error('Invalid pricing request. Please check your selections and try again.');
      }
      
      if (status === 404) {
        throw new Error('Event or performance not found');
      }
      
      if (status >= 500) {
        throw new Error('Server error: Please try again later');
      }
    }
    
    // Handle network errors and timeouts
    if (error instanceof Error && 'code' in error && error.code === 'ECONNABORTED') {
      throw new Error('Request timeout: The server is taking too long to respond. Please try again.');
    }
    
    if (error instanceof Error && !('response' in error)) {
      if (error.message.includes('Network error')) {
        throw new Error('Unable to connect to the server. Please check your internet connection and try again.');
      }
      if (error.message.includes('timeout')) {
        throw new Error('Request timeout: The server is taking too long to respond. Please try again.');
      }
    }
    
    // Re-throw the original error if it's not handled
    throw error;
  }
};

export const getEventOptions = async (eventId: string): Promise<{
  event_id: string;
  options: Array<{
    id: string;
    name: string;
    description: string;
    price: number;
    currency: string;
    option_type: string;
    max_quantity: number;
    is_available: boolean;
  }>;
}> => {
  const response = await apiClient.get(`/events/events/${eventId}/available-options/`);
  return (response as { data: {
    event_id: string;
    options: Array<{
      id: string;
      name: string;
      description: string;
      price: number;
      currency: string;
      option_type: string;
      max_quantity: number;
      is_available: boolean;
    }>;
  } }).data;
};

// Enhanced Seat Management APIs
export const getEventSeatMap = async (
  eventId: string
): Promise<EventSeatMap> => {
  const response = await apiClient.get(`/events/events/${eventId}/performances-detailed/`);
  // If a direct seat-map endpoint is required later, we can switch back; for now fetch detailed performances
  return (response as { data: EventSeatMap }).data;
};

export const getEventSeatMapLegacy = async (
  eventId: string,
  performanceId: string
): Promise<EventSeatMap> => {
  const response = await apiClient.get(`/events/events/${eventId}/seat-map/`, {
    params: { performance_id: performanceId }
  });
  return (response as { data: EventSeatMap }).data;
};

export const reserveEventSeats = async (
  eventId: string,
  reservation: EventSeatReservation
): Promise<{
  message: string;
  reservation_id: string;
  expires_at: string;
}> => {
  const response = await apiClient.post(`/events/events/${eventId}/reserve-seats/`, reservation);
  return (response as { data: {
    message: string;
    reservation_id: string;
    expires_at: string;
  } }).data;
};

// Legacy seat API for backward compatibility
export const getPerformanceSeats = async (
  eventId: string,
  performanceId: string,
  params?: {
    section?: string;
    ticket_type_id?: string;
    include_seats?: boolean | string | number;
  }
): Promise<PerformanceSeatsResponse> => {
  // Correct URL: /api/v1/events/events/{event_id}/performances/{performance_id}/seats/
  const response = await apiClient.get(`/events/events/${eventId}/performances/${performanceId}/seats/`, { params });
  return (response as { data: PerformanceSeatsResponse }).data;
};

// Seat hold/release
export const holdSeats = async (
  performanceId: string,
  payload: {
    seat_ids: string[];
    ticket_type_id?: string;
    ttl_seconds?: number;
  }
): Promise<{
  message: string;
  reservation_id: string;
  expires_at: string;
  seat_ids: string[];
  ticket_type_id?: string;
}> => {
  try {
    const response = await apiClient.post(`/events/performances/${performanceId}/hold/`, payload);
    return (response as { data: {
      message: string;
      reservation_id: string;
      expires_at: string;
      seat_ids: string[];
      ticket_type_id: string;
    } }).data;
  } catch (error: unknown) {
    console.error('Error holding seats:', error);
    
    // Handle specific error types
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status === 400) {
      throw new Error('Invalid seat hold request. Please check your selections.');
    }
    
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status === 409) {
      throw new Error('Seats are no longer available. Please select different seats.');
    }
    
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status >= 500) {
      throw new Error('Server error: Please try again later');
    }
    
    // Re-throw the original error if it's not handled
    throw error;
  }
};

export const releaseSeats = async (
  performanceId: string,
  payload: { reservation_id?: string; seat_ids?: string[] }
): Promise<{ message: string; released_count: number }> => {
  try {
    const response = await apiClient.post(`/events/performances/${performanceId}/release/`, payload);
    return (response as { data: { message: string; released_count: number } }).data;
  } catch (error: unknown) {
    console.error('Error releasing seats:', error);
    
    // Handle specific error types
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status === 400) {
      throw new Error('Invalid seat release request.');
    }
    
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status === 404) {
      throw new Error('Seat reservation not found.');
    }
    
    if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number' && error.response.status >= 500) {
      throw new Error('Server error: Please try again later');
    }
    
    // Re-throw the original error if it's not handled
    throw error;
  }
};

// Enhanced Capacity APIs
export const getPerformanceCapacitySummary = async (performanceId: string): Promise<{
  performance: {
    max_capacity: number;
    current_capacity: number;
    available_capacity: number;
    occupancy_rate: number;
  };
  sections: Array<{
    name: string;
    total_capacity: number;
    available_capacity: number;
    reserved_capacity: number;
    sold_capacity: number;
    occupancy_rate: number;
    ticket_types: Array<{
      name: string;
      allocated_capacity: number;
      available_capacity: number;
      reserved_capacity: number;
      sold_capacity: number;
      final_price: number;
    }>;
  }>;
}> => {
  const response = await apiClient.get(`/events/performances/${performanceId}/capacity-summary/`);
  return (response as { data: {
    performance: {
      max_capacity: number;
      current_capacity: number;
      available_capacity: number;
      occupancy_rate: number;
    };
    sections: Array<{
      name: string;
      total_capacity: number;
      available_capacity: number;
      reserved_capacity: number;
      sold_capacity: number;
      occupancy_rate: number;
      ticket_types: Array<{
        name: string;
        allocated_capacity: number;
        available_capacity: number;
        reserved_capacity: number;
        sold_capacity: number;
        final_price: number;
      }>;
    }>;
  } }).data;
};

export const getPerformanceAvailableSeats = async (performanceId: string): Promise<{
  performance_id: string;
  available_seats: Array<{
    id: string;
    section: {
      id: string;
      name: string;
    };
    ticket_type: {
      id: string;
      name: string;
      description: string;
      ticket_type: string;
      benefits: string[];
    };
    allocated_capacity: number;
    available_capacity: number;
    reserved_capacity: number;
    sold_capacity: number;
    price_modifier: number;
    final_price: number;
  }>;
}> => {
  const response = await apiClient.get(`/events/performances/${performanceId}/available-seats/`);
  return (response as { data: {
    performance_id: string;
    available_seats: Array<{
      id: string;
      section: {
        id: string;
        name: string;
      };
      ticket_type: {
        id: string;
        name: string;
        description: string;
        ticket_type: string;
        benefits: string[];
      };
      allocated_capacity: number;
      available_capacity: number;
      reserved_capacity: number;
      sold_capacity: number;
      price_modifier: number;
      final_price: number;
    }>;
  } }).data;
};

// Enhanced Event Reviews
export const getEventReviews = async (
  eventId: string, 
  params?: {
    page?: number;
    page_size?: number;
    ordering?: string;
  }
): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: EventReview[];
}> => {
  const response = await apiClient.get(`/events/events/${eventId}/reviews/`, { params });
  return (response as { data: {
    count: number;
    next: string | null;
    previous: string | null;
    results: EventReview[];
  } }).data;
};

export const addEventReview = async (
  eventId: string, 
  reviewData: {
    rating: number;
    title: string;
    comment: string;
  }
): Promise<EventReview> => {
  const response = await apiClient.post(`/events/events/${eventId}/add_review/`, reviewData);
  return (response as { data: EventReview }).data;
};

// Enhanced Event Booking
export const bookEvent = async (
  eventId: string, 
  bookingData: EventBookingRequest
): Promise<{
  message: string;
  event_id: string;
  booking_data: EventBookingRequest;
}> => {
  const response = await apiClient.post(`/events/events/${eventId}/book/`, bookingData);
  return (response as { data: {
    message: string;
    event_id: string;
    booking_data: EventBookingRequest;
  } }).data;
};

// Event Sections
export const getEventSections = async (performanceId: string): Promise<{
  sections: Array<{
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
  }>;
}> => {
  const response = await apiClient.get(`/events/performances/${performanceId}/sections/`);
  return (response as { data: {
    sections: Array<{
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
    }>;
  } }).data;
};

// Section Ticket Types
export const getSectionTicketTypes = async (sectionId: string): Promise<{
  ticket_types: Array<{
    id: string;
    section: {
      id: string;
      name: string;
    };
    ticket_type: {
      id: string;
      name: string;
      description: string;
      ticket_type: string;
      benefits: string[];
      age_min?: number;
      age_max?: number;
    };
    allocated_capacity: number;
    available_capacity: number;
    reserved_capacity: number;
    sold_capacity: number;
    price_modifier: number;
    final_price: number;
  }>;
}> => {
  const response = await apiClient.get(`/events/sections/${sectionId}/ticket-types/`);
  return (response as { data: {
    ticket_types: Array<{
      id: string;
      section: {
        id: string;
        name: string;
      };
      ticket_type: {
        id: string;
        name: string;
        description: string;
        ticket_type: string;
        benefits: string[];
        age_min?: number;
        age_max?: number;
      };
      allocated_capacity: number;
      available_capacity: number;
      reserved_capacity: number;
      sold_capacity: number;
      price_modifier: number;
      final_price: number;
    }>;
  } }).data;
};

// Event Pricing with new system
export const getEventPricing = async (eventId: string): Promise<{
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
  pricing_breakdown: {
    base_price: number;
    options_total: number;
    discounts_total: number;
    fees_total: number;
    taxes_total: number;
    grand_total: number;
    currency: string;
    breakdown: {
      options: Array<{
        name: string;
        price: number;
        quantity: number;
        total: number;
      }>;
      discounts: Array<{
        name: string;
        type: string;
        value: number;
        amount: number;
      }>;
      fees: Array<{
        name: string;
        type: string;
        value: number;
        amount: number;
      }>;
    };
  };
}> => {
  const event = await getEventById(eventId);
  
  // Get base price from pricing summary
  const pricingSummaryValues = Object.values(event.pricing_summary || {});
  const basePrice = pricingSummaryValues.length > 0 ? pricingSummaryValues[0].base_price : 0;
  
  // Mock pricing breakdown (will be replaced with actual API call)
  const pricing_breakdown = {
    base_price: basePrice,
    options_total: 0,
    discounts_total: 0,
    fees_total: 0,
    taxes_total: 0,
    grand_total: basePrice,
    currency: 'USD',
    breakdown: {
      options: [],
      discounts: [],
      fees: [],
    },
  };
  
  return {
    pricing_summary: event.pricing_summary,
    pricing_breakdown
  };
};

export const getEventAvailability = async (eventId: string): Promise<{
  available_performances: EventPerformance[];
  is_available_today: boolean;
}> => {
  const event = await getEventById(eventId);
  return {
    available_performances: event.available_performances || [],
    is_available_today: event.is_available_today || false
  };
};

// Event filters and search utilities
export const getEventFilters = async (): Promise<{
  categories: EventCategory[];
  venues: Venue[];
  styles: Array<{ value: string; label: string }>;
}> => {
  try {
    const response = await apiClient.get('/events/filters/');
    const data = (response as { data?: { categories?: EventCategory[]; venues?: Venue[]; styles?: Array<{ value: string; label: string }> } }).data || {};
    return {
      categories: Array.isArray(data.categories) ? data.categories : [],
      venues: Array.isArray(data.venues) ? data.venues : [],
      styles: Array.isArray(data.styles) ? data.styles : [],
    };
  } catch {
    // Fallback if /events/filters/ is not implemented on backend
    const [categories, venues] = await Promise.all([
      getEventCategories().catch(() => []),
      getVenues().catch(() => []),
    ]);
    const styles: Array<{ value: string; label: string }> = [];
    return { categories, venues, styles };
  }
};

// Event statistics
export const getEventStats = async (eventId: string): Promise<{
  average_rating: number;
  review_count: number;
  total_performances: number;
  upcoming_performances: number;
}> => {
  const response = await apiClient.get(`/events/events/${eventId}/stats/`);
  return (response as { data: {
    average_rating: number;
    review_count: number;
    total_performances: number;
    upcoming_performances: number;
  } }).data;
}; 

// Cart integration for events
export const addEventToCart = async (eventCartData: {
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
  special_requirements?: string;
}): Promise<{
  message: string;
  cart_item_id: string;
  expires_at: string;
}> => {
  const response = await apiClient.post('/cart/add-event/', eventCartData);
  return (response as { data: {
    message: string;
    cart_item_id: string;
    expires_at: string;
  } }).data;
}; 