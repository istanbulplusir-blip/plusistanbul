import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import * as carRentalsApi from '../api/car-rentals';

// Enhanced error types
export interface CarRentalBookingError {
  field: string;
  message: string;
  details?: unknown;
  retryable?: boolean;
}

export interface CarRentalBookingState {
  // Car Selection
  car_rental_id: string | null;
  car_rental_data: carRentalsApi.CarRental | null;
  
  // Rental Period
  pickup_date: string | null;
  dropoff_date: string | null;
  pickup_time: string | null;
  dropoff_time: string | null;
  pickup_location: string;
  dropoff_location: string;
  pickup_location_type: 'predefined' | 'custom';
  dropoff_location_type: 'predefined' | 'custom' | 'same_as_pickup';
  pickup_location_id: string | null;
  dropoff_location_id: string | null;
  pickup_location_coordinates: { lat: number; lng: number } | null;
  dropoff_location_coordinates: { lat: number; lng: number } | null;
  rental_days: number;
  rental_hours: number;
  total_hours: number;
  rental_type: 'hourly' | 'daily' | null;
  
  // Driver Information
  driver_name: string;
  driver_license: string;
  driver_phone: string;
  driver_email: string;
  additional_drivers: Array<{
    name: string;
    license: string;
    phone: string;
  }>;
  
  // Options & Insurance
  selected_options: Array<{
    id: string;
    quantity: number;
    name?: string;
    price?: string;
    price_type?: 'fixed' | 'daily' | 'percentage';
    price_percentage?: number;
    description?: string;
  }>;
  basic_insurance: boolean;
  comprehensive_insurance: boolean;
  special_requirements: string;
  
  // Pricing
  pricing_breakdown: {
    base_price: number;
    daily_rate: number;
    hourly_rate: number;
    weekly_discount: number;
    monthly_discount: number;
    options_total: number;
    insurance_total: number;
    final_price: number;
    rental_type: 'hourly' | 'daily' | null;
    rental_days: number;
    rental_hours: number;
    total_hours: number;
  } | null;
  total_price: number | null;
  currency: string;
  
  // UI State
  current_step: 'car' | 'dates' | 'driver' | 'options' | 'summary';
  is_calculating_price: boolean;
  price_calculation_error: string | null;
  is_booking: boolean;
  booking_error: string | null;
  
  // Enhanced error handling
  errors: {
    car?: CarRentalBookingError;
    dates?: CarRentalBookingError;
    driver?: CarRentalBookingError;
    options?: CarRentalBookingError;
    summary?: CarRentalBookingError;
    general?: CarRentalBookingError;
  };
}

interface CarRentalBookingActions {
  // State updates
  updateBookingData: (updates: Partial<CarRentalBookingState>) => void;
  
  // Car selection
  setCarRental: (car: carRentalsApi.CarRental) => void;
  
  // Date selection
  setRentalDates: (pickupDate: string, dropoffDate: string, pickupTime: string, dropoffTime: string) => void;
  setRentalLocations: (pickupLocation: string, dropoffLocation: string) => void;
  setPickupLocation: (location: string, type: 'predefined' | 'custom', locationId?: string, coordinates?: { lat: number; lng: number }) => void;
  setDropoffLocation: (location: string, type: 'predefined' | 'custom' | 'same_as_pickup', locationId?: string, coordinates?: { lat: number; lng: number }) => void;
  
  // Driver information
  setDriverInfo: (driverData: {
    driver_name: string;
    driver_license: string;
    driver_phone: string;
    driver_email: string;
    additional_drivers?: Array<{
      name: string;
      license: string;
      phone: string;
    }>;
  }) => void;
  
  // Options
  setSelectedOptions: (options: Array<{
    id: string;
    quantity: number;
    name?: string;
    price?: string;
    price_type?: 'fixed' | 'daily' | 'percentage';
    price_percentage?: number;
    description?: string;
  }>) => void;
  setInsurance: (basic: boolean, comprehensive: boolean) => void;
  setSpecialRequirements: (requirements: string) => void;
  
  // Pricing
  calculatePricing: () => Promise<void>;
  setPricingBreakdown: (breakdown: CarRentalBookingState['pricing_breakdown']) => void;
  
  // UI State
  setCurrentStep: (step: CarRentalBookingState['current_step']) => void;
  nextStep: () => void;
  previousStep: () => void;
  resetBooking: () => void;
  
  // Error handling
  setError: (field: keyof CarRentalBookingState['errors'], error: CarRentalBookingError | null) => void;
  clearErrors: () => void;
  
  // Booking
  createBooking: () => Promise<{ success: boolean; booking_id?: string; error?: string }>;
}

const STEPS: CarRentalBookingState['current_step'][] = [
  'car', 'dates', 'driver', 'options', 'summary'
];

