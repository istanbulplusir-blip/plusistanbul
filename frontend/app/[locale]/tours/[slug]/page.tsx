'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { useCart } from '@/app/lib/hooks/useCart';
import { useAuth } from '../../../../lib/contexts/AuthContext';
import { useCustomerData } from '../../../../lib/hooks/useCustomerData';
import { apiClient } from '../../../../lib/api/client';
import { useToast } from '@/components/Toast';
import { AlertCircle } from 'lucide-react';

import ProductCancellationPolicy from '@/components/common/ProductCancellationPolicy';
import TourItinerary from '@/components/tours/TourItinerary';
import TourErrorSummary from '@/components/tours/TourErrorSummary';
import TourParticipantSelector from '@/components/tours/TourParticipantSelector';
import { 
  Calendar, 
  Clock, 
  Users, 
  Star, 
  CheckCircle, 
  Bus,
  Plus,
  Minus,
  Info,
  Sparkles
} from 'lucide-react';
import Link from 'next/link';
import OptimizedImage from '@/components/common/OptimizedImage';
import { getImageUrl } from '@/lib/utils';
import PendingOrdersDisplay from '@/components/common/PendingOrdersDisplay';

interface TourVariant {
  id: string;
  name: string;
  description: string;
  base_price: number;
  capacity: number;
  is_active: boolean;
  includes_transfer: boolean;
  includes_guide: boolean;
  includes_meal: boolean;
  includes_photographer: boolean;
  extended_hours: number;
  private_transfer: boolean;
  expert_guide: boolean;
  special_meal: boolean;
  pricing: Array<{
    id: string;
    age_group: 'infant' | 'child' | 'adult';
    age_group_display: string;
    factor: number;
    is_free: boolean;
    requires_services: boolean;
  }>;
}

interface TourSchedule {
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
  variant_capacities: Record<string, { total: number; booked: number; available: number }>;
  cutoff_datetime: string;
}

interface TourItinerary {
  id: string;
  title: string;
  description: string;
  order: number;
  duration_minutes: number;
  location: string;
  image?: string;
}

interface TourOption {
  id: string;
  name: string;
  description: string;
  price: number;
  price_percentage: number;
  currency: string;
  option_type: 'service' | 'equipment' | 'food' | 'transport';
  is_available: boolean;
  max_quantity?: number;
}

// Extend Window interface for timeout management
declare global {
  interface Window {
    pricingTimeout?: NodeJS.Timeout;
  }
}

interface TourReview {
  id: string;
  rating: number;
  title: string;
  comment: string;
  is_verified: boolean;
  is_helpful: number;
  created_at: string;
  user_name: string;
}

interface Tour {
  id: string;
  slug: string;
  title: string;
  description: string;
  short_description: string;
  highlights: string;
  rules: string;
  required_items: string;
  image: string;
  gallery_images: {
    id: string;
    image: string;
    image_url: string;
    title: string;
    description: string;
    order: number;
    is_active: boolean;
  }[];
  price: number;
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
  tour_type: 'day' | 'night';
  transport_type: 'boat' | 'land' | 'air';
  pickup_time: string;
  start_time: string;
  end_time: string;
  min_participants: number;
  category: {
    id: string;
    name: string;
    description: string;
  };
  variants: TourVariant[];
  schedules: TourSchedule[];
  itinerary: TourItinerary[];
  options: TourOption[];
  reviews: TourReview[];
  average_rating: number;
  review_count: number;
  is_available_today: boolean;
  is_active: boolean;
  pricing_summary: Record<string, {
    base_price: number;
    age_groups: Record<string, {
      factor: number;
      final_price: number;
      is_free: boolean;
    }>;
    options: Array<{
      name: string;
      price: number;
      price_percentage: number;
    }>;
  }>;
}



