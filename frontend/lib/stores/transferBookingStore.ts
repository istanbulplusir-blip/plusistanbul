import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import * as transfersApi from '../api/transfers';

// Enhanced error types
export interface TransferBookingError {
  code: string;
  message: string;
  details?: unknown;
  retryable?: boolean;
}

export interface TransferBookingState {
  // Route & Vehicle
  route_id: string | null;
  route_data: transfersApi.TransferRoute | null;
  vehicle_type: string | null;
  
  // DateTime
  trip_type: 'one_way' | 'round_trip';
  outbound_date: string | null;
  outbound_time: string | null;
  return_date: string | null;
  return_time: string | null;
  
  // Passengers
  passenger_count: number;
  luggage_count: number;
  
  // Options
  selected_options: Array<{
    option_id: string;
    quantity: number;
    name?: string;
    price?: number;
    description?: string;
  }>;
  
  // Contact
  contact_name: string;
  contact_phone: string;
  special_requirements: string;
  
  // Pricing
  pricing_breakdown: transfersApi.TransferPriceCalculationResponse | null;
  final_price: number | null;
  
  // UI State
  current_step: 'route' | 'vehicle' | 'datetime' | 'passengers' | 'options' | 'contact' | 'summary';
  is_calculating_price: boolean;
  price_calculation_error: string | null;
  
  // Enhanced error handling
  errors: {
    route?: TransferBookingError;
    vehicle?: TransferBookingError;
    datetime?: TransferBookingError;
    passengers?: TransferBookingError;
    options?: TransferBookingError;
    contact?: TransferBookingError;
    summary?: TransferBookingError;
    general?: TransferBookingError;
  };
}

interface TransferBookingActions {
  // State updates
  updateBookingData: (updates: Partial<TransferBookingState>) => void;
  setRoute: (route: transfersApi.TransferRoute) => void;
  setVehicleType: (vehicleType: string) => void;
  setTripType: (tripType: 'one_way' | 'round_trip') => void;
  setDateTime: (date: string, time: string, isReturn?: boolean) => void;
  setPassengers: (passengerCount: number, luggageCount: number) => void;
  setOptions: (options: Array<{ 
    option_id: string; 
    quantity: number;
    name?: string;
    price?: number;
    description?: string;
  }>) => void;
  setContact: (contactData: {
    contact_name: string;
    contact_phone: string;
    special_requirements?: string;
  }) => void;
  setCurrentStep: (step: TransferBookingState['current_step']) => void;
  
  // Price calculation
  calculatePrice: () => Promise<void>;
  
  // Cart integration
  addToCart: () => Promise<{ success: boolean; error?: string }>;
  
  // Utilities
  clearBookingData: () => void;
  isStepValid: (step: TransferBookingState['current_step']) => boolean;
  getNextStep: () => TransferBookingState['current_step'] | null;
  getPreviousStep: () => TransferBookingState['current_step'] | null;
  
  // Enhanced error handling
  setError: (step: keyof TransferBookingState['errors'], error: TransferBookingError | null) => void;
  clearErrors: () => void;
}

const STEPS: TransferBookingState['current_step'][] = [
  'route', 'vehicle', 'datetime', 'passengers', 'options', 'contact', 'summary'
];

const initialState: TransferBookingState = {
  // Route & Vehicle
  route_id: null,
  route_data: null,
  vehicle_type: null,
  
  // DateTime
  trip_type: 'one_way',
  outbound_date: null,
  outbound_time: null,
  return_date: null,
  return_time: null,
  
  // Passengers
  passenger_count: 1,
  luggage_count: 0,
  
  // Options
  selected_options: [],
  
  // Contact
  contact_name: '',
  contact_phone: '',
  special_requirements: '',
  
  // Pricing
  pricing_breakdown: null,
  final_price: null,
  
  // UI State
  current_step: 'route',
  is_calculating_price: false,
  price_calculation_error: null,
  
  // Errors
  errors: {} as Record<string, never>,
};

