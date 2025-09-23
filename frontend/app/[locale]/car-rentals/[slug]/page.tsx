'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useTranslations, useLocale } from 'next-intl';
import { motion, AnimatePresence } from 'framer-motion';
import { useCart } from '@/app/lib/hooks/useCart';
import { useCustomerData } from '../../../../lib/hooks/useCustomerData';
import { useCarRentalBySlug, useCarRentalOptionsForCar, useCarRentalLocations } from '../../../../lib/hooks/useCarRentals';
import type { CarRental } from '../../../../lib/types/car-rentals';
import { useCarRentalBookingStore } from '../../../../lib/stores/carRentalBookingStore';
import { useToast } from '@/components/Toast';
import { 
  Car,
  MapPin,
  ChevronLeft,
  ChevronRight,
  Users
} from 'lucide-react';
import Link from 'next/link';
import OptimizedImage from '@/components/common/OptimizedImage';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import ProductCancellationPolicy from '@/components/common/ProductCancellationPolicy';

// Import booking components
import BookingProgressBar from './components/BookingProgressBar';
import DateLocationStep from './components/DateLocationStep';
import VehicleSelectionStep from './components/VehicleSelectionStep';
import OptionsSelectionStep from './components/OptionsSelectionStep';
import DriverInfoStep from './components/DriverInfoStep';
import BookingSummaryStep from './components/BookingSummaryStep';

interface BookingStep {
  id: number;
  title: string;
  description: string;
  isComplete: boolean;
  isActive: boolean;
}

