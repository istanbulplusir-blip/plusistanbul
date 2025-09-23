'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loading } from '@/components/ui/Loading';
import { agentApi, AvailableDate, TourVariant as TourVariantType, Tour, Customer, PricingData } from '@/lib/api/agents';


interface BookingData {
  tour: Tour | null;
  variant: TourVariantType | null;
  schedule_id?: string;
  date: string | null;
  time?: string;
  participants: {
    adults: number;
    children: number;
    infants: number;
  };
  options: number[];
  customer: Customer | null;
  pricing: PricingData | null;
}

interface DateVariantSelectorProps {
  bookingData: BookingData;
  onComplete: (data: Partial<BookingData>) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

export default function DateVariantSelector({ 
  bookingData, 
  onComplete, 
  onPrevious, 
  isFirstStep 
}: DateVariantSelectorProps) {
  const t = useTranslations('Agent.booking.dateVariantSelector');
  const [availableDates, setAvailableDates] = useState<AvailableDate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<string | null>(bookingData.date);
  const [selectedVariant, setSelectedVariant] = useState<TourVariantType | null>(bookingData.variant);
  const [participants, setParticipants] = useState({
    adults: bookingData.participants?.adults || 0,
    children: bookingData.participants?.children || 0,
    infants: bookingData.participants?.infants || 0
  });

  useEffect(() => {
    // Fetch available dates from API
    const fetchAvailableDates = async () => {
      if (!bookingData.tour?.id) return;
      
      try {
        setLoading(true);
        const datesData = await agentApi.tours.getAvailableDates(bookingData.tour.id);
        setAvailableDates(datesData);
      } catch (error) {
        console.error('Error fetching available dates:', error);
        // Fallback to mock data if API fails
        const mockDates: AvailableDate[] = [
          {
            date: '2025-01-15',
            schedule_id: 'schedule_1',
            available_slots: 15,
            variants: [
              {
                id: 1,
                name: 'استاندارد',
                description: 'تور استاندارد با خدمات کامل',
                base_price: 100,
                agent_price: 85,
                duration: '8 ساعت',
                max_participants: 20,
                includes: ['ترانسفر', 'راهنما', 'ناهار'],
                is_active: true
              },
              {
                id: 2,
                name: 'پریمیوم',
                description: 'تور پریمیوم با خدمات لوکس',
                base_price: 150,
                agent_price: 127,
                duration: '10 ساعت',
                max_participants: 15,
                includes: ['ترانسفر VIP', 'راهنما خصوصی', 'ناهار لوکس', 'هدیه'],
                is_active: true
              }
            ]
          },
          {
            date: '2025-01-16',
            schedule_id: 'schedule_2',
            available_slots: 12,
            variants: [
              {
                id: 1,
                name: 'استاندارد',
                description: 'تور استاندارد با خدمات کامل',
                base_price: 100,
                agent_price: 85,
                duration: '8 ساعت',
                max_participants: 20,
                includes: ['ترانسفر', 'راهنما', 'ناهار'],
                is_active: true
              }
            ]
          },
          {
            date: '2025-01-17',
            schedule_id: 'schedule_3',
            available_slots: 8,
            variants: [
              {
                id: 2,
                name: 'پریمیوم',
                description: 'تور پریمیوم با خدمات لوکس',
                base_price: 150,
                agent_price: 127,
                duration: '10 ساعت',
                max_participants: 15,
                includes: ['ترانسفر VIP', 'راهنما خصوصی', 'ناهار لوکس', 'هدیه'],
                is_active: true
              }
            ]
          }
        ];
        setAvailableDates(mockDates);
      } finally {
        setLoading(false);
      }
    };

    fetchAvailableDates();
  }, [bookingData.tour?.id]);

  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
    setSelectedVariant(null); // Reset variant when date changes
  };

  const handleVariantSelect = (variant: TourVariantType) => {
    setSelectedVariant(variant);
  };

  const handleParticipantsChange = (type: 'adults' | 'children' | 'infants', value: number) => {
    setParticipants(prev => ({ ...prev, [type]: value }));
  };

