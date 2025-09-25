'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter, useSearchParams, useParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  MapPin,
  Calendar,
  Users,
  Package,
  Car,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../../../lib/contexts/AuthContext';
import { useCart } from '../../../../lib/hooks/useCart';
import { useTransferBookingStore } from '@/lib/stores/transferBookingStore';
import { useHydration } from '@/lib/hooks/useHydration';
import { BookingStep } from '@/lib/types/transfers';
import PricingBreakdown from '@/components/events/PricingBreakdown';
import ProductCancellationPolicy from '@/components/common/ProductCancellationPolicy';

import RouteSelection from './components/RouteSelection';
import VehicleSelection from './components/VehicleSelection';
import DateTimeSelection from './components/DateTimeSelection';
import PassengerSelection from './components/PassengerSelection';
import OptionsSelection from './components/OptionsSelection';
import ContactForm from './components/ContactForm';
import BookingSummary from './components/BookingSummary';
import ErrorBoundary from '@/components/ErrorBoundary';
import { ToastProvider } from '@/components/Toast';
import OptimizedImage from '@/components/common/OptimizedImage';

// STEPS will be populated with translations in useEffect
const STEPS: { key: BookingStep; title: string; description: string }[] = [
  { key: 'route', title: '', description: '' },
  { key: 'vehicle', title: '', description: '' },
  { key: 'datetime', title: '', description: '' },
  { key: 'passengers', title: '', description: '' },
  { key: 'options', title: '', description: '' },
  { key: 'contact', title: '', description: '' },
  { key: 'summary', title: '', description: '' },
];

export default function TransferBookingPage() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <TransferBookingContent />
      </ToastProvider>
    </ErrorBoundary>
  );
}