export const useTransferBookingStore = create<TransferBookingState & TransferBookingActions>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      // State updates
      updateBookingData: (updates) => {
        set((state) => ({ ...state, ...updates }));
      },
      
      setRoute: (route) => {
        set((state) => ({
          ...state,
          route_id: route.id,
          route_data: route,
          errors: { ...state.errors, route: undefined }
        }));
      },
      
      setVehicleType: (vehicleType) => {
        set((state) => ({
          ...state,
          vehicle_type: vehicleType,
          errors: { ...state.errors, vehicle: undefined }
        }));
      },
      
      setTripType: (tripType) => {
        set((state) => ({
          ...state,
          trip_type: tripType,
          // Clear return data when switching to one way
          ...(tripType === 'one_way' && {
            return_date: null,
            return_time: null
          })
        }));
      },
      
      setDateTime: (date, time, isReturn = false) => {
        if (isReturn) {
          set((state) => ({
            ...state,
            return_date: date,
            return_time: time
          }));
        } else {
          set((state) => ({
            ...state,
            outbound_date: date,
            outbound_time: time
          }));
        }
      },
      
      setPassengers: (passengerCount, luggageCount) => {
        set((state) => ({
          ...state,
          passenger_count: passengerCount,
          luggage_count: luggageCount
        }));
      },
      
      setOptions: (options) => {
        set((state) => ({
          ...state,
          selected_options: options
        }));
      },
      
      setContact: (contactData) => {
        set((state) => ({
          ...state,
          ...contactData
        }));
      },
      
      setCurrentStep: (step) => {
        set((state) => ({ ...state, current_step: step }));
      },
      
      // Price calculation
      calculatePrice: async () => {
        const state = get();
        
        if (!state.route_id || !state.vehicle_type || !state.outbound_date || !state.outbound_time) {
          return;
        }
        
        set((state) => ({ ...state, is_calculating_price: true, price_calculation_error: null }));
        
        try {
          // Check if this is an agent booking context
          const isAgentContext = window.location.pathname.includes('/agent/');
          
          let pricingData;
          if (isAgentContext) {
            // Use agent pricing API
            const response = await fetch('/api/agents/pricing/transfer/', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                route_id: parseInt(state.route_id!),
                vehicle_type: state.vehicle_type!,
                passenger_count: state.passenger_count,
                trip_type: state.trip_type,
                hour: parseInt(state.outbound_time!.split(':')[0]),
                return_hour: state.trip_type === 'round_trip' && state.return_time ? 
                  parseInt(state.return_time.split(':')[0]) : undefined,
                selected_options: state.selected_options.map(opt => ({
                  id: opt.option_id,
                  name: opt.name || '',
                  price: opt.price || 0
                }))
              })
            });

            if (!response.ok) {
              throw new Error(`HTTP ${response.status}: Agent pricing failed`);
            }

            const result = await response.json();
            if (!result.success) {
              throw new Error(result.error || 'Agent pricing calculation failed');
            }

            pricingData = result;
          } else {
            // Use regular transfer pricing API
            pricingData = await transfersApi.calculateTransferPrice(state.route_id!, {
              vehicle_type: state.vehicle_type!,
              trip_type: state.trip_type,
              booking_time: state.outbound_time,
              return_time: state.trip_type === 'round_trip' && state.return_time ? state.return_time : undefined,
              selected_options: state.selected_options.map(opt => ({
                id: opt.option_id,
                quantity: opt.quantity
              }))
            });
          }
          
          // Adapt the response structure for both agent and regular pricing
          const adapted = isAgentContext ? {
            ...pricingData,
            price_breakdown: {
              base_price: pricingData.pricing?.base_price || 0,
              night_surcharge: pricingData.pricing?.night_surcharge || 0,
              options_total: pricingData.pricing?.options_total || 0,
              return_price: pricingData.pricing?.return_price || 0,
              return_discount: pricingData.pricing?.return_discount || 0,
              final_price: pricingData.pricing?.final_price || 0,
              agent_commission: pricingData.pricing?.agent_commission || 0,
              customer_price: pricingData.pricing?.customer_price || 0
            },
            trip_info: pricingData.trip_info || {
              vehicle_type: state.vehicle_type,
              is_round_trip: state.trip_type === 'round_trip',
              booking_time: state.outbound_time,
              return_time: state.return_time || undefined,
            },
            route_info: pricingData.trip_info || {
              origin: state.route_data?.origin || '',
              destination: state.route_data?.destination || '',
              name: state.route_data?.name || ''
            },
            capacity_info: pricingData.capacity_info || {
              is_valid: true,
              passenger_count: state.passenger_count,
              max_capacity: 4
            }
          } : {
            ...pricingData,
            trip_info: {
              vehicle_type: state.vehicle_type,
              is_round_trip: state.trip_type === 'round_trip',
              booking_time: state.outbound_time,
              return_time: state.return_time || undefined,
            },
            route_info: {
              origin: state.route_data?.origin || '',
              destination: state.route_data?.destination || '',
              name: state.route_data?.name || ''
            },
            time_info: {
              booking_hour: new Date().getHours(),
              time_category: 'standard',
              surcharge_percentage: 0
            },
          };
          
          set((state) => ({
            ...state,
            pricing_breakdown: adapted,
            final_price: adapted.price_breakdown?.final_price || adapted.price_breakdown?.customer_price || 0,
            is_calculating_price: false,
            price_calculation_error: null,
            errors: {
              ...state.errors,
              general: undefined
            }
          }));
        } catch (error: unknown) {
          const transferError: TransferBookingError = {
            code: (error as { code?: string })?.code || 'PRICE_CALCULATION_FAILED',
            message: (error as { message?: string })?.message || 'Failed to calculate price',
            details: error,
            retryable: true
          };
          
          set((state) => ({
            ...state,
            is_calculating_price: false,
            price_calculation_error: transferError.message,
            errors: {
              ...state.errors,
              general: transferError
            }
          }));
          
          throw transferError;
        }
      },
      
      // Cart integration
      addToCart: async () => {
        const state = get();
        
        if (!state.route_id || !state.vehicle_type || !state.outbound_date || !state.outbound_time) {
          return { success: false, error: 'Missing required booking data' };
        }
        
        try {
          // Check if this is an agent booking context
          const isAgentContext = window.location.pathname.includes('/agent/');
          
          if (isAgentContext) {
            // Use agent booking API with WhatsApp payment
            const bookingData = {
              customer_id: '', // This should be set by the agent booking page
              route_id: parseInt(state.route_id),
              vehicle_type: state.vehicle_type,
              passenger_count: state.passenger_count,
              trip_type: state.trip_type,
              booking_date: state.outbound_date,
              booking_time: state.outbound_time,
              return_time: state.trip_type === 'round_trip' && state.return_time ? state.return_time : null,
              selected_options: state.selected_options.map(opt => ({
                id: opt.option_id,
                name: opt.name || '',
                price: opt.price || 0
              })),
              customer_name: state.contact_name,
              customer_phone: state.contact_phone,
              customer_email: '', // Will be filled by agent
              payment_method: 'whatsapp'
            };

            const response = await fetch('/api/transfers/book/', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(bookingData)
            });

            if (!response.ok) {
              const errorData = await response.json().catch(() => ({}));
              throw new Error(errorData.error || `HTTP ${response.status}: Agent booking failed`);
            }

            const result = await response.json();
            if (!result.success) {
              throw new Error(result.error || 'Agent booking failed');
            }

            return { success: true, order_id: result.order_id };
          } else {
            // Use regular cart API for customer bookings
            const bookingData: transfersApi.TransferBookingRequest = {
              route_id: state.route_id,
              vehicle_type: state.vehicle_type,
              trip_type: state.trip_type,
              outbound_date: state.outbound_date,
              outbound_time: state.outbound_time,
              return_date: state.trip_type === 'round_trip' && state.return_date ? state.return_date : undefined,
              return_time: state.trip_type === 'round_trip' && state.return_time ? state.return_time : undefined,
              passenger_count: state.passenger_count,
              luggage_count: state.luggage_count,
              contact_name: state.contact_name,
              contact_phone: state.contact_phone,
              selected_options: state.selected_options.map(opt => ({
                id: opt.option_id,
                quantity: opt.quantity
              })),
              special_requirements: state.special_requirements || undefined,
              pickup_address: state.route_data?.origin || '',
              dropoff_address: state.route_data?.destination || '',
              pricing_breakdown: state.pricing_breakdown || undefined,
              final_price: state.final_price || undefined,
            };
            
            await transfersApi.addTransferToCart(bookingData);
            
            return { success: true };
          }
        } catch (error: unknown) {
          return { success: false, error: (error as { message?: string })?.message || 'Failed to add to cart' };
        }
      },
      
      // Utilities
      clearBookingData: () => {
        set(initialState);
      },
      
      // Step validation
      isStepValid: (step: TransferBookingState['current_step']) => {
        const state = get();
        
        switch (step) {
          case 'route':
            return Boolean(state.route_id && state.route_data);
          case 'vehicle':
            return Boolean(state.route_id && state.vehicle_type);
          case 'datetime':
            return Boolean(
              state.route_id && 
              state.vehicle_type && 
              state.outbound_date && 
              state.outbound_time &&
              // Add return validation for round trip
              (state.trip_type === 'one_way' || 
               (state.trip_type === 'round_trip' && state.return_date && state.return_time))
            );
          case 'passengers':
            return Boolean(
              state.route_id && 
              state.vehicle_type && 
              state.outbound_date && 
              state.outbound_time && 
              state.passenger_count > 0
            );
          case 'options':
            // Options are optional, but previous steps must be completed
            return Boolean(state.route_id && state.vehicle_type && state.outbound_date && state.outbound_time && state.passenger_count > 0);
          case 'contact':
            // Contact info required, and previous steps must be completed
            return Boolean(state.contact_name && state.contact_phone && state.route_id && state.vehicle_type && state.outbound_date && state.outbound_time && state.passenger_count > 0);
          case 'summary':
            // Summary requires all previous steps to be completed
            return Boolean(
              state.route_id && 
              state.vehicle_type && 
              state.outbound_date && 
              state.outbound_time && 
              state.passenger_count > 0 &&
              state.contact_name && 
              state.contact_phone
            );
          default:
            return false;
        }
      },
      
      getNextStep: () => {
        const state = get();
        const currentIndex = STEPS.indexOf(state.current_step);
        if (currentIndex < STEPS.length - 1) {
          return STEPS[currentIndex + 1];
        }
        return null;
      },
      
      getPreviousStep: () => {
        const state = get();
        const currentIndex = STEPS.indexOf(state.current_step);
        if (currentIndex > 0) {
          return STEPS[currentIndex - 1];
        }
        return null;
      },
      
      // Error handling
      setError: (step, error) => {
        set((state) => ({
          ...state,
          errors: { ...state.errors, [step]: error }
        }));
      },
      
      clearErrors: () => {
        set((state) => ({
          ...state,
          errors: {} as Record<string, never>
        }));
      },
    }),
    {
      name: 'transfer-booking-storage',
      version: 1,
      // Add hydration safety
      onRehydrateStorage: () => (state) => {
        // Ensure current_step is always valid after rehydration
        if (state && !STEPS.includes(state.current_step)) {
          state.current_step = 'route';
        }
      },
      partialize: (state) => ({
        // Only persist essential data, not UI state
        route_id: state.route_id,
        route_data: state.route_data,
        vehicle_type: state.vehicle_type,
        trip_type: state.trip_type,
        outbound_date: state.outbound_date,
        outbound_time: state.outbound_time,
        return_date: state.return_date,
        return_time: state.return_time,
        passenger_count: state.passenger_count,
        luggage_count: state.luggage_count,
        selected_options: state.selected_options,
        contact_name: state.contact_name,
        contact_phone: state.contact_phone,
        special_requirements: state.special_requirements,
        pricing_breakdown: state.pricing_breakdown,
        final_price: state.final_price,
      }),
    }
  )
); 