const initialState: CarRentalBookingState = {
  // Car Selection
  car_rental_id: null,
  car_rental_data: null,
  
  // Rental Period
  pickup_date: null,
  dropoff_date: null,
  pickup_time: null,
  dropoff_time: null,
  pickup_location: '',
  dropoff_location: '',
  pickup_location_type: 'predefined',
  dropoff_location_type: 'same_as_pickup',
  pickup_location_id: null,
  dropoff_location_id: null,
  pickup_location_coordinates: null,
  dropoff_location_coordinates: null,
  rental_days: 0,
  rental_hours: 0,
  total_hours: 0,
  rental_type: null,
  
  // Driver Information
  driver_name: '',
  driver_license: '',
  driver_phone: '',
  driver_email: '',
  additional_drivers: [],
  
  // Options & Insurance
  selected_options: [],
  basic_insurance: true,
  comprehensive_insurance: false,
  special_requirements: '',
  
  // Pricing
  pricing_breakdown: null,
  total_price: null,
  currency: 'USD',
  
  // UI State
  current_step: 'car',
  is_calculating_price: false,
  price_calculation_error: null,
  is_booking: false,
  booking_error: null,
  
  // Errors
  errors: {} as Record<string, never>,
};

export const useCarRentalBookingStore = create<CarRentalBookingState & CarRentalBookingActions>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      // State updates
      updateBookingData: (updates) => {
        set((state) => ({ ...state, ...updates }));
      },
      
      // Car selection
      setCarRental: (car) => {
        set((state) => ({
          ...state,
          car_rental_id: car.id,
          car_rental_data: car,
          currency: car.currency,
          errors: { ...state.errors, car: undefined }
        }));
      },
      
      // Date selection
      setRentalDates: (pickupDate, dropoffDate, pickupTime, dropoffTime) => {
        console.log('Store setRentalDates called:', { pickupDate, dropoffDate, pickupTime, dropoffTime });
        let rentalDays = 0;
        let rentalHours = 0;
        let totalHours = 0;
        let rentalType: 'hourly' | 'daily' | null = null;
        
        // Only calculate rental duration if both dates and times are valid
        if (pickupDate && dropoffDate && pickupTime && dropoffTime) {
          const pickup = new Date(`${pickupDate} ${pickupTime}`);
          const dropoff = new Date(`${dropoffDate} ${dropoffTime}`);
          
          // Check if dates are valid
          if (!isNaN(pickup.getTime()) && !isNaN(dropoff.getTime())) {
            const durationMs = dropoff.getTime() - pickup.getTime();
            totalHours = durationMs / (1000 * 60 * 60);
            
            if (pickupDate === dropoffDate) {
              // Same day rental (hourly)
              rentalType = 'hourly';
              rentalDays = 0;
              rentalHours = Math.ceil(totalHours);
            } else {
              // Multi-day rental - calculate days as difference between dates
              const pickupDateObj = new Date(pickupDate);
              const dropoffDateObj = new Date(dropoffDate);
              const daysDiff = Math.floor((dropoffDateObj.getTime() - pickupDateObj.getTime()) / (1000 * 60 * 60 * 24));

              rentalType = 'daily';
              rentalDays = daysDiff;
              rentalHours = Math.floor(totalHours % 24);
            }
          }
        }
        
        set((state) => {
          console.log('Store state updated:', { pickupDate, dropoffDate, pickupTime, dropoffTime, rentalDays, rentalHours, totalHours, rentalType });
          return {
            ...state,
            pickup_date: pickupDate,
            dropoff_date: dropoffDate,
            pickup_time: pickupTime,
            dropoff_time: dropoffTime,
            rental_days: rentalDays,
            rental_hours: rentalHours,
            total_hours: totalHours,
            rental_type: rentalType,
            errors: { ...state.errors, dates: undefined }
          };
        });
        
        // Recalculate pricing when dates change (only if both dates are set)
        if (pickupDate && dropoffDate) {
          get().calculatePricing();
        }
      },
      
      setRentalLocations: (pickupLocation, dropoffLocation) => {
        set((state) => ({
          ...state,
          pickup_location: pickupLocation,
          dropoff_location: dropoffLocation,
          errors: { ...state.errors, dates: undefined }
        }));
      },
      
      setPickupLocation: (location, type, locationId, coordinates) => {
        set((state) => ({
          ...state,
          pickup_location: location,
          pickup_location_type: type,
          pickup_location_id: locationId || null,
          pickup_location_coordinates: coordinates || null,
          errors: { ...state.errors, pickup_location: undefined }
        }));
      },
      
      setDropoffLocation: (location, type, locationId, coordinates) => {
        set((state) => ({
          ...state,
          dropoff_location: location,
          dropoff_location_type: type,
          dropoff_location_id: locationId || null,
          dropoff_location_coordinates: coordinates || null,
          errors: { ...state.errors, dropoff_location: undefined }
        }));
      },
      
      // Driver information
      setDriverInfo: (driverData) => {
        set((state) => ({
          ...state,
          ...driverData,
          errors: { ...state.errors, driver: undefined }
        }));
      },
      
      // Options
      setSelectedOptions: (options) => {
        set((state) => ({
          ...state,
          selected_options: options,
          errors: { ...state.errors, options: undefined }
        }));
        
        // Recalculate pricing when options change
        get().calculatePricing();
      },
      
      setInsurance: (basic, comprehensive) => {
        set((state) => ({
          ...state,
          basic_insurance: basic,
          comprehensive_insurance: comprehensive
        }));
        
        // Recalculate pricing when insurance changes
        get().calculatePricing();
      },
      
      setSpecialRequirements: (requirements) => {
        set((state) => ({
          ...state,
          special_requirements: requirements
        }));
      },
      
      // Pricing
      calculatePricing: async () => {
        const state = get();
        if (!state.car_rental_id || !state.pickup_date || !state.dropoff_date || !state.pickup_time || !state.dropoff_time) {
          return;
        }
        
        set((state) => ({
          ...state,
          is_calculating_price: true,
          price_calculation_error: null
        }));
        
        try {
          console.log('Calling API for pricing calculation...');
          const availabilityResponse = await carRentalsApi.checkCarRentalAvailability(
            state.car_rental_data?.slug || state.car_rental_id,
            {
              pickup_date: state.pickup_date,
              dropoff_date: state.dropoff_date,
              pickup_time: state.pickup_time,
              dropoff_time: state.dropoff_time
            }
          );
          
          console.log('API Response:', availabilityResponse);
          
          if (!availabilityResponse.available) {
            throw new Error('Car is not available for the selected dates');
          }
          
          // Use API pricing breakdown directly (backend handles all calculations)
          const apiPricingBreakdown = availabilityResponse.pricing_breakdown || {};
          
          // Get base price from API (backend calculates correctly)
          const apiBasePrice = typeof apiPricingBreakdown.base_price === 'number' 
            ? apiPricingBreakdown.base_price 
            : parseFloat(String(apiPricingBreakdown.base_price || '0'));
          
          // Get insurance price from API (backend calculates correctly)
          const apiInsurancePrice = typeof apiPricingBreakdown.insurance_total === 'number'
            ? apiPricingBreakdown.insurance_total
            : parseFloat(String(apiPricingBreakdown.insurance_total || '0'));
          
          // Calculate options total based on option type
          let optionsTotal = 0;
          for (const option of state.selected_options) {
            if (option.price) {
              const optionPrice = typeof option.price === 'string' 
                ? parseFloat(option.price) 
                : option.price;
              
              if (option.price_type === 'fixed') {
                // Fixed price options are constant regardless of rental duration
                optionsTotal += optionPrice * option.quantity;
              } else if (option.price_type === 'daily') {
                // Daily price options multiply by rental days
                optionsTotal += optionPrice * option.quantity * state.rental_days;
              } else if (option.price_type === 'percentage') {
                // Percentage options are calculated as percentage of base price
                optionsTotal += (apiBasePrice * (option.price_percentage || 0) / 100) * option.quantity;
              }
            }
          }
          
          const finalPrice = apiBasePrice + optionsTotal + apiInsurancePrice;
          
          const pricingBreakdown = {
            base_price: apiBasePrice,
            daily_rate: typeof (apiPricingBreakdown as Record<string, unknown>).daily_rate === 'number'
              ? (apiPricingBreakdown as Record<string, unknown>).daily_rate as number
              : parseFloat(String((apiPricingBreakdown as Record<string, unknown>).daily_rate || '0')),
            hourly_rate: typeof (apiPricingBreakdown as Record<string, unknown>).hourly_rate === 'number'
              ? (apiPricingBreakdown as Record<string, unknown>).hourly_rate as number
              : parseFloat(String((apiPricingBreakdown as Record<string, unknown>).hourly_rate || '0')),
            weekly_discount: typeof apiPricingBreakdown.weekly_discount === 'number'
              ? apiPricingBreakdown.weekly_discount
              : parseFloat(String(apiPricingBreakdown.weekly_discount || '0')),
            monthly_discount: typeof apiPricingBreakdown.monthly_discount === 'number'
              ? apiPricingBreakdown.monthly_discount
              : parseFloat(String(apiPricingBreakdown.monthly_discount || '0')),
            options_total: optionsTotal,
            insurance_total: apiInsurancePrice,
            final_price: finalPrice,
            rental_type: (apiPricingBreakdown as Record<string, unknown>).rental_type as 'hourly' | 'daily' | null || state.rental_type,
            rental_days: state.rental_days,
            rental_hours: state.rental_hours,
            total_hours: state.total_hours
          };
          
          console.log('Pricing calculation:', pricingBreakdown);
          
          set((state) => ({
            ...state,
            pricing_breakdown: pricingBreakdown,
            total_price: pricingBreakdown.final_price,
            is_calculating_price: false,
            price_calculation_error: null
          }));
        } catch (error) {
          console.error('Car rental pricing calculation error:', error);
          set((state) => ({
            ...state,
            is_calculating_price: false,
            price_calculation_error: error instanceof Error ? error.message : 'Failed to calculate pricing'
          }));
        }
      },
      
      setPricingBreakdown: (breakdown) => {
        set((state) => ({
          ...state,
          pricing_breakdown: breakdown,
          total_price: breakdown?.final_price || null
        }));
      },
      
      // UI State
      setCurrentStep: (step) => {
        set((state) => ({ ...state, current_step: step }));
      },
      
      nextStep: () => {
        set((state) => {
          const currentIndex = STEPS.indexOf(state.current_step);
          const nextIndex = Math.min(currentIndex + 1, STEPS.length - 1);
          return { ...state, current_step: STEPS[nextIndex] };
        });
      },
      
      previousStep: () => {
        set((state) => {
          const currentIndex = STEPS.indexOf(state.current_step);
          const prevIndex = Math.max(currentIndex - 1, 0);
          return { ...state, current_step: STEPS[prevIndex] };
        });
      },
      
      resetBooking: () => {
        set(initialState);
      },
      
      // Error handling
      setError: (field, error) => {
        set((state) => ({
          ...state,
          errors: { ...state.errors, [field]: error }
        }));
      },
      
      clearErrors: () => {
        set((state) => ({
          ...state,
          errors: {} as Record<string, never>
        }));
      },
      
      // Booking
      createBooking: async () => {
        const state = get();
        
        if (!state.car_rental_id || !state.pickup_date || !state.dropoff_date || !state.pickup_time || !state.dropoff_time) {
          return { success: false, error: 'Missing required booking information' };
        }
        
        set((state) => ({
          ...state,
          is_booking: true,
          booking_error: null
        }));
        
        try {
          const bookingParams: carRentalsApi.CarRentalBookingParams = {
            car_rental_id: state.car_rental_id,
            pickup_date: state.pickup_date,
            dropoff_date: state.dropoff_date,
            pickup_time: state.pickup_time,
            dropoff_time: state.dropoff_time,
            driver_name: state.driver_name,
            driver_license: state.driver_license,
            driver_phone: state.driver_phone,
            driver_email: state.driver_email,
            selected_options: state.selected_options.map(opt => ({
              id: opt.id,
              quantity: opt.quantity
            })),
            basic_insurance: state.basic_insurance,
            comprehensive_insurance: state.comprehensive_insurance,
            special_requirements: state.special_requirements
          };
          
          const response = await carRentalsApi.createCarRentalBooking(bookingParams);
          
          set((state) => ({
            ...state,
            is_booking: false,
            booking_error: null
          }));
          
          return { success: true, booking_id: response.id };
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to create booking';
          
          set((state) => ({
            ...state,
            is_booking: false,
            booking_error: errorMessage
          }));
          
          return { success: false, error: errorMessage };
        }
      },
    }),
    {
      name: 'car-rental-booking-storage',
      version: 1,
      onRehydrateStorage: () => (state) => {
        // Ensure current_step is always valid after rehydration
        if (state && !STEPS.includes(state.current_step)) {
          state.current_step = 'car';
        }
      },
      partialize: (state) => ({
        // Only persist essential data, not UI state
        car_rental_id: state.car_rental_id,
        car_rental_data: state.car_rental_data,
        pickup_date: state.pickup_date,
        dropoff_date: state.dropoff_date,
        pickup_time: state.pickup_time,
        dropoff_time: state.dropoff_time,
        pickup_location: state.pickup_location,
        dropoff_location: state.dropoff_location,
        pickup_location_type: state.pickup_location_type,
        dropoff_location_type: state.dropoff_location_type,
        pickup_location_id: state.pickup_location_id,
        dropoff_location_id: state.dropoff_location_id,
        pickup_location_coordinates: state.pickup_location_coordinates,
        dropoff_location_coordinates: state.dropoff_location_coordinates,
        rental_days: state.rental_days,
        driver_name: state.driver_name,
        driver_license: state.driver_license,
        driver_phone: state.driver_phone,
        driver_email: state.driver_email,
        additional_drivers: state.additional_drivers,
        selected_options: state.selected_options,
        basic_insurance: state.basic_insurance,
        comprehensive_insurance: state.comprehensive_insurance,
        special_requirements: state.special_requirements,
        pricing_breakdown: state.pricing_breakdown,
        total_price: state.total_price,
        currency: state.currency,
      }),
    }
  )
);
