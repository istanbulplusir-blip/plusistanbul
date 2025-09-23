'use client';

import React, { useState } from 'react';
import { NormalizedPriceBreakdown } from '@/lib/utils/pricing';
import { Receipt, TrendingDown, TrendingUp, CheckCircle2, Tag } from 'lucide-react';

export interface PriceSummaryProps {
  title?: string;
  breakdown: NormalizedPriceBreakdown | null | undefined;
  formatPrice?: (price: number, currency?: string) => string;
}

const defaultFormat = (price: number, currency?: string) => {
  try {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: currency || 'USD' }).format(price || 0);
  } catch {
    return `${currency || 'USD'} ${Number(price || 0).toFixed(2)}`;
  }
};

export default function PriceSummary({ title = 'Price Summary (Normalized)', breakdown, formatPrice = defaultFormat }: PriceSummaryProps) {
  const [expandedSections, setExpandedSections] = useState<{
    discounts: boolean;
  }>({
    discounts: false
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  if (!breakdown) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 text-center">
        <Receipt className="h-12 w-12 text-gray-300 dark:text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No pricing data</h3>
        <p className="text-gray-600 dark:text-gray-400">Select options for pricing</p>
      </div>
    );
  }

  const currency = breakdown.currency || 'USD';
  const modifiers = breakdown.modifiers || {};
  const hasOutbound = typeof modifiers.outbound_surcharge === 'number' && modifiers.outbound_surcharge !== 0;
  const hasReturn = typeof modifiers.return_surcharge === 'number' && modifiers.return_surcharge !== 0;
  const hasRoundTripDiscount = typeof modifiers.round_trip_discount === 'number' && modifiers.round_trip_discount !== 0;
  const hasPriceModifier = typeof modifiers.price_modifier === 'number' && modifiers.price_modifier !== 0;
  
  // Mock discounts for demonstration (since NormalizedPriceBreakdown doesn't have discounts)
  const mockDiscounts = hasRoundTripDiscount ? [
    {
      name: 'Round-trip Discount',
      amount: modifiers.round_trip_discount || 0,
      percentage: null
    }
  ] : [];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
        <div className="flex items-center">
          <Receipt className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
        </div>
      </div>

      <div className="p-4">
        {/* Base Price */}
        <div className="space-y-3 mb-4">
          {/* For round-trip transfers, show outbound and return separately */}
          {hasReturn && hasOutbound ? (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    Base Price
                  </span>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {formatPrice(Number(breakdown.base_price || 0) / 2, currency)} outbound
                  </div>
                </div>
                <span className="font-semibold text-gray-900 dark:text-gray-100">
                  {formatPrice(Number(breakdown.base_price || 0) / 2, currency)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    Base Price
                  </span>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {formatPrice(Number(breakdown.base_price || 0) / 2, currency)} return
                  </div>
                </div>
                <span className="font-semibold text-gray-900 dark:text-gray-100">
                  {formatPrice(Number(breakdown.base_price || 0) / 2, currency)}
                </span>
              </div>
            </div>
          ) : (
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  Base Price
                </span>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {formatPrice(Number(breakdown.base_price || 0), currency)}
                </div>
              </div>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(Number(breakdown.base_price || 0), currency)}
              </span>
            </div>
          )}
        </div>

        {/* Price Modifier */}
        {hasPriceModifier && (
          <div className="border-t pt-4 mb-4">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-900 dark:text-gray-100">Price Modifier</span>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {formatPrice(Number(modifiers.price_modifier || 0), currency)}
                </div>
              </div>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(Number(modifiers.price_modifier || 0), currency)}
              </span>
            </div>
          </div>
        )}

        {/* Outbound Surcharge */}
        {hasOutbound && (
          <div className="border-t pt-4 mb-4">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-900 dark:text-gray-100">Outbound Surcharge</span>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {formatPrice(Number(modifiers.outbound_surcharge || 0), currency)}
                </div>
              </div>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(Number(modifiers.outbound_surcharge || 0), currency)}
              </span>
            </div>
          </div>
        )}

        {/* Return Surcharge */}
        {hasReturn && (
          <div className="border-t pt-4 mb-4">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-900 dark:text-gray-100">Return Surcharge</span>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {formatPrice(Number(modifiers.return_surcharge || 0), currency)}
                </div>
              </div>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(Number(modifiers.return_surcharge || 0), currency)}
              </span>
            </div>
          </div>
        )}

        {/* Discounts */}
        {mockDiscounts.length > 0 && (
          <div className="border-t pt-4 mb-4">
            <button
              onClick={() => toggleSection('discounts')}
              className="flex items-center justify-between w-full text-left"
            >
              <div className="flex items-center">
                <span className="font-medium text-green-700">Discounts</span>
                <span className="ml-2 text-sm text-green-600">
                  ({mockDiscounts.length} applied)
                </span>
              </div>
              <div className="flex items-center">
                <span className="font-medium text-green-700 mr-2">
                  -{formatPrice(mockDiscounts.reduce((sum, d) => sum + d.amount, 0), currency)}
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
                {mockDiscounts.map((discount, index) => (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <div className="flex items-center">
                      <Tag className="h-3 w-3 text-green-500 mr-1" />
                      <span className="text-gray-900 dark:text-gray-100">{discount.name}</span>
                      {discount.percentage && (
                        <span className="text-green-600 ml-2">
                          ({discount.percentage}%)
                        </span>
                      )}
                    </div>
                    <span className="text-green-600 dark:text-green-400">
                      -{formatPrice(discount.amount, currency)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Options */}
        {Number(breakdown.options_total || 0) > 0 && (
          <div className="border-t pt-4 mb-4">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-900 dark:text-gray-100">Options</span>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {formatPrice(Number(breakdown.options_total || 0), currency)}
                </div>
              </div>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(Number(breakdown.options_total || 0), currency)}
              </span>
            </div>
          </div>
        )}

        {/* Fees */}
        {Number(breakdown.fees_total || 0) > 0 && (
          <div className="border-t pt-4 mb-4">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-900 dark:text-gray-100">Fees</span>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {formatPrice(Number(breakdown.fees_total || 0), currency)}
                </div>
              </div>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(Number(breakdown.fees_total || 0), currency)}
              </span>
            </div>
          </div>
        )}

        {/* Taxes */}
        {Number(breakdown.taxes_total || 0) > 0 && (
          <div className="border-t pt-4 mb-4">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-gray-900 dark:text-gray-100">Taxes</span>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {formatPrice(Number(breakdown.taxes_total || 0), currency)}
                </div>
              </div>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatPrice(Number(breakdown.taxes_total || 0), currency)}
              </span>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        {(hasRoundTripDiscount || Number(breakdown.fees_total || 0) > 0 || Number(breakdown.taxes_total || 0) > 0) && (
          <div className="border-t pt-4 mb-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {hasRoundTripDiscount && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-3">
                  <div className="flex items-center">
                    <TrendingDown className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm font-medium text-green-800 dark:text-green-200">Total Savings</span>
                  </div>
                  <div className="text-lg font-bold text-green-700 dark:text-green-300 mt-1">
                    {formatPrice(Number(modifiers.round_trip_discount || 0), currency)}
                  </div>
                </div>
              )}
              
              {(Number(breakdown.fees_total || 0) > 0 || Number(breakdown.taxes_total || 0) > 0) && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3">
                  <div className="flex items-center">
                    <TrendingUp className="h-4 w-4 text-blue-500 mr-2" />
                    <span className="text-sm font-medium text-blue-800 dark:text-blue-200">Fees & Taxes</span>
                  </div>
                  <div className="text-lg font-bold text-blue-700 dark:text-blue-300 mt-1">
                    {formatPrice(Number(breakdown.fees_total || 0) + Number(breakdown.taxes_total || 0), currency)}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Final Total */}
        <div className="border-t-2 border-gray-200 dark:border-gray-700 pt-4">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-xl font-bold text-gray-900 dark:text-gray-100">Total</span>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                All fees included
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {formatPrice(Number(breakdown.final_price || 0), currency)}
              </div>
              {hasRoundTripDiscount && (
                <div className="text-sm text-green-600 dark:text-green-400">
                  You save {formatPrice(Number(modifiers.round_trip_discount || 0), currency)}
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
              <p className="font-medium mb-1">Secure Payment</p>
              <p>Your payment information is encrypted and secure</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


