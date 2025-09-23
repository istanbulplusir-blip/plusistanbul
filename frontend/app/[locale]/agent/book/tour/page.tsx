'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui/Card';
import AgentHeader from '@/components/agent/AgentHeader';
import AgentSidebar from '@/components/agent/AgentSidebar';
import TourSelector from '@/components/agent/booking/TourSelector';
import DateVariantSelector from '@/components/agent/booking/DateVariantSelector';
import OptionsSelector from '@/components/agent/booking/OptionsSelector';
import CustomerSelector from '@/components/agent/booking/CustomerSelector';
import PricingSummary from '@/components/agent/booking/PricingSummary';
import PaymentSelector from '@/components/agent/booking/PaymentSelector';
import BookingConfirmation from '@/components/agent/booking/BookingConfirmation';
import ErrorBoundary from '@/components/ErrorBoundary';
import { Tour, TourVariant, Customer, PricingData } from '@/lib/api/agents';

interface BookingStep {
  id: string;
  title: string;
  component: React.ComponentType<BookingStepProps>;
  isCompleted: boolean;
}

interface BookingStepProps {
  bookingData: BookingData;
  onComplete: (data: Partial<BookingData>) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

interface BookingData {
  tour: Tour | null;
  variant: TourVariant | null;
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
  payment_method?: string;
}

export default function AgentTourBookingPage() {
  const t = useTranslations('Agent.booking');
  const [currentStep, setCurrentStep] = useState(0);
  const [bookingData, setBookingData] = useState<BookingData>({
    tour: null,
    variant: null,
    date: null,
    participants: { adults: 0, children: 0, infants: 0 },
    options: [],
    customer: null,
    pricing: null,
    payment_method: undefined
  });

  const steps: BookingStep[] = [
    { id: 'tour', title: t('steps.tour.title'), component: TourSelector, isCompleted: !!bookingData.tour },
    { id: 'date', title: t('steps.date.title'), component: DateVariantSelector, isCompleted: !!bookingData.variant && !!bookingData.date },
    { id: 'options', title: t('steps.options.title'), component: OptionsSelector, isCompleted: true },
    { id: 'customer', title: t('steps.customer.title'), component: CustomerSelector, isCompleted: !!bookingData.customer },
    { id: 'pricing', title: t('steps.pricing.title'), component: PricingSummary, isCompleted: !!bookingData.pricing },
    { id: 'payment', title: t('steps.payment.title'), component: PaymentSelector, isCompleted: !!bookingData.payment_method },
    { id: 'confirm', title: t('steps.confirm.title'), component: BookingConfirmation, isCompleted: false }
  ];

  const handleStepComplete = (stepId: string, data: Partial<BookingData>) => {
    setBookingData(prev => ({ ...prev, ...data }));
    
    const stepIndex = steps.findIndex(step => step.id === stepId);
    if (stepIndex < steps.length - 1) {
      setCurrentStep(stepIndex + 1);
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <AgentHeader />
      
      <div className="flex">
        <AgentSidebar />
        
        <main className="flex-1 p-6">
          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {t('tourBooking.title')}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {t('tourBooking.subtitle')}
              </p>
            </div>

            {/* Progress Steps */}
            <Card className="mb-8">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  {steps.map((step, index) => (
                    <div key={step.id} className="flex items-center flex-1">
                      <div className="flex flex-col items-center">
                        <div className={`flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300 ${
                          index <= currentStep 
                            ? 'bg-blue-600 border-blue-600 text-white shadow-lg' 
                            : 'bg-gray-200 border-gray-300 text-gray-500 dark:bg-gray-700 dark:border-gray-600'
                        }`}>
                          {index < currentStep ? (
                            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <span className="text-sm font-bold">{index + 1}</span>
                          )}
                        </div>
                        <div className="mt-2 text-center">
                          <p className={`text-xs font-medium ${
                            index <= currentStep 
                              ? 'text-blue-600 dark:text-blue-400' 
                              : 'text-gray-500 dark:text-gray-400'
                          }`}>
                            {step.title}
                          </p>
                          {index === currentStep && (
                            <div className="mt-1 w-2 h-2 bg-blue-600 rounded-full mx-auto animate-pulse"></div>
                          )}
                        </div>
                      </div>
                      {index < steps.length - 1 && (
                        <div className={`flex-1 h-0.5 mx-2 transition-all duration-300 ${
                          index < currentStep ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                        }`} />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            {/* Current Step Content */}
            <Card>
              <div className="p-6">
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {steps[currentStep].title}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    {t(`steps.${steps[currentStep].id}.description`)}
                  </p>
                </div>

                <ErrorBoundary>
                  <CurrentStepComponent
                    bookingData={bookingData}
                    onComplete={(data: Partial<BookingData>) => handleStepComplete(steps[currentStep].id, data)}
                    onPrevious={handlePreviousStep}
                    onNext={handleNextStep}
                    isFirstStep={currentStep === 0}
                    isLastStep={currentStep === steps.length - 1}
                  />
                </ErrorBoundary>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
