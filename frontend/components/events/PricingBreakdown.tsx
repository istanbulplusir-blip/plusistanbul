'use client';

import { useState, useCallback, useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { 
  Calculator, 
  Tag, 
  CheckCircle2, 
  Receipt,
  TrendingDown,
  TrendingUp
} from 'lucide-react';
import { EventPricingBreakdown } from '@/lib/types/api';

interface PricingBreakdownProps {
  breakdown: EventPricingBreakdown | null;
  selectedSeats?: Array<{
    id: string;
    seat_number: string;
    row_number: string;
    section: string;
    price: number;
    currency: string;
    is_premium: boolean;
    is_wheelchair_accessible: boolean;
  }>;
  selectedOptions?: Array<{
    id: string;
    name: string;
    price: number;
    currency: string;
    quantity: number;
  }>;
  isLoading?: boolean;
  discountCode?: string;
  onDiscountCodeChange?: (code: string) => void;
  onApplyDiscount?: () => void;
  onRemoveDiscount?: (discountIndex: number) => void;
  formatPrice: (price: number, currency: string) => string;
  showDetails?: boolean;
  onToggleDetails?: () => void;
}

export default function PricingBreakdown({
  breakdown,
  selectedSeats = [],
  selectedOptions = [],
  isLoading = false,
  discountCode = '',
  onDiscountCodeChange,
  onApplyDiscount,
  onRemoveDiscount,
  formatPrice,
  showDetails = false,
  onToggleDetails
}: PricingBreakdownProps) {
  const t = useTranslations('pricing');
  const [expandedSections, setExpandedSections] = useState<{
    options: boolean;
    discounts: boolean;
    fees: boolean;
    taxes: boolean;
  }>({
    options: false,
    discounts: false,
    fees: false,
    taxes: false
  });

  const toggleSection = useCallback((section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  }, []);

  const totalSavings = useMemo(() => {
    if (!breakdown) return 0;
    const discounts = Array.isArray((breakdown as { discounts?: Array<{ amount?: string | number }> }).discounts) 
      ? (breakdown as { discounts: Array<{ amount?: string | number }> }).discounts 
      : [];
    return discounts.reduce((sum: number, d: { amount?: string | number }) => sum + (Number(d?.amount) || 0), 0);
  }, [breakdown]);

  const totalExtras = useMemo(() => {
    if (!breakdown) return 0;
    return breakdown.fees_total + breakdown.taxes_total;
  }, [breakdown]);

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="animate-pulse">
          <div className="flex items-center justify-between mb-4">
            <div className="h-5 bg-gray-200 rounded w-32"></div>
            <div className="h-5 bg-gray-200 rounded w-20"></div>
          </div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex justify-between">
                <div className="h-4 bg-gray-200 rounded w-24"></div>
                <div className="h-4 bg-gray-200 rounded w-16"></div>
              </div>
            ))}
          </div>
          <div className="border-t pt-4 mt-4">
            <div className="flex justify-between">
              <div className="h-6 bg-gray-200 rounded w-20"></div>
              <div className="h-6 bg-gray-200 rounded w-24"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!breakdown) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 text-center">
        <Calculator className="h-12 w-12 text-gray-300 dark:text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{t('noPricingData')}</h3>
        <p className="text-gray-600 dark:text-gray-400">{t('selectSeatsForPricing')}</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Receipt className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('pricingBreakdown')}</h3>
          </div>
          
          {onToggleDetails && (
            <button
              onClick={onToggleDetails}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              {showDetails ? t('hideDetails') : t('showDetails')}
            </button>
          )}
        </div>
      </div>

      <div className="p-4">
        {/* Seats Pricing */}
        {selectedSeats.length > 0 && (
          <div className="space-y-3 mb-4">
            <div className="font-medium text-gray-900 dark:text-gray-100 mb-2">
              {t('seats')} ({selectedSeats.length} {selectedSeats.length === 1 ? t('seat') : t('seats')})
            </div>
            
            {/* Group seats by section */}
            {Object.entries(selectedSeats.reduce((acc: Record<string, typeof selectedSeats>, seat) => {
              if (!acc[seat.section]) acc[seat.section] = [];
              acc[seat.section].push(seat);
              return acc;
            }, {})).map(([sectionName, seats]) => (
              <div key={sectionName} className="border-l-2 border-gray-200 dark:border-gray-600 pl-3">
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {sectionName}
                </div>
                {seats.map((seat) => (
                  <div key={seat.id} className="flex justify-between items-center text-sm mb-1">
                    <div className="flex items-center">
                      <span className="text-gray-600 dark:text-gray-400">
                        Row {seat.row_number}, Seat {seat.seat_number}
                      </span>
                      {seat.is_premium && (
                        <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200 px-2 py-0.5 rounded">
                          Premium
                        </span>
                      )}
                      {seat.is_wheelchair_accessible && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-200 px-2 py-0.5 rounded">
                          Wheelchair
                        </span>
                      )}
                    </div>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {formatPrice(seat.price, seat.currency)}
                    </span>
                  </div>
                ))}
                <div className="flex justify-between items-center pt-1 border-t border-gray-100 dark:border-gray-600">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {sectionName} Total
                  </span>
                  <span className="font-semibold text-gray-900 dark:text-gray-100">
                    {formatPrice(seats.reduce((sum, seat) => sum + seat.price, 0), seats[0].currency)}
                  </span>
                </div>
              </div>
            ))}
            
            {/* Total Seats Price */}
            <div className="flex justify-between items-center pt-2 border-t border-gray-200 dark:border-gray-600">
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {t('seatsTotal')}
              </span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(selectedSeats.reduce((sum, seat) => sum + seat.price, 0), 'USD')}
              </span>
            </div>
          </div>
        )}

        {/* Fallback to breakdown if no seats selected */}
        {selectedSeats.length === 0 && breakdown && (
          <div className="space-y-3 mb-4">
            {/* Base Price - Simplified for transfers */}
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  {t('basePrice')}
                </span>
                {/* Only show quantity for non-transfer products */}
                {breakdown.pricing_type !== 'transfer' && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {formatPrice(breakdown.base_price, 'USD')} × {breakdown.quantity}
                  </div>
                )}
                {/* For transfers, show trip type context - REMOVED as requested */}
              </div>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(
                  // For transfers, show base_price directly (not multiplied by quantity)
                  // For events/tours, use the original calculation
                  breakdown.pricing_type === 'transfer' ? 
                  breakdown.base_price : 
                  breakdown.base_price * (breakdown.quantity || 1), 
                  'USD'
                )}
              </span>
            </div>

            {/* For round-trip transfers, show outbound and return separately */}
            {breakdown.pricing_type === 'transfer' && breakdown.trip_type === 'round_trip' && (
              <div className="space-y-2 ml-4">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {formatPrice(breakdown.base_price, 'USD')} {t('outbound')}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400">
                    {formatPrice(breakdown.base_price, 'USD')}
                  </span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {formatPrice(breakdown.base_price, 'USD')} {t('return')}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400">
                    {formatPrice(breakdown.base_price, 'USD')}
                  </span>
                </div>
              </div>
            )}

            {/* Outbound Surcharge - for transfers */}
            {breakdown.outbound_surcharge && breakdown.outbound_surcharge > 0 && (
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    Outbound Surcharge
                  </span>
                  {breakdown.outbound_surcharge_percentage && (
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Peak Hours +{breakdown.outbound_surcharge_percentage}%
                    </div>
                  )}
                </div>
                <span className="font-semibold text-gray-900 dark:text-gray-100">
                  {formatPrice(breakdown.outbound_surcharge, 'USD')}
                </span>
              </div>
            )}

            {/* Return Surcharge - for transfers */}
            {breakdown.return_surcharge && breakdown.return_surcharge > 0 && (
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    Return Surcharge
                  </span>
                  {breakdown.return_surcharge_percentage && (
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Return Trip +{breakdown.return_surcharge_percentage}%
                    </div>
                  )}
                </div>
                <span className="font-semibold text-gray-900 dark:text-gray-100">
                  {formatPrice(breakdown.return_surcharge, 'USD')}
                </span>
              </div>
            )}

            {/* Round Trip Discount - for transfers */}
            {breakdown.round_trip_discount && breakdown.round_trip_discount > 0 && (
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-medium text-green-700 dark:text-green-400">
                    Round Trip Discount
                  </span>
                  {breakdown.round_trip_discount_percentage && (
                    <div className="text-sm text-green-600 dark:text-green-400">
                      -{breakdown.round_trip_discount_percentage}%
                    </div>
                  )}
                </div>
                <span className="font-semibold text-green-700 dark:text-green-400">
                  -{formatPrice(breakdown.round_trip_discount, 'USD')}
                </span>
              </div>
            )}

            {/* Options - for transfers */}
            {breakdown.options_total && breakdown.options_total > 0 && (
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    Options
                  </span>
                </div>
                <span className="font-semibold text-gray-900 dark:text-gray-100">
                  {formatPrice(breakdown.options_total, 'USD')}
                </span>
              </div>
            )}

            {/* Subtotal - Only show for non-transfer products or when needed */}
            {breakdown.pricing_type !== 'transfer' && (
              <div className="flex justify-between items-center pt-2 border-t border-gray-200 dark:border-gray-600">
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  Subtotal
                </span>
                <span className="font-semibold text-gray-900 dark:text-gray-100">
                  {formatPrice(breakdown.subtotal || 0, 'USD')}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Options */}
        {selectedOptions.length > 0 && (
          <div className="border-t pt-4 mb-4">
            <button
              onClick={() => toggleSection('options')}
              className="flex items-center justify-between w-full text-left"
            >
              <div className="flex items-center">
                <span className="font-medium text-gray-900 dark:text-gray-100">{t('addOns')}</span>
                <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                  ({selectedOptions.length} {selectedOptions.length === 1 ? t('item') : t('items')})
                </span>
              </div>
              <div className="flex items-center">
                <span className="font-medium text-gray-900 dark:text-gray-100 mr-2">
                  {formatPrice(selectedOptions.reduce((sum, opt) => sum + (opt.price * opt.quantity), 0), 'USD')}
                </span>
                <TrendingDown 
                  className={`h-4 w-4 text-gray-400 transition-transform ${
                    expandedSections.options ? 'rotate-180' : ''
                  }`}
                />
              </div>
            </button>
            
            {expandedSections.options && (
              <div className="mt-3 pl-4 space-y-2">
                {selectedOptions.map((option) => (
                  <div key={option.id} className="flex justify-between items-center text-sm">
                    <div>
                      <span className="text-gray-900 dark:text-gray-100">{option.name}</span>
                      <span className="text-gray-600 dark:text-gray-400 ml-2">
                        ({formatPrice(option.price, 'USD')} × {option.quantity})
                      </span>
                    </div>
                    <span className="text-gray-900 dark:text-gray-100">
                      {formatPrice(option.price * option.quantity, 'USD')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Fallback to breakdown options if no selected options */}
        {selectedOptions.length === 0 && breakdown && breakdown.options.length > 0 && (
          <div className="border-t pt-4 mb-4">
            <button
              onClick={() => toggleSection('options')}
              className="flex items-center justify-between w-full text-left"
            >
              <div className="flex items-center">
                <span className="font-medium text-gray-900 dark:text-gray-100">{t('addOns')}</span>
                <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                  ({breakdown.options.length} {breakdown.options.length === 1 ? t('item') : t('items')})
                </span>
              </div>
              <div className="flex items-center">
                <span className="font-medium text-gray-900 dark:text-gray-100 mr-2">
                  {formatPrice(breakdown.options_total, 'USD')}
                </span>
                <TrendingDown 
                  className={`h-4 w-4 text-gray-400 transition-transform ${
                    expandedSections.options ? 'rotate-180' : ''
                  }`}
                />
              </div>
            </button>
            
            {expandedSections.options && (
              <div className="mt-3 pl-4 space-y-2">
                {breakdown.options.map((option) => (
                  <div key={option.name} className="flex justify-between items-center text-sm">
                    <div>
                      <span className="text-gray-900 dark:text-gray-100">{option.name}</span>
                      <span className="text-gray-600 dark:text-gray-400 ml-2">
                        ({formatPrice(option.price, 'USD')} × {option.quantity})
                      </span>
                    </div>
                    <span className="text-gray-900 dark:text-gray-100">
                      {formatPrice(option.total, 'USD')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Discounts */}
        {Array.isArray((breakdown as { discounts?: Array<{ name: string; percentage?: string; amount: number }>; discount_total?: number }).discounts) && (breakdown as { discounts: Array<{ name: string; percentage?: string; amount: number }>; discount_total?: number }).discounts.length > 0 && (
          <div className="border-t pt-4 mb-4">
            <button
              onClick={() => toggleSection('discounts')}
              className="flex items-center justify-between w-full text-left"
            >
              <div className="flex items-center">
                <span className="font-medium text-green-700">{t('discounts')}</span>
                <span className="ml-2 text-sm text-green-600">
                  ({(breakdown as { discounts: Array<{ name: string; percentage?: string; amount: number }> }).discounts.length} {(breakdown as { discounts: Array<{ name: string; percentage?: string; amount: number }> }).discounts.length === 1 ? t('applied') : t('applied')})
                </span>
              </div>
              <div className="flex items-center">
                <span className="font-medium text-green-700 mr-2">
                  -{formatPrice((breakdown as { discount_total?: number }).discount_total || 0, 'USD')}
                </span>
                <TrendingDown 
                  className={`h-4 w-4 text-green-500 transition-transform ${
                    expandedSections.discounts ? 'rotate-180' : ''
                  }`}
                />
              </div>
            </button>
            
            {expandedSections.discounts && (
              <div className="mt-3 pl-4 space-y-2">
                {breakdown.discounts.map((discount, index) => (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <div className="flex items-center">
                      <Tag className="h-3 w-3 text-green-500 mr-1" />
                      <span className="text-gray-900 dark:text-gray-100">{discount.name}</span>
                      {discount.percentage && (
                        <span className="text-green-600 ml-2">
                          ({discount.percentage}%)
                        </span>
                      )}
                      {onRemoveDiscount && (
                        <button
                          onClick={() => onRemoveDiscount(index)}
                          className="ml-2 text-red-500 hover:text-red-700 text-xs"
                        >
                          {t('remove')}
                        </button>
                      )}
                    </div>
                    <span className="text-green-700 font-medium">
                      -{formatPrice(discount.amount, 'USD')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Summary Cards */}
        {(totalSavings > 0 || (totalExtras > 0 && breakdown?.pricing_type !== 'transfer')) && (
          <div className="border-t pt-4 mb-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {totalSavings > 0 && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-3">
                  <div className="flex items-center">
                    <TrendingDown className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm font-medium text-green-800 dark:text-green-200">{t('totalSavings')}</span>
                  </div>
                  <div className="text-lg font-bold text-green-700 dark:text-green-300 mt-1">
                    {formatPrice(totalSavings, 'USD')}
                  </div>
                </div>
              )}
              
              {totalExtras > 0 && breakdown?.pricing_type !== 'transfer' && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3">
                  <div className="flex items-center">
                    <TrendingUp className="h-4 w-4 text-blue-500 mr-2" />
                    <span className="text-sm font-medium text-blue-800 dark:text-blue-200">{t('feesAndTaxes')}</span>
                  </div>
                  <div className="text-lg font-bold text-blue-700 dark:text-blue-300 mt-1">
                    {formatPrice(totalExtras, 'USD')}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Discount Code Input - Moved here before final total */}
        {onDiscountCodeChange && onApplyDiscount && (
          <div className="border-t pt-4 mb-4">
            <div className="flex items-center space-x-2">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder={t('enterDiscountCode')}
                  value={discountCode}
                  onChange={(e) => onDiscountCodeChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>
              <button
                onClick={onApplyDiscount}
                disabled={!discountCode.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                {t('apply')}
              </button>
            </div>
          </div>
        )}

        {/* Final Total */}
        <div className="border-t-2 border-gray-200 dark:border-gray-700 pt-4">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-xl font-bold text-gray-900 dark:text-gray-100">{t('total')}</span>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {t('allFeesIncluded')}
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {formatPrice(
                  // For transfers, use breakdown.final_price directly
                  // For events/tours, use the manual calculation
                  breakdown && breakdown.final_price ? breakdown.final_price :
                  (selectedSeats.length > 0 ? selectedSeats.reduce((sum, seat) => sum + seat.price, 0) : 0) +
                  (selectedOptions.length > 0 ? selectedOptions.reduce((sum, opt) => sum + (opt.price * opt.quantity), 0) : 0) +
                  (breakdown ? breakdown.fees_total + breakdown.taxes_total : 0),
                  'USD'
                )}
              </div>
              {totalSavings > 0 && (
                <div className="text-sm text-green-600 dark:text-green-400">
                  {t('youSave')} {formatPrice(totalSavings, 'USD')}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Payment Security Notice */}
        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="flex items-start">
            <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
            <div className="text-xs text-gray-600 dark:text-gray-400">
              <p className="font-medium mb-1">{t('securePayment')}</p>
              <p>{t('paymentSecurityNotice')}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 