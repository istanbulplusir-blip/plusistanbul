import React from 'react';
import { User, Smile, Baby, Plus, Minus, AlertCircle, Info, Users } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { ToastType } from '@/components/Toast';

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
  min_participants: number;
  booking_cutoff_hours: number;
  cancellation_hours: number;
  refund_percentage: number;
  includes_transfer: boolean;
  includes_guide: boolean;
  includes_meal: boolean;
  includes_photographer: boolean;
  tour_type: 'day' | 'night';
  transport_type: 'boat' | 'land' | 'air';
  pickup_time: string;
  start_time: string;
  end_time: string;
  category: {
    id: string;
    name: string;
    description: string;
  };
  variants: Array<{
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
  }>;
  schedules: Array<{
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
  }>;
  is_available_today: boolean;
  is_active: boolean;
}

interface ParticipantSelectorProps {
  participants: { adult: number; child: number; infant: number };
  setParticipants: (participants: { adult: number; child: number; infant: number }) => void;
  tour: Tour | null;
  selectedVariant: Tour['variants'][0] | null;
  selectedSchedule: Tour['schedules'][0] | null;
  validationErrors: { participants?: string };
  addToast: (toast: { type: ToastType; title: string; message?: string; duration?: number }) => void;
}

export default function TourParticipantSelector({
  participants,
  setParticipants,
  tour,
  selectedVariant,
  selectedSchedule,
  validationErrors,
  addToast
}: ParticipantSelectorProps) {
  const t = useTranslations('tours');

  const getButtonDisabledState = (participantType: 'adult' | 'child' | 'infant') => {
    const currentValue = participants[participantType];
    
    // Check if variant has capacity
    if (selectedVariant && selectedSchedule) {
      const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
      const isVariantAvailable = variantCapacity && variantCapacity.available > 0;
      
      if (!isVariantAvailable) {
        return true; // Disable all buttons if variant has no capacity
      }
    }
    
    switch (participantType) {
      case 'infant':
        return currentValue >= 2; // Maximum 2 infants
      
      case 'adult':
      case 'child':
        // Check adult + child combination limit using variant capacity
        if (selectedVariant && selectedSchedule) {
          const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
          const availableCapacity = variantCapacity?.available || 0;
          const adultChildTotal = participants.adult + participants.child;
          return adultChildTotal >= availableCapacity;
        }
        // Fallback to tour max if variant data not available
        const adultChildTotal = participants.adult + participants.child;
        const maxAdultChild = tour ? tour.max_participants - participants.infant : 0;
        return adultChildTotal >= maxAdultChild;
      
      default:
        return false;
    }
  };

  const getValidationMessage = (participantType: 'adult' | 'child' | 'infant') => {
    const currentValue = participants[participantType];
    
    switch (participantType) {
      case 'infant':
        if (currentValue >= 2) {
          return t('maxInfantsReached', { max: 2 });
        }
        break;
      
      case 'adult':
      case 'child':
        if (selectedVariant && selectedSchedule) {
          const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
          const availableCapacity = variantCapacity?.available || 0;
          const adultChildTotal = participants.adult + participants.child;
          if (adultChildTotal >= availableCapacity) {
            return t('maxAdultChildReached', {
              max: availableCapacity,
              remaining: participants.infant
            });
          }
        } else {
          // Fallback to tour max if variant data not available
          const adultChildTotal = participants.adult + participants.child;
          const maxAdultChild = tour ? tour.max_participants - participants.infant : 0;
          if (adultChildTotal >= maxAdultChild) {
            return t('maxAdultChildReached', {
              max: maxAdultChild,
              remaining: participants.infant
            });
          }
        }
        break;
    }
    
    return null;
  };

  const getCapacityDisplay = () => {
    if (!tour || !selectedVariant || !selectedSchedule) return null;

    const totalSelected = participants.adult + participants.child + participants.infant;

    // Use real-time variant capacity instead of static tour max capacity
    const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
    const availableCapacity = variantCapacity?.available || 0;
    const remaining = availableCapacity - (participants.adult + participants.child);

    return {
      total: availableCapacity,
      selected: totalSelected,
      remaining: remaining,
      isFull: remaining <= 0,
      adultChildTotal: participants.adult + participants.child,
      maxAdultChild: availableCapacity
    };
  };

  const handleParticipantChange = (type: 'adult' | 'child' | 'infant', increment: boolean) => {
    const currentValue = participants[type];
    const newValue = increment ? currentValue + 1 : Math.max(0, currentValue - 1);
    
    if (increment) {
      // Apply limits for increment
      let shouldUpdate = true;
      let errorMessage = '';
      
      // Check variant capacity first
      if (selectedVariant && selectedSchedule) {
        const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
        const isVariantAvailable = variantCapacity && variantCapacity.available > 0;
        
        if (!isVariantAvailable) {
          errorMessage = t('tourDetail.variantNoCapacity');
          shouldUpdate = false;
        } else {
          // Check if adding this participant would exceed variant capacity
          let newAdultChildTotal = participants.adult + participants.child;
          if (type === 'adult') {
            newAdultChildTotal = newValue + participants.child;
          } else if (type === 'child') {
            newAdultChildTotal = participants.adult + newValue;
          }
          
          if (newAdultChildTotal > variantCapacity.available) {
            errorMessage = t('tourDetail.variantCapacityExceeded', { 
              requested: newAdultChildTotal, 
              available: variantCapacity.available 
            });
            shouldUpdate = false;
          }
        }
      }
      
      if (type === 'infant' && newValue > 2) {
        errorMessage = t('maxInfantsExceeded', { max: 2 });
        shouldUpdate = false;
      } else if (type === 'adult' || type === 'child') {
        if (selectedVariant && selectedSchedule) {
          const variantCapacity = selectedSchedule.variant_capacities[selectedVariant.id];
          const availableCapacity = variantCapacity?.available || 0;
          let newAdultChildTotal = participants.adult + participants.child;
          if (type === 'adult') {
            newAdultChildTotal = newValue + participants.child;
          } else if (type === 'child') {
            newAdultChildTotal = participants.adult + newValue;
          }

          if (newAdultChildTotal > availableCapacity) {
            errorMessage = t('maxAdultChildExceeded', {
              max: availableCapacity,
              infant: participants.infant
            });
            shouldUpdate = false;
          }
        } else {
          // Fallback to tour max if variant data not available
          let newAdultChildTotal = participants.adult + participants.child;
          if (type === 'adult') {
            newAdultChildTotal = newValue + participants.child;
          } else if (type === 'child') {
            newAdultChildTotal = participants.adult + newValue;
          }
          
          const maxAdultChild = tour ? tour.max_participants - participants.infant : 0;

          if (newAdultChildTotal > maxAdultChild) {
            errorMessage = t('maxAdultChildExceeded', {
              max: maxAdultChild,
              infant: participants.infant
            });
            shouldUpdate = false;
          }
        }
      } else if (tour) {
        // This branch is for infant type, so we don't need to check adult/child capacity
        // Fallback validation
        const totalParticipants = participants.adult + participants.child + participants.infant + (type === 'infant' ? 1 : 0);
        if (totalParticipants > tour.max_participants) {
          errorMessage = t('exceedsMaxParticipants', { max: tour.max_participants });
          shouldUpdate = false;
        }
      }
      
      if (!shouldUpdate && errorMessage) {
        addToast({
          type: 'error',
          title: t('limitExceeded'),
          message: errorMessage,
          duration: 4000
        });
        return;
      }
    }
    
    setParticipants({
      ...participants,
      [type]: newValue
    });
  };

  const capacityDisplay = getCapacityDisplay();

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
          <Users className="h-5 w-5 mr-2 text-blue-600 dark:text-blue-400" />
          {t('participants')}
        </h3>
        
        {/* Capacity Display */}
        {capacityDisplay && (
          <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <span className="text-blue-700 dark:text-blue-300 font-medium flex items-center">
                <Info className="h-4 w-4 mr-1" />
                {t('capacityStatus')}
              </span>
              <span className={`font-semibold ${
                capacityDisplay.isFull 
                  ? 'text-red-600 dark:text-red-400' 
                  : 'text-blue-600 dark:text-blue-400'
              }`}>
                {capacityDisplay.selected} / {capacityDisplay.total} {t('selected')}
              </span>
            </div>
            <div className="mt-2 text-xs text-blue-600 dark:text-blue-400">
              {t('adultChildLimit', { 
                limit: capacityDisplay.maxAdultChild || 0
              })}
            </div>
          </div>
        )}
        
        <div className="space-y-4">
          {[
            { key: 'adult', label: t('adult'), icon: User, description: t('adultDesc') },
            { key: 'child', label: t('child'), icon: Smile, description: t('childDesc') },
            { key: 'infant', label: t('infant'), icon: Baby, description: t('infantDesc') }
          ].map(({ key, label, icon: Icon, description }) => {
            const participantType = key as 'adult' | 'child' | 'infant';
            const currentValue = participants[participantType];
            const isDisabled = getButtonDisabledState(participantType);
            const validationMessage = getValidationMessage(participantType);
            
            return (
              <div key={key} className="relative">
                <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex items-center">
                    <Icon className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <div className="font-medium text-gray-900 dark:text-gray-100">{label}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{description}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => handleParticipantChange(participantType, false)}
                      disabled={currentValue === 0}
                      className="p-1 rounded-full border border-gray-300 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      <Minus className="h-4 w-4" />
                    </button>
                    <span className="w-8 text-center font-medium text-gray-900 dark:text-gray-100">
                      {currentValue}
                    </span>
                    <button
                      onClick={() => handleParticipantChange(participantType, true)}
                      disabled={isDisabled}
                      className="p-1 rounded-full border border-gray-300 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                
                {/* Inline Validation Message */}
                {isDisabled && validationMessage && (
                  <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <div className="flex items-center text-xs text-red-700 dark:text-red-300">
                      <AlertCircle className="h-3 w-3 mr-1 flex-shrink-0" />
                      {validationMessage}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        {/* General Validation Errors Display */}
        {validationErrors.participants && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
              <span className="text-sm text-red-700 dark:text-red-300">
                {validationErrors.participants}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
