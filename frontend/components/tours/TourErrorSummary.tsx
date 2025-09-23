import React from 'react';
import { AlertCircle, CheckCircle, Info, HelpCircle, Users, Calendar, Package } from 'lucide-react';
import { useTranslations } from 'next-intl';

interface ValidationErrors {
  participants?: string;
  options?: string;
  capacity?: string;
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
  variants: TourVariant[];
  schedules: TourSchedule[];
  is_available_today: boolean;
  is_active: boolean;
}

interface TourErrorSummaryProps {
  validationErrors: ValidationErrors;
  selectedSchedule: TourSchedule | null;
  selectedVariant: TourVariant | null;
  participants: { adult: number; child: number; infant: number };
  tour: Tour | null;
}

export default function TourErrorSummary({
  validationErrors,
  selectedSchedule,
  selectedVariant,
  participants,
  tour
}: TourErrorSummaryProps) {
  const t = useTranslations('tours');

  const hasErrors = Object.keys(validationErrors).length > 0;
  const totalParticipants = participants.adult + participants.child + participants.infant;
  const isReadyToBook = selectedSchedule && selectedVariant && totalParticipants > 0 && !hasErrors;

  // Booking progress calculation
  const getBookingProgress = () => {
    const steps = [];
    
    if (selectedSchedule) {
      steps.push({ name: t('dateSelected'), icon: Calendar, completed: true });
    } else {
      steps.push({ name: t('selectDate'), icon: Calendar, completed: false });
    }
    
    if (selectedVariant) {
      steps.push({ name: t('packageSelected'), icon: Package, completed: true });
    } else {
      steps.push({ name: t('selectPackage'), icon: Package, completed: false });
    }
    
    if (totalParticipants > 0) {
      steps.push({ name: t('participantsSelected'), icon: Users, completed: true });
    } else {
      steps.push({ name: t('selectParticipants'), icon: Users, completed: false });
    }
    
    return steps;
  };

  const bookingSteps = getBookingProgress();

  return (
    <div className="space-y-4">
      {/* Booking Progress */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center">
            <HelpCircle className="h-5 w-5 mr-2 text-blue-600 dark:text-blue-400" />
            {t('bookingProgress')}
          </h3>
        </div>
        <div className="p-4">
          <div className="space-y-3">
            {bookingSteps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div className={`flex items-center justify-center w-6 h-6 rounded-full mr-3 ${
                  step.completed 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                }`}>
                  {step.completed ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <span className="text-xs font-medium">{index + 1}</span>
                  )}
                </div>
                <span className={`text-sm ${
                  step.completed 
                    ? 'text-green-700 dark:text-green-300 font-medium' 
                    : 'text-gray-600 dark:text-gray-400'
                }`}>
                  {step.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Error Summary */}
      {hasErrors && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="p-4 border-b border-red-200 dark:border-red-700 bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-3 flex-shrink-0" />
              <h4 className="text-sm font-medium text-red-800 dark:text-red-200">
                {t('pleaseFixIssues')}
              </h4>
            </div>
          </div>
          <div className="p-4">
            <ul className="space-y-2">
              {validationErrors.participants && (
                <li className="flex items-start">
                  <AlertCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-red-700 dark:text-red-300">
                    {validationErrors.participants}
                  </span>
                </li>
              )}
              {validationErrors.options && (
                <li className="flex items-start">
                  <AlertCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-red-700 dark:text-red-300">
                    {validationErrors.options}
                  </span>
                </li>
              )}
              {validationErrors.capacity && (
                <li className="flex items-start">
                  <AlertCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-red-700 dark:text-red-300">
                    {validationErrors.capacity}
                  </span>
                </li>
              )}
            </ul>
          </div>
        </div>
      )}

      {/* Success Status */}
      {isReadyToBook && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="p-4 border-b border-green-200 dark:border-green-700 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
              <h4 className="text-sm font-medium text-green-800 dark:text-green-200">
                {t('readyToBook')}
              </h4>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-2 text-sm text-green-700 dark:text-green-300">
              <div className="flex items-center">
                <Calendar className="h-4 w-4 mr-2" />
                <span>{t('dateSelected')}: {selectedSchedule?.start_date}</span>
              </div>
              <div className="flex items-center">
                <Package className="h-4 w-4 mr-2" />
                <span>{t('packageSelected')}: {selectedVariant?.name}</span>
              </div>
              <div className="flex items-center">
                <Users className="h-4 w-4 mr-2" />
                <span>{t('participantsSelected')}: {totalParticipants} {t('people')}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Booking Guidelines */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div className="p-4 border-b border-blue-200 dark:border-blue-700 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20">
          <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200 flex items-center">
            <Info className="h-4 w-4 mr-2" />
            {t('bookingGuidelines')}
          </h4>
        </div>
        <div className="p-4">
          <ul className="space-y-2 text-sm text-blue-700 dark:text-blue-300">
            <li className="flex items-start">
              <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
              <span>{t('minParticipantsRequired', { min: tour?.min_participants || 1 })}</span>
            </li>
            <li className="flex items-start">
              <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
              <span>{t('maxParticipantsLimit', { max: tour?.max_participants || 20 })}</span>
            </li>
            <li className="flex items-start">
              <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
              <span>{t('maxInfantsLimit', { max: 2 })}</span>
            </li>
            <li className="flex items-start">
              <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
              <span>{t('infantsNotCounted')}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
