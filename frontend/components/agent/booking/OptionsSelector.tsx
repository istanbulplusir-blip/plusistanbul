'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loading } from '@/components/ui/Loading';
import { agentApi, TourOption, Tour, TourVariant, Customer, PricingData } from '@/lib/api/agents';


interface BookingData {
  tour: Tour | null;
  variant: TourVariant | null;
  date: string | null;
  participants: {
    adults: number;
    children: number;
    infants: number;
  };
  options: number[];
  customer: Customer | null;
  pricing: PricingData | null;
}

interface OptionsSelectorProps {
  bookingData: BookingData;
  onComplete: (data: Partial<BookingData>) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

export default function OptionsSelector({ 
  bookingData, 
  onComplete, 
  onPrevious, 
  isFirstStep 
}: OptionsSelectorProps) {
  const t = useTranslations('agent.booking.optionsSelector');
  const [options, setOptions] = useState<TourOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOptions, setSelectedOptions] = useState<number[]>(bookingData.options || []);

  useEffect(() => {
    // Fetch tour options from API
    const fetchOptions = async () => {
      if (!bookingData.tour?.id) return;
      
      try {
        setLoading(true);
        const optionsData = await agentApi.tours.getTourOptions(bookingData.tour.id);
        setOptions(optionsData);
      } catch (error) {
        console.error('Error fetching options:', error);
        // Fallback to mock data if API fails
        const mockOptions: TourOption[] = [
          {
            id: 1,
            name: 'صبحانه اضافی',
            description: 'صبحانه کامل در هتل',
            base_price: 15,
            agent_price: 12,
            is_required: false,
            is_active: true,
            category: 'غذا'
          },
          {
            id: 2,
            name: 'راهنمای خصوصی',
            description: 'راهنمای تخصصی برای گروه شما',
            base_price: 50,
            agent_price: 42,
            is_required: false,
            is_active: true,
            category: 'خدمات'
          },
          {
            id: 3,
            name: 'پکیج عکس حرفه‌ای',
            description: 'عکاسی حرفه‌ای در طول تور',
            base_price: 30,
            agent_price: 25,
            is_required: false,
            is_active: true,
            category: 'عکاسی'
          },
          {
            id: 4,
            name: 'ترانسفر فرودگاه',
            description: 'ترانسفر رفت و برگشت از فرودگاه',
            base_price: 25,
            agent_price: 21,
            is_required: false,
            is_active: true,
            category: 'ترانسفر'
          },
          {
            id: 5,
            name: 'بیمه سفر',
            description: 'بیمه کامل سفر و حوادث',
            base_price: 20,
            agent_price: 17,
            is_required: false,
            is_active: true,
            category: 'بیمه'
          }
        ];
        setOptions(mockOptions);
      } finally {
        setLoading(false);
      }
    };

    fetchOptions();
  }, [bookingData.tour?.id]);

  const handleOptionToggle = (optionId: number) => {
    setSelectedOptions(prev => {
      if (prev.includes(optionId)) {
        return prev.filter(id => id !== optionId);
      } else {
        return [...prev, optionId];
      }
    });
  };

  const handleContinue = () => {
    onComplete({ options: selectedOptions });
  };

  const getSelectedOptionsTotal = () => {
    return selectedOptions.reduce((total, optionId) => {
      const option = options.find(opt => opt.id === optionId);
      return total + (option?.agent_price || 0);
    }, 0);
  };

  const getSelectedOptionsRegularTotal = () => {
    return selectedOptions.reduce((total, optionId) => {
      const option = options.find(opt => opt.id === optionId);
      return total + (option?.base_price || 0);
    }, 0);
  };

  const getSavings = () => {
    return getSelectedOptionsRegularTotal() - getSelectedOptionsTotal();
  };

  const getSavingsPercentage = () => {
    const regularTotal = getSelectedOptionsRegularTotal();
    return regularTotal > 0 ? Math.round((getSavings() / regularTotal) * 100) : 0;
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {options.map((option) => (
          <Card
            key={option.id}
            className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
              selectedOptions.includes(option.id)
                ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                : 'hover:ring-1 hover:ring-gray-300'
            }`}
            onClick={() => handleOptionToggle(option.id)}
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {option.name}
                </h3>
                <Badge variant="secondary">{option.category}</Badge>
              </div>

              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {option.description}
              </p>

              <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="space-y-1">
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {t('regularPrice')}: ${option.base_price}
                  </div>
                  <div className="text-lg font-bold text-green-600 dark:text-green-400">
                    {t('agentPrice')}: ${option.agent_price}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-green-600 dark:text-green-400 font-medium">
                    {t('savings')}: ${option.base_price - option.agent_price}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {Math.round(((option.base_price - option.agent_price) / option.base_price) * 100)}% {t('discount')}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Selected Options Summary */}
      {selectedOptions.length > 0 && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {t('selectedOptions')}
            </h3>
            
            <div className="space-y-3">
              {selectedOptions.map((optionId) => {
                const option = options.find(opt => opt.id === optionId);
                if (!option) return null;
                
                return (
                  <div key={optionId} className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
                    <div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {option.name}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                        ({option.category})
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500 dark:text-gray-400 line-through">
                        ${option.base_price}
                      </div>
                      <div className="text-sm font-semibold text-green-600 dark:text-green-400">
                        ${option.agent_price}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <span className="text-lg font-semibold text-gray-900 dark:text-white">
                  {t('totalOptions')}:
                </span>
                <div className="text-right">
                  <div className="text-sm text-gray-500 dark:text-gray-400 line-through">
                    ${getSelectedOptionsRegularTotal()}
                  </div>
                  <div className="text-lg font-bold text-green-600 dark:text-green-400">
                    ${getSelectedOptionsTotal()}
                  </div>
                  <div className="text-sm text-green-600 dark:text-green-400">
                    {t('savings')}: ${getSavings()} ({getSavingsPercentage()}%)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* No Options Selected Message */}
      {selectedOptions.length === 0 && (
        <Card>
          <div className="p-6 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {t('noOptionsSelected')}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {t('noOptionsDescription')}
            </p>
          </div>
        </Card>
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
          className="bg-blue-600 hover:bg-blue-700"
        >
          {t('continue')}
        </Button>
      </div>
    </div>
  );
}