function TransferBookingContent() {
  const t = useTranslations('transfers');
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = useParams();
  const locale = params.locale as string;
  const { isAuthenticated } = useAuth();
  const { refreshCart } = useCart();
  
  // Hydration safety
  const mounted = useHydration();
  
  // PricingBreakdown state
  const [showPricingDetails, setShowPricingDetails] = useState(false);
  const [discountCode, setDiscountCode] = useState('');
  
  // Get booking state from store
  const {
    current_step,
    setCurrentStep,
    isStepValid,
    getNextStep,
    getPreviousStep,
    calculatePrice,
    addToCart,
    updateBookingData,
    route_data,
    vehicle_type,
    trip_type,
    outbound_date,
    outbound_time,
    return_date,
    return_time,
    passenger_count,
    luggage_count,
    selected_options,
    pricing_breakdown,
  } = useTransferBookingStore();

  // Initialize from URL params
  useEffect(() => {
    const origin = searchParams.get('origin');
    const destination = searchParams.get('destination');
    const route_id = searchParams.get('route_id');

    if (origin && destination && route_id) {
      // If we have route_id, we should fetch the route data
      // This will be handled by the RouteSelection component
    }
  }, [searchParams]);

  // Check for pending transfer booking after login
  useEffect(() => {
    if (isAuthenticated) {
      const completeBookingData = localStorage.getItem('completeTransferBooking');
      if (completeBookingData) {
        try {
          const bookingData = JSON.parse(completeBookingData);
          
          // Restore booking data to store
          updateBookingData({
            route_data: bookingData.route_data,
            vehicle_type: bookingData.vehicle_type,
            trip_type: bookingData.trip_type,
            outbound_date: bookingData.outbound_date,
            outbound_time: bookingData.outbound_time,
            return_date: bookingData.return_date,
            return_time: bookingData.return_time,
            passenger_count: bookingData.passenger_count,
            luggage_count: bookingData.luggage_count,
            selected_options: bookingData.selected_options,
            contact_name: bookingData.contact_name,
            contact_phone: bookingData.contact_phone,
            special_requirements: bookingData.special_requirements,
            pricing_breakdown: bookingData.pricing_breakdown,
            final_price: bookingData.final_price,
            current_step: 'summary'
          });
          
          // Auto-complete the booking
          setTimeout(async () => {
            const result = await addToCart();
            if (result.success) {
              // Refresh cart to update navbar count
              await refreshCart();
              // Clear the stored booking data
              localStorage.removeItem('completeTransferBooking');
              // Redirect to cart with locale
              router.push(`/${locale}/cart`);
            } else {
              console.error('Failed to complete booking:', result.error);
              // Stay on current step for manual retry
              setCurrentStep('summary');
            }
          }, 1000);
          
        } catch (error) {
          console.error('Error processing pending booking:', error);
          localStorage.removeItem('completeTransferBooking');
        }
      }
    }
  }, [isAuthenticated, addToCart, updateBookingData, router, setCurrentStep, locale, refreshCart]);

  // Populate STEPS with translations
  useEffect(() => {
    STEPS[0] = { key: 'route', title: t('stepRouteTitle'), description: t('stepRouteDescription') };
    STEPS[1] = { key: 'vehicle', title: t('stepVehicleTitle'), description: t('stepVehicleDescription') };
    STEPS[2] = { key: 'datetime', title: t('stepDateTimeTitle'), description: t('stepDateTimeDescription') };
    STEPS[3] = { key: 'passengers', title: t('stepPassengersTitle'), description: t('stepPassengersDescription') };
    STEPS[4] = { key: 'options', title: t('stepOptionsTitle'), description: t('stepOptionsDescription') };
    STEPS[5] = { key: 'contact', title: t('stepContactTitle'), description: t('stepContactDescription') };
    STEPS[6] = { key: 'summary', title: t('stepSummaryTitle'), description: t('stepSummaryDescription') };
  }, [t]);

  // Don't render until mounted (hydration complete)
  if (!mounted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-8">
            {/* Header Skeleton */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
              <div className="h-64 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded-t-2xl"></div>
              <div className="p-8 space-y-4">
                <div className="h-8 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded-lg w-3/4"></div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="h-16 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded-xl"></div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Steps Skeleton */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-8">
              <div className="h-6 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded-lg w-48 mb-6"></div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-7 gap-4">
                {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                  <div key={i} className="flex flex-col items-center space-y-2">
                    <div className="w-12 h-12 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded-full"></div>
                    <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded w-16"></div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Content Skeleton */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="h-96 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-8">
                  <div className="space-y-4">
                    <div className="h-6 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded-lg w-1/2"></div>
                    <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded-lg w-3/4"></div>
                    <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded-lg w-1/2"></div>
                  </div>
                </div>
              </div>
              <div className="space-y-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-48 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-6">
                    <div className="space-y-3">
                      <div className="h-5 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded w-3/4"></div>
                      <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded w-1/2"></div>
                      <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded w-2/3"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Format price with currency
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  // Handle discount code application
  const handleDiscountApply = () => {
    // This will trigger pricing recalculation
    console.log('Applying discount:', discountCode);
  };

  // Convert transfer pricing to PricingBreakdown format with corrected calculations
  const convertToPricingBreakdown = () => {
    try {
      if (!pricing_breakdown) {
        return null;
      }

      const { price_breakdown: pb } = pricing_breakdown;
      const options_breakdown = pb?.options_breakdown || [];
      
      if (!pb) {
        return null;
      }
    
      // Use the exact values from the backend without manual calculations
      const base = Number(pb?.base_price || 0);
      const outS = Number(pb?.outbound_surcharge || 0);
      const retS = Number(pb?.return_surcharge || 0);
      const options = Number(pb?.options_total || 0);
      const rtd = Number(pb?.round_trip_discount || 0);
      
      // Use the backend's calculated values directly
      const subtotal = Number(pb?.final_price || 0);
      const final_price = Number(pb?.final_price || 0);
      
      // Calculate percentages for display
      const outS_percentage = base > 0 ? Math.round((outS / base) * 100) : 0;
      const rtd_percentage = base > 0 ? Math.round((rtd / base) * 100) : 0;
      
      // Create normalized pricing breakdown that matches the main content
      return {
        base_price: base,
        price_modifier: 1, // Default modifier for transfers
        unit_price: base,
        quantity: passenger_count || 1,
        subtotal: subtotal,
        final_price: final_price,
        pricing_type: 'transfer' as const, // Add this field to identify transfer products
        trip_type: trip_type, // Include trip type for conditional display
        
        // Transfer-specific fields
        outbound_surcharge: outS,
        outbound_surcharge_percentage: outS_percentage,
        return_surcharge: retS,
        return_surcharge_percentage: retS > 0 ? Math.round((retS / base) * 100) : 0,
        round_trip_discount: rtd,
        round_trip_discount_percentage: rtd_percentage,
        
        // Options - use the exact values from backend
        options: (options_breakdown || []).map((option: { option_id?: string; name?: string; price?: number; quantity?: number; total?: number }) => ({
          option_id: option?.option_id || '',
          name: option?.name || '',
          type: 'transfer_option',
          price: option?.price || 0,
          quantity: option?.quantity || 0,
          total: option?.total || 0
        })),
        options_total: options,
        
        // Discounts - use exact values from backend
        discounts: rtd > 0 ? [{
          type: 'fixed',
          name: t('roundTripDiscountName'),
          amount: rtd,
          percentage: rtd_percentage
        }] : [],
        discount_total: rtd,
        
        // Fees - use exact values from backend
        fees: [
          ...(outS > 0 ? [{
            name: t('outboundSurchargeName'),
            type: 'fixed',
            amount: outS
          }] : []),
          ...(retS > 0 ? [{
            name: t('returnSurchargeName'),
            type: 'fixed',
            amount: retS
          }] : [])
        ],
        fees_total: outS + retS,
        taxes: [],
        taxes_total: 0
      };
    } catch (error) {
      console.error('Error in convertToPricingBreakdown:', error);
      return null;
    }
  };

  // Navigation functions
  const nextStep = () => {
    const next = getNextStep();
    if (next) {
      setCurrentStep(next);
      
      // Auto-calculate price when moving to summary step
      if (next === 'summary') {
        calculatePrice();
      }
    }
  };

  const prevStep = () => {
    const prev = getPreviousStep();
    if (prev) {
      setCurrentStep(prev);
    }
  };



  // Handle booking confirmation
  const handleConfirmBooking = async () => {
    const result = await addToCart();
    if (result.success) {
      // Refresh cart to update navbar count
      await refreshCart();
      router.push(`/${locale}/cart`);
    } else {
      // Handle error - could show a toast notification
      console.error('Failed to add to cart:', result.error);
    }
  };

  // Render current step
  const renderCurrentStep = () => {
    switch (current_step) {
      case 'route':
        return (
          <RouteSelection
            onNext={nextStep}
          />
        );
      case 'vehicle':
        return (
          <VehicleSelection
            onNext={nextStep}
            onBack={prevStep}
          />
        );
      case 'datetime':
        return (
          <DateTimeSelection
            onNext={nextStep}
            onBack={prevStep}
          />
        );
      case 'passengers':
        return (
          <PassengerSelection
            onNext={nextStep}
            onBack={prevStep}
          />
        );
      case 'options':
        return (
          <OptionsSelection
            onNext={nextStep}
            onBack={prevStep}
          />
        );
      case 'contact':
        return (
          <ContactForm
            onNext={nextStep}
            onBack={prevStep}
          />
        );
      case 'summary':
        return (
          <BookingSummary
            onBack={prevStep}
            onConfirm={handleConfirmBooking}
          />
        );
      default:
        return null;
    }
  };

  // Format date for display
  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <motion.div 
      className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Transfer Header */}
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 mb-8 overflow-hidden"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="relative">
            <OptimizedImage
              src="/images/black-van-top.jpg"
              alt="Transfer Service"
              width={800}
              height={256}
              className="w-full h-64 object-cover rounded-t-2xl"
              style={{ width: 'auto', height: 'auto' }}
              priority
              fallbackSrc="/images/placeholder-car.jpg"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-t-2xl" />
            <motion.div 
              className="absolute top-4 left-4"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg backdrop-blur-sm">
                <Sparkles className="w-4 h-4 mr-2" />
                {t('title')}
              </span>
            </motion.div>
          </div>
          
          <motion.div 
            className="p-8"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <motion.h1 
              className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent mb-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              {t('customTransferBooking')}
            </motion.h1>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {[
                { icon: MapPin, text: `${route_data?.origin || t('selectOrigin')} → ${route_data?.destination || t('selectDestination')}`, delay: 0.6 },
                { icon: Calendar, text: outbound_date ? formatDate(outbound_date) : t('selectDate'), delay: 0.7 },
                { icon: Users, text: `${passenger_count || 0} ${t('passengerCount')}`, delay: 0.8 },
                { icon: Package, text: `${luggage_count || 0} ${t('luggageCount')}`, delay: 0.9 }
              ].map((item, index) => (
                <motion.div 
                  key={index}
                  className="flex items-center p-3 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 border border-gray-200/50 dark:border-gray-600/50 hover:shadow-md transition-all duration-300"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: item.delay }}
                  whileHover={{ scale: 1.02, y: -2 }}
                >
                  <item.icon className="h-5 w-5 mr-3 text-primary-500 dark:text-primary-400" />
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    {item.text}
                  </span>
                </motion.div>
              ))}
            </div>
            
            <motion.div 
              className="flex flex-wrap items-center gap-4 mb-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.0 }}
            >
              <div className="flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border border-primary-200/50 dark:border-primary-700/50">
                <Car className="h-5 w-5 text-primary-500 dark:text-primary-400 mr-2" />
                <span className="text-sm font-medium text-primary-700 dark:text-primary-300">
                  {vehicle_type ? vehicle_type : t('selectVehicleType')}
                </span>
              </div>
              
              <div className="flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-secondary-50 to-accent-50 dark:from-secondary-900/20 dark:to-accent-900/20 border border-secondary-200/50 dark:border-secondary-700/50">
                <span className="text-sm font-medium text-secondary-700 dark:text-secondary-300">
                  {trip_type === 'round_trip' ? t('roundTripTrip') : t('oneWayTrip')}
                </span>
              </div>
            </motion.div>
            
            <motion.p 
              className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.1 }}
            >
              {t('transferDescription')}
            </motion.p>
          </motion.div>
        </motion.div>

        {/* Booking Steps */}
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 mb-8 overflow-hidden"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="p-8">
            <motion.h2 
              className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              {t('bookingSteps')}
            </motion.h2>
            
            {/* Enhanced responsive layout with better mobile experience */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-7 gap-4">
              {STEPS.map((step, index) => (
                <motion.div 
                  key={step.key} 
                  className="relative"
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.4 + (index * 0.1) }}
                >
                  <div className="flex flex-col items-center text-center p-4 rounded-xl transition-all duration-300 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <motion.div 
                      className={`flex items-center justify-center w-12 h-12 rounded-full border-2 mb-3 transition-all duration-300 ${
                        isStepValid(step.key) 
                          ? 'bg-gradient-to-r from-success-500 to-success-600 border-success-500 text-white shadow-lg shadow-success-500/25' 
                          : current_step === step.key
                            ? 'bg-gradient-to-r from-primary-500 to-secondary-500 border-primary-500 text-white shadow-lg shadow-primary-500/25 animate-pulse-glow' 
                            : 'bg-gray-100 dark:bg-gray-600 border-gray-300 dark:border-gray-500 text-gray-400 dark:text-gray-300'
                      }`}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {isStepValid(step.key) ? (
                        <motion.div
                          initial={{ scale: 0, rotate: -180 }}
                          animate={{ scale: 1, rotate: 0 }}
                          transition={{ duration: 0.5 }}
                        >
                          <CheckCircle className="h-6 w-6" />
                        </motion.div>
                      ) : (
                        <span className="text-sm font-bold">{index + 1}</span>
                      )}
                    </motion.div>
                    
                    <div className="min-w-0 flex-1">
                      <div className={`text-sm font-semibold mb-1 transition-colors duration-300 ${
                        current_step === step.key ? 'text-primary-600 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {step.title}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                        {step.description}
                      </div>
                    </div>
                  </div>
                  
                  {/* Connection line for desktop */}
                  {index < STEPS.length - 1 && (
                    <div className="hidden xl:block absolute top-6 -right-2 w-4 h-0.5 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-600 dark:to-gray-700" />
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Booking Flow */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <motion.div 
            className="lg:col-span-2 space-y-6"
            initial={{ x: -30, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            {/* Current Step Content */}
            <motion.div 
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
              layout
              transition={{ duration: 0.3 }}
            >
              <div className="p-8">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={current_step}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    {renderCurrentStep()}
                  </motion.div>
                </AnimatePresence>
              </div>
            </motion.div>
          </motion.div>

          {/* Sidebar */}
          <motion.div 
            className="space-y-6"
            initial={{ x: 30, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {/* Comprehensive Booking Summary */}
            {route_data && (
              <motion.div 
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 sticky top-22 overflow-hidden"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20">
                  <h3 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">{t('bookingSummaryTitle')}</h3>
                </div>
                <div className="p-4 space-y-4">
                  {/* Route Information */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      <div className="flex-1">
                        <div className="font-medium text-gray-900 dark:text-gray-100 text-sm">
                          {route_data.origin} → {route_data.destination}
                        </div>
                        {pricing_breakdown?.price_breakdown?.base_price && (
                          <div className="text-xs text-gray-600 dark:text-gray-400">
                            {formatPrice(pricing_breakdown.price_breakdown.base_price)} USD
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Trip Type and Date */}
                    {trip_type && (
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        <div className="text-sm">
                          <span className="text-gray-600 dark:text-gray-400">{t('tripTypeLabel')}:</span>
                          <span className="font-medium text-gray-900 dark:text-gray-100 mr-2">
                            {trip_type === 'round_trip' ? t('roundTripTrip') : t('oneWayTrip')}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Passengers and Luggage */}
                    {(passenger_count || luggage_count) && (
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        <div className="text-sm">
                          <span className="text-gray-600 dark:text-gray-400">{t('passengerCount')}:</span>
                          <span className="font-medium text-gray-900 dark:text-gray-100 mr-3">{passenger_count || 0}</span>
                          <span className="text-gray-600 dark:text-gray-400">{t('luggageCount')}:</span>
                          <span className="font-medium text-gray-900 dark:text-gray-100">{luggage_count || 0}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Vehicle Information */}
                  {vehicle_type && (
                    <div className="pt-3 border-t border-gray-100 dark:border-gray-600">
                      <div className="space-y-3">
                        <div className="flex items-center gap-2">
                          <Car className="w-4 h-4 text-green-600 dark:text-green-400" />
                          <div className="text-sm">
                            <span className="text-gray-600 dark:text-gray-400">{t('vehicleTypeLabel')}:</span>
                            <span className="font-medium text-gray-900 dark:text-gray-100 mr-2">
                              {t(vehicle_type) || vehicle_type}
                            </span>
                          </div>
                        </div>
                        
                        {/* Vehicle Features and Amenities removed - properties don't exist on TransferRoute type */}
                      </div>
                    </div>
                  )}

                  {/* Selected Options */}
                  {selected_options && selected_options.length > 0 && (
                    <div className="pt-3 border-t border-gray-100 dark:border-gray-600">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">{t('selectedOptionsLabel')}:</div>
                      <div className="space-y-2">
                        {selected_options.map((option) => (
                          <div key={option.option_id} className="flex justify-between items-center text-xs">
                            <span className="text-gray-900 dark:text-gray-100">
                              {option.name || `${t('optionName')} ${option.option_id.slice(0, 8)}...`}
                            </span>
                            <span className="text-gray-600 dark:text-gray-400">
                              {option.quantity}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Time Information */}
                  {outbound_time && (
                    <div className="pt-3 border-t border-gray-100 dark:border-gray-600">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">{t('timeDetails')}:</div>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-gray-900 dark:text-gray-100">{t('outboundTimeLabel')}:</span>
                          <span className="text-gray-600 dark:text-gray-400">{outbound_date} ساعت {outbound_time}</span>
                          {parseFloat(route_data.peak_hour_surcharge || '0') > 0 && (
                            <span className="text-orange-600 dark:text-orange-400 text-xs">
                              ({t('peakHourSurcharge')} +{route_data.peak_hour_surcharge}%)
                            </span>
                          )}
                        </div>
                        {trip_type === 'round_trip' && return_time && (
                          <div className="flex items-center gap-2 text-xs">
                            <span className="text-gray-900 dark:text-gray-100">{t('returnTimeLabel')}:</span>
                            <span className="text-gray-600 dark:text-gray-400">{return_date} ساعت {return_time}</span>
                            {parseFloat(route_data.peak_hour_surcharge || '0') > 0 && (
                              <span className="text-orange-600 dark:text-orange-400 text-xs">
                                ({t('peakHourSurcharge')} +{route_data.peak_hour_surcharge}%)
                              </span>
                            )}
                            {parseFloat(route_data.midnight_surcharge || '0') > 0 && (
                              <span className="text-purple-600 dark:text-purple-400 text-xs">
                                ({t('midnightSurcharge')} +{route_data.midnight_surcharge}%)
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {/* Pricing Breakdown */}
            {(() => {
              try {
                if (!pricing_breakdown) {
                  return (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 dark:border-gray-700">
                      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('priceDetails')}</h3>
                      </div>
                      <div className="p-4">
                        <p className="text-sm text-gray-500 dark:text-gray-400 text-center">{t('priceDetailsMessage')}</p>
                      </div>
                    </div>
                  );
                }

                const breakdown = convertToPricingBreakdown();
                if (breakdown) {
                  return (
                    <PricingBreakdown
                      breakdown={breakdown}
                      discountCode={discountCode}
                      onDiscountCodeChange={setDiscountCode}
                      onApplyDiscount={handleDiscountApply}
                      formatPrice={formatPrice}
                      showDetails={showPricingDetails}
                      onToggleDetails={() => setShowPricingDetails(!showPricingDetails)}
                    />
                  );
                }
              } catch (error) {
                console.error('Error converting pricing breakdown:', error);
              }
              
              return (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('priceDetails')}</h3>
                  </div>
                  <div className="p-4">
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center">{t('priceDetailsMessage')}</p>
                  </div>
                </div>
              );
            })()}

            {/* Booking Button */}
            <motion.button
              onClick={handleConfirmBooking}
              disabled={!isStepValid('summary')}
              className={`w-full py-4 px-6 rounded-xl font-bold text-lg transition-all duration-300 ${
                isStepValid('summary')
                  ? 'bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white shadow-lg hover:shadow-glow transform hover:scale-[1.02]'
                  : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              }`}
              whileHover={isStepValid('summary') ? { scale: 1.02, y: -2 } : {}}
              whileTap={isStepValid('summary') ? { scale: 0.98 } : {}}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              <span className="flex items-center justify-center gap-2">
                <Sparkles className="w-5 h-5" />
                {t('addToCartButton')}
              </span>
            </motion.button>

            {/* Cancellation Policy */}
            <ProductCancellationPolicy
              policies={(() => {
                // Use backend cancellation policies if available
                if (route_data?.cancellation_policies && route_data.cancellation_policies.length > 0) {
                  return route_data.cancellation_policies
                    .filter(policy => policy.is_active)
                    .map(policy => ({
                      hours_before: policy.hours_before,
                      refund_percentage: policy.refund_percentage,
                      description: policy.description || `${policy.refund_percentage}% ${t('refundUpTo')} ${policy.hours_before} ${t('hoursBeforeService')}`
                    }));
                }
                
                // Fallback to legacy fields if new policies are not available
                if (route_data?.cancellation_hours && route_data?.refund_percentage !== undefined) {
                  return [{
                    hours_before: route_data.cancellation_hours,
                    refund_percentage: route_data.refund_percentage,
                    description: `${route_data.refund_percentage}% ${t('refundUpTo')} ${route_data.cancellation_hours} ${t('hoursBeforeService')}`
                  }];
                }
                
                // Default fallback policies if no backend data is available
                return [
                  {
                    hours_before: 24,
                    refund_percentage: 100,
                    description: t('freeCancel24h')
                  },
                  {
                    hours_before: 12,
                    refund_percentage: 75,
                    description: t('refund75Percent12h')
                  },
                  {
                    hours_before: 6,
                    refund_percentage: 50,
                    description: t('refund50Percent6h')
                  },
                  {
                    hours_before: 2,
                    refund_percentage: 0,
                    description: t('noRefund2h')
                  }
                ];
              })()}
              productType="transfer"
              productData={{
                date: outbound_date || undefined,
                time: outbound_time || undefined,
                location: route_data?.origin || undefined,
                venue: route_data?.destination || undefined,
                duration: route_data?.estimated_duration_minutes 
                  ? `${route_data.estimated_duration_minutes} ${t('estimatedDuration')}`
                  : t('defaultDuration')
              }}
              className="mb-4"
            />

            {/* Guest Info */}
            {!isAuthenticated && (
              <div className="bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-600 rounded-lg p-4">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                                     <strong>{t('guestUserNotice')}</strong> 
                   <button 
                     onClick={() => router.push(`/${locale}/login`)}
                     className="text-blue-600 dark:text-blue-400 hover:underline"
                   >
                     {t('loginSyncMessage')}
                   </button>
                </p>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
} 