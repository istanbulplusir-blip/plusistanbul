'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { agentApi, BookingRequest, BookingResponse, Tour, TourVariant, Customer, PricingData } from '@/lib/api/agents';

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

// Using imported types from @/lib/api/agents

interface BookingConfirmationProps {
  bookingData: BookingData;
  onComplete: (data: Partial<BookingData>) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

export default function BookingConfirmation({ 
  bookingData, 
  onPrevious, 
  isFirstStep 
}: BookingConfirmationProps) {
  const t = useTranslations('agent.customers');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [bookingResult, setBookingResult] = useState<BookingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleConfirmBooking = async () => {
    if (!bookingData.tour?.id || !bookingData.variant?.id || !bookingData.customer?.id || !bookingData.date || !bookingData.participants) {
      console.error('Missing required booking data');
      return;
    }
    
    try {
      setIsSubmitting(true);
      
      const bookingRequest: BookingRequest = {
        customer_id: bookingData.customer.id,
        tour_id: bookingData.tour.id,
        variant_id: bookingData.variant.id,
        schedule_id: bookingData.schedule_id || '', // Don't use variant_id as fallback - schedule_id is required
        booking_date: bookingData.date,
        booking_time: bookingData.time || '09:00', // Default time
        participants: {
          adults: bookingData.participants.adults || 0,
          children: bookingData.participants.children || 0,
          infants: bookingData.participants.infants || 0
        },
        selected_options: bookingData.options || [],
        payment_method: bookingData.payment_method || 'whatsapp'
      };
      
      
      const bookingResult = await agentApi.booking.createBooking(bookingRequest);
      setBookingResult(bookingResult);
    } catch (error) {
      console.error('Error creating booking:', error);
      setError(error instanceof Error ? error.message : 'Failed to create booking');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackToDashboard = () => {
    // TODO: Navigate to agent dashboard
    window.location.href = '/agent';
  };

  const handleNewBooking = () => {
    // TODO: Reset booking data and start new booking
    window.location.reload();
  };

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-red-900 dark:text-red-100">
            Booking Failed
          </h3>
          <p className="text-sm text-red-600 dark:text-red-400 max-w-md">
            {error}
          </p>
          <div className="flex space-x-3 mt-6">
            <Button
              variant="outline"
              onClick={() => setError(null)}
            >
              Try Again
            </Button>
            <Button
              variant="outline"
              onClick={onPrevious}
            >
              Go Back
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (isSubmitting) {
    return (
      <div className="text-center py-12">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {t('processingBooking')}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 max-w-md">
            {t('processingDescription')}
          </p>
        </div>
      </div>
    );
  }

  if (bookingResult) {
    return (
      <div className="space-y-6">
        {/* Success Message */}
        <Card className="border-green-200 bg-green-50 dark:bg-green-900/20">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-semibold text-green-800 dark:text-green-200">
                  {t('bookingConfirmed')}
                </h3>
                <p className="mt-1 text-sm text-green-700 dark:text-green-300">
                  {t('bookingConfirmedDescription')}
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Booking Details */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {t('bookingDetails')}
            </h3>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('bookingId')}
                  </label>
                  <p className="text-sm text-gray-900 dark:text-white font-mono">
                    {bookingResult.booking_id}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('confirmationCode')}
                  </label>
                  <p className="text-sm text-gray-900 dark:text-white font-mono">
                    {bookingResult.confirmation_code}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('status')}
                  </label>
                  <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    {t('confirmed')}
                  </Badge>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('totalAmount')}
                  </label>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    ${bookingResult.total_amount}
                  </p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  {t('tourDetails')}
                </h4>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p><strong>{t('tour')}:</strong> {bookingData.tour?.title}</p>
                  <p><strong>{t('variant')}:</strong> {bookingData.variant?.name}</p>
                  <p><strong>{t('date')}:</strong> {bookingData.date}</p>
                  <p><strong>{t('participants')}:</strong> {bookingData.participants?.adults} {t('adults')}, {bookingData.participants?.children} {t('children')}, {bookingData.participants?.infants} {t('infants')}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  {t('customerDetails')}
                </h4>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p><strong>{t('name')}:</strong> {bookingData.customer?.first_name} {bookingData.customer?.last_name}</p>
                  <p><strong>{t('email')}:</strong> {bookingData.customer?.email}</p>
                  <p><strong>{t('phone')}:</strong> {bookingData.customer?.phone}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  {t('commissionInfo')}
                </h4>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p><strong>{t('commissionRate')}:</strong> 5%</p>
                  <p><strong>{t('commissionAmount')}:</strong> <span className="text-green-600 dark:text-green-400 font-semibold">${bookingResult.commission_amount?.toFixed(2) || '0.00'}</span></p>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Actions */}
        <div className="flex justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
          <Button
            variant="outline"
            onClick={handleBackToDashboard}
          >
            {t('backToDashboard')}
          </Button>
          
          <div className="space-x-3">
            <Button
              variant="outline"
              onClick={handleNewBooking}
            >
              {t('newBooking')}
            </Button>
            <Button
              onClick={() => window.print()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {t('printConfirmation')}
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Final Review */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('finalReview')}
          </h3>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Tour Summary */}
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  {t('tourSummary')}
                </h4>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p><strong>{t('tour')}:</strong> {bookingData.tour?.title}</p>
                  <p><strong>{t('variant')}:</strong> {bookingData.variant?.name}</p>
                  <p><strong>{t('date')}:</strong> {bookingData.date}</p>
                  <p><strong>{t('duration')}:</strong> {bookingData.variant?.duration}</p>
                </div>
              </div>

              {/* Customer Summary */}
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  {t('customerSummary')}
                </h4>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p><strong>{t('name')}:</strong> {bookingData.customer?.first_name} {bookingData.customer?.last_name}</p>
                  <p><strong>{t('email')}:</strong> {bookingData.customer?.email}</p>
                  <p><strong>{t('phone')}:</strong> {bookingData.customer?.phone}</p>
                </div>
              </div>
            </div>

            {/* Pricing Summary */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                {t('pricingSummary')}
              </h4>
              <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex justify-between">
                  <span>{t('subtotal')}:</span>
                  <span>${bookingData.pricing?.agent_subtotal}</span>
                </div>
                <div className="flex justify-between">
                  <span>{t('serviceFee')}:</span>
                  <span>${bookingData.pricing?.agent_fees}</span>
                </div>
                <div className="flex justify-between">
                  <span>{t('vat')}:</span>
                  <span>${bookingData.pricing?.agent_taxes}</span>
                </div>
                <div className="flex justify-between font-semibold text-lg pt-2 border-t border-gray-200 dark:border-gray-700">
                  <span>{t('total')}:</span>
                  <span className="text-blue-600 dark:text-blue-400">${bookingData.pricing?.agent_total}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Terms and Conditions */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('termsAndConditions')}
          </h3>
          
          <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
            <p>{t('terms1')}</p>
            <p>{t('terms2')}</p>
            <p>{t('terms3')}</p>
            <p>{t('terms4')}</p>
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
          onClick={handleConfirmBooking}
          className="bg-green-600 hover:bg-green-700"
        >
          {t('confirmBooking')}
        </Button>
      </div>
    </div>
  );
}