export default function TourDetailPage() {
  const t = useTranslations('TourDetail');
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;
  const locale = params.locale as string;
  
  const { refreshCart } = useCart();
  const { isAuthenticated, user } = useAuth();
  const { } = useCustomerData();
  const { addToast } = useToast();
  
  // State
  const [tour, setTour] = useState<Tour | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Use ref to avoid infinite loops
  const tourRef = useRef<Tour | null>(null);
  
  // Booking state
  const [selectedSchedule, setSelectedSchedule] = useState<TourSchedule | null>(null);
  const [selectedVariant, setSelectedVariant] = useState<TourVariant | null>(null);
  const [participants, setParticipants] = useState({
    adult: 1,
    child: 0,
    infant: 0
  });
  const [selectedOptions, setSelectedOptions] = useState<Record<string, number>>({});
  const [specialRequests, setSpecialRequests] = useState('');
  const [isBooking, setIsBooking] = useState(false);
  const [bookingMessage, setBookingMessage] = useState<string | null>(null);
  
  // Validation state
  const [validationErrors, setValidationErrors] = useState<{
    participants?: string;
    options?: string;
    capacity?: string;
  }>({});
  

  
  // Booking steps state
  const [bookingSteps, setBookingSteps] = useState([
    {
      id: 1,
      title: t('selectDate'),
      description: t('selectDateDesc'),
      isComplete: false,
      isActive: true
    },
    {
      id: 2,
      title: t('selectPackage'),
      description: t('selectPackageDesc'),
      isComplete: false,
      isActive: false
    },
    {
      id: 3,
      title: t('participants'),
      description: t('participantsDesc'),
      isComplete: false,
      isActive: false
    },
    {
      id: 4,
      title: t('review'),
      description: t('reviewDesc'),
      isComplete: false,
      isActive: false
    }
  ]);

  // Update booking steps based on current state
  useEffect(() => {
    setBookingSteps(prevSteps => {
      const updatedSteps = prevSteps.map(step => {
        switch (step.id) {
          case 1: // Select Date
            return {
              ...step,
              isComplete: !!selectedSchedule,
              isActive: !selectedSchedule
            };
          case 2: // Select Package
            return {
              ...step,
              isComplete: !!selectedVariant,
              isActive: !!selectedSchedule && !selectedVariant
            };
          case 3: // Participants
            return {
              ...step,
              isComplete: !!selectedVariant && participants.adult > 0,
              isActive: !!selectedVariant && participants.adult === 0
            };
          case 4: // Review
            return {
              ...step,
              isComplete: false,
              isActive: !!selectedVariant && participants.adult > 0
            };
          default:
            return step;
        }
      });
      return updatedSteps;
    });
  }, [selectedSchedule, selectedVariant, participants.adult, participants.child, participants.infant]);

  
  // Reviews state
  const [showReviewForm, setShowReviewForm] = useState(false);

  // Validation functions
  const validateParticipants = useCallback((participantsData: { adult: number; child: number; infant: number }) => {
    const errors: string[] = [];
    
    // Check total participants
    const totalParticipants = participantsData.adult + participantsData.child + participantsData.infant;
    
    if (totalParticipants === 0) {
      errors.push(t('atLeastOneParticipantRequired'));
    }
    
    if (tour && totalParticipants > tour.max_participants) {
      errors.push(t('exceedsMaxParticipants', { max: tour.max_participants }));
    }
    
    // Check infant limit
    if (participantsData.infant > 2) {
      errors.push(t('maxInfantsExceeded', { max: 2 }));
    }
    
    // Check adult + child combination limit
    const adultChildTotal = participantsData.adult + participantsData.child;
    const maxAdultChild = tour ? tour.max_participants - participantsData.infant : 0;
    if (tour && adultChildTotal > maxAdultChild) {
      errors.push(t('maxAdultChildExceeded', { 
        max: maxAdultChild, 
        infant: participantsData.infant 
      }));
    }
    
    // Check minimum participants
    if (tourRef.current && totalParticipants < tourRef.current.min_participants) {
      errors.push(t('minParticipantsRequired', { min: tourRef.current.min_participants }));
    }
    
    return errors.length > 0 ? errors.join('. ') : null;
  }, [t]); // eslint-disable-line react-hooks/exhaustive-deps

  const validateOptions = useCallback((options: Record<string, number>, tourOptions: TourOption[]) => {
    const errors: string[] = [];
    
    Object.entries(options).forEach(([optionId, quantity]) => {
      if (quantity > 0) {
        const option = tourOptions.find(opt => opt.id === optionId);
        if (option && option.max_quantity && quantity > option.max_quantity) {
          errors.push(t('optionQuantityExceeded', { 
            option: option.name, 
            max: option.max_quantity 
          }));
        }
      }
    });
    
    return errors.length > 0 ? errors.join('. ') : null;
  }, [t]);

  const validateCapacity = useCallback(async (participantsData: { adult: number; child: number; infant: number }, selectedVariant: TourVariant | null, selectedSchedule: TourSchedule | null) => {
    if (!selectedVariant || !selectedSchedule) return null;

    const totalParticipants = participantsData.adult + participantsData.child; // Infants don't count for capacity

    // First check local capacity data
    const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
    if (variantCapacity && totalParticipants > variantCapacity.available) {
      return t('insufficientCapacity', {
        requested: totalParticipants,
        available: variantCapacity.available
      });
    }

    // For authenticated users, also check backend for real-time capacity
    if (isAuthenticated && totalParticipants > 0) {
      try {
        const capacityCheckResponse = await apiClient.post('/cart/check-capacity/', {
          product_type: 'tour',
          product_id: tourRef.current?.id,
          variant_id: selectedVariant.id,
          booking_data: {
            schedule_id: selectedSchedule.id,
            participants: participantsData
          }
        }) as { data: { available: boolean; available_capacity: number } };

        if (capacityCheckResponse.data?.available === false) {
          return t('insufficientCapacity', {
            requested: totalParticipants,
            available: capacityCheckResponse.data?.available_capacity || 0
          });
        }
      } catch (error) {
        console.warn('Backend capacity check failed:', error);
        // Continue with local validation
      }
    }

    return null;
  }, [t, isAuthenticated]);



  // Reset selected variant when schedule changes
  useEffect(() => {
    if (selectedSchedule && selectedVariant) {
      const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
      const isVariantAvailable = variantCapacity && variantCapacity.available > 0;
      
      // If selected variant is not available for the new schedule, reset it
      if (!isVariantAvailable) {
        setSelectedVariant(null);
      }
    }
  }, [selectedSchedule, selectedVariant]);

  // Real-time validation
  useEffect(() => {
    const runValidation = async () => {
      const errors: typeof validationErrors = {};

      // Validate participants
      const participantError = validateParticipants(participants);
      if (participantError) {
        errors.participants = participantError;
      }

      // Validate options
      if (tourRef.current?.options) {
        const optionError = validateOptions(selectedOptions, tourRef.current.options);
        if (optionError) {
          errors.options = optionError;
        }
      }

      // Validate capacity (async)
      const capacityError = await validateCapacity(participants, selectedVariant, selectedSchedule);
      if (capacityError) {
        errors.capacity = capacityError;
      }

      setValidationErrors(errors);
    };

    runValidation();
  }, [participants, selectedOptions, selectedVariant, selectedSchedule, validateParticipants, validateOptions, validateCapacity]);
  const [newReview, setNewReview] = useState({
    rating: 5,
    title: '',
    comment: '',
    category: 'general'
  });
  const [hasPurchaseHistory, setHasPurchaseHistory] = useState(false);
  const [isCheckingPurchase, setIsCheckingPurchase] = useState(false);



  // Fetch tour data
  const fetchTour = useCallback(async () => {
    try {
      setIsLoading(true);
      try {
        // Detail endpoint is /tours/<slug>/ (baseURL already includes /api/v1)
        const resp = await apiClient.get(`/tours/${slug}/`);
        const data = (resp as { data: Tour }).data;
        setTour(data);
        tourRef.current = data;
        // Set default variant if available
        if (data.variants && data.variants.length > 0 && !selectedVariant) {
          setSelectedVariant(data.variants[0]);
        }

        // Update selectedSchedule with fresh data if it exists
        if (selectedSchedule && data.schedules) {
          const updatedSchedule = data.schedules.find(s => s.id === selectedSchedule.id);
          if (updatedSchedule) {
            setSelectedSchedule(updatedSchedule);
          }
        }

        // Fetch booking steps from API
        try {
          const bookingStepsResp = await apiClient.get(`/tours/${slug}/booking-steps/`);
          if ((bookingStepsResp as { data: unknown }).data && ((bookingStepsResp as { data: unknown }).data as { booking_steps: unknown }).booking_steps) {
            setBookingSteps(((bookingStepsResp as { data: unknown }).data as { booking_steps: unknown }).booking_steps as { id: number; title: string; description: string; isComplete: boolean; isActive: boolean; }[]);
          }
        } catch (error) {
          console.warn('Failed to fetch booking steps, using default:', error);
          // Set default booking steps if API fails
          setBookingSteps([
            {
              id: 1,
              title: t('selectDate'),
              description: t('selectDateDesc'),
              isComplete: false,
              isActive: true
            },
            {
              id: 2,
              title: t('selectPackage'),
              description: t('selectPackageDesc'),
              isComplete: false,
              isActive: false
            },
            {
              id: 3,
              title: t('participants'),
              description: t('participantsDesc'),
              isComplete: false,
              isActive: false
            },
            {
              id: 4,
              title: t('review'),
              description: t('reviewDesc'),
              isComplete: false,
              isActive: false
            }
          ]);
        }
      } catch {
        setError('Tour not found');
      }
    } catch (error) {
      console.error('Error fetching tour:', error);
      setError('Failed to load tour');
    } finally {
      setIsLoading(false);
    }

  }, [slug, t, selectedVariant, selectedSchedule]);

  useEffect(() => {
    if (slug) {
      fetchTour();
    }
  }, [slug]); // eslint-disable-line react-hooks/exhaustive-deps



  // Calculate pricing using new structure
  const calculatePricing = () => {
    if (!tour || !selectedVariant || !selectedSchedule) return null;

    // Check if tour has valid pricing data
    if (!tour.pricing_summary || !tour.pricing_summary[selectedVariant.id]) {
      return {
        total: 0,
        breakdown: { adult: 0, child: 0, infant: 0, options: 0 },
        hasPricingError: true,
        pricingError: t('pricingError')
      };
    }

    const variantPricing = tour.pricing_summary[selectedVariant.id];
    let total = 0;
    const breakdown = {
      adult: 0,
      child: 0,
      infant: 0,
      options: 0
    };

    // Calculate participant costs using new pricing structure
    Object.entries(participants).forEach(([type, count]) => {
      const ageGroupPricing = variantPricing.age_groups[type];
      if (ageGroupPricing) {
        // Ensure infant pricing is always 0
        let price = ageGroupPricing.final_price;
        if (type === 'infant' || ageGroupPricing.is_free) {
          price = 0;
        }
        const cost = price * count;
        breakdown[type as keyof typeof breakdown] = cost;
        total += cost;
      }
    });

    // Calculate options cost
    Object.entries(selectedOptions).forEach(([optionId, quantity]) => {
      const option = tour.options.find(o => o.id === optionId);
      if (option) {
        const cost = option.price * quantity;
        breakdown.options += cost;
        total += cost;
      }
    });

    return { total, breakdown, hasPricingError: false };
  };

  // Check if tour is bookable
  const isTourBookable = () => {
    if (!tour) return false;
    
    // Check if tour is active
    if (!tour.is_active) return false;
    
    // Check if tour is available today
    if (!tour.is_available_today) return false;
    
    // Check if tour has available schedules
    if (!tour.schedules || tour.schedules.length === 0) return false;
    
    // Check if tour has available variants
    if (!tour.variants || tour.variants.length === 0) return false;
    
    return true;
  };





  const pricing = calculatePricing();
  const isBookable = isTourBookable();
  const [backendPricing, setBackendPricing] = useState<{ total: number; unit_price: number; options_total: number; currency: string; age_breakdown?: { adult?: number; child?: number; infant?: number } } | null>(null);

  // Fetch backend pricing with debouncing
  const fetchBackendPricing = useCallback(async () => {
    if (!tourRef.current || !selectedVariant || !selectedSchedule) return;
    
    // Clear existing timeout
    const existingTimeout = window.pricingTimeout;
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }
    
    // Set new timeout for debouncing
    const newTimeout = setTimeout(async () => {
      try {
        const cartData = {
          dry_run: true,
          product_type: 'tour',
          product_id: tourRef.current!.id,
          variant_id: selectedVariant.id,
          quantity: participants.adult + participants.child + participants.infant,
          selected_options: Object.entries(selectedOptions).map(([optionId, quantity]) => {
            const option = tourRef.current?.options.find(o => o.id === optionId);
            return {
              option_id: optionId,
              quantity,
              price: option ? option.price : 0,
              name: option ? option.name : `Option ${optionId.slice(0, 8)}`
            };
          }).filter(option => option.quantity > 0),
          booking_data: {
            schedule_id: selectedSchedule.id,
            participants: {
              adult: participants.adult,
              child: participants.child,
              infant: participants.infant
            },
            special_requests: specialRequests
          }
        };
        const resp = await apiClient.post('/cart/add/', cartData, { params: { dry_run: 1 } });
        if ((resp as { data: unknown })?.data) {
          const { total, unit_price, options_total, currency, age_breakdown } = (resp as { data: { total: number; unit_price: number; options_total: number; currency: string; age_breakdown: { adult?: number; child?: number; infant?: number } } }).data;
          setBackendPricing({ total, unit_price, options_total, currency, age_breakdown });
        }
      } catch (error) {
        console.warn('Backend pricing calculation failed:', error);
        setBackendPricing(null);
      }
    }, 500); // 500ms debounce delay
    
    // Store the timeout reference
    window.pricingTimeout = newTimeout;
  }, [participants.adult, participants.child, participants.infant, selectedOptions, selectedSchedule, selectedVariant, specialRequests]);

  useEffect(() => {
    fetchBackendPricing();
  }, [fetchBackendPricing]);

  // Check purchase history for reviews
  useEffect(() => {
    const checkPurchaseHistory = async () => {
      if (!isAuthenticated || !tourRef.current) return;
      
      setIsCheckingPurchase(true);
      try {
        // Check if user has purchased this tour
        const response = await apiClient.get(`/tours/${slug}/purchase-check/`);
        setHasPurchaseHistory(((response as { data: { has_purchased: boolean } }).data).has_purchased || false);
      } catch (error) {
        console.warn('Could not check purchase history:', error);
        setHasPurchaseHistory(false);
      } finally {
        setIsCheckingPurchase(false);
      }
    };

    checkPurchaseHistory();
  }, [isAuthenticated, slug]);

  // Handle booking
  const handleBooking = async () => {
    console.log('🔍 handleBooking called');
    console.log('selectedVariant:', selectedVariant);
    console.log('selectedVariant.id:', selectedVariant?.id);
    console.log('selectedVariant.name:', selectedVariant?.name);

    if (!tour || !selectedVariant || !selectedSchedule || !isBookable) {
      console.log('❌ Missing required data for booking');
      return;
    }

    // Validate before booking
    const participantError = validateParticipants(participants);
    const optionError = tour.options ? validateOptions(selectedOptions, tour.options) : null;
    const capacityError = await validateCapacity(participants, selectedVariant, selectedSchedule);

    if (participantError || optionError || capacityError) {
      const errorMessage = [participantError, optionError, capacityError].filter(Boolean).join('. ');
      addToast({
        type: 'error',
        title: t('validationError'),
        message: errorMessage,
        duration: 6000
      });
      return;
    }

    // Additional frontend duplicate check for better UX
    if (isAuthenticated) {
      try {
        const pendingOrdersResponse = await apiClient.get(`/tours/${slug}/user-pending-orders/`);
        const pendingOrders = (pendingOrdersResponse as { data: { items: { product_type: string; product_id: string; variant_id: string; booking_date: string; booking_data?: { schedule_id: string } }[] }[] }).data || [];

        const duplicateOrder = pendingOrders.find(order =>
          order.items.some(item =>
            item.product_type === 'tour' &&
            item.product_id === tour.id &&
            item.booking_data?.schedule_id === selectedSchedule.id
          )
        );

        if (duplicateOrder) {
          addToast({
            type: 'error',
            title: t('duplicateBooking'),
            message: t('duplicateBookingDesc'),
            duration: 6000
          });
          return;
        }
      } catch (error) {
        console.warn('Could not check for duplicate bookings:', error);
        // Continue with booking attempt - backend will catch duplicates
      }
    }

    setIsBooking(true);
    setBookingMessage(null);

    try {
      // Calculate pricing
      const pricing = calculatePricing();
      if (!pricing || pricing.hasPricingError) {
        setBookingMessage(pricing?.pricingError || t('pricingCalculationError'));
        addToast({
          type: 'error',
          title: t('pricingError'),
          message: pricing?.pricingError || t('pricingCalculationError'),
          duration: 5000
        });
        return;
      }

      // Prepare data for backend API
      const cartData = {
        product_type: 'tour',
        product_id: tour.id,
        variant_id: selectedVariant.id,
        quantity: participants.adult + participants.child + participants.infant,
        selected_options: Object.entries(selectedOptions).map(([optionId, quantity]) => {
          const option = tour.options.find(o => o.id === optionId);
          return {
            option_id: optionId,
            quantity,
            price: option ? option.price : 0,
            name: option ? option.name : `Option ${optionId.slice(0, 8)}`
          };
        }).filter(option => option.quantity > 0), // Only include options with quantity > 0
        booking_data: {
          schedule_id: selectedSchedule.id,
          participants: {
            adult: participants.adult,
            child: participants.child,
            infant: participants.infant
          },
          special_requests: specialRequests
        }
      };

      // Add to backend cart (guest via session or user via token handled by apiClient)
      console.log('🔄 Calling /cart/add/ API...');
      try {
        const cartResponse = await apiClient.post('/cart/add/', cartData);
        console.log('✅ Cart add response:', cartResponse);
        console.log('✅ Cart add status:', (cartResponse as any).status); // eslint-disable-line @typescript-eslint/no-explicit-any
        console.log('✅ Cart add data:', (cartResponse as any).data); // eslint-disable-line @typescript-eslint/no-explicit-any
      } catch (cartError) {
        console.error('❌ Cart add failed:', cartError);
        console.error('❌ Cart add response:', (cartError as any)?.response?.data); // eslint-disable-line @typescript-eslint/no-explicit-any
        throw cartError;
      }

      await refreshCart();

      // Log cart addition for debugging
      console.log('✅ Tour added to cart:', {
        product_type: 'tour',
        product_id: tour.id,
        variant_id: selectedVariant.id,
        quantity: participants.adult + participants.child + participants.infant,
        isAuthenticated,
        userEmail: user?.email || 'Guest'
      });

      // Refresh tour data to update capacity displays after booking
      await fetchTour();
      
      addToast({
        type: 'success',
        title: t('bookingSuccess'),
        message: t('addedToCartSuccess'),
        duration: 4000
      });
      
      router.push(`/${locale}/cart`);
      
    } catch (error: unknown) {
      console.error('Booking error:', error);
      
      // Handle specific error messages from backend
      let errorMessage = t('addToCartError');
      let errorCode = null;
      
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { error?: string; code?: string; message?: string; redirect_to?: string }; status?: number } };
        if (axiosError.response?.status === 429) {
          errorMessage = t('rateLimitExceeded');
          errorCode = 'RATE_LIMIT_EXCEEDED';
        } else if (axiosError.response?.data?.code === 'OVERBOOKING_LIMIT_EXCEEDED') {
          errorMessage = axiosError.response.data.error || 'Overbooking limit exceeded';
          errorCode = 'OVERBOOKING_LIMIT_EXCEEDED';
          
          // Show overbooking error with redirect option
          addToast({
            type: 'error',
            title: t('overbookingError'),
            message: errorMessage,
            duration: 6000,
            action: axiosError.response?.data?.redirect_to ? {
              label: axiosError.response.data.redirect_to === 'cart' ? t('viewCart') : t('proceedToCheckout'),
              onClick: () => {
                const redirectTo = axiosError.response?.data?.redirect_to;
                if (redirectTo) {
                  router.push(`/${locale}/${redirectTo}`);
                }
              }
            } : undefined
          });
          return;
        } else if (axiosError.response?.data?.error) {
          errorMessage = axiosError.response.data.error;
          errorCode = axiosError.response.data.code || 'UNKNOWN_ERROR';
        } else if (axiosError.response?.data?.message) {
          errorMessage = axiosError.response.data.message;
        }
      } else if (error && typeof error === 'object' && 'message' in error) {
        errorMessage = (error as { message: string }).message;
      }
      
              // Handle specific error codes
        if (errorCode === 'DUPLICATE_BOOKING') {
          errorMessage = t('duplicateBooking');
        } else if (errorCode === 'DUPLICATE_CART_ITEM') {
          errorMessage = t('duplicateCartItem');
        } else if (errorCode === 'GUEST_LIMIT_EXCEEDED') {
          errorMessage = t('guestLimitExceeded');
        } else if (errorCode === 'GUEST_CART_TOTAL_LIMIT') {
          errorMessage = t('guestCartTotalLimit');
        } else if (errorCode === 'GUEST_CART_LIMIT_EXCEEDED') {
          errorMessage = t('guestCartItemsLimitExceeded');
        } else if (errorCode === 'GUEST_CART_TOTAL_EXCEEDED') {
          errorMessage = t('guestCartTotalLimit');
        } else if (errorCode === 'CART_ITEMS_LIMIT_EXCEEDED') {
          errorMessage = t('userCartItemsLimitExceeded');
        } else if (errorCode === 'CART_TOTAL_LIMIT_EXCEEDED') {
          errorMessage = t('userCartTotalLimit');
        } else if (errorCode === 'MERGE_LIMIT_EXCEEDED') {
          errorMessage = t('mergeItemsLimitExceeded');
        } else if (errorCode === 'MERGE_TOTAL_EXCEEDED') {
          errorMessage = t('mergeTotalLimitExceeded');
        } else if (errorCode === 'GUEST_TOO_MANY_CARTS') {
          errorMessage = t('guestTooManyCarts');
        } else if (errorCode === 'GUEST_RATE_LIMIT_EXCEEDED') {
          errorMessage = t('guestRateLimitExceeded');
        } else if (errorCode === 'RATE_LIMIT_EXCEEDED') {
          errorMessage = t('rateLimitExceeded');
        } else if (errorCode === 'INSUFFICIENT_CAPACITY') {
          // Extract requested and available from error message
          if (error && typeof error === 'object' && 'response' in error) {
            const axiosError = error as { response?: { data?: { error?: string; code?: string; message?: string }; status?: number } };
            const errorText = axiosError.response?.data?.error || '';
            const requestedMatch = errorText.match(/Requested: (\d+)/);
            const availableMatch = errorText.match(/Available: (\d+)/);
            
            if (requestedMatch && availableMatch) {
              const requested = requestedMatch[1];
              const available = availableMatch[1];
              errorMessage = t('insufficientCapacity', { requested, available });
            } else {
              errorMessage = t('insufficientCapacity');
            }
          } else {
            errorMessage = t('insufficientCapacity');
          }
        }
      
      addToast({
        type: 'error',
        title: t('bookingError'),
        message: errorMessage,
        duration: 6000
      });
      
      setBookingMessage(errorMessage);
    } finally {
      setIsBooking(false);
    }
  };



  // Format functions
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">{t('loading')}</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !tour) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">{t('notFound')}</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">{error || t('notFoundDesc')}</p>
          <div className="space-x-4">
            <button
              onClick={() => router.push(`/${locale}/tours`)}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700"
            >
              {t('backToTours')}
            </button>
            <button
              onClick={() => router.push(`/${locale}`)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              {t('backToHome')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >


      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tour Header */}
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 mb-8 overflow-hidden"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="relative">
            <OptimizedImage
              src={getImageUrl(tour.image)}
              alt={tour.title}
              fill
              className="w-full h-64 sm:h-80 md:h-96 lg:h-[28rem] xl:h-[32rem] object-cover rounded-t-2xl"
              priority
              fallbackSrc="/images/tour-image.jpg"
              sizes="(max-width: 640px) 100vw, (max-width: 768px) 100vw, (max-width: 1024px) 100vw, 100vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-t-2xl" />
            <motion.div 
              className="absolute top-4 left-4"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg backdrop-blur-sm border border-white/20">
                <Sparkles className="w-4 h-4 mr-2" />
                {tour.category.name}
              </span>
            </motion.div>
          </div>
          
          <motion.div 
            className="p-8"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <motion.h1 
              className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent mb-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              {tour.title}
            </motion.h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {[
                { icon: Calendar, text: tour.tour_type === 'day' ? t('dailyTour') : t('nightTour'), delay: 0.7 },
                { icon: Clock, text: `${tour.duration_hours} ${t('hours')}`, delay: 0.8 },
                { icon: Bus, text: tour.transport_type === 'boat' ? t('boat') : tour.transport_type === 'air' ? t('air') : t('ground'), delay: 0.9 },
                { icon: Users, text: `${tour.max_participants} ${t('people')} ${t('capacity')}`, delay: 1.0 }
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
            
            <div className="flex flex-wrap items-center gap-4 mb-6">
              <motion.div 
                className="flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border border-yellow-200/50 dark:border-yellow-700/50"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, delay: 1.1 }}
                whileHover={{ scale: 1.05 }}
              >
                <Star className="h-5 w-5 text-yellow-500 fill-current mr-2" />
                <span className="text-sm font-semibold text-yellow-700 dark:text-yellow-300">
                  {tour.average_rating?.toFixed(1) || 'N/A'} ({tour.review_count || 0} {t('reviews')})
                </span>
              </motion.div>
              
              <motion.div 
                className="px-4 py-2 rounded-full bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border border-primary-200/50 dark:border-primary-700/50"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, delay: 1.2 }}
                whileHover={{ scale: 1.05 }}
              >
                <span className="text-sm font-semibold text-primary-700 dark:text-primary-300">
                  {tour.tour_type === 'day' ? t('dailyTour') : t('nightTour')}
                </span>
              </motion.div>
            </div>
            
            <motion.p 
              className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.3 }}
            >
              {tour.description}
            </motion.p>
          </motion.div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <motion.div 
            className="lg:col-span-2 space-y-6"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {/* Booking Steps */}
            <motion.div 
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
                <h3 className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
                  {t('bookingSteps')}
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {bookingSteps.map((step) => (
                    <div key={step.id} className="flex items-center space-x-4">
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                        step.isComplete 
                          ? 'bg-green-500 text-white' 
                          : step.isActive 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                      }`}>
                        {step.isComplete ? '✓' : step.id}
                      </div>
                      <div className="flex-1">
                        <h4 className={`font-medium ${
                          step.isActive 
                            ? 'text-blue-600 dark:text-blue-400' 
                            : 'text-gray-600 dark:text-gray-400'
                        }`}>
                          {step.title}
                        </h4>
                        <p className="text-sm text-gray-500 dark:text-gray-500">
                          {step.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
            {/* Schedule Selection */}
            <motion.div 
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20">
                <motion.h3 
                  className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                  initial={{ y: 10, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                >
                  {t('selectDate')}
                </motion.h3>
              </div>
              <div className="p-6">
                {tour.schedules && tour.schedules.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {tour.schedules.map((schedule, index) => (
                      <motion.div
                        key={schedule.id}
                        onClick={() => setSelectedSchedule(schedule)}
                        className={`p-6 border-2 rounded-xl cursor-pointer transition-all duration-300 ${
                          selectedSchedule?.id === schedule.id
                            ? 'border-primary-500 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 shadow-lg'
                            : 'border-gray-200/50 dark:border-gray-700/50 hover:border-primary-300 dark:hover:border-primary-600 hover:shadow-md bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-600/50'
                        }`}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.6 + (index * 0.1) }}
                        whileHover={{ scale: 1.02, y: -2 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <span className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
                            {formatDate(schedule.start_date)}
                          </span>
                          <motion.span 
                            className={`text-xs px-3 py-1.5 rounded-full font-semibold border ${
                              schedule.is_available && !schedule.is_full
                                ? 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 text-green-700 dark:text-green-300 border-green-200/50 dark:border-green-700/50'
                                : 'bg-gradient-to-r from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 text-red-700 dark:text-red-300 border-red-200/50 dark:border-red-700/50'
                            }`}
                            whileHover={{ scale: 1.05 }}
                          >
                            {schedule.is_full ? t('full') : schedule.is_available ? t('available') : t('inactive')}
                          </motion.span>
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                          <div className="flex items-center p-2 rounded-lg bg-white/50 dark:bg-gray-800/50">
                            <Clock className="h-4 w-4 mr-3 text-primary-500" />
                            <span className="font-medium">{t('startTime')}: {formatTime(schedule.start_time)} - {t('endTime')}: {formatTime(schedule.end_time)}</span>
                          </div>
                          {tour.pickup_time && (
                            <div className="flex items-center p-2 rounded-lg bg-white/50 dark:bg-gray-800/50">
                              <Clock className="h-4 w-4 mr-3 text-primary-500" />
                              <span className="font-medium">{t('pickupTime')}: {formatTime(tour.pickup_time)}</span>
                            </div>
                          )}
                          <div className="flex items-center p-2 rounded-lg bg-white/50 dark:bg-gray-800/50">
                            <Users className="h-4 w-4 mr-3 text-primary-500" />
                            <span className="font-medium">{schedule.available_capacity} {t('of')} {schedule.max_capacity} {t('availableCapacity')}</span>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <motion.div 
                    className="text-center py-8"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.6 }}
                  >
                    <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400">{t('noScheduleAvailable')}</p>
                  </motion.div>
                )}
              </div>
            </motion.div>

            {/* Variant Selection */}
            {selectedSchedule && tour.variants && tour.variants.length > 0 && (
              <motion.div 
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 }}
              >
                <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
                  <motion.h3 
                    className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                    initial={{ y: 10, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.6 }}
                  >
                    {t('selectPackage')}
                  </motion.h3>
                </div>
                <div className="p-6">
                  {/* Show message if no variants are available for selected date */}
                  {selectedSchedule && tour.variants.every(variant => {
                    const variantCapacity = selectedSchedule.variant_capacities[variant.id];
                    return !(variantCapacity && variantCapacity.available > 0);
                  }) && (
                    <div className="mb-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg">
                      <div className="flex items-center">
                        <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mr-2" />
                        <p className="text-yellow-800 dark:text-yellow-200 text-sm">
                          {t('noVariantsAvailableForDate')}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {tour.variants
                      .filter((variant) => {
                        // Only show variants that have capacity for the selected schedule
                        const variantCapacity = selectedSchedule.variant_capacities[variant.id];
                        return variantCapacity && variantCapacity.total > 0;
                      })
                      .map((variant) => {
                        const variantCapacity = selectedSchedule.variant_capacities[variant.id];
                        const isVariantAvailable = variantCapacity && variantCapacity.available > 0;
                        
                        return (
                          <div
                            key={variant.id}
                            onClick={() => {
                              if (isVariantAvailable) {
                                console.log('🎯 Selecting variant:', variant);
                                console.log('Variant ID:', variant.id);
                                console.log('Variant name:', variant.name);
                                setSelectedVariant(variant);
                              }
                            }}
                            className={`p-4 border-2 rounded-lg transition-all duration-300 ${
                              !isVariantAvailable
                                ? 'border-gray-200 dark:border-gray-700 opacity-50 cursor-not-allowed'
                                : selectedVariant?.id === variant.id
                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 cursor-pointer shadow-md'
                                : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 cursor-pointer hover:shadow-sm'
                            }`}
                          >
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-gray-900 dark:text-gray-100">{variant.name}</h4>
                            <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                              ${variant.base_price}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{variant.description}</p>
                          
                          {/* Variant Features */}
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            {variant.includes_transfer && (
                              <div className="flex items-center text-green-600 dark:text-green-400">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                <span>{t('transfer')}</span>
                              </div>
                            )}
                            {variant.includes_guide && (
                              <div className="flex items-center text-green-600 dark:text-green-400">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                <span>{t('guide')}</span>
                              </div>
                            )}
                            {variant.includes_meal && (
                              <div className="flex items-center text-green-600 dark:text-green-400">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                <span>{t('meal')}</span>
                              </div>
                            )}
                            {variant.includes_photographer && (
                              <div className="flex items-center text-green-600 dark:text-green-400">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                <span>{t('photographer')}</span>
                              </div>
                            )}
                          </div>
                          
                          {/* Capacity Info */}
                          {variantCapacity && (
                            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-500 dark:text-gray-400">{t('capacity')}:</span>
                                <span className={`font-medium ${
                                  isVariantAvailable 
                                    ? 'text-green-600 dark:text-green-400' 
                                    : 'text-red-600 dark:text-red-400'
                                }`}>
                                  {variantCapacity.available} {t('of')} {variantCapacity.total}
                                </span>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Participant Selection */}
            {selectedSchedule && selectedVariant && (
              <motion.div 
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20">
                  <motion.h3 
                    className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                    initial={{ y: 10, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                  >
                    {t('participants')}
                  </motion.h3>
                </div>
                <div className="p-6">
                  <TourParticipantSelector
                    participants={participants}
                    setParticipants={setParticipants}
                    tour={tour}
                    selectedVariant={selectedVariant}
                    selectedSchedule={selectedSchedule}
                    validationErrors={validationErrors}
                    addToast={addToast}
                  />
                </div>
              </motion.div>
            )}

            {/* Options Selection */}
            {tour.options && tour.options.length > 0 && selectedSchedule && selectedVariant && (participants.adult + participants.child + participants.infant) > 0 && (
              <motion.div 
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
                  <motion.h3 
                    className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                    initial={{ y: 10, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                  >
                    {t('additionalOptions')}
                  </motion.h3>
                </div>
                <div className="p-6">
                  
                  {/* Warning when variant has no capacity */}
                  {selectedSchedule && selectedVariant && (() => {
                    const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
                    const isVariantAvailable = variantCapacity && variantCapacity.available > 0;
                    
                    if (!isVariantAvailable) {
                      return (
                        <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                          <div className="flex items-center">
                            <AlertCircle className="h-4 w-4 text-yellow-500 mr-2" />
                            <span className="text-sm text-yellow-700 dark:text-yellow-300">
                              {t('variantNoCapacity')} - {t('optionsDisabled')}
                            </span>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })()}
                  
                  <div className="space-y-4">
                    {tour.options.map((option) => {
                      // Check if variant has capacity
                      const variantCapacity = selectedSchedule?.variant_capacities[selectedVariant.id];
                      const isVariantAvailable = variantCapacity && variantCapacity.available > 0;
                      
                      return (
                        <div key={option.id} className={`flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg ${
                          !isVariantAvailable ? 'opacity-50' : ''
                        }`}>
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-medium text-gray-900 dark:text-gray-100">{option.name}</h4>
                              <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                                ${option.price}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{option.description}</p>
                          </div>
                          <div className="flex items-center space-x-3 ml-4">
                            <button
                              onClick={() => setSelectedOptions(prev => ({
                                ...prev,
                                [option.id]: Math.max(0, (prev[option.id] || 0) - 1)
                              }))}
                              disabled={!selectedOptions[option.id] || selectedOptions[option.id] === 0 || !isVariantAvailable}
                              className="p-1 rounded-full border border-gray-300 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
                            >
                              <Minus className="h-4 w-4" />
                            </button>
                            <span className="w-8 text-center font-medium">
                              {selectedOptions[option.id] || 0}
                            </span>
                            <button
                              onClick={() => {
                                const currentQuantity = selectedOptions[option.id] || 0;
                                const newQuantity = currentQuantity + 1;
                                
                                if (option.max_quantity && newQuantity > option.max_quantity) {
                                  addToast({
                                    type: 'error',
                                    title: t('limitExceeded'),
                                    message: t('optionQuantityExceeded', { 
                                      option: option.name, 
                                      max: option.max_quantity 
                                    }),
                                    duration: 4000
                                  });
                                  return;
                                }
                                
                                setSelectedOptions(prev => ({
                                  ...prev,
                                  [option.id]: newQuantity
                                }));
                              }}
                              disabled={
                                !isVariantAvailable ||
                                (!!option.max_quantity && 
                                (selectedOptions[option.id] || 0) >= option.max_quantity)
                              }
                              className="p-1 rounded-full border border-gray-300 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
                            >
                              <Plus className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  
                  {/* Options Validation Errors Display */}
                  {validationErrors.options && (
                    <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                      <div className="flex items-center">
                        <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                        <span className="text-sm text-red-700 dark:text-red-300">
                          {validationErrors.options}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {/* Special Requests */}
            {selectedSchedule && selectedVariant && (participants.adult + participants.child + participants.infant) > 0 && (
              <motion.div 
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20">
                  <motion.h3 
                    className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                    initial={{ y: 10, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                  >
                    {t('specialRequests')}
                  </motion.h3>
                </div>
                <div className="p-6">
                  <textarea
                    value={specialRequests}
                    onChange={(e) => setSpecialRequests(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    rows={4}
                    placeholder={t('specialRequests')}
                  />
                </div>
              </motion.div>
            )}
          </motion.div>

          {/* Sidebar */}
          <motion.div 
            className="space-y-6"
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            {/* Sticky Pricing Container */}
            <div className="sticky top-24 space-y-6">
            {/* Booking Summary */}
            {selectedSchedule && selectedVariant && (
              <motion.div 
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
                  <motion.h3 
                    className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                    initial={{ y: 10, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                  >
                    {t('bookingSummary')}
                  </motion.h3>
                </div>
                <div className="p-6 space-y-3">
                  {/* Tour Info */}
                  <div>
                    <div className="font-medium text-gray-900 dark:text-gray-100">{tour.title}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{selectedVariant.name}</div>
                  </div>

                  {/* Date & Time */}
                  <div className="flex items-center text-sm">
                    <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                    <span className="text-gray-600 dark:text-gray-400">
                      {formatDate(selectedSchedule.start_date)}
                    </span>
                  </div>
                  <div className="flex items-center text-sm">
                    <Clock className="h-4 w-4 mr-2 text-gray-400" />
                    <span className="text-gray-600 dark:text-gray-400">
                      {formatTime(selectedSchedule.start_time)} - {formatTime(selectedSchedule.end_time)}
                    </span>
                  </div>

                  {/* Participants */}
                  <div className="flex items-center text-sm">
                    <Users className="h-4 w-4 mr-2 text-gray-400" />
                    <span className="text-gray-600 dark:text-gray-400">
                      {participants.adult + participants.child + participants.infant} {t('people')}
                    </span>
                  </div>

                  {/* Pricing */}
                  {pricing && !pricing.hasPricingError && (
                    <div className="border-t border-gray-200 dark:border-gray-700 pt-3 mt-3">
                      <div className="space-y-2 text-sm">
                        {participants.adult > 0 && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">{t('adultCount', { count: participants.adult })}</span>
                            <span className="text-gray-900 dark:text-gray-100">${pricing.breakdown.adult.toFixed(2)}</span>
                          </div>
                        )}
                        {participants.child > 0 && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">{t('childCount', { count: participants.child })}</span>
                            <span className="text-gray-900 dark:text-gray-100">${pricing.breakdown.child.toFixed(2)}</span>
                          </div>
                        )}
                        {participants.infant > 0 && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">{t('infantCount', { count: participants.infant })}</span>
                            <span className="text-gray-900 dark:text-gray-100">{t('free')}</span>
                          </div>
                        )}
                        {pricing.breakdown.options > 0 && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">{t('additionalOptions')}</span>
                            <span className="text-gray-900 dark:text-gray-100">${pricing.breakdown.options.toFixed(2)}</span>
                          </div>
                        )}
                        <div className="border-t border-gray-200 dark:border-gray-700 pt-2 mt-2">
                          <div className="flex justify-between font-bold">
                            <span className="text-gray-900 dark:text-gray-100">{t('total')}</span>
                            <span className="text-blue-600 dark:text-blue-400">${pricing.total.toFixed(2)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Backend Pricing Comparison */}
                  {backendPricing && (
                    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-3 mt-3">
                      <div className="text-sm">
                        <div className="font-medium text-green-800 dark:text-green-200 mb-1">{t('finalServerPrice')}</div>
                        <div className="flex justify-between">
                          <span className="text-green-700 dark:text-green-300">{t('total')}</span>
                          <span className="font-bold text-green-800 dark:text-green-200">
                            ${backendPricing.total.toFixed(2)} {backendPricing.currency}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Options Details */}
                  {Object.entries(selectedOptions).some(([, quantity]) => quantity > 0) && (
                    <div className="border-t border-gray-200 dark:border-gray-700 pt-3 mt-3">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">{t('selectedOptions')}</div>
                      <ul className="text-sm space-y-1">
                        {Object.entries(selectedOptions).map(([optionId, quantity]) => {
                          if (quantity === 0) return null;
                          const option = tour.options.find(o => o.id === optionId);
                          return option ? (
                            <li key={optionId} className="flex justify-between text-sm">
                              <span>{option.name} ({quantity}x)</span>
                              <span>${(option.price * quantity).toFixed(2)}</span>
                            </li>
                          ) : null;
                        })}
                      </ul>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {/* Error Summary and Booking Guidance */}
            <TourErrorSummary
              validationErrors={validationErrors}
              selectedSchedule={selectedSchedule}
              selectedVariant={selectedVariant}
              participants={participants}
              tour={tour}
            />

            {/* Booking Button */}
            <button
              onClick={handleBooking}
              disabled={
                !isBookable || 
                !selectedSchedule || 
                !selectedVariant || 
                isBooking || 
                (participants.adult + participants.child + participants.infant) === 0 ||
                Object.keys(validationErrors).length > 0
              }
              className="w-full bg-blue-600 text-white py-4 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isBooking ? (
                <span className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {t('bookingInProgress')}
                </span>
              ) : !isBookable ? (
                t('notAvailable')
              ) : (
                t('addToCart')
              )}
            </button>

            {/* Pending Orders Display */}
            {isAuthenticated && (
              <div className="mt-4">
                <PendingOrdersDisplay 
                  tourId={tour?.id} 
                  scheduleId={selectedSchedule?.id}
                  variantId={selectedVariant?.id}
                  onOrderUpdate={refreshCart}
                />
              </div>
            )}

            {/* Booking Message */}
            {bookingMessage && (
              <div className={`p-3 rounded-lg text-sm ${
                bookingMessage.includes('successfully') || bookingMessage.includes(t('addedToCartSuccess'))
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {bookingMessage}
              </div>
            )}

            {/* Cancellation Policy */}
            <ProductCancellationPolicy
              policies={(() => {
                // Use new backend cancellation policies if available
                if (tour.cancellation_policies && tour.cancellation_policies.length > 0) {
                  return tour.cancellation_policies.filter(policy => policy.is_active);
                }
                
                // Fallback to legacy cancellation policy if available
                if (tour.cancellation_hours && tour.refund_percentage !== undefined) {
                  return [{
                    hours_before: tour.cancellation_hours,
                    refund_percentage: tour.refund_percentage,
                    description: `${tour.refund_percentage}% ${t('cancellationPolicy.refundUpTo')} ${tour.cancellation_hours} ${t('cancellationPolicy.hoursBeforeService')}`
                  }];
                }
                
                // Fallback to default policies if no backend data is available
                return [
                  {
                    hours_before: 24,
                    refund_percentage: 100,
                    description: t('cancellationPolicy.freeCancel24h')
                  },
                  {
                    hours_before: 12,
                    refund_percentage: 50,
                    description: t('cancellationPolicy.refund75Percent12h')
                  },
                  {
                    hours_before: 6,
                    refund_percentage: 0,
                    description: t('cancellationPolicy.noRefund2h')
                  }
                ];
              })()}
              productType="tour"
              productData={{
                date: selectedSchedule?.start_date,
                location: tour.category?.name,
                duration: `${tour.duration_hours} ${t('hours')}`
              }}
              className="mb-4"
            />



            {/* Guest Info */}
            {!isAuthenticated && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  <strong>{t('guestUser')}:</strong> {t('guestUserDescription')}
                  <Link href={`/${locale}/login`} className="text-blue-600 dark:text-blue-400 hover:underline">
                    {t('loginToSync')}
                  </Link>
                </p>
              </div>
            )}
            </div>
          </motion.div>
        </div>

        {/* Tour Itinerary Section */}
        <div className="mb-8 mt-6">
          <TourItinerary 
            itinerary={tour.itinerary || []} 
            rules={tour.rules}
            required_items={tour.required_items}
            highlights={tour.highlights}
            booking_cutoff_hours={tour.booking_cutoff_hours}
            min_participants={tour.min_participants}
            max_participants={tour.max_participants}
            tour_type={tour.tour_type}
            transport_type={tour.transport_type}
          />
        </div>

        {/* Reviews Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-8">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">{t('reviewsAndRatings')}</h2>
            <div className="space-y-6">
              {/* Rating Summary */}
              <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-4xl font-bold text-yellow-500">
                      {tour.average_rating?.toFixed(1) || '0.0'}
                    </div>
                    <div>
                      <div className="flex items-center space-x-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`h-5 w-5 ${
                              star <= (tour.average_rating || 0)
                                ? 'text-yellow-400 fill-current'
                                : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {tour.review_count || 0} {t('reviews')}
                      </p>
                    </div>
                  </div>
                  {isAuthenticated ? (
                    <button
                      onClick={() => setShowReviewForm(!showReviewForm)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      {showReviewForm ? t('cancel') : t('submitReview')}
                    </button>
                  ) : (
                    <div className="text-center">
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {t('loginToReview')}
                      </p>
                      <Link
                        href={`/${locale}/login?redirect=${encodeURIComponent(`/${locale}/tours/${slug}`)}`}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      >
                        {t('loginSignup')}
                      </Link>
                    </div>
                  )}
                </div>
              </div>

              {/* Review Form */}
              {showReviewForm && (
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 bg-gray-50 dark:bg-gray-800">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">{t('submitNewReview')}</h3>
                  
                  {/* Purchase History Check */}
                  {isCheckingPurchase ? (
                    <div className="text-center py-4">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{t('checkingPurchaseHistory')}</p>
                    </div>
                  ) : !hasPurchaseHistory ? (
                    <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4 mb-4">
                      <div className="flex items-start">
                        <Info className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                        <div className="text-sm">
                          <p className="font-medium text-yellow-800 dark:text-yellow-200 mb-1">
                            {t('reviewRestriction')}
                          </p>
                          <p className="text-yellow-700 dark:text-yellow-300">
                            {t('reviewRestrictionDesc')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* Rating Selection */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('yourRating')}
                        </label>
                        <div className="flex items-center space-x-2">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <button
                              key={star}
                              onClick={() => setNewReview(prev => ({ ...prev, rating: star }))}
                              className={`p-1 ${
                                star <= newReview.rating
                                  ? 'text-yellow-400'
                                  : 'text-gray-300'
                              }`}
                            >
                              <Star
                                className={`h-6 w-6 ${
                                  star <= newReview.rating
                                    ? 'fill-current'
                                    : ''
                                }`}
                              />
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Title */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('reviewTitle')}
                        </label>
                        <input
                          type="text"
                          value={newReview.title}
                          onChange={(e) => setNewReview(prev => ({ ...prev, title: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          placeholder={t('reviewTitlePlaceholder')}
                        />
                      </div>

                      {/* Comment */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('yourReview')}
                        </label>
                        <textarea
                          value={newReview.comment}
                          onChange={(e) => setNewReview(prev => ({ ...prev, comment: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          rows={4}
                          placeholder={t('yourReviewPlaceholder')}
                          required
                        />
                      </div>

                      {/* Category */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('category')}
                        </label>
                        <select
                          value={newReview.category}
                          onChange={(e) => setNewReview(prev => ({ ...prev, category: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="general">{t('categoryGeneral')}</option>
                          <option value="service">{t('categoryService')}</option>
                          <option value="quality">{t('categoryQuality')}</option>
                          <option value="value">{t('categoryValue')}</option>
                        </select>
                      </div>

                      {/* Submit Button */}
                      <div className="flex justify-end space-x-3">
                        <button
                          onClick={() => setShowReviewForm(false)}
                          className="px-4 py-2 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                        >
                          {t('cancel')}
                        </button>
                        <button
                          onClick={async () => {
                            try {
                              await apiClient.post(`/tours/${slug}/reviews/create/`, newReview);
                              alert(t('reviewSubmitted'));
                              setShowReviewForm(false);
                              setNewReview({ rating: 5, title: '', comment: '', category: 'general' });
                              // Refresh tour data to show new review
                              window.location.reload();
                            } catch (error: unknown) {
                              console.error('Error submitting review:', error);
                              if (error instanceof Error && 'response' in error && error.response && typeof error.response === 'object' && 'status' in error.response && typeof error.response.status === 'number') {
                                if (error.response.status === 401) {
                                  alert(t('loginRequired'));
                                } else if (error.response.status === 403) {
                                  alert(t('notAuthorized'));
                                } else {
                                  alert(t('reviewError'));
                                }
                              } else {
                                alert(t('reviewError'));
                              }
                            }
                          }}
                          disabled={!newReview.comment.trim()}
                          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {t('submitReview')}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Reviews List */}
              <div>
                {tour.reviews && tour.reviews.length > 0 ? (
                  <div className="space-y-4">
                    {tour.reviews.map((review: { id: string; rating: number; user_name: string; created_at: string; title?: string; comment: string }) => (
                      <div key={review.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <div className="flex items-center space-x-1">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                  key={star}
                                  className={`h-4 w-4 ${
                                    star <= review.rating
                                      ? 'text-yellow-400 fill-current'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                              {review.user_name}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(review.created_at).toLocaleDateString('fa-IR')}
                          </span>
                        </div>
                        {review.title && (
                          <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                            {review.title}
                          </h4>
                        )}
                        <p className="text-gray-600 dark:text-gray-300 text-sm">
                          {review.comment}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Star className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400 mb-2">{t('noReviewsYet')}</p>
                    <p className="text-sm text-gray-400 dark:text-gray-500 mb-4">
                      {t('beFirstReviewer')}
                    </p>
                    {!isAuthenticated && (
                      <Link
                        href={`/${locale}/login?redirect=${encodeURIComponent(`/${locale}/tours/${slug}`)}`}
                        className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                      >
                        {t('loginToReviewButton')}
                      </Link>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
