'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAgentTranslations } from '@/lib/hooks/useAgentTranslations';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { useLocale } from 'next-intl';
import { useUnifiedCurrency } from '@/lib/contexts/UnifiedCurrencyContext';
import { cn } from '@/lib/utils';
import { 
  CheckIcon, 
  InformationCircleIcon, 
  TruckIcon,
  CheckCircleIcon,
  ArrowLeftIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';
import { TransferRoute, TransferVehicle, TransferPricing } from '@/lib/api/agents';
import { 
  validateTransferBooking, 
  validateTransferCapacity, 
  validateTimeSurcharges,
  validateRoundTripDiscount,
  getDefaultRouteConstraints,
  getDefaultVehicleCapacities,
  type TransferBookingData as ValidationBookingData,
  type VehicleCapacity,
  type RouteConstraints
} from '@/lib/utils/transferValidation';

interface TransferBookingData {
  customer_id: string;
  route_id: number;
  vehicle_type: string;
  booking_date: string;
  booking_time: string;
  passenger_count: number;
  luggage_count: number;
  trip_type: 'one_way' | 'round_trip';
  return_date?: string;
  return_time?: string;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
    name?: string;
    price?: number;
  }>;
  special_requests?: string;
  notes?: string;
  customer_name?: string;
  customer_phone?: string;
  customer_email?: string;
  payment_method?: string;
}

// Using imported TransferRoute from @/lib/api/agents

// Using imported TransferVehicle from @/lib/api/agents
type VehicleType = TransferVehicle;

interface TransferOption {
  id: string;
  name: string;
  description: string;
  price: number;
  option_type: string;
  price_type: string;
  max_quantity?: number;
  is_active: boolean;
}

interface BookingStep {
  id: string;
  title: string;
  description: string;
  isCompleted: boolean;
  component: React.ComponentType<BookingStepProps>;
}

interface BookingStepProps {
  bookingData: TransferBookingData;
  onComplete: (data: Partial<TransferBookingData>) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
  validationErrors: Record<string, string>;
  setValidationErrors: (errors: Record<string, string>) => void;
}

