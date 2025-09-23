'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Tour, TourVariant, Customer, PricingData } from '@/lib/api/agents';

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
  payment_method?: string;
}

// Using imported types from @/lib/api/agents

interface PaymentMethod {
  id: string;
  name: string;
  description: string;
  icon: string;
  isAvailable: boolean;
  processingTime: string;
  fees?: number;
}

interface PaymentSelectorProps {
  bookingData: BookingData;
  onComplete: (data: Partial<BookingData>) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

export default function PaymentSelector({ 
  bookingData, 
  onComplete, 
  onPrevious, 
  isFirstStep 
}: PaymentSelectorProps) {
  const t = useTranslations('Agent.booking.payment');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string>('whatsapp');

  const paymentMethods: PaymentMethod[] = [
    {
      id: 'whatsapp',
      name: 'WhatsApp Payment',
      description: 'Payment confirmation via WhatsApp. Order will be marked as pending until payment is confirmed by admin.',
      icon: '📱',
      isAvailable: true,
      processingTime: 'Manual confirmation required',
      fees: 0
    },
    {
      id: 'direct_payment',
      name: 'Direct Payment / Bank Gateway',
      description: 'Direct payment through bank gateway. Order will be automatically marked as paid upon successful payment.',
      icon: '🏦',
      isAvailable: true,
      processingTime: 'Instant',
      fees: 0
    },
    {
      id: 'agent_credit',
      name: 'Agent Credit Account',
      description: 'Deduct from agent\'s credit balance. Requires sufficient credit balance.',
      icon: '💳',
      isAvailable: false, // Placeholder for future implementation
      processingTime: 'Instant',
      fees: 0
    }
  ];

  const handlePaymentMethodSelect = (methodId: string) => {
    setSelectedPaymentMethod(methodId);
  };

  const handleContinue = () => {
    onComplete({ payment_method: selectedPaymentMethod });
  };

  const selectedMethod = paymentMethods.find(method => method.id === selectedPaymentMethod);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {t('title')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('subtitle')}
        </p>
      </div>

      {/* Payment Methods */}
      <div className="space-y-4">
        {paymentMethods.map((method) => (
          <Card 
            key={method.id}
            className={`cursor-pointer transition-all duration-200 ${
              selectedPaymentMethod === method.id 
                ? 'ring-2 ring-blue-500 border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                : 'hover:border-gray-300 dark:hover:border-gray-600'
            } ${!method.isAvailable ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={() => method.isAvailable && handlePaymentMethodSelect(method.id)}
          >
            <div className="p-6">
              <div className="flex items-start space-x-4">
                <div className="text-3xl">{method.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {method.name}
                    </h3>
                    {method.isAvailable ? (
                      <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        {t('available')}
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">
                        {t('comingSoon')}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {method.description}
                  </p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                    <span className="flex items-center space-x-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>{method.processingTime}</span>
                    </span>
                    {method.fees !== undefined && (
                      <span className="flex items-center space-x-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                        </svg>
                        <span>{method.fees === 0 ? t('noFees') : `$${method.fees} ${t('fees')}`}</span>
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
          </Card>
        ))}
      </div>

      {/* Payment Summary */}
      {selectedMethod && (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/20">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-4">
              {t('paymentSummary')}
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-blue-800 dark:text-blue-300">
                  {t('selectedMethod')}:
                </span>
                <span className="font-medium text-blue-900 dark:text-blue-200">
                  {selectedMethod.name}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-blue-800 dark:text-blue-300">
                  {t('processingTime')}:
                </span>
                <span className="font-medium text-blue-900 dark:text-blue-200">
                  {selectedMethod.processingTime}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-blue-800 dark:text-blue-300">
                  {t('totalAmount')}:
                </span>
                <span className="text-lg font-bold text-blue-900 dark:text-blue-200">
                  ${bookingData.pricing?.agent_total || 0}
                </span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Important Notes */}
      <Card className="border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20">
        <div className="p-6">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                {t('importantNote')}
              </h4>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                {selectedPaymentMethod === 'whatsapp' 
                  ? t('whatsappNote')
                  : selectedPaymentMethod === 'direct_payment'
                  ? t('directPaymentNote')
                  : t('generalNote')
                }
              </p>
            </div>
          </div>
        </div>
      </Card>

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
          disabled={!selectedPaymentMethod}
        >
          {t('continue')}
        </Button>
      </div>
    </div>
  );
}