export default function CarRentalDetailPage() {
  const params = useParams();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations('carRentalBooking');
  const { customerData } = useCustomerData();
  const { addItem } = useCart();
  const { showToast } = useToast();
  
  const slug = params.slug as string;
  
  const { data: carRental, isLoading } = useCarRentalBySlug(slug);
  const { data: options } = useCarRentalOptionsForCar(slug);
  const { data: allLocations } = useCarRentalLocations();
  
  // Extract default locations from car rental data or use all locations as fallback
  const defaultPickupLocations = Array.isArray(carRental?.default_pickup_locations) 
    ? carRental.default_pickup_locations 
    : Array.isArray(allLocations) 
      ? allLocations.map(loc => ({
          ...loc,
          location_type: loc.location_type || 'other' as const
        }))
      : [];
  const defaultDropoffLocations = Array.isArray(carRental?.default_dropoff_locations) 
    ? carRental.default_dropoff_locations 
    : Array.isArray(allLocations) 
      ? allLocations.map(loc => ({
          ...loc,
          location_type: loc.location_type || 'other' as const
        }))
      : [];
  const allowCustomPickupLocation = carRental?.allow_custom_pickup_location ?? true;
  const allowCustomDropoffLocation = carRental?.allow_custom_dropoff_location ?? true;
  
  const {
    pickup_date,
    dropoff_date,
    pickup_time,
    dropoff_time,
    pickup_location,
    dropoff_location,
    driver_name,
    driver_license,
    driver_phone,
    driver_email,
    additional_drivers,
    selected_options,
    basic_insurance,
    comprehensive_insurance,
    special_requirements,
    pricing_breakdown,
    total_price,
    currency,
    rental_type,
    rental_days,
    rental_hours,
    total_hours,
    setCarRental,
    setRentalDates,
    setRentalLocations,
    setDriverInfo,
    setSelectedOptions,
    setInsurance,
    calculatePricing,
    resetBooking
  } = useCarRentalBookingStore();

  // Tab state - start with booking tab for better UX
  const [activeTab, setActiveTab] = useState<'details' | 'booking'>('booking');
  
  // Booking flow state
  const [currentStep, setCurrentStep] = useState(1);
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Booking steps
  const [bookingSteps, setBookingSteps] = useState<BookingStep[]>([
    {
      id: 1,
      title: t('selectDatesAndLocation'),
      description: t('choosePickupDropoff'),
      isComplete: false,
      isActive: true
    },
    {
      id: 2,
      title: t('confirmVehicle'),
      description: t('reviewVehicleDetails'),
      isComplete: false,
      isActive: false
    },
    {
      id: 3,
      title: t('selectOptions'),
      description: t('chooseAddOns'),
      isComplete: false,
      isActive: false
    },
    {
      id: 4,
      title: t('driverInformation'),
      description: t('enterDriverDetails'),
      isComplete: false,
      isActive: false
    },
    {
      id: 5,
      title: t('reviewBooking'),
      description: t('confirmAndBook'),
      isComplete: false,
      isActive: false
    }
  ]);

  // Reset booking form when slug changes (when navigating from list to detail)
  useEffect(() => {
    // Reset the booking form when the slug changes
    resetBooking();
    setCurrentStep(1);
    // Set booking tab as active for better UX
    setActiveTab('booking');
    // Reset booking steps
    setBookingSteps([
      {
        id: 1,
        title: t('selectDatesAndLocation'),
        description: t('choosePickupDropoff'),
        isComplete: false,
        isActive: true
      },
      {
        id: 2,
        title: t('confirmVehicle'),
        description: t('reviewVehicleDetails'),
        isComplete: false,
        isActive: false
      },
      {
        id: 3,
        title: t('selectOptions'),
        description: t('chooseAddOns'),
        isComplete: false,
        isActive: false
      },
      {
        id: 4,
        title: t('driverInformation'),
        description: t('enterDriverDetails'),
        isComplete: false,
        isActive: false
      },
      {
        id: 5,
        title: t('reviewBooking'),
        description: t('confirmAndBook'),
        isComplete: false,
        isActive: false
      }
    ]);
  }, [slug, resetBooking, t]);

  // Set car rental data when loaded
  useEffect(() => {
    if (carRental) {
      // Set the new car rental data
      setCarRental(carRental);
    }
  }, [carRental, setCarRental]);

  // Pre-fill driver info from customer data
  useEffect(() => {
    if (customerData && !driver_name) {
      setDriverInfo({
        driver_name: customerData.full_name || '',
        driver_license: customerData.driver_license || '',
        driver_phone: customerData.phone || '',
        driver_email: customerData.email || '',
        additional_drivers: []
      });
    }
  }, [customerData, driver_name, setDriverInfo]);

  // Update booking steps based on current state
  useEffect(() => {
    setBookingSteps(prev => prev.map(step => ({
      ...step,
      isComplete: step.id === 1 ? !!(pickup_date && dropoff_date && pickup_time && dropoff_time) :
                  step.id === 2 ? true : // Vehicle is already selected
                  step.id === 3 ? true : // Options are optional
                  step.id === 4 ? !!(driver_name && driver_license && driver_phone && driver_email) :
                  step.id === 5 ? !!pricing_breakdown : false,
      isActive: step.id === currentStep
    })));
  }, [pickup_date, dropoff_date, pickup_time, dropoff_time, driver_name, driver_license, driver_phone, driver_email, pricing_breakdown, currentStep]);

  // Calculate pricing when dates change
  useEffect(() => {
    if (pickup_date && dropoff_date && carRental) {
      calculatePricing();
    }
  }, [pickup_date, dropoff_date, carRental, calculatePricing]);

  // Booking flow handlers
  const handleStepClick = useCallback((stepId: number) => {
    if (stepId <= currentStep || bookingSteps[stepId - 1]?.isComplete) {
      setCurrentStep(stepId);
    }
  }, [currentStep, bookingSteps]);

  const handleNextStep = useCallback(() => {
    if (currentStep < bookingSteps.length) {
      setCurrentStep(currentStep + 1);
    }
  }, [currentStep, bookingSteps.length]);

  const handlePrevStep = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  }, [currentStep]);

  const handleDateChange = useCallback((field: 'pickup_date' | 'dropoff_date', value: string) => {
    console.log('Date change:', field, value);
    
    // Only update the specific field that changed, don't auto-set other fields
    if (field === 'pickup_date') {
      setRentalDates(
        value,
        dropoff_date || '', // Keep existing dropoff_date, don't auto-set
        pickup_time || '',
        dropoff_time || ''
      );
    } else {
      setRentalDates(
        pickup_date || '',
        value,
        pickup_time || '',
        dropoff_time || ''
      );
    }
  }, [pickup_date, dropoff_date, pickup_time, dropoff_time, setRentalDates]);

  const handleTimeChange = useCallback((field: 'pickup_time' | 'dropoff_time', value: string) => {
    console.log('Time change:', field, value);
    
    // Only update the specific field that changed, don't auto-set other fields
    if (field === 'pickup_time') {
      setRentalDates(
        pickup_date || '',
        dropoff_date || '',
        value,
        dropoff_time || '' // Keep existing dropoff_time, don't auto-set
      );
    } else {
      setRentalDates(
        pickup_date || '',
        dropoff_date || '',
        pickup_time || '', // Keep existing pickup_time, don't auto-set
        value
      );
    }
  }, [pickup_date, dropoff_date, pickup_time, dropoff_time, setRentalDates]);

  const handleLocationChange = useCallback((field: 'pickup_location' | 'dropoff_location', value: string) => {
    // Only update the specific field that changed, don't auto-set other fields
    if (field === 'pickup_location') {
      setRentalLocations(value, dropoff_location || '');
    } else {
      setRentalLocations(pickup_location || '', value);
    }
  }, [pickup_location, dropoff_location, setRentalLocations]);

  const handleDriverInfoChange = useCallback((info: {
    driver_name: string;
    driver_license: string;
    driver_phone: string;
    driver_email: string;
    additional_drivers?: Array<{ name: string; license: string; phone: string; }>;
  }) => {
    setDriverInfo(info);
  }, [setDriverInfo]);

  const handleOptionsChange = useCallback((options: Array<{
    id: string;
    quantity: number;
    name?: string;
    price?: string | number;
    description?: string;
  }>) => {
    // Convert price from number to string as expected by the store
    const convertedOptions = options.map(option => ({
      ...option,
      price: typeof option.price === 'number' ? option.price.toString() : option.price,
      price_type: 'fixed' as const
    }));
    setSelectedOptions(convertedOptions);
  }, [setSelectedOptions]);

  const handleInsuranceChange = useCallback((basic: boolean, comprehensive: boolean) => {
    setInsurance(basic, comprehensive);
  }, [setInsurance]);

  const handleConfirmBooking = useCallback(async () => {
    if (!carRental || !pickup_date || !dropoff_date || !pickup_time || !dropoff_time) {
      showToast(t('selectDatesRequired'), 'error');
      return;
    }

    if (!driver_name || !driver_license || !driver_phone || !driver_email) {
      showToast(t('driverInfoRequired'), 'error');
      return;
    }

    if (!total_price || total_price <= 0) {
      showToast('Please wait for price calculation to complete', 'error');
      return;
    }

    setIsAddingToCart(true);

    try {
      const rentalDays = Math.ceil((new Date(dropoff_date).getTime() - new Date(pickup_date).getTime()) / (1000 * 60 * 60 * 24));
      
      const bookingData = {
        product_type: 'car_rental' as const,
        product_id: carRental.id,
        product_title: carRental.title,
        product_slug: carRental.slug,
        booking_date: pickup_date,
        booking_time: pickup_time,
        quantity: 1,
        unit_price: total_price || 0,
        total_price: total_price || 0,
        currency: currency,
        selected_options: selected_options.map(opt => ({
          option_id: opt.id,
          quantity: opt.quantity,
          price: typeof opt.price === 'string' ? parseFloat(opt.price) : opt.price || 0
        })),
        options_total: selected_options.reduce((sum, opt) => sum + ((typeof opt.price === 'string' ? parseFloat(opt.price) : opt.price || 0) * opt.quantity), 0),
        comprehensive_insurance: comprehensive_insurance,
        insurance_total: comprehensive_insurance ? (carRental?.comprehensive_insurance_price ? parseFloat(carRental.comprehensive_insurance_price) * rentalDays : 0) : 0,
        booking_data: {
          car_rental_id: carRental.id,
          pickup_date,
          dropoff_date,
          pickup_time: pickup_time,
          dropoff_time: dropoff_time,
          rental_days: rentalDays,
          driver_name,
          driver_license,
          driver_phone,
          driver_email,
          additional_drivers: additional_drivers || [],
          basic_insurance,
          comprehensive_insurance,
          special_requirements,
          selected_options: selected_options,
          pricing_breakdown: pricing_breakdown
        }
      };

      console.log('Adding car rental to cart with data:', bookingData);

      const result = await addItem(bookingData);
      
      if (result.success) {
        showToast(t('bookingSuccess'), 'success');
        
        // Reset booking form
        resetBooking();
        
        // Navigate to cart page
        router.push(`/${locale}/cart`);
      } else {
        console.error('Add to cart failed:', result.error);
        showToast(result.error || t('bookingError'), 'error');
      }
    } catch (error) {
      console.error('Error adding car rental to cart:', error);
      showToast(t('bookingError'), 'error');
    } finally {
      setIsAddingToCart(false);
    }
  }, [
    carRental, pickup_date, dropoff_date, pickup_time, dropoff_time,
    driver_name, driver_license, driver_phone, driver_email,
    additional_drivers, selected_options, basic_insurance, comprehensive_insurance,
    special_requirements, total_price, currency, pricing_breakdown, addItem, showToast, t, resetBooking, router, locale
  ]);


  const getFuelIcon = (fuelType: string) => {
    switch (fuelType) {
      case 'gasoline': return '⛽';
      case 'diesel': return '🚛';
      case 'hybrid': return '🔋';
      case 'electric': return '⚡';
      case 'lpg': return '🔥';
      default: return '⛽';
    }
  };

  const getTransmissionIcon = (transmission: string) => {
    switch (transmission) {
      case 'manual': return '🔄';
      case 'automatic': return '⚙️';
      case 'semi_automatic': return '🔧';
      default: return '⚙️';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!carRental) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            {t('carNotFound')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            {t('carNotFoundDesc')}
          </p>
          <Link href="/car-rentals">
            <Button>{t('browseAllCars')}</Button>
          </Link>
        </div>
      </div>
    );
  }

  // Check if car is available
  if (!carRental.is_available) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="mb-6">
            <div className="w-24 h-24 mx-auto mb-4 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
              <span className="text-4xl">🚫</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              {t('carNotAvailable')}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              {t('carNotAvailableDesc')}
            </p>
          </div>
          <div className="space-x-4">
            <Link href="/car-rentals">
              <Button>{t('browseAllCars')}</Button>
            </Link>
            <Button variant="outline" onClick={() => router.back()}>
              {t('goBack')}
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const images = carRental.image_url ? [carRental.image_url] : [];
  const currentImage = images[currentImageIndex] || '/images/placeholder-car.jpg';

  const renderBookingStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <DateLocationStep
            pickupDate={pickup_date}
            dropoffDate={dropoff_date}
            pickupTime={pickup_time}
            dropoffTime={dropoff_time}
            pickupLocation={pickup_location}
            dropoffLocation={dropoff_location}
            onDateChange={handleDateChange}
            onTimeChange={handleTimeChange}
            onLocationChange={handleLocationChange}
            onNext={handleNextStep}
            isLoading={isAddingToCart}
            defaultPickupLocations={defaultPickupLocations}
            defaultDropoffLocations={defaultDropoffLocations}
            allowCustomPickupLocation={allowCustomPickupLocation}
            allowCustomDropoffLocation={allowCustomDropoffLocation}
            carRental={carRental ? {
              price_per_day: parseFloat(carRental.price_per_day),
              price_per_hour: carRental.price_per_hour ? parseFloat(carRental.price_per_hour) : undefined,
              weekly_discount_percentage: (carRental as CarRental & { weekly_discount_percentage?: number }).weekly_discount_percentage || 0,
              monthly_discount_percentage: (carRental as CarRental & { monthly_discount_percentage?: number }).monthly_discount_percentage || 0,
              currency: carRental.currency,
              min_rent_days: (carRental as CarRental & { min_rent_days?: number }).min_rent_days || 1,
              max_rent_days: (carRental as CarRental & { max_rent_days?: number }).max_rent_days || 30,
              mileage_limit_per_day: (carRental as CarRental & { mileage_limit_per_day?: number }).mileage_limit_per_day || 200,
              advance_booking_days: (carRental as CarRental & { advance_booking_days?: number }).advance_booking_days || 1,
              deposit_amount: (carRental as CarRental & { deposit_amount?: number }).deposit_amount || 0,
              allow_hourly_rental: carRental.allow_hourly_rental ?? false,
              min_rent_hours: carRental.min_rent_hours || 2,
              max_hourly_rental_hours: carRental.max_hourly_rental_hours || 8
            } : undefined}
          />
        );
      case 2:
        return (
          <VehicleSelectionStep
            carRental={carRental}
            onNext={handleNextStep}
            onBack={handlePrevStep}
            isLoading={isAddingToCart}
            bookingInfo={{
              pickup_date: pickup_date || '',
              dropoff_date: dropoff_date || '',
              pickup_time: pickup_time || '',
              dropoff_time: dropoff_time || '',
              pickup_location: pickup_location || '',
              dropoff_location: dropoff_location || '',
              rental_type: rental_type,
              rental_days: rental_days,
              rental_hours: rental_hours,
              total_hours: total_hours
            }}
          />
        );
      case 3:
        return (
          <OptionsSelectionStep
            options={options || []}
            selectedOptions={selected_options}
            basicInsurance={basic_insurance}
            comprehensiveInsurance={comprehensive_insurance}
            onOptionsChange={handleOptionsChange}
            onInsuranceChange={handleInsuranceChange}
            onNext={handleNextStep}
            onBack={handlePrevStep}
            isLoading={isAddingToCart}
            currency={currency}
            rentalDays={Math.ceil((new Date(dropoff_date || '').getTime() - new Date(pickup_date || '').getTime()) / (1000 * 60 * 60 * 24))}
            carRentalData={carRental}
          />
        );
      case 4:
        return (
          <DriverInfoStep
            driverInfo={{
              driver_name,
              driver_license,
              driver_phone,
              driver_email,
              additional_drivers: additional_drivers || []
            }}
            onDriverInfoChange={handleDriverInfoChange}
            onNext={handleNextStep}
            onBack={handlePrevStep}
            isLoading={isAddingToCart}
          />
        );
      case 5:
        return (
          <BookingSummaryStep
            carRental={carRental}
            pickupDate={pickup_date || ''}
            dropoffDate={dropoff_date || ''}
            pickupTime={pickup_time || ''}
            dropoffTime={dropoff_time || ''}
            pickupLocation={carRental.pickup_location}
            dropoffLocation={carRental.dropoff_location}
            driverInfo={{
              driver_name,
              driver_license,
              driver_phone,
              driver_email,
              additional_drivers: additional_drivers || []
            }}
            selectedOptions={selected_options}
            basicInsurance={basic_insurance}
            comprehensiveInsurance={comprehensive_insurance}
            specialRequirements={special_requirements}
            pricingBreakdown={pricing_breakdown}
            currency={currency}
            onConfirm={handleConfirmBooking}
            onBack={handlePrevStep}
            isLoading={isAddingToCart}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/car-rentals">
              <Button variant="ghost" size="sm">
                <ChevronLeft className="w-4 h-4 mr-1" />
                {t('backToCars')}
              </Button>
            </Link>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {carRental.title}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {carRental.brand} {carRental.model} • {carRental.year}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('details')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'details'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                {t('details')}
              </button>
              <button
                onClick={() => {
                  setActiveTab('booking');
                  // Reset to first step when switching to booking tab
                  setCurrentStep(1);
                }}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'booking'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                {t('booking')}
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'details' ? (
            <motion.div
              key="details"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-8"
            >
              {/* Image Gallery */}
              <Card>
                <CardContent className="p-0">
                  <div className="relative h-96 overflow-hidden rounded-lg">
                    <OptimizedImage
                      src={currentImage}
                      alt={carRental.title}
                      fill
                      className="w-full h-full object-cover"
                      fallbackSrc="/images/placeholder-car.jpg"
                    />
                    
                    {images.length > 1 && (
                      <>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white/90"
                          onClick={() => setCurrentImageIndex(Math.max(0, currentImageIndex - 1))}
                          disabled={currentImageIndex === 0}
                        >
                          <ChevronLeft className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white/90"
                          onClick={() => setCurrentImageIndex(Math.min(images.length - 1, currentImageIndex + 1))}
                          disabled={currentImageIndex === images.length - 1}
                        >
                          <ChevronRight className="w-4 h-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Car Details */}
              <Card>
                <CardHeader>
                  <CardTitle>{t('carDetails')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div className="text-center">
                      <div className="text-2xl mb-2">{getFuelIcon(carRental.fuel_type)}</div>
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{t('fuelType')}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">{carRental.fuel_type}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl mb-2">{getTransmissionIcon(carRental.transmission)}</div>
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{t('transmission')}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">{carRental.transmission}</div>
                    </div>
                    <div className="text-center">
                      <Users className="w-6 h-6 mx-auto mb-2 text-gray-600 dark:text-gray-400" />
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{t('seats')}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">{carRental.seats}</div>
                    </div>
                    <div className="text-center">
                      <Car className="w-6 h-6 mx-auto mb-2 text-gray-600 dark:text-gray-400" />
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{t('year')}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">{carRental.year}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Description */}
              <Card>
                <CardHeader>
                  <CardTitle>{t('description')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {carRental.description}
                  </p>
                </CardContent>
              </Card>

              {/* Location */}
              <Card>
                <CardHeader>
                  <CardTitle>{t('pickupDropoffLocation')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <MapPin className="w-5 h-5 text-blue-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">{t('pickupLocation')}</div>
                        <div className="text-gray-600 dark:text-gray-400">{carRental.pickup_location}</div>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <MapPin className="w-5 h-5 text-green-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">{t('dropoffLocation')}</div>
                        <div className="text-gray-600 dark:text-gray-400">{carRental.dropoff_location}</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Cancellation Policy */}
              <ProductCancellationPolicy 
                productType="car_rental" 
                policies={[]}
                productData={{
                  title: carRental.title,
                  duration: `${Math.ceil((new Date(dropoff_date || '').getTime() - new Date(pickup_date || '').getTime()) / (1000 * 60 * 60 * 24))} days`
                }}
              />
            </motion.div>
          ) : (
            <motion.div
              key="booking"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-8"
            >
              {/* Booking Progress Bar */}
              <BookingProgressBar
                steps={bookingSteps}
                currentStep={currentStep}
                onStepClick={handleStepClick}
              />

              {/* Booking Step Content */}
              {renderBookingStep()}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