export default function AgentTransferBookingPage() {
  const t = useAgentTranslations();
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
    customers,
    loadCustomers,
    bookTransfer,
    getPricingPreview,
    loading,
    agent, // اضافه کردن agent
    loadDashboard, // اضافه کردن loadDashboard
  } = useAgent();
  
  const { currency: unifiedCurrency } = useUnifiedCurrency();

  // State for booking data
  const [bookingData, setBookingData] = useState<TransferBookingData>({
    customer_id: '',
    route_id: 0,
    vehicle_type: '',
    booking_date: '',
    booking_time: '',
    passenger_count: 1,
    luggage_count: 0,
    trip_type: 'one_way',
    selected_options: [],
    special_requests: '',
    notes: ''
  });

  // State for UI
  const [currentStep, setCurrentStep] = useState(0);
  const [routes, setRoutes] = useState<TransferRoute[]>([]);
  const [vehicleTypes, setVehicleTypes] = useState<VehicleType[]>([]);
  const [options, setOptions] = useState<TransferOption[]>([]);
  const [pricing, setPricing] = useState<TransferPricing | null>(null);
  const [loadingPricing, setLoadingPricing] = useState(false);
  const [loadingRoutes, setLoadingRoutes] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [validationWarnings, setValidationWarnings] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Step component definitions (defined before steps array)
  const RouteSelectorStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => (
    <div className="space-y-4">
      {loadingRoutes && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600 dark:text-gray-400">{t.transfer.calculatingPricing || 'Loading routes...'}</span>
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}
      
      {routes.length === 0 && !loadingRoutes && !error && (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">{t.transfer.pricingNotAvailable || 'No transfer routes found.'}</p>
        </div>
      )}
      
      {routes.length > 0 && (
        <div className="grid gap-4">
          {routes.map((route) => (
            <div
              key={route.id}
              className={cn(
                "p-4 border rounded-lg cursor-pointer transition-all duration-200",
                bookingData.route_id === route.id
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
              )}
              onClick={() => onComplete({ route_id: route.id })}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {route.origin} → {route.destination}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    مدت زمان: {route.estimated_duration} دقیقه
                  </p>
                  {route.vehicle_types && route.vehicle_types.length > 0 && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      از {formatCurrency(route.vehicle_types[0].base_price)} شروع می‌شود
                    </p>
                  )}
                </div>
                <div className="flex items-center">
                  {bookingData.route_id === route.id && (
                    <CheckIcon className="w-5 h-5 text-blue-600" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {validationErrors.routes && (
        <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.routes}</p>
      )}
    </div>
  );
  
  const VehicleSelectorStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => {
    const selectedRoute = routes.find(route => route.id === bookingData.route_id);
    const availableVehicles = selectedRoute?.vehicle_types || [];
    
    return (
      <div className="space-y-4">
        {!selectedRoute && (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">Please select a route first.</p>
          </div>
        )}
        
        {selectedRoute && availableVehicles.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">No vehicles found for this route.</p>
          </div>
        )}
        
        {availableVehicles.length > 0 && (
          <div className="grid gap-4">
            {availableVehicles.map((vehicle, index) => (
              <div
                key={vehicle.type}
                className={cn(
                  "p-4 border rounded-lg cursor-pointer transition-all duration-200",
                  bookingData.vehicle_type === vehicle.type
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                    : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                )}
                onClick={() => onComplete({ vehicle_type: vehicle.type })}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {vehicle.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {vehicle.features?.join(', ') || 'Standard features'}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Capacity: {vehicle.capacity} passengers
                    </p>
                    <p className="text-sm font-medium text-green-600 dark:text-green-400">
                      Price: {formatCurrency(vehicle.base_price)}
                    </p>
                  </div>
                  <div className="flex items-center">
                    {bookingData.vehicle_type === vehicle.type && (
                      <CheckIcon className="w-5 h-5 text-blue-600" />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {validationErrors.vehicle_type && (
          <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.vehicle_type}</p>
        )}
      </div>
    );
  };
  
  const DateTimeSelectorStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => {
    const today = new Date().toISOString().split('T')[0];
    const [selectedDate, setSelectedDate] = useState(bookingData.booking_date || today);
    const [selectedTime, setSelectedTime] = useState(bookingData.booking_time || '');
    const [isRoundTrip, setIsRoundTrip] = useState(bookingData.trip_type === 'round_trip');
    const [returnDate, setReturnDate] = useState(bookingData.return_date || '');
    const [returnTime, setReturnTime] = useState(bookingData.return_time || '');

    // Calculate minimum time (2 hours from now)
    const getMinimumTime = () => {
      const now = new Date();
      const minTime = new Date(now.getTime() + 2 * 60 * 60 * 1000); // 2 hours from now
      return minTime.toTimeString().slice(0, 5);
    };

    // Calculate minimum return time (2 hours after departure)
    const getMinimumReturnTime = () => {
      if (!selectedDate || !selectedTime) return '';
      const departureDateTime = new Date(`${selectedDate}T${selectedTime}`);
      const minReturnTime = new Date(departureDateTime.getTime() + 2 * 60 * 60 * 1000); // 2 hours after departure
      return minReturnTime.toTimeString().slice(0, 5);
    };

    const handleDateChange = (date: string) => {
      setSelectedDate(date);
      onComplete({ booking_date: date });
      
      // If it's today, ensure time is at least 2 hours from now
      if (date === today && selectedTime) {
        const minTime = getMinimumTime();
        if (selectedTime < minTime) {
          setSelectedTime(minTime);
          onComplete({ booking_time: minTime });
        }
      }
    };

    const handleTimeChange = (time: string) => {
      // Validate minimum time for today's bookings
      if (selectedDate === today) {
        const minTime = getMinimumTime();
        if (time < minTime) {
          setValidationErrors(prev => ({
            ...prev,
            booking_time: `زمان رفت باید حداقل ۲ ساعت از الان باشد. حداقل زمان: ${minTime}`
          }));
          return;
        }
      }
      
      setSelectedTime(time);
      onComplete({ booking_time: time });
      
      // Clear time validation error
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.booking_time;
        return newErrors;
      });
    };

    const handleTripTypeChange = (tripType: 'one_way' | 'round_trip') => {
      setIsRoundTrip(tripType === 'round_trip');
      onComplete({ trip_type: tripType });
      
      // Clear return time if switching to one way
      if (tripType === 'one_way') {
        setReturnDate('');
        setReturnTime('');
        onComplete({ return_date: '', return_time: '' });
      }
    };

    const handleReturnDateChange = (date: string) => {
      setReturnDate(date);
      onComplete({ return_date: date });
      
      // If return date is same as departure date, ensure return time is at least 2 hours after departure
      if (date === selectedDate && returnTime) {
        const minReturnTime = getMinimumReturnTime();
        if (returnTime < minReturnTime) {
          setReturnTime(minReturnTime);
          onComplete({ return_time: minReturnTime });
        }
      }
    };

    const handleReturnTimeChange = (time: string) => {
      // Validate minimum return time (2 hours after departure)
      if (selectedDate && selectedTime && returnDate === selectedDate) {
        const minReturnTime = getMinimumReturnTime();
        if (time < minReturnTime) {
          setValidationErrors(prev => ({
            ...prev,
            return_time: `زمان برگشت باید حداقل ۲ ساعت بعد از زمان رفت باشد. حداقل زمان: ${minReturnTime}`
          }));
          return;
        }
      }
      
      setReturnTime(time);
      onComplete({ return_time: time });
      
      // Clear return time validation error
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.return_time;
        return newErrors;
      });
    };

    return (
      <div className="space-y-6">
        {/* Trip Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            نوع سفر
          </label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => handleTripTypeChange('one_way')}
              className={cn(
                "p-4 border rounded-lg text-center transition-all duration-200",
                !isRoundTrip
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                  : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
              )}
            >
              <div className="font-medium">یک طرفه</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">فقط رفت</div>
            </button>
            <button
              type="button"
              onClick={() => handleTripTypeChange('round_trip')}
              className={cn(
                "p-4 border rounded-lg text-center transition-all duration-200",
                isRoundTrip
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                  : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
              )}
            >
              <div className="font-medium">رفت و برگشت</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">با تخفیف</div>
            </button>
          </div>
        </div>

        {/* Outbound Date and Time */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              تاریخ رفت
            </label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => handleDateChange(e.target.value)}
              min={today}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              زمان رفت
            </label>
            <input
              type="time"
              value={selectedTime}
              onChange={(e) => handleTimeChange(e.target.value)}
              min={selectedDate === today ? getMinimumTime() : undefined}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
            {selectedDate === today && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                حداقل زمان: {getMinimumTime()} (۲ ساعت از الان)
              </p>
            )}
          </div>
        </div>

        {/* Return Date and Time (only for round trip) */}
        {isRoundTrip && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                تاریخ برگشت
              </label>
              <input
                type="date"
                value={returnDate}
                onChange={(e) => handleReturnDateChange(e.target.value)}
                min={selectedDate}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                زمان برگشت
              </label>
              <input
                type="time"
                value={returnTime}
                onChange={(e) => handleReturnTimeChange(e.target.value)}
                min={returnDate === selectedDate ? getMinimumReturnTime() : undefined}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
              {returnDate === selectedDate && selectedTime && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  حداقل زمان: {getMinimumReturnTime()} (۲ ساعت بعد از رفت)
                </p>
              )}
            </div>
          </div>
        )}

        {/* Validation Errors */}
        {(validationErrors.booking_date || validationErrors.booking_time || validationErrors.return_date || validationErrors.return_time) && (
          <div className="space-y-1">
            {validationErrors.booking_date && (
              <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.booking_date}</p>
            )}
            {validationErrors.booking_time && (
              <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.booking_time}</p>
            )}
            {validationErrors.return_date && (
              <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.return_date}</p>
            )}
            {validationErrors.return_time && (
              <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.return_time}</p>
            )}
          </div>
        )}
      </div>
    );
  };
  
  const PassengersSelectorStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => {
    const [passengerCount, setPassengerCount] = useState(bookingData.passenger_count || 1);
    const [luggageCount, setLuggageCount] = useState(bookingData.luggage_count || 0);
    
    const selectedRoute = routes.find(route => route.id === bookingData.route_id);
    const selectedVehicle = selectedRoute?.vehicle_types?.find(vehicle => vehicle.type === bookingData.vehicle_type);
    const maxCapacity = selectedVehicle?.capacity || 4;
    const maxLuggage = 4; // Default luggage capacity

    const handlePassengerChange = (count: number) => {
      if (count >= 1 && count <= maxCapacity) {
        setPassengerCount(count);
        onComplete({ passenger_count: count });
        
        // Clear validation errors
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors.passenger_count;
          return newErrors;
        });
      } else if (count > maxCapacity) {
        setValidationErrors(prev => ({
          ...prev,
          passenger_count: `تعداد مسافران نمی‌تواند بیشتر از ظرفیت خودرو (${maxCapacity} نفر) باشد`
        }));
      }
    };

    const handleLuggageChange = (count: number) => {
      if (count >= 0 && count <= maxLuggage) {
        setLuggageCount(count);
        onComplete({ luggage_count: count });
        
        // Clear validation errors
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors.luggage_count;
          return newErrors;
        });
      } else if (count > maxLuggage) {
        setValidationErrors(prev => ({
          ...prev,
          luggage_count: `تعداد چمدان نمی‌تواند بیشتر از ظرفیت خودرو (${maxLuggage} عدد) باشد`
        }));
      }
    };

    return (
      <div className="space-y-6">
        {/* Passenger Count */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Number of Passengers
          </label>
          <div className="flex items-center space-x-4 space-x-reverse">
            <button
              type="button"
              onClick={() => handlePassengerChange(passengerCount - 1)}
              disabled={passengerCount <= 1}
              className="w-10 h-10 rounded-full border border-gray-300 dark:border-gray-600 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              -
            </button>
            <span className="text-2xl font-medium text-gray-900 dark:text-white min-w-[3rem] text-center">
              {passengerCount}
            </span>
            <button
              type="button"
              onClick={() => handlePassengerChange(passengerCount + 1)}
              disabled={passengerCount >= maxCapacity}
              className={cn(
                "w-10 h-10 rounded-full border flex items-center justify-center transition-colors",
                passengerCount >= maxCapacity
                  ? "border-gray-200 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed"
                  : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
              )}
            >
              +
            </button>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            حداکثر ظرفیت: {maxCapacity} نفر
          </p>
        </div>

        {/* Luggage Count */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            تعداد چمدان
          </label>
          <div className="flex items-center space-x-4 space-x-reverse">
            <button
              type="button"
              onClick={() => handleLuggageChange(luggageCount - 1)}
              disabled={luggageCount <= 0}
              className="w-10 h-10 rounded-full border border-gray-300 dark:border-gray-600 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              -
            </button>
            <span className="text-2xl font-medium text-gray-900 dark:text-white min-w-[3rem] text-center">
              {luggageCount}
            </span>
            <button
              type="button"
              onClick={() => handleLuggageChange(luggageCount + 1)}
              disabled={luggageCount >= maxLuggage}
              className={cn(
                "w-10 h-10 rounded-full border flex items-center justify-center transition-colors",
                luggageCount >= maxLuggage
                  ? "border-gray-200 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed"
                  : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
              )}
            >
              +
            </button>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            حداکثر ظرفیت چمدان: {maxLuggage} عدد
          </p>
        </div>

        {/* Capacity Warning */}
        {passengerCount > maxCapacity && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-200 text-sm">
              Passenger count ({passengerCount}) exceeds vehicle capacity ({maxCapacity}).
            </p>
          </div>
        )}

        {/* Validation Errors */}
        {(validationErrors.passenger_count || validationErrors.luggage_count) && (
          <div className="space-y-1">
            {validationErrors.passenger_count && (
              <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.passenger_count}</p>
            )}
            {validationErrors.luggage_count && (
              <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.luggage_count}</p>
            )}
          </div>
        )}
      </div>
    );
  };
  
  const OptionsSelectorStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => {
    console.log('OptionsSelectorStep - Component rendered');
    console.log('OptionsSelectorStep - bookingData:', bookingData);
    console.log('OptionsSelectorStep - routes:', routes);
    console.log('OptionsSelectorStep - options state:', options);
    
    const [selectedOptions, setSelectedOptions] = useState<Array<{option_id: string; quantity: number; name?: string; price?: number}>>(
      bookingData.selected_options || []
    );
    
    const selectedRoute = routes.find(route => route.id === bookingData.route_id);
    const routeSpecificOptions = selectedRoute?.options || [];
    const globalOptions = options || [];
    
    console.log('OptionsSelectorStep - selectedRoute:', selectedRoute);
    console.log('OptionsSelectorStep - routeSpecificOptions:', routeSpecificOptions);
    console.log('OptionsSelectorStep - globalOptions:', globalOptions);

    // Calculate total options price
    const calculateOptionsTotal = () => {
      return selectedOptions.reduce((total, option) => {
        const optionData = [...routeSpecificOptions, ...globalOptions].find(opt => opt.id === option.option_id);
        return total + (optionData?.price || 0) * option.quantity;
      }, 0);
    };

    const handleOptionToggle = (optionId: string, optionName: string, optionPrice: number) => {
      const existingIndex = selectedOptions.findIndex(opt => opt.option_id === optionId);
      
      if (existingIndex >= 0) {
        // Remove option
        const newOptions = selectedOptions.filter(opt => opt.option_id !== optionId);
        setSelectedOptions(newOptions);
        onComplete({ selected_options: newOptions });
      } else {
        // Add option with full details
        const newOptions = [...selectedOptions, { 
          option_id: optionId, 
          quantity: 1, 
          name: optionName, 
          price: optionPrice 
        }];
        setSelectedOptions(newOptions);
        onComplete({ selected_options: newOptions });
      }
    };

    const handleQuantityChange = (optionId: string, quantity: number) => {
      if (quantity <= 0) {
        // Remove option if quantity is 0 or less
        const newOptions = selectedOptions.filter(opt => opt.option_id !== optionId);
        setSelectedOptions(newOptions);
        onComplete({ selected_options: newOptions });
      } else {
        // Update quantity and preserve option details
        const optionData = [...routeSpecificOptions, ...globalOptions].find(opt => opt.id === optionId);
        const newOptions = selectedOptions.map(opt => 
          opt.option_id === optionId ? { 
            ...opt, 
            quantity,
            name: optionData?.name || opt.name,
            price: optionData?.price || opt.price
          } : opt
        );
        setSelectedOptions(newOptions);
        onComplete({ selected_options: newOptions });
      }
    };

    const isOptionSelected = (optionId: string) => {
      return selectedOptions.some(opt => opt.option_id === optionId);
    };

    const getSelectedQuantity = (optionId: string) => {
      const selected = selectedOptions.find(opt => opt.option_id === optionId);
      return selected ? selected.quantity : 0;
    };

    return (
      <div className="space-y-6">
        {/* Route-specific options */}
        {routeSpecificOptions.length > 0 && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Route-specific options
            </h3>
            <div className="grid gap-4">
              {routeSpecificOptions.map((option) => (
                <div
                  key={option.id}
                  className={cn(
                    "p-4 border rounded-lg transition-all duration-200",
                    isOptionSelected(option.id)
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {option.name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {option.description}
                      </p>
                      <p className="text-sm font-medium text-green-600 dark:text-green-400 mt-1">
                        Price: {formatCurrency(option.price)}
                      </p>
                    </div>
                    <div className="flex items-center space-x-3 space-x-reverse">
                      {isOptionSelected(option.id) && (
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <button
                            type="button"
                            onClick={() => handleQuantityChange(option.id, getSelectedQuantity(option.id) - 1)}
                            className="w-8 h-8 rounded-full border border-gray-300 dark:border-gray-600 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-700"
                          >
                            -
                          </button>
                          <span className="w-8 text-center font-medium">
                            {getSelectedQuantity(option.id)}
                          </span>
                          <button
                            type="button"
                            onClick={() => handleQuantityChange(option.id, getSelectedQuantity(option.id) + 1)}
                            className="w-8 h-8 rounded-full border border-gray-300 dark:border-gray-600 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-700"
                          >
                            +
                          </button>
                        </div>
                      )}
                      <button
                        type="button"
                        onClick={() => handleOptionToggle(option.id, option.name, option.price)}
                        className={cn(
                          "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                          isOptionSelected(option.id)
                            ? "bg-blue-600 text-white hover:bg-blue-700"
                            : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                        )}
                      >
                        {isOptionSelected(option.id) ? 'حذف' : 'افزودن'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Debug info */}
        <div className="mb-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Debug: Global options count: {globalOptions.length}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Options state: {JSON.stringify(options, null, 2)}
          </p>
          <button
            onClick={() => loadTransferOptions()}
            className="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-sm"
          >
            Reload Options
          </button>
          <button
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8000/api/v1/transfers/options/');
                const data = await response.json();
                console.log('Manual API test result:', data);
                alert(`API test successful! Found ${data.results?.length || 0} options`);
              } catch (error) {
                console.error('Manual API test failed:', error);
                alert(`API test failed: ${error}`);
              }
            }}
            className="mt-2 ml-2 px-3 py-1 bg-green-500 text-white rounded text-sm"
          >
            Test API
          </button>
        </div>

        {/* Global options */}
        {globalOptions.length > 0 && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Additional options
            </h3>
            <div className="grid gap-4">
              {globalOptions.map((option) => (
                <div
                  key={option.id}
                  className={cn(
                    "p-4 border rounded-lg transition-all duration-200",
                    isOptionSelected(option.id)
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {option.name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {option.description}
                      </p>
                      <p className="text-sm font-medium text-green-600 dark:text-green-400 mt-1">
                        Price: {formatCurrency(option.price)}
                      </p>
                    </div>
                    <div className="flex items-center space-x-3 space-x-reverse">
                      {isOptionSelected(option.id) && (
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <button
                            type="button"
                            onClick={() => handleQuantityChange(option.id, getSelectedQuantity(option.id) - 1)}
                            className="w-8 h-8 rounded-full border border-gray-300 dark:border-gray-600 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-700"
                          >
                            -
                          </button>
                          <span className="w-8 text-center font-medium">
                            {getSelectedQuantity(option.id)}
                          </span>
                          <button
                            type="button"
                            onClick={() => handleQuantityChange(option.id, getSelectedQuantity(option.id) + 1)}
                            className="w-8 h-8 rounded-full border border-gray-300 dark:border-gray-600 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-700"
                          >
                            +
                          </button>
                        </div>
                      )}
                      <button
                        type="button"
                        onClick={() => handleOptionToggle(option.id, option.name, option.price)}
                        className={cn(
                          "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                          isOptionSelected(option.id)
                            ? "bg-blue-600 text-white hover:bg-blue-700"
                            : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                        )}
                      >
                        {isOptionSelected(option.id) ? 'حذف' : 'افزودن'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No options available */}
        {routeSpecificOptions.length === 0 && globalOptions.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              No additional options available for this route.
            </p>
          </div>
        )}

        {/* Selected options summary */}
        {selectedOptions.length > 0 && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
              Selected options:
            </h4>
            <div className="space-y-1">
              {selectedOptions.map((selected) => {
                const allOptions = [...routeSpecificOptions, ...globalOptions];
                const option = allOptions.find(opt => opt.id === selected.option_id);
                return option ? (
                  <div key={selected.option_id} className="text-sm text-blue-800 dark:text-blue-200">
                    {option.name} × {selected.quantity} = {formatCurrency(option.price * selected.quantity)}
                  </div>
                ) : null;
              })}
            </div>
          </div>
        )}

        {/* Selected Options Summary */}
        {selectedOptions.length > 0 && (
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">Selected Options:</h4>
            <div className="space-y-2">
              {selectedOptions.map(option => {
                const optionData = [...routeSpecificOptions, ...globalOptions].find(opt => opt.id === option.option_id);
                const optionPrice = optionData?.price || option.price || 0;
                const totalPrice = optionPrice * option.quantity;
                return (
                  <div key={option.option_id} className="flex justify-between items-center text-sm">
                    <span className="text-gray-700 dark:text-gray-300">
                      {optionData?.name || option.name} (x{option.quantity})
                    </span>
                    <span className="font-medium text-green-600 dark:text-green-400">
                      {formatCurrency(totalPrice)}
                    </span>
                  </div>
                );
              })}
              <div className="border-t border-gray-200 dark:border-gray-600 pt-2 mt-2">
                <div className="flex justify-between items-center font-medium">
                  <span className="text-gray-900 dark:text-white">Options Total:</span>
                  <span className="text-green-600 dark:text-green-400">
                    {formatCurrency(calculateOptionsTotal())}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Validation Errors */}
        {validationErrors.selected_options && (
          <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.selected_options}</p>
        )}
      </div>
    );
  };
  
  const CustomerSelectorStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => {
    const [selectedCustomer, setSelectedCustomer] = useState(customers.find(c => c.id === bookingData.customer_id) || null);
    const [searchTerm, setSearchTerm] = useState('');
    const [showNewCustomerForm, setShowNewCustomerForm] = useState(false);
    const [newCustomer, setNewCustomer] = useState({
      name: '',
      phone: '',
      email: ''
    });

    const filteredCustomers = customers.filter(customer =>
      (customer.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (customer.phone || '').includes(searchTerm) ||
      (customer.email || '').toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleCustomerSelect = (customer: any) => {
      setSelectedCustomer(customer);
      onComplete({ customer_id: customer.id });
      
      // Clear validation errors
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.customer_id;
        return newErrors;
      });
    };

    const handleNewCustomerSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      try {
        // Create new customer via API
        const response = await fetch('http://localhost:8000/api/agents/customers/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newCustomer)
        });

        if (response.ok) {
          const customer = await response.json();
          setSelectedCustomer(customer);
          onComplete({ customer_id: customer.id });
          setShowNewCustomerForm(false);
          setNewCustomer({ name: '', phone: '', email: '' });
        } else {
          throw new Error('Failed to create customer');
        }
      } catch (error) {
        console.error('Error creating customer:', error);
        // Fallback to local creation
        const customer = {
          id: Date.now().toString(),
          ...newCustomer,
          created_at: new Date().toISOString().split('T')[0]
        };
        setSelectedCustomer(customer as any);
        onComplete({ customer_id: customer.id });
        setShowNewCustomerForm(false);
        setNewCustomer({ name: '', phone: '', email: '' });
      }
    };

    return (
      <div className="space-y-6">
        {/* Search and New Customer Button */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="جستجوی مشتری..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 pl-10 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setShowNewCustomerForm(!showNewCustomerForm)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 whitespace-nowrap"
          >
            {showNewCustomerForm ? 'لغو' : 'مشتری جدید'}
          </button>
        </div>

        {/* New Customer Form */}
        {showNewCustomerForm && (
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              اطلاعات مشتری جدید
            </h3>
            <form onSubmit={handleNewCustomerSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    نام و نام خانوادگی *
                  </label>
                  <input
                    type="text"
                    value={newCustomer.name}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, name: e.target.value }))}
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    شماره تلفن *
                  </label>
                  <input
                    type="tel"
                    value={newCustomer.phone}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, phone: e.target.value }))}
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    ایمیل
                  </label>
                  <input
                    type="email"
                    value={newCustomer.email}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 space-x-reverse">
                <button
                  type="button"
                  onClick={() => setShowNewCustomerForm(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  لغو
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
                >
                  ایجاد مشتری
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Customers List */}
        <div className="space-y-4">
          {filteredCustomers.map((customer) => (
            <div
              key={customer.id}
              className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 ${
                selectedCustomer?.id === customer.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
              onClick={() => handleCustomerSelect(customer)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {customer.name}
                  </h3>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      {customer.phone}
                    </div>
                    {customer.email && (
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        {customer.email}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center">
                  {selectedCustomer?.id === customer.id && (
                    <CheckIcon className="w-6 h-6 text-green-600" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredCustomers.length === 0 && !showNewCustomerForm && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              مشتری یافت نشد
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              مشتری مورد نظر یافت نشد. می‌توانید مشتری جدید ایجاد کنید.
            </p>
          </div>
        )}

        {/* Validation Errors */}
        {validationErrors.customer_id && (
          <div className="text-center">
            <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.customer_id}</p>
          </div>
        )}
      </div>
    );
  };
  
  const PricingSummaryStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => {
    const [isCalculating, setIsCalculating] = useState(false);

    const handleCalculatePricing = async () => {
      setIsCalculating(true);
      try {
        await calculatePricing();
      } finally {
        setIsCalculating(false);
      }
    };

    const selectedRoute = routes.find(route => route.id === bookingData.route_id);
    const selectedVehicle = selectedRoute?.vehicle_types?.find(vehicle => vehicle.type === bookingData.vehicle_type);

    // Helper function to determine time surcharge type
    const getTimeSurchargeType = (time: string) => {
      if (!time) return null;
      const hour = parseInt(time.split(':')[0]);
      if (hour >= 22 || hour <= 6) return 'midnight';
      if (hour >= 7 && hour <= 9) return 'peak';
      if (hour >= 17 && hour <= 19) return 'peak';
      return null;
    };

    const outboundSurchargeType = getTimeSurchargeType(bookingData.booking_time);
    const returnSurchargeType = getTimeSurchargeType(bookingData.return_time || '');

    return (
      <div className="space-y-6">
        <div className="text-center">
          <button
            type="button"
            onClick={handleCalculatePricing}
            disabled={isCalculating || !bookingData.route_id || !bookingData.vehicle_type}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCalculating ? 'Calculating...' : 'Calculate Price'}
          </button>
        </div>

        {pricing && (
          <div className="space-y-6">
            {/* Route Information */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                📍 Route Information
              </h3>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 px-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {selectedRoute?.origin} → {selectedRoute?.destination}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Selected Route
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                      {formatCurrency(pricing.base_price)}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Base Price
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Trip Type:</div>
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {bookingData.trip_type === 'round_trip' ? 'Round Trip' : 'One Way'}
                    </div>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Vehicle Type:</div>
                    <div className="font-semibold text-gray-900 dark:text-white">{selectedVehicle?.name}</div>
                  </div>
                </div>
                
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Trip Details:</div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Outbound Date:</span>
                      <span className="font-medium">{bookingData.booking_date} at {bookingData.booking_time}</span>
                    </div>
                    {bookingData.trip_type === 'round_trip' && bookingData.return_date && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Return Date:</span>
                        <span className="font-medium">{bookingData.return_date} at {bookingData.return_time}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Passengers:</span>
                      <span className="font-medium">{bookingData.passenger_count} passengers</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Luggage:</span>
                      <span className="font-medium">{bookingData.luggage_count} pieces</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Route Features */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                ⚡ Route Features
              </h4>
              
              <div className="space-y-3">
                {bookingData.trip_type === 'round_trip' && (
                  <div className="flex justify-between items-center py-2 px-3 bg-green-50 dark:bg-green-900/20 rounded">
                    <span className="text-green-700 dark:text-green-300 font-medium">Round Trip Discount:</span>
                    <span className="font-bold text-green-600 dark:text-green-400">
                      {(pricing as any).round_trip_discount_percentage?.toFixed(0) || 0}%
                    </span>
                  </div>
                )}
                
                {outboundSurchargeType === 'peak' && (
                  <div className="flex justify-between items-center py-2 px-3 bg-orange-50 dark:bg-orange-900/20 rounded">
                    <span className="text-orange-700 dark:text-orange-300 font-medium">Peak Hour Surcharge:</span>
                    <span className="font-bold text-orange-600 dark:text-orange-400">
                      {(pricing as any).peak_hour_surcharge_percentage?.toFixed(0) || 0}%
                    </span>
                  </div>
                )}
                
                {outboundSurchargeType === 'midnight' && (
                  <div className="flex justify-between items-center py-2 px-3 bg-purple-50 dark:bg-purple-900/20 rounded">
                    <span className="text-purple-700 dark:text-purple-300 font-medium">Midnight Surcharge:</span>
                    <span className="font-bold text-purple-600 dark:text-purple-400">
                      {(pricing as any).midnight_surcharge_percentage?.toFixed(0) || 0}%
                    </span>
                  </div>
                )}
                
                {!outboundSurchargeType && (
                  <div className="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded">
                    <span className="text-gray-700 dark:text-gray-300 font-medium">Regular Hours:</span>
                    <span className="font-bold text-gray-600 dark:text-gray-400">No Surcharge</span>
                  </div>
                )}
              </div>
            </div>

            {/* Vehicle Details */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                🚗 Vehicle Details
              </h4>
              
              <div className="space-y-3">
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <div className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {selectedVehicle?.name}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {selectedVehicle?.features?.join(', ') || 'Standard Features'}
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Capacity:</span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {selectedVehicle?.capacity || 4} passengers
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Time Information */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                ⏰ Time Information
              </h4>
              
              <div className="space-y-4">
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Outbound Time:</span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {bookingData.booking_time}
                    </span>
                  </div>
                  {outboundSurchargeType && (
                    <div className={cn(
                      "text-xs px-3 py-1 rounded-full inline-block",
                      outboundSurchargeType === 'midnight' 
                        ? "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300"
                        : "bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300"
                    )}>
                      {outboundSurchargeType === 'midnight' ? 'Midnight Hours' : 'Peak Hours'}
                      {outboundSurchargeType === 'midnight' ? ' +5%' : ' +10%'}
                    </div>
                  )}
                </div>
                
                {bookingData.trip_type === 'round_trip' && bookingData.return_time && (
                  <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Return Time:</span>
                      <span className="font-semibold text-gray-900 dark:text-white">
                        {bookingData.return_time}
                      </span>
                    </div>
                    {returnSurchargeType && (
                      <div className={cn(
                        "text-xs px-3 py-1 rounded-full inline-block",
                        returnSurchargeType === 'midnight' 
                          ? "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300"
                          : "bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300"
                      )}>
                        {returnSurchargeType === 'midnight' ? 'Midnight Hours' : 'Peak Hours'}
                        {returnSurchargeType === 'midnight' ? ' +5%' : ' +10%'}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Clear Pricing Breakdown */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                💰 Detailed Pricing
              </h4>
              
              <div className="space-y-4">
                {/* Base Price */}
                <div className="flex justify-between items-center py-2">
                  <span className="text-gray-700 dark:text-gray-300">Base Transfer Price</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {formatCurrency(pricing.base_price)}
                  </span>
                </div>
                
                {/* Time Surcharges */}
                {pricing.night_surcharge > 0 && (
                  <div className="flex justify-between items-center py-2 bg-orange-50 dark:bg-orange-900/20 px-3 rounded">
                    <span className="text-orange-700 dark:text-orange-300">
                      {outboundSurchargeType === 'midnight' ? 'Midnight Surcharge' : 'Peak Hour Surcharge'}
                    </span>
                    <span className="font-semibold text-orange-600 dark:text-orange-400">
                      +{formatCurrency(pricing.night_surcharge)}
                    </span>
                  </div>
                )}
                
                {/* Round Trip Return Price */}
                {bookingData.trip_type === 'round_trip' && (
                  <div className="flex justify-between items-center py-2">
                    <span className="text-gray-700 dark:text-gray-300">Return Price</span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {formatCurrency(pricing.base_price)}
                    </span>
                  </div>
                )}
                
                {/* Round Trip Discount */}
                {pricing.return_discount > 0 && (
                  <div className="flex justify-between items-center py-2 bg-green-50 dark:bg-green-900/20 px-3 rounded">
                    <span className="text-green-700 dark:text-green-300">Round Trip Discount</span>
                    <span className="font-semibold text-green-600 dark:text-green-400">
                      -{formatCurrency(pricing.return_discount)}
                    </span>
                  </div>
                )}
                
                {/* Options */}
                {pricing.options_total > 0 && (
                  <div className="flex justify-between items-center py-2 bg-blue-50 dark:bg-blue-900/20 px-3 rounded">
                    <span className="text-blue-700 dark:text-blue-300">Additional Options</span>
                    <span className="font-semibold text-blue-600 dark:text-blue-400">
                      +{formatCurrency(pricing.options_total)}
                    </span>
                  </div>
                )}
                
                {/* Subtotal */}
                <div className="border-t border-gray-300 dark:border-gray-600 pt-3">
                  <div className="flex justify-between items-center py-2">
                    <span className="text-gray-700 dark:text-gray-300 font-medium">Subtotal</span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {formatCurrency(pricing.subtotal || pricing.final_price)}
                    </span>
                  </div>
                </div>
                
                {/* Fees */}
                {pricing.fees_total > 0 && (
                  <div className="flex justify-between items-center py-2 bg-blue-50 dark:bg-blue-900/20 px-3 rounded">
                    <span className="text-blue-700 dark:text-blue-300">Service Fee (3%)</span>
                    <span className="font-semibold text-blue-600 dark:text-blue-400">
                      +{formatCurrency(pricing.fees_total)}
                    </span>
                  </div>
                )}
                
                {/* Tax */}
                {pricing.tax_total > 0 && (
                  <div className="flex justify-between items-center py-2 bg-purple-50 dark:bg-purple-900/20 px-3 rounded">
                    <span className="text-purple-700 dark:text-purple-300">VAT (9%)</span>
                    <span className="font-semibold text-purple-600 dark:text-purple-400">
                      +{formatCurrency(pricing.tax_total)}
                    </span>
                  </div>
                )}
                
                {/* Final Total */}
                <div className="border-t-2 border-gray-400 dark:border-gray-500 pt-4">
                  <div className="flex justify-between items-center py-3 bg-gray-50 dark:bg-gray-700 px-4 rounded-lg">
                    <span className="text-lg font-bold text-gray-900 dark:text-white">Total</span>
                    <span className="text-xl font-bold text-green-600 dark:text-green-400">
                      {formatCurrency(pricing.grand_total || pricing.customer_price)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Commission Information */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                💰 Commission Information
              </h4>
              
              <div className="space-y-4">
                {/* Agent Pricing */}
                <div className="space-y-2">
                  <h5 className="font-medium text-gray-900 dark:text-white">Agent Pricing</h5>
                  <div className="space-y-1 pl-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Regular Subtotal:</span>
                      <span className="text-gray-900 dark:text-white line-through">
                        {formatCurrency((pricing as any).subtotal || pricing.final_price)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Agent Discount ({pricing.savings_percentage?.toFixed(1) || 0}%):</span>
                      <span className="text-green-600 dark:text-green-400">
                        -{formatCurrency(pricing.savings || 0)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Agent Subtotal:</span>
                      <span className="text-green-600 dark:text-green-400 font-semibold">
                        {formatCurrency((pricing as any).agent_subtotal || 0)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Service Fee (3%):</span>
                      <span className="text-blue-600 dark:text-blue-400">
                        +{formatCurrency((pricing as any).fees_total || 0)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">VAT (9%):</span>
                      <span className="text-purple-600 dark:text-purple-400">
                        +{formatCurrency((pricing as any).tax_total || 0)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm border-t border-gray-200 dark:border-gray-700 pt-2">
                      <span className="text-gray-600 dark:text-gray-400 font-semibold">Agent Final Price:</span>
                      <span className="text-green-600 dark:text-green-400 font-bold">
                        {formatCurrency(pricing.agent_total || 0)}
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Commission Details */}
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <h5 className="font-medium text-gray-900 dark:text-white mb-2">Commission Details</h5>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Commission Rate:</span>
                      <span className="text-gray-900 dark:text-white">
                        {(pricing as any).commission_rate?.toFixed(1) || 0}%
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Commission Base:</span>
                      <span className="text-gray-900 dark:text-white">
                        {formatCurrency((pricing as any).commission_base || 0)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Your Commission:</span>
                      <span className="text-green-600 dark:text-green-400 font-semibold">
                        {formatCurrency((pricing as any).commission_amount || 0)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Selected Options Details */}
            {bookingData.selected_options && bookingData.selected_options.length > 0 && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  🎯 Selected Options Details
                </h4>
                <div className="space-y-3">
                  {bookingData.selected_options.map(option => {
                    const selectedRoute = routes.find(route => route.id === bookingData.route_id);
                    const routeSpecificOptions = selectedRoute?.options || [];
                    const globalOptions = options || [];
                    const optionData = [...routeSpecificOptions, ...globalOptions].find(opt => opt.id === option.option_id);
                    const optionPrice = optionData?.price || option.price || 0;
                    const totalPrice = optionPrice * option.quantity;
                    
                    return (
                      <div key={option.option_id} className="flex justify-between items-center py-2 px-3 bg-white dark:bg-gray-800 rounded border">
                        <div className="flex items-center">
                          <span className="text-gray-700 dark:text-gray-300 font-medium">
                            {optionData?.name || option.name}
                          </span>
                          <span className="text-gray-500 dark:text-gray-400 ml-2 text-sm">
                            (Quantity: {option.quantity})
                          </span>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-green-600 dark:text-green-400">
                            {formatCurrency(totalPrice)}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {formatCurrency(optionPrice)} × {option.quantity}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  <div className="border-t-2 border-blue-300 dark:border-blue-600 pt-3 mt-3">
                    <div className="flex justify-between items-center py-2 px-3 bg-blue-100 dark:bg-blue-800/30 rounded">
                      <span className="text-blue-800 dark:text-blue-200 font-bold">Total Options:</span>
                      <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
                        {formatCurrency(pricing.options_total || 0)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {!pricing && (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              Please select a route and vehicle first to view pricing
            </p>
          </div>
        )}
      </div>
    );
  };
  
  const PaymentMethodStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => {
    const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(bookingData.payment_method || 'whatsapp');

    const paymentMethods = [
      {
        id: 'whatsapp',
        name: 'WhatsApp Payment',
        description: 'Payment confirmation via WhatsApp. Order will be pending until manual confirmation by admin.',
        icon: '📱',
        isAvailable: true,
        processingTime: 'Manual confirmation required',
        fees: 0
      },
      {
        id: 'direct_payment',
        name: 'Direct Payment / Bank Gateway',
        description: 'Direct payment through bank gateway. Order will be automatically confirmed after successful payment.',
        icon: '🏦',
        isAvailable: true,
        processingTime: 'Instant',
        fees: 0
      },
      {
        id: 'agent_credit',
        name: 'Agent Credit Account',
        description: 'Deduct from agent credit balance. Requires sufficient balance.',
        icon: '💳',
        isAvailable: false,
        processingTime: 'Instant',
        fees: 0
      }
    ];

    const handlePaymentMethodSelect = (methodId: string) => {
      setSelectedPaymentMethod(methodId);
      onComplete({ payment_method: methodId });
      
      // Clear validation errors
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.payment_method;
        return newErrors;
      });
    };

    const selectedMethod = paymentMethods.find(method => method.id === selectedPaymentMethod);

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Select Payment Method
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Choose the appropriate payment method for this transfer booking
          </p>
        </div>

        {/* Payment Methods */}
        <div className="space-y-4">
          {paymentMethods.map((method) => (
            <div
              key={method.id}
              className={`p-6 border rounded-lg cursor-pointer transition-all duration-200 ${
                selectedPaymentMethod === method.id
                  ? 'ring-2 ring-blue-500 border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              } ${!method.isAvailable ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => method.isAvailable && handlePaymentMethodSelect(method.id)}
            >
              <div className="flex items-start space-x-4 space-x-reverse">
                <div className="text-3xl">{method.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 space-x-reverse mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {method.name}
                    </h3>
                    {method.isAvailable ? (
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                        Available
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200 rounded-full">
                        Coming Soon
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {method.description}
                  </p>
                  <div className="flex items-center space-x-4 space-x-reverse text-xs text-gray-500 dark:text-gray-400">
                    <span className="flex items-center space-x-1 space-x-reverse">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>{method.processingTime}</span>
                    </span>
                    {method.fees !== undefined && (
                      <span className="flex items-center space-x-1 space-x-reverse">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                        </svg>
                        <span>{method.fees === 0 ? 'بدون کارمزد' : `${method.fees} تومان کارمزد`}</span>
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                    selectedPaymentMethod === method.id
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}>
                    {selectedPaymentMethod === method.id && (
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Payment Summary */}
        {selectedMethod && (
          <div className="border-blue-200 bg-blue-50 dark:bg-blue-900/20 border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-4">
              خلاصه پرداخت
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-blue-800 dark:text-blue-300">
                  روش انتخابی:
                </span>
                <span className="font-medium text-blue-900 dark:text-blue-200">
                  {selectedMethod.name}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-blue-800 dark:text-blue-300">
                  زمان پردازش:
                </span>
                <span className="font-medium text-blue-900 dark:text-blue-200">
                  {selectedMethod.processingTime}
                </span>
              </div>
              {pricing && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-800 dark:text-blue-300">
                    مبلغ کل:
                  </span>
                  <span className="text-lg font-bold text-blue-900 dark:text-blue-200">
                    {formatCurrency(pricing.final_price)}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Important Notes */}
        <div className="border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20 border rounded-lg p-6">
          <div className="flex items-start space-x-3 space-x-reverse">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                نکته مهم
              </h4>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                {selectedPaymentMethod === 'whatsapp'
                  ? 'پس از تأیید رزرو، مشتری از طریق واتساپ پرداخت خواهد کرد. پس از تأیید پرداخت توسط ادمین، رزرو فعال خواهد شد.'
                  : selectedPaymentMethod === 'direct_payment'
                  ? 'پرداخت از طریق درگاه بانکی انجام می‌شود و پس از تأیید، رزرو به صورت خودکار فعال خواهد شد.'
                  : 'Please select an appropriate payment method.'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Validation Errors */}
        {validationErrors.payment_method && (
          <div className="text-center">
            <p className="text-red-600 dark:text-red-400 text-sm">{validationErrors.payment_method}</p>
          </div>
        )}
      </div>
    );
  };

  const BookingConfirmationStep = ({ bookingData, onComplete, validationErrors }: BookingStepProps) => {
    const selectedRoute = routes.find(route => route.id === bookingData.route_id);
    const selectedVehicle = selectedRoute?.vehicle_types?.find(vehicle => vehicle.type === bookingData.vehicle_type);
    const selectedCustomer = customers.find(c => c.id === bookingData.customer_id);

    const paymentMethodNames = {
      'whatsapp': 'WhatsApp Payment',
      'direct_payment': 'Direct Payment / Bank Gateway',
      'agent_credit': 'Agent Credit Account'
    };

    return (
      <div className="space-y-6">
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
            Final Booking Confirmation
          </h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">Trip Details:</h4>
              <div className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                <p><strong>Route:</strong> {selectedRoute?.origin} → {selectedRoute?.destination}</p>
                <p><strong>Vehicle Type:</strong> {selectedVehicle?.name}</p>
                <p><strong>Outbound Date:</strong> {bookingData.booking_date}</p>
                <p><strong>Outbound Time:</strong> {bookingData.booking_time}</p>
                {bookingData.trip_type === 'round_trip' && (
                  <>
                    <p><strong>Return Date:</strong> {bookingData.return_date}</p>
                    <p><strong>Return Time:</strong> {bookingData.return_time}</p>
                  </>
                )}
                <p><strong>Passengers:</strong> {bookingData.passenger_count} people</p>
                <p><strong>Luggage:</strong> {bookingData.luggage_count} pieces</p>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">Customer Information:</h4>
              <div className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                <p><strong>Name:</strong> {selectedCustomer?.name}</p>
                <p><strong>Phone:</strong> {selectedCustomer?.phone}</p>
                {selectedCustomer?.email && (
                  <p><strong>Email:</strong> {selectedCustomer.email}</p>
                )}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">Payment Method:</h4>
              <div className="text-sm text-blue-700 dark:text-blue-300">
                <p><strong>{paymentMethodNames[bookingData.payment_method as keyof typeof paymentMethodNames] || 'نامشخص'}</strong></p>
              </div>
            </div>
            
            {pricing && (
              <div>
                <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">Final Price:</h4>
                <div className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                  <p><strong>Regular Price:</strong> {formatCurrency(pricing.final_price)}</p>
                  <p><strong>Agent Price:</strong> {formatCurrency(pricing.agent_total)}</p>
                  <p><strong>Your Commission:</strong> {formatCurrency((pricing as any).commission_amount || 0)}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            By clicking "Confirm Booking" you agree to the terms and conditions.
          </p>
        </div>
      </div>
    );
  };

  // Define booking steps similar to Tour booking
  const steps: BookingStep[] = [
    { 
      id: 'route', 
      title: 'انتخاب مسیر', 
      description: 'مسیر ترانسفر خود را انتخاب کنید',
      isCompleted: !!bookingData.route_id,
      component: RouteSelectorStep
    },
    { 
      id: 'vehicle', 
      title: 'انتخاب خودرو', 
      description: 'نوع خودرو خود را انتخاب کنید',
      isCompleted: !!bookingData.vehicle_type,
      component: VehicleSelectorStep
    },
    { 
      id: 'datetime', 
      title: 'تاریخ و زمان', 
      description: 'تاریخ و زمان سفر خود را تنظیم کنید',
      isCompleted: !!bookingData.booking_date && !!bookingData.booking_time,
      component: DateTimeSelectorStep
    },
    { 
      id: 'passengers', 
      title: 'مسافران', 
      description: 'تعداد مسافران و چمدان را تنظیم کنید',
      isCompleted: bookingData.passenger_count > 0,
      component: PassengersSelectorStep
    },
    { 
      id: 'options', 
      title: 'گزینه‌های اضافی', 
      description: 'گزینه‌های اضافی را انتخاب کنید',
      isCompleted: true,
      component: OptionsSelectorStep
    },
    { 
      id: 'customer', 
      title: 'مشتری', 
      description: 'مشتری را انتخاب کنید',
      isCompleted: !!bookingData.customer_id,
      component: CustomerSelectorStep
    },
    { 
      id: 'pricing', 
      title: 'قیمت‌گذاری', 
      description: 'قیمت و کمیسیون را بررسی کنید',
      isCompleted: !!pricing,
      component: PricingSummaryStep
    },
    { 
      id: 'payment', 
      title: 'Payment Method', 
      description: 'Select payment method',
      isCompleted: !!bookingData.payment_method,
      component: PaymentMethodStep
    },
    { 
      id: 'confirm', 
      title: 'Final Confirmation', 
      description: 'Confirm your booking',
      isCompleted: false,
      component: BookingConfirmationStep
    }
  ];
  
  // State for route pagination and search
  const [displayedRoutes, setDisplayedRoutes] = useState<TransferRoute[]>([]);
  const [routesPerPage] = useState(4);
  const [currentPage, setCurrentPage] = useState(1);
  const [filteredRoutes, setFilteredRoutes] = useState<TransferRoute[]>([]);
  const [searchOrigin, setSearchOrigin] = useState('');
  const [searchDestination, setSearchDestination] = useState('');
  const [timeSurcharges, setTimeSurcharges] = useState({
    peak_hour_surcharge: 0,
    midnight_surcharge: 0,
    round_trip_discount: 0
  });

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      console.log('Loading initial data...');
      await loadTransferData();
      await loadTransferOptions();
      await loadCustomers();
    };
    
    loadData();
  }, []);

  // Debug current step
  useEffect(() => {
    console.log('Current step changed to:', currentStep);
    console.log('Current step component:', steps[currentStep]?.title);
  }, [currentStep]);

  // Update filtered routes when search changes
  useEffect(() => {
    let filtered = routes;
    
    if (searchOrigin) {
      filtered = filtered.filter(route => 
        route.origin.toLowerCase().includes(searchOrigin.toLowerCase())
      );
    }
    
    if (searchDestination) {
      filtered = filtered.filter(route => 
        route.destination.toLowerCase().includes(searchDestination.toLowerCase())
      );
    }
    
    setFilteredRoutes(filtered);
    setCurrentPage(1); // Reset to first page when search changes
  }, [routes, searchOrigin, searchDestination]);

  // Update displayed routes based on pagination
  useEffect(() => {
    const startIndex = (currentPage - 1) * routesPerPage;
    const endIndex = startIndex + routesPerPage;
    setDisplayedRoutes(filteredRoutes.slice(startIndex, endIndex));
  }, [filteredRoutes, currentPage, routesPerPage]);

  // Load transfer data from API
  const loadTransferData = async () => {
    try {
      // Use the agent API endpoint for transfer routes
      const response = await fetch('http://localhost:8000/api/agents/transfers/routes/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setRoutes(data.routes || data.results || []);
          
          // Don't set global vehicle types - they will be set per route
          setVehicleTypes([]);
        } else {
          throw new Error(data.error || 'Failed to load transfer routes');
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: Failed to load transfer routes`);
      }
    } catch (error) {
      console.error('Error loading transfer data:', error);
      setValidationErrors(prev => ({
        ...prev,
        routes: `Error loading routes: ${error instanceof Error ? error.message : 'Unknown error'}`
      }));
      // Fallback to empty arrays
      setRoutes([]);
      setVehicleTypes([]);
    }
  };

  // Load global transfer options from API
  const loadTransferOptions = async () => {
    console.log('loadTransferOptions - Starting API call...');
    try {
      const url = 'http://localhost:8000/api/v1/transfers/options/';
      console.log('loadTransferOptions - Calling URL:', url);
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('loadTransferOptions - Response status:', response.status);
      console.log('loadTransferOptions - Response ok:', response.ok);
      
      if (response.ok) {
        const data = await response.json();
        console.log('loadTransferOptions - Raw response data:', data);
        
        // Handle both array response and paginated response
        const allOptions = Array.isArray(data) ? data : (data.results || data.options || []);
        console.log('loadTransferOptions - All options:', allOptions.length);
        
        // Filter to only global options (those without a specific route)
        const globalOptions = allOptions.filter((option: any) => !option.route);
        console.log('loadTransferOptions - Global options after filtering:', globalOptions.length);
        console.log('loadTransferOptions - Global options data:', globalOptions);
        
        setOptions(globalOptions);
        console.log('loadTransferOptions - Options state updated');
      } else {
        console.error('Failed to load transfer options:', response.status, response.statusText);
        setOptions([]);
      }
    } catch (error) {
      console.error('Error loading transfer options:', error);
      setOptions([]);
    }
  };

  // Calculate pricing using agent pricing API
  const calculatePricing = useCallback(async () => {
    if (!bookingData.route_id || !bookingData.vehicle_type) return;

    setLoadingPricing(true);
    setValidationErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors.pricing; // Clear previous pricing errors
      return newErrors;
    });
    
    try {
      // Get selected route and options for complete data
      const selectedRoute = routes.find(route => route.id === bookingData.route_id);
      const routeSpecificOptions = selectedRoute?.options || [];
      const globalOptions = options || [];
      
      // Prepare pricing request data with complete option information
      const pricingData = {
        product_type: 'transfer', // Required by the API
        route_id: bookingData.route_id,
        vehicle_type: bookingData.vehicle_type,
        passenger_count: bookingData.passenger_count,
        trip_type: bookingData.trip_type,
        booking_time: bookingData.booking_time, // Send as string, API will parse it
        return_time: bookingData.return_time, // Send as string, API will parse it
        selected_options: bookingData.selected_options?.map(opt => {
          const optionData = [...routeSpecificOptions, ...globalOptions].find(o => o.id === opt.option_id);
          return {
            id: opt.option_id,
            quantity: opt.quantity || 1,
            name: optionData?.name || opt.name,
            price: optionData?.price || opt.price
          };
        }) || []
      };

      // Call agent pricing API - use the correct endpoint
      const response = await fetch('http://localhost:8000/api/agents/pricing/transfer/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(pricingData)
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Transform the response to match our expected structure
          const pricingData = result.pricing;
          const feesTaxes = pricingData.fees_taxes_breakdown || {};
          const commissionInfo = pricingData.commission_info || {};
          const transformedPricing = {
            base_price: pricingData.base_price || 0, // This is now the actual base price
            final_price: pricingData.final_price || 0, // Customer pays the regular price (without commission)
            agent_commission: pricingData.savings || 0, // Agent commission is the savings
            night_surcharge: pricingData.price_breakdown?.outbound_surcharge || 0, // Use outbound_surcharge
            options_total: pricingData.options_total || 0,
            return_price: pricingData.price_breakdown?.return_price || 0,
            return_discount: pricingData.price_breakdown?.round_trip_discount || 0,
            customer_price: feesTaxes.grand_total || pricingData.final_price || 0, // Customer pays total with fees and taxes
            // Additional fields from the response
            agent_total: pricingData.agent_total || 0, // Agent price (with commission)
            agent_subtotal: pricingData.agent_subtotal || 0, // Agent subtotal (before fees and taxes)
            savings: pricingData.savings || 0,
            savings_percentage: pricingData.savings_percentage || 0,
            currency: pricingData.currency || 'USD',
            capacity_info: pricingData.capacity_info || {},
            trip_info: pricingData.trip_info || {},
            // Add actual percentages for display
            round_trip_discount_percentage: pricingData.round_trip_discount_percentage || 0,
            peak_hour_surcharge_percentage: pricingData.peak_hour_surcharge_percentage || 0,
            midnight_surcharge_percentage: pricingData.midnight_surcharge_percentage || 0,
            // Add fees and taxes information
            fees_total: feesTaxes.fees_total || 0,
            tax_total: feesTaxes.tax_total || 0,
            grand_total: feesTaxes.grand_total || 0,
            subtotal: feesTaxes.subtotal || 0,
            // Add commission information
            commission_rate: commissionInfo.commission_rate || 0,
            commission_amount: commissionInfo.commission_amount || 0,
            commission_base: commissionInfo.commission_base || 0
          };
          
          setPricing(transformedPricing);
          
          // Extract surcharge information from pricing data
          setTimeSurcharges({
            peak_hour_surcharge: transformedPricing.night_surcharge || 0,
            midnight_surcharge: transformedPricing.night_surcharge || 0,
            round_trip_discount: transformedPricing.return_discount || 0
          });
        } else {
          throw new Error(result.error || 'Pricing calculation failed');
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: Pricing calculation failed`);
      }
    } catch (error) {
      console.error('Agent pricing calculation failed:', error);
      setValidationErrors(prev => ({
        ...prev,
        pricing: `Error calculating pricing: ${error instanceof Error ? error.message : 'Unknown error'}`
      }));
      setPricing(null);
    } finally {
      setLoadingPricing(false);
    }
  }, [bookingData, routes, options]);

  // Auto-calculate pricing when relevant data changes (excluding passenger_count)
  // Auto-calculate pricing only after options are selected (step 4)
  useEffect(() => {
    if (currentStep >= 4 && bookingData.route_id && bookingData.vehicle_type && bookingData.booking_date && bookingData.booking_time) {
      calculatePricing();
    }
  }, [currentStep, bookingData.route_id, bookingData.vehicle_type, bookingData.booking_date, bookingData.booking_time, bookingData.trip_type, bookingData.return_time, bookingData.selected_options, calculatePricing]);

  // Update booking data
  const updateBookingData = (updates: Partial<TransferBookingData>) => {
    setBookingData(prev => ({ ...prev, ...updates }));
  };

  // Pagination handlers
  const handleNextPage = () => {
    const totalPages = Math.ceil(filteredRoutes.length / routesPerPage);
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleViewMore = () => {
    handleNextPage();
  };

  // Clear search
  const clearSearch = () => {
    setSearchOrigin('');
    setSearchDestination('');
  };

  // Step navigation handlers (similar to Tour booking)
  const handleStepComplete = (data: Partial<TransferBookingData>) => {
    setBookingData(prev => ({ ...prev, ...data }));
    
    // Clear validation errors for current step
    setValidationErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[steps[currentStep].id];
      return newErrors;
    });
    
    // Auto-advance only for steps 0 and 1 (Route Selection and Vehicle Selection)
    // Steps 2+ require manual "Next" button click with validation
    if (currentStep <= 1 && currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleNextStep = () => {
    // Validate current step before proceeding
    const isValid = validateStep(currentStep);
    if (isValid && currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };


  // Enhanced validation functions with transfer-specific validations
  const validateStep = (stepIndex: number): boolean => {
    const errors: Record<string, string> = {};
    const warnings: Record<string, string> = {};
    
    // Get default constraints and capacities
    const defaultConstraints = getDefaultRouteConstraints();
    const vehicleCapacities = getDefaultVehicleCapacities();
    
    // Use actual vehicle capacity from the selected route instead of default capacities
    const selectedRoute = routes.find(route => route.id === bookingData.route_id);
    const selectedVehicleFromRoute = selectedRoute?.vehicle_types?.find(vt => vt.type === bookingData.vehicle_type);
    const vehicleCapacity = selectedVehicleFromRoute ? {
      max_passengers: selectedVehicleFromRoute.max_passengers,
      max_luggage: selectedVehicleFromRoute.max_luggage,
      vehicle_type: selectedVehicleFromRoute.type
    } : vehicleCapacities.sedan;
    
    // Use actual vehicle types from the selected route instead of hardcoded constraints
    const availableVehicleTypes = selectedRoute?.vehicle_types?.map(vt => vt.type) || [];
    const routeConstraints = {
      ...defaultConstraints,
      allowed_vehicle_types: availableVehicleTypes.length > 0 ? availableVehicleTypes : defaultConstraints.allowed_vehicle_types
    };
    
    switch (stepIndex) {
      case 0: // Route selection
        if (!bookingData.route_id) {
          errors.route_id = 'Please select a route';
        }
        break;
      case 1: // Vehicle selection
        if (!bookingData.vehicle_type) {
          errors.vehicle_type = 'Please select a vehicle type';
        }
        break;
      case 2: // Date & Time
        // Use transfer-specific validation
        const validationData: ValidationBookingData = {
          route_id: bookingData.route_id,
          vehicle_type: bookingData.vehicle_type || '',
          passenger_count: bookingData.passenger_count,
          luggage_count: bookingData.luggage_count,
          trip_type: bookingData.trip_type,
          booking_date: bookingData.booking_date,
          booking_time: bookingData.booking_time,
          return_date: bookingData.return_date,
          return_time: bookingData.return_time,
          selected_options: bookingData.selected_options
        };
        
        const validationResult = validateTransferBooking(validationData, vehicleCapacity, routeConstraints);
        console.log('🔍 Validation Debug - Step:', stepIndex);
        console.log('🔍 Validation Result:', validationResult);
        console.log('🔍 ValidationResult.errors:', validationResult.errors);
        console.log('🔍 Current errors before merge:', errors);
        Object.assign(errors, validationResult.errors);
        Object.assign(warnings, validationResult.warnings);
        console.log('🔍 Current errors after merge:', errors);
        
        // Additional time-based validations
        if (bookingData.booking_time) {
          const timeValidation = validateTimeSurcharges(
            bookingData.booking_time, 
            bookingData.return_time, 
            routeConstraints
          );
          timeValidation.warnings.forEach(warning => {
            warnings[`time_${Date.now()}`] = warning;
          });
        }
        
        // Round trip discount validation
        if (bookingData.trip_type === 'round_trip' && bookingData.booking_date && bookingData.return_date) {
          const discountValidation = validateRoundTripDiscount(
            bookingData.booking_date,
            bookingData.return_date,
            bookingData.booking_time,
            bookingData.return_time
          );
          discountValidation.warnings.forEach(warning => {
            warnings[`discount_${Date.now()}`] = warning;
          });
        }
        break;
      case 3: // Passengers
        // Use capacity validation
        const capacityValidation = validateTransferCapacity(
          bookingData.passenger_count,
          bookingData.luggage_count,
          vehicleCapacity
        );
        Object.assign(errors, capacityValidation.errors);
        Object.assign(warnings, capacityValidation.warnings);
        break;
      case 4: // Options
        // Validate selected options
        if (bookingData.selected_options && bookingData.selected_options.length > 0) {
          for (const option of bookingData.selected_options) {
            if (option.quantity < 1) {
              errors[`option_${option.option_id}`] = `Invalid quantity for ${option.name || 'option'}`;
            }
            if (option.quantity > 10) {
              warnings[`option_${option.option_id}`] = `High quantity for ${option.name || 'option'} - please verify`;
            }
          }
        }
        break;
      case 5: // Customer
        // In agent booking flow, customer should already be selected by the agent
        if (!bookingData.customer_id) {
          errors.customer_id = 'لطفاً مشتری را انتخاب کنید';
        }
        break;
      case 6: // Pricing
        // No validation needed for pricing step - it's just a summary
        break;
      case 7: // Payment Method
        if (!bookingData.payment_method) {
          errors.payment_method = 'Please select a payment method';
        }
        break;
    }

    console.log('🔍 Final validation errors for step', stepIndex, ':', errors);
    console.log('🔍 Final validation warnings for step', stepIndex, ':', warnings);
    console.log('🔍 Error keys:', Object.keys(errors));
    console.log('🔍 Error values:', Object.values(errors));
    
    // Check for empty or problematic error values
    Object.entries(errors).forEach(([key, value]) => {
      if (!value || value.trim().length === 0) {
        console.warn('⚠️ Empty error detected:', key, '=', value);
      }
    });
    
    setValidationErrors(errors);
    setValidationWarnings(warnings);
    return Object.keys(errors).length === 0;
  };

  // Handle booking submission
  const handleBookingSubmit = async () => {
    // Validate all steps before submission
    if (!validateAllSteps()) {
      return;
    }

    setIsSubmitting(true);
    setValidationErrors({}); // Clear previous errors

    try {
      // Ensure we have pricing information
      if (!pricing) {
        await calculatePricing();
        if (!pricing) {
          throw new Error('Unable to calculate pricing');
        }
      }

      // Get customer information from agent-selected customer
      const selectedCustomer = customers.find(c => c.id === bookingData.customer_id);
      if (!selectedCustomer) {
        throw new Error('Customer not found. Please select a customer.');
      }

      // Prepare booking data for agent API
      const transferBookingData = {
        customer_id: bookingData.customer_id,
        route_id: bookingData.route_id,
        vehicle_type: bookingData.vehicle_type,
        passenger_count: bookingData.passenger_count,
        luggage_count: bookingData.luggage_count,
        trip_type: bookingData.trip_type,
        booking_date: bookingData.booking_date,
        booking_time: bookingData.booking_time,
        return_date: bookingData.return_date || null,
        return_time: bookingData.return_time || null,
        selected_options: bookingData.selected_options || [],
        special_requests: bookingData.special_requests || '',
        notes: bookingData.notes || '',
        customer_name: selectedCustomer.name || '',
        customer_phone: selectedCustomer.phone || '',
        customer_email: selectedCustomer.email || '',
        payment_method: bookingData.payment_method || 'whatsapp'
      };

      // Call unified transfer booking API
      const response = await fetch('http://localhost:8000/api/transfers/book/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(transferBookingData)
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Handle success with detailed information
          const successMessage = `Transfer booked successfully!

Order Number: ${result.order_number || result.order_id}
Total Amount: ${formatCurrency(result.total_amount)}
Commission: ${formatCurrency(result.commission_amount)}
Payment Method: ${bookingData.payment_method === 'whatsapp' ? 'WhatsApp (Pending Admin Approval)' : 'Direct Payment'}

${result.pricing_info ? `
Pricing Details:
- Base Price: ${formatCurrency(result.pricing_info.base_price)}
- Agent Price: ${formatCurrency(result.pricing_info.agent_price)}
- Savings: ${formatCurrency(result.pricing_info.savings)} (${result.pricing_info.savings_percentage?.toFixed(1)}%)
` : ''}`;
          
          alert(successMessage);
          
          // Reset form after successful booking
          setBookingData({
            customer_id: '',
            route_id: 0,
            vehicle_type: '',
            booking_date: '',
            booking_time: '',
            passenger_count: 1,
            luggage_count: 0,
            trip_type: 'one_way',
            selected_options: [],
            special_requests: '',
            notes: ''
          });
          setPricing(null);
          setCurrentStep(0);
        } else {
          throw new Error(result.error || 'Booking failed');
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: Booking failed`);
      }
      
    } catch (error) {
      console.error('Transfer booking failed:', error);
      const errorMessage = error instanceof Error ? error.message : t.transfer.bookingError;
      setValidationErrors(prev => ({
        ...prev,
        submission: `خطا در ثبت ترانسفر: ${errorMessage}`
      }));
    } finally {
      setIsSubmitting(false);
    }
  };

  // Format currency with agent's preferred currency
  const formatCurrency = (amount: number | undefined | null, currency?: string) => {
    if (amount === undefined || amount === null || isNaN(amount)) {
      return '0';
    }
    
    const currencyCode = currency || unifiedCurrency || 'USD';
    
    // Use English locale for currency display to avoid Persian number issues
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  // Validate all steps
  const validateAllSteps = (): boolean => {
    let allValid = true;
    for (let i = 0; i < steps.length - 1; i++) { // Exclude confirmation step
      if (!validateStep(i)) {
        allValid = false;
      }
    }
    return allValid;
  };

  // Get selected route
  const selectedRoute = routes.find(route => route.id === bookingData.route_id);
  const selectedVehicle = selectedRoute?.vehicle_types?.find(vt => vt.type === bookingData.vehicle_type);
  const selectedCustomer = customers.find(customer => customer.id === bookingData.customer_id);

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t.transfer.title}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {t.transfer.subtitle}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg mb-8">
          <div className="p-6">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center flex-1">
                  <div className="flex flex-col items-center">
                    <div className={cn(
                      "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
                      index <= currentStep
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400"
                    )}>
                      {step.isCompleted ? (
                        <CheckCircleIcon className="w-5 h-5" />
                      ) : (
                        index + 1
                      )}
                    </div>
                    <span className={cn(
                      "mt-2 text-xs text-center",
                      index <= currentStep
                        ? "text-blue-600 dark:text-blue-400"
                        : "text-gray-500 dark:text-gray-400"
                    )}>
                      {step.title}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={cn(
                      "flex-1 h-0.5 mx-4",
                      index < currentStep
                        ? "bg-blue-600"
                        : "bg-gray-200 dark:bg-gray-700"
                    )} />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="p-6">
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {steps[currentStep].title}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    {steps[currentStep].description}
                  </p>
                </div>

                {/* Validation Warnings */}
                {Object.keys(validationWarnings).length > 0 && (
                  <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <div className="flex items-start">
                      <InformationCircleIcon className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                          توجه
                        </h4>
                        <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                          {Object.values(validationWarnings).map((warning, index) => (
                            <li key={index}>• {warning}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* Validation Errors */}
                {Object.values(validationErrors).some(error => error && error.trim().length > 0) && (
                  <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <div className="flex items-start">
                      <InformationCircleIcon className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <h4 className="text-sm font-medium text-red-800 dark:text-red-200 mb-2">
                          خطاهای اعتبارسنجی
                        </h4>
                        <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                          {Object.values(validationErrors).filter(error => error && error.trim().length > 0).map((error, index) => (
                            <li key={index}>• {error}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* Step Component */}
                <CurrentStepComponent
                  bookingData={bookingData}
                  onComplete={handleStepComplete}
                  onPrevious={handlePreviousStep}
                  onNext={handleNextStep}
                  isFirstStep={currentStep === 0}
                  isLastStep={currentStep === steps.length - 1}
                  validationErrors={validationErrors}
                  setValidationErrors={setValidationErrors}
                />

                {/* Navigation Buttons */}
                <div className="flex justify-between mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={handlePreviousStep}
                    disabled={currentStep === 0}
                    className={cn(
                      "px-4 py-2 rounded-md text-sm font-medium transition-colors",
                      currentStep === 0
                        ? "bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500"
                        : "bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500"
                    )}
                  >
                    {t.transfer.previous}
                  </button>
                  
                  <button
                    onClick={currentStep === steps.length - 1 ? handleBookingSubmit : handleNextStep}
                    disabled={isSubmitting}
                    className={cn(
                      "px-6 py-2 rounded-md text-sm font-medium transition-colors",
                      isSubmitting
                        ? "bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500"
                        : "bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
                    )}
                  >
                    {isSubmitting ? 'در حال ارسال...' : 
                     currentStep === steps.length - 1 ? t.transfer.confirmBooking : t.transfer.next}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Booking Summary
              </h3>
              
              {selectedRoute && (
                <div className="space-y-4">
                  {/* Route Info */}
                  <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {selectedRoute.origin} → {selectedRoute.destination}
                    </div>
                    {pricing && (
                      <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                        {formatCurrency(pricing.base_price)} {(pricing as any).currency || 'USD'}
                      </div>
                    )}
                  </div>

                  {/* Trip Details */}
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Trip Type:</span>
                      <span className="font-medium">
                        {bookingData.trip_type === 'round_trip' ? 'Round Trip' : 'One Way'}
                      </span>
                    </div>
                    
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Passengers:</span>
                      <span className="font-medium">{bookingData.passenger_count}</span>
                    </div>
                    
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Luggage:</span>
                      <span className="font-medium">{bookingData.luggage_count}</span>
                    </div>
                    
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Vehicle Type:</span>
                      <span className="font-medium">{selectedVehicle?.name}</span>
                    </div>
                  </div>

                  {/* Time Details */}
                  {bookingData.booking_date && (
                    <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        Time Details:
                      </h4>
                      
                      <div className="space-y-2">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            Outbound Time:
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {bookingData.booking_date} ساعت {bookingData.booking_time}
                          </div>
                          {(() => {
                            const hour = parseInt(bookingData.booking_time?.split(':')[0] || '0');
                            if (hour >= 22 || hour <= 6) {
                              return (
                                <div className="text-xs text-purple-600 dark:text-purple-400">
                                  (Midnight Surcharge +5.00%)
                                </div>
                              );
                            } else if (hour >= 7 && hour <= 9 || hour >= 17 && hour <= 19) {
                              return (
                                <div className="text-xs text-orange-600 dark:text-orange-400">
                                  (Peak Hour Surcharge +10.00%)
                                </div>
                              );
                            }
                            return null;
                          })()}
                        </div>
                        
                        {bookingData.trip_type === 'round_trip' && bookingData.return_date && bookingData.return_time && (
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              Return Time:
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              {bookingData.return_date} ساعت {bookingData.return_time}
                            </div>
                            {(() => {
                              const hour = parseInt(bookingData.return_time?.split(':')[0] || '0');
                              if (hour >= 22 || hour <= 6) {
                                return (
                                  <div className="text-xs text-purple-600 dark:text-purple-400">
                                    (Midnight Surcharge +5.00%)
                                  </div>
                                );
                              } else if (hour >= 7 && hour <= 9 || hour >= 17 && hour <= 19) {
                                return (
                                  <div className="text-xs text-orange-600 dark:text-orange-400">
                                    (Peak Hour Surcharge +10.00%)
                                  </div>
                                );
                              }
                              return null;
                            })()}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Pricing Breakdown */}
                  {pricing && (
                    <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        Pricing Breakdown:
                      </h4>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Base Price</span>
                          <span className="font-medium">{formatCurrency(pricing.base_price)}</span>
                        </div>
                        
                        {bookingData.trip_type === 'round_trip' && (
                          <>
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">$120.00 Outbound</span>
                              <span className="font-medium">{formatCurrency(pricing.base_price)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">$120.00 Return</span>
                              <span className="font-medium">{formatCurrency(pricing.base_price)}</span>
                            </div>
                          </>
                        )}
                        
                        {pricing.night_surcharge > 0 && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">
                              {(() => {
                                const hour = parseInt(bookingData.booking_time?.split(':')[0] || '0');
                                if (hour >= 22 || hour <= 6) {
                                  return 'Outbound Surcharge Midnight +5%';
                                } else {
                                  return 'Outbound Surcharge Peak Hours +10%';
                                }
                              })()}
                            </span>
                            <span className="font-medium text-orange-600 dark:text-orange-400">
                              +{formatCurrency(pricing.night_surcharge)}
                            </span>
                          </div>
                        )}
                        
                        {bookingData.trip_type === 'round_trip' && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Return Surcharge Return Trip +10%</span>
                            <span className="font-medium text-orange-600 dark:text-orange-400">
                              +{formatCurrency(pricing.night_surcharge || 0)}
                            </span>
                          </div>
                        )}
                        
                        {pricing.return_discount > 0 && (
                          <div className="flex justify-between text-green-600 dark:text-green-400">
                            <span>Round Trip Discount -{(pricing as any).round_trip_discount_percentage?.toFixed(0) || 0}%</span>
                            <span className="font-medium">-{formatCurrency(pricing.return_discount)}</span>
                          </div>
                        )}
                        
                        {/* Options */}
                        {bookingData.selected_options && bookingData.selected_options.length > 0 && (
                          <>
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-600 dark:text-gray-400">Add-ons</span>
                              <span className="font-medium text-blue-600 dark:text-blue-400">
                                ({bookingData.selected_options.length} Items)
                              </span>
                            </div>
                            {bookingData.selected_options.map(option => {
                              const selectedRoute = routes.find(route => route.id === bookingData.route_id);
                              const routeSpecificOptions = selectedRoute?.options || [];
                              const globalOptions = options || [];
                              const optionData = [...routeSpecificOptions, ...globalOptions].find(opt => opt.id === option.option_id);
                              const optionPrice = optionData?.price || option.price || 0;
                              const totalPrice = optionPrice * option.quantity;
                              
                              return (
                                <div key={option.option_id} className="flex justify-between text-sm pl-4">
                                  <span className="text-gray-600 dark:text-gray-400">
                                    {optionData?.name || option.name} ({formatCurrency(optionPrice)} × {option.quantity})
                                  </span>
                                  <span className="font-medium text-blue-600 dark:text-blue-400">
                                    {formatCurrency(totalPrice)}
                                  </span>
                                </div>
                              );
                            })}
                            <div className="flex justify-between text-sm font-medium">
                              <span className="text-gray-600 dark:text-gray-400">Total Options:</span>
                              <span className="text-blue-600 dark:text-blue-400">
                                {formatCurrency(pricing.options_total || 0)}
                              </span>
                            </div>
                          </>
                        )}
                        
                        {/* Subtotal */}
                        <div className="border-t border-gray-200 dark:border-gray-700 pt-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Subtotal</span>
                            <span className="font-medium">{formatCurrency(pricing.subtotal || pricing.final_price)}</span>
                          </div>
                        </div>
                        
                        {/* Fees */}
                        {pricing.fees_total > 0 && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Service Fee (3%)</span>
                            <span className="font-medium text-blue-600 dark:text-blue-400">
                              +{formatCurrency(pricing.fees_total)}
                            </span>
                          </div>
                        )}
                        
                        {/* Tax */}
                        {pricing.tax_total > 0 && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">VAT (9%)</span>
                            <span className="font-medium text-purple-600 dark:text-purple-400">
                              +{formatCurrency(pricing.tax_total)}
                            </span>
                          </div>
                        )}
                        
                        {/* Final Total */}
                        <div className="border-t border-gray-200 dark:border-gray-700 pt-2">
                          <div className="flex justify-between text-base font-semibold">
                            <span>Total</span>
                            <span className="text-blue-600 dark:text-blue-400">
                              {formatCurrency(pricing.grand_total || pricing.customer_price)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {!selectedRoute && (
                <div className="text-center py-8">
                  <p className="text-gray-500 dark:text-gray-400">
                    Please select a route and vehicle first
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}