  const handleContinue = () => {
    if (selectedDate && selectedVariant) {
      // Find the schedule_id for the selected date
      const selectedDateData = availableDates.find(d => d.date === selectedDate);
      const schedule_id = selectedDateData?.schedule_id; // Use the actual schedule_id from API
      
      if (!schedule_id) {
        console.error('Schedule ID not found for selected date');
        return;
      }
      
      onComplete({ 
        date: selectedDate, 
        variant: selectedVariant, 
        schedule_id: schedule_id,
        participants 
      });
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  const getTotalParticipants = () => {
    return participants.adults + participants.children + participants.infants;
  };

  const isParticipantsValid = () => {
    const total = getTotalParticipants();
    const maxCapacity = selectedVariant?.available_capacity || selectedVariant?.max_participants || 0;
    return total > 0 && total <= maxCapacity;
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Date Selection */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {t('selectDate')}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableDates.map((dateInfo) => (
            <Card
              key={dateInfo.date}
              className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                selectedDate === dateInfo.date 
                  ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                  : 'hover:ring-1 hover:ring-gray-300'
              }`}
              onClick={() => handleDateSelect(dateInfo.date)}
            >
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    {formatDate(dateInfo.date)}
                  </h4>
                  <Badge variant="secondary">
                    {dateInfo.available_slots} {t('availableSlots')}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {t('availableVariants')}: {dateInfo.variants.length}
                </p>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Variant Selection */}
      {selectedDate && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('selectVariant')}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableDates
              .find(d => d.date === selectedDate)?.variants
              .map((variant) => (
                <Card
                  key={variant.id}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                    selectedVariant?.id === variant.id 
                      ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                      : 'hover:ring-1 hover:ring-gray-300'
                  }`}
                  onClick={() => handleVariantSelect(variant)}
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {variant.name}
                      </h4>
                      <Badge variant="outline">{variant.duration}</Badge>
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      {variant.description}
                    </p>

                    <div className="space-y-2 mb-4">
                      <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                        {t('includes')}:
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {variant.includes && typeof variant.includes === 'object' ? (
                          // Handle object format from agent API
                          Object.entries(variant.includes)
                            .filter(([, value]) => value === true)
                            .map(([key], index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </Badge>
                            ))
                        ) : Array.isArray(variant.includes) ? (
                          // Handle array format from regular API
                          (variant.includes as string[]).map((item, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {item}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            {t('noIncludes')}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
                      <div className="space-y-1">
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {t('regularPrice')}: ${variant.base_price}
                        </div>
                        <div className="text-lg font-bold text-green-600 dark:text-green-400">
                          {t('agentPrice')}: ${variant.agent_price}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-green-600 dark:text-green-400 font-medium">
                          {t('savings')}: ${variant.base_price - variant.agent_price}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {Math.round(((variant.base_price - variant.agent_price) / variant.base_price) * 100)}% {t('discount')}
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
          </div>
        </div>
      )}

      {/* Participants Selection */}
      {selectedVariant && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('selectParticipants')}
          </h3>
          <Card>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('adults')} (18+)
                  </label>
                  <div className="flex items-center space-x-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleParticipantsChange('adults', Math.max(0, participants.adults - 1))}
                      disabled={participants.adults === 0}
                    >
                      -
                    </Button>
                    <span className="text-lg font-semibold text-gray-900 dark:text-white min-w-[2rem] text-center">
                      {participants.adults}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleParticipantsChange('adults', participants.adults + 1)}
                      disabled={getTotalParticipants() >= (selectedVariant.available_capacity || selectedVariant.max_participants)}
                    >
                      +
                    </Button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('children')} (2-17)
                  </label>
                  <div className="flex items-center space-x-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleParticipantsChange('children', Math.max(0, participants.children - 1))}
                      disabled={participants.children === 0}
                    >
                      -
                    </Button>
                    <span className="text-lg font-semibold text-gray-900 dark:text-white min-w-[2rem] text-center">
                      {participants.children}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleParticipantsChange('children', participants.children + 1)}
                      disabled={getTotalParticipants() >= (selectedVariant.available_capacity || selectedVariant.max_participants)}
                    >
                      +
                    </Button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('infants')} (0-2)
                  </label>
                  <div className="flex items-center space-x-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleParticipantsChange('infants', Math.max(0, participants.infants - 1))}
                      disabled={participants.infants === 0}
                    >
                      -
                    </Button>
                    <span className="text-lg font-semibold text-gray-900 dark:text-white min-w-[2rem] text-center">
                      {participants.infants}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleParticipantsChange('infants', participants.infants + 1)}
                      disabled={getTotalParticipants() >= (selectedVariant.available_capacity || selectedVariant.max_participants)}
                    >
                      +
                    </Button>
                  </div>
                </div>
              </div>

              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {t('totalParticipants')}:
                  </span>
                  <span className="text-lg font-semibold text-gray-900 dark:text-white">
                    {getTotalParticipants()} / {selectedVariant.available_capacity || selectedVariant.max_participants}
                  </span>
                </div>
                {!isParticipantsValid() && (
                  <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                    {t('invalidParticipants')}
                  </p>
                )}
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
        <Button
          variant="outline"
          onClick={onPrevious}
          disabled={isFirstStep}
        >
          {t('previous')}
        </Button>
        
        <Button
          onClick={handleContinue}
          disabled={!selectedDate || !selectedVariant || !isParticipantsValid()}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {t('continue')}
        </Button>
      </div>
    </div>
  );
}
