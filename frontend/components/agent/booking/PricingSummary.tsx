'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loading } from '@/components/ui/Loading';
import { agentApi, PricingData, Tour, TourVariant, Customer } from '@/lib/api/agents';

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

// Using imported types from @/lib/api/agents


interface PricingSummaryProps {
  bookingData: BookingData;
  onComplete: (data: Partial<BookingData>) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

export default function PricingSummary({ 
  bookingData, 
  onComplete, 
  onPrevious, 
  isFirstStep 
}: PricingSummaryProps) {
  const t = useTranslations('agent.booking.pricingSummary');
  const [pricing, setPricing] = useState<PricingData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Calculate pricing using API
    const calculatePricing = async () => {
      console.log('PricingSummary - bookingData:', bookingData);
      
      if (!bookingData.tour?.id || !bookingData.variant?.id || !bookingData.participants || !bookingData.options) {
        console.log('Missing required data:', {
          tour: bookingData.tour?.id,
          variant: bookingData.variant?.id,
          participants: bookingData.participants,
          options: bookingData.options
        });
        return;
      }
      
      try {
        setLoading(true);
        
        console.log('Sending to API:', {
          tour_id: bookingData.tour.id,
          variant_id: bookingData.variant.id,
          participants: bookingData.participants,
          options: bookingData.options
        });
        
        const pricingData = await agentApi.pricing.calculatePricing({
          tour_id: bookingData.tour.id,
          variant_id: bookingData.variant.id,
          participants: bookingData.participants,
          options: bookingData.options
        });
        
        console.log('API pricing response:', pricingData);
        console.log('API pricing data:', pricingData);
        setPricing(pricingData);
      } catch (error) {
        console.error('Error calculating pricing:', error);
        console.log('Using fallback calculation with data:', {
          variant: bookingData.variant,
          participants: bookingData.participants,
          options: bookingData.options
        });
        
        // Fallback to local calculation if API fails
        const adults = bookingData.participants?.adults || 0;
        const children = bookingData.participants?.children || 0;
        const infants = bookingData.participants?.infants || 0;
        const basePricePerPerson = bookingData.variant?.base_price || 0;
        const agentPricePerPerson = bookingData.variant?.agent_price || 0;
        
        const basePrice = (basePricePerPerson * adults) + (basePricePerPerson * 0.7 * children);
        const agentPrice = (agentPricePerPerson * adults) + (agentPricePerPerson * 0.7 * children);
        
        console.log('Options array:', bookingData.options);
        console.log('Options details:', bookingData.options.map(id => ({ id, type: typeof id })));
        
        const optionsTotal = bookingData.options?.reduce((total, optionId) => {
          // Mock options pricing - in real app, fetch from API
          const optionPrices = { 1: 12, 2: 42, 3: 25, 4: 21, 5: 17 };
          const price = optionPrices[optionId as keyof typeof optionPrices] || 0;
          console.log(`Option ${optionId}: $${price}`);
          return total + price;
        }, 0) || 0;
        
        console.log('Total options cost:', optionsTotal);
        
        const agentSubtotal = agentPrice + optionsTotal;
        const serviceFee = agentSubtotal * 0.03;
        const vat = (agentSubtotal + serviceFee) * 0.09;
        const agentTotal = agentSubtotal + serviceFee + vat;
        const savings = basePrice - agentPrice;
        
        const mockPricing: PricingData = {
          base_price: basePrice + optionsTotal,
          agent_subtotal: agentSubtotal,
          agent_fees: serviceFee,
          agent_taxes: vat,
          agent_total: agentTotal,
          savings: savings,
          savings_percentage: basePrice > 0 ? Math.round((savings / basePrice) * 100) : 0,
          pricing_method: 'discount_percentage',
          breakdown: {
            adults: basePricePerPerson * adults,
            children: basePricePerPerson * 0.7 * children,
            infants: 0,
            options: optionsTotal
          },
          fees_taxes_breakdown: {
            subtotal: agentSubtotal,
            discounts_total: 0,
            fees_total: serviceFee,
            tax_total: vat,
            grand_total: agentTotal,
            service_fee_rate: 0.03,
            vat_rate: 0.09
          }
        };
        
        console.log('Generated mock pricing:', mockPricing);
        console.log('Calculation details:', {
          adults, children, infants,
          basePricePerPerson, agentPricePerPerson,
          basePrice, agentPrice, optionsTotal,
          agentSubtotal, serviceFee, vat, agentTotal, savings
        });
        
        setPricing(mockPricing);
      } finally {
        setLoading(false);
      }
    };

    calculatePricing();
  }, [bookingData]);

  const handleContinue = () => {
    if (pricing) {
      onComplete({ pricing });
    }
  };

  if (loading) {
    return <Loading />;
  }

  if (!pricing) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
          {t('noPricingData')}
        </h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {t('noPricingDescription')}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Booking Summary */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('bookingSummary')}
          </h3>
          
          <div className="space-y-4">
            {/* Tour Info */}
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white">
                  {bookingData.tour?.title}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {bookingData.variant?.name} - {bookingData.date}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {t('participants')}: {bookingData.participants?.adults || 0} {t('adults')}, {bookingData.participants?.children || 0} {t('children')}, {bookingData.participants?.infants || 0} {t('infants')}
                </p>
              </div>
              <Badge variant="outline">{bookingData.variant?.duration}</Badge>
            </div>

            {/* Customer Info */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                {t('customer')}
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {bookingData.customer?.first_name} {bookingData.customer?.last_name}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {bookingData.customer?.email} - {bookingData.customer?.phone}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Pricing Breakdown */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('pricingBreakdown')}
          </h3>
          
          <div className="space-y-4">
            {/* Base Pricing */}
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900 dark:text-white">
                {t('basePricing')}
              </h4>
              <div className="space-y-1 pl-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('adults')} ({bookingData.participants?.adults || 0}x):
                  </span>
                  <span className="text-gray-900 dark:text-white">
                    ${pricing.breakdown?.adults || 0}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('children')} ({bookingData.participants?.children || 0}x):
                  </span>
                  <span className="text-gray-900 dark:text-white">
                    ${pricing.breakdown?.children || 0}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('infants')} ({bookingData.participants?.infants || 0}x):
                  </span>
                  <span className="text-gray-900 dark:text-white">
                    {t('free')}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('additionalOptions')}:
                  </span>
                  <span className="text-gray-900 dark:text-white">
                    ${pricing.breakdown?.options || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Agent Pricing */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 dark:text-white">
                  {t('agentPricing')}
                </h4>
                <Badge variant="secondary">
                  {pricing.savings_percentage || 0}% {t('discount')}
                </Badge>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('regularPrice')}:
                  </span>
                  <span className="text-gray-900 dark:text-white line-through">
                    ${pricing.base_price || 0}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('agentPrice')}:
                  </span>
                  <span className="text-green-600 dark:text-green-400 font-semibold">
                    ${pricing.agent_subtotal || 0}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('savings')}:
                  </span>
                  <span className="text-green-600 dark:text-green-400 font-semibold">
                    ${pricing.savings || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Fees and Taxes */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                {t('feesAndTaxes')}
              </h4>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('subtotal')}:
                  </span>
                  <span className="text-gray-900 dark:text-white">
                    ${pricing.fees_taxes_breakdown?.subtotal || 0}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('serviceFee')} (3%):
                  </span>
                  <span className="text-gray-900 dark:text-white">
                    ${pricing.fees_taxes_breakdown?.fees_total || 0}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('vat')} (9%):
                  </span>
                  <span className="text-gray-900 dark:text-white">
                    ${pricing.fees_taxes_breakdown?.tax_total || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Total */}
            <div className="pt-4 border-t-2 border-gray-300 dark:border-gray-600">
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold text-gray-900 dark:text-white">
                  {t('total')}:
                </span>
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  ${pricing.agent_total || 0}
                </span>
              </div>
              <div className="text-right">
                <div className="text-sm text-green-600 dark:text-green-400">
                  {t('totalSavings')}: ${pricing.savings || 0} ({pricing.savings_percentage || 0}%)
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Commission Info */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('commissionInfo')}
          </h3>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">
                {t('commissionRate')}:
              </span>
              <span className="text-gray-900 dark:text-white">
                5%
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">
                {t('commissionAmount')}:
              </span>
              <span className="text-green-600 dark:text-green-400 font-semibold">
                ${((pricing.agent_total || 0) * 0.05).toFixed(2)}
              </span>
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
        >
          {t('continue')}
        </Button>
      </div>
    </div>
  );
}
